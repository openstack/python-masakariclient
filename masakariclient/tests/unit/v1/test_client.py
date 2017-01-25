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
"""
test_masakariclient
----------------------------------

Tests for `masakariclient` module.
"""
import mock

from masakariclient.sdk.ha import connection
from masakariclient.tests import base
import masakariclient.v1.client as mc


class FakeConnection(object):

    def __init__(self, prof=None, user_agent=None, **kwargs):
        super(FakeConnection, self).__init__()
        self.ha = None


class TestV1Client(base.TestCase):

    def setUp(self):
        super(TestV1Client, self).setUp()
        self.conn = mock.Mock()
        self.service = mock.Mock()
        self.conn.ha = self.service

    def test_client_init(self):
        with mock.patch.object(connection,
                               'create_connection') as mock_connection:
            mock_connection.return_value = self.conn

            res = mc.Client()

            self.assertEqual(self.conn.ha, res.service)
            mock_connection.assert_called_once_with(prof=None, user_agent=None)
