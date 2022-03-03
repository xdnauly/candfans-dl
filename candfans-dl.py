import shutil
import json
import os
import pathlib
import requests


class Candfans(object): # noqa
    URL = 'https://candfans.jp/api'
    CONTENT_URL = 'https://fanty-master-storage.s3.ap-northeast-1.amazonaws.com'
    sess = requests.Session()
    sub_dict = {}

    def __init__(self):
        assert pathlib.Path('auth.json').is_file()

        with open('auth.json') as f:
            ljson = json.load(f)

        self.sess.headers['X-Xsrf-Token'] = ljson['X-Xsrf-Token']
        self.sess.headers['Cookie'] = ljson['Cookie']
        self.sess.headers['User-Agent'] = ljson['User-Agent']

        self.sess.headers['Accept'] = 'application/json, text/plain, */*'
        self.sess.headers['Referer'] = 'https://candfans.jp/'

    # shorten
    def get(self, path: str, params: dict | None = None) -> requests.Response:
        return self.sess.get(f'{self.URL}{path}', params=params)

    # shorten
    def post(self, path: str, data: dict = None) -> requests.Response:
        return self.sess.post(f'{self.URL}/{path}', data=data)

    # get user's id
    def get_user_id(self) -> int:
        user_info = self.get('/user/get-user-mine').json()

        return user_info['data']['users'][0]['id']

    # get user's all subscriptions
    def get_subscriptions(self, user_id: int) -> dict:

        return self.get(f'/user/get-follow/{user_id}').json()['data']

    # chose model to download
    def select_subscription(self) -> None:
        user_id = self.get_user_id()
        subs = self.get_subscriptions(user_id)

        if len(subs) == 0:
            print('No models subbed')
            exit()

        all_models = {}
        print('0 | *** Download All Models ***')
        for i, sub in enumerate(subs):
            print(f'{i + 1} | {sub["username"]}')
            all_models.update({str(i + 1): sub['user_id']})

        model = str(input('\nEnter number to download model: '))

        result = []
        if model == '0':
            result.extend(all_models.values())
        elif model in all_models:
            result.append(all_models.get(model))
        else:
            exit()

        for profile_id in result:
            PROFILE = subs[int(model) - 1]['username'] # noqa
            self.assure_dir("profiles")
            self.assure_dir("profiles/" + PROFILE)
            self.assure_dir("profiles/" + PROFILE + "/photos")
            self.assure_dir("profiles/" + PROFILE + "/videos")
            print(f'\nYou are downloading {PROFILE}\'s photos and videos')
            print()
            self.get_all_photos(profile_id)

    def get_all_photos(self, user_id: int):
        has_more_page = True
        page = 0
        while has_more_page:
            photos = self.get('/contents/get-timeline',
                              params={'user_id': user_id,
                                      'page': page
                                      }).json()['data']

            # begin download photos
            for photo in photos:
                if not photo['can_browsing'] == 0:
                    username = photo['username']
                    for content_path in self.get_content_paths(photo):
                        path = content_path.split('/')[-1]
                        if not os.path.isfile(f'profiles/{username}/photos/{path}'):
                            self.download_file(source=self.photo_url(content_path), profile=username, path=path)

            if len(photos) == 0:
                has_more_page = False

            page += 1

    def photo_url(self, content_path: str) -> str:
        return self.CONTENT_URL + content_path

    @staticmethod
    def download_file(source: str, profile: str, path: str) -> None:
        print(f'{profile} | {path}')
        r = requests.get(source, stream=True)

        with open(f'profiles/{profile}/photos/{path}', 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    @staticmethod
    def get_content_paths(model_post: dict) -> list[str]:
        content_path = [
            model_post['contents_path1'],
            model_post['contents_path2'],
            model_post['contents_path3'],
            model_post['contents_path4'],
        ]

        return [_ for _ in content_path if _ != '']

    @staticmethod
    def assure_dir(path: str) -> None:
        if not os.path.isdir(path):
            os.mkdir(path)

    def dl(self):
        self.select_subscription()


Candfans().dl()
