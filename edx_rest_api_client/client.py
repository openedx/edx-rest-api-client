import datetime
import os
import socket
import warnings

import requests
import requests.utils
import slumber

from edx_django_utils.cache import TieredCache
from edx_django_utils.monitoring import set_custom_metric
from edx_rest_api_client.auth import BearerAuth, JwtAuth, SuppliedJwtAuth
from edx_rest_api_client.__version__ import __version__


# When caching tokens, use this value to err on expiring tokens a little early so they are
# sure to be valid at the time they are used.
ACCESS_TOKEN_EXPIRED_THRESHOLD_SECONDS = 5


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


def _get_oauth_url(url):
    """
    Returns the complete url for the oauth2 endpoint.

    Args:
        url (str): base url of the LMS oauth endpoint, which can optionally include some or all of the path
            ``/oauth2/access_token``. Common example settings that would work for ``url`` would include:
                LMS_BASE_URL = 'http://edx.devstack.lms:18000'
                BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = 'http://edx.devstack.lms:18000/oauth2'

    """
    stripped_url = url.rstrip('/')
    if stripped_url.endswith('/access_token'):
        return url

    if stripped_url.endswith('/oauth2'):
        return stripped_url + '/access_token'

    return stripped_url + '/oauth2/access_token'


def get_oauth_access_token(url, client_id, client_secret, token_type='jwt', grant_type='client_credentials',
                           refresh_token=None):
    """ Retrieves OAuth 2.0 access token using the given grant type.

    Args:
        url (str): Oauth2 access token endpoint, optionally including part of the path.
        client_id (str): client ID
        client_secret (str): client secret
    Kwargs:
        token_type (str): Type of token to return. Options include bearer and jwt.
        grant_type (str): One of 'client_credentials' or 'refresh_token'
        refresh_token (str): The previous access token (for grant_type=refresh_token)

    Raises:
        requests.RequestException if there is a problem retrieving the access token.

    Returns:
        tuple: Tuple containing (access token string, expiration datetime).

    """
    now = datetime.datetime.utcnow()
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
        _get_oauth_url(url),
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

    expires_at = now + datetime.timedelta(seconds=expires_in)

    return access_token, expires_at


def get_and_cache_oauth_access_token(url, client_id, client_secret, token_type='jwt', grant_type='client_credentials',
                                     refresh_token=None):
    """ Retrieves a possibly cached OAuth 2.0 access token using the given grant type.

    See ``get_oauth_access_token`` for usage details.

    First retrieves the access token from the cache and ensures it has not expired. If
    the access token either wasn't found in the cache, or was expired, retrieves a new
    access token and caches it for the lifetime of the token.

    Note: Consider tokens to be expired ACCESS_TOKEN_EXPIRED_THRESHOLD_SECONDS early
    to ensure the token won't expire while it is in use.

    Returns:
        tuple: Tuple containing (access token string, expiration datetime).

    """
    cache_key = 'edx_rest_api_client.access_token.{}.{}.{}'.format(
        token_type,
        grant_type,
        client_id,
    )
    cached_response = TieredCache.get_cached_response(cache_key)

    # Attempt to get an unexpired cached access token
    if cached_response.is_found:
        _, expiration = cached_response.value
        # Double-check the token hasn't already expired as a safety net.
        adjusted_expiration = expiration - datetime.timedelta(seconds=ACCESS_TOKEN_EXPIRED_THRESHOLD_SECONDS)
        if datetime.datetime.utcnow() < adjusted_expiration:
            return cached_response.value

    # Get a new access token if no unexpired access token was found in the cache.
    oauth_access_token_response = get_oauth_access_token(
        _get_oauth_url(url),
        client_id,
        client_secret,
        grant_type=grant_type,
        refresh_token=refresh_token
    )

    # Cache the new access token with an expiration matching the lifetime of the token.
    _, expiration = oauth_access_token_response
    expires_in = (expiration - datetime.datetime.utcnow()).seconds - ACCESS_TOKEN_EXPIRED_THRESHOLD_SECONDS
    TieredCache.set_all_tiers(cache_key, oauth_access_token_response, expires_in)

    return oauth_access_token_response


class OAuthAPIClient(requests.Session):
    """
    A :class:`requests.Session` that automatically authenticates against edX's preferred
    authentication method, given a client id and client secret. The underlying implementation
    is subject to change.

    Note: Requires Django + Middleware for TieredCache, used for caching the access token.
    See https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/cache/README.rst#tieredcache

    """
    def __init__(self, base_url, client_id, client_secret, **kwargs):
        """
        Args:
            base_url (str): base url of the LMS oauth endpoint, which can optionally include the path `/oauth2`.
                Commonly example settings that would work for `base_url` might include:
                    LMS_BASE_URL = 'http://edx.devstack.lms:18000'
                    BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = 'http://edx.devstack.lms:18000/oauth2'
            client_id (str): Client ID
            client_secret (str): Client secret

        """
        super(OAuthAPIClient, self).__init__(**kwargs)
        self.headers['user-agent'] = USER_AGENT
        self._base_url = base_url.rstrip('/')
        self._client_id = client_id
        self._client_secret = client_secret

        self.auth = SuppliedJwtAuth(None)

    def _ensure_authentication(self):
        """
        Ensures that the Session's auth.token is set with an unexpired token.

        Raises:
            requests.RequestException if there is a problem retrieving the access token.

        """
        oauth_access_token_response = get_and_cache_oauth_access_token(
            self._base_url,
            self._client_id,
            self._client_secret,
            grant_type='client_credentials'
        )

        self.auth.token, _ = oauth_access_token_response

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """
        Overrides Session.request to ensure that the session is authenticated
        """
        set_custom_metric('api_client', 'OAuthAPIClient')
        self._ensure_authentication()
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
        warnings.warn((
            'To help transition to OAuthAPIClient, use EdxRestApiClient.get_and_cache_jwt_oauth_access_token instead'
            'of EdxRestApiClient.get_oauth_access_token to share cached jwt token used by OAuthAPIClient.'
        ))
        return get_oauth_access_token(url, client_id, client_secret, token_type=token_type)

    @classmethod
    def get_and_cache_jwt_oauth_access_token(cls, url, client_id, client_secret):
        return get_and_cache_oauth_access_token(url, client_id, client_secret, token_type="jwt")

    def __init__(self, url, signing_key=None, username=None, full_name=None, email=None,
                 timeout=5, issuer=None, expires_in=30, tracking_context=None, oauth_access_token=None,
                 session=None, jwt=None, **kwargs):
        """
        Instantiate a new client. You can pass extra kwargs to Slumber like
        'append_slash'.

        Raises:
            ValueError: If a URL is not provided.

        """
        set_custom_metric('api_client', 'EdxRestApiClient')
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
