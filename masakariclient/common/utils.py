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
