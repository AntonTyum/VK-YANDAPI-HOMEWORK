import json
from datetime import datetime
from pprint import pprint

import requests

import vkapi as vk
import yandapi as ya

def load_cfg(filename='config.json'):
    with open(filename) as f:
        cfg = json.load(f)
    return cfg

vk_token = input("Введите токен ВК (Нажмите Enter если токен добавлен в config.json): ")
if vk_token == "":
    vk_token = load_cfg()['vk_token']
ya_token = input("Введите токен Яндекс (Нажмите Enter если токен добавлен в config.json): ")
if ya_token == '':
    ya_token = load_cfg()['ya_token']

user_id = input('Введите ID пользователя ВК :').strip()
while not user_id.isdigit():
    print("Ошибка! Введите числовой идентификатор пользователя.")
    user_id = input('Введите ID пользователя ВК :').strip()

class VKAPIClient:
    def get_proile_photos_info(self):
        params = {
            'access_token': self.token,
            'v': self.api_version,
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': '1'
        }
        response = requests.get(self.base_url + 'photos.get', params=params)
        return response.json()

vk_client = vk.VKAPIClient(vk_token, user_id)
ya_client = ya.YandexDiskAPIClient(ya_token)
photos_info = {}

def get_photo_url_n_likes(quantity=5):
    photo_info = vk_client.get_proile_photos_info()
    photos = photo_info.get('response', {}).get('items', [])
    for photo in photos:
        photo_url = photo['sizes'][-1]['url']
        likes = photo.get('likes', {}).get('count', 0)
        date = photo['date']
        photo_type = photo['sizes'][-1]['type']
        photos_info[likes] = {'url': photo_url, 'date': date, 'type': photo_type}
    return photos_info

def backup_photos(vk_id, quantity=5):
    def progress_bar(n, width=50, file=''):
        percent = n / quantity
        filled = int(width * percent)
        bar = '*' * filled + '-' * (width - filled)
        print(f'\r[{bar}] {percent * 100:.2f}% {file}', end='')

    def upload_photo(filename, data):
        ya_client.upload_file_by_url(data['url'], f'{filename}.jpg')

    url_and_likes = get_photo_url_n_likes(quantity)

    n = 0
    progress_bar(n)
    for likes, data in url_and_likes.items():
        date = datetime.fromtimestamp(data['date']).strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'backup_{vk_id}/{likes}-{date}'
        upload_photo(filename, data)
        progress_bar(n, file=f'{filename}.jpg')
        n += 1

    progress_bar(quantity)
    print()
    pprint(photos_info)
    with open(f'backup_{vk_id}.json', 'w') as json_file:
        json.dump(photos_info, json_file)

def user_input():
    while True:
        quantity_input = input("Введите количество фотографий для загрузки: ")
        if quantity_input.strip():
            try:
                quantity = int(quantity_input)
                break
            except ValueError:
                print("Ошибка! Введите целое число.")
        else:
            print("Ошибка! Введите количество фотографий.")

    backup_photos(user_id, quantity=quantity)

user_input()
