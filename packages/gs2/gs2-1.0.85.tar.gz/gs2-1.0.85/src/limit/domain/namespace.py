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
from limit import Gs2LimitRestClient, request as request_, result as result_
from limit.domain.iterator.namespaces import DescribeNamespacesIterator
from limit.domain.iterator.counters import DescribeCountersIterator
from limit.domain.iterator.counters_by_user_id import DescribeCountersByUserIdIterator
from limit.domain.iterator.limit_model_masters import DescribeLimitModelMastersIterator
from limit.domain.iterator.limit_models import DescribeLimitModelsIterator
from limit.domain.cache.namespace import NamespaceDomainCache
from limit.domain.cache.counter import CounterDomainCache
from limit.domain.cache.limit_model_master import LimitModelMasterDomainCache
from limit.domain.cache.limit_model import LimitModelDomainCache
from limit.domain.current_limit_master import CurrentLimitMasterDomain
from limit.domain.limit_model import LimitModelDomain
from limit.domain.user import UserDomain
from limit.domain.user_access_token import UserAccessTokenDomain
from limit.domain.user_access_token import UserAccessTokenDomain
from limit.domain.limit_model_master import LimitModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2LimitRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _limit_model_master_cache: LimitModelMasterDomainCache
    _limit_model_cache: LimitModelDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2LimitRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._limit_model_master_cache = LimitModelMasterDomainCache()
        self._limit_model_cache = LimitModelDomainCache()

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

    def create_limit_model_master(
        self,
        request: request_.CreateLimitModelMasterRequest,
    ) -> result_.CreateLimitModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_limit_model_master(
            request,
        )
        return r

    def limit_model_masters(
        self,
    ) -> DescribeLimitModelMastersIterator:
        return DescribeLimitModelMastersIterator(
            self._limit_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def limit_models(
        self,
    ) -> DescribeLimitModelsIterator:
        return DescribeLimitModelsIterator(
            self._limit_model_cache,
            self._client,
            self._namespace_name,
        )

    def current_limit_master(
        self,
    ) -> CurrentLimitMasterDomain:
        return CurrentLimitMasterDomain(
            self._session,
            self._namespace_name,
        )

    def limit_model(
        self,
        limit_name: str,
    ) -> LimitModelDomain:
        return LimitModelDomain(
            self._session,
            self._limit_model_cache,
            self._namespace_name,
            limit_name,
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

    def limit_model_master(
        self,
        limit_name: str,
    ) -> LimitModelMasterDomain:
        return LimitModelMasterDomain(
            self._session,
            self._limit_model_master_cache,
            self._namespace_name,
            limit_name,
        )
