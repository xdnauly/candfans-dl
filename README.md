# candfans-dl

## ❗ Warning

ダウンロードして頂いた作品（画像・動画）は著作権法によって保護されており、二次利用、無断転載、無断転売、複製、上映、その他第三者への公開・譲渡を一切禁じさせていただきます。

## 🎇 Introduction

Inspired by onlyfans-dl.

Only support python 3.9 | 3.10 | 3.11

## 🌟 Requirements

```
    httpx
```

## ⚡ Quick Start

1. install httpx

    `pip install httpx`
    
    `pip install tqdm`

2. Open browser find out the Cookie and X-Xsrf-Token.
    ![session](./images/file.jpg)

3. Create auth.json file and fill in value.

    ![auth.json](./images/file.PNG)

    ![auth.json](./images/auth.PNG)

4. `python .\candfans-dl.py`

    ![session](./images/cmd.PNG)

## Feature

- type hint
- use asyncio
- good performance

## TODO

- imporve async method
- choose more than one model everytime
- imporve process bar
