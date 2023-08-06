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
from account.request import *
from account.result import *


class Gs2AccountWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
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
            service="account",
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
        if request.change_password_if_take_over is not None:
            body["changePasswordIfTakeOver"] = request.change_password_if_take_over
        if request.different_user_id_for_login_and_data_retention is not None:
            body["differentUserIdForLoginAndDataRetention"] = request.different_user_id_for_login_and_data_retention
        if request.create_account_script is not None:
            body["createAccountScript"] = request.create_account_script.to_dict()
        if request.authentication_script is not None:
            body["authenticationScript"] = request.authentication_script.to_dict()
        if request.create_take_over_script is not None:
            body["createTakeOverScript"] = request.create_take_over_script.to_dict()
        if request.do_take_over_script is not None:
            body["doTakeOverScript"] = request.do_take_over_script.to_dict()
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
            service="account",
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
            service="account",
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
            service="account",
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
        if request.change_password_if_take_over is not None:
            body["changePasswordIfTakeOver"] = request.change_password_if_take_over
        if request.different_user_id_for_login_and_data_retention is not None:
            body["differentUserIdForLoginAndDataRetention"] = request.different_user_id_for_login_and_data_retention
        if request.create_account_script is not None:
            body["createAccountScript"] = request.create_account_script.to_dict()
        if request.authentication_script is not None:
            body["authenticationScript"] = request.authentication_script.to_dict()
        if request.create_take_over_script is not None:
            body["createTakeOverScript"] = request.create_take_over_script.to_dict()
        if request.do_take_over_script is not None:
            body["doTakeOverScript"] = request.do_take_over_script.to_dict()
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
            service="account",
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

    def _describe_accounts(
        self,
        request: DescribeAccountsRequest,
        callback: Callable[[AsyncResult[DescribeAccountsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='describeAccounts',
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
                result_type=DescribeAccountsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_accounts(
        self,
        request: DescribeAccountsRequest,
    ) -> DescribeAccountsResult:
        async_result = []
        with timeout(30):
            self._describe_accounts(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_accounts_async(
        self,
        request: DescribeAccountsRequest,
    ) -> DescribeAccountsResult:
        async_result = []
        self._describe_accounts(
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

    def _create_account(
        self,
        request: CreateAccountRequest,
        callback: Callable[[AsyncResult[CreateAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='createAccount',
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
                result_type=CreateAccountResult,
                callback=callback,
                body=body,
            )
        )

    def create_account(
        self,
        request: CreateAccountRequest,
    ) -> CreateAccountResult:
        async_result = []
        with timeout(30):
            self._create_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_account_async(
        self,
        request: CreateAccountRequest,
    ) -> CreateAccountResult:
        async_result = []
        self._create_account(
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

    def _update_time_offset(
        self,
        request: UpdateTimeOffsetRequest,
        callback: Callable[[AsyncResult[UpdateTimeOffsetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='updateTimeOffset',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset is not None:
            body["timeOffset"] = request.time_offset

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateTimeOffsetResult,
                callback=callback,
                body=body,
            )
        )

    def update_time_offset(
        self,
        request: UpdateTimeOffsetRequest,
    ) -> UpdateTimeOffsetResult:
        async_result = []
        with timeout(30):
            self._update_time_offset(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_time_offset_async(
        self,
        request: UpdateTimeOffsetRequest,
    ) -> UpdateTimeOffsetResult:
        async_result = []
        self._update_time_offset(
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

    def _update_banned(
        self,
        request: UpdateBannedRequest,
        callback: Callable[[AsyncResult[UpdateBannedResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='updateBanned',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.banned is not None:
            body["banned"] = request.banned

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateBannedResult,
                callback=callback,
                body=body,
            )
        )

    def update_banned(
        self,
        request: UpdateBannedRequest,
    ) -> UpdateBannedResult:
        async_result = []
        with timeout(30):
            self._update_banned(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_banned_async(
        self,
        request: UpdateBannedRequest,
    ) -> UpdateBannedResult:
        async_result = []
        self._update_banned(
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

    def _get_account(
        self,
        request: GetAccountRequest,
        callback: Callable[[AsyncResult[GetAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='getAccount',
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
                result_type=GetAccountResult,
                callback=callback,
                body=body,
            )
        )

    def get_account(
        self,
        request: GetAccountRequest,
    ) -> GetAccountResult:
        async_result = []
        with timeout(30):
            self._get_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_account_async(
        self,
        request: GetAccountRequest,
    ) -> GetAccountResult:
        async_result = []
        self._get_account(
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

    def _delete_account(
        self,
        request: DeleteAccountRequest,
        callback: Callable[[AsyncResult[DeleteAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='deleteAccount',
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
                result_type=DeleteAccountResult,
                callback=callback,
                body=body,
            )
        )

    def delete_account(
        self,
        request: DeleteAccountRequest,
    ) -> DeleteAccountResult:
        async_result = []
        with timeout(30):
            self._delete_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_account_async(
        self,
        request: DeleteAccountRequest,
    ) -> DeleteAccountResult:
        async_result = []
        self._delete_account(
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

    def _authentication(
        self,
        request: AuthenticationRequest,
        callback: Callable[[AsyncResult[AuthenticationResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='authentication',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AuthenticationResult,
                callback=callback,
                body=body,
            )
        )

    def authentication(
        self,
        request: AuthenticationRequest,
    ) -> AuthenticationResult:
        async_result = []
        with timeout(30):
            self._authentication(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def authentication_async(
        self,
        request: AuthenticationRequest,
    ) -> AuthenticationResult:
        async_result = []
        self._authentication(
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

    def _describe_take_overs(
        self,
        request: DescribeTakeOversRequest,
        callback: Callable[[AsyncResult[DescribeTakeOversResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='describeTakeOvers',
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
                result_type=DescribeTakeOversResult,
                callback=callback,
                body=body,
            )
        )

    def describe_take_overs(
        self,
        request: DescribeTakeOversRequest,
    ) -> DescribeTakeOversResult:
        async_result = []
        with timeout(30):
            self._describe_take_overs(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_take_overs_async(
        self,
        request: DescribeTakeOversRequest,
    ) -> DescribeTakeOversResult:
        async_result = []
        self._describe_take_overs(
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

    def _describe_take_overs_by_user_id(
        self,
        request: DescribeTakeOversByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeTakeOversByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='describeTakeOversByUserId',
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
                result_type=DescribeTakeOversByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_take_overs_by_user_id(
        self,
        request: DescribeTakeOversByUserIdRequest,
    ) -> DescribeTakeOversByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_take_overs_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_take_overs_by_user_id_async(
        self,
        request: DescribeTakeOversByUserIdRequest,
    ) -> DescribeTakeOversByUserIdResult:
        async_result = []
        self._describe_take_overs_by_user_id(
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

    def _create_take_over(
        self,
        request: CreateTakeOverRequest,
        callback: Callable[[AsyncResult[CreateTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='createTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def create_take_over(
        self,
        request: CreateTakeOverRequest,
    ) -> CreateTakeOverResult:
        async_result = []
        with timeout(30):
            self._create_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_take_over_async(
        self,
        request: CreateTakeOverRequest,
    ) -> CreateTakeOverResult:
        async_result = []
        self._create_take_over(
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

    def _create_take_over_by_user_id(
        self,
        request: CreateTakeOverByUserIdRequest,
        callback: Callable[[AsyncResult[CreateTakeOverByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='createTakeOverByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateTakeOverByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_take_over_by_user_id(
        self,
        request: CreateTakeOverByUserIdRequest,
    ) -> CreateTakeOverByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_take_over_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_take_over_by_user_id_async(
        self,
        request: CreateTakeOverByUserIdRequest,
    ) -> CreateTakeOverByUserIdResult:
        async_result = []
        self._create_take_over_by_user_id(
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

    def _get_take_over(
        self,
        request: GetTakeOverRequest,
        callback: Callable[[AsyncResult[GetTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='getTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def get_take_over(
        self,
        request: GetTakeOverRequest,
    ) -> GetTakeOverResult:
        async_result = []
        with timeout(30):
            self._get_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_take_over_async(
        self,
        request: GetTakeOverRequest,
    ) -> GetTakeOverResult:
        async_result = []
        self._get_take_over(
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

    def _get_take_over_by_user_id(
        self,
        request: GetTakeOverByUserIdRequest,
        callback: Callable[[AsyncResult[GetTakeOverByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='getTakeOverByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetTakeOverByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_take_over_by_user_id(
        self,
        request: GetTakeOverByUserIdRequest,
    ) -> GetTakeOverByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_take_over_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_take_over_by_user_id_async(
        self,
        request: GetTakeOverByUserIdRequest,
    ) -> GetTakeOverByUserIdResult:
        async_result = []
        self._get_take_over_by_user_id(
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

    def _update_take_over(
        self,
        request: UpdateTakeOverRequest,
        callback: Callable[[AsyncResult[UpdateTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='updateTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.old_password is not None:
            body["oldPassword"] = request.old_password
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def update_take_over(
        self,
        request: UpdateTakeOverRequest,
    ) -> UpdateTakeOverResult:
        async_result = []
        with timeout(30):
            self._update_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_take_over_async(
        self,
        request: UpdateTakeOverRequest,
    ) -> UpdateTakeOverResult:
        async_result = []
        self._update_take_over(
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

    def _update_take_over_by_user_id(
        self,
        request: UpdateTakeOverByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateTakeOverByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='updateTakeOverByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.old_password is not None:
            body["oldPassword"] = request.old_password
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateTakeOverByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def update_take_over_by_user_id(
        self,
        request: UpdateTakeOverByUserIdRequest,
    ) -> UpdateTakeOverByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_take_over_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_take_over_by_user_id_async(
        self,
        request: UpdateTakeOverByUserIdRequest,
    ) -> UpdateTakeOverByUserIdResult:
        async_result = []
        self._update_take_over_by_user_id(
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

    def _delete_take_over(
        self,
        request: DeleteTakeOverRequest,
        callback: Callable[[AsyncResult[DeleteTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='deleteTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def delete_take_over(
        self,
        request: DeleteTakeOverRequest,
    ) -> DeleteTakeOverResult:
        async_result = []
        with timeout(30):
            self._delete_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_take_over_async(
        self,
        request: DeleteTakeOverRequest,
    ) -> DeleteTakeOverResult:
        async_result = []
        self._delete_take_over(
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

    def _delete_take_over_by_user_identifier(
        self,
        request: DeleteTakeOverByUserIdentifierRequest,
        callback: Callable[[AsyncResult[DeleteTakeOverByUserIdentifierResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='deleteTakeOverByUserIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteTakeOverByUserIdentifierResult,
                callback=callback,
                body=body,
            )
        )

    def delete_take_over_by_user_identifier(
        self,
        request: DeleteTakeOverByUserIdentifierRequest,
    ) -> DeleteTakeOverByUserIdentifierResult:
        async_result = []
        with timeout(30):
            self._delete_take_over_by_user_identifier(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_take_over_by_user_identifier_async(
        self,
        request: DeleteTakeOverByUserIdentifierRequest,
    ) -> DeleteTakeOverByUserIdentifierResult:
        async_result = []
        self._delete_take_over_by_user_identifier(
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

    def _do_take_over(
        self,
        request: DoTakeOverRequest,
        callback: Callable[[AsyncResult[DoTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='doTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DoTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def do_take_over(
        self,
        request: DoTakeOverRequest,
    ) -> DoTakeOverResult:
        async_result = []
        with timeout(30):
            self._do_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def do_take_over_async(
        self,
        request: DoTakeOverRequest,
    ) -> DoTakeOverResult:
        async_result = []
        self._do_take_over(
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

    def _get_data_owner_by_user_id(
        self,
        request: GetDataOwnerByUserIdRequest,
        callback: Callable[[AsyncResult[GetDataOwnerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='dataOwner',
            function='getDataOwnerByUserId',
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
                result_type=GetDataOwnerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_data_owner_by_user_id(
        self,
        request: GetDataOwnerByUserIdRequest,
    ) -> GetDataOwnerByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_data_owner_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_data_owner_by_user_id_async(
        self,
        request: GetDataOwnerByUserIdRequest,
    ) -> GetDataOwnerByUserIdResult:
        async_result = []
        self._get_data_owner_by_user_id(
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

    def _delete_data_owner_by_user_id(
        self,
        request: DeleteDataOwnerByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteDataOwnerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='dataOwner',
            function='deleteDataOwnerByUserId',
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
                result_type=DeleteDataOwnerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_data_owner_by_user_id(
        self,
        request: DeleteDataOwnerByUserIdRequest,
    ) -> DeleteDataOwnerByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_data_owner_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_data_owner_by_user_id_async(
        self,
        request: DeleteDataOwnerByUserIdRequest,
    ) -> DeleteDataOwnerByUserIdResult:
        async_result = []
        self._delete_data_owner_by_user_id(
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