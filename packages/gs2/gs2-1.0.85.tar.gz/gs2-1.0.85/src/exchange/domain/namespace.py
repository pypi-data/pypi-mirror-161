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
from exchange import Gs2ExchangeRestClient, request as request_, result as result_
from exchange.domain.iterator.namespaces import DescribeNamespacesIterator
from exchange.domain.iterator.rate_models import DescribeRateModelsIterator
from exchange.domain.iterator.rate_model_masters import DescribeRateModelMastersIterator
from exchange.domain.iterator.awaits import DescribeAwaitsIterator
from exchange.domain.iterator.awaits_by_user_id import DescribeAwaitsByUserIdIterator
from exchange.domain.cache.namespace import NamespaceDomainCache
from exchange.domain.cache.rate_model import RateModelDomainCache
from exchange.domain.cache.rate_model_master import RateModelMasterDomainCache
from exchange.domain.cache.await_ import AwaitDomainCache
from exchange.domain.rate_model_master import RateModelMasterDomain
from exchange.domain.current_rate_master import CurrentRateMasterDomain
from exchange.domain.rate_model import RateModelDomain
from exchange.domain.user import UserDomain
from exchange.domain.user_access_token import UserAccessTokenDomain
from exchange.domain.user_access_token import UserAccessTokenDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2ExchangeRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _rate_model_cache: RateModelDomainCache
    _rate_model_master_cache: RateModelMasterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2ExchangeRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._rate_model_cache = RateModelDomainCache()
        self._rate_model_master_cache = RateModelMasterDomainCache()

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

    def create_rate_model_master(
        self,
        request: request_.CreateRateModelMasterRequest,
    ) -> result_.CreateRateModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_rate_model_master(
            request,
        )
        return r

    def rate_models(
        self,
    ) -> DescribeRateModelsIterator:
        return DescribeRateModelsIterator(
            self._rate_model_cache,
            self._client,
            self._namespace_name,
        )

    def rate_model_masters(
        self,
    ) -> DescribeRateModelMastersIterator:
        return DescribeRateModelMastersIterator(
            self._rate_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def rate_model_master(
        self,
        rate_name: str,
    ) -> RateModelMasterDomain:
        return RateModelMasterDomain(
            self._session,
            self._rate_model_master_cache,
            self._namespace_name,
            rate_name,
        )

    def current_rate_master(
        self,
    ) -> CurrentRateMasterDomain:
        return CurrentRateMasterDomain(
            self._session,
            self._namespace_name,
        )

    def rate_model(
        self,
        rate_name: str,
    ) -> RateModelDomain:
        return RateModelDomain(
            self._session,
            self._rate_model_cache,
            self._namespace_name,
            rate_name,
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
