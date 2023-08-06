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
from datastore.domain.data_object import DataObjectDomain
from datastore.domain.data_object_access_token import DataObjectAccessTokenDomain
from datastore.domain.data_object_access_token import DataObjectAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2DatastoreRestClient
    _namespace_name: str
    _access_token: AccessToken
    _data_object_cache: DataObjectDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2DatastoreRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._data_object_cache = DataObjectDomainCache()

    def prepare_upload(
        self,
        request: request_.PrepareUploadRequest,
    ) -> result_.PrepareUploadResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.prepare_upload(
            request,
        )
        return r

    def prepare_re_upload(
        self,
        request: request_.PrepareReUploadRequest,
    ) -> result_.PrepareReUploadResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.prepare_re_upload(
            request,
        )
        return r

    def prepare_download(
        self,
        request: request_.PrepareDownloadRequest,
    ) -> result_.PrepareDownloadResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.prepare_download(
            request,
        )
        return r

    def prepare_download_by_generation(
        self,
        request: request_.PrepareDownloadByGenerationRequest,
    ) -> result_.PrepareDownloadByGenerationResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.prepare_download_by_generation(
            request,
        )
        return r

    def prepare_download_own_data(
        self,
        request: request_.PrepareDownloadOwnDataRequest,
    ) -> result_.PrepareDownloadOwnDataResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.prepare_download_own_data(
            request,
        )
        return r

    def prepare_download_own_data_by_generation(
        self,
        request: request_.PrepareDownloadOwnDataByGenerationRequest,
    ) -> result_.PrepareDownloadOwnDataByGenerationResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.prepare_download_own_data_by_generation(
            request,
        )
        return r

    def data_objects(
        self,
        status: str,
    ) -> DescribeDataObjectsIterator:
        return DescribeDataObjectsIterator(
            self._data_object_cache,
            self._client,
            self._namespace_name,
            self._access_token,
            status,
        )

    def data_object(
        self,
        data_object_name: str,
    ) -> DataObjectAccessTokenDomain:
        return DataObjectAccessTokenDomain(
            self._session,
            self._data_object_cache,
            self._namespace_name,
            self._access_token,
            data_object_name,
        )
