import os
import socket
import warnings
from datetime import datetime, timedelta

import requests
import requests.utils
import slumber

from edx_django_utils.cache import TieredCache
from edx_rest_api_client.auth import BearerAuth, JwtAuth, SuppliedJwtAuth
from edx_rest_api_client.__version__ import __version__


def user_agent():
    """
    Return a User-Agent that identifies this client.

    Example:
        python-requests/2.9.1 edx-rest-api-client/1.7.2 ecommerce

    The last item in the list will be the application name, taken from the
    OS environment variable EDX_REST_API_CLIENT_NAME. If that environment
    variable is not set, it will default to the hostname.
    """
    client_name = 'unknown_client_name'
    try:
        client_name = os.environ.get("EDX_REST_API_CLIENT_NAME") or socket.gethostbyname(socket.gethostname())
    except:  # pylint: disable=bare-except
        pass  # using 'unknown_client_name' is good enough.  no need to log.
    return "{} edx-rest-api-client/{} {}".format(
        requests.utils.default_user_agent(),  # e.g. "python-requests/2.9.1"
        __version__,  # version of this client
        client_name
    )


USER_AGENT = user_agent()


def get_oauth_access_token(url, client_id, client_secret, token_type='jwt', grant_type='client_credentials',
                           refresh_token=None):
    """ Retrieves OAuth 2.0 access token using the given grant type.

    Args:
        url (str): Oauth2 access token endpoint
        client_id (str): client ID
        client_secret (str): client secret
    Kwargs:
        token_type (str): Type of token to return. Options include bearer and jwt.
        grant_type (str): One of 'client_credentials' or 'refresh_token'
        refresh_token (str): The previous access token (for grant_type=refresh_token)

    Returns:
        tuple: Tuple containing access token string and expiration datetime.
    """
    now = datetime.utcnow()
    data = {
        'grant_type': grant_type,
        'client_id': client_id,
        'client_secret': client_secret,
        'token_type': token_type,
    }
    if refresh_token:
        data['refresh_token'] = refresh_token
    else:
        assert grant_type != 'refresh_token', "refresh_token parameter required"

    response = requests.post(
        url,
        data=data,
        headers={
            'User-Agent': USER_AGENT,
        },
    )

    data = response.json()
    try:
        access_token = data['access_token']
        expires_in = data['expires_in']
    except KeyError:
        raise requests.RequestException(response=response)

    expires_at = now + timedelta(seconds=expires_in)

    return access_token, expires_at


class OAuthAPIClient(requests.Session):
    """
    A :class:`requests.Session` that automatically authenticates against edX's preferred
    authentication method, given a client id and client secret. The underlying implementation
    is subject to change.

    Note: Requires Django + Middleware for TieredCache, used for caching the access token.
    See https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/cache/README.rst#tieredcache
    """
    # Consider tokens that expire in 5 seconds as already expired
    ACCESS_TOKEN_EXPIRED_THRESHOLD = 5
    ALREADY_EXPIRED_DATETIME = datetime(1983, 4, 6, 7, 30, 0)

    def __init__(self, base_url, client_id, client_secret, **kwargs):
        """
        Args:
            base_url (str): base url of the LMS instance, with or without including the path `/oauth2` (see note).
            client_id (str): Client ID
            client_secret (str): Client secret

        Note:
            The example value of either of the following two commonly found settings would be acceptable as
            the `base_url` argument.::

                LMS_BASE_URL = 'http://edx.devstack.lms:18000'
                BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = 'http://edx.devstack.lms:18000/oauth2'

        """
        super(OAuthAPIClient, self).__init__(**kwargs)
        self.headers['user-agent'] = USER_AGENT
        self._base_url = base_url.rstrip('/')
        self._client_id = client_id
        self._client_secret = client_secret

        self.auth = SuppliedJwtAuth(None)

    def _get_oauth_url(self, base_url):
        """
        Returns the oauth2 url.

        Note:
            The resulting url will always be something like http://<LMS_BASE_URL>/oauth2/access_token,
            regardless of whether the `base_url` already included the path `/oauth2`.

        """
        base_url = base_url.rstrip('/')
        if base_url.endswith('/oauth2'):
            return base_url + '/access_token'

        return base_url + '/oauth2/access_token'

    def _get_oauth_access_token_cache_key(self):
        return 'edx_rest_api_client.oauth_access_token_response.{}'.format(self._client_id)

    def _check_auth(self):
        oauth_access_token_cache_key = self._get_oauth_access_token_cache_key()
        cached_response = TieredCache.get_cached_response(oauth_access_token_cache_key)

        if cached_response.is_found:
            _, expiration = cached_response.value
            adjusted_expiration = expiration - timedelta(seconds=self.ACCESS_TOKEN_EXPIRED_THRESHOLD)
        else:
            adjusted_expiration = self.ALREADY_EXPIRED_DATETIME

        if datetime.utcnow() > adjusted_expiration:
            oauth_url = self._get_oauth_url(self._base_url)
            grant_type = 'client_credentials'
            oauth_access_token_response = get_oauth_access_token(
                oauth_url,
                self._client_id,
                self._client_secret,
                grant_type=grant_type)
            self.auth.token, _ = oauth_access_token_response
            TieredCache.set_all_tiers(oauth_access_token_cache_key, oauth_access_token_response)

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """
        Overrides Session.request to ensure that the session is authenticated
        """
        self._check_auth()
        return super(OAuthAPIClient, self).request(method, url, **kwargs)


class EdxRestApiClient(slumber.API):
    """
    API client for edX REST API.

    (deprecated)
    """

    @classmethod
    def user_agent(cls):
        return USER_AGENT

    @classmethod
    def get_oauth_access_token(cls, url, client_id, client_secret, token_type='bearer'):
        return get_oauth_access_token(url, client_id, client_secret, token_type=token_type)

    def __init__(self, url, signing_key=None, username=None, full_name=None, email=None,
                 timeout=5, issuer=None, expires_in=30, tracking_context=None, oauth_access_token=None,
                 session=None, jwt=None, **kwargs):
        """
        Instantiate a new client. You can pass extra kwargs to Slumber like
        'append_slash'.

        Raises:
            ValueError: If a URL is not provided.

        """

        if not url:
            raise ValueError('An API url must be supplied!')

        warnings.warn('EdxRestApiClient is deprecated. Use OAuthAPIClient instead.')

        if jwt:
            auth = SuppliedJwtAuth(jwt)
        elif oauth_access_token:
            auth = BearerAuth(oauth_access_token)
        elif signing_key and username:
            auth = JwtAuth(username, full_name, email, signing_key,
                           issuer=issuer, expires_in=expires_in, tracking_context=tracking_context)
        else:
            auth = None

        session = session or requests.Session()
        session.headers['User-Agent'] = self.user_agent()

        session.timeout = timeout
        super(EdxRestApiClient, self).__init__(
            url,
            session=session,
            auth=auth,
            **kwargs
        )


EdxRestApiClient.user_agent.__func__.__doc__ = user_agent.__doc__
EdxRestApiClient.get_oauth_access_token.__func__.__doc__ = get_oauth_access_token.__doc__
