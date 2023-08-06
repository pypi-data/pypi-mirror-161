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
from news import Gs2NewsRestClient, request as request_, result as result_
from news.domain.iterator.namespaces import DescribeNamespacesIterator
from news.domain.iterator.news import DescribeNewsIterator
from news.domain.iterator.news_by_user_id import DescribeNewsByUserIdIterator
from news.domain.cache.namespace import NamespaceDomainCache
from news.domain.cache.news import NewsDomainCache


class CurrentNewsMasterDomain:
    _session: Gs2RestSession
    _client: Gs2NewsRestClient
    _namespace_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2NewsRestClient(
            session,
        )
        self._namespace_name = namespace_name

    def prepare_update(
        self,
        request: request_.PrepareUpdateCurrentNewsMasterRequest,
    ) -> result_.PrepareUpdateCurrentNewsMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.prepare_update_current_news_master(
            request,
        )
        return r

    def update(
        self,
        request: request_.UpdateCurrentNewsMasterRequest,
    ) -> result_.UpdateCurrentNewsMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_news_master(
            request,
        )
        return r

    def prepare_update_from_git_hub(
        self,
        request: request_.PrepareUpdateCurrentNewsMasterFromGitHubRequest,
    ) -> result_.PrepareUpdateCurrentNewsMasterFromGitHubResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.prepare_update_current_news_master_from_git_hub(
            request,
        )
        return r
