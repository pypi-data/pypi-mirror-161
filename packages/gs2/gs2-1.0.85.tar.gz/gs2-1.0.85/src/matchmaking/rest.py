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

from core.rest import *
from core.model import Gs2Constant
from matchmaking.request import *
from matchmaking.result import *


class Gs2MatchmakingRestClient(AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeNamespacesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/status".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetNamespaceStatusResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetNamespaceResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteNamespaceResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeGatheringsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateGatheringResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/user/{userId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateGatheringByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/{gatheringName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.attribute_ranges is not None:
            body["attributeRanges"] = [
                item.to_dict()
                for item in request.attribute_ranges
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=UpdateGatheringResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/{gatheringName}/user/{userId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.attribute_ranges is not None:
            body["attributeRanges"] = [
                item.to_dict()
                for item in request.attribute_ranges
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=UpdateGatheringByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/player/do".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.matchmaking_context_token is not None:
            body["matchmakingContextToken"] = request.matchmaking_context_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=DoMatchmakingByPlayerResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/do".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.matchmaking_context_token is not None:
            body["matchmakingContextToken"] = request.matchmaking_context_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=DoMatchmakingResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/gathering/do".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.player is not None:
            body["player"] = request.player.to_dict()
        if request.matchmaking_context_token is not None:
            body["matchmakingContextToken"] = request.matchmaking_context_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=DoMatchmakingByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/{gatheringName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetGatheringResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/{gatheringName}/user/me".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=CancelMatchmakingResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/{gatheringName}/user/{userId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=CancelMatchmakingByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/gathering/{gatheringName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteGatheringResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master/rating".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeRatingModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master/rating".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.volatility is not None:
            body["volatility"] = request.volatility

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateRatingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master/rating/{ratingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetRatingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master/rating/{ratingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.volatility is not None:
            body["volatility"] = request.volatility

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateRatingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master/rating/{ratingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteRatingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/rating".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeRatingModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/rating/{ratingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetRatingModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master/export".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=ExportMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetCurrentRatingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.settings is not None:
            body["settings"] = request.settings

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateCurrentRatingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/master/from_git_hub".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateCurrentRatingModelMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/rating".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeRatingsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/rating".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeRatingsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/rating/{ratingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetRatingResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/rating/{ratingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetRatingByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/rating/{ratingName}/vote".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.game_results is not None:
            body["gameResults"] = [
                item.to_dict()
                for item in request.game_results
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=PutResultResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/rating/{ratingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteRatingResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/vote/{ratingName}/{gatheringName}/ballot".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.number_of_player is not None:
            body["numberOfPlayer"] = request.number_of_player
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=GetBallotResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/vote/{ratingName}/{gatheringName}/ballot".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.number_of_player is not None:
            body["numberOfPlayer"] = request.number_of_player
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=GetBallotByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/action/vote".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=VoteResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/action/vote/multiple".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=VoteMultipleResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='matchmaking',
            region=self.session.region,
        ) + "/{namespaceName}/vote/{ratingName}/{gatheringName}/action/vote/commit".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            ratingName=request.rating_name if request.rating_name is not None and request.rating_name != '' else 'null',
            gatheringName=request.gathering_name if request.gathering_name is not None and request.gathering_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CommitVoteResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result