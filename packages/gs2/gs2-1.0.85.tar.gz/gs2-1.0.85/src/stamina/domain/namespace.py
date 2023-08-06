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
from stamina.domain.current_stamina_master import CurrentStaminaMasterDomain
from stamina.domain.stamina_model import StaminaModelDomain
from stamina.domain.user import UserDomain
from stamina.domain.user_access_token import UserAccessTokenDomain
from stamina.domain.user_access_token import UserAccessTokenDomain
from stamina.domain.recover_interval_table_master import RecoverIntervalTableMasterDomain
from stamina.domain.max_stamina_table_master import MaxStaminaTableMasterDomain
from stamina.domain.recover_value_table_master import RecoverValueTableMasterDomain
from stamina.domain.stamina_model_master import StaminaModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2StaminaRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _stamina_model_master_cache: StaminaModelMasterDomainCache
    _max_stamina_table_master_cache: MaxStaminaTableMasterDomainCache
    _recover_interval_table_master_cache: RecoverIntervalTableMasterDomainCache
    _recover_value_table_master_cache: RecoverValueTableMasterDomainCache
    _stamina_model_cache: StaminaModelDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2StaminaRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._stamina_model_master_cache = StaminaModelMasterDomainCache()
        self._max_stamina_table_master_cache = MaxStaminaTableMasterDomainCache()
        self._recover_interval_table_master_cache = RecoverIntervalTableMasterDomainCache()
        self._recover_value_table_master_cache = RecoverValueTableMasterDomainCache()
        self._stamina_model_cache = StaminaModelDomainCache()

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

    def create_stamina_model_master(
        self,
        request: request_.CreateStaminaModelMasterRequest,
    ) -> result_.CreateStaminaModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_stamina_model_master(
            request,
        )
        return r

    def create_max_stamina_table_master(
        self,
        request: request_.CreateMaxStaminaTableMasterRequest,
    ) -> result_.CreateMaxStaminaTableMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_max_stamina_table_master(
            request,
        )
        return r

    def create_recover_interval_table_master(
        self,
        request: request_.CreateRecoverIntervalTableMasterRequest,
    ) -> result_.CreateRecoverIntervalTableMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_recover_interval_table_master(
            request,
        )
        return r

    def create_recover_value_table_master(
        self,
        request: request_.CreateRecoverValueTableMasterRequest,
    ) -> result_.CreateRecoverValueTableMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_recover_value_table_master(
            request,
        )
        return r

    def stamina_model_masters(
        self,
    ) -> DescribeStaminaModelMastersIterator:
        return DescribeStaminaModelMastersIterator(
            self._stamina_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def max_stamina_table_masters(
        self,
    ) -> DescribeMaxStaminaTableMastersIterator:
        return DescribeMaxStaminaTableMastersIterator(
            self._max_stamina_table_master_cache,
            self._client,
            self._namespace_name,
        )

    def recover_interval_table_masters(
        self,
    ) -> DescribeRecoverIntervalTableMastersIterator:
        return DescribeRecoverIntervalTableMastersIterator(
            self._recover_interval_table_master_cache,
            self._client,
            self._namespace_name,
        )

    def recover_value_table_masters(
        self,
    ) -> DescribeRecoverValueTableMastersIterator:
        return DescribeRecoverValueTableMastersIterator(
            self._recover_value_table_master_cache,
            self._client,
            self._namespace_name,
        )

    def stamina_models(
        self,
    ) -> DescribeStaminaModelsIterator:
        return DescribeStaminaModelsIterator(
            self._stamina_model_cache,
            self._client,
            self._namespace_name,
        )

    def current_stamina_master(
        self,
    ) -> CurrentStaminaMasterDomain:
        return CurrentStaminaMasterDomain(
            self._session,
            self._namespace_name,
        )

    def stamina_model(
        self,
        stamina_name: str,
    ) -> StaminaModelDomain:
        return StaminaModelDomain(
            self._session,
            self._stamina_model_cache,
            self._namespace_name,
            stamina_name,
        )

    def user(
        self,
        user_id: str,
    ) -> UserDomain:
        return UserDomain(
            self._session,
            self._namespace_name,
            user_id,
        )

    def access_token(
        self,
        access_token: AccessToken,
    ) -> UserAccessTokenDomain:
        return UserAccessTokenDomain(
            self._session,
            self._namespace_name,
            access_token,
        )

    def recover_interval_table_master(
        self,
        recover_interval_table_name: str,
    ) -> RecoverIntervalTableMasterDomain:
        return RecoverIntervalTableMasterDomain(
            self._session,
            self._recover_interval_table_master_cache,
            self._namespace_name,
            recover_interval_table_name,
        )

    def max_stamina_table_master(
        self,
        max_stamina_table_name: str,
    ) -> MaxStaminaTableMasterDomain:
        return MaxStaminaTableMasterDomain(
            self._session,
            self._max_stamina_table_master_cache,
            self._namespace_name,
            max_stamina_table_name,
        )

    def recover_value_table_master(
        self,
        recover_value_table_name: str,
    ) -> RecoverValueTableMasterDomain:
        return RecoverValueTableMasterDomain(
            self._session,
            self._recover_value_table_master_cache,
            self._namespace_name,
            recover_value_table_name,
        )

    def stamina_model_master(
        self,
        stamina_name: str,
    ) -> StaminaModelMasterDomain:
        return StaminaModelMasterDomain(
            self._session,
            self._stamina_model_master_cache,
            self._namespace_name,
            stamina_name,
        )
