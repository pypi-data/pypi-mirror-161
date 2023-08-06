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

from account.model import *


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
    change_password_if_take_over: bool = None
    different_user_id_for_login_and_data_retention: bool = None
    create_account_script: ScriptSetting = None
    authentication_script: ScriptSetting = None
    create_take_over_script: ScriptSetting = None
    do_take_over_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_change_password_if_take_over(self, change_password_if_take_over: bool) -> CreateNamespaceRequest:
        self.change_password_if_take_over = change_password_if_take_over
        return self

    def with_different_user_id_for_login_and_data_retention(self, different_user_id_for_login_and_data_retention: bool) -> CreateNamespaceRequest:
        self.different_user_id_for_login_and_data_retention = different_user_id_for_login_and_data_retention
        return self

    def with_create_account_script(self, create_account_script: ScriptSetting) -> CreateNamespaceRequest:
        self.create_account_script = create_account_script
        return self

    def with_authentication_script(self, authentication_script: ScriptSetting) -> CreateNamespaceRequest:
        self.authentication_script = authentication_script
        return self

    def with_create_take_over_script(self, create_take_over_script: ScriptSetting) -> CreateNamespaceRequest:
        self.create_take_over_script = create_take_over_script
        return self

    def with_do_take_over_script(self, do_take_over_script: ScriptSetting) -> CreateNamespaceRequest:
        self.do_take_over_script = do_take_over_script
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
            .with_change_password_if_take_over(data.get('changePasswordIfTakeOver'))\
            .with_different_user_id_for_login_and_data_retention(data.get('differentUserIdForLoginAndDataRetention'))\
            .with_create_account_script(ScriptSetting.from_dict(data.get('createAccountScript')))\
            .with_authentication_script(ScriptSetting.from_dict(data.get('authenticationScript')))\
            .with_create_take_over_script(ScriptSetting.from_dict(data.get('createTakeOverScript')))\
            .with_do_take_over_script(ScriptSetting.from_dict(data.get('doTakeOverScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "changePasswordIfTakeOver": self.change_password_if_take_over,
            "differentUserIdForLoginAndDataRetention": self.different_user_id_for_login_and_data_retention,
            "createAccountScript": self.create_account_script.to_dict() if self.create_account_script else None,
            "authenticationScript": self.authentication_script.to_dict() if self.authentication_script else None,
            "createTakeOverScript": self.create_take_over_script.to_dict() if self.create_take_over_script else None,
            "doTakeOverScript": self.do_take_over_script.to_dict() if self.do_take_over_script else None,
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
    change_password_if_take_over: bool = None
    different_user_id_for_login_and_data_retention: bool = None
    create_account_script: ScriptSetting = None
    authentication_script: ScriptSetting = None
    create_take_over_script: ScriptSetting = None
    do_take_over_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_change_password_if_take_over(self, change_password_if_take_over: bool) -> UpdateNamespaceRequest:
        self.change_password_if_take_over = change_password_if_take_over
        return self

    def with_different_user_id_for_login_and_data_retention(self, different_user_id_for_login_and_data_retention: bool) -> UpdateNamespaceRequest:
        self.different_user_id_for_login_and_data_retention = different_user_id_for_login_and_data_retention
        return self

    def with_create_account_script(self, create_account_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.create_account_script = create_account_script
        return self

    def with_authentication_script(self, authentication_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.authentication_script = authentication_script
        return self

    def with_create_take_over_script(self, create_take_over_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.create_take_over_script = create_take_over_script
        return self

    def with_do_take_over_script(self, do_take_over_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.do_take_over_script = do_take_over_script
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
            .with_change_password_if_take_over(data.get('changePasswordIfTakeOver'))\
            .with_different_user_id_for_login_and_data_retention(data.get('differentUserIdForLoginAndDataRetention'))\
            .with_create_account_script(ScriptSetting.from_dict(data.get('createAccountScript')))\
            .with_authentication_script(ScriptSetting.from_dict(data.get('authenticationScript')))\
            .with_create_take_over_script(ScriptSetting.from_dict(data.get('createTakeOverScript')))\
            .with_do_take_over_script(ScriptSetting.from_dict(data.get('doTakeOverScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "changePasswordIfTakeOver": self.change_password_if_take_over,
            "differentUserIdForLoginAndDataRetention": self.different_user_id_for_login_and_data_retention,
            "createAccountScript": self.create_account_script.to_dict() if self.create_account_script else None,
            "authenticationScript": self.authentication_script.to_dict() if self.authentication_script else None,
            "createTakeOverScript": self.create_take_over_script.to_dict() if self.create_take_over_script else None,
            "doTakeOverScript": self.do_take_over_script.to_dict() if self.do_take_over_script else None,
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


class DescribeAccountsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAccountsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeAccountsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeAccountsRequest:
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
    ) -> Optional[DescribeAccountsRequest]:
        if data is None:
            return None
        return DescribeAccountsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateAccountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateAccountRequest:
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
    ) -> Optional[CreateAccountRequest]:
        if data is None:
            return None
        return CreateAccountRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateTimeOffsetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateTimeOffsetRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateTimeOffsetRequest:
        self.user_id = user_id
        return self

    def with_time_offset(self, time_offset: int) -> UpdateTimeOffsetRequest:
        self.time_offset = time_offset
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateTimeOffsetRequest:
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
    ) -> Optional[UpdateTimeOffsetRequest]:
        if data is None:
            return None
        return UpdateTimeOffsetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset(data.get('timeOffset'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffset": self.time_offset,
        }


class UpdateBannedRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    banned: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateBannedRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateBannedRequest:
        self.user_id = user_id
        return self

    def with_banned(self, banned: bool) -> UpdateBannedRequest:
        self.banned = banned
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateBannedRequest:
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
    ) -> Optional[UpdateBannedRequest]:
        if data is None:
            return None
        return UpdateBannedRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_banned(data.get('banned'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "banned": self.banned,
        }


class GetAccountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAccountRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetAccountRequest:
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
    ) -> Optional[GetAccountRequest]:
        if data is None:
            return None
        return GetAccountRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }


class DeleteAccountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteAccountRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteAccountRequest:
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
    ) -> Optional[DeleteAccountRequest]:
        if data is None:
            return None
        return DeleteAccountRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }


class AuthenticationRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    key_id: str = None
    password: str = None

    def with_namespace_name(self, namespace_name: str) -> AuthenticationRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AuthenticationRequest:
        self.user_id = user_id
        return self

    def with_key_id(self, key_id: str) -> AuthenticationRequest:
        self.key_id = key_id
        return self

    def with_password(self, password: str) -> AuthenticationRequest:
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
    ) -> Optional[AuthenticationRequest]:
        if data is None:
            return None
        return AuthenticationRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_key_id(data.get('keyId'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "keyId": self.key_id,
            "password": self.password,
        }


class DescribeTakeOversRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTakeOversRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeTakeOversRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeTakeOversRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeTakeOversRequest:
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
    ) -> Optional[DescribeTakeOversRequest]:
        if data is None:
            return None
        return DescribeTakeOversRequest()\
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


class DescribeTakeOversByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTakeOversByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeTakeOversByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeTakeOversByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeTakeOversByUserIdRequest:
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
    ) -> Optional[DescribeTakeOversByUserIdRequest]:
        if data is None:
            return None
        return DescribeTakeOversByUserIdRequest()\
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


class CreateTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    user_identifier: str = None
    password: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreateTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> CreateTakeOverRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> CreateTakeOverRequest:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> CreateTakeOverRequest:
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
    ) -> Optional[CreateTakeOverRequest]:
        if data is None:
            return None
        return CreateTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
        }


class CreateTakeOverByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    user_identifier: str = None
    password: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateTakeOverByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateTakeOverByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> CreateTakeOverByUserIdRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> CreateTakeOverByUserIdRequest:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> CreateTakeOverByUserIdRequest:
        self.password = password
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateTakeOverByUserIdRequest:
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
    ) -> Optional[CreateTakeOverByUserIdRequest]:
        if data is None:
            return None
        return CreateTakeOverByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
        }


class GetTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> GetTakeOverRequest:
        self.type = type
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
    ) -> Optional[GetTakeOverRequest]:
        if data is None:
            return None
        return GetTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
        }


class GetTakeOverByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None

    def with_namespace_name(self, namespace_name: str) -> GetTakeOverByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetTakeOverByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> GetTakeOverByUserIdRequest:
        self.type = type
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
    ) -> Optional[GetTakeOverByUserIdRequest]:
        if data is None:
            return None
        return GetTakeOverByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
        }


class UpdateTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    old_password: str = None
    password: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> UpdateTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> UpdateTakeOverRequest:
        self.type = type
        return self

    def with_old_password(self, old_password: str) -> UpdateTakeOverRequest:
        self.old_password = old_password
        return self

    def with_password(self, password: str) -> UpdateTakeOverRequest:
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
    ) -> Optional[UpdateTakeOverRequest]:
        if data is None:
            return None
        return UpdateTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_old_password(data.get('oldPassword'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "oldPassword": self.old_password,
            "password": self.password,
        }


class UpdateTakeOverByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    old_password: str = None
    password: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateTakeOverByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateTakeOverByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> UpdateTakeOverByUserIdRequest:
        self.type = type
        return self

    def with_old_password(self, old_password: str) -> UpdateTakeOverByUserIdRequest:
        self.old_password = old_password
        return self

    def with_password(self, password: str) -> UpdateTakeOverByUserIdRequest:
        self.password = password
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateTakeOverByUserIdRequest:
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
    ) -> Optional[UpdateTakeOverByUserIdRequest]:
        if data is None:
            return None
        return UpdateTakeOverByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_old_password(data.get('oldPassword'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "oldPassword": self.old_password,
            "password": self.password,
        }


class DeleteTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    user_identifier: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> DeleteTakeOverRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> DeleteTakeOverRequest:
        self.user_identifier = user_identifier
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
    ) -> Optional[DeleteTakeOverRequest]:
        if data is None:
            return None
        return DeleteTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "userIdentifier": self.user_identifier,
        }


class DeleteTakeOverByUserIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    user_identifier: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTakeOverByUserIdentifierRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> DeleteTakeOverByUserIdentifierRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> DeleteTakeOverByUserIdentifierRequest:
        self.user_identifier = user_identifier
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteTakeOverByUserIdentifierRequest:
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
    ) -> Optional[DeleteTakeOverByUserIdentifierRequest]:
        if data is None:
            return None
        return DeleteTakeOverByUserIdentifierRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "userIdentifier": self.user_identifier,
        }


class DoTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    user_identifier: str = None
    password: str = None

    def with_namespace_name(self, namespace_name: str) -> DoTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> DoTakeOverRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> DoTakeOverRequest:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> DoTakeOverRequest:
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
    ) -> Optional[DoTakeOverRequest]:
        if data is None:
            return None
        return DoTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
        }


class GetDataOwnerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDataOwnerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetDataOwnerByUserIdRequest:
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
    ) -> Optional[GetDataOwnerByUserIdRequest]:
        if data is None:
            return None
        return GetDataOwnerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }


class DeleteDataOwnerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteDataOwnerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteDataOwnerByUserIdRequest:
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
    ) -> Optional[DeleteDataOwnerByUserIdRequest]:
        if data is None:
            return None
        return DeleteDataOwnerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }