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

import logging

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from masakariclient.common.i18n import _
import masakariclient.common.utils as masakariclient_utils

# Get the logger of this module
LOG = logging.getLogger(__name__)


class ListVMove(command.Lister):
    """List VMoves."""

    def get_parser(self, prog_name):
        parser = super(ListVMove, self).get_parser(prog_name)
        parser.add_argument(
            'notification_id',
            metavar='<notification_id>',
            help=_('UUID of notification.')
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of vmoves returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return vmoves that appear after the given vmove ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['type', 'status', 'start_time', "
                   "'end_time']")
        )
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned vmoves. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['type', 'status'"),
            action='append'
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha

        columns = ['uuid', 'server_id', 'server_name',
                   'source_host', 'dest_host',
                   'start_time', 'end_time',
                   'type', 'status']

        queries = masakariclient_utils.format_sort_filter_params(parsed_args)
        vmoves = masakari_client.vmoves(parsed_args.notification_id,
                                        **queries)
        formatters = {}
        return (
            columns,
            (utils.get_item_properties(p, columns, formatters=formatters)
             for p in vmoves)
        )


class ShowVMove(command.ShowOne):
    """Show vmove details."""

    def get_parser(self, prog_name):
        parser = super(ShowVMove, self).get_parser(prog_name)
        parser.add_argument(
            'notification_id',
            metavar='<notification_id>',
            help=_('UUID of COMPUTE_NODE type notification.')
        )
        parser.add_argument(
            'vmove_id',
            metavar='<vmove_id>',
            help='UUID of the VMove',
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        return _show_vmove(masakari_client, parsed_args.notification_id,
                           parsed_args.vmove_id)


def _show_vmove(masakari_client, notification_id, vmove_id):
    try:
        vmove = masakari_client.get_vmove(vmove_id, notification_id)
    except sdk_exc.ResourceNotFound:
        raise exceptions.CommandError(_('VMove %s is not found.')
                                      % vmove_id)

    formatters = {}
    columns = [
        'created_at',
        'updated_at',
        'uuid',
        'server_id',
        'server_name',
        'source_host',
        'dest_host',
        'start_time',
        'end_time',
        'type',
        'status',
        'message'
    ]
    return columns, utils.get_dict_properties(vmove.to_dict(), columns,
                                              formatters=formatters)
