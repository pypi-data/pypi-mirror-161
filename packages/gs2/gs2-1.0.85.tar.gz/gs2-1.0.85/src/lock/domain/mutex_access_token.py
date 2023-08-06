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
from lock import Gs2LockRestClient, request as request_, result as result_
from lock.domain.iterator.namespaces import DescribeNamespacesIterator
from lock.domain.iterator.mutexes import DescribeMutexesIterator
from lock.domain.iterator.mutexes_by_user_id import DescribeMutexesByUserIdIterator
from lock.domain.cache.namespace import NamespaceDomainCache
from lock.domain.cache.mutex import MutexDomainCache


class MutexAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2LockRestClient
    _mutex_cache: MutexDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _property_id: str

    def __init__(
        self,
        session: Gs2RestSession,
        mutex_cache: MutexDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        property_id: str,
    ):
        self._session = session
        self._client = Gs2LockRestClient(
            session,
        )
        self._mutex_cache = mutex_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._property_id = property_id

    def lock(
        self,
        request: request_.LockRequest,
    ) -> result_.LockResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_property_id(self._property_id)
        r = self._client.lock(
            request,
        )
        self._mutex_cache.update(r.item)
        return r

    def unlock(
        self,
        request: request_.UnlockRequest,
    ) -> result_.UnlockResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_property_id(self._property_id)
        r = self._client.unlock(
            request,
        )
        self._mutex_cache.update(r.item)
        return r

    def load(
        self,
        request: request_.GetMutexRequest,
    ) -> result_.GetMutexResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_property_id(self._property_id)
        r = self._client.get_mutex(
            request,
        )
        self._mutex_cache.update(r.item)
        return r
