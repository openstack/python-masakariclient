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

import ddt
import uuid

from osc_lib.tests import utils as osc_lib_utils
from osc_lib import utils

from masakariclient.osc.v1.segment import CreateSegment
from masakariclient.osc.v1.segment import DeleteSegment
from masakariclient.osc.v1.segment import ShowSegment
from masakariclient.osc.v1.segment import UpdateSegment
from masakariclient.tests import base

SEGMENT_NAME = 'segment_name'
SEGMENT_ID = uuid.uuid4()


class FakeNamespace(object):
    """Fake parser object."""
    def __init__(self, segment=None, name=None,
                 description=None,
                 recovery_method=None, service_type=None):
        super(FakeNamespace, self).__init__()
        self.segment = segment
        self.name = name
        self.description = description
        self.recovery_method = recovery_method
        self.service_type = service_type


class FakeSegments(object):
    """Fake segment list."""
    def __init__(self, name=None, uuid=None,
                 description=None,
                 recovery_method=None, service_type=None):
        super(FakeSegments, self).__init__()
        self.name = name
        self.uuid = uuid
        self.description = description
        self.recovery_method = recovery_method
        self.service_type = service_type


class FakeSegment(object):
    """Fake segment show detail."""
    def __init__(self,):
        super(FakeSegment, self).__init__()

    def to_dict(self):
        return {
            'created_at': '2016-12-18T05:47:46.000000',
            'updated_at': '2016-12-18T06:05:16.000000',
            'uuid': SEGMENT_ID,
            'name': SEGMENT_NAME,
            'description': 'test_segment_description',
            'id': 1,
            'service_type': 'test_type',
            'recovery_method': 'auto',
            }


class BaseV1Segment(base.TestCase):
    def setUp(self):
        super(BaseV1Segment, self).setUp()

        self.app = mock.Mock()
        self.app_args = mock.Mock()
        self.client_manager = mock.Mock()
        self.client_manager.default_microversion = '1.0'
        self.app.client_manager.ha = self.client_manager
        # segment data setup
        self.dummy_segment = FakeSegment()


class TestV1ShowSegment(BaseV1Segment):
    def setUp(self):
        super(TestV1ShowSegment, self).setUp()

        self.show_seg = ShowSegment(self.app,
                                    self.app_args,
                                    cmd_name='segment show')
        self.columns = ['created_at', 'updated_at', 'uuid',
                        'name', 'description', 'id', 'service_type',
                        'recovery_method',
                        ]
        # return value segment list
        self.dummy_segments = [FakeSegments(name=SEGMENT_NAME,
                                            uuid=SEGMENT_ID)]

    def test_take_action_by_uuid(self):

        # command param
        parsed_args = FakeNamespace(segment=SEGMENT_ID)
        self._test_take_action(parsed_args)

    def test_take_action_by_name(self):

        # command param
        parsed_args = FakeNamespace(segment=SEGMENT_NAME)
        self._test_take_action(parsed_args)

    @mock.patch.object(utils, 'get_dict_properties')
    def _test_take_action(self, parsed_args, mock_get_dict_properties):
        # return value segment list
        self.app.client_manager.ha.segments.return_value = self.dummy_segments
        # return value segment show
        self.app.client_manager.ha.get_segment.return_value = (
            self.dummy_segment)
        # show segment
        self.show_seg.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_segment.to_dict(), self.columns, formatters={})


class TestV1UpdateSegment(BaseV1Segment, osc_lib_utils.TestCommand):
    def setUp(self):
        super(TestV1UpdateSegment, self).setUp()

        self.update_seg = UpdateSegment(self.app,
                                        self.app_args,
                                        cmd_name='segment update')
        self.columns = ['created_at', 'updated_at', 'uuid',
                        'name', 'description', 'id', 'service_type',
                        'recovery_method',
                        ]
        # segment list
        self.dummy_segments = [
            FakeSegments(
                name=SEGMENT_NAME, uuid=SEGMENT_ID,
                description='FakeNamespace_description',
                recovery_method='Update_recovery_method',
                service_type='test_type')]
        self.dummy_segments.append(FakeSegments(
            name=SEGMENT_NAME, uuid=SEGMENT_ID,
            description='FakeNamespace_description',
            recovery_method='Update_recovery_method',
            service_type='test_type'))

    def test_take_action_by_uuid(self):

        # command param
        arglist = ['8c35987c-f416-46ca-be37-52f58fd8d294',
                   '--name', 'test_segment',
                   '--recovery_method', 'rh_priority',
                   '--service_type', 'test_service',
                   '--description', 'test_segment']

        parsed_args = self.check_parser(self.update_seg, arglist, [])
        self._test_take_action(parsed_args)

    def test_take_action_by_name(self):

        # command param
        arglist = [SEGMENT_NAME, '--name', 'test_segment',
                                 '--recovery_method', 'auto_priority',
                                 '--service_type', 'test_service',
                                 '--description', 'test_segment']

        parsed_args = self.check_parser(self.update_seg, arglist, [])
        self._test_take_action(parsed_args)

    def test_update_segment_with_recovery_method_reserved_host(self):

        arglist = ['8c35987c-f416-46ca-be37-52f58fd8d294',
                   '--name', 'test_segment',
                   '--recovery_method', 'reserved_host',
                   '--service_type', 'test_service',
                   '--description', 'test_segment']

        parsed_args = self.check_parser(self.update_seg, arglist, [])
        self._test_take_action(parsed_args)

    @mock.patch.object(utils, 'get_dict_properties')
    def _test_take_action(self, parsed_args, mock_get_dict_properties):
        # return value segment list
        self.app.client_manager.ha.segments.return_value = self.dummy_segments
        # return value segment data setup
        self.app.client_manager.ha.get_segment.return_value = (
            self.dummy_segment)
        # segment update
        self.update_seg.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_segment.to_dict(), self.columns, formatters={})

    def test_update_with_invalid_recovery_method(self):
        arglist = [SEGMENT_NAME, '--name', 'test_segment',
                   '--recovery_method', 'invalid-rcovery-method',
                   '--service_type', 'test_service',
                   '--description', 'test_segment']
        self.assertRaises(osc_lib_utils.ParserException,
                          self.check_parser, self.update_seg, arglist, [])


class TestV1DeleteSegment(BaseV1Segment):
    def setUp(self):
        super(TestV1DeleteSegment, self).setUp()

        self.delete_seg = DeleteSegment(self.app,
                                        self.app_args,
                                        cmd_name='segment delete')
        # segment list
        self.dummy_segments = [
            FakeSegments(
                name=SEGMENT_NAME, uuid=SEGMENT_ID,
                description='FakeNamespace_description',
                recovery_method='Update_recovery_method',
                service_type='test_type')]

    def test_take_action_by_uuid(self):

        # command param
        parsed_args = FakeNamespace(segment=[SEGMENT_ID])
        self._test_take_action(parsed_args)

    def test_take_action_by_name(self):

        # command param
        parsed_args = FakeNamespace(segment=[SEGMENT_NAME])
        self._test_take_action(parsed_args)

    def _test_take_action(self, parsed_args):

        # return_value segment list
        self.app.client_manager.ha.segments.return_value = self.dummy_segments

        # return_value segment delete
        self.app.client_manager.ha.delete_segment.return_value = None

        # segment delete
        self.delete_seg.take_action(parsed_args)

        self.app.client_manager.ha.delete_segment.assert_called_once_with(
            SEGMENT_ID, False)


@ddt.ddt
class TestV1CreateSegment(BaseV1Segment, osc_lib_utils.TestCommand):

    def setUp(self):
        super(TestV1CreateSegment, self).setUp()
        self.cmd = CreateSegment(self.app, None)

    @ddt.data({"recovery_method": "auto"},
              {"recovery_method": "reserved_host"},
              {"recovery_method": "auto_priority"},
              {"recovery_method": "rh_priority"})
    def test_create_with_all_recovery_methods(self, ddt_data):
        arglist = ['test_segment', ddt_data['recovery_method'], 'test_service',
                   '--description', 'test_segment']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self._test_take_action(parsed_args, arglist)

    def _test_take_action(self, parsed_args, arglist):
        # return value segment list
        self.app.client_manager.ha.segments.return_value = arglist
        # return value segment data setup
        self.app.client_manager.ha.get_segment.return_value = (
            self.dummy_segment)
        self.cmd.take_action(parsed_args)
        self.app.client_manager.ha.create_segment.assert_called_with(
            description='test_segment',
            name='test_segment',
            recovery_method=arglist[1],
            service_type='test_service')

    def test_create_segment_recovery_method_invalid(self):
        arglist = ['test_segment', 'invalid_recovery_method', 'test_service',
                   '--description', 'test_segment']
        self.assertRaises(osc_lib_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])
