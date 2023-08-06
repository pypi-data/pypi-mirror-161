from dofast.network import Twitter
from dofast.pipe import author
import ast


class API(object):
    def __init__(self):
        pass

    @property
    def twitter(self):
        keys = ast.literal_eval(author.get('slp'))
        return Twitter(keys['consumer_key'], keys['consumer_secret'],
                       keys['access_token'], keys['access_token_secret'])



