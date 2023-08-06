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


class ShowcaseMasterDomain:
    _session: Gs2RestSession
    _client: Gs2ShowcaseRestClient
    _showcase_master_cache: ShowcaseMasterDomainCache
    _namespace_name: str
    _showcase_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        showcase_master_cache: ShowcaseMasterDomainCache,
        namespace_name: str,
        showcase_name: str,
    ):
        self._session = session
        self._client = Gs2ShowcaseRestClient(
            session,
        )
        self._showcase_master_cache = showcase_master_cache
        self._namespace_name = namespace_name
        self._showcase_name = showcase_name

    def load(
        self,
        request: request_.GetShowcaseMasterRequest,
    ) -> result_.GetShowcaseMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_showcase_name(self._showcase_name)
        r = self._client.get_showcase_master(
            request,
        )
        self._showcase_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateShowcaseMasterRequest,
    ) -> result_.UpdateShowcaseMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_showcase_name(self._showcase_name)
        r = self._client.update_showcase_master(
            request,
        )
        self._showcase_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteShowcaseMasterRequest,
    ) -> result_.DeleteShowcaseMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_showcase_name(self._showcase_name)
        r = self._client.delete_showcase_master(
            request,
        )
        self._showcase_master_cache.delete(r.item)
        return r
