import ast
import re
import json
from typing import List, Union

import codefast as cf
from dofast.bots.processors.base import TextProcessor
from dofast.network import Twitter
from dofast.pipe import author
from telegram import Update
import hashlib


class OldFilesCleaner(object):
    def labor(self):
        # clean files in /tmp older than 7 day
        cf.shell('find /tmp -type f -mtime +7 -exec rm -f {} \;')


"""TODO
post with fileid
{'entities': [], 'photo': [], 'channel_chat_created': False, 'new_chat_photo': [], 'group_chat_created': False, 'delete_chat_photo': False, 'date': 1652106859, 
'video': {'file_id': 'BAACAgUAAxkDAAI9wmJ5Jmtyo2_BLwKKjbZdI7auS8a-AAJbBgACyWvJV-hmKUmzauW-JAQ', 'file_name': 'a3098cdfd2818b1ab8a8e9a58dac4a8a.mp4', 'file_size': 38448890, 'file_unique_id': 'AgADWwYAAslryVc', 'height': 320, 'mime_type': 'video/mp4', 'width': 320, 'duration': 0}, 'new_chat_members': [], 'chat': {'type': 'private', 'first_name': 'Gurkha', 'id': 460172892}, 'message_id': 15810, 'caption_entities': [], 'supergroup_chat_created': False, 'from': {'username': 'LinuxLogger_bot', 'first_name': '河马河马、一口吃俩', 'id':' , 'is_bot': True}}
"""


class VideoCache(object):
    def __init__(self) -> None:
        from authc import get_redis
        self.redis = get_redis()

    def query_video_id(self, digest_value: str) -> Union[str, None]:
        if self.redis.exists(digest_value):
            return self.redis.get(digest_value).decode('utf-8')
        return None

    def save_video_id(self, digest_value: str, message: dict) -> None:
        self.redis.set(digest_value,
                       message['video']['file_id'],
                       ex=30 * 24 * 60 * 60)


class TwitterVideoDownloader(TextProcessor):
    def match(self, text: str) -> bool:
        return text.startswith('https://twitter.com/')

    def run(self, text: str, update: Update) -> bool:
        update.message.delete()
        message = update.message.reply_text(f'Downloading video from {text}')
        filename = hashlib.md5(text.encode('utf-8')).hexdigest()
        video = f"/tmp/{filename}.mp4"
        cacher = VideoCache()
        try:
            video_id = cacher.query_video_id(filename)
            if video_id is not None:
                message.edit_text(f'Video already cached.')
                cf.info('file id is {}'.format(video_id))
                update.message.reply_video(video_id, supports_streaming=True)
            else:
                cf.shell('youtube-dl -f best {} -o {}'.format(text, video))
                cf.info(f'video {video} downloaded.')
                message.edit_text(f'Uploading video ...')
                _msg = update.message.reply_video(open(video, 'rb'),
                                                  supports_streaming=True)
                js = json.loads(_msg.to_json())
                cacher.save_video_id(filename, js)
            message.delete()
            cf.info(f'video {video} sent.')
        except Exception as e:
            update.message.reply_text(str(e))
        finally:
            cf.shell('rm -f {}'.format(video))
        OldFilesCleaner().labor()
        return True


class TwitterBlockerProcessor(TextProcessor):
    def __init__(self) -> None:
        self.accounts = ['slp', 'elena']

    def match(self, text: str) -> bool:
        return text.startswith('https://twitter.com/')

    def run(self, text, update: Update) -> bool:
        for account_name in self.accounts:
            _auth = ast.literal_eval(author.get(account_name))
            self.api = None
            if _auth:
                self.api = Twitter(_auth['consumer_key'],
                                   _auth['consumer_secret'],
                                   _auth['access_token'],
                                   _auth['access_token_secret'])
            screen_name = re.findall(r'https://twitter.com/(.*)/status',
                                     text)[0]
            self.api.block_by_screenname(screen_name)
            cf.info('Blocked {} for {}'.format(screen_name, account_name))
        return True
