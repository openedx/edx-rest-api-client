import jwt
from requests.auth import AuthBase


class JwtAuth(AuthBase):
    """Attaches JWT Authentication to the given Request object."""

    def __init__(self, username, email, signing_key, tracking_context=None):
        self.username = username
        self.email = email
        self.signing_key = signing_key
        self.tracking_context = tracking_context

    def __call__(self, r):
        data = {
            'username': self.username,
            'email': self.email,
        }

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
