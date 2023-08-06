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
from auth.request import *
from auth.result import *


class Gs2AuthWebSocketClient(AbstractGs2WebSocketClient):

    def _login(
        self,
        request: LoginRequest,
        callback: Callable[[AsyncResult[LoginResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="auth",
            component='accessToken',
            function='login',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset is not None:
            body["timeOffset"] = request.time_offset

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=LoginResult,
                callback=callback,
                body=body,
            )
        )

    def login(
        self,
        request: LoginRequest,
    ) -> LoginResult:
        async_result = []
        with timeout(30):
            self._login(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def login_async(
        self,
        request: LoginRequest,
    ) -> LoginResult:
        async_result = []
        self._login(
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

    def _login_by_signature(
        self,
        request: LoginBySignatureRequest,
        callback: Callable[[AsyncResult[LoginBySignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="auth",
            component='accessToken',
            function='loginBySignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.body is not None:
            body["body"] = request.body
        if request.signature is not None:
            body["signature"] = request.signature

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=LoginBySignatureResult,
                callback=callback,
                body=body,
            )
        )

    def login_by_signature(
        self,
        request: LoginBySignatureRequest,
    ) -> LoginBySignatureResult:
        async_result = []
        with timeout(30):
            self._login_by_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def login_by_signature_async(
        self,
        request: LoginBySignatureRequest,
    ) -> LoginBySignatureResult:
        async_result = []
        self._login_by_signature(
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