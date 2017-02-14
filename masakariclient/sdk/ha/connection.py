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

from masakariclient.sdk.ha import ha_service

LOG = logging.getLogger(__name__)


def create_connection(prof=None, user_agent=None, **kwargs):
    """Create connection to masakari_api."""

    if not prof:
        prof = profile.Profile()

    prof._add_service(ha_service.HAService(version="v1"))
    interface = kwargs.pop('interface', None)
    region_name = kwargs.pop('region_name', None)
    if interface:
        prof.set_interface('ha', interface)
    if region_name:
        prof.set_region('ha', region_name)

    prof.set_api_version('ha', '1')

    try:
        conn = connection.Connection(profile=prof,
                                     user_agent=user_agent,
                                     **kwargs)
        LOG.debug('Connection: %s', conn)
        LOG.debug('masakari client initialized: %s', conn.ha)
    except Exception as e:
        raise e

    return conn
