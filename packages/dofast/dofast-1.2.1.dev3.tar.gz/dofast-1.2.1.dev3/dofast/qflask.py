import sys
import time

import codefast as cf
import requests
from authc import authc
from flask import Flask, redirect, request
from waitress import serve

from dofast.cell import supercell
from dofast.config import CHANNEL_MESSALERT
from dofast.flask.model import lock_device, open_url_on_linux, unlock_device
from dofast.flask.utils import authenticate_flask
from dofast.toolkits.telegram import Channel

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1000 * 1000  # Maximum size 1GB
authenticate_flask(app)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    cf.error(error)
    raise error


@app.route('/bark', methods=['GET', 'POST'])
def _bark():
    return redirect("http://localhost:10101", code=302)


@app.route('/public', methods=['GET'])
def _public():
    return supercell.flask_worker.public_handler(request)


@app.route('/open_url_on_linux', methods=['GET', 'POST'])
def _open_url_on_linux():
    url = request.json.get('url')
    if url:
        url = url.replace(' ', '+')
    open_url_on_linux.delay(url)
    return {'status': 'OK'}


@app.route('/device_control', methods=['GET', 'POST'])
def device_control():
    accs = authc()
    if request.headers.get('User-Agent') != accs['whitelist_agent']:
        cf.warning('input header is:', request.headers)
        cf.warning('expected :', accs['whitelist_agent'])
        return 'UNRECOGNIZED device'
    action = request.args.get('action', 'lock')
    task = unlock_device.delay() if action == 'unlock' else lock_device.delay()
    TIMEOUT = 10
    while TIMEOUT > 0:
        if task.status == 'SUCCESS':
            return redirect('https://www.google.com')
        time.sleep(1)
        TIMEOUT -= 1
    return redirect('https://www.baidu.com')


@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
    resp = supercell.twitter_service.post(request)
    return {'response': str(resp)}


@app.route('/messalert', methods=['GET', 'POST'])
def msg():
    js = request.get_json()
    Channel(CHANNEL_MESSALERT).post(js['text'])
    return 'SUCCESS'


@app.route('/hello', methods=['GET', 'POST'])
def hello_world():
    return supercell.flask_worker.hello_world()


@app.route('/s', methods=['GET', 'POST'])
def shorten() -> str:
    """Url shortener"""
    return supercell.flask_worker.shorten_url(request)


@app.route('/rss', methods=['GET', 'POST'])
def rss():
    # render rss
    return supercell.flask_worker.render_rss()


@app.route('/<path:path>')
def default_route(path):
    result = supercell.flask_worker.default_route(path)
    return redirect(result)


@app.route('/hanlp', methods=['POST', 'GET'])
def hanlp_route():
    texts = request.json.get('texts', [])
    cf.info('hanlp input texts:', texts)
    resp = requests.post('http://localhost:55555/hanlp', json={'texts': texts})
    return resp.json()


def run():
    port = int(sys.argv[1]) if len(sys.argv) >= 2 else 6363
    cf.info('qflask is running on port:', port)
    serve(app, host="0.0.0.0", port=port)


if __name__ == '__main__':
    run()
