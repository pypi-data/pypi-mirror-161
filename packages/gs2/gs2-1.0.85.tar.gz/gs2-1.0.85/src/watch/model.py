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

import re
from typing import *
import core


class StatsEvent(core.Gs2Model):
    grn: str = None
    service: str = None
    method: str = None
    metric: str = None
    cumulative: bool = None
    value: float = None
    tags: List[str] = None
    call_at: int = None

    def with_grn(self, grn: str) -> StatsEvent:
        self.grn = grn
        return self

    def with_service(self, service: str) -> StatsEvent:
        self.service = service
        return self

    def with_method(self, method: str) -> StatsEvent:
        self.method = method
        return self

    def with_metric(self, metric: str) -> StatsEvent:
        self.metric = metric
        return self

    def with_cumulative(self, cumulative: bool) -> StatsEvent:
        self.cumulative = cumulative
        return self

    def with_value(self, value: float) -> StatsEvent:
        self.value = value
        return self

    def with_tags(self, tags: List[str]) -> StatsEvent:
        self.tags = tags
        return self

    def with_call_at(self, call_at: int) -> StatsEvent:
        self.call_at = call_at
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
    ) -> Optional[StatsEvent]:
        if data is None:
            return None
        return StatsEvent()\
            .with_grn(data.get('grn'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_metric(data.get('metric'))\
            .with_cumulative(data.get('cumulative'))\
            .with_value(data.get('value'))\
            .with_tags([
                data.get('tags')[i]
                for i in range(len(data.get('tags')) if data.get('tags') else 0)
            ])\
            .with_call_at(data.get('callAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grn": self.grn,
            "service": self.service,
            "method": self.method,
            "metric": self.metric,
            "cumulative": self.cumulative,
            "value": self.value,
            "tags": [
                self.tags[i]
                for i in range(len(self.tags) if self.tags else 0)
            ],
            "callAt": self.call_at,
        }


class BillingActivity(core.Gs2Model):
    billing_activity_id: str = None
    year: int = None
    month: int = None
    service: str = None
    activity_type: str = None
    value: int = None

    def with_billing_activity_id(self, billing_activity_id: str) -> BillingActivity:
        self.billing_activity_id = billing_activity_id
        return self

    def with_year(self, year: int) -> BillingActivity:
        self.year = year
        return self

    def with_month(self, month: int) -> BillingActivity:
        self.month = month
        return self

    def with_service(self, service: str) -> BillingActivity:
        self.service = service
        return self

    def with_activity_type(self, activity_type: str) -> BillingActivity:
        self.activity_type = activity_type
        return self

    def with_value(self, value: int) -> BillingActivity:
        self.value = value
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        year,
        month,
        service,
        activity_type,
    ):
        return 'grn:gs2:{region}:{ownerId}:watch:{year}:{month}:{service}:{activityType}'.format(
            region=region,
            ownerId=owner_id,
            year=year,
            month=month,
            service=service,
            activityType=activity_type,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<year>.+):(?P<month>.+):(?P<service>.+):(?P<activityType>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<year>.+):(?P<month>.+):(?P<service>.+):(?P<activityType>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_year_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<year>.+):(?P<month>.+):(?P<service>.+):(?P<activityType>.+)', grn)
        if match is None:
            return None
        return match.group('year')

    @classmethod
    def get_month_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<year>.+):(?P<month>.+):(?P<service>.+):(?P<activityType>.+)', grn)
        if match is None:
            return None
        return match.group('month')

    @classmethod
    def get_service_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<year>.+):(?P<month>.+):(?P<service>.+):(?P<activityType>.+)', grn)
        if match is None:
            return None
        return match.group('service')

    @classmethod
    def get_activity_type_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<year>.+):(?P<month>.+):(?P<service>.+):(?P<activityType>.+)', grn)
        if match is None:
            return None
        return match.group('activity_type')

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
    ) -> Optional[BillingActivity]:
        if data is None:
            return None
        return BillingActivity()\
            .with_billing_activity_id(data.get('billingActivityId'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_service(data.get('service'))\
            .with_activity_type(data.get('activityType'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "billingActivityId": self.billing_activity_id,
            "year": self.year,
            "month": self.month,
            "service": self.service,
            "activityType": self.activity_type,
            "value": self.value,
        }


class Cumulative(core.Gs2Model):
    cumulative_id: str = None
    resource_grn: str = None
    name: str = None
    value: int = None
    updated_at: int = None

    def with_cumulative_id(self, cumulative_id: str) -> Cumulative:
        self.cumulative_id = cumulative_id
        return self

    def with_resource_grn(self, resource_grn: str) -> Cumulative:
        self.resource_grn = resource_grn
        return self

    def with_name(self, name: str) -> Cumulative:
        self.name = name
        return self

    def with_value(self, value: int) -> Cumulative:
        self.value = value
        return self

    def with_updated_at(self, updated_at: int) -> Cumulative:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        resource_grn,
        name,
    ):
        return 'grn:gs2:{region}:{ownerId}:watch:{resourceGrn}:{name}'.format(
            region=region,
            ownerId=owner_id,
            resourceGrn=resource_grn,
            name=name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<resourceGrn>.+):(?P<name>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<resourceGrn>.+):(?P<name>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_resource_grn_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<resourceGrn>.+):(?P<name>.+)', grn)
        if match is None:
            return None
        return match.group('resource_grn')

    @classmethod
    def get_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):watch:(?P<resourceGrn>.+):(?P<name>.+)', grn)
        if match is None:
            return None
        return match.group('name')

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
    ) -> Optional[Cumulative]:
        if data is None:
            return None
        return Cumulative()\
            .with_cumulative_id(data.get('cumulativeId'))\
            .with_resource_grn(data.get('resourceGrn'))\
            .with_name(data.get('name'))\
            .with_value(data.get('value'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cumulativeId": self.cumulative_id,
            "resourceGrn": self.resource_grn,
            "name": self.name,
            "value": self.value,
            "updatedAt": self.updated_at,
        }


class Chart(core.Gs2Model):
    chart_id: str = None
    embed_id: str = None
    html: str = None

    def with_chart_id(self, chart_id: str) -> Chart:
        self.chart_id = chart_id
        return self

    def with_embed_id(self, embed_id: str) -> Chart:
        self.embed_id = embed_id
        return self

    def with_html(self, html: str) -> Chart:
        self.html = html
        return self

    @classmethod
    def create_grn(
        cls,
    ):
        return ''.format(
        )

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
    ) -> Optional[Chart]:
        if data is None:
            return None
        return Chart()\
            .with_chart_id(data.get('chartId'))\
            .with_embed_id(data.get('embedId'))\
            .with_html(data.get('html'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chartId": self.chart_id,
            "embedId": self.embed_id,
            "html": self.html,
        }