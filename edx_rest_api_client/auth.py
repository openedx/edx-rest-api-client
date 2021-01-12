import datetime

import jwt
from edx_django_utils.monitoring import set_custom_attribute
from requests.auth import AuthBase


# pylint: disable=line-too-long
class JwtAuth(AuthBase):
    """
    Attaches JWT Authentication to the given Request object.

    Deprecated:
        See https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/oauth_dispatch/docs/decisions/0008-use-asymmetric-jwts.rst

    Note: Remove pyjwt dependency when this class is removed.

    """

    def __init__(self, username, full_name, email, signing_key, issuer=None, expires_in=30, tracking_context=None):
        self.issuer = issuer
        self.expires_in = expires_in
        self.username = username
        self.email = email
        self.full_name = full_name
        self.signing_key = signing_key
        self.tracking_context = tracking_context

    def __call__(self, r):
        now = datetime.datetime.utcnow()
        data = {
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'iat': now,
        }

        if self.issuer:
            data['iss'] = self.issuer

        if self.expires_in:
            data['exp'] = now + datetime.timedelta(seconds=self.expires_in)

        if self.tracking_context is not None:
            data['tracking_context'] = self.tracking_context

        set_custom_attribute('deprecated_jwt_signing', 'JwtAuth')
        r.headers['Authorization'] = 'JWT {jwt}'.format(jwt=jwt.encode(data, self.signing_key))
        return r


class SuppliedJwtAuth(AuthBase):
    """Attaches a supplied JWT to the given Request object."""

    def __init__(self, token):
        """Instantiate the auth class."""
        self.token = token

    def __call__(self, r):
        """Update the request headers."""
        r.headers['Authorization'] = f'JWT {self.token}'
        return r


class BearerAuth(AuthBase):
    """ Attaches Bearer Authentication to the given Request object. """

    def __init__(self, token):
        """ Instantiate the auth class. """
        self.token = token

    def __call__(self, r):
        """ Update the request headers. """
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r
