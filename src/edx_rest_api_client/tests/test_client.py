import datetime
import json
from unittest import TestCase, mock

import ddt
import requests
import responses
from edx_django_utils.cache import TieredCache
from freezegun import freeze_time

from edx_rest_api_client import __version__
from edx_rest_api_client.client import (OAuthAPIClient, get_and_cache_oauth_access_token,
                                        get_oauth_access_token)
from edx_rest_api_client.tests.mixins import AuthenticationTestMixin

URL = 'http://example.com/api/v2'
OAUTH_URL = "http://test-auth.com/oauth2/access_token"
OAUTH_URL_2 = "http://test-auth.com/edx/oauth2/access_token"
SIGNING_KEY = 'edx'
USERNAME = 'edx'
FULL_NAME = 'édx äpp'
EMAIL = 'edx@example.com'
TRACKING_CONTEXT = {'foo': 'bar'}
ACCESS_TOKEN = 'abc123'
JWT = 'abc.123.doremi'


@ddt.ddt
class ClientCredentialTests(AuthenticationTestMixin, TestCase):
    """
    Test client credentials requests.
    """

    def test_refresh_token_required(self):
        self._mock_auth_api(OAUTH_URL, 200, body=None)
        with self.assertRaises(AssertionError):
            get_oauth_access_token(OAUTH_URL, 'client_id', 'client_secret', grant_type='refresh_token')


class CachedClientCredentialTests(AuthenticationTestMixin, TestCase):
    """
    Test cached client credentials requests.
    """

    def setUp(self):
        super().setUp()
        TieredCache.dangerous_clear_all_tiers()

    @responses.activate
    def test_token_caching(self):
        """
        Test that tokens are cached based on client, token_type, and grant_type
        """
        tokens = [
            'auth2-cred4', 'auth2-cred3', 'auth2-cred2', 'auth2-cred1',
            'auth1-cred4', 'auth1-cred3', 'auth1-cred2', 'auth1-cred1',
        ]

        def auth_callback(request):   # pylint: disable=unused-argument
            resp = {'expires_in': 60}
            resp['access_token'] = 'no-more-credentials' if not tokens else tokens.pop()
            return (200, {}, json.dumps(resp))

        responses.add_callback(responses.POST, OAUTH_URL, callback=auth_callback, content_type='application/json')
        responses.add_callback(responses.POST, OAUTH_URL_2, callback=auth_callback, content_type='application/json')

        kwargs_list = [
            {'client_id': 'test-id-1', 'token_type': "jwt", 'grant_type': 'client_credentials'},
            {'client_id': 'test-id-2', 'token_type': "jwt", 'grant_type': 'client_credentials'},
            {'client_id': 'test-id-1', 'token_type': "bearer", 'grant_type': 'client_credentials'},
            {'client_id': 'test-id-1', 'token_type': "jwt", 'grant_type': 'refresh_token'},
        ]

        # initial requests to OAUTH_URL should call the mock client and get the correct credentials
        for index, kwargs in enumerate(kwargs_list):
            token_response = self._get_and_cache_oauth_access_token(OAUTH_URL, **kwargs)
            expected_token = 'auth1-cred{}'.format(index + 1)
            self.assertEqual(token_response[0], expected_token)
        self.assertEqual(len(responses.calls), 4)

        # initial requests to OAUTH_URL_2 should call the mock client and get the correct credentials
        for index, kwargs in enumerate(kwargs_list):
            token_response = self._get_and_cache_oauth_access_token(OAUTH_URL_2, **kwargs)
            expected_token = 'auth2-cred{}'.format(index + 1)
            self.assertEqual(token_response[0], expected_token)
        self.assertEqual(len(responses.calls), 8)

        # second set of requests to OAUTH_URL should return the same credentials without making any new mock calls
        for index, kwargs in enumerate(kwargs_list):
            token_response = self._get_and_cache_oauth_access_token(OAUTH_URL, **kwargs)
            expected_token = 'auth1-cred{}'.format(index + 1)
            self.assertEqual(token_response[0], expected_token)
        self.assertEqual(len(responses.calls), 8)

        # second set of requests to OAUTH_URL_2 should return the same credentials without making any new mock calls
        for index, kwargs in enumerate(kwargs_list):
            token_response = self._get_and_cache_oauth_access_token(OAUTH_URL_2, **kwargs)
            expected_token = 'auth2-cred{}'.format(index + 1)
            self.assertEqual(token_response[0], expected_token)
        self.assertEqual(len(responses.calls), 8)

    def _get_and_cache_oauth_access_token(self, auth_url, client_id, token_type, grant_type):
        refresh_token = 'test-refresh-token' if grant_type == 'refresh_token' else None
        return get_and_cache_oauth_access_token(
            auth_url, client_id, 'test-secret', token_type=token_type, grant_type=grant_type,
            refresh_token=refresh_token,
        )


@ddt.ddt
class OAuthAPIClientTests(AuthenticationTestMixin, TestCase):
    """
    Tests for OAuthAPIClient
    """
    base_url = 'http://testing.test'
    client_id = 'test'
    client_secret = 'secret'

    def setUp(self):
        super().setUp()
        TieredCache.dangerous_clear_all_tiers()

    @responses.activate
    @ddt.data(
        ('http://testing.test', None, 'http://testing.test/oauth2/access_token'),
        ('http://testing.test', '/edx', 'http://testing.test/edx/oauth2/access_token'),
        ('http://testing.test', '/edx/oauth2', 'http://testing.test/edx/oauth2/access_token'),
        ('http://testing.test', '/edx/oauth2/access_token', 'http://testing.test/edx/oauth2/access_token'),
        ('http://testing.test/oauth2', None, 'http://testing.test/oauth2/access_token'),
        ('http://testing.test/test', '/edx/oauth2/access_token', 'http://testing.test/test/edx/oauth2/access_token'),
    )
    @ddt.unpack
    def test_automatic_auth(self, client_base_url, custom_oauth_uri, expected_oauth_url):
        """
        Test that the JWT token is automatically set
        """
        client_session = OAuthAPIClient(client_base_url, self.client_id, self.client_secret)
        client_session.oauth_uri = custom_oauth_uri

        self._mock_auth_api(expected_oauth_url, 200, {'access_token': 'abcd', 'expires_in': 60})
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
        first_call_datetime = datetime.datetime.utcnow()
        self.assertEqual(client_session.auth.token, 'cred1')
        self.assertEqual(response.json()['status'], 'ok')
        # after only 30 seconds should still use the cached token
        with freeze_time(first_call_datetime + datetime.timedelta(seconds=30)):
            response = client_session.post(self.base_url + '/endpoint', data={'test': 'ok'})
            self.assertEqual(client_session.auth.token, 'cred1')
        # after just under a minute, should request a new token
        # - expires early due to ACCESS_TOKEN_EXPIRED_THRESHOLD_SECONDS
        with freeze_time(first_call_datetime + datetime.timedelta(seconds=56)):
            response = client_session.post(self.base_url + '/endpoint', data={'test': 'ok'})
            self.assertEqual(client_session.auth.token, 'cred2')

    @mock.patch('edx_rest_api_client.client.requests.post')
    def test_access_token_request_timeout_wiring2(self, mock_access_token_post):
        mock_access_token_post.return_value.json.return_value = {'access_token': 'token', 'expires_in': 1000}

        timeout_override = (6.1, 2)
        client = OAuthAPIClient(self.base_url, self.client_id, self.client_secret, timeout=timeout_override)
        client._ensure_authentication()  # pylint: disable=protected-access

        assert mock_access_token_post.call_args.kwargs['timeout'] == timeout_override

    @responses.activate
    def test_access_token_invalid_json_response(self):
        responses.add(responses.POST,
                      self.base_url + '/oauth2/access_token',
                      status=200,
                      body="Not JSON")
        client = OAuthAPIClient(self.base_url, self.client_id, self.client_secret)

        with self.assertRaises(requests.RequestException):
            client._ensure_authentication()  # pylint: disable=protected-access

    @responses.activate
    def test_access_token_bad_response_code(self):
        responses.add(responses.POST,
                      self.base_url + '/oauth2/access_token',
                      status=500,
                      json={})
        client = OAuthAPIClient(self.base_url, self.client_id, self.client_secret)
        with self.assertRaises(requests.HTTPError):
            client._ensure_authentication()  # pylint: disable=protected-access

    @responses.activate
    def test_get_jwt_access_token(self):
        token = 'abcd'
        self._mock_auth_api(self.base_url + '/oauth2/access_token', 200, {'access_token': token, 'expires_in': 60})
        client = OAuthAPIClient(self.base_url, self.client_id, self.client_secret)
        access_token = client.get_jwt_access_token()
        self.assertEqual(access_token, token)

    @responses.activate
    @mock.patch('crum.get_current_request')
    def test_request_id_forwarding(self, mock_crum_get_current_request):
        request_id = 'a-fake-request-id'
        mock_request = mock.MagicMock()
        mock_request.headers.get.return_value = request_id
        mock_crum_get_current_request.return_value = mock_request
        token = 'abcd'
        self._mock_auth_api(self.base_url + '/oauth2/access_token', 200, {'access_token': token, 'expires_in': 60})
        client = OAuthAPIClient(self.base_url, self.client_id, self.client_secret)
        post_url = self.base_url + '/oauth2/access_token'
        responses.add(responses.POST,
                      post_url,
                      status=200,
                      json={})
        response = client.post(post_url, data={'test': 'ok'})
        assert response.request.headers.get('X-Request-ID') == request_id

    @responses.activate
    @mock.patch('crum.get_current_request')
    def test_request_id_forwarding_no_id(self, mock_crum_get_current_request):
        mock_request = mock.MagicMock()
        mock_request.headers.get.return_value = None
        mock_crum_get_current_request.return_value = mock_request
        token = 'abcd'
        self._mock_auth_api(self.base_url + '/oauth2/access_token', 200, {'access_token': token, 'expires_in': 60})
        client = OAuthAPIClient(self.base_url, self.client_id, self.client_secret)
        post_url = self.base_url + '/oauth2/access_token'
        responses.add(responses.POST,
                      post_url,
                      status=200,
                      json={})
        response = client.post(post_url, data={'test': 'ok'})
        assert response.request.headers.get('X-Request-ID') is None

    @responses.activate
    @mock.patch('crum.get_current_request')
    def test_request_id_forwarding_no_request(self, mock_crum_get_current_request):
        mock_crum_get_current_request.return_value = None
        token = 'abcd'
        self._mock_auth_api(self.base_url + '/oauth2/access_token', 200, {'access_token': token, 'expires_in': 60})
        client = OAuthAPIClient(self.base_url, self.client_id, self.client_secret)
        post_url = self.base_url + '/oauth2/access_token'
        responses.add(responses.POST,
                      post_url,
                      status=200,
                      json={})
        response = client.post(post_url, data={'test': 'ok'})
        assert response.request.headers.get('X-Request-ID') is None
