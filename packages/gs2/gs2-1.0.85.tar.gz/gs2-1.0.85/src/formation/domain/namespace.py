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
from formation.domain.current_form_master import CurrentFormMasterDomain
from formation.domain.mold_model import MoldModelDomain
from formation.domain.user import UserDomain
from formation.domain.user_access_token import UserAccessTokenDomain
from formation.domain.user_access_token import UserAccessTokenDomain
from formation.domain.form_model_master import FormModelMasterDomain
from formation.domain.mold_model_master import MoldModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2FormationRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _form_model_master_cache: FormModelMasterDomainCache
    _mold_model_cache: MoldModelDomainCache
    _mold_model_master_cache: MoldModelMasterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2FormationRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._form_model_master_cache = FormModelMasterDomainCache()
        self._mold_model_cache = MoldModelDomainCache()
        self._mold_model_master_cache = MoldModelMasterDomainCache()

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

    def create_form_model_master(
        self,
        request: request_.CreateFormModelMasterRequest,
    ) -> result_.CreateFormModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_form_model_master(
            request,
        )
        return r

    def create_mold_model_master(
        self,
        request: request_.CreateMoldModelMasterRequest,
    ) -> result_.CreateMoldModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_mold_model_master(
            request,
        )
        return r

    def form_model_masters(
        self,
    ) -> DescribeFormModelMastersIterator:
        return DescribeFormModelMastersIterator(
            self._form_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def mold_models(
        self,
    ) -> DescribeMoldModelsIterator:
        return DescribeMoldModelsIterator(
            self._mold_model_cache,
            self._client,
            self._namespace_name,
        )

    def mold_model_masters(
        self,
    ) -> DescribeMoldModelMastersIterator:
        return DescribeMoldModelMastersIterator(
            self._mold_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def current_form_master(
        self,
    ) -> CurrentFormMasterDomain:
        return CurrentFormMasterDomain(
            self._session,
            self._namespace_name,
        )

    def mold_model(
        self,
        mold_name: str,
    ) -> MoldModelDomain:
        return MoldModelDomain(
            self._session,
            self._mold_model_cache,
            self._namespace_name,
            mold_name,
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

    def form_model_master(
        self,
        form_model_name: str,
    ) -> FormModelMasterDomain:
        return FormModelMasterDomain(
            self._session,
            self._form_model_master_cache,
            self._namespace_name,
            form_model_name,
        )

    def mold_model_master(
        self,
        mold_name: str,
    ) -> MoldModelMasterDomain:
        return MoldModelMasterDomain(
            self._session,
            self._mold_model_master_cache,
            self._namespace_name,
            mold_name,
        )
