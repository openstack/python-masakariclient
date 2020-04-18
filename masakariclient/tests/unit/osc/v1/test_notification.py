# Copyright(c) 2019 NTT DATA
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

from osc_lib.tests import utils as osc_lib_utils
from osc_lib import utils

from masakariclient.osc.v1.notification import ShowNotification
from masakariclient.tests import base

NOTIFICATION_NAME = 'notification_name'
NOTIFICATION_ID = uuid.uuid4()
RECOVERY_WORKFLOW_DETAILS = [{
    "progress": 1.0, "state": "SUCCESS",
    "name": "DisableComputeNodeTask",
    "progress_details": [
        {"timestamp:": "2019-02-28 07:21:33.170190",
         "progress": 0.5,
         "message": "Disabling compute host: host"},
        {"timestamp:": "2019-02-28 07:21:33.291810",
         "progress": 1.0,
         "message": "Skipping recovery for process nova-compute "
                    "as it is already disabled"}]}]


class FakeNotification(object):
    """Fake notification show detail."""
    def __init__(self,):
        super(FakeNotification, self).__init__()

    def to_dict(self):
        return {
            'created_at': '2019-02-18T05:47:46.000000',
            'updated_at': '2019-02-18T06:05:16.000000',
            'notification_uuid': NOTIFICATION_ID,
            'source_host_uuid': '9ab67dc7-110a-4a4c-af64-abc6e5798433',
            'name': NOTIFICATION_NAME,
            'id': 1,
            'type': 'VM',
            'payload': {
                "instance_uuid": "99ffc832-2252-4a9e-9b98-28bc70f7ff09",
                "vir_domain_event": "STOPPED_FAILED", "event": "LIFECYCLE"},
            'status': 'finished',
            'recovery_workflow_details': RECOVERY_WORKFLOW_DETAILS,
            'generated_time': '2019-02-13T15:34:55.000000'
            }


class BaseV1Notification(base.TestCase, osc_lib_utils.TestCommand):
    def setUp(self):
        super(BaseV1Notification, self).setUp()
        self.app = mock.Mock()
        self.app_args = mock.Mock()
        self.client_manager = mock.Mock()
        self.client_manager.default_microversion = '1.0'
        self.app.client_manager.ha = self.client_manager
        self.dummy_notification = FakeNotification()
        self.show_notification = ShowNotification(
            self.app, self.app_args, cmd_name='notification show')
        self.columns = ['created_at', 'updated_at', 'notification_uuid',
                        'type', 'status', 'source_host_uuid',
                        'generated_time', 'payload']


class TestShowNotificationV1(BaseV1Notification):

    def test_take_action_by_uuid(self):
        arglist = ['8c35987c-f416-46ca-be37-52f58fd8d294']
        parsed_args = self.check_parser(self.show_notification, arglist, [])
        self._test_take_action(parsed_args)

    @mock.patch.object(utils, 'get_dict_properties')
    def _test_take_action(self, parsed_args, mock_get_dict_properties):
        self.app.client_manager.ha.get_notification.return_value = (
            self.dummy_notification)

        self.show_notification.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_notification.to_dict(), self.columns, formatters={})


class TestShowNotificationV1_1(TestShowNotificationV1):

    def setUp(self):
        super(TestShowNotificationV1_1, self).setUp()
        self.client_manager.default_microversion = '1.1'
        self.columns.append('recovery_workflow_details')
