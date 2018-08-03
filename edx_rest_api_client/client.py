import datetime
import os
import socket

import requests
import requests.utils
import slumber

from edx_rest_api_client.auth import BearerAuth, JwtAuth, SuppliedJwtAuth
from edx_rest_api_client.__version__ import __version__


class EdxRestApiClient(slumber.API):

    @classmethod
    def user_agent(cls):
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

    @classmethod
    def get_oauth_access_token(cls, url, client_id, client_secret, token_type='bearer'):
        """ Retrieves OAuth 2.0 access token using the client credentials grant.

        Args:
            url (str): Oauth2 access token endpoint
            client_id (str): client ID
            client_secret (str): client secret
            token_type (str): Type of token to return. Options include bearer and jwt.

        Returns:
            tuple: Tuple containing access token string and expiration datetime.
        """
        now = datetime.datetime.utcnow()

        response = requests.post(
            url,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'token_type': token_type,
            },
            headers={
                'User-Agent': cls.user_agent(),
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
