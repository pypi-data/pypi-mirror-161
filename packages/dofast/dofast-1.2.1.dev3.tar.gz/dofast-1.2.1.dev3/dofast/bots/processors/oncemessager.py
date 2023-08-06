#!/usr/bin/env python
import re
from datetime import datetime
from typing import Union

import codefast as cf
from authc.myredis import rc


class OnceMessager(object):
    def match(self, text: str) -> bool:
        return 'oncemessage' in text

    def process(self, text: str, updater: "Updater") -> None:
        _, time, msg = text.split(' ', 2)
        setname = 'ONCE_MESSAGE_SET_2022'
        key = msg + cf.random_string(32)
        expire_time = self.seconds_diff(time)
        rc.us.set(key, 1, ex=expire_time)
        rc.us.sadd(setname, key)
        updater.message.reply_text(
            'Message will be delivered in {} seconds'.format(expire_time))

    def seconds_diff(self, text: str) -> int:
        # parse datetime from text and return seconds difference
        parsed = self.parse(text)
        if parsed is None:
            # maybe pure seconds is given
            if text.isdigit():
                return int(text)
            else:
                cf.warning('Cannot parse time from "{}"'.format(text))
                return 0
        else:
            seconds = int((parsed - datetime.now()).total_seconds())
            if seconds < 0:
                cf.warning('Time in past: {}'.format(text))
            return max(seconds, 0)

    def parse(self, text: str) -> Union[datetime, None]:
        r = re.search(
            r'(((?P<month>[\w+|\d+])?([\/\:\-]))?(?P<day>\d+)([\s]+))?(?P<hour>\d+)[\:\-\/](?P<minute>\d+)([\:\-\/](?P<second>\d+))?$',
            text)
        if r:
            year = datetime.now().year
            month = int(r.group('month') or datetime.now().month)
            day = int(r.group('day') or datetime.now().day)
            hour = int(r.group('hour'))
            minute = int(r.group('minute'))
            second = int(r.group('second') or 0)
            date_str = '{}-{}-{} {}:{}:{}'.format(year, month, day, hour,
                                                  minute, second)
            cf.info('parsed date: {}'.format(date_str))
            return datetime(year, month, day, hour, minute, second)
        return None
