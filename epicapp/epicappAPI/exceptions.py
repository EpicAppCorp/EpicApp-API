class UnauthenticatedError(Exception):
    '''Raise when no JWT found in request header'''

class ExpiredTokenError(Exception):
    '''Raise when token is expired'''

class InvalidTokenError(Exception):
    '''Raise when cannot decode JWT'''
