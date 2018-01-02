# Copyright 2014 NeuroData (http://neurodata.io)
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

from readerwriterlock import ReaderWriterLock

def WriterLock(lock_name, host=None, port=None, db=None, timeout=None,
               sleep=0.1, blocking_timeout=None, max_connections=None):
  class _WriterLock(object):

    def __init__(self, func):
      try:
        self.func = func
      except Exception as e:
        raise

    def __get__(self, obj, type=None):
      new_func = self.func.__get__(obj, type)
      return self.__class__(new_func)

    def __call__(self, *args, **kwargs):
      self.rw_lock = ReaderWriterLock(lock_name, host=host, port=port, db=db,
                                      timeout=timeout, sleep=sleep,
                                      blocking_timeout=blocking_timeout,
                                      max_connections=max_connections)
      self.rw_lock.acquire_write()
      return_value = self.func(*args, **kwargs)
      self.rw_lock.release_write()
      return return_value

  return _WriterLock
