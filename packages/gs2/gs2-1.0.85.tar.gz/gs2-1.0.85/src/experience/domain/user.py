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
from experience import Gs2ExperienceRestClient, request as request_, result as result_
from experience.domain.iterator.namespaces import DescribeNamespacesIterator
from experience.domain.iterator.experience_model_masters import DescribeExperienceModelMastersIterator
from experience.domain.iterator.experience_models import DescribeExperienceModelsIterator
from experience.domain.iterator.threshold_masters import DescribeThresholdMastersIterator
from experience.domain.iterator.statuses import DescribeStatusesIterator
from experience.domain.iterator.statuses_by_user_id import DescribeStatusesByUserIdIterator
from experience.domain.cache.namespace import NamespaceDomainCache
from experience.domain.cache.experience_model_master import ExperienceModelMasterDomainCache
from experience.domain.cache.experience_model import ExperienceModelDomainCache
from experience.domain.cache.threshold_master import ThresholdMasterDomainCache
from experience.domain.cache.status import StatusDomainCache
from experience.domain.status import StatusDomain
from experience.domain.status_access_token import StatusAccessTokenDomain
from experience.domain.status_access_token import StatusAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2ExperienceRestClient
    _namespace_name: str
    _user_id: str
    _status_cache: StatusDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2ExperienceRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._status_cache = StatusDomainCache()

    def statuses(
        self,
        experience_name: str,
    ) -> DescribeStatusesByUserIdIterator:
        return DescribeStatusesByUserIdIterator(
            self._status_cache,
            self._client,
            self._namespace_name,
            experience_name,
            self._user_id,
        )

    def status(
        self,
        experience_name: str,
        property_id: str,
    ) -> StatusDomain:
        return StatusDomain(
            self._session,
            self._status_cache,
            self._namespace_name,
            self._user_id,
            experience_name,
            property_id,
        )
