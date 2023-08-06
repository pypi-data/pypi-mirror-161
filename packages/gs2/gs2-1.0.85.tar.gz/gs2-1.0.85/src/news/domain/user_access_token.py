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


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2NewsRestClient
    _namespace_name: str
    _access_token: AccessToken
    _news_cache: NewsDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2NewsRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._news_cache = NewsDomainCache()

    def want_grant(
        self,
        request: request_.WantGrantRequest,
    ) -> result_.WantGrantResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.want_grant(
            request,
        )
        return r

    def newses(
        self,
    ) -> DescribeNewsIterator:
        return DescribeNewsIterator(
            self._news_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )
