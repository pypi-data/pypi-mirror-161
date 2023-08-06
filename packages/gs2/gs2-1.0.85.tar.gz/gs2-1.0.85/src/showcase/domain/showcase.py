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


class ShowcaseDomain:
    _session: Gs2RestSession
    _client: Gs2ShowcaseRestClient
    _showcase_cache: ShowcaseDomainCache
    _namespace_name: str
    _user_id: str
    _showcase_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        showcase_cache: ShowcaseDomainCache,
        namespace_name: str,
        user_id: str,
        showcase_name: str,
    ):
        self._session = session
        self._client = Gs2ShowcaseRestClient(
            session,
        )
        self._showcase_cache = showcase_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._showcase_name = showcase_name

    def load(
        self,
        request: request_.GetShowcaseByUserIdRequest,
    ) -> result_.GetShowcaseByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_showcase_name(self._showcase_name)
        r = self._client.get_showcase_by_user_id(
            request,
        )
        self._showcase_cache.update(r.item)
        return r

    def buy(
        self,
        request: request_.BuyByUserIdRequest,
    ) -> result_.BuyByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_showcase_name(self._showcase_name)
        r = self._client.buy_by_user_id(
            request,
        )
        return r
