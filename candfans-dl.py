import json
import os
import shutil
import sys
import requests

URL = 'https://candfans.jp/api'
CONTENT_URL = 'https://fanty-master-storage.s3.ap-northeast-1.amazonaws.com'

def assure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.mkdir(path)

def create_auth() -> dict:
    if os.path.isfile('auth.json')
    
    with open('auth.json') as f:
        ljson = json.load(f)
    
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        "Cookie": 'lang=ja; app_id=Kxgg5ffdAy56wP9ziXeVrBMyDoP4NAASOR2cOQqeksd95c0wJv; XSRF-TOKEN=eyJpdiI6IitMZnJuWmR1b3R4MEFXWVB4eGNTelE9PSIsInZhbHVlIjoidkNNVzZpcDA4TmJ1bmdmOFVyRjd1ZVNoa1Zlc0VrYzhqeGE3UG9PNytlUFBFcXpETTIxdlROVmsrN3lDaFdLcU1WYzNtRGhPSE1YdTNBYjRiZWRrUW1WKzhLcFRXY1hsT252dFltK3hTSlBLUDdCeUVUQkJKb1dRZmNmc1pEOEkiLCJtYWMiOiJlNjRjN2UzOWNmMmUzYjlmNGFlYWU4N2U1YzQ1OTEzNDE1NmY5MTUwMjFkMWY1NTc1NmMzZTU1MDg2M2ZiZTNlIiwidGFnIjoiIn0%3D; candfans_session=eyJpdiI6Ii9TWEpuNmZvK1JqRGJDa1VCNXBLMFE9PSIsInZhbHVlIjoiR2twS3E5UkFhUGR3bXpZMXd1djZoMWNMOHQzaDFxd0JqUU5jSWdVZ3Y3ZGNYUS9pV1F1citQRG42Q1BqMG5OYm4yRjkvbmY2Q1dxTy92VDZvaTU4S2oydW5BTGZTbjU5dGlvZnhmVFRDRHREL1o5YmxGVkZxSUQ4c2xBbHQwVUsiLCJtYWMiOiI1NzZkMDk4MmRiZjM3N2ExM2Y0ZTBlYTc0NTNkNWQyMTU4ZWYyZTVlNDNkZTBlM2Y1NGRjZmQyNzNhMTkzZTNhIiwidGFnIjoiIn0%3D',
        "Accept-Encoding": "gzip, deflate",
        'X-Xsrf-Token': 'eyJpdiI6IitMZnJuWmR1b3R4MEFXWVB4eGNTelE9PSIsInZhbHVlIjoidkNNVzZpcDA4TmJ1bmdmOFVyRjd1ZVNoa1Zlc0VrYzhqeGE3UG9PNytlUFBFcXpETTIxdlROVmsrN3lDaFdLcU1WYzNtRGhPSE1YdTNBYjRiZWRrUW1WKzhLcFRXY1hsT252dFltK3hTSlBLUDdCeUVUQkJKb1dRZmNmc1pEOEkiLCJtYWMiOiJlNjRjN2UzOWNmMmUzYjlmNGFlYWU4N2U1YzQ1OTEzNDE1NmY5MTUwMjFkMWY1NTc1NmMzZTU1MDg2M2ZiZTNlIiwidGFnIjoiIn0=',
    }
    

# get download url

def api_request(endpoint: str, getdata=None, postdata=None, getparams=None) -> requests.Response:

    headers = create_auth()
    
    return requests.get(URL + endpoint,
                        headers=header,
                        params=getparams,
                        )

# get all following people in json
def get_follow() -> dict:
    USER_ID = USERID
    
    return api_request('/user/get-follow/297518').json()['data']

def select_sub() -> list['str']:
    # Get Subscriptions
    SUBS = get_follow()
    
    sub_dict.update({"0": "*** Download All Models ***"})
    ALL_LIST = []
    
    for i in range(1, len(SUBS) + 1):
        ALL_LIST.append(i)
    
    for i in range(0, len(SUBS)):
        sub_dict.update({
            i+1: SUBS[i]['username']
        })
        
        sub_userid_dict.update({
            i+1: SUBS[i]['user_id']
        })
    
    if len(sub_dict) == 1:
        print('No models subbed')
        exit()
    
    if ARG1 == 'ALL':
        return ALL_LIST
    MODELS = str((input('\n'.join('{} | {}'.format(key, value) for key, value in sub_dict.items()) + "\nEnter number to download model\n")))
    
    if MODELS == '0':
        return ALL_LIST
    else:
        return [x.strip() for x in MODELS.split(',')]

def download_file(source: str, profile: str, path: str) -> None:
    r = requests.get(source, 
                     stream=True,
                     headers={
                         'User-Agent': ''
                     })

    with open(f'profiles/{profile}/{path}', 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

def get_photo_url(content_path: str) -> str:
    return CONTENT_URL + content_path

def get_content_paths(post: dict) -> list[str]:
    # 
    content_path = [
        post['contents_path1'],
        post['contents_path2'],
        post['contents_path3'],
        post['contents_path4'],
    ]
    
    return [_ for _ in content_path if content_path != '']

def get_all_photos(user_id: str):
    has_more_page = True
    page = 0
    while has_more_page:
        photos = api_request('/contents/get-timeline',
                    getparams={
                    'user_id': user_id,
                    'page': page
                },
        ).json()['data']
        
        # begin download photos 
        for photo in photos:
            # skip the unaviable img
            if photo['can_browsing'] == 0 or photo['contents_type'] != 1:
                continue
            
            username = photo['username']
            for content_path in get_content_paths(photo):
                path = content_path.split('/')[-1]
                download_file(source=get_photo_url(content_path), profile=username, path=path)
        
        if len(photos) == 0:
            has_more_page = False
        
        page += 1

if __name__ == '__main__':
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('hi,')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    
    # Gather inputs
    if len(sys.argv) != 2:
        ARG1 = ''
    else:
        ARG1 = sys.argv[1]
    
    sub_dict = {}
    sub_userid_dict = {}

    SELECTED_MODELS = select_sub()
    
    for M in SELECTED_MODELS:
        PROFILE_ID = str(sub_userid_dict[int(M)])
        PROFILE = str(sub_dict[int(M)])
        
        print('\ncandfans-dl is downloading content to profiles/' + PROFILE + '!\n')

        if os.path.isdir('profiles/' + PROFILE):
            print("\nThe folder profiles/" + PROFILE + " exists.")
            print("Media already present will not be re-downloaded.")
        
        assure_dir("profiles")
        assure_dir("profiles/" + PROFILE)
        assure_dir("profiles/" + PROFILE + "/photos")
        assure_dir("profiles/" + PROFILE + "/videos")
        print("Saving profile info...")
        get_all_photos(PROFILE_ID)
