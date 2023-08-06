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
from project.request import *
from project.result import *


class Gs2ProjectWebSocketClient(AbstractGs2WebSocketClient):

    def _create_account(
        self,
        request: CreateAccountRequest,
        callback: Callable[[AsyncResult[CreateAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='createAccount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.full_name is not None:
            body["fullName"] = request.full_name
        if request.company_name is not None:
            body["companyName"] = request.company_name
        if request.password is not None:
            body["password"] = request.password
        if request.lang is not None:
            body["lang"] = request.lang

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

    def _verify(
        self,
        request: VerifyRequest,
        callback: Callable[[AsyncResult[VerifyResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='verify',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.verify_token is not None:
            body["verifyToken"] = request.verify_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=VerifyResult,
                callback=callback,
                body=body,
            )
        )

    def verify(
        self,
        request: VerifyRequest,
    ) -> VerifyResult:
        async_result = []
        with timeout(30):
            self._verify(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_async(
        self,
        request: VerifyRequest,
    ) -> VerifyResult:
        async_result = []
        self._verify(
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

    def _sign_in(
        self,
        request: SignInRequest,
        callback: Callable[[AsyncResult[SignInResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='signIn',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=SignInResult,
                callback=callback,
                body=body,
            )
        )

    def sign_in(
        self,
        request: SignInRequest,
    ) -> SignInResult:
        async_result = []
        with timeout(30):
            self._sign_in(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sign_in_async(
        self,
        request: SignInRequest,
    ) -> SignInResult:
        async_result = []
        self._sign_in(
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

    def _issue_account_token(
        self,
        request: IssueAccountTokenRequest,
        callback: Callable[[AsyncResult[IssueAccountTokenResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='issueAccountToken',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_name is not None:
            body["accountName"] = request.account_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=IssueAccountTokenResult,
                callback=callback,
                body=body,
            )
        )

    def issue_account_token(
        self,
        request: IssueAccountTokenRequest,
    ) -> IssueAccountTokenResult:
        async_result = []
        with timeout(30):
            self._issue_account_token(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def issue_account_token_async(
        self,
        request: IssueAccountTokenRequest,
    ) -> IssueAccountTokenResult:
        async_result = []
        self._issue_account_token(
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

    def _forget(
        self,
        request: ForgetRequest,
        callback: Callable[[AsyncResult[ForgetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='forget',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.lang is not None:
            body["lang"] = request.lang

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=ForgetResult,
                callback=callback,
                body=body,
            )
        )

    def forget(
        self,
        request: ForgetRequest,
    ) -> ForgetResult:
        async_result = []
        with timeout(30):
            self._forget(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def forget_async(
        self,
        request: ForgetRequest,
    ) -> ForgetResult:
        async_result = []
        self._forget(
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

    def _issue_password(
        self,
        request: IssuePasswordRequest,
        callback: Callable[[AsyncResult[IssuePasswordResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='issuePassword',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.issue_password_token is not None:
            body["issuePasswordToken"] = request.issue_password_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=IssuePasswordResult,
                callback=callback,
                body=body,
            )
        )

    def issue_password(
        self,
        request: IssuePasswordRequest,
    ) -> IssuePasswordResult:
        async_result = []
        with timeout(30):
            self._issue_password(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def issue_password_async(
        self,
        request: IssuePasswordRequest,
    ) -> IssuePasswordResult:
        async_result = []
        self._issue_password(
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

    def _update_account(
        self,
        request: UpdateAccountRequest,
        callback: Callable[[AsyncResult[UpdateAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='updateAccount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.full_name is not None:
            body["fullName"] = request.full_name
        if request.company_name is not None:
            body["companyName"] = request.company_name
        if request.password is not None:
            body["password"] = request.password
        if request.account_token is not None:
            body["accountToken"] = request.account_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateAccountResult,
                callback=callback,
                body=body,
            )
        )

    def update_account(
        self,
        request: UpdateAccountRequest,
    ) -> UpdateAccountResult:
        async_result = []
        with timeout(30):
            self._update_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_account_async(
        self,
        request: UpdateAccountRequest,
    ) -> UpdateAccountResult:
        async_result = []
        self._update_account(
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
            service="project",
            component='account',
            function='deleteAccount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token

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

    def _describe_projects(
        self,
        request: DescribeProjectsRequest,
        callback: Callable[[AsyncResult[DescribeProjectsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='describeProjects',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeProjectsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_projects(
        self,
        request: DescribeProjectsRequest,
    ) -> DescribeProjectsResult:
        async_result = []
        with timeout(30):
            self._describe_projects(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_projects_async(
        self,
        request: DescribeProjectsRequest,
    ) -> DescribeProjectsResult:
        async_result = []
        self._describe_projects(
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

    def _create_project(
        self,
        request: CreateProjectRequest,
        callback: Callable[[AsyncResult[CreateProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='createProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.plan is not None:
            body["plan"] = request.plan
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name
        if request.enable_event_bridge is not None:
            body["enableEventBridge"] = request.enable_event_bridge
        if request.event_bridge_aws_account_id is not None:
            body["eventBridgeAwsAccountId"] = request.event_bridge_aws_account_id
        if request.event_bridge_aws_region is not None:
            body["eventBridgeAwsRegion"] = request.event_bridge_aws_region

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateProjectResult,
                callback=callback,
                body=body,
            )
        )

    def create_project(
        self,
        request: CreateProjectRequest,
    ) -> CreateProjectResult:
        async_result = []
        with timeout(30):
            self._create_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_project_async(
        self,
        request: CreateProjectRequest,
    ) -> CreateProjectResult:
        async_result = []
        self._create_project(
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

    def _get_project(
        self,
        request: GetProjectRequest,
        callback: Callable[[AsyncResult[GetProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='getProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetProjectResult,
                callback=callback,
                body=body,
            )
        )

    def get_project(
        self,
        request: GetProjectRequest,
    ) -> GetProjectResult:
        async_result = []
        with timeout(30):
            self._get_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_project_async(
        self,
        request: GetProjectRequest,
    ) -> GetProjectResult:
        async_result = []
        self._get_project(
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

    def _get_project_token(
        self,
        request: GetProjectTokenRequest,
        callback: Callable[[AsyncResult[GetProjectTokenResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='getProjectToken',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.account_token is not None:
            body["accountToken"] = request.account_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetProjectTokenResult,
                callback=callback,
                body=body,
            )
        )

    def get_project_token(
        self,
        request: GetProjectTokenRequest,
    ) -> GetProjectTokenResult:
        async_result = []
        with timeout(30):
            self._get_project_token(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_project_token_async(
        self,
        request: GetProjectTokenRequest,
    ) -> GetProjectTokenResult:
        async_result = []
        self._get_project_token(
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

    def _get_project_token_by_identifier(
        self,
        request: GetProjectTokenByIdentifierRequest,
        callback: Callable[[AsyncResult[GetProjectTokenByIdentifierResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='getProjectTokenByIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_name is not None:
            body["accountName"] = request.account_name
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetProjectTokenByIdentifierResult,
                callback=callback,
                body=body,
            )
        )

    def get_project_token_by_identifier(
        self,
        request: GetProjectTokenByIdentifierRequest,
    ) -> GetProjectTokenByIdentifierResult:
        async_result = []
        with timeout(30):
            self._get_project_token_by_identifier(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_project_token_by_identifier_async(
        self,
        request: GetProjectTokenByIdentifierRequest,
    ) -> GetProjectTokenByIdentifierResult:
        async_result = []
        self._get_project_token_by_identifier(
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

    def _update_project(
        self,
        request: UpdateProjectRequest,
        callback: Callable[[AsyncResult[UpdateProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='updateProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.description is not None:
            body["description"] = request.description
        if request.plan is not None:
            body["plan"] = request.plan
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name
        if request.enable_event_bridge is not None:
            body["enableEventBridge"] = request.enable_event_bridge
        if request.event_bridge_aws_account_id is not None:
            body["eventBridgeAwsAccountId"] = request.event_bridge_aws_account_id
        if request.event_bridge_aws_region is not None:
            body["eventBridgeAwsRegion"] = request.event_bridge_aws_region

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateProjectResult,
                callback=callback,
                body=body,
            )
        )

    def update_project(
        self,
        request: UpdateProjectRequest,
    ) -> UpdateProjectResult:
        async_result = []
        with timeout(30):
            self._update_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_project_async(
        self,
        request: UpdateProjectRequest,
    ) -> UpdateProjectResult:
        async_result = []
        self._update_project(
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

    def _delete_project(
        self,
        request: DeleteProjectRequest,
        callback: Callable[[AsyncResult[DeleteProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='deleteProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteProjectResult,
                callback=callback,
                body=body,
            )
        )

    def delete_project(
        self,
        request: DeleteProjectRequest,
    ) -> DeleteProjectResult:
        async_result = []
        with timeout(30):
            self._delete_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_project_async(
        self,
        request: DeleteProjectRequest,
    ) -> DeleteProjectResult:
        async_result = []
        self._delete_project(
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

    def _describe_billing_methods(
        self,
        request: DescribeBillingMethodsRequest,
        callback: Callable[[AsyncResult[DescribeBillingMethodsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='describeBillingMethods',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeBillingMethodsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_billing_methods(
        self,
        request: DescribeBillingMethodsRequest,
    ) -> DescribeBillingMethodsResult:
        async_result = []
        with timeout(30):
            self._describe_billing_methods(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_billing_methods_async(
        self,
        request: DescribeBillingMethodsRequest,
    ) -> DescribeBillingMethodsResult:
        async_result = []
        self._describe_billing_methods(
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

    def _create_billing_method(
        self,
        request: CreateBillingMethodRequest,
        callback: Callable[[AsyncResult[CreateBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='createBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.description is not None:
            body["description"] = request.description
        if request.method_type is not None:
            body["methodType"] = request.method_type
        if request.card_customer_id is not None:
            body["cardCustomerId"] = request.card_customer_id
        if request.partner_id is not None:
            body["partnerId"] = request.partner_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def create_billing_method(
        self,
        request: CreateBillingMethodRequest,
    ) -> CreateBillingMethodResult:
        async_result = []
        with timeout(30):
            self._create_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_billing_method_async(
        self,
        request: CreateBillingMethodRequest,
    ) -> CreateBillingMethodResult:
        async_result = []
        self._create_billing_method(
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

    def _get_billing_method(
        self,
        request: GetBillingMethodRequest,
        callback: Callable[[AsyncResult[GetBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='getBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def get_billing_method(
        self,
        request: GetBillingMethodRequest,
    ) -> GetBillingMethodResult:
        async_result = []
        with timeout(30):
            self._get_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_billing_method_async(
        self,
        request: GetBillingMethodRequest,
    ) -> GetBillingMethodResult:
        async_result = []
        self._get_billing_method(
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

    def _update_billing_method(
        self,
        request: UpdateBillingMethodRequest,
        callback: Callable[[AsyncResult[UpdateBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='updateBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name
        if request.description is not None:
            body["description"] = request.description

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def update_billing_method(
        self,
        request: UpdateBillingMethodRequest,
    ) -> UpdateBillingMethodResult:
        async_result = []
        with timeout(30):
            self._update_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_billing_method_async(
        self,
        request: UpdateBillingMethodRequest,
    ) -> UpdateBillingMethodResult:
        async_result = []
        self._update_billing_method(
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

    def _delete_billing_method(
        self,
        request: DeleteBillingMethodRequest,
        callback: Callable[[AsyncResult[DeleteBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='deleteBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def delete_billing_method(
        self,
        request: DeleteBillingMethodRequest,
    ) -> DeleteBillingMethodResult:
        async_result = []
        with timeout(30):
            self._delete_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_billing_method_async(
        self,
        request: DeleteBillingMethodRequest,
    ) -> DeleteBillingMethodResult:
        async_result = []
        self._delete_billing_method(
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

    def _describe_receipts(
        self,
        request: DescribeReceiptsRequest,
        callback: Callable[[AsyncResult[DescribeReceiptsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='receipt',
            function='describeReceipts',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeReceiptsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_receipts(
        self,
        request: DescribeReceiptsRequest,
    ) -> DescribeReceiptsResult:
        async_result = []
        with timeout(30):
            self._describe_receipts(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_receipts_async(
        self,
        request: DescribeReceiptsRequest,
    ) -> DescribeReceiptsResult:
        async_result = []
        self._describe_receipts(
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

    def _describe_billings(
        self,
        request: DescribeBillingsRequest,
        callback: Callable[[AsyncResult[DescribeBillingsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billing',
            function='describeBillings',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.region is not None:
            body["region"] = request.region
        if request.service is not None:
            body["service"] = request.service

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeBillingsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_billings(
        self,
        request: DescribeBillingsRequest,
    ) -> DescribeBillingsResult:
        async_result = []
        with timeout(30):
            self._describe_billings(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_billings_async(
        self,
        request: DescribeBillingsRequest,
    ) -> DescribeBillingsResult:
        async_result = []
        self._describe_billings(
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