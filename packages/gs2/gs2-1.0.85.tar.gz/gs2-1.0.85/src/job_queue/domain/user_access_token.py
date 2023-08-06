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
from job_queue import Gs2JobQueueRestClient, request as request_, result as result_
from job_queue.domain.iterator.namespaces import DescribeNamespacesIterator
from job_queue.domain.iterator.jobs_by_user_id import DescribeJobsByUserIdIterator
from job_queue.domain.iterator.dead_letter_jobs_by_user_id import DescribeDeadLetterJobsByUserIdIterator
from job_queue.domain.cache.namespace import NamespaceDomainCache
from job_queue.domain.cache.job import JobDomainCache
from job_queue.domain.cache.dead_letter_job import DeadLetterJobDomainCache
from job_queue.domain.job import JobDomain
from job_queue.domain.job_access_token import JobAccessTokenDomain
from job_queue.domain.job_access_token import JobAccessTokenDomain
from job_queue.domain.dead_letter_job import DeadLetterJobDomain
from job_queue.domain.dead_letter_job_access_token import DeadLetterJobAccessTokenDomain
from job_queue.domain.dead_letter_job_access_token import DeadLetterJobAccessTokenDomain


class UserAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2JobQueueRestClient
    _namespace_name: str
    _access_token: AccessToken
    _job_cache: JobDomainCache
    _dead_letter_job_cache: DeadLetterJobDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        access_token: AccessToken,
    ):
        self._session = session
        self._client = Gs2JobQueueRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._job_cache = JobDomainCache()
        self._dead_letter_job_cache = DeadLetterJobDomainCache()

    def run(
        self,
        request: request_.RunRequest,
    ) -> result_.RunResult:
        request.with_namespace_name(self._namespace_name)
        request.with_access_token(self._access_token.token if self._access_token else None)
        r = self._client.run(
            request,
        )
        return r

    def job(
        self,
        job_name: str,
    ) -> JobAccessTokenDomain:
        return JobAccessTokenDomain(
            self._session,
            self._job_cache,
            self._namespace_name,
            self._access_token,
            job_name,
        )

    def dead_letter_job(
        self,
        dead_letter_job_name: str,
    ) -> DeadLetterJobAccessTokenDomain:
        return DeadLetterJobAccessTokenDomain(
            self._session,
            self._dead_letter_job_cache,
            self._namespace_name,
            self._access_token,
            dead_letter_job_name,
        )
