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
from gateway import Gs2GatewayRestClient, request as request_, result as result_
from gateway.domain.iterator.namespaces import DescribeNamespacesIterator
from gateway.domain.iterator.web_socket_sessions import DescribeWebSocketSessionsIterator
from gateway.domain.iterator.web_socket_sessions_by_user_id import DescribeWebSocketSessionsByUserIdIterator
from gateway.domain.cache.namespace import NamespaceDomainCache
from gateway.domain.cache.web_socket_session import WebSocketSessionDomainCache
from gateway.domain.web_socket_session import WebSocketSessionDomain
from gateway.domain.web_socket_session_access_token import WebSocketSessionAccessTokenDomain
from gateway.domain.web_socket_session_access_token import WebSocketSessionAccessTokenDomain
from gateway.domain.firebase_token import FirebaseTokenDomain
from gateway.domain.firebase_token_access_token import FirebaseTokenAccessTokenDomain
from gateway.domain.firebase_token_access_token import FirebaseTokenAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2GatewayRestClient
    _namespace_name: str
    _access_token: AccessToken
    _web_socket_session_cache: WebSocketSessionDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2GatewayRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._web_socket_session_cache = WebSocketSessionDomainCache()

    def web_socket_sessions(
        self,
    ) -> DescribeWebSocketSessionsIterator:
        return DescribeWebSocketSessionsIterator(
            self._web_socket_session_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def web_socket_session(
        self,
    ) -> WebSocketSessionAccessTokenDomain:
        return WebSocketSessionAccessTokenDomain(
            self._session,
            self._web_socket_session_cache,
            self._namespace_name,
            self._access_token,
        )

    def firebase_token(
        self,
    ) -> FirebaseTokenAccessTokenDomain:
        return FirebaseTokenAccessTokenDomain(
            self._session,
            self._namespace_name,
            self._access_token,
        )
