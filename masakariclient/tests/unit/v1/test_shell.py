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

import ddt
import mock
import six
import sys

from openstack import exceptions as sdk_exc
from openstack.instance_ha.v1 import _proxy

from masakariclient.common.i18n import _
from masakariclient.common import utils
from masakariclient import shell
from masakariclient.tests import base
from masakariclient.tests.unit.v1 import fakes
import masakariclient.v1.shell as ms


@ddt.ddt
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
        self.hosts_object = fakes.FakeHost(self.hosts_vals)

    def _run_command(self, cmd):
        shell.main(cmd.split())

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

    @mock.patch.object(utils, 'print_dict')
    @mock.patch.object(utils, 'get_uuid_by_name')
    def test_do_segment_show(self, mock_get_uuid_by_name, mock_print_dict):
        mock_get_uuid_by_name.return_value = self.segment_vals.get('uuid')
        service = mock.Mock()
        segment_object = fakes.FakeSegment(self.segment_vals)
        service.get_segment.return_value = segment_object
        args = mock.Mock()

        ms.do_segment_show(service, args)
        mock_get_uuid_by_name.assert_called_once_with(service, args.id)
        mock_print_dict.assert_called_once_with(self.segment_vals)

    @mock.patch.object(utils, 'print_dict')
    @ddt.data({"recovery_method": "auto"},
              {"recovery_method": "reserved_host"},
              {"recovery_method": "auto_priority"},
              {"recovery_method": "rh_priority"})
    def test_do_segment_create_with_all_recovery_methods(
            self, ddt_data, mock_print_dict):
        service = mock.Mock()
        args = mock.Mock()
        self.segment_vals['recovery_method'] = ddt_data['recovery_method']
        segment_object = fakes.FakeSegment(self.segment_vals)
        service.create_segment.return_value = segment_object
        self._run_command(
            "segment-create "
            "--name 'test-segment'"
            " --recovery-method %s "
            "--service-type test_service" % ddt_data['recovery_method'])
        ms.do_segment_create(service, args)
        mock_print_dict.assert_called_once_with(
            self.segment_vals)

    def test_do_segment_create_with_invalid_recovery_method(self):
        cmd = ("segment-create --name 'test-segment' --recovery-method"
               " invalid_recovery_method --service-type test_service")
        self.assertRaises(SystemExit, self._run_command, cmd)

    @mock.patch.object(utils, 'print_dict')
    @mock.patch.object(utils, 'remove_unspecified_items')
    @mock.patch.object(utils, 'get_uuid_by_name')
    @ddt.data({"recovery_method": "auto"},
              {"recovery_method": "reserved_host"},
              {"recovery_method": "auto_priority"},
              {"recovery_method": "rh_priority"})
    def test_do_segment_update(self, ddt_data,
                               mock_get_uuid_by_name,
                               mock_remove_unspecified_items,
                               mock_print_dict):
        mock_get_uuid_by_name.return_value = self.segment_vals.get('uuid')
        self.segment_vals['recovery_method'] = ddt_data['recovery_method']
        mock_remove_unspecified_items.return_value = self.segment_vals
        service = mock.Mock()
        segment_object = fakes.FakeSegment(self.segment_vals)
        service.update_segment.return_value = segment_object
        args = mock.Mock()
        args.recovery_method = ddt_data['recovery_method']
        ms.do_segment_update(service, args)
        mock_get_uuid_by_name.assert_called_once_with(service, args.id)
        attrs = {
            'name': args.name,
            'description': args.description,
            'recovery_method': args.recovery_method,
            'service_type': args.service_type,
        }
        mock_remove_unspecified_items.assert_called_once_with(attrs)
        mock_print_dict.assert_called_once_with(self.segment_vals)

    def test_do_segment_update_with_invalid_recovery_method(self):
        cmd = ("segment-update --id bdba001e-c01b-490e-9405-fdf72d849b41 "
               "--recovery-method invalid_recovery_method")
        self.assertRaises(SystemExit, self._run_command, cmd)

    @mock.patch.object(utils, 'print_dict')
    @mock.patch.object(utils, 'get_uuid_by_name')
    def test_do_segment_delete(self, mock_get_uuid_by_name, mock_print_dict):
        mock_get_uuid_by_name.return_value = self.segment_vals.get('uuid')
        service = mock.Mock()
        segment_object = fakes.FakeSegment(self.segment_vals)
        service.delete_segment.return_value = segment_object
        args = mock.Mock()

        ms.do_segment_delete(service, args)
        mock_get_uuid_by_name.assert_called_once_with(service, args.id)
        mock_print_dict.assert_called_once_with(self.segment_vals)

    @mock.patch.object(utils, 'get_uuid_by_name')
    @mock.patch.object(_proxy.Proxy, 'delete_segment')
    def test_do_segment_delete_with_non_existing_uuid(
            self, mock_get_uuid_by_name, mock_delete_segment):
        mock_get_uuid_by_name.return_value = self.segment_vals.get('uuid')

        expected_msg = _("No failover segment with "
                         "id (%s)") % mock_get_uuid_by_name

        def fake_delete_segment(self, mock_get_uuid_by_name,
                                ignore_missing=False):
            if not ignore_missing:
                raise sdk_exc.ResourceNotFound(expected_msg)

        mock_delete_segment.side_effect = fake_delete_segment
        service = mock.Mock()
        args = mock.Mock()

        original = sys.stdout
        sys.stdout = six.StringIO()
        ms.do_segment_delete(service, args)
        output = sys.stdout.getvalue()
        sys.stdout = original
        self.assertIn(expected_msg, output)

    @mock.patch.object(utils, 'print_list')
    @mock.patch.object(utils, 'get_uuid_by_name')
    def test_do_host_list(self, mock_get_uuid_by_name, mock_print_list):
        mock_get_uuid_by_name.return_value = self.segment_vals.get('uuid')
        service = mock.Mock()
        service.hosts.return_value = self.hosts_vals
        args = mock.Mock()
        columns = [
            'uuid',
            'name',
            'type',
            'control_attributes',
            'reserved',
            'on_maintenance',
            'failover_segment_id']

        ms.do_host_list(service, args)

        mock_get_uuid_by_name.assert_called_once_with(service, args.segment_id)
        mock_print_list.assert_called_once_with(
            self.hosts_vals,
            columns)

    @mock.patch.object(utils, 'print_dict')
    @mock.patch.object(utils, 'get_uuid_by_name')
    def test_do_host_show(self, mock_get_uuid_by_name, mock_print_dict):
        mock_get_uuid_by_name.side_effect = [self.segment_vals.get('uuid'),
                                             self.hosts_vals.get('uuid')]
        service = mock.Mock()
        service.get_host.return_value = self.hosts_object
        args = mock.Mock()

        ms.do_host_show(service, args)
        mock_get_uuid_by_name.assert_any_call(service, args.segment_id)
        mock_get_uuid_by_name.assert_any_call(
            service, args.id, segment=self.segment_vals.get('uuid'))
        mock_print_dict.assert_called_once_with(self.hosts_vals)

    @mock.patch.object(utils, 'print_dict')
    @mock.patch.object(utils, 'remove_unspecified_items')
    @mock.patch.object(utils, 'get_uuid_by_name')
    def test_do_host_create(self,
                            mock_get_uuid_by_name,
                            mock_remove_unspecified_items,
                            mock_print_dict):
        mock_get_uuid_by_name.return_value = self.hosts_vals.get('uuid')
        mock_remove_unspecified_items.return_value = self.hosts_vals
        service = mock.Mock()
        service.create_host.return_value = self.hosts_object
        args = mock.Mock()

        ms.do_host_create(service, args)
        mock_get_uuid_by_name.assert_called_once_with(service, args.segment_id)
        attrs = {
            'name': args.name,
            'type': args.type,
            'control_attributes': args.control_attributes,
            'reserved': args.reserved,
            'on_maintenance': args.on_maintenance,
        }
        mock_remove_unspecified_items.assert_called_once_with(attrs)
        mock_print_dict.assert_called_once_with(self.hosts_vals)

    @mock.patch.object(utils, 'print_dict')
    @mock.patch.object(utils, 'remove_unspecified_items')
    @mock.patch.object(utils, 'get_uuid_by_name')
    def test_do_host_update(self,
                            mock_get_uuid_by_name,
                            mock_remove_unspecified_items,
                            mock_print_dict):
        mock_get_uuid_by_name.side_effect = [self.segment_vals.get('uuid'),
                                             self.hosts_vals.get('uuid')]
        mock_remove_unspecified_items.return_value = self.hosts_vals
        service = mock.Mock()
        service.update_host.return_value = self.hosts_object
        args = mock.Mock()

        ms.do_host_update(service, args)
        mock_get_uuid_by_name.assert_any_call(service, args.segment_id)
        mock_get_uuid_by_name.assert_any_call(
            service, args.id, segment=self.segment_vals.get('uuid'))
        attrs = {
            'name': args.name,
            'type': args.type,
            'control_attributes': args.control_attributes,
            'reserved': args.reserved,
            'on_maintenance': args.on_maintenance,
        }
        mock_remove_unspecified_items.assert_called_once_with(attrs)
        mock_print_dict.assert_called_once_with(self.hosts_vals)

    @mock.patch.object(utils, 'print_dict')
    @mock.patch.object(utils, 'get_uuid_by_name')
    def test_do_host_delete(self, mock_get_uuid_by_name, mock_print_dict):
        mock_get_uuid_by_name.side_effect = [self.segment_vals.get('uuid'),
                                             self.hosts_vals.get('uuid')]
        service = mock.Mock()
        service.delete_host.return_value = self.hosts_object
        args = mock.Mock()

        ms.do_host_delete(service, args)
        mock_get_uuid_by_name.assert_any_call(service, args.segment_id)
        mock_get_uuid_by_name.assert_any_call(
            service, args.id, segment=self.segment_vals.get('uuid'))
        mock_print_dict.assert_called_once_with(self.hosts_vals)

    @mock.patch.object(utils, 'get_uuid_by_name')
    @mock.patch.object(_proxy.Proxy, 'delete_host')
    def test_do_host_delete_with_non_existing_uuid(self,
                                                   mock_get_uuid_by_name,
                                                   mock_delete_host):
        mock_get_uuid_by_name.return_value = self.segment_vals.get('uuid')
        host_id = self.hosts_vals.get('uuid')
        expected_msg = _("Host '%(host_id)s' under failover_segment " "'"
                         "%(seg_id)s' ""could not be found") % {
            'host_id': host_id, 'seg_id': mock_get_uuid_by_name}

        def fake_delete_host(
                host_id, mock_get_uuid_by_name, ignore_missing=False):
            if not ignore_missing:
                raise sdk_exc.ResourceNotFound(expected_msg)

        mock_delete_host.side_effect = fake_delete_host
        service = mock.Mock()
        args = mock.Mock()

        original = sys.stdout
        sys.stdout = six.StringIO()
        ms.do_host_delete(service, args)
        output = sys.stdout.getvalue()
        sys.stdout = original
        self.assertIn(expected_msg, output)
