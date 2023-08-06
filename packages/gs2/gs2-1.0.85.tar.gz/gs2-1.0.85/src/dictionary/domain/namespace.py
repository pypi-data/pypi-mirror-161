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
from dictionary import Gs2DictionaryRestClient, request as request_, result as result_
from dictionary.domain.iterator.namespaces import DescribeNamespacesIterator
from dictionary.domain.iterator.entry_models import DescribeEntryModelsIterator
from dictionary.domain.iterator.entry_model_masters import DescribeEntryModelMastersIterator
from dictionary.domain.iterator.entries import DescribeEntriesIterator
from dictionary.domain.iterator.entries_by_user_id import DescribeEntriesByUserIdIterator
from dictionary.domain.cache.namespace import NamespaceDomainCache
from dictionary.domain.cache.entry_model import EntryModelDomainCache
from dictionary.domain.cache.entry_model_master import EntryModelMasterDomainCache
from dictionary.domain.cache.entry import EntryDomainCache
from dictionary.domain.current_entry_master import CurrentEntryMasterDomain
from dictionary.domain.entry_model import EntryModelDomain
from dictionary.domain.user import UserDomain
from dictionary.domain.user_access_token import UserAccessTokenDomain
from dictionary.domain.user_access_token import UserAccessTokenDomain
from dictionary.domain.entry_model_master import EntryModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2DictionaryRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _entry_model_cache: EntryModelDomainCache
    _entry_model_master_cache: EntryModelMasterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2DictionaryRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._entry_model_cache = EntryModelDomainCache()
        self._entry_model_master_cache = EntryModelMasterDomainCache()

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

    def create_entry_model_master(
        self,
        request: request_.CreateEntryModelMasterRequest,
    ) -> result_.CreateEntryModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_entry_model_master(
            request,
        )
        return r

    def entry_models(
        self,
    ) -> DescribeEntryModelsIterator:
        return DescribeEntryModelsIterator(
            self._entry_model_cache,
            self._client,
            self._namespace_name,
        )

    def entry_model_masters(
        self,
    ) -> DescribeEntryModelMastersIterator:
        return DescribeEntryModelMastersIterator(
            self._entry_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def current_entry_master(
        self,
    ) -> CurrentEntryMasterDomain:
        return CurrentEntryMasterDomain(
            self._session,
            self._namespace_name,
        )

    def entry_model(
        self,
        entry_name: str,
    ) -> EntryModelDomain:
        return EntryModelDomain(
            self._session,
            self._entry_model_cache,
            self._namespace_name,
            entry_name,
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

    def entry_model_master(
        self,
        entry_name: str,
    ) -> EntryModelMasterDomain:
        return EntryModelMasterDomain(
            self._session,
            self._entry_model_master_cache,
            self._namespace_name,
            entry_name,
        )
