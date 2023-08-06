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


class RecoverValueTableMasterDomain:
    _session: Gs2RestSession
    _client: Gs2StaminaRestClient
    _recover_value_table_master_cache: RecoverValueTableMasterDomainCache
    _namespace_name: str
    _recover_value_table_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        recover_value_table_master_cache: RecoverValueTableMasterDomainCache,
        namespace_name: str,
        recover_value_table_name: str,
    ):
        self._session = session
        self._client = Gs2StaminaRestClient(
            session,
        )
        self._recover_value_table_master_cache = recover_value_table_master_cache
        self._namespace_name = namespace_name
        self._recover_value_table_name = recover_value_table_name

    def load(
        self,
        request: request_.GetRecoverValueTableMasterRequest,
    ) -> result_.GetRecoverValueTableMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_recover_value_table_name(self._recover_value_table_name)
        r = self._client.get_recover_value_table_master(
            request,
        )
        self._recover_value_table_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateRecoverValueTableMasterRequest,
    ) -> result_.UpdateRecoverValueTableMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_recover_value_table_name(self._recover_value_table_name)
        r = self._client.update_recover_value_table_master(
            request,
        )
        self._recover_value_table_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteRecoverValueTableMasterRequest,
    ) -> result_.DeleteRecoverValueTableMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_recover_value_table_name(self._recover_value_table_name)
        r = self._client.delete_recover_value_table_master(
            request,
        )
        self._recover_value_table_master_cache.delete(r.item)
        return r
