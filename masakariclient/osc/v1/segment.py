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

import logging

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import strutils

from masakariclient import api_versions
from masakariclient.common.i18n import _
import masakariclient.common.utils as masakariclient_utils

# Get the logger of this module
LOG = logging.getLogger(__name__)


class ListSegment(command.Lister):
    """List segments."""

    def get_parser(self, prog_name):
        parser = super(ListSegment, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of segments returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return segments that appear after the given segment '
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
            help=_("Filter parameters to apply on returned segments. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['recovery_method', 'service_type']"),
            action='append'
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha
        columns = ['uuid', 'name', 'description', 'service_type',
                   'recovery_method']

        if masakari_client.default_microversion:
            api_version = api_versions.APIVersion(
                masakari_client.default_microversion)
            if api_version >= api_versions.APIVersion("1.2"):
                columns.append('is_enabled')

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
        uuid = masakariclient_utils.get_uuid_by_name(
            masakari_client, parsed_args.segment)
        return _show_segment(masakari_client, segment_uuid=uuid)


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
            choices=['auto', 'reserved_host', 'auto_priority', 'rh_priority'],
            help=_('Recovery method of segment. The supported options are: '
                   'auto, reserved_host, auto_priority, rh_priority.')
        )
        parser.add_argument(
            'service_type',
            metavar='<service_type>',
            help=_('Service type of segment.')
        )
        parser.add_argument(
            '--is_enabled',
            metavar='<boolean>',
            help=_('The enabled flag of this segment. '
                   'Supported after microversion 1.2.')
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

        if masakari_client.default_microversion:
            api_version = api_versions.APIVersion(
                masakari_client.default_microversion)
            if (api_version >= api_versions.APIVersion("1.2") and
                    parsed_args.is_enabled is not None):
                attrs['is_enabled'] = strutils.bool_from_string(
                    parsed_args.is_enabled,
                    strict=True)

        # Remove not specified keys
        attrs = masakariclient_utils.remove_unspecified_items(attrs)

        try:
            segment = masakari_client.create_segment(**attrs)
        except Exception as ex:
            LOG.debug(_("Failed to create segment: %s"), parsed_args)
            raise ex
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
            '--recovery_method',
            metavar='<recovery_method>',
            choices=['auto', 'reserved_host', 'auto_priority', 'rh_priority'],
            help=_('Recovery method of segment. The supported options are: '
                   'auto, reserved_host, auto_priority, rh_priority')
        )
        parser.add_argument(
            '--service_type',
            metavar='<service_type>',
            help=_('Service type of segment.')
        )
        parser.add_argument(
            '--is_enabled',
            metavar='<boolean>',
            help=_('The enabled flag of this segment. '
                   'Supported after microversion 1.2.')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of segment.')
        )
        return parser

    def take_action(self, parsed_args):
        masakari_client = self.app.client_manager.ha

        uuid = masakariclient_utils.get_uuid_by_name(
            masakari_client, parsed_args.segment)

        attrs = {
            'name': parsed_args.name,
            'description': parsed_args.description,
            'recovery_method': parsed_args.recovery_method,
            'service_type': parsed_args.service_type,
        }

        if masakari_client.default_microversion:
            api_version = api_versions.APIVersion(
                masakari_client.default_microversion)
            if (api_version >= api_versions.APIVersion("1.2") and
                    parsed_args.is_enabled is not None):
                attrs['is_enabled'] = strutils.bool_from_string(
                    parsed_args.is_enabled,
                    strict=True)

        # Remove not specified keys
        attrs = masakariclient_utils.remove_unspecified_items(attrs)

        try:
            masakari_client.update_segment(segment=uuid, **attrs)
        # Reraise. To unify exceptions with other functions.
        except sdk_exc.NotFoundException:
            LOG.debug(_("Segment is not found: %s"), parsed_args)
            raise sdk_exc.ResourceNotFound(
                _('No Segment found for %s') % uuid)
        except Exception as ex:
            LOG.debug(_("Failed to update segment: %s"), parsed_args)
            raise ex
        return _show_segment(masakari_client, uuid)


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
                uuid = masakariclient_utils.get_uuid_by_name(
                    masakari_client, sid)
                masakari_client.delete_segment(uuid, False)
                print('Segment deleted: %s' % sid)
            except Exception as ex:
                print(ex)


def _show_segment(masakari_client, segment_uuid):
    try:
        segment = masakari_client.get_segment(segment_uuid)
    except sdk_exc.ResourceNotFound:
        raise exceptions.CommandError(_('Segment is not found: %s'
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

    if masakari_client.default_microversion:
        api_version = api_versions.APIVersion(
            masakari_client.default_microversion)
        if api_version >= api_versions.APIVersion("1.2"):
            columns.append('is_enabled')

    return columns, utils.get_dict_properties(segment.to_dict(), columns,
                                              formatters=formatters)
