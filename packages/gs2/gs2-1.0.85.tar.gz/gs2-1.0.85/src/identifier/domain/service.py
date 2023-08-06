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
from identifier import Gs2IdentifierRestClient, request as request_, result as result_
from identifier.domain.iterator.users import DescribeUsersIterator
from identifier.domain.iterator.security_policies import DescribeSecurityPoliciesIterator
from identifier.domain.iterator.common_security_policies import DescribeCommonSecurityPoliciesIterator
from identifier.domain.cache.user import UserDomainCache
from identifier.domain.cache.security_policy import SecurityPolicyDomainCache
from identifier.domain.user import UserDomain
from identifier.domain.security_policy import SecurityPolicyDomain


class Gs2Identifier:

    def __init__(
        self,
        session: Gs2RestSession,
    ):
        self._session = session
        self._client = Gs2IdentifierRestClient(
            session=session,
        )
        self._user_cache = UserDomainCache()
        self._security_policy_cache = SecurityPolicyDomainCache()

    def create_user(
        self,
        request: request_.CreateUserRequest,
    ) -> result_.CreateUserResult:
        r = self._client.create_user(
            request=request,
        )
        self._user_cache.update(r.item)
        return r

    def update_user(
        self,
        request: request_.UpdateUserRequest,
    ) -> result_.UpdateUserResult:
        r = self._client.update_user(
            request=request,
        )
        self._user_cache.update(r.item)
        return r

    def delete_user(
        self,
        request: request_.DeleteUserRequest,
    ) -> result_.DeleteUserResult:
        r = self._client.delete_user(
            request=request,
        )
        return r

    def create_security_policy(
        self,
        request: request_.CreateSecurityPolicyRequest,
    ) -> result_.CreateSecurityPolicyResult:
        r = self._client.create_security_policy(
            request=request,
        )
        self._security_policy_cache.update(r.item)
        return r

    def update_security_policy(
        self,
        request: request_.UpdateSecurityPolicyRequest,
    ) -> result_.UpdateSecurityPolicyResult:
        r = self._client.update_security_policy(
            request=request,
        )
        self._security_policy_cache.update(r.item)
        return r

    def delete_security_policy(
        self,
        request: request_.DeleteSecurityPolicyRequest,
    ) -> result_.DeleteSecurityPolicyResult:
        r = self._client.delete_security_policy(
            request=request,
        )
        return r

    def create_identifier(
        self,
        request: request_.CreateIdentifierRequest,
    ) -> result_.CreateIdentifierResult:
        r = self._client.create_identifier(
            request=request,
        )
        return r

    def delete_identifier(
        self,
        request: request_.DeleteIdentifierRequest,
    ) -> result_.DeleteIdentifierResult:
        r = self._client.delete_identifier(
            request=request,
        )
        return r

    def login(
        self,
        request: request_.LoginRequest,
    ) -> result_.LoginResult:
        r = self._client.login(
            request=request,
        )
        return r

    def login_by_user(
        self,
        request: request_.LoginByUserRequest,
    ) -> result_.LoginByUserResult:
        r = self._client.login_by_user(
            request=request,
        )
        return r

    def users(
        self,
    ) -> DescribeUsersIterator:
        return DescribeUsersIterator(
            user_cache=self._user_cache,
            client=self._client,
        )

    def security_policies(
        self,
    ) -> DescribeSecurityPoliciesIterator:
        return DescribeSecurityPoliciesIterator(
            security_policy_cache=self._security_policy_cache,
            client=self._client,
        )

    def common_security_policies(
        self,
    ) -> DescribeCommonSecurityPoliciesIterator:
        return DescribeCommonSecurityPoliciesIterator(
            security_policy_cache=self._security_policy_cache,
            client=self._client,
        )

    def user(
        self,
        user_name: str,
    ) -> UserDomain:
        return UserDomain(
            session=self._session,
            user_cache=self._user_cache,
            user_name=user_name,
        )

    def security_policy(
        self,
        security_policy_name: str,
    ) -> SecurityPolicyDomain:
        return SecurityPolicyDomain(
            session=self._session,
            security_policy_cache=self._security_policy_cache,
            security_policy_name=security_policy_name,
        )
