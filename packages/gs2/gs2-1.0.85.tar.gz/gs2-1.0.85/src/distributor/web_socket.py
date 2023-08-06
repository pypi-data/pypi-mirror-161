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
from distributor.request import *
from distributor.result import *


class Gs2DistributorWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
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
            service="distributor",
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
        if request.assume_user_id is not None:
            body["assumeUserId"] = request.assume_user_id
        if request.auto_run_stamp_sheet_notification is not None:
            body["autoRunStampSheetNotification"] = request.auto_run_stamp_sheet_notification.to_dict()
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
            service="distributor",
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
            service="distributor",
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
            service="distributor",
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
        if request.assume_user_id is not None:
            body["assumeUserId"] = request.assume_user_id
        if request.auto_run_stamp_sheet_notification is not None:
            body["autoRunStampSheetNotification"] = request.auto_run_stamp_sheet_notification.to_dict()
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
            service="distributor",
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

    def _describe_distributor_model_masters(
        self,
        request: DescribeDistributorModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeDistributorModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distributorModelMaster',
            function='describeDistributorModelMasters',
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
                result_type=DescribeDistributorModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_distributor_model_masters(
        self,
        request: DescribeDistributorModelMastersRequest,
    ) -> DescribeDistributorModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_distributor_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_distributor_model_masters_async(
        self,
        request: DescribeDistributorModelMastersRequest,
    ) -> DescribeDistributorModelMastersResult:
        async_result = []
        self._describe_distributor_model_masters(
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

    def _create_distributor_model_master(
        self,
        request: CreateDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[CreateDistributorModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distributorModelMaster',
            function='createDistributorModelMaster',
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
        if request.inbox_namespace_id is not None:
            body["inboxNamespaceId"] = request.inbox_namespace_id
        if request.white_list_target_ids is not None:
            body["whiteListTargetIds"] = [
                item
                for item in request.white_list_target_ids
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateDistributorModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_distributor_model_master(
        self,
        request: CreateDistributorModelMasterRequest,
    ) -> CreateDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_distributor_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_distributor_model_master_async(
        self,
        request: CreateDistributorModelMasterRequest,
    ) -> CreateDistributorModelMasterResult:
        async_result = []
        self._create_distributor_model_master(
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

    def _get_distributor_model_master(
        self,
        request: GetDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[GetDistributorModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distributorModelMaster',
            function='getDistributorModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.distributor_name is not None:
            body["distributorName"] = request.distributor_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetDistributorModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_distributor_model_master(
        self,
        request: GetDistributorModelMasterRequest,
    ) -> GetDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_distributor_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_distributor_model_master_async(
        self,
        request: GetDistributorModelMasterRequest,
    ) -> GetDistributorModelMasterResult:
        async_result = []
        self._get_distributor_model_master(
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

    def _update_distributor_model_master(
        self,
        request: UpdateDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateDistributorModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distributorModelMaster',
            function='updateDistributorModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.distributor_name is not None:
            body["distributorName"] = request.distributor_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.inbox_namespace_id is not None:
            body["inboxNamespaceId"] = request.inbox_namespace_id
        if request.white_list_target_ids is not None:
            body["whiteListTargetIds"] = [
                item
                for item in request.white_list_target_ids
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateDistributorModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_distributor_model_master(
        self,
        request: UpdateDistributorModelMasterRequest,
    ) -> UpdateDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_distributor_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_distributor_model_master_async(
        self,
        request: UpdateDistributorModelMasterRequest,
    ) -> UpdateDistributorModelMasterResult:
        async_result = []
        self._update_distributor_model_master(
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

    def _delete_distributor_model_master(
        self,
        request: DeleteDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteDistributorModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distributorModelMaster',
            function='deleteDistributorModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.distributor_name is not None:
            body["distributorName"] = request.distributor_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteDistributorModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_distributor_model_master(
        self,
        request: DeleteDistributorModelMasterRequest,
    ) -> DeleteDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_distributor_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_distributor_model_master_async(
        self,
        request: DeleteDistributorModelMasterRequest,
    ) -> DeleteDistributorModelMasterResult:
        async_result = []
        self._delete_distributor_model_master(
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

    def _describe_distributor_models(
        self,
        request: DescribeDistributorModelsRequest,
        callback: Callable[[AsyncResult[DescribeDistributorModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distributorModel',
            function='describeDistributorModels',
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
                result_type=DescribeDistributorModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_distributor_models(
        self,
        request: DescribeDistributorModelsRequest,
    ) -> DescribeDistributorModelsResult:
        async_result = []
        with timeout(30):
            self._describe_distributor_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_distributor_models_async(
        self,
        request: DescribeDistributorModelsRequest,
    ) -> DescribeDistributorModelsResult:
        async_result = []
        self._describe_distributor_models(
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

    def _get_distributor_model(
        self,
        request: GetDistributorModelRequest,
        callback: Callable[[AsyncResult[GetDistributorModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distributorModel',
            function='getDistributorModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.distributor_name is not None:
            body["distributorName"] = request.distributor_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetDistributorModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_distributor_model(
        self,
        request: GetDistributorModelRequest,
    ) -> GetDistributorModelResult:
        async_result = []
        with timeout(30):
            self._get_distributor_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_distributor_model_async(
        self,
        request: GetDistributorModelRequest,
    ) -> GetDistributorModelResult:
        async_result = []
        self._get_distributor_model(
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
            service="distributor",
            component='currentDistributorMaster',
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

    def _get_current_distributor_master(
        self,
        request: GetCurrentDistributorMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentDistributorMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='currentDistributorMaster',
            function='getCurrentDistributorMaster',
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
                result_type=GetCurrentDistributorMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_distributor_master(
        self,
        request: GetCurrentDistributorMasterRequest,
    ) -> GetCurrentDistributorMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_distributor_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_distributor_master_async(
        self,
        request: GetCurrentDistributorMasterRequest,
    ) -> GetCurrentDistributorMasterResult:
        async_result = []
        self._get_current_distributor_master(
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

    def _update_current_distributor_master(
        self,
        request: UpdateCurrentDistributorMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentDistributorMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='currentDistributorMaster',
            function='updateCurrentDistributorMaster',
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
                result_type=UpdateCurrentDistributorMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_distributor_master(
        self,
        request: UpdateCurrentDistributorMasterRequest,
    ) -> UpdateCurrentDistributorMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_distributor_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_distributor_master_async(
        self,
        request: UpdateCurrentDistributorMasterRequest,
    ) -> UpdateCurrentDistributorMasterResult:
        async_result = []
        self._update_current_distributor_master(
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

    def _update_current_distributor_master_from_git_hub(
        self,
        request: UpdateCurrentDistributorMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentDistributorMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='currentDistributorMaster',
            function='updateCurrentDistributorMasterFromGitHub',
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
                result_type=UpdateCurrentDistributorMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_distributor_master_from_git_hub(
        self,
        request: UpdateCurrentDistributorMasterFromGitHubRequest,
    ) -> UpdateCurrentDistributorMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_distributor_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_distributor_master_from_git_hub_async(
        self,
        request: UpdateCurrentDistributorMasterFromGitHubRequest,
    ) -> UpdateCurrentDistributorMasterFromGitHubResult:
        async_result = []
        self._update_current_distributor_master_from_git_hub(
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

    def _distribute(
        self,
        request: DistributeRequest,
        callback: Callable[[AsyncResult[DistributeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='distribute',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.distributor_name is not None:
            body["distributorName"] = request.distributor_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.distribute_resource is not None:
            body["distributeResource"] = request.distribute_resource.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DistributeResult,
                callback=callback,
                body=body,
            )
        )

    def distribute(
        self,
        request: DistributeRequest,
    ) -> DistributeResult:
        async_result = []
        with timeout(30):
            self._distribute(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def distribute_async(
        self,
        request: DistributeRequest,
    ) -> DistributeResult:
        async_result = []
        self._distribute(
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

    def _distribute_without_overflow_process(
        self,
        request: DistributeWithoutOverflowProcessRequest,
        callback: Callable[[AsyncResult[DistributeWithoutOverflowProcessResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='distributeWithoutOverflowProcess',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.distribute_resource is not None:
            body["distributeResource"] = request.distribute_resource.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DistributeWithoutOverflowProcessResult,
                callback=callback,
                body=body,
            )
        )

    def distribute_without_overflow_process(
        self,
        request: DistributeWithoutOverflowProcessRequest,
    ) -> DistributeWithoutOverflowProcessResult:
        async_result = []
        with timeout(30):
            self._distribute_without_overflow_process(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def distribute_without_overflow_process_async(
        self,
        request: DistributeWithoutOverflowProcessRequest,
    ) -> DistributeWithoutOverflowProcessResult:
        async_result = []
        self._distribute_without_overflow_process(
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

    def _run_stamp_task(
        self,
        request: RunStampTaskRequest,
        callback: Callable[[AsyncResult[RunStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='runStampTask',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=RunStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def run_stamp_task(
        self,
        request: RunStampTaskRequest,
    ) -> RunStampTaskResult:
        async_result = []
        with timeout(30):
            self._run_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_task_async(
        self,
        request: RunStampTaskRequest,
    ) -> RunStampTaskResult:
        async_result = []
        self._run_stamp_task(
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

    def _run_stamp_sheet(
        self,
        request: RunStampSheetRequest,
        callback: Callable[[AsyncResult[RunStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='runStampSheet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=RunStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def run_stamp_sheet(
        self,
        request: RunStampSheetRequest,
    ) -> RunStampSheetResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_async(
        self,
        request: RunStampSheetRequest,
    ) -> RunStampSheetResult:
        async_result = []
        self._run_stamp_sheet(
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

    def _run_stamp_sheet_express(
        self,
        request: RunStampSheetExpressRequest,
        callback: Callable[[AsyncResult[RunStampSheetExpressResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='runStampSheetExpress',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=RunStampSheetExpressResult,
                callback=callback,
                body=body,
            )
        )

    def run_stamp_sheet_express(
        self,
        request: RunStampSheetExpressRequest,
    ) -> RunStampSheetExpressResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet_express(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_express_async(
        self,
        request: RunStampSheetExpressRequest,
    ) -> RunStampSheetExpressResult:
        async_result = []
        self._run_stamp_sheet_express(
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

    def _run_stamp_task_without_namespace(
        self,
        request: RunStampTaskWithoutNamespaceRequest,
        callback: Callable[[AsyncResult[RunStampTaskWithoutNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='runStampTaskWithoutNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=RunStampTaskWithoutNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def run_stamp_task_without_namespace(
        self,
        request: RunStampTaskWithoutNamespaceRequest,
    ) -> RunStampTaskWithoutNamespaceResult:
        async_result = []
        with timeout(30):
            self._run_stamp_task_without_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_task_without_namespace_async(
        self,
        request: RunStampTaskWithoutNamespaceRequest,
    ) -> RunStampTaskWithoutNamespaceResult:
        async_result = []
        self._run_stamp_task_without_namespace(
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

    def _run_stamp_sheet_without_namespace(
        self,
        request: RunStampSheetWithoutNamespaceRequest,
        callback: Callable[[AsyncResult[RunStampSheetWithoutNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='runStampSheetWithoutNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=RunStampSheetWithoutNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def run_stamp_sheet_without_namespace(
        self,
        request: RunStampSheetWithoutNamespaceRequest,
    ) -> RunStampSheetWithoutNamespaceResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet_without_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_without_namespace_async(
        self,
        request: RunStampSheetWithoutNamespaceRequest,
    ) -> RunStampSheetWithoutNamespaceResult:
        async_result = []
        self._run_stamp_sheet_without_namespace(
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

    def _run_stamp_sheet_express_without_namespace(
        self,
        request: RunStampSheetExpressWithoutNamespaceRequest,
        callback: Callable[[AsyncResult[RunStampSheetExpressWithoutNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='distribute',
            function='runStampSheetExpressWithoutNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=RunStampSheetExpressWithoutNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def run_stamp_sheet_express_without_namespace(
        self,
        request: RunStampSheetExpressWithoutNamespaceRequest,
    ) -> RunStampSheetExpressWithoutNamespaceResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet_express_without_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_express_without_namespace_async(
        self,
        request: RunStampSheetExpressWithoutNamespaceRequest,
    ) -> RunStampSheetExpressWithoutNamespaceResult:
        async_result = []
        self._run_stamp_sheet_express_without_namespace(
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

    def _get_stamp_sheet_result(
        self,
        request: GetStampSheetResultRequest,
        callback: Callable[[AsyncResult[GetStampSheetResultResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='stampSheetResult',
            function='getStampSheetResult',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetStampSheetResultResult,
                callback=callback,
                body=body,
            )
        )

    def get_stamp_sheet_result(
        self,
        request: GetStampSheetResultRequest,
    ) -> GetStampSheetResultResult:
        async_result = []
        with timeout(30):
            self._get_stamp_sheet_result(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamp_sheet_result_async(
        self,
        request: GetStampSheetResultRequest,
    ) -> GetStampSheetResultResult:
        async_result = []
        self._get_stamp_sheet_result(
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

    def _get_stamp_sheet_result_by_user_id(
        self,
        request: GetStampSheetResultByUserIdRequest,
        callback: Callable[[AsyncResult[GetStampSheetResultByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="distributor",
            component='stampSheetResult',
            function='getStampSheetResultByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetStampSheetResultByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_stamp_sheet_result_by_user_id(
        self,
        request: GetStampSheetResultByUserIdRequest,
    ) -> GetStampSheetResultByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_stamp_sheet_result_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamp_sheet_result_by_user_id_async(
        self,
        request: GetStampSheetResultByUserIdRequest,
    ) -> GetStampSheetResultByUserIdResult:
        async_result = []
        self._get_stamp_sheet_result_by_user_id(
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