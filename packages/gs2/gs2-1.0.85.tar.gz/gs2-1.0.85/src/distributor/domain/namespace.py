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
from distributor.domain.current_distributor_master import CurrentDistributorMasterDomain
from distributor.domain.distributor_model import DistributorModelDomain
from distributor.domain.distributor_model_master import DistributorModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2DistributorRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _distributor_model_master_cache: DistributorModelMasterDomainCache
    _distributor_model_cache: DistributorModelDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2DistributorRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._distributor_model_master_cache = DistributorModelMasterDomainCache()
        self._distributor_model_cache = DistributorModelDomainCache()

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

    def create_distributor_model_master(
        self,
        request: request_.CreateDistributorModelMasterRequest,
    ) -> result_.CreateDistributorModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_distributor_model_master(
            request,
        )
        return r

    def distribute(
        self,
        request: request_.DistributeRequest,
    ) -> result_.DistributeResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.distribute(
            request,
        )
        return r

    def run_stamp_task(
        self,
        request: request_.RunStampTaskRequest,
    ) -> result_.RunStampTaskResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.run_stamp_task(
            request,
        )
        return r

    def run_stamp_sheet(
        self,
        request: request_.RunStampSheetRequest,
    ) -> result_.RunStampSheetResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.run_stamp_sheet(
            request,
        )
        return r

    def run_stamp_sheet_express(
        self,
        request: request_.RunStampSheetExpressRequest,
    ) -> result_.RunStampSheetExpressResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.run_stamp_sheet_express(
            request,
        )
        return r

    def distributor_model_masters(
        self,
    ) -> DescribeDistributorModelMastersIterator:
        return DescribeDistributorModelMastersIterator(
            self._distributor_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def distributor_models(
        self,
    ) -> DescribeDistributorModelsIterator:
        return DescribeDistributorModelsIterator(
            self._distributor_model_cache,
            self._client,
            self._namespace_name,
        )

    def current_distributor_master(
        self,
    ) -> CurrentDistributorMasterDomain:
        return CurrentDistributorMasterDomain(
            self._session,
            self._namespace_name,
        )

    def distributor_model(
        self,
        distributor_name: str,
    ) -> DistributorModelDomain:
        return DistributorModelDomain(
            self._session,
            self._distributor_model_cache,
            self._namespace_name,
            distributor_name,
        )

    def distributor_model_master(
        self,
        distributor_name: str,
    ) -> DistributorModelMasterDomain:
        return DistributorModelMasterDomain(
            self._session,
            self._distributor_model_master_cache,
            self._namespace_name,
            distributor_name,
        )
