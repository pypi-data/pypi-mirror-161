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


class GlobalMessageDomain:
    _session: Gs2RestSession
    _client: Gs2InboxRestClient
    _global_message_cache: GlobalMessageDomainCache
    _namespace_name: str
    _global_message_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        global_message_cache: GlobalMessageDomainCache,
        namespace_name: str,
        global_message_name: str,
    ):
        self._session = session
        self._client = Gs2InboxRestClient(
            session,
        )
        self._global_message_cache = global_message_cache
        self._namespace_name = namespace_name
        self._global_message_name = global_message_name

    def load(
        self,
        request: request_.GetGlobalMessageRequest,
    ) -> result_.GetGlobalMessageResult:
        request.with_namespace_name(self._namespace_name)
        request.with_global_message_name(self._global_message_name)
        r = self._client.get_global_message(
            request,
        )
        self._global_message_cache.update(r.item)
        return r
