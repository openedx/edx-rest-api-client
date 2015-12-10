import requests
import slumber

from edx_rest_api_client.auth import BearerAuth, JwtAuth, SuppliedJwtAuth


class EdxRestApiClient(slumber.API):
    def __init__(self, url, signing_key=None, username=None, full_name=None, email=None,
                 timeout=5, issuer=None, expires_in=30, tracking_context=None, oauth_access_token=None,
                 session=None, jwt=None):
        """
        Instantiate a new client.

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
            auth=auth
        )
