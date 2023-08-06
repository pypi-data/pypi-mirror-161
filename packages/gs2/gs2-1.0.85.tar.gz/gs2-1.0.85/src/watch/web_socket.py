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
from watch.request import *
from watch.result import *


class Gs2WatchWebSocketClient(AbstractGs2WebSocketClient):

    def _get_chart(
        self,
        request: GetChartRequest,
        callback: Callable[[AsyncResult[GetChartResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="watch",
            component='chart',
            function='getChart',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.metrics is not None:
            body["metrics"] = request.metrics
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
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetChartResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="watch",
            component='cumulative',
            function='getCumulative',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.resource_grn is not None:
            body["resourceGrn"] = request.resource_grn

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetCumulativeResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="watch",
            component='billingActivity',
            function='describeBillingActivities',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.service is not None:
            body["service"] = request.service
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeBillingActivitiesResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="watch",
            component='billingActivity',
            function='getBillingActivity',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.service is not None:
            body["service"] = request.service
        if request.activity_type is not None:
            body["activityType"] = request.activity_type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetBillingActivityResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result