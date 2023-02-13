# Copyright(c) 2022 Inspur
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

from unittest import mock
import uuid

from osc_lib import utils

from masakariclient.osc.v1.vmove import ShowVMove
from masakariclient.tests import base

VMOVE_ID = uuid.uuid4()
NOTIFICATION_ID = uuid.uuid4()
SERVER_ID = uuid.uuid4()


class FakeNamespace(object):
    """Fake parser object."""
    def __init__(self, notification_id=None, vmove_id=None):
        super(FakeNamespace, self).__init__()
        self.notification_id = notification_id
        self.vmove_id = vmove_id


class FakeVMove(object):
    """Fake notification show detail."""
    def __init__(self,):
        super(FakeVMove, self).__init__()

    def to_dict(self):
        return {
            'created_at': '2023-01-28T14:55:27.000000',
            'uuid': VMOVE_ID,
            'notification_id': NOTIFICATION_ID,
            'server_id': SERVER_ID,
            'server_name': 'test',
            'source_host': 'host1',
            'dest_host': 'host2',
            'start_time': '2023-01-28T14:55:27.000000',
            'end_time': "2023-01-28T14:55:31.000000",
            'status': 'succeeded',
            'type': 'evacuation',
            'message': None,
            }


class BaseV1VMove(base.TestCase):
    def setUp(self):
        super(BaseV1VMove, self).setUp()

        self.app = mock.Mock()
        self.app_args = mock.Mock()
        self.client_manager = mock.Mock()
        self.app.client_manager.ha = self.client_manager
        self.columns = [
            'created_at', 'updated_at',
            'uuid', 'server_id', 'server_name',
            'source_host', 'dest_host',
            'start_time', 'end_time',
            'type', 'status', 'message'
        ]
        self.dummy_vmove = FakeVMove()


class TestV1ShowVMove(BaseV1VMove):
    def setUp(self):
        super(TestV1ShowVMove, self).setUp()
        self.show_vmove = ShowVMove(self.app, self.app_args,
                                    cmd_name='vmove show')

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action(self, mock_get_dict_properties):
        parsed_args = FakeNamespace(notification_id=NOTIFICATION_ID,
                                    vmove_id=VMOVE_ID)
        self.app.client_manager.ha.get_vmove.return_value = self.dummy_vmove

        # show the vmove specified by uuid
        self.show_vmove.take_action(parsed_args)
        self.app.client_manager.ha.get_vmove.assert_called_once_with(
            VMOVE_ID, NOTIFICATION_ID)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_vmove.to_dict(), self.columns, formatters={})
