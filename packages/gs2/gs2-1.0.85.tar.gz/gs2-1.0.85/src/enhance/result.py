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

from enhance.model import *


class DescribeNamespacesResult(core.Gs2Result):
    items: List[Namespace] = None
    next_page_token: str = None

    def with_items(self, items: List[Namespace]) -> DescribeNamespacesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeNamespacesResult:
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
    ) -> Optional[DescribeNamespacesResult]:
        if data is None:
            return None
        return DescribeNamespacesResult()\
            .with_items([
                Namespace.from_dict(data.get('items')[i])
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


class CreateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> CreateNamespaceResult:
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
    ) -> Optional[CreateNamespaceResult]:
        if data is None:
            return None
        return CreateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetNamespaceStatusResult(core.Gs2Result):
    status: str = None

    def with_status(self, status: str) -> GetNamespaceStatusResult:
        self.status = status
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
    ) -> Optional[GetNamespaceStatusResult]:
        if data is None:
            return None
        return GetNamespaceStatusResult()\
            .with_status(data.get('status'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
        }


class GetNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> GetNamespaceResult:
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
    ) -> Optional[GetNamespaceResult]:
        if data is None:
            return None
        return GetNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> UpdateNamespaceResult:
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
    ) -> Optional[UpdateNamespaceResult]:
        if data is None:
            return None
        return UpdateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> DeleteNamespaceResult:
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
    ) -> Optional[DeleteNamespaceResult]:
        if data is None:
            return None
        return DeleteNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRateModelsResult(core.Gs2Result):
    items: List[RateModel] = None

    def with_items(self, items: List[RateModel]) -> DescribeRateModelsResult:
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
    ) -> Optional[DescribeRateModelsResult]:
        if data is None:
            return None
        return DescribeRateModelsResult()\
            .with_items([
                RateModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
        }


class GetRateModelResult(core.Gs2Result):
    item: RateModel = None

    def with_item(self, item: RateModel) -> GetRateModelResult:
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
    ) -> Optional[GetRateModelResult]:
        if data is None:
            return None
        return GetRateModelResult()\
            .with_item(RateModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRateModelMastersResult(core.Gs2Result):
    items: List[RateModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[RateModelMaster]) -> DescribeRateModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRateModelMastersResult:
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
    ) -> Optional[DescribeRateModelMastersResult]:
        if data is None:
            return None
        return DescribeRateModelMastersResult()\
            .with_items([
                RateModelMaster.from_dict(data.get('items')[i])
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


class CreateRateModelMasterResult(core.Gs2Result):
    item: RateModelMaster = None

    def with_item(self, item: RateModelMaster) -> CreateRateModelMasterResult:
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
    ) -> Optional[CreateRateModelMasterResult]:
        if data is None:
            return None
        return CreateRateModelMasterResult()\
            .with_item(RateModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetRateModelMasterResult(core.Gs2Result):
    item: RateModelMaster = None

    def with_item(self, item: RateModelMaster) -> GetRateModelMasterResult:
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
    ) -> Optional[GetRateModelMasterResult]:
        if data is None:
            return None
        return GetRateModelMasterResult()\
            .with_item(RateModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateRateModelMasterResult(core.Gs2Result):
    item: RateModelMaster = None

    def with_item(self, item: RateModelMaster) -> UpdateRateModelMasterResult:
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
    ) -> Optional[UpdateRateModelMasterResult]:
        if data is None:
            return None
        return UpdateRateModelMasterResult()\
            .with_item(RateModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteRateModelMasterResult(core.Gs2Result):
    item: RateModelMaster = None

    def with_item(self, item: RateModelMaster) -> DeleteRateModelMasterResult:
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
    ) -> Optional[DeleteRateModelMasterResult]:
        if data is None:
            return None
        return DeleteRateModelMasterResult()\
            .with_item(RateModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DirectEnhanceResult(core.Gs2Result):
    item: RateModel = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    acquire_experience: int = None
    bonus_rate: float = None

    def with_item(self, item: RateModel) -> DirectEnhanceResult:
        self.item = item
        return self

    def with_transaction_id(self, transaction_id: str) -> DirectEnhanceResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> DirectEnhanceResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> DirectEnhanceResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> DirectEnhanceResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_acquire_experience(self, acquire_experience: int) -> DirectEnhanceResult:
        self.acquire_experience = acquire_experience
        return self

    def with_bonus_rate(self, bonus_rate: float) -> DirectEnhanceResult:
        self.bonus_rate = bonus_rate
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
    ) -> Optional[DirectEnhanceResult]:
        if data is None:
            return None
        return DirectEnhanceResult()\
            .with_item(RateModel.from_dict(data.get('item')))\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_acquire_experience(data.get('acquireExperience'))\
            .with_bonus_rate(data.get('bonusRate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "acquireExperience": self.acquire_experience,
            "bonusRate": self.bonus_rate,
        }


class DirectEnhanceByUserIdResult(core.Gs2Result):
    item: RateModel = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    acquire_experience: int = None
    bonus_rate: float = None

    def with_item(self, item: RateModel) -> DirectEnhanceByUserIdResult:
        self.item = item
        return self

    def with_transaction_id(self, transaction_id: str) -> DirectEnhanceByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> DirectEnhanceByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> DirectEnhanceByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> DirectEnhanceByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_acquire_experience(self, acquire_experience: int) -> DirectEnhanceByUserIdResult:
        self.acquire_experience = acquire_experience
        return self

    def with_bonus_rate(self, bonus_rate: float) -> DirectEnhanceByUserIdResult:
        self.bonus_rate = bonus_rate
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
    ) -> Optional[DirectEnhanceByUserIdResult]:
        if data is None:
            return None
        return DirectEnhanceByUserIdResult()\
            .with_item(RateModel.from_dict(data.get('item')))\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_acquire_experience(data.get('acquireExperience'))\
            .with_bonus_rate(data.get('bonusRate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "acquireExperience": self.acquire_experience,
            "bonusRate": self.bonus_rate,
        }


class DirectEnhanceByStampSheetResult(core.Gs2Result):
    item: RateModel = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    acquire_experience: int = None
    bonus_rate: float = None

    def with_item(self, item: RateModel) -> DirectEnhanceByStampSheetResult:
        self.item = item
        return self

    def with_transaction_id(self, transaction_id: str) -> DirectEnhanceByStampSheetResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> DirectEnhanceByStampSheetResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> DirectEnhanceByStampSheetResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> DirectEnhanceByStampSheetResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_acquire_experience(self, acquire_experience: int) -> DirectEnhanceByStampSheetResult:
        self.acquire_experience = acquire_experience
        return self

    def with_bonus_rate(self, bonus_rate: float) -> DirectEnhanceByStampSheetResult:
        self.bonus_rate = bonus_rate
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
    ) -> Optional[DirectEnhanceByStampSheetResult]:
        if data is None:
            return None
        return DirectEnhanceByStampSheetResult()\
            .with_item(RateModel.from_dict(data.get('item')))\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_acquire_experience(data.get('acquireExperience'))\
            .with_bonus_rate(data.get('bonusRate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "acquireExperience": self.acquire_experience,
            "bonusRate": self.bonus_rate,
        }


class DescribeProgressesByUserIdResult(core.Gs2Result):
    items: List[Progress] = None
    next_page_token: str = None

    def with_items(self, items: List[Progress]) -> DescribeProgressesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeProgressesByUserIdResult:
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
    ) -> Optional[DescribeProgressesByUserIdResult]:
        if data is None:
            return None
        return DescribeProgressesByUserIdResult()\
            .with_items([
                Progress.from_dict(data.get('items')[i])
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


class CreateProgressByUserIdResult(core.Gs2Result):
    item: Progress = None

    def with_item(self, item: Progress) -> CreateProgressByUserIdResult:
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
    ) -> Optional[CreateProgressByUserIdResult]:
        if data is None:
            return None
        return CreateProgressByUserIdResult()\
            .with_item(Progress.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetProgressResult(core.Gs2Result):
    item: Progress = None
    rate_model: RateModel = None

    def with_item(self, item: Progress) -> GetProgressResult:
        self.item = item
        return self

    def with_rate_model(self, rate_model: RateModel) -> GetProgressResult:
        self.rate_model = rate_model
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
    ) -> Optional[GetProgressResult]:
        if data is None:
            return None
        return GetProgressResult()\
            .with_item(Progress.from_dict(data.get('item')))\
            .with_rate_model(RateModel.from_dict(data.get('rateModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "rateModel": self.rate_model.to_dict() if self.rate_model else None,
        }


class GetProgressByUserIdResult(core.Gs2Result):
    item: Progress = None
    rate_model: RateModel = None

    def with_item(self, item: Progress) -> GetProgressByUserIdResult:
        self.item = item
        return self

    def with_rate_model(self, rate_model: RateModel) -> GetProgressByUserIdResult:
        self.rate_model = rate_model
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
    ) -> Optional[GetProgressByUserIdResult]:
        if data is None:
            return None
        return GetProgressByUserIdResult()\
            .with_item(Progress.from_dict(data.get('item')))\
            .with_rate_model(RateModel.from_dict(data.get('rateModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "rateModel": self.rate_model.to_dict() if self.rate_model else None,
        }


class StartResult(core.Gs2Result):
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None

    def with_transaction_id(self, transaction_id: str) -> StartResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> StartResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> StartResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> StartResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
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
    ) -> Optional[StartResult]:
        if data is None:
            return None
        return StartResult()\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
        }


class StartByUserIdResult(core.Gs2Result):
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None

    def with_transaction_id(self, transaction_id: str) -> StartByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> StartByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> StartByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> StartByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
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
    ) -> Optional[StartByUserIdResult]:
        if data is None:
            return None
        return StartByUserIdResult()\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
        }


class EndResult(core.Gs2Result):
    item: Progress = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    acquire_experience: int = None
    bonus_rate: float = None

    def with_item(self, item: Progress) -> EndResult:
        self.item = item
        return self

    def with_transaction_id(self, transaction_id: str) -> EndResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> EndResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> EndResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> EndResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_acquire_experience(self, acquire_experience: int) -> EndResult:
        self.acquire_experience = acquire_experience
        return self

    def with_bonus_rate(self, bonus_rate: float) -> EndResult:
        self.bonus_rate = bonus_rate
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
    ) -> Optional[EndResult]:
        if data is None:
            return None
        return EndResult()\
            .with_item(Progress.from_dict(data.get('item')))\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_acquire_experience(data.get('acquireExperience'))\
            .with_bonus_rate(data.get('bonusRate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "acquireExperience": self.acquire_experience,
            "bonusRate": self.bonus_rate,
        }


class EndByUserIdResult(core.Gs2Result):
    item: Progress = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    acquire_experience: int = None
    bonus_rate: float = None

    def with_item(self, item: Progress) -> EndByUserIdResult:
        self.item = item
        return self

    def with_transaction_id(self, transaction_id: str) -> EndByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> EndByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> EndByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> EndByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_acquire_experience(self, acquire_experience: int) -> EndByUserIdResult:
        self.acquire_experience = acquire_experience
        return self

    def with_bonus_rate(self, bonus_rate: float) -> EndByUserIdResult:
        self.bonus_rate = bonus_rate
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
    ) -> Optional[EndByUserIdResult]:
        if data is None:
            return None
        return EndByUserIdResult()\
            .with_item(Progress.from_dict(data.get('item')))\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_acquire_experience(data.get('acquireExperience'))\
            .with_bonus_rate(data.get('bonusRate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "acquireExperience": self.acquire_experience,
            "bonusRate": self.bonus_rate,
        }


class DeleteProgressResult(core.Gs2Result):
    item: Progress = None

    def with_item(self, item: Progress) -> DeleteProgressResult:
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
    ) -> Optional[DeleteProgressResult]:
        if data is None:
            return None
        return DeleteProgressResult()\
            .with_item(Progress.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteProgressByUserIdResult(core.Gs2Result):
    item: Progress = None

    def with_item(self, item: Progress) -> DeleteProgressByUserIdResult:
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
    ) -> Optional[DeleteProgressByUserIdResult]:
        if data is None:
            return None
        return DeleteProgressByUserIdResult()\
            .with_item(Progress.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateProgressByStampSheetResult(core.Gs2Result):
    item: Progress = None

    def with_item(self, item: Progress) -> CreateProgressByStampSheetResult:
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
    ) -> Optional[CreateProgressByStampSheetResult]:
        if data is None:
            return None
        return CreateProgressByStampSheetResult()\
            .with_item(Progress.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteProgressByStampTaskResult(core.Gs2Result):
    item: Progress = None
    new_context_stack: str = None

    def with_item(self, item: Progress) -> DeleteProgressByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> DeleteProgressByStampTaskResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[DeleteProgressByStampTaskResult]:
        if data is None:
            return None
        return DeleteProgressByStampTaskResult()\
            .with_item(Progress.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentRateMaster = None

    def with_item(self, item: CurrentRateMaster) -> ExportMasterResult:
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
    ) -> Optional[ExportMasterResult]:
        if data is None:
            return None
        return ExportMasterResult()\
            .with_item(CurrentRateMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentRateMasterResult(core.Gs2Result):
    item: CurrentRateMaster = None

    def with_item(self, item: CurrentRateMaster) -> GetCurrentRateMasterResult:
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
    ) -> Optional[GetCurrentRateMasterResult]:
        if data is None:
            return None
        return GetCurrentRateMasterResult()\
            .with_item(CurrentRateMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentRateMasterResult(core.Gs2Result):
    item: CurrentRateMaster = None

    def with_item(self, item: CurrentRateMaster) -> UpdateCurrentRateMasterResult:
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
    ) -> Optional[UpdateCurrentRateMasterResult]:
        if data is None:
            return None
        return UpdateCurrentRateMasterResult()\
            .with_item(CurrentRateMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentRateMasterFromGitHubResult(core.Gs2Result):
    item: CurrentRateMaster = None

    def with_item(self, item: CurrentRateMaster) -> UpdateCurrentRateMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentRateMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentRateMasterFromGitHubResult()\
            .with_item(CurrentRateMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }