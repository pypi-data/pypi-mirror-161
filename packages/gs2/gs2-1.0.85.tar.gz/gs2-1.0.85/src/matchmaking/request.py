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

from matchmaking.model import *


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
    enable_rating: bool = None
    create_gathering_trigger_type: str = None
    create_gathering_trigger_realtime_namespace_id: str = None
    create_gathering_trigger_script_id: str = None
    complete_matchmaking_trigger_type: str = None
    complete_matchmaking_trigger_realtime_namespace_id: str = None
    complete_matchmaking_trigger_script_id: str = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    complete_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_enable_rating(self, enable_rating: bool) -> CreateNamespaceRequest:
        self.enable_rating = enable_rating
        return self

    def with_create_gathering_trigger_type(self, create_gathering_trigger_type: str) -> CreateNamespaceRequest:
        self.create_gathering_trigger_type = create_gathering_trigger_type
        return self

    def with_create_gathering_trigger_realtime_namespace_id(self, create_gathering_trigger_realtime_namespace_id: str) -> CreateNamespaceRequest:
        self.create_gathering_trigger_realtime_namespace_id = create_gathering_trigger_realtime_namespace_id
        return self

    def with_create_gathering_trigger_script_id(self, create_gathering_trigger_script_id: str) -> CreateNamespaceRequest:
        self.create_gathering_trigger_script_id = create_gathering_trigger_script_id
        return self

    def with_complete_matchmaking_trigger_type(self, complete_matchmaking_trigger_type: str) -> CreateNamespaceRequest:
        self.complete_matchmaking_trigger_type = complete_matchmaking_trigger_type
        return self

    def with_complete_matchmaking_trigger_realtime_namespace_id(self, complete_matchmaking_trigger_realtime_namespace_id: str) -> CreateNamespaceRequest:
        self.complete_matchmaking_trigger_realtime_namespace_id = complete_matchmaking_trigger_realtime_namespace_id
        return self

    def with_complete_matchmaking_trigger_script_id(self, complete_matchmaking_trigger_script_id: str) -> CreateNamespaceRequest:
        self.complete_matchmaking_trigger_script_id = complete_matchmaking_trigger_script_id
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.leave_notification = leave_notification
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.complete_notification = complete_notification
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
            .with_enable_rating(data.get('enableRating'))\
            .with_create_gathering_trigger_type(data.get('createGatheringTriggerType'))\
            .with_create_gathering_trigger_realtime_namespace_id(data.get('createGatheringTriggerRealtimeNamespaceId'))\
            .with_create_gathering_trigger_script_id(data.get('createGatheringTriggerScriptId'))\
            .with_complete_matchmaking_trigger_type(data.get('completeMatchmakingTriggerType'))\
            .with_complete_matchmaking_trigger_realtime_namespace_id(data.get('completeMatchmakingTriggerRealtimeNamespaceId'))\
            .with_complete_matchmaking_trigger_script_id(data.get('completeMatchmakingTriggerScriptId'))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "enableRating": self.enable_rating,
            "createGatheringTriggerType": self.create_gathering_trigger_type,
            "createGatheringTriggerRealtimeNamespaceId": self.create_gathering_trigger_realtime_namespace_id,
            "createGatheringTriggerScriptId": self.create_gathering_trigger_script_id,
            "completeMatchmakingTriggerType": self.complete_matchmaking_trigger_type,
            "completeMatchmakingTriggerRealtimeNamespaceId": self.complete_matchmaking_trigger_realtime_namespace_id,
            "completeMatchmakingTriggerScriptId": self.complete_matchmaking_trigger_script_id,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
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
    enable_rating: bool = None
    create_gathering_trigger_type: str = None
    create_gathering_trigger_realtime_namespace_id: str = None
    create_gathering_trigger_script_id: str = None
    complete_matchmaking_trigger_type: str = None
    complete_matchmaking_trigger_realtime_namespace_id: str = None
    complete_matchmaking_trigger_script_id: str = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    complete_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_enable_rating(self, enable_rating: bool) -> UpdateNamespaceRequest:
        self.enable_rating = enable_rating
        return self

    def with_create_gathering_trigger_type(self, create_gathering_trigger_type: str) -> UpdateNamespaceRequest:
        self.create_gathering_trigger_type = create_gathering_trigger_type
        return self

    def with_create_gathering_trigger_realtime_namespace_id(self, create_gathering_trigger_realtime_namespace_id: str) -> UpdateNamespaceRequest:
        self.create_gathering_trigger_realtime_namespace_id = create_gathering_trigger_realtime_namespace_id
        return self

    def with_create_gathering_trigger_script_id(self, create_gathering_trigger_script_id: str) -> UpdateNamespaceRequest:
        self.create_gathering_trigger_script_id = create_gathering_trigger_script_id
        return self

    def with_complete_matchmaking_trigger_type(self, complete_matchmaking_trigger_type: str) -> UpdateNamespaceRequest:
        self.complete_matchmaking_trigger_type = complete_matchmaking_trigger_type
        return self

    def with_complete_matchmaking_trigger_realtime_namespace_id(self, complete_matchmaking_trigger_realtime_namespace_id: str) -> UpdateNamespaceRequest:
        self.complete_matchmaking_trigger_realtime_namespace_id = complete_matchmaking_trigger_realtime_namespace_id
        return self

    def with_complete_matchmaking_trigger_script_id(self, complete_matchmaking_trigger_script_id: str) -> UpdateNamespaceRequest:
        self.complete_matchmaking_trigger_script_id = complete_matchmaking_trigger_script_id
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.leave_notification = leave_notification
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.complete_notification = complete_notification
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
            .with_enable_rating(data.get('enableRating'))\
            .with_create_gathering_trigger_type(data.get('createGatheringTriggerType'))\
            .with_create_gathering_trigger_realtime_namespace_id(data.get('createGatheringTriggerRealtimeNamespaceId'))\
            .with_create_gathering_trigger_script_id(data.get('createGatheringTriggerScriptId'))\
            .with_complete_matchmaking_trigger_type(data.get('completeMatchmakingTriggerType'))\
            .with_complete_matchmaking_trigger_realtime_namespace_id(data.get('completeMatchmakingTriggerRealtimeNamespaceId'))\
            .with_complete_matchmaking_trigger_script_id(data.get('completeMatchmakingTriggerScriptId'))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "enableRating": self.enable_rating,
            "createGatheringTriggerType": self.create_gathering_trigger_type,
            "createGatheringTriggerRealtimeNamespaceId": self.create_gathering_trigger_realtime_namespace_id,
            "createGatheringTriggerScriptId": self.create_gathering_trigger_script_id,
            "completeMatchmakingTriggerType": self.complete_matchmaking_trigger_type,
            "completeMatchmakingTriggerRealtimeNamespaceId": self.complete_matchmaking_trigger_realtime_namespace_id,
            "completeMatchmakingTriggerScriptId": self.complete_matchmaking_trigger_script_id,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
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


class DescribeGatheringsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGatheringsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGatheringsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGatheringsRequest:
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
    ) -> Optional[DescribeGatheringsRequest]:
        if data is None:
            return None
        return DescribeGatheringsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    player: Player = None
    attribute_ranges: List[AttributeRange] = None
    capacity_of_roles: List[CapacityOfRole] = None
    allow_user_ids: List[str] = None
    expires_at: int = None
    expires_at_time_span: TimeSpan = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreateGatheringRequest:
        self.access_token = access_token
        return self

    def with_player(self, player: Player) -> CreateGatheringRequest:
        self.player = player
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> CreateGatheringRequest:
        self.attribute_ranges = attribute_ranges
        return self

    def with_capacity_of_roles(self, capacity_of_roles: List[CapacityOfRole]) -> CreateGatheringRequest:
        self.capacity_of_roles = capacity_of_roles
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> CreateGatheringRequest:
        self.allow_user_ids = allow_user_ids
        return self

    def with_expires_at(self, expires_at: int) -> CreateGatheringRequest:
        self.expires_at = expires_at
        return self

    def with_expires_at_time_span(self, expires_at_time_span: TimeSpan) -> CreateGatheringRequest:
        self.expires_at_time_span = expires_at_time_span
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
    ) -> Optional[CreateGatheringRequest]:
        if data is None:
            return None
        return CreateGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_attribute_ranges([
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')) if data.get('attributeRanges') else 0)
            ])\
            .with_capacity_of_roles([
                CapacityOfRole.from_dict(data.get('capacityOfRoles')[i])
                for i in range(len(data.get('capacityOfRoles')) if data.get('capacityOfRoles') else 0)
            ])\
            .with_allow_user_ids([
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')) if data.get('allowUserIds') else 0)
            ])\
            .with_expires_at(data.get('expiresAt'))\
            .with_expires_at_time_span(TimeSpan.from_dict(data.get('expiresAtTimeSpan')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "player": self.player.to_dict() if self.player else None,
            "attributeRanges": [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges) if self.attribute_ranges else 0)
            ],
            "capacityOfRoles": [
                self.capacity_of_roles[i].to_dict() if self.capacity_of_roles[i] else None
                for i in range(len(self.capacity_of_roles) if self.capacity_of_roles else 0)
            ],
            "allowUserIds": [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids) if self.allow_user_ids else 0)
            ],
            "expiresAt": self.expires_at,
            "expiresAtTimeSpan": self.expires_at_time_span.to_dict() if self.expires_at_time_span else None,
        }


class CreateGatheringByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    player: Player = None
    attribute_ranges: List[AttributeRange] = None
    capacity_of_roles: List[CapacityOfRole] = None
    allow_user_ids: List[str] = None
    expires_at: int = None
    expires_at_time_span: TimeSpan = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGatheringByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateGatheringByUserIdRequest:
        self.user_id = user_id
        return self

    def with_player(self, player: Player) -> CreateGatheringByUserIdRequest:
        self.player = player
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> CreateGatheringByUserIdRequest:
        self.attribute_ranges = attribute_ranges
        return self

    def with_capacity_of_roles(self, capacity_of_roles: List[CapacityOfRole]) -> CreateGatheringByUserIdRequest:
        self.capacity_of_roles = capacity_of_roles
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> CreateGatheringByUserIdRequest:
        self.allow_user_ids = allow_user_ids
        return self

    def with_expires_at(self, expires_at: int) -> CreateGatheringByUserIdRequest:
        self.expires_at = expires_at
        return self

    def with_expires_at_time_span(self, expires_at_time_span: TimeSpan) -> CreateGatheringByUserIdRequest:
        self.expires_at_time_span = expires_at_time_span
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateGatheringByUserIdRequest:
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
    ) -> Optional[CreateGatheringByUserIdRequest]:
        if data is None:
            return None
        return CreateGatheringByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_attribute_ranges([
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')) if data.get('attributeRanges') else 0)
            ])\
            .with_capacity_of_roles([
                CapacityOfRole.from_dict(data.get('capacityOfRoles')[i])
                for i in range(len(data.get('capacityOfRoles')) if data.get('capacityOfRoles') else 0)
            ])\
            .with_allow_user_ids([
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')) if data.get('allowUserIds') else 0)
            ])\
            .with_expires_at(data.get('expiresAt'))\
            .with_expires_at_time_span(TimeSpan.from_dict(data.get('expiresAtTimeSpan')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "player": self.player.to_dict() if self.player else None,
            "attributeRanges": [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges) if self.attribute_ranges else 0)
            ],
            "capacityOfRoles": [
                self.capacity_of_roles[i].to_dict() if self.capacity_of_roles[i] else None
                for i in range(len(self.capacity_of_roles) if self.capacity_of_roles else 0)
            ],
            "allowUserIds": [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids) if self.allow_user_ids else 0)
            ],
            "expiresAt": self.expires_at,
            "expiresAtTimeSpan": self.expires_at_time_span.to_dict() if self.expires_at_time_span else None,
        }


class UpdateGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    access_token: str = None
    attribute_ranges: List[AttributeRange] = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> UpdateGatheringRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> UpdateGatheringRequest:
        self.access_token = access_token
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> UpdateGatheringRequest:
        self.attribute_ranges = attribute_ranges
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
    ) -> Optional[UpdateGatheringRequest]:
        if data is None:
            return None
        return UpdateGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))\
            .with_attribute_ranges([
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')) if data.get('attributeRanges') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
            "attributeRanges": [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges) if self.attribute_ranges else 0)
            ],
        }


class UpdateGatheringByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    user_id: str = None
    attribute_ranges: List[AttributeRange] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGatheringByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> UpdateGatheringByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> UpdateGatheringByUserIdRequest:
        self.user_id = user_id
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> UpdateGatheringByUserIdRequest:
        self.attribute_ranges = attribute_ranges
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateGatheringByUserIdRequest:
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
    ) -> Optional[UpdateGatheringByUserIdRequest]:
        if data is None:
            return None
        return UpdateGatheringByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_attribute_ranges([
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')) if data.get('attributeRanges') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
            "attributeRanges": [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges) if self.attribute_ranges else 0)
            ],
        }


class DoMatchmakingByPlayerRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    player: Player = None
    matchmaking_context_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DoMatchmakingByPlayerRequest:
        self.namespace_name = namespace_name
        return self

    def with_player(self, player: Player) -> DoMatchmakingByPlayerRequest:
        self.player = player
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingByPlayerRequest:
        self.matchmaking_context_token = matchmaking_context_token
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
    ) -> Optional[DoMatchmakingByPlayerRequest]:
        if data is None:
            return None
        return DoMatchmakingByPlayerRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "player": self.player.to_dict() if self.player else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class DoMatchmakingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    player: Player = None
    matchmaking_context_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DoMatchmakingRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DoMatchmakingRequest:
        self.access_token = access_token
        return self

    def with_player(self, player: Player) -> DoMatchmakingRequest:
        self.player = player
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingRequest:
        self.matchmaking_context_token = matchmaking_context_token
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
    ) -> Optional[DoMatchmakingRequest]:
        if data is None:
            return None
        return DoMatchmakingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "player": self.player.to_dict() if self.player else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class DoMatchmakingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    player: Player = None
    matchmaking_context_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DoMatchmakingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DoMatchmakingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_player(self, player: Player) -> DoMatchmakingByUserIdRequest:
        self.player = player
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingByUserIdRequest:
        self.matchmaking_context_token = matchmaking_context_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DoMatchmakingByUserIdRequest:
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
    ) -> Optional[DoMatchmakingByUserIdRequest]:
        if data is None:
            return None
        return DoMatchmakingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "player": self.player.to_dict() if self.player else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class GetGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> GetGatheringRequest:
        self.gathering_name = gathering_name
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
    ) -> Optional[GetGatheringRequest]:
        if data is None:
            return None
        return GetGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
        }


class CancelMatchmakingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CancelMatchmakingRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> CancelMatchmakingRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> CancelMatchmakingRequest:
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
    ) -> Optional[CancelMatchmakingRequest]:
        if data is None:
            return None
        return CancelMatchmakingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
        }


class CancelMatchmakingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CancelMatchmakingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> CancelMatchmakingByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> CancelMatchmakingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CancelMatchmakingByUserIdRequest:
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
    ) -> Optional[CancelMatchmakingByUserIdRequest]:
        if data is None:
            return None
        return CancelMatchmakingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
        }


class DeleteGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> DeleteGatheringRequest:
        self.gathering_name = gathering_name
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
    ) -> Optional[DeleteGatheringRequest]:
        if data is None:
            return None
        return DeleteGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
        }


class DescribeRatingModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRatingModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRatingModelMastersRequest:
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
    ) -> Optional[DescribeRatingModelMastersRequest]:
        if data is None:
            return None
        return DescribeRatingModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    volatility: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRatingModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRatingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRatingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_volatility(self, volatility: int) -> CreateRatingModelMasterRequest:
        self.volatility = volatility
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
    ) -> Optional[CreateRatingModelMasterRequest]:
        if data is None:
            return None
        return CreateRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_volatility(data.get('volatility'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "volatility": self.volatility,
        }


class GetRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingModelMasterRequest:
        self.rating_name = rating_name
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
    ) -> Optional[GetRatingModelMasterRequest]:
        if data is None:
            return None
        return GetRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
        }


class UpdateRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    description: str = None
    metadata: str = None
    volatility: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> UpdateRatingModelMasterRequest:
        self.rating_name = rating_name
        return self

    def with_description(self, description: str) -> UpdateRatingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRatingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_volatility(self, volatility: int) -> UpdateRatingModelMasterRequest:
        self.volatility = volatility
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
    ) -> Optional[UpdateRatingModelMasterRequest]:
        if data is None:
            return None
        return UpdateRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_volatility(data.get('volatility'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "description": self.description,
            "metadata": self.metadata,
            "volatility": self.volatility,
        }


class DeleteRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> DeleteRatingModelMasterRequest:
        self.rating_name = rating_name
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
    ) -> Optional[DeleteRatingModelMasterRequest]:
        if data is None:
            return None
        return DeleteRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
        }


class DescribeRatingModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingModelsRequest:
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
    ) -> Optional[DescribeRatingModelsRequest]:
        if data is None:
            return None
        return DescribeRatingModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetRatingModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingModelRequest:
        self.rating_name = rating_name
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
    ) -> Optional[GetRatingModelRequest]:
        if data is None:
            return None
        return GetRatingModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
        }


class ExportMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> ExportMasterRequest:
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
    ) -> Optional[ExportMasterRequest]:
        if data is None:
            return None
        return ExportMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCurrentRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentRatingModelMasterRequest:
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
    ) -> Optional[GetCurrentRatingModelMasterRequest]:
        if data is None:
            return None
        return GetCurrentRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentRatingModelMasterRequest:
        self.settings = settings
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
    ) -> Optional[UpdateCurrentRatingModelMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentRatingModelMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRatingModelMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentRatingModelMasterFromGitHubRequest:
        self.checkout_setting = checkout_setting
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
    ) -> Optional[UpdateCurrentRatingModelMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentRatingModelMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeRatingsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeRatingsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeRatingsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRatingsRequest:
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
    ) -> Optional[DescribeRatingsRequest]:
        if data is None:
            return None
        return DescribeRatingsRequest()\
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


class DescribeRatingsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeRatingsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeRatingsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRatingsByUserIdRequest:
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
    ) -> Optional[DescribeRatingsByUserIdRequest]:
        if data is None:
            return None
        return DescribeRatingsByUserIdRequest()\
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


class GetRatingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    rating_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetRatingRequest:
        self.access_token = access_token
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingRequest:
        self.rating_name = rating_name
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
    ) -> Optional[GetRatingRequest]:
        if data is None:
            return None
        return GetRatingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "ratingName": self.rating_name,
        }


class GetRatingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetRatingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingByUserIdRequest:
        self.rating_name = rating_name
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
    ) -> Optional[GetRatingByUserIdRequest]:
        if data is None:
            return None
        return GetRatingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "ratingName": self.rating_name,
        }


class PutResultRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    game_results: List[GameResult] = None

    def with_namespace_name(self, namespace_name: str) -> PutResultRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> PutResultRequest:
        self.rating_name = rating_name
        return self

    def with_game_results(self, game_results: List[GameResult]) -> PutResultRequest:
        self.game_results = game_results
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
    ) -> Optional[PutResultRequest]:
        if data is None:
            return None
        return PutResultRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_game_results([
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')) if data.get('gameResults') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gameResults": [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results) if self.game_results else 0)
            ],
        }


class DeleteRatingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rating_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRatingRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteRatingRequest:
        self.user_id = user_id
        return self

    def with_rating_name(self, rating_name: str) -> DeleteRatingRequest:
        self.rating_name = rating_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteRatingRequest:
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
    ) -> Optional[DeleteRatingRequest]:
        if data is None:
            return None
        return DeleteRatingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "ratingName": self.rating_name,
        }


class GetBallotRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    gathering_name: str = None
    access_token: str = None
    number_of_player: int = None
    key_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBallotRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetBallotRequest:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> GetBallotRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> GetBallotRequest:
        self.access_token = access_token
        return self

    def with_number_of_player(self, number_of_player: int) -> GetBallotRequest:
        self.number_of_player = number_of_player
        return self

    def with_key_id(self, key_id: str) -> GetBallotRequest:
        self.key_id = key_id
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
    ) -> Optional[GetBallotRequest]:
        if data is None:
            return None
        return GetBallotRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))\
            .with_number_of_player(data.get('numberOfPlayer'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
            "numberOfPlayer": self.number_of_player,
            "keyId": self.key_id,
        }


class GetBallotByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    gathering_name: str = None
    user_id: str = None
    number_of_player: int = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBallotByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetBallotByUserIdRequest:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> GetBallotByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> GetBallotByUserIdRequest:
        self.user_id = user_id
        return self

    def with_number_of_player(self, number_of_player: int) -> GetBallotByUserIdRequest:
        self.number_of_player = number_of_player
        return self

    def with_key_id(self, key_id: str) -> GetBallotByUserIdRequest:
        self.key_id = key_id
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
    ) -> Optional[GetBallotByUserIdRequest]:
        if data is None:
            return None
        return GetBallotByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_number_of_player(data.get('numberOfPlayer'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
            "numberOfPlayer": self.number_of_player,
            "keyId": self.key_id,
        }


class VoteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ballot_body: str = None
    ballot_signature: str = None
    game_results: List[GameResult] = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> VoteRequest:
        self.namespace_name = namespace_name
        return self

    def with_ballot_body(self, ballot_body: str) -> VoteRequest:
        self.ballot_body = ballot_body
        return self

    def with_ballot_signature(self, ballot_signature: str) -> VoteRequest:
        self.ballot_signature = ballot_signature
        return self

    def with_game_results(self, game_results: List[GameResult]) -> VoteRequest:
        self.game_results = game_results
        return self

    def with_key_id(self, key_id: str) -> VoteRequest:
        self.key_id = key_id
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
    ) -> Optional[VoteRequest]:
        if data is None:
            return None
        return VoteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ballot_body(data.get('ballotBody'))\
            .with_ballot_signature(data.get('ballotSignature'))\
            .with_game_results([
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')) if data.get('gameResults') else 0)
            ])\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ballotBody": self.ballot_body,
            "ballotSignature": self.ballot_signature,
            "gameResults": [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results) if self.game_results else 0)
            ],
            "keyId": self.key_id,
        }


class VoteMultipleRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    signed_ballots: List[SignedBallot] = None
    game_results: List[GameResult] = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> VoteMultipleRequest:
        self.namespace_name = namespace_name
        return self

    def with_signed_ballots(self, signed_ballots: List[SignedBallot]) -> VoteMultipleRequest:
        self.signed_ballots = signed_ballots
        return self

    def with_game_results(self, game_results: List[GameResult]) -> VoteMultipleRequest:
        self.game_results = game_results
        return self

    def with_key_id(self, key_id: str) -> VoteMultipleRequest:
        self.key_id = key_id
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
    ) -> Optional[VoteMultipleRequest]:
        if data is None:
            return None
        return VoteMultipleRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_signed_ballots([
                SignedBallot.from_dict(data.get('signedBallots')[i])
                for i in range(len(data.get('signedBallots')) if data.get('signedBallots') else 0)
            ])\
            .with_game_results([
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')) if data.get('gameResults') else 0)
            ])\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "signedBallots": [
                self.signed_ballots[i].to_dict() if self.signed_ballots[i] else None
                for i in range(len(self.signed_ballots) if self.signed_ballots else 0)
            ],
            "gameResults": [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results) if self.game_results else 0)
            ],
            "keyId": self.key_id,
        }


class CommitVoteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CommitVoteRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> CommitVoteRequest:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> CommitVoteRequest:
        self.gathering_name = gathering_name
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
    ) -> Optional[CommitVoteRequest]:
        if data is None:
            return None
        return CommitVoteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
        }