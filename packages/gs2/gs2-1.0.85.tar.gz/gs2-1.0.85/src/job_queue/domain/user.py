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


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2JobQueueRestClient
    _namespace_name: str
    _user_id: str
    _job_cache: JobDomainCache
    _dead_letter_job_cache: DeadLetterJobDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2JobQueueRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._job_cache = JobDomainCache()
        self._dead_letter_job_cache = DeadLetterJobDomainCache()

    def push(
        self,
        request: request_.PushByUserIdRequest,
    ) -> result_.PushByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.push_by_user_id(
            request,
        )
        return r

    def run(
        self,
        request: request_.RunByUserIdRequest,
    ) -> result_.RunByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.run_by_user_id(
            request,
        )
        return r

    def jobs(
        self,
    ) -> DescribeJobsByUserIdIterator:
        return DescribeJobsByUserIdIterator(
            self._job_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def dead_letter_jobs(
        self,
    ) -> DescribeDeadLetterJobsByUserIdIterator:
        return DescribeDeadLetterJobsByUserIdIterator(
            self._dead_letter_job_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def job(
        self,
        job_name: str,
    ) -> JobDomain:
        return JobDomain(
            self._session,
            self._job_cache,
            self._namespace_name,
            self._user_id,
            job_name,
        )

    def dead_letter_job(
        self,
        dead_letter_job_name: str,
    ) -> DeadLetterJobDomain:
        return DeadLetterJobDomain(
            self._session,
            self._dead_letter_job_cache,
            self._namespace_name,
            self._user_id,
            dead_letter_job_name,
        )
