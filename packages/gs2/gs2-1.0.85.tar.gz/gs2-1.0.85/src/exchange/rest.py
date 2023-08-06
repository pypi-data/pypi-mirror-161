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
from exchange.request import *
from exchange.result import *


class Gs2ExchangeRestClient(AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
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
            service='exchange',
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
        if request.enable_await_exchange is not None:
            body["enableAwaitExchange"] = request.enable_await_exchange
        if request.enable_direct_exchange is not None:
            body["enableDirectExchange"] = request.enable_direct_exchange
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
        if request.exchange_script is not None:
            body["exchangeScript"] = request.exchange_script.to_dict()
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()
        if request.queue_namespace_id is not None:
            body["queueNamespaceId"] = request.queue_namespace_id
        if request.key_id is not None:
            body["keyId"] = request.key_id

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
            service='exchange',
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
            service='exchange',
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
            service='exchange',
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
        if request.enable_await_exchange is not None:
            body["enableAwaitExchange"] = request.enable_await_exchange
        if request.enable_direct_exchange is not None:
            body["enableDirectExchange"] = request.enable_direct_exchange
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
        if request.exchange_script is not None:
            body["exchangeScript"] = request.exchange_script.to_dict()
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()
        if request.queue_namespace_id is not None:
            body["queueNamespaceId"] = request.queue_namespace_id
        if request.key_id is not None:
            body["keyId"] = request.key_id

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
            service='exchange',
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

    def _describe_rate_models(
        self,
        request: DescribeRateModelsRequest,
        callback: Callable[[AsyncResult[DescribeRateModelsResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/model".format(
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
            result_type=DescribeRateModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_rate_models(
        self,
        request: DescribeRateModelsRequest,
    ) -> DescribeRateModelsResult:
        async_result = []
        with timeout(30):
            self._describe_rate_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rate_models_async(
        self,
        request: DescribeRateModelsRequest,
    ) -> DescribeRateModelsResult:
        async_result = []
        self._describe_rate_models(
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

    def _get_rate_model(
        self,
        request: GetRateModelRequest,
        callback: Callable[[AsyncResult[GetRateModelResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/model/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
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
            result_type=GetRateModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_rate_model(
        self,
        request: GetRateModelRequest,
    ) -> GetRateModelResult:
        async_result = []
        with timeout(30):
            self._get_rate_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rate_model_async(
        self,
        request: GetRateModelRequest,
    ) -> GetRateModelResult:
        async_result = []
        self._get_rate_model(
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

    def _describe_rate_model_masters(
        self,
        request: DescribeRateModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeRateModelMastersResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/master/model".format(
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
            result_type=DescribeRateModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_rate_model_masters(
        self,
        request: DescribeRateModelMastersRequest,
    ) -> DescribeRateModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_rate_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rate_model_masters_async(
        self,
        request: DescribeRateModelMastersRequest,
    ) -> DescribeRateModelMastersResult:
        async_result = []
        self._describe_rate_model_masters(
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

    def _create_rate_model_master(
        self,
        request: CreateRateModelMasterRequest,
        callback: Callable[[AsyncResult[CreateRateModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/master/model".format(
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
        if request.timing_type is not None:
            body["timingType"] = request.timing_type
        if request.lock_time is not None:
            body["lockTime"] = request.lock_time
        if request.enable_skip is not None:
            body["enableSkip"] = request.enable_skip
        if request.skip_consume_actions is not None:
            body["skipConsumeActions"] = [
                item.to_dict()
                for item in request.skip_consume_actions
            ]
        if request.acquire_actions is not None:
            body["acquireActions"] = [
                item.to_dict()
                for item in request.acquire_actions
            ]
        if request.consume_actions is not None:
            body["consumeActions"] = [
                item.to_dict()
                for item in request.consume_actions
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateRateModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_rate_model_master(
        self,
        request: CreateRateModelMasterRequest,
    ) -> CreateRateModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_rate_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_rate_model_master_async(
        self,
        request: CreateRateModelMasterRequest,
    ) -> CreateRateModelMasterResult:
        async_result = []
        self._create_rate_model_master(
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

    def _get_rate_model_master(
        self,
        request: GetRateModelMasterRequest,
        callback: Callable[[AsyncResult[GetRateModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
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
            result_type=GetRateModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_rate_model_master(
        self,
        request: GetRateModelMasterRequest,
    ) -> GetRateModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_rate_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rate_model_master_async(
        self,
        request: GetRateModelMasterRequest,
    ) -> GetRateModelMasterResult:
        async_result = []
        self._get_rate_model_master(
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

    def _update_rate_model_master(
        self,
        request: UpdateRateModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateRateModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.timing_type is not None:
            body["timingType"] = request.timing_type
        if request.lock_time is not None:
            body["lockTime"] = request.lock_time
        if request.enable_skip is not None:
            body["enableSkip"] = request.enable_skip
        if request.skip_consume_actions is not None:
            body["skipConsumeActions"] = [
                item.to_dict()
                for item in request.skip_consume_actions
            ]
        if request.acquire_actions is not None:
            body["acquireActions"] = [
                item.to_dict()
                for item in request.acquire_actions
            ]
        if request.consume_actions is not None:
            body["consumeActions"] = [
                item.to_dict()
                for item in request.consume_actions
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateRateModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_rate_model_master(
        self,
        request: UpdateRateModelMasterRequest,
    ) -> UpdateRateModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_rate_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_rate_model_master_async(
        self,
        request: UpdateRateModelMasterRequest,
    ) -> UpdateRateModelMasterResult:
        async_result = []
        self._update_rate_model_master(
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

    def _delete_rate_model_master(
        self,
        request: DeleteRateModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteRateModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
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
            result_type=DeleteRateModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_rate_model_master(
        self,
        request: DeleteRateModelMasterRequest,
    ) -> DeleteRateModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_rate_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_rate_model_master_async(
        self,
        request: DeleteRateModelMasterRequest,
    ) -> DeleteRateModelMasterResult:
        async_result = []
        self._delete_rate_model_master(
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

    def _exchange(
        self,
        request: ExchangeRequest,
        callback: Callable[[AsyncResult[ExchangeResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/exchange/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=ExchangeResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def exchange(
        self,
        request: ExchangeRequest,
    ) -> ExchangeResult:
        async_result = []
        with timeout(30):
            self._exchange(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def exchange_async(
        self,
        request: ExchangeRequest,
    ) -> ExchangeResult:
        async_result = []
        self._exchange(
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

    def _exchange_by_user_id(
        self,
        request: ExchangeByUserIdRequest,
        callback: Callable[[AsyncResult[ExchangeByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=ExchangeByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def exchange_by_user_id(
        self,
        request: ExchangeByUserIdRequest,
    ) -> ExchangeByUserIdResult:
        async_result = []
        with timeout(30):
            self._exchange_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def exchange_by_user_id_async(
        self,
        request: ExchangeByUserIdRequest,
    ) -> ExchangeByUserIdResult:
        async_result = []
        self._exchange_by_user_id(
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

    def _exchange_by_stamp_sheet(
        self,
        request: ExchangeByStampSheetRequest,
        callback: Callable[[AsyncResult[ExchangeByStampSheetResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/stamp/exchange"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=ExchangeByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def exchange_by_stamp_sheet(
        self,
        request: ExchangeByStampSheetRequest,
    ) -> ExchangeByStampSheetResult:
        async_result = []
        with timeout(30):
            self._exchange_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def exchange_by_stamp_sheet_async(
        self,
        request: ExchangeByStampSheetRequest,
    ) -> ExchangeByStampSheetResult:
        async_result = []
        self._exchange_by_stamp_sheet(
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
            service='exchange',
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

    def _get_current_rate_master(
        self,
        request: GetCurrentRateMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentRateMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
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
            result_type=GetCurrentRateMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_current_rate_master(
        self,
        request: GetCurrentRateMasterRequest,
    ) -> GetCurrentRateMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_rate_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_rate_master_async(
        self,
        request: GetCurrentRateMasterRequest,
    ) -> GetCurrentRateMasterResult:
        async_result = []
        self._get_current_rate_master(
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

    def _update_current_rate_master(
        self,
        request: UpdateCurrentRateMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRateMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
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
            result_type=UpdateCurrentRateMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_rate_master(
        self,
        request: UpdateCurrentRateMasterRequest,
    ) -> UpdateCurrentRateMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_rate_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_rate_master_async(
        self,
        request: UpdateCurrentRateMasterRequest,
    ) -> UpdateCurrentRateMasterResult:
        async_result = []
        self._update_current_rate_master(
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

    def _update_current_rate_master_from_git_hub(
        self,
        request: UpdateCurrentRateMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRateMasterFromGitHubResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
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
            result_type=UpdateCurrentRateMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_rate_master_from_git_hub(
        self,
        request: UpdateCurrentRateMasterFromGitHubRequest,
    ) -> UpdateCurrentRateMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_rate_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_rate_master_from_git_hub_async(
        self,
        request: UpdateCurrentRateMasterFromGitHubRequest,
    ) -> UpdateCurrentRateMasterFromGitHubResult:
        async_result = []
        self._update_current_rate_master_from_git_hub(
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

    def _create_await_by_user_id(
        self,
        request: CreateAwaitByUserIdRequest,
        callback: Callable[[AsyncResult[CreateAwaitByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/{rateName}/await".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=CreateAwaitByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_await_by_user_id(
        self,
        request: CreateAwaitByUserIdRequest,
    ) -> CreateAwaitByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_await_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_await_by_user_id_async(
        self,
        request: CreateAwaitByUserIdRequest,
    ) -> CreateAwaitByUserIdResult:
        async_result = []
        self._create_await_by_user_id(
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

    def _describe_awaits(
        self,
        request: DescribeAwaitsRequest,
        callback: Callable[[AsyncResult[DescribeAwaitsResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/exchange/await".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.rate_name is not None:
            query_strings["rateName"] = request.rate_name
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
            result_type=DescribeAwaitsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_awaits(
        self,
        request: DescribeAwaitsRequest,
    ) -> DescribeAwaitsResult:
        async_result = []
        with timeout(30):
            self._describe_awaits(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_awaits_async(
        self,
        request: DescribeAwaitsRequest,
    ) -> DescribeAwaitsResult:
        async_result = []
        self._describe_awaits(
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

    def _describe_awaits_by_user_id(
        self,
        request: DescribeAwaitsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeAwaitsByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/await".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.rate_name is not None:
            query_strings["rateName"] = request.rate_name
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeAwaitsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_awaits_by_user_id(
        self,
        request: DescribeAwaitsByUserIdRequest,
    ) -> DescribeAwaitsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_awaits_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_awaits_by_user_id_async(
        self,
        request: DescribeAwaitsByUserIdRequest,
    ) -> DescribeAwaitsByUserIdResult:
        async_result = []
        self._describe_awaits_by_user_id(
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

    def _get_await(
        self,
        request: GetAwaitRequest,
        callback: Callable[[AsyncResult[GetAwaitResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/exchange/{rateName}/await/{awaitName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
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
            result_type=GetAwaitResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_await(
        self,
        request: GetAwaitRequest,
    ) -> GetAwaitResult:
        async_result = []
        with timeout(30):
            self._get_await(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_await_async(
        self,
        request: GetAwaitRequest,
    ) -> GetAwaitResult:
        async_result = []
        self._get_await(
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

    def _get_await_by_user_id(
        self,
        request: GetAwaitByUserIdRequest,
        callback: Callable[[AsyncResult[GetAwaitByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/{rateName}/await/{awaitName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
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
            result_type=GetAwaitByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_await_by_user_id(
        self,
        request: GetAwaitByUserIdRequest,
    ) -> GetAwaitByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_await_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_await_by_user_id_async(
        self,
        request: GetAwaitByUserIdRequest,
    ) -> GetAwaitByUserIdResult:
        async_result = []
        self._get_await_by_user_id(
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

    def _acquire(
        self,
        request: AcquireRequest,
        callback: Callable[[AsyncResult[AcquireResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/exchange/{rateName}/await/{awaitName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire(
        self,
        request: AcquireRequest,
    ) -> AcquireResult:
        async_result = []
        with timeout(30):
            self._acquire(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_async(
        self,
        request: AcquireRequest,
    ) -> AcquireResult:
        async_result = []
        self._acquire(
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

    def _acquire_by_user_id(
        self,
        request: AcquireByUserIdRequest,
        callback: Callable[[AsyncResult[AcquireByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/{rateName}/await/{awaitName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_by_user_id(
        self,
        request: AcquireByUserIdRequest,
    ) -> AcquireByUserIdResult:
        async_result = []
        with timeout(30):
            self._acquire_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_by_user_id_async(
        self,
        request: AcquireByUserIdRequest,
    ) -> AcquireByUserIdResult:
        async_result = []
        self._acquire_by_user_id(
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

    def _acquire_force_by_user_id(
        self,
        request: AcquireForceByUserIdRequest,
        callback: Callable[[AsyncResult[AcquireForceByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/{rateName}/await/{awaitName}/force".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireForceByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_force_by_user_id(
        self,
        request: AcquireForceByUserIdRequest,
    ) -> AcquireForceByUserIdResult:
        async_result = []
        with timeout(30):
            self._acquire_force_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_force_by_user_id_async(
        self,
        request: AcquireForceByUserIdRequest,
    ) -> AcquireForceByUserIdResult:
        async_result = []
        self._acquire_force_by_user_id(
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

    def _skip(
        self,
        request: SkipRequest,
        callback: Callable[[AsyncResult[SkipResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/exchange/{rateName}/await/{awaitName}/skip".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=SkipResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def skip(
        self,
        request: SkipRequest,
    ) -> SkipResult:
        async_result = []
        with timeout(30):
            self._skip(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def skip_async(
        self,
        request: SkipRequest,
    ) -> SkipResult:
        async_result = []
        self._skip(
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

    def _skip_by_user_id(
        self,
        request: SkipByUserIdRequest,
        callback: Callable[[AsyncResult[SkipByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/{rateName}/await/{awaitName}/skip".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=SkipByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def skip_by_user_id(
        self,
        request: SkipByUserIdRequest,
    ) -> SkipByUserIdResult:
        async_result = []
        with timeout(30):
            self._skip_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def skip_by_user_id_async(
        self,
        request: SkipByUserIdRequest,
    ) -> SkipByUserIdResult:
        async_result = []
        self._skip_by_user_id(
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

    def _delete_await(
        self,
        request: DeleteAwaitRequest,
        callback: Callable[[AsyncResult[DeleteAwaitResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/exchange/{rateName}/await/{awaitName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
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
            result_type=DeleteAwaitResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_await(
        self,
        request: DeleteAwaitRequest,
    ) -> DeleteAwaitResult:
        async_result = []
        with timeout(30):
            self._delete_await(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_await_async(
        self,
        request: DeleteAwaitRequest,
    ) -> DeleteAwaitResult:
        async_result = []
        self._delete_await(
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

    def _delete_await_by_user_id(
        self,
        request: DeleteAwaitByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteAwaitByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/exchange/{rateName}/await/{awaitName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            awaitName=request.await_name if request.await_name is not None and request.await_name != '' else 'null',
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
            result_type=DeleteAwaitByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_await_by_user_id(
        self,
        request: DeleteAwaitByUserIdRequest,
    ) -> DeleteAwaitByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_await_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_await_by_user_id_async(
        self,
        request: DeleteAwaitByUserIdRequest,
    ) -> DeleteAwaitByUserIdResult:
        async_result = []
        self._delete_await_by_user_id(
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

    def _create_await_by_stamp_sheet(
        self,
        request: CreateAwaitByStampSheetRequest,
        callback: Callable[[AsyncResult[CreateAwaitByStampSheetResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/stamp/await/create"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateAwaitByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_await_by_stamp_sheet(
        self,
        request: CreateAwaitByStampSheetRequest,
    ) -> CreateAwaitByStampSheetResult:
        async_result = []
        with timeout(30):
            self._create_await_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_await_by_stamp_sheet_async(
        self,
        request: CreateAwaitByStampSheetRequest,
    ) -> CreateAwaitByStampSheetResult:
        async_result = []
        self._create_await_by_stamp_sheet(
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

    def _delete_await_by_stamp_task(
        self,
        request: DeleteAwaitByStampTaskRequest,
        callback: Callable[[AsyncResult[DeleteAwaitByStampTaskResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='exchange',
            region=self.session.region,
        ) + "/stamp/await/delete"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=DeleteAwaitByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_await_by_stamp_task(
        self,
        request: DeleteAwaitByStampTaskRequest,
    ) -> DeleteAwaitByStampTaskResult:
        async_result = []
        with timeout(30):
            self._delete_await_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_await_by_stamp_task_async(
        self,
        request: DeleteAwaitByStampTaskRequest,
    ) -> DeleteAwaitByStampTaskResult:
        async_result = []
        self._delete_await_by_stamp_task(
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