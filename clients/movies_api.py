from constans import MOVIES_ENDPOINT
from custom_requester.custom_requester import CustomRequester

class MoviesAPI(CustomRequester):
    # def __init__(self, session):
    #     super().__init__(session=session, base_url='https://api.dev-cinescope.coconutqa.ru')

    MOVIE_BASE_URL = "https://api.dev-cinescope.coconutqa.ru"

    def __init__(self, session):
        self.session = session
        super().__init__(session, self.MOVIE_BASE_URL)


    def create_movie(self, movie_data, expected_status=201):
        return self.send_request(
            method='POST',
            endpoint=MOVIES_ENDPOINT,
            json=movie_data,
            expected_status=expected_status
        )

    def get_movies(self, params=None, expected_status=200):
        return self.send_request(
            method='GET',
            endpoint=MOVIES_ENDPOINT,
            params=params,
            expected_status=expected_status
        )

    def get_movie(self, movie_id, expected_status=200):
        return self.send_request(
            method='GET',
            endpoint=f'{MOVIES_ENDPOINT}/{movie_id}',
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        return self.send_request(
            method='DELETE',
            endpoint=f'{MOVIES_ENDPOINT}/{movie_id}',
            expected_status=expected_status
        )

    def patch_movie(self, movie_id, movie_data, expected_status=200):
        return self.send_request(
            method='PATCH',
            endpoint=f'{MOVIES_ENDPOINT}/{movie_id}',
            json=movie_data,
            expected_status=expected_status
        )
