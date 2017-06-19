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
import uuid

from osc_lib import utils

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

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_uuid(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(segment=SEGMENT_ID)
        # return value segment list
        self.app.client_manager.ha.segments.return_value =\
            self.dummy_segments
        # return value segment show
        self.app.client_manager.ha.get_segment.return_value =\
            self.dummy_segment
        # show segment
        self.show_seg.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_segment.to_dict(), self.columns, formatters={})

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_name(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(segment=SEGMENT_NAME)
        # return value segment list
        self.app.client_manager.ha.segments.return_value =\
            self.dummy_segments
        # return value segment show
        dummy_segment = FakeSegment()
        self.app.client_manager.ha.get_segment.return_value =\
            dummy_segment
        # show segment
        self.show_seg.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            dummy_segment.to_dict(), self.columns, formatters={})


class TestV1UpdateSegment(BaseV1Segment):
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

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_uuid(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(
            segment=SEGMENT_ID,
            description='FakeNamespace_description')
        # return value segment list
        self.app.client_manager.ha.segments.return_value =\
            self.dummy_segments
        # return value segment data setup
        self.app.client_manager.ha.get_segment.return_value =\
            self.dummy_segment
        # segment update
        self.update_seg.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_segment.to_dict(), self.columns, formatters={})

    @mock.patch.object(utils, 'get_dict_properties')
    def test_take_action_by_name(self, mock_get_dict_properties):

        # command param
        parsed_args = FakeNamespace(segment=SEGMENT_NAME)
        # return value segment list
        self.app.client_manager.ha.segments.return_value =\
            self.dummy_segments
        # return value segment data setup
        self.app.client_manager.ha.get_segment.return_value =\
            self.dummy_segment
        # segment update
        self.update_seg.take_action(parsed_args)
        mock_get_dict_properties.assert_called_once_with(
            self.dummy_segment.to_dict(), self.columns, formatters={})


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

        # return_value segment list
        self.app.client_manager.ha.segments.return_value =\
            self.dummy_segments

        # return_value segment delete
        self.app.client_manager.ha.delete_segment.return_value = None

        # segment delete
        self.delete_seg.take_action(parsed_args)

        self.app.client_manager.ha.delete_segment.assert_called_once_with(
            SEGMENT_ID, False)

    def test_take_action_by_name(self):

        # command param
        parsed_args = FakeNamespace(segment=[SEGMENT_NAME])

        # return_value segment list
        self.app.client_manager.ha.segments.return_value =\
            self.dummy_segments

        # return_value segment delete
        self.app.client_manager.ha.delete_segment.return_value = None

        # segment delete
        self.delete_seg.take_action(parsed_args)

        self.app.client_manager.ha.delete_segment.assert_called_once_with(
            SEGMENT_ID, False)
