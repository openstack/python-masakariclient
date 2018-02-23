# Copyright(c) 2016 Nippon Telegraph and Telephone Corporation
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

from masakariclient.sdk.ha import connection


class Client(object):

    # TODO(mordred) This will need to be updated, which will be an API break.
    # Not sure what the best way to deal with that is. Perhaps just add a
    # config argument and use it if it's there. I mean, a human can't create
    # a Profile once they've installed a new enough SDK.
    def __init__(self, prof=None, user_agent=None, **kwargs):
        self.con = connection.create_connection(
            prof=prof, user_agent=user_agent, **kwargs)
        self.service = self.con.ha
