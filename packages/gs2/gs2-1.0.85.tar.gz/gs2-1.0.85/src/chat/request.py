# Copyright 2016 Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import annotations

from chat.model import *


class DescribeNamespacesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeNamespacesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeNamespacesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeNamespacesRequest]:
        if data is None:
            return None
        return DescribeNamespacesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    allow_create_room: bool = None
    post_message_script: ScriptSetting = None
    create_room_script: ScriptSetting = None
    delete_room_script: ScriptSetting = None
    subscribe_room_script: ScriptSetting = None
    unsubscribe_room_script: ScriptSetting = None
    post_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_allow_create_room(self, allow_create_room: bool) -> CreateNamespaceRequest:
        self.allow_create_room = allow_create_room
        return self

    def with_post_message_script(self, post_message_script: ScriptSetting) -> CreateNamespaceRequest:
        self.post_message_script = post_message_script
        return self

    def with_create_room_script(self, create_room_script: ScriptSetting) -> CreateNamespaceRequest:
        self.create_room_script = create_room_script
        return self

    def with_delete_room_script(self, delete_room_script: ScriptSetting) -> CreateNamespaceRequest:
        self.delete_room_script = delete_room_script
        return self

    def with_subscribe_room_script(self, subscribe_room_script: ScriptSetting) -> CreateNamespaceRequest:
        self.subscribe_room_script = subscribe_room_script
        return self

    def with_unsubscribe_room_script(self, unsubscribe_room_script: ScriptSetting) -> CreateNamespaceRequest:
        self.unsubscribe_room_script = unsubscribe_room_script
        return self

    def with_post_notification(self, post_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.post_notification = post_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_allow_create_room(data.get('allowCreateRoom'))\
            .with_post_message_script(ScriptSetting.from_dict(data.get('postMessageScript')))\
            .with_create_room_script(ScriptSetting.from_dict(data.get('createRoomScript')))\
            .with_delete_room_script(ScriptSetting.from_dict(data.get('deleteRoomScript')))\
            .with_subscribe_room_script(ScriptSetting.from_dict(data.get('subscribeRoomScript')))\
            .with_unsubscribe_room_script(ScriptSetting.from_dict(data.get('unsubscribeRoomScript')))\
            .with_post_notification(NotificationSetting.from_dict(data.get('postNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "allowCreateRoom": self.allow_create_room,
            "postMessageScript": self.post_message_script.to_dict() if self.post_message_script else None,
            "createRoomScript": self.create_room_script.to_dict() if self.create_room_script else None,
            "deleteRoomScript": self.delete_room_script.to_dict() if self.delete_room_script else None,
            "subscribeRoomScript": self.subscribe_room_script.to_dict() if self.subscribe_room_script else None,
            "unsubscribeRoomScript": self.unsubscribe_room_script.to_dict() if self.unsubscribe_room_script else None,
            "postNotification": self.post_notification.to_dict() if self.post_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class GetNamespaceStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceStatusRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceStatusRequest]:
        if data is None:
            return None
        return GetNamespaceStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceRequest]:
        if data is None:
            return None
        return GetNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    description: str = None
    allow_create_room: bool = None
    post_message_script: ScriptSetting = None
    create_room_script: ScriptSetting = None
    delete_room_script: ScriptSetting = None
    subscribe_room_script: ScriptSetting = None
    unsubscribe_room_script: ScriptSetting = None
    post_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_allow_create_room(self, allow_create_room: bool) -> UpdateNamespaceRequest:
        self.allow_create_room = allow_create_room
        return self

    def with_post_message_script(self, post_message_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.post_message_script = post_message_script
        return self

    def with_create_room_script(self, create_room_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.create_room_script = create_room_script
        return self

    def with_delete_room_script(self, delete_room_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.delete_room_script = delete_room_script
        return self

    def with_subscribe_room_script(self, subscribe_room_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.subscribe_room_script = subscribe_room_script
        return self

    def with_unsubscribe_room_script(self, unsubscribe_room_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.unsubscribe_room_script = unsubscribe_room_script
        return self

    def with_post_notification(self, post_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.post_notification = post_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_allow_create_room(data.get('allowCreateRoom'))\
            .with_post_message_script(ScriptSetting.from_dict(data.get('postMessageScript')))\
            .with_create_room_script(ScriptSetting.from_dict(data.get('createRoomScript')))\
            .with_delete_room_script(ScriptSetting.from_dict(data.get('deleteRoomScript')))\
            .with_subscribe_room_script(ScriptSetting.from_dict(data.get('subscribeRoomScript')))\
            .with_unsubscribe_room_script(ScriptSetting.from_dict(data.get('unsubscribeRoomScript')))\
            .with_post_notification(NotificationSetting.from_dict(data.get('postNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "allowCreateRoom": self.allow_create_room,
            "postMessageScript": self.post_message_script.to_dict() if self.post_message_script else None,
            "createRoomScript": self.create_room_script.to_dict() if self.create_room_script else None,
            "deleteRoomScript": self.delete_room_script.to_dict() if self.delete_room_script else None,
            "subscribeRoomScript": self.subscribe_room_script.to_dict() if self.subscribe_room_script else None,
            "unsubscribeRoomScript": self.unsubscribe_room_script.to_dict() if self.unsubscribe_room_script else None,
            "postNotification": self.post_notification.to_dict() if self.post_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class DeleteNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteNamespaceRequest]:
        if data is None:
            return None
        return DeleteNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class DescribeRoomsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRoomsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRoomsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRoomsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeRoomsRequest]:
        if data is None:
            return None
        return DescribeRoomsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRoomRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    name: str = None
    metadata: str = None
    password: str = None
    white_list_user_ids: List[str] = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateRoomRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreateRoomRequest:
        self.access_token = access_token
        return self

    def with_name(self, name: str) -> CreateRoomRequest:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CreateRoomRequest:
        self.metadata = metadata
        return self

    def with_password(self, password: str) -> CreateRoomRequest:
        self.password = password
        return self

    def with_white_list_user_ids(self, white_list_user_ids: List[str]) -> CreateRoomRequest:
        self.white_list_user_ids = white_list_user_ids
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateRoomRequest]:
        if data is None:
            return None
        return CreateRoomRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_password(data.get('password'))\
            .with_white_list_user_ids([
                data.get('whiteListUserIds')[i]
                for i in range(len(data.get('whiteListUserIds')) if data.get('whiteListUserIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "name": self.name,
            "metadata": self.metadata,
            "password": self.password,
            "whiteListUserIds": [
                self.white_list_user_ids[i]
                for i in range(len(self.white_list_user_ids) if self.white_list_user_ids else 0)
            ],
        }


class CreateRoomFromBackendRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    user_id: str = None
    metadata: str = None
    password: str = None
    white_list_user_ids: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> CreateRoomFromBackendRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRoomFromBackendRequest:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> CreateRoomFromBackendRequest:
        self.user_id = user_id
        return self

    def with_metadata(self, metadata: str) -> CreateRoomFromBackendRequest:
        self.metadata = metadata
        return self

    def with_password(self, password: str) -> CreateRoomFromBackendRequest:
        self.password = password
        return self

    def with_white_list_user_ids(self, white_list_user_ids: List[str]) -> CreateRoomFromBackendRequest:
        self.white_list_user_ids = white_list_user_ids
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateRoomFromBackendRequest]:
        if data is None:
            return None
        return CreateRoomFromBackendRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_metadata(data.get('metadata'))\
            .with_password(data.get('password'))\
            .with_white_list_user_ids([
                data.get('whiteListUserIds')[i]
                for i in range(len(data.get('whiteListUserIds')) if data.get('whiteListUserIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "userId": self.user_id,
            "metadata": self.metadata,
            "password": self.password,
            "whiteListUserIds": [
                self.white_list_user_ids[i]
                for i in range(len(self.white_list_user_ids) if self.white_list_user_ids else 0)
            ],
        }


class GetRoomRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRoomRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> GetRoomRequest:
        self.room_name = room_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRoomRequest]:
        if data is None:
            return None
        return GetRoomRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
        }


class UpdateRoomRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    metadata: str = None
    password: str = None
    white_list_user_ids: List[str] = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRoomRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> UpdateRoomRequest:
        self.room_name = room_name
        return self

    def with_metadata(self, metadata: str) -> UpdateRoomRequest:
        self.metadata = metadata
        return self

    def with_password(self, password: str) -> UpdateRoomRequest:
        self.password = password
        return self

    def with_white_list_user_ids(self, white_list_user_ids: List[str]) -> UpdateRoomRequest:
        self.white_list_user_ids = white_list_user_ids
        return self

    def with_access_token(self, access_token: str) -> UpdateRoomRequest:
        self.access_token = access_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateRoomRequest]:
        if data is None:
            return None
        return UpdateRoomRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_metadata(data.get('metadata'))\
            .with_password(data.get('password'))\
            .with_white_list_user_ids([
                data.get('whiteListUserIds')[i]
                for i in range(len(data.get('whiteListUserIds')) if data.get('whiteListUserIds') else 0)
            ])\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "metadata": self.metadata,
            "password": self.password,
            "whiteListUserIds": [
                self.white_list_user_ids[i]
                for i in range(len(self.white_list_user_ids) if self.white_list_user_ids else 0)
            ],
            "accessToken": self.access_token,
        }


class UpdateRoomFromBackendRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    metadata: str = None
    password: str = None
    white_list_user_ids: List[str] = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRoomFromBackendRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> UpdateRoomFromBackendRequest:
        self.room_name = room_name
        return self

    def with_metadata(self, metadata: str) -> UpdateRoomFromBackendRequest:
        self.metadata = metadata
        return self

    def with_password(self, password: str) -> UpdateRoomFromBackendRequest:
        self.password = password
        return self

    def with_white_list_user_ids(self, white_list_user_ids: List[str]) -> UpdateRoomFromBackendRequest:
        self.white_list_user_ids = white_list_user_ids
        return self

    def with_user_id(self, user_id: str) -> UpdateRoomFromBackendRequest:
        self.user_id = user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateRoomFromBackendRequest]:
        if data is None:
            return None
        return UpdateRoomFromBackendRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_metadata(data.get('metadata'))\
            .with_password(data.get('password'))\
            .with_white_list_user_ids([
                data.get('whiteListUserIds')[i]
                for i in range(len(data.get('whiteListUserIds')) if data.get('whiteListUserIds') else 0)
            ])\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "metadata": self.metadata,
            "password": self.password,
            "whiteListUserIds": [
                self.white_list_user_ids[i]
                for i in range(len(self.white_list_user_ids) if self.white_list_user_ids else 0)
            ],
            "userId": self.user_id,
        }


class DeleteRoomRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRoomRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> DeleteRoomRequest:
        self.room_name = room_name
        return self

    def with_access_token(self, access_token: str) -> DeleteRoomRequest:
        self.access_token = access_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRoomRequest]:
        if data is None:
            return None
        return DeleteRoomRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "accessToken": self.access_token,
        }


class DeleteRoomFromBackendRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRoomFromBackendRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> DeleteRoomFromBackendRequest:
        self.room_name = room_name
        return self

    def with_user_id(self, user_id: str) -> DeleteRoomFromBackendRequest:
        self.user_id = user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRoomFromBackendRequest]:
        if data is None:
            return None
        return DeleteRoomFromBackendRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "userId": self.user_id,
        }


class DescribeMessagesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    password: str = None
    access_token: str = None
    start_at: int = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMessagesRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> DescribeMessagesRequest:
        self.room_name = room_name
        return self

    def with_password(self, password: str) -> DescribeMessagesRequest:
        self.password = password
        return self

    def with_access_token(self, access_token: str) -> DescribeMessagesRequest:
        self.access_token = access_token
        return self

    def with_start_at(self, start_at: int) -> DescribeMessagesRequest:
        self.start_at = start_at
        return self

    def with_limit(self, limit: int) -> DescribeMessagesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeMessagesRequest]:
        if data is None:
            return None
        return DescribeMessagesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_password(data.get('password'))\
            .with_access_token(data.get('accessToken'))\
            .with_start_at(data.get('startAt'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "password": self.password,
            "accessToken": self.access_token,
            "startAt": self.start_at,
            "limit": self.limit,
        }


class DescribeMessagesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    password: str = None
    user_id: str = None
    start_at: int = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMessagesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> DescribeMessagesByUserIdRequest:
        self.room_name = room_name
        return self

    def with_password(self, password: str) -> DescribeMessagesByUserIdRequest:
        self.password = password
        return self

    def with_user_id(self, user_id: str) -> DescribeMessagesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_start_at(self, start_at: int) -> DescribeMessagesByUserIdRequest:
        self.start_at = start_at
        return self

    def with_limit(self, limit: int) -> DescribeMessagesByUserIdRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeMessagesByUserIdRequest]:
        if data is None:
            return None
        return DescribeMessagesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_password(data.get('password'))\
            .with_user_id(data.get('userId'))\
            .with_start_at(data.get('startAt'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "password": self.password,
            "userId": self.user_id,
            "startAt": self.start_at,
            "limit": self.limit,
        }


class PostRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    access_token: str = None
    category: int = None
    metadata: str = None
    password: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PostRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> PostRequest:
        self.room_name = room_name
        return self

    def with_access_token(self, access_token: str) -> PostRequest:
        self.access_token = access_token
        return self

    def with_category(self, category: int) -> PostRequest:
        self.category = category
        return self

    def with_metadata(self, metadata: str) -> PostRequest:
        self.metadata = metadata
        return self

    def with_password(self, password: str) -> PostRequest:
        self.password = password
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PostRequest]:
        if data is None:
            return None
        return PostRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_access_token(data.get('accessToken'))\
            .with_category(data.get('category'))\
            .with_metadata(data.get('metadata'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "accessToken": self.access_token,
            "category": self.category,
            "metadata": self.metadata,
            "password": self.password,
        }


class PostByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    user_id: str = None
    category: int = None
    metadata: str = None
    password: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PostByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> PostByUserIdRequest:
        self.room_name = room_name
        return self

    def with_user_id(self, user_id: str) -> PostByUserIdRequest:
        self.user_id = user_id
        return self

    def with_category(self, category: int) -> PostByUserIdRequest:
        self.category = category
        return self

    def with_metadata(self, metadata: str) -> PostByUserIdRequest:
        self.metadata = metadata
        return self

    def with_password(self, password: str) -> PostByUserIdRequest:
        self.password = password
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PostByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PostByUserIdRequest]:
        if data is None:
            return None
        return PostByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_user_id(data.get('userId'))\
            .with_category(data.get('category'))\
            .with_metadata(data.get('metadata'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "userId": self.user_id,
            "category": self.category,
            "metadata": self.metadata,
            "password": self.password,
        }


class GetMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    message_name: str = None
    password: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> GetMessageRequest:
        self.room_name = room_name
        return self

    def with_message_name(self, message_name: str) -> GetMessageRequest:
        self.message_name = message_name
        return self

    def with_password(self, password: str) -> GetMessageRequest:
        self.password = password
        return self

    def with_access_token(self, access_token: str) -> GetMessageRequest:
        self.access_token = access_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMessageRequest]:
        if data is None:
            return None
        return GetMessageRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_message_name(data.get('messageName'))\
            .with_password(data.get('password'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "messageName": self.message_name,
            "password": self.password,
            "accessToken": self.access_token,
        }


class GetMessageByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    message_name: str = None
    password: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMessageByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> GetMessageByUserIdRequest:
        self.room_name = room_name
        return self

    def with_message_name(self, message_name: str) -> GetMessageByUserIdRequest:
        self.message_name = message_name
        return self

    def with_password(self, password: str) -> GetMessageByUserIdRequest:
        self.password = password
        return self

    def with_user_id(self, user_id: str) -> GetMessageByUserIdRequest:
        self.user_id = user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMessageByUserIdRequest]:
        if data is None:
            return None
        return GetMessageByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_message_name(data.get('messageName'))\
            .with_password(data.get('password'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "messageName": self.message_name,
            "password": self.password,
            "userId": self.user_id,
        }


class DeleteMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    user_id: str = None
    message_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> DeleteMessageRequest:
        self.room_name = room_name
        return self

    def with_user_id(self, user_id: str) -> DeleteMessageRequest:
        self.user_id = user_id
        return self

    def with_message_name(self, message_name: str) -> DeleteMessageRequest:
        self.message_name = message_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMessageRequest]:
        if data is None:
            return None
        return DeleteMessageRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_user_id(data.get('userId'))\
            .with_message_name(data.get('messageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "userId": self.user_id,
            "messageName": self.message_name,
        }


class DescribeSubscribesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSubscribesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeSubscribesRequest]:
        if data is None:
            return None
        return DescribeSubscribesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSubscribesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSubscribesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribesByUserIdRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeSubscribesByUserIdRequest]:
        if data is None:
            return None
        return DescribeSubscribesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSubscribesByRoomNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribesByRoomNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> DescribeSubscribesByRoomNameRequest:
        self.room_name = room_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribesByRoomNameRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribesByRoomNameRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeSubscribesByRoomNameRequest]:
        if data is None:
            return None
        return DescribeSubscribesByRoomNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class SubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    access_token: str = None
    notification_types: List[NotificationType] = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> SubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> SubscribeRequest:
        self.room_name = room_name
        return self

    def with_access_token(self, access_token: str) -> SubscribeRequest:
        self.access_token = access_token
        return self

    def with_notification_types(self, notification_types: List[NotificationType]) -> SubscribeRequest:
        self.notification_types = notification_types
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeRequest]:
        if data is None:
            return None
        return SubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_access_token(data.get('accessToken'))\
            .with_notification_types([
                NotificationType.from_dict(data.get('notificationTypes')[i])
                for i in range(len(data.get('notificationTypes')) if data.get('notificationTypes') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "accessToken": self.access_token,
            "notificationTypes": [
                self.notification_types[i].to_dict() if self.notification_types[i] else None
                for i in range(len(self.notification_types) if self.notification_types else 0)
            ],
        }


class SubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    user_id: str = None
    notification_types: List[NotificationType] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> SubscribeByUserIdRequest:
        self.room_name = room_name
        return self

    def with_user_id(self, user_id: str) -> SubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_notification_types(self, notification_types: List[NotificationType]) -> SubscribeByUserIdRequest:
        self.notification_types = notification_types
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubscribeByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeByUserIdRequest]:
        if data is None:
            return None
        return SubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_user_id(data.get('userId'))\
            .with_notification_types([
                NotificationType.from_dict(data.get('notificationTypes')[i])
                for i in range(len(data.get('notificationTypes')) if data.get('notificationTypes') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "userId": self.user_id,
            "notificationTypes": [
                self.notification_types[i].to_dict() if self.notification_types[i] else None
                for i in range(len(self.notification_types) if self.notification_types else 0)
            ],
        }


class GetSubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> GetSubscribeRequest:
        self.room_name = room_name
        return self

    def with_access_token(self, access_token: str) -> GetSubscribeRequest:
        self.access_token = access_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSubscribeRequest]:
        if data is None:
            return None
        return GetSubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "accessToken": self.access_token,
        }


class GetSubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> GetSubscribeByUserIdRequest:
        self.room_name = room_name
        return self

    def with_user_id(self, user_id: str) -> GetSubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSubscribeByUserIdRequest]:
        if data is None:
            return None
        return GetSubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "userId": self.user_id,
        }


class UpdateNotificationTypeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    access_token: str = None
    notification_types: List[NotificationType] = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNotificationTypeRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> UpdateNotificationTypeRequest:
        self.room_name = room_name
        return self

    def with_access_token(self, access_token: str) -> UpdateNotificationTypeRequest:
        self.access_token = access_token
        return self

    def with_notification_types(self, notification_types: List[NotificationType]) -> UpdateNotificationTypeRequest:
        self.notification_types = notification_types
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateNotificationTypeRequest]:
        if data is None:
            return None
        return UpdateNotificationTypeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_access_token(data.get('accessToken'))\
            .with_notification_types([
                NotificationType.from_dict(data.get('notificationTypes')[i])
                for i in range(len(data.get('notificationTypes')) if data.get('notificationTypes') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "accessToken": self.access_token,
            "notificationTypes": [
                self.notification_types[i].to_dict() if self.notification_types[i] else None
                for i in range(len(self.notification_types) if self.notification_types else 0)
            ],
        }


class UpdateNotificationTypeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    user_id: str = None
    notification_types: List[NotificationType] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNotificationTypeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> UpdateNotificationTypeByUserIdRequest:
        self.room_name = room_name
        return self

    def with_user_id(self, user_id: str) -> UpdateNotificationTypeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_notification_types(self, notification_types: List[NotificationType]) -> UpdateNotificationTypeByUserIdRequest:
        self.notification_types = notification_types
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateNotificationTypeByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateNotificationTypeByUserIdRequest]:
        if data is None:
            return None
        return UpdateNotificationTypeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_user_id(data.get('userId'))\
            .with_notification_types([
                NotificationType.from_dict(data.get('notificationTypes')[i])
                for i in range(len(data.get('notificationTypes')) if data.get('notificationTypes') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "userId": self.user_id,
            "notificationTypes": [
                self.notification_types[i].to_dict() if self.notification_types[i] else None
                for i in range(len(self.notification_types) if self.notification_types else 0)
            ],
        }


class UnsubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UnsubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> UnsubscribeRequest:
        self.room_name = room_name
        return self

    def with_access_token(self, access_token: str) -> UnsubscribeRequest:
        self.access_token = access_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UnsubscribeRequest]:
        if data is None:
            return None
        return UnsubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "accessToken": self.access_token,
        }


class UnsubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    room_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnsubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_room_name(self, room_name: str) -> UnsubscribeByUserIdRequest:
        self.room_name = room_name
        return self

    def with_user_id(self, user_id: str) -> UnsubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnsubscribeByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UnsubscribeByUserIdRequest]:
        if data is None:
            return None
        return UnsubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_room_name(data.get('roomName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "roomName": self.room_name,
            "userId": self.user_id,
        }