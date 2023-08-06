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


class GatheringAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2MatchmakingRestClient
    _gathering_cache: GatheringDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _gathering_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        gathering_cache: GatheringDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        gathering_name: str,
    ):
        self._session = session
        self._client = Gs2MatchmakingRestClient(
            session,
        )
        self._gathering_cache = gathering_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._gathering_name = gathering_name

    def update(
        self,
        request: request_.UpdateGatheringRequest,
    ) -> result_.UpdateGatheringResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_gathering_name(self._gathering_name)
        r = self._client.update_gathering(
            request,
        )
        self._gathering_cache.update(r.item)
        return r

    def cancel_matchmaking(
        self,
        request: request_.CancelMatchmakingRequest,
    ) -> result_.CancelMatchmakingResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_gathering_name(self._gathering_name)
        r = self._client.cancel_matchmaking(
            request,
        )
        self._gathering_cache.update(r.item)
        return r
