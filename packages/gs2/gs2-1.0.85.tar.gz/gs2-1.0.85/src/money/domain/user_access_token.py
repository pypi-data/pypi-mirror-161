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
from money.domain.wallet import WalletDomain
from money.domain.wallet_access_token import WalletAccessTokenDomain
from money.domain.wallet_access_token import WalletAccessTokenDomain
from money.domain.receipt import ReceiptDomain
from money.domain.receipt_access_token import ReceiptAccessTokenDomain
from money.domain.receipt_access_token import ReceiptAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2MoneyRestClient
    _namespace_name: str
    _access_token: AccessToken
    _wallet_cache: WalletDomainCache
    _receipt_cache: ReceiptDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2MoneyRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._wallet_cache = WalletDomainCache()
        self._receipt_cache = ReceiptDomainCache()

    def wallets(
        self,
    ) -> DescribeWalletsIterator:
        return DescribeWalletsIterator(
            self._wallet_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def wallet(
        self,
        slot: int,
    ) -> WalletAccessTokenDomain:
        return WalletAccessTokenDomain(
            self._session,
            self._wallet_cache,
            self._namespace_name,
            self._access_token,
            slot,
        )

    def receipt(
        self,
        transaction_id: str,
    ) -> ReceiptAccessTokenDomain:
        return ReceiptAccessTokenDomain(
            self._session,
            self._receipt_cache,
            self._namespace_name,
            self._access_token,
            transaction_id,
        )
