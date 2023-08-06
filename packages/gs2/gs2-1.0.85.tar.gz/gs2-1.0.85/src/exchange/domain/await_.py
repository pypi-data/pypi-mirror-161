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


class AwaitDomain:
    _session: Gs2RestSession
    _client: Gs2ExchangeRestClient
    _await_cache: AwaitDomainCache
    _namespace_name: str
    _user_id: str
    _await_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        await_cache: AwaitDomainCache,
        namespace_name: str,
        user_id: str,
        await_name: str,
    ):
        self._session = session
        self._client = Gs2ExchangeRestClient(
            session,
        )
        self._await_cache = await_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._await_name = await_name

    def load(
        self,
        request: request_.GetAwaitByUserIdRequest,
    ) -> result_.GetAwaitByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_await_name(self._await_name)
        r = self._client.get_await_by_user_id(
            request,
        )
        self._await_cache.update(r.item)
        return r

    def acquire(
        self,
        request: request_.AcquireByUserIdRequest,
    ) -> result_.AcquireByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_await_name(self._await_name)
        r = self._client.acquire_by_user_id(
            request,
        )
        self._await_cache.update(r.item)
        return r

    def acquire_force(
        self,
        request: request_.AcquireForceByUserIdRequest,
    ) -> result_.AcquireForceByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_await_name(self._await_name)
        r = self._client.acquire_force_by_user_id(
            request,
        )
        self._await_cache.update(r.item)
        return r

    def skip(
        self,
        request: request_.SkipByUserIdRequest,
    ) -> result_.SkipByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_await_name(self._await_name)
        r = self._client.skip_by_user_id(
            request,
        )
        self._await_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteAwaitByUserIdRequest,
    ) -> result_.DeleteAwaitByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_await_name(self._await_name)
        r = self._client.delete_await_by_user_id(
            request,
        )
        self._await_cache.delete(r.item)
        return r
