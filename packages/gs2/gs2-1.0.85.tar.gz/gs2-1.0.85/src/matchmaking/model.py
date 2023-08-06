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


class TimeSpan(core.Gs2Model):
    days: int = None
    hours: int = None
    minutes: int = None

    def with_days(self, days: int) -> TimeSpan:
        self.days = days
        return self

    def with_hours(self, hours: int) -> TimeSpan:
        self.hours = hours
        return self

    def with_minutes(self, minutes: int) -> TimeSpan:
        self.minutes = minutes
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
    ) -> Optional[TimeSpan]:
        if data is None:
            return None
        return TimeSpan()\
            .with_days(data.get('days'))\
            .with_hours(data.get('hours'))\
            .with_minutes(data.get('minutes'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes,
        }


class Vote(core.Gs2Model):
    vote_id: str = None
    rating_name: str = None
    gathering_name: str = None
    written_ballots: List[WrittenBallot] = None
    created_at: int = None
    updated_at: int = None

    def with_vote_id(self, vote_id: str) -> Vote:
        self.vote_id = vote_id
        return self

    def with_rating_name(self, rating_name: str) -> Vote:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> Vote:
        self.gathering_name = gathering_name
        return self

    def with_written_ballots(self, written_ballots: List[WrittenBallot]) -> Vote:
        self.written_ballots = written_ballots
        return self

    def with_created_at(self, created_at: int) -> Vote:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Vote:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rating_name,
        gathering_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:matchmaking:{namespaceName}:vote:{ratingName}:{gatheringName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            ratingName=rating_name,
            gatheringName=gathering_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):vote:(?P<ratingName>.+):(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):vote:(?P<ratingName>.+):(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):vote:(?P<ratingName>.+):(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rating_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):vote:(?P<ratingName>.+):(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('rating_name')

    @classmethod
    def get_gathering_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):vote:(?P<ratingName>.+):(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('gathering_name')

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
    ) -> Optional[Vote]:
        if data is None:
            return None
        return Vote()\
            .with_vote_id(data.get('voteId'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_written_ballots([
                WrittenBallot.from_dict(data.get('writtenBallots')[i])
                for i in range(len(data.get('writtenBallots')) if data.get('writtenBallots') else 0)
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voteId": self.vote_id,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
            "writtenBallots": [
                self.written_ballots[i].to_dict() if self.written_ballots[i] else None
                for i in range(len(self.written_ballots) if self.written_ballots else 0)
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class WrittenBallot(core.Gs2Model):
    ballot: Ballot = None
    game_results: List[GameResult] = None

    def with_ballot(self, ballot: Ballot) -> WrittenBallot:
        self.ballot = ballot
        return self

    def with_game_results(self, game_results: List[GameResult]) -> WrittenBallot:
        self.game_results = game_results
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
    ) -> Optional[WrittenBallot]:
        if data is None:
            return None
        return WrittenBallot()\
            .with_ballot(Ballot.from_dict(data.get('ballot')))\
            .with_game_results([
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')) if data.get('gameResults') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ballot": self.ballot.to_dict() if self.ballot else None,
            "gameResults": [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results) if self.game_results else 0)
            ],
        }


class SignedBallot(core.Gs2Model):
    body: str = None
    signature: str = None

    def with_body(self, body: str) -> SignedBallot:
        self.body = body
        return self

    def with_signature(self, signature: str) -> SignedBallot:
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
    ) -> Optional[SignedBallot]:
        if data is None:
            return None
        return SignedBallot()\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body": self.body,
            "signature": self.signature,
        }


class Ballot(core.Gs2Model):
    user_id: str = None
    rating_name: str = None
    gathering_name: str = None
    number_of_player: int = None

    def with_user_id(self, user_id: str) -> Ballot:
        self.user_id = user_id
        return self

    def with_rating_name(self, rating_name: str) -> Ballot:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> Ballot:
        self.gathering_name = gathering_name
        return self

    def with_number_of_player(self, number_of_player: int) -> Ballot:
        self.number_of_player = number_of_player
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
    ) -> Optional[Ballot]:
        if data is None:
            return None
        return Ballot()\
            .with_user_id(data.get('userId'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_number_of_player(data.get('numberOfPlayer'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
            "numberOfPlayer": self.number_of_player,
        }


class GameResult(core.Gs2Model):
    rank: int = None
    user_id: str = None

    def with_rank(self, rank: int) -> GameResult:
        self.rank = rank
        return self

    def with_user_id(self, user_id: str) -> GameResult:
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
    ) -> Optional[GameResult]:
        if data is None:
            return None
        return GameResult()\
            .with_rank(data.get('rank'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "userId": self.user_id,
        }


class Rating(core.Gs2Model):
    rating_id: str = None
    name: str = None
    user_id: str = None
    rate_value: float = None
    created_at: int = None
    updated_at: int = None

    def with_rating_id(self, rating_id: str) -> Rating:
        self.rating_id = rating_id
        return self

    def with_name(self, name: str) -> Rating:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> Rating:
        self.user_id = user_id
        return self

    def with_rate_value(self, rate_value: float) -> Rating:
        self.rate_value = rate_value
        return self

    def with_created_at(self, created_at: int) -> Rating:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Rating:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        rating_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:matchmaking:{namespaceName}:user:{userId}:rating:{ratingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            ratingName=rating_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):user:(?P<userId>.+):rating:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):user:(?P<userId>.+):rating:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):user:(?P<userId>.+):rating:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):user:(?P<userId>.+):rating:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_rating_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):user:(?P<userId>.+):rating:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('rating_name')

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
    ) -> Optional[Rating]:
        if data is None:
            return None
        return Rating()\
            .with_rating_id(data.get('ratingId'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_rate_value(data.get('rateValue'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ratingId": self.rating_id,
            "name": self.name,
            "userId": self.user_id,
            "rateValue": self.rate_value,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Player(core.Gs2Model):
    user_id: str = None
    attributes: List[Attribute] = None
    role_name: str = None
    deny_user_ids: List[str] = None

    def with_user_id(self, user_id: str) -> Player:
        self.user_id = user_id
        return self

    def with_attributes(self, attributes: List[Attribute]) -> Player:
        self.attributes = attributes
        return self

    def with_role_name(self, role_name: str) -> Player:
        self.role_name = role_name
        return self

    def with_deny_user_ids(self, deny_user_ids: List[str]) -> Player:
        self.deny_user_ids = deny_user_ids
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
    ) -> Optional[Player]:
        if data is None:
            return None
        return Player()\
            .with_user_id(data.get('userId'))\
            .with_attributes([
                Attribute.from_dict(data.get('attributes')[i])
                for i in range(len(data.get('attributes')) if data.get('attributes') else 0)
            ])\
            .with_role_name(data.get('roleName'))\
            .with_deny_user_ids([
                data.get('denyUserIds')[i]
                for i in range(len(data.get('denyUserIds')) if data.get('denyUserIds') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "attributes": [
                self.attributes[i].to_dict() if self.attributes[i] else None
                for i in range(len(self.attributes) if self.attributes else 0)
            ],
            "roleName": self.role_name,
            "denyUserIds": [
                self.deny_user_ids[i]
                for i in range(len(self.deny_user_ids) if self.deny_user_ids else 0)
            ],
        }


class Attribute(core.Gs2Model):
    name: str = None
    value: int = None

    def with_name(self, name: str) -> Attribute:
        self.name = name
        return self

    def with_value(self, value: int) -> Attribute:
        self.value = value
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
    ) -> Optional[Attribute]:
        if data is None:
            return None
        return Attribute()\
            .with_name(data.get('name'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
        }


class CapacityOfRole(core.Gs2Model):
    role_name: str = None
    role_aliases: List[str] = None
    capacity: int = None
    participants: List[Player] = None

    def with_role_name(self, role_name: str) -> CapacityOfRole:
        self.role_name = role_name
        return self

    def with_role_aliases(self, role_aliases: List[str]) -> CapacityOfRole:
        self.role_aliases = role_aliases
        return self

    def with_capacity(self, capacity: int) -> CapacityOfRole:
        self.capacity = capacity
        return self

    def with_participants(self, participants: List[Player]) -> CapacityOfRole:
        self.participants = participants
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
    ) -> Optional[CapacityOfRole]:
        if data is None:
            return None
        return CapacityOfRole()\
            .with_role_name(data.get('roleName'))\
            .with_role_aliases([
                data.get('roleAliases')[i]
                for i in range(len(data.get('roleAliases')) if data.get('roleAliases') else 0)
            ])\
            .with_capacity(data.get('capacity'))\
            .with_participants([
                Player.from_dict(data.get('participants')[i])
                for i in range(len(data.get('participants')) if data.get('participants') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "roleName": self.role_name,
            "roleAliases": [
                self.role_aliases[i]
                for i in range(len(self.role_aliases) if self.role_aliases else 0)
            ],
            "capacity": self.capacity,
            "participants": [
                self.participants[i].to_dict() if self.participants[i] else None
                for i in range(len(self.participants) if self.participants else 0)
            ],
        }


class AttributeRange(core.Gs2Model):
    name: str = None
    min: int = None
    max: int = None

    def with_name(self, name: str) -> AttributeRange:
        self.name = name
        return self

    def with_min(self, min: int) -> AttributeRange:
        self.min = min
        return self

    def with_max(self, max: int) -> AttributeRange:
        self.max = max
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
    ) -> Optional[AttributeRange]:
        if data is None:
            return None
        return AttributeRange()\
            .with_name(data.get('name'))\
            .with_min(data.get('min'))\
            .with_max(data.get('max'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "min": self.min,
            "max": self.max,
        }


class GitHubCheckoutSetting(core.Gs2Model):
    api_key_id: str = None
    repository_name: str = None
    source_path: str = None
    reference_type: str = None
    commit_hash: str = None
    branch_name: str = None
    tag_name: str = None

    def with_api_key_id(self, api_key_id: str) -> GitHubCheckoutSetting:
        self.api_key_id = api_key_id
        return self

    def with_repository_name(self, repository_name: str) -> GitHubCheckoutSetting:
        self.repository_name = repository_name
        return self

    def with_source_path(self, source_path: str) -> GitHubCheckoutSetting:
        self.source_path = source_path
        return self

    def with_reference_type(self, reference_type: str) -> GitHubCheckoutSetting:
        self.reference_type = reference_type
        return self

    def with_commit_hash(self, commit_hash: str) -> GitHubCheckoutSetting:
        self.commit_hash = commit_hash
        return self

    def with_branch_name(self, branch_name: str) -> GitHubCheckoutSetting:
        self.branch_name = branch_name
        return self

    def with_tag_name(self, tag_name: str) -> GitHubCheckoutSetting:
        self.tag_name = tag_name
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
    ) -> Optional[GitHubCheckoutSetting]:
        if data is None:
            return None
        return GitHubCheckoutSetting()\
            .with_api_key_id(data.get('apiKeyId'))\
            .with_repository_name(data.get('repositoryName'))\
            .with_source_path(data.get('sourcePath'))\
            .with_reference_type(data.get('referenceType'))\
            .with_commit_hash(data.get('commitHash'))\
            .with_branch_name(data.get('branchName'))\
            .with_tag_name(data.get('tagName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiKeyId": self.api_key_id,
            "repositoryName": self.repository_name,
            "sourcePath": self.source_path,
            "referenceType": self.reference_type,
            "commitHash": self.commit_hash,
            "branchName": self.branch_name,
            "tagName": self.tag_name,
        }


class LogSetting(core.Gs2Model):
    logging_namespace_id: str = None

    def with_logging_namespace_id(self, logging_namespace_id: str) -> LogSetting:
        self.logging_namespace_id = logging_namespace_id
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
    ) -> Optional[LogSetting]:
        if data is None:
            return None
        return LogSetting()\
            .with_logging_namespace_id(data.get('loggingNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loggingNamespaceId": self.logging_namespace_id,
        }


class NotificationSetting(core.Gs2Model):
    gateway_namespace_id: str = None
    enable_transfer_mobile_notification: bool = None
    sound: str = None

    def with_gateway_namespace_id(self, gateway_namespace_id: str) -> NotificationSetting:
        self.gateway_namespace_id = gateway_namespace_id
        return self

    def with_enable_transfer_mobile_notification(self, enable_transfer_mobile_notification: bool) -> NotificationSetting:
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        return self

    def with_sound(self, sound: str) -> NotificationSetting:
        self.sound = sound
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
    ) -> Optional[NotificationSetting]:
        if data is None:
            return None
        return NotificationSetting()\
            .with_gateway_namespace_id(data.get('gatewayNamespaceId'))\
            .with_enable_transfer_mobile_notification(data.get('enableTransferMobileNotification'))\
            .with_sound(data.get('sound'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatewayNamespaceId": self.gateway_namespace_id,
            "enableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "sound": self.sound,
        }


class CurrentRatingModelMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentRatingModelMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentRatingModelMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:matchmaking:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

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
    ) -> Optional[CurrentRatingModelMaster]:
        if data is None:
            return None
        return CurrentRatingModelMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class RatingModel(core.Gs2Model):
    rating_model_id: str = None
    name: str = None
    metadata: str = None
    volatility: int = None

    def with_rating_model_id(self, rating_model_id: str) -> RatingModel:
        self.rating_model_id = rating_model_id
        return self

    def with_name(self, name: str) -> RatingModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RatingModel:
        self.metadata = metadata
        return self

    def with_volatility(self, volatility: int) -> RatingModel:
        self.volatility = volatility
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rating_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:matchmaking:{namespaceName}:model:{ratingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            ratingName=rating_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rating_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('rating_name')

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
    ) -> Optional[RatingModel]:
        if data is None:
            return None
        return RatingModel()\
            .with_rating_model_id(data.get('ratingModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_volatility(data.get('volatility'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ratingModelId": self.rating_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "volatility": self.volatility,
        }


class RatingModelMaster(core.Gs2Model):
    rating_model_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    volatility: int = None
    created_at: int = None
    updated_at: int = None

    def with_rating_model_id(self, rating_model_id: str) -> RatingModelMaster:
        self.rating_model_id = rating_model_id
        return self

    def with_name(self, name: str) -> RatingModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RatingModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> RatingModelMaster:
        self.description = description
        return self

    def with_volatility(self, volatility: int) -> RatingModelMaster:
        self.volatility = volatility
        return self

    def with_created_at(self, created_at: int) -> RatingModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RatingModelMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rating_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:matchmaking:{namespaceName}:model:{ratingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            ratingName=rating_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rating_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):model:(?P<ratingName>.+)', grn)
        if match is None:
            return None
        return match.group('rating_name')

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
    ) -> Optional[RatingModelMaster]:
        if data is None:
            return None
        return RatingModelMaster()\
            .with_rating_model_id(data.get('ratingModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_volatility(data.get('volatility'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ratingModelId": self.rating_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "volatility": self.volatility,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Gathering(core.Gs2Model):
    gathering_id: str = None
    name: str = None
    attribute_ranges: List[AttributeRange] = None
    capacity_of_roles: List[CapacityOfRole] = None
    allow_user_ids: List[str] = None
    metadata: str = None
    expires_at: int = None
    created_at: int = None
    updated_at: int = None

    def with_gathering_id(self, gathering_id: str) -> Gathering:
        self.gathering_id = gathering_id
        return self

    def with_name(self, name: str) -> Gathering:
        self.name = name
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> Gathering:
        self.attribute_ranges = attribute_ranges
        return self

    def with_capacity_of_roles(self, capacity_of_roles: List[CapacityOfRole]) -> Gathering:
        self.capacity_of_roles = capacity_of_roles
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> Gathering:
        self.allow_user_ids = allow_user_ids
        return self

    def with_metadata(self, metadata: str) -> Gathering:
        self.metadata = metadata
        return self

    def with_expires_at(self, expires_at: int) -> Gathering:
        self.expires_at = expires_at
        return self

    def with_created_at(self, created_at: int) -> Gathering:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Gathering:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        gathering_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:matchmaking:{namespaceName}:gathering:{gatheringName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            gatheringName=gathering_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):gathering:(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):gathering:(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):gathering:(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_gathering_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+):gathering:(?P<gatheringName>.+)', grn)
        if match is None:
            return None
        return match.group('gathering_name')

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
    ) -> Optional[Gathering]:
        if data is None:
            return None
        return Gathering()\
            .with_gathering_id(data.get('gatheringId'))\
            .with_name(data.get('name'))\
            .with_attribute_ranges([
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')) if data.get('attributeRanges') else 0)
            ])\
            .with_capacity_of_roles([
                CapacityOfRole.from_dict(data.get('capacityOfRoles')[i])
                for i in range(len(data.get('capacityOfRoles')) if data.get('capacityOfRoles') else 0)
            ])\
            .with_allow_user_ids([
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')) if data.get('allowUserIds') else 0)
            ])\
            .with_metadata(data.get('metadata'))\
            .with_expires_at(data.get('expiresAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatheringId": self.gathering_id,
            "name": self.name,
            "attributeRanges": [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges) if self.attribute_ranges else 0)
            ],
            "capacityOfRoles": [
                self.capacity_of_roles[i].to_dict() if self.capacity_of_roles[i] else None
                for i in range(len(self.capacity_of_roles) if self.capacity_of_roles else 0)
            ],
            "allowUserIds": [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids) if self.allow_user_ids else 0)
            ],
            "metadata": self.metadata,
            "expiresAt": self.expires_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    enable_rating: bool = None
    create_gathering_trigger_type: str = None
    create_gathering_trigger_realtime_namespace_id: str = None
    create_gathering_trigger_script_id: str = None
    complete_matchmaking_trigger_type: str = None
    complete_matchmaking_trigger_realtime_namespace_id: str = None
    complete_matchmaking_trigger_script_id: str = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    complete_notification: NotificationSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_enable_rating(self, enable_rating: bool) -> Namespace:
        self.enable_rating = enable_rating
        return self

    def with_create_gathering_trigger_type(self, create_gathering_trigger_type: str) -> Namespace:
        self.create_gathering_trigger_type = create_gathering_trigger_type
        return self

    def with_create_gathering_trigger_realtime_namespace_id(self, create_gathering_trigger_realtime_namespace_id: str) -> Namespace:
        self.create_gathering_trigger_realtime_namespace_id = create_gathering_trigger_realtime_namespace_id
        return self

    def with_create_gathering_trigger_script_id(self, create_gathering_trigger_script_id: str) -> Namespace:
        self.create_gathering_trigger_script_id = create_gathering_trigger_script_id
        return self

    def with_complete_matchmaking_trigger_type(self, complete_matchmaking_trigger_type: str) -> Namespace:
        self.complete_matchmaking_trigger_type = complete_matchmaking_trigger_type
        return self

    def with_complete_matchmaking_trigger_realtime_namespace_id(self, complete_matchmaking_trigger_realtime_namespace_id: str) -> Namespace:
        self.complete_matchmaking_trigger_realtime_namespace_id = complete_matchmaking_trigger_realtime_namespace_id
        return self

    def with_complete_matchmaking_trigger_script_id(self, complete_matchmaking_trigger_script_id: str) -> Namespace:
        self.complete_matchmaking_trigger_script_id = complete_matchmaking_trigger_script_id
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> Namespace:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> Namespace:
        self.leave_notification = leave_notification
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> Namespace:
        self.complete_notification = complete_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> Namespace:
        self.log_setting = log_setting
        return self

    def with_created_at(self, created_at: int) -> Namespace:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Namespace:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:matchmaking:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):matchmaking:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

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
    ) -> Optional[Namespace]:
        if data is None:
            return None
        return Namespace()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_enable_rating(data.get('enableRating'))\
            .with_create_gathering_trigger_type(data.get('createGatheringTriggerType'))\
            .with_create_gathering_trigger_realtime_namespace_id(data.get('createGatheringTriggerRealtimeNamespaceId'))\
            .with_create_gathering_trigger_script_id(data.get('createGatheringTriggerScriptId'))\
            .with_complete_matchmaking_trigger_type(data.get('completeMatchmakingTriggerType'))\
            .with_complete_matchmaking_trigger_realtime_namespace_id(data.get('completeMatchmakingTriggerRealtimeNamespaceId'))\
            .with_complete_matchmaking_trigger_script_id(data.get('completeMatchmakingTriggerScriptId'))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "enableRating": self.enable_rating,
            "createGatheringTriggerType": self.create_gathering_trigger_type,
            "createGatheringTriggerRealtimeNamespaceId": self.create_gathering_trigger_realtime_namespace_id,
            "createGatheringTriggerScriptId": self.create_gathering_trigger_script_id,
            "completeMatchmakingTriggerType": self.complete_matchmaking_trigger_type,
            "completeMatchmakingTriggerRealtimeNamespaceId": self.complete_matchmaking_trigger_realtime_namespace_id,
            "completeMatchmakingTriggerScriptId": self.complete_matchmaking_trigger_script_id,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }