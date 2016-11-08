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

from openstack import resource

from masakariclient.sdk.vmha import vmha_service


class Segment(resource.Resource):
    resource_key = "segment"
    resources_key = "segments"
    base_path = "/segments"
    service = vmha_service.VMHAService()

    # capabilities
    # 1] GET /v1/segments
    # 2] GET /v1/segments/<segment_uuid>
    # 3] POST /v1/segments
    # 4] POST /v1/segments
    # 5] POST /v1/segments
    allow_list = True
    allow_retrieve = True
    allow_create = True
    allow_update = True
    allow_delete = True

    # Properties
    # Refer "https://github.com/openstack/masakari/tree/
    # master/masakari/api/openstack/ha/schemas"
    # for properties of each API

    #: A ID of representing this segment.
    id = resource.prop("id")
    #: The name of this segment.
    name = resource.prop("name")
    #: The description of this segment.
    description = resource.prop("description")
    #: The recovery method of this segment.
    recovery_method = resource.prop("recovery_method")
    #: The service type of this segment.
    service_type = resource.prop("service_type")

    def update(self, session):
        """Update the segment.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        if not self.is_dirty:
            return

        dirty_attrs = dict((k, self._attrs[k]) for k in self._dirty)
        resp = self.update_by_id(session, self.id, dirty_attrs, path_args=self)
        try:
            resp_id = resp.pop("uuid")
        except KeyError:
            pass
        else:
            if resp_id != self.id:
                raise ValueError("IDs, %s and %s are not match" % (resp_id,
                                                                   self.id))
        self._update_attrs_from_response(resp, include_headers=True)
        self._reset_dirty()
        return self
