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


class ExecuteStampTaskLogCount(core.Gs2Model):
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    count: int = None

    def with_service(self, service: str) -> ExecuteStampTaskLogCount:
        self.service = service
        return self

    def with_method(self, method: str) -> ExecuteStampTaskLogCount:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> ExecuteStampTaskLogCount:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> ExecuteStampTaskLogCount:
        self.action = action
        return self

    def with_count(self, count: int) -> ExecuteStampTaskLogCount:
        self.count = count
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
    ) -> Optional[ExecuteStampTaskLogCount]:
        if data is None:
            return None
        return ExecuteStampTaskLogCount()\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "count": self.count,
        }


class ExecuteStampTaskLog(core.Gs2Model):
    timestamp: int = None
    task_id: str = None
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    args: str = None

    def with_timestamp(self, timestamp: int) -> ExecuteStampTaskLog:
        self.timestamp = timestamp
        return self

    def with_task_id(self, task_id: str) -> ExecuteStampTaskLog:
        self.task_id = task_id
        return self

    def with_service(self, service: str) -> ExecuteStampTaskLog:
        self.service = service
        return self

    def with_method(self, method: str) -> ExecuteStampTaskLog:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> ExecuteStampTaskLog:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> ExecuteStampTaskLog:
        self.action = action
        return self

    def with_args(self, args: str) -> ExecuteStampTaskLog:
        self.args = args
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
    ) -> Optional[ExecuteStampTaskLog]:
        if data is None:
            return None
        return ExecuteStampTaskLog()\
            .with_timestamp(data.get('timestamp'))\
            .with_task_id(data.get('taskId'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_args(data.get('args'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "taskId": self.task_id,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "args": self.args,
        }


class ExecuteStampSheetLogCount(core.Gs2Model):
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    count: int = None

    def with_service(self, service: str) -> ExecuteStampSheetLogCount:
        self.service = service
        return self

    def with_method(self, method: str) -> ExecuteStampSheetLogCount:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> ExecuteStampSheetLogCount:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> ExecuteStampSheetLogCount:
        self.action = action
        return self

    def with_count(self, count: int) -> ExecuteStampSheetLogCount:
        self.count = count
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
    ) -> Optional[ExecuteStampSheetLogCount]:
        if data is None:
            return None
        return ExecuteStampSheetLogCount()\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "count": self.count,
        }


class ExecuteStampSheetLog(core.Gs2Model):
    timestamp: int = None
    transaction_id: str = None
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    args: str = None

    def with_timestamp(self, timestamp: int) -> ExecuteStampSheetLog:
        self.timestamp = timestamp
        return self

    def with_transaction_id(self, transaction_id: str) -> ExecuteStampSheetLog:
        self.transaction_id = transaction_id
        return self

    def with_service(self, service: str) -> ExecuteStampSheetLog:
        self.service = service
        return self

    def with_method(self, method: str) -> ExecuteStampSheetLog:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> ExecuteStampSheetLog:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> ExecuteStampSheetLog:
        self.action = action
        return self

    def with_args(self, args: str) -> ExecuteStampSheetLog:
        self.args = args
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
    ) -> Optional[ExecuteStampSheetLog]:
        if data is None:
            return None
        return ExecuteStampSheetLog()\
            .with_timestamp(data.get('timestamp'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_args(data.get('args'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "transactionId": self.transaction_id,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "args": self.args,
        }


class IssueStampSheetLogCount(core.Gs2Model):
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    count: int = None

    def with_service(self, service: str) -> IssueStampSheetLogCount:
        self.service = service
        return self

    def with_method(self, method: str) -> IssueStampSheetLogCount:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> IssueStampSheetLogCount:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> IssueStampSheetLogCount:
        self.action = action
        return self

    def with_count(self, count: int) -> IssueStampSheetLogCount:
        self.count = count
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
    ) -> Optional[IssueStampSheetLogCount]:
        if data is None:
            return None
        return IssueStampSheetLogCount()\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "count": self.count,
        }


class IssueStampSheetLog(core.Gs2Model):
    timestamp: int = None
    transaction_id: str = None
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    args: str = None
    tasks: List[str] = None

    def with_timestamp(self, timestamp: int) -> IssueStampSheetLog:
        self.timestamp = timestamp
        return self

    def with_transaction_id(self, transaction_id: str) -> IssueStampSheetLog:
        self.transaction_id = transaction_id
        return self

    def with_service(self, service: str) -> IssueStampSheetLog:
        self.service = service
        return self

    def with_method(self, method: str) -> IssueStampSheetLog:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> IssueStampSheetLog:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> IssueStampSheetLog:
        self.action = action
        return self

    def with_args(self, args: str) -> IssueStampSheetLog:
        self.args = args
        return self

    def with_tasks(self, tasks: List[str]) -> IssueStampSheetLog:
        self.tasks = tasks
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
    ) -> Optional[IssueStampSheetLog]:
        if data is None:
            return None
        return IssueStampSheetLog()\
            .with_timestamp(data.get('timestamp'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_args(data.get('args'))\
            .with_tasks([
                data.get('tasks')[i]
                for i in range(len(data.get('tasks')) if data.get('tasks') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "transactionId": self.transaction_id,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "args": self.args,
            "tasks": [
                self.tasks[i]
                for i in range(len(self.tasks) if self.tasks else 0)
            ],
        }


class AccessLogCount(core.Gs2Model):
    service: str = None
    method: str = None
    user_id: str = None
    count: int = None

    def with_service(self, service: str) -> AccessLogCount:
        self.service = service
        return self

    def with_method(self, method: str) -> AccessLogCount:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> AccessLogCount:
        self.user_id = user_id
        return self

    def with_count(self, count: int) -> AccessLogCount:
        self.count = count
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
    ) -> Optional[AccessLogCount]:
        if data is None:
            return None
        return AccessLogCount()\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "count": self.count,
        }


class AccessLog(core.Gs2Model):
    timestamp: int = None
    request_id: str = None
    service: str = None
    method: str = None
    user_id: str = None
    request: str = None
    result: str = None

    def with_timestamp(self, timestamp: int) -> AccessLog:
        self.timestamp = timestamp
        return self

    def with_request_id(self, request_id: str) -> AccessLog:
        self.request_id = request_id
        return self

    def with_service(self, service: str) -> AccessLog:
        self.service = service
        return self

    def with_method(self, method: str) -> AccessLog:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> AccessLog:
        self.user_id = user_id
        return self

    def with_request(self, request: str) -> AccessLog:
        self.request = request
        return self

    def with_result(self, result: str) -> AccessLog:
        self.result = result
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
    ) -> Optional[AccessLog]:
        if data is None:
            return None
        return AccessLog()\
            .with_timestamp(data.get('timestamp'))\
            .with_request_id(data.get('requestId'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_request(data.get('request'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "requestId": self.request_id,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "request": self.request,
            "result": self.result,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    type: str = None
    gcp_credential_json: str = None
    big_query_dataset_name: str = None
    log_expire_days: int = None
    aws_region: str = None
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    firehose_stream_name: str = None
    status: str = None
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

    def with_type(self, type: str) -> Namespace:
        self.type = type
        return self

    def with_gcp_credential_json(self, gcp_credential_json: str) -> Namespace:
        self.gcp_credential_json = gcp_credential_json
        return self

    def with_big_query_dataset_name(self, big_query_dataset_name: str) -> Namespace:
        self.big_query_dataset_name = big_query_dataset_name
        return self

    def with_log_expire_days(self, log_expire_days: int) -> Namespace:
        self.log_expire_days = log_expire_days
        return self

    def with_aws_region(self, aws_region: str) -> Namespace:
        self.aws_region = aws_region
        return self

    def with_aws_access_key_id(self, aws_access_key_id: str) -> Namespace:
        self.aws_access_key_id = aws_access_key_id
        return self

    def with_aws_secret_access_key(self, aws_secret_access_key: str) -> Namespace:
        self.aws_secret_access_key = aws_secret_access_key
        return self

    def with_firehose_stream_name(self, firehose_stream_name: str) -> Namespace:
        self.firehose_stream_name = firehose_stream_name
        return self

    def with_status(self, status: str) -> Namespace:
        self.status = status
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
        return 'grn:gs2:{region}:{ownerId}:log:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):log:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):log:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):log:(?P<namespaceName>.+)', grn)
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
            .with_type(data.get('type'))\
            .with_gcp_credential_json(data.get('gcpCredentialJson'))\
            .with_big_query_dataset_name(data.get('bigQueryDatasetName'))\
            .with_log_expire_days(data.get('logExpireDays'))\
            .with_aws_region(data.get('awsRegion'))\
            .with_aws_access_key_id(data.get('awsAccessKeyId'))\
            .with_aws_secret_access_key(data.get('awsSecretAccessKey'))\
            .with_firehose_stream_name(data.get('firehoseStreamName'))\
            .with_status(data.get('status'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "gcpCredentialJson": self.gcp_credential_json,
            "bigQueryDatasetName": self.big_query_dataset_name,
            "logExpireDays": self.log_expire_days,
            "awsRegion": self.aws_region,
            "awsAccessKeyId": self.aws_access_key_id,
            "awsSecretAccessKey": self.aws_secret_access_key,
            "firehoseStreamName": self.firehose_stream_name,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }