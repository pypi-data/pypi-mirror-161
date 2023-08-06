import requests
import sys
import bs4
import codefast as cf
import string
from authc import get_redis_cn


class YouDao(object):
    def _get_header(self):
        headers = {}
        headers[
            "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@6.002}"
        headers[
            "Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        return headers

    def search_word(self, kw='novice'):
        s = requests.Session()
        url = 'http://dict.youdao.com/w/{}'.format('%20'.join(kw.split()))
        res = s.get(url, headers=self._get_header())
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        trans = soup.findAll('div', class_='trans-container')

        if len(trans) == 0:
            cf.warning("Sorry, no translation was found for {}".format(kw))
            return

        result = ""
        """ Chinese to English """
        for span in soup.findAll('span', class_='contentTitle'):
            if kw[0] in string.ascii_lowercase:     # Only print this for Chinese word
                continue

            trans = span.text.replace(";", '').strip()
            if trans[-1] in string.ascii_lowercase:
                result += trans + '\n'

        """ English to Chinese """
        ul = soup.findAll('ul')[1]
        for li in ul.findAll('li'):
            result += '\t{}\n'.format(li.text)

        import re
        for div in soup.findAll('div',
                                {'class': {'examples', 'collinsMajorTrans'}}):
            # print(div.text)
            con = re.sub(r'(\s+)', ' ', div.text.strip())
            result += '\t{}\n'.format(con)
            if div.attrs['class'][0] == 'examples':
                result += '\n'
        return result

    def search_from_redis(self, kw: str):
        """Search from redis"""
        _redis = get_redis_cn()
        _key = 'YouDaoDict_'+kw
        if _redis.exists(_key):
            return _redis.get(_key).decode()


def youdao_dict(word: str):
    yd = YouDao()
    res = yd.search_from_redis(word)
    if res:
        print(res)
        return
    res = yd.search_word(word)
    if res:
        _redis = get_redis_cn()
        _key = 'YouDaoDict_'+word
        _redis.set(_key, res)
        print(res)


def run():
    youdao_dict(sys.argv[1])
