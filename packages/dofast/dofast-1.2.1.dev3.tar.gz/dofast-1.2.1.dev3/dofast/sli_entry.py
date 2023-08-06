import json
import os
import socketserver
import sys

import codefast as cf
from codefast.argparser import PLACEHOLDER

from dofast.flask.config import AUTH_KEY
from dofast.bots.hemabot import Psycho

from .network import (Bookmark, CoinMarketCap,
                      CustomHTTPRequestHandler, Douban, InputMethod,
                      LunarCalendar, Phone)
from .oss import Bucket, Message
from .pipe import author
from .security._hmac import generate_token
from .utils import download as getfile
from dofast.toolkits.telegram import Channel
import ast


def hemabot():
    Psycho.main()


def jsonify() -> dict:
    if len(sys.argv) > 1:
        jsf = sys.argv[1]
        assert cf.io.exists(jsf)
        js = cf.js.read(cf.io.read(jsf, ''))
        js = json.dumps(js)
        print(js)
    else:
        _stdin = sys.stdin
        x = _stdin.buffer.read().decode('utf-8')
        x = ast.literal_eval(x)
        _dict = json.dumps(x, indent=4)
        print(_dict)

def nsq_sync():
    cli = Bucket()
    if len(sys.argv) > 1:
        cf.utils.shell('zip -r9 -P syncsync63 -FSr /tmp/sync.zip {}'.format(
            ' '.join(sys.argv[1:])))
        cf.info('Files zipped.')
        cli.upload('/tmp/sync.zip')
        token = generate_token(AUTH_KEY, expire=5)
        _uuid = cf.utils.uuid(),
        cf.js.write({'uuid': _uuid}, '/tmp/syncfile.json')
        js = {
            'token': token,
            'topic': 'file',
            'channel': 'sync',
            'uuid': _uuid,
            'data': {
                'uuid': _uuid,
                'filename': 'sync.zip'
            }
        }
        SERVER_HOST = author.get('SERVER_HOST')
        res = cf.net.post(f'http://{SERVER_HOST}:6363/nsq', json=js)
        cf.info('FileSync', res.text)


def _hint_wubi():
    if len(sys.argv) > 1:
        InputMethod().entry(sys.argv[1])


def main():
    sp = cf.argparser.ArgParser()
    from dofast.apps import Apps
    # PLACEHOLDER = cf.argparser.PLACEHOLDER
    sp.input('-cos',
             '--cos',
             sub_args=[["u", "up", "upload"], ["download", "d", "dw"],
                       ["l", "list"], ["del", "delete"]])
    sp.input('-oss',
             '--oss',
             sub_args=[["u", "up", "upload"], ["d", "dw", 'download'],
                       ["l", "list"], ["del", "delete"], ['size']])
    sp.input('-dw', '--download', sub_args=[['p', 'proxy']])
    sp.input('-puboss',
             '--puboss',
             description="upload to oss and return public url")
    sp.input('-d', '--ddfile')
    sp.input('-ip',
             '--ip',
             sub_args=[['p', 'port']],
             default_value="localhost")
    sp.input('-rc', '--roundcorner', sub_args=[['r', 'radius']])
    sp.input('-gu', '--githubupload')
    sp.input('-sm', '--smms')
    sp.input('-fd', '--find', sub_args=[['dir', 'directory']])
    sp.input('-m', '--msg', sub_args=[['r', 'read'], ['w', 'write']])
    sp.input('-fund', '--fund', sub_args=[['ba', 'buyalert']])
    sp.input('-stock', '--stock')
    sp.input('-gcr', '--githubcommitreminder')
    sp.input('-pf', '--phoneflow')
    sp.input('-hx', '--happyxiao')
    sp.input('-tgbot', '--telegrambot')
    sp.input('-snapshot',
             '--snapshot',
             description='post a snapshot message to Channel')
    sp.input('-db', '--doubaninfo', description='Get douban film information.')
    sp.input('-tt', '-twitter', description='Twitter API.')
    sp.input(
        '-lunar',
        '-lunarcalendar',
        default_value="",
        description='Lunar calendar. Usage:\n sli -lc or sli -lc 2088-09-09.')
    sp.input('-fi', '-fileinfo', description='Get file meta information.')
    sp.input(
        '-st',
        '-securitytext',
        sub_args=[['-d', '-decode'], ['-o', '-output']],
        description='Generate secirty text. Usage: \n sli -st input.txt -o output.txt \n sli -st input.txt -d -o m.txt'
    )

    sp.input('-coin',
             sub_args=[['-q', '-quote']],
             description='Coin Market API. Usage: \n sli -coin -q \n sli -coin -q btc')

    sp.input('-bitly', description='Bitly shorten url.')
    sp.input('-http',
             '-httpserver',
             sub_args=[['p', 'port']],
             description='Simple HTTP server. Usage:\n sli -http -p 8899')

    sp.input('-uni', description='Unicom data flow usage.')
    sp.input(
        '-bm',
        '--bookmark',
        sub_args=[['a', 'add'], ['d', 'delete'], ['l', 'list'], ['o', 'open'],
                  ['reload']],
        description='Make bookmark easier. Usage:\n sli -bm -o google \n sli -bm -a google https://google.com \n sli -bm -d google'
    )

    sp.input('-ebb',
             '--ebbinghaus',
             sub_args=[['u', 'update']],
             description='\nEbbinghaus forgive curve in usage.')

    sp.input('-e2c', '-excel2csv', description='Extract sheets to CSVs')
    sp.input('-gg', '-google_translate', description='Google translation API.')
    sp.input('-pcloud', description='pcloud sync file.')
    sp.input('-botsync', description='sync files from Hema bot')
    sp.input('-ccard',
             sub_args=[['-len', '--length']],
             description='Credit card generator.')
    sp.input('-avatar', description='Generate random avatar.')
    sp.input('-dlj', description='URL shortener.')
    sp.parse()
    apps = Apps()
    # ------------------------------------
    if sp.dlj:
        apps.httptools.url_shortener(sp.dlj.value)

    elif sp.avatar:
        import dofast.pyavatar as pa
        pa.PyAvataaar().random()

    elif sp.ccard:
        from dofast.toolkits.credit_card_generator import create_cc_numbers
        _len = 16 if not sp.ccard.length else int(sp.ccard.length)
        _bin = '537630' if sp.ccard.value == PLACEHOLDER else sp.ccard.value
        cf.info(_bin, _len)
        for n in create_cc_numbers(_bin, ccnumber_length=_len):
            print(n)

    elif sp.botsync:
        from dofast.toolkits.telegram import download_latest_file
        download_latest_file()

    elif sp.pcloud:
        from dofast.web.pcloud import SyncFile
        SyncFile().sync()

    elif sp.google_translate:
        apps.translator.run(client='google')

    elif sp.excel2csv:
        os.system('mkdir -p /tmp/excel/')
        cf.reader.Excel(sp.excel2csv.value).to_csv('/tmp/excel/')

    elif sp.ebbinghaus:
        from dofast.apps.ebb2022 import push, fetch
        if len(sys.argv) >= 3:
            push(sys.argv[2])
        else:
            fetch()

    elif sp.bookmark:
        bm = Bookmark()
        if sp.bookmark.open:
            _key, url = sp.bookmark.open, 'http://google.com'
            matched = [(k, v) for k, v in bm.json.items() if _key in k]
            if len(matched) == 1:
                url = matched[0][1]

            elif len(matched) > 1:
                for i, pair in enumerate(matched):
                    print("{:<3} {:<10} {:<10}".format(i, pair[0], pair[1]))
                c = input('Pick one:')
                url = matched[int(c) % len(matched)][1]

            cmd = f'open "{url}"' if 'macos' in cf.os.platform(
            ) else f'xdg-open "{url}"'
            cf.shell(cmd)

        elif sp.bookmark.add:
            _args = sp.bookmark.add
            assert len(_args) == 2, 'Usage: sli -bm -a/-add keyword URL'
            bm.add(keyword=_args[0], url=_args[1])

        elif sp.bookmark.delete:
            _args = sp.bookmark.delete
            if _args.startswith('http'):
                bm.remove(url=_args)
            else:
                bm.remove(keyword=_args)

        elif sp.bookmark.reload:
            bm.reload()

        else:
            bm.list()

    elif sp.uni:
        Phone().unicom()

    elif sp.httpserver:
        port = 8899 if not sp.httpserver.port else int(sp.httpserver.port)
        Handler = CustomHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            cf.logger.info(f"serving at port {port}")
            httpd.serve_forever()

    elif sp.bitly:
        apps.httptools.bitly(sp.bitly.value)

    elif sp.coin:
        cmc, _quote = CoinMarketCap(), sp.coin.quote
        if _quote:
            coins = ['BTC', 'ETC', 'ETH', 'SHIB'] if isinstance(
                _quote, dict) else [_quote]
            cmc.part_display(cmc.quote(coins))

    elif sp.fileinfo:
        info = cf.io.info(sp.fileinfo.value)
        important_features = {
            'channel_layout', 'channels', 'duration', 'sample_rate'
        }
        for key in ('bit_rate', 'channel_layout', 'channels',
                    'codec_tag_string', 'codec_long_name', 'codec_name',
                    'duration', 'filename', 'format_name', 'sample_rate',
                    'size', 'width'):
            if key == 'duration':
                v = info[key]
                info[key] = "{} ({})".format(v, cf.io.readable_duration(v))
            colortext = cf.fp.green(info.get(key, None), attrs=[
                'bold'
            ]) if key in important_features else info.get(key, None)
            print('{:<20} {}'.format(key, colortext))

    elif sp.doubaninfo:
        Douban.query_film_info(sp.doubaninfo.value)

    elif sp.twitter:
        apps.tweetbot.post()

    elif sp.tgbot:
        Channel('messalert').post(sp.tgbot.value)

    elif sp.snapshot:
        show_time = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        Channel('messalert').snapshot(sp.snapshot.value, show_time)

    elif sp.happyxiao:
        from .crontasks import HappyXiao
        HappyXiao.rss()

    elif sp.phoneflow:
        from .crontasks import PapaPhone
        phone = PapaPhone()
        s = '\n'.join([phone.get_cost_summary(), phone.get_flow_summary()])
        print(s)

    elif sp.githubcommitreminder:
        from .crontasks import GithubTasks
        GithubTasks.git_commit_reminder()
        GithubTasks.tasks_reminder()

    elif sp.cos:
        from .cos import COS
        cli = COS()
        if sp.cos.upload:
            cli.upload_file(sp.cos.upload, "transfer/")
        elif sp.cos.download:
            _file = sp.cos.download
            cli.download_file(f"transfer/{_file}", _file)
        elif sp.cos.delete:
            cli.delete_file(f"transfer/{sp.cos.delete}")
        elif sp.cos.list:
            print(cli.prefix())
            cli.list_files("transfer/")

    elif sp.puboss:
        apps.public_bucket.upload(sp.puboss.value)

    elif sp.oss:
        cli = Bucket()
        if sp.oss.upload:
            cli.upload(sp.oss.upload)

        elif sp.oss.download:
            _basename = cf.io.basename(sp.oss.download)
            cli._download(_basename, _basename)

        elif sp.oss.delete:
            cli.delete(sp.oss.delete)
        elif sp.oss.list:
            print(cli.url_prefix)
            if sp.oss.size:
                cli.list_files_by_size()
            else:
                cli.list_files()

    elif sp.download:
        cf.net.download(sp.download.value)

    elif sp.ddfile:
        from .utils import create_random_file
        create_random_file(int(sp.ddfile.value or 100))

    elif sp.ip:
        v_ip, v_port = sp.ip.value, sp.ip.port
        from .utils import shell
        if not sp.ip.port:
            print(shell("curl -s cip.cc"))
        else:
            print("Checking on:", v_ip, v_port)
            curl_socks = f"curl -s --connect-timeout 5 --socks5 {v_ip}:{v_port} ipinfo.io"
            curl_http = f"curl -s --connect-timeout 5 --proxy {v_ip}:{v_port} ipinfo.io"
            res = shell(curl_socks)
            if res != '':
                print(res)
            else:
                print('FAILED(socks5 proxy check)')
                print(shell(curl_http))

    elif sp.roundcorner:
        from .utils import rounded_corners
        image_path, radius = sys.argv[2], -1
        if len(sys.argv) == 4:
            radius = int(sys.argv[3])
        elif len(sys.argv) == 5:
            radius = int(sys.argv[4])
        rounded_corners(image_path, radius)

    elif sp.githubupload:
        from .network import githup_upload
        githup_upload(sp.githubupload.value)

    elif sp.smms:
        from .utils import smms_upload
        smms_upload(sp.smms.value)

    elif sp.find:
        from .utils import findfile
        print(sp.find.value, sp.find.directory or '.')
        findfile(sp.find.value, sp.find.directory or '.')

    elif sp.fund:
        from .fund import invest_advice, tgalert
        if sp.fund.buyalert:
            tgalert()
        else:
            invest_advice(None if sp.fund.value ==
                          PLACEHOLDER else sp.fund.value)

    elif sp.stock:
        from .stock import Stock
        if sp.stock.value != PLACEHOLDER:
            Stock().trend(sp.stock.value)
        else:
            Stock().my_trend()

    elif sp.lunarcalendar:
        date: str = sp.lunarcalendar.value.replace('PLACEHOLDER', '')
        LunarCalendar.display(date)

    else:
        from .data.msg import display_message
        display_message()
        sp.help()
        done, total = sp._arg_counter, 50
        print('✶' * done + '﹆' * (total - done) +
              "({}/{})".format(done, total))


if __name__ == '__main__':
    main()
