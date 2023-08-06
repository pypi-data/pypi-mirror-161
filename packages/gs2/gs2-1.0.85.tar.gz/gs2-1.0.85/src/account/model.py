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

import re
from typing import *
import core


class LogSetting(core.Gs2Model):
    logging_namespace_id: str = None

    def with_logging_namespace_id(self, logging_namespace_id: str) -> LogSetting:
        self.logging_namespace_id = logging_namespace_id
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
    ) -> Optional[LogSetting]:
        if data is None:
            return None
        return LogSetting()\
            .with_logging_namespace_id(data.get('loggingNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loggingNamespaceId": self.logging_namespace_id,
        }


class ScriptSetting(core.Gs2Model):
    trigger_script_id: str = None
    done_trigger_target_type: str = None
    done_trigger_script_id: str = None
    done_trigger_queue_namespace_id: str = None

    def with_trigger_script_id(self, trigger_script_id: str) -> ScriptSetting:
        self.trigger_script_id = trigger_script_id
        return self

    def with_done_trigger_target_type(self, done_trigger_target_type: str) -> ScriptSetting:
        self.done_trigger_target_type = done_trigger_target_type
        return self

    def with_done_trigger_script_id(self, done_trigger_script_id: str) -> ScriptSetting:
        self.done_trigger_script_id = done_trigger_script_id
        return self

    def with_done_trigger_queue_namespace_id(self, done_trigger_queue_namespace_id: str) -> ScriptSetting:
        self.done_trigger_queue_namespace_id = done_trigger_queue_namespace_id
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
    ) -> Optional[ScriptSetting]:
        if data is None:
            return None
        return ScriptSetting()\
            .with_trigger_script_id(data.get('triggerScriptId'))\
            .with_done_trigger_target_type(data.get('doneTriggerTargetType'))\
            .with_done_trigger_script_id(data.get('doneTriggerScriptId'))\
            .with_done_trigger_queue_namespace_id(data.get('doneTriggerQueueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggerScriptId": self.trigger_script_id,
            "doneTriggerTargetType": self.done_trigger_target_type,
            "doneTriggerScriptId": self.done_trigger_script_id,
            "doneTriggerQueueNamespaceId": self.done_trigger_queue_namespace_id,
        }


class DataOwner(core.Gs2Model):
    data_owner_id: str = None
    user_id: str = None
    name: str = None
    created_at: int = None

    def with_data_owner_id(self, data_owner_id: str) -> DataOwner:
        self.data_owner_id = data_owner_id
        return self

    def with_user_id(self, user_id: str) -> DataOwner:
        self.user_id = user_id
        return self

    def with_name(self, name: str) -> DataOwner:
        self.name = name
        return self

    def with_created_at(self, created_at: int) -> DataOwner:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        data_owner_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:account:{userId}:dataOwner:{dataOwnerName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            dataOwnerName=data_owner_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_data_owner_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('data_owner_name')

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
    ) -> Optional[DataOwner]:
        if data is None:
            return None
        return DataOwner()\
            .with_data_owner_id(data.get('dataOwnerId'))\
            .with_user_id(data.get('userId'))\
            .with_name(data.get('name'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataOwnerId": self.data_owner_id,
            "userId": self.user_id,
            "name": self.name,
            "createdAt": self.created_at,
        }


class TakeOver(core.Gs2Model):
    take_over_id: str = None
    user_id: str = None
    type: int = None
    user_identifier: str = None
    password: str = None
    created_at: int = None

    def with_take_over_id(self, take_over_id: str) -> TakeOver:
        self.take_over_id = take_over_id
        return self

    def with_user_id(self, user_id: str) -> TakeOver:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> TakeOver:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> TakeOver:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> TakeOver:
        self.password = password
        return self

    def with_created_at(self, created_at: int) -> TakeOver:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        _type,
        user_identifier,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:takeOver:{type}:{userIdentifier}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            Type=_type,
            userIdentifier=user_identifier,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get__type_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('_type')

    @classmethod
    def get_user_identifier_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('user_identifier')

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
    ) -> Optional[TakeOver]:
        if data is None:
            return None
        return TakeOver()\
            .with_take_over_id(data.get('takeOverId'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "takeOverId": self.take_over_id,
            "userId": self.user_id,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
            "createdAt": self.created_at,
        }


class Account(core.Gs2Model):
    account_id: str = None
    user_id: str = None
    password: str = None
    time_offset: int = None
    banned: bool = None
    created_at: int = None

    def with_account_id(self, account_id: str) -> Account:
        self.account_id = account_id
        return self

    def with_user_id(self, user_id: str) -> Account:
        self.user_id = user_id
        return self

    def with_password(self, password: str) -> Account:
        self.password = password
        return self

    def with_time_offset(self, time_offset: int) -> Account:
        self.time_offset = time_offset
        return self

    def with_banned(self, banned: bool) -> Account:
        self.banned = banned
        return self

    def with_created_at(self, created_at: int) -> Account:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:account:{userId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

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
    ) -> Optional[Account]:
        if data is None:
            return None
        return Account()\
            .with_account_id(data.get('accountId'))\
            .with_user_id(data.get('userId'))\
            .with_password(data.get('password'))\
            .with_time_offset(data.get('timeOffset'))\
            .with_banned(data.get('banned'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountId": self.account_id,
            "userId": self.user_id,
            "password": self.password,
            "timeOffset": self.time_offset,
            "banned": self.banned,
            "createdAt": self.created_at,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    change_password_if_take_over: bool = None
    different_user_id_for_login_and_data_retention: bool = None
    create_account_script: ScriptSetting = None
    authentication_script: ScriptSetting = None
    create_take_over_script: ScriptSetting = None
    do_take_over_script: ScriptSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_change_password_if_take_over(self, change_password_if_take_over: bool) -> Namespace:
        self.change_password_if_take_over = change_password_if_take_over
        return self

    def with_different_user_id_for_login_and_data_retention(self, different_user_id_for_login_and_data_retention: bool) -> Namespace:
        self.different_user_id_for_login_and_data_retention = different_user_id_for_login_and_data_retention
        return self

    def with_create_account_script(self, create_account_script: ScriptSetting) -> Namespace:
        self.create_account_script = create_account_script
        return self

    def with_authentication_script(self, authentication_script: ScriptSetting) -> Namespace:
        self.authentication_script = authentication_script
        return self

    def with_create_take_over_script(self, create_take_over_script: ScriptSetting) -> Namespace:
        self.create_take_over_script = create_take_over_script
        return self

    def with_do_take_over_script(self, do_take_over_script: ScriptSetting) -> Namespace:
        self.do_take_over_script = do_take_over_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> Namespace:
        self.log_setting = log_setting
        return self

    def with_created_at(self, created_at: int) -> Namespace:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Namespace:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

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
    ) -> Optional[Namespace]:
        if data is None:
            return None
        return Namespace()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_change_password_if_take_over(data.get('changePasswordIfTakeOver'))\
            .with_different_user_id_for_login_and_data_retention(data.get('differentUserIdForLoginAndDataRetention'))\
            .with_create_account_script(ScriptSetting.from_dict(data.get('createAccountScript')))\
            .with_authentication_script(ScriptSetting.from_dict(data.get('authenticationScript')))\
            .with_create_take_over_script(ScriptSetting.from_dict(data.get('createTakeOverScript')))\
            .with_do_take_over_script(ScriptSetting.from_dict(data.get('doTakeOverScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "changePasswordIfTakeOver": self.change_password_if_take_over,
            "differentUserIdForLoginAndDataRetention": self.different_user_id_for_login_and_data_retention,
            "createAccountScript": self.create_account_script.to_dict() if self.create_account_script else None,
            "authenticationScript": self.authentication_script.to_dict() if self.authentication_script else None,
            "createTakeOverScript": self.create_take_over_script.to_dict() if self.create_take_over_script else None,
            "doTakeOverScript": self.do_take_over_script.to_dict() if self.do_take_over_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }