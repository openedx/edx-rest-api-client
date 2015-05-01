import requests
import slumber

from ecommerce_api_client.auth import JwtAuth


class EcommerceApiClient(slumber.API):
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, url, signing_key, username, email, timeout=5):
        """
        Instantiate a new client.

        Raises
            ValueError if any of the arguments--url, signing_key, username, email--are non-truthy values.
        """

        args = (('url', url), ('signing_key', signing_key), ('username', username), ('email', email))
        invalid_fields = []
        for field, value in args:
            if not value:
                invalid_fields.append(field)

        if invalid_fields:
            raise ValueError(
                'Cannot instantiate API client. Values for the following fields are invalid: {}'.format(
                    ', '.join(invalid_fields)))

        session = requests.Session()
        session.timeout = timeout
        super(EcommerceApiClient, self).__init__(url, session=session, auth=JwtAuth(username, email, signing_key))
