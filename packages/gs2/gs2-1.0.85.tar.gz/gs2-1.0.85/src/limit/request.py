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

from limit.model import *


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


class DescribeCountersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    limit_name: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCountersRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeCountersRequest:
        self.access_token = access_token
        return self

    def with_limit_name(self, limit_name: str) -> DescribeCountersRequest:
        self.limit_name = limit_name
        return self

    def with_page_token(self, page_token: str) -> DescribeCountersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCountersRequest:
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
    ) -> Optional[DescribeCountersRequest]:
        if data is None:
            return None
        return DescribeCountersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_limit_name(data.get('limitName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "limitName": self.limit_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeCountersByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    limit_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCountersByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeCountersByUserIdRequest:
        self.user_id = user_id
        return self

    def with_limit_name(self, limit_name: str) -> DescribeCountersByUserIdRequest:
        self.limit_name = limit_name
        return self

    def with_page_token(self, page_token: str) -> DescribeCountersByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCountersByUserIdRequest:
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
    ) -> Optional[DescribeCountersByUserIdRequest]:
        if data is None:
            return None
        return DescribeCountersByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_limit_name(data.get('limitName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "limitName": self.limit_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetCounterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None
    access_token: str = None
    counter_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCounterRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> GetCounterRequest:
        self.limit_name = limit_name
        return self

    def with_access_token(self, access_token: str) -> GetCounterRequest:
        self.access_token = access_token
        return self

    def with_counter_name(self, counter_name: str) -> GetCounterRequest:
        self.counter_name = counter_name
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
    ) -> Optional[GetCounterRequest]:
        if data is None:
            return None
        return GetCounterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))\
            .with_access_token(data.get('accessToken'))\
            .with_counter_name(data.get('counterName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
            "accessToken": self.access_token,
            "counterName": self.counter_name,
        }


class GetCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None
    user_id: str = None
    counter_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> GetCounterByUserIdRequest:
        self.limit_name = limit_name
        return self

    def with_user_id(self, user_id: str) -> GetCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_counter_name(self, counter_name: str) -> GetCounterByUserIdRequest:
        self.counter_name = counter_name
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
    ) -> Optional[GetCounterByUserIdRequest]:
        if data is None:
            return None
        return GetCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))\
            .with_user_id(data.get('userId'))\
            .with_counter_name(data.get('counterName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
            "userId": self.user_id,
            "counterName": self.counter_name,
        }


class CountUpRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None
    counter_name: str = None
    access_token: str = None
    count_up_value: int = None
    max_value: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CountUpRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> CountUpRequest:
        self.limit_name = limit_name
        return self

    def with_counter_name(self, counter_name: str) -> CountUpRequest:
        self.counter_name = counter_name
        return self

    def with_access_token(self, access_token: str) -> CountUpRequest:
        self.access_token = access_token
        return self

    def with_count_up_value(self, count_up_value: int) -> CountUpRequest:
        self.count_up_value = count_up_value
        return self

    def with_max_value(self, max_value: int) -> CountUpRequest:
        self.max_value = max_value
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
    ) -> Optional[CountUpRequest]:
        if data is None:
            return None
        return CountUpRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))\
            .with_counter_name(data.get('counterName'))\
            .with_access_token(data.get('accessToken'))\
            .with_count_up_value(data.get('countUpValue'))\
            .with_max_value(data.get('maxValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
            "counterName": self.counter_name,
            "accessToken": self.access_token,
            "countUpValue": self.count_up_value,
            "maxValue": self.max_value,
        }


class CountUpByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None
    counter_name: str = None
    user_id: str = None
    count_up_value: int = None
    max_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CountUpByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> CountUpByUserIdRequest:
        self.limit_name = limit_name
        return self

    def with_counter_name(self, counter_name: str) -> CountUpByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_user_id(self, user_id: str) -> CountUpByUserIdRequest:
        self.user_id = user_id
        return self

    def with_count_up_value(self, count_up_value: int) -> CountUpByUserIdRequest:
        self.count_up_value = count_up_value
        return self

    def with_max_value(self, max_value: int) -> CountUpByUserIdRequest:
        self.max_value = max_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CountUpByUserIdRequest:
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
    ) -> Optional[CountUpByUserIdRequest]:
        if data is None:
            return None
        return CountUpByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))\
            .with_counter_name(data.get('counterName'))\
            .with_user_id(data.get('userId'))\
            .with_count_up_value(data.get('countUpValue'))\
            .with_max_value(data.get('maxValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
            "counterName": self.counter_name,
            "userId": self.user_id,
            "countUpValue": self.count_up_value,
            "maxValue": self.max_value,
        }


class DeleteCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None
    user_id: str = None
    counter_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> DeleteCounterByUserIdRequest:
        self.limit_name = limit_name
        return self

    def with_user_id(self, user_id: str) -> DeleteCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_counter_name(self, counter_name: str) -> DeleteCounterByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteCounterByUserIdRequest:
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
    ) -> Optional[DeleteCounterByUserIdRequest]:
        if data is None:
            return None
        return DeleteCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))\
            .with_user_id(data.get('userId'))\
            .with_counter_name(data.get('counterName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
            "userId": self.user_id,
            "counterName": self.counter_name,
        }


class CountUpByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> CountUpByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> CountUpByStampTaskRequest:
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
    ) -> Optional[CountUpByStampTaskRequest]:
        if data is None:
            return None
        return CountUpByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DeleteByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DeleteByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DeleteByStampSheetRequest:
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
    ) -> Optional[DeleteByStampSheetRequest]:
        if data is None:
            return None
        return DeleteByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DescribeLimitModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeLimitModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeLimitModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeLimitModelMastersRequest:
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
    ) -> Optional[DescribeLimitModelMastersRequest]:
        if data is None:
            return None
        return DescribeLimitModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateLimitModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateLimitModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateLimitModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateLimitModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateLimitModelMasterRequest:
        self.metadata = metadata
        return self

    def with_reset_type(self, reset_type: str) -> CreateLimitModelMasterRequest:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> CreateLimitModelMasterRequest:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> CreateLimitModelMasterRequest:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> CreateLimitModelMasterRequest:
        self.reset_hour = reset_hour
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
    ) -> Optional[CreateLimitModelMasterRequest]:
        if data is None:
            return None
        return CreateLimitModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
        }


class GetLimitModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetLimitModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> GetLimitModelMasterRequest:
        self.limit_name = limit_name
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
    ) -> Optional[GetLimitModelMasterRequest]:
        if data is None:
            return None
        return GetLimitModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
        }


class UpdateLimitModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None
    description: str = None
    metadata: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateLimitModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> UpdateLimitModelMasterRequest:
        self.limit_name = limit_name
        return self

    def with_description(self, description: str) -> UpdateLimitModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateLimitModelMasterRequest:
        self.metadata = metadata
        return self

    def with_reset_type(self, reset_type: str) -> UpdateLimitModelMasterRequest:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> UpdateLimitModelMasterRequest:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> UpdateLimitModelMasterRequest:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> UpdateLimitModelMasterRequest:
        self.reset_hour = reset_hour
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
    ) -> Optional[UpdateLimitModelMasterRequest]:
        if data is None:
            return None
        return UpdateLimitModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
            "description": self.description,
            "metadata": self.metadata,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
        }


class DeleteLimitModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteLimitModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> DeleteLimitModelMasterRequest:
        self.limit_name = limit_name
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
    ) -> Optional[DeleteLimitModelMasterRequest]:
        if data is None:
            return None
        return DeleteLimitModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
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


class GetCurrentLimitMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentLimitMasterRequest:
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
    ) -> Optional[GetCurrentLimitMasterRequest]:
        if data is None:
            return None
        return GetCurrentLimitMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentLimitMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentLimitMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentLimitMasterRequest:
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
    ) -> Optional[UpdateCurrentLimitMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentLimitMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentLimitMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentLimitMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentLimitMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentLimitMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentLimitMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeLimitModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeLimitModelsRequest:
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
    ) -> Optional[DescribeLimitModelsRequest]:
        if data is None:
            return None
        return DescribeLimitModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetLimitModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    limit_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetLimitModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_limit_name(self, limit_name: str) -> GetLimitModelRequest:
        self.limit_name = limit_name
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
    ) -> Optional[GetLimitModelRequest]:
        if data is None:
            return None
        return GetLimitModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_limit_name(data.get('limitName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "limitName": self.limit_name,
        }