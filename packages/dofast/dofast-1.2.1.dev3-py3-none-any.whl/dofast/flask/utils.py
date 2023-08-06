import codefast as cf
from flask import request
from dofast.data.dynamic import TOKEN


def make_response(code: int, msg: str):
    return {'code': code, 'message': msg}


# AUTH off for URL shortener
WHITE_LIST_PATHS = ['/s', '/bark', '/uploladed', '/hanlp',
                  '/hello', '/public', '/open_url_on_linux']

def authenticate_flask(app):
    @app.before_request
    def _():
        cf.info('request', repr(request))
        if any(map(lambda x: request.path.startswith(x), WHITE_LIST_PATHS)):
            return
        token = request.args.get('token', '')
        if token == TOKEN:
            cf.info('Authentication SUCCESS.')
            return
        return make_response(401, 'Authentication failed.')
