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

from distributor.model import *


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
    auto_run_stamp_sheet_notification: NotificationSetting = None
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

    def with_auto_run_stamp_sheet_notification(self, auto_run_stamp_sheet_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.auto_run_stamp_sheet_notification = auto_run_stamp_sheet_notification
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
            .with_auto_run_stamp_sheet_notification(NotificationSetting.from_dict(data.get('autoRunStampSheetNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "autoRunStampSheetNotification": self.auto_run_stamp_sheet_notification.to_dict() if self.auto_run_stamp_sheet_notification else None,
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
    auto_run_stamp_sheet_notification: NotificationSetting = None
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

    def with_auto_run_stamp_sheet_notification(self, auto_run_stamp_sheet_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.auto_run_stamp_sheet_notification = auto_run_stamp_sheet_notification
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
            .with_auto_run_stamp_sheet_notification(NotificationSetting.from_dict(data.get('autoRunStampSheetNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "autoRunStampSheetNotification": self.auto_run_stamp_sheet_notification.to_dict() if self.auto_run_stamp_sheet_notification else None,
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


class DescribeDistributorModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDistributorModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeDistributorModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDistributorModelMastersRequest:
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
    ) -> Optional[DescribeDistributorModelMastersRequest]:
        if data is None:
            return None
        return DescribeDistributorModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> CreateDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateDistributorModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateDistributorModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateDistributorModelMasterRequest:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> CreateDistributorModelMasterRequest:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> CreateDistributorModelMasterRequest:
        self.white_list_target_ids = white_list_target_ids
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
    ) -> Optional[CreateDistributorModelMasterRequest]:
        if data is None:
            return None
        return CreateDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids([
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')) if data.get('whiteListTargetIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids) if self.white_list_target_ids else 0)
            ],
        }


class GetDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> GetDistributorModelMasterRequest:
        self.distributor_name = distributor_name
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
    ) -> Optional[GetDistributorModelMasterRequest]:
        if data is None:
            return None
        return GetDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
        }


class UpdateDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None
    description: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> UpdateDistributorModelMasterRequest:
        self.distributor_name = distributor_name
        return self

    def with_description(self, description: str) -> UpdateDistributorModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateDistributorModelMasterRequest:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> UpdateDistributorModelMasterRequest:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> UpdateDistributorModelMasterRequest:
        self.white_list_target_ids = white_list_target_ids
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
    ) -> Optional[UpdateDistributorModelMasterRequest]:
        if data is None:
            return None
        return UpdateDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids([
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')) if data.get('whiteListTargetIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
            "description": self.description,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids) if self.white_list_target_ids else 0)
            ],
        }


class DeleteDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> DeleteDistributorModelMasterRequest:
        self.distributor_name = distributor_name
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
    ) -> Optional[DeleteDistributorModelMasterRequest]:
        if data is None:
            return None
        return DeleteDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
        }


class DescribeDistributorModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDistributorModelsRequest:
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
    ) -> Optional[DescribeDistributorModelsRequest]:
        if data is None:
            return None
        return DescribeDistributorModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetDistributorModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDistributorModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> GetDistributorModelRequest:
        self.distributor_name = distributor_name
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
    ) -> Optional[GetDistributorModelRequest]:
        if data is None:
            return None
        return GetDistributorModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
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


class GetCurrentDistributorMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentDistributorMasterRequest:
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
    ) -> Optional[GetCurrentDistributorMasterRequest]:
        if data is None:
            return None
        return GetCurrentDistributorMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentDistributorMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentDistributorMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentDistributorMasterRequest:
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
    ) -> Optional[UpdateCurrentDistributorMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentDistributorMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentDistributorMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentDistributorMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentDistributorMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DistributeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None
    user_id: str = None
    distribute_resource: DistributeResource = None

    def with_namespace_name(self, namespace_name: str) -> DistributeRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> DistributeRequest:
        self.distributor_name = distributor_name
        return self

    def with_user_id(self, user_id: str) -> DistributeRequest:
        self.user_id = user_id
        return self

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeRequest:
        self.distribute_resource = distribute_resource
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
    ) -> Optional[DistributeRequest]:
        if data is None:
            return None
        return DistributeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))\
            .with_user_id(data.get('userId'))\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
            "userId": self.user_id,
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
        }


class DistributeWithoutOverflowProcessRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    distribute_resource: DistributeResource = None

    def with_user_id(self, user_id: str) -> DistributeWithoutOverflowProcessRequest:
        self.user_id = user_id
        return self

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeWithoutOverflowProcessRequest:
        self.distribute_resource = distribute_resource
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
    ) -> Optional[DistributeWithoutOverflowProcessRequest]:
        if data is None:
            return None
        return DistributeWithoutOverflowProcessRequest()\
            .with_user_id(data.get('userId'))\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
        }


class RunStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamp_task: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RunStampTaskRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamp_task(self, stamp_task: str) -> RunStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> RunStampTaskRequest:
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
    ) -> Optional[RunStampTaskRequest]:
        if data is None:
            return None
        return RunStampTaskRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class RunStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RunStampSheetRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetRequest:
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
    ) -> Optional[RunStampSheetRequest]:
        if data is None:
            return None
        return RunStampSheetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RunStampSheetExpressRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RunStampSheetExpressRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetExpressRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetExpressRequest:
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
    ) -> Optional[RunStampSheetExpressRequest]:
        if data is None:
            return None
        return RunStampSheetExpressRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RunStampTaskWithoutNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> RunStampTaskWithoutNamespaceRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> RunStampTaskWithoutNamespaceRequest:
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
    ) -> Optional[RunStampTaskWithoutNamespaceRequest]:
        if data is None:
            return None
        return RunStampTaskWithoutNamespaceRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class RunStampSheetWithoutNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetWithoutNamespaceRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetWithoutNamespaceRequest:
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
    ) -> Optional[RunStampSheetWithoutNamespaceRequest]:
        if data is None:
            return None
        return RunStampSheetWithoutNamespaceRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RunStampSheetExpressWithoutNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetExpressWithoutNamespaceRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetExpressWithoutNamespaceRequest:
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
    ) -> Optional[RunStampSheetExpressWithoutNamespaceRequest]:
        if data is None:
            return None
        return RunStampSheetExpressWithoutNamespaceRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class GetStampSheetResultRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    transaction_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStampSheetResultRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetStampSheetResultRequest:
        self.access_token = access_token
        return self

    def with_transaction_id(self, transaction_id: str) -> GetStampSheetResultRequest:
        self.transaction_id = transaction_id
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
    ) -> Optional[GetStampSheetResultRequest]:
        if data is None:
            return None
        return GetStampSheetResultRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "transactionId": self.transaction_id,
        }


class GetStampSheetResultByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    transaction_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStampSheetResultByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetStampSheetResultByUserIdRequest:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> GetStampSheetResultByUserIdRequest:
        self.transaction_id = transaction_id
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
    ) -> Optional[GetStampSheetResultByUserIdRequest]:
        if data is None:
            return None
        return GetStampSheetResultByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
        }