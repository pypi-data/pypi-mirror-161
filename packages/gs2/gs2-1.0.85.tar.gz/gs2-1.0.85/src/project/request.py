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

from project.model import *


class CreateAccountRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    full_name: str = None
    company_name: str = None
    password: str = None
    lang: str = None

    def with_email(self, email: str) -> CreateAccountRequest:
        self.email = email
        return self

    def with_full_name(self, full_name: str) -> CreateAccountRequest:
        self.full_name = full_name
        return self

    def with_company_name(self, company_name: str) -> CreateAccountRequest:
        self.company_name = company_name
        return self

    def with_password(self, password: str) -> CreateAccountRequest:
        self.password = password
        return self

    def with_lang(self, lang: str) -> CreateAccountRequest:
        self.lang = lang
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
    ) -> Optional[CreateAccountRequest]:
        if data is None:
            return None
        return CreateAccountRequest()\
            .with_email(data.get('email'))\
            .with_full_name(data.get('fullName'))\
            .with_company_name(data.get('companyName'))\
            .with_password(data.get('password'))\
            .with_lang(data.get('lang'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "fullName": self.full_name,
            "companyName": self.company_name,
            "password": self.password,
            "lang": self.lang,
        }


class VerifyRequest(core.Gs2Request):

    context_stack: str = None
    verify_token: str = None

    def with_verify_token(self, verify_token: str) -> VerifyRequest:
        self.verify_token = verify_token
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
    ) -> Optional[VerifyRequest]:
        if data is None:
            return None
        return VerifyRequest()\
            .with_verify_token(data.get('verifyToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verifyToken": self.verify_token,
        }


class SignInRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    password: str = None

    def with_email(self, email: str) -> SignInRequest:
        self.email = email
        return self

    def with_password(self, password: str) -> SignInRequest:
        self.password = password
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
    ) -> Optional[SignInRequest]:
        if data is None:
            return None
        return SignInRequest()\
            .with_email(data.get('email'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "password": self.password,
        }


class IssueAccountTokenRequest(core.Gs2Request):

    context_stack: str = None
    account_name: str = None

    def with_account_name(self, account_name: str) -> IssueAccountTokenRequest:
        self.account_name = account_name
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
    ) -> Optional[IssueAccountTokenRequest]:
        if data is None:
            return None
        return IssueAccountTokenRequest()\
            .with_account_name(data.get('accountName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountName": self.account_name,
        }


class ForgetRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    lang: str = None

    def with_email(self, email: str) -> ForgetRequest:
        self.email = email
        return self

    def with_lang(self, lang: str) -> ForgetRequest:
        self.lang = lang
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
    ) -> Optional[ForgetRequest]:
        if data is None:
            return None
        return ForgetRequest()\
            .with_email(data.get('email'))\
            .with_lang(data.get('lang'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "lang": self.lang,
        }


class IssuePasswordRequest(core.Gs2Request):

    context_stack: str = None
    issue_password_token: str = None

    def with_issue_password_token(self, issue_password_token: str) -> IssuePasswordRequest:
        self.issue_password_token = issue_password_token
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
    ) -> Optional[IssuePasswordRequest]:
        if data is None:
            return None
        return IssuePasswordRequest()\
            .with_issue_password_token(data.get('issuePasswordToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issuePasswordToken": self.issue_password_token,
        }


class UpdateAccountRequest(core.Gs2Request):

    context_stack: str = None
    email: str = None
    full_name: str = None
    company_name: str = None
    password: str = None
    account_token: str = None

    def with_email(self, email: str) -> UpdateAccountRequest:
        self.email = email
        return self

    def with_full_name(self, full_name: str) -> UpdateAccountRequest:
        self.full_name = full_name
        return self

    def with_company_name(self, company_name: str) -> UpdateAccountRequest:
        self.company_name = company_name
        return self

    def with_password(self, password: str) -> UpdateAccountRequest:
        self.password = password
        return self

    def with_account_token(self, account_token: str) -> UpdateAccountRequest:
        self.account_token = account_token
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
    ) -> Optional[UpdateAccountRequest]:
        if data is None:
            return None
        return UpdateAccountRequest()\
            .with_email(data.get('email'))\
            .with_full_name(data.get('fullName'))\
            .with_company_name(data.get('companyName'))\
            .with_password(data.get('password'))\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "fullName": self.full_name,
            "companyName": self.company_name,
            "password": self.password,
            "accountToken": self.account_token,
        }


class DeleteAccountRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None

    def with_account_token(self, account_token: str) -> DeleteAccountRequest:
        self.account_token = account_token
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
    ) -> Optional[DeleteAccountRequest]:
        if data is None:
            return None
        return DeleteAccountRequest()\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
        }


class DescribeProjectsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    page_token: str = None
    limit: int = None

    def with_account_token(self, account_token: str) -> DescribeProjectsRequest:
        self.account_token = account_token
        return self

    def with_page_token(self, page_token: str) -> DescribeProjectsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeProjectsRequest:
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
    ) -> Optional[DescribeProjectsRequest]:
        if data is None:
            return None
        return DescribeProjectsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    name: str = None
    description: str = None
    plan: str = None
    billing_method_name: str = None
    enable_event_bridge: str = None
    event_bridge_aws_account_id: str = None
    event_bridge_aws_region: str = None

    def with_account_token(self, account_token: str) -> CreateProjectRequest:
        self.account_token = account_token
        return self

    def with_name(self, name: str) -> CreateProjectRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateProjectRequest:
        self.description = description
        return self

    def with_plan(self, plan: str) -> CreateProjectRequest:
        self.plan = plan
        return self

    def with_billing_method_name(self, billing_method_name: str) -> CreateProjectRequest:
        self.billing_method_name = billing_method_name
        return self

    def with_enable_event_bridge(self, enable_event_bridge: str) -> CreateProjectRequest:
        self.enable_event_bridge = enable_event_bridge
        return self

    def with_event_bridge_aws_account_id(self, event_bridge_aws_account_id: str) -> CreateProjectRequest:
        self.event_bridge_aws_account_id = event_bridge_aws_account_id
        return self

    def with_event_bridge_aws_region(self, event_bridge_aws_region: str) -> CreateProjectRequest:
        self.event_bridge_aws_region = event_bridge_aws_region
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
    ) -> Optional[CreateProjectRequest]:
        if data is None:
            return None
        return CreateProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_plan(data.get('plan'))\
            .with_billing_method_name(data.get('billingMethodName'))\
            .with_enable_event_bridge(data.get('enableEventBridge'))\
            .with_event_bridge_aws_account_id(data.get('eventBridgeAwsAccountId'))\
            .with_event_bridge_aws_region(data.get('eventBridgeAwsRegion'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "name": self.name,
            "description": self.description,
            "plan": self.plan,
            "billingMethodName": self.billing_method_name,
            "enableEventBridge": self.enable_event_bridge,
            "eventBridgeAwsAccountId": self.event_bridge_aws_account_id,
            "eventBridgeAwsRegion": self.event_bridge_aws_region,
        }


class GetProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None

    def with_account_token(self, account_token: str) -> GetProjectRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> GetProjectRequest:
        self.project_name = project_name
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
    ) -> Optional[GetProjectRequest]:
        if data is None:
            return None
        return GetProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
        }


class GetProjectTokenRequest(core.Gs2Request):

    context_stack: str = None
    project_name: str = None
    account_token: str = None

    def with_project_name(self, project_name: str) -> GetProjectTokenRequest:
        self.project_name = project_name
        return self

    def with_account_token(self, account_token: str) -> GetProjectTokenRequest:
        self.account_token = account_token
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
    ) -> Optional[GetProjectTokenRequest]:
        if data is None:
            return None
        return GetProjectTokenRequest()\
            .with_project_name(data.get('projectName'))\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projectName": self.project_name,
            "accountToken": self.account_token,
        }


class GetProjectTokenByIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    account_name: str = None
    project_name: str = None
    user_name: str = None
    password: str = None

    def with_account_name(self, account_name: str) -> GetProjectTokenByIdentifierRequest:
        self.account_name = account_name
        return self

    def with_project_name(self, project_name: str) -> GetProjectTokenByIdentifierRequest:
        self.project_name = project_name
        return self

    def with_user_name(self, user_name: str) -> GetProjectTokenByIdentifierRequest:
        self.user_name = user_name
        return self

    def with_password(self, password: str) -> GetProjectTokenByIdentifierRequest:
        self.password = password
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
    ) -> Optional[GetProjectTokenByIdentifierRequest]:
        if data is None:
            return None
        return GetProjectTokenByIdentifierRequest()\
            .with_account_name(data.get('accountName'))\
            .with_project_name(data.get('projectName'))\
            .with_user_name(data.get('userName'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountName": self.account_name,
            "projectName": self.project_name,
            "userName": self.user_name,
            "password": self.password,
        }


class UpdateProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None
    description: str = None
    plan: str = None
    billing_method_name: str = None
    enable_event_bridge: str = None
    event_bridge_aws_account_id: str = None
    event_bridge_aws_region: str = None

    def with_account_token(self, account_token: str) -> UpdateProjectRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> UpdateProjectRequest:
        self.project_name = project_name
        return self

    def with_description(self, description: str) -> UpdateProjectRequest:
        self.description = description
        return self

    def with_plan(self, plan: str) -> UpdateProjectRequest:
        self.plan = plan
        return self

    def with_billing_method_name(self, billing_method_name: str) -> UpdateProjectRequest:
        self.billing_method_name = billing_method_name
        return self

    def with_enable_event_bridge(self, enable_event_bridge: str) -> UpdateProjectRequest:
        self.enable_event_bridge = enable_event_bridge
        return self

    def with_event_bridge_aws_account_id(self, event_bridge_aws_account_id: str) -> UpdateProjectRequest:
        self.event_bridge_aws_account_id = event_bridge_aws_account_id
        return self

    def with_event_bridge_aws_region(self, event_bridge_aws_region: str) -> UpdateProjectRequest:
        self.event_bridge_aws_region = event_bridge_aws_region
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
    ) -> Optional[UpdateProjectRequest]:
        if data is None:
            return None
        return UpdateProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))\
            .with_description(data.get('description'))\
            .with_plan(data.get('plan'))\
            .with_billing_method_name(data.get('billingMethodName'))\
            .with_enable_event_bridge(data.get('enableEventBridge'))\
            .with_event_bridge_aws_account_id(data.get('eventBridgeAwsAccountId'))\
            .with_event_bridge_aws_region(data.get('eventBridgeAwsRegion'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
            "description": self.description,
            "plan": self.plan,
            "billingMethodName": self.billing_method_name,
            "enableEventBridge": self.enable_event_bridge,
            "eventBridgeAwsAccountId": self.event_bridge_aws_account_id,
            "eventBridgeAwsRegion": self.event_bridge_aws_region,
        }


class DeleteProjectRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None

    def with_account_token(self, account_token: str) -> DeleteProjectRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> DeleteProjectRequest:
        self.project_name = project_name
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
    ) -> Optional[DeleteProjectRequest]:
        if data is None:
            return None
        return DeleteProjectRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
        }


class DescribeBillingMethodsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    page_token: str = None
    limit: int = None

    def with_account_token(self, account_token: str) -> DescribeBillingMethodsRequest:
        self.account_token = account_token
        return self

    def with_page_token(self, page_token: str) -> DescribeBillingMethodsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBillingMethodsRequest:
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
    ) -> Optional[DescribeBillingMethodsRequest]:
        if data is None:
            return None
        return DescribeBillingMethodsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    description: str = None
    method_type: str = None
    card_customer_id: str = None
    partner_id: str = None

    def with_account_token(self, account_token: str) -> CreateBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_description(self, description: str) -> CreateBillingMethodRequest:
        self.description = description
        return self

    def with_method_type(self, method_type: str) -> CreateBillingMethodRequest:
        self.method_type = method_type
        return self

    def with_card_customer_id(self, card_customer_id: str) -> CreateBillingMethodRequest:
        self.card_customer_id = card_customer_id
        return self

    def with_partner_id(self, partner_id: str) -> CreateBillingMethodRequest:
        self.partner_id = partner_id
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
    ) -> Optional[CreateBillingMethodRequest]:
        if data is None:
            return None
        return CreateBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_description(data.get('description'))\
            .with_method_type(data.get('methodType'))\
            .with_card_customer_id(data.get('cardCustomerId'))\
            .with_partner_id(data.get('partnerId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "description": self.description,
            "methodType": self.method_type,
            "cardCustomerId": self.card_customer_id,
            "partnerId": self.partner_id,
        }


class GetBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    billing_method_name: str = None

    def with_account_token(self, account_token: str) -> GetBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_billing_method_name(self, billing_method_name: str) -> GetBillingMethodRequest:
        self.billing_method_name = billing_method_name
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
    ) -> Optional[GetBillingMethodRequest]:
        if data is None:
            return None
        return GetBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_billing_method_name(data.get('billingMethodName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "billingMethodName": self.billing_method_name,
        }


class UpdateBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    billing_method_name: str = None
    description: str = None

    def with_account_token(self, account_token: str) -> UpdateBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_billing_method_name(self, billing_method_name: str) -> UpdateBillingMethodRequest:
        self.billing_method_name = billing_method_name
        return self

    def with_description(self, description: str) -> UpdateBillingMethodRequest:
        self.description = description
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
    ) -> Optional[UpdateBillingMethodRequest]:
        if data is None:
            return None
        return UpdateBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_billing_method_name(data.get('billingMethodName'))\
            .with_description(data.get('description'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "billingMethodName": self.billing_method_name,
            "description": self.description,
        }


class DeleteBillingMethodRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    billing_method_name: str = None

    def with_account_token(self, account_token: str) -> DeleteBillingMethodRequest:
        self.account_token = account_token
        return self

    def with_billing_method_name(self, billing_method_name: str) -> DeleteBillingMethodRequest:
        self.billing_method_name = billing_method_name
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
    ) -> Optional[DeleteBillingMethodRequest]:
        if data is None:
            return None
        return DeleteBillingMethodRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_billing_method_name(data.get('billingMethodName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "billingMethodName": self.billing_method_name,
        }


class DescribeReceiptsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    page_token: str = None
    limit: int = None

    def with_account_token(self, account_token: str) -> DescribeReceiptsRequest:
        self.account_token = account_token
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiptsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiptsRequest:
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
    ) -> Optional[DescribeReceiptsRequest]:
        if data is None:
            return None
        return DescribeReceiptsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeBillingsRequest(core.Gs2Request):

    context_stack: str = None
    account_token: str = None
    project_name: str = None
    year: int = None
    month: int = None
    region: str = None
    service: str = None

    def with_account_token(self, account_token: str) -> DescribeBillingsRequest:
        self.account_token = account_token
        return self

    def with_project_name(self, project_name: str) -> DescribeBillingsRequest:
        self.project_name = project_name
        return self

    def with_year(self, year: int) -> DescribeBillingsRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> DescribeBillingsRequest:
        self.month = month
        return self

    def with_region(self, region: str) -> DescribeBillingsRequest:
        self.region = region
        return self

    def with_service(self, service: str) -> DescribeBillingsRequest:
        self.service = service
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
    ) -> Optional[DescribeBillingsRequest]:
        if data is None:
            return None
        return DescribeBillingsRequest()\
            .with_account_token(data.get('accountToken'))\
            .with_project_name(data.get('projectName'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_region(data.get('region'))\
            .with_service(data.get('service'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
            "projectName": self.project_name,
            "year": self.year,
            "month": self.month,
            "region": self.region,
            "service": self.service,
        }