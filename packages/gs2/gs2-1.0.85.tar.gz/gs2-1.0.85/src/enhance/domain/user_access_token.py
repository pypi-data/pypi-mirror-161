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
from enhance import Gs2EnhanceRestClient, request as request_, result as result_
from enhance.domain.iterator.namespaces import DescribeNamespacesIterator
from enhance.domain.iterator.rate_models import DescribeRateModelsIterator
from enhance.domain.iterator.rate_model_masters import DescribeRateModelMastersIterator
from enhance.domain.iterator.progresses_by_user_id import DescribeProgressesByUserIdIterator
from enhance.domain.cache.namespace import NamespaceDomainCache
from enhance.domain.cache.rate_model import RateModelDomainCache
from enhance.domain.cache.rate_model_master import RateModelMasterDomainCache
from enhance.domain.cache.progress import ProgressDomainCache
from enhance.domain.progress import ProgressDomain
from enhance.domain.progress_access_token import ProgressAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2EnhanceRestClient
    _namespace_name: str
    _access_token: AccessToken
    _progress_cache: ProgressDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2EnhanceRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._progress_cache = ProgressDomainCache()

    def direct_enhance(
        self,
        request: request_.DirectEnhanceRequest,
    ) -> result_.DirectEnhanceResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.direct_enhance(
            request,
        )
        return r

    def start(
        self,
        request: request_.StartRequest,
    ) -> result_.StartResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.start(
            request,
        )
        return r

    def end(
        self,
        request: request_.EndRequest,
    ) -> result_.EndResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.end(
            request,
        )
        return r

    def delete_progress(
        self,
        request: request_.DeleteProgressRequest,
    ) -> result_.DeleteProgressResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.delete_progress(
            request,
        )
        return r

    def progress(
        self,
    ) -> ProgressAccessTokenDomain:
        return ProgressAccessTokenDomain(
            self._session,
            self._progress_cache,
            self._namespace_name,
            self._access_token,
        )
