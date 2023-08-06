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

from inventory.model import *


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


class DescribeInventoryModelMastersResult(core.Gs2Result):
    items: List[InventoryModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[InventoryModelMaster]) -> DescribeInventoryModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeInventoryModelMastersResult:
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
    ) -> Optional[DescribeInventoryModelMastersResult]:
        if data is None:
            return None
        return DescribeInventoryModelMastersResult()\
            .with_items([
                InventoryModelMaster.from_dict(data.get('items')[i])
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


class CreateInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> CreateInventoryModelMasterResult:
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
    ) -> Optional[CreateInventoryModelMasterResult]:
        if data is None:
            return None
        return CreateInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> GetInventoryModelMasterResult:
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
    ) -> Optional[GetInventoryModelMasterResult]:
        if data is None:
            return None
        return GetInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> UpdateInventoryModelMasterResult:
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
    ) -> Optional[UpdateInventoryModelMasterResult]:
        if data is None:
            return None
        return UpdateInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> DeleteInventoryModelMasterResult:
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
    ) -> Optional[DeleteInventoryModelMasterResult]:
        if data is None:
            return None
        return DeleteInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeInventoryModelsResult(core.Gs2Result):
    items: List[InventoryModel] = None

    def with_items(self, items: List[InventoryModel]) -> DescribeInventoryModelsResult:
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
    ) -> Optional[DescribeInventoryModelsResult]:
        if data is None:
            return None
        return DescribeInventoryModelsResult()\
            .with_items([
                InventoryModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
        }


class GetInventoryModelResult(core.Gs2Result):
    item: InventoryModel = None

    def with_item(self, item: InventoryModel) -> GetInventoryModelResult:
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
    ) -> Optional[GetInventoryModelResult]:
        if data is None:
            return None
        return GetInventoryModelResult()\
            .with_item(InventoryModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeItemModelMastersResult(core.Gs2Result):
    items: List[ItemModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[ItemModelMaster]) -> DescribeItemModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeItemModelMastersResult:
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
    ) -> Optional[DescribeItemModelMastersResult]:
        if data is None:
            return None
        return DescribeItemModelMastersResult()\
            .with_items([
                ItemModelMaster.from_dict(data.get('items')[i])
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


class CreateItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> CreateItemModelMasterResult:
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
    ) -> Optional[CreateItemModelMasterResult]:
        if data is None:
            return None
        return CreateItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> GetItemModelMasterResult:
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
    ) -> Optional[GetItemModelMasterResult]:
        if data is None:
            return None
        return GetItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> UpdateItemModelMasterResult:
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
    ) -> Optional[UpdateItemModelMasterResult]:
        if data is None:
            return None
        return UpdateItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> DeleteItemModelMasterResult:
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
    ) -> Optional[DeleteItemModelMasterResult]:
        if data is None:
            return None
        return DeleteItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeItemModelsResult(core.Gs2Result):
    items: List[ItemModel] = None

    def with_items(self, items: List[ItemModel]) -> DescribeItemModelsResult:
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
    ) -> Optional[DescribeItemModelsResult]:
        if data is None:
            return None
        return DescribeItemModelsResult()\
            .with_items([
                ItemModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
        }


class GetItemModelResult(core.Gs2Result):
    item: ItemModel = None

    def with_item(self, item: ItemModel) -> GetItemModelResult:
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
    ) -> Optional[GetItemModelResult]:
        if data is None:
            return None
        return GetItemModelResult()\
            .with_item(ItemModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> ExportMasterResult:
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
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentItemModelMasterResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> GetCurrentItemModelMasterResult:
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
    ) -> Optional[GetCurrentItemModelMasterResult]:
        if data is None:
            return None
        return GetCurrentItemModelMasterResult()\
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentItemModelMasterResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> UpdateCurrentItemModelMasterResult:
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
    ) -> Optional[UpdateCurrentItemModelMasterResult]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterResult()\
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentItemModelMasterFromGitHubResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> UpdateCurrentItemModelMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentItemModelMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterFromGitHubResult()\
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeInventoriesResult(core.Gs2Result):
    items: List[Inventory] = None
    next_page_token: str = None

    def with_items(self, items: List[Inventory]) -> DescribeInventoriesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeInventoriesResult:
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
    ) -> Optional[DescribeInventoriesResult]:
        if data is None:
            return None
        return DescribeInventoriesResult()\
            .with_items([
                Inventory.from_dict(data.get('items')[i])
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


class DescribeInventoriesByUserIdResult(core.Gs2Result):
    items: List[Inventory] = None
    next_page_token: str = None

    def with_items(self, items: List[Inventory]) -> DescribeInventoriesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeInventoriesByUserIdResult:
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
    ) -> Optional[DescribeInventoriesByUserIdResult]:
        if data is None:
            return None
        return DescribeInventoriesByUserIdResult()\
            .with_items([
                Inventory.from_dict(data.get('items')[i])
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


class GetInventoryResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> GetInventoryResult:
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
    ) -> Optional[GetInventoryResult]:
        if data is None:
            return None
        return GetInventoryResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetInventoryByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> GetInventoryByUserIdResult:
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
    ) -> Optional[GetInventoryByUserIdResult]:
        if data is None:
            return None
        return GetInventoryByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AddCapacityByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> AddCapacityByUserIdResult:
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
    ) -> Optional[AddCapacityByUserIdResult]:
        if data is None:
            return None
        return AddCapacityByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SetCapacityByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> SetCapacityByUserIdResult:
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
    ) -> Optional[SetCapacityByUserIdResult]:
        if data is None:
            return None
        return SetCapacityByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteInventoryByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> DeleteInventoryByUserIdResult:
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
    ) -> Optional[DeleteInventoryByUserIdResult]:
        if data is None:
            return None
        return DeleteInventoryByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AddCapacityByStampSheetResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> AddCapacityByStampSheetResult:
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
    ) -> Optional[AddCapacityByStampSheetResult]:
        if data is None:
            return None
        return AddCapacityByStampSheetResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SetCapacityByStampSheetResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> SetCapacityByStampSheetResult:
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
    ) -> Optional[SetCapacityByStampSheetResult]:
        if data is None:
            return None
        return SetCapacityByStampSheetResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeItemSetsResult(core.Gs2Result):
    items: List[ItemSet] = None
    next_page_token: str = None

    def with_items(self, items: List[ItemSet]) -> DescribeItemSetsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeItemSetsResult:
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
    ) -> Optional[DescribeItemSetsResult]:
        if data is None:
            return None
        return DescribeItemSetsResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
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


class DescribeItemSetsByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    next_page_token: str = None

    def with_items(self, items: List[ItemSet]) -> DescribeItemSetsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeItemSetsByUserIdResult:
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
    ) -> Optional[DescribeItemSetsByUserIdResult]:
        if data is None:
            return None
        return DescribeItemSetsByUserIdResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
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


class GetItemSetResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> GetItemSetResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemSetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemSetResult:
        self.inventory = inventory
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
    ) -> Optional[GetItemSetResult]:
        if data is None:
            return None
        return GetItemSetResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> GetItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemSetByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[GetItemSetByUserIdResult]:
        if data is None:
            return None
        return GetItemSetByUserIdResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetItemWithSignatureResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    body: str = None
    signature: str = None

    def with_items(self, items: List[ItemSet]) -> GetItemWithSignatureResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemWithSignatureResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemWithSignatureResult:
        self.inventory = inventory
        return self

    def with_body(self, body: str) -> GetItemWithSignatureResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetItemWithSignatureResult:
        self.signature = signature
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
    ) -> Optional[GetItemWithSignatureResult]:
        if data is None:
            return None
        return GetItemWithSignatureResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "body": self.body,
            "signature": self.signature,
        }


class GetItemWithSignatureByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    body: str = None
    signature: str = None

    def with_items(self, items: List[ItemSet]) -> GetItemWithSignatureByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemWithSignatureByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemWithSignatureByUserIdResult:
        self.inventory = inventory
        return self

    def with_body(self, body: str) -> GetItemWithSignatureByUserIdResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetItemWithSignatureByUserIdResult:
        self.signature = signature
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
    ) -> Optional[GetItemWithSignatureByUserIdResult]:
        if data is None:
            return None
        return GetItemWithSignatureByUserIdResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "body": self.body,
            "signature": self.signature,
        }


class AcquireItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    overflow_count: int = None

    def with_items(self, items: List[ItemSet]) -> AcquireItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> AcquireItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AcquireItemSetByUserIdResult:
        self.inventory = inventory
        return self

    def with_overflow_count(self, overflow_count: int) -> AcquireItemSetByUserIdResult:
        self.overflow_count = overflow_count
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
    ) -> Optional[AcquireItemSetByUserIdResult]:
        if data is None:
            return None
        return AcquireItemSetByUserIdResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_overflow_count(data.get('overflowCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "overflowCount": self.overflow_count,
        }


class ConsumeItemSetResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> ConsumeItemSetResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> ConsumeItemSetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> ConsumeItemSetResult:
        self.inventory = inventory
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
    ) -> Optional[ConsumeItemSetResult]:
        if data is None:
            return None
        return ConsumeItemSetResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class ConsumeItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> ConsumeItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> ConsumeItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> ConsumeItemSetByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[ConsumeItemSetByUserIdResult]:
        if data is None:
            return None
        return ConsumeItemSetByUserIdResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> DeleteItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteItemSetByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[DeleteItemSetByUserIdResult]:
        if data is None:
            return None
        return DeleteItemSetByUserIdResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class AcquireItemSetByStampSheetResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    overflow_count: int = None

    def with_items(self, items: List[ItemSet]) -> AcquireItemSetByStampSheetResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> AcquireItemSetByStampSheetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AcquireItemSetByStampSheetResult:
        self.inventory = inventory
        return self

    def with_overflow_count(self, overflow_count: int) -> AcquireItemSetByStampSheetResult:
        self.overflow_count = overflow_count
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
    ) -> Optional[AcquireItemSetByStampSheetResult]:
        if data is None:
            return None
        return AcquireItemSetByStampSheetResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_overflow_count(data.get('overflowCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "overflowCount": self.overflow_count,
        }


class ConsumeItemSetByStampTaskResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    new_context_stack: str = None

    def with_items(self, items: List[ItemSet]) -> ConsumeItemSetByStampTaskResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> ConsumeItemSetByStampTaskResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> ConsumeItemSetByStampTaskResult:
        self.inventory = inventory
        return self

    def with_new_context_stack(self, new_context_stack: str) -> ConsumeItemSetByStampTaskResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[ConsumeItemSetByStampTaskResult]:
        if data is None:
            return None
        return ConsumeItemSetByStampTaskResult()\
            .with_items([
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeReferenceOfResult(core.Gs2Result):
    items: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[str]) -> DescribeReferenceOfResult:
        self.items = items
        return self

    def with_item_set(self, item_set: ItemSet) -> DescribeReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DescribeReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DescribeReferenceOfResult:
        self.inventory = inventory
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
    ) -> Optional[DescribeReferenceOfResult]:
        if data is None:
            return None
        return DescribeReferenceOfResult()\
            .with_items([
                data.get('items')[i]
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i]
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DescribeReferenceOfByUserIdResult(core.Gs2Result):
    items: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[str]) -> DescribeReferenceOfByUserIdResult:
        self.items = items
        return self

    def with_item_set(self, item_set: ItemSet) -> DescribeReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DescribeReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DescribeReferenceOfByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[DescribeReferenceOfByUserIdResult]:
        if data is None:
            return None
        return DescribeReferenceOfByUserIdResult()\
            .with_items([
                data.get('items')[i]
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i]
                for i in range(len(self.items) if self.items else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetReferenceOfResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> GetReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> GetReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> GetReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetReferenceOfResult:
        self.inventory = inventory
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
    ) -> Optional[GetReferenceOfResult]:
        if data is None:
            return None
        return GetReferenceOfResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetReferenceOfByUserIdResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> GetReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> GetReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> GetReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetReferenceOfByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[GetReferenceOfByUserIdResult]:
        if data is None:
            return None
        return GetReferenceOfByUserIdResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class VerifyReferenceOfResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> VerifyReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> VerifyReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> VerifyReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> VerifyReferenceOfResult:
        self.inventory = inventory
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
    ) -> Optional[VerifyReferenceOfResult]:
        if data is None:
            return None
        return VerifyReferenceOfResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class VerifyReferenceOfByUserIdResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> VerifyReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> VerifyReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> VerifyReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> VerifyReferenceOfByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[VerifyReferenceOfByUserIdResult]:
        if data is None:
            return None
        return VerifyReferenceOfByUserIdResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class AddReferenceOfResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> AddReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> AddReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> AddReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AddReferenceOfResult:
        self.inventory = inventory
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
    ) -> Optional[AddReferenceOfResult]:
        if data is None:
            return None
        return AddReferenceOfResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class AddReferenceOfByUserIdResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> AddReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> AddReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> AddReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AddReferenceOfByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[AddReferenceOfByUserIdResult]:
        if data is None:
            return None
        return AddReferenceOfByUserIdResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteReferenceOfResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> DeleteReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> DeleteReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteReferenceOfResult:
        self.inventory = inventory
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
    ) -> Optional[DeleteReferenceOfResult]:
        if data is None:
            return None
        return DeleteReferenceOfResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteReferenceOfByUserIdResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> DeleteReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> DeleteReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteReferenceOfByUserIdResult:
        self.inventory = inventory
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
    ) -> Optional[DeleteReferenceOfByUserIdResult]:
        if data is None:
            return None
        return DeleteReferenceOfByUserIdResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class AddReferenceOfItemSetByStampSheetResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> AddReferenceOfItemSetByStampSheetResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> AddReferenceOfItemSetByStampSheetResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> AddReferenceOfItemSetByStampSheetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AddReferenceOfItemSetByStampSheetResult:
        self.inventory = inventory
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
    ) -> Optional[AddReferenceOfItemSetByStampSheetResult]:
        if data is None:
            return None
        return AddReferenceOfItemSetByStampSheetResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteReferenceOfItemSetByStampSheetResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: List[str]) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.inventory = inventory
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
    ) -> Optional[DeleteReferenceOfItemSetByStampSheetResult]:
        if data is None:
            return None
        return DeleteReferenceOfItemSetByStampSheetResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class VerifyReferenceOfByStampTaskResult(core.Gs2Result):
    item: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None
    new_context_stack: str = None

    def with_item(self, item: List[str]) -> VerifyReferenceOfByStampTaskResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> VerifyReferenceOfByStampTaskResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> VerifyReferenceOfByStampTaskResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> VerifyReferenceOfByStampTaskResult:
        self.inventory = inventory
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyReferenceOfByStampTaskResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[VerifyReferenceOfByStampTaskResult]:
        if data is None:
            return None
        return VerifyReferenceOfByStampTaskResult()\
            .with_item([
                data.get('item')[i]
                for i in range(len(data.get('item')) if data.get('item') else 0)
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": [
                self.item[i]
                for i in range(len(self.item) if self.item else 0)
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "newContextStack": self.new_context_stack,
        }