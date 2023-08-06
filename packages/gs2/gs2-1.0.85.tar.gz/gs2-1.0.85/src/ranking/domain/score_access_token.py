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


class ScoreAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2RankingRestClient
    _score_cache: ScoreDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _category_name: str
    _scorer_user_id: str
    _unique_id: str

    def __init__(
        self,
        session: Gs2RestSession,
        score_cache: ScoreDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        category_name: str,
        scorer_user_id: str,
        unique_id: str,
    ):
        self._session = session
        self._client = Gs2RankingRestClient(
            session,
        )
        self._score_cache = score_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._category_name = category_name
        self._scorer_user_id = scorer_user_id
        self._unique_id = unique_id

    def load(
        self,
        request: request_.GetScoreRequest,
    ) -> result_.GetScoreResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_category_name(self._category_name)
        request.with_scorer_user_id(self._scorer_user_id)
        request.with_unique_id(self._unique_id)
        r = self._client.get_score(
            request,
        )
        self._score_cache.update(r.item)
        return r
