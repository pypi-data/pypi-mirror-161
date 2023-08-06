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
from inventory.request import *
from inventory.result import *


class Gs2InventoryWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
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
            service="inventory",
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
        if request.acquire_script is not None:
            body["acquireScript"] = request.acquire_script.to_dict()
        if request.overflow_script is not None:
            body["overflowScript"] = request.overflow_script.to_dict()
        if request.consume_script is not None:
            body["consumeScript"] = request.consume_script.to_dict()
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
            service="inventory",
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
            service="inventory",
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
            service="inventory",
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
        if request.acquire_script is not None:
            body["acquireScript"] = request.acquire_script.to_dict()
        if request.overflow_script is not None:
            body["overflowScript"] = request.overflow_script.to_dict()
        if request.consume_script is not None:
            body["consumeScript"] = request.consume_script.to_dict()
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
            service="inventory",
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

    def _describe_inventory_model_masters(
        self,
        request: DescribeInventoryModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeInventoryModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventoryModelMaster',
            function='describeInventoryModelMasters',
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
                result_type=DescribeInventoryModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_inventory_model_masters(
        self,
        request: DescribeInventoryModelMastersRequest,
    ) -> DescribeInventoryModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_inventory_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventory_model_masters_async(
        self,
        request: DescribeInventoryModelMastersRequest,
    ) -> DescribeInventoryModelMastersResult:
        async_result = []
        self._describe_inventory_model_masters(
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

    def _create_inventory_model_master(
        self,
        request: CreateInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[CreateInventoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventoryModelMaster',
            function='createInventoryModelMaster',
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
        if request.initial_capacity is not None:
            body["initialCapacity"] = request.initial_capacity
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity
        if request.protect_referenced_item is not None:
            body["protectReferencedItem"] = request.protect_referenced_item

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateInventoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_inventory_model_master(
        self,
        request: CreateInventoryModelMasterRequest,
    ) -> CreateInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_inventory_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_inventory_model_master_async(
        self,
        request: CreateInventoryModelMasterRequest,
    ) -> CreateInventoryModelMasterResult:
        async_result = []
        self._create_inventory_model_master(
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

    def _get_inventory_model_master(
        self,
        request: GetInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[GetInventoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventoryModelMaster',
            function='getInventoryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetInventoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_inventory_model_master(
        self,
        request: GetInventoryModelMasterRequest,
    ) -> GetInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_inventory_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_model_master_async(
        self,
        request: GetInventoryModelMasterRequest,
    ) -> GetInventoryModelMasterResult:
        async_result = []
        self._get_inventory_model_master(
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

    def _update_inventory_model_master(
        self,
        request: UpdateInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateInventoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventoryModelMaster',
            function='updateInventoryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.initial_capacity is not None:
            body["initialCapacity"] = request.initial_capacity
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity
        if request.protect_referenced_item is not None:
            body["protectReferencedItem"] = request.protect_referenced_item

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateInventoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_inventory_model_master(
        self,
        request: UpdateInventoryModelMasterRequest,
    ) -> UpdateInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_inventory_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_inventory_model_master_async(
        self,
        request: UpdateInventoryModelMasterRequest,
    ) -> UpdateInventoryModelMasterResult:
        async_result = []
        self._update_inventory_model_master(
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

    def _delete_inventory_model_master(
        self,
        request: DeleteInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteInventoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventoryModelMaster',
            function='deleteInventoryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteInventoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_inventory_model_master(
        self,
        request: DeleteInventoryModelMasterRequest,
    ) -> DeleteInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_inventory_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_inventory_model_master_async(
        self,
        request: DeleteInventoryModelMasterRequest,
    ) -> DeleteInventoryModelMasterResult:
        async_result = []
        self._delete_inventory_model_master(
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

    def _describe_inventory_models(
        self,
        request: DescribeInventoryModelsRequest,
        callback: Callable[[AsyncResult[DescribeInventoryModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventoryModel',
            function='describeInventoryModels',
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
                result_type=DescribeInventoryModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_inventory_models(
        self,
        request: DescribeInventoryModelsRequest,
    ) -> DescribeInventoryModelsResult:
        async_result = []
        with timeout(30):
            self._describe_inventory_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventory_models_async(
        self,
        request: DescribeInventoryModelsRequest,
    ) -> DescribeInventoryModelsResult:
        async_result = []
        self._describe_inventory_models(
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

    def _get_inventory_model(
        self,
        request: GetInventoryModelRequest,
        callback: Callable[[AsyncResult[GetInventoryModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventoryModel',
            function='getInventoryModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetInventoryModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_inventory_model(
        self,
        request: GetInventoryModelRequest,
    ) -> GetInventoryModelResult:
        async_result = []
        with timeout(30):
            self._get_inventory_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_model_async(
        self,
        request: GetInventoryModelRequest,
    ) -> GetInventoryModelResult:
        async_result = []
        self._get_inventory_model(
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

    def _describe_item_model_masters(
        self,
        request: DescribeItemModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeItemModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemModelMaster',
            function='describeItemModelMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeItemModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_item_model_masters(
        self,
        request: DescribeItemModelMastersRequest,
    ) -> DescribeItemModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_item_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_model_masters_async(
        self,
        request: DescribeItemModelMastersRequest,
    ) -> DescribeItemModelMastersResult:
        async_result = []
        self._describe_item_model_masters(
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

    def _create_item_model_master(
        self,
        request: CreateItemModelMasterRequest,
        callback: Callable[[AsyncResult[CreateItemModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemModelMaster',
            function='createItemModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.stacking_limit is not None:
            body["stackingLimit"] = request.stacking_limit
        if request.allow_multiple_stacks is not None:
            body["allowMultipleStacks"] = request.allow_multiple_stacks
        if request.sort_value is not None:
            body["sortValue"] = request.sort_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateItemModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_item_model_master(
        self,
        request: CreateItemModelMasterRequest,
    ) -> CreateItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_item_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_item_model_master_async(
        self,
        request: CreateItemModelMasterRequest,
    ) -> CreateItemModelMasterResult:
        async_result = []
        self._create_item_model_master(
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

    def _get_item_model_master(
        self,
        request: GetItemModelMasterRequest,
        callback: Callable[[AsyncResult[GetItemModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemModelMaster',
            function='getItemModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.item_name is not None:
            body["itemName"] = request.item_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetItemModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_item_model_master(
        self,
        request: GetItemModelMasterRequest,
    ) -> GetItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_item_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_model_master_async(
        self,
        request: GetItemModelMasterRequest,
    ) -> GetItemModelMasterResult:
        async_result = []
        self._get_item_model_master(
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

    def _update_item_model_master(
        self,
        request: UpdateItemModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateItemModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemModelMaster',
            function='updateItemModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.stacking_limit is not None:
            body["stackingLimit"] = request.stacking_limit
        if request.allow_multiple_stacks is not None:
            body["allowMultipleStacks"] = request.allow_multiple_stacks
        if request.sort_value is not None:
            body["sortValue"] = request.sort_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateItemModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_item_model_master(
        self,
        request: UpdateItemModelMasterRequest,
    ) -> UpdateItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_item_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_item_model_master_async(
        self,
        request: UpdateItemModelMasterRequest,
    ) -> UpdateItemModelMasterResult:
        async_result = []
        self._update_item_model_master(
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

    def _delete_item_model_master(
        self,
        request: DeleteItemModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteItemModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemModelMaster',
            function='deleteItemModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.item_name is not None:
            body["itemName"] = request.item_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteItemModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_item_model_master(
        self,
        request: DeleteItemModelMasterRequest,
    ) -> DeleteItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_item_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_item_model_master_async(
        self,
        request: DeleteItemModelMasterRequest,
    ) -> DeleteItemModelMasterResult:
        async_result = []
        self._delete_item_model_master(
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

    def _describe_item_models(
        self,
        request: DescribeItemModelsRequest,
        callback: Callable[[AsyncResult[DescribeItemModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemModel',
            function='describeItemModels',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeItemModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_item_models(
        self,
        request: DescribeItemModelsRequest,
    ) -> DescribeItemModelsResult:
        async_result = []
        with timeout(30):
            self._describe_item_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_models_async(
        self,
        request: DescribeItemModelsRequest,
    ) -> DescribeItemModelsResult:
        async_result = []
        self._describe_item_models(
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

    def _get_item_model(
        self,
        request: GetItemModelRequest,
        callback: Callable[[AsyncResult[GetItemModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemModel',
            function='getItemModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.item_name is not None:
            body["itemName"] = request.item_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetItemModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_item_model(
        self,
        request: GetItemModelRequest,
    ) -> GetItemModelResult:
        async_result = []
        with timeout(30):
            self._get_item_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_model_async(
        self,
        request: GetItemModelRequest,
    ) -> GetItemModelResult:
        async_result = []
        self._get_item_model(
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
            service="inventory",
            component='currentItemModelMaster',
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

    def _get_current_item_model_master(
        self,
        request: GetCurrentItemModelMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentItemModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='currentItemModelMaster',
            function='getCurrentItemModelMaster',
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
                result_type=GetCurrentItemModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_item_model_master(
        self,
        request: GetCurrentItemModelMasterRequest,
    ) -> GetCurrentItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_item_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_item_model_master_async(
        self,
        request: GetCurrentItemModelMasterRequest,
    ) -> GetCurrentItemModelMasterResult:
        async_result = []
        self._get_current_item_model_master(
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

    def _update_current_item_model_master(
        self,
        request: UpdateCurrentItemModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentItemModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='currentItemModelMaster',
            function='updateCurrentItemModelMaster',
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
                result_type=UpdateCurrentItemModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_item_model_master(
        self,
        request: UpdateCurrentItemModelMasterRequest,
    ) -> UpdateCurrentItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_item_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_item_model_master_async(
        self,
        request: UpdateCurrentItemModelMasterRequest,
    ) -> UpdateCurrentItemModelMasterResult:
        async_result = []
        self._update_current_item_model_master(
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

    def _update_current_item_model_master_from_git_hub(
        self,
        request: UpdateCurrentItemModelMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentItemModelMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='currentItemModelMaster',
            function='updateCurrentItemModelMasterFromGitHub',
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
                result_type=UpdateCurrentItemModelMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_item_model_master_from_git_hub(
        self,
        request: UpdateCurrentItemModelMasterFromGitHubRequest,
    ) -> UpdateCurrentItemModelMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_item_model_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_item_model_master_from_git_hub_async(
        self,
        request: UpdateCurrentItemModelMasterFromGitHubRequest,
    ) -> UpdateCurrentItemModelMasterFromGitHubResult:
        async_result = []
        self._update_current_item_model_master_from_git_hub(
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

    def _describe_inventories(
        self,
        request: DescribeInventoriesRequest,
        callback: Callable[[AsyncResult[DescribeInventoriesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='describeInventories',
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
                result_type=DescribeInventoriesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_inventories(
        self,
        request: DescribeInventoriesRequest,
    ) -> DescribeInventoriesResult:
        async_result = []
        with timeout(30):
            self._describe_inventories(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventories_async(
        self,
        request: DescribeInventoriesRequest,
    ) -> DescribeInventoriesResult:
        async_result = []
        self._describe_inventories(
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

    def _describe_inventories_by_user_id(
        self,
        request: DescribeInventoriesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeInventoriesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='describeInventoriesByUserId',
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
                result_type=DescribeInventoriesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_inventories_by_user_id(
        self,
        request: DescribeInventoriesByUserIdRequest,
    ) -> DescribeInventoriesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_inventories_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventories_by_user_id_async(
        self,
        request: DescribeInventoriesByUserIdRequest,
    ) -> DescribeInventoriesByUserIdResult:
        async_result = []
        self._describe_inventories_by_user_id(
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

    def _get_inventory(
        self,
        request: GetInventoryRequest,
        callback: Callable[[AsyncResult[GetInventoryResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='getInventory',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetInventoryResult,
                callback=callback,
                body=body,
            )
        )

    def get_inventory(
        self,
        request: GetInventoryRequest,
    ) -> GetInventoryResult:
        async_result = []
        with timeout(30):
            self._get_inventory(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_async(
        self,
        request: GetInventoryRequest,
    ) -> GetInventoryResult:
        async_result = []
        self._get_inventory(
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

    def _get_inventory_by_user_id(
        self,
        request: GetInventoryByUserIdRequest,
        callback: Callable[[AsyncResult[GetInventoryByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='getInventoryByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetInventoryByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_inventory_by_user_id(
        self,
        request: GetInventoryByUserIdRequest,
    ) -> GetInventoryByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_inventory_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_by_user_id_async(
        self,
        request: GetInventoryByUserIdRequest,
    ) -> GetInventoryByUserIdResult:
        async_result = []
        self._get_inventory_by_user_id(
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

    def _add_capacity_by_user_id(
        self,
        request: AddCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[AddCapacityByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='addCapacityByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.add_capacity_value is not None:
            body["addCapacityValue"] = request.add_capacity_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AddCapacityByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_capacity_by_user_id(
        self,
        request: AddCapacityByUserIdRequest,
    ) -> AddCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_capacity_by_user_id_async(
        self,
        request: AddCapacityByUserIdRequest,
    ) -> AddCapacityByUserIdResult:
        async_result = []
        self._add_capacity_by_user_id(
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

    def _set_capacity_by_user_id(
        self,
        request: SetCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[SetCapacityByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='setCapacityByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.new_capacity_value is not None:
            body["newCapacityValue"] = request.new_capacity_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=SetCapacityByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_capacity_by_user_id(
        self,
        request: SetCapacityByUserIdRequest,
    ) -> SetCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_capacity_by_user_id_async(
        self,
        request: SetCapacityByUserIdRequest,
    ) -> SetCapacityByUserIdResult:
        async_result = []
        self._set_capacity_by_user_id(
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

    def _delete_inventory_by_user_id(
        self,
        request: DeleteInventoryByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteInventoryByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='deleteInventoryByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteInventoryByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_inventory_by_user_id(
        self,
        request: DeleteInventoryByUserIdRequest,
    ) -> DeleteInventoryByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_inventory_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_inventory_by_user_id_async(
        self,
        request: DeleteInventoryByUserIdRequest,
    ) -> DeleteInventoryByUserIdResult:
        async_result = []
        self._delete_inventory_by_user_id(
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

    def _add_capacity_by_stamp_sheet(
        self,
        request: AddCapacityByStampSheetRequest,
        callback: Callable[[AsyncResult[AddCapacityByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='addCapacityByStampSheet',
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
                result_type=AddCapacityByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_capacity_by_stamp_sheet(
        self,
        request: AddCapacityByStampSheetRequest,
    ) -> AddCapacityByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_capacity_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_capacity_by_stamp_sheet_async(
        self,
        request: AddCapacityByStampSheetRequest,
    ) -> AddCapacityByStampSheetResult:
        async_result = []
        self._add_capacity_by_stamp_sheet(
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

    def _set_capacity_by_stamp_sheet(
        self,
        request: SetCapacityByStampSheetRequest,
        callback: Callable[[AsyncResult[SetCapacityByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='inventory',
            function='setCapacityByStampSheet',
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
                result_type=SetCapacityByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_capacity_by_stamp_sheet(
        self,
        request: SetCapacityByStampSheetRequest,
    ) -> SetCapacityByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_capacity_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_capacity_by_stamp_sheet_async(
        self,
        request: SetCapacityByStampSheetRequest,
    ) -> SetCapacityByStampSheetResult:
        async_result = []
        self._set_capacity_by_stamp_sheet(
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

    def _describe_item_sets(
        self,
        request: DescribeItemSetsRequest,
        callback: Callable[[AsyncResult[DescribeItemSetsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='describeItemSets',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
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
                result_type=DescribeItemSetsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_item_sets(
        self,
        request: DescribeItemSetsRequest,
    ) -> DescribeItemSetsResult:
        async_result = []
        with timeout(30):
            self._describe_item_sets(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_sets_async(
        self,
        request: DescribeItemSetsRequest,
    ) -> DescribeItemSetsResult:
        async_result = []
        self._describe_item_sets(
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

    def _describe_item_sets_by_user_id(
        self,
        request: DescribeItemSetsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeItemSetsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='describeItemSetsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
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
                result_type=DescribeItemSetsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_item_sets_by_user_id(
        self,
        request: DescribeItemSetsByUserIdRequest,
    ) -> DescribeItemSetsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_item_sets_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_sets_by_user_id_async(
        self,
        request: DescribeItemSetsByUserIdRequest,
    ) -> DescribeItemSetsByUserIdResult:
        async_result = []
        self._describe_item_sets_by_user_id(
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

    def _get_item_set(
        self,
        request: GetItemSetRequest,
        callback: Callable[[AsyncResult[GetItemSetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='getItemSet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetItemSetResult,
                callback=callback,
                body=body,
            )
        )

    def get_item_set(
        self,
        request: GetItemSetRequest,
    ) -> GetItemSetResult:
        async_result = []
        with timeout(30):
            self._get_item_set(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_set_async(
        self,
        request: GetItemSetRequest,
    ) -> GetItemSetResult:
        async_result = []
        self._get_item_set(
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

    def _get_item_set_by_user_id(
        self,
        request: GetItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[GetItemSetByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='getItemSetByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetItemSetByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_item_set_by_user_id(
        self,
        request: GetItemSetByUserIdRequest,
    ) -> GetItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_set_by_user_id_async(
        self,
        request: GetItemSetByUserIdRequest,
    ) -> GetItemSetByUserIdResult:
        async_result = []
        self._get_item_set_by_user_id(
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

    def _get_item_with_signature(
        self,
        request: GetItemWithSignatureRequest,
        callback: Callable[[AsyncResult[GetItemWithSignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='getItemWithSignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetItemWithSignatureResult,
                callback=callback,
                body=body,
            )
        )

    def get_item_with_signature(
        self,
        request: GetItemWithSignatureRequest,
    ) -> GetItemWithSignatureResult:
        async_result = []
        with timeout(30):
            self._get_item_with_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_with_signature_async(
        self,
        request: GetItemWithSignatureRequest,
    ) -> GetItemWithSignatureResult:
        async_result = []
        self._get_item_with_signature(
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

    def _get_item_with_signature_by_user_id(
        self,
        request: GetItemWithSignatureByUserIdRequest,
        callback: Callable[[AsyncResult[GetItemWithSignatureByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='getItemWithSignatureByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetItemWithSignatureByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_item_with_signature_by_user_id(
        self,
        request: GetItemWithSignatureByUserIdRequest,
    ) -> GetItemWithSignatureByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_item_with_signature_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_with_signature_by_user_id_async(
        self,
        request: GetItemWithSignatureByUserIdRequest,
    ) -> GetItemWithSignatureByUserIdResult:
        async_result = []
        self._get_item_with_signature_by_user_id(
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

    def _acquire_item_set_by_user_id(
        self,
        request: AcquireItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[AcquireItemSetByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='acquireItemSetByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.acquire_count is not None:
            body["acquireCount"] = request.acquire_count
        if request.expires_at is not None:
            body["expiresAt"] = request.expires_at
        if request.create_new_item_set is not None:
            body["createNewItemSet"] = request.create_new_item_set
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AcquireItemSetByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def acquire_item_set_by_user_id(
        self,
        request: AcquireItemSetByUserIdRequest,
    ) -> AcquireItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._acquire_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_item_set_by_user_id_async(
        self,
        request: AcquireItemSetByUserIdRequest,
    ) -> AcquireItemSetByUserIdResult:
        async_result = []
        self._acquire_item_set_by_user_id(
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

    def _consume_item_set(
        self,
        request: ConsumeItemSetRequest,
        callback: Callable[[AsyncResult[ConsumeItemSetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='consumeItemSet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.consume_count is not None:
            body["consumeCount"] = request.consume_count
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=ConsumeItemSetResult,
                callback=callback,
                body=body,
            )
        )

    def consume_item_set(
        self,
        request: ConsumeItemSetRequest,
    ) -> ConsumeItemSetResult:
        async_result = []
        with timeout(30):
            self._consume_item_set(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_item_set_async(
        self,
        request: ConsumeItemSetRequest,
    ) -> ConsumeItemSetResult:
        async_result = []
        self._consume_item_set(
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

    def _consume_item_set_by_user_id(
        self,
        request: ConsumeItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[ConsumeItemSetByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='consumeItemSetByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.consume_count is not None:
            body["consumeCount"] = request.consume_count
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=ConsumeItemSetByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def consume_item_set_by_user_id(
        self,
        request: ConsumeItemSetByUserIdRequest,
    ) -> ConsumeItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._consume_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_item_set_by_user_id_async(
        self,
        request: ConsumeItemSetByUserIdRequest,
    ) -> ConsumeItemSetByUserIdResult:
        async_result = []
        self._consume_item_set_by_user_id(
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

    def _delete_item_set_by_user_id(
        self,
        request: DeleteItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteItemSetByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='deleteItemSetByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteItemSetByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_item_set_by_user_id(
        self,
        request: DeleteItemSetByUserIdRequest,
    ) -> DeleteItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_item_set_by_user_id_async(
        self,
        request: DeleteItemSetByUserIdRequest,
    ) -> DeleteItemSetByUserIdResult:
        async_result = []
        self._delete_item_set_by_user_id(
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

    def _acquire_item_set_by_stamp_sheet(
        self,
        request: AcquireItemSetByStampSheetRequest,
        callback: Callable[[AsyncResult[AcquireItemSetByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='acquireItemSetByStampSheet',
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
                result_type=AcquireItemSetByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def acquire_item_set_by_stamp_sheet(
        self,
        request: AcquireItemSetByStampSheetRequest,
    ) -> AcquireItemSetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._acquire_item_set_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_item_set_by_stamp_sheet_async(
        self,
        request: AcquireItemSetByStampSheetRequest,
    ) -> AcquireItemSetByStampSheetResult:
        async_result = []
        self._acquire_item_set_by_stamp_sheet(
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

    def _consume_item_set_by_stamp_task(
        self,
        request: ConsumeItemSetByStampTaskRequest,
        callback: Callable[[AsyncResult[ConsumeItemSetByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='itemSet',
            function='consumeItemSetByStampTask',
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
                result_type=ConsumeItemSetByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def consume_item_set_by_stamp_task(
        self,
        request: ConsumeItemSetByStampTaskRequest,
    ) -> ConsumeItemSetByStampTaskResult:
        async_result = []
        with timeout(30):
            self._consume_item_set_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_item_set_by_stamp_task_async(
        self,
        request: ConsumeItemSetByStampTaskRequest,
    ) -> ConsumeItemSetByStampTaskResult:
        async_result = []
        self._consume_item_set_by_stamp_task(
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

    def _describe_reference_of(
        self,
        request: DescribeReferenceOfRequest,
        callback: Callable[[AsyncResult[DescribeReferenceOfResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='describeReferenceOf',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeReferenceOfResult,
                callback=callback,
                body=body,
            )
        )

    def describe_reference_of(
        self,
        request: DescribeReferenceOfRequest,
    ) -> DescribeReferenceOfResult:
        async_result = []
        with timeout(30):
            self._describe_reference_of(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_reference_of_async(
        self,
        request: DescribeReferenceOfRequest,
    ) -> DescribeReferenceOfResult:
        async_result = []
        self._describe_reference_of(
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

    def _describe_reference_of_by_user_id(
        self,
        request: DescribeReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeReferenceOfByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='describeReferenceOfByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeReferenceOfByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_reference_of_by_user_id(
        self,
        request: DescribeReferenceOfByUserIdRequest,
    ) -> DescribeReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_reference_of_by_user_id_async(
        self,
        request: DescribeReferenceOfByUserIdRequest,
    ) -> DescribeReferenceOfByUserIdResult:
        async_result = []
        self._describe_reference_of_by_user_id(
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

    def _get_reference_of(
        self,
        request: GetReferenceOfRequest,
        callback: Callable[[AsyncResult[GetReferenceOfResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='getReferenceOf',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetReferenceOfResult,
                callback=callback,
                body=body,
            )
        )

    def get_reference_of(
        self,
        request: GetReferenceOfRequest,
    ) -> GetReferenceOfResult:
        async_result = []
        with timeout(30):
            self._get_reference_of(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_reference_of_async(
        self,
        request: GetReferenceOfRequest,
    ) -> GetReferenceOfResult:
        async_result = []
        self._get_reference_of(
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

    def _get_reference_of_by_user_id(
        self,
        request: GetReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[GetReferenceOfByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='getReferenceOfByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetReferenceOfByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_reference_of_by_user_id(
        self,
        request: GetReferenceOfByUserIdRequest,
    ) -> GetReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_reference_of_by_user_id_async(
        self,
        request: GetReferenceOfByUserIdRequest,
    ) -> GetReferenceOfByUserIdResult:
        async_result = []
        self._get_reference_of_by_user_id(
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

    def _verify_reference_of(
        self,
        request: VerifyReferenceOfRequest,
        callback: Callable[[AsyncResult[VerifyReferenceOfResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='verifyReferenceOf',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=VerifyReferenceOfResult,
                callback=callback,
                body=body,
            )
        )

    def verify_reference_of(
        self,
        request: VerifyReferenceOfRequest,
    ) -> VerifyReferenceOfResult:
        async_result = []
        with timeout(30):
            self._verify_reference_of(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_reference_of_async(
        self,
        request: VerifyReferenceOfRequest,
    ) -> VerifyReferenceOfResult:
        async_result = []
        self._verify_reference_of(
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

    def _verify_reference_of_by_user_id(
        self,
        request: VerifyReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyReferenceOfByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='verifyReferenceOfByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=VerifyReferenceOfByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_reference_of_by_user_id(
        self,
        request: VerifyReferenceOfByUserIdRequest,
    ) -> VerifyReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_reference_of_by_user_id_async(
        self,
        request: VerifyReferenceOfByUserIdRequest,
    ) -> VerifyReferenceOfByUserIdResult:
        async_result = []
        self._verify_reference_of_by_user_id(
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

    def _add_reference_of(
        self,
        request: AddReferenceOfRequest,
        callback: Callable[[AsyncResult[AddReferenceOfResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='addReferenceOf',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AddReferenceOfResult,
                callback=callback,
                body=body,
            )
        )

    def add_reference_of(
        self,
        request: AddReferenceOfRequest,
    ) -> AddReferenceOfResult:
        async_result = []
        with timeout(30):
            self._add_reference_of(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_reference_of_async(
        self,
        request: AddReferenceOfRequest,
    ) -> AddReferenceOfResult:
        async_result = []
        self._add_reference_of(
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

    def _add_reference_of_by_user_id(
        self,
        request: AddReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[AddReferenceOfByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='addReferenceOfByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AddReferenceOfByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_reference_of_by_user_id(
        self,
        request: AddReferenceOfByUserIdRequest,
    ) -> AddReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_reference_of_by_user_id_async(
        self,
        request: AddReferenceOfByUserIdRequest,
    ) -> AddReferenceOfByUserIdResult:
        async_result = []
        self._add_reference_of_by_user_id(
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

    def _delete_reference_of(
        self,
        request: DeleteReferenceOfRequest,
        callback: Callable[[AsyncResult[DeleteReferenceOfResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='deleteReferenceOf',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteReferenceOfResult,
                callback=callback,
                body=body,
            )
        )

    def delete_reference_of(
        self,
        request: DeleteReferenceOfRequest,
    ) -> DeleteReferenceOfResult:
        async_result = []
        with timeout(30):
            self._delete_reference_of(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_reference_of_async(
        self,
        request: DeleteReferenceOfRequest,
    ) -> DeleteReferenceOfResult:
        async_result = []
        self._delete_reference_of(
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

    def _delete_reference_of_by_user_id(
        self,
        request: DeleteReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteReferenceOfByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='deleteReferenceOfByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.inventory_name is not None:
            body["inventoryName"] = request.inventory_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.item_name is not None:
            body["itemName"] = request.item_name
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteReferenceOfByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_reference_of_by_user_id(
        self,
        request: DeleteReferenceOfByUserIdRequest,
    ) -> DeleteReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_reference_of_by_user_id_async(
        self,
        request: DeleteReferenceOfByUserIdRequest,
    ) -> DeleteReferenceOfByUserIdResult:
        async_result = []
        self._delete_reference_of_by_user_id(
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

    def _add_reference_of_item_set_by_stamp_sheet(
        self,
        request: AddReferenceOfItemSetByStampSheetRequest,
        callback: Callable[[AsyncResult[AddReferenceOfItemSetByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='addReferenceOfItemSetByStampSheet',
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
                result_type=AddReferenceOfItemSetByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_reference_of_item_set_by_stamp_sheet(
        self,
        request: AddReferenceOfItemSetByStampSheetRequest,
    ) -> AddReferenceOfItemSetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_reference_of_item_set_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_reference_of_item_set_by_stamp_sheet_async(
        self,
        request: AddReferenceOfItemSetByStampSheetRequest,
    ) -> AddReferenceOfItemSetByStampSheetResult:
        async_result = []
        self._add_reference_of_item_set_by_stamp_sheet(
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

    def _delete_reference_of_item_set_by_stamp_sheet(
        self,
        request: DeleteReferenceOfItemSetByStampSheetRequest,
        callback: Callable[[AsyncResult[DeleteReferenceOfItemSetByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='deleteReferenceOfItemSetByStampSheet',
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
                result_type=DeleteReferenceOfItemSetByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def delete_reference_of_item_set_by_stamp_sheet(
        self,
        request: DeleteReferenceOfItemSetByStampSheetRequest,
    ) -> DeleteReferenceOfItemSetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._delete_reference_of_item_set_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_reference_of_item_set_by_stamp_sheet_async(
        self,
        request: DeleteReferenceOfItemSetByStampSheetRequest,
    ) -> DeleteReferenceOfItemSetByStampSheetResult:
        async_result = []
        self._delete_reference_of_item_set_by_stamp_sheet(
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

    def _verify_reference_of_by_stamp_task(
        self,
        request: VerifyReferenceOfByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyReferenceOfByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="inventory",
            component='referenceOf',
            function='verifyReferenceOfByStampTask',
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
                result_type=VerifyReferenceOfByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_reference_of_by_stamp_task(
        self,
        request: VerifyReferenceOfByStampTaskRequest,
    ) -> VerifyReferenceOfByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_reference_of_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_reference_of_by_stamp_task_async(
        self,
        request: VerifyReferenceOfByStampTaskRequest,
    ) -> VerifyReferenceOfByStampTaskResult:
        async_result = []
        self._verify_reference_of_by_stamp_task(
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