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
from ranking import Gs2RankingRestClient, request as request_, result as result_
from ranking.domain.iterator.namespaces import DescribeNamespacesIterator
from ranking.domain.iterator.category_models import DescribeCategoryModelsIterator
from ranking.domain.iterator.category_model_masters import DescribeCategoryModelMastersIterator
from ranking.domain.iterator.subscribes_by_category_name import DescribeSubscribesByCategoryNameIterator
from ranking.domain.iterator.subscribes_by_category_name_and_user_id import DescribeSubscribesByCategoryNameAndUserIdIterator
from ranking.domain.iterator.scores import DescribeScoresIterator
from ranking.domain.iterator.scores_by_user_id import DescribeScoresByUserIdIterator
from ranking.domain.iterator.rankings import DescribeRankingsIterator
from ranking.domain.iterator.rankings_by_user_id import DescribeRankingsByUserIdIterator
from ranking.domain.iterator.near_rankings import DescribeNearRankingsIterator
from ranking.domain.cache.namespace import NamespaceDomainCache
from ranking.domain.cache.category_model import CategoryModelDomainCache
from ranking.domain.cache.category_model_master import CategoryModelMasterDomainCache
from ranking.domain.cache.subscribe_user import SubscribeUserDomainCache
from ranking.domain.cache.score import ScoreDomainCache
from ranking.domain.cache.ranking import RankingDomainCache
from ranking.domain.current_ranking_master import CurrentRankingMasterDomain
from ranking.domain.category_model import CategoryModelDomain
from ranking.domain.user import UserDomain
from ranking.domain.user_access_token import UserAccessTokenDomain
from ranking.domain.user_access_token import UserAccessTokenDomain
from ranking.domain.category_model_master import CategoryModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2RankingRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _category_model_cache: CategoryModelDomainCache
    _category_model_master_cache: CategoryModelMasterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2RankingRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._category_model_cache = CategoryModelDomainCache()
        self._category_model_master_cache = CategoryModelMasterDomainCache()

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

    def create_category_model_master(
        self,
        request: request_.CreateCategoryModelMasterRequest,
    ) -> result_.CreateCategoryModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_category_model_master(
            request,
        )
        return r

    def category_models(
        self,
    ) -> DescribeCategoryModelsIterator:
        return DescribeCategoryModelsIterator(
            self._category_model_cache,
            self._client,
            self._namespace_name,
        )

    def category_model_masters(
        self,
    ) -> DescribeCategoryModelMastersIterator:
        return DescribeCategoryModelMastersIterator(
            self._category_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def current_ranking_master(
        self,
    ) -> CurrentRankingMasterDomain:
        return CurrentRankingMasterDomain(
            self._session,
            self._namespace_name,
        )

    def category_model(
        self,
        category_name: str,
    ) -> CategoryModelDomain:
        return CategoryModelDomain(
            self._session,
            self._category_model_cache,
            self._namespace_name,
            category_name,
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

    def category_model_master(
        self,
        category_name: str,
    ) -> CategoryModelMasterDomain:
        return CategoryModelMasterDomain(
            self._session,
            self._category_model_master_cache,
            self._namespace_name,
            category_name,
        )
