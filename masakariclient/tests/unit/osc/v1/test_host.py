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
from unittest import mock
import uuid

from osc_lib import utils

from masakariclient.osc.v1.host import DeleteHost
from masakariclient.osc.v1.host import ShowHost
from masakariclient.osc.v1.host import UpdateHost
from masakariclient.tests import base

HOST_NAME = 'host_name'
HOST_ID = uuid.uuid4()
SEGMENT_NAME = 'segment_name'
SEGMENT_ID = uuid.uuid4()


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


class FakeSegments(object):
    """Fake segment show detail."""
    def __init__(self, name=None, uuid=None):
        super(FakeSegments, self).__init__()
        self.name = name
        self.uuid = uuid


class FakeHost(object):
    """Fake segment show detail."""
    def __init__(self,):
        super(FakeHost, self).__init__()

    def to_dict(self):
        return {
            'reserved': 'False',
            'uuid': HOST_ID,
            'on_maintenance': False,
            'created_at': '2016-12-18T05:47:55.000000',
            'control_attributes': 'control_attributes',
            'updated_at': None,
            'name': HOST_NAME,
            'type': 'auto',
            'id': 18,
            'failover_segment_id': SEGMENT_ID,
            }


class BaseV1Host(base.TestCase):
    def setUp(self):
        super(BaseV1Host, self).setUp()

        self.app = mock.Mock()
        self.app_args = mock.Mock()
        self.client_manager = mock.Mock()
        self.app.client_manager.ha = self.client_manager
        self.columns = [
            'created_at', 'updated_at', 'uuid', 'name', 'type',
            'control_attributes', 'reserved', 'on_maintenance',
            'failover_segment_id',
        ]
        # fake host list
        self.dummy_hosts = [FakeHosts(name=HOST_NAME, uuid=HOST_ID)]
        # fake segment list
        self.dummy_segments = [FakeSegments(name=SEGMENT_NAME,
                                            uuid=SEGMENT_ID)]
        # fake host show
        self.dummy_host = FakeHost()


class TestV1ShowHost(BaseV1Host):
    def setUp(self):
        super(TestV1ShowHost, self).setUp()
        self.show_host = ShowHost(self.app, self.app_args,
                                  cmd_name='host show')

    def test_take_action_by_uuid(self):

        # command param
        parsed_args = FakeNamespace(segment_id=SEGMENT_ID, host=HOST_ID)
        self._test_take_action(parsed_args)

    def test_take_action_by_name(self):

        # command param
        parsed_args = FakeNamespace(segment_id=SEGMENT_ID, host=HOST_NAME)
        self._test_take_action(parsed_args)

    @mock.patch.object(utils, 'get_dict_properties')
    def _test_take_action(self, parsed_args, mock_get_dict_properties):
        # return value segment list
        self.app.client_manager.ha.segments.return_value = self.dummy_segments
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value = self.dummy_host

        # show the host specified by uuid
        self.show_host.take_action(parsed_args)
        self.app.client_manager.ha.get_host.assert_called_once_with(
            HOST_ID, segment_id=SEGMENT_ID)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_host.to_dict(), self.columns, formatters={})


class TestV1UpdateHost(BaseV1Host):
    def setUp(self):
        super(TestV1UpdateHost, self).setUp()
        self.update_host = UpdateHost(self.app, self.app_args,
                                      cmd_name='host update')

    def test_take_action_by_uuid(self):

        # command param
        parsed_args = FakeNamespace(
            segment_id=SEGMENT_ID, host=HOST_ID, reserved=True)
        self._test_take_action(parsed_args)

    def test_take_action_by_name(self):

        # command param
        parsed_args = FakeNamespace(
            segment_id=SEGMENT_ID, host=HOST_NAME, reserved=True)
        self._test_take_action(parsed_args)

    @mock.patch.object(utils, 'get_dict_properties')
    def _test_take_action(self, parsed_args, mock_get_dict_properties):
        # return value segment list
        self.app.client_manager.ha.segments.return_value = self.dummy_segments
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.get_host.return_value = self.dummy_host
        # show the host specified by uuid
        self.update_host.take_action(parsed_args)
        self.app.client_manager.ha.update_host.assert_called_once_with(
            HOST_ID, segment_id=SEGMENT_ID, reserved=True)
        self.app.client_manager.ha.get_host.assert_called_once_with(
            HOST_ID, segment_id=SEGMENT_ID)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_host.to_dict(), self.columns, formatters={})


class TestV1DeleteHost(BaseV1Host):
    def setUp(self):
        super(TestV1DeleteHost, self).setUp()
        self.delete_host = DeleteHost(self.app, self.app_args,
                                      cmd_name='host delete')

    def test_take_action_by_uuid(self):

        # command param
        parsed_args = FakeNamespace(segment_id=SEGMENT_ID, host=HOST_ID)
        self._test_take_action(parsed_args)

    def test_take_action_by_name(self):

        # command param
        parsed_args = FakeNamespace(segment_id=SEGMENT_ID, host=HOST_NAME)
        self._test_take_action(parsed_args)

    def _test_take_action(self, parsed_args):
        # return value segment list
        self.app.client_manager.ha.segments.return_value = self.dummy_segments
        # return value host list
        self.app.client_manager.ha.hosts.return_value = self.dummy_hosts
        # return value host show
        self.app.client_manager.ha.delete_host.return_value = None
        # show the host specified by uuid
        self.delete_host.take_action(parsed_args)

        self.app.client_manager.ha.delete_host.assert_called_once_with(
            HOST_ID, segment_id=SEGMENT_ID, ignore_missing=False)
