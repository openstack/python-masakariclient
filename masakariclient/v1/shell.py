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


from oslo_serialization import jsonutils

from masakariclient.common import utils


def do_notification_list(service, args):
    """List notifications.

    :param service: service object.
    :param args: API args.
    """
    try:
        notifications = service.notifications()
        columns = [
            'notification_uuid', 'generated_time', 'status',
            'source_host_uuid', 'type']
        utils.print_list(notifications, columns)

    except Exception as e:
        print(e)


@utils.arg('--id', metavar='<NOTIFICATION_ID>', required=True,
           help='Notification to display (name or ID)')
def do_notification_show(service, args):
    """Show a notification details."""
    try:
        notification = service.get_notification(args.id)
        utils.print_dict(notification.to_dict())

    except Exception as e:
        print(e)


@utils.arg('--type', metavar='<TYPE>', required=True,
           choices=['COMPUTE_HOST', 'VM', 'PROCESS'],
           help='Type of failure. The supported options are: '
                'COMPUTE_HOST, VM, PROCESS.')
@utils.arg('--hostname', metavar='<HOSTNAME>', required=True,
           help='Hostname of notification.')
@utils.arg('--generated-time', metavar='<GENERATED_TIME>', required=True,
           help='Timestamp for notification. e.g. 2016-01-01T01:00:00.000')
@utils.arg('--payload', metavar='<PAYLOAD>', required=True,
           help='JSON string about failure event.')
def do_notification_create(service, args):
    """Create a notification."""
    try:
        payload = jsonutils.loads(args.payload)
        attrs = {
            'type': args.type,
            'hostname': args.hostname,
            'generated_time': args.generated_time,
            'payload': payload,
        }
        notification = service.create_notification(**attrs)
        utils.print_dict(notification.to_dict())

    except Exception as e:
        print(e)


def do_segment_list(service, args):
    """List segments."""
    try:
        segments = service.segments()
        fields = [
            'uuid', 'name', 'description',
            'service_type', 'recovery_method']
        utils.print_list(segments, fields)
    except Exception as e:
        print(e)


@utils.arg('--id', metavar='<SEGMENT_ID>', required=True,
           help='Segment to display (name or ID)')
def do_segment_show(service, args):
    """Show a segment details."""
    try:
        segment_id = utils.get_uuid_by_name(service, args.id)
        segment = service.get_segment(segment_id)
        utils.print_dict(segment.to_dict())
    except Exception as e:
        print(e)


@utils.arg('--name', metavar='<SEGMENT_NAME>', required=True,
           help='Name of segment.')
@utils.arg('--recovery-method', metavar='<RECOVERY_METHOD>', required=True,
           choices=['auto', 'reserved_host', 'auto_priority', 'rh_priority'],
           help='Recovery method. '
                'The supported options are: auto, reserved_host,'
                ' auto_priority, rh_priority.')
@utils.arg('--service-type', metavar='<SERVICE_TYPE>', required=True,
           help='Service type of segment.')
@utils.arg('--description', metavar='<DESCRIPTION>', required=False,
           help='Description of segment.')
def do_segment_create(service, args):
    """Create segment."""
    try:
        attrs = {
            'name': args.name,
            'description': args.description,
            'recovery_method': args.recovery_method,
            'service_type': args.service_type,
        }
        segment = service.create_segment(**attrs)
        utils.print_dict(segment.to_dict())
    except Exception as e:
        print(e)


@utils.arg('--id', metavar='<SEGMENT_ID>',
           required=True, help='Name or ID of segment.')
@utils.arg('--name', metavar='<SEGMENT_NAME>',
           required=False, help='Name of segment.')
@utils.arg('--recovery-method', metavar='<RECOVERY_METHOD>',
           choices=['auto', 'reserved_host', 'auto_priority', 'rh_priority'],
           required=False,
           help='Recovery method. '
                'The supported options are: auto, reserved_host, '
                'auto_priority, rh_priority.')
@utils.arg('--service-type', metavar='<SERVICE_TYPE>',
           required=False, help='Service type of segment.')
@utils.arg('--description', metavar='<DESCRIPTION>',
           required=False, help='Description of segment.')
def do_segment_update(service, args):
    """Update a segment."""
    try:
        segment_id = utils.get_uuid_by_name(
            service, args.id)
        attrs = {
            'name': args.name,
            'description': args.description,
            'recovery_method': args.recovery_method,
            'service_type': args.service_type,
        }
        attrs = utils.remove_unspecified_items(attrs)
        segment = service.update_segment(segment_id, **attrs)
        utils.print_dict(segment.to_dict())
    except Exception as e:
        print(e)


@utils.arg('--id', metavar='<SEGMENT_ID>', required=True,
           help='Name or ID of the segment to delete.')
def do_segment_delete(service, args):
    """Delete a segment."""
    try:
        segment_id = utils.get_uuid_by_name(
            service, args.id)
        segment = service.delete_segment(segment_id, ignore_missing=False)
        utils.print_dict(segment.to_dict())
    except Exception as e:
        print(e)


@utils.arg('--segment-id', metavar='<SEGMENT_ID>', required=True,
           help='Segment to display (name or ID)')
def do_host_list(service, args):
    """List hosts."""
    try:
        segment_id = utils.get_uuid_by_name(
            service, args.segment_id)
        hosts = service.hosts(segment_id)
        fields = [
            'uuid', 'name', 'type', 'control_attributes', 'reserved',
            'on_maintenance', 'failover_segment_id']
        utils.print_list(hosts, fields)
    except Exception as e:
        print(e)


@utils.arg('--segment-id', metavar='<SEGMENT_ID>', required=True,
           help='Segment to display (name or ID)')
@utils.arg('--id', metavar='<HOST_ID>', required=True,
           help='Host to display (name or ID)')
def do_host_show(service, args):
    """Show a host details."""
    try:
        segment_id = utils.get_uuid_by_name(
            service, args.segment_id)
        host_id = utils.get_uuid_by_name(
            service, args.id, segment=segment_id)
        host = service.get_host(host_id, segment_id=segment_id)
        utils.print_dict(host.to_dict())
    except Exception as e:
        print(e)


@utils.arg('--name', metavar='<HOST_NAME>', required=True,
           help='Name of host.')
@utils.arg('--type', metavar='<TYPE>', required=True,
           help='Type of host.')
@utils.arg('--control-attributes', metavar='<CONTROL_ATTRIBUTES>',
           required=True, help='Control attributes of host.')
@utils.arg('--segment-id', metavar='<SEGMENT_ID>', required=True,
           help='Name or ID of segment.')
@utils.arg('--reserved', metavar='<RESERVED>', required=False,
           choices=['True', 'False'],
           help='Host reservation. The supported options are: True, False.')
@utils.arg('--on-maintenance', metavar='<ON_MAINTENANCE>', required=False,
           choices=['True', 'False'],
           help='Maintenance status of host. The supported options are: '
                'True, False.')
def do_host_create(service, args):
    """Create a host."""
    try:
        segment_id = utils.get_uuid_by_name(
            service, args.segment_id)
        attrs = {
            'name': args.name,
            'type': args.type,
            'control_attributes': args.control_attributes,
            'reserved': args.reserved,
            'on_maintenance': args.on_maintenance,
        }
        utils.remove_unspecified_items(attrs)
        host = service.create_host(segment_id, **attrs)
        utils.print_dict(host.to_dict())
    except Exception as e:
        print(e)


@utils.arg('--segment-id', metavar='<SEGMENT_ID>', required=True,
           help='Name or ID of segment.')
@utils.arg('--id', metavar='<HOST_ID>', required=True,
           help='Name or ID of host.')
@utils.arg('--reserved', metavar='<RESERVED>', required=False,
           choices=['True', 'False'],
           help='Host reservation. The supported options are: True, False.')
@utils.arg('--on-maintenance', metavar='<ON_MAINTENANCE>',
           required=False, choices=['True', 'False'],
           help='Maintenance status of host. The supported options are: '
                'True, False.')
@utils.arg('--name', metavar='<HOST_NAME>', required=False,
           help='Name of host.')
@utils.arg('--type', metavar='<TYPE>', required=False,
           help='Type of host.')
@utils.arg('--control-attributes', metavar='<CONTROL_ATTRIBUTES>',
           required=False, help='Control attributes of host.')
def do_host_update(service, args):
    """Update a host."""
    try:
        segment_id = utils.get_uuid_by_name(
            service, args.segment_id)
        host_id = utils.get_uuid_by_name(
            service, args.id, segment=segment_id)
        attrs = {
            'name': args.name,
            'type': args.type,
            'control_attributes': args.control_attributes,
            'reserved': args.reserved,
            'on_maintenance': args.on_maintenance,
        }
        attrs = utils.remove_unspecified_items(attrs)
        host = service.update_host(host_id, segment_id=segment_id, **attrs)
        utils.print_dict(host.to_dict())
    except Exception as e:
        print(e)


@utils.arg('--segment-id', metavar='<SEGMENT_ID>', required=True,
           help='Name or ID of segment.')
@utils.arg('--id', metavar='<HOST_ID>', required=True,
           help='Name or ID of the host to delete.')
def do_host_delete(service, args):
    """Delete a host."""
    try:
        segment_id = utils.get_uuid_by_name(
            service, args.segment_id)
        host_id = utils.get_uuid_by_name(
            service, args.id, segment=segment_id)
        host = service.delete_host(host_id, segment_id=segment_id,
                                   ignore_missing=False)
        utils.print_dict(host.to_dict())
    except Exception as e:
        print(e)
