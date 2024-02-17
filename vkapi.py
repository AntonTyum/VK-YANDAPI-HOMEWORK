import requests


def test_function():
    print('vk test function')


class VKAPIClient:
    api_base_url = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def _build_url(self, method):
        return f'{self.api_base_url}/{method}'

    def get_params(self):
        return {
            'access_token': self.token,
            'v': '5.199'
        }

    def get_proile_photos_info(self):
        params = self.get_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile'})
        response = requests.get(self._build_url('photos.get'), params=params)
        return response.json()

    def get_likes_count(self, photo_id):
        params = self.get_params()
        params.update({'type': 'photo', 'owner_id': self.user_id, 'item_id': photo_id})
        response = requests.get(self._build_url('likes.getList'), params=params)
        return response.json().get('response', {}).get('count', 0)