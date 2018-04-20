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

from keystoneauth1.identity.generic import password as ks_password
from keystoneauth1 import session as ks_session
from openstack import connection

from masakariclient.tests import base
import masakariclient.v1.client as mc


class FakeConnection(object):

    def __init__(self, prof=None, user_agent=None, **kwargs):
        super(FakeConnection, self).__init__()
        self.ha = None


class TestV1Client(base.TestCase):

    def setUp(self):
        super(TestV1Client, self).setUp()
        self.auth = mock.Mock()
        self.session = mock.Mock()
        self.conn = mock.Mock()
        self.service = mock.Mock()
        self.conn.instance_ha = self.service

    @mock.patch.object(connection, 'Connection')
    @mock.patch.object(ks_session, 'Session')
    @mock.patch.object(ks_password, 'Password')
    def test_client_init(self, mock_password, mock_session, mock_connection):

        mock_password.return_value = self.auth
        mock_session.return_value = self.session
        mock_connection.return_value = self.conn

        fake_auth_url = 'fake_auth_url'
        fake_username = 'fake_username'
        fake_password = 'fake_password'
        fake_user_domain_id = 'fake_user_domain_id'
        fake_project_name = 'fake_project_name'
        fake_project_domain_id = 'fake_project_domain_id'
        fake_interface = 'fake_interface'
        fake_region_name = 'fake_region_name'

        res = mc.Client(auth_url=fake_auth_url,
                        username=fake_username,
                        password=fake_password,
                        user_domain_id=fake_user_domain_id,
                        project_name=fake_project_name,
                        project_domain_id=fake_project_domain_id,
                        interface=fake_interface,
                        region_name=fake_region_name)

        self.assertEqual(self.conn.instance_ha, res.service)
        mock_password.assert_called_once_with(
            auth_url=fake_auth_url,
            username=fake_username,
            password=fake_password,
            user_domain_id=fake_user_domain_id,
            project_name=fake_project_name,
            project_domain_id=fake_project_domain_id)
        mock_session.assert_called_once_with(auth=self.auth)
        mock_connection.assert_called_once_with(
            session=self.session, interface=fake_interface,
            region_name=fake_region_name)
