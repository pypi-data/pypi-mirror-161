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


class CurrentQuestMasterDomain:
    _session: Gs2RestSession
    _client: Gs2QuestRestClient
    _namespace_name: str

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2QuestRestClient(
            session,
        )
        self._namespace_name = namespace_name

    def export_master(
        self,
        request: request_.ExportMasterRequest,
    ) -> result_.ExportMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.export_master(
            request,
        )
        return r

    def load(
        self,
        request: request_.GetCurrentQuestMasterRequest,
    ) -> result_.GetCurrentQuestMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.get_current_quest_master(
            request,
        )
        return r

    def update(
        self,
        request: request_.UpdateCurrentQuestMasterRequest,
    ) -> result_.UpdateCurrentQuestMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_quest_master(
            request,
        )
        return r

    def update_from_git_hub(
        self,
        request: request_.UpdateCurrentQuestMasterFromGitHubRequest,
    ) -> result_.UpdateCurrentQuestMasterFromGitHubResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.update_current_quest_master_from_git_hub(
            request,
        )
        return r
