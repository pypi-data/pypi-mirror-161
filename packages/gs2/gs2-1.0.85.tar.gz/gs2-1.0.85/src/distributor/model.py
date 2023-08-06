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


class NotificationSetting(core.Gs2Model):
    gateway_namespace_id: str = None
    enable_transfer_mobile_notification: bool = None
    sound: str = None

    def with_gateway_namespace_id(self, gateway_namespace_id: str) -> NotificationSetting:
        self.gateway_namespace_id = gateway_namespace_id
        return self

    def with_enable_transfer_mobile_notification(self, enable_transfer_mobile_notification: bool) -> NotificationSetting:
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        return self

    def with_sound(self, sound: str) -> NotificationSetting:
        self.sound = sound
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
    ) -> Optional[NotificationSetting]:
        if data is None:
            return None
        return NotificationSetting()\
            .with_gateway_namespace_id(data.get('gatewayNamespaceId'))\
            .with_enable_transfer_mobile_notification(data.get('enableTransferMobileNotification'))\
            .with_sound(data.get('sound'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatewayNamespaceId": self.gateway_namespace_id,
            "enableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "sound": self.sound,
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


class DistributeResource(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> DistributeResource:
        self.action = action
        return self

    def with_request(self, request: str) -> DistributeResource:
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
    ) -> Optional[DistributeResource]:
        if data is None:
            return None
        return DistributeResource()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
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


class StampSheetResult(core.Gs2Model):
    stamp_sheet_result_id: str = None
    user_id: str = None
    transaction_id: str = None
    task_requests: List[ConsumeAction] = None
    sheet_request: AcquireAction = None
    task_results: List[str] = None
    sheet_result: str = None
    next_transaction_id: str = None
    created_at: int = None

    def with_stamp_sheet_result_id(self, stamp_sheet_result_id: str) -> StampSheetResult:
        self.stamp_sheet_result_id = stamp_sheet_result_id
        return self

    def with_user_id(self, user_id: str) -> StampSheetResult:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> StampSheetResult:
        self.transaction_id = transaction_id
        return self

    def with_task_requests(self, task_requests: List[ConsumeAction]) -> StampSheetResult:
        self.task_requests = task_requests
        return self

    def with_sheet_request(self, sheet_request: AcquireAction) -> StampSheetResult:
        self.sheet_request = sheet_request
        return self

    def with_task_results(self, task_results: List[str]) -> StampSheetResult:
        self.task_results = task_results
        return self

    def with_sheet_result(self, sheet_result: str) -> StampSheetResult:
        self.sheet_result = sheet_result
        return self

    def with_next_transaction_id(self, next_transaction_id: str) -> StampSheetResult:
        self.next_transaction_id = next_transaction_id
        return self

    def with_created_at(self, created_at: int) -> StampSheetResult:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        transaction_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}:user:{userId}:stampSheet:result:{transactionId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            transactionId=transaction_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_transaction_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('transaction_id')

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
    ) -> Optional[StampSheetResult]:
        if data is None:
            return None
        return StampSheetResult()\
            .with_stamp_sheet_result_id(data.get('stampSheetResultId'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_task_requests([
                ConsumeAction.from_dict(data.get('taskRequests')[i])
                for i in range(len(data.get('taskRequests')) if data.get('taskRequests') else 0)
            ])\
            .with_sheet_request(AcquireAction.from_dict(data.get('sheetRequest')))\
            .with_task_results([
                data.get('taskResults')[i]
                for i in range(len(data.get('taskResults')) if data.get('taskResults') else 0)
            ])\
            .with_sheet_result(data.get('sheetResult'))\
            .with_next_transaction_id(data.get('nextTransactionId'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheetResultId": self.stamp_sheet_result_id,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "taskRequests": [
                self.task_requests[i].to_dict() if self.task_requests[i] else None
                for i in range(len(self.task_requests) if self.task_requests else 0)
            ],
            "sheetRequest": self.sheet_request.to_dict() if self.sheet_request else None,
            "taskResults": [
                self.task_results[i]
                for i in range(len(self.task_results) if self.task_results else 0)
            ],
            "sheetResult": self.sheet_result,
            "nextTransactionId": self.next_transaction_id,
            "createdAt": self.created_at,
        }


class CurrentDistributorMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentDistributorMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentDistributorMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentDistributorMaster]:
        if data is None:
            return None
        return CurrentDistributorMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class DistributorModel(core.Gs2Model):
    distributor_model_id: str = None
    name: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None

    def with_distributor_model_id(self, distributor_model_id: str) -> DistributorModel:
        self.distributor_model_id = distributor_model_id
        return self

    def with_name(self, name: str) -> DistributorModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> DistributorModel:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> DistributorModel:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> DistributorModel:
        self.white_list_target_ids = white_list_target_ids
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        distributor_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}:model:{distributorName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            distributorName=distributor_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_distributor_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('distributor_name')

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
    ) -> Optional[DistributorModel]:
        if data is None:
            return None
        return DistributorModel()\
            .with_distributor_model_id(data.get('distributorModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids([
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')) if data.get('whiteListTargetIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributorModelId": self.distributor_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids) if self.white_list_target_ids else 0)
            ],
        }


class DistributorModelMaster(core.Gs2Model):
    distributor_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None
    created_at: int = None
    updated_at: int = None

    def with_distributor_model_id(self, distributor_model_id: str) -> DistributorModelMaster:
        self.distributor_model_id = distributor_model_id
        return self

    def with_name(self, name: str) -> DistributorModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> DistributorModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> DistributorModelMaster:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> DistributorModelMaster:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> DistributorModelMaster:
        self.white_list_target_ids = white_list_target_ids
        return self

    def with_created_at(self, created_at: int) -> DistributorModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> DistributorModelMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        distributor_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}:model:{distributorName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            distributorName=distributor_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_distributor_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('distributor_name')

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
    ) -> Optional[DistributorModelMaster]:
        if data is None:
            return None
        return DistributorModelMaster()\
            .with_distributor_model_id(data.get('distributorModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids([
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')) if data.get('whiteListTargetIds') else 0)
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributorModelId": self.distributor_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids) if self.white_list_target_ids else 0)
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    assume_user_id: str = None
    auto_run_stamp_sheet_notification: NotificationSetting = None
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

    def with_assume_user_id(self, assume_user_id: str) -> Namespace:
        self.assume_user_id = assume_user_id
        return self

    def with_auto_run_stamp_sheet_notification(self, auto_run_stamp_sheet_notification: NotificationSetting) -> Namespace:
        self.auto_run_stamp_sheet_notification = auto_run_stamp_sheet_notification
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
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
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
            .with_assume_user_id(data.get('assumeUserId'))\
            .with_auto_run_stamp_sheet_notification(NotificationSetting.from_dict(data.get('autoRunStampSheetNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "autoRunStampSheetNotification": self.auto_run_stamp_sheet_notification.to_dict() if self.auto_run_stamp_sheet_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }