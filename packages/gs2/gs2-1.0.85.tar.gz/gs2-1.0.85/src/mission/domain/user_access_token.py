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
from mission import Gs2MissionRestClient, request as request_, result as result_
from mission.domain.iterator.completes import DescribeCompletesIterator
from mission.domain.iterator.completes_by_user_id import DescribeCompletesByUserIdIterator
from mission.domain.iterator.counter_model_masters import DescribeCounterModelMastersIterator
from mission.domain.iterator.mission_group_model_masters import DescribeMissionGroupModelMastersIterator
from mission.domain.iterator.namespaces import DescribeNamespacesIterator
from mission.domain.iterator.counters import DescribeCountersIterator
from mission.domain.iterator.counters_by_user_id import DescribeCountersByUserIdIterator
from mission.domain.iterator.counter_models import DescribeCounterModelsIterator
from mission.domain.iterator.mission_group_models import DescribeMissionGroupModelsIterator
from mission.domain.iterator.mission_task_models import DescribeMissionTaskModelsIterator
from mission.domain.iterator.mission_task_model_masters import DescribeMissionTaskModelMastersIterator
from mission.domain.cache.complete import CompleteDomainCache
from mission.domain.cache.counter_model_master import CounterModelMasterDomainCache
from mission.domain.cache.mission_group_model_master import MissionGroupModelMasterDomainCache
from mission.domain.cache.namespace import NamespaceDomainCache
from mission.domain.cache.counter import CounterDomainCache
from mission.domain.cache.counter_model import CounterModelDomainCache
from mission.domain.cache.mission_group_model import MissionGroupModelDomainCache
from mission.domain.cache.mission_task_model import MissionTaskModelDomainCache
from mission.domain.cache.mission_task_model_master import MissionTaskModelMasterDomainCache
from mission.domain.counter import CounterDomain
from mission.domain.counter_access_token import CounterAccessTokenDomain
from mission.domain.counter_access_token import CounterAccessTokenDomain
from mission.domain.complete import CompleteDomain
from mission.domain.complete_access_token import CompleteAccessTokenDomain
from mission.domain.complete_access_token import CompleteAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2MissionRestClient
    _namespace_name: str
    _access_token: AccessToken
    _complete_cache: CompleteDomainCache
    _counter_cache: CounterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2MissionRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._complete_cache = CompleteDomainCache()
        self._counter_cache = CounterDomainCache()

    def completes(
        self,
    ) -> DescribeCompletesIterator:
        return DescribeCompletesIterator(
            self._complete_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def counters(
        self,
    ) -> DescribeCountersIterator:
        return DescribeCountersIterator(
            self._counter_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def counter(
        self,
        counter_name: str,
    ) -> CounterAccessTokenDomain:
        return CounterAccessTokenDomain(
            self._session,
            self._counter_cache,
            self._namespace_name,
            self._access_token,
            counter_name,
        )

    def complete(
        self,
        mission_group_name: str,
    ) -> CompleteAccessTokenDomain:
        return CompleteAccessTokenDomain(
            self._session,
            self._complete_cache,
            self._namespace_name,
            self._access_token,
            mission_group_name,
        )
