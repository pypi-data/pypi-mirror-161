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


class CurrentRankingMasterDomain:
    _session: Gs2RestSession
    _client: Gs2RankingRestClient
    _namespace_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2RankingRestClient(
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
        request: request_.GetCurrentRankingMasterRequest,
    ) -> result_.GetCurrentRankingMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.get_current_ranking_master(
            request,
        )
        return r

    def update(
        self,
        request: request_.UpdateCurrentRankingMasterRequest,
    ) -> result_.UpdateCurrentRankingMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_ranking_master(
            request,
        )
        return r

    def update_from_git_hub(
        self,
        request: request_.UpdateCurrentRankingMasterFromGitHubRequest,
    ) -> result_.UpdateCurrentRankingMasterFromGitHubResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_ranking_master_from_git_hub(
            request,
        )
        return r
