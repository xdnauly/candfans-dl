import functools
import itertools
import math
import json
import pathlib
import httpx
import re
import asyncio
import datetime as dt
from tqdm import tqdm

from typing import Any, Dict, List, Set, Tuple
from pydantic import BaseModel


# DO NOT CHANGE 
URL = 'https://candfans.jp/api'
CONTENT_URL = 'https://fanty-master-storage.s3.ap-northeast-1.amazonaws.com'
# do not change
PROFILE = ''
FILES: Set[str] = set()
DOWNLOAD_TASKS: List[Any] = []

ILLEGAL_FILENAME_CHARS = ['\\', ':', '/', ':', '?', '*', '"', '<', '>', '|']
                
# asyncio limit
URL_LIMIT = 4

# Your user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"

# 
class User(BaseModel):
    user_id: str
    user_code: str
    username: str

@functools.cache
def create_header() -> Dict[str, str]:
    with open('auth.json') as f:
        ljson = json.load(f)

    return {
        'Cookie': ljson['Cookie'],
        'X-Xsrf-Token': ljson['X-Xsrf-Token'],
        'User-Agent': USER_AGENT,
        'referer': 'https://candfans.jp/'
    }


# https://candfans.jp/api/user/get-user-mine
def get_user_mine() -> Tuple[int, str]:
    user_data = httpx.get(url=f'{URL}/user/get-user-mine',
                          headers=create_header()
                          ).json()['data']['users'][0]
    
    return user_data['id'], user_data['user_code']

# https://candfans.jp/api/user/get-users?user_code={user_code}
def get_user(user_code: str) -> Dict:
    return httpx.get(url=f'{URL}/user/get-users?user_code={user_code}',
                     headers=create_header()
                     ).json()['data']['user']

def get_subscriptions(userinfo: Tuple[int, str]) -> List[Dict[str, Any]]:
    user_id, user_code = userinfo
    
    follow_cnt: int = get_user(user_code)['follow_cnt']
    
    subscriptions: List[Dict[str, Any]] = []
    for i in range(1, math.ceil(follow_cnt / 10) + 1):
        # https://candfans.jp/api/user/get-follow/{user_id}?page={i}
        sub = httpx.get(url=f'{URL}/user/get-follow/{user_id}',
                                 headers=create_header(),
                                 params={
                                     'page': i,
                                 }
                                 ).json()['data']

        subscriptions.extend(sub)
    
    return subscriptions


def select_subscription() -> None:
    user_info = get_user_mine()
    subs = get_subscriptions(user_info)

    if len(subs) == 0:
        print('No models subbed')
        exit()

    all_models: Dict[str, User] = {}
    # TODO fix enter 0 download all.
    print('0  |  *** Download all ***')
    for i, sub in enumerate(subs):
        print(f'{i + 1}  |  {sub["username"]}')
        all_models.update({str(i + 1): User(**sub)})
    print('q |  quit')

    model = str(input('\nEnter number to download model: '))
    selected_models: List[User] = []
    # all selected
    if model == '0':
        selected_models.extend(all_models.values())
    # single selected
    elif user := all_models.get(model):
        selected_models.append(user)
    # group selected
    elif re.match('(?:\d+,)+\d+', model):
        for m in model.split(','):
            if u := all_models.get(m.strip()):
                selected_models.append(u)
    # quit
    elif model == 'q':
        print('quit')
        exit()
    else:
        raise ValueError(f'The {model} is not correct number.')

    for user in selected_models:
        global PROFILE
        PROFILE = user.username
        user_code = user.user_code
        user_id = user.user_id
        
        # remove illegal char
        if any([ch in PROFILE for ch in ILLEGAL_FILENAME_CHARS]):
            new_profile = []
            for c in PROFILE:
                if c not in ILLEGAL_FILENAME_CHARS:
                    new_profile.append(c)
            PROFILE = ''.join(new_profile)
        
        assure_dir("profiles")
        assure_dir("profiles/" + PROFILE)
        assure_dir("profiles/" + PROFILE + '/info')
        assure_dir("profiles/" + PROFILE + '/photos')
        assure_dir("profiles/" + PROFILE + '/videos')
        print(f'\nYou are downloading {PROFILE}\'s photos and videos\n')
        
        userinfo: Dict[str, Any] = get_user(user_code)
        info = {
            'profile_text': userinfo['profile_text'],
            'username': userinfo['username'],
            'user_code': userinfo['user_code'],
            'id': userinfo['id'],
            'image_cnt': userinfo['image_cnt'],
            'movie_cnt': userinfo['movie_cnt'],
            'post_cnt': userinfo['post_cnt'],
            'follow_cnt': userinfo['follow_cnt'],
            'like_cnt': userinfo['like_cnt'],
        }
        with open("profiles/" + PROFILE + '/info/' + 'info.json', 'w') as f:
            json.dump(info, f)
        
        img_urls = [
            userinfo['apeal_img1'],
            userinfo['apeal_img2'],
            userinfo['apeal_img2'],
            userinfo['profile_cover_img'],
            userinfo['profile_img'],
        ]
        tasks = []
        for img_url in img_urls:
            if img_url != '':
                file_name = img_url.split('/')[-1]
                tasks.append(async_download_file(f'{CONTENT_URL}{img_url}', file_name, 'info'))
        asyncio.run(async_download(tasks))

        global FILES
        FILES.clear()
        for file in itertools.chain(pathlib.Path("profiles/" + PROFILE + '/photos').iterdir(),
                                    pathlib.Path("profiles/" + PROFILE + '/videos').iterdir(),
                                    ):
            FILES.add(file.name)

        print(f'Staring  at {dt.datetime.now()}')

        new, total = get_all_photos(user_id, user_code)
        
        print(f'Finishing at {dt.datetime.now()}')
        print(f'Download new {new} files, {total - new} exists')
        
def get_all_photos(user_id: str, user_code: str) -> Tuple[int, int]:
    post_cnt: int = get_user(user_code)['post_cnt']
    
    count = 0
    with tqdm(total=post_cnt, unit='posts', desc='posts') as pbar:
        for i in range(1, math.ceil(post_cnt / 20) + 1):
            posts = httpx.get(url=f'{URL}/contents/get-timeline',
                            headers=create_header(),
                            params={'user_id': user_id,
                                    'page': i
                                    }).json()['data']

            for post in posts:
                pbar.update(1)
                # 1: you can | 0: you can't
                if post['can_browsing'] == 0:
                    continue
                
                for content_path in get_content_paths(post):
                    # /user/{user_id}/profile_cover/{filename}.jpg
                    file_name = content_path.split('/')[-1]
                    if file_name in FILES:
                        pass
                    elif len(DOWNLOAD_TASKS) < 5:
                        DOWNLOAD_TASKS.append(async_download_file(
                            source=f'{CONTENT_URL}{content_path}',
                            file_name=file_name,
                            filetype='photos' if is_picture(file_name) else 'videos'
                        ))
                        count += 1
                    else:
                        asyncio.run(async_download(DOWNLOAD_TASKS.copy()))
                        DOWNLOAD_TASKS.clear()

        # finish rest 
        if len(DOWNLOAD_TASKS) > 0:
            asyncio.run(async_download(DOWNLOAD_TASKS))
            DOWNLOAD_TASKS.clear()
    return count, post_cnt
    
# TODO this code is ugly
async def async_download(lst: list):
    await asyncio.gather(*lst)

def assure_dir(path: str) -> None:
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir()

async def async_download_file(source: str, file_name: str, filetype: str):
    with open("profiles/" + PROFILE + f'/{filetype}/' + file_name, 'wb') as f:
        async with httpx.AsyncClient(timeout=None,) as client:
            async with client.stream('GET',
                                     source,
                                     headers={
                                         'User-Agent': USER_AGENT,
                                         'Accept-Encoding': 'gzip, deflate, br'
                                     }) as r:
                async for chunk in r.aiter_bytes():
                    f.write(chunk)

def is_picture(file_name: str) -> bool:
    suffixes = ['jpg', 'png', 'jpeg', 'gif', 'webp', 'cr2', 'tif', 'bmp', 'jxr', 'psd', 'ico']
    
    for suffix in suffixes:
        if file_name.endswith(suffix):
            return True
    
    return False

def get_content_paths(post: Dict) -> List[str]:
    paths = [
        post['contents_path1'],
        post['contents_path2'],
        post['contents_path3'],
        post['contents_path4'],
    ]
    
    return [path for path in paths if path != '']

if __name__ == '__main__':
    select_subscription()
