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
from lottery.domain.box import BoxDomain
from lottery.domain.box_access_token import BoxAccessTokenDomain
from lottery.domain.box_access_token import BoxAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2LotteryRestClient
    _namespace_name: str
    _access_token: AccessToken
    _box_cache: BoxDomainCache
    _probability_cache: ProbabilityDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2LotteryRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._box_cache = BoxDomainCache()
        self._probability_cache = ProbabilityDomainCache()

    def boxes(
        self,
    ) -> DescribeBoxesIterator:
        return DescribeBoxesIterator(
            self._box_cache,
            self._client,
            self._namespace_name,
            self._access_token,
        )

    def probabilities(
        self,
        lottery_name: str,
    ) -> DescribeProbabilitiesIterator:
        return DescribeProbabilitiesIterator(
            self._probability_cache,
            self._client,
            self._namespace_name,
            lottery_name,
            self._access_token,
        )

    def box(
        self,
        prize_table_name: str,
    ) -> BoxAccessTokenDomain:
        return BoxAccessTokenDomain(
            self._session,
            self._box_cache,
            self._namespace_name,
            self._access_token,
            prize_table_name,
        )
