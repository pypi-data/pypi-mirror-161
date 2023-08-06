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
from log.request import *
from log.result import *


class Gs2LogWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
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
            service="log",
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
        if request.type is not None:
            body["type"] = request.type
        if request.gcp_credential_json is not None:
            body["gcpCredentialJson"] = request.gcp_credential_json
        if request.big_query_dataset_name is not None:
            body["bigQueryDatasetName"] = request.big_query_dataset_name
        if request.log_expire_days is not None:
            body["logExpireDays"] = request.log_expire_days
        if request.aws_region is not None:
            body["awsRegion"] = request.aws_region
        if request.aws_access_key_id is not None:
            body["awsAccessKeyId"] = request.aws_access_key_id
        if request.aws_secret_access_key is not None:
            body["awsSecretAccessKey"] = request.aws_secret_access_key
        if request.firehose_stream_name is not None:
            body["firehoseStreamName"] = request.firehose_stream_name

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
            service="log",
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
            service="log",
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
            service="log",
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
        if request.type is not None:
            body["type"] = request.type
        if request.gcp_credential_json is not None:
            body["gcpCredentialJson"] = request.gcp_credential_json
        if request.big_query_dataset_name is not None:
            body["bigQueryDatasetName"] = request.big_query_dataset_name
        if request.log_expire_days is not None:
            body["logExpireDays"] = request.log_expire_days
        if request.aws_region is not None:
            body["awsRegion"] = request.aws_region
        if request.aws_access_key_id is not None:
            body["awsAccessKeyId"] = request.aws_access_key_id
        if request.aws_secret_access_key is not None:
            body["awsSecretAccessKey"] = request.aws_secret_access_key
        if request.firehose_stream_name is not None:
            body["firehoseStreamName"] = request.firehose_stream_name

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
            service="log",
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

    def _query_access_log(
        self,
        request: QueryAccessLogRequest,
        callback: Callable[[AsyncResult[QueryAccessLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='accessLog',
            function='queryAccessLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=QueryAccessLogResult,
                callback=callback,
                body=body,
            )
        )

    def query_access_log(
        self,
        request: QueryAccessLogRequest,
    ) -> QueryAccessLogResult:
        async_result = []
        with timeout(30):
            self._query_access_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_access_log_async(
        self,
        request: QueryAccessLogRequest,
    ) -> QueryAccessLogResult:
        async_result = []
        self._query_access_log(
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

    def _count_access_log(
        self,
        request: CountAccessLogRequest,
        callback: Callable[[AsyncResult[CountAccessLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='accessLog',
            function='countAccessLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CountAccessLogResult,
                callback=callback,
                body=body,
            )
        )

    def count_access_log(
        self,
        request: CountAccessLogRequest,
    ) -> CountAccessLogResult:
        async_result = []
        with timeout(30):
            self._count_access_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_access_log_async(
        self,
        request: CountAccessLogRequest,
    ) -> CountAccessLogResult:
        async_result = []
        self._count_access_log(
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

    def _query_issue_stamp_sheet_log(
        self,
        request: QueryIssueStampSheetLogRequest,
        callback: Callable[[AsyncResult[QueryIssueStampSheetLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='issueStampSheetLog',
            function='queryIssueStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=QueryIssueStampSheetLogResult,
                callback=callback,
                body=body,
            )
        )

    def query_issue_stamp_sheet_log(
        self,
        request: QueryIssueStampSheetLogRequest,
    ) -> QueryIssueStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._query_issue_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_issue_stamp_sheet_log_async(
        self,
        request: QueryIssueStampSheetLogRequest,
    ) -> QueryIssueStampSheetLogResult:
        async_result = []
        self._query_issue_stamp_sheet_log(
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

    def _count_issue_stamp_sheet_log(
        self,
        request: CountIssueStampSheetLogRequest,
        callback: Callable[[AsyncResult[CountIssueStampSheetLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='issueStampSheetLog',
            function='countIssueStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CountIssueStampSheetLogResult,
                callback=callback,
                body=body,
            )
        )

    def count_issue_stamp_sheet_log(
        self,
        request: CountIssueStampSheetLogRequest,
    ) -> CountIssueStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._count_issue_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_issue_stamp_sheet_log_async(
        self,
        request: CountIssueStampSheetLogRequest,
    ) -> CountIssueStampSheetLogResult:
        async_result = []
        self._count_issue_stamp_sheet_log(
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

    def _query_execute_stamp_sheet_log(
        self,
        request: QueryExecuteStampSheetLogRequest,
        callback: Callable[[AsyncResult[QueryExecuteStampSheetLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampSheetLog',
            function='queryExecuteStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=QueryExecuteStampSheetLogResult,
                callback=callback,
                body=body,
            )
        )

    def query_execute_stamp_sheet_log(
        self,
        request: QueryExecuteStampSheetLogRequest,
    ) -> QueryExecuteStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._query_execute_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_execute_stamp_sheet_log_async(
        self,
        request: QueryExecuteStampSheetLogRequest,
    ) -> QueryExecuteStampSheetLogResult:
        async_result = []
        self._query_execute_stamp_sheet_log(
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

    def _count_execute_stamp_sheet_log(
        self,
        request: CountExecuteStampSheetLogRequest,
        callback: Callable[[AsyncResult[CountExecuteStampSheetLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampSheetLog',
            function='countExecuteStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CountExecuteStampSheetLogResult,
                callback=callback,
                body=body,
            )
        )

    def count_execute_stamp_sheet_log(
        self,
        request: CountExecuteStampSheetLogRequest,
    ) -> CountExecuteStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._count_execute_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_execute_stamp_sheet_log_async(
        self,
        request: CountExecuteStampSheetLogRequest,
    ) -> CountExecuteStampSheetLogResult:
        async_result = []
        self._count_execute_stamp_sheet_log(
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

    def _query_execute_stamp_task_log(
        self,
        request: QueryExecuteStampTaskLogRequest,
        callback: Callable[[AsyncResult[QueryExecuteStampTaskLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampTaskLog',
            function='queryExecuteStampTaskLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=QueryExecuteStampTaskLogResult,
                callback=callback,
                body=body,
            )
        )

    def query_execute_stamp_task_log(
        self,
        request: QueryExecuteStampTaskLogRequest,
    ) -> QueryExecuteStampTaskLogResult:
        async_result = []
        with timeout(30):
            self._query_execute_stamp_task_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_execute_stamp_task_log_async(
        self,
        request: QueryExecuteStampTaskLogRequest,
    ) -> QueryExecuteStampTaskLogResult:
        async_result = []
        self._query_execute_stamp_task_log(
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

    def _count_execute_stamp_task_log(
        self,
        request: CountExecuteStampTaskLogRequest,
        callback: Callable[[AsyncResult[CountExecuteStampTaskLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampTaskLog',
            function='countExecuteStampTaskLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CountExecuteStampTaskLogResult,
                callback=callback,
                body=body,
            )
        )

    def count_execute_stamp_task_log(
        self,
        request: CountExecuteStampTaskLogRequest,
    ) -> CountExecuteStampTaskLogResult:
        async_result = []
        with timeout(30):
            self._count_execute_stamp_task_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_execute_stamp_task_log_async(
        self,
        request: CountExecuteStampTaskLogRequest,
    ) -> CountExecuteStampTaskLogResult:
        async_result = []
        self._count_execute_stamp_task_log(
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

    def _put_log(
        self,
        request: PutLogRequest,
        callback: Callable[[AsyncResult[PutLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='log',
            function='putLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.logging_namespace_id is not None:
            body["loggingNamespaceId"] = request.logging_namespace_id
        if request.log_category is not None:
            body["logCategory"] = request.log_category
        if request.payload is not None:
            body["payload"] = request.payload

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=PutLogResult,
                callback=callback,
                body=body,
            )
        )

    def put_log(
        self,
        request: PutLogRequest,
    ) -> PutLogResult:
        async_result = []
        with timeout(30):
            self._put_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_log_async(
        self,
        request: PutLogRequest,
    ) -> PutLogResult:
        async_result = []
        self._put_log(
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