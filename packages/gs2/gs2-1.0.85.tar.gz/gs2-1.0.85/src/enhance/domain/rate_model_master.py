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


class RateModelMasterDomain:
    _session: Gs2RestSession
    _client: Gs2EnhanceRestClient
    _rate_model_master_cache: RateModelMasterDomainCache
    _namespace_name: str
    _rate_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        rate_model_master_cache: RateModelMasterDomainCache,
        namespace_name: str,
        rate_name: str,
    ):
        self._session = session
        self._client = Gs2EnhanceRestClient(
            session,
        )
        self._rate_model_master_cache = rate_model_master_cache
        self._namespace_name = namespace_name
        self._rate_name = rate_name

    def load(
        self,
        request: request_.GetRateModelMasterRequest,
    ) -> result_.GetRateModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_rate_name(self._rate_name)
        r = self._client.get_rate_model_master(
            request,
        )
        self._rate_model_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateRateModelMasterRequest,
    ) -> result_.UpdateRateModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_rate_name(self._rate_name)
        r = self._client.update_rate_model_master(
            request,
        )
        self._rate_model_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteRateModelMasterRequest,
    ) -> result_.DeleteRateModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_rate_name(self._rate_name)
        r = self._client.delete_rate_model_master(
            request,
        )
        self._rate_model_master_cache.delete(r.item)
        return r
