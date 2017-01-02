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

from masakariclient.common.i18n import _
import masakariclient.common.utils as masakariclient_utils


class ListHost(command.Lister):
    """List Hosts."""

    def get_parser(self, prog_name):
        parser = super(ListHost, self).get_parser(prog_name)
        parser.add_argument(
            'segment_id',
            metavar='<segment_id>',
            help=_('UUID of segment.')
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of policies returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return policies that appear after the given policy '
                   'ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['type', 'name', 'created_at', "
                   "'updated_at']")
        )
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned policies. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['type', 'name']"),
            action='append'
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        columns = ['uuid', 'name', 'type', 'control_attributes', 'reserved',
                   'on_maintenance', 'failover_segment_id']

        queries = masakariclient_utils.format_sort_filter_params(parsed_args)
        hosts = masakari_client.hosts(parsed_args.segment_id, **queries)
        formatters = {}
        return (
            columns,
            (utils.get_item_properties(p, columns, formatters=formatters)
             for p in hosts)
        )


class ShowHost(command.ShowOne):
    """Show host details."""

    def get_parser(self, prog_name):
        parser = super(ShowHost, self).get_parser(prog_name)
        parser.add_argument(
            'segment_id',
            metavar='<segment_id>',
            help=_('UUID of segment.')
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Name or ID of the Host',
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        return _show_host(masakari_client,
                          parsed_args.segment_id,
                          parsed_args.host)


class CreateHost(command.ShowOne):
    """Create a Host."""

    def get_parser(self, prog_name):
        parser = super(CreateHost, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of host.')
        )
        parser.add_argument(
            'type',
            metavar='<type>',
            help=_('Type of host.')
        )
        parser.add_argument(
            'control_attributes',
            metavar='<control_attributes>',
            help=_('Attribute about control.')
        )
        parser.add_argument(
            'segment_id',
            metavar='<segment_id>',
            help=_('UUID of segment.')
        )
        parser.add_argument(
            '--reserved',
            metavar='<reserved>',
            help=_('Host reservation. True or False.')
        )
        parser.add_argument(
            '--on_maintenance',
            metavar='<on_maintenance>',
            help=_('Maintenance status of host. True or False.')
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        attrs = {
            'name': parsed_args.name,
            'type': parsed_args.type,
            'control_attributes': parsed_args.control_attributes,
            'reserved': parsed_args.reserved,
            'on_maintenance': parsed_args.on_maintenance,
        }
        # Remove not specified keys
        attrs = masakariclient_utils.remove_unspecified_items(attrs)

        host = masakari_client.create_host(segment_id=parsed_args.segment_id,
                                           **attrs)
        return _show_host(masakari_client,
                          parsed_args.segment_id,
                          host.uuid)


class UpdateHost(command.ShowOne):
    """Update a Host."""

    def get_parser(self, prog_name):
        parser = super(UpdateHost, self).get_parser(prog_name)
        parser.add_argument(
            'segment_id',
            metavar='<segment_id>',
            help=_('UUID of segment.')
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Name or ID of the Host',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of host.')
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            help=_('Type of host.')
        )
        parser.add_argument(
            '--control_attributes',
            metavar='<control_attributes>',
            help=_('Attributes about control.')
        )
        parser.add_argument(
            '--reserved',
            metavar='<reserved>',
            help=_('Host reservation. True or False.')
        )
        parser.add_argument(
            '--on_maintenance',
            metavar='<on_maintenance>',
            help=_('Maintenance status of host. True or False.')
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        attrs = {
            'name': parsed_args.name,
            'type': parsed_args.type,
            'control_attributes': parsed_args.control_attributes,
            'reserved': parsed_args.reserved,
            'on_maintenance': parsed_args.on_maintenance,
        }
        # Remove not specified keys
        attrs = masakariclient_utils.remove_unspecified_items(attrs)

        masakari_client.update_host(segment_id=parsed_args.segment_id,
                                    host=parsed_args.host,
                                    **attrs)
        return _show_host(masakari_client,
                          parsed_args.segment_id,
                          parsed_args.host)


class DeleteHost(command.ShowOne):
    """Delete a host."""

    def get_parser(self, prog_name):
        parser = super(DeleteHost, self).get_parser(prog_name)
        parser.add_argument(
            'segment_id',
            metavar='<segment_id>',
            help=_('UUID of segment.')
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Name or ID of the Host',
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        masakari_client.delete_host(parsed_args.segment_id,
                                    parsed_args.host)
        print('Host deleted: %s' % parsed_args.host)
        return ({}, {})


def _show_host(masakari_client, segment_id, uuid):
    try:
        host = masakari_client.get_host(segment_id, uuid)
    except sdk_exc.ResourceNotFound:
        raise exceptions.CommandError(_('Host not found: %s') % uuid)

    formatters = {}
    columns = [
        'created_at',
        'updated_at',
        'uuid',
        'name',
        'type',
        'control_attributes',
        'reserved',
        'on_maintenance',
        'failover_segment_id',
    ]
    return columns, utils.get_dict_properties(host.to_dict(), columns,
                                              formatters=formatters)
