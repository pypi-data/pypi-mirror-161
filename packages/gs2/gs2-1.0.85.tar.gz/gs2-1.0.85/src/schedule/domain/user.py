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
from schedule import Gs2ScheduleRestClient, request as request_, result as result_
from schedule.domain.iterator.namespaces import DescribeNamespacesIterator
from schedule.domain.iterator.event_masters import DescribeEventMastersIterator
from schedule.domain.iterator.triggers import DescribeTriggersIterator
from schedule.domain.iterator.triggers_by_user_id import DescribeTriggersByUserIdIterator
from schedule.domain.iterator.events import DescribeEventsIterator
from schedule.domain.iterator.events_by_user_id import DescribeEventsByUserIdIterator
from schedule.domain.iterator.raw_events import DescribeRawEventsIterator
from schedule.domain.cache.namespace import NamespaceDomainCache
from schedule.domain.cache.event_master import EventMasterDomainCache
from schedule.domain.cache.trigger import TriggerDomainCache
from schedule.domain.cache.event import EventDomainCache
from schedule.domain.trigger import TriggerDomain
from schedule.domain.trigger_access_token import TriggerAccessTokenDomain
from schedule.domain.trigger_access_token import TriggerAccessTokenDomain
from schedule.domain.event import EventDomain
from schedule.domain.event_access_token import EventAccessTokenDomain
from schedule.domain.event_access_token import EventAccessTokenDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2ScheduleRestClient
    _namespace_name: str
    _user_id: str
    _trigger_cache: TriggerDomainCache
    _event_cache: EventDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        namespace_name: str,
        user_id: str,
    ):
        self._session = session
        self._client = Gs2ScheduleRestClient(
            session,
        )
        self._namespace_name = namespace_name
        self._user_id = user_id
        self._trigger_cache = TriggerDomainCache()
        self._event_cache = EventDomainCache()

    def triggers(
        self,
    ) -> DescribeTriggersByUserIdIterator:
        return DescribeTriggersByUserIdIterator(
            self._trigger_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def events(
        self,
    ) -> DescribeEventsByUserIdIterator:
        return DescribeEventsByUserIdIterator(
            self._event_cache,
            self._client,
            self._namespace_name,
            self._user_id,
        )

    def raw_events(
        self,
    ) -> DescribeRawEventsIterator:
        return DescribeRawEventsIterator(
            self._event_cache,
            self._client,
            self._namespace_name,
        )

    def trigger(
        self,
        trigger_name: str,
    ) -> TriggerDomain:
        return TriggerDomain(
            self._session,
            self._trigger_cache,
            self._namespace_name,
            self._user_id,
            trigger_name,
        )

    def event(
        self,
        event_name: str,
    ) -> EventDomain:
        return EventDomain(
            self._session,
            self._event_cache,
            self._namespace_name,
            self._user_id,
            event_name,
        )
