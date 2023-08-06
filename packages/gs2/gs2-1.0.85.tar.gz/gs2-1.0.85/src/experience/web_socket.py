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

import time
from core.web_socket import *
from core.model import Gs2Constant
from experience.request import *
from experience.result import *


class Gs2ExperienceWebSocketClient(AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='namespace',
            function='describeNamespaces',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeNamespacesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
    ) -> DescribeNamespacesResult:
        async_result = []
        with timeout(30):
            self._describe_namespaces(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_namespaces_async(
        self,
        request: DescribeNamespacesRequest,
    ) -> DescribeNamespacesResult:
        async_result = []
        self._describe_namespaces(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_namespace(
        self,
        request: CreateNamespaceRequest,
        callback: Callable[[AsyncResult[CreateNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='namespace',
            function='createNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.experience_cap_script_id is not None:
            body["experienceCapScriptId"] = request.experience_cap_script_id
        if request.change_experience_script is not None:
            body["changeExperienceScript"] = request.change_experience_script.to_dict()
        if request.change_rank_script is not None:
            body["changeRankScript"] = request.change_rank_script.to_dict()
        if request.change_rank_cap_script is not None:
            body["changeRankCapScript"] = request.change_rank_cap_script.to_dict()
        if request.overflow_experience_script is not None:
            body["overflowExperienceScript"] = request.overflow_experience_script.to_dict()
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def create_namespace(
        self,
        request: CreateNamespaceRequest,
    ) -> CreateNamespaceResult:
        async_result = []
        with timeout(30):
            self._create_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_namespace_async(
        self,
        request: CreateNamespaceRequest,
    ) -> CreateNamespaceResult:
        async_result = []
        self._create_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_namespace_status(
        self,
        request: GetNamespaceStatusRequest,
        callback: Callable[[AsyncResult[GetNamespaceStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='namespace',
            function='getNamespaceStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetNamespaceStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_namespace_status(
        self,
        request: GetNamespaceStatusRequest,
    ) -> GetNamespaceStatusResult:
        async_result = []
        with timeout(30):
            self._get_namespace_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_namespace_status_async(
        self,
        request: GetNamespaceStatusRequest,
    ) -> GetNamespaceStatusResult:
        async_result = []
        self._get_namespace_status(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_namespace(
        self,
        request: GetNamespaceRequest,
        callback: Callable[[AsyncResult[GetNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='namespace',
            function='getNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def get_namespace(
        self,
        request: GetNamespaceRequest,
    ) -> GetNamespaceResult:
        async_result = []
        with timeout(30):
            self._get_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_namespace_async(
        self,
        request: GetNamespaceRequest,
    ) -> GetNamespaceResult:
        async_result = []
        self._get_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_namespace(
        self,
        request: UpdateNamespaceRequest,
        callback: Callable[[AsyncResult[UpdateNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='namespace',
            function='updateNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.description is not None:
            body["description"] = request.description
        if request.experience_cap_script_id is not None:
            body["experienceCapScriptId"] = request.experience_cap_script_id
        if request.change_experience_script is not None:
            body["changeExperienceScript"] = request.change_experience_script.to_dict()
        if request.change_rank_script is not None:
            body["changeRankScript"] = request.change_rank_script.to_dict()
        if request.change_rank_cap_script is not None:
            body["changeRankCapScript"] = request.change_rank_cap_script.to_dict()
        if request.overflow_experience_script is not None:
            body["overflowExperienceScript"] = request.overflow_experience_script.to_dict()
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def update_namespace(
        self,
        request: UpdateNamespaceRequest,
    ) -> UpdateNamespaceResult:
        async_result = []
        with timeout(30):
            self._update_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_namespace_async(
        self,
        request: UpdateNamespaceRequest,
    ) -> UpdateNamespaceResult:
        async_result = []
        self._update_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_namespace(
        self,
        request: DeleteNamespaceRequest,
        callback: Callable[[AsyncResult[DeleteNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='namespace',
            function='deleteNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def delete_namespace(
        self,
        request: DeleteNamespaceRequest,
    ) -> DeleteNamespaceResult:
        async_result = []
        with timeout(30):
            self._delete_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_namespace_async(
        self,
        request: DeleteNamespaceRequest,
    ) -> DeleteNamespaceResult:
        async_result = []
        self._delete_namespace(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_experience_model_masters(
        self,
        request: DescribeExperienceModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeExperienceModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='describeExperienceModelMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeExperienceModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_experience_model_masters(
        self,
        request: DescribeExperienceModelMastersRequest,
    ) -> DescribeExperienceModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_experience_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_experience_model_masters_async(
        self,
        request: DescribeExperienceModelMastersRequest,
    ) -> DescribeExperienceModelMastersResult:
        async_result = []
        self._describe_experience_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_experience_model_master(
        self,
        request: CreateExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[CreateExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='createExperienceModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.default_experience is not None:
            body["defaultExperience"] = request.default_experience
        if request.default_rank_cap is not None:
            body["defaultRankCap"] = request.default_rank_cap
        if request.max_rank_cap is not None:
            body["maxRankCap"] = request.max_rank_cap
        if request.rank_threshold_name is not None:
            body["rankThresholdName"] = request.rank_threshold_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_experience_model_master(
        self,
        request: CreateExperienceModelMasterRequest,
    ) -> CreateExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_experience_model_master_async(
        self,
        request: CreateExperienceModelMasterRequest,
    ) -> CreateExperienceModelMasterResult:
        async_result = []
        self._create_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_experience_model_master(
        self,
        request: GetExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[GetExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='getExperienceModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_experience_model_master(
        self,
        request: GetExperienceModelMasterRequest,
    ) -> GetExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_experience_model_master_async(
        self,
        request: GetExperienceModelMasterRequest,
    ) -> GetExperienceModelMasterResult:
        async_result = []
        self._get_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_experience_model_master(
        self,
        request: UpdateExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='updateExperienceModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.default_experience is not None:
            body["defaultExperience"] = request.default_experience
        if request.default_rank_cap is not None:
            body["defaultRankCap"] = request.default_rank_cap
        if request.max_rank_cap is not None:
            body["maxRankCap"] = request.max_rank_cap
        if request.rank_threshold_name is not None:
            body["rankThresholdName"] = request.rank_threshold_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_experience_model_master(
        self,
        request: UpdateExperienceModelMasterRequest,
    ) -> UpdateExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_experience_model_master_async(
        self,
        request: UpdateExperienceModelMasterRequest,
    ) -> UpdateExperienceModelMasterResult:
        async_result = []
        self._update_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_experience_model_master(
        self,
        request: DeleteExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='deleteExperienceModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_experience_model_master(
        self,
        request: DeleteExperienceModelMasterRequest,
    ) -> DeleteExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_experience_model_master_async(
        self,
        request: DeleteExperienceModelMasterRequest,
    ) -> DeleteExperienceModelMasterResult:
        async_result = []
        self._delete_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_experience_models(
        self,
        request: DescribeExperienceModelsRequest,
        callback: Callable[[AsyncResult[DescribeExperienceModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModel',
            function='describeExperienceModels',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeExperienceModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_experience_models(
        self,
        request: DescribeExperienceModelsRequest,
    ) -> DescribeExperienceModelsResult:
        async_result = []
        with timeout(30):
            self._describe_experience_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_experience_models_async(
        self,
        request: DescribeExperienceModelsRequest,
    ) -> DescribeExperienceModelsResult:
        async_result = []
        self._describe_experience_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_experience_model(
        self,
        request: GetExperienceModelRequest,
        callback: Callable[[AsyncResult[GetExperienceModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModel',
            function='getExperienceModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetExperienceModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_experience_model(
        self,
        request: GetExperienceModelRequest,
    ) -> GetExperienceModelResult:
        async_result = []
        with timeout(30):
            self._get_experience_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_experience_model_async(
        self,
        request: GetExperienceModelRequest,
    ) -> GetExperienceModelResult:
        async_result = []
        self._get_experience_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_threshold_masters(
        self,
        request: DescribeThresholdMastersRequest,
        callback: Callable[[AsyncResult[DescribeThresholdMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='describeThresholdMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeThresholdMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_threshold_masters(
        self,
        request: DescribeThresholdMastersRequest,
    ) -> DescribeThresholdMastersResult:
        async_result = []
        with timeout(30):
            self._describe_threshold_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_threshold_masters_async(
        self,
        request: DescribeThresholdMastersRequest,
    ) -> DescribeThresholdMastersResult:
        async_result = []
        self._describe_threshold_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_threshold_master(
        self,
        request: CreateThresholdMasterRequest,
        callback: Callable[[AsyncResult[CreateThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='createThresholdMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=CreateThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_threshold_master(
        self,
        request: CreateThresholdMasterRequest,
    ) -> CreateThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._create_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_threshold_master_async(
        self,
        request: CreateThresholdMasterRequest,
    ) -> CreateThresholdMasterResult:
        async_result = []
        self._create_threshold_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_threshold_master(
        self,
        request: GetThresholdMasterRequest,
        callback: Callable[[AsyncResult[GetThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='getThresholdMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.threshold_name is not None:
            body["thresholdName"] = request.threshold_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_threshold_master(
        self,
        request: GetThresholdMasterRequest,
    ) -> GetThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._get_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_threshold_master_async(
        self,
        request: GetThresholdMasterRequest,
    ) -> GetThresholdMasterResult:
        async_result = []
        self._get_threshold_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_threshold_master(
        self,
        request: UpdateThresholdMasterRequest,
        callback: Callable[[AsyncResult[UpdateThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='updateThresholdMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.threshold_name is not None:
            body["thresholdName"] = request.threshold_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_threshold_master(
        self,
        request: UpdateThresholdMasterRequest,
    ) -> UpdateThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._update_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_threshold_master_async(
        self,
        request: UpdateThresholdMasterRequest,
    ) -> UpdateThresholdMasterResult:
        async_result = []
        self._update_threshold_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_threshold_master(
        self,
        request: DeleteThresholdMasterRequest,
        callback: Callable[[AsyncResult[DeleteThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='deleteThresholdMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.threshold_name is not None:
            body["thresholdName"] = request.threshold_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_threshold_master(
        self,
        request: DeleteThresholdMasterRequest,
    ) -> DeleteThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._delete_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_threshold_master_async(
        self,
        request: DeleteThresholdMasterRequest,
    ) -> DeleteThresholdMasterResult:
        async_result = []
        self._delete_threshold_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _export_master(
        self,
        request: ExportMasterRequest,
        callback: Callable[[AsyncResult[ExportMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='exportMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=ExportMasterResult,
                callback=callback,
                body=body,
            )
        )

    def export_master(
        self,
        request: ExportMasterRequest,
    ) -> ExportMasterResult:
        async_result = []
        with timeout(30):
            self._export_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def export_master_async(
        self,
        request: ExportMasterRequest,
    ) -> ExportMasterResult:
        async_result = []
        self._export_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_current_experience_master(
        self,
        request: GetCurrentExperienceMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentExperienceMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='getCurrentExperienceMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetCurrentExperienceMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_experience_master(
        self,
        request: GetCurrentExperienceMasterRequest,
    ) -> GetCurrentExperienceMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_experience_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_experience_master_async(
        self,
        request: GetCurrentExperienceMasterRequest,
    ) -> GetCurrentExperienceMasterResult:
        async_result = []
        self._get_current_experience_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_experience_master(
        self,
        request: UpdateCurrentExperienceMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentExperienceMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='updateCurrentExperienceMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.settings is not None:
            body["settings"] = request.settings

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateCurrentExperienceMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_experience_master(
        self,
        request: UpdateCurrentExperienceMasterRequest,
    ) -> UpdateCurrentExperienceMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_experience_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_experience_master_async(
        self,
        request: UpdateCurrentExperienceMasterRequest,
    ) -> UpdateCurrentExperienceMasterResult:
        async_result = []
        self._update_current_experience_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_experience_master_from_git_hub(
        self,
        request: UpdateCurrentExperienceMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentExperienceMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='updateCurrentExperienceMasterFromGitHub',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=UpdateCurrentExperienceMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_experience_master_from_git_hub(
        self,
        request: UpdateCurrentExperienceMasterFromGitHubRequest,
    ) -> UpdateCurrentExperienceMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_experience_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_experience_master_from_git_hub_async(
        self,
        request: UpdateCurrentExperienceMasterFromGitHubRequest,
    ) -> UpdateCurrentExperienceMasterFromGitHubResult:
        async_result = []
        self._update_current_experience_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_statuses(
        self,
        request: DescribeStatusesRequest,
        callback: Callable[[AsyncResult[DescribeStatusesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='describeStatuses',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeStatusesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_statuses(
        self,
        request: DescribeStatusesRequest,
    ) -> DescribeStatusesResult:
        async_result = []
        with timeout(30):
            self._describe_statuses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_statuses_async(
        self,
        request: DescribeStatusesRequest,
    ) -> DescribeStatusesResult:
        async_result = []
        self._describe_statuses(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_statuses_by_user_id(
        self,
        request: DescribeStatusesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeStatusesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='describeStatusesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DescribeStatusesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_statuses_by_user_id(
        self,
        request: DescribeStatusesByUserIdRequest,
    ) -> DescribeStatusesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_statuses_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_statuses_by_user_id_async(
        self,
        request: DescribeStatusesByUserIdRequest,
    ) -> DescribeStatusesByUserIdResult:
        async_result = []
        self._describe_statuses_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status(
        self,
        request: GetStatusRequest,
        callback: Callable[[AsyncResult[GetStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_status(
        self,
        request: GetStatusRequest,
    ) -> GetStatusResult:
        async_result = []
        with timeout(30):
            self._get_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_async(
        self,
        request: GetStatusRequest,
    ) -> GetStatusResult:
        async_result = []
        self._get_status(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status_by_user_id(
        self,
        request: GetStatusByUserIdRequest,
        callback: Callable[[AsyncResult[GetStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_status_by_user_id(
        self,
        request: GetStatusByUserIdRequest,
    ) -> GetStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_by_user_id_async(
        self,
        request: GetStatusByUserIdRequest,
    ) -> GetStatusByUserIdResult:
        async_result = []
        self._get_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status_with_signature(
        self,
        request: GetStatusWithSignatureRequest,
        callback: Callable[[AsyncResult[GetStatusWithSignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatusWithSignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetStatusWithSignatureResult,
                callback=callback,
                body=body,
            )
        )

    def get_status_with_signature(
        self,
        request: GetStatusWithSignatureRequest,
    ) -> GetStatusWithSignatureResult:
        async_result = []
        with timeout(30):
            self._get_status_with_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_with_signature_async(
        self,
        request: GetStatusWithSignatureRequest,
    ) -> GetStatusWithSignatureResult:
        async_result = []
        self._get_status_with_signature(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status_with_signature_by_user_id(
        self,
        request: GetStatusWithSignatureByUserIdRequest,
        callback: Callable[[AsyncResult[GetStatusWithSignatureByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatusWithSignatureByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=GetStatusWithSignatureByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_status_with_signature_by_user_id(
        self,
        request: GetStatusWithSignatureByUserIdRequest,
    ) -> GetStatusWithSignatureByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_status_with_signature_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_with_signature_by_user_id_async(
        self,
        request: GetStatusWithSignatureByUserIdRequest,
    ) -> GetStatusWithSignatureByUserIdResult:
        async_result = []
        self._get_status_with_signature_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_experience_by_user_id(
        self,
        request: AddExperienceByUserIdRequest,
        callback: Callable[[AsyncResult[AddExperienceByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addExperienceByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.experience_value is not None:
            body["experienceValue"] = request.experience_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AddExperienceByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_experience_by_user_id(
        self,
        request: AddExperienceByUserIdRequest,
    ) -> AddExperienceByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_experience_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_experience_by_user_id_async(
        self,
        request: AddExperienceByUserIdRequest,
    ) -> AddExperienceByUserIdResult:
        async_result = []
        self._add_experience_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_experience_by_user_id(
        self,
        request: SetExperienceByUserIdRequest,
        callback: Callable[[AsyncResult[SetExperienceByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='setExperienceByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.experience_value is not None:
            body["experienceValue"] = request.experience_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=SetExperienceByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_experience_by_user_id(
        self,
        request: SetExperienceByUserIdRequest,
    ) -> SetExperienceByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_experience_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_experience_by_user_id_async(
        self,
        request: SetExperienceByUserIdRequest,
    ) -> SetExperienceByUserIdResult:
        async_result = []
        self._set_experience_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_rank_cap_by_user_id(
        self,
        request: AddRankCapByUserIdRequest,
        callback: Callable[[AsyncResult[AddRankCapByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addRankCapByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AddRankCapByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_rank_cap_by_user_id(
        self,
        request: AddRankCapByUserIdRequest,
    ) -> AddRankCapByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_rank_cap_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_rank_cap_by_user_id_async(
        self,
        request: AddRankCapByUserIdRequest,
    ) -> AddRankCapByUserIdResult:
        async_result = []
        self._add_rank_cap_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_rank_cap_by_user_id(
        self,
        request: SetRankCapByUserIdRequest,
        callback: Callable[[AsyncResult[SetRankCapByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='setRankCapByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=SetRankCapByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_rank_cap_by_user_id(
        self,
        request: SetRankCapByUserIdRequest,
    ) -> SetRankCapByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_rank_cap_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_rank_cap_by_user_id_async(
        self,
        request: SetRankCapByUserIdRequest,
    ) -> SetRankCapByUserIdResult:
        async_result = []
        self._set_rank_cap_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_status_by_user_id(
        self,
        request: DeleteStatusByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='deleteStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=DeleteStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_status_by_user_id(
        self,
        request: DeleteStatusByUserIdRequest,
    ) -> DeleteStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_status_by_user_id_async(
        self,
        request: DeleteStatusByUserIdRequest,
    ) -> DeleteStatusByUserIdResult:
        async_result = []
        self._delete_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_experience_by_stamp_sheet(
        self,
        request: AddExperienceByStampSheetRequest,
        callback: Callable[[AsyncResult[AddExperienceByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addExperienceByStampSheet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AddExperienceByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_experience_by_stamp_sheet(
        self,
        request: AddExperienceByStampSheetRequest,
    ) -> AddExperienceByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_experience_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_experience_by_stamp_sheet_async(
        self,
        request: AddExperienceByStampSheetRequest,
    ) -> AddExperienceByStampSheetResult:
        async_result = []
        self._add_experience_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_rank_cap_by_stamp_sheet(
        self,
        request: AddRankCapByStampSheetRequest,
        callback: Callable[[AsyncResult[AddRankCapByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addRankCapByStampSheet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=AddRankCapByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_rank_cap_by_stamp_sheet(
        self,
        request: AddRankCapByStampSheetRequest,
    ) -> AddRankCapByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_rank_cap_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_rank_cap_by_stamp_sheet_async(
        self,
        request: AddRankCapByStampSheetRequest,
    ) -> AddRankCapByStampSheetResult:
        async_result = []
        self._add_rank_cap_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_rank_cap_by_stamp_sheet(
        self,
        request: SetRankCapByStampSheetRequest,
        callback: Callable[[AsyncResult[SetRankCapByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='setRankCapByStampSheet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            NetworkJob(
                request_id=request_id,
                result_type=SetRankCapByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_rank_cap_by_stamp_sheet(
        self,
        request: SetRankCapByStampSheetRequest,
    ) -> SetRankCapByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_rank_cap_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_rank_cap_by_stamp_sheet_async(
        self,
        request: SetRankCapByStampSheetRequest,
    ) -> SetRankCapByStampSheetResult:
        async_result = []
        self._set_rank_cap_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result