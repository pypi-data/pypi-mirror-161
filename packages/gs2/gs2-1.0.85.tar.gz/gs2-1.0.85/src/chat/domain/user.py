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
from chat import Gs2ChatRestClient, request as request_, result as result_
from chat.domain.iterator.namespaces import DescribeNamespacesIterator
from chat.domain.iterator.rooms import DescribeRoomsIterator
from chat.domain.iterator.messages import DescribeMessagesIterator
from chat.domain.iterator.messages_by_user_id import DescribeMessagesByUserIdIterator
from chat.domain.iterator.subscribes import DescribeSubscribesIterator
from chat.domain.iterator.subscribes_by_user_id import DescribeSubscribesByUserIdIterator
from chat.domain.iterator.subscribes_by_room_name import DescribeSubscribesByRoomNameIterator
from chat.domain.cache.namespace import NamespaceDomainCache
from chat.domain.cache.room import RoomDomainCache
from chat.domain.cache.message import MessageDomainCache
from chat.domain.cache.subscribe import SubscribeDomainCache
from chat.domain.room import RoomDomain
from chat.domain.room_access_token import RoomAccessTokenDomain
from chat.domain.room_access_token import RoomAccessTokenDomain
from chat.domain.subscribe import SubscribeDomain
from chat.domain.subscribe_access_token import SubscribeAccessTokenDomain
from chat.domain.subscribe_access_token import SubscribeAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2ChatRestClient
    _namespace_name: str
    _user_id: str
    _room_cache: RoomDomainCache
    _subscribe_cache: SubscribeDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2ChatRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._room_cache = RoomDomainCache()
        self._subscribe_cache = SubscribeDomainCache()

    def create_room_from_backend(
        self,
        request: request_.CreateRoomFromBackendRequest,
    ) -> result_.CreateRoomFromBackendResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.create_room_from_backend(
            request,
        )
        return r

    def rooms(
        self,
    ) -> DescribeRoomsIterator:
        return DescribeRoomsIterator(
            self._room_cache,
            self._client,
            self._namespace_name,
        )

    def subscribes(
        self,
    ) -> DescribeSubscribesByUserIdIterator:
        return DescribeSubscribesByUserIdIterator(
            self._subscribe_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def room(
        self,
        room_name: str,
        password: str,
    ) -> RoomDomain:
        return RoomDomain(
            self._session,
            self._room_cache,
            self._namespace_name,
            self._user_id,
            room_name,
            password,
        )

    def subscribe(
        self,
        room_name: str,
    ) -> SubscribeDomain:
        return SubscribeDomain(
            self._session,
            self._subscribe_cache,
            self._namespace_name,
            self._user_id,
            room_name,
        )
