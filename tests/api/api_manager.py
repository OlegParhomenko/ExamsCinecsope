from .movies_api import MoviesAPI
from .auth_api import AuthAPI

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.movies_api = MoviesAPI(session)