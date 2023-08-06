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


class EntryModelMasterDomain:
    _session: Gs2RestSession
    _client: Gs2DictionaryRestClient
    _entry_model_master_cache: EntryModelMasterDomainCache
    _namespace_name: str
    _entry_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        entry_model_master_cache: EntryModelMasterDomainCache,
        namespace_name: str,
        entry_name: str,
    ):
        self._session = session
        self._client = Gs2DictionaryRestClient(
            session,
        )
        self._entry_model_master_cache = entry_model_master_cache
        self._namespace_name = namespace_name
        self._entry_name = entry_name

    def load(
        self,
        request: request_.GetEntryModelMasterRequest,
    ) -> result_.GetEntryModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_entry_name(self._entry_name)
        r = self._client.get_entry_model_master(
            request,
        )
        self._entry_model_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateEntryModelMasterRequest,
    ) -> result_.UpdateEntryModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_entry_name(self._entry_name)
        r = self._client.update_entry_model_master(
            request,
        )
        self._entry_model_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteEntryModelMasterRequest,
    ) -> result_.DeleteEntryModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_entry_name(self._entry_name)
        r = self._client.delete_entry_model_master(
            request,
        )
        self._entry_model_master_cache.delete(r.item)
        return r
