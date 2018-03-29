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

from openstack import connection
from osc_lib import utils


DEFAULT_HA_API_VERSION = '1'
API_VERSION_OPTION = 'os_ha_api_version'
API_NAME = 'ha'


def make_client(instance):
    """Returns a ha proxy"""
    conn = connection.Connection(session=instance.session)
    return conn.instance_ha


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-ha-api-version',
        metavar='<ha-api-version>',
        default=utils.env(
            'OS_HA_API_VERSION',
            default=DEFAULT_HA_API_VERSION),
        help='ha API version, default=' +
             DEFAULT_HA_API_VERSION +
             ' (Env: OS_HA_API_VERSION)')
    return parser
