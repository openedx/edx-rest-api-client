from unittest import TestCase

import ddt
import mock

from ecommerce_api_client.client import EcommerceApiClient


URL = 'http://example.com/api/v2'
SIGNING_KEY = 'edx'
USERNAME = 'edx'
EMAIL = 'edx@example.com'
TRACKING_CONTEXT = {'foo': 'bar'}


@ddt.ddt
class EcommerceApiClientTests(TestCase):
    """ Tests for the E-Commerce API client. """

    def test_valid_configuration(self):
        """ The constructor should return successfully if all arguments are valid. """
        EcommerceApiClient(URL, SIGNING_KEY, USERNAME, EMAIL)

    @ddt.data(
        (None, SIGNING_KEY, USERNAME, EMAIL),
        (URL, None, USERNAME, EMAIL),
        (URL, SIGNING_KEY, None, EMAIL),
        (URL, SIGNING_KEY, USERNAME, None),
    )
    def test_invalid_configuration(self, args):
        """ If the constructor arguments are invalid, an InvalidConfigurationError should be raised. """
        self.assertRaises(ValueError, EcommerceApiClient, *args)

    @mock.patch('ecommerce_api_client.auth.JwtAuth.__init__', return_value=None)
    def test_tracking_context(self, mock_auth):
        """ Ensure the tracking context is included with API requests if specified. """
        EcommerceApiClient(URL, SIGNING_KEY, USERNAME, EMAIL, tracking_context=TRACKING_CONTEXT)
        self.assertDictContainsSubset(mock_auth.call_args[1], TRACKING_CONTEXT)
