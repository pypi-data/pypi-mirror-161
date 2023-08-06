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
from ranking.domain.ranking import RankingDomain
from ranking.domain.ranking_access_token import RankingAccessTokenDomain
from ranking.domain.score import ScoreDomain
from ranking.domain.score_access_token import ScoreAccessTokenDomain
from ranking.domain.score_access_token import ScoreAccessTokenDomain
from ranking.domain.subscribe import SubscribeDomain
from ranking.domain.subscribe_access_token import SubscribeAccessTokenDomain
from ranking.domain.subscribe_access_token import SubscribeAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2RankingRestClient
    _namespace_name: str
    _access_token: AccessToken
    _score_cache: ScoreDomainCache
    _ranking_cache: RankingDomainCache
    _subscribe_user_cache: SubscribeUserDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2RankingRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._score_cache = ScoreDomainCache()
        self._ranking_cache = RankingDomainCache()
        self._subscribe_user_cache = SubscribeUserDomainCache()

    def put_score(
        self,
        request: request_.PutScoreRequest,
    ) -> result_.PutScoreResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.put_score(
            request,
        )
        return r

    def subscribe_users(
        self,
        category_name: str,
    ) -> DescribeSubscribesByCategoryNameIterator:
        return DescribeSubscribesByCategoryNameIterator(
            self._subscribe_user_cache,
            self._client,
            self._namespace_name,
            category_name,
            self._access_token,
        )

    def scores(
        self,
        category_name: str,
        scorer_user_id: str,
    ) -> DescribeScoresIterator:
        return DescribeScoresIterator(
            self._score_cache,
            self._client,
            self._namespace_name,
            category_name,
            self._access_token,
            scorer_user_id,
        )

    def rankings(
        self,
        category_name: str,
    ) -> DescribeRankingsIterator:
        return DescribeRankingsIterator(
            self._ranking_cache,
            self._client,
            self._namespace_name,
            category_name,
            self._access_token,
        )

    def ranking(
        self,
        category_name: str,
    ) -> RankingAccessTokenDomain:
        return RankingAccessTokenDomain(
            self._session,
            self._ranking_cache,
            self._namespace_name,
            self._access_token,
            category_name,
        )

    def score(
        self,
        category_name: str,
        scorer_user_id: str,
        unique_id: str,
    ) -> ScoreAccessTokenDomain:
        return ScoreAccessTokenDomain(
            self._session,
            self._score_cache,
            self._namespace_name,
            self._access_token,
            category_name,
            scorer_user_id,
            unique_id,
        )

    def subscribe(
        self,
        category_name: str,
    ) -> SubscribeAccessTokenDomain:
        return SubscribeAccessTokenDomain(
            self._session,
            self._namespace_name,
            self._access_token,
            category_name,
        )
