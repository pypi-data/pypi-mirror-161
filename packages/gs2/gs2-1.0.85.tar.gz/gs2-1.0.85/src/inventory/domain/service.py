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
from inventory import Gs2InventoryRestClient, request as request_, result as result_
from inventory.domain.iterator.namespaces import DescribeNamespacesIterator
from inventory.domain.cache.namespace import NamespaceDomainCache
from inventory.domain.namespace import NamespaceDomain

class Gs2Inventory:
    _session: Gs2RestSession
    _client: Gs2InventoryRestClient
    _namespace_cache: NamespaceDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
    ):
        self._session = session
        self._client = Gs2InventoryRestClient (
            session,
        )
        self._namespace_cache = NamespaceDomainCache()

    def create_namespace(
        self,
        request: request_.CreateNamespaceRequest,
    ) -> result_.CreateNamespaceResult:
        r = self._client.create_namespace(
            request,
        )
        self._namespace_cache.update(r.item)
        return r

    def add_capacity_by_stamp_sheet(
        self,
        request: request_.AddCapacityByStampSheetRequest,
    ) -> result_.AddCapacityByStampSheetResult:
        r = self._client.add_capacity_by_stamp_sheet(
            request,
        )
        return r

    def set_capacity_by_stamp_sheet(
        self,
        request: request_.SetCapacityByStampSheetRequest,
    ) -> result_.SetCapacityByStampSheetResult:
        r = self._client.set_capacity_by_stamp_sheet(
            request,
        )
        return r

    def acquire_item_set_by_stamp_sheet(
        self,
        request: request_.AcquireItemSetByStampSheetRequest,
    ) -> result_.AcquireItemSetByStampSheetResult:
        r = self._client.acquire_item_set_by_stamp_sheet(
            request,
        )
        return r

    def consume_item_set_by_stamp_task(
        self,
        request: request_.ConsumeItemSetByStampTaskRequest,
    ) -> result_.ConsumeItemSetByStampTaskResult:
        r = self._client.consume_item_set_by_stamp_task(
            request,
        )
        return r

    def add_reference_of_item_set_by_stamp_sheet(
        self,
        request: request_.AddReferenceOfItemSetByStampSheetRequest,
    ) -> result_.AddReferenceOfItemSetByStampSheetResult:
        r = self._client.add_reference_of_item_set_by_stamp_sheet(
            request,
        )
        return r

    def delete_reference_of_item_set_by_stamp_sheet(
        self,
        request: request_.DeleteReferenceOfItemSetByStampSheetRequest,
    ) -> result_.DeleteReferenceOfItemSetByStampSheetResult:
        r = self._client.delete_reference_of_item_set_by_stamp_sheet(
            request,
        )
        return r

    def verify_reference_of_by_stamp_task(
        self,
        request: request_.VerifyReferenceOfByStampTaskRequest,
    ) -> result_.VerifyReferenceOfByStampTaskResult:
        r = self._client.verify_reference_of_by_stamp_task(
            request,
        )
        return r

    def namespaces(
        self,
    ) -> DescribeNamespacesIterator:
        return DescribeNamespacesIterator(
            self._namespace_cache,
            self._client,
        )

    def namespace(
        self,
        namespace_name: str,
    ) -> NamespaceDomain:
        return NamespaceDomain(
            self._session,
            self._namespace_cache,
            namespace_name,
        )
