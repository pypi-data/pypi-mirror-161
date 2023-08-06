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


class TransactionSetting(core.Gs2Model):
    enable_auto_run: bool = None
    distributor_namespace_id: str = None
    key_id: str = None
    queue_namespace_id: str = None

    def with_enable_auto_run(self, enable_auto_run: bool) -> TransactionSetting:
        self.enable_auto_run = enable_auto_run
        return self

    def with_distributor_namespace_id(self, distributor_namespace_id: str) -> TransactionSetting:
        self.distributor_namespace_id = distributor_namespace_id
        return self

    def with_key_id(self, key_id: str) -> TransactionSetting:
        self.key_id = key_id
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> TransactionSetting:
        self.queue_namespace_id = queue_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TransactionSetting]:
        if data is None:
            return None
        return TransactionSetting()\
            .with_enable_auto_run(data.get('enableAutoRun'))\
            .with_distributor_namespace_id(data.get('distributorNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enableAutoRun": self.enable_auto_run,
            "distributorNamespaceId": self.distributor_namespace_id,
            "keyId": self.key_id,
            "queueNamespaceId": self.queue_namespace_id,
        }


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


class Config(core.Gs2Model):
    key: str = None
    value: str = None

    def with_key(self, key: str) -> Config:
        self.key = key
        return self

    def with_value(self, value: str) -> Config:
        self.value = value
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Config]:
        if data is None:
            return None
        return Config()\
            .with_key(data.get('key'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
        }


class ConsumeAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> ConsumeAction:
        self.action = action
        return self

    def with_request(self, request: str) -> ConsumeAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeAction]:
        if data is None:
            return None
        return ConsumeAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class AcquireAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> AcquireAction:
        self.action = action
        return self

    def with_request(self, request: str) -> AcquireAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireAction]:
        if data is None:
            return None
        return AcquireAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class Await(core.Gs2Model):
    await_id: str = None
    user_id: str = None
    rate_name: str = None
    name: str = None
    count: int = None
    exchanged_at: int = None

    def with_await_id(self, await_id: str) -> Await:
        self.await_id = await_id
        return self

    def with_user_id(self, user_id: str) -> Await:
        self.user_id = user_id
        return self

    def with_rate_name(self, rate_name: str) -> Await:
        self.rate_name = rate_name
        return self

    def with_name(self, name: str) -> Await:
        self.name = name
        return self

    def with_count(self, count: int) -> Await:
        self.count = count
        return self

    def with_exchanged_at(self, exchanged_at: int) -> Await:
        self.exchanged_at = exchanged_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        await_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:user:{userId}:await:{awaitName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            awaitName=await_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_await_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('await_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Await]:
        if data is None:
            return None
        return Await()\
            .with_await_id(data.get('awaitId'))\
            .with_user_id(data.get('userId'))\
            .with_rate_name(data.get('rateName'))\
            .with_name(data.get('name'))\
            .with_count(data.get('count'))\
            .with_exchanged_at(data.get('exchangedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "awaitId": self.await_id,
            "userId": self.user_id,
            "rateName": self.rate_name,
            "name": self.name,
            "count": self.count,
            "exchangedAt": self.exchanged_at,
        }


class CurrentRateMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentRateMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentRateMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentRateMaster]:
        if data is None:
            return None
        return CurrentRateMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class RateModelMaster(core.Gs2Model):
    rate_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    consume_actions: List[ConsumeAction] = None
    timing_type: str = None
    lock_time: int = None
    enable_skip: bool = None
    skip_consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None
    created_at: int = None
    updated_at: int = None

    def with_rate_model_id(self, rate_model_id: str) -> RateModelMaster:
        self.rate_model_id = rate_model_id
        return self

    def with_name(self, name: str) -> RateModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> RateModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> RateModelMaster:
        self.metadata = metadata
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> RateModelMaster:
        self.consume_actions = consume_actions
        return self

    def with_timing_type(self, timing_type: str) -> RateModelMaster:
        self.timing_type = timing_type
        return self

    def with_lock_time(self, lock_time: int) -> RateModelMaster:
        self.lock_time = lock_time
        return self

    def with_enable_skip(self, enable_skip: bool) -> RateModelMaster:
        self.enable_skip = enable_skip
        return self

    def with_skip_consume_actions(self, skip_consume_actions: List[ConsumeAction]) -> RateModelMaster:
        self.skip_consume_actions = skip_consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> RateModelMaster:
        self.acquire_actions = acquire_actions
        return self

    def with_created_at(self, created_at: int) -> RateModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RateModelMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:model:{rateName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rateName=rate_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('rate_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RateModelMaster]:
        if data is None:
            return None
        return RateModelMaster()\
            .with_rate_model_id(data.get('rateModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_actions([
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')) if data.get('consumeActions') else 0)
            ])\
            .with_timing_type(data.get('timingType'))\
            .with_lock_time(data.get('lockTime'))\
            .with_enable_skip(data.get('enableSkip'))\
            .with_skip_consume_actions([
                ConsumeAction.from_dict(data.get('skipConsumeActions')[i])
                for i in range(len(data.get('skipConsumeActions')) if data.get('skipConsumeActions') else 0)
            ])\
            .with_acquire_actions([
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')) if data.get('acquireActions') else 0)
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rateModelId": self.rate_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "consumeActions": [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions) if self.consume_actions else 0)
            ],
            "timingType": self.timing_type,
            "lockTime": self.lock_time,
            "enableSkip": self.enable_skip,
            "skipConsumeActions": [
                self.skip_consume_actions[i].to_dict() if self.skip_consume_actions[i] else None
                for i in range(len(self.skip_consume_actions) if self.skip_consume_actions else 0)
            ],
            "acquireActions": [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions) if self.acquire_actions else 0)
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class RateModel(core.Gs2Model):
    rate_model_id: str = None
    name: str = None
    metadata: str = None
    consume_actions: List[ConsumeAction] = None
    timing_type: str = None
    lock_time: int = None
    enable_skip: bool = None
    skip_consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None

    def with_rate_model_id(self, rate_model_id: str) -> RateModel:
        self.rate_model_id = rate_model_id
        return self

    def with_name(self, name: str) -> RateModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RateModel:
        self.metadata = metadata
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> RateModel:
        self.consume_actions = consume_actions
        return self

    def with_timing_type(self, timing_type: str) -> RateModel:
        self.timing_type = timing_type
        return self

    def with_lock_time(self, lock_time: int) -> RateModel:
        self.lock_time = lock_time
        return self

    def with_enable_skip(self, enable_skip: bool) -> RateModel:
        self.enable_skip = enable_skip
        return self

    def with_skip_consume_actions(self, skip_consume_actions: List[ConsumeAction]) -> RateModel:
        self.skip_consume_actions = skip_consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> RateModel:
        self.acquire_actions = acquire_actions
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:model:{rateName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rateName=rate_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('rate_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RateModel]:
        if data is None:
            return None
        return RateModel()\
            .with_rate_model_id(data.get('rateModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_actions([
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')) if data.get('consumeActions') else 0)
            ])\
            .with_timing_type(data.get('timingType'))\
            .with_lock_time(data.get('lockTime'))\
            .with_enable_skip(data.get('enableSkip'))\
            .with_skip_consume_actions([
                ConsumeAction.from_dict(data.get('skipConsumeActions')[i])
                for i in range(len(data.get('skipConsumeActions')) if data.get('skipConsumeActions') else 0)
            ])\
            .with_acquire_actions([
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')) if data.get('acquireActions') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rateModelId": self.rate_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "consumeActions": [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions) if self.consume_actions else 0)
            ],
            "timingType": self.timing_type,
            "lockTime": self.lock_time,
            "enableSkip": self.enable_skip,
            "skipConsumeActions": [
                self.skip_consume_actions[i].to_dict() if self.skip_consume_actions[i] else None
                for i in range(len(self.skip_consume_actions) if self.skip_consume_actions else 0)
            ],
            "acquireActions": [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions) if self.acquire_actions else 0)
            ],
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    enable_direct_exchange: bool = None
    enable_await_exchange: bool = None
    transaction_setting: TransactionSetting = None
    exchange_script: ScriptSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_enable_direct_exchange(self, enable_direct_exchange: bool) -> Namespace:
        self.enable_direct_exchange = enable_direct_exchange
        return self

    def with_enable_await_exchange(self, enable_await_exchange: bool) -> Namespace:
        self.enable_await_exchange = enable_await_exchange
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_exchange_script(self, exchange_script: ScriptSetting) -> Namespace:
        self.exchange_script = exchange_script
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

    def with_queue_namespace_id(self, queue_namespace_id: str) -> Namespace:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> Namespace:
        self.key_id = key_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
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
            .with_enable_direct_exchange(data.get('enableDirectExchange'))\
            .with_enable_await_exchange(data.get('enableAwaitExchange'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_exchange_script(ScriptSetting.from_dict(data.get('exchangeScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "enableDirectExchange": self.enable_direct_exchange,
            "enableAwaitExchange": self.enable_await_exchange,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "exchangeScript": self.exchange_script.to_dict() if self.exchange_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
        }