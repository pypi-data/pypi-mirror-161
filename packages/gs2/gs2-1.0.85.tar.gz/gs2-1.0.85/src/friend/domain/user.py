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
from friend.domain.profile import ProfileDomain
from friend.domain.profile_access_token import ProfileAccessTokenDomain
from friend.domain.profile_access_token import ProfileAccessTokenDomain
from friend.domain.black_list import BlackListDomain
from friend.domain.black_list_access_token import BlackListAccessTokenDomain
from friend.domain.black_list_access_token import BlackListAccessTokenDomain
from friend.domain.follow import FollowDomain
from friend.domain.follow_access_token import FollowAccessTokenDomain
from friend.domain.follow_access_token import FollowAccessTokenDomain
from friend.domain.friend import FriendDomain
from friend.domain.friend_access_token import FriendAccessTokenDomain
from friend.domain.friend_access_token import FriendAccessTokenDomain
from friend.domain.send_box import SendBoxDomain
from friend.domain.send_box_access_token import SendBoxAccessTokenDomain
from friend.domain.send_box_access_token import SendBoxAccessTokenDomain
from friend.domain.inbox import InboxDomain
from friend.domain.inbox_access_token import InboxAccessTokenDomain
from friend.domain.inbox_access_token import InboxAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2FriendRestClient
    _namespace_name: str
    _user_id: str
    _follow_user_cache: FollowUserDomainCache
    _friend_user_cache: FriendUserDomainCache
    _friend_request_cache: FriendRequestDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2FriendRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._follow_user_cache = FollowUserDomainCache()
        self._friend_user_cache = FriendUserDomainCache()
        self._friend_request_cache = FriendRequestDomainCache()

    def profile(
        self,
    ) -> ProfileDomain:
        return ProfileDomain(
            self._session,
            self._namespace_name,
            self._user_id,
        )

    def black_list(
        self,
    ) -> BlackListDomain:
        return BlackListDomain(
            self._session,
            self._namespace_name,
            self._user_id,
        )

    def follow(
        self,
    ) -> FollowDomain:
        return FollowDomain(
            self._session,
            self._namespace_name,
            self._user_id,
        )

    def friend(
        self,
    ) -> FriendDomain:
        return FriendDomain(
            self._session,
            self._namespace_name,
            self._user_id,
        )

    def send_box(
        self,
    ) -> SendBoxDomain:
        return SendBoxDomain(
            self._session,
            self._namespace_name,
            self._user_id,
        )

    def inbox(
        self,
    ) -> InboxDomain:
        return InboxDomain(
            self._session,
            self._namespace_name,
            self._user_id,
        )
