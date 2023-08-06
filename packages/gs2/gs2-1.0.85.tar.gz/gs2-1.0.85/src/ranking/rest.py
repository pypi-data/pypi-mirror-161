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
from ranking.request import *
from ranking.result import *


class Gs2RankingRestClient(AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
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
            service='ranking',
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
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

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
            service='ranking',
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
            service='ranking',
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
            service='ranking',
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
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

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
            service='ranking',
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

    def _describe_category_models(
        self,
        request: DescribeCategoryModelsRequest,
        callback: Callable[[AsyncResult[DescribeCategoryModelsResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/category".format(
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
            result_type=DescribeCategoryModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_category_models(
        self,
        request: DescribeCategoryModelsRequest,
    ) -> DescribeCategoryModelsResult:
        async_result = []
        with timeout(30):
            self._describe_category_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_category_models_async(
        self,
        request: DescribeCategoryModelsRequest,
    ) -> DescribeCategoryModelsResult:
        async_result = []
        self._describe_category_models(
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

    def _get_category_model(
        self,
        request: GetCategoryModelRequest,
        callback: Callable[[AsyncResult[GetCategoryModelResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/category/{categoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
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
            result_type=GetCategoryModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_category_model(
        self,
        request: GetCategoryModelRequest,
    ) -> GetCategoryModelResult:
        async_result = []
        with timeout(30):
            self._get_category_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_category_model_async(
        self,
        request: GetCategoryModelRequest,
    ) -> GetCategoryModelResult:
        async_result = []
        self._get_category_model(
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

    def _describe_category_model_masters(
        self,
        request: DescribeCategoryModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeCategoryModelMastersResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/master/category".format(
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
            result_type=DescribeCategoryModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_category_model_masters(
        self,
        request: DescribeCategoryModelMastersRequest,
    ) -> DescribeCategoryModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_category_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_category_model_masters_async(
        self,
        request: DescribeCategoryModelMastersRequest,
    ) -> DescribeCategoryModelMastersResult:
        async_result = []
        self._describe_category_model_masters(
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

    def _create_category_model_master(
        self,
        request: CreateCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[CreateCategoryModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/master/category".format(
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
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.scope is not None:
            body["scope"] = request.scope
        if request.unique_by_user_id is not None:
            body["uniqueByUserId"] = request.unique_by_user_id
        if request.calculate_fixed_timing_hour is not None:
            body["calculateFixedTimingHour"] = request.calculate_fixed_timing_hour
        if request.calculate_fixed_timing_minute is not None:
            body["calculateFixedTimingMinute"] = request.calculate_fixed_timing_minute
        if request.calculate_interval_minutes is not None:
            body["calculateIntervalMinutes"] = request.calculate_interval_minutes
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id
        if request.generation is not None:
            body["generation"] = request.generation

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CreateCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_category_model_master(
        self,
        request: CreateCategoryModelMasterRequest,
    ) -> CreateCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_category_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_category_model_master_async(
        self,
        request: CreateCategoryModelMasterRequest,
    ) -> CreateCategoryModelMasterResult:
        async_result = []
        self._create_category_model_master(
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

    def _get_category_model_master(
        self,
        request: GetCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[GetCategoryModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/master/category/{categoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
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
            result_type=GetCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_category_model_master(
        self,
        request: GetCategoryModelMasterRequest,
    ) -> GetCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_category_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_category_model_master_async(
        self,
        request: GetCategoryModelMasterRequest,
    ) -> GetCategoryModelMasterResult:
        async_result = []
        self._get_category_model_master(
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

    def _update_category_model_master(
        self,
        request: UpdateCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateCategoryModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/master/category/{categoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.scope is not None:
            body["scope"] = request.scope
        if request.unique_by_user_id is not None:
            body["uniqueByUserId"] = request.unique_by_user_id
        if request.calculate_fixed_timing_hour is not None:
            body["calculateFixedTimingHour"] = request.calculate_fixed_timing_hour
        if request.calculate_fixed_timing_minute is not None:
            body["calculateFixedTimingMinute"] = request.calculate_fixed_timing_minute
        if request.calculate_interval_minutes is not None:
            body["calculateIntervalMinutes"] = request.calculate_interval_minutes
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id
        if request.generation is not None:
            body["generation"] = request.generation

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_category_model_master(
        self,
        request: UpdateCategoryModelMasterRequest,
    ) -> UpdateCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_category_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_category_model_master_async(
        self,
        request: UpdateCategoryModelMasterRequest,
    ) -> UpdateCategoryModelMasterResult:
        async_result = []
        self._update_category_model_master(
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

    def _delete_category_model_master(
        self,
        request: DeleteCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteCategoryModelMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/master/category/{categoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
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
            result_type=DeleteCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_category_model_master(
        self,
        request: DeleteCategoryModelMasterRequest,
    ) -> DeleteCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_category_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_category_model_master_async(
        self,
        request: DeleteCategoryModelMasterRequest,
    ) -> DeleteCategoryModelMasterResult:
        async_result = []
        self._delete_category_model_master(
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

    def _subscribe(
        self,
        request: SubscribeRequest,
        callback: Callable[[AsyncResult[SubscribeResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/category/{categoryName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=SubscribeResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/category/{categoryName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=SubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_scores(
        self,
        request: DescribeScoresRequest,
        callback: Callable[[AsyncResult[DescribeScoresResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/category/{categoryName}/scorer/{scorerUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            scorerUserId=request.scorer_user_id if request.scorer_user_id is not None and request.scorer_user_id != '' else 'null',
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
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeScoresResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_scores(
        self,
        request: DescribeScoresRequest,
    ) -> DescribeScoresResult:
        async_result = []
        with timeout(30):
            self._describe_scores(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_scores_async(
        self,
        request: DescribeScoresRequest,
    ) -> DescribeScoresResult:
        async_result = []
        self._describe_scores(
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

    def _describe_scores_by_user_id(
        self,
        request: DescribeScoresByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeScoresByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/category/{categoryName}/scorer/{scorerUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            scorerUserId=request.scorer_user_id if request.scorer_user_id is not None and request.scorer_user_id != '' else 'null',
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
            result_type=DescribeScoresByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_scores_by_user_id(
        self,
        request: DescribeScoresByUserIdRequest,
    ) -> DescribeScoresByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_scores_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_scores_by_user_id_async(
        self,
        request: DescribeScoresByUserIdRequest,
    ) -> DescribeScoresByUserIdResult:
        async_result = []
        self._describe_scores_by_user_id(
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

    def _get_score(
        self,
        request: GetScoreRequest,
        callback: Callable[[AsyncResult[GetScoreResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/category/{categoryName}/scorer/{scorerUserId}/score/{uniqueId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            scorerUserId=request.scorer_user_id if request.scorer_user_id is not None and request.scorer_user_id != '' else 'null',
            uniqueId=request.unique_id if request.unique_id is not None and request.unique_id != '' else 'null',
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
            result_type=GetScoreResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_score(
        self,
        request: GetScoreRequest,
    ) -> GetScoreResult:
        async_result = []
        with timeout(30):
            self._get_score(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_score_async(
        self,
        request: GetScoreRequest,
    ) -> GetScoreResult:
        async_result = []
        self._get_score(
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

    def _get_score_by_user_id(
        self,
        request: GetScoreByUserIdRequest,
        callback: Callable[[AsyncResult[GetScoreByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/category/{categoryName}/scorer/{scorerUserId}/score/{uniqueId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            scorerUserId=request.scorer_user_id if request.scorer_user_id is not None and request.scorer_user_id != '' else 'null',
            uniqueId=request.unique_id if request.unique_id is not None and request.unique_id != '' else 'null',
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
            result_type=GetScoreByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_score_by_user_id(
        self,
        request: GetScoreByUserIdRequest,
    ) -> GetScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_score_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_score_by_user_id_async(
        self,
        request: GetScoreByUserIdRequest,
    ) -> GetScoreByUserIdResult:
        async_result = []
        self._get_score_by_user_id(
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

    def _describe_rankings(
        self,
        request: DescribeRankingsRequest,
        callback: Callable[[AsyncResult[DescribeRankingsResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/category/{categoryName}/ranking".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.start_index is not None:
            query_strings["startIndex"] = request.start_index
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
            result_type=DescribeRankingsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_rankings(
        self,
        request: DescribeRankingsRequest,
    ) -> DescribeRankingsResult:
        async_result = []
        with timeout(30):
            self._describe_rankings(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rankings_async(
        self,
        request: DescribeRankingsRequest,
    ) -> DescribeRankingsResult:
        async_result = []
        self._describe_rankings(
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

    def _describe_rankingss_by_user_id(
        self,
        request: DescribeRankingssByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeRankingssByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/category/{categoryName}/ranking".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.start_index is not None:
            query_strings["startIndex"] = request.start_index
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeRankingssByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_rankingss_by_user_id(
        self,
        request: DescribeRankingssByUserIdRequest,
    ) -> DescribeRankingssByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_rankingss_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rankingss_by_user_id_async(
        self,
        request: DescribeRankingssByUserIdRequest,
    ) -> DescribeRankingssByUserIdResult:
        async_result = []
        self._describe_rankingss_by_user_id(
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

    def _describe_near_rankings(
        self,
        request: DescribeNearRankingsRequest,
        callback: Callable[[AsyncResult[DescribeNearRankingsResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/category/{categoryName}/ranking/near".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            query_strings["score"] = request.score

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeNearRankingsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_near_rankings(
        self,
        request: DescribeNearRankingsRequest,
    ) -> DescribeNearRankingsResult:
        async_result = []
        with timeout(30):
            self._describe_near_rankings(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_near_rankings_async(
        self,
        request: DescribeNearRankingsRequest,
    ) -> DescribeNearRankingsResult:
        async_result = []
        self._describe_near_rankings(
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

    def _get_ranking(
        self,
        request: GetRankingRequest,
        callback: Callable[[AsyncResult[GetRankingResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/category/{categoryName}/ranking/scorer/{scorerUserId}/score/{uniqueId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            scorerUserId=request.scorer_user_id if request.scorer_user_id is not None and request.scorer_user_id != '' else 'null',
            uniqueId=request.unique_id if request.unique_id is not None and request.unique_id != '' else 'null',
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
            result_type=GetRankingResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_ranking(
        self,
        request: GetRankingRequest,
    ) -> GetRankingResult:
        async_result = []
        with timeout(30):
            self._get_ranking(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_ranking_async(
        self,
        request: GetRankingRequest,
    ) -> GetRankingResult:
        async_result = []
        self._get_ranking(
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

    def _get_ranking_by_user_id(
        self,
        request: GetRankingByUserIdRequest,
        callback: Callable[[AsyncResult[GetRankingByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/category/{categoryName}/ranking/scorer/{scorerUserId}/score/{uniqueId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            scorerUserId=request.scorer_user_id if request.scorer_user_id is not None and request.scorer_user_id != '' else 'null',
            uniqueId=request.unique_id if request.unique_id is not None and request.unique_id != '' else 'null',
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
            result_type=GetRankingByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_ranking_by_user_id(
        self,
        request: GetRankingByUserIdRequest,
    ) -> GetRankingByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_ranking_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_ranking_by_user_id_async(
        self,
        request: GetRankingByUserIdRequest,
    ) -> GetRankingByUserIdResult:
        async_result = []
        self._get_ranking_by_user_id(
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

    def _put_score(
        self,
        request: PutScoreRequest,
        callback: Callable[[AsyncResult[PutScoreResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/category/{categoryName}/ranking".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=PutScoreResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def put_score(
        self,
        request: PutScoreRequest,
    ) -> PutScoreResult:
        async_result = []
        with timeout(30):
            self._put_score(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_score_async(
        self,
        request: PutScoreRequest,
    ) -> PutScoreResult:
        async_result = []
        self._put_score(
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

    def _put_score_by_user_id(
        self,
        request: PutScoreByUserIdRequest,
        callback: Callable[[AsyncResult[PutScoreByUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/category/{categoryName}/ranking".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='PUT',
            result_type=PutScoreByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def put_score_by_user_id(
        self,
        request: PutScoreByUserIdRequest,
    ) -> PutScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._put_score_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_score_by_user_id_async(
        self,
        request: PutScoreByUserIdRequest,
    ) -> PutScoreByUserIdResult:
        async_result = []
        self._put_score_by_user_id(
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

    def _calc_ranking(
        self,
        request: CalcRankingRequest,
        callback: Callable[[AsyncResult[CalcRankingResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/category/{categoryName}/calc/ranking".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=CalcRankingResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def calc_ranking(
        self,
        request: CalcRankingRequest,
    ) -> CalcRankingResult:
        async_result = []
        with timeout(30):
            self._calc_ranking(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def calc_ranking_async(
        self,
        request: CalcRankingRequest,
    ) -> CalcRankingResult:
        async_result = []
        self._calc_ranking(
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
            service='ranking',
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

    def _get_current_ranking_master(
        self,
        request: GetCurrentRankingMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentRankingMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
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
            result_type=GetCurrentRankingMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_current_ranking_master(
        self,
        request: GetCurrentRankingMasterRequest,
    ) -> GetCurrentRankingMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_ranking_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_ranking_master_async(
        self,
        request: GetCurrentRankingMasterRequest,
    ) -> GetCurrentRankingMasterResult:
        async_result = []
        self._get_current_ranking_master(
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

    def _update_current_ranking_master(
        self,
        request: UpdateCurrentRankingMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRankingMasterResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
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
            result_type=UpdateCurrentRankingMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_ranking_master(
        self,
        request: UpdateCurrentRankingMasterRequest,
    ) -> UpdateCurrentRankingMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_ranking_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_ranking_master_async(
        self,
        request: UpdateCurrentRankingMasterRequest,
    ) -> UpdateCurrentRankingMasterResult:
        async_result = []
        self._update_current_ranking_master(
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

    def _update_current_ranking_master_from_git_hub(
        self,
        request: UpdateCurrentRankingMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRankingMasterFromGitHubResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
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
            result_type=UpdateCurrentRankingMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_ranking_master_from_git_hub(
        self,
        request: UpdateCurrentRankingMasterFromGitHubRequest,
    ) -> UpdateCurrentRankingMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_ranking_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_ranking_master_from_git_hub_async(
        self,
        request: UpdateCurrentRankingMasterFromGitHubRequest,
    ) -> UpdateCurrentRankingMasterFromGitHubResult:
        async_result = []
        self._update_current_ranking_master_from_git_hub(
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

    def _get_subscribe(
        self,
        request: GetSubscribeRequest,
        callback: Callable[[AsyncResult[GetSubscribeResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/category/{categoryName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            result_type=GetSubscribeResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/category/{categoryName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            result_type=GetSubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/category/{categoryName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            result_type=UnsubscribeResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/category/{categoryName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            result_type=UnsubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribes_by_category_name(
        self,
        request: DescribeSubscribesByCategoryNameRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesByCategoryNameResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/category/{categoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
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
            result_type=DescribeSubscribesByCategoryNameResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_subscribes_by_category_name(
        self,
        request: DescribeSubscribesByCategoryNameRequest,
    ) -> DescribeSubscribesByCategoryNameResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes_by_category_name(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_by_category_name_async(
        self,
        request: DescribeSubscribesByCategoryNameRequest,
    ) -> DescribeSubscribesByCategoryNameResult:
        async_result = []
        self._describe_subscribes_by_category_name(
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

    def _describe_subscribes_by_category_name_and_user_id(
        self,
        request: DescribeSubscribesByCategoryNameAndUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesByCategoryNameAndUserIdResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/category/{categoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            categoryName=request.category_name if request.category_name is not None and request.category_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
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
            result_type=DescribeSubscribesByCategoryNameAndUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_subscribes_by_category_name_and_user_id(
        self,
        request: DescribeSubscribesByCategoryNameAndUserIdRequest,
    ) -> DescribeSubscribesByCategoryNameAndUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes_by_category_name_and_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_by_category_name_and_user_id_async(
        self,
        request: DescribeSubscribesByCategoryNameAndUserIdRequest,
    ) -> DescribeSubscribesByCategoryNameAndUserIdResult:
        async_result = []
        self._describe_subscribes_by_category_name_and_user_id(
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