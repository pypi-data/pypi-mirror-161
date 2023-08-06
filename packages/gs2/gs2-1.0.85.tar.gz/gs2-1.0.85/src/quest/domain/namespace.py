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
from quest.domain.user import UserDomain
from quest.domain.user_access_token import UserAccessTokenDomain
from quest.domain.user_access_token import UserAccessTokenDomain
from quest.domain.current_quest_master import CurrentQuestMasterDomain
from quest.domain.quest_group_model import QuestGroupModelDomain
from quest.domain.quest_group_model_master import QuestGroupModelMasterDomain


class NamespaceDomain:
    _session: Gs2RestSession
    _client: Gs2QuestRestClient
    _namespace_cache: NamespaceDomainCache
    _namespace_name: str
    _quest_group_model_master_cache: QuestGroupModelMasterDomainCache
    _quest_group_model_cache: QuestGroupModelDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_cache: NamespaceDomainCache,
        namespace_name: str,
    ):
        self._session = session
        self._client = Gs2QuestRestClient(
            session,
        )
        self._namespace_cache = namespace_cache
        self._namespace_name = namespace_name
        self._quest_group_model_master_cache = QuestGroupModelMasterDomainCache()
        self._quest_group_model_cache = QuestGroupModelDomainCache()

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

    def create_quest_group_model_master(
        self,
        request: request_.CreateQuestGroupModelMasterRequest,
    ) -> result_.CreateQuestGroupModelMasterResult:
        request.with_namespace_name(self._namespace_name)
        r = self._client.create_quest_group_model_master(
            request,
        )
        return r

    def quest_group_model_masters(
        self,
    ) -> DescribeQuestGroupModelMastersIterator:
        return DescribeQuestGroupModelMastersIterator(
            self._quest_group_model_master_cache,
            self._client,
            self._namespace_name,
        )

    def quest_group_models(
        self,
    ) -> DescribeQuestGroupModelsIterator:
        return DescribeQuestGroupModelsIterator(
            self._quest_group_model_cache,
            self._client,
            self._namespace_name,
        )

    def user(
        self,
        user_id: str,
    ) -> UserDomain:
        return UserDomain(
            self._session,
            self._namespace_name,
            user_id,
        )

    def access_token(
        self,
        access_token: AccessToken,
    ) -> UserAccessTokenDomain:
        return UserAccessTokenDomain(
            self._session,
            self._namespace_name,
            access_token,
        )

    def current_quest_master(
        self,
    ) -> CurrentQuestMasterDomain:
        return CurrentQuestMasterDomain(
            self._session,
            self._namespace_name,
        )

    def quest_group_model(
        self,
        quest_group_name: str,
    ) -> QuestGroupModelDomain:
        return QuestGroupModelDomain(
            self._session,
            self._quest_group_model_cache,
            self._namespace_name,
            quest_group_name,
        )

    def quest_group_model_master(
        self,
        quest_group_name: str,
    ) -> QuestGroupModelMasterDomain:
        return QuestGroupModelMasterDomain(
            self._session,
            self._quest_group_model_master_cache,
            self._namespace_name,
            quest_group_name,
        )
