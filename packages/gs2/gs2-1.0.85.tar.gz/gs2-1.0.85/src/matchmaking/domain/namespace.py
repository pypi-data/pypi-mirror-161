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
from matchmaking.domain.user import UserDomain
from matchmaking.domain.user_access_token import UserAccessTokenDomain
from matchmaking.domain.user_access_token import UserAccessTokenDomain
from matchmaking.domain.current_rating_model_master import CurrentRatingModelMasterDomain
from matchmaking.domain.rating_model import RatingModelDomain
from matchmaking.domain.rating_model_master import RatingModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2MatchmakingRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _rating_model_master_cache: RatingModelMasterDomainCache
    _rating_model_cache: RatingModelDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2MatchmakingRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._rating_model_master_cache = RatingModelMasterDomainCache()
        self._rating_model_cache = RatingModelDomainCache()

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

    def create_rating_model_master(
        self,
        request: request_.CreateRatingModelMasterRequest,
    ) -> result_.CreateRatingModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_rating_model_master(
            request,
        )
        return r

    def rating_model_masters(
        self,
    ) -> DescribeRatingModelMastersIterator:
        return DescribeRatingModelMastersIterator(
            self._rating_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def rating_models(
        self,
    ) -> DescribeRatingModelsIterator:
        return DescribeRatingModelsIterator(
            self._rating_model_cache,
            self._client,
            self._namespace_name,
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

    def current_rating_model_master(
        self,
    ) -> CurrentRatingModelMasterDomain:
        return CurrentRatingModelMasterDomain(
            self._session,
            self._namespace_name,
        )

    def rating_model(
        self,
        rating_name: str,
    ) -> RatingModelDomain:
        return RatingModelDomain(
            self._session,
            self._rating_model_cache,
            self._namespace_name,
            rating_name,
        )

    def rating_model_master(
        self,
        rating_name: str,
    ) -> RatingModelMasterDomain:
        return RatingModelMasterDomain(
            self._session,
            self._rating_model_master_cache,
            self._namespace_name,
            rating_name,
        )
