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
from watch.request import *
from watch.result import *


class Gs2WatchRestClient(AbstractGs2RestClient):

    def _get_chart(
        self,
        request: GetChartRequest,
        callback: Callable[[AsyncResult[GetChartResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='watch',
            region=self.session.region,
        ) + "/chart/{metrics}".format(
            metrics=request.metrics if request.metrics is not None and request.metrics != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.grn is not None:
            body["grn"] = request.grn
        if request.queries is not None:
            body["queries"] = [
                item
                for item in request.queries
            ]
        if request.by is not None:
            body["by"] = request.by
        if request.timeframe is not None:
            body["timeframe"] = request.timeframe
        if request.size is not None:
            body["size"] = request.size
        if request.format is not None:
            body["format"] = request.format
        if request.aggregator is not None:
            body["aggregator"] = request.aggregator
        if request.style is not None:
            body["style"] = request.style
        if request.title is not None:
            body["title"] = request.title

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=GetChartResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_chart(
        self,
        request: GetChartRequest,
    ) -> GetChartResult:
        async_result = []
        with timeout(30):
            self._get_chart(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_chart_async(
        self,
        request: GetChartRequest,
    ) -> GetChartResult:
        async_result = []
        self._get_chart(
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

    def _get_cumulative(
        self,
        request: GetCumulativeRequest,
        callback: Callable[[AsyncResult[GetCumulativeResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='watch',
            region=self.session.region,
        ) + "/cumulative/{name}".format(
            name=request.name if request.name is not None and request.name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.resource_grn is not None:
            body["resourceGrn"] = request.resource_grn

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='POST',
            result_type=GetCumulativeResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_cumulative(
        self,
        request: GetCumulativeRequest,
    ) -> GetCumulativeResult:
        async_result = []
        with timeout(30):
            self._get_cumulative(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cumulative_async(
        self,
        request: GetCumulativeRequest,
    ) -> GetCumulativeResult:
        async_result = []
        self._get_cumulative(
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

    def _describe_billing_activities(
        self,
        request: DescribeBillingActivitiesRequest,
        callback: Callable[[AsyncResult[DescribeBillingActivitiesResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='watch',
            region=self.session.region,
        ) + "/billingActivity/{year}/{month}".format(
            year=request.year if request.year is not None and request.year != '' else 'null',
            month=request.month if request.month is not None and request.month != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeBillingActivitiesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_billing_activities(
        self,
        request: DescribeBillingActivitiesRequest,
    ) -> DescribeBillingActivitiesResult:
        async_result = []
        with timeout(30):
            self._describe_billing_activities(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_billing_activities_async(
        self,
        request: DescribeBillingActivitiesRequest,
    ) -> DescribeBillingActivitiesResult:
        async_result = []
        self._describe_billing_activities(
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

    def _get_billing_activity(
        self,
        request: GetBillingActivityRequest,
        callback: Callable[[AsyncResult[GetBillingActivityResult]], None],
        is_blocking: bool,
    ):
        url = Gs2Constant.ENDPOINT_HOST.format(
            service='watch',
            region=self.session.region,
        ) + "/billingActivity/{year}/{month}/{service}/{activityType}".format(
            year=request.year if request.year is not None and request.year != '' else 'null',
            month=request.month if request.month is not None and request.month != '' else 'null',
            service=request.service if request.service is not None and request.service != '' else 'null',
            activityType=request.activity_type if request.activity_type is not None and request.activity_type != '' else 'null',
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
            result_type=GetBillingActivityResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_billing_activity(
        self,
        request: GetBillingActivityRequest,
    ) -> GetBillingActivityResult:
        async_result = []
        with timeout(30):
            self._get_billing_activity(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_billing_activity_async(
        self,
        request: GetBillingActivityRequest,
    ) -> GetBillingActivityResult:
        async_result = []
        self._get_billing_activity(
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