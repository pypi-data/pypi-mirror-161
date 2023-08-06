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
from realtime import Gs2RealtimeRestClient, request as request_, result as result_
from realtime.domain.iterator.namespaces import DescribeNamespacesIterator
from realtime.domain.iterator.rooms import DescribeRoomsIterator
from realtime.domain.cache.namespace import NamespaceDomainCache
from realtime.domain.cache.room import RoomDomainCache
from realtime.domain.room import RoomDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2RealtimeRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _room_cache: RoomDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2RealtimeRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._room_cache = RoomDomainCache()

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

    def rooms(
        self,
    ) -> DescribeRoomsIterator:
        return DescribeRoomsIterator(
            self._room_cache,
            self._client,
            self._namespace_name,
        )

    def room(
        self,
        room_name: str,
    ) -> RoomDomain:
        return RoomDomain(
            self._session,
            self._room_cache,
            self._namespace_name,
            room_name,
        )
