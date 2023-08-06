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
    acquire_script: ScriptSetting = None
    overflow_script: ScriptSetting = None
    consume_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_acquire_script(self, acquire_script: ScriptSetting) -> CreateNamespaceRequest:
        self.acquire_script = acquire_script
        return self

    def with_overflow_script(self, overflow_script: ScriptSetting) -> CreateNamespaceRequest:
        self.overflow_script = overflow_script
        return self

    def with_consume_script(self, consume_script: ScriptSetting) -> CreateNamespaceRequest:
        self.consume_script = consume_script
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
            .with_acquire_script(ScriptSetting.from_dict(data.get('acquireScript')))\
            .with_overflow_script(ScriptSetting.from_dict(data.get('overflowScript')))\
            .with_consume_script(ScriptSetting.from_dict(data.get('consumeScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "acquireScript": self.acquire_script.to_dict() if self.acquire_script else None,
            "overflowScript": self.overflow_script.to_dict() if self.overflow_script else None,
            "consumeScript": self.consume_script.to_dict() if self.consume_script else None,
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
    acquire_script: ScriptSetting = None
    overflow_script: ScriptSetting = None
    consume_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_acquire_script(self, acquire_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.acquire_script = acquire_script
        return self

    def with_overflow_script(self, overflow_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.overflow_script = overflow_script
        return self

    def with_consume_script(self, consume_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.consume_script = consume_script
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
            .with_acquire_script(ScriptSetting.from_dict(data.get('acquireScript')))\
            .with_overflow_script(ScriptSetting.from_dict(data.get('overflowScript')))\
            .with_consume_script(ScriptSetting.from_dict(data.get('consumeScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "acquireScript": self.acquire_script.to_dict() if self.acquire_script else None,
            "overflowScript": self.overflow_script.to_dict() if self.overflow_script else None,
            "consumeScript": self.consume_script.to_dict() if self.consume_script else None,
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


class DescribeInventoryModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoryModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeInventoryModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeInventoryModelMastersRequest:
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
    ) -> Optional[DescribeInventoryModelMastersRequest]:
        if data is None:
            return None
        return DescribeInventoryModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    initial_capacity: int = None
    max_capacity: int = None
    protect_referenced_item: bool = None

    def with_namespace_name(self, namespace_name: str) -> CreateInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateInventoryModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateInventoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_initial_capacity(self, initial_capacity: int) -> CreateInventoryModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> CreateInventoryModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_protect_referenced_item(self, protect_referenced_item: bool) -> CreateInventoryModelMasterRequest:
        self.protect_referenced_item = protect_referenced_item
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
    ) -> Optional[CreateInventoryModelMasterRequest]:
        if data is None:
            return None
        return CreateInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_protect_referenced_item(data.get('protectReferencedItem'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "initialCapacity": self.initial_capacity,
            "maxCapacity": self.max_capacity,
            "protectReferencedItem": self.protect_referenced_item,
        }


class GetInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetInventoryModelMasterRequest]:
        if data is None:
            return None
        return GetInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class UpdateInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    description: str = None
    metadata: str = None
    initial_capacity: int = None
    max_capacity: int = None
    protect_referenced_item: bool = None

    def with_namespace_name(self, namespace_name: str) -> UpdateInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateInventoryModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_description(self, description: str) -> UpdateInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateInventoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_initial_capacity(self, initial_capacity: int) -> UpdateInventoryModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> UpdateInventoryModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_protect_referenced_item(self, protect_referenced_item: bool) -> UpdateInventoryModelMasterRequest:
        self.protect_referenced_item = protect_referenced_item
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
    ) -> Optional[UpdateInventoryModelMasterRequest]:
        if data is None:
            return None
        return UpdateInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_protect_referenced_item(data.get('protectReferencedItem'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "description": self.description,
            "metadata": self.metadata,
            "initialCapacity": self.initial_capacity,
            "maxCapacity": self.max_capacity,
            "protectReferencedItem": self.protect_referenced_item,
        }


class DeleteInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DeleteInventoryModelMasterRequest]:
        if data is None:
            return None
        return DeleteInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeInventoryModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoryModelsRequest:
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
    ) -> Optional[DescribeInventoryModelsRequest]:
        if data is None:
            return None
        return DescribeInventoryModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetInventoryModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryModelRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetInventoryModelRequest]:
        if data is None:
            return None
        return GetInventoryModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeItemModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemModelMastersRequest:
        self.inventory_name = inventory_name
        return self

    def with_page_token(self, page_token: str) -> DescribeItemModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeItemModelMastersRequest:
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
    ) -> Optional[DescribeItemModelMastersRequest]:
        if data is None:
            return None
        return DescribeItemModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    stacking_limit: int = None
    allow_multiple_stacks: bool = None
    sort_value: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> CreateItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_name(self, name: str) -> CreateItemModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateItemModelMasterRequest:
        self.metadata = metadata
        return self

    def with_stacking_limit(self, stacking_limit: int) -> CreateItemModelMasterRequest:
        self.stacking_limit = stacking_limit
        return self

    def with_allow_multiple_stacks(self, allow_multiple_stacks: bool) -> CreateItemModelMasterRequest:
        self.allow_multiple_stacks = allow_multiple_stacks
        return self

    def with_sort_value(self, sort_value: int) -> CreateItemModelMasterRequest:
        self.sort_value = sort_value
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
    ) -> Optional[CreateItemModelMasterRequest]:
        if data is None:
            return None
        return CreateItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_stacking_limit(data.get('stackingLimit'))\
            .with_allow_multiple_stacks(data.get('allowMultipleStacks'))\
            .with_sort_value(data.get('sortValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "stackingLimit": self.stacking_limit,
            "allowMultipleStacks": self.allow_multiple_stacks,
            "sortValue": self.sort_value,
        }


class GetItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[GetItemModelMasterRequest]:
        if data is None:
            return None
        return GetItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class UpdateItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None
    description: str = None
    metadata: str = None
    stacking_limit: int = None
    allow_multiple_stacks: bool = None
    sort_value: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> UpdateItemModelMasterRequest:
        self.item_name = item_name
        return self

    def with_description(self, description: str) -> UpdateItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateItemModelMasterRequest:
        self.metadata = metadata
        return self

    def with_stacking_limit(self, stacking_limit: int) -> UpdateItemModelMasterRequest:
        self.stacking_limit = stacking_limit
        return self

    def with_allow_multiple_stacks(self, allow_multiple_stacks: bool) -> UpdateItemModelMasterRequest:
        self.allow_multiple_stacks = allow_multiple_stacks
        return self

    def with_sort_value(self, sort_value: int) -> UpdateItemModelMasterRequest:
        self.sort_value = sort_value
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
    ) -> Optional[UpdateItemModelMasterRequest]:
        if data is None:
            return None
        return UpdateItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_stacking_limit(data.get('stackingLimit'))\
            .with_allow_multiple_stacks(data.get('allowMultipleStacks'))\
            .with_sort_value(data.get('sortValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "description": self.description,
            "metadata": self.metadata,
            "stackingLimit": self.stacking_limit,
            "allowMultipleStacks": self.allow_multiple_stacks,
            "sortValue": self.sort_value,
        }


class DeleteItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> DeleteItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[DeleteItemModelMasterRequest]:
        if data is None:
            return None
        return DeleteItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class DescribeItemModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemModelsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemModelsRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DescribeItemModelsRequest]:
        if data is None:
            return None
        return DescribeItemModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class GetItemModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemModelRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetItemModelRequest:
        self.item_name = item_name
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
    ) -> Optional[GetItemModelRequest]:
        if data is None:
            return None
        return GetItemModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
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


class GetCurrentItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentItemModelMasterRequest:
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
    ) -> Optional[GetCurrentItemModelMasterRequest]:
        if data is None:
            return None
        return GetCurrentItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentItemModelMasterRequest:
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
    ) -> Optional[UpdateCurrentItemModelMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentItemModelMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentItemModelMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentItemModelMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentItemModelMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeInventoriesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoriesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeInventoriesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeInventoriesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeInventoriesRequest:
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
    ) -> Optional[DescribeInventoriesRequest]:
        if data is None:
            return None
        return DescribeInventoriesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeInventoriesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoriesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeInventoriesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeInventoriesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeInventoriesByUserIdRequest:
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
    ) -> Optional[DescribeInventoriesByUserIdRequest]:
        if data is None:
            return None
        return DescribeInventoriesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetInventoryRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetInventoryRequest:
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
    ) -> Optional[GetInventoryRequest]:
        if data is None:
            return None
        return GetInventoryRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
        }


class GetInventoryByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetInventoryByUserIdRequest:
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
    ) -> Optional[GetInventoryByUserIdRequest]:
        if data is None:
            return None
        return GetInventoryByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
        }


class AddCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    add_capacity_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AddCapacityByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> AddCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_add_capacity_value(self, add_capacity_value: int) -> AddCapacityByUserIdRequest:
        self.add_capacity_value = add_capacity_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddCapacityByUserIdRequest:
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
    ) -> Optional[AddCapacityByUserIdRequest]:
        if data is None:
            return None
        return AddCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_add_capacity_value(data.get('addCapacityValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "addCapacityValue": self.add_capacity_value,
        }


class SetCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    new_capacity_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> SetCapacityByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> SetCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_new_capacity_value(self, new_capacity_value: int) -> SetCapacityByUserIdRequest:
        self.new_capacity_value = new_capacity_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetCapacityByUserIdRequest:
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
    ) -> Optional[SetCapacityByUserIdRequest]:
        if data is None:
            return None
        return SetCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_new_capacity_value(data.get('newCapacityValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "newCapacityValue": self.new_capacity_value,
        }


class DeleteInventoryByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteInventoryByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteInventoryByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteInventoryByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteInventoryByUserIdRequest:
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
    ) -> Optional[DeleteInventoryByUserIdRequest]:
        if data is None:
            return None
        return DeleteInventoryByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
        }


class AddCapacityByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddCapacityByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddCapacityByStampSheetRequest:
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
    ) -> Optional[AddCapacityByStampSheetRequest]:
        if data is None:
            return None
        return AddCapacityByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetCapacityByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetCapacityByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetCapacityByStampSheetRequest:
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
    ) -> Optional[SetCapacityByStampSheetRequest]:
        if data is None:
            return None
        return SetCapacityByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DescribeItemSetsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemSetsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemSetsRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DescribeItemSetsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeItemSetsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeItemSetsRequest:
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
    ) -> Optional[DescribeItemSetsRequest]:
        if data is None:
            return None
        return DescribeItemSetsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeItemSetsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemSetsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemSetsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DescribeItemSetsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeItemSetsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeItemSetsByUserIdRequest:
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
    ) -> Optional[DescribeItemSetsByUserIdRequest]:
        if data is None:
            return None
        return DescribeItemSetsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetItemSetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemSetRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemSetRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetItemSetRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetItemSetRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemSetRequest:
        self.item_set_name = item_set_name
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
    ) -> Optional[GetItemSetRequest]:
        if data is None:
            return None
        return GetItemSetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
        }


class GetItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemSetByUserIdRequest:
        self.item_set_name = item_set_name
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
    ) -> Optional[GetItemSetByUserIdRequest]:
        if data is None:
            return None
        return GetItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
        }


class GetItemWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    key_id: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemWithSignatureRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetItemWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetItemWithSignatureRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemWithSignatureRequest:
        self.item_set_name = item_set_name
        return self

    def with_key_id(self, key_id: str) -> GetItemWithSignatureRequest:
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
    ) -> Optional[GetItemWithSignatureRequest]:
        if data is None:
            return None
        return GetItemWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "keyId": self.key_id,
        }


class GetItemWithSignatureByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetItemWithSignatureByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_key_id(self, key_id: str) -> GetItemWithSignatureByUserIdRequest:
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
    ) -> Optional[GetItemWithSignatureByUserIdRequest]:
        if data is None:
            return None
        return GetItemWithSignatureByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "keyId": self.key_id,
        }


class AcquireItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None
    user_id: str = None
    acquire_count: int = None
    expires_at: int = None
    create_new_item_set: bool = None
    item_set_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AcquireItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> AcquireItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_user_id(self, user_id: str) -> AcquireItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_acquire_count(self, acquire_count: int) -> AcquireItemSetByUserIdRequest:
        self.acquire_count = acquire_count
        return self

    def with_expires_at(self, expires_at: int) -> AcquireItemSetByUserIdRequest:
        self.expires_at = expires_at
        return self

    def with_create_new_item_set(self, create_new_item_set: bool) -> AcquireItemSetByUserIdRequest:
        self.create_new_item_set = create_new_item_set
        return self

    def with_item_set_name(self, item_set_name: str) -> AcquireItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireItemSetByUserIdRequest:
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
    ) -> Optional[AcquireItemSetByUserIdRequest]:
        if data is None:
            return None
        return AcquireItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_user_id(data.get('userId'))\
            .with_acquire_count(data.get('acquireCount'))\
            .with_expires_at(data.get('expiresAt'))\
            .with_create_new_item_set(data.get('createNewItemSet'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "userId": self.user_id,
            "acquireCount": self.acquire_count,
            "expiresAt": self.expires_at,
            "createNewItemSet": self.create_new_item_set,
            "itemSetName": self.item_set_name,
        }


class ConsumeItemSetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    consume_count: int = None
    item_set_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeItemSetRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeItemSetRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> ConsumeItemSetRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> ConsumeItemSetRequest:
        self.item_name = item_name
        return self

    def with_consume_count(self, consume_count: int) -> ConsumeItemSetRequest:
        self.consume_count = consume_count
        return self

    def with_item_set_name(self, item_set_name: str) -> ConsumeItemSetRequest:
        self.item_set_name = item_set_name
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
    ) -> Optional[ConsumeItemSetRequest]:
        if data is None:
            return None
        return ConsumeItemSetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_consume_count(data.get('consumeCount'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "consumeCount": self.consume_count,
            "itemSetName": self.item_set_name,
        }


class ConsumeItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    consume_count: int = None
    item_set_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> ConsumeItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> ConsumeItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_consume_count(self, consume_count: int) -> ConsumeItemSetByUserIdRequest:
        self.consume_count = consume_count
        return self

    def with_item_set_name(self, item_set_name: str) -> ConsumeItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeItemSetByUserIdRequest:
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
    ) -> Optional[ConsumeItemSetByUserIdRequest]:
        if data is None:
            return None
        return ConsumeItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_consume_count(data.get('consumeCount'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "consumeCount": self.consume_count,
            "itemSetName": self.item_set_name,
        }


class DeleteItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> DeleteItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DeleteItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteItemSetByUserIdRequest:
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
    ) -> Optional[DeleteItemSetByUserIdRequest]:
        if data is None:
            return None
        return DeleteItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
        }


class AcquireItemSetByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireItemSetByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireItemSetByStampSheetRequest:
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
    ) -> Optional[AcquireItemSetByStampSheetRequest]:
        if data is None:
            return None
        return AcquireItemSetByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ConsumeItemSetByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ConsumeItemSetByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ConsumeItemSetByStampTaskRequest:
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
    ) -> Optional[ConsumeItemSetByStampTaskRequest]:
        if data is None:
            return None
        return ConsumeItemSetByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DescribeReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> DescribeReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DescribeReferenceOfRequest:
        self.item_set_name = item_set_name
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
    ) -> Optional[DescribeReferenceOfRequest]:
        if data is None:
            return None
        return DescribeReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
        }


class DescribeReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DescribeReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
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
    ) -> Optional[DescribeReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return DescribeReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
        }


class GetReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> GetReferenceOfRequest:
        self.reference_of = reference_of
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
    ) -> Optional[GetReferenceOfRequest]:
        if data is None:
            return None
        return GetReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class GetReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> GetReferenceOfByUserIdRequest:
        self.reference_of = reference_of
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
    ) -> Optional[GetReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return GetReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class VerifyReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    verify_type: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> VerifyReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> VerifyReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> VerifyReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> VerifyReferenceOfRequest:
        self.reference_of = reference_of
        return self

    def with_verify_type(self, verify_type: str) -> VerifyReferenceOfRequest:
        self.verify_type = verify_type
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
    ) -> Optional[VerifyReferenceOfRequest]:
        if data is None:
            return None
        return VerifyReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))\
            .with_verify_type(data.get('verifyType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
            "verifyType": self.verify_type,
        }


class VerifyReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    verify_type: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> VerifyReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> VerifyReferenceOfByUserIdRequest:
        self.reference_of = reference_of
        return self

    def with_verify_type(self, verify_type: str) -> VerifyReferenceOfByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyReferenceOfByUserIdRequest:
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
    ) -> Optional[VerifyReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return VerifyReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))\
            .with_verify_type(data.get('verifyType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
            "verifyType": self.verify_type,
        }


class AddReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> AddReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AddReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> AddReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> AddReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> AddReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> AddReferenceOfRequest:
        self.reference_of = reference_of
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
    ) -> Optional[AddReferenceOfRequest]:
        if data is None:
            return None
        return AddReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class AddReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AddReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> AddReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> AddReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> AddReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> AddReferenceOfByUserIdRequest:
        self.reference_of = reference_of
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddReferenceOfByUserIdRequest:
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
    ) -> Optional[AddReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return AddReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class DeleteReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DeleteReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> DeleteReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DeleteReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> DeleteReferenceOfRequest:
        self.reference_of = reference_of
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
    ) -> Optional[DeleteReferenceOfRequest]:
        if data is None:
            return None
        return DeleteReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class DeleteReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> DeleteReferenceOfByUserIdRequest:
        self.reference_of = reference_of
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteReferenceOfByUserIdRequest:
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
    ) -> Optional[DeleteReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return DeleteReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class AddReferenceOfItemSetByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddReferenceOfItemSetByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddReferenceOfItemSetByStampSheetRequest:
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
    ) -> Optional[AddReferenceOfItemSetByStampSheetRequest]:
        if data is None:
            return None
        return AddReferenceOfItemSetByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DeleteReferenceOfItemSetByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DeleteReferenceOfItemSetByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DeleteReferenceOfItemSetByStampSheetRequest:
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
    ) -> Optional[DeleteReferenceOfItemSetByStampSheetRequest]:
        if data is None:
            return None
        return DeleteReferenceOfItemSetByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class VerifyReferenceOfByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyReferenceOfByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyReferenceOfByStampTaskRequest:
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
    ) -> Optional[VerifyReferenceOfByStampTaskRequest]:
        if data is None:
            return None
        return VerifyReferenceOfByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }