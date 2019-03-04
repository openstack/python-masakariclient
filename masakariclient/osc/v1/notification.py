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

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_serialization import jsonutils

from masakariclient import api_versions
from masakariclient.common.i18n import _
import masakariclient.common.utils as masakariclient_utils


class ListNotification(command.Lister):
    """List notifications."""

    def get_parser(self, prog_name):
        parser = super(ListNotification, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of notifications returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return notifications that appear after the given '
                   'notification ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['type', 'created_at', 'updated_at']")
        )
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned notifications. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['source_host_uuid', 'type', 'status', "
                   "generated-since]"),
            action='append'
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        columns = ['notification_uuid', 'generated_time', 'status',
                   'type', 'source_host_uuid', 'payload']

        queries = masakariclient_utils.format_sort_filter_params(parsed_args)
        notifications = masakari_client.notifications(**queries)
        formatters = {}
        return (
            columns,
            (utils.get_item_properties(p, columns, formatters=formatters)
             for p in notifications)
        )


class ShowNotification(command.ShowOne):
    """Show notification details."""

    def get_parser(self, prog_name):
        parser = super(ShowNotification, self).get_parser(prog_name)
        parser.add_argument(
            'notification',
            metavar='<notification>',
            help='UUID of notification to display',
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        return _show_notification(masakari_client,
                                  notification_uuid=parsed_args.notification)


class CreateNotification(command.ShowOne):
    """Create notification."""

    def get_parser(self, prog_name):
        parser = super(CreateNotification, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<type>',
            choices=['COMPUTE_HOST', 'VM', 'PROCESS'],
            help=_('Type of failure. The supported options are: '
                   'COMPUTE_HOST, VM, PROCESS.')
        )
        parser.add_argument(
            'hostname',
            metavar='<hostname>',
            help=_('Hostname of notification.')
        )
        parser.add_argument(
            'generated_time',
            metavar='<generated_time>',
            help=_('Timestamp for notification. e.g. 2016-01-01T01:00:00.000')
        )
        parser.add_argument(
            'payload',
            metavar='<payload>',
            help=_('JSON string about failure event.')
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        payload = jsonutils.loads(parsed_args.payload)
        attrs = {
            'type': parsed_args.type,
            'hostname': parsed_args.hostname,
            'generated_time': parsed_args.generated_time,
            'payload': payload,
        }

        notification = masakari_client.create_notification(**attrs)
        return _show_notification(masakari_client,
                                  notification.notification_uuid)


def _show_notification(masakari_client, notification_uuid):
    try:
        notification = masakari_client.get_notification(notification_uuid)
    except sdk_exc.ResourceNotFound:
        raise exceptions.CommandError(_('Notification not found: %s'
                                        ) % notification_uuid)

    formatters = {}
    columns = [
        'created_at',
        'updated_at',
        'notification_uuid',
        'type',
        'status',
        'source_host_uuid',
        'generated_time',
        'payload'
    ]

    if masakari_client.default_microversion:
        api_version = api_versions.APIVersion(
            masakari_client.default_microversion)
        if api_version >= api_versions.APIVersion("1.1"):
            columns.append('recovery_workflow_details')

    return columns, utils.get_dict_properties(notification.to_dict(), columns,
                                              formatters=formatters)
