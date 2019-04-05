import base64
import binascii
import json
import random
import requests

from Crypto.Cipher import AES
from string import ascii_letters, digits

_charset = ascii_letters + digits


def rand_char(num=16):
    return ''.join(random.choice(_charset) for _ in range(num))


def aes_encrypt(msg, key, iv='0102030405060708'):
    def padded(msg):
        pad = 16 - len(msg) % 16
        return msg + pad * chr(pad)

    msg = padded(msg)
    cryptor = AES.new(key, IV=iv, mode=AES.MODE_CBC)
    text = cryptor.encrypt(msg)
    text = base64.b64encode(text)
    text = str(text, encoding="utf-8")
    return text


def gen_params(d, i):
    text = aes_encrypt(d, '0CoJUm6Qyw8W8jud')
    text = aes_encrypt(text, i)
    return text


def rsa_encrypt(msg):
    msg = msg.encode(encoding='utf-8')
    msg = binascii.b2a_hex(msg[::-1])
    msg = int(msg, 16)
    text = 1
    for _ in range(0x10001):
        text *= msg
        text %= 0x00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7
    return format(text, 'x')


def encrypt(query):
    query = json.dumps(query)
    rand_i = rand_char(16)
    params = gen_params(query, rand_i)
    enc_sec_key = rsa_encrypt(rand_i)
    data = {
        'params': params,
        'encSecKey': enc_sec_key
    }
    return data


def download_file(url, filename):
    # local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return filename


def download_song(song_name, song_id):
    song_url = "http://music.163.com/song/media/outer/url?id={}.mp3".format(song_id)
    print(song_url)
    print("正在下载歌曲:{}".format(song_name))
    download_file(song_url, "song\\{}.mp3".format(song_name))
    # urllib.request.urlretrieve(song_url, "song\\{}.mp3".format(song_name))
    print("下载成功")


if __name__ == '__main__':
    flag = True
    while flag:
        key = input("搜索:")
        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        headers = {
            'Connection': 'keep-alive',
            'Host': 'music.163.com',
            'Origin': 'http://music.163.com',
            'Referer': 'http://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
        }

        query = {
            "hlpretag": "<span class=\"s-fc7\">",
            "hlposttag": "</span>",
            "s": "{}".format(key),
            "type": "1",
            "offset": "0",
            "total": "true",
            "limit": "30",
            "csrf_token": ""
        }

        data = encrypt(query)
        r = requests.post(url, data=data, headers=headers).json()
        i = 0
        choose = []
        print('编号', '\t', '歌名')
        for item in r['result']['songs']:
            choose.append((item['name'], item['id']))
            s = "{:<3}      {:<10}".format(len(choose), item['name'])
            print(s)
        flag_2 = True
        while flag_2:
            try:
                print()
                num = input('输入你想下载的音乐的编号{退出下载:"quit"},{下載全部:"all"}:')
                if num == 'quit':
                    break
                elif num == 'all':
                    for i in range(len(choose)):
                        download_song(choose[i][0], choose[i][1])
                else:
                    num = int(num)
                    download_song(choose[num - 1][0], choose[num - 1][1])
            except Exception:
                flag_2 = False
                print("错误")

        x = input("是否继续搜索（y/n）: ")
        if x != 'y' and x != 'Y':
            flag = False

input('音乐已经保存在song文件夹目录下请按enter键退出:')
