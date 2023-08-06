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


class RatingDomain:
    _session: Gs2RestSession
    _client: Gs2MatchmakingRestClient
    _rating_cache: RatingDomainCache
    _namespace_name: str
    _user_id: str
    _rating_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        rating_cache: RatingDomainCache,
        namespace_name: str,
        user_id: str,
        rating_name: str,
    ):
        self._session = session
        self._client = Gs2MatchmakingRestClient(
            session,
        )
        self._rating_cache = rating_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._rating_name = rating_name

    def load(
        self,
        request: request_.GetRatingByUserIdRequest,
    ) -> result_.GetRatingByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_rating_name(self._rating_name)
        r = self._client.get_rating_by_user_id(
            request,
        )
        self._rating_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteRatingRequest,
    ) -> result_.DeleteRatingResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_rating_name(self._rating_name)
        r = self._client.delete_rating(
            request,
        )
        self._rating_cache.delete(r.item)
        return r
