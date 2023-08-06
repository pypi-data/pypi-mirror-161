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

from lottery.model import *


class DescribeNamespacesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeNamespacesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeNamespacesRequest:
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
    ) -> Optional[DescribeNamespacesRequest]:
        if data is None:
            return None
        return DescribeNamespacesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    lottery_trigger_script_id: str = None
    choice_prize_table_script_id: str = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> CreateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_lottery_trigger_script_id(self, lottery_trigger_script_id: str) -> CreateNamespaceRequest:
        self.lottery_trigger_script_id = lottery_trigger_script_id
        return self

    def with_choice_prize_table_script_id(self, choice_prize_table_script_id: str) -> CreateNamespaceRequest:
        self.choice_prize_table_script_id = choice_prize_table_script_id
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> CreateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> CreateNamespaceRequest:
        self.key_id = key_id
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
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_lottery_trigger_script_id(data.get('lotteryTriggerScriptId'))\
            .with_choice_prize_table_script_id(data.get('choicePrizeTableScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "lotteryTriggerScriptId": self.lottery_trigger_script_id,
            "choicePrizeTableScriptId": self.choice_prize_table_script_id,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
        }


class GetNamespaceStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceStatusRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetNamespaceStatusRequest]:
        if data is None:
            return None
        return GetNamespaceStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetNamespaceRequest]:
        if data is None:
            return None
        return GetNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    lottery_trigger_script_id: str = None
    choice_prize_table_script_id: str = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> UpdateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_lottery_trigger_script_id(self, lottery_trigger_script_id: str) -> UpdateNamespaceRequest:
        self.lottery_trigger_script_id = lottery_trigger_script_id
        return self

    def with_choice_prize_table_script_id(self, choice_prize_table_script_id: str) -> UpdateNamespaceRequest:
        self.choice_prize_table_script_id = choice_prize_table_script_id
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> UpdateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> UpdateNamespaceRequest:
        self.key_id = key_id
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
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_lottery_trigger_script_id(data.get('lotteryTriggerScriptId'))\
            .with_choice_prize_table_script_id(data.get('choicePrizeTableScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "lotteryTriggerScriptId": self.lottery_trigger_script_id,
            "choicePrizeTableScriptId": self.choice_prize_table_script_id,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
        }


class DeleteNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteNamespaceRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DeleteNamespaceRequest]:
        if data is None:
            return None
        return DeleteNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class DescribeLotteryModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeLotteryModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeLotteryModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeLotteryModelMastersRequest:
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
    ) -> Optional[DescribeLotteryModelMastersRequest]:
        if data is None:
            return None
        return DescribeLotteryModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateLotteryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    mode: str = None
    method: str = None
    prize_table_name: str = None
    choice_prize_table_script_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateLotteryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateLotteryModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateLotteryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateLotteryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_mode(self, mode: str) -> CreateLotteryModelMasterRequest:
        self.mode = mode
        return self

    def with_method(self, method: str) -> CreateLotteryModelMasterRequest:
        self.method = method
        return self

    def with_prize_table_name(self, prize_table_name: str) -> CreateLotteryModelMasterRequest:
        self.prize_table_name = prize_table_name
        return self

    def with_choice_prize_table_script_id(self, choice_prize_table_script_id: str) -> CreateLotteryModelMasterRequest:
        self.choice_prize_table_script_id = choice_prize_table_script_id
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
    ) -> Optional[CreateLotteryModelMasterRequest]:
        if data is None:
            return None
        return CreateLotteryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_mode(data.get('mode'))\
            .with_method(data.get('method'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_choice_prize_table_script_id(data.get('choicePrizeTableScriptId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "mode": self.mode,
            "method": self.method,
            "prizeTableName": self.prize_table_name,
            "choicePrizeTableScriptId": self.choice_prize_table_script_id,
        }


class GetLotteryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    lottery_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetLotteryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_lottery_name(self, lottery_name: str) -> GetLotteryModelMasterRequest:
        self.lottery_name = lottery_name
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
    ) -> Optional[GetLotteryModelMasterRequest]:
        if data is None:
            return None
        return GetLotteryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_lottery_name(data.get('lotteryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "lotteryName": self.lottery_name,
        }


class UpdateLotteryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    lottery_name: str = None
    description: str = None
    metadata: str = None
    mode: str = None
    method: str = None
    prize_table_name: str = None
    choice_prize_table_script_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateLotteryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_lottery_name(self, lottery_name: str) -> UpdateLotteryModelMasterRequest:
        self.lottery_name = lottery_name
        return self

    def with_description(self, description: str) -> UpdateLotteryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateLotteryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_mode(self, mode: str) -> UpdateLotteryModelMasterRequest:
        self.mode = mode
        return self

    def with_method(self, method: str) -> UpdateLotteryModelMasterRequest:
        self.method = method
        return self

    def with_prize_table_name(self, prize_table_name: str) -> UpdateLotteryModelMasterRequest:
        self.prize_table_name = prize_table_name
        return self

    def with_choice_prize_table_script_id(self, choice_prize_table_script_id: str) -> UpdateLotteryModelMasterRequest:
        self.choice_prize_table_script_id = choice_prize_table_script_id
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
    ) -> Optional[UpdateLotteryModelMasterRequest]:
        if data is None:
            return None
        return UpdateLotteryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_lottery_name(data.get('lotteryName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_mode(data.get('mode'))\
            .with_method(data.get('method'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_choice_prize_table_script_id(data.get('choicePrizeTableScriptId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "lotteryName": self.lottery_name,
            "description": self.description,
            "metadata": self.metadata,
            "mode": self.mode,
            "method": self.method,
            "prizeTableName": self.prize_table_name,
            "choicePrizeTableScriptId": self.choice_prize_table_script_id,
        }


class DeleteLotteryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    lottery_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteLotteryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_lottery_name(self, lottery_name: str) -> DeleteLotteryModelMasterRequest:
        self.lottery_name = lottery_name
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
    ) -> Optional[DeleteLotteryModelMasterRequest]:
        if data is None:
            return None
        return DeleteLotteryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_lottery_name(data.get('lotteryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "lotteryName": self.lottery_name,
        }


class DescribePrizeTableMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribePrizeTableMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribePrizeTableMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribePrizeTableMastersRequest:
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
    ) -> Optional[DescribePrizeTableMastersRequest]:
        if data is None:
            return None
        return DescribePrizeTableMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreatePrizeTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    prizes: List[Prize] = None

    def with_namespace_name(self, namespace_name: str) -> CreatePrizeTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreatePrizeTableMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreatePrizeTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreatePrizeTableMasterRequest:
        self.metadata = metadata
        return self

    def with_prizes(self, prizes: List[Prize]) -> CreatePrizeTableMasterRequest:
        self.prizes = prizes
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
    ) -> Optional[CreatePrizeTableMasterRequest]:
        if data is None:
            return None
        return CreatePrizeTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_prizes([
                Prize.from_dict(data.get('prizes')[i])
                for i in range(len(data.get('prizes')) if data.get('prizes') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "prizes": [
                self.prizes[i].to_dict() if self.prizes[i] else None
                for i in range(len(self.prizes) if self.prizes else 0)
            ],
        }


class GetPrizeTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPrizeTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> GetPrizeTableMasterRequest:
        self.prize_table_name = prize_table_name
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
    ) -> Optional[GetPrizeTableMasterRequest]:
        if data is None:
            return None
        return GetPrizeTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
        }


class UpdatePrizeTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None
    description: str = None
    metadata: str = None
    prizes: List[Prize] = None

    def with_namespace_name(self, namespace_name: str) -> UpdatePrizeTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> UpdatePrizeTableMasterRequest:
        self.prize_table_name = prize_table_name
        return self

    def with_description(self, description: str) -> UpdatePrizeTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdatePrizeTableMasterRequest:
        self.metadata = metadata
        return self

    def with_prizes(self, prizes: List[Prize]) -> UpdatePrizeTableMasterRequest:
        self.prizes = prizes
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
    ) -> Optional[UpdatePrizeTableMasterRequest]:
        if data is None:
            return None
        return UpdatePrizeTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_prizes([
                Prize.from_dict(data.get('prizes')[i])
                for i in range(len(data.get('prizes')) if data.get('prizes') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
            "description": self.description,
            "metadata": self.metadata,
            "prizes": [
                self.prizes[i].to_dict() if self.prizes[i] else None
                for i in range(len(self.prizes) if self.prizes else 0)
            ],
        }


class DeletePrizeTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeletePrizeTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> DeletePrizeTableMasterRequest:
        self.prize_table_name = prize_table_name
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
    ) -> Optional[DeletePrizeTableMasterRequest]:
        if data is None:
            return None
        return DeletePrizeTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
        }


class DescribeBoxesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBoxesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeBoxesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeBoxesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBoxesRequest:
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
    ) -> Optional[DescribeBoxesRequest]:
        if data is None:
            return None
        return DescribeBoxesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeBoxesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBoxesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeBoxesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeBoxesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBoxesByUserIdRequest:
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
    ) -> Optional[DescribeBoxesByUserIdRequest]:
        if data is None:
            return None
        return DescribeBoxesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetBoxRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBoxRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> GetBoxRequest:
        self.prize_table_name = prize_table_name
        return self

    def with_access_token(self, access_token: str) -> GetBoxRequest:
        self.access_token = access_token
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
    ) -> Optional[GetBoxRequest]:
        if data is None:
            return None
        return GetBoxRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
            "accessToken": self.access_token,
        }


class GetBoxByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBoxByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> GetBoxByUserIdRequest:
        self.prize_table_name = prize_table_name
        return self

    def with_user_id(self, user_id: str) -> GetBoxByUserIdRequest:
        self.user_id = user_id
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
    ) -> Optional[GetBoxByUserIdRequest]:
        if data is None:
            return None
        return GetBoxByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
            "userId": self.user_id,
        }


class ResetBoxRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> ResetBoxRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> ResetBoxRequest:
        self.prize_table_name = prize_table_name
        return self

    def with_access_token(self, access_token: str) -> ResetBoxRequest:
        self.access_token = access_token
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
    ) -> Optional[ResetBoxRequest]:
        if data is None:
            return None
        return ResetBoxRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
            "accessToken": self.access_token,
        }


class ResetBoxByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ResetBoxByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> ResetBoxByUserIdRequest:
        self.prize_table_name = prize_table_name
        return self

    def with_user_id(self, user_id: str) -> ResetBoxByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ResetBoxByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[ResetBoxByUserIdRequest]:
        if data is None:
            return None
        return ResetBoxByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
            "userId": self.user_id,
        }


class DescribeLotteryModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeLotteryModelsRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DescribeLotteryModelsRequest]:
        if data is None:
            return None
        return DescribeLotteryModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetLotteryModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    lottery_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetLotteryModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_lottery_name(self, lottery_name: str) -> GetLotteryModelRequest:
        self.lottery_name = lottery_name
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
    ) -> Optional[GetLotteryModelRequest]:
        if data is None:
            return None
        return GetLotteryModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_lottery_name(data.get('lotteryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "lotteryName": self.lottery_name,
        }


class DescribePrizeTablesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribePrizeTablesRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DescribePrizeTablesRequest]:
        if data is None:
            return None
        return DescribePrizeTablesRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetPrizeTableRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    prize_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPrizeTableRequest:
        self.namespace_name = namespace_name
        return self

    def with_prize_table_name(self, prize_table_name: str) -> GetPrizeTableRequest:
        self.prize_table_name = prize_table_name
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
    ) -> Optional[GetPrizeTableRequest]:
        if data is None:
            return None
        return GetPrizeTableRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_prize_table_name(data.get('prizeTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "prizeTableName": self.prize_table_name,
        }


class DrawByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    lottery_name: str = None
    user_id: str = None
    count: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DrawByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_lottery_name(self, lottery_name: str) -> DrawByUserIdRequest:
        self.lottery_name = lottery_name
        return self

    def with_user_id(self, user_id: str) -> DrawByUserIdRequest:
        self.user_id = user_id
        return self

    def with_count(self, count: int) -> DrawByUserIdRequest:
        self.count = count
        return self

    def with_config(self, config: List[Config]) -> DrawByUserIdRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DrawByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DrawByUserIdRequest]:
        if data is None:
            return None
        return DrawByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_lottery_name(data.get('lotteryName'))\
            .with_user_id(data.get('userId'))\
            .with_count(data.get('count'))\
            .with_config([
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')) if data.get('config') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "lotteryName": self.lottery_name,
            "userId": self.user_id,
            "count": self.count,
            "config": [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config) if self.config else 0)
            ],
        }


class DrawByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DrawByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DrawByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[DrawByStampSheetRequest]:
        if data is None:
            return None
        return DrawByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DescribeProbabilitiesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    lottery_name: str = None
    access_token: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeProbabilitiesRequest:
        self.namespace_name = namespace_name
        return self

    def with_lottery_name(self, lottery_name: str) -> DescribeProbabilitiesRequest:
        self.lottery_name = lottery_name
        return self

    def with_access_token(self, access_token: str) -> DescribeProbabilitiesRequest:
        self.access_token = access_token
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
    ) -> Optional[DescribeProbabilitiesRequest]:
        if data is None:
            return None
        return DescribeProbabilitiesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_lottery_name(data.get('lotteryName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "lotteryName": self.lottery_name,
            "accessToken": self.access_token,
        }


class DescribeProbabilitiesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    lottery_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeProbabilitiesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_lottery_name(self, lottery_name: str) -> DescribeProbabilitiesByUserIdRequest:
        self.lottery_name = lottery_name
        return self

    def with_user_id(self, user_id: str) -> DescribeProbabilitiesByUserIdRequest:
        self.user_id = user_id
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
    ) -> Optional[DescribeProbabilitiesByUserIdRequest]:
        if data is None:
            return None
        return DescribeProbabilitiesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_lottery_name(data.get('lotteryName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "lotteryName": self.lottery_name,
            "userId": self.user_id,
        }


class ExportMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> ExportMasterRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[ExportMasterRequest]:
        if data is None:
            return None
        return ExportMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCurrentLotteryMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentLotteryMasterRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetCurrentLotteryMasterRequest]:
        if data is None:
            return None
        return GetCurrentLotteryMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentLotteryMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentLotteryMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentLotteryMasterRequest:
        self.settings = settings
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
    ) -> Optional[UpdateCurrentLotteryMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentLotteryMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentLotteryMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentLotteryMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentLotteryMasterFromGitHubRequest:
        self.checkout_setting = checkout_setting
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
    ) -> Optional[UpdateCurrentLotteryMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentLotteryMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }