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
from chat.request import *
from chat.result import *


class Gs2ChatWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
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
            service="chat",
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
        if request.allow_create_room is not None:
            body["allowCreateRoom"] = request.allow_create_room
        if request.post_message_script is not None:
            body["postMessageScript"] = request.post_message_script.to_dict()
        if request.create_room_script is not None:
            body["createRoomScript"] = request.create_room_script.to_dict()
        if request.delete_room_script is not None:
            body["deleteRoomScript"] = request.delete_room_script.to_dict()
        if request.subscribe_room_script is not None:
            body["subscribeRoomScript"] = request.subscribe_room_script.to_dict()
        if request.unsubscribe_room_script is not None:
            body["unsubscribeRoomScript"] = request.unsubscribe_room_script.to_dict()
        if request.post_notification is not None:
            body["postNotification"] = request.post_notification.to_dict()
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
        if request.allow_create_room is not None:
            body["allowCreateRoom"] = request.allow_create_room
        if request.post_message_script is not None:
            body["postMessageScript"] = request.post_message_script.to_dict()
        if request.create_room_script is not None:
            body["createRoomScript"] = request.create_room_script.to_dict()
        if request.delete_room_script is not None:
            body["deleteRoomScript"] = request.delete_room_script.to_dict()
        if request.subscribe_room_script is not None:
            body["subscribeRoomScript"] = request.subscribe_room_script.to_dict()
        if request.unsubscribe_room_script is not None:
            body["unsubscribeRoomScript"] = request.unsubscribe_room_script.to_dict()
        if request.post_notification is not None:
            body["postNotification"] = request.post_notification.to_dict()
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
            service="chat",
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

    def _describe_rooms(
        self,
        request: DescribeRoomsRequest,
        callback: Callable[[AsyncResult[DescribeRoomsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='describeRooms',
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
                result_type=DescribeRoomsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rooms(
        self,
        request: DescribeRoomsRequest,
    ) -> DescribeRoomsResult:
        async_result = []
        with timeout(30):
            self._describe_rooms(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rooms_async(
        self,
        request: DescribeRoomsRequest,
    ) -> DescribeRoomsResult:
        async_result = []
        self._describe_rooms(
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

    def _create_room(
        self,
        request: CreateRoomRequest,
        callback: Callable[[AsyncResult[CreateRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='createRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.name is not None:
            body["name"] = request.name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateRoomResult,
                callback=callback,
                body=body,
            )
        )

    def create_room(
        self,
        request: CreateRoomRequest,
    ) -> CreateRoomResult:
        async_result = []
        with timeout(30):
            self._create_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_room_async(
        self,
        request: CreateRoomRequest,
    ) -> CreateRoomResult:
        async_result = []
        self._create_room(
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

    def _create_room_from_backend(
        self,
        request: CreateRoomFromBackendRequest,
        callback: Callable[[AsyncResult[CreateRoomFromBackendResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='createRoomFromBackend',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateRoomFromBackendResult,
                callback=callback,
                body=body,
            )
        )

    def create_room_from_backend(
        self,
        request: CreateRoomFromBackendRequest,
    ) -> CreateRoomFromBackendResult:
        async_result = []
        with timeout(30):
            self._create_room_from_backend(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_room_from_backend_async(
        self,
        request: CreateRoomFromBackendRequest,
    ) -> CreateRoomFromBackendResult:
        async_result = []
        self._create_room_from_backend(
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

    def _get_room(
        self,
        request: GetRoomRequest,
        callback: Callable[[AsyncResult[GetRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='getRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetRoomResult,
                callback=callback,
                body=body,
            )
        )

    def get_room(
        self,
        request: GetRoomRequest,
    ) -> GetRoomResult:
        async_result = []
        with timeout(30):
            self._get_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_room_async(
        self,
        request: GetRoomRequest,
    ) -> GetRoomResult:
        async_result = []
        self._get_room(
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

    def _update_room(
        self,
        request: UpdateRoomRequest,
        callback: Callable[[AsyncResult[UpdateRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='updateRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
            ]
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateRoomResult,
                callback=callback,
                body=body,
            )
        )

    def update_room(
        self,
        request: UpdateRoomRequest,
    ) -> UpdateRoomResult:
        async_result = []
        with timeout(30):
            self._update_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_room_async(
        self,
        request: UpdateRoomRequest,
    ) -> UpdateRoomResult:
        async_result = []
        self._update_room(
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

    def _update_room_from_backend(
        self,
        request: UpdateRoomFromBackendRequest,
        callback: Callable[[AsyncResult[UpdateRoomFromBackendResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='updateRoomFromBackend',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
            ]
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateRoomFromBackendResult,
                callback=callback,
                body=body,
            )
        )

    def update_room_from_backend(
        self,
        request: UpdateRoomFromBackendRequest,
    ) -> UpdateRoomFromBackendResult:
        async_result = []
        with timeout(30):
            self._update_room_from_backend(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_room_from_backend_async(
        self,
        request: UpdateRoomFromBackendRequest,
    ) -> UpdateRoomFromBackendResult:
        async_result = []
        self._update_room_from_backend(
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

    def _delete_room(
        self,
        request: DeleteRoomRequest,
        callback: Callable[[AsyncResult[DeleteRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='deleteRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteRoomResult,
                callback=callback,
                body=body,
            )
        )

    def delete_room(
        self,
        request: DeleteRoomRequest,
    ) -> DeleteRoomResult:
        async_result = []
        with timeout(30):
            self._delete_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_room_async(
        self,
        request: DeleteRoomRequest,
    ) -> DeleteRoomResult:
        async_result = []
        self._delete_room(
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

    def _delete_room_from_backend(
        self,
        request: DeleteRoomFromBackendRequest,
        callback: Callable[[AsyncResult[DeleteRoomFromBackendResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='deleteRoomFromBackend',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteRoomFromBackendResult,
                callback=callback,
                body=body,
            )
        )

    def delete_room_from_backend(
        self,
        request: DeleteRoomFromBackendRequest,
    ) -> DeleteRoomFromBackendResult:
        async_result = []
        with timeout(30):
            self._delete_room_from_backend(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_room_from_backend_async(
        self,
        request: DeleteRoomFromBackendRequest,
    ) -> DeleteRoomFromBackendResult:
        async_result = []
        self._delete_room_from_backend(
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

    def _describe_messages(
        self,
        request: DescribeMessagesRequest,
        callback: Callable[[AsyncResult[DescribeMessagesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='describeMessages',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.password is not None:
            body["password"] = request.password
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.start_at is not None:
            body["startAt"] = request.start_at
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeMessagesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_messages(
        self,
        request: DescribeMessagesRequest,
    ) -> DescribeMessagesResult:
        async_result = []
        with timeout(30):
            self._describe_messages(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_messages_async(
        self,
        request: DescribeMessagesRequest,
    ) -> DescribeMessagesResult:
        async_result = []
        self._describe_messages(
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

    def _describe_messages_by_user_id(
        self,
        request: DescribeMessagesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeMessagesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='describeMessagesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.password is not None:
            body["password"] = request.password
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.start_at is not None:
            body["startAt"] = request.start_at
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeMessagesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_messages_by_user_id(
        self,
        request: DescribeMessagesByUserIdRequest,
    ) -> DescribeMessagesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_messages_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_messages_by_user_id_async(
        self,
        request: DescribeMessagesByUserIdRequest,
    ) -> DescribeMessagesByUserIdResult:
        async_result = []
        self._describe_messages_by_user_id(
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

    def _post(
        self,
        request: PostRequest,
        callback: Callable[[AsyncResult[PostResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='post',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.category is not None:
            body["category"] = request.category
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=PostResult,
                callback=callback,
                body=body,
            )
        )

    def post(
        self,
        request: PostRequest,
    ) -> PostResult:
        async_result = []
        with timeout(30):
            self._post(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def post_async(
        self,
        request: PostRequest,
    ) -> PostResult:
        async_result = []
        self._post(
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

    def _post_by_user_id(
        self,
        request: PostByUserIdRequest,
        callback: Callable[[AsyncResult[PostByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='postByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.category is not None:
            body["category"] = request.category
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=PostByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def post_by_user_id(
        self,
        request: PostByUserIdRequest,
    ) -> PostByUserIdResult:
        async_result = []
        with timeout(30):
            self._post_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def post_by_user_id_async(
        self,
        request: PostByUserIdRequest,
    ) -> PostByUserIdResult:
        async_result = []
        self._post_by_user_id(
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

    def _get_message(
        self,
        request: GetMessageRequest,
        callback: Callable[[AsyncResult[GetMessageResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='getMessage',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.message_name is not None:
            body["messageName"] = request.message_name
        if request.password is not None:
            body["password"] = request.password
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetMessageResult,
                callback=callback,
                body=body,
            )
        )

    def get_message(
        self,
        request: GetMessageRequest,
    ) -> GetMessageResult:
        async_result = []
        with timeout(30):
            self._get_message(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_message_async(
        self,
        request: GetMessageRequest,
    ) -> GetMessageResult:
        async_result = []
        self._get_message(
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

    def _get_message_by_user_id(
        self,
        request: GetMessageByUserIdRequest,
        callback: Callable[[AsyncResult[GetMessageByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='getMessageByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.message_name is not None:
            body["messageName"] = request.message_name
        if request.password is not None:
            body["password"] = request.password
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetMessageByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_message_by_user_id(
        self,
        request: GetMessageByUserIdRequest,
    ) -> GetMessageByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_message_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_message_by_user_id_async(
        self,
        request: GetMessageByUserIdRequest,
    ) -> GetMessageByUserIdResult:
        async_result = []
        self._get_message_by_user_id(
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

    def _delete_message(
        self,
        request: DeleteMessageRequest,
        callback: Callable[[AsyncResult[DeleteMessageResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='deleteMessage',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.message_name is not None:
            body["messageName"] = request.message_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteMessageResult,
                callback=callback,
                body=body,
            )
        )

    def delete_message(
        self,
        request: DeleteMessageRequest,
    ) -> DeleteMessageResult:
        async_result = []
        with timeout(30):
            self._delete_message(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_message_async(
        self,
        request: DeleteMessageRequest,
    ) -> DeleteMessageResult:
        async_result = []
        self._delete_message(
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

    def _describe_subscribes(
        self,
        request: DescribeSubscribesRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='describeSubscribes',
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
                result_type=DescribeSubscribesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribes(
        self,
        request: DescribeSubscribesRequest,
    ) -> DescribeSubscribesResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_async(
        self,
        request: DescribeSubscribesRequest,
    ) -> DescribeSubscribesResult:
        async_result = []
        self._describe_subscribes(
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

    def _describe_subscribes_by_user_id(
        self,
        request: DescribeSubscribesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='describeSubscribesByUserId',
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
                result_type=DescribeSubscribesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribes_by_user_id(
        self,
        request: DescribeSubscribesByUserIdRequest,
    ) -> DescribeSubscribesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_by_user_id_async(
        self,
        request: DescribeSubscribesByUserIdRequest,
    ) -> DescribeSubscribesByUserIdResult:
        async_result = []
        self._describe_subscribes_by_user_id(
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

    def _describe_subscribes_by_room_name(
        self,
        request: DescribeSubscribesByRoomNameRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesByRoomNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='describeSubscribesByRoomName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeSubscribesByRoomNameResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribes_by_room_name(
        self,
        request: DescribeSubscribesByRoomNameRequest,
    ) -> DescribeSubscribesByRoomNameResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes_by_room_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_by_room_name_async(
        self,
        request: DescribeSubscribesByRoomNameRequest,
    ) -> DescribeSubscribesByRoomNameResult:
        async_result = []
        self._describe_subscribes_by_room_name(
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

    def _subscribe(
        self,
        request: SubscribeRequest,
        callback: Callable[[AsyncResult[SubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='subscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=SubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def subscribe(
        self,
        request: SubscribeRequest,
    ) -> SubscribeResult:
        async_result = []
        with timeout(30):
            self._subscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def subscribe_async(
        self,
        request: SubscribeRequest,
    ) -> SubscribeResult:
        async_result = []
        self._subscribe(
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

    def _subscribe_by_user_id(
        self,
        request: SubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[SubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='subscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=SubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def subscribe_by_user_id(
        self,
        request: SubscribeByUserIdRequest,
    ) -> SubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._subscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def subscribe_by_user_id_async(
        self,
        request: SubscribeByUserIdRequest,
    ) -> SubscribeByUserIdResult:
        async_result = []
        self._subscribe_by_user_id(
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

    def _get_subscribe(
        self,
        request: GetSubscribeRequest,
        callback: Callable[[AsyncResult[GetSubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='getSubscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe(
        self,
        request: GetSubscribeRequest,
    ) -> GetSubscribeResult:
        async_result = []
        with timeout(30):
            self._get_subscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_async(
        self,
        request: GetSubscribeRequest,
    ) -> GetSubscribeResult:
        async_result = []
        self._get_subscribe(
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

    def _get_subscribe_by_user_id(
        self,
        request: GetSubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[GetSubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='getSubscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_by_user_id(
        self,
        request: GetSubscribeByUserIdRequest,
    ) -> GetSubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_by_user_id_async(
        self,
        request: GetSubscribeByUserIdRequest,
    ) -> GetSubscribeByUserIdResult:
        async_result = []
        self._get_subscribe_by_user_id(
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

    def _update_notification_type(
        self,
        request: UpdateNotificationTypeRequest,
        callback: Callable[[AsyncResult[UpdateNotificationTypeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='updateNotificationType',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateNotificationTypeResult,
                callback=callback,
                body=body,
            )
        )

    def update_notification_type(
        self,
        request: UpdateNotificationTypeRequest,
    ) -> UpdateNotificationTypeResult:
        async_result = []
        with timeout(30):
            self._update_notification_type(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_notification_type_async(
        self,
        request: UpdateNotificationTypeRequest,
    ) -> UpdateNotificationTypeResult:
        async_result = []
        self._update_notification_type(
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

    def _update_notification_type_by_user_id(
        self,
        request: UpdateNotificationTypeByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateNotificationTypeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='updateNotificationTypeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateNotificationTypeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def update_notification_type_by_user_id(
        self,
        request: UpdateNotificationTypeByUserIdRequest,
    ) -> UpdateNotificationTypeByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_notification_type_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_notification_type_by_user_id_async(
        self,
        request: UpdateNotificationTypeByUserIdRequest,
    ) -> UpdateNotificationTypeByUserIdResult:
        async_result = []
        self._update_notification_type_by_user_id(
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

    def _unsubscribe(
        self,
        request: UnsubscribeRequest,
        callback: Callable[[AsyncResult[UnsubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='unsubscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UnsubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def unsubscribe(
        self,
        request: UnsubscribeRequest,
    ) -> UnsubscribeResult:
        async_result = []
        with timeout(30):
            self._unsubscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def unsubscribe_async(
        self,
        request: UnsubscribeRequest,
    ) -> UnsubscribeResult:
        async_result = []
        self._unsubscribe(
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

    def _unsubscribe_by_user_id(
        self,
        request: UnsubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[UnsubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='unsubscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UnsubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def unsubscribe_by_user_id(
        self,
        request: UnsubscribeByUserIdRequest,
    ) -> UnsubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._unsubscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def unsubscribe_by_user_id_async(
        self,
        request: UnsubscribeByUserIdRequest,
    ) -> UnsubscribeByUserIdResult:
        async_result = []
        self._unsubscribe_by_user_id(
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