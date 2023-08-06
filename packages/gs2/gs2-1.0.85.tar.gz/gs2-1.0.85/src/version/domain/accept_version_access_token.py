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


class AcceptVersionAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2VersionRestClient
    _accept_version_cache: AcceptVersionDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _version_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        accept_version_cache: AcceptVersionDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        version_name: str,
    ):
        self._session = session
        self._client = Gs2VersionRestClient(
            session,
        )
        self._accept_version_cache = accept_version_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._version_name = version_name

    def accept(
        self,
        request: request_.AcceptRequest,
    ) -> result_.AcceptResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_version_name(self._version_name)
        r = self._client.accept(
            request,
        )
        self._accept_version_cache.update(r.item)
        return r

    def load(
        self,
        request: request_.GetAcceptVersionRequest,
    ) -> result_.GetAcceptVersionResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_version_name(self._version_name)
        r = self._client.get_accept_version(
            request,
        )
        self._accept_version_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteAcceptVersionRequest,
    ) -> result_.DeleteAcceptVersionResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        request.with_version_name(self._version_name)
        r = self._client.delete_accept_version(
            request,
        )
        return r
