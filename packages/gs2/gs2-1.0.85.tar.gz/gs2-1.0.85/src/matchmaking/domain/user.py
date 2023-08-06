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
from matchmaking import Gs2MatchmakingRestClient, request as request_, result as result_
from matchmaking.domain.iterator.namespaces import DescribeNamespacesIterator
from matchmaking.domain.iterator.gatherings import DescribeGatheringsIterator
from matchmaking.domain.iterator.rating_model_masters import DescribeRatingModelMastersIterator
from matchmaking.domain.iterator.rating_models import DescribeRatingModelsIterator
from matchmaking.domain.iterator.ratings import DescribeRatingsIterator
from matchmaking.domain.iterator.ratings_by_user_id import DescribeRatingsByUserIdIterator
from matchmaking.domain.cache.namespace import NamespaceDomainCache
from matchmaking.domain.cache.gathering import GatheringDomainCache
from matchmaking.domain.cache.rating_model_master import RatingModelMasterDomainCache
from matchmaking.domain.cache.rating_model import RatingModelDomainCache
from matchmaking.domain.cache.rating import RatingDomainCache
from matchmaking.domain.rating import RatingDomain
from matchmaking.domain.rating_access_token import RatingAccessTokenDomain
from matchmaking.domain.rating_access_token import RatingAccessTokenDomain
from matchmaking.domain.gathering import GatheringDomain
from matchmaking.domain.gathering_access_token import GatheringAccessTokenDomain
from matchmaking.domain.gathering_access_token import GatheringAccessTokenDomain
from matchmaking.domain.vote import VoteDomain
from matchmaking.domain.vote_access_token import VoteAccessTokenDomain
from matchmaking.domain.vote_access_token import VoteAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2MatchmakingRestClient
    _namespace_name: str
    _user_id: str
    _gathering_cache: GatheringDomainCache
    _rating_cache: RatingDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2MatchmakingRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._gathering_cache = GatheringDomainCache()
        self._rating_cache = RatingDomainCache()

    def create_gathering(
        self,
        request: request_.CreateGatheringByUserIdRequest,
    ) -> result_.CreateGatheringByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.create_gathering_by_user_id(
            request,
        )
        return r

    def do_matchmaking(
        self,
        request: request_.DoMatchmakingByUserIdRequest,
    ) -> result_.DoMatchmakingByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.do_matchmaking_by_user_id(
            request,
        )
        return r

    def gatherings(
        self,
    ) -> DescribeGatheringsIterator:
        return DescribeGatheringsIterator(
            self._gathering_cache,
            self._client,
            self._namespace_name,
        )

    def ratings(
        self,
    ) -> DescribeRatingsByUserIdIterator:
        return DescribeRatingsByUserIdIterator(
            self._rating_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def rating(
        self,
        rating_name: str,
    ) -> RatingDomain:
        return RatingDomain(
            self._session,
            self._rating_cache,
            self._namespace_name,
            self._user_id,
            rating_name,
        )

    def gathering(
        self,
        gathering_name: str,
    ) -> GatheringDomain:
        return GatheringDomain(
            self._session,
            self._gathering_cache,
            self._namespace_name,
            self._user_id,
            gathering_name,
        )

    def vote(
        self,
        rating_name: str,
        gathering_name: str,
    ) -> VoteDomain:
        return VoteDomain(
            self._session,
            self._namespace_name,
            self._user_id,
            rating_name,
            gathering_name,
        )
