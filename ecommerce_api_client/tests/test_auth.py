from unittest import TestCase

import httpretty
import jwt
import requests

from ecommerce_api_client.auth import JwtAuth


class JwtAuthTests(TestCase):
    @httpretty.activate
    def test_headers(self):
        """ Verify the class adds an Authorization header that includes the correct JWT. """

        url = 'http://example.com/'
        username = 'alice'
        email = 'alice@example.com'
        signing_key = 'edx'

        # Mock the HTTP response and issue the request
        httpretty.register_uri(httpretty.GET, url)
        requests.get(url, auth=JwtAuth(username, email, signing_key))

        # Verify the header was set on the request
        data = {
            'username': username,
            'email': email
        }
        token = jwt.encode(data, signing_key)
        self.assertEqual(httpretty.last_request().headers['Authorization'], 'JWT {0}'.format(token))
