import datetime
from unittest import TestCase, mock

import jwt
import requests
import responses

from edx_rest_api_client import auth

CURRENT_TIME = datetime.datetime(2015, 7, 2, 10, 10, 10)


class JwtAuthTests(TestCase):

    def setUp(self):
        super().setUp()

        self.url = 'http://example.com/'
        self.username = 'alice'
        self.full_name = 'αlícє whítє'
        self.email = 'alice@example.com'
        self.signing_key = 'edx'

        datetime_patcher = mock.patch.object(
            auth.datetime, 'datetime',
            mock.Mock(wraps=datetime.datetime)
        )
        mocked_datetime = datetime_patcher.start()
        mocked_datetime.utcnow.return_value = CURRENT_TIME
        self.addCleanup(datetime_patcher.stop)

        responses.add(responses.GET, self.url)

    def assert_expected_token_value(self, tracking_context=None, issuer=None, expires_in=None):
        """
        DRY helper.
        """

        # Mock the HTTP response and issue the request
        auth_kwargs = {'expires_in': expires_in}

        signing_data = {
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'iat': CURRENT_TIME,
        }

        if issuer:
            auth_kwargs['issuer'] = issuer
            signing_data['iss'] = issuer

        if tracking_context:
            auth_kwargs['tracking_context'] = tracking_context
            signing_data['tracking_context'] = tracking_context

        if expires_in:
            signing_data['exp'] = CURRENT_TIME + datetime.timedelta(seconds=expires_in)

        requests.get(
            self.url,
            auth=auth.JwtAuth(
                self.username, self.full_name, self.email, self.signing_key,
                **auth_kwargs
            )
        )

        # Verify the header was set as expected on the request
        token = jwt.encode(signing_data, self.signing_key)
        self.assertEqual(responses.calls[0].request.headers['Authorization'], f'JWT {token}')

    @responses.activate
    def test_headers(self):
        """
        Verify the class adds an Authorization header that includes the correct JWT.
        """
        self.assert_expected_token_value()

    @responses.activate
    def test_tracking_context(self):
        """
        Verify the tracking context is enclosed in the token payload, when specified.
        """
        self.assert_expected_token_value(tracking_context={'foo': 'bar'})

    @responses.activate
    def test_issuer(self):
        """
        Verify that the issuer is enclosed in the token payload, when specified.
        """
        self.assert_expected_token_value(issuer='http://example.com/oauth')

    @responses.activate
    def test_expires_in(self):
        """
        Verify the expiration date is enclosed in the token payload, when specified.
        """
        self.assert_expected_token_value(expires_in=60)


class BearerAuthTests(TestCase):
    def setUp(self):
        super().setUp()
        self.url = 'http://example.com/'
        responses.add(responses.GET, self.url)

    @responses.activate
    def test_headers(self):
        """
        Verify the class adds an Authorization headers with the bearer token.
        """
        token = 'abc123'
        requests.get(self.url, auth=auth.BearerAuth(token))
        self.assertEqual(responses.calls[0].request.headers['Authorization'], f'Bearer {token}')


class SuppliedJwtAuthTests(TestCase):

    signing_key = 'super-secret'
    url = 'http://example.com/'

    def setUp(self):
        """Set up tests."""
        super().setUp()
        responses.add(responses.GET, self.url)

    @responses.activate
    def test_headers(self):
        """Verify that the token is added to the Authorization headers."""
        payload = {
            'key1': 'value1',
            'key2': 'vαlue2'
        }
        token = jwt.encode(payload, self.signing_key)
        requests.get(self.url, auth=auth.SuppliedJwtAuth(token))
        self.assertEqual(responses.calls[0].request.headers['Authorization'], f'JWT {token}')
