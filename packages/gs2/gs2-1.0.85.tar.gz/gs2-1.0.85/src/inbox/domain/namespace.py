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
from inbox.domain.user import UserDomain
from inbox.domain.user_access_token import UserAccessTokenDomain
from inbox.domain.user_access_token import UserAccessTokenDomain
from inbox.domain.current_message_master import CurrentMessageMasterDomain
from inbox.domain.global_message import GlobalMessageDomain
from inbox.domain.global_message_master import GlobalMessageMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2InboxRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _global_message_master_cache: GlobalMessageMasterDomainCache
    _global_message_cache: GlobalMessageDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2InboxRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._global_message_master_cache = GlobalMessageMasterDomainCache()
        self._global_message_cache = GlobalMessageDomainCache()

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

    def create_global_message_master(
        self,
        request: request_.CreateGlobalMessageMasterRequest,
    ) -> result_.CreateGlobalMessageMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_global_message_master(
            request,
        )
        return r

    def global_message_masters(
        self,
    ) -> DescribeGlobalMessageMastersIterator:
        return DescribeGlobalMessageMastersIterator(
            self._global_message_master_cache,
            self._client,
            self._namespace_name,
        )

    def global_messages(
        self,
    ) -> DescribeGlobalMessagesIterator:
        return DescribeGlobalMessagesIterator(
            self._global_message_cache,
            self._client,
            self._namespace_name,
        )

    def user(
        self,
        user_id: str,
    ) -> UserDomain:
        return UserDomain(
            self._session,
            self._namespace_name,
            user_id,
        )

    def access_token(
        self,
        access_token: AccessToken,
    ) -> UserAccessTokenDomain:
        return UserAccessTokenDomain(
            self._session,
            self._namespace_name,
            access_token,
        )

    def current_message_master(
        self,
    ) -> CurrentMessageMasterDomain:
        return CurrentMessageMasterDomain(
            self._session,
            self._namespace_name,
        )

    def global_message(
        self,
        global_message_name: str,
    ) -> GlobalMessageDomain:
        return GlobalMessageDomain(
            self._session,
            self._global_message_cache,
            self._namespace_name,
            global_message_name,
        )

    def global_message_master(
        self,
        global_message_name: str,
    ) -> GlobalMessageMasterDomain:
        return GlobalMessageMasterDomain(
            self._session,
            self._global_message_master_cache,
            self._namespace_name,
            global_message_name,
        )
