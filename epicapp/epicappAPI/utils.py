import jwt
from .exceptions import UnauthenticatedError, InvalidTokenError, ExpiredTokenError

def decode_token(token):
    if token is None:
        raise UnauthenticatedError("Unauthenticated!")
    try:
        return jwt.decode(token, 'SECRET_NOT_USING_ENV_CAUSE_WHO_CARES', algorithms=['HS256'])
    except jwt.InvalidSignatureError:
        raise InvalidTokenError("Invalid token!")
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError("Expired token!")
