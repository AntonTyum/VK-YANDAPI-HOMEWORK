import json
from datetime import datetime
from pprint import pprint
import vkapi as vk
import yandapi as ya
import os

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


vk_client = vk.VKAPIClient(vk_token, user_id)
ya_client = ya.YandexDiskAPIClient(ya_token)
photos_info = []

def get_photo_url_n_likes(quantity=5):

    photo_info = vk_client.get_proile_photos_info()
    photos = photo_info.get('response', {})['items']
    photo_tuples = []
    likes_pool = []
    n = 0
    if len(photos) < quantity: quantity = len(photos)
    while n < quantity:
        photo_tuples.append((photos[n].get('sizes', [])[-1]['url'],
                             vk_client.get_likes_count(photos[n].get('id', 0)),
                             photos[n].get('date', 0),
                             photos[n].get('sizes', [])[-1]['type']))
        likes_pool.append(vk_client.get_likes_count(photos[n].get('id', 0)))
        n += 1
    uniq_likes_pool = set([i for i in likes_pool if likes_pool.count(i) > 1])
    return photo_tuples, uniq_likes_pool


def backup_photos(vk_id, quantity=5):
    def progress_bar(n, width=50, file=''):
        percent = n / quantity
        filled = int(width * percent)
        bar = '*' * filled + '-' * (width - filled)
        print(f'\r[{bar}] {percent * 100:.2f}% {file}', end='')

    def fill_json(filename, size):
        return {'filename': filename, 'size': size}

    def upload_photo(filename, type):
        ya_client.upload_file_by_url(url, f'{filename}.jpg')
        photos_info.append(fill_json(f'{filename}.jpg', type))

    def upload_json(filename, var):
        ya_client.upload_var(f'backup_{vk_id}/{filename}.json', json.dumps(var))

    url_and_likes, likes_pool = get_photo_url_n_likes(quantity)

    n = 0
    progress_bar(n)
    for url, likes, date, type in url_and_likes:
        if likes in likes_pool:
            date = datetime.fromtimestamp(date).strftime('%Y-%m-%d_%H-%M-%S')
            # print(date)
            filename = f'backup_{vk_id}/{likes}-{date}'
            upload_photo(filename, type)
        else:
            filename = f'backup_{vk_id}/{likes}'
            upload_photo(filename, type)
        progress_bar(n, file=f'{filename}.jpg')
        n += 1


    progress_bar(quantity)
    print()
    pprint(photos_info)
    upload_json(f'backup_{vk_id}', photos_info)

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

os.system('pip freeze > requirements.txt')
print("Список всех зависимостей успешно добавлен в requirements.txt.")
