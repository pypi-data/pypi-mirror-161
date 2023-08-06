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


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2MatchmakingRestClient
    _namespace_name: str
    _access_token: AccessToken
    _gathering_cache: GatheringDomainCache
    _rating_cache: RatingDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2MatchmakingRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._gathering_cache = GatheringDomainCache()
        self._rating_cache = RatingDomainCache()

    def create_gathering(
        self,
        request: request_.CreateGatheringRequest,
    ) -> result_.CreateGatheringResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.create_gathering(
            request,
        )
        return r

    def do_matchmaking(
        self,
        request: request_.DoMatchmakingRequest,
    ) -> result_.DoMatchmakingResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.do_matchmaking(
            request,
        )
        return r

    def ratings(
        self,
    ) -> DescribeRatingsIterator:
        return DescribeRatingsIterator(
            self._rating_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def rating(
        self,
        rating_name: str,
    ) -> RatingAccessTokenDomain:
        return RatingAccessTokenDomain(
            self._session,
            self._rating_cache,
            self._namespace_name,
            self._access_token,
            rating_name,
        )

    def gathering(
        self,
        gathering_name: str,
    ) -> GatheringAccessTokenDomain:
        return GatheringAccessTokenDomain(
            self._session,
            self._gathering_cache,
            self._namespace_name,
            self._access_token,
            gathering_name,
        )

    def vote(
        self,
        rating_name: str,
        gathering_name: str,
    ) -> VoteAccessTokenDomain:
        return VoteAccessTokenDomain(
            self._session,
            self._namespace_name,
            self._access_token,
            rating_name,
            gathering_name,
        )
