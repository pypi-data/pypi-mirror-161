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
from limit.domain.counter import CounterDomain
from limit.domain.counter_access_token import CounterAccessTokenDomain
from limit.domain.counter_access_token import CounterAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2LimitRestClient
    _namespace_name: str
    _user_id: str
    _counter_cache: CounterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2LimitRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._counter_cache = CounterDomainCache()

    def counters(
        self,
        limit_name: str,
    ) -> DescribeCountersByUserIdIterator:
        return DescribeCountersByUserIdIterator(
            self._counter_cache,
            self._client,
            self._namespace_name,
            self._user_id,
            limit_name,
        )

    def counter(
        self,
        limit_name: str,
        counter_name: str,
    ) -> CounterDomain:
        return CounterDomain(
            self._session,
            self._counter_cache,
            self._namespace_name,
            self._user_id,
            limit_name,
            counter_name,
        )
