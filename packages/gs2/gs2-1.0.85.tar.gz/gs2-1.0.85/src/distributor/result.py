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


class DescribeNamespacesResult(core.Gs2Result):
    items: List[Namespace] = None
    next_page_token: str = None

    def with_items(self, items: List[Namespace]) -> DescribeNamespacesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeNamespacesResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeNamespacesResult]:
        if data is None:
            return None
        return DescribeNamespacesResult()\
            .with_items([
                Namespace.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> CreateNamespaceResult:
        self.item = item
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
    ) -> Optional[CreateNamespaceResult]:
        if data is None:
            return None
        return CreateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetNamespaceStatusResult(core.Gs2Result):
    status: str = None

    def with_status(self, status: str) -> GetNamespaceStatusResult:
        self.status = status
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
    ) -> Optional[GetNamespaceStatusResult]:
        if data is None:
            return None
        return GetNamespaceStatusResult()\
            .with_status(data.get('status'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
        }


class GetNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> GetNamespaceResult:
        self.item = item
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
    ) -> Optional[GetNamespaceResult]:
        if data is None:
            return None
        return GetNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> UpdateNamespaceResult:
        self.item = item
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
    ) -> Optional[UpdateNamespaceResult]:
        if data is None:
            return None
        return UpdateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> DeleteNamespaceResult:
        self.item = item
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
    ) -> Optional[DeleteNamespaceResult]:
        if data is None:
            return None
        return DeleteNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeDistributorModelMastersResult(core.Gs2Result):
    items: List[DistributorModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[DistributorModelMaster]) -> DescribeDistributorModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeDistributorModelMastersResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeDistributorModelMastersResult]:
        if data is None:
            return None
        return DescribeDistributorModelMastersResult()\
            .with_items([
                DistributorModelMaster.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> CreateDistributorModelMasterResult:
        self.item = item
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
    ) -> Optional[CreateDistributorModelMasterResult]:
        if data is None:
            return None
        return CreateDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> GetDistributorModelMasterResult:
        self.item = item
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
    ) -> Optional[GetDistributorModelMasterResult]:
        if data is None:
            return None
        return GetDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> UpdateDistributorModelMasterResult:
        self.item = item
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
    ) -> Optional[UpdateDistributorModelMasterResult]:
        if data is None:
            return None
        return UpdateDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> DeleteDistributorModelMasterResult:
        self.item = item
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
    ) -> Optional[DeleteDistributorModelMasterResult]:
        if data is None:
            return None
        return DeleteDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeDistributorModelsResult(core.Gs2Result):
    items: List[DistributorModel] = None

    def with_items(self, items: List[DistributorModel]) -> DescribeDistributorModelsResult:
        self.items = items
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
    ) -> Optional[DescribeDistributorModelsResult]:
        if data is None:
            return None
        return DescribeDistributorModelsResult()\
            .with_items([
                DistributorModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
        }


class GetDistributorModelResult(core.Gs2Result):
    item: DistributorModel = None

    def with_item(self, item: DistributorModel) -> GetDistributorModelResult:
        self.item = item
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
    ) -> Optional[GetDistributorModelResult]:
        if data is None:
            return None
        return GetDistributorModelResult()\
            .with_item(DistributorModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> ExportMasterResult:
        self.item = item
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
    ) -> Optional[ExportMasterResult]:
        if data is None:
            return None
        return ExportMasterResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentDistributorMasterResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> GetCurrentDistributorMasterResult:
        self.item = item
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
    ) -> Optional[GetCurrentDistributorMasterResult]:
        if data is None:
            return None
        return GetCurrentDistributorMasterResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentDistributorMasterResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> UpdateCurrentDistributorMasterResult:
        self.item = item
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
    ) -> Optional[UpdateCurrentDistributorMasterResult]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentDistributorMasterFromGitHubResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> UpdateCurrentDistributorMasterFromGitHubResult:
        self.item = item
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
    ) -> Optional[UpdateCurrentDistributorMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterFromGitHubResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DistributeResult(core.Gs2Result):
    distribute_resource: DistributeResource = None
    inbox_namespace_id: str = None
    result: str = None

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeResult:
        self.distribute_resource = distribute_resource
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> DistributeResult:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_result(self, result: str) -> DistributeResult:
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
    ) -> Optional[DistributeResult]:
        if data is None:
            return None
        return DistributeResult()\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
            "inboxNamespaceId": self.inbox_namespace_id,
            "result": self.result,
        }


class DistributeWithoutOverflowProcessResult(core.Gs2Result):
    distribute_resource: DistributeResource = None
    result: str = None

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeWithoutOverflowProcessResult:
        self.distribute_resource = distribute_resource
        return self

    def with_result(self, result: str) -> DistributeWithoutOverflowProcessResult:
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
    ) -> Optional[DistributeWithoutOverflowProcessResult]:
        if data is None:
            return None
        return DistributeWithoutOverflowProcessResult()\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
            "result": self.result,
        }


class RunStampTaskResult(core.Gs2Result):
    context_stack: str = None
    result: str = None

    def with_context_stack(self, context_stack: str) -> RunStampTaskResult:
        self.context_stack = context_stack
        return self

    def with_result(self, result: str) -> RunStampTaskResult:
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
    ) -> Optional[RunStampTaskResult]:
        if data is None:
            return None
        return RunStampTaskResult()\
            .with_context_stack(data.get('contextStack'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contextStack": self.context_stack,
            "result": self.result,
        }


class RunStampSheetResult(core.Gs2Result):
    result: str = None

    def with_result(self, result: str) -> RunStampSheetResult:
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
    ) -> Optional[RunStampSheetResult]:
        if data is None:
            return None
        return RunStampSheetResult()\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result,
        }


class RunStampSheetExpressResult(core.Gs2Result):
    task_results: List[str] = None
    sheet_result: str = None

    def with_task_results(self, task_results: List[str]) -> RunStampSheetExpressResult:
        self.task_results = task_results
        return self

    def with_sheet_result(self, sheet_result: str) -> RunStampSheetExpressResult:
        self.sheet_result = sheet_result
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
    ) -> Optional[RunStampSheetExpressResult]:
        if data is None:
            return None
        return RunStampSheetExpressResult()\
            .with_task_results([
                data.get('taskResults')[i]
                for i in range(len(data.get('taskResults')) if data.get('taskResults') else 0)
            ])\
            .with_sheet_result(data.get('sheetResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "taskResults": [
                self.task_results[i]
                for i in range(len(self.task_results) if self.task_results else 0)
            ],
            "sheetResult": self.sheet_result,
        }


class RunStampTaskWithoutNamespaceResult(core.Gs2Result):
    context_stack: str = None
    result: str = None

    def with_context_stack(self, context_stack: str) -> RunStampTaskWithoutNamespaceResult:
        self.context_stack = context_stack
        return self

    def with_result(self, result: str) -> RunStampTaskWithoutNamespaceResult:
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
    ) -> Optional[RunStampTaskWithoutNamespaceResult]:
        if data is None:
            return None
        return RunStampTaskWithoutNamespaceResult()\
            .with_context_stack(data.get('contextStack'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contextStack": self.context_stack,
            "result": self.result,
        }


class RunStampSheetWithoutNamespaceResult(core.Gs2Result):
    result: str = None

    def with_result(self, result: str) -> RunStampSheetWithoutNamespaceResult:
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
    ) -> Optional[RunStampSheetWithoutNamespaceResult]:
        if data is None:
            return None
        return RunStampSheetWithoutNamespaceResult()\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result,
        }


class RunStampSheetExpressWithoutNamespaceResult(core.Gs2Result):
    task_results: List[str] = None
    sheet_result: str = None

    def with_task_results(self, task_results: List[str]) -> RunStampSheetExpressWithoutNamespaceResult:
        self.task_results = task_results
        return self

    def with_sheet_result(self, sheet_result: str) -> RunStampSheetExpressWithoutNamespaceResult:
        self.sheet_result = sheet_result
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
    ) -> Optional[RunStampSheetExpressWithoutNamespaceResult]:
        if data is None:
            return None
        return RunStampSheetExpressWithoutNamespaceResult()\
            .with_task_results([
                data.get('taskResults')[i]
                for i in range(len(data.get('taskResults')) if data.get('taskResults') else 0)
            ])\
            .with_sheet_result(data.get('sheetResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "taskResults": [
                self.task_results[i]
                for i in range(len(self.task_results) if self.task_results else 0)
            ],
            "sheetResult": self.sheet_result,
        }


class GetStampSheetResultResult(core.Gs2Result):
    item: StampSheetResult = None

    def with_item(self, item: StampSheetResult) -> GetStampSheetResultResult:
        self.item = item
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
    ) -> Optional[GetStampSheetResultResult]:
        if data is None:
            return None
        return GetStampSheetResultResult()\
            .with_item(StampSheetResult.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetStampSheetResultByUserIdResult(core.Gs2Result):
    item: StampSheetResult = None

    def with_item(self, item: StampSheetResult) -> GetStampSheetResultByUserIdResult:
        self.item = item
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
    ) -> Optional[GetStampSheetResultByUserIdResult]:
        if data is None:
            return None
        return GetStampSheetResultByUserIdResult()\
            .with_item(StampSheetResult.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }