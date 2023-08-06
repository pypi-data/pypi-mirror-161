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

from datastore.model import *


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
    log_setting: LogSetting = None
    done_upload_script: ScriptSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_done_upload_script(self, done_upload_script: ScriptSetting) -> CreateNamespaceRequest:
        self.done_upload_script = done_upload_script
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_done_upload_script(ScriptSetting.from_dict(data.get('doneUploadScript')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "doneUploadScript": self.done_upload_script.to_dict() if self.done_upload_script else None,
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
    log_setting: LogSetting = None
    done_upload_script: ScriptSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_done_upload_script(self, done_upload_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.done_upload_script = done_upload_script
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_done_upload_script(ScriptSetting.from_dict(data.get('doneUploadScript')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "doneUploadScript": self.done_upload_script.to_dict() if self.done_upload_script else None,
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


class DescribeDataObjectsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    status: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDataObjectsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeDataObjectsRequest:
        self.access_token = access_token
        return self

    def with_status(self, status: str) -> DescribeDataObjectsRequest:
        self.status = status
        return self

    def with_page_token(self, page_token: str) -> DescribeDataObjectsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDataObjectsRequest:
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
    ) -> Optional[DescribeDataObjectsRequest]:
        if data is None:
            return None
        return DescribeDataObjectsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_status(data.get('status'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "status": self.status,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeDataObjectsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    status: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDataObjectsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeDataObjectsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_status(self, status: str) -> DescribeDataObjectsByUserIdRequest:
        self.status = status
        return self

    def with_page_token(self, page_token: str) -> DescribeDataObjectsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDataObjectsByUserIdRequest:
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
    ) -> Optional[DescribeDataObjectsByUserIdRequest]:
        if data is None:
            return None
        return DescribeDataObjectsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_status(data.get('status'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "status": self.status,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class PrepareUploadRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    name: str = None
    content_type: str = None
    scope: str = None
    allow_user_ids: List[str] = None
    update_if_exists: bool = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareUploadRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> PrepareUploadRequest:
        self.access_token = access_token
        return self

    def with_name(self, name: str) -> PrepareUploadRequest:
        self.name = name
        return self

    def with_content_type(self, content_type: str) -> PrepareUploadRequest:
        self.content_type = content_type
        return self

    def with_scope(self, scope: str) -> PrepareUploadRequest:
        self.scope = scope
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> PrepareUploadRequest:
        self.allow_user_ids = allow_user_ids
        return self

    def with_update_if_exists(self, update_if_exists: bool) -> PrepareUploadRequest:
        self.update_if_exists = update_if_exists
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
    ) -> Optional[PrepareUploadRequest]:
        if data is None:
            return None
        return PrepareUploadRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_name(data.get('name'))\
            .with_content_type(data.get('contentType'))\
            .with_scope(data.get('scope'))\
            .with_allow_user_ids([
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')) if data.get('allowUserIds') else 0)
            ])\
            .with_update_if_exists(data.get('updateIfExists'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "name": self.name,
            "contentType": self.content_type,
            "scope": self.scope,
            "allowUserIds": [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids) if self.allow_user_ids else 0)
            ],
            "updateIfExists": self.update_if_exists,
        }


class PrepareUploadByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    name: str = None
    content_type: str = None
    scope: str = None
    allow_user_ids: List[str] = None
    update_if_exists: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareUploadByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> PrepareUploadByUserIdRequest:
        self.user_id = user_id
        return self

    def with_name(self, name: str) -> PrepareUploadByUserIdRequest:
        self.name = name
        return self

    def with_content_type(self, content_type: str) -> PrepareUploadByUserIdRequest:
        self.content_type = content_type
        return self

    def with_scope(self, scope: str) -> PrepareUploadByUserIdRequest:
        self.scope = scope
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> PrepareUploadByUserIdRequest:
        self.allow_user_ids = allow_user_ids
        return self

    def with_update_if_exists(self, update_if_exists: bool) -> PrepareUploadByUserIdRequest:
        self.update_if_exists = update_if_exists
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareUploadByUserIdRequest:
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
    ) -> Optional[PrepareUploadByUserIdRequest]:
        if data is None:
            return None
        return PrepareUploadByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_name(data.get('name'))\
            .with_content_type(data.get('contentType'))\
            .with_scope(data.get('scope'))\
            .with_allow_user_ids([
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')) if data.get('allowUserIds') else 0)
            ])\
            .with_update_if_exists(data.get('updateIfExists'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "name": self.name,
            "contentType": self.content_type,
            "scope": self.scope,
            "allowUserIds": [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids) if self.allow_user_ids else 0)
            ],
            "updateIfExists": self.update_if_exists,
        }


class UpdateDataObjectRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    data_object_name: str = None
    access_token: str = None
    scope: str = None
    allow_user_ids: List[str] = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateDataObjectRequest:
        self.namespace_name = namespace_name
        return self

    def with_data_object_name(self, data_object_name: str) -> UpdateDataObjectRequest:
        self.data_object_name = data_object_name
        return self

    def with_access_token(self, access_token: str) -> UpdateDataObjectRequest:
        self.access_token = access_token
        return self

    def with_scope(self, scope: str) -> UpdateDataObjectRequest:
        self.scope = scope
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> UpdateDataObjectRequest:
        self.allow_user_ids = allow_user_ids
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
    ) -> Optional[UpdateDataObjectRequest]:
        if data is None:
            return None
        return UpdateDataObjectRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_access_token(data.get('accessToken'))\
            .with_scope(data.get('scope'))\
            .with_allow_user_ids([
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')) if data.get('allowUserIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "dataObjectName": self.data_object_name,
            "accessToken": self.access_token,
            "scope": self.scope,
            "allowUserIds": [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids) if self.allow_user_ids else 0)
            ],
        }


class UpdateDataObjectByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    data_object_name: str = None
    user_id: str = None
    scope: str = None
    allow_user_ids: List[str] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateDataObjectByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_data_object_name(self, data_object_name: str) -> UpdateDataObjectByUserIdRequest:
        self.data_object_name = data_object_name
        return self

    def with_user_id(self, user_id: str) -> UpdateDataObjectByUserIdRequest:
        self.user_id = user_id
        return self

    def with_scope(self, scope: str) -> UpdateDataObjectByUserIdRequest:
        self.scope = scope
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> UpdateDataObjectByUserIdRequest:
        self.allow_user_ids = allow_user_ids
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateDataObjectByUserIdRequest:
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
    ) -> Optional[UpdateDataObjectByUserIdRequest]:
        if data is None:
            return None
        return UpdateDataObjectByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_user_id(data.get('userId'))\
            .with_scope(data.get('scope'))\
            .with_allow_user_ids([
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')) if data.get('allowUserIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "dataObjectName": self.data_object_name,
            "userId": self.user_id,
            "scope": self.scope,
            "allowUserIds": [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids) if self.allow_user_ids else 0)
            ],
        }


class PrepareReUploadRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    data_object_name: str = None
    access_token: str = None
    content_type: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareReUploadRequest:
        self.namespace_name = namespace_name
        return self

    def with_data_object_name(self, data_object_name: str) -> PrepareReUploadRequest:
        self.data_object_name = data_object_name
        return self

    def with_access_token(self, access_token: str) -> PrepareReUploadRequest:
        self.access_token = access_token
        return self

    def with_content_type(self, content_type: str) -> PrepareReUploadRequest:
        self.content_type = content_type
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
    ) -> Optional[PrepareReUploadRequest]:
        if data is None:
            return None
        return PrepareReUploadRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_access_token(data.get('accessToken'))\
            .with_content_type(data.get('contentType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "dataObjectName": self.data_object_name,
            "accessToken": self.access_token,
            "contentType": self.content_type,
        }


class PrepareReUploadByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    data_object_name: str = None
    user_id: str = None
    content_type: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareReUploadByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_data_object_name(self, data_object_name: str) -> PrepareReUploadByUserIdRequest:
        self.data_object_name = data_object_name
        return self

    def with_user_id(self, user_id: str) -> PrepareReUploadByUserIdRequest:
        self.user_id = user_id
        return self

    def with_content_type(self, content_type: str) -> PrepareReUploadByUserIdRequest:
        self.content_type = content_type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareReUploadByUserIdRequest:
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
    ) -> Optional[PrepareReUploadByUserIdRequest]:
        if data is None:
            return None
        return PrepareReUploadByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_user_id(data.get('userId'))\
            .with_content_type(data.get('contentType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "dataObjectName": self.data_object_name,
            "userId": self.user_id,
            "contentType": self.content_type,
        }


class DoneUploadRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    data_object_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DoneUploadRequest:
        self.namespace_name = namespace_name
        return self

    def with_data_object_name(self, data_object_name: str) -> DoneUploadRequest:
        self.data_object_name = data_object_name
        return self

    def with_access_token(self, access_token: str) -> DoneUploadRequest:
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
    ) -> Optional[DoneUploadRequest]:
        if data is None:
            return None
        return DoneUploadRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "dataObjectName": self.data_object_name,
            "accessToken": self.access_token,
        }


class DoneUploadByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    data_object_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DoneUploadByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_data_object_name(self, data_object_name: str) -> DoneUploadByUserIdRequest:
        self.data_object_name = data_object_name
        return self

    def with_user_id(self, user_id: str) -> DoneUploadByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DoneUploadByUserIdRequest:
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
    ) -> Optional[DoneUploadByUserIdRequest]:
        if data is None:
            return None
        return DoneUploadByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "dataObjectName": self.data_object_name,
            "userId": self.user_id,
        }


class DeleteDataObjectRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    data_object_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteDataObjectRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteDataObjectRequest:
        self.access_token = access_token
        return self

    def with_data_object_name(self, data_object_name: str) -> DeleteDataObjectRequest:
        self.data_object_name = data_object_name
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
    ) -> Optional[DeleteDataObjectRequest]:
        if data is None:
            return None
        return DeleteDataObjectRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_data_object_name(data.get('dataObjectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "dataObjectName": self.data_object_name,
        }


class DeleteDataObjectByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_object_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteDataObjectByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteDataObjectByUserIdRequest:
        self.user_id = user_id
        return self

    def with_data_object_name(self, data_object_name: str) -> DeleteDataObjectByUserIdRequest:
        self.data_object_name = data_object_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteDataObjectByUserIdRequest:
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
    ) -> Optional[DeleteDataObjectByUserIdRequest]:
        if data is None:
            return None
        return DeleteDataObjectByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_object_name(data.get('dataObjectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataObjectName": self.data_object_name,
        }


class PrepareDownloadRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    data_object_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> PrepareDownloadRequest:
        self.access_token = access_token
        return self

    def with_data_object_id(self, data_object_id: str) -> PrepareDownloadRequest:
        self.data_object_id = data_object_id
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
    ) -> Optional[PrepareDownloadRequest]:
        if data is None:
            return None
        return PrepareDownloadRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_data_object_id(data.get('dataObjectId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "dataObjectId": self.data_object_id,
        }


class PrepareDownloadByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_object_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> PrepareDownloadByUserIdRequest:
        self.user_id = user_id
        return self

    def with_data_object_id(self, data_object_id: str) -> PrepareDownloadByUserIdRequest:
        self.data_object_id = data_object_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareDownloadByUserIdRequest:
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
    ) -> Optional[PrepareDownloadByUserIdRequest]:
        if data is None:
            return None
        return PrepareDownloadByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_object_id(data.get('dataObjectId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataObjectId": self.data_object_id,
        }


class PrepareDownloadByGenerationRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    data_object_id: str = None
    generation: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadByGenerationRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> PrepareDownloadByGenerationRequest:
        self.access_token = access_token
        return self

    def with_data_object_id(self, data_object_id: str) -> PrepareDownloadByGenerationRequest:
        self.data_object_id = data_object_id
        return self

    def with_generation(self, generation: str) -> PrepareDownloadByGenerationRequest:
        self.generation = generation
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
    ) -> Optional[PrepareDownloadByGenerationRequest]:
        if data is None:
            return None
        return PrepareDownloadByGenerationRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_data_object_id(data.get('dataObjectId'))\
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "dataObjectId": self.data_object_id,
            "generation": self.generation,
        }


class PrepareDownloadByGenerationAndUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_object_id: str = None
    generation: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadByGenerationAndUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> PrepareDownloadByGenerationAndUserIdRequest:
        self.user_id = user_id
        return self

    def with_data_object_id(self, data_object_id: str) -> PrepareDownloadByGenerationAndUserIdRequest:
        self.data_object_id = data_object_id
        return self

    def with_generation(self, generation: str) -> PrepareDownloadByGenerationAndUserIdRequest:
        self.generation = generation
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareDownloadByGenerationAndUserIdRequest:
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
    ) -> Optional[PrepareDownloadByGenerationAndUserIdRequest]:
        if data is None:
            return None
        return PrepareDownloadByGenerationAndUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_object_id(data.get('dataObjectId'))\
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataObjectId": self.data_object_id,
            "generation": self.generation,
        }


class PrepareDownloadOwnDataRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    data_object_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadOwnDataRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> PrepareDownloadOwnDataRequest:
        self.access_token = access_token
        return self

    def with_data_object_name(self, data_object_name: str) -> PrepareDownloadOwnDataRequest:
        self.data_object_name = data_object_name
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
    ) -> Optional[PrepareDownloadOwnDataRequest]:
        if data is None:
            return None
        return PrepareDownloadOwnDataRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_data_object_name(data.get('dataObjectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "dataObjectName": self.data_object_name,
        }


class PrepareDownloadByUserIdAndDataObjectNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_object_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadByUserIdAndDataObjectNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> PrepareDownloadByUserIdAndDataObjectNameRequest:
        self.user_id = user_id
        return self

    def with_data_object_name(self, data_object_name: str) -> PrepareDownloadByUserIdAndDataObjectNameRequest:
        self.data_object_name = data_object_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareDownloadByUserIdAndDataObjectNameRequest:
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
    ) -> Optional[PrepareDownloadByUserIdAndDataObjectNameRequest]:
        if data is None:
            return None
        return PrepareDownloadByUserIdAndDataObjectNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_object_name(data.get('dataObjectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataObjectName": self.data_object_name,
        }


class PrepareDownloadOwnDataByGenerationRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    data_object_name: str = None
    generation: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadOwnDataByGenerationRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> PrepareDownloadOwnDataByGenerationRequest:
        self.access_token = access_token
        return self

    def with_data_object_name(self, data_object_name: str) -> PrepareDownloadOwnDataByGenerationRequest:
        self.data_object_name = data_object_name
        return self

    def with_generation(self, generation: str) -> PrepareDownloadOwnDataByGenerationRequest:
        self.generation = generation
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
    ) -> Optional[PrepareDownloadOwnDataByGenerationRequest]:
        if data is None:
            return None
        return PrepareDownloadOwnDataByGenerationRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "dataObjectName": self.data_object_name,
            "generation": self.generation,
        }


class PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_object_name: str = None
    generation: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest:
        self.user_id = user_id
        return self

    def with_data_object_name(self, data_object_name: str) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest:
        self.data_object_name = data_object_name
        return self

    def with_generation(self, generation: str) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest:
        self.generation = generation
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest:
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
    ) -> Optional[PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest]:
        if data is None:
            return None
        return PrepareDownloadByUserIdAndDataObjectNameAndGenerationRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataObjectName": self.data_object_name,
            "generation": self.generation,
        }


class RestoreDataObjectRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    data_object_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RestoreDataObjectRequest:
        self.namespace_name = namespace_name
        return self

    def with_data_object_id(self, data_object_id: str) -> RestoreDataObjectRequest:
        self.data_object_id = data_object_id
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
    ) -> Optional[RestoreDataObjectRequest]:
        if data is None:
            return None
        return RestoreDataObjectRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_data_object_id(data.get('dataObjectId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "dataObjectId": self.data_object_id,
        }


class DescribeDataObjectHistoriesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    data_object_name: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDataObjectHistoriesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeDataObjectHistoriesRequest:
        self.access_token = access_token
        return self

    def with_data_object_name(self, data_object_name: str) -> DescribeDataObjectHistoriesRequest:
        self.data_object_name = data_object_name
        return self

    def with_page_token(self, page_token: str) -> DescribeDataObjectHistoriesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDataObjectHistoriesRequest:
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
    ) -> Optional[DescribeDataObjectHistoriesRequest]:
        if data is None:
            return None
        return DescribeDataObjectHistoriesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "dataObjectName": self.data_object_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeDataObjectHistoriesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_object_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDataObjectHistoriesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeDataObjectHistoriesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_data_object_name(self, data_object_name: str) -> DescribeDataObjectHistoriesByUserIdRequest:
        self.data_object_name = data_object_name
        return self

    def with_page_token(self, page_token: str) -> DescribeDataObjectHistoriesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDataObjectHistoriesByUserIdRequest:
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
    ) -> Optional[DescribeDataObjectHistoriesByUserIdRequest]:
        if data is None:
            return None
        return DescribeDataObjectHistoriesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataObjectName": self.data_object_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetDataObjectHistoryRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    data_object_name: str = None
    generation: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDataObjectHistoryRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetDataObjectHistoryRequest:
        self.access_token = access_token
        return self

    def with_data_object_name(self, data_object_name: str) -> GetDataObjectHistoryRequest:
        self.data_object_name = data_object_name
        return self

    def with_generation(self, generation: str) -> GetDataObjectHistoryRequest:
        self.generation = generation
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
    ) -> Optional[GetDataObjectHistoryRequest]:
        if data is None:
            return None
        return GetDataObjectHistoryRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "dataObjectName": self.data_object_name,
            "generation": self.generation,
        }


class GetDataObjectHistoryByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_object_name: str = None
    generation: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDataObjectHistoryByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetDataObjectHistoryByUserIdRequest:
        self.user_id = user_id
        return self

    def with_data_object_name(self, data_object_name: str) -> GetDataObjectHistoryByUserIdRequest:
        self.data_object_name = data_object_name
        return self

    def with_generation(self, generation: str) -> GetDataObjectHistoryByUserIdRequest:
        self.generation = generation
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
    ) -> Optional[GetDataObjectHistoryByUserIdRequest]:
        if data is None:
            return None
        return GetDataObjectHistoryByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataObjectName": self.data_object_name,
            "generation": self.generation,
        }