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


class FirebaseTokenAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2GatewayRestClient
    _namespace_name: str
    _access_token: AccessToken

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

    def set(
        self,
        request: request_.SetFirebaseTokenRequest,
    ) -> result_.SetFirebaseTokenResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.set_firebase_token(
            request,
        )
        return r

    def load(
        self,
        request: request_.GetFirebaseTokenRequest,
    ) -> result_.GetFirebaseTokenResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.get_firebase_token(
            request,
        )
        return r

    def delete(
        self,
        request: request_.DeleteFirebaseTokenRequest,
    ) -> result_.DeleteFirebaseTokenResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.delete_firebase_token(
            request,
        )
        return r
