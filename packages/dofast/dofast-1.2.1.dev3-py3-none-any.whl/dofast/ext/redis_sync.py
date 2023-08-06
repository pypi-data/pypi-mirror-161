import sys
from typing import List, Optional

import codefast as cf
import redis

from dofast.vendor.command import Command
from authc import get_redis_cn


class RedisSync(Command):
    def __init__(self):
        super().__init__()
        self.session_file = cf.io.dirname() + '/redis_sync_session.joblib'
        self.name = 'redis_sync'
        self.description = 'Sync data between Redis and local file system.'
        self.subcommands = [['st', 'sync_to_redis'], ['sf', 'sync_from_redis']]
        self.__cli = None

    @property
    def cli(self) -> redis.StrictRedis:
        """Redis client."""
        if not self.__cli:
            self.__cli = get_redis_cn()
            cf.info(self.__cli)
        return self.__cli

    def sync_from_redis(self) -> True:
        keys = self.cli.hkeys(self.name)
        cf.info('download file list: {}'.format(keys))
        for key in keys:
            cf.info('downloading {}'.format(key))
            v = self.cli.hget(self.name, key)
            with open(key, 'wb') as fp:
                fp.write(v)
        cf.info('download complete')
        return True

    def sync_to_redis(self, files: List[str], overwrite: bool = True) -> bool:
        """Encode file to binary and store in Redis."""
        if overwrite:
            for old_key in self.cli.hkeys(self.name):
                self.cli.hdel(self.name, old_key)

        for f in files:
            cf.info('uploading : {}'.format(f))
            with open(f, 'rb') as fp:
                self.cli.hset(self.name, cf.io.basename(f), fp.read())
        cf.info('upload complete')
        return True

    def _process(self, args: None) -> bool:
        if not args:
            self.sync_from_redis()
        else:
            self.sync_to_redis(args)

    def sync_message(self, msg: Optional[str]) -> None:
        if msg:
            self.cli.set('SYNC_MESSAGE', msg)
        else:
            print(self.cli.get('SYNC_MESSAGE').decode())


def msg():
    args = sys.argv[1] if len(sys.argv) > 1 else None
    RedisSync().sync_message(args)


def entry():
    RedisSync()._process(sys.argv[1:])
