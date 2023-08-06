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
from money import Gs2MoneyRestClient, request as request_, result as result_
from money.domain.iterator.namespaces import DescribeNamespacesIterator
from money.domain.iterator.wallets import DescribeWalletsIterator
from money.domain.iterator.wallets_by_user_id import DescribeWalletsByUserIdIterator
from money.domain.iterator.receipts import DescribeReceiptsIterator
from money.domain.cache.namespace import NamespaceDomainCache
from money.domain.cache.wallet import WalletDomainCache
from money.domain.cache.receipt import ReceiptDomainCache


class WalletDomain:
    _session: Gs2RestSession
    _client: Gs2MoneyRestClient
    _wallet_cache: WalletDomainCache
    _namespace_name: str
    _user_id: str
    _slot: int

    def __init__(
        self,
        session: Gs2RestSession,
        wallet_cache: WalletDomainCache,
        namespace_name: str,
        user_id: str,
        slot: int,
    ):
        self._session = session
        self._client = Gs2MoneyRestClient(
            session,
        )
        self._wallet_cache = wallet_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._slot = slot

    def load(
        self,
        request: request_.GetWalletByUserIdRequest,
    ) -> result_.GetWalletByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_slot(self._slot)
        r = self._client.get_wallet_by_user_id(
            request,
        )
        self._wallet_cache.update(r.item)
        return r

    def deposit(
        self,
        request: request_.DepositByUserIdRequest,
    ) -> result_.DepositByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_slot(self._slot)
        r = self._client.deposit_by_user_id(
            request,
        )
        self._wallet_cache.update(r.item)
        return r

    def withdraw(
        self,
        request: request_.WithdrawByUserIdRequest,
    ) -> result_.WithdrawByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_slot(self._slot)
        r = self._client.withdraw_by_user_id(
            request,
        )
        self._wallet_cache.update(r.item)
        return r
