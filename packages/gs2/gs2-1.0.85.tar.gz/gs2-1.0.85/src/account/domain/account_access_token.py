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


class AccountAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2AccountRestClient
    _account_cache: AccountDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _take_over_cache: TakeOverDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        account_cache: AccountDomainCache,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2AccountRestClient(
            session,
        )
        self._account_cache = account_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._take_over_cache = TakeOverDomainCache()

    def create_take_over(
        self,
        request: request_.CreateTakeOverRequest,
    ) -> result_.CreateTakeOverResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.create_take_over(
            request,
        )
        return r

    def take_overs(
        self,
    ) -> DescribeTakeOversIterator:
        return DescribeTakeOversIterator(
            self._take_over_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def take_over(
        self,
        type_: int,
    ) -> TakeOverAccessTokenDomain:
        return TakeOverAccessTokenDomain(
            self._session,
            self._take_over_cache,
            self._namespace_name,
            self._access_token,
            type_,
        )
