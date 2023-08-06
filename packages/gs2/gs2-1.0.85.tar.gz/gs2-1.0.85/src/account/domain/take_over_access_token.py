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


class TakeOverAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2AccountRestClient
    _take_over_cache: TakeOverDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _type_: int

    def __init__(
        self,
        session: Gs2RestSession,
        take_over_cache: TakeOverDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        type_: int,
    ):
        self._session = session
        self._client = Gs2AccountRestClient(
            session,
        )
        self._take_over_cache = take_over_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._type_ = type_

    def load(
        self,
        request: request_.GetTakeOverRequest,
    ) -> result_.GetTakeOverResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_type(self._type_)
        r = self._client.get_take_over(
            request,
        )
        self._take_over_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateTakeOverRequest,
    ) -> result_.UpdateTakeOverResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_type(self._type_)
        r = self._client.update_take_over(
            request,
        )
        self._take_over_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteTakeOverRequest,
    ) -> result_.DeleteTakeOverResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_type(self._type_)
        r = self._client.delete_take_over(
            request,
        )
        self._take_over_cache.delete(r.item)
        return r
