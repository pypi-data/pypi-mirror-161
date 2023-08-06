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

from ranking.model import *


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
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
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
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
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


class DescribeCategoryModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCategoryModelsRequest:
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
    ) -> Optional[DescribeCategoryModelsRequest]:
        if data is None:
            return None
        return DescribeCategoryModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCategoryModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCategoryModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetCategoryModelRequest:
        self.category_name = category_name
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
    ) -> Optional[GetCategoryModelRequest]:
        if data is None:
            return None
        return GetCategoryModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
        }


class DescribeCategoryModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCategoryModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeCategoryModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCategoryModelMastersRequest:
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
    ) -> Optional[DescribeCategoryModelMastersRequest]:
        if data is None:
            return None
        return DescribeCategoryModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
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

    def with_namespace_name(self, namespace_name: str) -> CreateCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateCategoryModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateCategoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateCategoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> CreateCategoryModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> CreateCategoryModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_order_direction(self, order_direction: str) -> CreateCategoryModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_scope(self, scope: str) -> CreateCategoryModelMasterRequest:
        self.scope = scope
        return self

    def with_unique_by_user_id(self, unique_by_user_id: bool) -> CreateCategoryModelMasterRequest:
        self.unique_by_user_id = unique_by_user_id
        return self

    def with_calculate_fixed_timing_hour(self, calculate_fixed_timing_hour: int) -> CreateCategoryModelMasterRequest:
        self.calculate_fixed_timing_hour = calculate_fixed_timing_hour
        return self

    def with_calculate_fixed_timing_minute(self, calculate_fixed_timing_minute: int) -> CreateCategoryModelMasterRequest:
        self.calculate_fixed_timing_minute = calculate_fixed_timing_minute
        return self

    def with_calculate_interval_minutes(self, calculate_interval_minutes: int) -> CreateCategoryModelMasterRequest:
        self.calculate_interval_minutes = calculate_interval_minutes
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> CreateCategoryModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> CreateCategoryModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def with_generation(self, generation: str) -> CreateCategoryModelMasterRequest:
        self.generation = generation
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
    ) -> Optional[CreateCategoryModelMasterRequest]:
        if data is None:
            return None
        return CreateCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
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
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
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
        }


class GetCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetCategoryModelMasterRequest:
        self.category_name = category_name
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
    ) -> Optional[GetCategoryModelMasterRequest]:
        if data is None:
            return None
        return GetCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
        }


class UpdateCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
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

    def with_namespace_name(self, namespace_name: str) -> UpdateCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> UpdateCategoryModelMasterRequest:
        self.category_name = category_name
        return self

    def with_description(self, description: str) -> UpdateCategoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateCategoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> UpdateCategoryModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> UpdateCategoryModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_order_direction(self, order_direction: str) -> UpdateCategoryModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_scope(self, scope: str) -> UpdateCategoryModelMasterRequest:
        self.scope = scope
        return self

    def with_unique_by_user_id(self, unique_by_user_id: bool) -> UpdateCategoryModelMasterRequest:
        self.unique_by_user_id = unique_by_user_id
        return self

    def with_calculate_fixed_timing_hour(self, calculate_fixed_timing_hour: int) -> UpdateCategoryModelMasterRequest:
        self.calculate_fixed_timing_hour = calculate_fixed_timing_hour
        return self

    def with_calculate_fixed_timing_minute(self, calculate_fixed_timing_minute: int) -> UpdateCategoryModelMasterRequest:
        self.calculate_fixed_timing_minute = calculate_fixed_timing_minute
        return self

    def with_calculate_interval_minutes(self, calculate_interval_minutes: int) -> UpdateCategoryModelMasterRequest:
        self.calculate_interval_minutes = calculate_interval_minutes
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> UpdateCategoryModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> UpdateCategoryModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def with_generation(self, generation: str) -> UpdateCategoryModelMasterRequest:
        self.generation = generation
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
    ) -> Optional[UpdateCategoryModelMasterRequest]:
        if data is None:
            return None
        return UpdateCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
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
            .with_generation(data.get('generation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
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
        }


class DeleteCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DeleteCategoryModelMasterRequest:
        self.category_name = category_name
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
    ) -> Optional[DeleteCategoryModelMasterRequest]:
        if data is None:
            return None
        return DeleteCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
        }


class SubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    target_user_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> SubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> SubscribeRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> SubscribeRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> SubscribeRequest:
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
    ) -> Optional[SubscribeRequest]:
        if data is None:
            return None
        return SubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class SubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> SubscribeByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> SubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> SubscribeByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubscribeByUserIdRequest:
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
    ) -> Optional[SubscribeByUserIdRequest]:
        if data is None:
            return None
        return SubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
        }


class DescribeScoresRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    scorer_user_id: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeScoresRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DescribeScoresRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> DescribeScoresRequest:
        self.access_token = access_token
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> DescribeScoresRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeScoresRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeScoresRequest:
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
    ) -> Optional[DescribeScoresRequest]:
        if data is None:
            return None
        return DescribeScoresRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "scorerUserId": self.scorer_user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeScoresByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    scorer_user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeScoresByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DescribeScoresByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> DescribeScoresByUserIdRequest:
        self.user_id = user_id
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> DescribeScoresByUserIdRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeScoresByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeScoresByUserIdRequest:
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
    ) -> Optional[DescribeScoresByUserIdRequest]:
        if data is None:
            return None
        return DescribeScoresByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "scorerUserId": self.scorer_user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    scorer_user_id: str = None
    unique_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetScoreRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> GetScoreRequest:
        self.access_token = access_token
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> GetScoreRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def with_unique_id(self, unique_id: str) -> GetScoreRequest:
        self.unique_id = unique_id
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
    ) -> Optional[GetScoreRequest]:
        if data is None:
            return None
        return GetScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_unique_id(data.get('uniqueId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "scorerUserId": self.scorer_user_id,
            "uniqueId": self.unique_id,
        }


class GetScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    scorer_user_id: str = None
    unique_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetScoreByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> GetScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> GetScoreByUserIdRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def with_unique_id(self, unique_id: str) -> GetScoreByUserIdRequest:
        self.unique_id = unique_id
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
    ) -> Optional[GetScoreByUserIdRequest]:
        if data is None:
            return None
        return GetScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_unique_id(data.get('uniqueId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "scorerUserId": self.scorer_user_id,
            "uniqueId": self.unique_id,
        }


class DescribeRankingsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    start_index: int = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRankingsRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DescribeRankingsRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> DescribeRankingsRequest:
        self.access_token = access_token
        return self

    def with_start_index(self, start_index: int) -> DescribeRankingsRequest:
        self.start_index = start_index
        return self

    def with_page_token(self, page_token: str) -> DescribeRankingsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRankingsRequest:
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
    ) -> Optional[DescribeRankingsRequest]:
        if data is None:
            return None
        return DescribeRankingsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_start_index(data.get('startIndex'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "startIndex": self.start_index,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeRankingssByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    start_index: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRankingssByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DescribeRankingssByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> DescribeRankingssByUserIdRequest:
        self.user_id = user_id
        return self

    def with_start_index(self, start_index: int) -> DescribeRankingssByUserIdRequest:
        self.start_index = start_index
        return self

    def with_page_token(self, page_token: str) -> DescribeRankingssByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRankingssByUserIdRequest:
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
    ) -> Optional[DescribeRankingssByUserIdRequest]:
        if data is None:
            return None
        return DescribeRankingssByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_start_index(data.get('startIndex'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "startIndex": self.start_index,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeNearRankingsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    score: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeNearRankingsRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DescribeNearRankingsRequest:
        self.category_name = category_name
        return self

    def with_score(self, score: int) -> DescribeNearRankingsRequest:
        self.score = score
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
    ) -> Optional[DescribeNearRankingsRequest]:
        if data is None:
            return None
        return DescribeNearRankingsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_score(data.get('score'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "score": self.score,
        }


class GetRankingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    scorer_user_id: str = None
    unique_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRankingRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetRankingRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> GetRankingRequest:
        self.access_token = access_token
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> GetRankingRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def with_unique_id(self, unique_id: str) -> GetRankingRequest:
        self.unique_id = unique_id
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
    ) -> Optional[GetRankingRequest]:
        if data is None:
            return None
        return GetRankingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_unique_id(data.get('uniqueId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "scorerUserId": self.scorer_user_id,
            "uniqueId": self.unique_id,
        }


class GetRankingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    scorer_user_id: str = None
    unique_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRankingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetRankingByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> GetRankingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> GetRankingByUserIdRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def with_unique_id(self, unique_id: str) -> GetRankingByUserIdRequest:
        self.unique_id = unique_id
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
    ) -> Optional[GetRankingByUserIdRequest]:
        if data is None:
            return None
        return GetRankingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_unique_id(data.get('uniqueId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "scorerUserId": self.scorer_user_id,
            "uniqueId": self.unique_id,
        }


class PutScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    score: int = None
    metadata: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PutScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> PutScoreRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> PutScoreRequest:
        self.access_token = access_token
        return self

    def with_score(self, score: int) -> PutScoreRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutScoreRequest:
        self.metadata = metadata
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
    ) -> Optional[PutScoreRequest]:
        if data is None:
            return None
        return PutScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "score": self.score,
            "metadata": self.metadata,
        }


class PutScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    score: int = None
    metadata: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> PutScoreByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> PutScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_score(self, score: int) -> PutScoreByUserIdRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutScoreByUserIdRequest:
        self.metadata = metadata
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutScoreByUserIdRequest:
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
    ) -> Optional[PutScoreByUserIdRequest]:
        if data is None:
            return None
        return PutScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "score": self.score,
            "metadata": self.metadata,
        }


class CalcRankingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CalcRankingRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> CalcRankingRequest:
        self.category_name = category_name
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
    ) -> Optional[CalcRankingRequest]:
        if data is None:
            return None
        return CalcRankingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
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


class GetCurrentRankingMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentRankingMasterRequest:
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
    ) -> Optional[GetCurrentRankingMasterRequest]:
        if data is None:
            return None
        return GetCurrentRankingMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentRankingMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRankingMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentRankingMasterRequest:
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
    ) -> Optional[UpdateCurrentRankingMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentRankingMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentRankingMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRankingMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentRankingMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentRankingMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentRankingMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class GetSubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    target_user_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetSubscribeRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> GetSubscribeRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> GetSubscribeRequest:
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
    ) -> Optional[GetSubscribeRequest]:
        if data is None:
            return None
        return GetSubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class GetSubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    target_user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetSubscribeByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> GetSubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> GetSubscribeByUserIdRequest:
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
    ) -> Optional[GetSubscribeByUserIdRequest]:
        if data is None:
            return None
        return GetSubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
        }


class UnsubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    target_user_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UnsubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> UnsubscribeRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> UnsubscribeRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> UnsubscribeRequest:
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
    ) -> Optional[UnsubscribeRequest]:
        if data is None:
            return None
        return UnsubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class UnsubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnsubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> UnsubscribeByUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> UnsubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> UnsubscribeByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnsubscribeByUserIdRequest:
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
    ) -> Optional[UnsubscribeByUserIdRequest]:
        if data is None:
            return None
        return UnsubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
        }


class DescribeSubscribesByCategoryNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribesByCategoryNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DescribeSubscribesByCategoryNameRequest:
        self.category_name = category_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSubscribesByCategoryNameRequest:
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
    ) -> Optional[DescribeSubscribesByCategoryNameRequest]:
        if data is None:
            return None
        return DescribeSubscribesByCategoryNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "accessToken": self.access_token,
        }


class DescribeSubscribesByCategoryNameAndUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribesByCategoryNameAndUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DescribeSubscribesByCategoryNameAndUserIdRequest:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSubscribesByCategoryNameAndUserIdRequest:
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
    ) -> Optional[DescribeSubscribesByCategoryNameAndUserIdRequest]:
        if data is None:
            return None
        return DescribeSubscribesByCategoryNameAndUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "userId": self.user_id,
        }