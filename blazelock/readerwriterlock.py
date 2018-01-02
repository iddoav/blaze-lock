# Copyright 2016 Kunal Lillaney (http://kunallillaney.github.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import redis
from contextlib import closing
from redispool import RedisPool
from types import *

REDIS_PREFIX = 'blazelock'
MESSAGE = 'ready'


class ReaderWriterLock(object):

  def __init__(self, lock_name, host=None, port=None, db=None, max_connections=None, timeout=None, sleep=0.1, blocking_timeout=None):

    assert lock_name
    assert type(lock_name) is StringType
    self.redis_lock = '{}_{}_redis_lock'.format(REDIS_PREFIX, lock_name)
    self.reader_counter = '{}_{}_reader_counter'.format(REDIS_PREFIX, lock_name)
    self.writer_counter = '{}_{}_writer_counter'.format(REDIS_PREFIX, lock_name)
    self.message_channel = '{}_{}_message_channel'.format(REDIS_PREFIX, lock_name)
    self.client = redis.StrictRedis(connection_pool=RedisPool(host, port, db, max_connections).blocking_pool)
    self.set_reader_count()
    self.set_writer_count()
    self._lua_lock = self.client.lock(self.redis_lock, timeout=timeout, sleep=sleep, blocking_timeout=blocking_timeout)
  
  def acquire_read(self):
    if self._lua_lock.acquire() and self.get_writer_count() == 0:
      try:
        self.increment_reader_count()
      finally:
        self._lua_lock.release()

  def release_read(self):
    if self._lua_lock.acquire():
      try:
        self.decrement_reader_count()
        if not self.get_reader_count():
          self.notify_all()
      finally:
        self._lua_lock.release()

  def acquire_write(self):
    if self._lua_lock.acquire():
      while self.get_reader_count() > 0:
        self.wait()

  def release_write(self):
    self.set_writer_count(0)
    self._lua_lock.release()
  
  def notify_all(self):
    self.client.publish(self.message_channel, MESSAGE)

  def wait(self):
    with closing(self.client.pubsub()) as pubsub:
      self.set_writer_count(1)
      pubsub.subscribe(self.message_channel)
      self._lua_lock.release()
      for msg in pubsub.listen():
        if msg['data'] == MESSAGE:
          self._lua_lock.acquire()
          return
  
  def get_writer_count(self):
    return int(self.client.get(self.writer_counter))

  def set_writer_count(self, value=0):
    self.client.setnx(self.writer_counter, value)

  def increment_writer_count(self):
    self.client.incr(self.writer_counter)

  def decrement_writer_count(self):
    self.client.decr(self.writer_counter)
  
  def get_reader_count(self):
    return int(self.client.get(self.reader_counter))

  def set_reader_count(self, value=0):
    self.client.setnx(self.reader_counter, value)

  def increment_reader_count(self):
    self.client.incr(self.reader_counter)

  def decrement_reader_count(self):
    self.client.decr(self.reader_counter)
