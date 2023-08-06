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
from showcase.domain.current_showcase_master import CurrentShowcaseMasterDomain
from showcase.domain.user import UserDomain
from showcase.domain.user_access_token import UserAccessTokenDomain
from showcase.domain.user_access_token import UserAccessTokenDomain
from showcase.domain.sales_item_master import SalesItemMasterDomain
from showcase.domain.sales_item_group_master import SalesItemGroupMasterDomain
from showcase.domain.showcase_master import ShowcaseMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2ShowcaseRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _sales_item_master_cache: SalesItemMasterDomainCache
    _sales_item_group_master_cache: SalesItemGroupMasterDomainCache
    _showcase_master_cache: ShowcaseMasterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2ShowcaseRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._sales_item_master_cache = SalesItemMasterDomainCache()
        self._sales_item_group_master_cache = SalesItemGroupMasterDomainCache()
        self._showcase_master_cache = ShowcaseMasterDomainCache()

    def get_status(
        self,
        request: request_.GetNamespaceStatusRequest,
    ) -> result_.GetNamespaceStatusResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.get_namespace_status(
            request,
        )
        return r

    def load(
        self,
        request: request_.GetNamespaceRequest,
    ) -> result_.GetNamespaceResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.get_namespace(
            request,
        )
        self._namespace_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateNamespaceRequest,
    ) -> result_.UpdateNamespaceResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_namespace(
            request,
        )
        self._namespace_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteNamespaceRequest,
    ) -> result_.DeleteNamespaceResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.delete_namespace(
            request,
        )
        self._namespace_cache.delete(r.item)
        return r

    def create_sales_item_master(
        self,
        request: request_.CreateSalesItemMasterRequest,
    ) -> result_.CreateSalesItemMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_sales_item_master(
            request,
        )
        return r

    def create_sales_item_group_master(
        self,
        request: request_.CreateSalesItemGroupMasterRequest,
    ) -> result_.CreateSalesItemGroupMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_sales_item_group_master(
            request,
        )
        return r

    def create_showcase_master(
        self,
        request: request_.CreateShowcaseMasterRequest,
    ) -> result_.CreateShowcaseMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_showcase_master(
            request,
        )
        return r

    def sales_item_masters(
        self,
    ) -> DescribeSalesItemMastersIterator:
        return DescribeSalesItemMastersIterator(
            self._sales_item_master_cache,
            self._client,
            self._namespace_name,
        )

    def sales_item_group_masters(
        self,
    ) -> DescribeSalesItemGroupMastersIterator:
        return DescribeSalesItemGroupMastersIterator(
            self._sales_item_group_master_cache,
            self._client,
            self._namespace_name,
        )

    def showcase_masters(
        self,
    ) -> DescribeShowcaseMastersIterator:
        return DescribeShowcaseMastersIterator(
            self._showcase_master_cache,
            self._client,
            self._namespace_name,
        )

    def current_showcase_master(
        self,
    ) -> CurrentShowcaseMasterDomain:
        return CurrentShowcaseMasterDomain(
            self._session,
            self._namespace_name,
        )

    def user(
        self,
        user_id: str,
    ) -> UserDomain:
        return UserDomain(
            self._session,
            self._namespace_name,
            user_id,
        )

    def access_token(
        self,
        access_token: AccessToken,
    ) -> UserAccessTokenDomain:
        return UserAccessTokenDomain(
            self._session,
            self._namespace_name,
            access_token,
        )

    def sales_item_master(
        self,
        sales_item_name: str,
    ) -> SalesItemMasterDomain:
        return SalesItemMasterDomain(
            self._session,
            self._sales_item_master_cache,
            self._namespace_name,
            sales_item_name,
        )

    def sales_item_group_master(
        self,
        sales_item_group_name: str,
    ) -> SalesItemGroupMasterDomain:
        return SalesItemGroupMasterDomain(
            self._session,
            self._sales_item_group_master_cache,
            self._namespace_name,
            sales_item_group_name,
        )

    def showcase_master(
        self,
        showcase_name: str,
    ) -> ShowcaseMasterDomain:
        return ShowcaseMasterDomain(
            self._session,
            self._showcase_master_cache,
            self._namespace_name,
            showcase_name,
        )
