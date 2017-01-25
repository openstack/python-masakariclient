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

from masakariclient.common import utils
from masakariclient.tests import base
import masakariclient.v1.shell as ms


class TestV1Shell(base.TestCase):

    def setUp(self):
        super(TestV1Shell, self).setUp()
        self.notification_vals = {
            'notification_uuid': 'b3bf75d7-c2e9-4023-a10b-e5b464b9b539',
            'source_host_uuid': '68fa7386-983e-4497-b5c4-3780f774d302',
            'created_at': '2016-11-15T12:24:39.000000',
            'updated_at': None,
            'payload': {'event': 'STOPPED'},
            'generated_time': '2016-10-10T10:00:00.000000',
            'type': 'VM',
            'id': '27'}

        self.segment_vals = {
            'uuid': '870da19d-37ec-41d2-a4b2-7be54b0d6ec9',
            'created_at': '2016-11-17T10:08:32.000000',
            'recovery_method': 'auto',
            'updated_at': '2016-11-17T10:09:56.000000',
            'name': 'testsegment05',
            'service_type': 'testsegment01_auto',
            'id': '14',
            'description': 'UPDATE Discription'}

        self.hosts_vals = {
            'reserved': False,
            'uuid': '0951e72c-49f5-46aa-8465-2d61ed3b46d9',
            'deleted': False,
            'on_maintenance': False,
            'created_at': '2016-11-29T11:10:51.000000',
            'control_attributes': 'control-attributesX',
            'updated_at': '2016-11-29T11:30:18.000000',
            'name': 'new_host-3',
            'failover_segment': {
                'uuid': '6b985a8a-f8c0-42e4-beaa-d2fcd8dabbb6',
                'deleted': False,
                'created_at': '2016-11-16T04:46:38.000000',
                'description': None,
                'recovery_method': 'auto',
                'updated_at': None,
                'service_type': 'testsegment01_auto',
                'deleted_at': None,
                'id': 3,
                'name': 'testsegment01'},
            'deleted_at': None,
            'type': 'typeX',
            'id': 10,
            'failover_segment_id': '6b985a8a-f8c0-42e4-beaa-d2fcd8dabbb6'}

    @mock.patch.object(utils, 'print_list')
    def test_do_notification_list(self, mock_print_list):
        service = mock.Mock()
        service.notifications.return_value = self.notification_vals
        args = mock.Mock()
        columns = [
            'notification_uuid',
            'generated_time',
            'status',
            'source_host_uuid',
            'type']

        ms.do_notification_list(service, args)

        mock_print_list.assert_called_once_with(
            self.notification_vals,
            columns)

    @mock.patch.object(utils, 'print_list')
    def test_do_segment_list(self, mock_print_list):
        service = mock.Mock()
        service.segments.return_value = self.segment_vals
        args = mock.Mock()
        columns = [
            'uuid',
            'name',
            'description',
            'service_type',
            'recovery_method']

        ms.do_segment_list(service, args)

        mock_print_list.assert_called_once_with(
            self.segment_vals,
            columns)

    @mock.patch.object(utils, 'print_list')
    def test_do_host_list(self, mock_print_list):
        service = mock.Mock()
        service.hosts.return_value = self.hosts_vals
        args = mock.Mock()
        columns = [
            'control_attributes',
            'failover_segment_id',
            'name',
            'on_maintenance',
            'type',
            'uuid']

        ms.do_host_list(service, args)

        mock_print_list.assert_called_once_with(
            self.hosts_vals,
            columns)
