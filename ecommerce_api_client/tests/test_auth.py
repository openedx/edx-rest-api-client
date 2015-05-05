from unittest import TestCase

import httpretty
import jwt
import requests

from ecommerce_api_client.auth import JwtAuth, BearerAuth


class JwtAuthTests(TestCase):
    def setUp(self):
        super(JwtAuthTests, self).setUp()
        self.url = 'http://example.com/'
        self.username = 'alice'
        self.email = 'alice@example.com'
        self.signing_key = 'edx'
        httpretty.register_uri(httpretty.GET, self.url)

    def assert_expected_token_value(self, tracking_context=None):
        """ DRY helper. """

        # Mock the HTTP response and issue the request
        auth_kwargs = {'tracking_context': tracking_context} if tracking_context else {}
        requests.get(self.url, auth=JwtAuth(self.username, self.email, self.signing_key, **auth_kwargs))

        # Verify the header was set as expected on the request
        data = {
            'username': self.username,
            'email': self.email
        }
        data.update(auth_kwargs)
        token = jwt.encode(data, self.signing_key)
        self.assertEqual(httpretty.last_request().headers['Authorization'], 'JWT {}'.format(token))

    @httpretty.activate
    def test_headers(self):
        """ Verify the class adds an Authorization header that includes the correct JWT. """
        self.assert_expected_token_value()

    @httpretty.activate
    def test_tracking_context(self):
        """ Verify the tracking context is enclosed in the token payload, when specified. """
        self.assert_expected_token_value({'foo': 'bar'})


class BearerAuthTests(TestCase):
    def setUp(self):
        super(BearerAuthTests, self).setUp()
        self.url = 'http://example.com/'
        httpretty.register_uri(httpretty.GET, self.url)

    @httpretty.activate
    def test_headers(self):
        """ Verify the class adds an Authorization headers with the bearer token. """
        token = 'abc123'
        requests.get(self.url, auth=BearerAuth(token))
        self.assertEqual(httpretty.last_request().headers['Authorization'], 'Bearer {}'.format(token))
