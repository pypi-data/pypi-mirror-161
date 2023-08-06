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


class DeadLetterJobAccessTokenDomain:
    _session: Gs2RestSession
    _client: Gs2JobQueueRestClient
    _dead_letter_job_cache: DeadLetterJobDomainCache
    _namespace_name: str
    _access_token: AccessToken
    _dead_letter_job_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        dead_letter_job_cache: DeadLetterJobDomainCache,
        namespace_name: str,
        access_token: AccessToken,
        dead_letter_job_name: str,
    ):
        self._session = session
        self._client = Gs2JobQueueRestClient(
            session,
        )
        self._dead_letter_job_cache = dead_letter_job_cache
        self._namespace_name = namespace_name
        self._access_token = access_token
        self._dead_letter_job_name = dead_letter_job_name
