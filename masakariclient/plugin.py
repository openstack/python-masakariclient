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

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_HA_API_VERSION = '1'
API_VERSION_OPTION = 'os_ha_api_version'
API_NAME = 'ha'
API_VERSIONS = {
    '1': 'masakariclient.v1.client.Client',
}


def make_client(instance):
    """Returns a instance_ha proxy"""
    version = instance._api_version[API_NAME]
    masakari_client = utils.get_client_class(
        API_NAME,
        version,
        API_VERSIONS)

    LOG.debug('Instantiating masakari service client: %s', masakari_client)
    client = masakari_client(session=instance.session,
                             interface=instance.interface,
                             region_name=instance.region_name)
    return client.service


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
