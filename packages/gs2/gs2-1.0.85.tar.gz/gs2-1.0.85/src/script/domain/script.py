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
from script import Gs2ScriptRestClient, request as request_, result as result_
from script.domain.iterator.namespaces import DescribeNamespacesIterator
from script.domain.iterator.scripts import DescribeScriptsIterator
from script.domain.cache.namespace import NamespaceDomainCache
from script.domain.cache.script import ScriptDomainCache


class ScriptDomain:
    _session: Gs2RestSession
    _client: Gs2ScriptRestClient
    _script_cache: ScriptDomainCache
    _namespace_name: str
    _script_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        script_cache: ScriptDomainCache,
        namespace_name: str,
        script_name: str,
    ):
        self._session = session
        self._client = Gs2ScriptRestClient(
            session,
        )
        self._script_cache = script_cache
        self._namespace_name = namespace_name
        self._script_name = script_name

    def load(
        self,
        request: request_.GetScriptRequest,
    ) -> result_.GetScriptResult:
        request.with_namespace_name(self._namespace_name)
        request.with_script_name(self._script_name)
        r = self._client.get_script(
            request,
        )
        self._script_cache.update(r.item)
        return r

    def update(
        self,
        request: request_.UpdateScriptRequest,
    ) -> result_.UpdateScriptResult:
        request.with_namespace_name(self._namespace_name)
        request.with_script_name(self._script_name)
        r = self._client.update_script(
            request,
        )
        self._script_cache.update(r.item)
        return r

    def update_from_git_hub(
        self,
        request: request_.UpdateScriptFromGitHubRequest,
    ) -> result_.UpdateScriptFromGitHubResult:
        request.with_namespace_name(self._namespace_name)
        request.with_script_name(self._script_name)
        r = self._client.update_script_from_git_hub(
            request,
        )
        self._script_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteScriptRequest,
    ) -> result_.DeleteScriptResult:
        request.with_namespace_name(self._namespace_name)
        request.with_script_name(self._script_name)
        r = self._client.delete_script(
            request,
        )
        return r
