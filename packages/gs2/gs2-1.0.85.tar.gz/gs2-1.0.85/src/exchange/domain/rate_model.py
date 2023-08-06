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
from exchange import Gs2ExchangeRestClient, request as request_, result as result_
from exchange.domain.iterator.namespaces import DescribeNamespacesIterator
from exchange.domain.iterator.rate_models import DescribeRateModelsIterator
from exchange.domain.iterator.rate_model_masters import DescribeRateModelMastersIterator
from exchange.domain.iterator.awaits import DescribeAwaitsIterator
from exchange.domain.iterator.awaits_by_user_id import DescribeAwaitsByUserIdIterator
from exchange.domain.cache.namespace import NamespaceDomainCache
from exchange.domain.cache.rate_model import RateModelDomainCache
from exchange.domain.cache.rate_model_master import RateModelMasterDomainCache
from exchange.domain.cache.await_ import AwaitDomainCache


class RateModelDomain:
    _session: Gs2RestSession
    _client: Gs2ExchangeRestClient
    _rate_model_cache: RateModelDomainCache
    _namespace_name: str
    _rate_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        rate_model_cache: RateModelDomainCache,
        namespace_name: str,
        rate_name: str,
    ):
        self._session = session
        self._client = Gs2ExchangeRestClient(
            session,
        )
        self._rate_model_cache = rate_model_cache
        self._namespace_name = namespace_name
        self._rate_name = rate_name

    def load(
        self,
        request: request_.GetRateModelRequest,
    ) -> result_.GetRateModelResult:
        request.with_namespace_name(self._namespace_name)
        request.with_rate_name(self._rate_name)
        r = self._client.get_rate_model(
            request,
        )
        self._rate_model_cache.update(r.item)
        return r
