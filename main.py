import json
from datetime import datetime
import requests

import yandapi as ya

def load_cfg(filename='config.json'):
    with open(filename) as f:
        cfg = json.load(f)
    return cfg

def backup_photos(vk_id, vk_token, ya_token, quantity=5):
    ya_client = ya.YandexDiskAPIClient(ya_token)

    def progress_bar(n, width=50, file=''):
        percent = n / quantity
        filled = int(width * percent)
        bar = '*' * filled + '-' * (width - filled)
        print(f'\r[{bar}] {percent * 100:.2f}% {file}', end='')

    def get_profile_photos_info(token, user_id):
        base_url = "https://api.vk.com/method/"
        api_version = "5.131"
        params = {
            'access_token': token,
            'v': api_version,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': '1'
        }
        response = requests.get(base_url + 'photos.get', params=params)
        return response.json()

    def upload_photo(filename, data):
        ya_client.upload_file_by_url(data['url'], f'{filename}.jpg')

    n = 0
    photos_info = {}

    photo_info = get_profile_photos_info(vk_token, vk_id)
    photos = photo_info.get('response', {}).get('items', [])

    for photo in photos:
        photo_url = photo['sizes'][-1]['url']
        likes = photo.get('likes', {}).get('count', 0)
        photo_type = photo['sizes'][-1]['type']

        if likes in photos_info:
            if 'date' not in photos_info[likes]:
                photos_info[likes]['date'] = photo['date']
        else:
            photos_info[likes] = {'url': photo_url, 'type': photo_type}
            if 'date' not in photos_info[likes]:
                photos_info[likes]['date'] = photo['date']

        if likes in photos_info and len(photos_info) <= quantity:
            date_str = datetime.fromtimestamp(photos_info[likes]['date']).strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'backup_{vk_id}/{likes}-{date_str}.jpg'
            upload_photo(filename, photos_info[likes])
            progress_bar(n, file=filename)
            n += 1

    progress_bar(quantity)
    print()

    with open(f'backup_{vk_id}.json', 'w') as json_file:
        json.dump(photos_info, json_file, indent=2)

def user_input():
    vk_token = input("Введите токен ВК (Нажмите Enter если токен добавлен в config.json): ")
    if vk_token == "":
        vk_token = load_cfg()['vk_token']
    ya_token = input("Введите токен Яндекс (Нажмите Enter если токен добавлен в config.json): ")
    if ya_token == '':
        ya_token = load_cfg()['ya_token']

    user_id = input('Введите ID пользователя ВК: ').strip()
    while not user_id.isdigit():
        print("Ошибка! Введите числовой идентификатор пользователя.")
        user_id = input('Введите ID пользователя ВК: ').strip()

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

    backup_photos(user_id, vk_token, ya_token, quantity=quantity)

user_input()
