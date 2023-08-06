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


class GitHubApiKeyDomain:
    _session: Gs2RestSession
    _client: Gs2KeyRestClient
    _git_hub_api_key_cache: GitHubApiKeyDomainCache
    _namespace_name: str
    _api_key_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        git_hub_api_key_cache: GitHubApiKeyDomainCache,
        namespace_name: str,
        api_key_name: str,
    ):
        self._session = session
        self._client = Gs2KeyRestClient(
            session,
        )
        self._git_hub_api_key_cache = git_hub_api_key_cache
        self._namespace_name = namespace_name
        self._api_key_name = api_key_name

    def update(
        self,
        request: request_.UpdateGitHubApiKeyRequest,
    ) -> result_.UpdateGitHubApiKeyResult:
        request.with_namespace_name(self._namespace_name)
        request.with_api_key_name(self._api_key_name)
        r = self._client.update_git_hub_api_key(
            request,
        )
        self._git_hub_api_key_cache.update(r.item)
        return r

    def load(
        self,
        request: request_.GetGitHubApiKeyRequest,
    ) -> result_.GetGitHubApiKeyResult:
        request.with_namespace_name(self._namespace_name)
        request.with_api_key_name(self._api_key_name)
        r = self._client.get_git_hub_api_key(
            request,
        )
        self._git_hub_api_key_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteGitHubApiKeyRequest,
    ) -> result_.DeleteGitHubApiKeyResult:
        request.with_namespace_name(self._namespace_name)
        request.with_api_key_name(self._api_key_name)
        r = self._client.delete_git_hub_api_key(
            request,
        )
        self._git_hub_api_key_cache.delete(r.item)
        return r
