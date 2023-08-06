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


class Billing(core.Gs2Model):
    billing_id: str = None
    project_name: str = None
    year: int = None
    month: int = None
    region: str = None
    service: str = None
    activity_type: str = None
    unit: float = None
    unit_name: str = None
    price: int = None
    currency: str = None
    created_at: int = None
    updated_at: int = None

    def with_billing_id(self, billing_id: str) -> Billing:
        self.billing_id = billing_id
        return self

    def with_project_name(self, project_name: str) -> Billing:
        self.project_name = project_name
        return self

    def with_year(self, year: int) -> Billing:
        self.year = year
        return self

    def with_month(self, month: int) -> Billing:
        self.month = month
        return self

    def with_region(self, region: str) -> Billing:
        self.region = region
        return self

    def with_service(self, service: str) -> Billing:
        self.service = service
        return self

    def with_activity_type(self, activity_type: str) -> Billing:
        self.activity_type = activity_type
        return self

    def with_unit(self, unit: float) -> Billing:
        self.unit = unit
        return self

    def with_unit_name(self, unit_name: str) -> Billing:
        self.unit_name = unit_name
        return self

    def with_price(self, price: int) -> Billing:
        self.price = price
        return self

    def with_currency(self, currency: str) -> Billing:
        self.currency = currency
        return self

    def with_created_at(self, created_at: int) -> Billing:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Billing:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        account_name,
        project_name,
        year,
        month,
    ):
        return 'grn:gs2:::gs2:account:{accountName}:project:{projectName}:billing:{year}:{month}'.format(
            accountName=account_name,
            projectName=project_name,
            year=year,
            month=month,
        )

    @classmethod
    def get_account_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):project:(?P<projectName>.+):billing:(?P<year>.+):(?P<month>.+)', grn)
        if match is None:
            return None
        return match.group('account_name')

    @classmethod
    def get_project_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):project:(?P<projectName>.+):billing:(?P<year>.+):(?P<month>.+)', grn)
        if match is None:
            return None
        return match.group('project_name')

    @classmethod
    def get_year_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):project:(?P<projectName>.+):billing:(?P<year>.+):(?P<month>.+)', grn)
        if match is None:
            return None
        return match.group('year')

    @classmethod
    def get_month_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):project:(?P<projectName>.+):billing:(?P<year>.+):(?P<month>.+)', grn)
        if match is None:
            return None
        return match.group('month')

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
    ) -> Optional[Billing]:
        if data is None:
            return None
        return Billing()\
            .with_billing_id(data.get('billingId'))\
            .with_project_name(data.get('projectName'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_region(data.get('region'))\
            .with_service(data.get('service'))\
            .with_activity_type(data.get('activityType'))\
            .with_unit(data.get('unit'))\
            .with_unit_name(data.get('unitName'))\
            .with_price(data.get('price'))\
            .with_currency(data.get('currency'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "billingId": self.billing_id,
            "projectName": self.project_name,
            "year": self.year,
            "month": self.month,
            "region": self.region,
            "service": self.service,
            "activityType": self.activity_type,
            "unit": self.unit,
            "unitName": self.unit_name,
            "price": self.price,
            "currency": self.currency,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Receipt(core.Gs2Model):
    receipt_id: str = None
    account_name: str = None
    name: str = None
    date: int = None
    amount: str = None
    pdf_url: str = None
    created_at: int = None
    updated_at: int = None

    def with_receipt_id(self, receipt_id: str) -> Receipt:
        self.receipt_id = receipt_id
        return self

    def with_account_name(self, account_name: str) -> Receipt:
        self.account_name = account_name
        return self

    def with_name(self, name: str) -> Receipt:
        self.name = name
        return self

    def with_date(self, date: int) -> Receipt:
        self.date = date
        return self

    def with_amount(self, amount: str) -> Receipt:
        self.amount = amount
        return self

    def with_pdf_url(self, pdf_url: str) -> Receipt:
        self.pdf_url = pdf_url
        return self

    def with_created_at(self, created_at: int) -> Receipt:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Receipt:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        account_name,
        receipt_name,
    ):
        return 'grn:gs2:::gs2:account:{accountName}:receipt:{receiptName}'.format(
            accountName=account_name,
            receiptName=receipt_name,
        )

    @classmethod
    def get_account_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):receipt:(?P<receiptName>.+)', grn)
        if match is None:
            return None
        return match.group('account_name')

    @classmethod
    def get_receipt_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):receipt:(?P<receiptName>.+)', grn)
        if match is None:
            return None
        return match.group('receipt_name')

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
    ) -> Optional[Receipt]:
        if data is None:
            return None
        return Receipt()\
            .with_receipt_id(data.get('receiptId'))\
            .with_account_name(data.get('accountName'))\
            .with_name(data.get('name'))\
            .with_date(data.get('date'))\
            .with_amount(data.get('amount'))\
            .with_pdf_url(data.get('pdfUrl'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receiptId": self.receipt_id,
            "accountName": self.account_name,
            "name": self.name,
            "date": self.date,
            "amount": self.amount,
            "pdfUrl": self.pdf_url,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class BillingMethod(core.Gs2Model):
    billing_method_id: str = None
    account_name: str = None
    name: str = None
    description: str = None
    method_type: str = None
    card_signature_name: str = None
    card_brand: str = None
    card_last4: str = None
    partner_id: str = None
    created_at: int = None
    updated_at: int = None

    def with_billing_method_id(self, billing_method_id: str) -> BillingMethod:
        self.billing_method_id = billing_method_id
        return self

    def with_account_name(self, account_name: str) -> BillingMethod:
        self.account_name = account_name
        return self

    def with_name(self, name: str) -> BillingMethod:
        self.name = name
        return self

    def with_description(self, description: str) -> BillingMethod:
        self.description = description
        return self

    def with_method_type(self, method_type: str) -> BillingMethod:
        self.method_type = method_type
        return self

    def with_card_signature_name(self, card_signature_name: str) -> BillingMethod:
        self.card_signature_name = card_signature_name
        return self

    def with_card_brand(self, card_brand: str) -> BillingMethod:
        self.card_brand = card_brand
        return self

    def with_card_last4(self, card_last4: str) -> BillingMethod:
        self.card_last4 = card_last4
        return self

    def with_partner_id(self, partner_id: str) -> BillingMethod:
        self.partner_id = partner_id
        return self

    def with_created_at(self, created_at: int) -> BillingMethod:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BillingMethod:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        account_name,
        billing_method_name,
    ):
        return 'grn:gs2:::gs2:account:{accountName}:billingMethod:{billingMethodName}'.format(
            accountName=account_name,
            billingMethodName=billing_method_name,
        )

    @classmethod
    def get_account_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):billingMethod:(?P<billingMethodName>.+)', grn)
        if match is None:
            return None
        return match.group('account_name')

    @classmethod
    def get_billing_method_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):billingMethod:(?P<billingMethodName>.+)', grn)
        if match is None:
            return None
        return match.group('billing_method_name')

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
    ) -> Optional[BillingMethod]:
        if data is None:
            return None
        return BillingMethod()\
            .with_billing_method_id(data.get('billingMethodId'))\
            .with_account_name(data.get('accountName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_method_type(data.get('methodType'))\
            .with_card_signature_name(data.get('cardSignatureName'))\
            .with_card_brand(data.get('cardBrand'))\
            .with_card_last4(data.get('cardLast4'))\
            .with_partner_id(data.get('partnerId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "billingMethodId": self.billing_method_id,
            "accountName": self.account_name,
            "name": self.name,
            "description": self.description,
            "methodType": self.method_type,
            "cardSignatureName": self.card_signature_name,
            "cardBrand": self.card_brand,
            "cardLast4": self.card_last4,
            "partnerId": self.partner_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Project(core.Gs2Model):
    project_id: str = None
    account_name: str = None
    name: str = None
    description: str = None
    plan: str = None
    billing_method_name: str = None
    enable_event_bridge: str = None
    event_bridge_aws_account_id: str = None
    event_bridge_aws_region: str = None
    created_at: int = None
    updated_at: int = None

    def with_project_id(self, project_id: str) -> Project:
        self.project_id = project_id
        return self

    def with_account_name(self, account_name: str) -> Project:
        self.account_name = account_name
        return self

    def with_name(self, name: str) -> Project:
        self.name = name
        return self

    def with_description(self, description: str) -> Project:
        self.description = description
        return self

    def with_plan(self, plan: str) -> Project:
        self.plan = plan
        return self

    def with_billing_method_name(self, billing_method_name: str) -> Project:
        self.billing_method_name = billing_method_name
        return self

    def with_enable_event_bridge(self, enable_event_bridge: str) -> Project:
        self.enable_event_bridge = enable_event_bridge
        return self

    def with_event_bridge_aws_account_id(self, event_bridge_aws_account_id: str) -> Project:
        self.event_bridge_aws_account_id = event_bridge_aws_account_id
        return self

    def with_event_bridge_aws_region(self, event_bridge_aws_region: str) -> Project:
        self.event_bridge_aws_region = event_bridge_aws_region
        return self

    def with_created_at(self, created_at: int) -> Project:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Project:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        account_name,
        project_name,
    ):
        return 'grn:gs2:::gs2:account:{accountName}:project:{projectName}'.format(
            accountName=account_name,
            projectName=project_name,
        )

    @classmethod
    def get_account_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):project:(?P<projectName>.+)', grn)
        if match is None:
            return None
        return match.group('account_name')

    @classmethod
    def get_project_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+):project:(?P<projectName>.+)', grn)
        if match is None:
            return None
        return match.group('project_name')

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
    ) -> Optional[Project]:
        if data is None:
            return None
        return Project()\
            .with_project_id(data.get('projectId'))\
            .with_account_name(data.get('accountName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_plan(data.get('plan'))\
            .with_billing_method_name(data.get('billingMethodName'))\
            .with_enable_event_bridge(data.get('enableEventBridge'))\
            .with_event_bridge_aws_account_id(data.get('eventBridgeAwsAccountId'))\
            .with_event_bridge_aws_region(data.get('eventBridgeAwsRegion'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projectId": self.project_id,
            "accountName": self.account_name,
            "name": self.name,
            "description": self.description,
            "plan": self.plan,
            "billingMethodName": self.billing_method_name,
            "enableEventBridge": self.enable_event_bridge,
            "eventBridgeAwsAccountId": self.event_bridge_aws_account_id,
            "eventBridgeAwsRegion": self.event_bridge_aws_region,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Account(core.Gs2Model):
    account_id: str = None
    owner_id: str = None
    name: str = None
    email: str = None
    full_name: str = None
    company_name: str = None
    status: str = None
    created_at: int = None
    updated_at: int = None

    def with_account_id(self, account_id: str) -> Account:
        self.account_id = account_id
        return self

    def with_owner_id(self, owner_id: str) -> Account:
        self.owner_id = owner_id
        return self

    def with_name(self, name: str) -> Account:
        self.name = name
        return self

    def with_email(self, email: str) -> Account:
        self.email = email
        return self

    def with_full_name(self, full_name: str) -> Account:
        self.full_name = full_name
        return self

    def with_company_name(self, company_name: str) -> Account:
        self.company_name = company_name
        return self

    def with_status(self, status: str) -> Account:
        self.status = status
        return self

    def with_created_at(self, created_at: int) -> Account:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Account:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        account_name,
    ):
        return 'grn:gs2:::gs2:account:{accountName}'.format(
            accountName=account_name,
        )

    @classmethod
    def get_account_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:::gs2:account:(?P<accountName>.+)', grn)
        if match is None:
            return None
        return match.group('account_name')

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
    ) -> Optional[Account]:
        if data is None:
            return None
        return Account()\
            .with_account_id(data.get('accountId'))\
            .with_owner_id(data.get('ownerId'))\
            .with_name(data.get('name'))\
            .with_email(data.get('email'))\
            .with_full_name(data.get('fullName'))\
            .with_company_name(data.get('companyName'))\
            .with_status(data.get('status'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountId": self.account_id,
            "ownerId": self.owner_id,
            "name": self.name,
            "email": self.email,
            "fullName": self.full_name,
            "companyName": self.company_name,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }