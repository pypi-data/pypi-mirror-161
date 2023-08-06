from typing import Dict, List, Any, Optional, Tuple
import jwt
from starlette.authentication import BaseUser, AuthenticationBackend, AuthenticationError, AuthCredentials
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse


class User(BaseUser):
    def __init__(self, user_id: str, display_name: str, scopes: List[str]):
        self.user_id = user_id
        self._display_name = display_name
        self.scopes = scopes

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def is_authenticated(self):
        return True

    @property
    def identity(self) -> str:
        return self.user_id

    def to_json(self) -> Dict[str, Any]:
        return {'user_id': self.user_id, 'display_name': self.display_name, 'scopes': self.scopes}


def get_token_from_header(authorization: str) -> str:
    try:
        scheme, token = authorization.split()
    except ValueError:
        raise AuthenticationError('Could not separate Authorization scheme and token')
    if scheme.lower() != 'bearer':
        raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
    return token


def get_user_from_token(token: str, secret: str) -> User:
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        user = User(payload['user_id'], payload['display_name'], payload['scopes'])
        return user
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f'JWT Token error: {e}')
    except Exception as e:
        raise AuthenticationError(f'Authentication error: {e}')


class JWTAuthBackend(AuthenticationBackend):
    def __init__(self, secret: str):
        self.secret = secret

    async def authenticate(self, request: HTTPConnection) -> Optional[Tuple[AuthCredentials, User]]:
        # Try to get token from header then from cookies
        auth_header = request.headers.get('Authorization', None)
        if auth_header is not None:
            token = get_token_from_header(auth_header)
        else:
            token = request.cookies.get('token')

        if token is None:
            return None

        user = get_user_from_token(token, self.secret)

        return AuthCredentials(user.scopes), user


def auth_error_handler(request, exc: Exception):
    response = JSONResponse({'error': str(exc)}, 400)
    response.delete_cookie('token')
    return response
