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

from inbox.model import *


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
    is_automatic_deleting_enabled: bool = None
    transaction_setting: TransactionSetting = None
    receive_message_script: ScriptSetting = None
    read_message_script: ScriptSetting = None
    delete_message_script: ScriptSetting = None
    receive_notification: NotificationSetting = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_is_automatic_deleting_enabled(self, is_automatic_deleting_enabled: bool) -> CreateNamespaceRequest:
        self.is_automatic_deleting_enabled = is_automatic_deleting_enabled
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> CreateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_receive_message_script(self, receive_message_script: ScriptSetting) -> CreateNamespaceRequest:
        self.receive_message_script = receive_message_script
        return self

    def with_read_message_script(self, read_message_script: ScriptSetting) -> CreateNamespaceRequest:
        self.read_message_script = read_message_script
        return self

    def with_delete_message_script(self, delete_message_script: ScriptSetting) -> CreateNamespaceRequest:
        self.delete_message_script = delete_message_script
        return self

    def with_receive_notification(self, receive_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.receive_notification = receive_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> CreateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> CreateNamespaceRequest:
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
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_is_automatic_deleting_enabled(data.get('isAutomaticDeletingEnabled'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_receive_message_script(ScriptSetting.from_dict(data.get('receiveMessageScript')))\
            .with_read_message_script(ScriptSetting.from_dict(data.get('readMessageScript')))\
            .with_delete_message_script(ScriptSetting.from_dict(data.get('deleteMessageScript')))\
            .with_receive_notification(NotificationSetting.from_dict(data.get('receiveNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "isAutomaticDeletingEnabled": self.is_automatic_deleting_enabled,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveMessageScript": self.receive_message_script.to_dict() if self.receive_message_script else None,
            "readMessageScript": self.read_message_script.to_dict() if self.read_message_script else None,
            "deleteMessageScript": self.delete_message_script.to_dict() if self.delete_message_script else None,
            "receiveNotification": self.receive_notification.to_dict() if self.receive_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
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
    is_automatic_deleting_enabled: bool = None
    transaction_setting: TransactionSetting = None
    receive_message_script: ScriptSetting = None
    read_message_script: ScriptSetting = None
    delete_message_script: ScriptSetting = None
    receive_notification: NotificationSetting = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_is_automatic_deleting_enabled(self, is_automatic_deleting_enabled: bool) -> UpdateNamespaceRequest:
        self.is_automatic_deleting_enabled = is_automatic_deleting_enabled
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> UpdateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_receive_message_script(self, receive_message_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.receive_message_script = receive_message_script
        return self

    def with_read_message_script(self, read_message_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.read_message_script = read_message_script
        return self

    def with_delete_message_script(self, delete_message_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.delete_message_script = delete_message_script
        return self

    def with_receive_notification(self, receive_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.receive_notification = receive_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> UpdateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> UpdateNamespaceRequest:
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
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_is_automatic_deleting_enabled(data.get('isAutomaticDeletingEnabled'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_receive_message_script(ScriptSetting.from_dict(data.get('receiveMessageScript')))\
            .with_read_message_script(ScriptSetting.from_dict(data.get('readMessageScript')))\
            .with_delete_message_script(ScriptSetting.from_dict(data.get('deleteMessageScript')))\
            .with_receive_notification(NotificationSetting.from_dict(data.get('receiveNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "isAutomaticDeletingEnabled": self.is_automatic_deleting_enabled,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveMessageScript": self.receive_message_script.to_dict() if self.receive_message_script else None,
            "readMessageScript": self.read_message_script.to_dict() if self.read_message_script else None,
            "deleteMessageScript": self.delete_message_script.to_dict() if self.delete_message_script else None,
            "receiveNotification": self.receive_notification.to_dict() if self.receive_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
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


class DescribeMessagesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMessagesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeMessagesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeMessagesRequest:
        self.page_token = page_token
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


class DescribeMessagesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMessagesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeMessagesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeMessagesByUserIdRequest:
        self.page_token = page_token
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


class SendMessageByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    metadata: str = None
    read_acquire_actions: List[AcquireAction] = None
    expires_at: int = None
    expires_time_span: TimeSpan = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SendMessageByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SendMessageByUserIdRequest:
        self.user_id = user_id
        return self

    def with_metadata(self, metadata: str) -> SendMessageByUserIdRequest:
        self.metadata = metadata
        return self

    def with_read_acquire_actions(self, read_acquire_actions: List[AcquireAction]) -> SendMessageByUserIdRequest:
        self.read_acquire_actions = read_acquire_actions
        return self

    def with_expires_at(self, expires_at: int) -> SendMessageByUserIdRequest:
        self.expires_at = expires_at
        return self

    def with_expires_time_span(self, expires_time_span: TimeSpan) -> SendMessageByUserIdRequest:
        self.expires_time_span = expires_time_span
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SendMessageByUserIdRequest:
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
    ) -> Optional[SendMessageByUserIdRequest]:
        if data is None:
            return None
        return SendMessageByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_metadata(data.get('metadata'))\
            .with_read_acquire_actions([
                AcquireAction.from_dict(data.get('readAcquireActions')[i])
                for i in range(len(data.get('readAcquireActions')) if data.get('readAcquireActions') else 0)
            ])\
            .with_expires_at(data.get('expiresAt'))\
            .with_expires_time_span(TimeSpan.from_dict(data.get('expiresTimeSpan')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "metadata": self.metadata,
            "readAcquireActions": [
                self.read_acquire_actions[i].to_dict() if self.read_acquire_actions[i] else None
                for i in range(len(self.read_acquire_actions) if self.read_acquire_actions else 0)
            ],
            "expiresAt": self.expires_at,
            "expiresTimeSpan": self.expires_time_span.to_dict() if self.expires_time_span else None,
        }


class GetMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    message_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetMessageRequest:
        self.access_token = access_token
        return self

    def with_message_name(self, message_name: str) -> GetMessageRequest:
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
    ) -> Optional[GetMessageRequest]:
        if data is None:
            return None
        return GetMessageRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_message_name(data.get('messageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "messageName": self.message_name,
        }


class GetMessageByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    message_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMessageByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetMessageByUserIdRequest:
        self.user_id = user_id
        return self

    def with_message_name(self, message_name: str) -> GetMessageByUserIdRequest:
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
    ) -> Optional[GetMessageByUserIdRequest]:
        if data is None:
            return None
        return GetMessageByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_message_name(data.get('messageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "messageName": self.message_name,
        }


class ReceiveGlobalMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveGlobalMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> ReceiveGlobalMessageRequest:
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
    ) -> Optional[ReceiveGlobalMessageRequest]:
        if data is None:
            return None
        return ReceiveGlobalMessageRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class ReceiveGlobalMessageByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveGlobalMessageByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> ReceiveGlobalMessageByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReceiveGlobalMessageByUserIdRequest:
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
    ) -> Optional[ReceiveGlobalMessageByUserIdRequest]:
        if data is None:
            return None
        return ReceiveGlobalMessageByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }


class OpenMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    message_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> OpenMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> OpenMessageRequest:
        self.access_token = access_token
        return self

    def with_message_name(self, message_name: str) -> OpenMessageRequest:
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
    ) -> Optional[OpenMessageRequest]:
        if data is None:
            return None
        return OpenMessageRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_message_name(data.get('messageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "messageName": self.message_name,
        }


class OpenMessageByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    message_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> OpenMessageByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> OpenMessageByUserIdRequest:
        self.user_id = user_id
        return self

    def with_message_name(self, message_name: str) -> OpenMessageByUserIdRequest:
        self.message_name = message_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> OpenMessageByUserIdRequest:
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
    ) -> Optional[OpenMessageByUserIdRequest]:
        if data is None:
            return None
        return OpenMessageByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_message_name(data.get('messageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "messageName": self.message_name,
        }


class ReadMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    message_name: str = None
    config: List[Config] = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> ReadMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> ReadMessageRequest:
        self.access_token = access_token
        return self

    def with_message_name(self, message_name: str) -> ReadMessageRequest:
        self.message_name = message_name
        return self

    def with_config(self, config: List[Config]) -> ReadMessageRequest:
        self.config = config
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
    ) -> Optional[ReadMessageRequest]:
        if data is None:
            return None
        return ReadMessageRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_message_name(data.get('messageName'))\
            .with_config([
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')) if data.get('config') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "messageName": self.message_name,
            "config": [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config) if self.config else 0)
            ],
        }


class ReadMessageByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    message_name: str = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReadMessageByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> ReadMessageByUserIdRequest:
        self.user_id = user_id
        return self

    def with_message_name(self, message_name: str) -> ReadMessageByUserIdRequest:
        self.message_name = message_name
        return self

    def with_config(self, config: List[Config]) -> ReadMessageByUserIdRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReadMessageByUserIdRequest:
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
    ) -> Optional[ReadMessageByUserIdRequest]:
        if data is None:
            return None
        return ReadMessageByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_message_name(data.get('messageName'))\
            .with_config([
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')) if data.get('config') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "messageName": self.message_name,
            "config": [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config) if self.config else 0)
            ],
        }


class DeleteMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    message_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteMessageRequest:
        self.access_token = access_token
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
            .with_access_token(data.get('accessToken'))\
            .with_message_name(data.get('messageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "messageName": self.message_name,
        }


class DeleteMessageByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    message_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMessageByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteMessageByUserIdRequest:
        self.user_id = user_id
        return self

    def with_message_name(self, message_name: str) -> DeleteMessageByUserIdRequest:
        self.message_name = message_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteMessageByUserIdRequest:
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
    ) -> Optional[DeleteMessageByUserIdRequest]:
        if data is None:
            return None
        return DeleteMessageByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_message_name(data.get('messageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "messageName": self.message_name,
        }


class SendByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SendByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SendByStampSheetRequest:
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
    ) -> Optional[SendByStampSheetRequest]:
        if data is None:
            return None
        return SendByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class OpenByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> OpenByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> OpenByStampTaskRequest:
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
    ) -> Optional[OpenByStampTaskRequest]:
        if data is None:
            return None
        return OpenByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
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


class GetCurrentMessageMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentMessageMasterRequest:
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
    ) -> Optional[GetCurrentMessageMasterRequest]:
        if data is None:
            return None
        return GetCurrentMessageMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentMessageMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentMessageMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentMessageMasterRequest:
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
    ) -> Optional[UpdateCurrentMessageMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentMessageMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentMessageMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentMessageMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentMessageMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentMessageMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentMessageMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeGlobalMessageMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalMessageMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalMessageMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalMessageMastersRequest:
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
    ) -> Optional[DescribeGlobalMessageMastersRequest]:
        if data is None:
            return None
        return DescribeGlobalMessageMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateGlobalMessageMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    metadata: str = None
    read_acquire_actions: List[AcquireAction] = None
    expires_time_span: TimeSpan = None
    expires_at: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateGlobalMessageMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateGlobalMessageMasterRequest:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CreateGlobalMessageMasterRequest:
        self.metadata = metadata
        return self

    def with_read_acquire_actions(self, read_acquire_actions: List[AcquireAction]) -> CreateGlobalMessageMasterRequest:
        self.read_acquire_actions = read_acquire_actions
        return self

    def with_expires_time_span(self, expires_time_span: TimeSpan) -> CreateGlobalMessageMasterRequest:
        self.expires_time_span = expires_time_span
        return self

    def with_expires_at(self, expires_at: int) -> CreateGlobalMessageMasterRequest:
        self.expires_at = expires_at
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
    ) -> Optional[CreateGlobalMessageMasterRequest]:
        if data is None:
            return None
        return CreateGlobalMessageMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_read_acquire_actions([
                AcquireAction.from_dict(data.get('readAcquireActions')[i])
                for i in range(len(data.get('readAcquireActions')) if data.get('readAcquireActions') else 0)
            ])\
            .with_expires_time_span(TimeSpan.from_dict(data.get('expiresTimeSpan')))\
            .with_expires_at(data.get('expiresAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "metadata": self.metadata,
            "readAcquireActions": [
                self.read_acquire_actions[i].to_dict() if self.read_acquire_actions[i] else None
                for i in range(len(self.read_acquire_actions) if self.read_acquire_actions else 0)
            ],
            "expiresTimeSpan": self.expires_time_span.to_dict() if self.expires_time_span else None,
            "expiresAt": self.expires_at,
        }


class GetGlobalMessageMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    global_message_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalMessageMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_global_message_name(self, global_message_name: str) -> GetGlobalMessageMasterRequest:
        self.global_message_name = global_message_name
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
    ) -> Optional[GetGlobalMessageMasterRequest]:
        if data is None:
            return None
        return GetGlobalMessageMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_global_message_name(data.get('globalMessageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "globalMessageName": self.global_message_name,
        }


class UpdateGlobalMessageMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    global_message_name: str = None
    metadata: str = None
    read_acquire_actions: List[AcquireAction] = None
    expires_time_span: TimeSpan = None
    expires_at: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGlobalMessageMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_global_message_name(self, global_message_name: str) -> UpdateGlobalMessageMasterRequest:
        self.global_message_name = global_message_name
        return self

    def with_metadata(self, metadata: str) -> UpdateGlobalMessageMasterRequest:
        self.metadata = metadata
        return self

    def with_read_acquire_actions(self, read_acquire_actions: List[AcquireAction]) -> UpdateGlobalMessageMasterRequest:
        self.read_acquire_actions = read_acquire_actions
        return self

    def with_expires_time_span(self, expires_time_span: TimeSpan) -> UpdateGlobalMessageMasterRequest:
        self.expires_time_span = expires_time_span
        return self

    def with_expires_at(self, expires_at: int) -> UpdateGlobalMessageMasterRequest:
        self.expires_at = expires_at
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
    ) -> Optional[UpdateGlobalMessageMasterRequest]:
        if data is None:
            return None
        return UpdateGlobalMessageMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_global_message_name(data.get('globalMessageName'))\
            .with_metadata(data.get('metadata'))\
            .with_read_acquire_actions([
                AcquireAction.from_dict(data.get('readAcquireActions')[i])
                for i in range(len(data.get('readAcquireActions')) if data.get('readAcquireActions') else 0)
            ])\
            .with_expires_time_span(TimeSpan.from_dict(data.get('expiresTimeSpan')))\
            .with_expires_at(data.get('expiresAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "globalMessageName": self.global_message_name,
            "metadata": self.metadata,
            "readAcquireActions": [
                self.read_acquire_actions[i].to_dict() if self.read_acquire_actions[i] else None
                for i in range(len(self.read_acquire_actions) if self.read_acquire_actions else 0)
            ],
            "expiresTimeSpan": self.expires_time_span.to_dict() if self.expires_time_span else None,
            "expiresAt": self.expires_at,
        }


class DeleteGlobalMessageMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    global_message_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGlobalMessageMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_global_message_name(self, global_message_name: str) -> DeleteGlobalMessageMasterRequest:
        self.global_message_name = global_message_name
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
    ) -> Optional[DeleteGlobalMessageMasterRequest]:
        if data is None:
            return None
        return DeleteGlobalMessageMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_global_message_name(data.get('globalMessageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "globalMessageName": self.global_message_name,
        }


class DescribeGlobalMessagesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalMessagesRequest:
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
    ) -> Optional[DescribeGlobalMessagesRequest]:
        if data is None:
            return None
        return DescribeGlobalMessagesRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetGlobalMessageRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    global_message_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalMessageRequest:
        self.namespace_name = namespace_name
        return self

    def with_global_message_name(self, global_message_name: str) -> GetGlobalMessageRequest:
        self.global_message_name = global_message_name
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
    ) -> Optional[GetGlobalMessageRequest]:
        if data is None:
            return None
        return GetGlobalMessageRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_global_message_name(data.get('globalMessageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "globalMessageName": self.global_message_name,
        }


class GetReceivedByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReceivedByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetReceivedByUserIdRequest:
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
    ) -> Optional[GetReceivedByUserIdRequest]:
        if data is None:
            return None
        return GetReceivedByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }


class UpdateReceivedByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    received_global_message_names: List[str] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateReceivedByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateReceivedByUserIdRequest:
        self.user_id = user_id
        return self

    def with_received_global_message_names(self, received_global_message_names: List[str]) -> UpdateReceivedByUserIdRequest:
        self.received_global_message_names = received_global_message_names
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateReceivedByUserIdRequest:
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
    ) -> Optional[UpdateReceivedByUserIdRequest]:
        if data is None:
            return None
        return UpdateReceivedByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_received_global_message_names([
                data.get('receivedGlobalMessageNames')[i]
                for i in range(len(data.get('receivedGlobalMessageNames')) if data.get('receivedGlobalMessageNames') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "receivedGlobalMessageNames": [
                self.received_global_message_names[i]
                for i in range(len(self.received_global_message_names) if self.received_global_message_names else 0)
            ],
        }


class DeleteReceivedByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteReceivedByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteReceivedByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteReceivedByUserIdRequest:
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
    ) -> Optional[DeleteReceivedByUserIdRequest]:
        if data is None:
            return None
        return DeleteReceivedByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }