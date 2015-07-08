import datetime

import jwt
from requests.auth import AuthBase


class JwtAuth(AuthBase):
    """Attaches JWT Authentication to the given Request object."""

    def __init__(self, username, full_name, email, signing_key, issuer=None, expires_in=30, tracking_context=None):
        self.issuer = issuer
        self.expires_in = expires_in
        self.username = username
        self.email = email
        self.full_name = full_name
        self.signing_key = signing_key
        self.tracking_context = tracking_context

    def __call__(self, r):

        data = {
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
        }

        if self.issuer:
            data['iss'] = self.issuer

        if self.expires_in:
            data['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expires_in)

        if self.tracking_context is not None:
            data['tracking_context'] = self.tracking_context

        r.headers['Authorization'] = 'JWT ' + jwt.encode(data, self.signing_key)
        return r


class BearerAuth(AuthBase):
    """ Attaches Bearer Authentication to the given Request object. """

    def __init__(self, token):
        """ Instantiate the auth class. """
        self.token = token

    def __call__(self, r):
        """ Update the request headers. """
        r.headers['Authorization'] = 'Bearer {}'.format(self.token)
        return r
