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
from distributor import Gs2DistributorRestClient, request as request_, result as result_
from distributor.domain.iterator.namespaces import DescribeNamespacesIterator
from distributor.domain.cache.namespace import NamespaceDomainCache
from distributor.domain.namespace import NamespaceDomain

class Gs2Distributor:
    _session: Gs2RestSession
    _client: Gs2DistributorRestClient
    _namespace_cache: NamespaceDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
    ):
        self._session = session
        self._client = Gs2DistributorRestClient (
            session,
        )
        self._namespace_cache = NamespaceDomainCache()

    def create_namespace(
        self,
        request: request_.CreateNamespaceRequest,
    ) -> result_.CreateNamespaceResult:
        r = self._client.create_namespace(
            request,
        )
        self._namespace_cache.update(r.item)
        return r

    def distribute_without_overflow_process(
        self,
        request: request_.DistributeWithoutOverflowProcessRequest,
    ) -> result_.DistributeWithoutOverflowProcessResult:
        r = self._client.distribute_without_overflow_process(
            request,
        )
        return r

    def run_stamp_task_without_namespace(
        self,
        request: request_.RunStampTaskWithoutNamespaceRequest,
    ) -> result_.RunStampTaskWithoutNamespaceResult:
        r = self._client.run_stamp_task_without_namespace(
            request,
        )
        return r

    def run_stamp_sheet_without_namespace(
        self,
        request: request_.RunStampSheetWithoutNamespaceRequest,
    ) -> result_.RunStampSheetWithoutNamespaceResult:
        r = self._client.run_stamp_sheet_without_namespace(
            request,
        )
        return r

    def run_stamp_sheet_express_without_namespace(
        self,
        request: request_.RunStampSheetExpressWithoutNamespaceRequest,
    ) -> result_.RunStampSheetExpressWithoutNamespaceResult:
        r = self._client.run_stamp_sheet_express_without_namespace(
            request,
        )
        return r

    def namespaces(
        self,
    ) -> DescribeNamespacesIterator:
        return DescribeNamespacesIterator(
            self._namespace_cache,
            self._client,
        )

    def namespace(
        self,
        namespace_name: str,
    ) -> NamespaceDomain:
        return NamespaceDomain(
            self._session,
            self._namespace_cache,
            namespace_name,
        )
