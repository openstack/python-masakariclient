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

from openstack.connection import Connection
from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_HA_API_VERSION = '1.3'
API_VERSION_OPTION = 'os_ha_api_version'
API_NAME = 'ha'

SUPPORTED_VERSIONS = [
    '1',
    '1.0',
    '1.1',
    '1.2',
    '1.3',
]

API_VERSIONS = {v: None
                for v in SUPPORTED_VERSIONS}


def make_client(instance):
    """Returns a instance_ha proxy"""
    LOG.debug('Instantiating masakari service client')
    con = Connection(session=instance.session,
                     interface=instance.interface,
                     region_name=instance.region_name,
                     ha_api_version=instance._api_version[API_NAME])
    return con.instance_ha


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
