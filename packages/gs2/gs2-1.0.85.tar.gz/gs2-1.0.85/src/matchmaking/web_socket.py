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
from matchmaking.request import *
from matchmaking.result import *


class Gs2MatchmakingWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
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
            service="matchmaking",
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
        if request.enable_rating is not None:
            body["enableRating"] = request.enable_rating
        if request.create_gathering_trigger_type is not None:
            body["createGatheringTriggerType"] = request.create_gathering_trigger_type
        if request.create_gathering_trigger_realtime_namespace_id is not None:
            body["createGatheringTriggerRealtimeNamespaceId"] = request.create_gathering_trigger_realtime_namespace_id
        if request.create_gathering_trigger_script_id is not None:
            body["createGatheringTriggerScriptId"] = request.create_gathering_trigger_script_id
        if request.complete_matchmaking_trigger_type is not None:
            body["completeMatchmakingTriggerType"] = request.complete_matchmaking_trigger_type
        if request.complete_matchmaking_trigger_realtime_namespace_id is not None:
            body["completeMatchmakingTriggerRealtimeNamespaceId"] = request.complete_matchmaking_trigger_realtime_namespace_id
        if request.complete_matchmaking_trigger_script_id is not None:
            body["completeMatchmakingTriggerScriptId"] = request.complete_matchmaking_trigger_script_id
        if request.join_notification is not None:
            body["joinNotification"] = request.join_notification.to_dict()
        if request.leave_notification is not None:
            body["leaveNotification"] = request.leave_notification.to_dict()
        if request.complete_notification is not None:
            body["completeNotification"] = request.complete_notification.to_dict()
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
            service="matchmaking",
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
            service="matchmaking",
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
            service="matchmaking",
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
        if request.enable_rating is not None:
            body["enableRating"] = request.enable_rating
        if request.create_gathering_trigger_type is not None:
            body["createGatheringTriggerType"] = request.create_gathering_trigger_type
        if request.create_gathering_trigger_realtime_namespace_id is not None:
            body["createGatheringTriggerRealtimeNamespaceId"] = request.create_gathering_trigger_realtime_namespace_id
        if request.create_gathering_trigger_script_id is not None:
            body["createGatheringTriggerScriptId"] = request.create_gathering_trigger_script_id
        if request.complete_matchmaking_trigger_type is not None:
            body["completeMatchmakingTriggerType"] = request.complete_matchmaking_trigger_type
        if request.complete_matchmaking_trigger_realtime_namespace_id is not None:
            body["completeMatchmakingTriggerRealtimeNamespaceId"] = request.complete_matchmaking_trigger_realtime_namespace_id
        if request.complete_matchmaking_trigger_script_id is not None:
            body["completeMatchmakingTriggerScriptId"] = request.complete_matchmaking_trigger_script_id
        if request.join_notification is not None:
            body["joinNotification"] = request.join_notification.to_dict()
        if request.leave_notification is not None:
            body["leaveNotification"] = request.leave_notification.to_dict()
        if request.complete_notification is not None:
            body["completeNotification"] = request.complete_notification.to_dict()
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
            service="matchmaking",
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

    def _describe_gatherings(
        self,
        request: DescribeGatheringsRequest,
        callback: Callable[[AsyncResult[DescribeGatheringsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='describeGatherings',
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
                result_type=DescribeGatheringsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_gatherings(
        self,
        request: DescribeGatheringsRequest,
    ) -> DescribeGatheringsResult:
        async_result = []
        with timeout(30):
            self._describe_gatherings(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_gatherings_async(
        self,
        request: DescribeGatheringsRequest,
    ) -> DescribeGatheringsResult:
        async_result = []
        self._describe_gatherings(
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

    def _create_gathering(
        self,
        request: CreateGatheringRequest,
        callback: Callable[[AsyncResult[CreateGatheringResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='createGathering',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.attribute_ranges is not None:
            body["attributeRanges"] = [
                item.to_dict()
                for item in request.attribute_ranges
            ]
        if request.capacity_of_roles is not None:
            body["capacityOfRoles"] = [
                item.to_dict()
                for item in request.capacity_of_roles
            ]
        if request.allow_user_ids is not None:
            body["allowUserIds"] = [
                item
                for item in request.allow_user_ids
            ]
        if request.expires_at is not None:
            body["expiresAt"] = request.expires_at
        if request.expires_at_time_span is not None:
            body["expiresAtTimeSpan"] = request.expires_at_time_span.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateGatheringResult,
                callback=callback,
                body=body,
            )
        )

    def create_gathering(
        self,
        request: CreateGatheringRequest,
    ) -> CreateGatheringResult:
        async_result = []
        with timeout(30):
            self._create_gathering(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_gathering_async(
        self,
        request: CreateGatheringRequest,
    ) -> CreateGatheringResult:
        async_result = []
        self._create_gathering(
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

    def _create_gathering_by_user_id(
        self,
        request: CreateGatheringByUserIdRequest,
        callback: Callable[[AsyncResult[CreateGatheringByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='createGatheringByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.attribute_ranges is not None:
            body["attributeRanges"] = [
                item.to_dict()
                for item in request.attribute_ranges
            ]
        if request.capacity_of_roles is not None:
            body["capacityOfRoles"] = [
                item.to_dict()
                for item in request.capacity_of_roles
            ]
        if request.allow_user_ids is not None:
            body["allowUserIds"] = [
                item
                for item in request.allow_user_ids
            ]
        if request.expires_at is not None:
            body["expiresAt"] = request.expires_at
        if request.expires_at_time_span is not None:
            body["expiresAtTimeSpan"] = request.expires_at_time_span.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateGatheringByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_gathering_by_user_id(
        self,
        request: CreateGatheringByUserIdRequest,
    ) -> CreateGatheringByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_gathering_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_gathering_by_user_id_async(
        self,
        request: CreateGatheringByUserIdRequest,
    ) -> CreateGatheringByUserIdResult:
        async_result = []
        self._create_gathering_by_user_id(
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

    def _update_gathering(
        self,
        request: UpdateGatheringRequest,
        callback: Callable[[AsyncResult[UpdateGatheringResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='updateGathering',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.attribute_ranges is not None:
            body["attributeRanges"] = [
                item.to_dict()
                for item in request.attribute_ranges
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateGatheringResult,
                callback=callback,
                body=body,
            )
        )

    def update_gathering(
        self,
        request: UpdateGatheringRequest,
    ) -> UpdateGatheringResult:
        async_result = []
        with timeout(30):
            self._update_gathering(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_gathering_async(
        self,
        request: UpdateGatheringRequest,
    ) -> UpdateGatheringResult:
        async_result = []
        self._update_gathering(
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

    def _update_gathering_by_user_id(
        self,
        request: UpdateGatheringByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateGatheringByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='updateGatheringByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.attribute_ranges is not None:
            body["attributeRanges"] = [
                item.to_dict()
                for item in request.attribute_ranges
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateGatheringByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def update_gathering_by_user_id(
        self,
        request: UpdateGatheringByUserIdRequest,
    ) -> UpdateGatheringByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_gathering_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_gathering_by_user_id_async(
        self,
        request: UpdateGatheringByUserIdRequest,
    ) -> UpdateGatheringByUserIdResult:
        async_result = []
        self._update_gathering_by_user_id(
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

    def _do_matchmaking_by_player(
        self,
        request: DoMatchmakingByPlayerRequest,
        callback: Callable[[AsyncResult[DoMatchmakingByPlayerResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='doMatchmakingByPlayer',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.matchmaking_context_token is not None:
            body["matchmakingContextToken"] = request.matchmaking_context_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DoMatchmakingByPlayerResult,
                callback=callback,
                body=body,
            )
        )

    def do_matchmaking_by_player(
        self,
        request: DoMatchmakingByPlayerRequest,
    ) -> DoMatchmakingByPlayerResult:
        async_result = []
        with timeout(30):
            self._do_matchmaking_by_player(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def do_matchmaking_by_player_async(
        self,
        request: DoMatchmakingByPlayerRequest,
    ) -> DoMatchmakingByPlayerResult:
        async_result = []
        self._do_matchmaking_by_player(
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

    def _do_matchmaking(
        self,
        request: DoMatchmakingRequest,
        callback: Callable[[AsyncResult[DoMatchmakingResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='doMatchmaking',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.matchmaking_context_token is not None:
            body["matchmakingContextToken"] = request.matchmaking_context_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DoMatchmakingResult,
                callback=callback,
                body=body,
            )
        )

    def do_matchmaking(
        self,
        request: DoMatchmakingRequest,
    ) -> DoMatchmakingResult:
        async_result = []
        with timeout(30):
            self._do_matchmaking(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def do_matchmaking_async(
        self,
        request: DoMatchmakingRequest,
    ) -> DoMatchmakingResult:
        async_result = []
        self._do_matchmaking(
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

    def _do_matchmaking_by_user_id(
        self,
        request: DoMatchmakingByUserIdRequest,
        callback: Callable[[AsyncResult[DoMatchmakingByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='doMatchmakingByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.matchmaking_context_token is not None:
            body["matchmakingContextToken"] = request.matchmaking_context_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DoMatchmakingByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def do_matchmaking_by_user_id(
        self,
        request: DoMatchmakingByUserIdRequest,
    ) -> DoMatchmakingByUserIdResult:
        async_result = []
        with timeout(30):
            self._do_matchmaking_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def do_matchmaking_by_user_id_async(
        self,
        request: DoMatchmakingByUserIdRequest,
    ) -> DoMatchmakingByUserIdResult:
        async_result = []
        self._do_matchmaking_by_user_id(
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

    def _get_gathering(
        self,
        request: GetGatheringRequest,
        callback: Callable[[AsyncResult[GetGatheringResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='getGathering',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetGatheringResult,
                callback=callback,
                body=body,
            )
        )

    def get_gathering(
        self,
        request: GetGatheringRequest,
    ) -> GetGatheringResult:
        async_result = []
        with timeout(30):
            self._get_gathering(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_gathering_async(
        self,
        request: GetGatheringRequest,
    ) -> GetGatheringResult:
        async_result = []
        self._get_gathering(
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

    def _cancel_matchmaking(
        self,
        request: CancelMatchmakingRequest,
        callback: Callable[[AsyncResult[CancelMatchmakingResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='cancelMatchmaking',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CancelMatchmakingResult,
                callback=callback,
                body=body,
            )
        )

    def cancel_matchmaking(
        self,
        request: CancelMatchmakingRequest,
    ) -> CancelMatchmakingResult:
        async_result = []
        with timeout(30):
            self._cancel_matchmaking(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def cancel_matchmaking_async(
        self,
        request: CancelMatchmakingRequest,
    ) -> CancelMatchmakingResult:
        async_result = []
        self._cancel_matchmaking(
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

    def _cancel_matchmaking_by_user_id(
        self,
        request: CancelMatchmakingByUserIdRequest,
        callback: Callable[[AsyncResult[CancelMatchmakingByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='cancelMatchmakingByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CancelMatchmakingByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def cancel_matchmaking_by_user_id(
        self,
        request: CancelMatchmakingByUserIdRequest,
    ) -> CancelMatchmakingByUserIdResult:
        async_result = []
        with timeout(30):
            self._cancel_matchmaking_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def cancel_matchmaking_by_user_id_async(
        self,
        request: CancelMatchmakingByUserIdRequest,
    ) -> CancelMatchmakingByUserIdResult:
        async_result = []
        self._cancel_matchmaking_by_user_id(
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

    def _delete_gathering(
        self,
        request: DeleteGatheringRequest,
        callback: Callable[[AsyncResult[DeleteGatheringResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='gathering',
            function='deleteGathering',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteGatheringResult,
                callback=callback,
                body=body,
            )
        )

    def delete_gathering(
        self,
        request: DeleteGatheringRequest,
    ) -> DeleteGatheringResult:
        async_result = []
        with timeout(30):
            self._delete_gathering(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_gathering_async(
        self,
        request: DeleteGatheringRequest,
    ) -> DeleteGatheringResult:
        async_result = []
        self._delete_gathering(
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

    def _describe_rating_model_masters(
        self,
        request: DescribeRatingModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeRatingModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ratingModelMaster',
            function='describeRatingModelMasters',
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
                result_type=DescribeRatingModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rating_model_masters(
        self,
        request: DescribeRatingModelMastersRequest,
    ) -> DescribeRatingModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_rating_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rating_model_masters_async(
        self,
        request: DescribeRatingModelMastersRequest,
    ) -> DescribeRatingModelMastersResult:
        async_result = []
        self._describe_rating_model_masters(
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

    def _create_rating_model_master(
        self,
        request: CreateRatingModelMasterRequest,
        callback: Callable[[AsyncResult[CreateRatingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ratingModelMaster',
            function='createRatingModelMaster',
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
        if request.volatility is not None:
            body["volatility"] = request.volatility

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateRatingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_rating_model_master(
        self,
        request: CreateRatingModelMasterRequest,
    ) -> CreateRatingModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_rating_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_rating_model_master_async(
        self,
        request: CreateRatingModelMasterRequest,
    ) -> CreateRatingModelMasterResult:
        async_result = []
        self._create_rating_model_master(
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

    def _get_rating_model_master(
        self,
        request: GetRatingModelMasterRequest,
        callback: Callable[[AsyncResult[GetRatingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ratingModelMaster',
            function='getRatingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetRatingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_rating_model_master(
        self,
        request: GetRatingModelMasterRequest,
    ) -> GetRatingModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_rating_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rating_model_master_async(
        self,
        request: GetRatingModelMasterRequest,
    ) -> GetRatingModelMasterResult:
        async_result = []
        self._get_rating_model_master(
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

    def _update_rating_model_master(
        self,
        request: UpdateRatingModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateRatingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ratingModelMaster',
            function='updateRatingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.volatility is not None:
            body["volatility"] = request.volatility

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateRatingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_rating_model_master(
        self,
        request: UpdateRatingModelMasterRequest,
    ) -> UpdateRatingModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_rating_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_rating_model_master_async(
        self,
        request: UpdateRatingModelMasterRequest,
    ) -> UpdateRatingModelMasterResult:
        async_result = []
        self._update_rating_model_master(
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

    def _delete_rating_model_master(
        self,
        request: DeleteRatingModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteRatingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ratingModelMaster',
            function='deleteRatingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteRatingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_rating_model_master(
        self,
        request: DeleteRatingModelMasterRequest,
    ) -> DeleteRatingModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_rating_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_rating_model_master_async(
        self,
        request: DeleteRatingModelMasterRequest,
    ) -> DeleteRatingModelMasterResult:
        async_result = []
        self._delete_rating_model_master(
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

    def _describe_rating_models(
        self,
        request: DescribeRatingModelsRequest,
        callback: Callable[[AsyncResult[DescribeRatingModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ratingModel',
            function='describeRatingModels',
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
                result_type=DescribeRatingModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rating_models(
        self,
        request: DescribeRatingModelsRequest,
    ) -> DescribeRatingModelsResult:
        async_result = []
        with timeout(30):
            self._describe_rating_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rating_models_async(
        self,
        request: DescribeRatingModelsRequest,
    ) -> DescribeRatingModelsResult:
        async_result = []
        self._describe_rating_models(
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

    def _get_rating_model(
        self,
        request: GetRatingModelRequest,
        callback: Callable[[AsyncResult[GetRatingModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ratingModel',
            function='getRatingModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetRatingModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_rating_model(
        self,
        request: GetRatingModelRequest,
    ) -> GetRatingModelResult:
        async_result = []
        with timeout(30):
            self._get_rating_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rating_model_async(
        self,
        request: GetRatingModelRequest,
    ) -> GetRatingModelResult:
        async_result = []
        self._get_rating_model(
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
            service="matchmaking",
            component='currentRatingModelMaster',
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

    def _get_current_rating_model_master(
        self,
        request: GetCurrentRatingModelMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentRatingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='currentRatingModelMaster',
            function='getCurrentRatingModelMaster',
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
                result_type=GetCurrentRatingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_rating_model_master(
        self,
        request: GetCurrentRatingModelMasterRequest,
    ) -> GetCurrentRatingModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_rating_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_rating_model_master_async(
        self,
        request: GetCurrentRatingModelMasterRequest,
    ) -> GetCurrentRatingModelMasterResult:
        async_result = []
        self._get_current_rating_model_master(
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

    def _update_current_rating_model_master(
        self,
        request: UpdateCurrentRatingModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRatingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='currentRatingModelMaster',
            function='updateCurrentRatingModelMaster',
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
                result_type=UpdateCurrentRatingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_rating_model_master(
        self,
        request: UpdateCurrentRatingModelMasterRequest,
    ) -> UpdateCurrentRatingModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_rating_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_rating_model_master_async(
        self,
        request: UpdateCurrentRatingModelMasterRequest,
    ) -> UpdateCurrentRatingModelMasterResult:
        async_result = []
        self._update_current_rating_model_master(
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

    def _update_current_rating_model_master_from_git_hub(
        self,
        request: UpdateCurrentRatingModelMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRatingModelMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='currentRatingModelMaster',
            function='updateCurrentRatingModelMasterFromGitHub',
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
                result_type=UpdateCurrentRatingModelMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_rating_model_master_from_git_hub(
        self,
        request: UpdateCurrentRatingModelMasterFromGitHubRequest,
    ) -> UpdateCurrentRatingModelMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_rating_model_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_rating_model_master_from_git_hub_async(
        self,
        request: UpdateCurrentRatingModelMasterFromGitHubRequest,
    ) -> UpdateCurrentRatingModelMasterFromGitHubResult:
        async_result = []
        self._update_current_rating_model_master_from_git_hub(
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

    def _describe_ratings(
        self,
        request: DescribeRatingsRequest,
        callback: Callable[[AsyncResult[DescribeRatingsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='rating',
            function='describeRatings',
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
                result_type=DescribeRatingsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_ratings(
        self,
        request: DescribeRatingsRequest,
    ) -> DescribeRatingsResult:
        async_result = []
        with timeout(30):
            self._describe_ratings(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_ratings_async(
        self,
        request: DescribeRatingsRequest,
    ) -> DescribeRatingsResult:
        async_result = []
        self._describe_ratings(
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

    def _describe_ratings_by_user_id(
        self,
        request: DescribeRatingsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeRatingsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='rating',
            function='describeRatingsByUserId',
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
                result_type=DescribeRatingsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_ratings_by_user_id(
        self,
        request: DescribeRatingsByUserIdRequest,
    ) -> DescribeRatingsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_ratings_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_ratings_by_user_id_async(
        self,
        request: DescribeRatingsByUserIdRequest,
    ) -> DescribeRatingsByUserIdResult:
        async_result = []
        self._describe_ratings_by_user_id(
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

    def _get_rating(
        self,
        request: GetRatingRequest,
        callback: Callable[[AsyncResult[GetRatingResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='rating',
            function='getRating',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetRatingResult,
                callback=callback,
                body=body,
            )
        )

    def get_rating(
        self,
        request: GetRatingRequest,
    ) -> GetRatingResult:
        async_result = []
        with timeout(30):
            self._get_rating(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rating_async(
        self,
        request: GetRatingRequest,
    ) -> GetRatingResult:
        async_result = []
        self._get_rating(
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

    def _get_rating_by_user_id(
        self,
        request: GetRatingByUserIdRequest,
        callback: Callable[[AsyncResult[GetRatingByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='rating',
            function='getRatingByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetRatingByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_rating_by_user_id(
        self,
        request: GetRatingByUserIdRequest,
    ) -> GetRatingByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_rating_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rating_by_user_id_async(
        self,
        request: GetRatingByUserIdRequest,
    ) -> GetRatingByUserIdResult:
        async_result = []
        self._get_rating_by_user_id(
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

    def _put_result(
        self,
        request: PutResultRequest,
        callback: Callable[[AsyncResult[PutResultResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='rating',
            function='putResult',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name
        if request.game_results is not None:
            body["gameResults"] = [
                item.to_dict()
                for item in request.game_results
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=PutResultResult,
                callback=callback,
                body=body,
            )
        )

    def put_result(
        self,
        request: PutResultRequest,
    ) -> PutResultResult:
        async_result = []
        with timeout(30):
            self._put_result(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_result_async(
        self,
        request: PutResultRequest,
    ) -> PutResultResult:
        async_result = []
        self._put_result(
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

    def _delete_rating(
        self,
        request: DeleteRatingRequest,
        callback: Callable[[AsyncResult[DeleteRatingResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='rating',
            function='deleteRating',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteRatingResult,
                callback=callback,
                body=body,
            )
        )

    def delete_rating(
        self,
        request: DeleteRatingRequest,
    ) -> DeleteRatingResult:
        async_result = []
        with timeout(30):
            self._delete_rating(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_rating_async(
        self,
        request: DeleteRatingRequest,
    ) -> DeleteRatingResult:
        async_result = []
        self._delete_rating(
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

    def _get_ballot(
        self,
        request: GetBallotRequest,
        callback: Callable[[AsyncResult[GetBallotResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ballot',
            function='getBallot',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.number_of_player is not None:
            body["numberOfPlayer"] = request.number_of_player
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetBallotResult,
                callback=callback,
                body=body,
            )
        )

    def get_ballot(
        self,
        request: GetBallotRequest,
    ) -> GetBallotResult:
        async_result = []
        with timeout(30):
            self._get_ballot(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_ballot_async(
        self,
        request: GetBallotRequest,
    ) -> GetBallotResult:
        async_result = []
        self._get_ballot(
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

    def _get_ballot_by_user_id(
        self,
        request: GetBallotByUserIdRequest,
        callback: Callable[[AsyncResult[GetBallotByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='ballot',
            function='getBallotByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.number_of_player is not None:
            body["numberOfPlayer"] = request.number_of_player
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetBallotByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_ballot_by_user_id(
        self,
        request: GetBallotByUserIdRequest,
    ) -> GetBallotByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_ballot_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_ballot_by_user_id_async(
        self,
        request: GetBallotByUserIdRequest,
    ) -> GetBallotByUserIdResult:
        async_result = []
        self._get_ballot_by_user_id(
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

    def _vote(
        self,
        request: VoteRequest,
        callback: Callable[[AsyncResult[VoteResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='vote',
            function='vote',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ballot_body is not None:
            body["ballotBody"] = request.ballot_body
        if request.ballot_signature is not None:
            body["ballotSignature"] = request.ballot_signature
        if request.game_results is not None:
            body["gameResults"] = [
                item.to_dict()
                for item in request.game_results
            ]
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=VoteResult,
                callback=callback,
                body=body,
            )
        )

    def vote(
        self,
        request: VoteRequest,
    ) -> VoteResult:
        async_result = []
        with timeout(30):
            self._vote(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def vote_async(
        self,
        request: VoteRequest,
    ) -> VoteResult:
        async_result = []
        self._vote(
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

    def _vote_multiple(
        self,
        request: VoteMultipleRequest,
        callback: Callable[[AsyncResult[VoteMultipleResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='vote',
            function='voteMultiple',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.signed_ballots is not None:
            body["signedBallots"] = [
                item.to_dict()
                for item in request.signed_ballots
            ]
        if request.game_results is not None:
            body["gameResults"] = [
                item.to_dict()
                for item in request.game_results
            ]
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=VoteMultipleResult,
                callback=callback,
                body=body,
            )
        )

    def vote_multiple(
        self,
        request: VoteMultipleRequest,
    ) -> VoteMultipleResult:
        async_result = []
        with timeout(30):
            self._vote_multiple(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def vote_multiple_async(
        self,
        request: VoteMultipleRequest,
    ) -> VoteMultipleResult:
        async_result = []
        self._vote_multiple(
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

    def _commit_vote(
        self,
        request: CommitVoteRequest,
        callback: Callable[[AsyncResult[CommitVoteResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="matchmaking",
            component='vote',
            function='commitVote',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.rating_name is not None:
            body["ratingName"] = request.rating_name
        if request.gathering_name is not None:
            body["gatheringName"] = request.gathering_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CommitVoteResult,
                callback=callback,
                body=body,
            )
        )

    def commit_vote(
        self,
        request: CommitVoteRequest,
    ) -> CommitVoteResult:
        async_result = []
        with timeout(30):
            self._commit_vote(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def commit_vote_async(
        self,
        request: CommitVoteRequest,
    ) -> CommitVoteResult:
        async_result = []
        self._commit_vote(
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