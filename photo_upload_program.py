import requests
import os
import json
import configparser
import time
from tqdm import tqdm

config = configparser.ConfigParser()
config.read("settings.ini")

TOKEN_VK = config['vk_api']['access_token']
TOKEN_YADISK = config['yadisk_api']['api_token']


class UserService:

    def __init__(self, user_id, token: str):
        self.user_id = user_id
        self.token = token
        self.api_version = config['vk_api']['api_version']
        self.get_photos_method_url = config['vk_api']['get_photos_method_url']
        self.download_file_path = config['files_path']['download_file_path']
        self.get_upload_url_api = config['yadisk_api']['get_upload_url_api']
        self.file_path = config['files_path']['download_file_path']
        self.mkdir_url = config['yadisk_api']['mkdir_url']

    def _get_photos_from_folder(self) -> list:
        file_list = os.listdir(self.file_path)
        return file_list

    def get_photos_method(self, user_id):
        params = {'access_token': self.token,
                  'v': self.api_version,
                  'album_id': 'profile',
                  'owner_id': user_id,
                  'extended': True,
                  'photo_sizes': True
                  }
        response = requests.get(self.get_photos_method_url, params=params)
        profile_list = response.json()

        for file in tqdm(profile_list['response']['items']):
            time.sleep(3)
            self.size = file['sizes'][-1]['type']
            photo_url = file['sizes'][-1]['src']
            file_name = file['likes']['count']
            download_photo = requests.get(photo_url)
            with open(f'{self.download_file_path}/{file_name}.jpg', 'wb') as f:
                f.write(download_photo.content)

    def create_folder(self):
        # self.mkdir_path = mkdir_path
        params = {'path': self.file_path}
        headers = {'Content-Type': 'application/json',
                   'Authorization': TOKEN_YADISK}
        create_dir = requests.api.put(self.mkdir_url, headers=headers, params=params)

    def upload_photo(self):
        headers = {'Content-Type': 'application/json',
                   'Authorization': TOKEN_YADISK}
        logs_list = []

        for photo in tqdm(self._get_photos_from_folder()):
            time.sleep(3)
            params = {'path': f'{self.file_path}/{photo}'}
            get_upload_url = requests.get(self.get_upload_url_api, headers=headers, params=params)
            get_url = get_upload_url.json()
            upload_url = get_url['href']
            file_upload = requests.api.put(upload_url, data=open(f'{self.file_path}/{photo}', 'rb'), headers=headers)
            status = file_upload.status_code

            download_log = {'file_name': photo, 'size': self.size}
            logs_list.append(download_log)

        with open('files/log.json', 'a') as file:
            json.dump(logs_list, file, indent=2)

        if 500 > status != 400:
            print('Фотографии успешно загружены!')
        else:
            print('Ошибка, фотографии не загружены!')


if __name__ == '__main__':
    user1 = UserService(552934290, TOKEN_VK)
    save_photos = user1.get_photos_method(user1.user_id)
    user1.create_folder()
    back_up = user1.upload_photo()
