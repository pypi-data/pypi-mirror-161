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


class DistributorModelMasterDomain:
    _session: Gs2RestSession
    _client: Gs2DistributorRestClient
    _distributor_model_master_cache: DistributorModelMasterDomainCache
    _namespace_name: str
    _distributor_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        distributor_model_master_cache: DistributorModelMasterDomainCache,
        namespace_name: str,
        distributor_name: str,
    ):
        self._session = session
        self._client = Gs2DistributorRestClient(
            session,
        )
        self._distributor_model_master_cache = distributor_model_master_cache
        self._namespace_name = namespace_name
        self._distributor_name = distributor_name

    def load(
        self,
        request: request_.GetDistributorModelMasterRequest,
    ) -> result_.GetDistributorModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_distributor_name(self._distributor_name)
        r = self._client.get_distributor_model_master(
            request,
        )
        self._distributor_model_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateDistributorModelMasterRequest,
    ) -> result_.UpdateDistributorModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_distributor_name(self._distributor_name)
        r = self._client.update_distributor_model_master(
            request,
        )
        self._distributor_model_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteDistributorModelMasterRequest,
    ) -> result_.DeleteDistributorModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_distributor_name(self._distributor_name)
        r = self._client.delete_distributor_model_master(
            request,
        )
        self._distributor_model_master_cache.delete(r.item)
        return r
