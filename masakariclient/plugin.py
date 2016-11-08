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

from openstack import connection
from openstack import profile
from osc_lib import utils

from masakariclient.sdk.vmha import vmha_service


LOG = logging.getLogger(__name__)

DEFAULT_VMHA_API_VERSION = '1'
API_VERSION_OPTION = 'os_vmha_api_version'
API_NAME = 'vmha'
API_VERSIONS = {
    '1': 'masakariclient.client.Client',
}


def make_client(instance):
    """Returns a vmha proxy"""
    prof = profile.Profile()
    prof._add_service(vmha_service.VMHAService(version="v1"))
    prof.set_region(API_NAME, instance.region_name)
    prof.set_version(API_NAME, instance._api_version[API_NAME])
    prof.set_interface(API_NAME, instance.interface)
    conn = connection.Connection(authenticator=instance.session.auth,
                                 verify=instance.session.verify,
                                 cert=instance.session.cert,
                                 profile=prof)
    LOG.debug('Connection: %s', conn)
    LOG.debug('masakari client initialized: %s', conn.vmha)
    return conn.vmha


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-vmha-api-version',
        metavar='<vmha-api-version>',
        default=utils.env(
            'OS_VMHA_API_VERSION',
            default=DEFAULT_VMHA_API_VERSION),
        help='vmha API version, default=' +
             DEFAULT_VMHA_API_VERSION +
             ' (Env: OS_VMHA_API_VERSION)')
    return parser
