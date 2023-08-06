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

from core import Gs2RestSession
from core.domain.access_token import AccessToken
from identifier import Gs2IdentifierRestClient, request as request_, result as result_
from identifier.domain.iterator.users import DescribeUsersIterator
from identifier.domain.iterator.security_policies import DescribeSecurityPoliciesIterator
from identifier.domain.iterator.common_security_policies import DescribeCommonSecurityPoliciesIterator
from identifier.domain.iterator.identifiers import DescribeIdentifiersIterator
from identifier.domain.iterator.passwords import DescribePasswordsIterator
from identifier.domain.cache.user import UserDomainCache
from identifier.domain.cache.security_policy import SecurityPolicyDomainCache
from identifier.domain.cache.identifier import IdentifierDomainCache
from identifier.domain.cache.password import PasswordDomainCache
from identifier.domain.identifier import IdentifierDomain
from identifier.domain.password import PasswordDomain


class UserDomain:
    _session: Gs2RestSession
    _client: Gs2IdentifierRestClient
    _user_cache: UserDomainCache
    _user_name: str
    _identifier_cache: IdentifierDomainCache
    _password_cache: PasswordDomainCache

    def __init__(
        self,
        session: Gs2RestSession,
        user_cache: UserDomainCache,
        user_name: str,
    ):
        self._session = session
        self._client = Gs2IdentifierRestClient(
            session,
        )
        self._user_cache = user_cache
        self._user_name = user_name
        self._identifier_cache = IdentifierDomainCache()
        self._password_cache = PasswordDomainCache()

    def load(
        self,
        request: request_.GetUserRequest,
    ) -> result_.GetUserResult:
        request.with_user_name(self._user_name)
        r = self._client.get_user(
            request,
        )
        self._user_cache.update(r.item)
        return r

    def create_password(
        self,
        request: request_.CreatePasswordRequest,
    ) -> result_.CreatePasswordResult:
        request.with_user_name(self._user_name)
        r = self._client.create_password(
            request,
        )
        return r

    def delete_password(
        self,
        request: request_.DeletePasswordRequest,
    ) -> result_.DeletePasswordResult:
        request.with_user_name(self._user_name)
        r = self._client.delete_password(
            request,
        )
        return r

    def get_has_security_policy(
        self,
        request: request_.GetHasSecurityPolicyRequest,
    ) -> result_.GetHasSecurityPolicyResult:
        request.with_user_name(self._user_name)
        r = self._client.get_has_security_policy(
            request,
        )
        return r

    def attach_security_policy(
        self,
        request: request_.AttachSecurityPolicyRequest,
    ) -> result_.AttachSecurityPolicyResult:
        request.with_user_name(self._user_name)
        r = self._client.attach_security_policy(
            request,
        )
        return r

    def detach_security_policy(
        self,
        request: request_.DetachSecurityPolicyRequest,
    ) -> result_.DetachSecurityPolicyResult:
        request.with_user_name(self._user_name)
        r = self._client.detach_security_policy(
            request,
        )
        return r

    def passwords(
        self,
    ) -> DescribePasswordsIterator:
        return DescribePasswordsIterator(
            self._password_cache,
            self._client,
            self._user_name,
        )

    def identifier(
        self,
    ) -> IdentifierDomain:
        return IdentifierDomain(
            self._session,
            self._identifier_cache,
            self._user_name,
        )

    def password(
        self,
    ) -> PasswordDomain:
        return PasswordDomain(
            self._session,
            self._password_cache,
            self._user_name,
        )
