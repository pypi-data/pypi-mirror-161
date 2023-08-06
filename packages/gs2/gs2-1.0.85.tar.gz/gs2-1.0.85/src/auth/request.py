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

from auth.model import *


class LoginRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset: int = None

    def with_user_id(self, user_id: str) -> LoginRequest:
        self.user_id = user_id
        return self

    def with_time_offset(self, time_offset: int) -> LoginRequest:
        self.time_offset = time_offset
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
    ) -> Optional[LoginRequest]:
        if data is None:
            return None
        return LoginRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset(data.get('timeOffset'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffset": self.time_offset,
        }


class LoginBySignatureRequest(core.Gs2Request):

    context_stack: str = None
    key_id: str = None
    body: str = None
    signature: str = None

    def with_key_id(self, key_id: str) -> LoginBySignatureRequest:
        self.key_id = key_id
        return self

    def with_body(self, body: str) -> LoginBySignatureRequest:
        self.body = body
        return self

    def with_signature(self, signature: str) -> LoginBySignatureRequest:
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
    ) -> Optional[LoginBySignatureRequest]:
        if data is None:
            return None
        return LoginBySignatureRequest()\
            .with_key_id(data.get('keyId'))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyId": self.key_id,
            "body": self.body,
            "signature": self.signature,
        }