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

from __future__ import annotations

from watch.model import *


class GetChartRequest(core.Gs2Request):

    context_stack: str = None
    metrics: str = None
    grn: str = None
    queries: List[str] = None
    by: str = None
    timeframe: str = None
    size: str = None
    format: str = None
    aggregator: str = None
    style: str = None
    title: str = None

    def with_metrics(self, metrics: str) -> GetChartRequest:
        self.metrics = metrics
        return self

    def with_grn(self, grn: str) -> GetChartRequest:
        self.grn = grn
        return self

    def with_queries(self, queries: List[str]) -> GetChartRequest:
        self.queries = queries
        return self

    def with_by(self, by: str) -> GetChartRequest:
        self.by = by
        return self

    def with_timeframe(self, timeframe: str) -> GetChartRequest:
        self.timeframe = timeframe
        return self

    def with_size(self, size: str) -> GetChartRequest:
        self.size = size
        return self

    def with_format(self, format: str) -> GetChartRequest:
        self.format = format
        return self

    def with_aggregator(self, aggregator: str) -> GetChartRequest:
        self.aggregator = aggregator
        return self

    def with_style(self, style: str) -> GetChartRequest:
        self.style = style
        return self

    def with_title(self, title: str) -> GetChartRequest:
        self.title = title
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetChartRequest]:
        if data is None:
            return None
        return GetChartRequest()\
            .with_metrics(data.get('metrics'))\
            .with_grn(data.get('grn'))\
            .with_queries([
                data.get('queries')[i]
                for i in range(len(data.get('queries')) if data.get('queries') else 0)
            ])\
            .with_by(data.get('by'))\
            .with_timeframe(data.get('timeframe'))\
            .with_size(data.get('size'))\
            .with_format(data.get('format'))\
            .with_aggregator(data.get('aggregator'))\
            .with_style(data.get('style'))\
            .with_title(data.get('title'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics,
            "grn": self.grn,
            "queries": [
                self.queries[i]
                for i in range(len(self.queries) if self.queries else 0)
            ],
            "by": self.by,
            "timeframe": self.timeframe,
            "size": self.size,
            "format": self.format,
            "aggregator": self.aggregator,
            "style": self.style,
            "title": self.title,
        }


class GetCumulativeRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    resource_grn: str = None

    def with_name(self, name: str) -> GetCumulativeRequest:
        self.name = name
        return self

    def with_resource_grn(self, resource_grn: str) -> GetCumulativeRequest:
        self.resource_grn = resource_grn
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCumulativeRequest]:
        if data is None:
            return None
        return GetCumulativeRequest()\
            .with_name(data.get('name'))\
            .with_resource_grn(data.get('resourceGrn'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "resourceGrn": self.resource_grn,
        }


class DescribeBillingActivitiesRequest(core.Gs2Request):

    context_stack: str = None
    year: int = None
    month: int = None
    service: str = None
    page_token: str = None
    limit: int = None

    def with_year(self, year: int) -> DescribeBillingActivitiesRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> DescribeBillingActivitiesRequest:
        self.month = month
        return self

    def with_service(self, service: str) -> DescribeBillingActivitiesRequest:
        self.service = service
        return self

    def with_page_token(self, page_token: str) -> DescribeBillingActivitiesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBillingActivitiesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeBillingActivitiesRequest]:
        if data is None:
            return None
        return DescribeBillingActivitiesRequest()\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_service(data.get('service'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "service": self.service,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetBillingActivityRequest(core.Gs2Request):

    context_stack: str = None
    year: int = None
    month: int = None
    service: str = None
    activity_type: str = None

    def with_year(self, year: int) -> GetBillingActivityRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> GetBillingActivityRequest:
        self.month = month
        return self

    def with_service(self, service: str) -> GetBillingActivityRequest:
        self.service = service
        return self

    def with_activity_type(self, activity_type: str) -> GetBillingActivityRequest:
        self.activity_type = activity_type
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetBillingActivityRequest]:
        if data is None:
            return None
        return GetBillingActivityRequest()\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_service(data.get('service'))\
            .with_activity_type(data.get('activityType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "service": self.service,
            "activityType": self.activity_type,
        }