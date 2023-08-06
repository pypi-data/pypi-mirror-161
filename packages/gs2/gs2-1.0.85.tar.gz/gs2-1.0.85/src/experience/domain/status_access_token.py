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


class StatusAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2ExperienceRestClient
    _status_cache: StatusDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _experience_name: str
    _property_id: str

    def __init__(
        self,
        session: Gs2RestSession,
        status_cache: StatusDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        experience_name: str,
        property_id: str,
    ):
        self._session = session
        self._client = Gs2ExperienceRestClient(
            session,
        )
        self._status_cache = status_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._experience_name = experience_name
        self._property_id = property_id

    def load(
        self,
        request: request_.GetStatusRequest,
    ) -> result_.GetStatusResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_experience_name(self._experience_name)
        request.with_property_id(self._property_id)
        r = self._client.get_status(
            request,
        )
        self._status_cache.update(r.item)
        return r

    def get_with_signature(
        self,
        request: request_.GetStatusWithSignatureRequest,
    ) -> result_.GetStatusWithSignatureResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_experience_name(self._experience_name)
        request.with_property_id(self._property_id)
        r = self._client.get_status_with_signature(
            request,
        )
        self._status_cache.update(r.item)
        return r
