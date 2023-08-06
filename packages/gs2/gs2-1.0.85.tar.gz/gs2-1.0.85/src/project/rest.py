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
from project.request import *
from project.result import *


class Gs2ProjectRestClient(AbstractGs2RestClient):

    def _create_account(
        self,
        request: CreateAccountRequest,
        callback: Callable[[AsyncResult[CreateAccountResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateAccountResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/verify"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.verify_token is not None:
            body["verifyToken"] = request.verify_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/signIn"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.email is not None:
            body["email"] = request.email
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=SignInResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/accountToken"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.account_name is not None:
            body["accountName"] = request.account_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=IssueAccountTokenResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/forget"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.email is not None:
            body["email"] = request.email
        if request.lang is not None:
            body["lang"] = request.lang

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=ForgetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/password/issue"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.issue_password_token is not None:
            body["issuePasswordToken"] = request.issue_password_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=IssuePasswordResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateAccountResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteAccountResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/project"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeProjectsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/project"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateProjectResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/project/{projectName}".format(
            projectName=request.project_name if request.project_name is not None and request.project_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetProjectResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/project/{projectName}/projectToken".format(
            projectName=request.project_name if request.project_name is not None and request.project_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            body["accountToken"] = request.account_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=GetProjectTokenResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/{accountName}/project/{projectName}/user/{userName}/projectToken".format(
            accountName=request.account_name if request.account_name is not None and request.account_name != '' else 'null',
            projectName=request.project_name if request.project_name is not None and request.project_name != '' else 'null',
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=GetProjectTokenByIdentifierResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/project/{projectName}".format(
            projectName=request.project_name if request.project_name is not None and request.project_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            body["accountToken"] = request.account_token
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateProjectResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/project/{projectName}".format(
            projectName=request.project_name if request.project_name is not None and request.project_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteProjectResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/billingMethod"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeBillingMethodsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/billingMethod"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateBillingMethodResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/billingMethod/{billingMethodName}".format(
            billingMethodName=request.billing_method_name if request.billing_method_name is not None and request.billing_method_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=GetBillingMethodResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/billingMethod/{billingMethodName}".format(
            billingMethodName=request.billing_method_name if request.billing_method_name is not None and request.billing_method_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.description is not None:
            body["description"] = request.description

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateBillingMethodResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/billingMethod/{billingMethodName}".format(
            billingMethodName=request.billing_method_name if request.billing_method_name is not None and request.billing_method_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteBillingMethodResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/receipt"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeReceiptsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='project',
            region=self.session.region,
        ) + "/account/me/billing/{projectName}/{year}/{month}".format(
            projectName=request.project_name if request.project_name is not None and request.project_name != '' else 'null',
            year=request.year if request.year is not None and request.year != '' else 'null',
            month=request.month if request.month is not None and request.month != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.account_token is not None:
            query_strings["accountToken"] = request.account_token
        if request.region is not None:
            query_strings["region"] = request.region
        if request.service is not None:
            query_strings["service"] = request.service

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeBillingsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result