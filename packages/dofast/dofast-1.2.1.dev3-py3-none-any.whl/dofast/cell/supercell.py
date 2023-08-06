from typing import Any
from typing import List, Dict, Tuple, Set, Optional, Union
import hashlib
from hashids import Hashids
import codefast as cf
from authc import get_redis, get_redis
from threading import Thread
import flask
from dofast.cell.api import API
import enum


class FlaskPublicHandlerArgs(str, enum.Enum):
    QX = 'TW05eE0wNXNVMVZUZDJsVWNRbz0K'
    HELLO = 'hello'


class _DataBase(object):
    __redis = None

    @classmethod
    def _init_redis(cls) -> None:
        """lazy initialization"""
        if cls.__redis is None:
            cls.__redis = get_redis()
        return cls.__redis

    @classmethod
    def set(cls, key: str, value: str) -> None:
        return cls._init_redis().set(key, value)

    @classmethod
    def get(cls, key: str) -> Optional[str]:
        return cls._init_redis().get(key)


class FlaskWorker(object):
    def __init__(self) -> None:
        pass

    def public_handler(self,
                       request: flask.request) -> Optional[Union[str, Dict]]:
        arg = request.args.get('arg')
        if arg == FlaskPublicHandlerArgs.QX:
            return _DataBase.get(FlaskPublicHandlerArgs.QX.value).decode()
        elif arg == FlaskPublicHandlerArgs.HELLO:
            return flask.Response('hello')

    def hello_world(self) -> Dict:
        return {'status': 'SUCCESS', 'code': 200, 'msg': 'HELLO'}

    def default_route(self, path: str) -> str:
        path_str = str(path)
        cf.info('request path: ' + path_str)
        if not path_str.startswith('s/'):
            return ''
        r = get_redis()
        key = 'shorten_' + path_str.replace('s/', '')
        out_url = r.get(key).decode() if r.exists(
            key) else 'https://www.baidu.com'
        cf.info('out_url: ' + out_url)
        return out_url

    def shorten_url(self, req: flask.request) -> Dict[str, str]:
        data = req.get_json(force=True)
        cf.info('input data: ' + str(data))
        if not data:
            return {}
        url = data.get('url', '')
        md5 = hashlib.md5(url.encode()).hexdigest()
        uniq_id = Hashids(salt=md5, min_length=6).encode(42)

        def persist(key, url):
            return _DataBase.set(key, url, ex=60 * 60 * 24 * 365)

        Thread(target=persist, args=('shorten_' + uniq_id, url)).start()
        return {
            'code': 200,
            'status': 'SUCCESS',
            'url': req.host_url + 's/' + uniq_id
        }

    def render_rss(self):
        from rss.base.wechat_rss import create_rss_worker
        wechat_ids = [
            'almosthuman', 'yuntoutiao', 'aifront', 'rgznnds', 'infoq',
            'geekpark', 'qqtech'
        ]
        for wechat_id in wechat_ids:
            worker = create_rss_worker(wechat_id)
            _, all_articles = worker.pipeline()
            cf.info('all_articles: ' + str(all_articles))


class TwitterService(object):
    def __init__(self, api: API) -> None:
        self.api = api

    def post(self, req: flask.request) -> None:
        text = req.args.get('text', '')
        cf.info('input text: ' + text)
        files = req.files.getlist('images')
        cf.info('input files: ' + str(files))
        media = ['/tmp/{}'.format(f.filename) for f in files]
        for m, f in zip(media, files):
            f.save(m)
        self.api.twitter.post([text] + media)
        return {'text': text, 'images': [f.filename for f in files]}


class BarkWorker(object):
    def __call__(self, req: flask.request) -> None:
        print(str(req))
        return {'status': 'SUCCESS', 'code': 200}


class SuperCell(object):
    def __init__(self) -> None:
        self.api = API()
        self.flask_worker = FlaskWorker()
        self.twitter_service = TwitterService(self.api)
        self.bark_worker = BarkWorker()
