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

from version.model import *


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
    assume_user_id: str = None
    accept_version_script: ScriptSetting = None
    check_version_trigger_script_id: str = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_assume_user_id(self, assume_user_id: str) -> CreateNamespaceRequest:
        self.assume_user_id = assume_user_id
        return self

    def with_accept_version_script(self, accept_version_script: ScriptSetting) -> CreateNamespaceRequest:
        self.accept_version_script = accept_version_script
        return self

    def with_check_version_trigger_script_id(self, check_version_trigger_script_id: str) -> CreateNamespaceRequest:
        self.check_version_trigger_script_id = check_version_trigger_script_id
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
            .with_assume_user_id(data.get('assumeUserId'))\
            .with_accept_version_script(ScriptSetting.from_dict(data.get('acceptVersionScript')))\
            .with_check_version_trigger_script_id(data.get('checkVersionTriggerScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "acceptVersionScript": self.accept_version_script.to_dict() if self.accept_version_script else None,
            "checkVersionTriggerScriptId": self.check_version_trigger_script_id,
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
    assume_user_id: str = None
    accept_version_script: ScriptSetting = None
    check_version_trigger_script_id: str = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_assume_user_id(self, assume_user_id: str) -> UpdateNamespaceRequest:
        self.assume_user_id = assume_user_id
        return self

    def with_accept_version_script(self, accept_version_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.accept_version_script = accept_version_script
        return self

    def with_check_version_trigger_script_id(self, check_version_trigger_script_id: str) -> UpdateNamespaceRequest:
        self.check_version_trigger_script_id = check_version_trigger_script_id
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
            .with_assume_user_id(data.get('assumeUserId'))\
            .with_accept_version_script(ScriptSetting.from_dict(data.get('acceptVersionScript')))\
            .with_check_version_trigger_script_id(data.get('checkVersionTriggerScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "acceptVersionScript": self.accept_version_script.to_dict() if self.accept_version_script else None,
            "checkVersionTriggerScriptId": self.check_version_trigger_script_id,
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


class DescribeVersionModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeVersionModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeVersionModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeVersionModelMastersRequest:
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
    ) -> Optional[DescribeVersionModelMastersRequest]:
        if data is None:
            return None
        return DescribeVersionModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateVersionModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    warning_version: Version = None
    error_version: Version = None
    scope: str = None
    current_version: Version = None
    need_signature: bool = None
    signature_key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateVersionModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateVersionModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateVersionModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateVersionModelMasterRequest:
        self.metadata = metadata
        return self

    def with_warning_version(self, warning_version: Version) -> CreateVersionModelMasterRequest:
        self.warning_version = warning_version
        return self

    def with_error_version(self, error_version: Version) -> CreateVersionModelMasterRequest:
        self.error_version = error_version
        return self

    def with_scope(self, scope: str) -> CreateVersionModelMasterRequest:
        self.scope = scope
        return self

    def with_current_version(self, current_version: Version) -> CreateVersionModelMasterRequest:
        self.current_version = current_version
        return self

    def with_need_signature(self, need_signature: bool) -> CreateVersionModelMasterRequest:
        self.need_signature = need_signature
        return self

    def with_signature_key_id(self, signature_key_id: str) -> CreateVersionModelMasterRequest:
        self.signature_key_id = signature_key_id
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
    ) -> Optional[CreateVersionModelMasterRequest]:
        if data is None:
            return None
        return CreateVersionModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_warning_version(Version.from_dict(data.get('warningVersion')))\
            .with_error_version(Version.from_dict(data.get('errorVersion')))\
            .with_scope(data.get('scope'))\
            .with_current_version(Version.from_dict(data.get('currentVersion')))\
            .with_need_signature(data.get('needSignature'))\
            .with_signature_key_id(data.get('signatureKeyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "warningVersion": self.warning_version.to_dict() if self.warning_version else None,
            "errorVersion": self.error_version.to_dict() if self.error_version else None,
            "scope": self.scope,
            "currentVersion": self.current_version.to_dict() if self.current_version else None,
            "needSignature": self.need_signature,
            "signatureKeyId": self.signature_key_id,
        }


class GetVersionModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    version_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetVersionModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> GetVersionModelMasterRequest:
        self.version_name = version_name
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
    ) -> Optional[GetVersionModelMasterRequest]:
        if data is None:
            return None
        return GetVersionModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
        }


class UpdateVersionModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    version_name: str = None
    description: str = None
    metadata: str = None
    warning_version: Version = None
    error_version: Version = None
    scope: str = None
    current_version: Version = None
    need_signature: bool = None
    signature_key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateVersionModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> UpdateVersionModelMasterRequest:
        self.version_name = version_name
        return self

    def with_description(self, description: str) -> UpdateVersionModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateVersionModelMasterRequest:
        self.metadata = metadata
        return self

    def with_warning_version(self, warning_version: Version) -> UpdateVersionModelMasterRequest:
        self.warning_version = warning_version
        return self

    def with_error_version(self, error_version: Version) -> UpdateVersionModelMasterRequest:
        self.error_version = error_version
        return self

    def with_scope(self, scope: str) -> UpdateVersionModelMasterRequest:
        self.scope = scope
        return self

    def with_current_version(self, current_version: Version) -> UpdateVersionModelMasterRequest:
        self.current_version = current_version
        return self

    def with_need_signature(self, need_signature: bool) -> UpdateVersionModelMasterRequest:
        self.need_signature = need_signature
        return self

    def with_signature_key_id(self, signature_key_id: str) -> UpdateVersionModelMasterRequest:
        self.signature_key_id = signature_key_id
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
    ) -> Optional[UpdateVersionModelMasterRequest]:
        if data is None:
            return None
        return UpdateVersionModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_warning_version(Version.from_dict(data.get('warningVersion')))\
            .with_error_version(Version.from_dict(data.get('errorVersion')))\
            .with_scope(data.get('scope'))\
            .with_current_version(Version.from_dict(data.get('currentVersion')))\
            .with_need_signature(data.get('needSignature'))\
            .with_signature_key_id(data.get('signatureKeyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
            "description": self.description,
            "metadata": self.metadata,
            "warningVersion": self.warning_version.to_dict() if self.warning_version else None,
            "errorVersion": self.error_version.to_dict() if self.error_version else None,
            "scope": self.scope,
            "currentVersion": self.current_version.to_dict() if self.current_version else None,
            "needSignature": self.need_signature,
            "signatureKeyId": self.signature_key_id,
        }


class DeleteVersionModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    version_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteVersionModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> DeleteVersionModelMasterRequest:
        self.version_name = version_name
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
    ) -> Optional[DeleteVersionModelMasterRequest]:
        if data is None:
            return None
        return DeleteVersionModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
        }


class DescribeVersionModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeVersionModelsRequest:
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
    ) -> Optional[DescribeVersionModelsRequest]:
        if data is None:
            return None
        return DescribeVersionModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetVersionModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    version_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetVersionModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> GetVersionModelRequest:
        self.version_name = version_name
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
    ) -> Optional[GetVersionModelRequest]:
        if data is None:
            return None
        return GetVersionModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
        }


class DescribeAcceptVersionsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAcceptVersionsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeAcceptVersionsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeAcceptVersionsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeAcceptVersionsRequest:
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
    ) -> Optional[DescribeAcceptVersionsRequest]:
        if data is None:
            return None
        return DescribeAcceptVersionsRequest()\
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


class DescribeAcceptVersionsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAcceptVersionsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeAcceptVersionsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeAcceptVersionsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeAcceptVersionsByUserIdRequest:
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
    ) -> Optional[DescribeAcceptVersionsByUserIdRequest]:
        if data is None:
            return None
        return DescribeAcceptVersionsByUserIdRequest()\
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


class AcceptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    version_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> AcceptRequest:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> AcceptRequest:
        self.version_name = version_name
        return self

    def with_access_token(self, access_token: str) -> AcceptRequest:
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
    ) -> Optional[AcceptRequest]:
        if data is None:
            return None
        return AcceptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
            "accessToken": self.access_token,
        }


class AcceptByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    version_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcceptByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> AcceptByUserIdRequest:
        self.version_name = version_name
        return self

    def with_user_id(self, user_id: str) -> AcceptByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcceptByUserIdRequest:
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
    ) -> Optional[AcceptByUserIdRequest]:
        if data is None:
            return None
        return AcceptByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
            "userId": self.user_id,
        }


class GetAcceptVersionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    version_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAcceptVersionRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetAcceptVersionRequest:
        self.access_token = access_token
        return self

    def with_version_name(self, version_name: str) -> GetAcceptVersionRequest:
        self.version_name = version_name
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
    ) -> Optional[GetAcceptVersionRequest]:
        if data is None:
            return None
        return GetAcceptVersionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_version_name(data.get('versionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "versionName": self.version_name,
        }


class GetAcceptVersionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    version_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAcceptVersionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetAcceptVersionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_version_name(self, version_name: str) -> GetAcceptVersionByUserIdRequest:
        self.version_name = version_name
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
    ) -> Optional[GetAcceptVersionByUserIdRequest]:
        if data is None:
            return None
        return GetAcceptVersionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_version_name(data.get('versionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "versionName": self.version_name,
        }


class DeleteAcceptVersionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    version_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteAcceptVersionRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteAcceptVersionRequest:
        self.access_token = access_token
        return self

    def with_version_name(self, version_name: str) -> DeleteAcceptVersionRequest:
        self.version_name = version_name
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
    ) -> Optional[DeleteAcceptVersionRequest]:
        if data is None:
            return None
        return DeleteAcceptVersionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_version_name(data.get('versionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "versionName": self.version_name,
        }


class DeleteAcceptVersionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    version_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteAcceptVersionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteAcceptVersionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_version_name(self, version_name: str) -> DeleteAcceptVersionByUserIdRequest:
        self.version_name = version_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteAcceptVersionByUserIdRequest:
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
    ) -> Optional[DeleteAcceptVersionByUserIdRequest]:
        if data is None:
            return None
        return DeleteAcceptVersionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_version_name(data.get('versionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "versionName": self.version_name,
        }


class CheckVersionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_versions: List[TargetVersion] = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CheckVersionRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CheckVersionRequest:
        self.access_token = access_token
        return self

    def with_target_versions(self, target_versions: List[TargetVersion]) -> CheckVersionRequest:
        self.target_versions = target_versions
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
    ) -> Optional[CheckVersionRequest]:
        if data is None:
            return None
        return CheckVersionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_versions([
                TargetVersion.from_dict(data.get('targetVersions')[i])
                for i in range(len(data.get('targetVersions')) if data.get('targetVersions') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetVersions": [
                self.target_versions[i].to_dict() if self.target_versions[i] else None
                for i in range(len(self.target_versions) if self.target_versions else 0)
            ],
        }


class CheckVersionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_versions: List[TargetVersion] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CheckVersionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CheckVersionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_versions(self, target_versions: List[TargetVersion]) -> CheckVersionByUserIdRequest:
        self.target_versions = target_versions
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CheckVersionByUserIdRequest:
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
    ) -> Optional[CheckVersionByUserIdRequest]:
        if data is None:
            return None
        return CheckVersionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_versions([
                TargetVersion.from_dict(data.get('targetVersions')[i])
                for i in range(len(data.get('targetVersions')) if data.get('targetVersions') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetVersions": [
                self.target_versions[i].to_dict() if self.target_versions[i] else None
                for i in range(len(self.target_versions) if self.target_versions else 0)
            ],
        }


class CalculateSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    version_name: str = None
    version: Version = None

    def with_namespace_name(self, namespace_name: str) -> CalculateSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> CalculateSignatureRequest:
        self.version_name = version_name
        return self

    def with_version(self, version: Version) -> CalculateSignatureRequest:
        self.version = version
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
    ) -> Optional[CalculateSignatureRequest]:
        if data is None:
            return None
        return CalculateSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))\
            .with_version(Version.from_dict(data.get('version')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
            "version": self.version.to_dict() if self.version else None,
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


class GetCurrentVersionMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentVersionMasterRequest:
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
    ) -> Optional[GetCurrentVersionMasterRequest]:
        if data is None:
            return None
        return GetCurrentVersionMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentVersionMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentVersionMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentVersionMasterRequest:
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
    ) -> Optional[UpdateCurrentVersionMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentVersionMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentVersionMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentVersionMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentVersionMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentVersionMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentVersionMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }