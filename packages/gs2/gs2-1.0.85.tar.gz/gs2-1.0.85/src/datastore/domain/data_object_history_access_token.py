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
from datastore import Gs2DatastoreRestClient, request as request_, result as result_
from datastore.domain.iterator.namespaces import DescribeNamespacesIterator
from datastore.domain.iterator.data_objects import DescribeDataObjectsIterator
from datastore.domain.iterator.data_objects_by_user_id import DescribeDataObjectsByUserIdIterator
from datastore.domain.iterator.data_object_histories import DescribeDataObjectHistoriesIterator
from datastore.domain.iterator.data_object_histories_by_user_id import DescribeDataObjectHistoriesByUserIdIterator
from datastore.domain.cache.namespace import NamespaceDomainCache
from datastore.domain.cache.data_object import DataObjectDomainCache
from datastore.domain.cache.data_object_history import DataObjectHistoryDomainCache


class DataObjectHistoryAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2DatastoreRestClient
    _data_object_history_cache: DataObjectHistoryDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _data_object_name: str
    _generation: str

    def __init__(
        self,
        session: Gs2RestSession,
        data_object_history_cache: DataObjectHistoryDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        data_object_name: str,
        generation: str,
    ):
        self._session = session
        self._client = Gs2DatastoreRestClient(
            session,
        )
        self._data_object_history_cache = data_object_history_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._data_object_name = data_object_name
        self._generation = generation

    def load(
        self,
        request: request_.GetDataObjectHistoryRequest,
    ) -> result_.GetDataObjectHistoryResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_data_object_name(self._data_object_name)
        request.with_generation(self._generation)
        r = self._client.get_data_object_history(
            request,
        )
        self._data_object_history_cache.update(r.item)
        return r
