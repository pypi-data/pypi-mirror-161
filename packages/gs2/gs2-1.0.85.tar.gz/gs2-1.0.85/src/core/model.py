# encoding: utf-8
#
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
from abc import abstractmethod
from typing import Optional, Dict, Any, Generic, TypeVar, Callable


class Gs2Constant(object):

    ENDPOINT_HOST = "https://{service}.{region}.gen2.gs2io.com"
    WS_ENDPOINT_HOST = "wss://gateway-ws.{region}.gen2.gs2io.com"


class IGs2Credential:

    @property
    @abstractmethod
    def client_id(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def client_secret(self) -> str:
        raise NotImplementedError()


class BasicGs2Credential(IGs2Credential):

    def __init__(
            self,
            client_id: str,
            client_secret: str,
    ):
        """
        コンストラクタ
        :param client_id: クライアントID
        :param client_secret: クライアントシークレット
        """
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret


class ProjectTokenGs2Credential(IGs2Credential):

    def __init__(
            self,
            owner_id: str,
            project_token: str,
    ):
        """
        コンストラクタ
        :param owner_id: オーナーID
        :param project_token: プロジェクトトークン
        """
        self._client_id = owner_id
        self._project_token = project_token

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return None

    @property
    def project_token(self) -> str:
        return self._project_token


class Gs2Request:

    request_id: str = None
    context_stack: str = None

    def with_request_id(
            self,
            request_id: str,
    ) -> Gs2Request:
        self.request_id = request_id
        return self

    def with_context_stack(
            self,
            context_stack: str,
    ) -> Gs2Request:
        self.context_stack = context_stack
        return self

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError()


class Gs2Result:

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError()


class Gs2Model:
    pass


class LoginResult(Gs2Result):
    """
    プロジェクトトークン を取得します のレスポンスモデル
    """
    access_token: str = None
    token_type: str = None
    expires_in: int = None

    def with_access_token(self, access_token: str):
        self.access_token = access_token
        return self

    def with_token_type(self, token_type: str):
        self.token_type = token_type
        return self

    def with_expires_in(self, expires_in: int):
        self.expires_in = expires_in
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
        return super.__getattribute__(key)

    @staticmethod
    def from_dict(
            data: Dict[str, Any],
    ) -> Optional[LoginResult]:
        if data is None:
            return None
        return LoginResult() \
            .with_access_token(data.get('access_token')) \
            .with_token_type(data.get('token_type')) \
            .with_expires_in(data.get('expires_in'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
        }


class ISession:

    @property
    @abstractmethod
    def credential(self) -> IGs2Credential:
        raise NotImplementedError()

    @property
    @abstractmethod
    def region(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def project_token(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _connect(
            self,
            callback: Callable[[AsyncResult[LoginResult]], None],
    ):
        raise NotImplementedError()

    @abstractmethod
    def connect(self):
        raise NotImplementedError()

    @abstractmethod
    async def connect_async(self):
        raise NotImplementedError()

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError()


class Region:

    AP_NORTHEAST_1 = 'ap-northeast-1'
    US_EAST_1 = 'us-east-1'
    EU_WEST_1 = 'eu-west-1'
    AP_SOUTHEAST_1 = 'ap-southeast-1'

    VALUES = [
        AP_NORTHEAST_1,
        US_EAST_1,
        EU_WEST_1,
        AP_SOUTHEAST_1,
    ]


class RequestError:

    def __init__(
            self,
            component: str,
            message: str,
    ):
        self._component = component
        self._message = message

    @property
    def component(self) -> str:
        return self._component

    @property
    def message(self) -> str:
        return self._message

    def __getitem__(self, key):
        if key == 'component':
            return self.component
        if key == 'message':
            return self.message
        return super(object, self).__getitem__(key)

    def get(self, key, default=None):
        if key == 'component':
            return self.component
        if key == 'message':
            return self.message
        try:
            return super(object, self).__getitem__(key)
        except ValueError:
            return default


T = TypeVar('T')


class AsyncResult(Generic[T]):

    def __init__(
        self,
        result: Optional[T] = None,
        error: Optional[Exception] = None,
    ):
        self._result = result
        self._error = error

    @property
    def result(self) -> Optional[T]:
        return self._result

    @property
    def error(self) -> Optional[Exception]:
        return self._error
