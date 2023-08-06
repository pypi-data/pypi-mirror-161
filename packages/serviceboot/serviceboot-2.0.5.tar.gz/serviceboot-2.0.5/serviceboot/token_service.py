import python_jwt
from jwcrypto import jwk
import threading
from serviceboot.request_info import get_request_info


class Token:
    def __init__(self):
        self.is_valid = False
        self.jwt = None
        self.username = None
        self.roles = []

    def has_role(self, role):
        return role in self.roles


def get_token():
    token = Token()

    jwt = get_request_info().get('jwt')
    if jwt is None:
        return token
    token.jwt = jwt

    try:
        public_key = threading.main_thread().uaa_public_key
    except:
        return token

    try:
        jwt_decoded = python_jwt.verify_jwt(
            token.jwt,
            jwk.JWK.from_pem(public_key),
            ['RS256'],
            checks_optional=True,
            ignore_not_implemented=True
        )
        claims = jwt_decoded[1]
        token.username = claims.get('user_name') or claims.get('client_id')
        token.roles = claims.get('authorities') or []
        token.is_valid = True
    except Exception as e:
        token.is_valid = False
        token.jwt = None
        token.username = None
        token.roles = []

    return token
