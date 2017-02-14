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


class Segment(resource2.Resource):
    resource_key = "segment"
    resources_key = "segments"
    base_path = "/segments"
    service = ha_service.HAService()

    # capabilities
    # 1] GET /v1/segments
    # 2] GET /v1/segments/<segment_uuid>
    # 3] POST /v1/segments
    # 4] POST /v1/segments
    # 5] POST /v1/segments
    allow_list = True
    allow_get = True
    allow_create = True
    allow_update = True
    allow_delete = True

    # Properties
    # Refer "https://github.com/openstack/masakari/tree/
    # master/masakari/api/openstack/ha/schemas"
    # for properties of each API

    #: A ID of representing this segment.
    id = resource2.Body("id")
    #: A Uuid of representing this segment.
    uuid = resource2.Body("uuid")
    #: A created time of representing this segment.
    created_at = resource2.Body("created_at")
    #: A latest updated time of representing this segment.
    updated_at = resource2.Body("updated_at")
    #: The name of this segment.
    name = resource2.Body("name")
    #: The description of this segment.
    description = resource2.Body("description")
    #: The recovery method of this segment.
    recovery_method = resource2.Body("recovery_method")
    #: The service type of this segment.
    service_type = resource2.Body("service_type")

    _query_mapping = resource2.QueryParameters(
        "sort_key", "sort_dir", recovery_method="recovery_method",
        service_type="service_type")

    def update(self, session, prepend_key=False, has_body=True):
        """Update a segment."""
        request = self._prepare_request(prepend_key=prepend_key)
        del request.body['id']
        request_body = {"segment": request.body}
        ret = session.put(request.uri, endpoint_filter=self.service,
                          json=request_body, headers=request.headers)
        self._translate_response(ret, has_body=has_body)
        return self
