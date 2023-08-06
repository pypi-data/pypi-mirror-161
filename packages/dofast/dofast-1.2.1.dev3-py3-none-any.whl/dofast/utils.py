# coding:utf-8
import base64
import json
import os
import subprocess
import time
from functools import wraps
from typing import Dict, List

import codefast as cf
import requests
from tqdm import tqdm
from authc import get_redis_cn, gunload
from .pipe import author


def ipinfo(ip: str = None) -> Dict[str, str]:
    """Get ip info.
    """
    KEY_PREFIX = '__ipinfo__'
    token = gunload('IPINFO_TOKEN')
    if not ip:
        url = 'http://ipinfo.io/json?token=' + token
        return requests.get(url).json()
    _redis = get_redis_cn()
    _key = '{}{}'.format(KEY_PREFIX, ip)
    if _redis.exists(_key):
        return json.loads(_redis.get(_key).decode())
    else:
        url = 'http://ipinfo.io/{}/json?token={}'.format(ip, token)
        _info = requests.get(url).json()
        _redis.set(_key, json.dumps(_info))
        _redis.expire(_key, 86400*180)
        return _info


class DeeplAPI(object):
    '''Deepl tranlation API'''

    def __init__(self) -> None:
        self._url = 'https://api-free.deepl.com/v2'
        self._headers = '''Host: api-free.deepl.com
            User-Agent: YourApp
            Accept: */*
            Content-Length: [length]
            Content-Type: application/x-www-form-urlencoded'''
        self._token = author.get('DEEPL_TOKEN')
        self._params = {'auth_key': self._token}

    def do_request(self, api_path: str) -> dict:
        resp = cf.net.post(self._url + api_path,
                           headers=cf.net.parse_headers(self._headers),
                           data=self._params)
        if resp.status_code != 200:
            raise Exception(resp)
        cf.io.say(resp.json())
        return resp.json()

    @property
    def stats(self):
        return self.do_request('/usage')

    def translate(self, text: str) -> str:
        target_lang = 'EN' if cf.nstr(text).is_cn() else 'ZH'
        self._params['text'] = text
        self._params['target_lang'] = target_lang
        return self.do_request('/translate')

    def document(self, file_name: str) -> dict:
        text = cf.io.reads(file_name)
        target_lang = 'EN' if cf.nstr(text).is_cn() else 'ZH'
        _auth = author.get('DEEPL_TOKEN')
        cmd = f'curl https://api-free.deepl.com/v2/document \
                -F "file=@{file_name}" \
                -F "auth_key={_auth}" \
                -F "target_lang={target_lang}"'

        resp = json.loads(cf.shell(cmd))
        cf.info(resp)
        _id, _key = resp['document_id'], resp['document_key']
        while True:
            resp = self.get_document_status(_id, _key)
            if resp['status'] == 'done':
                break
            time.sleep(3)

        _doc = self.get_translated_document(_id, _key)
        print(_doc)
        return _doc

    def get_document_status(self, doc_id: str, doc_key: str) -> dict:
        cf.info(f'Getting document status {doc_id} {doc_key}')
        self._params['document_key'] = doc_key
        return self.do_request(f'/document/{doc_id}')

    def get_translated_document(self, doc_id: str, doc_key: str) -> dict:
        cmd = f'curl https://api-free.deepl.com/v2/document/{doc_id}/result \
                -d auth_key={self._token} \
                -d document_key={doc_key}'

        return cf.shell(cmd)


def get_proxy() -> dict:
    proxies_file = cf.io.home() + '/.config/proxies.json'
    if cf.io.exists(proxies_file):
        cf.info(f'using proxy configuration from {proxies_file}')
        return cf.js(proxies_file)
    return {'https': author.get('HTTP_PROXY'), 'http': author.get('HTTP_PROXY')}


def google_translate(text: str = 'To live is to suffer.') -> str:
    _dest = 'en' if cf.nstr(text).is_cn() else 'zh-cn'
    from googletrans import Translator
    _proxies = get_proxy()
    cli = Translator()
    cf.info(cli)
    cf.info(text)
    ret = cli.translate(text, dest=_dest)
    cf.info(ret.text)
    return ret.text


def shell(cmd: str, print_str: bool = False) -> str:
    ret_str = ''
    try:
        ret_str = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True).decode('utf8')
    except Exception as e:
        print(e)
    finally:
        if print_str:
            cf.say(ret_str)
        return ret_str


def create_random_file(size: int = 100):     # Default 100M
    _file = 'cc.txt'
    open(_file, 'w').write("")
    print(f">> Create {_file} of size {size} MB")
    logfile = '/tmp/ddfile.txt'
    if cf.io.exists(logfile):
        for f in cf.io.read(logfile):
            cf.info('removing previous file', f)
            cf.io.rm(f)

    with open(_file, 'ab') as fout:
        cc_dir = os.path.join(cf.io.pwd().rstrip(), _file)
        cf.io.write([cc_dir], logfile)
        arr = bytearray(os.urandom(1 << 20))
        for _ in tqdm(range(size)):
            arr.pop()
            fout.write(arr)


def rounded_corners(image_name: str, rad: int = -1):
    """Add rounded_corners to images"""
    from PIL import Image, ImageDraw
    im = Image.open(image_name)
    w, h = im.size
    if rad < 0:
        hmean = 2 * w * h / (w + h)
        rad = int(hmean * 0.025)
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, "white")
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    import uuid
    export_name = f'{uuid.uuid4()}.png'
    print(f'Export to {export_name}')
    im.save(export_name)
    return im


def download(url: str, proxy=None, name=None, referer=None):
    if not name:
        name = url.split('/').pop()

    if len(name) >= 256:
        name = name[-32:]

    if proxy:
        proxy = {'http': proxy}
    headers_ = {'referer': referer}
    response = requests.get(url, stream=True, proxies=proxy, headers=headers_)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024     # 8 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    cf.info('Downloading file', name)

    with open(name, 'wb') as f:
        for chunk in response.iter_content(block_size):
            progress_bar.update(len(chunk))
            f.write(chunk)
    progress_bar.close()


# =========================================================== Decorator
def set_timeout(countdown: int, callback=print):
    def decorator(func):
        def handle(signum, frame):
            raise RuntimeError

        def wrapper(*args, **kwargs):
            import signal
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(countdown)     # set countdown
                r = func(*args, **kwargs)
                signal.alarm(0)     # close alarm
                return r
            except RuntimeError as e:
                print(e)
                callback()

        return wrapper

    return decorator


def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


def logged(logger_func, name=None, message=None):
    """
    Add logging to a function. name is the logger name, and message is the
    log message. If name and message aren't specified,
    they default to the function's module and name.
    """
    import logging

    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger_func(logmsg)
            return func(*args, **kwargs)

        return wrapper

    return decorate


# =========================================================== media


def smms_upload(file_path: str) -> dict:
    """Upload image to image server sm.ms"""
    url = "https://sm.ms/api/v2/upload"
    data = {'smfile': open(file_path, 'rb')}
    res = requests.Session().post(url,
                                  files=data,
                                  headers=cf.js('/usr/local/info/smms.json'))
    j = json.loads(res.text)
    try:
        cf.info(j['data']['url'])
    except Exception as e:
        cf.error(f"Exception {j}")
        cf.info(j['images'])     # Already uploaded
        raise Exception(str(e))
    finally:
        return j


# =========================================================== Network
def git_io_shorten(url):
    """Shorten url with git.io"""
    session = requests.Session()
    res = session.post('https://git.io/create', data={'url': url})
    return f'http://git.io/{res.text}'

# =========================================================== Search


def findfile(regex: str, dir: str = "."):
    for relpath, _, files in os.walk(dir):
        for f in files:
            if regex in f:
                full_path = os.path.join(dir, relpath, f)
                print(os.path.normpath(os.path.abspath(full_path)))
