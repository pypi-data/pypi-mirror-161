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
from experience.domain.current_experience_master import CurrentExperienceMasterDomain
from experience.domain.experience_model import ExperienceModelDomain
from experience.domain.user import UserDomain
from experience.domain.user_access_token import UserAccessTokenDomain
from experience.domain.user_access_token import UserAccessTokenDomain
from experience.domain.threshold_master import ThresholdMasterDomain
from experience.domain.experience_model_master import ExperienceModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2ExperienceRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _experience_model_master_cache: ExperienceModelMasterDomainCache
    _experience_model_cache: ExperienceModelDomainCache
    _threshold_master_cache: ThresholdMasterDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2ExperienceRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._experience_model_master_cache = ExperienceModelMasterDomainCache()
        self._experience_model_cache = ExperienceModelDomainCache()
        self._threshold_master_cache = ThresholdMasterDomainCache()

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

    def create_experience_model_master(
        self,
        request: request_.CreateExperienceModelMasterRequest,
    ) -> result_.CreateExperienceModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_experience_model_master(
            request,
        )
        return r

    def create_threshold_master(
        self,
        request: request_.CreateThresholdMasterRequest,
    ) -> result_.CreateThresholdMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_threshold_master(
            request,
        )
        return r

    def experience_model_masters(
        self,
    ) -> DescribeExperienceModelMastersIterator:
        return DescribeExperienceModelMastersIterator(
            self._experience_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def experience_models(
        self,
    ) -> DescribeExperienceModelsIterator:
        return DescribeExperienceModelsIterator(
            self._experience_model_cache,
            self._client,
            self._namespace_name,
        )

    def threshold_masters(
        self,
    ) -> DescribeThresholdMastersIterator:
        return DescribeThresholdMastersIterator(
            self._threshold_master_cache,
            self._client,
            self._namespace_name,
        )

    def current_experience_master(
        self,
    ) -> CurrentExperienceMasterDomain:
        return CurrentExperienceMasterDomain(
            self._session,
            self._namespace_name,
        )

    def experience_model(
        self,
        experience_name: str,
    ) -> ExperienceModelDomain:
        return ExperienceModelDomain(
            self._session,
            self._experience_model_cache,
            self._namespace_name,
            experience_name,
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

    def threshold_master(
        self,
        threshold_name: str,
    ) -> ThresholdMasterDomain:
        return ThresholdMasterDomain(
            self._session,
            self._threshold_master_cache,
            self._namespace_name,
            threshold_name,
        )

    def experience_model_master(
        self,
        experience_name: str,
    ) -> ExperienceModelMasterDomain:
        return ExperienceModelMasterDomain(
            self._session,
            self._experience_model_master_cache,
            self._namespace_name,
            experience_name,
        )
