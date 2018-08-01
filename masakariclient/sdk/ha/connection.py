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
import pbr.version

from keystoneauth1.identity.generic import password as ks_password
from keystoneauth1 import session as ks_session
from openstack import connection
sdk_ver = pbr.version.VersionInfo('openstacksdk').version_string()
if sdk_ver in ['0.11.0']:
    from masakariclient.sdk.ha.v1 import _proxy
    from openstack import service_description


LOG = logging.getLogger(__name__)


def create_connection(**kwargs):
    auth = ks_password.Password(
        auth_url=kwargs.get('auth_url'),
        username=kwargs.get('username'),
        password=kwargs.get('password'),
        user_domain_name=kwargs['user_domain_name'],
        user_domain_id=kwargs.get('user_domain_id'),
        project_name=kwargs.get('project_name'),
        project_domain_id=kwargs.get('project_domain_id'))
    session = ks_session.Session(auth=auth)

    if sdk_ver >= '0.11.1':
        conn = connection.Connection(session=session)
    else:
        desc = service_description.ServiceDescription(service_type='ha',
                                                      proxy_class=_proxy.Proxy)
        conn = connection.Connection(session=session)
        conn.add_service(desc)

    return conn
