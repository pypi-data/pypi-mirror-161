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


class TransactionSetting(core.Gs2Model):
    enable_auto_run: bool = None
    distributor_namespace_id: str = None
    key_id: str = None
    queue_namespace_id: str = None

    def with_enable_auto_run(self, enable_auto_run: bool) -> TransactionSetting:
        self.enable_auto_run = enable_auto_run
        return self

    def with_distributor_namespace_id(self, distributor_namespace_id: str) -> TransactionSetting:
        self.distributor_namespace_id = distributor_namespace_id
        return self

    def with_key_id(self, key_id: str) -> TransactionSetting:
        self.key_id = key_id
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> TransactionSetting:
        self.queue_namespace_id = queue_namespace_id
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
    ) -> Optional[TransactionSetting]:
        if data is None:
            return None
        return TransactionSetting()\
            .with_enable_auto_run(data.get('enableAutoRun'))\
            .with_distributor_namespace_id(data.get('distributorNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enableAutoRun": self.enable_auto_run,
            "distributorNamespaceId": self.distributor_namespace_id,
            "keyId": self.key_id,
            "queueNamespaceId": self.queue_namespace_id,
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


class Config(core.Gs2Model):
    key: str = None
    value: str = None

    def with_key(self, key: str) -> Config:
        self.key = key
        return self

    def with_value(self, value: str) -> Config:
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
    ) -> Optional[Config]:
        if data is None:
            return None
        return Config()\
            .with_key(data.get('key'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
        }


class AcquireAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> AcquireAction:
        self.action = action
        return self

    def with_request(self, request: str) -> AcquireAction:
        self.request = request
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
    ) -> Optional[AcquireAction]:
        if data is None:
            return None
        return AcquireAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class ConsumeAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> ConsumeAction:
        self.action = action
        return self

    def with_request(self, request: str) -> ConsumeAction:
        self.request = request
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
    ) -> Optional[ConsumeAction]:
        if data is None:
            return None
        return ConsumeAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class DisplayItemMaster(core.Gs2Model):
    display_item_id: str = None
    type: str = None
    sales_item_name: str = None
    sales_item_group_name: str = None
    sales_period_event_id: str = None

    def with_display_item_id(self, display_item_id: str) -> DisplayItemMaster:
        self.display_item_id = display_item_id
        return self

    def with_type(self, type: str) -> DisplayItemMaster:
        self.type = type
        return self

    def with_sales_item_name(self, sales_item_name: str) -> DisplayItemMaster:
        self.sales_item_name = sales_item_name
        return self

    def with_sales_item_group_name(self, sales_item_group_name: str) -> DisplayItemMaster:
        self.sales_item_group_name = sales_item_group_name
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> DisplayItemMaster:
        self.sales_period_event_id = sales_period_event_id
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
    ) -> Optional[DisplayItemMaster]:
        if data is None:
            return None
        return DisplayItemMaster()\
            .with_display_item_id(data.get('displayItemId'))\
            .with_type(data.get('type'))\
            .with_sales_item_name(data.get('salesItemName'))\
            .with_sales_item_group_name(data.get('salesItemGroupName'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "displayItemId": self.display_item_id,
            "type": self.type,
            "salesItemName": self.sales_item_name,
            "salesItemGroupName": self.sales_item_group_name,
            "salesPeriodEventId": self.sales_period_event_id,
        }


class DisplayItem(core.Gs2Model):
    display_item_id: str = None
    type: str = None
    sales_item: SalesItem = None
    sales_item_group: SalesItemGroup = None
    sales_period_event_id: str = None

    def with_display_item_id(self, display_item_id: str) -> DisplayItem:
        self.display_item_id = display_item_id
        return self

    def with_type(self, type: str) -> DisplayItem:
        self.type = type
        return self

    def with_sales_item(self, sales_item: SalesItem) -> DisplayItem:
        self.sales_item = sales_item
        return self

    def with_sales_item_group(self, sales_item_group: SalesItemGroup) -> DisplayItem:
        self.sales_item_group = sales_item_group
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> DisplayItem:
        self.sales_period_event_id = sales_period_event_id
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
    ) -> Optional[DisplayItem]:
        if data is None:
            return None
        return DisplayItem()\
            .with_display_item_id(data.get('displayItemId'))\
            .with_type(data.get('type'))\
            .with_sales_item(SalesItem.from_dict(data.get('salesItem')))\
            .with_sales_item_group(SalesItemGroup.from_dict(data.get('salesItemGroup')))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "displayItemId": self.display_item_id,
            "type": self.type,
            "salesItem": self.sales_item.to_dict() if self.sales_item else None,
            "salesItemGroup": self.sales_item_group.to_dict() if self.sales_item_group else None,
            "salesPeriodEventId": self.sales_period_event_id,
        }


class Showcase(core.Gs2Model):
    showcase_id: str = None
    name: str = None
    metadata: str = None
    sales_period_event_id: str = None
    display_items: List[DisplayItem] = None

    def with_showcase_id(self, showcase_id: str) -> Showcase:
        self.showcase_id = showcase_id
        return self

    def with_name(self, name: str) -> Showcase:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> Showcase:
        self.metadata = metadata
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> Showcase:
        self.sales_period_event_id = sales_period_event_id
        return self

    def with_display_items(self, display_items: List[DisplayItem]) -> Showcase:
        self.display_items = display_items
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        showcase_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:showcase:{showcaseName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            showcaseName=showcase_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_showcase_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('showcase_name')

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
    ) -> Optional[Showcase]:
        if data is None:
            return None
        return Showcase()\
            .with_showcase_id(data.get('showcaseId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))\
            .with_display_items([
                DisplayItem.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')) if data.get('displayItems') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "showcaseId": self.showcase_id,
            "name": self.name,
            "metadata": self.metadata,
            "salesPeriodEventId": self.sales_period_event_id,
            "displayItems": [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items) if self.display_items else 0)
            ],
        }


class SalesItemGroup(core.Gs2Model):
    name: str = None
    metadata: str = None
    sales_items: List[SalesItem] = None

    def with_name(self, name: str) -> SalesItemGroup:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SalesItemGroup:
        self.metadata = metadata
        return self

    def with_sales_items(self, sales_items: List[SalesItem]) -> SalesItemGroup:
        self.sales_items = sales_items
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
    ) -> Optional[SalesItemGroup]:
        if data is None:
            return None
        return SalesItemGroup()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_items([
                SalesItem.from_dict(data.get('salesItems')[i])
                for i in range(len(data.get('salesItems')) if data.get('salesItems') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "salesItems": [
                self.sales_items[i].to_dict() if self.sales_items[i] else None
                for i in range(len(self.sales_items) if self.sales_items else 0)
            ],
        }


class SalesItem(core.Gs2Model):
    name: str = None
    metadata: str = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None

    def with_name(self, name: str) -> SalesItem:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SalesItem:
        self.metadata = metadata
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> SalesItem:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> SalesItem:
        self.acquire_actions = acquire_actions
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
    ) -> Optional[SalesItem]:
        if data is None:
            return None
        return SalesItem()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_actions([
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')) if data.get('consumeActions') else 0)
            ])\
            .with_acquire_actions([
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')) if data.get('acquireActions') else 0)
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "consumeActions": [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions) if self.consume_actions else 0)
            ],
            "acquireActions": [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions) if self.acquire_actions else 0)
            ],
        }


class CurrentShowcaseMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentShowcaseMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentShowcaseMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentShowcaseMaster]:
        if data is None:
            return None
        return CurrentShowcaseMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class ShowcaseMaster(core.Gs2Model):
    showcase_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    sales_period_event_id: str = None
    display_items: List[DisplayItemMaster] = None
    created_at: int = None
    updated_at: int = None

    def with_showcase_id(self, showcase_id: str) -> ShowcaseMaster:
        self.showcase_id = showcase_id
        return self

    def with_name(self, name: str) -> ShowcaseMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> ShowcaseMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> ShowcaseMaster:
        self.metadata = metadata
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> ShowcaseMaster:
        self.sales_period_event_id = sales_period_event_id
        return self

    def with_display_items(self, display_items: List[DisplayItemMaster]) -> ShowcaseMaster:
        self.display_items = display_items
        return self

    def with_created_at(self, created_at: int) -> ShowcaseMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ShowcaseMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        showcase_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:showcase:{showcaseName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            showcaseName=showcase_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_showcase_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('showcase_name')

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
    ) -> Optional[ShowcaseMaster]:
        if data is None:
            return None
        return ShowcaseMaster()\
            .with_showcase_id(data.get('showcaseId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))\
            .with_display_items([
                DisplayItemMaster.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')) if data.get('displayItems') else 0)
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "showcaseId": self.showcase_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "salesPeriodEventId": self.sales_period_event_id,
            "displayItems": [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items) if self.display_items else 0)
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class SalesItemGroupMaster(core.Gs2Model):
    sales_item_group_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    sales_item_names: List[str] = None
    created_at: int = None
    updated_at: int = None

    def with_sales_item_group_id(self, sales_item_group_id: str) -> SalesItemGroupMaster:
        self.sales_item_group_id = sales_item_group_id
        return self

    def with_name(self, name: str) -> SalesItemGroupMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> SalesItemGroupMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> SalesItemGroupMaster:
        self.metadata = metadata
        return self

    def with_sales_item_names(self, sales_item_names: List[str]) -> SalesItemGroupMaster:
        self.sales_item_names = sales_item_names
        return self

    def with_created_at(self, created_at: int) -> SalesItemGroupMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SalesItemGroupMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        sales_item_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:salesItemGroup:{salesItemGroupName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            salesItemGroupName=sales_item_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_sales_item_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('sales_item_group_name')

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
    ) -> Optional[SalesItemGroupMaster]:
        if data is None:
            return None
        return SalesItemGroupMaster()\
            .with_sales_item_group_id(data.get('salesItemGroupId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_item_names([
                data.get('salesItemNames')[i]
                for i in range(len(data.get('salesItemNames')) if data.get('salesItemNames') else 0)
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "salesItemGroupId": self.sales_item_group_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "salesItemNames": [
                self.sales_item_names[i]
                for i in range(len(self.sales_item_names) if self.sales_item_names else 0)
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class SalesItemMaster(core.Gs2Model):
    sales_item_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None
    created_at: int = None
    updated_at: int = None

    def with_sales_item_id(self, sales_item_id: str) -> SalesItemMaster:
        self.sales_item_id = sales_item_id
        return self

    def with_name(self, name: str) -> SalesItemMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> SalesItemMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> SalesItemMaster:
        self.metadata = metadata
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> SalesItemMaster:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> SalesItemMaster:
        self.acquire_actions = acquire_actions
        return self

    def with_created_at(self, created_at: int) -> SalesItemMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SalesItemMaster:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        sales_item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:salesItem:{salesItemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            salesItemName=sales_item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_sales_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('sales_item_name')

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
    ) -> Optional[SalesItemMaster]:
        if data is None:
            return None
        return SalesItemMaster()\
            .with_sales_item_id(data.get('salesItemId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_actions([
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')) if data.get('consumeActions') else 0)
            ])\
            .with_acquire_actions([
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')) if data.get('acquireActions') else 0)
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "salesItemId": self.sales_item_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "consumeActions": [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions) if self.consume_actions else 0)
            ],
            "acquireActions": [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions) if self.acquire_actions else 0)
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
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

    def with_queue_namespace_id(self, queue_namespace_id: str) -> Namespace:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> Namespace:
        self.key_id = key_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
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
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
        }