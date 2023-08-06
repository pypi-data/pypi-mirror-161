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


class FormDomain:
    _session: Gs2RestSession
    _client: Gs2FormationRestClient
    _form_cache: FormDomainCache
    _namespace_name: str
    _user_id: str
    _mold_name: str
    _index: int

    def __init__(
        self,
        session: Gs2RestSession,
        form_cache: FormDomainCache,
        namespace_name: str,
        user_id: str,
        mold_name: str,
        index: int,
    ):
        self._session = session
        self._client = Gs2FormationRestClient(
            session,
        )
        self._form_cache = form_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._mold_name = mold_name
        self._index = index

    def load(
        self,
        request: request_.GetFormByUserIdRequest,
    ) -> result_.GetFormByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        request.with_index(self._index)
        r = self._client.get_form_by_user_id(
            request,
        )
        self._form_cache.update(r.item)
        return r

    def get_with_signature(
        self,
        request: request_.GetFormWithSignatureByUserIdRequest,
    ) -> result_.GetFormWithSignatureByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        request.with_index(self._index)
        r = self._client.get_form_with_signature_by_user_id(
            request,
        )
        self._form_cache.update(r.item)
        return r

    def set(
        self,
        request: request_.SetFormByUserIdRequest,
    ) -> result_.SetFormByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        request.with_index(self._index)
        r = self._client.set_form_by_user_id(
            request,
        )
        self._form_cache.update(r.item)
        return r

    def acquire_actions_to_properties(
        self,
        request: request_.AcquireActionsToFormPropertiesRequest,
    ) -> result_.AcquireActionsToFormPropertiesResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        request.with_index(self._index)
        r = self._client.acquire_actions_to_form_properties(
            request,
        )
        self._form_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteFormByUserIdRequest,
    ) -> result_.DeleteFormByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_mold_name(self._mold_name)
        request.with_index(self._index)
        r = self._client.delete_form_by_user_id(
            request,
        )
        self._form_cache.delete(r.item)
        return r
