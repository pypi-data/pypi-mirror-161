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


class CreateAccountResult(core.Gs2Result):
    item: Account = None

    def with_item(self, item: Account) -> CreateAccountResult:
        self.item = item
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
    ) -> Optional[CreateAccountResult]:
        if data is None:
            return None
        return CreateAccountResult()\
            .with_item(Account.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyResult(core.Gs2Result):
    item: Account = None

    def with_item(self, item: Account) -> VerifyResult:
        self.item = item
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
    ) -> Optional[VerifyResult]:
        if data is None:
            return None
        return VerifyResult()\
            .with_item(Account.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SignInResult(core.Gs2Result):
    item: Account = None
    account_token: str = None

    def with_item(self, item: Account) -> SignInResult:
        self.item = item
        return self

    def with_account_token(self, account_token: str) -> SignInResult:
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
    ) -> Optional[SignInResult]:
        if data is None:
            return None
        return SignInResult()\
            .with_item(Account.from_dict(data.get('item')))\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "accountToken": self.account_token,
        }


class IssueAccountTokenResult(core.Gs2Result):
    account_token: str = None

    def with_account_token(self, account_token: str) -> IssueAccountTokenResult:
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
    ) -> Optional[IssueAccountTokenResult]:
        if data is None:
            return None
        return IssueAccountTokenResult()\
            .with_account_token(data.get('accountToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountToken": self.account_token,
        }


class ForgetResult(core.Gs2Result):

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
    ) -> Optional[ForgetResult]:
        if data is None:
            return None
        return ForgetResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class IssuePasswordResult(core.Gs2Result):
    new_password: str = None

    def with_new_password(self, new_password: str) -> IssuePasswordResult:
        self.new_password = new_password
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
    ) -> Optional[IssuePasswordResult]:
        if data is None:
            return None
        return IssuePasswordResult()\
            .with_new_password(data.get('newPassword'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newPassword": self.new_password,
        }


class UpdateAccountResult(core.Gs2Result):
    item: Account = None

    def with_item(self, item: Account) -> UpdateAccountResult:
        self.item = item
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
    ) -> Optional[UpdateAccountResult]:
        if data is None:
            return None
        return UpdateAccountResult()\
            .with_item(Account.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteAccountResult(core.Gs2Result):
    item: Account = None

    def with_item(self, item: Account) -> DeleteAccountResult:
        self.item = item
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
    ) -> Optional[DeleteAccountResult]:
        if data is None:
            return None
        return DeleteAccountResult()\
            .with_item(Account.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeProjectsResult(core.Gs2Result):
    items: List[Project] = None
    next_page_token: str = None

    def with_items(self, items: List[Project]) -> DescribeProjectsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeProjectsResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeProjectsResult]:
        if data is None:
            return None
        return DescribeProjectsResult()\
            .with_items([
                Project.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateProjectResult(core.Gs2Result):
    item: Project = None

    def with_item(self, item: Project) -> CreateProjectResult:
        self.item = item
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
    ) -> Optional[CreateProjectResult]:
        if data is None:
            return None
        return CreateProjectResult()\
            .with_item(Project.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetProjectResult(core.Gs2Result):
    item: Project = None

    def with_item(self, item: Project) -> GetProjectResult:
        self.item = item
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
    ) -> Optional[GetProjectResult]:
        if data is None:
            return None
        return GetProjectResult()\
            .with_item(Project.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetProjectTokenResult(core.Gs2Result):
    item: Project = None
    owner_id: str = None
    project_token: str = None

    def with_item(self, item: Project) -> GetProjectTokenResult:
        self.item = item
        return self

    def with_owner_id(self, owner_id: str) -> GetProjectTokenResult:
        self.owner_id = owner_id
        return self

    def with_project_token(self, project_token: str) -> GetProjectTokenResult:
        self.project_token = project_token
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
    ) -> Optional[GetProjectTokenResult]:
        if data is None:
            return None
        return GetProjectTokenResult()\
            .with_item(Project.from_dict(data.get('item')))\
            .with_owner_id(data.get('ownerId'))\
            .with_project_token(data.get('projectToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "ownerId": self.owner_id,
            "projectToken": self.project_token,
        }


class GetProjectTokenByIdentifierResult(core.Gs2Result):
    item: Project = None
    owner_id: str = None
    project_token: str = None

    def with_item(self, item: Project) -> GetProjectTokenByIdentifierResult:
        self.item = item
        return self

    def with_owner_id(self, owner_id: str) -> GetProjectTokenByIdentifierResult:
        self.owner_id = owner_id
        return self

    def with_project_token(self, project_token: str) -> GetProjectTokenByIdentifierResult:
        self.project_token = project_token
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
    ) -> Optional[GetProjectTokenByIdentifierResult]:
        if data is None:
            return None
        return GetProjectTokenByIdentifierResult()\
            .with_item(Project.from_dict(data.get('item')))\
            .with_owner_id(data.get('ownerId'))\
            .with_project_token(data.get('projectToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "ownerId": self.owner_id,
            "projectToken": self.project_token,
        }


class UpdateProjectResult(core.Gs2Result):
    item: Project = None

    def with_item(self, item: Project) -> UpdateProjectResult:
        self.item = item
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
    ) -> Optional[UpdateProjectResult]:
        if data is None:
            return None
        return UpdateProjectResult()\
            .with_item(Project.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteProjectResult(core.Gs2Result):
    item: Project = None

    def with_item(self, item: Project) -> DeleteProjectResult:
        self.item = item
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
    ) -> Optional[DeleteProjectResult]:
        if data is None:
            return None
        return DeleteProjectResult()\
            .with_item(Project.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBillingMethodsResult(core.Gs2Result):
    items: List[BillingMethod] = None
    next_page_token: str = None

    def with_items(self, items: List[BillingMethod]) -> DescribeBillingMethodsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBillingMethodsResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeBillingMethodsResult]:
        if data is None:
            return None
        return DescribeBillingMethodsResult()\
            .with_items([
                BillingMethod.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateBillingMethodResult(core.Gs2Result):
    item: BillingMethod = None

    def with_item(self, item: BillingMethod) -> CreateBillingMethodResult:
        self.item = item
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
    ) -> Optional[CreateBillingMethodResult]:
        if data is None:
            return None
        return CreateBillingMethodResult()\
            .with_item(BillingMethod.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBillingMethodResult(core.Gs2Result):
    item: BillingMethod = None

    def with_item(self, item: BillingMethod) -> GetBillingMethodResult:
        self.item = item
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
    ) -> Optional[GetBillingMethodResult]:
        if data is None:
            return None
        return GetBillingMethodResult()\
            .with_item(BillingMethod.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateBillingMethodResult(core.Gs2Result):
    item: BillingMethod = None

    def with_item(self, item: BillingMethod) -> UpdateBillingMethodResult:
        self.item = item
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
    ) -> Optional[UpdateBillingMethodResult]:
        if data is None:
            return None
        return UpdateBillingMethodResult()\
            .with_item(BillingMethod.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteBillingMethodResult(core.Gs2Result):
    item: BillingMethod = None

    def with_item(self, item: BillingMethod) -> DeleteBillingMethodResult:
        self.item = item
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
    ) -> Optional[DeleteBillingMethodResult]:
        if data is None:
            return None
        return DeleteBillingMethodResult()\
            .with_item(BillingMethod.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeReceiptsResult(core.Gs2Result):
    items: List[Receipt] = None
    next_page_token: str = None

    def with_items(self, items: List[Receipt]) -> DescribeReceiptsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeReceiptsResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeReceiptsResult]:
        if data is None:
            return None
        return DescribeReceiptsResult()\
            .with_items([
                Receipt.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
            "nextPageToken": self.next_page_token,
        }


class DescribeBillingsResult(core.Gs2Result):
    items: List[Billing] = None

    def with_items(self, items: List[Billing]) -> DescribeBillingsResult:
        self.items = items
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
    ) -> Optional[DescribeBillingsResult]:
        if data is None:
            return None
        return DescribeBillingsResult()\
            .with_items([
                Billing.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
        }