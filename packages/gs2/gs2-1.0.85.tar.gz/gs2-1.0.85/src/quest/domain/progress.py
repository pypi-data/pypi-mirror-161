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
from quest import Gs2QuestRestClient, request as request_, result as result_
from quest.domain.iterator.namespaces import DescribeNamespacesIterator
from quest.domain.iterator.quest_group_model_masters import DescribeQuestGroupModelMastersIterator
from quest.domain.iterator.quest_model_masters import DescribeQuestModelMastersIterator
from quest.domain.iterator.progresses_by_user_id import DescribeProgressesByUserIdIterator
from quest.domain.iterator.completed_quest_lists import DescribeCompletedQuestListsIterator
from quest.domain.iterator.completed_quest_lists_by_user_id import DescribeCompletedQuestListsByUserIdIterator
from quest.domain.iterator.quest_group_models import DescribeQuestGroupModelsIterator
from quest.domain.iterator.quest_models import DescribeQuestModelsIterator
from quest.domain.cache.namespace import NamespaceDomainCache
from quest.domain.cache.quest_group_model_master import QuestGroupModelMasterDomainCache
from quest.domain.cache.quest_model_master import QuestModelMasterDomainCache
from quest.domain.cache.progress import ProgressDomainCache
from quest.domain.cache.completed_quest_list import CompletedQuestListDomainCache
from quest.domain.cache.quest_group_model import QuestGroupModelDomainCache
from quest.domain.cache.quest_model import QuestModelDomainCache


class ProgressDomain:
    _session: Gs2RestSession
    _client: Gs2QuestRestClient
    _progress_cache: ProgressDomainCache
    _namespace_name: str
    _user_id: str

    def __init__(
        self,
        session: Gs2RestSession,
        progress_cache: ProgressDomainCache,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2QuestRestClient(
            session,
        )
        self._progress_cache = progress_cache
        self._namespace_name = namespace_name
        self._user_id = user_id

    def load(
        self,
        request: request_.GetProgressByUserIdRequest,
    ) -> result_.GetProgressByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.get_progress_by_user_id(
            request,
        )
        self._progress_cache.update(r.item)
        return r

    def start(
        self,
        request: request_.StartByUserIdRequest,
    ) -> result_.StartByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.start_by_user_id(
            request,
        )
        return r

    def end(
        self,
        request: request_.EndByUserIdRequest,
    ) -> result_.EndByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.end_by_user_id(
            request,
        )
        self._progress_cache.update(r.item)
        return r

    def delete(
        self,
        request: request_.DeleteProgressByUserIdRequest,
    ) -> result_.DeleteProgressByUserIdResult:
        request.with_namespace_name(self._namespace_name)
        request.with_user_id(self._user_id)
        r = self._client.delete_progress_by_user_id(
            request,
        )
        self._progress_cache.delete(r.item)
        return r

    def list(
        self,
    ) -> DescribeProgressesByUserIdIterator:
        return DescribeProgressesByUserIdIterator(
            self._progress_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )
