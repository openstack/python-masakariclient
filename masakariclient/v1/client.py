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

from keystoneauth1.identity.generic import password as ks_password
from keystoneauth1 import session as ks_session
from openstack import connection


class Client(object):

    def __init__(self, **kwargs):
        session = kwargs.get('session')
        if session is None:
            auth = ks_password.Password(
                auth_url=kwargs.get('auth_url'),
                username=kwargs.get('username'),
                password=kwargs.get('password'),
                user_domain_id=kwargs.get('user_domain_id'),
                project_name=kwargs.get('project_name'),
                project_domain_id=kwargs.get('project_domain_id'))

            session = ks_session.Session(auth=auth)

        con = connection.Connection(
            session=session,
            interface=kwargs.get('interface'),
            region_name=kwargs.get('region_name'))
        self.service = con.instance_ha
