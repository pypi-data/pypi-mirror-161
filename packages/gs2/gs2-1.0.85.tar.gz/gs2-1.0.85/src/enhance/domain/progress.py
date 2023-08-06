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


class ProgressDomain:
    _session: Gs2RestSession
    _client: Gs2EnhanceRestClient
    _progress_cache: ProgressDomainCache
    _namespace_name: str
    _user_id: str

    def __init__(
        self,
        session: Gs2RestSession,
        progress_cache: ProgressDomainCache,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2EnhanceRestClient(
            session,
        )
        self._progress_cache = progress_cache
        self._namespace_name = namespace_name
        self._user_id = user_id

    def load(
        self,
        request: request_.GetProgressByUserIdRequest,
    ) -> result_.GetProgressByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.get_progress_by_user_id(
            request,
        )
        self._progress_cache.update(r.item)
        return r

    def list(
        self,
    ) -> DescribeProgressesByUserIdIterator:
        return DescribeProgressesByUserIdIterator(
            self._progress_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )
