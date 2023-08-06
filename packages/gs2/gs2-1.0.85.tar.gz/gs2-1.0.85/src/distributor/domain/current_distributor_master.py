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
from distributor import Gs2DistributorRestClient, request as request_, result as result_
from distributor.domain.iterator.namespaces import DescribeNamespacesIterator
from distributor.domain.iterator.distributor_model_masters import DescribeDistributorModelMastersIterator
from distributor.domain.iterator.distributor_models import DescribeDistributorModelsIterator
from distributor.domain.cache.namespace import NamespaceDomainCache
from distributor.domain.cache.distributor_model_master import DistributorModelMasterDomainCache
from distributor.domain.cache.distributor_model import DistributorModelDomainCache


class CurrentDistributorMasterDomain:
    _session: Gs2RestSession
    _client: Gs2DistributorRestClient
    _namespace_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2DistributorRestClient(
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
        request: request_.GetCurrentDistributorMasterRequest,
    ) -> result_.GetCurrentDistributorMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.get_current_distributor_master(
            request,
        )
        return r

    def update(
        self,
        request: request_.UpdateCurrentDistributorMasterRequest,
    ) -> result_.UpdateCurrentDistributorMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_distributor_master(
            request,
        )
        return r

    def update_from_git_hub(
        self,
        request: request_.UpdateCurrentDistributorMasterFromGitHubRequest,
    ) -> result_.UpdateCurrentDistributorMasterFromGitHubResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_distributor_master_from_git_hub(
            request,
        )
        return r
