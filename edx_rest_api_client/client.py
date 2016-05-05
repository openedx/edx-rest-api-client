import datetime

import requests
import slumber

from edx_rest_api_client.auth import BearerAuth, JwtAuth, SuppliedJwtAuth


class EdxRestApiClient(slumber.API):

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
            }
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
            auth = BearerAuth(oauth_access_token)  # pylint: disable=redefined-variable-type
        elif signing_key and username:
            auth = JwtAuth(username, full_name, email, signing_key,
                           issuer=issuer, expires_in=expires_in, tracking_context=tracking_context)
        else:
            auth = None

        session = session or requests.Session()
        session.timeout = timeout
        super(EdxRestApiClient, self).__init__(
            url,
            session=session,
            auth=auth,
            **kwargs
        )
