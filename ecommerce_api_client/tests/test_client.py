from unittest import TestCase

import ddt
import mock

from ecommerce_api_client.client import EcommerceApiClient


URL = 'http://example.com/api/v2'
SIGNING_KEY = 'edx'
USERNAME = 'edx'
EMAIL = 'edx@example.com'
TRACKING_CONTEXT = {'foo': 'bar'}
ACCESS_TOKEN = 'abc123'


@ddt.ddt
class EcommerceApiClientTests(TestCase):
    """ Tests for the E-Commerce API client. """

    def test_valid_configuration(self):
        """ The constructor should return successfully if all arguments are valid. """
        EcommerceApiClient(URL, SIGNING_KEY, USERNAME, EMAIL)

    @ddt.data(
        {'url': None, 'signing_key': SIGNING_KEY, 'username': USERNAME, 'email': EMAIL},
        {'url': URL, 'signing_key': None, 'username': USERNAME, 'email': EMAIL},
        {'url': URL, 'signing_key': SIGNING_KEY, 'username': None, 'email': EMAIL},
        {'url': URL, 'signing_key': SIGNING_KEY, 'username': USERNAME, 'email': None},
        {'url': None, 'signing_key': None, 'username': None, 'email': None, 'oauth_access_token': None},
    )
    def test_invalid_configuration(self, kwargs):
        """ If the constructor arguments are invalid, an InvalidConfigurationError should be raised. """
        self.assertRaises(ValueError, EcommerceApiClient, **kwargs)

    @mock.patch('ecommerce_api_client.auth.JwtAuth.__init__', return_value=None)
    def test_tracking_context(self, mock_auth):
        """ Ensure the tracking context is included with API requests if specified. """
        EcommerceApiClient(URL, SIGNING_KEY, USERNAME, EMAIL, tracking_context=TRACKING_CONTEXT)
        self.assertDictContainsSubset(mock_auth.call_args[1], TRACKING_CONTEXT)

    def test_oauth2(self):
        """ Ensure OAuth2 authentication is used when an access token is supplied to the constructor. """

        with mock.patch('ecommerce_api_client.auth.BearerAuth.__init__', return_value=None) as mock_auth:
            EcommerceApiClient(URL, oauth_access_token=ACCESS_TOKEN)
            mock_auth.assert_called_with(ACCESS_TOKEN)
