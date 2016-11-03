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


class Notification(resource.Resource):
    resource_key = "notification"
    resources_key = "notifications"
    base_path = "/notifications"
    service = vmha_service.VMHAService()

    # capabilities
    # 1] GET /v1/notifications
    # 2] GET /v1/notifications/<notification_uuid>
    # 3] POST /v1/notifications
    allow_list = True
    allow_retrieve = True
    allow_create = True
    allow_update = False
    allow_delete = False

    # Properties
    # Refer "https://github.com/openstack/masakari/tree/
    # master/masakari/api/openstack/ha/schemas/notificaions.py"
    # for properties of notifications API

    #: A ID of representing this notification.
    id = resource.prop("id")
    #: The type of failure. Valuse values include ''COMPUTE_HOST'',
    #: ''VM'', ''PROCESS''
    type = resource.prop("type")
    #: The hostname of this notification.
    hostname = resource.prop("hostname")
    #: The generated_time for this notitication.
    generated_time = resource.prop("generated_time")
    #: The payload of this notification.
    payload = resource.prop("payload")
