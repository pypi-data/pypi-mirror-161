''' crontab tasks. '''
import datetime
import enum
import json
import random
import re
import socket
import time
import urllib.parse
from threading import Thread

import codefast as cf
import pydantic
from apscheduler.schedulers.background import BackgroundScheduler
from ojbk import report_self

from .toolkits.telegram import Channel

socket.setdefaulttimeout(30)

postman = Channel('messalert')


class consts(object):
    INITIAL_COST = 0


class ExpendData(pydantic.BaseModel):
    name: pydantic.constr(strip_whitespace=True)
    expDate: str
    amount: str
    discountFee: str
    isSpecial: str

    def __str__(self):
        return f"<p> {self.name} | {self.amount} </p>"


class MobileEndpoints(enum.Enum):
    balance = 'https://h5.ha.chinamobile.com/h5-rest/balance/data'
    flow = 'https://h5.ha.chinamobile.com/h5-rest/flow/data'
    action = 'https://h5.ha.chinamobile.com/hnmccClient/action.dox'


class PapaPhone(object):

    def __init__(self, header_file=None) -> None:
        self.header_file = header_file
        self.params = {'channel': 2, 'version': '7.0.2'}
        self.rate_bucket_cnt = 0
        self.error_cnt = 0
        self.header_key = '7103_cmcc_headers'

    def is_cookie_expired(self) -> bool:
        js = self.check_once(MobileEndpoints.balance.value)
        if js and '未登录' in js.get('msg', ''):
            cf.warning('cookie is invalid')
            return True
        cf.info('cookie is valid')
        return False

    def update_cookie(self) -> bool:
        return
        from authc.myredis import rc
        auth_sign = rc.cn.get('CMCC_AUTH_SIGN').decode()
        cf.info('auth sign is', auth_sign)
        url = MobileEndpoints.action.value + '?authSign=' + urllib.parse.quote(
            auth_sign)
        cf.info('url is {}'.format(url))
        headers = self.get_headers()
        cmcc_headers_text = rc.cn.get("CMCC_HEADER").decode()

        cmcc_headers = cf.net.parse_headers(cmcc_headers_text)
        print(type(cmcc_headers))
        cf.info('cmcc headers is', cmcc_headers)
        # resp = cf.net.post(url, headers=cmcc_headers)

        hncmjsSSOCookie = resp.cookies.get('hncmjsSSOCookie')
        cf.info('new hncmjsSSOCookie:', hncmjsSSOCookie)

        def _update_sso(v: str, sso_value: str) -> str:
            return re.sub(r'hncmjsSSOCookie=(.{178})',
                          'hncmjsSSOCookie=' + sso_value, v)

        if hncmjsSSOCookie is not None:
            headers['Cookie'] = _update_sso(headers['Cookie'], hncmjsSSOCookie)
            headers['Authorization'] = _update_sso(headers['Authorization'],
                                                   hncmjsSSOCookie)
            rc.cn.set(self.header_key, json.dumps(headers))
            return True
        return False

    def get_headers(self) -> dict:
        if self.header_file and cf.io.exists(self.header_file):
            cf.info('reusing existing headers')
            return cf.js(self.header_file)
        else:
            from authc.myredis import rc
            headers = json.loads(rc.cn.get(self.header_key).decode())
            cf.info('headers is ', headers)
            return headers

    def check_once(self, endpoint: str) -> dict:
        try:
            headers = self.get_headers()
            resp = cf.net.get(endpoint, data=self.params,
                              headers=headers).json()
            cf.info('using header', headers)
            cf.info('check once result', resp)
            return resp
        except Exception as e:
            cf.error('check once error:', e)
            return {'error': str(e)}

    def monitor(self) -> dict:
        ERROR_CNT = 0
        while True:
            js = self.check_once()
            if 'data' not in js:
                ERROR_CNT += 1
                if ERROR_CNT > 3:
                    msg = 'Cellphone flow query failed 3 times. Error message: %s' % js[
                        'error']
                    postman.post(msg)
            else:
                general_flow = js['data']['flowList'][0]
                total, used = general_flow['totalFlow'], general_flow[
                    'flowUsed']
                msg = '{} / {} GB ({} %) data consumed'.format(
                    used, total,
                    float(used) / float(total) * 100)
                _cnt = int(float(used) * 3)
                if _cnt != self.rate_bucket_cnt:
                    self.rate_bucket_cnt = _cnt
                    postman.post(msg)
                if datetime.datetime.now().hour == 8:
                    postman.post('daily report: ' + msg)
                ERROR_CNT = 0
            time.sleep(random.randint(3600, 5400))

    def monitor_balance(self):
        try:
            js = self.check_once(MobileEndpoints.balance.value)
        except Exception as e:
            cf.error("monitor_balance error:", e)
            js = {}

        if 'data' not in js or js['businessCode'] != '0000':
            self.error_cnt += 1
            if self.error_cnt > 3:
                self.update_cookie()
            if self.error_cnt > 10:
                msg = 'Cellphone balance query failed 3 times, returned: %s' % json.dumps(
                    js)
                postman.post(msg)
                self.error_cnt = 0
        else:
            expend_list = js['data']['expendList']
            for e in expend_list:
                if '当天实时费用' in e['name']:
                    cost = e['amount']
                    if float(cost) != consts.INITIAL_COST:
                        msg = '当天实时费用: {}'.format(cost)
                        cf.info(msg)
                        postman.post(msg)
                        consts.INITIAL_COST = float(cost)
            self.error_cnt = 0

    def get_cost_summary(self) -> str:
        js = self.check_once(MobileEndpoints.balance.value)
        if 'data' not in js or js['data'] is None or 'expendList' not in js[
                'data']:
            msg = ''
        else:
            expend = list(map(ExpendData.parse_obj, js['data']['expendList']))
            msg = '\n'.join(map(str, expend))
        return msg

    def get_flow_summary(self) -> str:
        js = self.check_once(MobileEndpoints.flow.value)
        if 'data' not in js or js['data'] is None or 'flowList' not in js[
                'data']:
            msg = ''
        else:
            msg = "<p> name | all | remain </p>\n"
            for flow in js['data']['flowList']:
                if not flow or flow['details'] is None: continue
                for d in flow['details']:
                    msg += '<p> {} | {} | {} </p>\n'.format(
                        d['name'], d['totalFlow'], d['flowRemain'])
        return msg

    def post_to_tg(self, msg: str):
        from telegraph import Telegraph
        telegraph = Telegraph()
        telegraph.create_account(short_name=cf.random_string(10))
        response = telegraph.create_page(
            cf.random_string(16),
            html_content=msg,
        )
        msg = response['url']
        postman.post(msg)

    def post_summary(self) -> bool:
        succ = True
        try:
            report_self('papaphone')
            msg = self.get_cost_summary()
            msg += '-' * 30 + '\n'
            time.sleep(1)
            msg += self.get_flow_summary()
            if not msg: 
                return False
            self.post_to_tg(msg)
            return succ
        except Exception as e:
            succ = False
            cf.error('post_summary error:', e)
            raise e
        finally:
            return succ


if __name__ == '__main__':
    pp = PapaPhone()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=pp.post_summary,
                      trigger='cron',
                      hour='8',
                      minute='21',
                      timezone='Asia/Shanghai')
    scheduler.add_job(func=pp.monitor_balance,
                      trigger='cron',
                      minute='*/7',
                      timezone='Asia/Shanghai')
    scheduler.start()
    cf.info('scheduler started')
    while True:
        time.sleep(1)
