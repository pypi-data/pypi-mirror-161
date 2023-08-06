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


class CurrentLimitMasterDomain:
    _session: Gs2RestSession
    _client: Gs2LimitRestClient
    _namespace_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2LimitRestClient(
            session,
        )
        self._namespace_name = namespace_name

    def export_master(
        self,
        request: request_.ExportMasterRequest,
    ) -> result_.ExportMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.export_master(
            request,
        )
        return r

    def load(
        self,
        request: request_.GetCurrentLimitMasterRequest,
    ) -> result_.GetCurrentLimitMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.get_current_limit_master(
            request,
        )
        return r

    def update(
        self,
        request: request_.UpdateCurrentLimitMasterRequest,
    ) -> result_.UpdateCurrentLimitMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_limit_master(
            request,
        )
        return r

    def update_from_git_hub(
        self,
        request: request_.UpdateCurrentLimitMasterFromGitHubRequest,
    ) -> result_.UpdateCurrentLimitMasterFromGitHubResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_limit_master_from_git_hub(
            request,
        )
        return r
