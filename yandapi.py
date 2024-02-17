import requests


def test_function():
    print('yad test function')


class YandexDiskAPIClient:
    base_url = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Authorization': self.token
        }

    def get_folder_info(self, folder_name):
        response = requests.get(f'{self.base_url}/resources', headers=self.get_headers(), params={'path': folder_name})
        return response.status_code

    def create_folder(self, folder_name):
        response = requests.put(f'{self.base_url}/resources', headers=self.get_headers(), params={'path': folder_name})
        if response.status_code == 409:
            print(f'Папка {folder_name} уже существует')
        elif response.status_code == 201:
            print(f'Папка {folder_name} создана')

    def upload_var(self, path, var):
        url_get_upload = f'{self.base_url}/resources/upload'
        url_for_upload = requests.get(url_get_upload, headers=self.get_headers(),
                                      params={'path': path, 'overwrite': 'true'}).json().get('href', '')
        requests.put(url_for_upload, headers=self.get_headers(), data=var)

    def upload_file_by_url(self, file_url, file_name: str):
        api_upload_url = f'{self.base_url}/resources/upload'
        self.folder_name = file_name.split('/')[0] if file_name.count('/') > 0 else None
        if self.folder_name:
            if self.get_folder_info(self.folder_name) == 404: self.create_folder(self.folder_name)
        response = requests.post(api_upload_url, headers=self.get_headers(),
                                 params={'path': file_name, 'url': file_url})
