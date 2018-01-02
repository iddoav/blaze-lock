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
from singletontype import SingletonType

class RedisPool(object):
  __metaclass__ = SingletonType

  def __init__(self, host=None, port=None, db=None, max_connections=10):

    redis_connection_pool_kwargs = {}
    if host:
      redis_connection_pool_kwargs['host'] = host
    if port:
      redis_connection_pool_kwargs['port'] = port
    if db:
      redis_connection_pool_kwargs['db'] = db
    if max_connections:
      redis_connection_pool_kwargs['max_connections'] = max_connections

    print "entering init"
    self.blocking_pool = redis.BlockingConnectionPool(**redis_connection_pool_kwargs)
