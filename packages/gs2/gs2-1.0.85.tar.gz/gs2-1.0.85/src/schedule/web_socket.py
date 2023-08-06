# encoding: utf-8
#
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

import time
from core.web_socket import *
from core.model import Gs2Constant
from schedule.request import *
from schedule.result import *


class Gs2ScheduleWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='namespace',
            function='describeNamespaces',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeNamespacesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
    ) -> DescribeNamespacesResult:
        async_result = []
        with timeout(30):
            self._describe_namespaces(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_namespaces_async(
        self,
        request: DescribeNamespacesRequest,
    ) -> DescribeNamespacesResult:
        async_result = []
        self._describe_namespaces(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_namespace(
        self,
        request: CreateNamespaceRequest,
        callback: Callable[[AsyncResult[CreateNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='namespace',
            function='createNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def create_namespace(
        self,
        request: CreateNamespaceRequest,
    ) -> CreateNamespaceResult:
        async_result = []
        with timeout(30):
            self._create_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_namespace_async(
        self,
        request: CreateNamespaceRequest,
    ) -> CreateNamespaceResult:
        async_result = []
        self._create_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_namespace_status(
        self,
        request: GetNamespaceStatusRequest,
        callback: Callable[[AsyncResult[GetNamespaceStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='namespace',
            function='getNamespaceStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetNamespaceStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_namespace_status(
        self,
        request: GetNamespaceStatusRequest,
    ) -> GetNamespaceStatusResult:
        async_result = []
        with timeout(30):
            self._get_namespace_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_namespace_status_async(
        self,
        request: GetNamespaceStatusRequest,
    ) -> GetNamespaceStatusResult:
        async_result = []
        self._get_namespace_status(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_namespace(
        self,
        request: GetNamespaceRequest,
        callback: Callable[[AsyncResult[GetNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='namespace',
            function='getNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def get_namespace(
        self,
        request: GetNamespaceRequest,
    ) -> GetNamespaceResult:
        async_result = []
        with timeout(30):
            self._get_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_namespace_async(
        self,
        request: GetNamespaceRequest,
    ) -> GetNamespaceResult:
        async_result = []
        self._get_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_namespace(
        self,
        request: UpdateNamespaceRequest,
        callback: Callable[[AsyncResult[UpdateNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='namespace',
            function='updateNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.description is not None:
            body["description"] = request.description
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def update_namespace(
        self,
        request: UpdateNamespaceRequest,
    ) -> UpdateNamespaceResult:
        async_result = []
        with timeout(30):
            self._update_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_namespace_async(
        self,
        request: UpdateNamespaceRequest,
    ) -> UpdateNamespaceResult:
        async_result = []
        self._update_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_namespace(
        self,
        request: DeleteNamespaceRequest,
        callback: Callable[[AsyncResult[DeleteNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='namespace',
            function='deleteNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def delete_namespace(
        self,
        request: DeleteNamespaceRequest,
    ) -> DeleteNamespaceResult:
        async_result = []
        with timeout(30):
            self._delete_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_namespace_async(
        self,
        request: DeleteNamespaceRequest,
    ) -> DeleteNamespaceResult:
        async_result = []
        self._delete_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_event_masters(
        self,
        request: DescribeEventMastersRequest,
        callback: Callable[[AsyncResult[DescribeEventMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='eventMaster',
            function='describeEventMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeEventMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_event_masters(
        self,
        request: DescribeEventMastersRequest,
    ) -> DescribeEventMastersResult:
        async_result = []
        with timeout(30):
            self._describe_event_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_event_masters_async(
        self,
        request: DescribeEventMastersRequest,
    ) -> DescribeEventMastersResult:
        async_result = []
        self._describe_event_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_event_master(
        self,
        request: CreateEventMasterRequest,
        callback: Callable[[AsyncResult[CreateEventMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='eventMaster',
            function='createEventMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.schedule_type is not None:
            body["scheduleType"] = request.schedule_type
        if request.absolute_begin is not None:
            body["absoluteBegin"] = request.absolute_begin
        if request.absolute_end is not None:
            body["absoluteEnd"] = request.absolute_end
        if request.repeat_type is not None:
            body["repeatType"] = request.repeat_type
        if request.repeat_begin_day_of_month is not None:
            body["repeatBeginDayOfMonth"] = request.repeat_begin_day_of_month
        if request.repeat_end_day_of_month is not None:
            body["repeatEndDayOfMonth"] = request.repeat_end_day_of_month
        if request.repeat_begin_day_of_week is not None:
            body["repeatBeginDayOfWeek"] = request.repeat_begin_day_of_week
        if request.repeat_end_day_of_week is not None:
            body["repeatEndDayOfWeek"] = request.repeat_end_day_of_week
        if request.repeat_begin_hour is not None:
            body["repeatBeginHour"] = request.repeat_begin_hour
        if request.repeat_end_hour is not None:
            body["repeatEndHour"] = request.repeat_end_hour
        if request.relative_trigger_name is not None:
            body["relativeTriggerName"] = request.relative_trigger_name
        if request.relative_duration is not None:
            body["relativeDuration"] = request.relative_duration

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateEventMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_event_master(
        self,
        request: CreateEventMasterRequest,
    ) -> CreateEventMasterResult:
        async_result = []
        with timeout(30):
            self._create_event_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_event_master_async(
        self,
        request: CreateEventMasterRequest,
    ) -> CreateEventMasterResult:
        async_result = []
        self._create_event_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_event_master(
        self,
        request: GetEventMasterRequest,
        callback: Callable[[AsyncResult[GetEventMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='eventMaster',
            function='getEventMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.event_name is not None:
            body["eventName"] = request.event_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetEventMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_event_master(
        self,
        request: GetEventMasterRequest,
    ) -> GetEventMasterResult:
        async_result = []
        with timeout(30):
            self._get_event_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_event_master_async(
        self,
        request: GetEventMasterRequest,
    ) -> GetEventMasterResult:
        async_result = []
        self._get_event_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_event_master(
        self,
        request: UpdateEventMasterRequest,
        callback: Callable[[AsyncResult[UpdateEventMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='eventMaster',
            function='updateEventMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.event_name is not None:
            body["eventName"] = request.event_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.schedule_type is not None:
            body["scheduleType"] = request.schedule_type
        if request.absolute_begin is not None:
            body["absoluteBegin"] = request.absolute_begin
        if request.absolute_end is not None:
            body["absoluteEnd"] = request.absolute_end
        if request.repeat_type is not None:
            body["repeatType"] = request.repeat_type
        if request.repeat_begin_day_of_month is not None:
            body["repeatBeginDayOfMonth"] = request.repeat_begin_day_of_month
        if request.repeat_end_day_of_month is not None:
            body["repeatEndDayOfMonth"] = request.repeat_end_day_of_month
        if request.repeat_begin_day_of_week is not None:
            body["repeatBeginDayOfWeek"] = request.repeat_begin_day_of_week
        if request.repeat_end_day_of_week is not None:
            body["repeatEndDayOfWeek"] = request.repeat_end_day_of_week
        if request.repeat_begin_hour is not None:
            body["repeatBeginHour"] = request.repeat_begin_hour
        if request.repeat_end_hour is not None:
            body["repeatEndHour"] = request.repeat_end_hour
        if request.relative_trigger_name is not None:
            body["relativeTriggerName"] = request.relative_trigger_name
        if request.relative_duration is not None:
            body["relativeDuration"] = request.relative_duration

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateEventMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_event_master(
        self,
        request: UpdateEventMasterRequest,
    ) -> UpdateEventMasterResult:
        async_result = []
        with timeout(30):
            self._update_event_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_event_master_async(
        self,
        request: UpdateEventMasterRequest,
    ) -> UpdateEventMasterResult:
        async_result = []
        self._update_event_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_event_master(
        self,
        request: DeleteEventMasterRequest,
        callback: Callable[[AsyncResult[DeleteEventMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='eventMaster',
            function='deleteEventMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.event_name is not None:
            body["eventName"] = request.event_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteEventMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_event_master(
        self,
        request: DeleteEventMasterRequest,
    ) -> DeleteEventMasterResult:
        async_result = []
        with timeout(30):
            self._delete_event_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_event_master_async(
        self,
        request: DeleteEventMasterRequest,
    ) -> DeleteEventMasterResult:
        async_result = []
        self._delete_event_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_triggers(
        self,
        request: DescribeTriggersRequest,
        callback: Callable[[AsyncResult[DescribeTriggersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='trigger',
            function='describeTriggers',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeTriggersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_triggers(
        self,
        request: DescribeTriggersRequest,
    ) -> DescribeTriggersResult:
        async_result = []
        with timeout(30):
            self._describe_triggers(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_triggers_async(
        self,
        request: DescribeTriggersRequest,
    ) -> DescribeTriggersResult:
        async_result = []
        self._describe_triggers(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_triggers_by_user_id(
        self,
        request: DescribeTriggersByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeTriggersByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='trigger',
            function='describeTriggersByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeTriggersByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_triggers_by_user_id(
        self,
        request: DescribeTriggersByUserIdRequest,
    ) -> DescribeTriggersByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_triggers_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_triggers_by_user_id_async(
        self,
        request: DescribeTriggersByUserIdRequest,
    ) -> DescribeTriggersByUserIdResult:
        async_result = []
        self._describe_triggers_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_trigger(
        self,
        request: GetTriggerRequest,
        callback: Callable[[AsyncResult[GetTriggerResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='trigger',
            function='getTrigger',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.trigger_name is not None:
            body["triggerName"] = request.trigger_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetTriggerResult,
                callback=callback,
                body=body,
            )
        )

    def get_trigger(
        self,
        request: GetTriggerRequest,
    ) -> GetTriggerResult:
        async_result = []
        with timeout(30):
            self._get_trigger(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_trigger_async(
        self,
        request: GetTriggerRequest,
    ) -> GetTriggerResult:
        async_result = []
        self._get_trigger(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_trigger_by_user_id(
        self,
        request: GetTriggerByUserIdRequest,
        callback: Callable[[AsyncResult[GetTriggerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='trigger',
            function='getTriggerByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.trigger_name is not None:
            body["triggerName"] = request.trigger_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetTriggerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_trigger_by_user_id(
        self,
        request: GetTriggerByUserIdRequest,
    ) -> GetTriggerByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_trigger_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_trigger_by_user_id_async(
        self,
        request: GetTriggerByUserIdRequest,
    ) -> GetTriggerByUserIdResult:
        async_result = []
        self._get_trigger_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _trigger_by_user_id(
        self,
        request: TriggerByUserIdRequest,
        callback: Callable[[AsyncResult[TriggerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='trigger',
            function='triggerByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.trigger_name is not None:
            body["triggerName"] = request.trigger_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.trigger_strategy is not None:
            body["triggerStrategy"] = request.trigger_strategy
        if request.ttl is not None:
            body["ttl"] = request.ttl

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=TriggerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def trigger_by_user_id(
        self,
        request: TriggerByUserIdRequest,
    ) -> TriggerByUserIdResult:
        async_result = []
        with timeout(30):
            self._trigger_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def trigger_by_user_id_async(
        self,
        request: TriggerByUserIdRequest,
    ) -> TriggerByUserIdResult:
        async_result = []
        self._trigger_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_trigger(
        self,
        request: DeleteTriggerRequest,
        callback: Callable[[AsyncResult[DeleteTriggerResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='trigger',
            function='deleteTrigger',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.trigger_name is not None:
            body["triggerName"] = request.trigger_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteTriggerResult,
                callback=callback,
                body=body,
            )
        )

    def delete_trigger(
        self,
        request: DeleteTriggerRequest,
    ) -> DeleteTriggerResult:
        async_result = []
        with timeout(30):
            self._delete_trigger(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_trigger_async(
        self,
        request: DeleteTriggerRequest,
    ) -> DeleteTriggerResult:
        async_result = []
        self._delete_trigger(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_trigger_by_user_id(
        self,
        request: DeleteTriggerByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteTriggerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='trigger',
            function='deleteTriggerByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.trigger_name is not None:
            body["triggerName"] = request.trigger_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteTriggerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_trigger_by_user_id(
        self,
        request: DeleteTriggerByUserIdRequest,
    ) -> DeleteTriggerByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_trigger_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_trigger_by_user_id_async(
        self,
        request: DeleteTriggerByUserIdRequest,
    ) -> DeleteTriggerByUserIdResult:
        async_result = []
        self._delete_trigger_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_events(
        self,
        request: DescribeEventsRequest,
        callback: Callable[[AsyncResult[DescribeEventsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='event',
            function='describeEvents',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeEventsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_events(
        self,
        request: DescribeEventsRequest,
    ) -> DescribeEventsResult:
        async_result = []
        with timeout(30):
            self._describe_events(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_events_async(
        self,
        request: DescribeEventsRequest,
    ) -> DescribeEventsResult:
        async_result = []
        self._describe_events(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_events_by_user_id(
        self,
        request: DescribeEventsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeEventsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='event',
            function='describeEventsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeEventsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_events_by_user_id(
        self,
        request: DescribeEventsByUserIdRequest,
    ) -> DescribeEventsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_events_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_events_by_user_id_async(
        self,
        request: DescribeEventsByUserIdRequest,
    ) -> DescribeEventsByUserIdResult:
        async_result = []
        self._describe_events_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_raw_events(
        self,
        request: DescribeRawEventsRequest,
        callback: Callable[[AsyncResult[DescribeRawEventsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='event',
            function='describeRawEvents',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeRawEventsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_raw_events(
        self,
        request: DescribeRawEventsRequest,
    ) -> DescribeRawEventsResult:
        async_result = []
        with timeout(30):
            self._describe_raw_events(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_raw_events_async(
        self,
        request: DescribeRawEventsRequest,
    ) -> DescribeRawEventsResult:
        async_result = []
        self._describe_raw_events(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_event(
        self,
        request: GetEventRequest,
        callback: Callable[[AsyncResult[GetEventResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='event',
            function='getEvent',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.event_name is not None:
            body["eventName"] = request.event_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetEventResult,
                callback=callback,
                body=body,
            )
        )

    def get_event(
        self,
        request: GetEventRequest,
    ) -> GetEventResult:
        async_result = []
        with timeout(30):
            self._get_event(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_event_async(
        self,
        request: GetEventRequest,
    ) -> GetEventResult:
        async_result = []
        self._get_event(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_event_by_user_id(
        self,
        request: GetEventByUserIdRequest,
        callback: Callable[[AsyncResult[GetEventByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='event',
            function='getEventByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.event_name is not None:
            body["eventName"] = request.event_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetEventByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_event_by_user_id(
        self,
        request: GetEventByUserIdRequest,
    ) -> GetEventByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_event_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_event_by_user_id_async(
        self,
        request: GetEventByUserIdRequest,
    ) -> GetEventByUserIdResult:
        async_result = []
        self._get_event_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_raw_event(
        self,
        request: GetRawEventRequest,
        callback: Callable[[AsyncResult[GetRawEventResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='event',
            function='getRawEvent',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.event_name is not None:
            body["eventName"] = request.event_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetRawEventResult,
                callback=callback,
                body=body,
            )
        )

    def get_raw_event(
        self,
        request: GetRawEventRequest,
    ) -> GetRawEventResult:
        async_result = []
        with timeout(30):
            self._get_raw_event(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_raw_event_async(
        self,
        request: GetRawEventRequest,
    ) -> GetRawEventResult:
        async_result = []
        self._get_raw_event(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _export_master(
        self,
        request: ExportMasterRequest,
        callback: Callable[[AsyncResult[ExportMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='currentEventMaster',
            function='exportMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=ExportMasterResult,
                callback=callback,
                body=body,
            )
        )

    def export_master(
        self,
        request: ExportMasterRequest,
    ) -> ExportMasterResult:
        async_result = []
        with timeout(30):
            self._export_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def export_master_async(
        self,
        request: ExportMasterRequest,
    ) -> ExportMasterResult:
        async_result = []
        self._export_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_current_event_master(
        self,
        request: GetCurrentEventMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentEventMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='currentEventMaster',
            function='getCurrentEventMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetCurrentEventMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_event_master(
        self,
        request: GetCurrentEventMasterRequest,
    ) -> GetCurrentEventMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_event_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_event_master_async(
        self,
        request: GetCurrentEventMasterRequest,
    ) -> GetCurrentEventMasterResult:
        async_result = []
        self._get_current_event_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_event_master(
        self,
        request: UpdateCurrentEventMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentEventMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='currentEventMaster',
            function='updateCurrentEventMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.settings is not None:
            body["settings"] = request.settings

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateCurrentEventMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_event_master(
        self,
        request: UpdateCurrentEventMasterRequest,
    ) -> UpdateCurrentEventMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_event_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_event_master_async(
        self,
        request: UpdateCurrentEventMasterRequest,
    ) -> UpdateCurrentEventMasterResult:
        async_result = []
        self._update_current_event_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_event_master_from_git_hub(
        self,
        request: UpdateCurrentEventMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentEventMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="schedule",
            component='currentEventMaster',
            function='updateCurrentEventMasterFromGitHub',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateCurrentEventMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_event_master_from_git_hub(
        self,
        request: UpdateCurrentEventMasterFromGitHubRequest,
    ) -> UpdateCurrentEventMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_event_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_event_master_from_git_hub_async(
        self,
        request: UpdateCurrentEventMasterFromGitHubRequest,
    ) -> UpdateCurrentEventMasterFromGitHubResult:
        async_result = []
        self._update_current_event_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result