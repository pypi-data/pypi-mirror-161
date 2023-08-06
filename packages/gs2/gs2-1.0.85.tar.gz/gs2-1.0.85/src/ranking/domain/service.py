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
from ranking import Gs2RankingRestClient, request as request_, result as result_
from ranking.domain.iterator.namespaces import DescribeNamespacesIterator
from ranking.domain.cache.namespace import NamespaceDomainCache
from ranking.domain.cache.subscribe_user import SubscribeUserDomainCache
from ranking.domain.namespace import NamespaceDomain

class Gs2Ranking:
    _session: Gs2RestSession
    _client: Gs2RankingRestClient
    _namespace_cache: NamespaceDomainCache
    _subscribeUser_cache: SubscribeUserDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
    ):
        self._session = session
        self._client = Gs2RankingRestClient (
            session,
        )
        self._namespace_cache = NamespaceDomainCache()
        self._subscribeUser_cache = SubscribeUserDomainCache()

    def create_namespace(
        self,
        request: request_.CreateNamespaceRequest,
    ) -> result_.CreateNamespaceResult:
        r = self._client.create_namespace(
            request,
        )
        self._namespace_cache.update(r.item)
        return r

    def calc_ranking(
        self,
        request: request_.CalcRankingRequest,
    ) -> result_.CalcRankingResult:
        r = self._client.calc_ranking(
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
