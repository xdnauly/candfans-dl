import json
import os
import pathlib
import requests
from utils import download_file, assure_dir

# do not change


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
    def get(self, path: str) -> requests.Response:
        return self.sess.get(f'{self.URL}{path}')

    # shorten
    def post(self, path: str, data: dict = None) -> requests.Response:
        return self.sess.post(f'{self.URL}/{path}', data=data)

    # get user's id
    def _get_user_id(self) -> int:

        user_info = self.get('/user/get-user-mine').json()

        return user_info['data']['users'][0]['id']

    # get user's all subscriptions
    def get_subscriptions(self, user_id: int) -> dict:

        return self.get(f'/user/get-follow/{user_id}').json()['data']

    # chose model to download
    def select_subscription(self) -> list:
        user_id = self._get_user_id()
        subs = self.get_subscriptions(user_id)

        if len(subs) == 0:
            print('No models subbed')
            exit()

        all_models = {}
        print('0 | *** Download All Models ***')
        for i, sub in enumerate(subs):
            print(f'{i + 1} | {sub["username"]}')
            all_models.update({str(i + 1): sub['user_id']})

        model = str(input('Enter number to download model'))

        if model == '0':
            return list(all_models.values())
        elif model in all_models:
            return all_models.get(model)
        else:
            exit()

    def dl(self):
        self.select_subscription()


Candfans().dl()


#
#
#
#
#
#     def select_sub() -> list['str']:
#         """choice the account you want to download
#         """
#         SUBS = get_follow()
#         sub_dict.update({"0": "*** Download All Models ***"})
#         ALL_LIST = []
#
#         for i in range(1, len(SUBS) + 1):
#             ALL_LIST.append(i)
#
#         for i in range(0, len(SUBS)):
#             sub_dict.update({i + 1: SUBS[i]['username']})
#             sub_userid_dict.update({i + 1: SUBS[i]['user_id']})
#
#         if len(sub_dict) == 1:
#             print('No models subbed')
#             exit()
#
#         MODELS = str((input('\n'.join(
#             '{} | {}'.format(key, value) for key, value in sub_dict.items()) + "\nEnter number to download model\n")))
#
#         if MODELS == '0':
#             return ALL_LIST
#         else:
#             return [x.strip() for x in MODELS.split(',')]
#
#
# def get_all_photos(user_id: str):
#     has_more_page = True
#     page = 0
#     while has_more_page:
#         photos = api_request('/contents/get-timeline',
#                              getparams={
#                                  'user_id': user_id,
#                                  'page': page
#                              },
#                              ).json()['data']
#
#         # begin download photos
#         for photo in photos:
#             # skip the unaviable img
#             if not photo['can_browsing'] == 0:
#                 username = photo['username']
#                 for content_path in get_content_paths(photo):
#                     path = content_path.split('/')[-1]
#                     if not os.path.isfile(f'profiles/{username}/photos/{path}'):
#                         download_file(source=get_photo_url(content_path), profile=username, path=path)
#
#         if len(photos) == 0:
#             has_more_page = False
#
#         page += 1
#
#
# if __name__ == '__main__':
#     print('\n')
#
#     sub_dict = {}
#     sub_userid_dict = {}
#
#     SELECTED_MODELS = select_sub()
#
#     for M in SELECTED_MODELS:
#         PROFILE_ID = str(sub_userid_dict[int(M)])
#         PROFILE = str(sub_dict[int(M)])
#
#         # print('\ncandfans-dl is downloading content to profiles/' + PROFILE + '!\n')
#
#         if os.path.isdir('profiles/' + PROFILE):
#             print("\nThe folder profiles/" + PROFILE + " exists.")
#             print("Media already present will not be re-downloaded.")
#
#         assure_dir("profiles")
#         assure_dir("profiles/" + PROFILE)
#         assure_dir("profiles/" + PROFILE + "/photos")
#         assure_dir("profiles/" + PROFILE + "/videos")
#         print("Saving profile info...")
#         get_all_photos(PROFILE_ID)
