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

from openstack import resource2

from masakariclient.sdk.ha import ha_service


class Host(resource2.Resource):
    resource_key = "host"
    resources_key = "hosts"
    base_path = "/segments/%(segment_id)s/hosts"
    service = ha_service.HAService()

    # capabilities
    # 1] GET /v1/segments/<segment_uuid>/hosts
    # 2] GET /v1/segments/<segment_uuid>/hosts/<host_uuid>
    # 3] POST /v1/segments/<segment_uuid>/hosts
    # 4] PUT /v1/segments/<segment_uuid>/hosts
    # 5] DELETE /v1/segments/<segment_uuid>/hosts
    allow_list = True
    allow_get = True
    allow_create = True
    allow_update = True
    allow_delete = True

    # Properties
    # Refer "https://github.com/openstack/masakari/blob/
    # master/masakari/api/openstack/ha/schemas/hosts.py"
    # for properties of host API

    #: A ID of representing this host
    id = resource2.URI("id")
    #: A Uuid of representing this host
    uuid = resource2.Body("uuid")
    #: A failover segment ID of this host(in URI)
    segment_id = resource2.URI("segment_id")
    #: A created time of this host
    created_at = resource2.Body("created_at")
    #: A latest updated time of this host
    updated_at = resource2.Body("updated_at")
    #: A name of this host
    name = resource2.Body("name")
    #: A type of this host
    type = resource2.Body("type")
    #: A control attributes of this host
    control_attributes = resource2.Body("control_attributes")
    #: A maintenance status of this host
    on_maintenance = resource2.Body("on_maintenance")
    #: A reservation status of this host
    reserved = resource2.Body("reserved")
    #: A failover segment ID of this host(in Body)
    failover_segment_id = resource2.Body("failover_segment_id")

    _query_mapping = resource2.QueryParameters(
        "sort_key", "sort_dir", failover_segment_id="failover_segment_id",
        type="type", on_maintenance="on_maintenance", reserved="reserved")

    def update(self, session, prepend_key=False, has_body=True):
        """Update a host."""
        request = self._prepare_request(prepend_key=prepend_key)
        del request.body['id']
        request_body = {"host": request.body}
        res = session.put(request.uri, endpoint_filter=self.service,
                          json=request_body, headers=request.headers)
        self._translate_response(res, has_body=has_body)
        return self
