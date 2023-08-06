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
from mission.domain.current_mission_master import CurrentMissionMasterDomain
from mission.domain.mission_group_model import MissionGroupModelDomain
from mission.domain.counter_model import CounterModelDomain
from mission.domain.user import UserDomain
from mission.domain.user_access_token import UserAccessTokenDomain
from mission.domain.user_access_token import UserAccessTokenDomain
from mission.domain.mission_group_model_master import MissionGroupModelMasterDomain
from mission.domain.counter_model_master import CounterModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2MissionRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _counter_model_master_cache: CounterModelMasterDomainCache
    _mission_group_model_master_cache: MissionGroupModelMasterDomainCache
    _counter_model_cache: CounterModelDomainCache
    _mission_group_model_cache: MissionGroupModelDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2MissionRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._counter_model_master_cache = CounterModelMasterDomainCache()
        self._mission_group_model_master_cache = MissionGroupModelMasterDomainCache()
        self._counter_model_cache = CounterModelDomainCache()
        self._mission_group_model_cache = MissionGroupModelDomainCache()

    def create_counter_model_master(
        self,
        request: request_.CreateCounterModelMasterRequest,
    ) -> result_.CreateCounterModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_counter_model_master(
            request,
        )
        return r

    def create_mission_group_model_master(
        self,
        request: request_.CreateMissionGroupModelMasterRequest,
    ) -> result_.CreateMissionGroupModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_mission_group_model_master(
            request,
        )
        return r

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

    def counter_model_masters(
        self,
    ) -> DescribeCounterModelMastersIterator:
        return DescribeCounterModelMastersIterator(
            self._counter_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def mission_group_model_masters(
        self,
    ) -> DescribeMissionGroupModelMastersIterator:
        return DescribeMissionGroupModelMastersIterator(
            self._mission_group_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def counter_models(
        self,
    ) -> DescribeCounterModelsIterator:
        return DescribeCounterModelsIterator(
            self._counter_model_cache,
            self._client,
            self._namespace_name,
        )

    def mission_group_models(
        self,
    ) -> DescribeMissionGroupModelsIterator:
        return DescribeMissionGroupModelsIterator(
            self._mission_group_model_cache,
            self._client,
            self._namespace_name,
        )

    def current_mission_master(
        self,
    ) -> CurrentMissionMasterDomain:
        return CurrentMissionMasterDomain(
            self._session,
            self._namespace_name,
        )

    def mission_group_model(
        self,
        mission_group_name: str,
    ) -> MissionGroupModelDomain:
        return MissionGroupModelDomain(
            self._session,
            self._mission_group_model_cache,
            self._namespace_name,
            mission_group_name,
        )

    def counter_model(
        self,
        counter_name: str,
    ) -> CounterModelDomain:
        return CounterModelDomain(
            self._session,
            self._counter_model_cache,
            self._namespace_name,
            counter_name,
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

    def mission_group_model_master(
        self,
        mission_group_name: str,
    ) -> MissionGroupModelMasterDomain:
        return MissionGroupModelMasterDomain(
            self._session,
            self._mission_group_model_master_cache,
            self._namespace_name,
            mission_group_name,
        )

    def counter_model_master(
        self,
        counter_name: str,
    ) -> CounterModelMasterDomain:
        return CounterModelMasterDomain(
            self._session,
            self._counter_model_master_cache,
            self._namespace_name,
            counter_name,
        )
