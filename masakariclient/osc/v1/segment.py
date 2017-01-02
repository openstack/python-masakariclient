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


class ListSegment(command.Lister):
    """List segments."""

    def get_parser(self, prog_name):
        parser = super(ListSegment, self).get_parser(prog_name)
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
        columns = ['uuid', 'name', 'description', 'service_type',
                   'recovery_method']

        queries = masakariclient_utils.format_sort_filter_params(parsed_args)
        segments = masakari_client.segments(**queries)
        formatters = {}
        return (
            columns,
            (utils.get_item_properties(p, columns, formatters=formatters)
             for p in segments)
        )


class ShowSegment(command.ShowOne):
    """Show segment details."""

    def get_parser(self, prog_name):
        parser = super(ShowSegment, self).get_parser(prog_name)
        parser.add_argument(
            'segment',
            metavar='<segment>',
            help='Segment to display (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        return _show_segment(masakari_client,
                             segment_uuid=parsed_args.segment)


class CreateSegment(command.ShowOne):
    """Create segment."""

    def get_parser(self, prog_name):
        parser = super(CreateSegment, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of segment.')
        )
        parser.add_argument(
            'recovery_method',
            metavar='<recovery_method>',
            help=_('Recovery method of segment.')
        )
        parser.add_argument(
            'service_type',
            metavar='<service_type>',
            help=_('Service type of segment.')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of segment.')
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        attrs = {
            'name': parsed_args.name,
            'description': parsed_args.description,
            'recovery_method': parsed_args.recovery_method,
            'service_type': parsed_args.service_type,
        }
        # Remove not specified keys
        attrs = masakariclient_utils.remove_unspecified_items(attrs)

        segment = masakari_client.create_segment(**attrs)
        return _show_segment(masakari_client,
                             segment.uuid)


class UpdateSegment(command.ShowOne):
    """Update a segment."""

    def get_parser(self, prog_name):
        parser = super(UpdateSegment, self).get_parser(prog_name)
        parser.add_argument(
            'segment',
            metavar='<segment>',
            help=_('Name or ID of the segment to update.')
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of segment.')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of segment.')
        )
        parser.add_argument(
            '--recovery_method',
            metavar='<recovery_method>',
            help=_('Recovery method of segment.')
        )
        parser.add_argument(
            '--service_type',
            metavar='<service_type>',
            help=_('Service type of segment.')
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        attrs = {
            'name': parsed_args.name,
            'description': parsed_args.description,
            'recovery_method': parsed_args.recovery_method,
            'service_type': parsed_args.service_type,
        }
        # Remove not specified keys
        attrs = masakariclient_utils.remove_unspecified_items(attrs)

        masakari_client.update_segment(segment=parsed_args.segment,
                                       **attrs)
        return _show_segment(masakari_client,
                             parsed_args.segment)


class DeleteSegment(command.Command):
    """Delete a segment(s)."""

    def get_parser(self, prog_name):
        parser = super(DeleteSegment, self).get_parser(prog_name)
        parser.add_argument(
            'segment',
            metavar='<segment>',
            nargs='+',
            help=_('Name or ID of segment(s) to delete')
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha

        for sid in parsed_args.segment:
            try:
                masakari_client.delete_segment(sid, False)
                print('Segment deleted: %s' % sid)
            except Exception as ex:
                print(ex)


def _show_segment(masakari_client, segment_uuid):
    try:
        segment = masakari_client.get_segment(segment_uuid)
    except sdk_exc.ResourceNotFound:
        raise exceptions.CommandError(_('Segment not found: %s'
                                        ) % segment_uuid)

    formatters = {}
    columns = [
        'created_at',
        'updated_at',
        'uuid',
        'name',
        'description',
        'id',
        'service_type',
        'recovery_method',
    ]
    return columns, utils.get_dict_properties(segment.to_dict(), columns,
                                              formatters=formatters)
