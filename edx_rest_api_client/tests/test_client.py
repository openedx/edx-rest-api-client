# -*- coding: utf-8 -*-
from types import NoneType
from unittest import TestCase

import ddt
import mock

from edx_rest_api_client.auth import JwtAuth
from edx_rest_api_client.client import EdxRestApiClient


URL = 'http://example.com/api/v2'
SIGNING_KEY = 'edx'
USERNAME = 'edx'
FULL_NAME = 'édx äpp'
EMAIL = 'edx@example.com'
TRACKING_CONTEXT = {'foo': 'bar'}
ACCESS_TOKEN = 'abc123'
JWT = 'abc.123.doremi'


@ddt.ddt
class EdxRestApiClientTests(TestCase):
    """ Tests for the E-Commerce API client. """

    @ddt.unpack
    @ddt.data(
        ({'url': URL, 'signing_key': SIGNING_KEY, 'username': USERNAME,
          'full_name': FULL_NAME, 'email': EMAIL}, JwtAuth),
        ({'url': URL, 'signing_key': SIGNING_KEY, 'username': USERNAME, 'full_name': None, 'email': EMAIL}, JwtAuth),
        ({'url': URL, 'signing_key': SIGNING_KEY, 'username': USERNAME,
          'full_name': FULL_NAME, 'email': None}, JwtAuth),
        ({'url': URL, 'signing_key': SIGNING_KEY, 'username': USERNAME, 'full_name': None, 'email': None}, JwtAuth),
        ({'url': URL, 'signing_key': SIGNING_KEY, 'username': USERNAME}, JwtAuth),
        ({'url': URL, 'signing_key': None, 'username': USERNAME}, NoneType),
        ({'url': URL, 'signing_key': SIGNING_KEY, 'username': None}, NoneType),
        ({'url': URL, 'signing_key': None, 'username': None, 'oauth_access_token': None}, NoneType)
    )
    def test_valid_configuration(self, kwargs, auth_type):
        """
        The constructor should return successfully if all arguments are valid.
        We also check that the auth type of the api is what we expect.
        """
        api = EdxRestApiClient(**kwargs)
        self.assertEqual(auth_type, type(getattr(api._store["session"], "auth")))  # pylint: disable=protected-access

    @ddt.data(
        {'url': None, 'signing_key': SIGNING_KEY, 'username': USERNAME},
        {'url': None, 'signing_key': None, 'username': None, 'oauth_access_token': None},
    )
    def test_invalid_configuration(self, kwargs):
        """ If the constructor arguments are invalid, an InvalidConfigurationError should be raised. """
        self.assertRaises(ValueError, EdxRestApiClient, **kwargs)

    @mock.patch('edx_rest_api_client.auth.JwtAuth.__init__', return_value=None)
    def test_tracking_context(self, mock_auth):
        """ Ensure the tracking context is included with API requests if specified. """
        EdxRestApiClient(URL, SIGNING_KEY, USERNAME, FULL_NAME, EMAIL, tracking_context=TRACKING_CONTEXT)
        self.assertIn(TRACKING_CONTEXT, mock_auth.call_args[1].values())

    def test_oauth2(self):
        """ Ensure OAuth2 authentication is used when an access token is supplied to the constructor. """

        with mock.patch('edx_rest_api_client.auth.BearerAuth.__init__', return_value=None) as mock_auth:
            EdxRestApiClient(URL, oauth_access_token=ACCESS_TOKEN)
            mock_auth.assert_called_with(ACCESS_TOKEN)

    def test_supplied_jwt(self):
        """Ensure JWT authentication is used when a JWT is supplied to the constructor."""
        with mock.patch('edx_rest_api_client.auth.SuppliedJwtAuth.__init__', return_value=None) as mock_auth:
            EdxRestApiClient(URL, jwt=JWT)
            mock_auth.assert_called_with(JWT)