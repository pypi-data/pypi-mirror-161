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
from lock.domain.mutex import MutexDomain
from lock.domain.mutex_access_token import MutexAccessTokenDomain
from lock.domain.mutex_access_token import MutexAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2LockRestClient
    _namespace_name: str
    _user_id: str
    _mutex_cache: MutexDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2LockRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._mutex_cache = MutexDomainCache()

    def mutexes(
        self,
    ) -> DescribeMutexesByUserIdIterator:
        return DescribeMutexesByUserIdIterator(
            self._mutex_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def mutex(
        self,
        property_id: str,
    ) -> MutexDomain:
        return MutexDomain(
            self._session,
            self._mutex_cache,
            self._namespace_name,
            self._user_id,
            property_id,
        )
