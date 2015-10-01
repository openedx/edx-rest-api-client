import requests
import slumber

from ecommerce_api_client.auth import JwtAuth, BearerAuth


class EcommerceApiClient(slumber.API):
    def __init__(self, url, signing_key=None, username=None, full_name=None, email=None,
                 timeout=5, issuer=None, expires_in=30, tracking_context=None, oauth_access_token=None,
                 session=None):
        """
        Instantiate a new client.

        Raises:
            ValueError, if either the URL or necessary authentication values are not provided.
        """

        if not url:
            raise ValueError('An API url must be supplied!')

        if oauth_access_token:
            auth = BearerAuth(oauth_access_token)
        elif signing_key and username:
            auth = JwtAuth(username, full_name, email, signing_key,
                           issuer=issuer, expires_in=expires_in, tracking_context=tracking_context)
        else:
            raise ValueError('Either JWT or OAuth2 credentials must be suppled for authentication!')

        session = session or requests.Session()
        session.timeout = timeout
        super(EcommerceApiClient, self).__init__(
            url,
            session=session,
            auth=auth
        )
