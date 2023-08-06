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

from experience.model import *


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
    experience_cap_script_id: str = None
    change_experience_script: ScriptSetting = None
    change_rank_script: ScriptSetting = None
    change_rank_cap_script: ScriptSetting = None
    overflow_experience_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_experience_cap_script_id(self, experience_cap_script_id: str) -> CreateNamespaceRequest:
        self.experience_cap_script_id = experience_cap_script_id
        return self

    def with_change_experience_script(self, change_experience_script: ScriptSetting) -> CreateNamespaceRequest:
        self.change_experience_script = change_experience_script
        return self

    def with_change_rank_script(self, change_rank_script: ScriptSetting) -> CreateNamespaceRequest:
        self.change_rank_script = change_rank_script
        return self

    def with_change_rank_cap_script(self, change_rank_cap_script: ScriptSetting) -> CreateNamespaceRequest:
        self.change_rank_cap_script = change_rank_cap_script
        return self

    def with_overflow_experience_script(self, overflow_experience_script: ScriptSetting) -> CreateNamespaceRequest:
        self.overflow_experience_script = overflow_experience_script
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
            .with_experience_cap_script_id(data.get('experienceCapScriptId'))\
            .with_change_experience_script(ScriptSetting.from_dict(data.get('changeExperienceScript')))\
            .with_change_rank_script(ScriptSetting.from_dict(data.get('changeRankScript')))\
            .with_change_rank_cap_script(ScriptSetting.from_dict(data.get('changeRankCapScript')))\
            .with_overflow_experience_script(ScriptSetting.from_dict(data.get('overflowExperienceScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "experienceCapScriptId": self.experience_cap_script_id,
            "changeExperienceScript": self.change_experience_script.to_dict() if self.change_experience_script else None,
            "changeRankScript": self.change_rank_script.to_dict() if self.change_rank_script else None,
            "changeRankCapScript": self.change_rank_cap_script.to_dict() if self.change_rank_cap_script else None,
            "overflowExperienceScript": self.overflow_experience_script.to_dict() if self.overflow_experience_script else None,
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
    experience_cap_script_id: str = None
    change_experience_script: ScriptSetting = None
    change_rank_script: ScriptSetting = None
    change_rank_cap_script: ScriptSetting = None
    overflow_experience_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_experience_cap_script_id(self, experience_cap_script_id: str) -> UpdateNamespaceRequest:
        self.experience_cap_script_id = experience_cap_script_id
        return self

    def with_change_experience_script(self, change_experience_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.change_experience_script = change_experience_script
        return self

    def with_change_rank_script(self, change_rank_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.change_rank_script = change_rank_script
        return self

    def with_change_rank_cap_script(self, change_rank_cap_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.change_rank_cap_script = change_rank_cap_script
        return self

    def with_overflow_experience_script(self, overflow_experience_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.overflow_experience_script = overflow_experience_script
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
            .with_experience_cap_script_id(data.get('experienceCapScriptId'))\
            .with_change_experience_script(ScriptSetting.from_dict(data.get('changeExperienceScript')))\
            .with_change_rank_script(ScriptSetting.from_dict(data.get('changeRankScript')))\
            .with_change_rank_cap_script(ScriptSetting.from_dict(data.get('changeRankCapScript')))\
            .with_overflow_experience_script(ScriptSetting.from_dict(data.get('overflowExperienceScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "experienceCapScriptId": self.experience_cap_script_id,
            "changeExperienceScript": self.change_experience_script.to_dict() if self.change_experience_script else None,
            "changeRankScript": self.change_rank_script.to_dict() if self.change_rank_script else None,
            "changeRankCapScript": self.change_rank_cap_script.to_dict() if self.change_rank_cap_script else None,
            "overflowExperienceScript": self.overflow_experience_script.to_dict() if self.overflow_experience_script else None,
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


class DescribeExperienceModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeExperienceModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeExperienceModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeExperienceModelMastersRequest:
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
    ) -> Optional[DescribeExperienceModelMastersRequest]:
        if data is None:
            return None
        return DescribeExperienceModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    default_experience: int = None
    default_rank_cap: int = None
    max_rank_cap: int = None
    rank_threshold_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateExperienceModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateExperienceModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateExperienceModelMasterRequest:
        self.metadata = metadata
        return self

    def with_default_experience(self, default_experience: int) -> CreateExperienceModelMasterRequest:
        self.default_experience = default_experience
        return self

    def with_default_rank_cap(self, default_rank_cap: int) -> CreateExperienceModelMasterRequest:
        self.default_rank_cap = default_rank_cap
        return self

    def with_max_rank_cap(self, max_rank_cap: int) -> CreateExperienceModelMasterRequest:
        self.max_rank_cap = max_rank_cap
        return self

    def with_rank_threshold_name(self, rank_threshold_name: str) -> CreateExperienceModelMasterRequest:
        self.rank_threshold_name = rank_threshold_name
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
    ) -> Optional[CreateExperienceModelMasterRequest]:
        if data is None:
            return None
        return CreateExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_experience(data.get('defaultExperience'))\
            .with_default_rank_cap(data.get('defaultRankCap'))\
            .with_max_rank_cap(data.get('maxRankCap'))\
            .with_rank_threshold_name(data.get('rankThresholdName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultExperience": self.default_experience,
            "defaultRankCap": self.default_rank_cap,
            "maxRankCap": self.max_rank_cap,
            "rankThresholdName": self.rank_threshold_name,
        }


class GetExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> GetExperienceModelMasterRequest:
        self.experience_name = experience_name
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
    ) -> Optional[GetExperienceModelMasterRequest]:
        if data is None:
            return None
        return GetExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
        }


class UpdateExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None
    description: str = None
    metadata: str = None
    default_experience: int = None
    default_rank_cap: int = None
    max_rank_cap: int = None
    rank_threshold_name: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> UpdateExperienceModelMasterRequest:
        self.experience_name = experience_name
        return self

    def with_description(self, description: str) -> UpdateExperienceModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateExperienceModelMasterRequest:
        self.metadata = metadata
        return self

    def with_default_experience(self, default_experience: int) -> UpdateExperienceModelMasterRequest:
        self.default_experience = default_experience
        return self

    def with_default_rank_cap(self, default_rank_cap: int) -> UpdateExperienceModelMasterRequest:
        self.default_rank_cap = default_rank_cap
        return self

    def with_max_rank_cap(self, max_rank_cap: int) -> UpdateExperienceModelMasterRequest:
        self.max_rank_cap = max_rank_cap
        return self

    def with_rank_threshold_name(self, rank_threshold_name: str) -> UpdateExperienceModelMasterRequest:
        self.rank_threshold_name = rank_threshold_name
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
    ) -> Optional[UpdateExperienceModelMasterRequest]:
        if data is None:
            return None
        return UpdateExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_experience(data.get('defaultExperience'))\
            .with_default_rank_cap(data.get('defaultRankCap'))\
            .with_max_rank_cap(data.get('maxRankCap'))\
            .with_rank_threshold_name(data.get('rankThresholdName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultExperience": self.default_experience,
            "defaultRankCap": self.default_rank_cap,
            "maxRankCap": self.max_rank_cap,
            "rankThresholdName": self.rank_threshold_name,
        }


class DeleteExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> DeleteExperienceModelMasterRequest:
        self.experience_name = experience_name
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
    ) -> Optional[DeleteExperienceModelMasterRequest]:
        if data is None:
            return None
        return DeleteExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
        }


class DescribeExperienceModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeExperienceModelsRequest:
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
    ) -> Optional[DescribeExperienceModelsRequest]:
        if data is None:
            return None
        return DescribeExperienceModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetExperienceModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetExperienceModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> GetExperienceModelRequest:
        self.experience_name = experience_name
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
    ) -> Optional[GetExperienceModelRequest]:
        if data is None:
            return None
        return GetExperienceModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
        }


class DescribeThresholdMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeThresholdMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeThresholdMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeThresholdMastersRequest:
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
    ) -> Optional[DescribeThresholdMastersRequest]:
        if data is None:
            return None
        return DescribeThresholdMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateThresholdMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateThresholdMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateThresholdMasterRequest:
        self.metadata = metadata
        return self

    def with_values(self, values: List[int]) -> CreateThresholdMasterRequest:
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
    ) -> Optional[CreateThresholdMasterRequest]:
        if data is None:
            return None
        return CreateThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
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
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class GetThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    threshold_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_threshold_name(self, threshold_name: str) -> GetThresholdMasterRequest:
        self.threshold_name = threshold_name
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
    ) -> Optional[GetThresholdMasterRequest]:
        if data is None:
            return None
        return GetThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_threshold_name(data.get('thresholdName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "thresholdName": self.threshold_name,
        }


class UpdateThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    threshold_name: str = None
    description: str = None
    metadata: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_threshold_name(self, threshold_name: str) -> UpdateThresholdMasterRequest:
        self.threshold_name = threshold_name
        return self

    def with_description(self, description: str) -> UpdateThresholdMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateThresholdMasterRequest:
        self.metadata = metadata
        return self

    def with_values(self, values: List[int]) -> UpdateThresholdMasterRequest:
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
    ) -> Optional[UpdateThresholdMasterRequest]:
        if data is None:
            return None
        return UpdateThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_threshold_name(data.get('thresholdName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "thresholdName": self.threshold_name,
            "description": self.description,
            "metadata": self.metadata,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class DeleteThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    threshold_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_threshold_name(self, threshold_name: str) -> DeleteThresholdMasterRequest:
        self.threshold_name = threshold_name
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
    ) -> Optional[DeleteThresholdMasterRequest]:
        if data is None:
            return None
        return DeleteThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_threshold_name(data.get('thresholdName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "thresholdName": self.threshold_name,
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


class GetCurrentExperienceMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentExperienceMasterRequest:
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
    ) -> Optional[GetCurrentExperienceMasterRequest]:
        if data is None:
            return None
        return GetCurrentExperienceMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentExperienceMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentExperienceMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentExperienceMasterRequest:
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
    ) -> Optional[UpdateCurrentExperienceMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentExperienceMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentExperienceMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentExperienceMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentExperienceMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentExperienceMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentExperienceMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeStatusesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStatusesRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> DescribeStatusesRequest:
        self.experience_name = experience_name
        return self

    def with_access_token(self, access_token: str) -> DescribeStatusesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeStatusesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStatusesRequest:
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
    ) -> Optional[DescribeStatusesRequest]:
        if data is None:
            return None
        return DescribeStatusesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeStatusesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStatusesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> DescribeStatusesByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_user_id(self, user_id: str) -> DescribeStatusesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeStatusesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStatusesByUserIdRequest:
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
    ) -> Optional[DescribeStatusesByUserIdRequest]:
        if data is None:
            return None
        return DescribeStatusesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    property_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetStatusRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusRequest:
        self.property_id = property_id
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
    ) -> Optional[GetStatusRequest]:
        if data is None:
            return None
        return GetStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
        }


class GetStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusByUserIdRequest:
        self.property_id = property_id
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
    ) -> Optional[GetStatusByUserIdRequest]:
        if data is None:
            return None
        return GetStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
        }


class GetStatusWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    property_id: str = None
    key_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetStatusWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusWithSignatureRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusWithSignatureRequest:
        self.property_id = property_id
        return self

    def with_key_id(self, key_id: str) -> GetStatusWithSignatureRequest:
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
    ) -> Optional[GetStatusWithSignatureRequest]:
        if data is None:
            return None
        return GetStatusWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "keyId": self.key_id,
        }


class GetStatusWithSignatureByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusWithSignatureByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetStatusWithSignatureByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusWithSignatureByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusWithSignatureByUserIdRequest:
        self.property_id = property_id
        return self

    def with_key_id(self, key_id: str) -> GetStatusWithSignatureByUserIdRequest:
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
    ) -> Optional[GetStatusWithSignatureByUserIdRequest]:
        if data is None:
            return None
        return GetStatusWithSignatureByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "keyId": self.key_id,
        }


class AddExperienceByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    experience_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddExperienceByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AddExperienceByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> AddExperienceByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> AddExperienceByUserIdRequest:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> AddExperienceByUserIdRequest:
        self.experience_value = experience_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddExperienceByUserIdRequest:
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
    ) -> Optional[AddExperienceByUserIdRequest]:
        if data is None:
            return None
        return AddExperienceByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
        }


class SetExperienceByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    experience_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetExperienceByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetExperienceByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> SetExperienceByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SetExperienceByUserIdRequest:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> SetExperienceByUserIdRequest:
        self.experience_value = experience_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetExperienceByUserIdRequest:
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
    ) -> Optional[SetExperienceByUserIdRequest]:
        if data is None:
            return None
        return SetExperienceByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
        }


class AddRankCapByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    rank_cap_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddRankCapByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AddRankCapByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> AddRankCapByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> AddRankCapByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> AddRankCapByUserIdRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddRankCapByUserIdRequest:
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
    ) -> Optional[AddRankCapByUserIdRequest]:
        if data is None:
            return None
        return AddRankCapByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
        }


class SetRankCapByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    rank_cap_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRankCapByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetRankCapByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> SetRankCapByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SetRankCapByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> SetRankCapByUserIdRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRankCapByUserIdRequest:
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
    ) -> Optional[SetRankCapByUserIdRequest]:
        if data is None:
            return None
        return SetRankCapByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
        }


class DeleteStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> DeleteStatusByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> DeleteStatusByUserIdRequest:
        self.property_id = property_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteStatusByUserIdRequest:
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
    ) -> Optional[DeleteStatusByUserIdRequest]:
        if data is None:
            return None
        return DeleteStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
        }


class AddExperienceByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddExperienceByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddExperienceByStampSheetRequest:
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
    ) -> Optional[AddExperienceByStampSheetRequest]:
        if data is None:
            return None
        return AddExperienceByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class AddRankCapByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddRankCapByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddRankCapByStampSheetRequest:
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
    ) -> Optional[AddRankCapByStampSheetRequest]:
        if data is None:
            return None
        return AddRankCapByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetRankCapByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetRankCapByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetRankCapByStampSheetRequest:
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
    ) -> Optional[SetRankCapByStampSheetRequest]:
        if data is None:
            return None
        return SetRankCapByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }