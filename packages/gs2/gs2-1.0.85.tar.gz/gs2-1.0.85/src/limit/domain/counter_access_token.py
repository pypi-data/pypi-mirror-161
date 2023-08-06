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


class CounterAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2LimitRestClient
    _counter_cache: CounterDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _limit_name: str
    _counter_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        counter_cache: CounterDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        limit_name: str,
        counter_name: str,
    ):
        self._session = session
        self._client = Gs2LimitRestClient(
            session,
        )
        self._counter_cache = counter_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._limit_name = limit_name
        self._counter_name = counter_name

    def load(
        self,
        request: request_.GetCounterRequest,
    ) -> result_.GetCounterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_limit_name(self._limit_name)
        request.with_counter_name(self._counter_name)
        r = self._client.get_counter(
            request,
        )
        self._counter_cache.update(r.item)
        return r

    def count_up(
        self,
        request: request_.CountUpRequest,
    ) -> result_.CountUpResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_limit_name(self._limit_name)
        request.with_counter_name(self._counter_name)
        r = self._client.count_up(
            request,
        )
        self._counter_cache.update(r.item)
        return r
