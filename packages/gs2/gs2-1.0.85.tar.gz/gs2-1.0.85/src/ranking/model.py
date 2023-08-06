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


class SubscribeUser(core.Gs2Model):
    category_name: str = None
    user_id: str = None
    target_user_id: str = None

    def with_category_name(self, category_name: str) -> SubscribeUser:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> SubscribeUser:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> SubscribeUser:
        self.target_user_id = target_user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeUser]:
        if data is None:
            return None
        return SubscribeUser()\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryName": self.category_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
        }


class CalculatedAt(core.Gs2Model):
    category_name: str = None
    calculated_at: int = None

    def with_category_name(self, category_name: str) -> CalculatedAt:
        self.category_name = category_name
        return self

    def with_calculated_at(self, calculated_at: int) -> CalculatedAt:
        self.calculated_at = calculated_at
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CalculatedAt]:
        if data is None:
            return None
        return CalculatedAt()\
            .with_category_name(data.get('categoryName'))\
            .with_calculated_at(data.get('calculatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryName": self.category_name,
            "calculatedAt": self.calculated_at,
        }


class CurrentRankingMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentRankingMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentRankingMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentRankingMaster]:
        if data is None:
            return None
        return CurrentRankingMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class Ranking(core.Gs2Model):
    rank: int = None
    index: int = None
    user_id: str = None
    score: int = None
    metadata: str = None
    created_at: int = None

    def with_rank(self, rank: int) -> Ranking:
        self.rank = rank
        return self

    def with_index(self, index: int) -> Ranking:
        self.index = index
        return self

    def with_user_id(self, user_id: str) -> Ranking:
        self.user_id = user_id
        return self

    def with_score(self, score: int) -> Ranking:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> Ranking:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> Ranking:
        self.created_at = created_at
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Ranking]:
        if data is None:
            return None
        return Ranking()\
            .with_rank(data.get('rank'))\
            .with_index(data.get('index'))\
            .with_user_id(data.get('userId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "index": self.index,
            "userId": self.user_id,
            "score": self.score,
            "metadata": self.metadata,
            "createdAt": self.created_at,
        }


class Score(core.Gs2Model):
    score_id: str = None
    category_name: str = None
    user_id: str = None
    unique_id: str = None
    scorer_user_id: str = None
    score: int = None
    metadata: str = None
    created_at: int = None

    def with_score_id(self, score_id: str) -> Score:
        self.score_id = score_id
        return self

    def with_category_name(self, category_name: str) -> Score:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> Score:
        self.user_id = user_id
        return self

    def with_unique_id(self, unique_id: str) -> Score:
        self.unique_id = unique_id
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> Score:
        self.scorer_user_id = scorer_user_id
        return self

    def with_score(self, score: int) -> Score:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> Score:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> Score:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        category_name,
        scorer_user_id,
        unique_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking:{namespaceName}:user:{userId}:category:{categoryName}:score:{scorerUserId}:{uniqueId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            categoryName=category_name,
            scorerUserId=scorer_user_id,
            uniqueId=unique_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):category:(?P<categoryName>.+):score:(?P<scorerUserId>.+):(?P<uniqueId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):category:(?P<categoryName>.+):score:(?P<scorerUserId>.+):(?P<uniqueId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):category:(?P<categoryName>.+):score:(?P<scorerUserId>.+):(?P<uniqueId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):category:(?P<categoryName>.+):score:(?P<scorerUserId>.+):(?P<uniqueId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_category_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):category:(?P<categoryName>.+):score:(?P<scorerUserId>.+):(?P<uniqueId>.+)', grn)
        if match is None:
            return None
        return match.group('category_name')

    @classmethod
    def get_scorer_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):category:(?P<categoryName>.+):score:(?P<scorerUserId>.+):(?P<uniqueId>.+)', grn)
        if match is None:
            return None
        return match.group('scorer_user_id')

    @classmethod
    def get_unique_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):category:(?P<categoryName>.+):score:(?P<scorerUserId>.+):(?P<uniqueId>.+)', grn)
        if match is None:
            return None
        return match.group('unique_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Score]:
        if data is None:
            return None
        return Score()\
            .with_score_id(data.get('scoreId'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_unique_id(data.get('uniqueId'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scoreId": self.score_id,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "uniqueId": self.unique_id,
            "scorerUserId": self.scorer_user_id,
            "score": self.score,
            "metadata": self.metadata,
            "createdAt": self.created_at,
        }


class Subscribe(core.Gs2Model):
    subscribe_id: str = None
    category_name: str = None
    user_id: str = None
    target_user_ids: List[str] = None
    subscribed_user_ids: List[str] = None
    created_at: int = None

    def with_subscribe_id(self, subscribe_id: str) -> Subscribe:
        self.subscribe_id = subscribe_id
        return self

    def with_category_name(self, category_name: str) -> Subscribe:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> Subscribe:
        self.user_id = user_id
        return self

    def with_target_user_ids(self, target_user_ids: List[str]) -> Subscribe:
        self.target_user_ids = target_user_ids
        return self

    def with_subscribed_user_ids(self, subscribed_user_ids: List[str]) -> Subscribe:
        self.subscribed_user_ids = subscribed_user_ids
        return self

    def with_created_at(self, created_at: int) -> Subscribe:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        category_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking:{namespaceName}:user:{userId}:subscribe:category:{categoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            categoryName=category_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:category:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:category:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:category:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:category:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_category_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:category:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('category_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Subscribe]:
        if data is None:
            return None
        return Subscribe()\
            .with_subscribe_id(data.get('subscribeId'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_ids([
                data.get('targetUserIds')[i]
                for i in range(len(data.get('targetUserIds')) if data.get('targetUserIds') else 0)
            ])\
            .with_subscribed_user_ids([
                data.get('subscribedUserIds')[i]
                for i in range(len(data.get('subscribedUserIds')) if data.get('subscribedUserIds') else 0)
            ])\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscribeId": self.subscribe_id,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "targetUserIds": [
                self.target_user_ids[i]
                for i in range(len(self.target_user_ids) if self.target_user_ids else 0)
            ],
            "subscribedUserIds": [
                self.subscribed_user_ids[i]
                for i in range(len(self.subscribed_user_ids) if self.subscribed_user_ids else 0)
            ],
            "createdAt": self.created_at,
        }


class CategoryModelMaster(core.Gs2Model):
    category_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    order_direction: str = None
    scope: str = None
    unique_by_user_id: bool = None
    calculate_fixed_timing_hour: int = None
    calculate_fixed_timing_minute: int = None
    calculate_interval_minutes: int = None
    entry_period_event_id: str = None
    access_period_event_id: str = None
    generation: str = None
    created_at: int = None
    updated_at: int = None

    def with_category_model_id(self, category_model_id: str) -> CategoryModelMaster:
        self.category_model_id = category_model_id
        return self

    def with_name(self, name: str) -> CategoryModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> CategoryModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CategoryModelMaster:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> CategoryModelMaster:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> CategoryModelMaster:
        self.maximum_value = maximum_value
        return self

    def with_order_direction(self, order_direction: str) -> CategoryModelMaster:
        self.order_direction = order_direction
        return self

    def with_scope(self, scope: str) -> CategoryModelMaster:
        self.scope = scope
        return self

    def with_unique_by_user_id(self, unique_by_user_id: bool) -> CategoryModelMaster:
        self.unique_by_user_id = unique_by_user_id
        return self

    def with_calculate_fixed_timing_hour(self, calculate_fixed_timing_hour: int) -> CategoryModelMaster:
        self.calculate_fixed_timing_hour = calculate_fixed_timing_hour
        return self

    def with_calculate_fixed_timing_minute(self, calculate_fixed_timing_minute: int) -> CategoryModelMaster:
        self.calculate_fixed_timing_minute = calculate_fixed_timing_minute
        return self

    def with_calculate_interval_minutes(self, calculate_interval_minutes: int) -> CategoryModelMaster:
        self.calculate_interval_minutes = calculate_interval_minutes
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> CategoryModelMaster:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> CategoryModelMaster:
        self.access_period_event_id = access_period_event_id
        return self

    def with_generation(self, generation: str) -> CategoryModelMaster:
        self.generation = generation
        return self

    def with_created_at(self, created_at: int) -> CategoryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> CategoryModelMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        category_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking:{namespaceName}:categoryModelMaster:{categoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            categoryName=category_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModelMaster:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModelMaster:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModelMaster:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_category_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModelMaster:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('category_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CategoryModelMaster]:
        if data is None:
            return None
        return CategoryModelMaster()\
            .with_category_model_id(data.get('categoryModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_scope(data.get('scope'))\
            .with_unique_by_user_id(data.get('uniqueByUserId'))\
            .with_calculate_fixed_timing_hour(data.get('calculateFixedTimingHour'))\
            .with_calculate_fixed_timing_minute(data.get('calculateFixedTimingMinute'))\
            .with_calculate_interval_minutes(data.get('calculateIntervalMinutes'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))\
            .with_generation(data.get('generation'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryModelId": self.category_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "orderDirection": self.order_direction,
            "scope": self.scope,
            "uniqueByUserId": self.unique_by_user_id,
            "calculateFixedTimingHour": self.calculate_fixed_timing_hour,
            "calculateFixedTimingMinute": self.calculate_fixed_timing_minute,
            "calculateIntervalMinutes": self.calculate_interval_minutes,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
            "generation": self.generation,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class CategoryModel(core.Gs2Model):
    category_model_id: str = None
    name: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    order_direction: str = None
    scope: str = None
    unique_by_user_id: bool = None
    calculate_fixed_timing_hour: int = None
    calculate_fixed_timing_minute: int = None
    calculate_interval_minutes: int = None
    entry_period_event_id: str = None
    access_period_event_id: str = None
    generation: str = None

    def with_category_model_id(self, category_model_id: str) -> CategoryModel:
        self.category_model_id = category_model_id
        return self

    def with_name(self, name: str) -> CategoryModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CategoryModel:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> CategoryModel:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> CategoryModel:
        self.maximum_value = maximum_value
        return self

    def with_order_direction(self, order_direction: str) -> CategoryModel:
        self.order_direction = order_direction
        return self

    def with_scope(self, scope: str) -> CategoryModel:
        self.scope = scope
        return self

    def with_unique_by_user_id(self, unique_by_user_id: bool) -> CategoryModel:
        self.unique_by_user_id = unique_by_user_id
        return self

    def with_calculate_fixed_timing_hour(self, calculate_fixed_timing_hour: int) -> CategoryModel:
        self.calculate_fixed_timing_hour = calculate_fixed_timing_hour
        return self

    def with_calculate_fixed_timing_minute(self, calculate_fixed_timing_minute: int) -> CategoryModel:
        self.calculate_fixed_timing_minute = calculate_fixed_timing_minute
        return self

    def with_calculate_interval_minutes(self, calculate_interval_minutes: int) -> CategoryModel:
        self.calculate_interval_minutes = calculate_interval_minutes
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> CategoryModel:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> CategoryModel:
        self.access_period_event_id = access_period_event_id
        return self

    def with_generation(self, generation: str) -> CategoryModel:
        self.generation = generation
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        category_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking:{namespaceName}:categoryModel:{categoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            categoryName=category_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_category_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('category_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CategoryModel]:
        if data is None:
            return None
        return CategoryModel()\
            .with_category_model_id(data.get('categoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_scope(data.get('scope'))\
            .with_unique_by_user_id(data.get('uniqueByUserId'))\
            .with_calculate_fixed_timing_hour(data.get('calculateFixedTimingHour'))\
            .with_calculate_fixed_timing_minute(data.get('calculateFixedTimingMinute'))\
            .with_calculate_interval_minutes(data.get('calculateIntervalMinutes'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))\
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryModelId": self.category_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "orderDirection": self.order_direction,
            "scope": self.scope,
            "uniqueByUserId": self.unique_by_user_id,
            "calculateFixedTimingHour": self.calculate_fixed_timing_hour,
            "calculateFixedTimingMinute": self.calculate_fixed_timing_minute,
            "calculateIntervalMinutes": self.calculate_interval_minutes,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
            "generation": self.generation,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    last_calculated_ats: List[CalculatedAt] = None
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

    def with_last_calculated_ats(self, last_calculated_ats: List[CalculatedAt]) -> Namespace:
        self.last_calculated_ats = last_calculated_ats
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
        return 'grn:gs2:{region}:{ownerId}:ranking:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking:(?P<namespaceName>.+)', grn)
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
            .with_last_calculated_ats([
                CalculatedAt.from_dict(data.get('lastCalculatedAts')[i])
                for i in range(len(data.get('lastCalculatedAts')) if data.get('lastCalculatedAts') else 0)
            ])\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "lastCalculatedAts": [
                self.last_calculated_ats[i].to_dict() if self.last_calculated_ats[i] else None
                for i in range(len(self.last_calculated_ats) if self.last_calculated_ats else 0)
            ],
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }