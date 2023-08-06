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
from money import Gs2MoneyRestClient, request as request_, result as result_
from money.domain.iterator.namespaces import DescribeNamespacesIterator
from money.domain.cache.namespace import NamespaceDomainCache
from money.domain.namespace import NamespaceDomain

class Gs2Money:
    _session: Gs2RestSession
    _client: Gs2MoneyRestClient
    _namespace_cache: NamespaceDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
    ):
        self._session = session
        self._client = Gs2MoneyRestClient (
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

    def deposit_by_stamp_sheet(
        self,
        request: request_.DepositByStampSheetRequest,
    ) -> result_.DepositByStampSheetResult:
        r = self._client.deposit_by_stamp_sheet(
            request,
        )
        return r

    def withdraw_by_stamp_task(
        self,
        request: request_.WithdrawByStampTaskRequest,
    ) -> result_.WithdrawByStampTaskResult:
        r = self._client.withdraw_by_stamp_task(
            request,
        )
        return r

    def record_receipt(
        self,
        request: request_.RecordReceiptRequest,
    ) -> result_.RecordReceiptResult:
        r = self._client.record_receipt(
            request,
        )
        return r

    def record_receipt_by_stamp_task(
        self,
        request: request_.RecordReceiptByStampTaskRequest,
    ) -> result_.RecordReceiptByStampTaskResult:
        r = self._client.record_receipt_by_stamp_task(
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
