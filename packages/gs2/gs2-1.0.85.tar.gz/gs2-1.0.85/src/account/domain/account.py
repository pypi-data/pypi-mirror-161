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
from account import Gs2AccountRestClient, request as request_, result as result_
from account.domain.iterator.namespaces import DescribeNamespacesIterator
from account.domain.iterator.accounts import DescribeAccountsIterator
from account.domain.iterator.take_overs import DescribeTakeOversIterator
from account.domain.iterator.take_overs_by_user_id import DescribeTakeOversByUserIdIterator
from account.domain.cache.namespace import NamespaceDomainCache
from account.domain.cache.account import AccountDomainCache
from account.domain.cache.take_over import TakeOverDomainCache
from account.domain.take_over import TakeOverDomain
from account.domain.take_over_access_token import TakeOverAccessTokenDomain
from account.domain.take_over_access_token import TakeOverAccessTokenDomain


class AccountDomain:
    _session: Gs2RestSession
    _client: Gs2AccountRestClient
    _account_cache: AccountDomainCache
    _namespace_name: str
    _user_id: str
    _take_over_cache: TakeOverDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        account_cache: AccountDomainCache,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2AccountRestClient(
            session,
        )
        self._account_cache = account_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._take_over_cache = TakeOverDomainCache()

    def update_time_offset(
        self,
        request: request_.UpdateTimeOffsetRequest,
    ) -> result_.UpdateTimeOffsetResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.update_time_offset(
            request,
        )
        self._account_cache.update(r.item)
        return r

    def load(
        self,
        request: request_.GetAccountRequest,
    ) -> result_.GetAccountResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.get_account(
            request,
        )
        self._account_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteAccountRequest,
    ) -> result_.DeleteAccountResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.delete_account(
            request,
        )
        self._account_cache.delete(r.item)
        return r

    def authentication(
        self,
        request: request_.AuthenticationRequest,
    ) -> result_.AuthenticationResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.authentication(
            request,
        )
        self._account_cache.update(r.item)
        return r

    def create_take_over(
        self,
        request: request_.CreateTakeOverByUserIdRequest,
    ) -> result_.CreateTakeOverByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.create_take_over_by_user_id(
            request,
        )
        return r

    def take_overs(
        self,
    ) -> DescribeTakeOversByUserIdIterator:
        return DescribeTakeOversByUserIdIterator(
            self._take_over_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def take_over(
        self,
        type_: int,
    ) -> TakeOverDomain:
        return TakeOverDomain(
            self._session,
            self._take_over_cache,
            self._namespace_name,
            self._user_id,
            type_,
        )
