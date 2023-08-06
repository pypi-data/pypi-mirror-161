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


class GitHubCheckoutSetting(core.Gs2Model):
    api_key_id: str = None
    repository_name: str = None
    source_path: str = None
    reference_type: str = None
    commit_hash: str = None
    branch_name: str = None
    tag_name: str = None

    def with_api_key_id(self, api_key_id: str) -> GitHubCheckoutSetting:
        self.api_key_id = api_key_id
        return self

    def with_repository_name(self, repository_name: str) -> GitHubCheckoutSetting:
        self.repository_name = repository_name
        return self

    def with_source_path(self, source_path: str) -> GitHubCheckoutSetting:
        self.source_path = source_path
        return self

    def with_reference_type(self, reference_type: str) -> GitHubCheckoutSetting:
        self.reference_type = reference_type
        return self

    def with_commit_hash(self, commit_hash: str) -> GitHubCheckoutSetting:
        self.commit_hash = commit_hash
        return self

    def with_branch_name(self, branch_name: str) -> GitHubCheckoutSetting:
        self.branch_name = branch_name
        return self

    def with_tag_name(self, tag_name: str) -> GitHubCheckoutSetting:
        self.tag_name = tag_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GitHubCheckoutSetting]:
        if data is None:
            return None
        return GitHubCheckoutSetting()\
            .with_api_key_id(data.get('apiKeyId'))\
            .with_repository_name(data.get('repositoryName'))\
            .with_source_path(data.get('sourcePath'))\
            .with_reference_type(data.get('referenceType'))\
            .with_commit_hash(data.get('commitHash'))\
            .with_branch_name(data.get('branchName'))\
            .with_tag_name(data.get('tagName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiKeyId": self.api_key_id,
            "repositoryName": self.repository_name,
            "sourcePath": self.source_path,
            "referenceType": self.reference_type,
            "commitHash": self.commit_hash,
            "branchName": self.branch_name,
            "tagName": self.tag_name,
        }


class Status(core.Gs2Model):
    status_id: str = None
    experience_name: str = None
    user_id: str = None
    property_id: str = None
    experience_value: int = None
    rank_value: int = None
    rank_cap_value: int = None
    next_rank_up_experience_value: int = None
    created_at: int = None
    updated_at: int = None

    def with_status_id(self, status_id: str) -> Status:
        self.status_id = status_id
        return self

    def with_experience_name(self, experience_name: str) -> Status:
        self.experience_name = experience_name
        return self

    def with_user_id(self, user_id: str) -> Status:
        self.user_id = user_id
        return self

    def with_property_id(self, property_id: str) -> Status:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> Status:
        self.experience_value = experience_value
        return self

    def with_rank_value(self, rank_value: int) -> Status:
        self.rank_value = rank_value
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> Status:
        self.rank_cap_value = rank_cap_value
        return self

    def with_next_rank_up_experience_value(self, next_rank_up_experience_value: int) -> Status:
        self.next_rank_up_experience_value = next_rank_up_experience_value
        return self

    def with_created_at(self, created_at: int) -> Status:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Status:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        experience_name,
        property_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:experience:{namespaceName}:user:{userId}:experienceModel:{experienceName}:property:{propertyId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            experienceName=experience_name,
            propertyId=property_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):user:(?P<userId>.+):experienceModel:(?P<experienceName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):user:(?P<userId>.+):experienceModel:(?P<experienceName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):user:(?P<userId>.+):experienceModel:(?P<experienceName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):user:(?P<userId>.+):experienceModel:(?P<experienceName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_experience_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):user:(?P<userId>.+):experienceModel:(?P<experienceName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('experience_name')

    @classmethod
    def get_property_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):user:(?P<userId>.+):experienceModel:(?P<experienceName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('property_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Status]:
        if data is None:
            return None
        return Status()\
            .with_status_id(data.get('statusId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))\
            .with_rank_value(data.get('rankValue'))\
            .with_rank_cap_value(data.get('rankCapValue'))\
            .with_next_rank_up_experience_value(data.get('nextRankUpExperienceValue'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statusId": self.status_id,
            "experienceName": self.experience_name,
            "userId": self.user_id,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
            "rankValue": self.rank_value,
            "rankCapValue": self.rank_cap_value,
            "nextRankUpExperienceValue": self.next_rank_up_experience_value,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class CurrentExperienceMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentExperienceMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentExperienceMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:experience:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentExperienceMaster]:
        if data is None:
            return None
        return CurrentExperienceMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class Threshold(core.Gs2Model):
    metadata: str = None
    values: List[int] = None

    def with_metadata(self, metadata: str) -> Threshold:
        self.metadata = metadata
        return self

    def with_values(self, values: List[int]) -> Threshold:
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
    ) -> Optional[Threshold]:
        if data is None:
            return None
        return Threshold()\
            .with_metadata(data.get('metadata'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
        }


class ThresholdMaster(core.Gs2Model):
    threshold_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    values: List[int] = None
    created_at: int = None
    updated_at: int = None

    def with_threshold_id(self, threshold_id: str) -> ThresholdMaster:
        self.threshold_id = threshold_id
        return self

    def with_name(self, name: str) -> ThresholdMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> ThresholdMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> ThresholdMaster:
        self.metadata = metadata
        return self

    def with_values(self, values: List[int]) -> ThresholdMaster:
        self.values = values
        return self

    def with_created_at(self, created_at: int) -> ThresholdMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ThresholdMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        threshold_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:experience:{namespaceName}:threshold:{thresholdName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            thresholdName=threshold_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):threshold:(?P<thresholdName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):threshold:(?P<thresholdName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):threshold:(?P<thresholdName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_threshold_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):threshold:(?P<thresholdName>.+)', grn)
        if match is None:
            return None
        return match.group('threshold_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ThresholdMaster]:
        if data is None:
            return None
        return ThresholdMaster()\
            .with_threshold_id(data.get('thresholdId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_values([
                data.get('values')[i]
                for i in range(len(data.get('values')) if data.get('values') else 0)
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thresholdId": self.threshold_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "values": [
                self.values[i]
                for i in range(len(self.values) if self.values else 0)
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class ExperienceModel(core.Gs2Model):
    experience_model_id: str = None
    name: str = None
    metadata: str = None
    default_experience: int = None
    default_rank_cap: int = None
    max_rank_cap: int = None
    rank_threshold: Threshold = None

    def with_experience_model_id(self, experience_model_id: str) -> ExperienceModel:
        self.experience_model_id = experience_model_id
        return self

    def with_name(self, name: str) -> ExperienceModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> ExperienceModel:
        self.metadata = metadata
        return self

    def with_default_experience(self, default_experience: int) -> ExperienceModel:
        self.default_experience = default_experience
        return self

    def with_default_rank_cap(self, default_rank_cap: int) -> ExperienceModel:
        self.default_rank_cap = default_rank_cap
        return self

    def with_max_rank_cap(self, max_rank_cap: int) -> ExperienceModel:
        self.max_rank_cap = max_rank_cap
        return self

    def with_rank_threshold(self, rank_threshold: Threshold) -> ExperienceModel:
        self.rank_threshold = rank_threshold
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        experience_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:experience:{namespaceName}:model:{experienceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            experienceName=experience_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_experience_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('experience_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ExperienceModel]:
        if data is None:
            return None
        return ExperienceModel()\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_default_experience(data.get('defaultExperience'))\
            .with_default_rank_cap(data.get('defaultRankCap'))\
            .with_max_rank_cap(data.get('maxRankCap'))\
            .with_rank_threshold(Threshold.from_dict(data.get('rankThreshold')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experienceModelId": self.experience_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "defaultExperience": self.default_experience,
            "defaultRankCap": self.default_rank_cap,
            "maxRankCap": self.max_rank_cap,
            "rankThreshold": self.rank_threshold.to_dict() if self.rank_threshold else None,
        }


class ExperienceModelMaster(core.Gs2Model):
    experience_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    default_experience: int = None
    default_rank_cap: int = None
    max_rank_cap: int = None
    rank_threshold_name: str = None
    created_at: int = None
    updated_at: int = None

    def with_experience_model_id(self, experience_model_id: str) -> ExperienceModelMaster:
        self.experience_model_id = experience_model_id
        return self

    def with_name(self, name: str) -> ExperienceModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> ExperienceModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> ExperienceModelMaster:
        self.metadata = metadata
        return self

    def with_default_experience(self, default_experience: int) -> ExperienceModelMaster:
        self.default_experience = default_experience
        return self

    def with_default_rank_cap(self, default_rank_cap: int) -> ExperienceModelMaster:
        self.default_rank_cap = default_rank_cap
        return self

    def with_max_rank_cap(self, max_rank_cap: int) -> ExperienceModelMaster:
        self.max_rank_cap = max_rank_cap
        return self

    def with_rank_threshold_name(self, rank_threshold_name: str) -> ExperienceModelMaster:
        self.rank_threshold_name = rank_threshold_name
        return self

    def with_created_at(self, created_at: int) -> ExperienceModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ExperienceModelMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        experience_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:experience:{namespaceName}:model:{experienceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            experienceName=experience_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_experience_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+):model:(?P<experienceName>.+)', grn)
        if match is None:
            return None
        return match.group('experience_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ExperienceModelMaster]:
        if data is None:
            return None
        return ExperienceModelMaster()\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_experience(data.get('defaultExperience'))\
            .with_default_rank_cap(data.get('defaultRankCap'))\
            .with_max_rank_cap(data.get('maxRankCap'))\
            .with_rank_threshold_name(data.get('rankThresholdName'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experienceModelId": self.experience_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultExperience": self.default_experience,
            "defaultRankCap": self.default_rank_cap,
            "maxRankCap": self.max_rank_cap,
            "rankThresholdName": self.rank_threshold_name,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    experience_cap_script_id: str = None
    change_experience_script: ScriptSetting = None
    change_rank_script: ScriptSetting = None
    change_rank_cap_script: ScriptSetting = None
    overflow_experience_script: ScriptSetting = None
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

    def with_experience_cap_script_id(self, experience_cap_script_id: str) -> Namespace:
        self.experience_cap_script_id = experience_cap_script_id
        return self

    def with_change_experience_script(self, change_experience_script: ScriptSetting) -> Namespace:
        self.change_experience_script = change_experience_script
        return self

    def with_change_rank_script(self, change_rank_script: ScriptSetting) -> Namespace:
        self.change_rank_script = change_rank_script
        return self

    def with_change_rank_cap_script(self, change_rank_cap_script: ScriptSetting) -> Namespace:
        self.change_rank_cap_script = change_rank_cap_script
        return self

    def with_overflow_experience_script(self, overflow_experience_script: ScriptSetting) -> Namespace:
        self.overflow_experience_script = overflow_experience_script
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
        return 'grn:gs2:{region}:{ownerId}:experience:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):experience:(?P<namespaceName>.+)', grn)
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
            .with_experience_cap_script_id(data.get('experienceCapScriptId'))\
            .with_change_experience_script(ScriptSetting.from_dict(data.get('changeExperienceScript')))\
            .with_change_rank_script(ScriptSetting.from_dict(data.get('changeRankScript')))\
            .with_change_rank_cap_script(ScriptSetting.from_dict(data.get('changeRankCapScript')))\
            .with_overflow_experience_script(ScriptSetting.from_dict(data.get('overflowExperienceScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "experienceCapScriptId": self.experience_cap_script_id,
            "changeExperienceScript": self.change_experience_script.to_dict() if self.change_experience_script else None,
            "changeRankScript": self.change_rank_script.to_dict() if self.change_rank_script else None,
            "changeRankCapScript": self.change_rank_cap_script.to_dict() if self.change_rank_cap_script else None,
            "overflowExperienceScript": self.overflow_experience_script.to_dict() if self.overflow_experience_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }