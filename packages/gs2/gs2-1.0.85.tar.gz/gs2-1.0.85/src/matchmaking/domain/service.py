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
from matchmaking import Gs2MatchmakingRestClient, request as request_, result as result_
from matchmaking.domain.iterator.namespaces import DescribeNamespacesIterator
from matchmaking.domain.cache.namespace import NamespaceDomainCache
from matchmaking.domain.namespace import NamespaceDomain

class Gs2Matchmaking:
    _session: Gs2RestSession
    _client: Gs2MatchmakingRestClient
    _namespace_cache: NamespaceDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
    ):
        self._session = session
        self._client = Gs2MatchmakingRestClient (
            session,
        )
        self._namespace_cache = NamespaceDomainCache()

    def create_namespace(
        self,
        request: request_.CreateNamespaceRequest,
    ) -> result_.CreateNamespaceResult:
        r = self._client.create_namespace(
            request,
        )
        self._namespace_cache.update(r.item)
        return r

    def do_matchmaking_by_player(
        self,
        request: request_.DoMatchmakingByPlayerRequest,
    ) -> result_.DoMatchmakingByPlayerResult:
        r = self._client.do_matchmaking_by_player(
            request,
        )
        return r

    def delete_gathering(
        self,
        request: request_.DeleteGatheringRequest,
    ) -> result_.DeleteGatheringResult:
        r = self._client.delete_gathering(
            request,
        )
        return r

    def put_result(
        self,
        request: request_.PutResultRequest,
    ) -> result_.PutResultResult:
        r = self._client.put_result(
            request,
        )
        return r

    def vote(
        self,
        request: request_.VoteRequest,
    ) -> result_.VoteResult:
        r = self._client.vote(
            request,
        )
        return r

    def vote_multiple(
        self,
        request: request_.VoteMultipleRequest,
    ) -> result_.VoteMultipleResult:
        r = self._client.vote_multiple(
            request,
        )
        return r

    def commit_vote(
        self,
        request: request_.CommitVoteRequest,
    ) -> result_.CommitVoteResult:
        r = self._client.commit_vote(
            request,
        )
        return r

    def namespaces(
        self,
    ) -> DescribeNamespacesIterator:
        return DescribeNamespacesIterator(
            self._namespace_cache,
            self._client,
        )

    def namespace(
        self,
        namespace_name: str,
    ) -> NamespaceDomain:
        return NamespaceDomain(
            self._session,
            self._namespace_cache,
            namespace_name,
        )
