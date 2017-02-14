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

from osc_lib import utils

from masakariclient.osc.v1.host import DeleteHost
from masakariclient.osc.v1.host import ShowHost
from masakariclient.osc.v1.host import UpdateHost
from masakariclient.tests import base


class FakeNamespace(object):
    """Fake parser object."""
    def __init__(self, segment_id=None, host=None,
                 reserved=None, name=None, type=None,
                 control_attributes=None, on_maintenance=None):
        super(FakeNamespace, self).__init__()
        self.segment_id = segment_id
        self.host = host
        self.reserved = reserved
        self.name = name
        self.type = type
        self.control_attributes = control_attributes
        self.on_maintenance = on_maintenance


class FakeHosts(object):
    """Fake segment host list."""
    def __init__(self, name=None, uuid=None):
        super(FakeHosts, self).__init__()
        self.name = name
        self.uuid = uuid


class FakeHost(object):
    """Fake segment show detail."""
    def __init__(self,):
        super(FakeHost, self).__init__()

    def to_dict(self):
        return {
            'reserved': 'False',
            'uuid': '124aa63c-bbe1-46c3-91a9-285fac7d86c6',
            'segment_id': '870da19d-37ec-41d2-a4b2-7be54b0d6ec9',
            'on_maintenance': False,
            'created_at': '2016-12-18T05:47:55.000000',
            'control_attributes': 'control_attributes',
            'updated_at': None,
            'name': 'host_name',
            'type': 'auto',
            'id': 18,
            'failover_segment_id': '187dd15a-9c1d-4bf7-9f6c-014d5bc66992',
            }


class TestV1ShowHost(base.TestCase):
    def setUp(self):
        super(TestV1ShowHost, self).setUp()

        self.app = mock.Mock()
        self.app_args = mock.Mock()
        self.show_host = ShowHost(self.app, self.app_args,
                                  cmd_name='host show')
        self.client_manager = mock.Mock()
        self.app.client_manager.ha = self.client_manager
        self.columns = [
            'created_at', 'updated_at', 'uuid', 'name', 'type',
            'control_attributes', 'reserved', 'on_maintenance',
            'failover_segment_id',
        ]
        # fake host list
        self.dummy_hosts = []
        self.dummy_hosts.append(FakeHosts(
            name='host_name',
            uuid='124aa63c-bbe1-46c3-91a9-285fac7d86c6'))
        # fake host show
        self.dummy_host = FakeHost()

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_uuid(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(
            segment_id='187dd15a-9c1d-4bf7-9f6c-014d5bc66992',
            host='124aa63c-bbe1-46c3-91a9-285fac7d86c6')
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value = self.dummy_host

        # show the host specified by uuid
        self.show_host.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_host.to_dict(), self.columns, formatters={})

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_name(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(
            segment_id='187dd15a-9c1d-4bf7-9f6c-014d5bc66992',
            host='host_name')
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value = self.dummy_host
        # show the host specified by name
        self.show_host.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_host.to_dict(), self.columns, formatters={})


class TestV1UpdateHost(base.TestCase):
    def setUp(self):
        super(TestV1UpdateHost, self).setUp()

        self.app = mock.Mock()
        self.app_args = mock.Mock()
        self.update_host = UpdateHost(self.app, self.app_args,
                                      cmd_name='host update')
        self.client_manager = mock.Mock()
        self.app.client_manager.ha = self.client_manager
        self.columns = [
            'created_at', 'updated_at', 'uuid', 'name', 'type',
            'control_attributes', 'reserved', 'on_maintenance',
            'failover_segment_id',
        ]
        # fake host list
        self.dummy_hosts = []
        self.dummy_hosts.append(FakeHosts(
            name='host_name',
            uuid='124aa63c-bbe1-46c3-91a9-285fac7d86c6'))
        # fake host show
        self.dummy_host = FakeHost()

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_uuid(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(
            segment_id='187dd15a-9c1d-4bf7-9f6c-014d5bc66992',
            host='124aa63c-bbe1-46c3-91a9-285fac7d86c6',
            reserved=True)
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value = self.dummy_host
        # show the host specified by uuid
        self.update_host.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_host.to_dict(), self.columns, formatters={})

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_name(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(
            segment_id='187dd15a-9c1d-4bf7-9f6c-014d5bc66992',
            host='host_name',
            reserved=True)
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value = self.dummy_host
        # show the host specified by name
        self.update_host.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_host.to_dict(), self.columns, formatters={})


class TestV1DeleteHost(base.TestCase):
    def setUp(self):
        super(TestV1DeleteHost, self).setUp()

        self.app = mock.Mock()
        self.app_args = mock.Mock()
        self.delete_host = DeleteHost(self.app, self.app_args,
                                      cmd_name='host update')
        self.client_manager = mock.Mock()
        self.app.client_manager.ha = self.client_manager
        self.columns = [
            'created_at', 'updated_at', 'uuid', 'name', 'type',
            'control_attributes', 'reserved', 'on_maintenance',
            'failover_segment_id',
        ]
        # fake host list
        self.dummy_hosts = []
        self.dummy_hosts.append(FakeHosts(
            name='host_name',
            uuid='124aa63c-bbe1-46c3-91a9-285fac7d86c6'))
        # fake host show
        self.dummy_host = FakeHost()

    def test_take_action_by_uuid(self):

        # command param
        parsed_args = FakeNamespace(
            segment_id='187dd15a-9c1d-4bf7-9f6c-014d5bc66992',
            host='124aa63c-bbe1-46c3-91a9-285fac7d86c6')
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value =\
            self.dummy_host
        # show the host specified by uuid
        self.delete_host.take_action(parsed_args)

    def test_take_action_by_name(self):

        # command param
        parsed_args = FakeNamespace(
            segment_id='187dd15a-9c1d-4bf7-9f6c-014d5bc66992',
            host='host_name')
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value =\
            self.dummy_host
        # show the host specified by name
        self.delete_host.take_action(parsed_args)
