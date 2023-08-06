import json
from collections import Counter
import requests
import time
import heapq
import codefast as cf
import traceback
from abc import ABCMeta, abstractmethod
import atexit
import signal
import sys
from authc import get_redis


class Processor(metaclass=ABCMeta):
    def __init__(self):
        self._continue = True

    @abstractmethod
    def process(self):
        pass

    def _safe_kill_handler(self, signum, frame):
        self._continue = False

    def run(self):
        @atexit.register
        def atexit_fun():
            exc_type, exc_value, exc_tb = sys.exc_info()
            s = traceback.format_exception(exc_type, exc_value, exc_tb)
            if exc_type:
                cf.error(__name__ + ' exit:' + str(s))
            else:
                cf.info(__name__ + ' exit:' + str(s))

        signal.signal(signal.SIGTERM, self._safe_kill_handler)
        signal.signal(signal.SIGINT, self._safe_kill_handler)
        signal.signal(signal.SIGHUP, self._safe_kill_handler)

        while self._continue:
            self.process()


class PriorityTaskDispatcher(Processor):
    def __init__(self, topic_name: str, channel_name: str):
        super().__init__()
        self.tasks = []
        self.timer = 0
        self.TOPIC_NAME = topic_name
        self.CHANNEL_NAME = channel_name

    def get_channel_depth(self) -> int:
        nsqd_url = 'http://localhost:4151/stats?format=json'
        stats_json = requests.get(nsqd_url).json()
        for topic in stats_json['topics']:
            for channel in topic['channels']:
                if channel['channel_name'] == self.CHANNEL_NAME:
                    return int(channel['depth'])

    def _safe_kill_handler(self, signum, frame):
        super()._safe_kill_handler(signum, frame)
        pipe = get_redis().pipeline()
        for _, task_id, task_info in self.tasks:
            pipe.set('priority_task_' + task_id, json.dumps(task_info))
        pipe.execute()

    def process(self):
        myredis = get_redis()
        for key in myredis.keys('priority_task_*'):
            r_key = key
            task_info = myredis.get(r_key)
            task_info = json.loads(task_info)
            task_id = r_key.strip('priority_task_')
            heapq.heappush(self.tasks,
                           (task_info['priority'], task_id, task_info))
            myredis.delete(r_key)

        if self.get_channel_depth() < 10:
            N = min(100, len(self.tasks))
            for _ in range(N):
                priority, task_id, task_info = heapq.heappop(self.tasks)
                cf.info('{} / {}'.format(priority, task_id))
                # produce messages

        time.sleep(1)
        self.timer += 1
        self.show_progress()

    def show_progress(self):
        if len(self.tasks) == 0:
            if (self.timer & (self.timer - 1) == 0) and self.timer != 0:
                cf.info('no more task for {} seconds.'.format(self.timer))
        elif self.timer % 3 == 0:
            cter = Counter([tp[0] for tp in self.tasks])
            cf.info('prioritied event task quota: ' + str(cter))


if __name__ == '__main__':
    ptd = PriorityTaskDispatcher()
    ptd.run()
