from clients.movies_api import MoviesAPI
from clients.auth_api import AuthAPI
from clients.user_api import UserApi


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.movies_api = MoviesAPI(session)
        self.user_api = UserApi(session)

    def close_session(self):
        self.session.close()
