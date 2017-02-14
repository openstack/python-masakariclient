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
           help='Type of failure.')
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
