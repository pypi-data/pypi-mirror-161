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
from key import Gs2KeyRestClient, request as request_, result as result_
from key.domain.iterator.namespaces import DescribeNamespacesIterator
from key.domain.iterator.keys import DescribeKeysIterator
from key.domain.iterator.git_hub_api_keys import DescribeGitHubApiKeysIterator
from key.domain.cache.namespace import NamespaceDomainCache
from key.domain.cache.key import KeyDomainCache
from key.domain.cache.git_hub_api_key import GitHubApiKeyDomainCache
from key.domain.key import KeyDomain
from key.domain.git_hub_api_key import GitHubApiKeyDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2KeyRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _key_cache: KeyDomainCache
    _git_hub_api_key_cache: GitHubApiKeyDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2KeyRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._key_cache = KeyDomainCache()
        self._git_hub_api_key_cache = GitHubApiKeyDomainCache()

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

    def create_key(
        self,
        request: request_.CreateKeyRequest,
    ) -> result_.CreateKeyResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_key(
            request,
        )
        return r

    def create_git_hub_api_key(
        self,
        request: request_.CreateGitHubApiKeyRequest,
    ) -> result_.CreateGitHubApiKeyResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_git_hub_api_key(
            request,
        )
        return r

    def keys(
        self,
    ) -> DescribeKeysIterator:
        return DescribeKeysIterator(
            self._key_cache,
            self._client,
            self._namespace_name,
        )

    def git_hub_api_keys(
        self,
    ) -> DescribeGitHubApiKeysIterator:
        return DescribeGitHubApiKeysIterator(
            self._git_hub_api_key_cache,
            self._client,
            self._namespace_name,
        )

    def key(
        self,
        key_name: str,
    ) -> KeyDomain:
        return KeyDomain(
            self._session,
            self._key_cache,
            self._namespace_name,
            key_name,
        )

    def git_hub_api_key(
        self,
        api_key_name: str,
    ) -> GitHubApiKeyDomain:
        return GitHubApiKeyDomain(
            self._session,
            self._git_hub_api_key_cache,
            self._namespace_name,
            api_key_name,
        )
