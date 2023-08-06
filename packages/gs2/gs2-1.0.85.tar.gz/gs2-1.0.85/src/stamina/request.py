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

from stamina.model import *


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
    overflow_trigger_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_overflow_trigger_script(self, overflow_trigger_script: ScriptSetting) -> CreateNamespaceRequest:
        self.overflow_trigger_script = overflow_trigger_script
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
            .with_overflow_trigger_script(ScriptSetting.from_dict(data.get('overflowTriggerScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "overflowTriggerScript": self.overflow_trigger_script.to_dict() if self.overflow_trigger_script else None,
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
    overflow_trigger_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_overflow_trigger_script(self, overflow_trigger_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.overflow_trigger_script = overflow_trigger_script
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
            .with_overflow_trigger_script(ScriptSetting.from_dict(data.get('overflowTriggerScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "overflowTriggerScript": self.overflow_trigger_script.to_dict() if self.overflow_trigger_script else None,
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


class DescribeStaminaModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminaModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeStaminaModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStaminaModelMastersRequest:
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
    ) -> Optional[DescribeStaminaModelMastersRequest]:
        if data is None:
            return None
        return DescribeStaminaModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    recover_interval_minutes: int = None
    recover_value: int = None
    initial_capacity: int = None
    is_overflow: bool = None
    max_capacity: int = None
    max_stamina_table_name: str = None
    recover_interval_table_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateStaminaModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateStaminaModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateStaminaModelMasterRequest:
        self.metadata = metadata
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> CreateStaminaModelMasterRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> CreateStaminaModelMasterRequest:
        self.recover_value = recover_value
        return self

    def with_initial_capacity(self, initial_capacity: int) -> CreateStaminaModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_is_overflow(self, is_overflow: bool) -> CreateStaminaModelMasterRequest:
        self.is_overflow = is_overflow
        return self

    def with_max_capacity(self, max_capacity: int) -> CreateStaminaModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> CreateStaminaModelMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> CreateStaminaModelMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> CreateStaminaModelMasterRequest:
        self.recover_value_table_name = recover_value_table_name
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
    ) -> Optional[CreateStaminaModelMasterRequest]:
        if data is None:
            return None
        return CreateStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_is_overflow(data.get('isOverflow'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "initialCapacity": self.initial_capacity,
            "isOverflow": self.is_overflow,
            "maxCapacity": self.max_capacity,
            "maxStaminaTableName": self.max_stamina_table_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
            "recoverValueTableName": self.recover_value_table_name,
        }


class GetStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaModelMasterRequest:
        self.stamina_name = stamina_name
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
    ) -> Optional[GetStaminaModelMasterRequest]:
        if data is None:
            return None
        return GetStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
        }


class UpdateStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    description: str = None
    metadata: str = None
    recover_interval_minutes: int = None
    recover_value: int = None
    initial_capacity: int = None
    is_overflow: bool = None
    max_capacity: int = None
    max_stamina_table_name: str = None
    recover_interval_table_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> UpdateStaminaModelMasterRequest:
        self.stamina_name = stamina_name
        return self

    def with_description(self, description: str) -> UpdateStaminaModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateStaminaModelMasterRequest:
        self.metadata = metadata
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> UpdateStaminaModelMasterRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> UpdateStaminaModelMasterRequest:
        self.recover_value = recover_value
        return self

    def with_initial_capacity(self, initial_capacity: int) -> UpdateStaminaModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_is_overflow(self, is_overflow: bool) -> UpdateStaminaModelMasterRequest:
        self.is_overflow = is_overflow
        return self

    def with_max_capacity(self, max_capacity: int) -> UpdateStaminaModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> UpdateStaminaModelMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> UpdateStaminaModelMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> UpdateStaminaModelMasterRequest:
        self.recover_value_table_name = recover_value_table_name
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
    ) -> Optional[UpdateStaminaModelMasterRequest]:
        if data is None:
            return None
        return UpdateStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_is_overflow(data.get('isOverflow'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "description": self.description,
            "metadata": self.metadata,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "initialCapacity": self.initial_capacity,
            "isOverflow": self.is_overflow,
            "maxCapacity": self.max_capacity,
            "maxStaminaTableName": self.max_stamina_table_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
            "recoverValueTableName": self.recover_value_table_name,
        }


class DeleteStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> DeleteStaminaModelMasterRequest:
        self.stamina_name = stamina_name
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
    ) -> Optional[DeleteStaminaModelMasterRequest]:
        if data is None:
            return None
        return DeleteStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
        }


class DescribeMaxStaminaTableMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMaxStaminaTableMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeMaxStaminaTableMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMaxStaminaTableMastersRequest:
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
    ) -> Optional[DescribeMaxStaminaTableMastersRequest]:
        if data is None:
            return None
        return DescribeMaxStaminaTableMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateMaxStaminaTableMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateMaxStaminaTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateMaxStaminaTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateMaxStaminaTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> CreateMaxStaminaTableMasterRequest:
        self.values = values
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
    ) -> Optional[CreateMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return CreateMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class GetMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    max_stamina_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> GetMaxStaminaTableMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
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
    ) -> Optional[GetMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return GetMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "maxStaminaTableName": self.max_stamina_table_name,
        }


class UpdateMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    max_stamina_table_name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> UpdateMaxStaminaTableMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def with_description(self, description: str) -> UpdateMaxStaminaTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateMaxStaminaTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateMaxStaminaTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> UpdateMaxStaminaTableMasterRequest:
        self.values = values
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
    ) -> Optional[UpdateMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return UpdateMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "maxStaminaTableName": self.max_stamina_table_name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class DeleteMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    max_stamina_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> DeleteMaxStaminaTableMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
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
    ) -> Optional[DeleteMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return DeleteMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "maxStaminaTableName": self.max_stamina_table_name,
        }


class DescribeRecoverIntervalTableMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRecoverIntervalTableMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRecoverIntervalTableMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRecoverIntervalTableMastersRequest:
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
    ) -> Optional[DescribeRecoverIntervalTableMastersRequest]:
        if data is None:
            return None
        return DescribeRecoverIntervalTableMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRecoverIntervalTableMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRecoverIntervalTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRecoverIntervalTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateRecoverIntervalTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> CreateRecoverIntervalTableMasterRequest:
        self.values = values
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
    ) -> Optional[CreateRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return CreateRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class GetRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_interval_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> GetRecoverIntervalTableMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
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
    ) -> Optional[GetRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return GetRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
        }


class UpdateRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_interval_table_name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def with_description(self, description: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> UpdateRecoverIntervalTableMasterRequest:
        self.values = values
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
    ) -> Optional[UpdateRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return UpdateRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class DeleteRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_interval_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> DeleteRecoverIntervalTableMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
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
    ) -> Optional[DeleteRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return DeleteRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
        }


class DescribeRecoverValueTableMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRecoverValueTableMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRecoverValueTableMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRecoverValueTableMastersRequest:
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
    ) -> Optional[DescribeRecoverValueTableMastersRequest]:
        if data is None:
            return None
        return DescribeRecoverValueTableMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRecoverValueTableMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRecoverValueTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRecoverValueTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateRecoverValueTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> CreateRecoverValueTableMasterRequest:
        self.values = values
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
    ) -> Optional[CreateRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return CreateRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class GetRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> GetRecoverValueTableMasterRequest:
        self.recover_value_table_name = recover_value_table_name
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
    ) -> Optional[GetRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return GetRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverValueTableName": self.recover_value_table_name,
        }


class UpdateRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_value_table_name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> UpdateRecoverValueTableMasterRequest:
        self.recover_value_table_name = recover_value_table_name
        return self

    def with_description(self, description: str) -> UpdateRecoverValueTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRecoverValueTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateRecoverValueTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> UpdateRecoverValueTableMasterRequest:
        self.values = values
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
    ) -> Optional[UpdateRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return UpdateRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverValueTableName": self.recover_value_table_name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class DeleteRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> DeleteRecoverValueTableMasterRequest:
        self.recover_value_table_name = recover_value_table_name
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
    ) -> Optional[DeleteRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return DeleteRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverValueTableName": self.recover_value_table_name,
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


class GetCurrentStaminaMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentStaminaMasterRequest:
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
    ) -> Optional[GetCurrentStaminaMasterRequest]:
        if data is None:
            return None
        return GetCurrentStaminaMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentStaminaMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentStaminaMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentStaminaMasterRequest:
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
    ) -> Optional[UpdateCurrentStaminaMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentStaminaMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentStaminaMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentStaminaMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentStaminaMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentStaminaMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentStaminaMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeStaminaModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminaModelsRequest:
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
    ) -> Optional[DescribeStaminaModelsRequest]:
        if data is None:
            return None
        return DescribeStaminaModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetStaminaModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaModelRequest:
        self.stamina_name = stamina_name
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
    ) -> Optional[GetStaminaModelRequest]:
        if data is None:
            return None
        return GetStaminaModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
        }


class DescribeStaminasRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminasRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeStaminasRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeStaminasRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStaminasRequest:
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
    ) -> Optional[DescribeStaminasRequest]:
        if data is None:
            return None
        return DescribeStaminasRequest()\
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


class DescribeStaminasByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminasByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeStaminasByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeStaminasByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStaminasByUserIdRequest:
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
    ) -> Optional[DescribeStaminasByUserIdRequest]:
        if data is None:
            return None
        return DescribeStaminasByUserIdRequest()\
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


class GetStaminaRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> GetStaminaRequest:
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
    ) -> Optional[GetStaminaRequest]:
        if data is None:
            return None
        return GetStaminaRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
        }


class GetStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> GetStaminaByUserIdRequest:
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
    ) -> Optional[GetStaminaByUserIdRequest]:
        if data is None:
            return None
        return GetStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
        }


class UpdateStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    value: int = None
    max_value: int = None
    recover_interval_minutes: int = None
    recover_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> UpdateStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> UpdateStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_value(self, value: int) -> UpdateStaminaByUserIdRequest:
        self.value = value
        return self

    def with_max_value(self, max_value: int) -> UpdateStaminaByUserIdRequest:
        self.max_value = max_value
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> UpdateStaminaByUserIdRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> UpdateStaminaByUserIdRequest:
        self.recover_value = recover_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateStaminaByUserIdRequest:
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
    ) -> Optional[UpdateStaminaByUserIdRequest]:
        if data is None:
            return None
        return UpdateStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_value(data.get('value'))\
            .with_max_value(data.get('maxValue'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "value": self.value,
            "maxValue": self.max_value,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
        }


class ConsumeStaminaRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    consume_value: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeStaminaRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> ConsumeStaminaRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> ConsumeStaminaRequest:
        self.access_token = access_token
        return self

    def with_consume_value(self, consume_value: int) -> ConsumeStaminaRequest:
        self.consume_value = consume_value
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
    ) -> Optional[ConsumeStaminaRequest]:
        if data is None:
            return None
        return ConsumeStaminaRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_consume_value(data.get('consumeValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "consumeValue": self.consume_value,
        }


class ConsumeStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    consume_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> ConsumeStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> ConsumeStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_consume_value(self, consume_value: int) -> ConsumeStaminaByUserIdRequest:
        self.consume_value = consume_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeStaminaByUserIdRequest:
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
    ) -> Optional[ConsumeStaminaByUserIdRequest]:
        if data is None:
            return None
        return ConsumeStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_consume_value(data.get('consumeValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "consumeValue": self.consume_value,
        }


class RecoverStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    recover_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RecoverStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> RecoverStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> RecoverStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_recover_value(self, recover_value: int) -> RecoverStaminaByUserIdRequest:
        self.recover_value = recover_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RecoverStaminaByUserIdRequest:
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
    ) -> Optional[RecoverStaminaByUserIdRequest]:
        if data is None:
            return None
        return RecoverStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_recover_value(data.get('recoverValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "recoverValue": self.recover_value,
        }


class RaiseMaxValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    raise_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RaiseMaxValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> RaiseMaxValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> RaiseMaxValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_raise_value(self, raise_value: int) -> RaiseMaxValueByUserIdRequest:
        self.raise_value = raise_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RaiseMaxValueByUserIdRequest:
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
    ) -> Optional[RaiseMaxValueByUserIdRequest]:
        if data is None:
            return None
        return RaiseMaxValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_raise_value(data.get('raiseValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "raiseValue": self.raise_value,
        }


class SetMaxValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    max_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetMaxValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetMaxValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> SetMaxValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_max_value(self, max_value: int) -> SetMaxValueByUserIdRequest:
        self.max_value = max_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetMaxValueByUserIdRequest:
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
    ) -> Optional[SetMaxValueByUserIdRequest]:
        if data is None:
            return None
        return SetMaxValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_max_value(data.get('maxValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "maxValue": self.max_value,
        }


class SetRecoverIntervalByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    recover_interval_minutes: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverIntervalByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverIntervalByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> SetRecoverIntervalByUserIdRequest:
        self.user_id = user_id
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> SetRecoverIntervalByUserIdRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRecoverIntervalByUserIdRequest:
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
    ) -> Optional[SetRecoverIntervalByUserIdRequest]:
        if data is None:
            return None
        return SetRecoverIntervalByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "recoverIntervalMinutes": self.recover_interval_minutes,
        }


class SetRecoverValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    recover_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> SetRecoverValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_recover_value(self, recover_value: int) -> SetRecoverValueByUserIdRequest:
        self.recover_value = recover_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRecoverValueByUserIdRequest:
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
    ) -> Optional[SetRecoverValueByUserIdRequest]:
        if data is None:
            return None
        return SetRecoverValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_recover_value(data.get('recoverValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "recoverValue": self.recover_value,
        }


class SetMaxValueByStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    key_id: str = None
    signed_status_body: str = None
    signed_status_signature: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> SetMaxValueByStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetMaxValueByStatusRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> SetMaxValueByStatusRequest:
        self.access_token = access_token
        return self

    def with_key_id(self, key_id: str) -> SetMaxValueByStatusRequest:
        self.key_id = key_id
        return self

    def with_signed_status_body(self, signed_status_body: str) -> SetMaxValueByStatusRequest:
        self.signed_status_body = signed_status_body
        return self

    def with_signed_status_signature(self, signed_status_signature: str) -> SetMaxValueByStatusRequest:
        self.signed_status_signature = signed_status_signature
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
    ) -> Optional[SetMaxValueByStatusRequest]:
        if data is None:
            return None
        return SetMaxValueByStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_key_id(data.get('keyId'))\
            .with_signed_status_body(data.get('signedStatusBody'))\
            .with_signed_status_signature(data.get('signedStatusSignature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "keyId": self.key_id,
            "signedStatusBody": self.signed_status_body,
            "signedStatusSignature": self.signed_status_signature,
        }


class SetRecoverIntervalByStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    key_id: str = None
    signed_status_body: str = None
    signed_status_signature: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverIntervalByStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverIntervalByStatusRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> SetRecoverIntervalByStatusRequest:
        self.access_token = access_token
        return self

    def with_key_id(self, key_id: str) -> SetRecoverIntervalByStatusRequest:
        self.key_id = key_id
        return self

    def with_signed_status_body(self, signed_status_body: str) -> SetRecoverIntervalByStatusRequest:
        self.signed_status_body = signed_status_body
        return self

    def with_signed_status_signature(self, signed_status_signature: str) -> SetRecoverIntervalByStatusRequest:
        self.signed_status_signature = signed_status_signature
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
    ) -> Optional[SetRecoverIntervalByStatusRequest]:
        if data is None:
            return None
        return SetRecoverIntervalByStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_key_id(data.get('keyId'))\
            .with_signed_status_body(data.get('signedStatusBody'))\
            .with_signed_status_signature(data.get('signedStatusSignature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "keyId": self.key_id,
            "signedStatusBody": self.signed_status_body,
            "signedStatusSignature": self.signed_status_signature,
        }


class SetRecoverValueByStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    key_id: str = None
    signed_status_body: str = None
    signed_status_signature: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverValueByStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverValueByStatusRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> SetRecoverValueByStatusRequest:
        self.access_token = access_token
        return self

    def with_key_id(self, key_id: str) -> SetRecoverValueByStatusRequest:
        self.key_id = key_id
        return self

    def with_signed_status_body(self, signed_status_body: str) -> SetRecoverValueByStatusRequest:
        self.signed_status_body = signed_status_body
        return self

    def with_signed_status_signature(self, signed_status_signature: str) -> SetRecoverValueByStatusRequest:
        self.signed_status_signature = signed_status_signature
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
    ) -> Optional[SetRecoverValueByStatusRequest]:
        if data is None:
            return None
        return SetRecoverValueByStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_key_id(data.get('keyId'))\
            .with_signed_status_body(data.get('signedStatusBody'))\
            .with_signed_status_signature(data.get('signedStatusSignature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "keyId": self.key_id,
            "signedStatusBody": self.signed_status_body,
            "signedStatusSignature": self.signed_status_signature,
        }


class DeleteStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> DeleteStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> DeleteStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteStaminaByUserIdRequest:
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
    ) -> Optional[DeleteStaminaByUserIdRequest]:
        if data is None:
            return None
        return DeleteStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
        }


class RecoverStaminaByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RecoverStaminaByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RecoverStaminaByStampSheetRequest:
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
    ) -> Optional[RecoverStaminaByStampSheetRequest]:
        if data is None:
            return None
        return RecoverStaminaByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RaiseMaxValueByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RaiseMaxValueByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RaiseMaxValueByStampSheetRequest:
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
    ) -> Optional[RaiseMaxValueByStampSheetRequest]:
        if data is None:
            return None
        return RaiseMaxValueByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetMaxValueByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetMaxValueByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetMaxValueByStampSheetRequest:
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
    ) -> Optional[SetMaxValueByStampSheetRequest]:
        if data is None:
            return None
        return SetMaxValueByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetRecoverIntervalByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetRecoverIntervalByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetRecoverIntervalByStampSheetRequest:
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
    ) -> Optional[SetRecoverIntervalByStampSheetRequest]:
        if data is None:
            return None
        return SetRecoverIntervalByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetRecoverValueByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetRecoverValueByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetRecoverValueByStampSheetRequest:
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
    ) -> Optional[SetRecoverValueByStampSheetRequest]:
        if data is None:
            return None
        return SetRecoverValueByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ConsumeStaminaByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ConsumeStaminaByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ConsumeStaminaByStampTaskRequest:
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
    ) -> Optional[ConsumeStaminaByStampTaskRequest]:
        if data is None:
            return None
        return ConsumeStaminaByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }