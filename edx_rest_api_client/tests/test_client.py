# -*- coding: utf-8 -*-
import datetime
import json
import os
from unittest import TestCase

import ddt
import mock
import requests
import responses
from freezegun import freeze_time

from edx_rest_api_client import __version__
from edx_rest_api_client.auth import JwtAuth
from edx_rest_api_client.client import EdxRestApiClient, OAuthAPIClient, get_oauth_access_token, user_agent
from edx_rest_api_client.tests.mixins import AuthenticationTestMixin

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
        ({'url': URL, 'signing_key': None, 'username': USERNAME}, type(None)),
        ({'url': URL, 'signing_key': SIGNING_KEY, 'username': None}, type(None)),
        ({'url': URL, 'signing_key': None, 'username': None, 'oauth_access_token': None}, type(None))
    )
    def test_valid_configuration(self, kwargs, auth_type):
        """
        The constructor should return successfully if all arguments are valid.
        We also check that the auth type of the api is what we expect.
        """
        api = EdxRestApiClient(**kwargs)
        self.assertIsInstance(api._store['session'].auth, auth_type)  # pylint: disable=protected-access

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

    def test_user_agent(self):
        """Make sure our custom User-Agent is getting built correctly."""
        with mock.patch('socket.gethostbyname', return_value='test_hostname'):
            default_user_agent = user_agent()
            self.assertIn('python-requests', default_user_agent)
            self.assertIn('edx-rest-api-client/{}'.format(__version__), default_user_agent)
            self.assertIn('test_hostname', default_user_agent)

        with mock.patch('socket.gethostbyname') as mock_gethostbyname:
            mock_gethostbyname.side_effect = ValueError()
            default_user_agent = user_agent()
            self.assertIn('unknown_client_name', default_user_agent)

        with mock.patch.dict(os.environ, {'EDX_REST_API_CLIENT_NAME': "awesome_app"}):
            uagent = user_agent()
            self.assertIn('awesome_app', uagent)

        self.assertEqual(user_agent(), EdxRestApiClient.user_agent())


@ddt.ddt
class ClientCredentialTests(AuthenticationTestMixin, TestCase):
    """ Test client credentials requests. """

    URL = "http://test-auth/access_token/"

    @responses.activate
    def test_get_client_credential_access_token_success(self):
        """ Test that the get access token method handles 200 responses and returns the access token. """
        code = 200
        body = {"access_token": "my-token", "expires_in": 1000}
        now = datetime.datetime.utcnow()

        expected_return = ("my-token", now + datetime.timedelta(seconds=1000))

        with freeze_time(now):
            self._mock_auth_api(URL, code, body=body)
            self.assertEqual(
                EdxRestApiClient.get_oauth_access_token(URL, "client_id", "client_secret"),
                expected_return
            )

    @ddt.data(
        (400, {"error": "denied"}),
        (500, None)
    )
    @ddt.unpack
    @responses.activate
    def test_get_client_credential_access_token_failure(self, code, body):
        """ Test that the get access token method handles failure responses. """
        with self.assertRaises(requests.RequestException):
            self._mock_auth_api(URL, code, body=body)
            EdxRestApiClient.get_oauth_access_token(URL, "client_id", "client_secret")

    def test_refresh_token_required(self):
        self._mock_auth_api(URL, 200, body=None)
        with self.assertRaises(AssertionError):
            get_oauth_access_token(URL, 'client_id', 'client_secret', grant_type='refresh_token')


@ddt.ddt
class OAuthAPIClientTests(AuthenticationTestMixin, TestCase):
    """
    Tests for OAuthAPIClient
    """
    base_url = 'http://testing.test'
    client_id = 'test'
    client_secret = 'secret'

    @responses.activate
    @ddt.data(
        'http://testing.test',
        'http://testing.test/oauth2',
    )
    def test_automatic_auth(self, client_base_url):
        """
        Test that the JWT token is automatically set
        """
        client_session = OAuthAPIClient(client_base_url, self.client_id, self.client_secret)
        self._mock_auth_api(self.base_url + '/oauth2/access_token', 200, {'access_token': 'abcd', 'expires_in': 60})
        self._mock_auth_api(self.base_url + '/endpoint', 200, {'status': 'ok'})
        response = client_session.post(self.base_url + '/endpoint', data={'test': 'ok'})
        self.assertIn('client_id=%s' % self.client_id, responses.calls[0].request.body)
        self.assertEqual(client_session.auth.token, 'abcd')
        self.assertEqual(response.json()['status'], 'ok')

    @responses.activate
    def test_automatic_token_refresh(self):
        """
        Test that the JWT token is automatically refreshed
        """
        tokens = ['cred2', 'cred1']

        def auth_callback(request):
            resp = {'expires_in': 60}
            if 'grant_type=client_credentials' in request.body:
                resp['access_token'] = tokens.pop()
            return (200, {}, json.dumps(resp))

        responses.add_callback(
            responses.POST, self.base_url + '/oauth2/access_token',
            callback=auth_callback,
            content_type='application/json',
        )

        client_session = OAuthAPIClient(self.base_url, self.client_id, self.client_secret)
        self._mock_auth_api(self.base_url + '/endpoint', 200, {'status': 'ok'})
        response = client_session.post(self.base_url + '/endpoint', data={'test': 'ok'})
        self.assertEqual(client_session.auth.token, 'cred1')
        self.assertEqual(response.json()['status'], 'ok')
        with freeze_time(datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)):
            response = client_session.post(self.base_url + '/endpoint', data={'test': 'ok'})
            self.assertEqual(client_session.auth.token, 'cred2')
