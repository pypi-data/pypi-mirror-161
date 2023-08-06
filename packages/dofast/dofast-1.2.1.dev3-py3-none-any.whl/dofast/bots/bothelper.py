import json

import codefast as cf


class BotHelper:
    def __init__(self):
        ...

class CMCCCookieUpdater(object):
    def match(self, text:str)->bool:
        if 'h5.ha.chinamobile.com' in text and 'Authorization' in text:
            self.text = text
            return True
        return False
    
    def process(self, text:str, updater:'Updater')->None:
        if update_cmcc_app_cookie(text):
            updater.message.reply_text("CMCC cookie update SUCCESS")
        else:
            updater.message.reply_text("CMCC cookie update FAILED")

def update_cmcc_app_cookie(cookie: str):
    hashmap = {}
    for c in cookie.split('\n'):
        if not c: continue
        k, v = c.split(':', 1)
        hashmap[k] = v.lstrip(' ').rstrip(' ')

    try:
        from authc.myredis import rc
        if rc.cn.set('7103_cmcc_headers', json.dumps(hashmap)):
            cf.info('CMCC cookie updated')
        return True
    except Exception as e:
        cf.error(str(e))
        return False

