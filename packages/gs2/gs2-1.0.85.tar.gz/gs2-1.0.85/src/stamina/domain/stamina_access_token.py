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
from stamina import Gs2StaminaRestClient, request as request_, result as result_
from stamina.domain.iterator.namespaces import DescribeNamespacesIterator
from stamina.domain.iterator.stamina_model_masters import DescribeStaminaModelMastersIterator
from stamina.domain.iterator.max_stamina_table_masters import DescribeMaxStaminaTableMastersIterator
from stamina.domain.iterator.recover_interval_table_masters import DescribeRecoverIntervalTableMastersIterator
from stamina.domain.iterator.recover_value_table_masters import DescribeRecoverValueTableMastersIterator
from stamina.domain.iterator.stamina_models import DescribeStaminaModelsIterator
from stamina.domain.iterator.staminas import DescribeStaminasIterator
from stamina.domain.iterator.staminas_by_user_id import DescribeStaminasByUserIdIterator
from stamina.domain.cache.namespace import NamespaceDomainCache
from stamina.domain.cache.stamina_model_master import StaminaModelMasterDomainCache
from stamina.domain.cache.max_stamina_table_master import MaxStaminaTableMasterDomainCache
from stamina.domain.cache.recover_interval_table_master import RecoverIntervalTableMasterDomainCache
from stamina.domain.cache.recover_value_table_master import RecoverValueTableMasterDomainCache
from stamina.domain.cache.stamina_model import StaminaModelDomainCache
from stamina.domain.cache.stamina import StaminaDomainCache


class StaminaAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2StaminaRestClient
    _stamina_cache: StaminaDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _stamina_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        stamina_cache: StaminaDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        stamina_name: str,
    ):
        self._session = session
        self._client = Gs2StaminaRestClient(
            session,
        )
        self._stamina_cache = stamina_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._stamina_name = stamina_name

    def load(
        self,
        request: request_.GetStaminaRequest,
    ) -> result_.GetStaminaResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_stamina_name(self._stamina_name)
        r = self._client.get_stamina(
            request,
        )
        self._stamina_cache.update(r.item)
        return r

    def consume(
        self,
        request: request_.ConsumeStaminaRequest,
    ) -> result_.ConsumeStaminaResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_stamina_name(self._stamina_name)
        r = self._client.consume_stamina(
            request,
        )
        self._stamina_cache.update(r.item)
        return r

    def set_max_value_by_status(
        self,
        request: request_.SetMaxValueByStatusRequest,
    ) -> result_.SetMaxValueByStatusResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_stamina_name(self._stamina_name)
        r = self._client.set_max_value_by_status(
            request,
        )
        self._stamina_cache.update(r.item)
        return r

    def set_recover_interval_by_status(
        self,
        request: request_.SetRecoverIntervalByStatusRequest,
    ) -> result_.SetRecoverIntervalByStatusResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_stamina_name(self._stamina_name)
        r = self._client.set_recover_interval_by_status(
            request,
        )
        self._stamina_cache.update(r.item)
        return r

    def set_recover_value_by_status(
        self,
        request: request_.SetRecoverValueByStatusRequest,
    ) -> result_.SetRecoverValueByStatusResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_stamina_name(self._stamina_name)
        r = self._client.set_recover_value_by_status(
            request,
        )
        self._stamina_cache.update(r.item)
        return r
