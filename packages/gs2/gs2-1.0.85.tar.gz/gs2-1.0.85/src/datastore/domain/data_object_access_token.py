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
from datastore.domain.data_object_history import DataObjectHistoryDomain
from datastore.domain.data_object_history_access_token import DataObjectHistoryAccessTokenDomain
from datastore.domain.data_object_history_access_token import DataObjectHistoryAccessTokenDomain


class DataObjectAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2DatastoreRestClient
    _data_object_cache: DataObjectDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _data_object_name: str
    _data_object_history_cache: DataObjectHistoryDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        data_object_cache: DataObjectDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        data_object_name: str,
    ):
        self._session = session
        self._client = Gs2DatastoreRestClient(
            session,
        )
        self._data_object_cache = data_object_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._data_object_name = data_object_name
        self._data_object_history_cache = DataObjectHistoryDomainCache()

    def update(
        self,
        request: request_.UpdateDataObjectRequest,
    ) -> result_.UpdateDataObjectResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_data_object_name(self._data_object_name)
        r = self._client.update_data_object(
            request,
        )
        self._data_object_cache.update(r.item)
        return r

    def done_upload(
        self,
        request: request_.DoneUploadRequest,
    ) -> result_.DoneUploadResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_data_object_name(self._data_object_name)
        r = self._client.done_upload(
            request,
        )
        self._data_object_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteDataObjectRequest,
    ) -> result_.DeleteDataObjectResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_data_object_name(self._data_object_name)
        r = self._client.delete_data_object(
            request,
        )
        self._data_object_cache.delete(r.item)
        return r

    def data_object_histories(
        self,
    ) -> DescribeDataObjectHistoriesIterator:
        return DescribeDataObjectHistoriesIterator(
            self._data_object_history_cache,
            self._client,
            self._namespace_name,
            self._access_token,
            self._data_object_name,
        )

    def data_object_history(
        self,
        generation: str,
    ) -> DataObjectHistoryAccessTokenDomain:
        return DataObjectHistoryAccessTokenDomain(
            self._session,
            self._data_object_history_cache,
            self._namespace_name,
            self._access_token,
            self._data_object_name,
            generation,
        )
