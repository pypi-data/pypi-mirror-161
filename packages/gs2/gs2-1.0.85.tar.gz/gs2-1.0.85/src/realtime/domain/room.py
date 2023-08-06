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


class RoomDomain:
    _session: Gs2RestSession
    _client: Gs2RealtimeRestClient
    _room_cache: RoomDomainCache
    _namespace_name: str
    _room_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        room_cache: RoomDomainCache,
        namespace_name: str,
        room_name: str,
    ):
        self._session = session
        self._client = Gs2RealtimeRestClient(
            session,
        )
        self._room_cache = room_cache
        self._namespace_name = namespace_name
        self._room_name = room_name

    def load(
        self,
        request: request_.GetRoomRequest,
    ) -> result_.GetRoomResult:
        request.with_namespace_name(self._namespace_name)
        request.with_room_name(self._room_name)
        r = self._client.get_room(
            request,
        )
        self._room_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteRoomRequest,
    ) -> result_.DeleteRoomResult:
        request.with_namespace_name(self._namespace_name)
        request.with_room_name(self._room_name)
        r = self._client.delete_room(
            request,
        )
        self._room_cache.delete(r.item)
        return r
