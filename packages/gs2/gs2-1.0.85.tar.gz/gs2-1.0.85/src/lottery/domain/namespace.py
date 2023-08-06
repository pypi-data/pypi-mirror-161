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
from lottery import Gs2LotteryRestClient, request as request_, result as result_
from lottery.domain.iterator.namespaces import DescribeNamespacesIterator
from lottery.domain.iterator.lottery_model_masters import DescribeLotteryModelMastersIterator
from lottery.domain.iterator.prize_table_masters import DescribePrizeTableMastersIterator
from lottery.domain.iterator.boxes import DescribeBoxesIterator
from lottery.domain.iterator.boxes_by_user_id import DescribeBoxesByUserIdIterator
from lottery.domain.iterator.lottery_models import DescribeLotteryModelsIterator
from lottery.domain.iterator.prize_tables import DescribePrizeTablesIterator
from lottery.domain.iterator.probabilities import DescribeProbabilitiesIterator
from lottery.domain.iterator.probabilities_by_user_id import DescribeProbabilitiesByUserIdIterator
from lottery.domain.cache.namespace import NamespaceDomainCache
from lottery.domain.cache.lottery_model_master import LotteryModelMasterDomainCache
from lottery.domain.cache.prize_table_master import PrizeTableMasterDomainCache
from lottery.domain.cache.box import BoxDomainCache
from lottery.domain.cache.lottery_model import LotteryModelDomainCache
from lottery.domain.cache.prize_table import PrizeTableDomainCache
from lottery.domain.cache.probability import ProbabilityDomainCache
from lottery.domain.user import UserDomain
from lottery.domain.user_access_token import UserAccessTokenDomain
from lottery.domain.user_access_token import UserAccessTokenDomain
from lottery.domain.current_lottery_master import CurrentLotteryMasterDomain
from lottery.domain.lottery_model import LotteryModelDomain
from lottery.domain.prize_table_master import PrizeTableMasterDomain
from lottery.domain.lottery_model_master import LotteryModelMasterDomain
from lottery.domain.prize_table import PrizeTableDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2LotteryRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _lottery_model_master_cache: LotteryModelMasterDomainCache
    _prize_table_master_cache: PrizeTableMasterDomainCache
    _lottery_model_cache: LotteryModelDomainCache
    _prize_table_cache: PrizeTableDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2LotteryRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._lottery_model_master_cache = LotteryModelMasterDomainCache()
        self._prize_table_master_cache = PrizeTableMasterDomainCache()
        self._lottery_model_cache = LotteryModelDomainCache()
        self._prize_table_cache = PrizeTableDomainCache()

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

    def create_lottery_model_master(
        self,
        request: request_.CreateLotteryModelMasterRequest,
    ) -> result_.CreateLotteryModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_lottery_model_master(
            request,
        )
        return r

    def create_prize_table_master(
        self,
        request: request_.CreatePrizeTableMasterRequest,
    ) -> result_.CreatePrizeTableMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_prize_table_master(
            request,
        )
        return r

    def lottery_model_masters(
        self,
    ) -> DescribeLotteryModelMastersIterator:
        return DescribeLotteryModelMastersIterator(
            self._lottery_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def prize_table_masters(
        self,
    ) -> DescribePrizeTableMastersIterator:
        return DescribePrizeTableMastersIterator(
            self._prize_table_master_cache,
            self._client,
            self._namespace_name,
        )

    def lottery_models(
        self,
    ) -> DescribeLotteryModelsIterator:
        return DescribeLotteryModelsIterator(
            self._lottery_model_cache,
            self._client,
            self._namespace_name,
        )

    def prize_tables(
        self,
    ) -> DescribePrizeTablesIterator:
        return DescribePrizeTablesIterator(
            self._prize_table_cache,
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

    def current_lottery_master(
        self,
    ) -> CurrentLotteryMasterDomain:
        return CurrentLotteryMasterDomain(
            self._session,
            self._namespace_name,
        )

    def lottery_model(
        self,
        lottery_name: str,
    ) -> LotteryModelDomain:
        return LotteryModelDomain(
            self._session,
            self._lottery_model_cache,
            self._namespace_name,
            lottery_name,
        )

    def prize_table_master(
        self,
        prize_table_name: str,
    ) -> PrizeTableMasterDomain:
        return PrizeTableMasterDomain(
            self._session,
            self._prize_table_master_cache,
            self._namespace_name,
            prize_table_name,
        )

    def lottery_model_master(
        self,
        lottery_name: str,
    ) -> LotteryModelMasterDomain:
        return LotteryModelMasterDomain(
            self._session,
            self._lottery_model_master_cache,
            self._namespace_name,
            lottery_name,
        )

    def prize_table(
        self,
        prize_table_name: str,
    ) -> PrizeTableDomain:
        return PrizeTableDomain(
            self._session,
            self._prize_table_cache,
            self._namespace_name,
            prize_table_name,
        )
