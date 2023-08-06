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
from enhance.request import *
from enhance.result import *


class Gs2EnhanceRestClient(AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
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
            service='enhance',
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
        if request.enable_direct_enhance is not None:
            body["enableDirectEnhance"] = request.enable_direct_enhance
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
        if request.enhance_script is not None:
            body["enhanceScript"] = request.enhance_script.to_dict()
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
            service='enhance',
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
            service='enhance',
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
            service='enhance',
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
        if request.enable_direct_enhance is not None:
            body["enableDirectEnhance"] = request.enable_direct_enhance
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
        if request.enhance_script is not None:
            body["enhanceScript"] = request.enhance_script.to_dict()
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
            service='enhance',
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
            service='enhance',
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
            service='enhance',
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
            service='enhance',
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
            service='enhance',
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
        if request.target_inventory_model_id is not None:
            body["targetInventoryModelId"] = request.target_inventory_model_id
        if request.acquire_experience_suffix is not None:
            body["acquireExperienceSuffix"] = request.acquire_experience_suffix
        if request.material_inventory_model_id is not None:
            body["materialInventoryModelId"] = request.material_inventory_model_id
        if request.acquire_experience_hierarchy is not None:
            body["acquireExperienceHierarchy"] = [
                item
                for item in request.acquire_experience_hierarchy
            ]
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.bonus_rates is not None:
            body["bonusRates"] = [
                item.to_dict()
                for item in request.bonus_rates
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
            service='enhance',
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
            service='enhance',
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
        if request.target_inventory_model_id is not None:
            body["targetInventoryModelId"] = request.target_inventory_model_id
        if request.acquire_experience_suffix is not None:
            body["acquireExperienceSuffix"] = request.acquire_experience_suffix
        if request.material_inventory_model_id is not None:
            body["materialInventoryModelId"] = request.material_inventory_model_id
        if request.acquire_experience_hierarchy is not None:
            body["acquireExperienceHierarchy"] = [
                item
                for item in request.acquire_experience_hierarchy
            ]
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.bonus_rates is not None:
            body["bonusRates"] = [
                item.to_dict()
                for item in request.bonus_rates
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
            service='enhance',
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

    def _direct_enhance(
        self,
        request: DirectEnhanceRequest,
        callback: Callable[[AsyncResult[DirectEnhanceResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/enhance/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.target_item_set_id is not None:
            body["targetItemSetId"] = request.target_item_set_id
        if request.materials is not None:
            body["materials"] = [
                item.to_dict()
                for item in request.materials
            ]
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
            result_type=DirectEnhanceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def direct_enhance(
        self,
        request: DirectEnhanceRequest,
    ) -> DirectEnhanceResult:
        async_result = []
        with timeout(30):
            self._direct_enhance(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def direct_enhance_async(
        self,
        request: DirectEnhanceRequest,
    ) -> DirectEnhanceResult:
        async_result = []
        self._direct_enhance(
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

    def _direct_enhance_by_user_id(
        self,
        request: DirectEnhanceByUserIdRequest,
        callback: Callable[[AsyncResult[DirectEnhanceByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/enhance/{rateName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.target_item_set_id is not None:
            body["targetItemSetId"] = request.target_item_set_id
        if request.materials is not None:
            body["materials"] = [
                item.to_dict()
                for item in request.materials
            ]
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
            result_type=DirectEnhanceByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def direct_enhance_by_user_id(
        self,
        request: DirectEnhanceByUserIdRequest,
    ) -> DirectEnhanceByUserIdResult:
        async_result = []
        with timeout(30):
            self._direct_enhance_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def direct_enhance_by_user_id_async(
        self,
        request: DirectEnhanceByUserIdRequest,
    ) -> DirectEnhanceByUserIdResult:
        async_result = []
        self._direct_enhance_by_user_id(
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

    def _direct_enhance_by_stamp_sheet(
        self,
        request: DirectEnhanceByStampSheetRequest,
        callback: Callable[[AsyncResult[DirectEnhanceByStampSheetResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/stamp/enhance/direct"

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
            result_type=DirectEnhanceByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def direct_enhance_by_stamp_sheet(
        self,
        request: DirectEnhanceByStampSheetRequest,
    ) -> DirectEnhanceByStampSheetResult:
        async_result = []
        with timeout(30):
            self._direct_enhance_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def direct_enhance_by_stamp_sheet_async(
        self,
        request: DirectEnhanceByStampSheetRequest,
    ) -> DirectEnhanceByStampSheetResult:
        async_result = []
        self._direct_enhance_by_stamp_sheet(
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

    def _describe_progresses_by_user_id(
        self,
        request: DescribeProgressesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeProgressesByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/progress".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeProgressesByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_progresses_by_user_id(
        self,
        request: DescribeProgressesByUserIdRequest,
    ) -> DescribeProgressesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_progresses_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_progresses_by_user_id_async(
        self,
        request: DescribeProgressesByUserIdRequest,
    ) -> DescribeProgressesByUserIdResult:
        async_result = []
        self._describe_progresses_by_user_id(
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

    def _create_progress_by_user_id(
        self,
        request: CreateProgressByUserIdRequest,
        callback: Callable[[AsyncResult[CreateProgressByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/progress".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.rate_name is not None:
            body["rateName"] = request.rate_name
        if request.target_item_set_id is not None:
            body["targetItemSetId"] = request.target_item_set_id
        if request.materials is not None:
            body["materials"] = [
                item.to_dict()
                for item in request.materials
            ]
        if request.force is not None:
            body["force"] = request.force

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateProgressByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_progress_by_user_id(
        self,
        request: CreateProgressByUserIdRequest,
    ) -> CreateProgressByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_progress_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_progress_by_user_id_async(
        self,
        request: CreateProgressByUserIdRequest,
    ) -> CreateProgressByUserIdResult:
        async_result = []
        self._create_progress_by_user_id(
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

    def _get_progress(
        self,
        request: GetProgressRequest,
        callback: Callable[[AsyncResult[GetProgressResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/progress/{rateName}/progress/{progressName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            progressName=request.progress_name if request.progress_name is not None and request.progress_name != '' else 'null',
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
            result_type=GetProgressResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_progress(
        self,
        request: GetProgressRequest,
    ) -> GetProgressResult:
        async_result = []
        with timeout(30):
            self._get_progress(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_progress_async(
        self,
        request: GetProgressRequest,
    ) -> GetProgressResult:
        async_result = []
        self._get_progress(
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

    def _get_progress_by_user_id(
        self,
        request: GetProgressByUserIdRequest,
        callback: Callable[[AsyncResult[GetProgressByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/progress/{rateName}/progress/{progressName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            progressName=request.progress_name if request.progress_name is not None and request.progress_name != '' else 'null',
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
            result_type=GetProgressByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_progress_by_user_id(
        self,
        request: GetProgressByUserIdRequest,
    ) -> GetProgressByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_progress_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_progress_by_user_id_async(
        self,
        request: GetProgressByUserIdRequest,
    ) -> GetProgressByUserIdResult:
        async_result = []
        self._get_progress_by_user_id(
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

    def _start(
        self,
        request: StartRequest,
        callback: Callable[[AsyncResult[StartResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/progress/rate/{rateName}/start".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.target_item_set_id is not None:
            body["targetItemSetId"] = request.target_item_set_id
        if request.materials is not None:
            body["materials"] = [
                item.to_dict()
                for item in request.materials
            ]
        if request.force is not None:
            body["force"] = request.force
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
            result_type=StartResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def start(
        self,
        request: StartRequest,
    ) -> StartResult:
        async_result = []
        with timeout(30):
            self._start(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def start_async(
        self,
        request: StartRequest,
    ) -> StartResult:
        async_result = []
        self._start(
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

    def _start_by_user_id(
        self,
        request: StartByUserIdRequest,
        callback: Callable[[AsyncResult[StartByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/progress/rate/{rateName}/start".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.target_item_set_id is not None:
            body["targetItemSetId"] = request.target_item_set_id
        if request.materials is not None:
            body["materials"] = [
                item.to_dict()
                for item in request.materials
            ]
        if request.force is not None:
            body["force"] = request.force
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
            result_type=StartByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def start_by_user_id(
        self,
        request: StartByUserIdRequest,
    ) -> StartByUserIdResult:
        async_result = []
        with timeout(30):
            self._start_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def start_by_user_id_async(
        self,
        request: StartByUserIdRequest,
    ) -> StartByUserIdResult:
        async_result = []
        self._start_by_user_id(
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

    def _end(
        self,
        request: EndRequest,
        callback: Callable[[AsyncResult[EndResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/progress/rate/{rateName}/progress/{progressName}/end".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            progressName=request.progress_name if request.progress_name is not None and request.progress_name != '' else 'null',
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
            result_type=EndResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def end(
        self,
        request: EndRequest,
    ) -> EndResult:
        async_result = []
        with timeout(30):
            self._end(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def end_async(
        self,
        request: EndRequest,
    ) -> EndResult:
        async_result = []
        self._end(
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

    def _end_by_user_id(
        self,
        request: EndByUserIdRequest,
        callback: Callable[[AsyncResult[EndByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/progress/rate/{rateName}/progress/{progressName}/end".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            progressName=request.progress_name if request.progress_name is not None and request.progress_name != '' else 'null',
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
            result_type=EndByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def end_by_user_id(
        self,
        request: EndByUserIdRequest,
    ) -> EndByUserIdResult:
        async_result = []
        with timeout(30):
            self._end_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def end_by_user_id_async(
        self,
        request: EndByUserIdRequest,
    ) -> EndByUserIdResult:
        async_result = []
        self._end_by_user_id(
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

    def _delete_progress(
        self,
        request: DeleteProgressRequest,
        callback: Callable[[AsyncResult[DeleteProgressResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/progress/rate/{rateName}/progress/{progressName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            progressName=request.progress_name if request.progress_name is not None and request.progress_name != '' else 'null',
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
            result_type=DeleteProgressResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_progress(
        self,
        request: DeleteProgressRequest,
    ) -> DeleteProgressResult:
        async_result = []
        with timeout(30):
            self._delete_progress(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_progress_async(
        self,
        request: DeleteProgressRequest,
    ) -> DeleteProgressResult:
        async_result = []
        self._delete_progress(
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

    def _delete_progress_by_user_id(
        self,
        request: DeleteProgressByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteProgressByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/progress/rate/{rateName}/progress/{progressName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rateName=request.rate_name if request.rate_name is not None and request.rate_name != '' else 'null',
            progressName=request.progress_name if request.progress_name is not None and request.progress_name != '' else 'null',
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
            result_type=DeleteProgressByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_progress_by_user_id(
        self,
        request: DeleteProgressByUserIdRequest,
    ) -> DeleteProgressByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_progress_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_progress_by_user_id_async(
        self,
        request: DeleteProgressByUserIdRequest,
    ) -> DeleteProgressByUserIdResult:
        async_result = []
        self._delete_progress_by_user_id(
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

    def _create_progress_by_stamp_sheet(
        self,
        request: CreateProgressByStampSheetRequest,
        callback: Callable[[AsyncResult[CreateProgressByStampSheetResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/stamp/progress/create"

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
            result_type=CreateProgressByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_progress_by_stamp_sheet(
        self,
        request: CreateProgressByStampSheetRequest,
    ) -> CreateProgressByStampSheetResult:
        async_result = []
        with timeout(30):
            self._create_progress_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_progress_by_stamp_sheet_async(
        self,
        request: CreateProgressByStampSheetRequest,
    ) -> CreateProgressByStampSheetResult:
        async_result = []
        self._create_progress_by_stamp_sheet(
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

    def _delete_progress_by_stamp_task(
        self,
        request: DeleteProgressByStampTaskRequest,
        callback: Callable[[AsyncResult[DeleteProgressByStampTaskResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enhance',
            region=self.session.region,
        ) + "/stamp/progress/delete"

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
            result_type=DeleteProgressByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_progress_by_stamp_task(
        self,
        request: DeleteProgressByStampTaskRequest,
    ) -> DeleteProgressByStampTaskResult:
        async_result = []
        with timeout(30):
            self._delete_progress_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_progress_by_stamp_task_async(
        self,
        request: DeleteProgressByStampTaskRequest,
    ) -> DeleteProgressByStampTaskResult:
        async_result = []
        self._delete_progress_by_stamp_task(
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
            service='enhance',
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
            service='enhance',
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
            service='enhance',
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
            service='enhance',
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