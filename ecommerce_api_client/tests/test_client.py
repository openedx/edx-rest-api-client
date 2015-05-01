from unittest import TestCase

import ddt

from ecommerce_api_client.client import EcommerceApiClient


URL = 'http://example.com/api/v2'
SIGNING_KEY = 'edx'
USERNAME = 'edx'
EMAIL = 'edx@example.com'


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
