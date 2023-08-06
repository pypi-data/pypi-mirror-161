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

from core import Gs2RestSession
from core.domain.access_token import AccessToken
from inventory import Gs2InventoryRestClient, request as request_, result as result_
from inventory.domain.iterator.namespaces import DescribeNamespacesIterator
from inventory.domain.iterator.inventory_model_masters import DescribeInventoryModelMastersIterator
from inventory.domain.iterator.inventory_models import DescribeInventoryModelsIterator
from inventory.domain.iterator.item_model_masters import DescribeItemModelMastersIterator
from inventory.domain.iterator.item_models import DescribeItemModelsIterator
from inventory.domain.iterator.inventories import DescribeInventoriesIterator
from inventory.domain.iterator.inventories_by_user_id import DescribeInventoriesByUserIdIterator
from inventory.domain.iterator.item_sets import DescribeItemSetsIterator
from inventory.domain.iterator.item_sets_by_user_id import DescribeItemSetsByUserIdIterator
from inventory.domain.iterator.reference_of import DescribeReferenceOfIterator
from inventory.domain.iterator.reference_of_by_user_id import DescribeReferenceOfByUserIdIterator
from inventory.domain.cache.namespace import NamespaceDomainCache
from inventory.domain.cache.inventory_model_master import InventoryModelMasterDomainCache
from inventory.domain.cache.inventory_model import InventoryModelDomainCache
from inventory.domain.cache.item_model_master import ItemModelMasterDomainCache
from inventory.domain.cache.item_model import ItemModelDomainCache
from inventory.domain.cache.inventory import InventoryDomainCache
from inventory.domain.cache.item_set import ItemSetDomainCache
from inventory.domain.item_set import ItemSetDomain
from inventory.domain.item_set_access_token import ItemSetAccessTokenDomain
from inventory.domain.item_set_access_token import ItemSetAccessTokenDomain


class InventoryDomain:
    _session: Gs2RestSession
    _client: Gs2InventoryRestClient
    _inventory_cache: InventoryDomainCache
    _namespace_name: str
    _user_id: str
    _inventory_name: str
    _item_set_cache: ItemSetDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        inventory_cache: InventoryDomainCache,
        namespace_name: str,
        user_id: str,
        inventory_name: str,
    ):
        self._session = session
        self._client = Gs2InventoryRestClient(
            session,
        )
        self._inventory_cache = inventory_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._inventory_name = inventory_name
        self._item_set_cache = ItemSetDomainCache()

    def load(
        self,
        request: request_.GetInventoryByUserIdRequest,
    ) -> result_.GetInventoryByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_inventory_name(self._inventory_name)
        r = self._client.get_inventory_by_user_id(
            request,
        )
        self._inventory_cache.update(r.item)
        return r

    def add_capacity(
        self,
        request: request_.AddCapacityByUserIdRequest,
    ) -> result_.AddCapacityByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_inventory_name(self._inventory_name)
        r = self._client.add_capacity_by_user_id(
            request,
        )
        self._inventory_cache.update(r.item)
        return r

    def set_capacity(
        self,
        request: request_.SetCapacityByUserIdRequest,
    ) -> result_.SetCapacityByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_inventory_name(self._inventory_name)
        r = self._client.set_capacity_by_user_id(
            request,
        )
        self._inventory_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteInventoryByUserIdRequest,
    ) -> result_.DeleteInventoryByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_inventory_name(self._inventory_name)
        r = self._client.delete_inventory_by_user_id(
            request,
        )
        self._inventory_cache.delete(r.item)
        return r

    def item_sets(
        self,
    ) -> DescribeItemSetsByUserIdIterator:
        return DescribeItemSetsByUserIdIterator(
            self._item_set_cache,
            self._client,
            self._namespace_name,
            self._inventory_name,
            self._user_id,
        )

    def item_set(
        self,
        item_name: str,
        item_set_name: str,
    ) -> ItemSetDomain:
        return ItemSetDomain(
            self._session,
            self._item_set_cache,
            self._namespace_name,
            self._user_id,
            self._inventory_name,
            item_name,
            item_set_name,
        )
