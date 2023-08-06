#!/usr/bin/env python
import hashlib
import os
from typing import Dict, List, Optional, Set, Tuple, Any

import codefast as cf
from authc import get_redis_cn, gunload

from dofast.oss import Bucket

cf.logger.level = 'info'


class BaseLoader(object):
    pass


class BaseFile(object):
    def __init__(self, path: str) -> None:
        self._path = path

    @property
    def path(self):
        return self._path

    def zip(self, password: str, out_path: str):
        cmd = 'zip -P "{}" {} {}'.format(password, out_path, self._path)
        os.system(cmd)
        return self

    def unzip(self, password: str, out_dir: str):
        cmd = 'unzip -j -P "{}" {} -d {}'.format(password, self._path, out_dir)
        os.system(cmd)
        return self

    def suicide(self):
        """remove self file"""
        try:
            cf.io.rm(self.path)
        except Exception as e:
            cf.warning(e)
        return self

    def download_from_remote(self, url: str):
        cf.net.download(url, self.path)
        return self

    def upload_to_remote(self, url: str, remote_path: str):
        cf.net.upload_file(url, remote_path)
        return self

    def clone(self, new_path: str) -> 'BaseFile':
        return BaseFile(new_path)


class FilednLoader(BaseLoader):
    def __init__(self) -> None:
        self.url_prefix = gunload('filedn_syncfile_url')
        _folderid = gunload('filedn_syncfile_id')
        _auth = gunload('pcloud_auth')
        self.url = 'https://api.pcloud.com/uploadfile?folderid={}&filename=x&auth={}'.format(
            _folderid, _auth)
        self.zip_password = gunload('filedn_zip_password')

    def pull(self, file_name: str, remote_dir: str, local_dir: str):
        """ Download file from bucket.
        Args:
            file_name(str): file name with no path
            remote_dir(str): remote dir path of file
            local_dir(str): local dir path to save file
        """
        remote_path = cf.urljoin(remote_dir, file_name).replace('/',
                                                                '--') + '.zip'
        remote_url = cf.urljoin(self.url_prefix, remote_path)
        local_path = os.path.join(local_dir, file_name) + '.zip'
        BaseFile(local_path)\
            .download_from_remote(remote_url)\
            .unzip(self.zip_password, out_dir=local_dir)\
            .suicide()
        return self

    def push(self, file_name: str, remote_dir: str, local_dir: str):
        """ Upload file to bucket.
        Args:
            file_name(str): local file path, e.g., /tmp/abc.md
        """
        local_path = os.path.join(local_dir, file_name)

        remote_path = cf.urljoin(remote_dir, file_name).replace('/',
                                                                '--') + '.zip'
        BaseFile(local_path)\
            .zip(self.zip_password, remote_path)\
            .upload_to_remote(self.url, remote_path)\
            .clone(remote_path)\
            .suicide()
        return self


class _OSSLoader(BaseLoader):
    def __init__(self, require_encryption: bool = False) -> None:
        """
        Args:
            require_encryption(bool): encrypte file or not before uploading
        """
        self.bucket = Bucket()
        self.require_encryption = require_encryption

    def pull(self, file_name: str, remote_dir: str, local_dir: str):
        """ Download file from bucket.
        Args:
            file_name(str): file name with no path
            remote_dir(str): remote dir path of file
            local_dir(str): local dir path to save file
        """
        remote_path = os.path.join(remote_dir, file_name)
        local_path = os.path.join(local_dir, file_name)
        self.bucket.download(remote_path, local_path)
        return self

    def push(self, file_name: str, remote_dir: str, local_dir: str):
        """ Upload file to bucket.
        Args:
            file_name(str): local file path, e.g., /tmp/abc.md
        """
        local_path = os.path.join(local_dir, file_name)
        self.bucket.upload(local_path,
                           remote_dir,
                           encryption=self.require_encryption)
        return self


def md5sum(file_path: str) -> str:
    """ Calculate md5sum of file.
    Args:
        file_path(str): file path
    """
    return hashlib.md5(open(file_path, 'rb').read()).hexdigest()


class SyncFile(object):
    def __init__(self,
                 name: str,
                 remote_dir: str = None,
                 local_dir: str = None,
                 loader_name: str = None) -> None:
        """
        Args:
            local, alias of local_dir
            remote, alias of remote_dir
        """
        self.name = name
        self.remote_dir = remote_dir.lstrip('/') if remote_dir else 'tmp'
        self.local_dir = local_dir if local_dir else '/tmp'
        self._path = os.path.join(local_dir, name)

        self.loader_name = loader_name
        if loader_name == 'oss_loader':
            self.loader = _OSSLoader()
        else:
            self.loader_name = 'filedn_loader'
            self.loader = FilednLoader()
        self._redis = get_redis_cn()
        self._json = None
        self._str = None

    def set_loader(self, loader):
        self.loader = loader
        return self

    def pull(self, overwrite: bool = False):
        """pull file from remote to local
        Args:
            overwrite(bool): overwrite local file or not
        """
        if not cf.io.exists(self.local_dir):
            cf.io.mkdir(self.local_dir)
        if not cf.io.exists(
                os.path.join(self.local_dir + self.name)) or overwrite:
            self.loader.pull(self.name, self.remote_dir, self.local_dir)
        return self

    def push(self):
        self.loader.push(self.name, self.remote_dir, self.local_dir)
        return self

    @property
    def path(self):
        """ Everytime the file is visited, it will sync with remote server.
        """
        _path = os.path.join(self.local_dir, self.name)
        if not cf.io.exists(_path):
            self.pull()
        else:
            md5sum_key = 'md5sum_{}'.format(md5sum(_path))
            if not self._redis.exists(md5sum_key):
                # 20 minutes for uploading
                self._redis.set(md5sum_key, 'wip', ex=1200)
                self.push()
                self._redis.set(md5sum_key, _path)
        self.bookkeeping()
        return _path

    def bookkeeping(self):
        # Keep file information into a json file in same directory
        if self.name == 'bookkeeping.json':
            return self
        keeper = SyncFile('bookkeeping.json', self.remote_dir, self.local_dir)
        js = keeper.loadjs()
        js[self.name] = {
            'md5sum': md5sum(self._path),
            'size': os.path.getsize(self._path),
            '_path': self._path,
            '_remote_path': self.remote_dir + self.name,
        }
        keeper.dumpjs(js)
        return self

    def copy(self, name: str) -> 'SyncFile':
        """ Quickly create a new SyncFile object with same remote_dir and local_dir.
        """
        return SyncFile(name, self.remote_dir, self.local_dir,
                        self.loader_name)

    def clone(self, name: str) -> 'SyncFile':
        """ Quickly create a new SyncFile object with same remote_dir and local_dir.
        """
        return SyncFile(name, self.remote_dir, self.local_dir,
                        self.loader_name)

    def writes(self, data: str):
        cf.io.write(data, self.path)
        return self

    def dumpjs(self, data: Dict):
        cf.js.write(data, self.path)
        return self

    def loads(self):
        return cf.io.reads(self.path)

    def loadjs(self):
        return cf.js(self.path)

    def read_csv(self, show_head: bool = False):
        import pandas as pd
        self.df = pd.read_csv(self.path)
        if show_head:
            print(self.df.head())
        return self

    def to_csv(self, data_frame):
        """
        Args:
            data_frame(pandas.DataFrame): data frame
        """
        data_frame.to_csv(self.path, index=False)

    @property
    def json(self):
        if not self._json:
            self._json = cf.js(self.path)
        return self._json

    @property
    def str(self):
        if not self._str:
            self._str = cf.io.reads(self.path)
        return self._str

    def info(self):
        print(self)
        return self

    def __repr__(self):
        return '\n'.join(('{:<20}: {}'.format(k, v)
                          for k, v in self.__dict__.items()
                          if not k.startswith('_')))


class SyncDir(object):
    def __init__(self, dir_name: str, local_path: str, remote_path: str,
                 loader_name: str) -> None:
        self.dir_name = dir_name
        self.local_path = local_path
        self.remote_path = remote_path
        self.zipped_path = os.path.join(local_path, dir_name + '.zip')

        self.sync_zip_file = SyncFile(dir_name + '.zip',
                                      remote_path,
                                      local_path,
                                      loader_name=loader_name)
