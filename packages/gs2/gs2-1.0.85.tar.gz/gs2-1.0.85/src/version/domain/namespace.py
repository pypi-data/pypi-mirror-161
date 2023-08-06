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
from version.domain.current_version_master import CurrentVersionMasterDomain
from version.domain.version_model import VersionModelDomain
from version.domain.user import UserDomain
from version.domain.user_access_token import UserAccessTokenDomain
from version.domain.user_access_token import UserAccessTokenDomain
from version.domain.version_model_master import VersionModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2VersionRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _version_model_master_cache: VersionModelMasterDomainCache
    _version_model_cache: VersionModelDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2VersionRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._version_model_master_cache = VersionModelMasterDomainCache()
        self._version_model_cache = VersionModelDomainCache()

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

    def create_version_model_master(
        self,
        request: request_.CreateVersionModelMasterRequest,
    ) -> result_.CreateVersionModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_version_model_master(
            request,
        )
        return r

    def version_model_masters(
        self,
    ) -> DescribeVersionModelMastersIterator:
        return DescribeVersionModelMastersIterator(
            self._version_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def version_models(
        self,
    ) -> DescribeVersionModelsIterator:
        return DescribeVersionModelsIterator(
            self._version_model_cache,
            self._client,
            self._namespace_name,
        )

    def current_version_master(
        self,
    ) -> CurrentVersionMasterDomain:
        return CurrentVersionMasterDomain(
            self._session,
            self._namespace_name,
        )

    def version_model(
        self,
        version_name: str,
    ) -> VersionModelDomain:
        return VersionModelDomain(
            self._session,
            self._version_model_cache,
            self._namespace_name,
            version_name,
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

    def version_model_master(
        self,
        version_name: str,
    ) -> VersionModelMasterDomain:
        return VersionModelMasterDomain(
            self._session,
            self._version_model_master_cache,
            self._namespace_name,
            version_name,
        )
