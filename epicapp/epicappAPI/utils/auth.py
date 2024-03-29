import jwt
from ..exceptions import UnauthenticatedError, InvalidTokenError, ExpiredTokenError
from django.http import HttpResponseBadRequest
from rest_framework.request import Request


def decode_token(token):
    if token is None:
        return None
    try:
        return jwt.decode(token, 'SECRET_NOT_USING_ENV_CAUSE_WHO_CARES', algorithms=['HS256'])
    except jwt.InvalidSignatureError:
        raise InvalidTokenError("Invalid token!")
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError("Expired token!")


def authenticated(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                token = arg.headers.get('Authorization')
                try:
                    if token:
                        arg._auth = decode_token(token)
                        return func(*args, **kwargs)
                    else:
                        return HttpResponseBadRequest(status=401)
                except (UnauthenticatedError, InvalidTokenError, ExpiredTokenError) as err:
                    return HttpResponseBadRequest(status=401)
        return HttpResponseBadRequest(status=599)
    return wrapper
