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

from oslo_utils import uuidutils

from masakariclient.common import exception as exc
from masakariclient.common.i18n import _


def _format_parameters(params, parse_semicolon=True):
    """Reformat parameters into dict of format expected by the API."""
    if not params:
        return {}

    if parse_semicolon:
        # expect multiple invocations of --parameters but fall back to ';'
        # delimited if only one --parameters is specified
        if len(params) == 1:
            params = params[0].split(';')

    parameters = {}
    for p in params:
        try:
            (n, v) = p.split(('='), 1)
        except ValueError:
            msg = _('Malformed parameter(%s). Use the key=value format.') % p
            raise exc.CommandError(msg)

        if n not in parameters:
            parameters[n] = v
        else:
            if not isinstance(parameters[n], list):
                parameters[n] = [parameters[n]]
            parameters[n].append(v)

    return parameters


def remove_unspecified_items(attrs):
    """Remove the items that don't have any values."""
    for key, value in list(attrs.items()):
        if value is None:
            del attrs[key]
    return attrs


def format_sort_filter_params(parsed_args):
    queries = {}
    limit = parsed_args.limit
    marker = parsed_args.marker
    sort = parsed_args.sort
    if limit:
        queries['limit'] = limit
    if marker:
        queries['marker'] = marker

    sort_keys = []
    sort_dirs = []
    if sort:
        for sort_param in sort.split(','):
            sort_key, _sep, sort_dir = sort_param.partition(':')
            if not sort_dir:
                sort_dir = 'desc'
            elif sort_dir not in ('asc', 'desc'):
                raise exc.CommandError(_(
                    'Unknown sort direction: %s') % sort_dir)
            sort_keys.append(sort_key)
            sort_dirs.append(sort_dir)

        queries['sort_key'] = sort_keys
        queries['sort_dir'] = sort_dirs

    if parsed_args.filters:
        queries.update(_format_parameters(parsed_args.filters))

    return queries


def get_uuid_by_name(manager, name, segment=None):
    """Helper methods for getting uuid of segment or host by name.

    :param manager: A client manager class
    :param name: The resource we are trying to find a uuid
    :param segment: segment id, default None
    :return: The uuid of found resource
    """

    # If it cannot be found return the name.
    uuid = name
    if not uuidutils.is_uuid_like(name):
        if segment:
            items = manager.hosts(segment)
        else:
            items = manager.segments()

        for item in items:
            item_name = getattr(item, 'name')
            if item_name == name:
                uuid = getattr(item, 'uuid')
                break
    return uuid
