import requests
import slumber

from ecommerce_api_client.auth import JwtAuth, BearerAuth


class EcommerceApiClient(slumber.API):
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, url, signing_key=None, username=None, email=None, timeout=5, tracking_context=None,
                 oauth_access_token=None):
        """
        Instantiate a new client.

        Raises
            ValueError if either the URL or necessary authentication values are not provided.
        """

        if not url:
            raise ValueError('An API url must be supplied!')

        if oauth_access_token:
            auth = BearerAuth(oauth_access_token)
        elif signing_key and username and email:
            auth = JwtAuth(username, email, signing_key, tracking_context)
        else:
            raise ValueError('Either JWT or OAuth2 credentials must be suppled for authentication!')

        session = requests.Session()
        session.timeout = timeout
        super(EcommerceApiClient, self).__init__(
            url,
            session=session,
            auth=auth
        )
