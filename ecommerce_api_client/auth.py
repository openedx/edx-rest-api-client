import jwt
from requests.auth import AuthBase


class JwtAuth(AuthBase):
    """Attaches JWT Authentication to the given Request object."""

    def __init__(self, username, email, signing_key):
        self.username = username
        self.email = email
        self.signing_key = signing_key

    def __call__(self, r):
        data = {
            'username': self.username,
            'email': self.email
        }

        r.headers['Authorization'] = 'JWT ' + jwt.encode(data, self.signing_key)
        return r
