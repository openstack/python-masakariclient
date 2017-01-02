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


class Notification(resource2.Resource):
    resource_key = "notification"
    resources_key = "notifications"
    base_path = "/notifications"
    service = ha_service.HAService()

    # capabilities
    # 1] GET /v1/notifications
    # 2] GET /v1/notifications/<notification_uuid>
    # 3] POST /v1/notifications
    allow_list = True
    allow_get = True
    allow_create = True
    allow_update = False
    allow_delete = False

    # Properties
    # Refer "https://github.com/openstack/masakari/tree/
    # master/masakari/api/openstack/ha/schemas/notificaions.py"
    # for properties of notifications API

    #: A ID of representing this notification.
    id = resource2.Body("id")
    #: A Uuid of representing this notification.
    notification_uuid = resource2.Body("notification_uuid")
    #: A created time of representing this notification.
    created_at = resource2.Body("created_at")
    #: A latest updated time of representing this notification.
    updated_at = resource2.Body("updated_at")
    #: The type of failure. Valuse values include ''COMPUTE_HOST'',
    #: ''VM'', ''PROCESS''
    type = resource2.Body("type")
    #: The hostname of this notification.
    hostname = resource2.Body("hostname")
    #: The status for this notitication.
    status = resource2.Body("status")
    #: The generated_time for this notitication.
    generated_time = resource2.Body("generated_time")
    #: The payload of this notification.
    payload = resource2.Body("payload")
    #: The source host uuid of this notification.
    source_host_uuid = resource2.Body("source_host_uuid")

    _query_mapping = resource2.QueryParameters(
        "sort_key", "sort_dir", source_host_uuid="source_host_uuid",
        type="type", status="status", generated_since="generated-since")
