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
from formation import Gs2FormationRestClient, request as request_, result as result_
from formation.domain.iterator.namespaces import DescribeNamespacesIterator
from formation.domain.iterator.form_model_masters import DescribeFormModelMastersIterator
from formation.domain.iterator.mold_models import DescribeMoldModelsIterator
from formation.domain.iterator.mold_model_masters import DescribeMoldModelMastersIterator
from formation.domain.iterator.molds import DescribeMoldsIterator
from formation.domain.iterator.molds_by_user_id import DescribeMoldsByUserIdIterator
from formation.domain.iterator.forms import DescribeFormsIterator
from formation.domain.iterator.forms_by_user_id import DescribeFormsByUserIdIterator
from formation.domain.cache.namespace import NamespaceDomainCache
from formation.domain.cache.form_model_master import FormModelMasterDomainCache
from formation.domain.cache.mold_model import MoldModelDomainCache
from formation.domain.cache.mold_model_master import MoldModelMasterDomainCache
from formation.domain.cache.mold import MoldDomainCache
from formation.domain.cache.form import FormDomainCache
from formation.domain.form import FormDomain
from formation.domain.form_access_token import FormAccessTokenDomain
from formation.domain.form_access_token import FormAccessTokenDomain


class MoldDomain:
    _session: Gs2RestSession
    _client: Gs2FormationRestClient
    _mold_cache: MoldDomainCache
    _namespace_name: str
    _user_id: str
    _mold_name: str
    _form_cache: FormDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        mold_cache: MoldDomainCache,
        namespace_name: str,
        user_id: str,
        mold_name: str,
    ):
        self._session = session
        self._client = Gs2FormationRestClient(
            session,
        )
        self._mold_cache = mold_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._mold_name = mold_name
        self._form_cache = FormDomainCache()

    def load(
        self,
        request: request_.GetMoldByUserIdRequest,
    ) -> result_.GetMoldByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        r = self._client.get_mold_by_user_id(
            request,
        )
        self._mold_cache.update(r.item)
        return r

    def set_capacity(
        self,
        request: request_.SetMoldCapacityByUserIdRequest,
    ) -> result_.SetMoldCapacityByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        r = self._client.set_mold_capacity_by_user_id(
            request,
        )
        self._mold_cache.update(r.item)
        return r

    def add_capacity(
        self,
        request: request_.AddMoldCapacityByUserIdRequest,
    ) -> result_.AddMoldCapacityByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        r = self._client.add_mold_capacity_by_user_id(
            request,
        )
        self._mold_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteMoldByUserIdRequest,
    ) -> result_.DeleteMoldByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        r = self._client.delete_mold_by_user_id(
            request,
        )
        self._mold_cache.delete(r.item)
        return r

    def forms(
        self,
    ) -> DescribeFormsByUserIdIterator:
        return DescribeFormsByUserIdIterator(
            self._form_cache,
            self._client,
            self._namespace_name,
            self._mold_name,
            self._user_id,
        )

    def form(
        self,
        index: int,
    ) -> FormDomain:
        return FormDomain(
            self._session,
            self._form_cache,
            self._namespace_name,
            self._user_id,
            self._mold_name,
            index,
        )
