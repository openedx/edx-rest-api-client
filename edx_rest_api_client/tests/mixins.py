""" Test mixins """
import json

import httpretty


class AuthenticationTestMixin(object):
    """ Mixin for testing authentication. """

    def _mock_auth_api(self, url, status, body=None):
        self.assertTrue(httpretty.is_enabled(), 'httpretty must be enabled to mock authentication API calls.')

        body = body or {}
        httpretty.register_uri(
            httpretty.POST,
            url,
            status=status,
            body=json.dumps(body),
            content_type='application/json'
        )
