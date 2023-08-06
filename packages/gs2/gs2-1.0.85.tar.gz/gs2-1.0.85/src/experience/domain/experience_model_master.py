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


class ExperienceModelMasterDomain:
    _session: Gs2RestSession
    _client: Gs2ExperienceRestClient
    _experience_model_master_cache: ExperienceModelMasterDomainCache
    _namespace_name: str
    _experience_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        experience_model_master_cache: ExperienceModelMasterDomainCache,
        namespace_name: str,
        experience_name: str,
    ):
        self._session = session
        self._client = Gs2ExperienceRestClient(
            session,
        )
        self._experience_model_master_cache = experience_model_master_cache
        self._namespace_name = namespace_name
        self._experience_name = experience_name

    def load(
        self,
        request: request_.GetExperienceModelMasterRequest,
    ) -> result_.GetExperienceModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_experience_name(self._experience_name)
        r = self._client.get_experience_model_master(
            request,
        )
        self._experience_model_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateExperienceModelMasterRequest,
    ) -> result_.UpdateExperienceModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_experience_name(self._experience_name)
        r = self._client.update_experience_model_master(
            request,
        )
        self._experience_model_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteExperienceModelMasterRequest,
    ) -> result_.DeleteExperienceModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_experience_name(self._experience_name)
        r = self._client.delete_experience_model_master(
            request,
        )
        self._experience_model_master_cache.delete(r.item)
        return r
