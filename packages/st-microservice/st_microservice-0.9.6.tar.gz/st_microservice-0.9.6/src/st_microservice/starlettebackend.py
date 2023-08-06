from typing import List, Optional
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from starlette.applications import Starlette
from starlette.routing import BaseRoute, Route
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import Response, JSONResponse

from .auth_utils import JWTAuthBackend, auth_error_handler


# Utilities
def get_required_env(var_name: str) -> str:
    var = getenv(var_name)
    if var is None:
        raise EnvironmentError(f'Could not get {var_name} from ENV')
    return var


def hasenv(var_name: str) -> bool:
    return getenv(var_name, False) is not False


# Database
class DBMiddleware(BaseHTTPMiddleware):
    """ Will start a DB Session at every request and commit or rollback in the end """
    def __init__(self, app, session_class):
        super().__init__(app)
        self.session_class = session_class

    async def dispatch(self, request, call_next) -> Response:
        session = self.session_class()
        request.state.dbsession = session

        # Continue with request
        response = await call_next(request)

        try:  # Try to commit
            session.commit()
            return response
        except SQLAlchemyError:
            session.rollback()
            return JSONResponse({'errors': 'Error while commiting to Database'}, status_code=500)
        finally:
            session.close()


def get_dbsessionclass(database_uri: str, database_args: Optional[dict]):
    """ Helper function to be able to get the Session class outside of the DBMiddleware """
    if database_args is None:
        database_args = {}
    if 'connect_timeout' not in database_args:
        database_args['connect_timeout'] = 5
    engine = create_engine(database_uri, connect_args=database_args)
    return sessionmaker(bind=engine)


def get_user(request) -> JSONResponse:
    """ Get user route """
    return JSONResponse(request.user.to_json() if request.user.is_authenticated else None)


# App factory
def create_app(routes: List[BaseRoute], secret: str, root_domain: str, database_uri: str, debug=False, database_ssl=False) -> Starlette:
    authbackend = JWTAuthBackend(secret)

    # Allow origins from both HTTP or HTTPS, root or subdomains, any port
    root_domain_re = r'https?://(.*\.)?{}(:\d*)?'.format(root_domain.replace('.', r'\.'))
    print('Allowed Origins Regex:', root_domain_re)

    database_args = {'sslmode': 'require'} if database_ssl else None

    middleware = [
        Middleware(CORSMiddleware, allow_origin_regex=root_domain_re, allow_credentials=True, allow_methods=['*']),
        Middleware(DBMiddleware, session_class=get_dbsessionclass(database_uri, database_args)),
        Middleware(AuthenticationMiddleware, backend=authbackend, on_error=auth_error_handler)
    ]

    app = Starlette(debug=debug, routes=routes+[Route('/getuser', get_user, methods=['GET'])], middleware=middleware)
    app.router.redirect_slashes = False
    return app
