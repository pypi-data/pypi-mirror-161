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
from log import Gs2LogRestClient, request as request_, result as result_
from log.domain.iterator.namespaces import DescribeNamespacesIterator
from log.domain.cache.namespace import NamespaceDomainCache


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2LogRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2LogRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name

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

    def query_access_log(
        self,
        request: request_.QueryAccessLogRequest,
    ) -> result_.QueryAccessLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.query_access_log(
            request,
        )
        return r

    def count_access_log(
        self,
        request: request_.CountAccessLogRequest,
    ) -> result_.CountAccessLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.count_access_log(
            request,
        )
        return r

    def query_issue_stamp_sheet_log(
        self,
        request: request_.QueryIssueStampSheetLogRequest,
    ) -> result_.QueryIssueStampSheetLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.query_issue_stamp_sheet_log(
            request,
        )
        return r

    def count_issue_stamp_sheet_log(
        self,
        request: request_.CountIssueStampSheetLogRequest,
    ) -> result_.CountIssueStampSheetLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.count_issue_stamp_sheet_log(
            request,
        )
        return r

    def query_execute_stamp_sheet_log(
        self,
        request: request_.QueryExecuteStampSheetLogRequest,
    ) -> result_.QueryExecuteStampSheetLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.query_execute_stamp_sheet_log(
            request,
        )
        return r

    def count_execute_stamp_sheet_log(
        self,
        request: request_.CountExecuteStampSheetLogRequest,
    ) -> result_.CountExecuteStampSheetLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.count_execute_stamp_sheet_log(
            request,
        )
        return r

    def query_execute_stamp_task_log(
        self,
        request: request_.QueryExecuteStampTaskLogRequest,
    ) -> result_.QueryExecuteStampTaskLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.query_execute_stamp_task_log(
            request,
        )
        return r

    def count_execute_stamp_task_log(
        self,
        request: request_.CountExecuteStampTaskLogRequest,
    ) -> result_.CountExecuteStampTaskLogResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.count_execute_stamp_task_log(
            request,
        )
        return r
