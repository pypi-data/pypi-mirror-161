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

from matchmaking.model import *


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


class DescribeGatheringsResult(core.Gs2Result):
    items: List[Gathering] = None
    next_page_token: str = None

    def with_items(self, items: List[Gathering]) -> DescribeGatheringsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGatheringsResult:
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
    ) -> Optional[DescribeGatheringsResult]:
        if data is None:
            return None
        return DescribeGatheringsResult()\
            .with_items([
                Gathering.from_dict(data.get('items')[i])
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


class CreateGatheringResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> CreateGatheringResult:
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
    ) -> Optional[CreateGatheringResult]:
        if data is None:
            return None
        return CreateGatheringResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateGatheringByUserIdResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> CreateGatheringByUserIdResult:
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
    ) -> Optional[CreateGatheringByUserIdResult]:
        if data is None:
            return None
        return CreateGatheringByUserIdResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateGatheringResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> UpdateGatheringResult:
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
    ) -> Optional[UpdateGatheringResult]:
        if data is None:
            return None
        return UpdateGatheringResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateGatheringByUserIdResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> UpdateGatheringByUserIdResult:
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
    ) -> Optional[UpdateGatheringByUserIdResult]:
        if data is None:
            return None
        return UpdateGatheringByUserIdResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DoMatchmakingByPlayerResult(core.Gs2Result):
    item: Gathering = None
    matchmaking_context_token: str = None

    def with_item(self, item: Gathering) -> DoMatchmakingByPlayerResult:
        self.item = item
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingByPlayerResult:
        self.matchmaking_context_token = matchmaking_context_token
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
    ) -> Optional[DoMatchmakingByPlayerResult]:
        if data is None:
            return None
        return DoMatchmakingByPlayerResult()\
            .with_item(Gathering.from_dict(data.get('item')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class DoMatchmakingResult(core.Gs2Result):
    item: Gathering = None
    matchmaking_context_token: str = None

    def with_item(self, item: Gathering) -> DoMatchmakingResult:
        self.item = item
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingResult:
        self.matchmaking_context_token = matchmaking_context_token
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
    ) -> Optional[DoMatchmakingResult]:
        if data is None:
            return None
        return DoMatchmakingResult()\
            .with_item(Gathering.from_dict(data.get('item')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class DoMatchmakingByUserIdResult(core.Gs2Result):
    item: Gathering = None
    matchmaking_context_token: str = None

    def with_item(self, item: Gathering) -> DoMatchmakingByUserIdResult:
        self.item = item
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingByUserIdResult:
        self.matchmaking_context_token = matchmaking_context_token
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
    ) -> Optional[DoMatchmakingByUserIdResult]:
        if data is None:
            return None
        return DoMatchmakingByUserIdResult()\
            .with_item(Gathering.from_dict(data.get('item')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class GetGatheringResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> GetGatheringResult:
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
    ) -> Optional[GetGatheringResult]:
        if data is None:
            return None
        return GetGatheringResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CancelMatchmakingResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> CancelMatchmakingResult:
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
    ) -> Optional[CancelMatchmakingResult]:
        if data is None:
            return None
        return CancelMatchmakingResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CancelMatchmakingByUserIdResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> CancelMatchmakingByUserIdResult:
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
    ) -> Optional[CancelMatchmakingByUserIdResult]:
        if data is None:
            return None
        return CancelMatchmakingByUserIdResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGatheringResult(core.Gs2Result):
    item: Gathering = None

    def with_item(self, item: Gathering) -> DeleteGatheringResult:
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
    ) -> Optional[DeleteGatheringResult]:
        if data is None:
            return None
        return DeleteGatheringResult()\
            .with_item(Gathering.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRatingModelMastersResult(core.Gs2Result):
    items: List[RatingModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[RatingModelMaster]) -> DescribeRatingModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRatingModelMastersResult:
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
    ) -> Optional[DescribeRatingModelMastersResult]:
        if data is None:
            return None
        return DescribeRatingModelMastersResult()\
            .with_items([
                RatingModelMaster.from_dict(data.get('items')[i])
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


class CreateRatingModelMasterResult(core.Gs2Result):
    item: RatingModelMaster = None

    def with_item(self, item: RatingModelMaster) -> CreateRatingModelMasterResult:
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
    ) -> Optional[CreateRatingModelMasterResult]:
        if data is None:
            return None
        return CreateRatingModelMasterResult()\
            .with_item(RatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetRatingModelMasterResult(core.Gs2Result):
    item: RatingModelMaster = None

    def with_item(self, item: RatingModelMaster) -> GetRatingModelMasterResult:
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
    ) -> Optional[GetRatingModelMasterResult]:
        if data is None:
            return None
        return GetRatingModelMasterResult()\
            .with_item(RatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateRatingModelMasterResult(core.Gs2Result):
    item: RatingModelMaster = None

    def with_item(self, item: RatingModelMaster) -> UpdateRatingModelMasterResult:
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
    ) -> Optional[UpdateRatingModelMasterResult]:
        if data is None:
            return None
        return UpdateRatingModelMasterResult()\
            .with_item(RatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteRatingModelMasterResult(core.Gs2Result):
    item: RatingModelMaster = None

    def with_item(self, item: RatingModelMaster) -> DeleteRatingModelMasterResult:
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
    ) -> Optional[DeleteRatingModelMasterResult]:
        if data is None:
            return None
        return DeleteRatingModelMasterResult()\
            .with_item(RatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRatingModelsResult(core.Gs2Result):
    items: List[RatingModel] = None

    def with_items(self, items: List[RatingModel]) -> DescribeRatingModelsResult:
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
    ) -> Optional[DescribeRatingModelsResult]:
        if data is None:
            return None
        return DescribeRatingModelsResult()\
            .with_items([
                RatingModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
        }


class GetRatingModelResult(core.Gs2Result):
    item: RatingModel = None

    def with_item(self, item: RatingModel) -> GetRatingModelResult:
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
    ) -> Optional[GetRatingModelResult]:
        if data is None:
            return None
        return GetRatingModelResult()\
            .with_item(RatingModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentRatingModelMaster = None

    def with_item(self, item: CurrentRatingModelMaster) -> ExportMasterResult:
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
            .with_item(CurrentRatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentRatingModelMasterResult(core.Gs2Result):
    item: CurrentRatingModelMaster = None

    def with_item(self, item: CurrentRatingModelMaster) -> GetCurrentRatingModelMasterResult:
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
    ) -> Optional[GetCurrentRatingModelMasterResult]:
        if data is None:
            return None
        return GetCurrentRatingModelMasterResult()\
            .with_item(CurrentRatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentRatingModelMasterResult(core.Gs2Result):
    item: CurrentRatingModelMaster = None

    def with_item(self, item: CurrentRatingModelMaster) -> UpdateCurrentRatingModelMasterResult:
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
    ) -> Optional[UpdateCurrentRatingModelMasterResult]:
        if data is None:
            return None
        return UpdateCurrentRatingModelMasterResult()\
            .with_item(CurrentRatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentRatingModelMasterFromGitHubResult(core.Gs2Result):
    item: CurrentRatingModelMaster = None

    def with_item(self, item: CurrentRatingModelMaster) -> UpdateCurrentRatingModelMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentRatingModelMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentRatingModelMasterFromGitHubResult()\
            .with_item(CurrentRatingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRatingsResult(core.Gs2Result):
    items: List[Rating] = None
    next_page_token: str = None

    def with_items(self, items: List[Rating]) -> DescribeRatingsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRatingsResult:
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
    ) -> Optional[DescribeRatingsResult]:
        if data is None:
            return None
        return DescribeRatingsResult()\
            .with_items([
                Rating.from_dict(data.get('items')[i])
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


class DescribeRatingsByUserIdResult(core.Gs2Result):
    items: List[Rating] = None
    next_page_token: str = None

    def with_items(self, items: List[Rating]) -> DescribeRatingsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRatingsByUserIdResult:
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
    ) -> Optional[DescribeRatingsByUserIdResult]:
        if data is None:
            return None
        return DescribeRatingsByUserIdResult()\
            .with_items([
                Rating.from_dict(data.get('items')[i])
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


class GetRatingResult(core.Gs2Result):
    item: Rating = None

    def with_item(self, item: Rating) -> GetRatingResult:
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
    ) -> Optional[GetRatingResult]:
        if data is None:
            return None
        return GetRatingResult()\
            .with_item(Rating.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetRatingByUserIdResult(core.Gs2Result):
    item: Rating = None

    def with_item(self, item: Rating) -> GetRatingByUserIdResult:
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
    ) -> Optional[GetRatingByUserIdResult]:
        if data is None:
            return None
        return GetRatingByUserIdResult()\
            .with_item(Rating.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PutResultResult(core.Gs2Result):
    items: List[Rating] = None

    def with_items(self, items: List[Rating]) -> PutResultResult:
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
    ) -> Optional[PutResultResult]:
        if data is None:
            return None
        return PutResultResult()\
            .with_items([
                Rating.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')) if data.get('items') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items) if self.items else 0)
            ],
        }


class DeleteRatingResult(core.Gs2Result):
    item: Rating = None

    def with_item(self, item: Rating) -> DeleteRatingResult:
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
    ) -> Optional[DeleteRatingResult]:
        if data is None:
            return None
        return DeleteRatingResult()\
            .with_item(Rating.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBallotResult(core.Gs2Result):
    item: Ballot = None
    body: str = None
    signature: str = None

    def with_item(self, item: Ballot) -> GetBallotResult:
        self.item = item
        return self

    def with_body(self, body: str) -> GetBallotResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetBallotResult:
        self.signature = signature
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
    ) -> Optional[GetBallotResult]:
        if data is None:
            return None
        return GetBallotResult()\
            .with_item(Ballot.from_dict(data.get('item')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "body": self.body,
            "signature": self.signature,
        }


class GetBallotByUserIdResult(core.Gs2Result):
    item: Ballot = None
    body: str = None
    signature: str = None

    def with_item(self, item: Ballot) -> GetBallotByUserIdResult:
        self.item = item
        return self

    def with_body(self, body: str) -> GetBallotByUserIdResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetBallotByUserIdResult:
        self.signature = signature
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
    ) -> Optional[GetBallotByUserIdResult]:
        if data is None:
            return None
        return GetBallotByUserIdResult()\
            .with_item(Ballot.from_dict(data.get('item')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "body": self.body,
            "signature": self.signature,
        }


class VoteResult(core.Gs2Result):
    item: Ballot = None

    def with_item(self, item: Ballot) -> VoteResult:
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
    ) -> Optional[VoteResult]:
        if data is None:
            return None
        return VoteResult()\
            .with_item(Ballot.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VoteMultipleResult(core.Gs2Result):
    item: Ballot = None

    def with_item(self, item: Ballot) -> VoteMultipleResult:
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
    ) -> Optional[VoteMultipleResult]:
        if data is None:
            return None
        return VoteMultipleResult()\
            .with_item(Ballot.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CommitVoteResult(core.Gs2Result):

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
    ) -> Optional[CommitVoteResult]:
        if data is None:
            return None
        return CommitVoteResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }