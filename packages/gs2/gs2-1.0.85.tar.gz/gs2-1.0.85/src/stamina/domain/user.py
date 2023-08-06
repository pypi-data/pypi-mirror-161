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
from stamina.domain.stamina import StaminaDomain
from stamina.domain.stamina_access_token import StaminaAccessTokenDomain
from stamina.domain.stamina_access_token import StaminaAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2StaminaRestClient
    _namespace_name: str
    _user_id: str
    _stamina_cache: StaminaDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2StaminaRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._stamina_cache = StaminaDomainCache()

    def staminas(
        self,
    ) -> DescribeStaminasByUserIdIterator:
        return DescribeStaminasByUserIdIterator(
            self._stamina_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def stamina(
        self,
        stamina_name: str,
    ) -> StaminaDomain:
        return StaminaDomain(
            self._session,
            self._stamina_cache,
            self._namespace_name,
            self._user_id,
            stamina_name,
        )
