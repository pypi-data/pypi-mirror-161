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
from version import Gs2VersionRestClient, request as request_, result as result_
from version.domain.iterator.namespaces import DescribeNamespacesIterator
from version.domain.iterator.version_model_masters import DescribeVersionModelMastersIterator
from version.domain.iterator.version_models import DescribeVersionModelsIterator
from version.domain.iterator.accept_versions import DescribeAcceptVersionsIterator
from version.domain.iterator.accept_versions_by_user_id import DescribeAcceptVersionsByUserIdIterator
from version.domain.cache.namespace import NamespaceDomainCache
from version.domain.cache.version_model_master import VersionModelMasterDomainCache
from version.domain.cache.version_model import VersionModelDomainCache
from version.domain.cache.accept_version import AcceptVersionDomainCache


class VersionModelMasterDomain:
    _session: Gs2RestSession
    _client: Gs2VersionRestClient
    _version_model_master_cache: VersionModelMasterDomainCache
    _namespace_name: str
    _version_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        version_model_master_cache: VersionModelMasterDomainCache,
        namespace_name: str,
        version_name: str,
    ):
        self._session = session
        self._client = Gs2VersionRestClient(
            session,
        )
        self._version_model_master_cache = version_model_master_cache
        self._namespace_name = namespace_name
        self._version_name = version_name

    def load(
        self,
        request: request_.GetVersionModelMasterRequest,
    ) -> result_.GetVersionModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_version_name(self._version_name)
        r = self._client.get_version_model_master(
            request,
        )
        self._version_model_master_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateVersionModelMasterRequest,
    ) -> result_.UpdateVersionModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_version_name(self._version_name)
        r = self._client.update_version_model_master(
            request,
        )
        self._version_model_master_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteVersionModelMasterRequest,
    ) -> result_.DeleteVersionModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        request.with_version_name(self._version_name)
        r = self._client.delete_version_model_master(
            request,
        )
        self._version_model_master_cache.delete(r.item)
        return r
