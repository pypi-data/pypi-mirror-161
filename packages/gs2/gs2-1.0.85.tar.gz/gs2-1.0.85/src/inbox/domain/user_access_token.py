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
from inbox import Gs2InboxRestClient, request as request_, result as result_
from inbox.domain.iterator.namespaces import DescribeNamespacesIterator
from inbox.domain.iterator.messages import DescribeMessagesIterator
from inbox.domain.iterator.messages_by_user_id import DescribeMessagesByUserIdIterator
from inbox.domain.iterator.global_message_masters import DescribeGlobalMessageMastersIterator
from inbox.domain.iterator.global_messages import DescribeGlobalMessagesIterator
from inbox.domain.cache.namespace import NamespaceDomainCache
from inbox.domain.cache.message import MessageDomainCache
from inbox.domain.cache.global_message_master import GlobalMessageMasterDomainCache
from inbox.domain.cache.global_message import GlobalMessageDomainCache
from inbox.domain.message import MessageDomain
from inbox.domain.message_access_token import MessageAccessTokenDomain
from inbox.domain.message_access_token import MessageAccessTokenDomain
from inbox.domain.received import ReceivedDomain
from inbox.domain.received_access_token import ReceivedAccessTokenDomain
from inbox.domain.received_access_token import ReceivedAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2InboxRestClient
    _namespace_name: str
    _access_token: AccessToken
    _message_cache: MessageDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2InboxRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._message_cache = MessageDomainCache()

    def receive_global_message(
        self,
        request: request_.ReceiveGlobalMessageRequest,
    ) -> result_.ReceiveGlobalMessageResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.receive_global_message(
            request,
        )
        return r

    def messages(
        self,
    ) -> DescribeMessagesIterator:
        return DescribeMessagesIterator(
            self._message_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def message(
        self,
        message_name: str,
    ) -> MessageAccessTokenDomain:
        return MessageAccessTokenDomain(
            self._session,
            self._message_cache,
            self._namespace_name,
            self._access_token,
            message_name,
        )

    def received(
        self,
    ) -> ReceivedAccessTokenDomain:
        return ReceivedAccessTokenDomain(
            self._session,
            self._namespace_name,
            self._access_token,
        )
