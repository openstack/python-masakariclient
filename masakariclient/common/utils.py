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

import os
import prettytable
import six
import textwrap

from oslo_serialization import jsonutils
from oslo_utils import encodeutils
from oslo_utils import importutils
from oslo_utils import uuidutils

from masakariclient.common import exception as exc
from masakariclient.common.i18n import _


def format_parameters(params, parse_semicolon=True):
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
    for key, value in attrs.items():
        if not value:
            del attrs[key]
    return attrs


def import_versioned_module(version, submodule=None):
    module = 'masakariclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def arg(*args, **kwargs):
    """Decorator for CLI args."""

    def _decorator(func):
        if not hasattr(func, 'arguments'):
            func.arguments = []

        if (args, kwargs) not in func.arguments:
            func.arguments.insert(0, (args, kwargs))

        return func

    return _decorator


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


def print_list(objs, fields, formatters={}, sortby_index=None):
    """Print list data by PrettyTable."""

    if sortby_index is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    mixed_case_fields = ['serverId']
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, '')
                if data is None:
                    data = '-'
                # '\r' would break the table, so remove it.
                data = six.text_type(data).replace("\r", "")
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = encodeutils.safe_encode(pt.get_string(sortby=sortby))
    else:
        result = encodeutils.safe_encode(pt.get_string())

    if six.PY3:
        result = result.decode()

    print(result)


def print_dict(d, dict_property="Property", dict_value="Value", wrap=0):
    """Print dictionary data (eg. show) by PrettyTable."""

    pt = prettytable.PrettyTable([dict_property, dict_value], caching=False)
    pt.align = 'l'
    for k, v in sorted(d.items()):
        # convert dict to str to check length
        if isinstance(v, (dict, list)):
            v = jsonutils.dumps(v)
        if wrap > 0:
            v = textwrap.fill(six.text_type(v), wrap)
        # if value has a newline, add in multiple rows
        # e.g. fault with stacktrace
        if v and isinstance(v, six.string_types) and (r'\n' in v or '\r' in v):
            # '\r' would break the table, so remove it.
            if '\r' in v:
                v = v.replace('\r', '')
            lines = v.strip().split(r'\n')
            col1 = k
            for line in lines:
                pt.add_row([col1, line])
                col1 = ''
        else:
            if v is None:
                v = '-'
            pt.add_row([k, v])

    result = encodeutils.safe_encode(pt.get_string())

    if six.PY3:
        result = result.decode()

    print(result)


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
        queries.update(format_parameters(parsed_args.filters))

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
