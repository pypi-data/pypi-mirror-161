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


class ReceiptDomain:
    _session: Gs2RestSession
    _client: Gs2MoneyRestClient
    _receipt_cache: ReceiptDomainCache
    _namespace_name: str
    _user_id: str
    _transaction_id: str

    def __init__(
        self,
        session: Gs2RestSession,
        receipt_cache: ReceiptDomainCache,
        namespace_name: str,
        user_id: str,
        transaction_id: str,
    ):
        self._session = session
        self._client = Gs2MoneyRestClient(
            session,
        )
        self._receipt_cache = receipt_cache
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._transaction_id = transaction_id

    def get_by_user_id_and_transaction_id(
        self,
        request: request_.GetByUserIdAndTransactionIdRequest,
    ) -> result_.GetByUserIdAndTransactionIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        request.with_transaction_id(self._transaction_id)
        r = self._client.get_by_user_id_and_transaction_id(
            request,
        )
        self._receipt_cache.update(r.item)
        return r
