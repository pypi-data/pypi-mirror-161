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
from showcase import Gs2ShowcaseRestClient, request as request_, result as result_
from showcase.domain.iterator.namespaces import DescribeNamespacesIterator
from showcase.domain.iterator.sales_item_masters import DescribeSalesItemMastersIterator
from showcase.domain.iterator.sales_item_group_masters import DescribeSalesItemGroupMastersIterator
from showcase.domain.iterator.showcase_masters import DescribeShowcaseMastersIterator
from showcase.domain.iterator.showcases import DescribeShowcasesIterator
from showcase.domain.iterator.showcases_by_user_id import DescribeShowcasesByUserIdIterator
from showcase.domain.cache.namespace import NamespaceDomainCache
from showcase.domain.cache.sales_item_master import SalesItemMasterDomainCache
from showcase.domain.cache.sales_item_group_master import SalesItemGroupMasterDomainCache
from showcase.domain.cache.showcase_master import ShowcaseMasterDomainCache
from showcase.domain.cache.showcase import ShowcaseDomainCache


class SalesItemGroupMasterDomain:
    _session: Gs2RestSession
    _client: Gs2ShowcaseRestClient
    _sales_item_group_master_cache: SalesItemGroupMasterDomainCache
    _namespace_name: str
    _sales_item_group_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        sales_item_group_master_cache: SalesItemGroupMasterDomainCache,
        namespace_name: str,
        sales_item_group_name: str,
    ):
        self._session = session
        self._client = Gs2ShowcaseRestClient(
            session,
        )
        self._sales_item_group_master_cache = sales_item_group_master_cache
        self._namespace_name = namespace_name
        self._sales_item_group_name = sales_item_group_name

    def load(
        self,
        request: request_.GetSalesItemGroupMasterRequest,
    ) -> result_.GetSalesItemGroupMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_sales_item_group_name(self._sales_item_group_name)
        r = self._client.get_sales_item_group_master(
            request,
        )
        self._sales_item_group_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateSalesItemGroupMasterRequest,
    ) -> result_.UpdateSalesItemGroupMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_sales_item_group_name(self._sales_item_group_name)
        r = self._client.update_sales_item_group_master(
            request,
        )
        self._sales_item_group_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteSalesItemGroupMasterRequest,
    ) -> result_.DeleteSalesItemGroupMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_sales_item_group_name(self._sales_item_group_name)
        r = self._client.delete_sales_item_group_master(
            request,
        )
        self._sales_item_group_master_cache.delete(r.item)
        return r
