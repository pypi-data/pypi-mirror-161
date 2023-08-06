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


class CurrentShowcaseMasterDomain:
    _session: Gs2RestSession
    _client: Gs2ShowcaseRestClient
    _namespace_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2ShowcaseRestClient(
            session,
        )
        self._namespace_name = namespace_name

    def export_master(
        self,
        request: request_.ExportMasterRequest,
    ) -> result_.ExportMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.export_master(
            request,
        )
        return r

    def load(
        self,
        request: request_.GetCurrentShowcaseMasterRequest,
    ) -> result_.GetCurrentShowcaseMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.get_current_showcase_master(
            request,
        )
        return r

    def update(
        self,
        request: request_.UpdateCurrentShowcaseMasterRequest,
    ) -> result_.UpdateCurrentShowcaseMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_showcase_master(
            request,
        )
        return r

    def update_from_git_hub(
        self,
        request: request_.UpdateCurrentShowcaseMasterFromGitHubRequest,
    ) -> result_.UpdateCurrentShowcaseMasterFromGitHubResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_showcase_master_from_git_hub(
            request,
        )
        return r
