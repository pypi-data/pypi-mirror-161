import re
from dofast.flask.core import produce_cn_app
import subprocess
import codefast as cf
app = produce_cn_app('linux_work')


def is_valid_url(url: str) -> bool:
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


@app.task
def open_url_on_linux(url: str):
    if is_valid_url(url):
        cf.info('open url:', url)
        cmd = "/usr/bin/google-chrome \"%s\"" % url
        subprocess.Popen(cmd, shell=True)
    else:  # pure text
        cf.io.write(url, '/tmp/url.txt')
        subprocess.Popen('/usr/bin/google-chrome /tmp/url.txt', shell=True)
        cf.warning('not a valid url:', url)
    return 'SUCCESS'


def get_session_id() -> str:
    cmd = "loginctl -l| grep seat |awk '{print $1}'"
    return cf.shell(cmd).strip()


@app.task
def unlock_device() -> str:
    sid = get_session_id()
    cmd = "/bin/loginctl unlock-session {}".format(sid)
    subprocess.Popen(cmd, shell=True)
    return 'DONE'


@app.task
def lock_device() -> str:
    sid = get_session_id()
    cmd = "/bin/loginctl lock-session {}".format(sid)
    subprocess.Popen(cmd, shell=True)
    return 'DONE'
