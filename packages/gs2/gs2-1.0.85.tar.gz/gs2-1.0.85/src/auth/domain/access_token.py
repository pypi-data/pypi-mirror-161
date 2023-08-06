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
#
# deny overwrite

from __future__ import annotations

from core import Gs2RestSession
from core.domain.access_token import AccessToken
from auth import Gs2AuthRestClient, request as request_, result as result_


class AccessTokenDomain:

    def __init__(
        self,
        session: Gs2RestSession,
    ):
        self._session = session
        self._client = Gs2AuthRestClient(
            session=session,
        )

    def login(
            self,
            request: request_.LoginRequest,
    ) -> AccessToken:

        result = self._client.login(
            request
        )
        return AccessToken(
            user_id=result.user_id,
            token=result.token,
            expire=result.expire,
        )

    def login_by_signature(
            self,
            request: request_.LoginBySignatureRequest,
    ) -> AccessToken:

        result = self._client.login_by_signature(
            request
        )
        return AccessToken(
            user_id=result.user_id,
            token=result.token,
            expire=result.expire,
        )

