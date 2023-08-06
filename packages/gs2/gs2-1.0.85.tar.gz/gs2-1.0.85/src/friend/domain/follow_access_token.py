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
from friend import Gs2FriendRestClient, request as request_, result as result_
from friend.domain.iterator.namespaces import DescribeNamespacesIterator
from friend.domain.iterator.follows import DescribeFollowsIterator
from friend.domain.iterator.follows_by_user_id import DescribeFollowsByUserIdIterator
from friend.domain.iterator.friends import DescribeFriendsIterator
from friend.domain.iterator.friends_by_user_id import DescribeFriendsByUserIdIterator
from friend.domain.iterator.send_requests import DescribeSendRequestsIterator
from friend.domain.iterator.send_requests_by_user_id import DescribeSendRequestsByUserIdIterator
from friend.domain.iterator.receive_requests import DescribeReceiveRequestsIterator
from friend.domain.iterator.receive_requests_by_user_id import DescribeReceiveRequestsByUserIdIterator
from friend.domain.iterator.black_list import DescribeBlackListIterator
from friend.domain.iterator.black_list_by_user_id import DescribeBlackListByUserIdIterator
from friend.domain.cache.namespace import NamespaceDomainCache
from friend.domain.cache.follow_user import FollowUserDomainCache
from friend.domain.cache.friend_user import FriendUserDomainCache
from friend.domain.cache.friend_request import FriendRequestDomainCache


class FollowAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2FriendRestClient
    _follow_user_cache: FollowUserDomainCache
    _namespace_name: str
    _access_token: AccessToken

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2FriendRestClient(
            session,
        )
        self._follow_user_cache = FollowUserDomainCache()
        self._namespace_name = namespace_name
        self._access_token = access_token

    def load(
        self,
        request: request_.GetFollowRequest,
    ) -> result_.GetFollowResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.get_follow(
            request,
        )
        return r

    def follow(
        self,
        request: request_.FollowRequest,
    ) -> result_.FollowResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.follow(
            request,
        )
        return r

    def unfollow(
        self,
        request: request_.UnfollowRequest,
    ) -> result_.UnfollowResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.unfollow(
            request,
        )
        return r

    def list(
        self,
        with_profile: bool,
    ) -> DescribeFollowsIterator:
        return DescribeFollowsIterator(
            self._follow_user_cache,
            self._client,
            self._namespace_name,
            self._access_token,
            with_profile,
        )
