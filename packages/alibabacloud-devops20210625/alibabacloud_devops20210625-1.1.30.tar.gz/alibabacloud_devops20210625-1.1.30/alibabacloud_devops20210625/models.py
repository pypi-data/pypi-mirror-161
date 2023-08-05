# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import List, Dict, Any


class AddRepositoryMemberRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        access_level: int = None,
        aliyun_pks: str = None,
        organization_id: str = None,
    ):
        self.access_token = access_token
        self.access_level = access_level
        self.aliyun_pks = aliyun_pks
        self.organization_id = organization_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['AccessToken'] = self.access_token
        if self.access_level is not None:
            result['accessLevel'] = self.access_level
        if self.aliyun_pks is not None:
            result['aliyunPks'] = self.aliyun_pks
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AccessToken') is not None:
            self.access_token = m.get('AccessToken')
        if m.get('accessLevel') is not None:
            self.access_level = m.get('accessLevel')
        if m.get('aliyunPks') is not None:
            self.aliyun_pks = m.get('aliyunPks')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        return self


class AddRepositoryMemberResponseBodyResult(TeaModel):
    def __init__(
        self,
        access_level: int = None,
        avatar_url: str = None,
        email: str = None,
        extern_user_id: str = None,
        id: int = None,
        state: str = None,
    ):
        self.access_level = access_level
        self.avatar_url = avatar_url
        self.email = email
        self.extern_user_id = extern_user_id
        self.id = id
        self.state = state

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_level is not None:
            result['AccessLevel'] = self.access_level
        if self.avatar_url is not None:
            result['AvatarUrl'] = self.avatar_url
        if self.email is not None:
            result['Email'] = self.email
        if self.extern_user_id is not None:
            result['ExternUserId'] = self.extern_user_id
        if self.id is not None:
            result['Id'] = self.id
        if self.state is not None:
            result['State'] = self.state
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AccessLevel') is not None:
            self.access_level = m.get('AccessLevel')
        if m.get('AvatarUrl') is not None:
            self.avatar_url = m.get('AvatarUrl')
        if m.get('Email') is not None:
            self.email = m.get('Email')
        if m.get('ExternUserId') is not None:
            self.extern_user_id = m.get('ExternUserId')
        if m.get('Id') is not None:
            self.id = m.get('Id')
        if m.get('State') is not None:
            self.state = m.get('State')
        return self


class AddRepositoryMemberResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: List[AddRepositoryMemberResponseBodyResult] = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            for k in self.result:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['ErrorCode'] = self.error_code
        if self.error_message is not None:
            result['ErrorMessage'] = self.error_message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        result['Result'] = []
        if self.result is not None:
            for k in self.result:
                result['Result'].append(k.to_map() if k else None)
        if self.success is not None:
            result['Success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ErrorCode') is not None:
            self.error_code = m.get('ErrorCode')
        if m.get('ErrorMessage') is not None:
            self.error_message = m.get('ErrorMessage')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        self.result = []
        if m.get('Result') is not None:
            for k in m.get('Result'):
                temp_model = AddRepositoryMemberResponseBodyResult()
                self.result.append(temp_model.from_map(k))
        if m.get('Success') is not None:
            self.success = m.get('Success')
        return self


class AddRepositoryMemberResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AddRepositoryMemberResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AddRepositoryMemberResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class AddWebhookRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        organization_id: str = None,
        description: str = None,
        enable_ssl_verification: bool = None,
        merge_requests_events: bool = None,
        note_events: bool = None,
        push_events: bool = None,
        secret_token: str = None,
        tag_push_events: bool = None,
        url: str = None,
    ):
        self.access_token = access_token
        self.organization_id = organization_id
        self.description = description
        self.enable_ssl_verification = enable_ssl_verification
        self.merge_requests_events = merge_requests_events
        self.note_events = note_events
        self.push_events = push_events
        self.secret_token = secret_token
        self.tag_push_events = tag_push_events
        self.url = url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['AccessToken'] = self.access_token
        if self.organization_id is not None:
            result['OrganizationId'] = self.organization_id
        if self.description is not None:
            result['description'] = self.description
        if self.enable_ssl_verification is not None:
            result['enableSslVerification'] = self.enable_ssl_verification
        if self.merge_requests_events is not None:
            result['mergeRequestsEvents'] = self.merge_requests_events
        if self.note_events is not None:
            result['noteEvents'] = self.note_events
        if self.push_events is not None:
            result['pushEvents'] = self.push_events
        if self.secret_token is not None:
            result['secretToken'] = self.secret_token
        if self.tag_push_events is not None:
            result['tagPushEvents'] = self.tag_push_events
        if self.url is not None:
            result['url'] = self.url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AccessToken') is not None:
            self.access_token = m.get('AccessToken')
        if m.get('OrganizationId') is not None:
            self.organization_id = m.get('OrganizationId')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('enableSslVerification') is not None:
            self.enable_ssl_verification = m.get('enableSslVerification')
        if m.get('mergeRequestsEvents') is not None:
            self.merge_requests_events = m.get('mergeRequestsEvents')
        if m.get('noteEvents') is not None:
            self.note_events = m.get('noteEvents')
        if m.get('pushEvents') is not None:
            self.push_events = m.get('pushEvents')
        if m.get('secretToken') is not None:
            self.secret_token = m.get('secretToken')
        if m.get('tagPushEvents') is not None:
            self.tag_push_events = m.get('tagPushEvents')
        if m.get('url') is not None:
            self.url = m.get('url')
        return self


class AddWebhookResponseBodyResult(TeaModel):
    def __init__(
        self,
        created_at: str = None,
        description: str = None,
        enable_ssl_verification: bool = None,
        id: int = None,
        last_test_result: str = None,
        merge_requests_events: bool = None,
        note_events: bool = None,
        push_events: bool = None,
        repository_id: int = None,
        secret_token: str = None,
        tag_push_events: bool = None,
        url: str = None,
    ):
        self.created_at = created_at
        self.description = description
        self.enable_ssl_verification = enable_ssl_verification
        self.id = id
        self.last_test_result = last_test_result
        self.merge_requests_events = merge_requests_events
        self.note_events = note_events
        self.push_events = push_events
        self.repository_id = repository_id
        self.secret_token = secret_token
        self.tag_push_events = tag_push_events
        self.url = url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.created_at is not None:
            result['createdAt'] = self.created_at
        if self.description is not None:
            result['description'] = self.description
        if self.enable_ssl_verification is not None:
            result['enableSslVerification'] = self.enable_ssl_verification
        if self.id is not None:
            result['id'] = self.id
        if self.last_test_result is not None:
            result['lastTestResult'] = self.last_test_result
        if self.merge_requests_events is not None:
            result['mergeRequestsEvents'] = self.merge_requests_events
        if self.note_events is not None:
            result['noteEvents'] = self.note_events
        if self.push_events is not None:
            result['pushEvents'] = self.push_events
        if self.repository_id is not None:
            result['repositoryId'] = self.repository_id
        if self.secret_token is not None:
            result['secretToken'] = self.secret_token
        if self.tag_push_events is not None:
            result['tagPushEvents'] = self.tag_push_events
        if self.url is not None:
            result['url'] = self.url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createdAt') is not None:
            self.created_at = m.get('createdAt')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('enableSslVerification') is not None:
            self.enable_ssl_verification = m.get('enableSslVerification')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('lastTestResult') is not None:
            self.last_test_result = m.get('lastTestResult')
        if m.get('mergeRequestsEvents') is not None:
            self.merge_requests_events = m.get('mergeRequestsEvents')
        if m.get('noteEvents') is not None:
            self.note_events = m.get('noteEvents')
        if m.get('pushEvents') is not None:
            self.push_events = m.get('pushEvents')
        if m.get('repositoryId') is not None:
            self.repository_id = m.get('repositoryId')
        if m.get('secretToken') is not None:
            self.secret_token = m.get('secretToken')
        if m.get('tagPushEvents') is not None:
            self.tag_push_events = m.get('tagPushEvents')
        if m.get('url') is not None:
            self.url = m.get('url')
        return self


class AddWebhookResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: AddWebhookResponseBodyResult = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            self.result.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.result is not None:
            result['result'] = self.result.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('result') is not None:
            temp_model = AddWebhookResponseBodyResult()
            self.result = temp_model.from_map(m['result'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class AddWebhookResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AddWebhookResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AddWebhookResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateFlowTagRequest(TeaModel):
    def __init__(
        self,
        color: str = None,
        flow_tag_group_id: int = None,
        name: str = None,
    ):
        self.color = color
        self.flow_tag_group_id = flow_tag_group_id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.color is not None:
            result['color'] = self.color
        if self.flow_tag_group_id is not None:
            result['flowTagGroupId'] = self.flow_tag_group_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('color') is not None:
            self.color = m.get('color')
        if m.get('flowTagGroupId') is not None:
            self.flow_tag_group_id = m.get('flowTagGroupId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class CreateFlowTagResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        id: int = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.id = id
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.id is not None:
            result['id'] = self.id
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateFlowTagResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateFlowTagResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateFlowTagResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateFlowTagGroupRequest(TeaModel):
    def __init__(
        self,
        name: str = None,
    ):
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class CreateFlowTagGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        id: int = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.id = id
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.id is not None:
            result['id'] = self.id
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateFlowTagGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateFlowTagGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateFlowTagGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateHostGroupRequest(TeaModel):
    def __init__(
        self,
        aliyun_region: str = None,
        ecs_label_key: str = None,
        ecs_label_value: str = None,
        ecs_type: str = None,
        env_id: str = None,
        machine_infos: str = None,
        name: str = None,
        service_connection_id: int = None,
        tag_ids: str = None,
        type: str = None,
    ):
        self.aliyun_region = aliyun_region
        self.ecs_label_key = ecs_label_key
        self.ecs_label_value = ecs_label_value
        self.ecs_type = ecs_type
        self.env_id = env_id
        self.machine_infos = machine_infos
        self.name = name
        self.service_connection_id = service_connection_id
        self.tag_ids = tag_ids
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.aliyun_region is not None:
            result['aliyunRegion'] = self.aliyun_region
        if self.ecs_label_key is not None:
            result['ecsLabelKey'] = self.ecs_label_key
        if self.ecs_label_value is not None:
            result['ecsLabelValue'] = self.ecs_label_value
        if self.ecs_type is not None:
            result['ecsType'] = self.ecs_type
        if self.env_id is not None:
            result['envId'] = self.env_id
        if self.machine_infos is not None:
            result['machineInfos'] = self.machine_infos
        if self.name is not None:
            result['name'] = self.name
        if self.service_connection_id is not None:
            result['serviceConnectionId'] = self.service_connection_id
        if self.tag_ids is not None:
            result['tagIds'] = self.tag_ids
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('aliyunRegion') is not None:
            self.aliyun_region = m.get('aliyunRegion')
        if m.get('ecsLabelKey') is not None:
            self.ecs_label_key = m.get('ecsLabelKey')
        if m.get('ecsLabelValue') is not None:
            self.ecs_label_value = m.get('ecsLabelValue')
        if m.get('ecsType') is not None:
            self.ecs_type = m.get('ecsType')
        if m.get('envId') is not None:
            self.env_id = m.get('envId')
        if m.get('machineInfos') is not None:
            self.machine_infos = m.get('machineInfos')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('serviceConnectionId') is not None:
            self.service_connection_id = m.get('serviceConnectionId')
        if m.get('tagIds') is not None:
            self.tag_ids = m.get('tagIds')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class CreateHostGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        host_group_id: int = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.host_group_id = host_group_id
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.host_group_id is not None:
            result['hostGroupId'] = self.host_group_id
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('hostGroupId') is not None:
            self.host_group_id = m.get('hostGroupId')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateHostGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateHostGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateHostGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateOAuthTokenRequest(TeaModel):
    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        code: str = None,
        grant_type: str = None,
        login: str = None,
        scope: str = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.code = code
        self.grant_type = grant_type
        self.login = login
        self.scope = scope

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_id is not None:
            result['clientId'] = self.client_id
        if self.client_secret is not None:
            result['clientSecret'] = self.client_secret
        if self.code is not None:
            result['code'] = self.code
        if self.grant_type is not None:
            result['grantType'] = self.grant_type
        if self.login is not None:
            result['login'] = self.login
        if self.scope is not None:
            result['scope'] = self.scope
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('clientId') is not None:
            self.client_id = m.get('clientId')
        if m.get('clientSecret') is not None:
            self.client_secret = m.get('clientSecret')
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('grantType') is not None:
            self.grant_type = m.get('grantType')
        if m.get('login') is not None:
            self.login = m.get('login')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        return self


class CreateOAuthTokenResponseBodyResult(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        id: str = None,
        scope: str = None,
        token_type: str = None,
    ):
        self.access_token = access_token
        self.id = id
        self.scope = scope
        self.token_type = token_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.id is not None:
            result['id'] = self.id
        if self.scope is not None:
            result['scope'] = self.scope
        if self.token_type is not None:
            result['tokenType'] = self.token_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('tokenType') is not None:
            self.token_type = m.get('tokenType')
        return self


class CreateOAuthTokenResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: CreateOAuthTokenResponseBodyResult = None,
        success: str = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            self.result.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.result is not None:
            result['result'] = self.result.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('result') is not None:
            temp_model = CreateOAuthTokenResponseBodyResult()
            self.result = temp_model.from_map(m['result'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateOAuthTokenResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateOAuthTokenResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateOAuthTokenResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreatePipelineRequestBasicInfo(TeaModel):
    def __init__(
        self,
        env_id: int = None,
        group_id: int = None,
        name: str = None,
        tag_ids: str = None,
    ):
        self.env_id = env_id
        self.group_id = group_id
        self.name = name
        self.tag_ids = tag_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.env_id is not None:
            result['envId'] = self.env_id
        if self.group_id is not None:
            result['groupId'] = self.group_id
        if self.name is not None:
            result['name'] = self.name
        if self.tag_ids is not None:
            result['tagIds'] = self.tag_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('envId') is not None:
            self.env_id = m.get('envId')
        if m.get('groupId') is not None:
            self.group_id = m.get('groupId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('tagIds') is not None:
            self.tag_ids = m.get('tagIds')
        return self


class CreatePipelineRequestSettingsCaches(TeaModel):
    def __init__(
        self,
        desc: str = None,
        directory: str = None,
        disable: bool = None,
    ):
        self.desc = desc
        self.directory = directory
        self.disable = disable

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.desc is not None:
            result['desc'] = self.desc
        if self.directory is not None:
            result['directory'] = self.directory
        if self.disable is not None:
            result['disable'] = self.disable
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('desc') is not None:
            self.desc = m.get('desc')
        if m.get('directory') is not None:
            self.directory = m.get('directory')
        if m.get('disable') is not None:
            self.disable = m.get('disable')
        return self


class CreatePipelineRequestSettingsGlobalParams(TeaModel):
    def __init__(
        self,
        key: str = None,
        mask: bool = None,
        running_config: bool = None,
        value: str = None,
    ):
        self.key = key
        self.mask = mask
        self.running_config = running_config
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['key'] = self.key
        if self.mask is not None:
            result['mask'] = self.mask
        if self.running_config is not None:
            result['runningConfig'] = self.running_config
        if self.value is not None:
            result['value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('key') is not None:
            self.key = m.get('key')
        if m.get('mask') is not None:
            self.mask = m.get('mask')
        if m.get('runningConfig') is not None:
            self.running_config = m.get('runningConfig')
        if m.get('value') is not None:
            self.value = m.get('value')
        return self


class CreatePipelineRequestSettings(TeaModel):
    def __init__(
        self,
        caches: List[CreatePipelineRequestSettingsCaches] = None,
        global_params: List[CreatePipelineRequestSettingsGlobalParams] = None,
        runner_cache_mode: str = None,
    ):
        self.caches = caches
        self.global_params = global_params
        self.runner_cache_mode = runner_cache_mode

    def validate(self):
        if self.caches:
            for k in self.caches:
                if k:
                    k.validate()
        if self.global_params:
            for k in self.global_params:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['caches'] = []
        if self.caches is not None:
            for k in self.caches:
                result['caches'].append(k.to_map() if k else None)
        result['globalParams'] = []
        if self.global_params is not None:
            for k in self.global_params:
                result['globalParams'].append(k.to_map() if k else None)
        if self.runner_cache_mode is not None:
            result['runnerCacheMode'] = self.runner_cache_mode
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.caches = []
        if m.get('caches') is not None:
            for k in m.get('caches'):
                temp_model = CreatePipelineRequestSettingsCaches()
                self.caches.append(temp_model.from_map(k))
        self.global_params = []
        if m.get('globalParams') is not None:
            for k in m.get('globalParams'):
                temp_model = CreatePipelineRequestSettingsGlobalParams()
                self.global_params.append(temp_model.from_map(k))
        if m.get('runnerCacheMode') is not None:
            self.runner_cache_mode = m.get('runnerCacheMode')
        return self


class CreatePipelineRequestTriggerInfoScheduled(TeaModel):
    def __init__(
        self,
        days_of_week: str = None,
        fixed_time: str = None,
        from_: str = None,
        interval: int = None,
        only_source_change: bool = None,
        to: str = None,
        type: str = None,
    ):
        self.days_of_week = days_of_week
        self.fixed_time = fixed_time
        self.from_ = from_
        self.interval = interval
        self.only_source_change = only_source_change
        self.to = to
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.days_of_week is not None:
            result['daysOfWeek'] = self.days_of_week
        if self.fixed_time is not None:
            result['fixedTime'] = self.fixed_time
        if self.from_ is not None:
            result['from'] = self.from_
        if self.interval is not None:
            result['interval'] = self.interval
        if self.only_source_change is not None:
            result['onlySourceChange'] = self.only_source_change
        if self.to is not None:
            result['to'] = self.to
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('daysOfWeek') is not None:
            self.days_of_week = m.get('daysOfWeek')
        if m.get('fixedTime') is not None:
            self.fixed_time = m.get('fixedTime')
        if m.get('from') is not None:
            self.from_ = m.get('from')
        if m.get('interval') is not None:
            self.interval = m.get('interval')
        if m.get('onlySourceChange') is not None:
            self.only_source_change = m.get('onlySourceChange')
        if m.get('to') is not None:
            self.to = m.get('to')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class CreatePipelineRequestTriggerInfo(TeaModel):
    def __init__(
        self,
        scheduled: CreatePipelineRequestTriggerInfoScheduled = None,
        webhook_enable: bool = None,
    ):
        self.scheduled = scheduled
        self.webhook_enable = webhook_enable

    def validate(self):
        if self.scheduled:
            self.scheduled.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.scheduled is not None:
            result['scheduled'] = self.scheduled.to_map()
        if self.webhook_enable is not None:
            result['webhookEnable'] = self.webhook_enable
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('scheduled') is not None:
            temp_model = CreatePipelineRequestTriggerInfoScheduled()
            self.scheduled = temp_model.from_map(m['scheduled'])
        if m.get('webhookEnable') is not None:
            self.webhook_enable = m.get('webhookEnable')
        return self


class CreatePipelineRequest(TeaModel):
    def __init__(
        self,
        basic_info: CreatePipelineRequestBasicInfo = None,
        pipeline_yaml: str = None,
        settings: CreatePipelineRequestSettings = None,
        trigger_info: CreatePipelineRequestTriggerInfo = None,
    ):
        self.basic_info = basic_info
        self.pipeline_yaml = pipeline_yaml
        self.settings = settings
        self.trigger_info = trigger_info

    def validate(self):
        if self.basic_info:
            self.basic_info.validate()
        if self.settings:
            self.settings.validate()
        if self.trigger_info:
            self.trigger_info.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.basic_info is not None:
            result['basicInfo'] = self.basic_info.to_map()
        if self.pipeline_yaml is not None:
            result['pipelineYaml'] = self.pipeline_yaml
        if self.settings is not None:
            result['settings'] = self.settings.to_map()
        if self.trigger_info is not None:
            result['triggerInfo'] = self.trigger_info.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('basicInfo') is not None:
            temp_model = CreatePipelineRequestBasicInfo()
            self.basic_info = temp_model.from_map(m['basicInfo'])
        if m.get('pipelineYaml') is not None:
            self.pipeline_yaml = m.get('pipelineYaml')
        if m.get('settings') is not None:
            temp_model = CreatePipelineRequestSettings()
            self.settings = temp_model.from_map(m['settings'])
        if m.get('triggerInfo') is not None:
            temp_model = CreatePipelineRequestTriggerInfo()
            self.trigger_info = temp_model.from_map(m['triggerInfo'])
        return self


class CreatePipelineResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        object: int = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.object = object
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.object is not None:
            result['object'] = self.object
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('object') is not None:
            self.object = m.get('object')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreatePipelineResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreatePipelineResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreatePipelineResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreatePipelineGroupRequest(TeaModel):
    def __init__(
        self,
        name: str = None,
    ):
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class CreatePipelineGroupResponseBodyPipelineGroup(TeaModel):
    def __init__(
        self,
        id: int = None,
        name: str = None,
    ):
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class CreatePipelineGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        pipeline_group: CreatePipelineGroupResponseBodyPipelineGroup = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.pipeline_group = pipeline_group
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.pipeline_group:
            self.pipeline_group.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.pipeline_group is not None:
            result['pipelineGroup'] = self.pipeline_group.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('pipelineGroup') is not None:
            temp_model = CreatePipelineGroupResponseBodyPipelineGroup()
            self.pipeline_group = temp_model.from_map(m['pipelineGroup'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreatePipelineGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreatePipelineGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreatePipelineGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateProjectRequest(TeaModel):
    def __init__(
        self,
        custom_code: str = None,
        name: str = None,
        scope: str = None,
        template_identifier: str = None,
    ):
        self.custom_code = custom_code
        self.name = name
        self.scope = scope
        self.template_identifier = template_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.custom_code is not None:
            result['customCode'] = self.custom_code
        if self.name is not None:
            result['name'] = self.name
        if self.scope is not None:
            result['scope'] = self.scope
        if self.template_identifier is not None:
            result['templateIdentifier'] = self.template_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('customCode') is not None:
            self.custom_code = m.get('customCode')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('templateIdentifier') is not None:
            self.template_identifier = m.get('templateIdentifier')
        return self


class CreateProjectResponseBodyProject(TeaModel):
    def __init__(
        self,
        category_identifier: str = None,
        creator: str = None,
        custom_code: str = None,
        description: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        icon: str = None,
        identifier: str = None,
        logical_status: str = None,
        modifier: str = None,
        name: str = None,
        organization_identifier: str = None,
        scope: str = None,
        status_identifier: str = None,
        status_stage_identifier: str = None,
        type_identifier: str = None,
    ):
        self.category_identifier = category_identifier
        self.creator = creator
        self.custom_code = custom_code
        self.description = description
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.icon = icon
        self.identifier = identifier
        self.logical_status = logical_status
        self.modifier = modifier
        self.name = name
        self.organization_identifier = organization_identifier
        self.scope = scope
        self.status_identifier = status_identifier
        self.status_stage_identifier = status_stage_identifier
        self.type_identifier = type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        if self.custom_code is not None:
            result['customCode'] = self.custom_code
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.icon is not None:
            result['icon'] = self.icon
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.logical_status is not None:
            result['logicalStatus'] = self.logical_status
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.organization_identifier is not None:
            result['organizationIdentifier'] = self.organization_identifier
        if self.scope is not None:
            result['scope'] = self.scope
        if self.status_identifier is not None:
            result['statusIdentifier'] = self.status_identifier
        if self.status_stage_identifier is not None:
            result['statusStageIdentifier'] = self.status_stage_identifier
        if self.type_identifier is not None:
            result['typeIdentifier'] = self.type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('customCode') is not None:
            self.custom_code = m.get('customCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('icon') is not None:
            self.icon = m.get('icon')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('logicalStatus') is not None:
            self.logical_status = m.get('logicalStatus')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('organizationIdentifier') is not None:
            self.organization_identifier = m.get('organizationIdentifier')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('statusIdentifier') is not None:
            self.status_identifier = m.get('statusIdentifier')
        if m.get('statusStageIdentifier') is not None:
            self.status_stage_identifier = m.get('statusStageIdentifier')
        if m.get('typeIdentifier') is not None:
            self.type_identifier = m.get('typeIdentifier')
        return self


class CreateProjectResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        project: CreateProjectResponseBodyProject = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.project = project
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.project:
            self.project.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.project is not None:
            result['project'] = self.project.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('project') is not None:
            temp_model = CreateProjectResponseBodyProject()
            self.project = temp_model.from_map(m['project'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateProjectResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateProjectResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateProjectResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateRepositoryRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        avatar_url: str = None,
        description: str = None,
        gitignore_type: str = None,
        import_account: str = None,
        import_demo_project: bool = None,
        import_repo_type: str = None,
        import_token: str = None,
        import_token_encrypted: str = None,
        import_url: str = None,
        init_standard_service: bool = None,
        is_crypto_enabled: bool = None,
        local_import_url: str = None,
        name: str = None,
        namespace_id: int = None,
        path: str = None,
        readme_type: str = None,
        visibility_level: int = None,
        create_parent_path: bool = None,
        organization_id: str = None,
        sync: bool = None,
    ):
        self.access_token = access_token
        self.avatar_url = avatar_url
        self.description = description
        self.gitignore_type = gitignore_type
        self.import_account = import_account
        self.import_demo_project = import_demo_project
        self.import_repo_type = import_repo_type
        self.import_token = import_token
        self.import_token_encrypted = import_token_encrypted
        self.import_url = import_url
        self.init_standard_service = init_standard_service
        self.is_crypto_enabled = is_crypto_enabled
        self.local_import_url = local_import_url
        self.name = name
        self.namespace_id = namespace_id
        self.path = path
        self.readme_type = readme_type
        self.visibility_level = visibility_level
        self.create_parent_path = create_parent_path
        self.organization_id = organization_id
        self.sync = sync

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.avatar_url is not None:
            result['avatarUrl'] = self.avatar_url
        if self.description is not None:
            result['description'] = self.description
        if self.gitignore_type is not None:
            result['gitignoreType'] = self.gitignore_type
        if self.import_account is not None:
            result['importAccount'] = self.import_account
        if self.import_demo_project is not None:
            result['importDemoProject'] = self.import_demo_project
        if self.import_repo_type is not None:
            result['importRepoType'] = self.import_repo_type
        if self.import_token is not None:
            result['importToken'] = self.import_token
        if self.import_token_encrypted is not None:
            result['importTokenEncrypted'] = self.import_token_encrypted
        if self.import_url is not None:
            result['importUrl'] = self.import_url
        if self.init_standard_service is not None:
            result['initStandardService'] = self.init_standard_service
        if self.is_crypto_enabled is not None:
            result['isCryptoEnabled'] = self.is_crypto_enabled
        if self.local_import_url is not None:
            result['localImportUrl'] = self.local_import_url
        if self.name is not None:
            result['name'] = self.name
        if self.namespace_id is not None:
            result['namespaceId'] = self.namespace_id
        if self.path is not None:
            result['path'] = self.path
        if self.readme_type is not None:
            result['readmeType'] = self.readme_type
        if self.visibility_level is not None:
            result['visibilityLevel'] = self.visibility_level
        if self.create_parent_path is not None:
            result['createParentPath'] = self.create_parent_path
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        if self.sync is not None:
            result['sync'] = self.sync
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('avatarUrl') is not None:
            self.avatar_url = m.get('avatarUrl')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gitignoreType') is not None:
            self.gitignore_type = m.get('gitignoreType')
        if m.get('importAccount') is not None:
            self.import_account = m.get('importAccount')
        if m.get('importDemoProject') is not None:
            self.import_demo_project = m.get('importDemoProject')
        if m.get('importRepoType') is not None:
            self.import_repo_type = m.get('importRepoType')
        if m.get('importToken') is not None:
            self.import_token = m.get('importToken')
        if m.get('importTokenEncrypted') is not None:
            self.import_token_encrypted = m.get('importTokenEncrypted')
        if m.get('importUrl') is not None:
            self.import_url = m.get('importUrl')
        if m.get('initStandardService') is not None:
            self.init_standard_service = m.get('initStandardService')
        if m.get('isCryptoEnabled') is not None:
            self.is_crypto_enabled = m.get('isCryptoEnabled')
        if m.get('localImportUrl') is not None:
            self.local_import_url = m.get('localImportUrl')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('namespaceId') is not None:
            self.namespace_id = m.get('namespaceId')
        if m.get('path') is not None:
            self.path = m.get('path')
        if m.get('readmeType') is not None:
            self.readme_type = m.get('readmeType')
        if m.get('visibilityLevel') is not None:
            self.visibility_level = m.get('visibilityLevel')
        if m.get('createParentPath') is not None:
            self.create_parent_path = m.get('createParentPath')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        if m.get('sync') is not None:
            self.sync = m.get('sync')
        return self


class CreateRepositoryResponseBodyResultNamespace(TeaModel):
    def __init__(
        self,
        avatar: str = None,
        created_at: str = None,
        description: str = None,
        id: int = None,
        name: str = None,
        owner_id: int = None,
        path: str = None,
        public: bool = None,
        updated_at: str = None,
        visibility_level: str = None,
    ):
        self.avatar = avatar
        self.created_at = created_at
        self.description = description
        self.id = id
        self.name = name
        self.owner_id = owner_id
        self.path = path
        self.public = public
        self.updated_at = updated_at
        self.visibility_level = visibility_level

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.avatar is not None:
            result['avatar'] = self.avatar
        if self.created_at is not None:
            result['createdAt'] = self.created_at
        if self.description is not None:
            result['description'] = self.description
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.owner_id is not None:
            result['ownerId'] = self.owner_id
        if self.path is not None:
            result['path'] = self.path
        if self.public is not None:
            result['public'] = self.public
        if self.updated_at is not None:
            result['updatedAt'] = self.updated_at
        if self.visibility_level is not None:
            result['visibilityLevel'] = self.visibility_level
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('avatar') is not None:
            self.avatar = m.get('avatar')
        if m.get('createdAt') is not None:
            self.created_at = m.get('createdAt')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('ownerId') is not None:
            self.owner_id = m.get('ownerId')
        if m.get('path') is not None:
            self.path = m.get('path')
        if m.get('public') is not None:
            self.public = m.get('public')
        if m.get('updatedAt') is not None:
            self.updated_at = m.get('updatedAt')
        if m.get('visibilityLevel') is not None:
            self.visibility_level = m.get('visibilityLevel')
        return self


class CreateRepositoryResponseBodyResult(TeaModel):
    def __init__(
        self,
        import_from_svn: bool = None,
        archived: bool = None,
        avatar_url: str = None,
        created_at: str = None,
        creator_id: int = None,
        default_branch: str = None,
        demo_project: bool = None,
        description: str = None,
        http_url_to_repo: str = None,
        id: int = None,
        last_activity_at: str = None,
        name: str = None,
        name_with_namespace: str = None,
        namespace: CreateRepositoryResponseBodyResultNamespace = None,
        path: str = None,
        path_with_namespace: str = None,
        ssh_url_to_repo: str = None,
        visibility_level: str = None,
        web_url: str = None,
    ):
        self.import_from_svn = import_from_svn
        self.archived = archived
        self.avatar_url = avatar_url
        self.created_at = created_at
        self.creator_id = creator_id
        self.default_branch = default_branch
        self.demo_project = demo_project
        self.description = description
        self.http_url_to_repo = http_url_to_repo
        self.id = id
        self.last_activity_at = last_activity_at
        self.name = name
        self.name_with_namespace = name_with_namespace
        self.namespace = namespace
        self.path = path
        self.path_with_namespace = path_with_namespace
        self.ssh_url_to_repo = ssh_url_to_repo
        self.visibility_level = visibility_level
        self.web_url = web_url

    def validate(self):
        if self.namespace:
            self.namespace.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.import_from_svn is not None:
            result['Import_from_svn'] = self.import_from_svn
        if self.archived is not None:
            result['archived'] = self.archived
        if self.avatar_url is not None:
            result['avatar_url'] = self.avatar_url
        if self.created_at is not None:
            result['createdAt'] = self.created_at
        if self.creator_id is not None:
            result['creatorId'] = self.creator_id
        if self.default_branch is not None:
            result['defaultBranch'] = self.default_branch
        if self.demo_project is not None:
            result['demoProject'] = self.demo_project
        if self.description is not None:
            result['description'] = self.description
        if self.http_url_to_repo is not None:
            result['httpUrlToRepo'] = self.http_url_to_repo
        if self.id is not None:
            result['id'] = self.id
        if self.last_activity_at is not None:
            result['lastActivityAt'] = self.last_activity_at
        if self.name is not None:
            result['name'] = self.name
        if self.name_with_namespace is not None:
            result['nameWithNamespace'] = self.name_with_namespace
        if self.namespace is not None:
            result['namespace'] = self.namespace.to_map()
        if self.path is not None:
            result['path'] = self.path
        if self.path_with_namespace is not None:
            result['pathWithNamespace'] = self.path_with_namespace
        if self.ssh_url_to_repo is not None:
            result['sshUrlToRepo'] = self.ssh_url_to_repo
        if self.visibility_level is not None:
            result['visibilityLevel'] = self.visibility_level
        if self.web_url is not None:
            result['webUrl'] = self.web_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Import_from_svn') is not None:
            self.import_from_svn = m.get('Import_from_svn')
        if m.get('archived') is not None:
            self.archived = m.get('archived')
        if m.get('avatar_url') is not None:
            self.avatar_url = m.get('avatar_url')
        if m.get('createdAt') is not None:
            self.created_at = m.get('createdAt')
        if m.get('creatorId') is not None:
            self.creator_id = m.get('creatorId')
        if m.get('defaultBranch') is not None:
            self.default_branch = m.get('defaultBranch')
        if m.get('demoProject') is not None:
            self.demo_project = m.get('demoProject')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('httpUrlToRepo') is not None:
            self.http_url_to_repo = m.get('httpUrlToRepo')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('lastActivityAt') is not None:
            self.last_activity_at = m.get('lastActivityAt')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nameWithNamespace') is not None:
            self.name_with_namespace = m.get('nameWithNamespace')
        if m.get('namespace') is not None:
            temp_model = CreateRepositoryResponseBodyResultNamespace()
            self.namespace = temp_model.from_map(m['namespace'])
        if m.get('path') is not None:
            self.path = m.get('path')
        if m.get('pathWithNamespace') is not None:
            self.path_with_namespace = m.get('pathWithNamespace')
        if m.get('sshUrlToRepo') is not None:
            self.ssh_url_to_repo = m.get('sshUrlToRepo')
        if m.get('visibilityLevel') is not None:
            self.visibility_level = m.get('visibilityLevel')
        if m.get('webUrl') is not None:
            self.web_url = m.get('webUrl')
        return self


class CreateRepositoryResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: CreateRepositoryResponseBodyResult = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            self.result.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.result is not None:
            result['result'] = self.result.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('result') is not None:
            temp_model = CreateRepositoryResponseBodyResult()
            self.result = temp_model.from_map(m['result'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateRepositoryResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateRepositoryResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateRepositoryResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateResourceMemberRequest(TeaModel):
    def __init__(
        self,
        account_id: str = None,
        role_name: str = None,
    ):
        self.account_id = account_id
        self.role_name = role_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.account_id is not None:
            result['accountId'] = self.account_id
        if self.role_name is not None:
            result['roleName'] = self.role_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accountId') is not None:
            self.account_id = m.get('accountId')
        if m.get('roleName') is not None:
            self.role_name = m.get('roleName')
        return self


class CreateResourceMemberResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateResourceMemberResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateResourceMemberResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateResourceMemberResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateSprintRequest(TeaModel):
    def __init__(
        self,
        end_date: str = None,
        name: str = None,
        space_identifier: str = None,
        staff_ids: List[str] = None,
        start_date: str = None,
    ):
        self.end_date = end_date
        self.name = name
        self.space_identifier = space_identifier
        self.staff_ids = staff_ids
        self.start_date = start_date

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.end_date is not None:
            result['endDate'] = self.end_date
        if self.name is not None:
            result['name'] = self.name
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.staff_ids is not None:
            result['staffIds'] = self.staff_ids
        if self.start_date is not None:
            result['startDate'] = self.start_date
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('endDate') is not None:
            self.end_date = m.get('endDate')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('staffIds') is not None:
            self.staff_ids = m.get('staffIds')
        if m.get('startDate') is not None:
            self.start_date = m.get('startDate')
        return self


class CreateSprintResponseBodySprint(TeaModel):
    def __init__(
        self,
        creator: str = None,
        description: str = None,
        end_date: int = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        modifier: str = None,
        name: str = None,
        scope: str = None,
        space_identifier: str = None,
        start_date: int = None,
        status: str = None,
    ):
        self.creator = creator
        self.description = description
        self.end_date = end_date
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.modifier = modifier
        self.name = name
        self.scope = scope
        self.space_identifier = space_identifier
        self.start_date = start_date
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator is not None:
            result['creator'] = self.creator
        if self.description is not None:
            result['description'] = self.description
        if self.end_date is not None:
            result['endDate'] = self.end_date
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.scope is not None:
            result['scope'] = self.scope
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.start_date is not None:
            result['startDate'] = self.start_date
        if self.status is not None:
            result['status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('endDate') is not None:
            self.end_date = m.get('endDate')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('startDate') is not None:
            self.start_date = m.get('startDate')
        if m.get('status') is not None:
            self.status = m.get('status')
        return self


class CreateSprintResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        request_id: str = None,
        sprint: CreateSprintResponseBodySprint = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.request_id = request_id
        self.sprint = sprint
        self.success = success

    def validate(self):
        if self.sprint:
            self.sprint.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.sprint is not None:
            result['sprint'] = self.sprint.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('sprint') is not None:
            temp_model = CreateSprintResponseBodySprint()
            self.sprint = temp_model.from_map(m['sprint'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateSprintResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateSprintResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateSprintResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateSshKeyResponseBodySshKey(TeaModel):
    def __init__(
        self,
        id: int = None,
        public_key: str = None,
    ):
        self.id = id
        self.public_key = public_key

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.public_key is not None:
            result['publicKey'] = self.public_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('publicKey') is not None:
            self.public_key = m.get('publicKey')
        return self


class CreateSshKeyResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        ssh_key: CreateSshKeyResponseBodySshKey = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.ssh_key = ssh_key
        self.success = success

    def validate(self):
        if self.ssh_key:
            self.ssh_key.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.ssh_key is not None:
            result['sshKey'] = self.ssh_key.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('sshKey') is not None:
            temp_model = CreateSshKeyResponseBodySshKey()
            self.ssh_key = temp_model.from_map(m['sshKey'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class CreateSshKeyResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateSshKeyResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateSshKeyResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateVariableGroupRequest(TeaModel):
    def __init__(
        self,
        description: str = None,
        name: str = None,
        variables: str = None,
    ):
        self.description = description
        self.name = name
        self.variables = variables

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.description is not None:
            result['description'] = self.description
        if self.name is not None:
            result['name'] = self.name
        if self.variables is not None:
            result['variables'] = self.variables
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('variables') is not None:
            self.variables = m.get('variables')
        return self


class CreateVariableGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        variable_group_id: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.variable_group_id = variable_group_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.variable_group_id is not None:
            result['variableGroupId'] = self.variable_group_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('variableGroupId') is not None:
            self.variable_group_id = m.get('variableGroupId')
        return self


class CreateVariableGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateVariableGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateVariableGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateWorkitemRequestFieldValueList(TeaModel):
    def __init__(
        self,
        field_identifier: str = None,
        value: str = None,
        workitem_identifier: str = None,
    ):
        self.field_identifier = field_identifier
        self.value = value
        self.workitem_identifier = workitem_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.field_identifier is not None:
            result['fieldIdentifier'] = self.field_identifier
        if self.value is not None:
            result['value'] = self.value
        if self.workitem_identifier is not None:
            result['workitemIdentifier'] = self.workitem_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fieldIdentifier') is not None:
            self.field_identifier = m.get('fieldIdentifier')
        if m.get('value') is not None:
            self.value = m.get('value')
        if m.get('workitemIdentifier') is not None:
            self.workitem_identifier = m.get('workitemIdentifier')
        return self


class CreateWorkitemRequest(TeaModel):
    def __init__(
        self,
        assigned_to: str = None,
        category: str = None,
        description: str = None,
        description_format: str = None,
        field_value_list: List[CreateWorkitemRequestFieldValueList] = None,
        parent: str = None,
        participant: List[str] = None,
        space: str = None,
        space_identifier: str = None,
        space_type: str = None,
        sprint: List[str] = None,
        subject: str = None,
        tracker: List[str] = None,
        verifier: List[str] = None,
        workitem_type: str = None,
    ):
        self.assigned_to = assigned_to
        self.category = category
        self.description = description
        self.description_format = description_format
        self.field_value_list = field_value_list
        self.parent = parent
        self.participant = participant
        self.space = space
        self.space_identifier = space_identifier
        self.space_type = space_type
        self.sprint = sprint
        self.subject = subject
        self.tracker = tracker
        self.verifier = verifier
        self.workitem_type = workitem_type

    def validate(self):
        if self.field_value_list:
            for k in self.field_value_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.assigned_to is not None:
            result['assignedTo'] = self.assigned_to
        if self.category is not None:
            result['category'] = self.category
        if self.description is not None:
            result['description'] = self.description
        if self.description_format is not None:
            result['descriptionFormat'] = self.description_format
        result['fieldValueList'] = []
        if self.field_value_list is not None:
            for k in self.field_value_list:
                result['fieldValueList'].append(k.to_map() if k else None)
        if self.parent is not None:
            result['parent'] = self.parent
        if self.participant is not None:
            result['participant'] = self.participant
        if self.space is not None:
            result['space'] = self.space
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.sprint is not None:
            result['sprint'] = self.sprint
        if self.subject is not None:
            result['subject'] = self.subject
        if self.tracker is not None:
            result['tracker'] = self.tracker
        if self.verifier is not None:
            result['verifier'] = self.verifier
        if self.workitem_type is not None:
            result['workitemType'] = self.workitem_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('assignedTo') is not None:
            self.assigned_to = m.get('assignedTo')
        if m.get('category') is not None:
            self.category = m.get('category')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('descriptionFormat') is not None:
            self.description_format = m.get('descriptionFormat')
        self.field_value_list = []
        if m.get('fieldValueList') is not None:
            for k in m.get('fieldValueList'):
                temp_model = CreateWorkitemRequestFieldValueList()
                self.field_value_list.append(temp_model.from_map(k))
        if m.get('parent') is not None:
            self.parent = m.get('parent')
        if m.get('participant') is not None:
            self.participant = m.get('participant')
        if m.get('space') is not None:
            self.space = m.get('space')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('sprint') is not None:
            self.sprint = m.get('sprint')
        if m.get('subject') is not None:
            self.subject = m.get('subject')
        if m.get('tracker') is not None:
            self.tracker = m.get('tracker')
        if m.get('verifier') is not None:
            self.verifier = m.get('verifier')
        if m.get('workitemType') is not None:
            self.workitem_type = m.get('workitemType')
        return self


class CreateWorkitemResponseBodyWorkitem(TeaModel):
    def __init__(
        self,
        assigned_to: str = None,
        category_identifier: str = None,
        creator: str = None,
        document: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        logical_status: str = None,
        modifier: str = None,
        parent_identifier: str = None,
        serial_number: str = None,
        space_identifier: str = None,
        space_name: str = None,
        space_type: str = None,
        sprint_identifier: str = None,
        status: str = None,
        status_identifier: str = None,
        status_stage_identifier: str = None,
        subject: str = None,
        update_status_at: int = None,
        workitem_type_identifier: str = None,
    ):
        self.assigned_to = assigned_to
        self.category_identifier = category_identifier
        self.creator = creator
        self.document = document
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.logical_status = logical_status
        self.modifier = modifier
        self.parent_identifier = parent_identifier
        self.serial_number = serial_number
        self.space_identifier = space_identifier
        self.space_name = space_name
        self.space_type = space_type
        self.sprint_identifier = sprint_identifier
        self.status = status
        self.status_identifier = status_identifier
        self.status_stage_identifier = status_stage_identifier
        self.subject = subject
        self.update_status_at = update_status_at
        self.workitem_type_identifier = workitem_type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.assigned_to is not None:
            result['assignedTo'] = self.assigned_to
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        if self.document is not None:
            result['document'] = self.document
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.logical_status is not None:
            result['logicalStatus'] = self.logical_status
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.parent_identifier is not None:
            result['parentIdentifier'] = self.parent_identifier
        if self.serial_number is not None:
            result['serialNumber'] = self.serial_number
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_name is not None:
            result['spaceName'] = self.space_name
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.sprint_identifier is not None:
            result['sprintIdentifier'] = self.sprint_identifier
        if self.status is not None:
            result['status'] = self.status
        if self.status_identifier is not None:
            result['statusIdentifier'] = self.status_identifier
        if self.status_stage_identifier is not None:
            result['statusStageIdentifier'] = self.status_stage_identifier
        if self.subject is not None:
            result['subject'] = self.subject
        if self.update_status_at is not None:
            result['updateStatusAt'] = self.update_status_at
        if self.workitem_type_identifier is not None:
            result['workitemTypeIdentifier'] = self.workitem_type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('assignedTo') is not None:
            self.assigned_to = m.get('assignedTo')
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('document') is not None:
            self.document = m.get('document')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('logicalStatus') is not None:
            self.logical_status = m.get('logicalStatus')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('parentIdentifier') is not None:
            self.parent_identifier = m.get('parentIdentifier')
        if m.get('serialNumber') is not None:
            self.serial_number = m.get('serialNumber')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceName') is not None:
            self.space_name = m.get('spaceName')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('sprintIdentifier') is not None:
            self.sprint_identifier = m.get('sprintIdentifier')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('statusIdentifier') is not None:
            self.status_identifier = m.get('statusIdentifier')
        if m.get('statusStageIdentifier') is not None:
            self.status_stage_identifier = m.get('statusStageIdentifier')
        if m.get('subject') is not None:
            self.subject = m.get('subject')
        if m.get('updateStatusAt') is not None:
            self.update_status_at = m.get('updateStatusAt')
        if m.get('workitemTypeIdentifier') is not None:
            self.workitem_type_identifier = m.get('workitemTypeIdentifier')
        return self


class CreateWorkitemResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        request_id: str = None,
        success: bool = None,
        workitem: CreateWorkitemResponseBodyWorkitem = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.request_id = request_id
        self.success = success
        self.workitem = workitem

    def validate(self):
        if self.workitem:
            self.workitem.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.workitem is not None:
            result['workitem'] = self.workitem.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('workitem') is not None:
            temp_model = CreateWorkitemResponseBodyWorkitem()
            self.workitem = temp_model.from_map(m['workitem'])
        return self


class CreateWorkitemResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateWorkitemResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateWorkitemResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateWorkspaceRequest(TeaModel):
    def __init__(
        self,
        code_url: str = None,
        code_version: str = None,
        file_path: str = None,
        name: str = None,
        request_from: str = None,
        resource_identifier: str = None,
        reuse: bool = None,
        workspace_template: str = None,
    ):
        self.code_url = code_url
        self.code_version = code_version
        self.file_path = file_path
        self.name = name
        self.request_from = request_from
        self.resource_identifier = resource_identifier
        self.reuse = reuse
        self.workspace_template = workspace_template

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code_url is not None:
            result['codeUrl'] = self.code_url
        if self.code_version is not None:
            result['codeVersion'] = self.code_version
        if self.file_path is not None:
            result['filePath'] = self.file_path
        if self.name is not None:
            result['name'] = self.name
        if self.request_from is not None:
            result['requestFrom'] = self.request_from
        if self.resource_identifier is not None:
            result['resourceIdentifier'] = self.resource_identifier
        if self.reuse is not None:
            result['reuse'] = self.reuse
        if self.workspace_template is not None:
            result['workspaceTemplate'] = self.workspace_template
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('codeUrl') is not None:
            self.code_url = m.get('codeUrl')
        if m.get('codeVersion') is not None:
            self.code_version = m.get('codeVersion')
        if m.get('filePath') is not None:
            self.file_path = m.get('filePath')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('requestFrom') is not None:
            self.request_from = m.get('requestFrom')
        if m.get('resourceIdentifier') is not None:
            self.resource_identifier = m.get('resourceIdentifier')
        if m.get('reuse') is not None:
            self.reuse = m.get('reuse')
        if m.get('workspaceTemplate') is not None:
            self.workspace_template = m.get('workspaceTemplate')
        return self


class CreateWorkspaceResponseBodyWorkspace(TeaModel):
    def __init__(
        self,
        create_time: str = None,
        creator: str = None,
        id: str = None,
        name: str = None,
        status: str = None,
        template: str = None,
    ):
        self.create_time = create_time
        self.creator = creator
        self.id = id
        self.name = name
        self.status = status
        self.template = template

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator is not None:
            result['creator'] = self.creator
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.status is not None:
            result['status'] = self.status
        if self.template is not None:
            result['template'] = self.template
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('template') is not None:
            self.template = m.get('template')
        return self


class CreateWorkspaceResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        workspace: CreateWorkspaceResponseBodyWorkspace = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.workspace = workspace

    def validate(self):
        if self.workspace:
            self.workspace.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.workspace is not None:
            result['workspace'] = self.workspace.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('workspace') is not None:
            temp_model = CreateWorkspaceResponseBodyWorkspace()
            self.workspace = temp_model.from_map(m['workspace'])
        return self


class CreateWorkspaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateWorkspaceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateWorkspaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteFlowTagResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeleteFlowTagResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteFlowTagResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteFlowTagResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteFlowTagGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeleteFlowTagGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteFlowTagGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteFlowTagGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteHostGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeleteHostGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteHostGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteHostGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeletePipelineResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeletePipelineResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeletePipelineResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeletePipelineResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeletePipelineGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeletePipelineGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeletePipelineGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeletePipelineGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteProjectRequest(TeaModel):
    def __init__(
        self,
        identifier: str = None,
    ):
        self.identifier = identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.identifier is not None:
            result['identifier'] = self.identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        return self


class DeleteProjectResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        request_id: str = None,
        result: bool = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.result is not None:
            result['result'] = self.result
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('result') is not None:
            self.result = m.get('result')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeleteProjectResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteProjectResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteProjectResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteResourceMemberResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeleteResourceMemberResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteResourceMemberResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteResourceMemberResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteVariableGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class DeleteVariableGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteVariableGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteVariableGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class FrozenWorkspaceResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class FrozenWorkspaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: FrozenWorkspaceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = FrozenWorkspaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetCodeupOrganizationRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
    ):
        self.access_token = access_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['AccessToken'] = self.access_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AccessToken') is not None:
            self.access_token = m.get('AccessToken')
        return self


class GetCodeupOrganizationResponseBodyResult(TeaModel):
    def __init__(
        self,
        created_at: str = None,
        id: int = None,
        namespace_id: int = None,
        organization_id: str = None,
        path: str = None,
        updated_at: str = None,
        user_role: str = None,
    ):
        self.created_at = created_at
        self.id = id
        self.namespace_id = namespace_id
        self.organization_id = organization_id
        self.path = path
        self.updated_at = updated_at
        self.user_role = user_role

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.created_at is not None:
            result['CreatedAt'] = self.created_at
        if self.id is not None:
            result['Id'] = self.id
        if self.namespace_id is not None:
            result['NamespaceId'] = self.namespace_id
        if self.organization_id is not None:
            result['OrganizationId'] = self.organization_id
        if self.path is not None:
            result['Path'] = self.path
        if self.updated_at is not None:
            result['UpdatedAt'] = self.updated_at
        if self.user_role is not None:
            result['UserRole'] = self.user_role
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CreatedAt') is not None:
            self.created_at = m.get('CreatedAt')
        if m.get('Id') is not None:
            self.id = m.get('Id')
        if m.get('NamespaceId') is not None:
            self.namespace_id = m.get('NamespaceId')
        if m.get('OrganizationId') is not None:
            self.organization_id = m.get('OrganizationId')
        if m.get('Path') is not None:
            self.path = m.get('Path')
        if m.get('UpdatedAt') is not None:
            self.updated_at = m.get('UpdatedAt')
        if m.get('UserRole') is not None:
            self.user_role = m.get('UserRole')
        return self


class GetCodeupOrganizationResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: GetCodeupOrganizationResponseBodyResult = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            self.result.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['ErrorCode'] = self.error_code
        if self.error_message is not None:
            result['ErrorMessage'] = self.error_message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.result is not None:
            result['Result'] = self.result.to_map()
        if self.success is not None:
            result['Success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ErrorCode') is not None:
            self.error_code = m.get('ErrorCode')
        if m.get('ErrorMessage') is not None:
            self.error_message = m.get('ErrorMessage')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('Result') is not None:
            temp_model = GetCodeupOrganizationResponseBodyResult()
            self.result = temp_model.from_map(m['Result'])
        if m.get('Success') is not None:
            self.success = m.get('Success')
        return self


class GetCodeupOrganizationResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetCodeupOrganizationResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetCodeupOrganizationResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetCustomFieldOptionRequest(TeaModel):
    def __init__(
        self,
        space_identifier: str = None,
        space_type: str = None,
        workitem_type_identifier: str = None,
    ):
        self.space_identifier = space_identifier
        self.space_type = space_type
        self.workitem_type_identifier = workitem_type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.workitem_type_identifier is not None:
            result['workitemTypeIdentifier'] = self.workitem_type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('workitemTypeIdentifier') is not None:
            self.workitem_type_identifier = m.get('workitemTypeIdentifier')
        return self


class GetCustomFieldOptionResponseBodyFileds(TeaModel):
    def __init__(
        self,
        display_value: str = None,
        field_identifier: str = None,
        identifier: str = None,
        level: int = None,
        position: int = None,
        value: str = None,
        value_en: str = None,
    ):
        self.display_value = display_value
        self.field_identifier = field_identifier
        self.identifier = identifier
        self.level = level
        self.position = position
        self.value = value
        self.value_en = value_en

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.display_value is not None:
            result['displayValue'] = self.display_value
        if self.field_identifier is not None:
            result['fieldIdentifier'] = self.field_identifier
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.level is not None:
            result['level'] = self.level
        if self.position is not None:
            result['position'] = self.position
        if self.value is not None:
            result['value'] = self.value
        if self.value_en is not None:
            result['valueEn'] = self.value_en
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('displayValue') is not None:
            self.display_value = m.get('displayValue')
        if m.get('fieldIdentifier') is not None:
            self.field_identifier = m.get('fieldIdentifier')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('level') is not None:
            self.level = m.get('level')
        if m.get('position') is not None:
            self.position = m.get('position')
        if m.get('value') is not None:
            self.value = m.get('value')
        if m.get('valueEn') is not None:
            self.value_en = m.get('valueEn')
        return self


class GetCustomFieldOptionResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        fileds: List[GetCustomFieldOptionResponseBodyFileds] = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.fileds = fileds
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.fileds:
            for k in self.fileds:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        result['fileds'] = []
        if self.fileds is not None:
            for k in self.fileds:
                result['fileds'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        self.fileds = []
        if m.get('fileds') is not None:
            for k in m.get('fileds'):
                temp_model = GetCustomFieldOptionResponseBodyFileds()
                self.fileds.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetCustomFieldOptionResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetCustomFieldOptionResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetCustomFieldOptionResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetFileLastCommitRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        filepath: str = None,
        organization_id: str = None,
        sha: str = None,
    ):
        self.access_token = access_token
        self.filepath = filepath
        self.organization_id = organization_id
        self.sha = sha

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.filepath is not None:
            result['filepath'] = self.filepath
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        if self.sha is not None:
            result['sha'] = self.sha
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('filepath') is not None:
            self.filepath = m.get('filepath')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        if m.get('sha') is not None:
            self.sha = m.get('sha')
        return self


class GetFileLastCommitResponseBodyResultSignature(TeaModel):
    def __init__(
        self,
        gpg_key_id: str = None,
        verification_status: str = None,
    ):
        self.gpg_key_id = gpg_key_id
        self.verification_status = verification_status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.gpg_key_id is not None:
            result['GpgKeyId'] = self.gpg_key_id
        if self.verification_status is not None:
            result['VerificationStatus'] = self.verification_status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('GpgKeyId') is not None:
            self.gpg_key_id = m.get('GpgKeyId')
        if m.get('VerificationStatus') is not None:
            self.verification_status = m.get('VerificationStatus')
        return self


class GetFileLastCommitResponseBodyResult(TeaModel):
    def __init__(
        self,
        author_date: str = None,
        author_email: str = None,
        author_name: str = None,
        committed_date: str = None,
        committer_email: str = None,
        committer_name: str = None,
        created_at: str = None,
        id: str = None,
        message: str = None,
        parent_ids: List[str] = None,
        short_id: str = None,
        signature: GetFileLastCommitResponseBodyResultSignature = None,
        title: str = None,
    ):
        self.author_date = author_date
        self.author_email = author_email
        self.author_name = author_name
        self.committed_date = committed_date
        self.committer_email = committer_email
        self.committer_name = committer_name
        self.created_at = created_at
        self.id = id
        self.message = message
        self.parent_ids = parent_ids
        self.short_id = short_id
        self.signature = signature
        self.title = title

    def validate(self):
        if self.signature:
            self.signature.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.author_date is not None:
            result['AuthorDate'] = self.author_date
        if self.author_email is not None:
            result['AuthorEmail'] = self.author_email
        if self.author_name is not None:
            result['AuthorName'] = self.author_name
        if self.committed_date is not None:
            result['CommittedDate'] = self.committed_date
        if self.committer_email is not None:
            result['CommitterEmail'] = self.committer_email
        if self.committer_name is not None:
            result['CommitterName'] = self.committer_name
        if self.created_at is not None:
            result['CreatedAt'] = self.created_at
        if self.id is not None:
            result['Id'] = self.id
        if self.message is not None:
            result['Message'] = self.message
        if self.parent_ids is not None:
            result['ParentIds'] = self.parent_ids
        if self.short_id is not None:
            result['ShortId'] = self.short_id
        if self.signature is not None:
            result['Signature'] = self.signature.to_map()
        if self.title is not None:
            result['Title'] = self.title
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AuthorDate') is not None:
            self.author_date = m.get('AuthorDate')
        if m.get('AuthorEmail') is not None:
            self.author_email = m.get('AuthorEmail')
        if m.get('AuthorName') is not None:
            self.author_name = m.get('AuthorName')
        if m.get('CommittedDate') is not None:
            self.committed_date = m.get('CommittedDate')
        if m.get('CommitterEmail') is not None:
            self.committer_email = m.get('CommitterEmail')
        if m.get('CommitterName') is not None:
            self.committer_name = m.get('CommitterName')
        if m.get('CreatedAt') is not None:
            self.created_at = m.get('CreatedAt')
        if m.get('Id') is not None:
            self.id = m.get('Id')
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('ParentIds') is not None:
            self.parent_ids = m.get('ParentIds')
        if m.get('ShortId') is not None:
            self.short_id = m.get('ShortId')
        if m.get('Signature') is not None:
            temp_model = GetFileLastCommitResponseBodyResultSignature()
            self.signature = temp_model.from_map(m['Signature'])
        if m.get('Title') is not None:
            self.title = m.get('Title')
        return self


class GetFileLastCommitResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: GetFileLastCommitResponseBodyResult = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            self.result.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['ErrorCode'] = self.error_code
        if self.error_message is not None:
            result['ErrorMessage'] = self.error_message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.result is not None:
            result['Result'] = self.result.to_map()
        if self.success is not None:
            result['Success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ErrorCode') is not None:
            self.error_code = m.get('ErrorCode')
        if m.get('ErrorMessage') is not None:
            self.error_message = m.get('ErrorMessage')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('Result') is not None:
            temp_model = GetFileLastCommitResponseBodyResult()
            self.result = temp_model.from_map(m['Result'])
        if m.get('Success') is not None:
            self.success = m.get('Success')
        return self


class GetFileLastCommitResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetFileLastCommitResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetFileLastCommitResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetFlowTagGroupResponseBodyFlowTagGroupFlowTagList(TeaModel):
    def __init__(
        self,
        color: str = None,
        creator_account_id: str = None,
        id: int = None,
        modifer_account_id: str = None,
        name: str = None,
    ):
        self.color = color
        self.creator_account_id = creator_account_id
        self.id = id
        self.modifer_account_id = modifer_account_id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.color is not None:
            result['color'] = self.color
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.id is not None:
            result['id'] = self.id
        if self.modifer_account_id is not None:
            result['modiferAccountId'] = self.modifer_account_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('color') is not None:
            self.color = m.get('color')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('modiferAccountId') is not None:
            self.modifer_account_id = m.get('modiferAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class GetFlowTagGroupResponseBodyFlowTagGroup(TeaModel):
    def __init__(
        self,
        creator_account_id: str = None,
        flow_tag_list: List[GetFlowTagGroupResponseBodyFlowTagGroupFlowTagList] = None,
        id: int = None,
        modifer_account_id: str = None,
        name: str = None,
    ):
        self.creator_account_id = creator_account_id
        self.flow_tag_list = flow_tag_list
        self.id = id
        self.modifer_account_id = modifer_account_id
        self.name = name

    def validate(self):
        if self.flow_tag_list:
            for k in self.flow_tag_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        result['flowTagList'] = []
        if self.flow_tag_list is not None:
            for k in self.flow_tag_list:
                result['flowTagList'].append(k.to_map() if k else None)
        if self.id is not None:
            result['id'] = self.id
        if self.modifer_account_id is not None:
            result['modiferAccountId'] = self.modifer_account_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        self.flow_tag_list = []
        if m.get('flowTagList') is not None:
            for k in m.get('flowTagList'):
                temp_model = GetFlowTagGroupResponseBodyFlowTagGroupFlowTagList()
                self.flow_tag_list.append(temp_model.from_map(k))
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('modiferAccountId') is not None:
            self.modifer_account_id = m.get('modiferAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class GetFlowTagGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        flow_tag_group: GetFlowTagGroupResponseBodyFlowTagGroup = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.flow_tag_group = flow_tag_group
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.flow_tag_group:
            self.flow_tag_group.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.flow_tag_group is not None:
            result['flowTagGroup'] = self.flow_tag_group.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('flowTagGroup') is not None:
            temp_model = GetFlowTagGroupResponseBodyFlowTagGroup()
            self.flow_tag_group = temp_model.from_map(m['flowTagGroup'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetFlowTagGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetFlowTagGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetFlowTagGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetHostGroupResponseBodyHostGroupHostInfos(TeaModel):
    def __init__(
        self,
        aliyun_region_id: str = None,
        create_time: int = None,
        creator_account_id: str = None,
        instance_name: str = None,
        ip: str = None,
        machine_sn: str = None,
        modifier_account_id: str = None,
        object_type: str = None,
        update_time: int = None,
    ):
        self.aliyun_region_id = aliyun_region_id
        self.create_time = create_time
        self.creator_account_id = creator_account_id
        self.instance_name = instance_name
        self.ip = ip
        self.machine_sn = machine_sn
        self.modifier_account_id = modifier_account_id
        self.object_type = object_type
        self.update_time = update_time

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.aliyun_region_id is not None:
            result['aliyunRegionId'] = self.aliyun_region_id
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.instance_name is not None:
            result['instanceName'] = self.instance_name
        if self.ip is not None:
            result['ip'] = self.ip
        if self.machine_sn is not None:
            result['machineSn'] = self.machine_sn
        if self.modifier_account_id is not None:
            result['modifierAccountId'] = self.modifier_account_id
        if self.object_type is not None:
            result['objectType'] = self.object_type
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('aliyunRegionId') is not None:
            self.aliyun_region_id = m.get('aliyunRegionId')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('instanceName') is not None:
            self.instance_name = m.get('instanceName')
        if m.get('ip') is not None:
            self.ip = m.get('ip')
        if m.get('machineSn') is not None:
            self.machine_sn = m.get('machineSn')
        if m.get('modifierAccountId') is not None:
            self.modifier_account_id = m.get('modifierAccountId')
        if m.get('objectType') is not None:
            self.object_type = m.get('objectType')
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        return self


class GetHostGroupResponseBodyHostGroup(TeaModel):
    def __init__(
        self,
        aliyun_region: str = None,
        create_time: int = None,
        creator_account_id: str = None,
        description: str = None,
        ecs_label_key: str = None,
        ecs_label_value: str = None,
        ecs_type: str = None,
        host_infos: List[GetHostGroupResponseBodyHostGroupHostInfos] = None,
        host_num: int = None,
        id: int = None,
        modifier_account_id: str = None,
        name: str = None,
        service_connection_id: int = None,
        type: str = None,
        upate_time: int = None,
    ):
        self.aliyun_region = aliyun_region
        self.create_time = create_time
        self.creator_account_id = creator_account_id
        self.description = description
        self.ecs_label_key = ecs_label_key
        self.ecs_label_value = ecs_label_value
        self.ecs_type = ecs_type
        self.host_infos = host_infos
        self.host_num = host_num
        self.id = id
        self.modifier_account_id = modifier_account_id
        self.name = name
        self.service_connection_id = service_connection_id
        self.type = type
        self.upate_time = upate_time

    def validate(self):
        if self.host_infos:
            for k in self.host_infos:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.aliyun_region is not None:
            result['aliyunRegion'] = self.aliyun_region
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.description is not None:
            result['description'] = self.description
        if self.ecs_label_key is not None:
            result['ecsLabelKey'] = self.ecs_label_key
        if self.ecs_label_value is not None:
            result['ecsLabelValue'] = self.ecs_label_value
        if self.ecs_type is not None:
            result['ecsType'] = self.ecs_type
        result['hostInfos'] = []
        if self.host_infos is not None:
            for k in self.host_infos:
                result['hostInfos'].append(k.to_map() if k else None)
        if self.host_num is not None:
            result['hostNum'] = self.host_num
        if self.id is not None:
            result['id'] = self.id
        if self.modifier_account_id is not None:
            result['modifierAccountId'] = self.modifier_account_id
        if self.name is not None:
            result['name'] = self.name
        if self.service_connection_id is not None:
            result['serviceConnectionId'] = self.service_connection_id
        if self.type is not None:
            result['type'] = self.type
        if self.upate_time is not None:
            result['upateTIme'] = self.upate_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('aliyunRegion') is not None:
            self.aliyun_region = m.get('aliyunRegion')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('ecsLabelKey') is not None:
            self.ecs_label_key = m.get('ecsLabelKey')
        if m.get('ecsLabelValue') is not None:
            self.ecs_label_value = m.get('ecsLabelValue')
        if m.get('ecsType') is not None:
            self.ecs_type = m.get('ecsType')
        self.host_infos = []
        if m.get('hostInfos') is not None:
            for k in m.get('hostInfos'):
                temp_model = GetHostGroupResponseBodyHostGroupHostInfos()
                self.host_infos.append(temp_model.from_map(k))
        if m.get('hostNum') is not None:
            self.host_num = m.get('hostNum')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('modifierAccountId') is not None:
            self.modifier_account_id = m.get('modifierAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('serviceConnectionId') is not None:
            self.service_connection_id = m.get('serviceConnectionId')
        if m.get('type') is not None:
            self.type = m.get('type')
        if m.get('upateTIme') is not None:
            self.upate_time = m.get('upateTIme')
        return self


class GetHostGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        host_group: GetHostGroupResponseBodyHostGroup = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.host_group = host_group
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.host_group:
            self.host_group.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.host_group is not None:
            result['hostGroup'] = self.host_group.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('hostGroup') is not None:
            temp_model = GetHostGroupResponseBodyHostGroup()
            self.host_group = temp_model.from_map(m['hostGroup'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetHostGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetHostGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetHostGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetOrganizationMemberResponseBodyMemberIdentities(TeaModel):
    def __init__(
        self,
        extern_uid: str = None,
        provider: str = None,
    ):
        self.extern_uid = extern_uid
        self.provider = provider

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.extern_uid is not None:
            result['externUid'] = self.extern_uid
        if self.provider is not None:
            result['provider'] = self.provider
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('externUid') is not None:
            self.extern_uid = m.get('externUid')
        if m.get('provider') is not None:
            self.provider = m.get('provider')
        return self


class GetOrganizationMemberResponseBodyMember(TeaModel):
    def __init__(
        self,
        account_id: str = None,
        birthday: int = None,
        dept_lists: List[str] = None,
        email: str = None,
        hired_date: int = None,
        identities: GetOrganizationMemberResponseBodyMemberIdentities = None,
        join_time: int = None,
        last_visit_time: int = None,
        mobile: str = None,
        organization_member_name: str = None,
        organization_role_id: str = None,
        organization_role_name: str = None,
        state: str = None,
    ):
        self.account_id = account_id
        self.birthday = birthday
        self.dept_lists = dept_lists
        self.email = email
        self.hired_date = hired_date
        self.identities = identities
        self.join_time = join_time
        self.last_visit_time = last_visit_time
        self.mobile = mobile
        self.organization_member_name = organization_member_name
        self.organization_role_id = organization_role_id
        self.organization_role_name = organization_role_name
        self.state = state

    def validate(self):
        if self.identities:
            self.identities.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.account_id is not None:
            result['accountId'] = self.account_id
        if self.birthday is not None:
            result['birthday'] = self.birthday
        if self.dept_lists is not None:
            result['deptLists'] = self.dept_lists
        if self.email is not None:
            result['email'] = self.email
        if self.hired_date is not None:
            result['hiredDate'] = self.hired_date
        if self.identities is not None:
            result['identities'] = self.identities.to_map()
        if self.join_time is not None:
            result['joinTime'] = self.join_time
        if self.last_visit_time is not None:
            result['lastVisitTime'] = self.last_visit_time
        if self.mobile is not None:
            result['mobile'] = self.mobile
        if self.organization_member_name is not None:
            result['organizationMemberName'] = self.organization_member_name
        if self.organization_role_id is not None:
            result['organizationRoleId'] = self.organization_role_id
        if self.organization_role_name is not None:
            result['organizationRoleName'] = self.organization_role_name
        if self.state is not None:
            result['state'] = self.state
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accountId') is not None:
            self.account_id = m.get('accountId')
        if m.get('birthday') is not None:
            self.birthday = m.get('birthday')
        if m.get('deptLists') is not None:
            self.dept_lists = m.get('deptLists')
        if m.get('email') is not None:
            self.email = m.get('email')
        if m.get('hiredDate') is not None:
            self.hired_date = m.get('hiredDate')
        if m.get('identities') is not None:
            temp_model = GetOrganizationMemberResponseBodyMemberIdentities()
            self.identities = temp_model.from_map(m['identities'])
        if m.get('joinTime') is not None:
            self.join_time = m.get('joinTime')
        if m.get('lastVisitTime') is not None:
            self.last_visit_time = m.get('lastVisitTime')
        if m.get('mobile') is not None:
            self.mobile = m.get('mobile')
        if m.get('organizationMemberName') is not None:
            self.organization_member_name = m.get('organizationMemberName')
        if m.get('organizationRoleId') is not None:
            self.organization_role_id = m.get('organizationRoleId')
        if m.get('organizationRoleName') is not None:
            self.organization_role_name = m.get('organizationRoleName')
        if m.get('state') is not None:
            self.state = m.get('state')
        return self


class GetOrganizationMemberResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        member: GetOrganizationMemberResponseBodyMember = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.member = member
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.member:
            self.member.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.member is not None:
            result['member'] = self.member.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('member') is not None:
            temp_model = GetOrganizationMemberResponseBodyMember()
            self.member = temp_model.from_map(m['member'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetOrganizationMemberResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetOrganizationMemberResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetOrganizationMemberResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetPipelineResponseBodyPipelinePipelineConfigSourcesData(TeaModel):
    def __init__(
        self,
        branch: str = None,
        clone_depth: int = None,
        credential_id: int = None,
        credential_label: str = None,
        credential_type: str = None,
        events: List[str] = None,
        is_branch_mode: bool = None,
        is_clone_depth: bool = None,
        is_submodule: bool = None,
        is_trigger: bool = None,
        label: str = None,
        namespace: str = None,
        repo: str = None,
        service_connection_id: int = None,
        trigger_filter: str = None,
        webhook: str = None,
    ):
        self.branch = branch
        self.clone_depth = clone_depth
        self.credential_id = credential_id
        self.credential_label = credential_label
        self.credential_type = credential_type
        self.events = events
        self.is_branch_mode = is_branch_mode
        self.is_clone_depth = is_clone_depth
        self.is_submodule = is_submodule
        self.is_trigger = is_trigger
        self.label = label
        self.namespace = namespace
        self.repo = repo
        self.service_connection_id = service_connection_id
        self.trigger_filter = trigger_filter
        self.webhook = webhook

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.branch is not None:
            result['branch'] = self.branch
        if self.clone_depth is not None:
            result['cloneDepth'] = self.clone_depth
        if self.credential_id is not None:
            result['credentialId'] = self.credential_id
        if self.credential_label is not None:
            result['credentialLabel'] = self.credential_label
        if self.credential_type is not None:
            result['credentialType'] = self.credential_type
        if self.events is not None:
            result['events'] = self.events
        if self.is_branch_mode is not None:
            result['isBranchMode'] = self.is_branch_mode
        if self.is_clone_depth is not None:
            result['isCloneDepth'] = self.is_clone_depth
        if self.is_submodule is not None:
            result['isSubmodule'] = self.is_submodule
        if self.is_trigger is not None:
            result['isTrigger'] = self.is_trigger
        if self.label is not None:
            result['label'] = self.label
        if self.namespace is not None:
            result['namespace'] = self.namespace
        if self.repo is not None:
            result['repo'] = self.repo
        if self.service_connection_id is not None:
            result['serviceConnectionId'] = self.service_connection_id
        if self.trigger_filter is not None:
            result['triggerFilter'] = self.trigger_filter
        if self.webhook is not None:
            result['webhook'] = self.webhook
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('branch') is not None:
            self.branch = m.get('branch')
        if m.get('cloneDepth') is not None:
            self.clone_depth = m.get('cloneDepth')
        if m.get('credentialId') is not None:
            self.credential_id = m.get('credentialId')
        if m.get('credentialLabel') is not None:
            self.credential_label = m.get('credentialLabel')
        if m.get('credentialType') is not None:
            self.credential_type = m.get('credentialType')
        if m.get('events') is not None:
            self.events = m.get('events')
        if m.get('isBranchMode') is not None:
            self.is_branch_mode = m.get('isBranchMode')
        if m.get('isCloneDepth') is not None:
            self.is_clone_depth = m.get('isCloneDepth')
        if m.get('isSubmodule') is not None:
            self.is_submodule = m.get('isSubmodule')
        if m.get('isTrigger') is not None:
            self.is_trigger = m.get('isTrigger')
        if m.get('label') is not None:
            self.label = m.get('label')
        if m.get('namespace') is not None:
            self.namespace = m.get('namespace')
        if m.get('repo') is not None:
            self.repo = m.get('repo')
        if m.get('serviceConnectionId') is not None:
            self.service_connection_id = m.get('serviceConnectionId')
        if m.get('triggerFilter') is not None:
            self.trigger_filter = m.get('triggerFilter')
        if m.get('webhook') is not None:
            self.webhook = m.get('webhook')
        return self


class GetPipelineResponseBodyPipelinePipelineConfigSources(TeaModel):
    def __init__(
        self,
        data: GetPipelineResponseBodyPipelinePipelineConfigSourcesData = None,
        sign: str = None,
        type: str = None,
    ):
        self.data = data
        self.sign = sign
        self.type = type

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['data'] = self.data.to_map()
        if self.sign is not None:
            result['sign'] = self.sign
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('data') is not None:
            temp_model = GetPipelineResponseBodyPipelinePipelineConfigSourcesData()
            self.data = temp_model.from_map(m['data'])
        if m.get('sign') is not None:
            self.sign = m.get('sign')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class GetPipelineResponseBodyPipelinePipelineConfig(TeaModel):
    def __init__(
        self,
        flow: str = None,
        settings: str = None,
        sources: List[GetPipelineResponseBodyPipelinePipelineConfigSources] = None,
    ):
        self.flow = flow
        self.settings = settings
        self.sources = sources

    def validate(self):
        if self.sources:
            for k in self.sources:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.flow is not None:
            result['flow'] = self.flow
        if self.settings is not None:
            result['settings'] = self.settings
        result['sources'] = []
        if self.sources is not None:
            for k in self.sources:
                result['sources'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('flow') is not None:
            self.flow = m.get('flow')
        if m.get('settings') is not None:
            self.settings = m.get('settings')
        self.sources = []
        if m.get('sources') is not None:
            for k in m.get('sources'):
                temp_model = GetPipelineResponseBodyPipelinePipelineConfigSources()
                self.sources.append(temp_model.from_map(k))
        return self


class GetPipelineResponseBodyPipelineTagList(TeaModel):
    def __init__(
        self,
        id: int = None,
        name: str = None,
    ):
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class GetPipelineResponseBodyPipeline(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        creator_account_id: str = None,
        env_id: int = None,
        env_name: str = None,
        group_id: int = None,
        modifier_account_id: str = None,
        name: str = None,
        pipeline_config: GetPipelineResponseBodyPipelinePipelineConfig = None,
        tag_list: List[GetPipelineResponseBodyPipelineTagList] = None,
        update_time: int = None,
    ):
        self.create_time = create_time
        self.creator_account_id = creator_account_id
        self.env_id = env_id
        self.env_name = env_name
        self.group_id = group_id
        self.modifier_account_id = modifier_account_id
        self.name = name
        self.pipeline_config = pipeline_config
        self.tag_list = tag_list
        self.update_time = update_time

    def validate(self):
        if self.pipeline_config:
            self.pipeline_config.validate()
        if self.tag_list:
            for k in self.tag_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.env_id is not None:
            result['envId'] = self.env_id
        if self.env_name is not None:
            result['envName'] = self.env_name
        if self.group_id is not None:
            result['groupId'] = self.group_id
        if self.modifier_account_id is not None:
            result['modifierAccountId'] = self.modifier_account_id
        if self.name is not None:
            result['name'] = self.name
        if self.pipeline_config is not None:
            result['pipelineConfig'] = self.pipeline_config.to_map()
        result['tagList'] = []
        if self.tag_list is not None:
            for k in self.tag_list:
                result['tagList'].append(k.to_map() if k else None)
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('envId') is not None:
            self.env_id = m.get('envId')
        if m.get('envName') is not None:
            self.env_name = m.get('envName')
        if m.get('groupId') is not None:
            self.group_id = m.get('groupId')
        if m.get('modifierAccountId') is not None:
            self.modifier_account_id = m.get('modifierAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('pipelineConfig') is not None:
            temp_model = GetPipelineResponseBodyPipelinePipelineConfig()
            self.pipeline_config = temp_model.from_map(m['pipelineConfig'])
        self.tag_list = []
        if m.get('tagList') is not None:
            for k in m.get('tagList'):
                temp_model = GetPipelineResponseBodyPipelineTagList()
                self.tag_list.append(temp_model.from_map(k))
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        return self


class GetPipelineResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        pipeline: GetPipelineResponseBodyPipeline = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.pipeline = pipeline
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.pipeline:
            self.pipeline.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.pipeline is not None:
            result['pipeline'] = self.pipeline.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('pipeline') is not None:
            temp_model = GetPipelineResponseBodyPipeline()
            self.pipeline = temp_model.from_map(m['pipeline'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetPipelineResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetPipelineResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetPipelineResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetPipelineArtifactUrlRequest(TeaModel):
    def __init__(
        self,
        file_name: str = None,
        file_path: str = None,
    ):
        self.file_name = file_name
        self.file_path = file_path

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.file_name is not None:
            result['fileName'] = self.file_name
        if self.file_path is not None:
            result['filePath'] = self.file_path
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fileName') is not None:
            self.file_name = m.get('fileName')
        if m.get('filePath') is not None:
            self.file_path = m.get('filePath')
        return self


class GetPipelineArtifactUrlResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        file_url: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.file_url = file_url
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.file_url is not None:
            result['fileUrl'] = self.file_url
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('fileUrl') is not None:
            self.file_url = m.get('fileUrl')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetPipelineArtifactUrlResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetPipelineArtifactUrlResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetPipelineArtifactUrlResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetPipelineEmasArtifactUrlRequest(TeaModel):
    def __init__(
        self,
        service_connection_id: int = None,
    ):
        self.service_connection_id = service_connection_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.service_connection_id is not None:
            result['serviceConnectionId'] = self.service_connection_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('serviceConnectionId') is not None:
            self.service_connection_id = m.get('serviceConnectionId')
        return self


class GetPipelineEmasArtifactUrlResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        file_url: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.file_url = file_url
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.file_url is not None:
            result['fileUrl'] = self.file_url
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('fileUrl') is not None:
            self.file_url = m.get('fileUrl')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetPipelineEmasArtifactUrlResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetPipelineEmasArtifactUrlResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetPipelineEmasArtifactUrlResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetPipelineGroupResponseBodyPipelineGroup(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        id: int = None,
        name: str = None,
    ):
        self.create_time = create_time
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class GetPipelineGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        pipeline_group: GetPipelineGroupResponseBodyPipelineGroup = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.pipeline_group = pipeline_group
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.pipeline_group:
            self.pipeline_group.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.pipeline_group is not None:
            result['pipelineGroup'] = self.pipeline_group.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('pipelineGroup') is not None:
            temp_model = GetPipelineGroupResponseBodyPipelineGroup()
            self.pipeline_group = temp_model.from_map(m['pipelineGroup'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetPipelineGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetPipelineGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetPipelineGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetPipelineRunResponseBodyPipelineRunSourcesData(TeaModel):
    def __init__(
        self,
        branch: str = None,
        commint: str = None,
        repo: str = None,
    ):
        self.branch = branch
        self.commint = commint
        self.repo = repo

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.branch is not None:
            result['branch'] = self.branch
        if self.commint is not None:
            result['commint'] = self.commint
        if self.repo is not None:
            result['repo'] = self.repo
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('branch') is not None:
            self.branch = m.get('branch')
        if m.get('commint') is not None:
            self.commint = m.get('commint')
        if m.get('repo') is not None:
            self.repo = m.get('repo')
        return self


class GetPipelineRunResponseBodyPipelineRunSources(TeaModel):
    def __init__(
        self,
        data: GetPipelineRunResponseBodyPipelineRunSourcesData = None,
        sign: str = None,
        type: str = None,
    ):
        self.data = data
        self.sign = sign
        self.type = type

    def validate(self):
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.data is not None:
            result['data'] = self.data.to_map()
        if self.sign is not None:
            result['sign'] = self.sign
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('data') is not None:
            temp_model = GetPipelineRunResponseBodyPipelineRunSourcesData()
            self.data = temp_model.from_map(m['data'])
        if m.get('sign') is not None:
            self.sign = m.get('sign')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class GetPipelineRunResponseBodyPipelineRunStagesStageInfoJobsActions(TeaModel):
    def __init__(
        self,
        disable: bool = None,
        params: Dict[str, Any] = None,
        type: str = None,
    ):
        self.disable = disable
        self.params = params
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.disable is not None:
            result['disable'] = self.disable
        if self.params is not None:
            result['params'] = self.params
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('disable') is not None:
            self.disable = m.get('disable')
        if m.get('params') is not None:
            self.params = m.get('params')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class GetPipelineRunResponseBodyPipelineRunStagesStageInfoJobs(TeaModel):
    def __init__(
        self,
        actions: List[GetPipelineRunResponseBodyPipelineRunStagesStageInfoJobsActions] = None,
        end_time: int = None,
        id: int = None,
        name: str = None,
        params: str = None,
        start_time: int = None,
        status: str = None,
    ):
        self.actions = actions
        self.end_time = end_time
        self.id = id
        self.name = name
        self.params = params
        self.start_time = start_time
        self.status = status

    def validate(self):
        if self.actions:
            for k in self.actions:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['actions'] = []
        if self.actions is not None:
            for k in self.actions:
                result['actions'].append(k.to_map() if k else None)
        if self.end_time is not None:
            result['endTime'] = self.end_time
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.params is not None:
            result['params'] = self.params
        if self.start_time is not None:
            result['startTime'] = self.start_time
        if self.status is not None:
            result['status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.actions = []
        if m.get('actions') is not None:
            for k in m.get('actions'):
                temp_model = GetPipelineRunResponseBodyPipelineRunStagesStageInfoJobsActions()
                self.actions.append(temp_model.from_map(k))
        if m.get('endTime') is not None:
            self.end_time = m.get('endTime')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('params') is not None:
            self.params = m.get('params')
        if m.get('startTime') is not None:
            self.start_time = m.get('startTime')
        if m.get('status') is not None:
            self.status = m.get('status')
        return self


class GetPipelineRunResponseBodyPipelineRunStagesStageInfo(TeaModel):
    def __init__(
        self,
        end_time: int = None,
        jobs: List[GetPipelineRunResponseBodyPipelineRunStagesStageInfoJobs] = None,
        name: str = None,
        start_time: int = None,
        status: str = None,
    ):
        self.end_time = end_time
        self.jobs = jobs
        self.name = name
        self.start_time = start_time
        self.status = status

    def validate(self):
        if self.jobs:
            for k in self.jobs:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.end_time is not None:
            result['endTime'] = self.end_time
        result['jobs'] = []
        if self.jobs is not None:
            for k in self.jobs:
                result['jobs'].append(k.to_map() if k else None)
        if self.name is not None:
            result['name'] = self.name
        if self.start_time is not None:
            result['startTime'] = self.start_time
        if self.status is not None:
            result['status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('endTime') is not None:
            self.end_time = m.get('endTime')
        self.jobs = []
        if m.get('jobs') is not None:
            for k in m.get('jobs'):
                temp_model = GetPipelineRunResponseBodyPipelineRunStagesStageInfoJobs()
                self.jobs.append(temp_model.from_map(k))
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('startTime') is not None:
            self.start_time = m.get('startTime')
        if m.get('status') is not None:
            self.status = m.get('status')
        return self


class GetPipelineRunResponseBodyPipelineRunStages(TeaModel):
    def __init__(
        self,
        name: str = None,
        stage_info: GetPipelineRunResponseBodyPipelineRunStagesStageInfo = None,
    ):
        self.name = name
        self.stage_info = stage_info

    def validate(self):
        if self.stage_info:
            self.stage_info.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        if self.stage_info is not None:
            result['stageInfo'] = self.stage_info.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('stageInfo') is not None:
            temp_model = GetPipelineRunResponseBodyPipelineRunStagesStageInfo()
            self.stage_info = temp_model.from_map(m['stageInfo'])
        return self


class GetPipelineRunResponseBodyPipelineRun(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        creator_account_id: str = None,
        modifier_account_id: str = None,
        pipeline_id: int = None,
        pipeline_run_id: int = None,
        sources: List[GetPipelineRunResponseBodyPipelineRunSources] = None,
        stage_group: List[List[str]] = None,
        stages: List[GetPipelineRunResponseBodyPipelineRunStages] = None,
        status: str = None,
        trigger_mode: int = None,
        update_time: int = None,
    ):
        self.create_time = create_time
        self.creator_account_id = creator_account_id
        self.modifier_account_id = modifier_account_id
        self.pipeline_id = pipeline_id
        self.pipeline_run_id = pipeline_run_id
        self.sources = sources
        self.stage_group = stage_group
        self.stages = stages
        self.status = status
        self.trigger_mode = trigger_mode
        self.update_time = update_time

    def validate(self):
        if self.sources:
            for k in self.sources:
                if k:
                    k.validate()
        if self.stages:
            for k in self.stages:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.modifier_account_id is not None:
            result['modifierAccountId'] = self.modifier_account_id
        if self.pipeline_id is not None:
            result['pipelineId'] = self.pipeline_id
        if self.pipeline_run_id is not None:
            result['pipelineRunId'] = self.pipeline_run_id
        result['sources'] = []
        if self.sources is not None:
            for k in self.sources:
                result['sources'].append(k.to_map() if k else None)
        if self.stage_group is not None:
            result['stageGroup'] = self.stage_group
        result['stages'] = []
        if self.stages is not None:
            for k in self.stages:
                result['stages'].append(k.to_map() if k else None)
        if self.status is not None:
            result['status'] = self.status
        if self.trigger_mode is not None:
            result['triggerMode'] = self.trigger_mode
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('modifierAccountId') is not None:
            self.modifier_account_id = m.get('modifierAccountId')
        if m.get('pipelineId') is not None:
            self.pipeline_id = m.get('pipelineId')
        if m.get('pipelineRunId') is not None:
            self.pipeline_run_id = m.get('pipelineRunId')
        self.sources = []
        if m.get('sources') is not None:
            for k in m.get('sources'):
                temp_model = GetPipelineRunResponseBodyPipelineRunSources()
                self.sources.append(temp_model.from_map(k))
        if m.get('stageGroup') is not None:
            self.stage_group = m.get('stageGroup')
        self.stages = []
        if m.get('stages') is not None:
            for k in m.get('stages'):
                temp_model = GetPipelineRunResponseBodyPipelineRunStages()
                self.stages.append(temp_model.from_map(k))
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('triggerMode') is not None:
            self.trigger_mode = m.get('triggerMode')
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        return self


class GetPipelineRunResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        pipeline_run: GetPipelineRunResponseBodyPipelineRun = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.pipeline_run = pipeline_run
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.pipeline_run:
            self.pipeline_run.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.pipeline_run is not None:
            result['pipelineRun'] = self.pipeline_run.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('pipelineRun') is not None:
            temp_model = GetPipelineRunResponseBodyPipelineRun()
            self.pipeline_run = temp_model.from_map(m['pipelineRun'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetPipelineRunResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetPipelineRunResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetPipelineRunResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetPipelineScanReportUrlRequest(TeaModel):
    def __init__(
        self,
        report_path: str = None,
    ):
        self.report_path = report_path

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.report_path is not None:
            result['reportPath'] = self.report_path
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('reportPath') is not None:
            self.report_path = m.get('reportPath')
        return self


class GetPipelineScanReportUrlResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        report_url: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.report_url = report_url
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.report_url is not None:
            result['reportUrl'] = self.report_url
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('reportUrl') is not None:
            self.report_url = m.get('reportUrl')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetPipelineScanReportUrlResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetPipelineScanReportUrlResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetPipelineScanReportUrlResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetProjectInfoResponseBodyProject(TeaModel):
    def __init__(
        self,
        category: str = None,
        category_identifier: str = None,
        creator: str = None,
        custom_code: str = None,
        description: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        icon: str = None,
        icon_big: str = None,
        icon_group: str = None,
        icon_small: str = None,
        id: str = None,
        identifier: str = None,
        identifier_path: str = None,
        logical_status: str = None,
        modifier: str = None,
        name: str = None,
        organization_identifier: str = None,
        parent_identifier: str = None,
        scope: str = None,
        status_identifier: str = None,
        status_stage_identifier: str = None,
        sub_type: str = None,
        type_identifier: str = None,
    ):
        self.category = category
        self.category_identifier = category_identifier
        self.creator = creator
        self.custom_code = custom_code
        self.description = description
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.icon = icon
        self.icon_big = icon_big
        self.icon_group = icon_group
        self.icon_small = icon_small
        self.id = id
        self.identifier = identifier
        self.identifier_path = identifier_path
        self.logical_status = logical_status
        self.modifier = modifier
        self.name = name
        self.organization_identifier = organization_identifier
        self.parent_identifier = parent_identifier
        self.scope = scope
        self.status_identifier = status_identifier
        self.status_stage_identifier = status_stage_identifier
        self.sub_type = sub_type
        self.type_identifier = type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category is not None:
            result['category'] = self.category
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        if self.custom_code is not None:
            result['customCode'] = self.custom_code
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.icon is not None:
            result['icon'] = self.icon
        if self.icon_big is not None:
            result['iconBig'] = self.icon_big
        if self.icon_group is not None:
            result['iconGroup'] = self.icon_group
        if self.icon_small is not None:
            result['iconSmall'] = self.icon_small
        if self.id is not None:
            result['id'] = self.id
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.identifier_path is not None:
            result['identifierPath'] = self.identifier_path
        if self.logical_status is not None:
            result['logicalStatus'] = self.logical_status
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.organization_identifier is not None:
            result['organizationIdentifier'] = self.organization_identifier
        if self.parent_identifier is not None:
            result['parentIdentifier'] = self.parent_identifier
        if self.scope is not None:
            result['scope'] = self.scope
        if self.status_identifier is not None:
            result['statusIdentifier'] = self.status_identifier
        if self.status_stage_identifier is not None:
            result['statusStageIdentifier'] = self.status_stage_identifier
        if self.sub_type is not None:
            result['subType'] = self.sub_type
        if self.type_identifier is not None:
            result['typeIdentifier'] = self.type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('category') is not None:
            self.category = m.get('category')
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('customCode') is not None:
            self.custom_code = m.get('customCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('icon') is not None:
            self.icon = m.get('icon')
        if m.get('iconBig') is not None:
            self.icon_big = m.get('iconBig')
        if m.get('iconGroup') is not None:
            self.icon_group = m.get('iconGroup')
        if m.get('iconSmall') is not None:
            self.icon_small = m.get('iconSmall')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('identifierPath') is not None:
            self.identifier_path = m.get('identifierPath')
        if m.get('logicalStatus') is not None:
            self.logical_status = m.get('logicalStatus')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('organizationIdentifier') is not None:
            self.organization_identifier = m.get('organizationIdentifier')
        if m.get('parentIdentifier') is not None:
            self.parent_identifier = m.get('parentIdentifier')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('statusIdentifier') is not None:
            self.status_identifier = m.get('statusIdentifier')
        if m.get('statusStageIdentifier') is not None:
            self.status_stage_identifier = m.get('statusStageIdentifier')
        if m.get('subType') is not None:
            self.sub_type = m.get('subType')
        if m.get('typeIdentifier') is not None:
            self.type_identifier = m.get('typeIdentifier')
        return self


class GetProjectInfoResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        project: GetProjectInfoResponseBodyProject = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.project = project
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.project:
            self.project.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.project is not None:
            result['project'] = self.project.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('project') is not None:
            temp_model = GetProjectInfoResponseBodyProject()
            self.project = temp_model.from_map(m['project'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetProjectInfoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetProjectInfoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetProjectInfoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetProjectMemberRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        organization_id: str = None,
        repository_id: int = None,
        user_aliyun_pk: str = None,
    ):
        self.access_token = access_token
        self.organization_id = organization_id
        self.repository_id = repository_id
        self.user_aliyun_pk = user_aliyun_pk

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['AccessToken'] = self.access_token
        if self.organization_id is not None:
            result['OrganizationId'] = self.organization_id
        if self.repository_id is not None:
            result['repositoryId'] = self.repository_id
        if self.user_aliyun_pk is not None:
            result['userAliyunPk'] = self.user_aliyun_pk
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AccessToken') is not None:
            self.access_token = m.get('AccessToken')
        if m.get('OrganizationId') is not None:
            self.organization_id = m.get('OrganizationId')
        if m.get('repositoryId') is not None:
            self.repository_id = m.get('repositoryId')
        if m.get('userAliyunPk') is not None:
            self.user_aliyun_pk = m.get('userAliyunPk')
        return self


class GetProjectMemberResponseBodyResult(TeaModel):
    def __init__(
        self,
        access_level: int = None,
        avatar_url: str = None,
        extern_user_id: str = None,
        id: int = None,
        name: str = None,
    ):
        self.access_level = access_level
        self.avatar_url = avatar_url
        self.extern_user_id = extern_user_id
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_level is not None:
            result['accessLevel'] = self.access_level
        if self.avatar_url is not None:
            result['avatarUrl'] = self.avatar_url
        if self.extern_user_id is not None:
            result['externUserId'] = self.extern_user_id
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessLevel') is not None:
            self.access_level = m.get('accessLevel')
        if m.get('avatarUrl') is not None:
            self.avatar_url = m.get('avatarUrl')
        if m.get('externUserId') is not None:
            self.extern_user_id = m.get('externUserId')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class GetProjectMemberResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: GetProjectMemberResponseBodyResult = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            self.result.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.result is not None:
            result['result'] = self.result.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('result') is not None:
            temp_model = GetProjectMemberResponseBodyResult()
            self.result = temp_model.from_map(m['result'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetProjectMemberResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetProjectMemberResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetProjectMemberResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetRepositoryRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        identity: str = None,
        organization_id: str = None,
    ):
        self.access_token = access_token
        self.identity = identity
        self.organization_id = organization_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.identity is not None:
            result['identity'] = self.identity
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('identity') is not None:
            self.identity = m.get('identity')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        return self


class GetRepositoryResponseBodyRepositoryNamespace(TeaModel):
    def __init__(
        self,
        avatar: str = None,
        created_at: str = None,
        description: str = None,
        id: int = None,
        name: str = None,
        owner_id: int = None,
        path: str = None,
        updated_at: str = None,
        visibility_level: int = None,
    ):
        self.avatar = avatar
        self.created_at = created_at
        self.description = description
        self.id = id
        self.name = name
        self.owner_id = owner_id
        self.path = path
        self.updated_at = updated_at
        self.visibility_level = visibility_level

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.avatar is not None:
            result['avatar'] = self.avatar
        if self.created_at is not None:
            result['createdAt'] = self.created_at
        if self.description is not None:
            result['description'] = self.description
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.owner_id is not None:
            result['ownerId'] = self.owner_id
        if self.path is not None:
            result['path'] = self.path
        if self.updated_at is not None:
            result['updatedAt'] = self.updated_at
        if self.visibility_level is not None:
            result['visibilityLevel'] = self.visibility_level
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('avatar') is not None:
            self.avatar = m.get('avatar')
        if m.get('createdAt') is not None:
            self.created_at = m.get('createdAt')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('ownerId') is not None:
            self.owner_id = m.get('ownerId')
        if m.get('path') is not None:
            self.path = m.get('path')
        if m.get('updatedAt') is not None:
            self.updated_at = m.get('updatedAt')
        if m.get('visibilityLevel') is not None:
            self.visibility_level = m.get('visibilityLevel')
        return self


class GetRepositoryResponseBodyRepository(TeaModel):
    def __init__(
        self,
        archive: bool = None,
        avatar_url: str = None,
        created_at: str = None,
        creator_id: int = None,
        default_branch: str = None,
        demo_project_status: bool = None,
        description: str = None,
        http_url_to_repository: str = None,
        id: int = None,
        last_activity_at: str = None,
        name: str = None,
        name_with_namespace: str = None,
        namespace: GetRepositoryResponseBodyRepositoryNamespace = None,
        path: str = None,
        path_with_namespace: str = None,
        ssh_url_to_repository: str = None,
        visibility_level: int = None,
        web_url: str = None,
    ):
        self.archive = archive
        self.avatar_url = avatar_url
        self.created_at = created_at
        self.creator_id = creator_id
        self.default_branch = default_branch
        self.demo_project_status = demo_project_status
        self.description = description
        self.http_url_to_repository = http_url_to_repository
        self.id = id
        self.last_activity_at = last_activity_at
        self.name = name
        self.name_with_namespace = name_with_namespace
        self.namespace = namespace
        self.path = path
        self.path_with_namespace = path_with_namespace
        self.ssh_url_to_repository = ssh_url_to_repository
        self.visibility_level = visibility_level
        self.web_url = web_url

    def validate(self):
        if self.namespace:
            self.namespace.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.archive is not None:
            result['archive'] = self.archive
        if self.avatar_url is not None:
            result['avatarUrl'] = self.avatar_url
        if self.created_at is not None:
            result['createdAt'] = self.created_at
        if self.creator_id is not None:
            result['creatorId'] = self.creator_id
        if self.default_branch is not None:
            result['defaultBranch'] = self.default_branch
        if self.demo_project_status is not None:
            result['demoProjectStatus'] = self.demo_project_status
        if self.description is not None:
            result['description'] = self.description
        if self.http_url_to_repository is not None:
            result['httpUrlToRepository'] = self.http_url_to_repository
        if self.id is not None:
            result['id'] = self.id
        if self.last_activity_at is not None:
            result['lastActivityAt'] = self.last_activity_at
        if self.name is not None:
            result['name'] = self.name
        if self.name_with_namespace is not None:
            result['nameWithNamespace'] = self.name_with_namespace
        if self.namespace is not None:
            result['namespace'] = self.namespace.to_map()
        if self.path is not None:
            result['path'] = self.path
        if self.path_with_namespace is not None:
            result['pathWithNamespace'] = self.path_with_namespace
        if self.ssh_url_to_repository is not None:
            result['sshUrlToRepository'] = self.ssh_url_to_repository
        if self.visibility_level is not None:
            result['visibilityLevel'] = self.visibility_level
        if self.web_url is not None:
            result['webUrl'] = self.web_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('archive') is not None:
            self.archive = m.get('archive')
        if m.get('avatarUrl') is not None:
            self.avatar_url = m.get('avatarUrl')
        if m.get('createdAt') is not None:
            self.created_at = m.get('createdAt')
        if m.get('creatorId') is not None:
            self.creator_id = m.get('creatorId')
        if m.get('defaultBranch') is not None:
            self.default_branch = m.get('defaultBranch')
        if m.get('demoProjectStatus') is not None:
            self.demo_project_status = m.get('demoProjectStatus')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('httpUrlToRepository') is not None:
            self.http_url_to_repository = m.get('httpUrlToRepository')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('lastActivityAt') is not None:
            self.last_activity_at = m.get('lastActivityAt')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nameWithNamespace') is not None:
            self.name_with_namespace = m.get('nameWithNamespace')
        if m.get('namespace') is not None:
            temp_model = GetRepositoryResponseBodyRepositoryNamespace()
            self.namespace = temp_model.from_map(m['namespace'])
        if m.get('path') is not None:
            self.path = m.get('path')
        if m.get('pathWithNamespace') is not None:
            self.path_with_namespace = m.get('pathWithNamespace')
        if m.get('sshUrlToRepository') is not None:
            self.ssh_url_to_repository = m.get('sshUrlToRepository')
        if m.get('visibilityLevel') is not None:
            self.visibility_level = m.get('visibilityLevel')
        if m.get('webUrl') is not None:
            self.web_url = m.get('webUrl')
        return self


class GetRepositoryResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        repository: GetRepositoryResponseBodyRepository = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.repository = repository
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.repository:
            self.repository.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.repository is not None:
            result['repository'] = self.repository.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('repository') is not None:
            temp_model = GetRepositoryResponseBodyRepository()
            self.repository = temp_model.from_map(m['repository'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetRepositoryResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetRepositoryResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetRepositoryResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetSprintInfoResponseBodySprint(TeaModel):
    def __init__(
        self,
        creator: str = None,
        description: str = None,
        end_date: int = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        modifier: str = None,
        name: str = None,
        scope: str = None,
        space_identifier: str = None,
        start_date: int = None,
        status: str = None,
    ):
        self.creator = creator
        self.description = description
        self.end_date = end_date
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.modifier = modifier
        self.name = name
        self.scope = scope
        self.space_identifier = space_identifier
        self.start_date = start_date
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator is not None:
            result['creator'] = self.creator
        if self.description is not None:
            result['description'] = self.description
        if self.end_date is not None:
            result['endDate'] = self.end_date
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.scope is not None:
            result['scope'] = self.scope
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.start_date is not None:
            result['startDate'] = self.start_date
        if self.status is not None:
            result['status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('endDate') is not None:
            self.end_date = m.get('endDate')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('startDate') is not None:
            self.start_date = m.get('startDate')
        if m.get('status') is not None:
            self.status = m.get('status')
        return self


class GetSprintInfoResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        sprint: GetSprintInfoResponseBodySprint = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.sprint = sprint
        self.success = success

    def validate(self):
        if self.sprint:
            self.sprint.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.sprint is not None:
            result['sprint'] = self.sprint.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('sprint') is not None:
            temp_model = GetSprintInfoResponseBodySprint()
            self.sprint = temp_model.from_map(m['sprint'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetSprintInfoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetSprintInfoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetSprintInfoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetVMDeployOrderResponseBodyDeployOrderActions(TeaModel):
    def __init__(
        self,
        disable: bool = None,
        params: Any = None,
        type: str = None,
    ):
        self.disable = disable
        self.params = params
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.disable is not None:
            result['disable'] = self.disable
        if self.params is not None:
            result['params'] = self.params
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('disable') is not None:
            self.disable = m.get('disable')
        if m.get('params') is not None:
            self.params = m.get('params')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfoDeployMachinesActions(TeaModel):
    def __init__(
        self,
        disable: bool = None,
        params: Any = None,
        type: str = None,
    ):
        self.disable = disable
        self.params = params
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.disable is not None:
            result['disable'] = self.disable
        if self.params is not None:
            result['params'] = self.params
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('disable') is not None:
            self.disable = m.get('disable')
        if m.get('params') is not None:
            self.params = m.get('params')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfoDeployMachines(TeaModel):
    def __init__(
        self,
        actions: List[GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfoDeployMachinesActions] = None,
        batch_num: int = None,
        client_status: str = None,
        create_time: int = None,
        ip: str = None,
        machine_sn: str = None,
        status: str = None,
        update_time: int = None,
    ):
        self.actions = actions
        self.batch_num = batch_num
        self.client_status = client_status
        self.create_time = create_time
        self.ip = ip
        self.machine_sn = machine_sn
        self.status = status
        self.update_time = update_time

    def validate(self):
        if self.actions:
            for k in self.actions:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['actions'] = []
        if self.actions is not None:
            for k in self.actions:
                result['actions'].append(k.to_map() if k else None)
        if self.batch_num is not None:
            result['batchNum'] = self.batch_num
        if self.client_status is not None:
            result['clientStatus'] = self.client_status
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.ip is not None:
            result['ip'] = self.ip
        if self.machine_sn is not None:
            result['machineSn'] = self.machine_sn
        if self.status is not None:
            result['status'] = self.status
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.actions = []
        if m.get('actions') is not None:
            for k in m.get('actions'):
                temp_model = GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfoDeployMachinesActions()
                self.actions.append(temp_model.from_map(k))
        if m.get('batchNum') is not None:
            self.batch_num = m.get('batchNum')
        if m.get('clientStatus') is not None:
            self.client_status = m.get('clientStatus')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('ip') is not None:
            self.ip = m.get('ip')
        if m.get('machineSn') is not None:
            self.machine_sn = m.get('machineSn')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        return self


class GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfo(TeaModel):
    def __init__(
        self,
        batch_num: int = None,
        deploy_machines: List[GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfoDeployMachines] = None,
        host_group_id: int = None,
    ):
        self.batch_num = batch_num
        self.deploy_machines = deploy_machines
        self.host_group_id = host_group_id

    def validate(self):
        if self.deploy_machines:
            for k in self.deploy_machines:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.batch_num is not None:
            result['batchNum'] = self.batch_num
        result['deployMachines'] = []
        if self.deploy_machines is not None:
            for k in self.deploy_machines:
                result['deployMachines'].append(k.to_map() if k else None)
        if self.host_group_id is not None:
            result['hostGroupId'] = self.host_group_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('batchNum') is not None:
            self.batch_num = m.get('batchNum')
        self.deploy_machines = []
        if m.get('deployMachines') is not None:
            for k in m.get('deployMachines'):
                temp_model = GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfoDeployMachines()
                self.deploy_machines.append(temp_model.from_map(k))
        if m.get('hostGroupId') is not None:
            self.host_group_id = m.get('hostGroupId')
        return self


class GetVMDeployOrderResponseBodyDeployOrder(TeaModel):
    def __init__(
        self,
        actions: List[GetVMDeployOrderResponseBodyDeployOrderActions] = None,
        create_time: int = None,
        creator: str = None,
        current_batch: int = None,
        deploy_machine_info: GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfo = None,
        deploy_order_id: str = None,
        exception_code: str = None,
        status: str = None,
        total_batch: int = None,
        update_time: int = None,
    ):
        self.actions = actions
        self.create_time = create_time
        self.creator = creator
        self.current_batch = current_batch
        self.deploy_machine_info = deploy_machine_info
        self.deploy_order_id = deploy_order_id
        self.exception_code = exception_code
        self.status = status
        self.total_batch = total_batch
        self.update_time = update_time

    def validate(self):
        if self.actions:
            for k in self.actions:
                if k:
                    k.validate()
        if self.deploy_machine_info:
            self.deploy_machine_info.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['actions'] = []
        if self.actions is not None:
            for k in self.actions:
                result['actions'].append(k.to_map() if k else None)
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator is not None:
            result['creator'] = self.creator
        if self.current_batch is not None:
            result['currentBatch'] = self.current_batch
        if self.deploy_machine_info is not None:
            result['deployMachineInfo'] = self.deploy_machine_info.to_map()
        if self.deploy_order_id is not None:
            result['deployOrderId'] = self.deploy_order_id
        if self.exception_code is not None:
            result['exceptionCode'] = self.exception_code
        if self.status is not None:
            result['status'] = self.status
        if self.total_batch is not None:
            result['totalBatch'] = self.total_batch
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.actions = []
        if m.get('actions') is not None:
            for k in m.get('actions'):
                temp_model = GetVMDeployOrderResponseBodyDeployOrderActions()
                self.actions.append(temp_model.from_map(k))
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('currentBatch') is not None:
            self.current_batch = m.get('currentBatch')
        if m.get('deployMachineInfo') is not None:
            temp_model = GetVMDeployOrderResponseBodyDeployOrderDeployMachineInfo()
            self.deploy_machine_info = temp_model.from_map(m['deployMachineInfo'])
        if m.get('deployOrderId') is not None:
            self.deploy_order_id = m.get('deployOrderId')
        if m.get('exceptionCode') is not None:
            self.exception_code = m.get('exceptionCode')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('totalBatch') is not None:
            self.total_batch = m.get('totalBatch')
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        return self


class GetVMDeployOrderResponseBody(TeaModel):
    def __init__(
        self,
        deploy_order: GetVMDeployOrderResponseBodyDeployOrder = None,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.deploy_order = deploy_order
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.deploy_order:
            self.deploy_order.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.deploy_order is not None:
            result['deployOrder'] = self.deploy_order.to_map()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deployOrder') is not None:
            temp_model = GetVMDeployOrderResponseBodyDeployOrder()
            self.deploy_order = temp_model.from_map(m['deployOrder'])
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetVMDeployOrderResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetVMDeployOrderResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetVMDeployOrderResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetVariableGroupResponseBodyVariableGroupRelatedPipelines(TeaModel):
    def __init__(
        self,
        id: int = None,
        name: str = None,
    ):
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class GetVariableGroupResponseBodyVariableGroupVariables(TeaModel):
    def __init__(
        self,
        is_encrypted: bool = None,
        name: str = None,
        value: str = None,
    ):
        self.is_encrypted = is_encrypted
        self.name = name
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.is_encrypted is not None:
            result['isEncrypted'] = self.is_encrypted
        if self.name is not None:
            result['name'] = self.name
        if self.value is not None:
            result['value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('isEncrypted') is not None:
            self.is_encrypted = m.get('isEncrypted')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('value') is not None:
            self.value = m.get('value')
        return self


class GetVariableGroupResponseBodyVariableGroup(TeaModel):
    def __init__(
        self,
        ccreator_account_id: str = None,
        create_time: int = None,
        description: str = None,
        id: int = None,
        modifier_account_id: str = None,
        name: str = None,
        related_pipelines: List[GetVariableGroupResponseBodyVariableGroupRelatedPipelines] = None,
        update_time: int = None,
        variables: List[GetVariableGroupResponseBodyVariableGroupVariables] = None,
    ):
        self.ccreator_account_id = ccreator_account_id
        self.create_time = create_time
        self.description = description
        self.id = id
        self.modifier_account_id = modifier_account_id
        self.name = name
        self.related_pipelines = related_pipelines
        self.update_time = update_time
        self.variables = variables

    def validate(self):
        if self.related_pipelines:
            for k in self.related_pipelines:
                if k:
                    k.validate()
        if self.variables:
            for k in self.variables:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ccreator_account_id is not None:
            result['ccreatorAccountId'] = self.ccreator_account_id
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.description is not None:
            result['description'] = self.description
        if self.id is not None:
            result['id'] = self.id
        if self.modifier_account_id is not None:
            result['modifierAccountId'] = self.modifier_account_id
        if self.name is not None:
            result['name'] = self.name
        result['relatedPipelines'] = []
        if self.related_pipelines is not None:
            for k in self.related_pipelines:
                result['relatedPipelines'].append(k.to_map() if k else None)
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        result['variables'] = []
        if self.variables is not None:
            for k in self.variables:
                result['variables'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ccreatorAccountId') is not None:
            self.ccreator_account_id = m.get('ccreatorAccountId')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('modifierAccountId') is not None:
            self.modifier_account_id = m.get('modifierAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        self.related_pipelines = []
        if m.get('relatedPipelines') is not None:
            for k in m.get('relatedPipelines'):
                temp_model = GetVariableGroupResponseBodyVariableGroupRelatedPipelines()
                self.related_pipelines.append(temp_model.from_map(k))
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        self.variables = []
        if m.get('variables') is not None:
            for k in m.get('variables'):
                temp_model = GetVariableGroupResponseBodyVariableGroupVariables()
                self.variables.append(temp_model.from_map(k))
        return self


class GetVariableGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        variable_group: GetVariableGroupResponseBodyVariableGroup = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.variable_group = variable_group

    def validate(self):
        if self.variable_group:
            self.variable_group.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.variable_group is not None:
            result['variableGroup'] = self.variable_group.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('variableGroup') is not None:
            temp_model = GetVariableGroupResponseBodyVariableGroup()
            self.variable_group = temp_model.from_map(m['variableGroup'])
        return self


class GetVariableGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetVariableGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetVariableGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetWorkItemActivityResponseBodyActivitiesProperty(TeaModel):
    def __init__(
        self,
        display_name: str = None,
        property_identifier: str = None,
        property_name: str = None,
        property_type: str = None,
    ):
        self.display_name = display_name
        self.property_identifier = property_identifier
        self.property_name = property_name
        self.property_type = property_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.display_name is not None:
            result['displayName'] = self.display_name
        if self.property_identifier is not None:
            result['propertyIdentifier'] = self.property_identifier
        if self.property_name is not None:
            result['propertyName'] = self.property_name
        if self.property_type is not None:
            result['propertyType'] = self.property_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('displayName') is not None:
            self.display_name = m.get('displayName')
        if m.get('propertyIdentifier') is not None:
            self.property_identifier = m.get('propertyIdentifier')
        if m.get('propertyName') is not None:
            self.property_name = m.get('propertyName')
        if m.get('propertyType') is not None:
            self.property_type = m.get('propertyType')
        return self


class GetWorkItemActivityResponseBodyActivities(TeaModel):
    def __init__(
        self,
        action_type: str = None,
        event_id: int = None,
        event_time: int = None,
        event_type: str = None,
        operator: str = None,
        parent_event_id: int = None,
        property: GetWorkItemActivityResponseBodyActivitiesProperty = None,
        resource_identifier: str = None,
    ):
        self.action_type = action_type
        self.event_id = event_id
        self.event_time = event_time
        self.event_type = event_type
        self.operator = operator
        self.parent_event_id = parent_event_id
        self.property = property
        self.resource_identifier = resource_identifier

    def validate(self):
        if self.property:
            self.property.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.action_type is not None:
            result['actionType'] = self.action_type
        if self.event_id is not None:
            result['eventId'] = self.event_id
        if self.event_time is not None:
            result['eventTime'] = self.event_time
        if self.event_type is not None:
            result['eventType'] = self.event_type
        if self.operator is not None:
            result['operator'] = self.operator
        if self.parent_event_id is not None:
            result['parentEventId'] = self.parent_event_id
        if self.property is not None:
            result['property'] = self.property.to_map()
        if self.resource_identifier is not None:
            result['resourceIdentifier'] = self.resource_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('actionType') is not None:
            self.action_type = m.get('actionType')
        if m.get('eventId') is not None:
            self.event_id = m.get('eventId')
        if m.get('eventTime') is not None:
            self.event_time = m.get('eventTime')
        if m.get('eventType') is not None:
            self.event_type = m.get('eventType')
        if m.get('operator') is not None:
            self.operator = m.get('operator')
        if m.get('parentEventId') is not None:
            self.parent_event_id = m.get('parentEventId')
        if m.get('property') is not None:
            temp_model = GetWorkItemActivityResponseBodyActivitiesProperty()
            self.property = temp_model.from_map(m['property'])
        if m.get('resourceIdentifier') is not None:
            self.resource_identifier = m.get('resourceIdentifier')
        return self


class GetWorkItemActivityResponseBody(TeaModel):
    def __init__(
        self,
        activities: List[GetWorkItemActivityResponseBodyActivities] = None,
        error_code: str = None,
        error_msg: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.activities = activities
        self.error_code = error_code
        self.error_msg = error_msg
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.activities:
            for k in self.activities:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['activities'] = []
        if self.activities is not None:
            for k in self.activities:
                result['activities'].append(k.to_map() if k else None)
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.activities = []
        if m.get('activities') is not None:
            for k in m.get('activities'):
                temp_model = GetWorkItemActivityResponseBodyActivities()
                self.activities.append(temp_model.from_map(k))
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class GetWorkItemActivityResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetWorkItemActivityResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetWorkItemActivityResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetWorkItemInfoResponseBodyWorkitemCustomFieldsValueList(TeaModel):
    def __init__(
        self,
        display_value: str = None,
        identifier: str = None,
        level: int = None,
        value: str = None,
        value_en: str = None,
    ):
        self.display_value = display_value
        self.identifier = identifier
        self.level = level
        self.value = value
        self.value_en = value_en

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.display_value is not None:
            result['displayValue'] = self.display_value
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.level is not None:
            result['level'] = self.level
        if self.value is not None:
            result['value'] = self.value
        if self.value_en is not None:
            result['valueEn'] = self.value_en
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('displayValue') is not None:
            self.display_value = m.get('displayValue')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('level') is not None:
            self.level = m.get('level')
        if m.get('value') is not None:
            self.value = m.get('value')
        if m.get('valueEn') is not None:
            self.value_en = m.get('valueEn')
        return self


class GetWorkItemInfoResponseBodyWorkitemCustomFields(TeaModel):
    def __init__(
        self,
        field_class_name: str = None,
        field_format: str = None,
        field_identifier: str = None,
        level: int = None,
        object_value: str = None,
        position: int = None,
        value: str = None,
        value_list: List[GetWorkItemInfoResponseBodyWorkitemCustomFieldsValueList] = None,
        workitem_identifier: str = None,
    ):
        self.field_class_name = field_class_name
        self.field_format = field_format
        self.field_identifier = field_identifier
        self.level = level
        self.object_value = object_value
        self.position = position
        self.value = value
        self.value_list = value_list
        self.workitem_identifier = workitem_identifier

    def validate(self):
        if self.value_list:
            for k in self.value_list:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.field_class_name is not None:
            result['fieldClassName'] = self.field_class_name
        if self.field_format is not None:
            result['fieldFormat'] = self.field_format
        if self.field_identifier is not None:
            result['fieldIdentifier'] = self.field_identifier
        if self.level is not None:
            result['level'] = self.level
        if self.object_value is not None:
            result['objectValue'] = self.object_value
        if self.position is not None:
            result['position'] = self.position
        if self.value is not None:
            result['value'] = self.value
        result['valueList'] = []
        if self.value_list is not None:
            for k in self.value_list:
                result['valueList'].append(k.to_map() if k else None)
        if self.workitem_identifier is not None:
            result['workitemIdentifier'] = self.workitem_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fieldClassName') is not None:
            self.field_class_name = m.get('fieldClassName')
        if m.get('fieldFormat') is not None:
            self.field_format = m.get('fieldFormat')
        if m.get('fieldIdentifier') is not None:
            self.field_identifier = m.get('fieldIdentifier')
        if m.get('level') is not None:
            self.level = m.get('level')
        if m.get('objectValue') is not None:
            self.object_value = m.get('objectValue')
        if m.get('position') is not None:
            self.position = m.get('position')
        if m.get('value') is not None:
            self.value = m.get('value')
        self.value_list = []
        if m.get('valueList') is not None:
            for k in m.get('valueList'):
                temp_model = GetWorkItemInfoResponseBodyWorkitemCustomFieldsValueList()
                self.value_list.append(temp_model.from_map(k))
        if m.get('workitemIdentifier') is not None:
            self.workitem_identifier = m.get('workitemIdentifier')
        return self


class GetWorkItemInfoResponseBodyWorkitem(TeaModel):
    def __init__(
        self,
        assigned_to: str = None,
        category_identifier: str = None,
        creator: str = None,
        custom_fields: List[GetWorkItemInfoResponseBodyWorkitemCustomFields] = None,
        document: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        logical_status: str = None,
        modifier: str = None,
        parent_identifier: str = None,
        participant: List[str] = None,
        serial_number: str = None,
        space_identifier: str = None,
        space_name: str = None,
        space_type: str = None,
        sprint: List[str] = None,
        status: str = None,
        status_identifier: str = None,
        status_stage_identifier: str = None,
        subject: str = None,
        tag: List[str] = None,
        tracker: List[str] = None,
        update_status_at: int = None,
        verifier: List[str] = None,
        workitem_type_identifier: str = None,
    ):
        self.assigned_to = assigned_to
        self.category_identifier = category_identifier
        self.creator = creator
        self.custom_fields = custom_fields
        self.document = document
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.logical_status = logical_status
        self.modifier = modifier
        self.parent_identifier = parent_identifier
        self.participant = participant
        self.serial_number = serial_number
        self.space_identifier = space_identifier
        self.space_name = space_name
        self.space_type = space_type
        self.sprint = sprint
        self.status = status
        self.status_identifier = status_identifier
        self.status_stage_identifier = status_stage_identifier
        self.subject = subject
        self.tag = tag
        self.tracker = tracker
        self.update_status_at = update_status_at
        self.verifier = verifier
        self.workitem_type_identifier = workitem_type_identifier

    def validate(self):
        if self.custom_fields:
            for k in self.custom_fields:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.assigned_to is not None:
            result['assignedTo'] = self.assigned_to
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        result['customFields'] = []
        if self.custom_fields is not None:
            for k in self.custom_fields:
                result['customFields'].append(k.to_map() if k else None)
        if self.document is not None:
            result['document'] = self.document
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.logical_status is not None:
            result['logicalStatus'] = self.logical_status
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.parent_identifier is not None:
            result['parentIdentifier'] = self.parent_identifier
        if self.participant is not None:
            result['participant'] = self.participant
        if self.serial_number is not None:
            result['serialNumber'] = self.serial_number
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_name is not None:
            result['spaceName'] = self.space_name
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.sprint is not None:
            result['sprint'] = self.sprint
        if self.status is not None:
            result['status'] = self.status
        if self.status_identifier is not None:
            result['statusIdentifier'] = self.status_identifier
        if self.status_stage_identifier is not None:
            result['statusStageIdentifier'] = self.status_stage_identifier
        if self.subject is not None:
            result['subject'] = self.subject
        if self.tag is not None:
            result['tag'] = self.tag
        if self.tracker is not None:
            result['tracker'] = self.tracker
        if self.update_status_at is not None:
            result['updateStatusAt'] = self.update_status_at
        if self.verifier is not None:
            result['verifier'] = self.verifier
        if self.workitem_type_identifier is not None:
            result['workitemTypeIdentifier'] = self.workitem_type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('assignedTo') is not None:
            self.assigned_to = m.get('assignedTo')
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        self.custom_fields = []
        if m.get('customFields') is not None:
            for k in m.get('customFields'):
                temp_model = GetWorkItemInfoResponseBodyWorkitemCustomFields()
                self.custom_fields.append(temp_model.from_map(k))
        if m.get('document') is not None:
            self.document = m.get('document')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('logicalStatus') is not None:
            self.logical_status = m.get('logicalStatus')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('parentIdentifier') is not None:
            self.parent_identifier = m.get('parentIdentifier')
        if m.get('participant') is not None:
            self.participant = m.get('participant')
        if m.get('serialNumber') is not None:
            self.serial_number = m.get('serialNumber')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceName') is not None:
            self.space_name = m.get('spaceName')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('sprint') is not None:
            self.sprint = m.get('sprint')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('statusIdentifier') is not None:
            self.status_identifier = m.get('statusIdentifier')
        if m.get('statusStageIdentifier') is not None:
            self.status_stage_identifier = m.get('statusStageIdentifier')
        if m.get('subject') is not None:
            self.subject = m.get('subject')
        if m.get('tag') is not None:
            self.tag = m.get('tag')
        if m.get('tracker') is not None:
            self.tracker = m.get('tracker')
        if m.get('updateStatusAt') is not None:
            self.update_status_at = m.get('updateStatusAt')
        if m.get('verifier') is not None:
            self.verifier = m.get('verifier')
        if m.get('workitemTypeIdentifier') is not None:
            self.workitem_type_identifier = m.get('workitemTypeIdentifier')
        return self


class GetWorkItemInfoResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        workitem: GetWorkItemInfoResponseBodyWorkitem = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.workitem = workitem

    def validate(self):
        if self.workitem:
            self.workitem.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.workitem is not None:
            result['workitem'] = self.workitem.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('workitem') is not None:
            temp_model = GetWorkItemInfoResponseBodyWorkitem()
            self.workitem = temp_model.from_map(m['workitem'])
        return self


class GetWorkItemInfoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetWorkItemInfoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetWorkItemInfoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetWorkItemWorkFlowInfoRequest(TeaModel):
    def __init__(
        self,
        configuration_id: str = None,
    ):
        self.configuration_id = configuration_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.configuration_id is not None:
            result['configurationId'] = self.configuration_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('configurationId') is not None:
            self.configuration_id = m.get('configurationId')
        return self


class GetWorkItemWorkFlowInfoResponseBodyWorkflowStatuses(TeaModel):
    def __init__(
        self,
        creator: str = None,
        description: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        modifier: str = None,
        name: str = None,
        resource_type: str = None,
        source: str = None,
        workflow_stage_identifier: str = None,
        workflow_stage_name: str = None,
    ):
        self.creator = creator
        self.description = description
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.modifier = modifier
        self.name = name
        self.resource_type = resource_type
        self.source = source
        self.workflow_stage_identifier = workflow_stage_identifier
        self.workflow_stage_name = workflow_stage_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator is not None:
            result['creator'] = self.creator
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.resource_type is not None:
            result['resourceType'] = self.resource_type
        if self.source is not None:
            result['source'] = self.source
        if self.workflow_stage_identifier is not None:
            result['workflowStageIdentifier'] = self.workflow_stage_identifier
        if self.workflow_stage_name is not None:
            result['workflowStageName'] = self.workflow_stage_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('resourceType') is not None:
            self.resource_type = m.get('resourceType')
        if m.get('source') is not None:
            self.source = m.get('source')
        if m.get('workflowStageIdentifier') is not None:
            self.workflow_stage_identifier = m.get('workflowStageIdentifier')
        if m.get('workflowStageName') is not None:
            self.workflow_stage_name = m.get('workflowStageName')
        return self


class GetWorkItemWorkFlowInfoResponseBodyWorkflowWorkflowActions(TeaModel):
    def __init__(
        self,
        id: int = None,
        name: str = None,
        next_workflow_status_identifier: str = None,
        workflow_identifier: str = None,
        workflow_status_identifier: str = None,
    ):
        self.id = id
        self.name = name
        self.next_workflow_status_identifier = next_workflow_status_identifier
        self.workflow_identifier = workflow_identifier
        self.workflow_status_identifier = workflow_status_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.next_workflow_status_identifier is not None:
            result['nextWorkflowStatusIdentifier'] = self.next_workflow_status_identifier
        if self.workflow_identifier is not None:
            result['workflowIdentifier'] = self.workflow_identifier
        if self.workflow_status_identifier is not None:
            result['workflowStatusIdentifier'] = self.workflow_status_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nextWorkflowStatusIdentifier') is not None:
            self.next_workflow_status_identifier = m.get('nextWorkflowStatusIdentifier')
        if m.get('workflowIdentifier') is not None:
            self.workflow_identifier = m.get('workflowIdentifier')
        if m.get('workflowStatusIdentifier') is not None:
            self.workflow_status_identifier = m.get('workflowStatusIdentifier')
        return self


class GetWorkItemWorkFlowInfoResponseBodyWorkflow(TeaModel):
    def __init__(
        self,
        creator: str = None,
        default_status_identifier: str = None,
        description: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        modifier: str = None,
        name: str = None,
        owner_space_identifier: str = None,
        owner_space_type: str = None,
        resource_type: str = None,
        source: str = None,
        status_order: str = None,
        statuses: List[GetWorkItemWorkFlowInfoResponseBodyWorkflowStatuses] = None,
        workflow_actions: List[GetWorkItemWorkFlowInfoResponseBodyWorkflowWorkflowActions] = None,
    ):
        self.creator = creator
        self.default_status_identifier = default_status_identifier
        self.description = description
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.modifier = modifier
        self.name = name
        self.owner_space_identifier = owner_space_identifier
        self.owner_space_type = owner_space_type
        self.resource_type = resource_type
        self.source = source
        self.status_order = status_order
        self.statuses = statuses
        self.workflow_actions = workflow_actions

    def validate(self):
        if self.statuses:
            for k in self.statuses:
                if k:
                    k.validate()
        if self.workflow_actions:
            for k in self.workflow_actions:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator is not None:
            result['creator'] = self.creator
        if self.default_status_identifier is not None:
            result['defaultStatusIdentifier'] = self.default_status_identifier
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.owner_space_identifier is not None:
            result['ownerSpaceIdentifier'] = self.owner_space_identifier
        if self.owner_space_type is not None:
            result['ownerSpaceType'] = self.owner_space_type
        if self.resource_type is not None:
            result['resourceType'] = self.resource_type
        if self.source is not None:
            result['source'] = self.source
        if self.status_order is not None:
            result['statusOrder'] = self.status_order
        result['statuses'] = []
        if self.statuses is not None:
            for k in self.statuses:
                result['statuses'].append(k.to_map() if k else None)
        result['workflowActions'] = []
        if self.workflow_actions is not None:
            for k in self.workflow_actions:
                result['workflowActions'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('defaultStatusIdentifier') is not None:
            self.default_status_identifier = m.get('defaultStatusIdentifier')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('ownerSpaceIdentifier') is not None:
            self.owner_space_identifier = m.get('ownerSpaceIdentifier')
        if m.get('ownerSpaceType') is not None:
            self.owner_space_type = m.get('ownerSpaceType')
        if m.get('resourceType') is not None:
            self.resource_type = m.get('resourceType')
        if m.get('source') is not None:
            self.source = m.get('source')
        if m.get('statusOrder') is not None:
            self.status_order = m.get('statusOrder')
        self.statuses = []
        if m.get('statuses') is not None:
            for k in m.get('statuses'):
                temp_model = GetWorkItemWorkFlowInfoResponseBodyWorkflowStatuses()
                self.statuses.append(temp_model.from_map(k))
        self.workflow_actions = []
        if m.get('workflowActions') is not None:
            for k in m.get('workflowActions'):
                temp_model = GetWorkItemWorkFlowInfoResponseBodyWorkflowWorkflowActions()
                self.workflow_actions.append(temp_model.from_map(k))
        return self


class GetWorkItemWorkFlowInfoResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        workflow: GetWorkItemWorkFlowInfoResponseBodyWorkflow = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.workflow = workflow

    def validate(self):
        if self.workflow:
            self.workflow.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.workflow is not None:
            result['workflow'] = self.workflow.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('workflow') is not None:
            temp_model = GetWorkItemWorkFlowInfoResponseBodyWorkflow()
            self.workflow = temp_model.from_map(m['workflow'])
        return self


class GetWorkItemWorkFlowInfoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetWorkItemWorkFlowInfoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetWorkItemWorkFlowInfoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetWorkspaceResponseBodyWorkspace(TeaModel):
    def __init__(
        self,
        code_url: str = None,
        code_version: str = None,
        create_time: str = None,
        id: str = None,
        name: str = None,
        spec: str = None,
        status: str = None,
        template: str = None,
        user_id: str = None,
    ):
        self.code_url = code_url
        self.code_version = code_version
        self.create_time = create_time
        self.id = id
        self.name = name
        self.spec = spec
        self.status = status
        self.template = template
        self.user_id = user_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code_url is not None:
            result['codeUrl'] = self.code_url
        if self.code_version is not None:
            result['codeVersion'] = self.code_version
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.spec is not None:
            result['spec'] = self.spec
        if self.status is not None:
            result['status'] = self.status
        if self.template is not None:
            result['template'] = self.template
        if self.user_id is not None:
            result['userId'] = self.user_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('codeUrl') is not None:
            self.code_url = m.get('codeUrl')
        if m.get('codeVersion') is not None:
            self.code_version = m.get('codeVersion')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('spec') is not None:
            self.spec = m.get('spec')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('template') is not None:
            self.template = m.get('template')
        if m.get('userId') is not None:
            self.user_id = m.get('userId')
        return self


class GetWorkspaceResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        workspace: GetWorkspaceResponseBodyWorkspace = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.workspace = workspace

    def validate(self):
        if self.workspace:
            self.workspace.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.workspace is not None:
            result['workspace'] = self.workspace.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('workspace') is not None:
            temp_model = GetWorkspaceResponseBodyWorkspace()
            self.workspace = temp_model.from_map(m['workspace'])
        return self


class GetWorkspaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetWorkspaceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetWorkspaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class JoinPipelineGroupRequest(TeaModel):
    def __init__(
        self,
        group_id: int = None,
        pipeline_ids: str = None,
    ):
        self.group_id = group_id
        self.pipeline_ids = pipeline_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.group_id is not None:
            result['groupId'] = self.group_id
        if self.pipeline_ids is not None:
            result['pipelineIds'] = self.pipeline_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('groupId') is not None:
            self.group_id = m.get('groupId')
        if m.get('pipelineIds') is not None:
            self.pipeline_ids = m.get('pipelineIds')
        return self


class JoinPipelineGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class JoinPipelineGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: JoinPipelineGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = JoinPipelineGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListFlowTagGroupsResponseBodyFlowTagGroups(TeaModel):
    def __init__(
        self,
        creator_account_id: str = None,
        id: int = None,
        modifer_account_id: str = None,
        name: str = None,
    ):
        self.creator_account_id = creator_account_id
        self.id = id
        self.modifer_account_id = modifer_account_id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.id is not None:
            result['id'] = self.id
        if self.modifer_account_id is not None:
            result['modiferAccountId'] = self.modifer_account_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('modiferAccountId') is not None:
            self.modifer_account_id = m.get('modiferAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class ListFlowTagGroupsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        flow_tag_groups: List[ListFlowTagGroupsResponseBodyFlowTagGroups] = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.flow_tag_groups = flow_tag_groups
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.flow_tag_groups:
            for k in self.flow_tag_groups:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        result['flowTagGroups'] = []
        if self.flow_tag_groups is not None:
            for k in self.flow_tag_groups:
                result['flowTagGroups'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        self.flow_tag_groups = []
        if m.get('flowTagGroups') is not None:
            for k in m.get('flowTagGroups'):
                temp_model = ListFlowTagGroupsResponseBodyFlowTagGroups()
                self.flow_tag_groups.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListFlowTagGroupsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListFlowTagGroupsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListFlowTagGroupsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListHostGroupsRequest(TeaModel):
    def __init__(
        self,
        create_end_time: int = None,
        create_start_time: int = None,
        creator_account_ids: str = None,
        ids: str = None,
        max_results: int = None,
        name: str = None,
        next_token: str = None,
        page_order: str = None,
        page_sort: str = None,
    ):
        self.create_end_time = create_end_time
        self.create_start_time = create_start_time
        self.creator_account_ids = creator_account_ids
        self.ids = ids
        self.max_results = max_results
        self.name = name
        self.next_token = next_token
        self.page_order = page_order
        self.page_sort = page_sort

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_end_time is not None:
            result['createEndTime'] = self.create_end_time
        if self.create_start_time is not None:
            result['createStartTime'] = self.create_start_time
        if self.creator_account_ids is not None:
            result['creatorAccountIds'] = self.creator_account_ids
        if self.ids is not None:
            result['ids'] = self.ids
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.name is not None:
            result['name'] = self.name
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.page_order is not None:
            result['pageOrder'] = self.page_order
        if self.page_sort is not None:
            result['pageSort'] = self.page_sort
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createEndTime') is not None:
            self.create_end_time = m.get('createEndTime')
        if m.get('createStartTime') is not None:
            self.create_start_time = m.get('createStartTime')
        if m.get('creatorAccountIds') is not None:
            self.creator_account_ids = m.get('creatorAccountIds')
        if m.get('ids') is not None:
            self.ids = m.get('ids')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('pageOrder') is not None:
            self.page_order = m.get('pageOrder')
        if m.get('pageSort') is not None:
            self.page_sort = m.get('pageSort')
        return self


class ListHostGroupsResponseBodyHostGroups(TeaModel):
    def __init__(
        self,
        aliyun_region: str = None,
        create_time: int = None,
        creator_account_id: str = None,
        description: str = None,
        ecs_label_key: str = None,
        ecs_label_value: str = None,
        ecs_type: str = None,
        host_num: int = None,
        id: int = None,
        modifier_account_id: str = None,
        name: str = None,
        service_connection_id: int = None,
        type: str = None,
        update_time: int = None,
    ):
        self.aliyun_region = aliyun_region
        self.create_time = create_time
        self.creator_account_id = creator_account_id
        self.description = description
        self.ecs_label_key = ecs_label_key
        self.ecs_label_value = ecs_label_value
        self.ecs_type = ecs_type
        self.host_num = host_num
        self.id = id
        self.modifier_account_id = modifier_account_id
        self.name = name
        self.service_connection_id = service_connection_id
        self.type = type
        self.update_time = update_time

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.aliyun_region is not None:
            result['aliyunRegion'] = self.aliyun_region
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.description is not None:
            result['description'] = self.description
        if self.ecs_label_key is not None:
            result['ecsLabelKey'] = self.ecs_label_key
        if self.ecs_label_value is not None:
            result['ecsLabelValue'] = self.ecs_label_value
        if self.ecs_type is not None:
            result['ecsType'] = self.ecs_type
        if self.host_num is not None:
            result['hostNum'] = self.host_num
        if self.id is not None:
            result['id'] = self.id
        if self.modifier_account_id is not None:
            result['modifierAccountId'] = self.modifier_account_id
        if self.name is not None:
            result['name'] = self.name
        if self.service_connection_id is not None:
            result['serviceConnectionId'] = self.service_connection_id
        if self.type is not None:
            result['type'] = self.type
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('aliyunRegion') is not None:
            self.aliyun_region = m.get('aliyunRegion')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('ecsLabelKey') is not None:
            self.ecs_label_key = m.get('ecsLabelKey')
        if m.get('ecsLabelValue') is not None:
            self.ecs_label_value = m.get('ecsLabelValue')
        if m.get('ecsType') is not None:
            self.ecs_type = m.get('ecsType')
        if m.get('hostNum') is not None:
            self.host_num = m.get('hostNum')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('modifierAccountId') is not None:
            self.modifier_account_id = m.get('modifierAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('serviceConnectionId') is not None:
            self.service_connection_id = m.get('serviceConnectionId')
        if m.get('type') is not None:
            self.type = m.get('type')
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        return self


class ListHostGroupsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        host_groups: List[ListHostGroupsResponseBodyHostGroups] = None,
        next_token: str = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.host_groups = host_groups
        self.next_token = next_token
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.host_groups:
            for k in self.host_groups:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        result['hostGroups'] = []
        if self.host_groups is not None:
            for k in self.host_groups:
                result['hostGroups'].append(k.to_map() if k else None)
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        self.host_groups = []
        if m.get('hostGroups') is not None:
            for k in m.get('hostGroups'):
                temp_model = ListHostGroupsResponseBodyHostGroups()
                self.host_groups.append(temp_model.from_map(k))
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListHostGroupsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListHostGroupsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListHostGroupsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListOrganizationMembersRequest(TeaModel):
    def __init__(
        self,
        extern_uid: str = None,
        join_time_from: int = None,
        join_time_to: int = None,
        max_results: int = None,
        next_token: str = None,
        organization_member_name: str = None,
        provider: str = None,
        state: str = None,
    ):
        self.extern_uid = extern_uid
        self.join_time_from = join_time_from
        self.join_time_to = join_time_to
        self.max_results = max_results
        self.next_token = next_token
        self.organization_member_name = organization_member_name
        self.provider = provider
        self.state = state

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.extern_uid is not None:
            result['externUid'] = self.extern_uid
        if self.join_time_from is not None:
            result['joinTimeFrom'] = self.join_time_from
        if self.join_time_to is not None:
            result['joinTimeTo'] = self.join_time_to
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.organization_member_name is not None:
            result['organizationMemberName'] = self.organization_member_name
        if self.provider is not None:
            result['provider'] = self.provider
        if self.state is not None:
            result['state'] = self.state
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('externUid') is not None:
            self.extern_uid = m.get('externUid')
        if m.get('joinTimeFrom') is not None:
            self.join_time_from = m.get('joinTimeFrom')
        if m.get('joinTimeTo') is not None:
            self.join_time_to = m.get('joinTimeTo')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('organizationMemberName') is not None:
            self.organization_member_name = m.get('organizationMemberName')
        if m.get('provider') is not None:
            self.provider = m.get('provider')
        if m.get('state') is not None:
            self.state = m.get('state')
        return self


class ListOrganizationMembersResponseBodyMembersIdentities(TeaModel):
    def __init__(
        self,
        extern_uid: str = None,
        provider: str = None,
    ):
        self.extern_uid = extern_uid
        self.provider = provider

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.extern_uid is not None:
            result['externUid'] = self.extern_uid
        if self.provider is not None:
            result['provider'] = self.provider
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('externUid') is not None:
            self.extern_uid = m.get('externUid')
        if m.get('provider') is not None:
            self.provider = m.get('provider')
        return self


class ListOrganizationMembersResponseBodyMembers(TeaModel):
    def __init__(
        self,
        account_id: str = None,
        birthday: int = None,
        dept_lists: List[str] = None,
        email: str = None,
        hired_date: int = None,
        identities: ListOrganizationMembersResponseBodyMembersIdentities = None,
        join_time: int = None,
        last_visit_time: int = None,
        mobile: str = None,
        organization_member_name: str = None,
        organization_role_id: str = None,
        organization_role_name: str = None,
        state: str = None,
    ):
        self.account_id = account_id
        self.birthday = birthday
        self.dept_lists = dept_lists
        self.email = email
        self.hired_date = hired_date
        self.identities = identities
        self.join_time = join_time
        self.last_visit_time = last_visit_time
        self.mobile = mobile
        self.organization_member_name = organization_member_name
        self.organization_role_id = organization_role_id
        self.organization_role_name = organization_role_name
        self.state = state

    def validate(self):
        if self.identities:
            self.identities.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.account_id is not None:
            result['accountId'] = self.account_id
        if self.birthday is not None:
            result['birthday'] = self.birthday
        if self.dept_lists is not None:
            result['deptLists'] = self.dept_lists
        if self.email is not None:
            result['email'] = self.email
        if self.hired_date is not None:
            result['hiredDate'] = self.hired_date
        if self.identities is not None:
            result['identities'] = self.identities.to_map()
        if self.join_time is not None:
            result['joinTime'] = self.join_time
        if self.last_visit_time is not None:
            result['lastVisitTime'] = self.last_visit_time
        if self.mobile is not None:
            result['mobile'] = self.mobile
        if self.organization_member_name is not None:
            result['organizationMemberName'] = self.organization_member_name
        if self.organization_role_id is not None:
            result['organizationRoleId'] = self.organization_role_id
        if self.organization_role_name is not None:
            result['organizationRoleName'] = self.organization_role_name
        if self.state is not None:
            result['state'] = self.state
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accountId') is not None:
            self.account_id = m.get('accountId')
        if m.get('birthday') is not None:
            self.birthday = m.get('birthday')
        if m.get('deptLists') is not None:
            self.dept_lists = m.get('deptLists')
        if m.get('email') is not None:
            self.email = m.get('email')
        if m.get('hiredDate') is not None:
            self.hired_date = m.get('hiredDate')
        if m.get('identities') is not None:
            temp_model = ListOrganizationMembersResponseBodyMembersIdentities()
            self.identities = temp_model.from_map(m['identities'])
        if m.get('joinTime') is not None:
            self.join_time = m.get('joinTime')
        if m.get('lastVisitTime') is not None:
            self.last_visit_time = m.get('lastVisitTime')
        if m.get('mobile') is not None:
            self.mobile = m.get('mobile')
        if m.get('organizationMemberName') is not None:
            self.organization_member_name = m.get('organizationMemberName')
        if m.get('organizationRoleId') is not None:
            self.organization_role_id = m.get('organizationRoleId')
        if m.get('organizationRoleName') is not None:
            self.organization_role_name = m.get('organizationRoleName')
        if m.get('state') is not None:
            self.state = m.get('state')
        return self


class ListOrganizationMembersResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        members: List[ListOrganizationMembersResponseBodyMembers] = None,
        next_token: str = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.members = members
        self.next_token = next_token
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = ListOrganizationMembersResponseBodyMembers()
                self.members.append(temp_model.from_map(k))
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListOrganizationMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListOrganizationMembersResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListOrganizationMembersResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListPipelineGroupPipelinesRequest(TeaModel):
    def __init__(
        self,
        create_end_time: int = None,
        create_start_time: int = None,
        execute_end_time: int = None,
        execute_start_time: int = None,
        max_results: int = None,
        next_token: str = None,
        pipeline_name: str = None,
        result_status_list: str = None,
    ):
        self.create_end_time = create_end_time
        self.create_start_time = create_start_time
        self.execute_end_time = execute_end_time
        self.execute_start_time = execute_start_time
        self.max_results = max_results
        self.next_token = next_token
        self.pipeline_name = pipeline_name
        self.result_status_list = result_status_list

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_end_time is not None:
            result['createEndTime'] = self.create_end_time
        if self.create_start_time is not None:
            result['createStartTime'] = self.create_start_time
        if self.execute_end_time is not None:
            result['executeEndTime'] = self.execute_end_time
        if self.execute_start_time is not None:
            result['executeStartTime'] = self.execute_start_time
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.pipeline_name is not None:
            result['pipelineName'] = self.pipeline_name
        if self.result_status_list is not None:
            result['resultStatusList'] = self.result_status_list
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createEndTime') is not None:
            self.create_end_time = m.get('createEndTime')
        if m.get('createStartTime') is not None:
            self.create_start_time = m.get('createStartTime')
        if m.get('executeEndTime') is not None:
            self.execute_end_time = m.get('executeEndTime')
        if m.get('executeStartTime') is not None:
            self.execute_start_time = m.get('executeStartTime')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('pipelineName') is not None:
            self.pipeline_name = m.get('pipelineName')
        if m.get('resultStatusList') is not None:
            self.result_status_list = m.get('resultStatusList')
        return self


class ListPipelineGroupPipelinesResponseBodyPipelines(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        pipeline_id: int = None,
        pipeline_name: str = None,
    ):
        self.create_time = create_time
        self.pipeline_id = pipeline_id
        self.pipeline_name = pipeline_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.pipeline_id is not None:
            result['pipelineId'] = self.pipeline_id
        if self.pipeline_name is not None:
            result['pipelineName'] = self.pipeline_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('pipelineId') is not None:
            self.pipeline_id = m.get('pipelineId')
        if m.get('pipelineName') is not None:
            self.pipeline_name = m.get('pipelineName')
        return self


class ListPipelineGroupPipelinesResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        next_token: str = None,
        pipelines: List[ListPipelineGroupPipelinesResponseBodyPipelines] = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.next_token = next_token
        self.pipelines = pipelines
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.pipelines:
            for k in self.pipelines:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        result['pipelines'] = []
        if self.pipelines is not None:
            for k in self.pipelines:
                result['pipelines'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        self.pipelines = []
        if m.get('pipelines') is not None:
            for k in m.get('pipelines'):
                temp_model = ListPipelineGroupPipelinesResponseBodyPipelines()
                self.pipelines.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListPipelineGroupPipelinesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListPipelineGroupPipelinesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListPipelineGroupPipelinesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListPipelineGroupsRequest(TeaModel):
    def __init__(
        self,
        max_results: int = None,
        next_token: str = None,
    ):
        self.max_results = max_results
        self.next_token = next_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        return self


class ListPipelineGroupsResponseBodyPipelineGroups(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        id: int = None,
        name: str = None,
    ):
        self.create_time = create_time
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class ListPipelineGroupsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        next_token: str = None,
        pipeline_groups: List[ListPipelineGroupsResponseBodyPipelineGroups] = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.next_token = next_token
        self.pipeline_groups = pipeline_groups
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.pipeline_groups:
            for k in self.pipeline_groups:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        result['pipelineGroups'] = []
        if self.pipeline_groups is not None:
            for k in self.pipeline_groups:
                result['pipelineGroups'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        self.pipeline_groups = []
        if m.get('pipelineGroups') is not None:
            for k in m.get('pipelineGroups'):
                temp_model = ListPipelineGroupsResponseBodyPipelineGroups()
                self.pipeline_groups.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListPipelineGroupsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListPipelineGroupsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListPipelineGroupsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListPipelineJobHistorysRequest(TeaModel):
    def __init__(
        self,
        category: str = None,
        identifier: str = None,
        max_results: int = None,
        next_token: str = None,
    ):
        self.category = category
        self.identifier = identifier
        self.max_results = max_results
        self.next_token = next_token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category is not None:
            result['category'] = self.category
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('category') is not None:
            self.category = m.get('category')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        return self


class ListPipelineJobHistorysResponseBodyJobs(TeaModel):
    def __init__(
        self,
        execute_number: int = None,
        identifier: str = None,
        job_id: int = None,
        job_name: str = None,
        operator_account_id: str = None,
        pipeline_id: int = None,
        pipeline_run_id: int = None,
        sources: str = None,
        status: str = None,
    ):
        self.execute_number = execute_number
        self.identifier = identifier
        self.job_id = job_id
        self.job_name = job_name
        self.operator_account_id = operator_account_id
        self.pipeline_id = pipeline_id
        self.pipeline_run_id = pipeline_run_id
        self.sources = sources
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.execute_number is not None:
            result['executeNumber'] = self.execute_number
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.job_id is not None:
            result['jobId'] = self.job_id
        if self.job_name is not None:
            result['jobName'] = self.job_name
        if self.operator_account_id is not None:
            result['operatorAccountId'] = self.operator_account_id
        if self.pipeline_id is not None:
            result['pipelineId'] = self.pipeline_id
        if self.pipeline_run_id is not None:
            result['pipelineRunId'] = self.pipeline_run_id
        if self.sources is not None:
            result['sources'] = self.sources
        if self.status is not None:
            result['status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('executeNumber') is not None:
            self.execute_number = m.get('executeNumber')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('jobId') is not None:
            self.job_id = m.get('jobId')
        if m.get('jobName') is not None:
            self.job_name = m.get('jobName')
        if m.get('operatorAccountId') is not None:
            self.operator_account_id = m.get('operatorAccountId')
        if m.get('pipelineId') is not None:
            self.pipeline_id = m.get('pipelineId')
        if m.get('pipelineRunId') is not None:
            self.pipeline_run_id = m.get('pipelineRunId')
        if m.get('sources') is not None:
            self.sources = m.get('sources')
        if m.get('status') is not None:
            self.status = m.get('status')
        return self


class ListPipelineJobHistorysResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        jobs: List[ListPipelineJobHistorysResponseBodyJobs] = None,
        next_token: str = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.jobs = jobs
        self.next_token = next_token
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.jobs:
            for k in self.jobs:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        result['jobs'] = []
        if self.jobs is not None:
            for k in self.jobs:
                result['jobs'].append(k.to_map() if k else None)
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        self.jobs = []
        if m.get('jobs') is not None:
            for k in m.get('jobs'):
                temp_model = ListPipelineJobHistorysResponseBodyJobs()
                self.jobs.append(temp_model.from_map(k))
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListPipelineJobHistorysResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListPipelineJobHistorysResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListPipelineJobHistorysResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListPipelineJobsRequest(TeaModel):
    def __init__(
        self,
        category: str = None,
    ):
        self.category = category

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category is not None:
            result['category'] = self.category
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('category') is not None:
            self.category = m.get('category')
        return self


class ListPipelineJobsResponseBodyJobs(TeaModel):
    def __init__(
        self,
        identifier: str = None,
        job_name: str = None,
        last_job_id: int = None,
        last_job_params: str = None,
    ):
        self.identifier = identifier
        self.job_name = job_name
        self.last_job_id = last_job_id
        self.last_job_params = last_job_params

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.job_name is not None:
            result['jobName'] = self.job_name
        if self.last_job_id is not None:
            result['lastJobId'] = self.last_job_id
        if self.last_job_params is not None:
            result['lastJobParams'] = self.last_job_params
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('jobName') is not None:
            self.job_name = m.get('jobName')
        if m.get('lastJobId') is not None:
            self.last_job_id = m.get('lastJobId')
        if m.get('lastJobParams') is not None:
            self.last_job_params = m.get('lastJobParams')
        return self


class ListPipelineJobsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        jobs: List[ListPipelineJobsResponseBodyJobs] = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.jobs = jobs
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.jobs:
            for k in self.jobs:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        result['jobs'] = []
        if self.jobs is not None:
            for k in self.jobs:
                result['jobs'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        self.jobs = []
        if m.get('jobs') is not None:
            for k in m.get('jobs'):
                temp_model = ListPipelineJobsResponseBodyJobs()
                self.jobs.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListPipelineJobsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListPipelineJobsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListPipelineJobsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListPipelineRunsRequest(TeaModel):
    def __init__(
        self,
        end_time: int = None,
        max_results: int = None,
        next_token: str = None,
        start_time: int = None,
        status: str = None,
        trigger_mode: int = None,
    ):
        self.end_time = end_time
        self.max_results = max_results
        self.next_token = next_token
        self.start_time = start_time
        self.status = status
        self.trigger_mode = trigger_mode

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.end_time is not None:
            result['endTime'] = self.end_time
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.start_time is not None:
            result['startTime'] = self.start_time
        if self.status is not None:
            result['status'] = self.status
        if self.trigger_mode is not None:
            result['triggerMode'] = self.trigger_mode
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('endTime') is not None:
            self.end_time = m.get('endTime')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('startTime') is not None:
            self.start_time = m.get('startTime')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('triggerMode') is not None:
            self.trigger_mode = m.get('triggerMode')
        return self


class ListPipelineRunsResponseBodyPipelineRuns(TeaModel):
    def __init__(
        self,
        creator_account_id: str = None,
        end_time: int = None,
        pipeline_id: int = None,
        pipeline_run_id: int = None,
        start_time: int = None,
        status: str = None,
        trigger_mode: int = None,
    ):
        self.creator_account_id = creator_account_id
        self.end_time = end_time
        self.pipeline_id = pipeline_id
        self.pipeline_run_id = pipeline_run_id
        self.start_time = start_time
        self.status = status
        self.trigger_mode = trigger_mode

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.end_time is not None:
            result['endTime'] = self.end_time
        if self.pipeline_id is not None:
            result['pipelineId'] = self.pipeline_id
        if self.pipeline_run_id is not None:
            result['pipelineRunId'] = self.pipeline_run_id
        if self.start_time is not None:
            result['startTime'] = self.start_time
        if self.status is not None:
            result['status'] = self.status
        if self.trigger_mode is not None:
            result['triggerMode'] = self.trigger_mode
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('endTime') is not None:
            self.end_time = m.get('endTime')
        if m.get('pipelineId') is not None:
            self.pipeline_id = m.get('pipelineId')
        if m.get('pipelineRunId') is not None:
            self.pipeline_run_id = m.get('pipelineRunId')
        if m.get('startTime') is not None:
            self.start_time = m.get('startTime')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('triggerMode') is not None:
            self.trigger_mode = m.get('triggerMode')
        return self


class ListPipelineRunsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        next_token: str = None,
        pipeline_runs: List[ListPipelineRunsResponseBodyPipelineRuns] = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.next_token = next_token
        self.pipeline_runs = pipeline_runs
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.pipeline_runs:
            for k in self.pipeline_runs:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        result['pipelineRuns'] = []
        if self.pipeline_runs is not None:
            for k in self.pipeline_runs:
                result['pipelineRuns'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        self.pipeline_runs = []
        if m.get('pipelineRuns') is not None:
            for k in m.get('pipelineRuns'):
                temp_model = ListPipelineRunsResponseBodyPipelineRuns()
                self.pipeline_runs.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListPipelineRunsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListPipelineRunsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListPipelineRunsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListPipelinesRequest(TeaModel):
    def __init__(
        self,
        create_end_time: int = None,
        create_start_time: int = None,
        creator_account_ids: str = None,
        execute_account_ids: str = None,
        execute_end_time: int = None,
        execute_start_time: int = None,
        max_results: int = None,
        next_token: str = None,
        pipeline_name: str = None,
        status_list: str = None,
    ):
        self.create_end_time = create_end_time
        self.create_start_time = create_start_time
        self.creator_account_ids = creator_account_ids
        self.execute_account_ids = execute_account_ids
        self.execute_end_time = execute_end_time
        self.execute_start_time = execute_start_time
        self.max_results = max_results
        self.next_token = next_token
        self.pipeline_name = pipeline_name
        self.status_list = status_list

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_end_time is not None:
            result['createEndTime'] = self.create_end_time
        if self.create_start_time is not None:
            result['createStartTime'] = self.create_start_time
        if self.creator_account_ids is not None:
            result['creatorAccountIds'] = self.creator_account_ids
        if self.execute_account_ids is not None:
            result['executeAccountIds'] = self.execute_account_ids
        if self.execute_end_time is not None:
            result['executeEndTime'] = self.execute_end_time
        if self.execute_start_time is not None:
            result['executeStartTime'] = self.execute_start_time
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.pipeline_name is not None:
            result['pipelineName'] = self.pipeline_name
        if self.status_list is not None:
            result['statusList'] = self.status_list
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createEndTime') is not None:
            self.create_end_time = m.get('createEndTime')
        if m.get('createStartTime') is not None:
            self.create_start_time = m.get('createStartTime')
        if m.get('creatorAccountIds') is not None:
            self.creator_account_ids = m.get('creatorAccountIds')
        if m.get('executeAccountIds') is not None:
            self.execute_account_ids = m.get('executeAccountIds')
        if m.get('executeEndTime') is not None:
            self.execute_end_time = m.get('executeEndTime')
        if m.get('executeStartTime') is not None:
            self.execute_start_time = m.get('executeStartTime')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('pipelineName') is not None:
            self.pipeline_name = m.get('pipelineName')
        if m.get('statusList') is not None:
            self.status_list = m.get('statusList')
        return self


class ListPipelinesResponseBodyPipelines(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        creator_account_id: str = None,
        group_id: int = None,
        pipeline_id: int = None,
        pipeline_name: str = None,
    ):
        self.create_time = create_time
        self.creator_account_id = creator_account_id
        self.group_id = group_id
        self.pipeline_id = pipeline_id
        self.pipeline_name = pipeline_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.group_id is not None:
            result['groupId'] = self.group_id
        if self.pipeline_id is not None:
            result['pipelineId'] = self.pipeline_id
        if self.pipeline_name is not None:
            result['pipelineName'] = self.pipeline_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('groupId') is not None:
            self.group_id = m.get('groupId')
        if m.get('pipelineId') is not None:
            self.pipeline_id = m.get('pipelineId')
        if m.get('pipelineName') is not None:
            self.pipeline_name = m.get('pipelineName')
        return self


class ListPipelinesResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        next_token: str = None,
        pipelines: List[ListPipelinesResponseBodyPipelines] = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.next_token = next_token
        self.pipelines = pipelines
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.pipelines:
            for k in self.pipelines:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        result['pipelines'] = []
        if self.pipelines is not None:
            for k in self.pipelines:
                result['pipelines'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        self.pipelines = []
        if m.get('pipelines') is not None:
            for k in m.get('pipelines'):
                temp_model = ListPipelinesResponseBodyPipelines()
                self.pipelines.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListPipelinesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListPipelinesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListPipelinesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListProjectMembersRequest(TeaModel):
    def __init__(
        self,
        target_type: str = None,
    ):
        self.target_type = target_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.target_type is not None:
            result['targetType'] = self.target_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('targetType') is not None:
            self.target_type = m.get('targetType')
        return self


class ListProjectMembersResponseBodyMembersDivision(TeaModel):
    def __init__(
        self,
        identifier: str = None,
    ):
        self.identifier = identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.identifier is not None:
            result['identifier'] = self.identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        return self


class ListProjectMembersResponseBodyMembersOrganizationUserInfo(TeaModel):
    def __init__(
        self,
        organization_identifier: str = None,
    ):
        self.organization_identifier = organization_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.organization_identifier is not None:
            result['organizationIdentifier'] = self.organization_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('organizationIdentifier') is not None:
            self.organization_identifier = m.get('organizationIdentifier')
        return self


class ListProjectMembersResponseBodyMembers(TeaModel):
    def __init__(
        self,
        account: str = None,
        avatar: str = None,
        ding_talk_id: str = None,
        display_name: str = None,
        display_nick_name: str = None,
        display_real_name: str = None,
        division: ListProjectMembersResponseBodyMembersDivision = None,
        email: str = None,
        gender: str = None,
        identifier: str = None,
        mobile: str = None,
        name_en: str = None,
        nick_name: str = None,
        nick_name_pinyin: str = None,
        organization_user_info: ListProjectMembersResponseBodyMembersOrganizationUserInfo = None,
        real_name: str = None,
        real_name_pinyin: str = None,
        stamp: str = None,
        tb_role_id: str = None,
    ):
        self.account = account
        self.avatar = avatar
        self.ding_talk_id = ding_talk_id
        self.display_name = display_name
        self.display_nick_name = display_nick_name
        self.display_real_name = display_real_name
        self.division = division
        self.email = email
        self.gender = gender
        self.identifier = identifier
        self.mobile = mobile
        self.name_en = name_en
        self.nick_name = nick_name
        self.nick_name_pinyin = nick_name_pinyin
        self.organization_user_info = organization_user_info
        self.real_name = real_name
        self.real_name_pinyin = real_name_pinyin
        self.stamp = stamp
        self.tb_role_id = tb_role_id

    def validate(self):
        if self.division:
            self.division.validate()
        if self.organization_user_info:
            self.organization_user_info.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.account is not None:
            result['account'] = self.account
        if self.avatar is not None:
            result['avatar'] = self.avatar
        if self.ding_talk_id is not None:
            result['dingTalkId'] = self.ding_talk_id
        if self.display_name is not None:
            result['displayName'] = self.display_name
        if self.display_nick_name is not None:
            result['displayNickName'] = self.display_nick_name
        if self.display_real_name is not None:
            result['displayRealName'] = self.display_real_name
        if self.division is not None:
            result['division'] = self.division.to_map()
        if self.email is not None:
            result['email'] = self.email
        if self.gender is not None:
            result['gender'] = self.gender
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.mobile is not None:
            result['mobile'] = self.mobile
        if self.name_en is not None:
            result['nameEn'] = self.name_en
        if self.nick_name is not None:
            result['nickName'] = self.nick_name
        if self.nick_name_pinyin is not None:
            result['nickNamePinyin'] = self.nick_name_pinyin
        if self.organization_user_info is not None:
            result['organizationUserInfo'] = self.organization_user_info.to_map()
        if self.real_name is not None:
            result['realName'] = self.real_name
        if self.real_name_pinyin is not None:
            result['realNamePinyin'] = self.real_name_pinyin
        if self.stamp is not None:
            result['stamp'] = self.stamp
        if self.tb_role_id is not None:
            result['tbRoleId'] = self.tb_role_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('account') is not None:
            self.account = m.get('account')
        if m.get('avatar') is not None:
            self.avatar = m.get('avatar')
        if m.get('dingTalkId') is not None:
            self.ding_talk_id = m.get('dingTalkId')
        if m.get('displayName') is not None:
            self.display_name = m.get('displayName')
        if m.get('displayNickName') is not None:
            self.display_nick_name = m.get('displayNickName')
        if m.get('displayRealName') is not None:
            self.display_real_name = m.get('displayRealName')
        if m.get('division') is not None:
            temp_model = ListProjectMembersResponseBodyMembersDivision()
            self.division = temp_model.from_map(m['division'])
        if m.get('email') is not None:
            self.email = m.get('email')
        if m.get('gender') is not None:
            self.gender = m.get('gender')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('mobile') is not None:
            self.mobile = m.get('mobile')
        if m.get('nameEn') is not None:
            self.name_en = m.get('nameEn')
        if m.get('nickName') is not None:
            self.nick_name = m.get('nickName')
        if m.get('nickNamePinyin') is not None:
            self.nick_name_pinyin = m.get('nickNamePinyin')
        if m.get('organizationUserInfo') is not None:
            temp_model = ListProjectMembersResponseBodyMembersOrganizationUserInfo()
            self.organization_user_info = temp_model.from_map(m['organizationUserInfo'])
        if m.get('realName') is not None:
            self.real_name = m.get('realName')
        if m.get('realNamePinyin') is not None:
            self.real_name_pinyin = m.get('realNamePinyin')
        if m.get('stamp') is not None:
            self.stamp = m.get('stamp')
        if m.get('tbRoleId') is not None:
            self.tb_role_id = m.get('tbRoleId')
        return self


class ListProjectMembersResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        members: List[ListProjectMembersResponseBodyMembers] = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.members = members
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.members:
            for k in self.members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        result['members'] = []
        if self.members is not None:
            for k in self.members:
                result['members'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        self.members = []
        if m.get('members') is not None:
            for k in m.get('members'):
                temp_model = ListProjectMembersResponseBodyMembers()
                self.members.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListProjectMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListProjectMembersResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListProjectMembersResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListProjectTemplatesRequest(TeaModel):
    def __init__(
        self,
        category: str = None,
    ):
        self.category = category

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category is not None:
            result['category'] = self.category
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('category') is not None:
            self.category = m.get('category')
        return self


class ListProjectTemplatesResponseBodyTemplates(TeaModel):
    def __init__(
        self,
        copy_from: str = None,
        creator: str = None,
        description: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        icon: str = None,
        identifier: str = None,
        modifier: str = None,
        name: str = None,
        name_en: str = None,
        resource_category: str = None,
        resource_type: str = None,
        space_identifier: str = None,
        space_type: str = None,
        type: int = None,
    ):
        self.copy_from = copy_from
        self.creator = creator
        self.description = description
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.icon = icon
        self.identifier = identifier
        self.modifier = modifier
        self.name = name
        self.name_en = name_en
        self.resource_category = resource_category
        self.resource_type = resource_type
        self.space_identifier = space_identifier
        self.space_type = space_type
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.copy_from is not None:
            result['copyFrom'] = self.copy_from
        if self.creator is not None:
            result['creator'] = self.creator
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.icon is not None:
            result['icon'] = self.icon
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.name_en is not None:
            result['nameEn'] = self.name_en
        if self.resource_category is not None:
            result['resourceCategory'] = self.resource_category
        if self.resource_type is not None:
            result['resourceType'] = self.resource_type
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('copyFrom') is not None:
            self.copy_from = m.get('copyFrom')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('icon') is not None:
            self.icon = m.get('icon')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nameEn') is not None:
            self.name_en = m.get('nameEn')
        if m.get('resourceCategory') is not None:
            self.resource_category = m.get('resourceCategory')
        if m.get('resourceType') is not None:
            self.resource_type = m.get('resourceType')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class ListProjectTemplatesResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        request_id: str = None,
        success: bool = None,
        templates: List[ListProjectTemplatesResponseBodyTemplates] = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.request_id = request_id
        self.success = success
        self.templates = templates

    def validate(self):
        if self.templates:
            for k in self.templates:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        result['templates'] = []
        if self.templates is not None:
            for k in self.templates:
                result['templates'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        self.templates = []
        if m.get('templates') is not None:
            for k in m.get('templates'):
                temp_model = ListProjectTemplatesResponseBodyTemplates()
                self.templates.append(temp_model.from_map(k))
        return self


class ListProjectTemplatesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListProjectTemplatesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListProjectTemplatesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListProjectWorkitemTypesRequest(TeaModel):
    def __init__(
        self,
        category: str = None,
        space_type: str = None,
    ):
        self.category = category
        self.space_type = space_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category is not None:
            result['category'] = self.category
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('category') is not None:
            self.category = m.get('category')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        return self


class ListProjectWorkitemTypesResponseBodyWorkitemTypes(TeaModel):
    def __init__(
        self,
        add_user: str = None,
        category_identifier: str = None,
        creator: str = None,
        default_type: bool = None,
        description: str = None,
        enable: bool = None,
        gmt_add: int = None,
        gmt_create: int = None,
        identifier: str = None,
        name: str = None,
        name_en: str = None,
        system_default: bool = None,
    ):
        self.add_user = add_user
        self.category_identifier = category_identifier
        self.creator = creator
        self.default_type = default_type
        self.description = description
        self.enable = enable
        self.gmt_add = gmt_add
        self.gmt_create = gmt_create
        self.identifier = identifier
        self.name = name
        self.name_en = name_en
        self.system_default = system_default

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.add_user is not None:
            result['addUser'] = self.add_user
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        if self.default_type is not None:
            result['defaultType'] = self.default_type
        if self.description is not None:
            result['description'] = self.description
        if self.enable is not None:
            result['enable'] = self.enable
        if self.gmt_add is not None:
            result['gmtAdd'] = self.gmt_add
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.name is not None:
            result['name'] = self.name
        if self.name_en is not None:
            result['nameEn'] = self.name_en
        if self.system_default is not None:
            result['systemDefault'] = self.system_default
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('addUser') is not None:
            self.add_user = m.get('addUser')
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('defaultType') is not None:
            self.default_type = m.get('defaultType')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('enable') is not None:
            self.enable = m.get('enable')
        if m.get('gmtAdd') is not None:
            self.gmt_add = m.get('gmtAdd')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nameEn') is not None:
            self.name_en = m.get('nameEn')
        if m.get('systemDefault') is not None:
            self.system_default = m.get('systemDefault')
        return self


class ListProjectWorkitemTypesResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        workitem_types: List[ListProjectWorkitemTypesResponseBodyWorkitemTypes] = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.workitem_types = workitem_types

    def validate(self):
        if self.workitem_types:
            for k in self.workitem_types:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        result['workitemTypes'] = []
        if self.workitem_types is not None:
            for k in self.workitem_types:
                result['workitemTypes'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        self.workitem_types = []
        if m.get('workitemTypes') is not None:
            for k in m.get('workitemTypes'):
                temp_model = ListProjectWorkitemTypesResponseBodyWorkitemTypes()
                self.workitem_types.append(temp_model.from_map(k))
        return self


class ListProjectWorkitemTypesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListProjectWorkitemTypesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListProjectWorkitemTypesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListProjectsRequest(TeaModel):
    def __init__(
        self,
        category: str = None,
        conditions: str = None,
        extra_conditions: str = None,
        max_results: int = None,
        next_token: str = None,
        scope: str = None,
    ):
        self.category = category
        self.conditions = conditions
        self.extra_conditions = extra_conditions
        self.max_results = max_results
        self.next_token = next_token
        self.scope = scope

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category is not None:
            result['category'] = self.category
        if self.conditions is not None:
            result['conditions'] = self.conditions
        if self.extra_conditions is not None:
            result['extraConditions'] = self.extra_conditions
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.scope is not None:
            result['scope'] = self.scope
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('category') is not None:
            self.category = m.get('category')
        if m.get('conditions') is not None:
            self.conditions = m.get('conditions')
        if m.get('extraConditions') is not None:
            self.extra_conditions = m.get('extraConditions')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        return self


class ListProjectsResponseBodyProjects(TeaModel):
    def __init__(
        self,
        category_identifier: str = None,
        creator: str = None,
        custom_code: str = None,
        delete_time: int = None,
        description: str = None,
        gmt_create: int = None,
        icon: str = None,
        identifier: str = None,
        logical_status: str = None,
        name: str = None,
        scope: str = None,
        status_stage_identifier: str = None,
        type_identifier: str = None,
    ):
        self.category_identifier = category_identifier
        self.creator = creator
        self.custom_code = custom_code
        self.delete_time = delete_time
        self.description = description
        self.gmt_create = gmt_create
        self.icon = icon
        self.identifier = identifier
        self.logical_status = logical_status
        self.name = name
        self.scope = scope
        self.status_stage_identifier = status_stage_identifier
        self.type_identifier = type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        if self.custom_code is not None:
            result['customCode'] = self.custom_code
        if self.delete_time is not None:
            result['deleteTime'] = self.delete_time
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.icon is not None:
            result['icon'] = self.icon
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.logical_status is not None:
            result['logicalStatus'] = self.logical_status
        if self.name is not None:
            result['name'] = self.name
        if self.scope is not None:
            result['scope'] = self.scope
        if self.status_stage_identifier is not None:
            result['statusStageIdentifier'] = self.status_stage_identifier
        if self.type_identifier is not None:
            result['typeIdentifier'] = self.type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('customCode') is not None:
            self.custom_code = m.get('customCode')
        if m.get('deleteTime') is not None:
            self.delete_time = m.get('deleteTime')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('icon') is not None:
            self.icon = m.get('icon')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('logicalStatus') is not None:
            self.logical_status = m.get('logicalStatus')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('statusStageIdentifier') is not None:
            self.status_stage_identifier = m.get('statusStageIdentifier')
        if m.get('typeIdentifier') is not None:
            self.type_identifier = m.get('typeIdentifier')
        return self


class ListProjectsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        max_results: int = None,
        next_token: str = None,
        projects: List[ListProjectsResponseBodyProjects] = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.max_results = max_results
        self.next_token = next_token
        self.projects = projects
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.projects:
            for k in self.projects:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        result['projects'] = []
        if self.projects is not None:
            for k in self.projects:
                result['projects'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        self.projects = []
        if m.get('projects') is not None:
            for k in m.get('projects'):
                temp_model = ListProjectsResponseBodyProjects()
                self.projects.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListProjectsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListProjectsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListProjectsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListRepositoriesRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        archived: bool = None,
        order_by: str = None,
        organization_id: str = None,
        page: int = None,
        per_page: int = None,
        search: str = None,
        sort: str = None,
    ):
        self.access_token = access_token
        self.archived = archived
        self.order_by = order_by
        self.organization_id = organization_id
        self.page = page
        self.per_page = per_page
        self.search = search
        self.sort = sort

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.archived is not None:
            result['archived'] = self.archived
        if self.order_by is not None:
            result['orderBy'] = self.order_by
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        if self.page is not None:
            result['page'] = self.page
        if self.per_page is not None:
            result['perPage'] = self.per_page
        if self.search is not None:
            result['search'] = self.search
        if self.sort is not None:
            result['sort'] = self.sort
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('archived') is not None:
            self.archived = m.get('archived')
        if m.get('orderBy') is not None:
            self.order_by = m.get('orderBy')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        if m.get('page') is not None:
            self.page = m.get('page')
        if m.get('perPage') is not None:
            self.per_page = m.get('perPage')
        if m.get('search') is not None:
            self.search = m.get('search')
        if m.get('sort') is not None:
            self.sort = m.get('sort')
        return self


class ListRepositoriesResponseBodyResult(TeaModel):
    def __init__(
        self,
        id: int = None,
        access_level: int = None,
        archive: bool = None,
        avatar_url: str = None,
        created_at: str = None,
        description: str = None,
        import_status: str = None,
        last_activity_at: str = None,
        name: str = None,
        name_with_namespace: str = None,
        namespace_id: int = None,
        path: str = None,
        path_with_namespace: str = None,
        star: bool = None,
        star_count: int = None,
        updated_at: str = None,
        visibility_level: str = None,
        web_url: str = None,
    ):
        self.id = id
        self.access_level = access_level
        self.archive = archive
        self.avatar_url = avatar_url
        self.created_at = created_at
        self.description = description
        self.import_status = import_status
        self.last_activity_at = last_activity_at
        self.name = name
        self.name_with_namespace = name_with_namespace
        self.namespace_id = namespace_id
        self.path = path
        self.path_with_namespace = path_with_namespace
        self.star = star
        self.star_count = star_count
        self.updated_at = updated_at
        self.visibility_level = visibility_level
        self.web_url = web_url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['Id'] = self.id
        if self.access_level is not None:
            result['accessLevel'] = self.access_level
        if self.archive is not None:
            result['archive'] = self.archive
        if self.avatar_url is not None:
            result['avatarUrl'] = self.avatar_url
        if self.created_at is not None:
            result['createdAt'] = self.created_at
        if self.description is not None:
            result['description'] = self.description
        if self.import_status is not None:
            result['importStatus'] = self.import_status
        if self.last_activity_at is not None:
            result['lastActivityAt'] = self.last_activity_at
        if self.name is not None:
            result['name'] = self.name
        if self.name_with_namespace is not None:
            result['nameWithNamespace'] = self.name_with_namespace
        if self.namespace_id is not None:
            result['namespaceId'] = self.namespace_id
        if self.path is not None:
            result['path'] = self.path
        if self.path_with_namespace is not None:
            result['pathWithNamespace'] = self.path_with_namespace
        if self.star is not None:
            result['star'] = self.star
        if self.star_count is not None:
            result['starCount'] = self.star_count
        if self.updated_at is not None:
            result['updatedAt'] = self.updated_at
        if self.visibility_level is not None:
            result['visibilityLevel'] = self.visibility_level
        if self.web_url is not None:
            result['webUrl'] = self.web_url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Id') is not None:
            self.id = m.get('Id')
        if m.get('accessLevel') is not None:
            self.access_level = m.get('accessLevel')
        if m.get('archive') is not None:
            self.archive = m.get('archive')
        if m.get('avatarUrl') is not None:
            self.avatar_url = m.get('avatarUrl')
        if m.get('createdAt') is not None:
            self.created_at = m.get('createdAt')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('importStatus') is not None:
            self.import_status = m.get('importStatus')
        if m.get('lastActivityAt') is not None:
            self.last_activity_at = m.get('lastActivityAt')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nameWithNamespace') is not None:
            self.name_with_namespace = m.get('nameWithNamespace')
        if m.get('namespaceId') is not None:
            self.namespace_id = m.get('namespaceId')
        if m.get('path') is not None:
            self.path = m.get('path')
        if m.get('pathWithNamespace') is not None:
            self.path_with_namespace = m.get('pathWithNamespace')
        if m.get('star') is not None:
            self.star = m.get('star')
        if m.get('starCount') is not None:
            self.star_count = m.get('starCount')
        if m.get('updatedAt') is not None:
            self.updated_at = m.get('updatedAt')
        if m.get('visibilityLevel') is not None:
            self.visibility_level = m.get('visibilityLevel')
        if m.get('webUrl') is not None:
            self.web_url = m.get('webUrl')
        return self


class ListRepositoriesResponseBody(TeaModel):
    def __init__(
        self,
        error_code: int = None,
        error_message: str = None,
        request_id: str = None,
        result: List[ListRepositoriesResponseBodyResult] = None,
        success: bool = None,
        total: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success
        self.total = total

    def validate(self):
        if self.result:
            for k in self.result:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        result['result'] = []
        if self.result is not None:
            for k in self.result:
                result['result'].append(k.to_map() if k else None)
        if self.success is not None:
            result['success'] = self.success
        if self.total is not None:
            result['total'] = self.total
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        self.result = []
        if m.get('result') is not None:
            for k in m.get('result'):
                temp_model = ListRepositoriesResponseBodyResult()
                self.result.append(temp_model.from_map(k))
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('total') is not None:
            self.total = m.get('total')
        return self


class ListRepositoriesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListRepositoriesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListRepositoriesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListRepositoryMemberWithInheritedRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        organization_id: str = None,
    ):
        self.access_token = access_token
        self.organization_id = organization_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        return self


class ListRepositoryMemberWithInheritedResponseBodyResultInherited(TeaModel):
    def __init__(
        self,
        id: int = None,
        name: str = None,
        name_with_namespace: str = None,
        path: str = None,
        path_with_namespace: str = None,
        type: str = None,
        visibility_level: str = None,
    ):
        self.id = id
        self.name = name
        self.name_with_namespace = name_with_namespace
        self.path = path
        self.path_with_namespace = path_with_namespace
        self.type = type
        self.visibility_level = visibility_level

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.name_with_namespace is not None:
            result['nameWithNamespace'] = self.name_with_namespace
        if self.path is not None:
            result['path'] = self.path
        if self.path_with_namespace is not None:
            result['pathWithNamespace'] = self.path_with_namespace
        if self.type is not None:
            result['type'] = self.type
        if self.visibility_level is not None:
            result['visibilityLevel'] = self.visibility_level
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('nameWithNamespace') is not None:
            self.name_with_namespace = m.get('nameWithNamespace')
        if m.get('path') is not None:
            self.path = m.get('path')
        if m.get('pathWithNamespace') is not None:
            self.path_with_namespace = m.get('pathWithNamespace')
        if m.get('type') is not None:
            self.type = m.get('type')
        if m.get('visibilityLevel') is not None:
            self.visibility_level = m.get('visibilityLevel')
        return self


class ListRepositoryMemberWithInheritedResponseBodyResult(TeaModel):
    def __init__(
        self,
        access_level: int = None,
        avatar_url: str = None,
        email: str = None,
        extern_user_id: str = None,
        id: int = None,
        inherited: ListRepositoryMemberWithInheritedResponseBodyResultInherited = None,
        name: str = None,
        state: str = None,
        username: str = None,
    ):
        self.access_level = access_level
        self.avatar_url = avatar_url
        self.email = email
        self.extern_user_id = extern_user_id
        self.id = id
        self.inherited = inherited
        self.name = name
        self.state = state
        self.username = username

    def validate(self):
        if self.inherited:
            self.inherited.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_level is not None:
            result['accessLevel'] = self.access_level
        if self.avatar_url is not None:
            result['avatarUrl'] = self.avatar_url
        if self.email is not None:
            result['email'] = self.email
        if self.extern_user_id is not None:
            result['externUserId'] = self.extern_user_id
        if self.id is not None:
            result['id'] = self.id
        if self.inherited is not None:
            result['inherited'] = self.inherited.to_map()
        if self.name is not None:
            result['name'] = self.name
        if self.state is not None:
            result['state'] = self.state
        if self.username is not None:
            result['username'] = self.username
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessLevel') is not None:
            self.access_level = m.get('accessLevel')
        if m.get('avatarUrl') is not None:
            self.avatar_url = m.get('avatarUrl')
        if m.get('email') is not None:
            self.email = m.get('email')
        if m.get('externUserId') is not None:
            self.extern_user_id = m.get('externUserId')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('inherited') is not None:
            temp_model = ListRepositoryMemberWithInheritedResponseBodyResultInherited()
            self.inherited = temp_model.from_map(m['inherited'])
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('state') is not None:
            self.state = m.get('state')
        if m.get('username') is not None:
            self.username = m.get('username')
        return self


class ListRepositoryMemberWithInheritedResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: List[ListRepositoryMemberWithInheritedResponseBodyResult] = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            for k in self.result:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        result['result'] = []
        if self.result is not None:
            for k in self.result:
                result['result'].append(k.to_map() if k else None)
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        self.result = []
        if m.get('result') is not None:
            for k in m.get('result'):
                temp_model = ListRepositoryMemberWithInheritedResponseBodyResult()
                self.result.append(temp_model.from_map(k))
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListRepositoryMemberWithInheritedResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListRepositoryMemberWithInheritedResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListRepositoryMemberWithInheritedResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListRepositoryWebhookRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        organization_id: str = None,
        page: int = None,
        page_size: int = None,
    ):
        self.access_token = access_token
        self.organization_id = organization_id
        self.page = page
        self.page_size = page_size

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        if self.page is not None:
            result['page'] = self.page
        if self.page_size is not None:
            result['pageSize'] = self.page_size
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        if m.get('page') is not None:
            self.page = m.get('page')
        if m.get('pageSize') is not None:
            self.page_size = m.get('pageSize')
        return self


class ListRepositoryWebhookResponseBodyResult(TeaModel):
    def __init__(
        self,
        created_at: str = None,
        description: str = None,
        enable_ssl_verification: bool = None,
        id: int = None,
        last_test_result: str = None,
        merge_requests_events: bool = None,
        note_events: bool = None,
        project_id: int = None,
        push_events: bool = None,
        secret_token: str = None,
        tag_push_events: bool = None,
        url: str = None,
    ):
        self.created_at = created_at
        self.description = description
        self.enable_ssl_verification = enable_ssl_verification
        self.id = id
        self.last_test_result = last_test_result
        self.merge_requests_events = merge_requests_events
        self.note_events = note_events
        self.project_id = project_id
        self.push_events = push_events
        self.secret_token = secret_token
        self.tag_push_events = tag_push_events
        self.url = url

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.created_at is not None:
            result['createdAt'] = self.created_at
        if self.description is not None:
            result['description'] = self.description
        if self.enable_ssl_verification is not None:
            result['enableSslVerification'] = self.enable_ssl_verification
        if self.id is not None:
            result['id'] = self.id
        if self.last_test_result is not None:
            result['lastTestResult'] = self.last_test_result
        if self.merge_requests_events is not None:
            result['mergeRequestsEvents'] = self.merge_requests_events
        if self.note_events is not None:
            result['noteEvents'] = self.note_events
        if self.project_id is not None:
            result['projectId'] = self.project_id
        if self.push_events is not None:
            result['pushEvents'] = self.push_events
        if self.secret_token is not None:
            result['secretToken'] = self.secret_token
        if self.tag_push_events is not None:
            result['tagPushEvents'] = self.tag_push_events
        if self.url is not None:
            result['url'] = self.url
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createdAt') is not None:
            self.created_at = m.get('createdAt')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('enableSslVerification') is not None:
            self.enable_ssl_verification = m.get('enableSslVerification')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('lastTestResult') is not None:
            self.last_test_result = m.get('lastTestResult')
        if m.get('mergeRequestsEvents') is not None:
            self.merge_requests_events = m.get('mergeRequestsEvents')
        if m.get('noteEvents') is not None:
            self.note_events = m.get('noteEvents')
        if m.get('projectId') is not None:
            self.project_id = m.get('projectId')
        if m.get('pushEvents') is not None:
            self.push_events = m.get('pushEvents')
        if m.get('secretToken') is not None:
            self.secret_token = m.get('secretToken')
        if m.get('tagPushEvents') is not None:
            self.tag_push_events = m.get('tagPushEvents')
        if m.get('url') is not None:
            self.url = m.get('url')
        return self


class ListRepositoryWebhookResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: List[ListRepositoryWebhookResponseBodyResult] = None,
        success: bool = None,
        total: int = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success
        self.total = total

    def validate(self):
        if self.result:
            for k in self.result:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        result['result'] = []
        if self.result is not None:
            for k in self.result:
                result['result'].append(k.to_map() if k else None)
        if self.success is not None:
            result['success'] = self.success
        if self.total is not None:
            result['total'] = self.total
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        self.result = []
        if m.get('result') is not None:
            for k in m.get('result'):
                temp_model = ListRepositoryWebhookResponseBodyResult()
                self.result.append(temp_model.from_map(k))
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('total') is not None:
            self.total = m.get('total')
        return self


class ListRepositoryWebhookResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListRepositoryWebhookResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListRepositoryWebhookResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListResourceMembersResponseBodyResourceMembers(TeaModel):
    def __init__(
        self,
        account_id: str = None,
        role_name: str = None,
        username: str = None,
    ):
        self.account_id = account_id
        self.role_name = role_name
        self.username = username

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.account_id is not None:
            result['accountId'] = self.account_id
        if self.role_name is not None:
            result['roleName'] = self.role_name
        if self.username is not None:
            result['username'] = self.username
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accountId') is not None:
            self.account_id = m.get('accountId')
        if m.get('roleName') is not None:
            self.role_name = m.get('roleName')
        if m.get('username') is not None:
            self.username = m.get('username')
        return self


class ListResourceMembersResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        resource_members: List[ListResourceMembersResponseBodyResourceMembers] = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.resource_members = resource_members
        self.success = success

    def validate(self):
        if self.resource_members:
            for k in self.resource_members:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        result['resourceMembers'] = []
        if self.resource_members is not None:
            for k in self.resource_members:
                result['resourceMembers'].append(k.to_map() if k else None)
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        self.resource_members = []
        if m.get('resourceMembers') is not None:
            for k in m.get('resourceMembers'):
                temp_model = ListResourceMembersResponseBodyResourceMembers()
                self.resource_members.append(temp_model.from_map(k))
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListResourceMembersResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListResourceMembersResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListResourceMembersResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListServiceConnectionsRequest(TeaModel):
    def __init__(
        self,
        serice_connection_type: str = None,
    ):
        self.serice_connection_type = serice_connection_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.serice_connection_type is not None:
            result['sericeConnectionType'] = self.serice_connection_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('sericeConnectionType') is not None:
            self.serice_connection_type = m.get('sericeConnectionType')
        return self


class ListServiceConnectionsResponseBodyServiceConnections(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        id: int = None,
        name: str = None,
        owner_account_id: int = None,
        type: str = None,
    ):
        self.create_time = create_time
        self.id = id
        self.name = name
        self.owner_account_id = owner_account_id
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.owner_account_id is not None:
            result['ownerAccountId'] = self.owner_account_id
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('ownerAccountId') is not None:
            self.owner_account_id = m.get('ownerAccountId')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class ListServiceConnectionsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        service_connections: List[ListServiceConnectionsResponseBodyServiceConnections] = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.service_connections = service_connections
        self.success = success

    def validate(self):
        if self.service_connections:
            for k in self.service_connections:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        result['serviceConnections'] = []
        if self.service_connections is not None:
            for k in self.service_connections:
                result['serviceConnections'].append(k.to_map() if k else None)
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        self.service_connections = []
        if m.get('serviceConnections') is not None:
            for k in m.get('serviceConnections'):
                temp_model = ListServiceConnectionsResponseBodyServiceConnections()
                self.service_connections.append(temp_model.from_map(k))
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListServiceConnectionsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListServiceConnectionsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListServiceConnectionsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListSprintsRequest(TeaModel):
    def __init__(
        self,
        max_results: int = None,
        next_token: str = None,
        space_identifier: str = None,
        space_type: str = None,
    ):
        self.max_results = max_results
        self.next_token = next_token
        self.space_identifier = space_identifier
        self.space_type = space_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        return self


class ListSprintsResponseBodySprints(TeaModel):
    def __init__(
        self,
        creator: str = None,
        description: str = None,
        end_date: int = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        modifier: str = None,
        name: str = None,
        scope: str = None,
        space_identifier: str = None,
        start_date: int = None,
        status: str = None,
    ):
        self.creator = creator
        self.description = description
        self.end_date = end_date
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.modifier = modifier
        self.name = name
        self.scope = scope
        self.space_identifier = space_identifier
        self.start_date = start_date
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator is not None:
            result['creator'] = self.creator
        if self.description is not None:
            result['description'] = self.description
        if self.end_date is not None:
            result['endDate'] = self.end_date
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.scope is not None:
            result['scope'] = self.scope
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.start_date is not None:
            result['startDate'] = self.start_date
        if self.status is not None:
            result['status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('endDate') is not None:
            self.end_date = m.get('endDate')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('scope') is not None:
            self.scope = m.get('scope')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('startDate') is not None:
            self.start_date = m.get('startDate')
        if m.get('status') is not None:
            self.status = m.get('status')
        return self


class ListSprintsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        sprints: List[ListSprintsResponseBodySprints] = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.sprints = sprints
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.sprints:
            for k in self.sprints:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.request_id is not None:
            result['requestId'] = self.request_id
        result['sprints'] = []
        if self.sprints is not None:
            for k in self.sprints:
                result['sprints'].append(k.to_map() if k else None)
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        self.sprints = []
        if m.get('sprints') is not None:
            for k in m.get('sprints'):
                temp_model = ListSprintsResponseBodySprints()
                self.sprints.append(temp_model.from_map(k))
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        return self


class ListSprintsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListSprintsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListSprintsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListVariableGroupsRequest(TeaModel):
    def __init__(
        self,
        max_results: int = None,
        next_token: str = None,
        page_order: str = None,
        page_sort: str = None,
    ):
        self.max_results = max_results
        self.next_token = next_token
        self.page_order = page_order
        self.page_sort = page_sort

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.page_order is not None:
            result['pageOrder'] = self.page_order
        if self.page_sort is not None:
            result['pageSort'] = self.page_sort
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('pageOrder') is not None:
            self.page_order = m.get('pageOrder')
        if m.get('pageSort') is not None:
            self.page_sort = m.get('pageSort')
        return self


class ListVariableGroupsResponseBodyVariableGroupsRelatedPipelines(TeaModel):
    def __init__(
        self,
        id: int = None,
        name: str = None,
    ):
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class ListVariableGroupsResponseBodyVariableGroupsVariables(TeaModel):
    def __init__(
        self,
        is_encrypted: bool = None,
        name: str = None,
        value: str = None,
    ):
        self.is_encrypted = is_encrypted
        self.name = name
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.is_encrypted is not None:
            result['isEncrypted'] = self.is_encrypted
        if self.name is not None:
            result['name'] = self.name
        if self.value is not None:
            result['value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('isEncrypted') is not None:
            self.is_encrypted = m.get('isEncrypted')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('value') is not None:
            self.value = m.get('value')
        return self


class ListVariableGroupsResponseBodyVariableGroups(TeaModel):
    def __init__(
        self,
        create_time: int = None,
        creator_account_id: str = None,
        description: str = None,
        id: int = None,
        modifier_account_id: str = None,
        name: str = None,
        related_pipelines: List[ListVariableGroupsResponseBodyVariableGroupsRelatedPipelines] = None,
        update_time: int = None,
        variables: List[ListVariableGroupsResponseBodyVariableGroupsVariables] = None,
    ):
        self.create_time = create_time
        self.creator_account_id = creator_account_id
        self.description = description
        self.id = id
        self.modifier_account_id = modifier_account_id
        self.name = name
        self.related_pipelines = related_pipelines
        self.update_time = update_time
        self.variables = variables

    def validate(self):
        if self.related_pipelines:
            for k in self.related_pipelines:
                if k:
                    k.validate()
        if self.variables:
            for k in self.variables:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.creator_account_id is not None:
            result['creatorAccountId'] = self.creator_account_id
        if self.description is not None:
            result['description'] = self.description
        if self.id is not None:
            result['id'] = self.id
        if self.modifier_account_id is not None:
            result['modifierAccountId'] = self.modifier_account_id
        if self.name is not None:
            result['name'] = self.name
        result['relatedPipelines'] = []
        if self.related_pipelines is not None:
            for k in self.related_pipelines:
                result['relatedPipelines'].append(k.to_map() if k else None)
        if self.update_time is not None:
            result['updateTime'] = self.update_time
        result['variables'] = []
        if self.variables is not None:
            for k in self.variables:
                result['variables'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('creatorAccountId') is not None:
            self.creator_account_id = m.get('creatorAccountId')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('modifierAccountId') is not None:
            self.modifier_account_id = m.get('modifierAccountId')
        if m.get('name') is not None:
            self.name = m.get('name')
        self.related_pipelines = []
        if m.get('relatedPipelines') is not None:
            for k in m.get('relatedPipelines'):
                temp_model = ListVariableGroupsResponseBodyVariableGroupsRelatedPipelines()
                self.related_pipelines.append(temp_model.from_map(k))
        if m.get('updateTime') is not None:
            self.update_time = m.get('updateTime')
        self.variables = []
        if m.get('variables') is not None:
            for k in m.get('variables'):
                temp_model = ListVariableGroupsResponseBodyVariableGroupsVariables()
                self.variables.append(temp_model.from_map(k))
        return self


class ListVariableGroupsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        next_token: str = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
        variable_groups: List[ListVariableGroupsResponseBodyVariableGroups] = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.next_token = next_token
        self.request_id = request_id
        self.success = success
        self.total_count = total_count
        self.variable_groups = variable_groups

    def validate(self):
        if self.variable_groups:
            for k in self.variable_groups:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        result['variableGroups'] = []
        if self.variable_groups is not None:
            for k in self.variable_groups:
                result['variableGroups'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        self.variable_groups = []
        if m.get('variableGroups') is not None:
            for k in m.get('variableGroups'):
                temp_model = ListVariableGroupsResponseBodyVariableGroups()
                self.variable_groups.append(temp_model.from_map(k))
        return self


class ListVariableGroupsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListVariableGroupsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListVariableGroupsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListWorkItemAllFieldsRequest(TeaModel):
    def __init__(
        self,
        space_identifier: str = None,
        space_type: str = None,
        workitem_type_identifier: str = None,
    ):
        self.space_identifier = space_identifier
        self.space_type = space_type
        self.workitem_type_identifier = workitem_type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.workitem_type_identifier is not None:
            result['workitemTypeIdentifier'] = self.workitem_type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('workitemTypeIdentifier') is not None:
            self.workitem_type_identifier = m.get('workitemTypeIdentifier')
        return self


class ListWorkItemAllFieldsResponseBodyFieldsOptions(TeaModel):
    def __init__(
        self,
        display_value: str = None,
        field_identifier: str = None,
        identifier: str = None,
        level: int = None,
        position: int = None,
        value: str = None,
        value_en: str = None,
    ):
        self.display_value = display_value
        self.field_identifier = field_identifier
        self.identifier = identifier
        self.level = level
        self.position = position
        self.value = value
        self.value_en = value_en

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.display_value is not None:
            result['displayValue'] = self.display_value
        if self.field_identifier is not None:
            result['fieldIdentifier'] = self.field_identifier
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.level is not None:
            result['level'] = self.level
        if self.position is not None:
            result['position'] = self.position
        if self.value is not None:
            result['value'] = self.value
        if self.value_en is not None:
            result['valueEn'] = self.value_en
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('displayValue') is not None:
            self.display_value = m.get('displayValue')
        if m.get('fieldIdentifier') is not None:
            self.field_identifier = m.get('fieldIdentifier')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('level') is not None:
            self.level = m.get('level')
        if m.get('position') is not None:
            self.position = m.get('position')
        if m.get('value') is not None:
            self.value = m.get('value')
        if m.get('valueEn') is not None:
            self.value_en = m.get('valueEn')
        return self


class ListWorkItemAllFieldsResponseBodyFields(TeaModel):
    def __init__(
        self,
        class_name: str = None,
        creator: str = None,
        default_value: str = None,
        description: str = None,
        format: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        is_required: bool = None,
        is_show_when_create: bool = None,
        is_system_required: bool = None,
        link_with_service: str = None,
        modifier: str = None,
        name: str = None,
        options: List[ListWorkItemAllFieldsResponseBodyFieldsOptions] = None,
        resource_type: str = None,
        type: str = None,
    ):
        self.class_name = class_name
        self.creator = creator
        self.default_value = default_value
        self.description = description
        self.format = format
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.is_required = is_required
        self.is_show_when_create = is_show_when_create
        self.is_system_required = is_system_required
        self.link_with_service = link_with_service
        self.modifier = modifier
        self.name = name
        self.options = options
        self.resource_type = resource_type
        self.type = type

    def validate(self):
        if self.options:
            for k in self.options:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.class_name is not None:
            result['className'] = self.class_name
        if self.creator is not None:
            result['creator'] = self.creator
        if self.default_value is not None:
            result['defaultValue'] = self.default_value
        if self.description is not None:
            result['description'] = self.description
        if self.format is not None:
            result['format'] = self.format
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.is_required is not None:
            result['isRequired'] = self.is_required
        if self.is_show_when_create is not None:
            result['isShowWhenCreate'] = self.is_show_when_create
        if self.is_system_required is not None:
            result['isSystemRequired'] = self.is_system_required
        if self.link_with_service is not None:
            result['linkWithService'] = self.link_with_service
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        result['options'] = []
        if self.options is not None:
            for k in self.options:
                result['options'].append(k.to_map() if k else None)
        if self.resource_type is not None:
            result['resourceType'] = self.resource_type
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('className') is not None:
            self.class_name = m.get('className')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('defaultValue') is not None:
            self.default_value = m.get('defaultValue')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('format') is not None:
            self.format = m.get('format')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('isRequired') is not None:
            self.is_required = m.get('isRequired')
        if m.get('isShowWhenCreate') is not None:
            self.is_show_when_create = m.get('isShowWhenCreate')
        if m.get('isSystemRequired') is not None:
            self.is_system_required = m.get('isSystemRequired')
        if m.get('linkWithService') is not None:
            self.link_with_service = m.get('linkWithService')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        self.options = []
        if m.get('options') is not None:
            for k in m.get('options'):
                temp_model = ListWorkItemAllFieldsResponseBodyFieldsOptions()
                self.options.append(temp_model.from_map(k))
        if m.get('resourceType') is not None:
            self.resource_type = m.get('resourceType')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class ListWorkItemAllFieldsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        fields: List[ListWorkItemAllFieldsResponseBodyFields] = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.fields = fields
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.fields:
            for k in self.fields:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        result['fields'] = []
        if self.fields is not None:
            for k in self.fields:
                result['fields'].append(k.to_map() if k else None)
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        self.fields = []
        if m.get('fields') is not None:
            for k in m.get('fields'):
                temp_model = ListWorkItemAllFieldsResponseBodyFields()
                self.fields.append(temp_model.from_map(k))
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListWorkItemAllFieldsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListWorkItemAllFieldsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListWorkItemAllFieldsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListWorkItemWorkFlowStatusRequest(TeaModel):
    def __init__(
        self,
        space_identifier: str = None,
        space_type: str = None,
        workitem_category_identifier: str = None,
        workitem_type_identifier: str = None,
    ):
        self.space_identifier = space_identifier
        self.space_type = space_type
        self.workitem_category_identifier = workitem_category_identifier
        self.workitem_type_identifier = workitem_type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.workitem_category_identifier is not None:
            result['workitemCategoryIdentifier'] = self.workitem_category_identifier
        if self.workitem_type_identifier is not None:
            result['workitemTypeIdentifier'] = self.workitem_type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('workitemCategoryIdentifier') is not None:
            self.workitem_category_identifier = m.get('workitemCategoryIdentifier')
        if m.get('workitemTypeIdentifier') is not None:
            self.workitem_type_identifier = m.get('workitemTypeIdentifier')
        return self


class ListWorkItemWorkFlowStatusResponseBodyStatuses(TeaModel):
    def __init__(
        self,
        creator: str = None,
        description: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        modifier: str = None,
        name: str = None,
        resource_type: str = None,
        source: str = None,
        workflow_stage_identifier: str = None,
        workflow_stage_name: str = None,
    ):
        self.creator = creator
        self.description = description
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.modifier = modifier
        self.name = name
        self.resource_type = resource_type
        self.source = source
        self.workflow_stage_identifier = workflow_stage_identifier
        self.workflow_stage_name = workflow_stage_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.creator is not None:
            result['creator'] = self.creator
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.name is not None:
            result['name'] = self.name
        if self.resource_type is not None:
            result['resourceType'] = self.resource_type
        if self.source is not None:
            result['source'] = self.source
        if self.workflow_stage_identifier is not None:
            result['workflowStageIdentifier'] = self.workflow_stage_identifier
        if self.workflow_stage_name is not None:
            result['workflowStageName'] = self.workflow_stage_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('resourceType') is not None:
            self.resource_type = m.get('resourceType')
        if m.get('source') is not None:
            self.source = m.get('source')
        if m.get('workflowStageIdentifier') is not None:
            self.workflow_stage_identifier = m.get('workflowStageIdentifier')
        if m.get('workflowStageName') is not None:
            self.workflow_stage_name = m.get('workflowStageName')
        return self


class ListWorkItemWorkFlowStatusResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        statuses: List[ListWorkItemWorkFlowStatusResponseBodyStatuses] = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.statuses = statuses
        self.success = success

    def validate(self):
        if self.statuses:
            for k in self.statuses:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        result['statuses'] = []
        if self.statuses is not None:
            for k in self.statuses:
                result['statuses'].append(k.to_map() if k else None)
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        self.statuses = []
        if m.get('statuses') is not None:
            for k in m.get('statuses'):
                temp_model = ListWorkItemWorkFlowStatusResponseBodyStatuses()
                self.statuses.append(temp_model.from_map(k))
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ListWorkItemWorkFlowStatusResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListWorkItemWorkFlowStatusResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListWorkItemWorkFlowStatusResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListWorkitemTimeResponseBodyWorkitemTime(TeaModel):
    def __init__(
        self,
        actual_time: int = None,
        description: str = None,
        gmt_create: int = None,
        gmt_end: int = None,
        gmt_modified: int = None,
        gmt_start: int = None,
        identifier: str = None,
        record_user: str = None,
        type: str = None,
        workitem_identifier: str = None,
    ):
        self.actual_time = actual_time
        self.description = description
        self.gmt_create = gmt_create
        self.gmt_end = gmt_end
        self.gmt_modified = gmt_modified
        self.gmt_start = gmt_start
        self.identifier = identifier
        self.record_user = record_user
        self.type = type
        self.workitem_identifier = workitem_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.actual_time is not None:
            result['actualTime'] = self.actual_time
        if self.description is not None:
            result['description'] = self.description
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_end is not None:
            result['gmtEnd'] = self.gmt_end
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.gmt_start is not None:
            result['gmtStart'] = self.gmt_start
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.record_user is not None:
            result['recordUser'] = self.record_user
        if self.type is not None:
            result['type'] = self.type
        if self.workitem_identifier is not None:
            result['workitemIdentifier'] = self.workitem_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('actualTime') is not None:
            self.actual_time = m.get('actualTime')
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtEnd') is not None:
            self.gmt_end = m.get('gmtEnd')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('gmtStart') is not None:
            self.gmt_start = m.get('gmtStart')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('recordUser') is not None:
            self.record_user = m.get('recordUser')
        if m.get('type') is not None:
            self.type = m.get('type')
        if m.get('workitemIdentifier') is not None:
            self.workitem_identifier = m.get('workitemIdentifier')
        return self


class ListWorkitemTimeResponseBody(TeaModel):
    def __init__(
        self,
        code: int = None,
        error_code: str = None,
        error_msg: str = None,
        request_id: str = None,
        success: bool = None,
        workitem_time: List[ListWorkitemTimeResponseBodyWorkitemTime] = None,
    ):
        self.code = code
        self.error_code = error_code
        self.error_msg = error_msg
        self.request_id = request_id
        self.success = success
        self.workitem_time = workitem_time

    def validate(self):
        if self.workitem_time:
            for k in self.workitem_time:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        result['workitemTime'] = []
        if self.workitem_time is not None:
            for k in self.workitem_time:
                result['workitemTime'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        self.workitem_time = []
        if m.get('workitemTime') is not None:
            for k in m.get('workitemTime'):
                temp_model = ListWorkitemTimeResponseBodyWorkitemTime()
                self.workitem_time.append(temp_model.from_map(k))
        return self


class ListWorkitemTimeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListWorkitemTimeResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListWorkitemTimeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListWorkitemsRequest(TeaModel):
    def __init__(
        self,
        category: str = None,
        conditions: str = None,
        extra_conditions: str = None,
        group_condition: str = None,
        max_results: str = None,
        next_token: str = None,
        order_by: str = None,
        search_type: str = None,
        space_identifier: str = None,
        space_type: str = None,
    ):
        self.category = category
        self.conditions = conditions
        self.extra_conditions = extra_conditions
        self.group_condition = group_condition
        self.max_results = max_results
        self.next_token = next_token
        self.order_by = order_by
        self.search_type = search_type
        self.space_identifier = space_identifier
        self.space_type = space_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.category is not None:
            result['category'] = self.category
        if self.conditions is not None:
            result['conditions'] = self.conditions
        if self.extra_conditions is not None:
            result['extraConditions'] = self.extra_conditions
        if self.group_condition is not None:
            result['groupCondition'] = self.group_condition
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.order_by is not None:
            result['orderBy'] = self.order_by
        if self.search_type is not None:
            result['searchType'] = self.search_type
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('category') is not None:
            self.category = m.get('category')
        if m.get('conditions') is not None:
            self.conditions = m.get('conditions')
        if m.get('extraConditions') is not None:
            self.extra_conditions = m.get('extraConditions')
        if m.get('groupCondition') is not None:
            self.group_condition = m.get('groupCondition')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('orderBy') is not None:
            self.order_by = m.get('orderBy')
        if m.get('searchType') is not None:
            self.search_type = m.get('searchType')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        return self


class ListWorkitemsResponseBodyWorkitems(TeaModel):
    def __init__(
        self,
        assigned_to: str = None,
        category_identifier: str = None,
        creator: str = None,
        document: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        logical_status: str = None,
        modifier: str = None,
        parent_identifier: str = None,
        serial_number: str = None,
        space_identifier: str = None,
        space_name: str = None,
        space_type: str = None,
        sprint_identifier: str = None,
        status: str = None,
        status_identifier: str = None,
        status_stage_identifier: str = None,
        subject: str = None,
        update_status_at: int = None,
        workitem_type_identifier: str = None,
    ):
        self.assigned_to = assigned_to
        self.category_identifier = category_identifier
        self.creator = creator
        self.document = document
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.logical_status = logical_status
        self.modifier = modifier
        self.parent_identifier = parent_identifier
        self.serial_number = serial_number
        self.space_identifier = space_identifier
        self.space_name = space_name
        self.space_type = space_type
        self.sprint_identifier = sprint_identifier
        self.status = status
        self.status_identifier = status_identifier
        self.status_stage_identifier = status_stage_identifier
        self.subject = subject
        self.update_status_at = update_status_at
        self.workitem_type_identifier = workitem_type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.assigned_to is not None:
            result['assignedTo'] = self.assigned_to
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        if self.document is not None:
            result['document'] = self.document
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.logical_status is not None:
            result['logicalStatus'] = self.logical_status
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.parent_identifier is not None:
            result['parentIdentifier'] = self.parent_identifier
        if self.serial_number is not None:
            result['serialNumber'] = self.serial_number
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_name is not None:
            result['spaceName'] = self.space_name
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.sprint_identifier is not None:
            result['sprintIdentifier'] = self.sprint_identifier
        if self.status is not None:
            result['status'] = self.status
        if self.status_identifier is not None:
            result['statusIdentifier'] = self.status_identifier
        if self.status_stage_identifier is not None:
            result['statusStageIdentifier'] = self.status_stage_identifier
        if self.subject is not None:
            result['subject'] = self.subject
        if self.update_status_at is not None:
            result['updateStatusAt'] = self.update_status_at
        if self.workitem_type_identifier is not None:
            result['workitemTypeIdentifier'] = self.workitem_type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('assignedTo') is not None:
            self.assigned_to = m.get('assignedTo')
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('document') is not None:
            self.document = m.get('document')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('logicalStatus') is not None:
            self.logical_status = m.get('logicalStatus')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('parentIdentifier') is not None:
            self.parent_identifier = m.get('parentIdentifier')
        if m.get('serialNumber') is not None:
            self.serial_number = m.get('serialNumber')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceName') is not None:
            self.space_name = m.get('spaceName')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('sprintIdentifier') is not None:
            self.sprint_identifier = m.get('sprintIdentifier')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('statusIdentifier') is not None:
            self.status_identifier = m.get('statusIdentifier')
        if m.get('statusStageIdentifier') is not None:
            self.status_stage_identifier = m.get('statusStageIdentifier')
        if m.get('subject') is not None:
            self.subject = m.get('subject')
        if m.get('updateStatusAt') is not None:
            self.update_status_at = m.get('updateStatusAt')
        if m.get('workitemTypeIdentifier') is not None:
            self.workitem_type_identifier = m.get('workitemTypeIdentifier')
        return self


class ListWorkitemsResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
        workitems: List[ListWorkitemsResponseBodyWorkitems] = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.success = success
        self.total_count = total_count
        self.workitems = workitems

    def validate(self):
        if self.workitems:
            for k in self.workitems:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        result['workitems'] = []
        if self.workitems is not None:
            for k in self.workitems:
                result['workitems'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        self.workitems = []
        if m.get('workitems') is not None:
            for k in m.get('workitems'):
                temp_model = ListWorkitemsResponseBodyWorkitems()
                self.workitems.append(temp_model.from_map(k))
        return self


class ListWorkitemsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListWorkitemsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListWorkitemsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListWorkspacesRequest(TeaModel):
    def __init__(
        self,
        max_results: int = None,
        next_token: str = None,
        status_list: List[str] = None,
        workspace_template_list: List[str] = None,
    ):
        self.max_results = max_results
        self.next_token = next_token
        self.status_list = status_list
        self.workspace_template_list = workspace_template_list

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.status_list is not None:
            result['statusList'] = self.status_list
        if self.workspace_template_list is not None:
            result['workspaceTemplateList'] = self.workspace_template_list
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('statusList') is not None:
            self.status_list = m.get('statusList')
        if m.get('workspaceTemplateList') is not None:
            self.workspace_template_list = m.get('workspaceTemplateList')
        return self


class ListWorkspacesShrinkRequest(TeaModel):
    def __init__(
        self,
        max_results: int = None,
        next_token: str = None,
        status_list_shrink: str = None,
        workspace_template_list_shrink: str = None,
    ):
        self.max_results = max_results
        self.next_token = next_token
        self.status_list_shrink = status_list_shrink
        self.workspace_template_list_shrink = workspace_template_list_shrink

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.status_list_shrink is not None:
            result['statusList'] = self.status_list_shrink
        if self.workspace_template_list_shrink is not None:
            result['workspaceTemplateList'] = self.workspace_template_list_shrink
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('statusList') is not None:
            self.status_list_shrink = m.get('statusList')
        if m.get('workspaceTemplateList') is not None:
            self.workspace_template_list_shrink = m.get('workspaceTemplateList')
        return self


class ListWorkspacesResponseBodyWorkspaces(TeaModel):
    def __init__(
        self,
        code_url: str = None,
        code_version: str = None,
        create_time: str = None,
        id: str = None,
        name: str = None,
        spec: str = None,
        status: str = None,
        template: str = None,
        user_id: str = None,
    ):
        self.code_url = code_url
        self.code_version = code_version
        self.create_time = create_time
        self.id = id
        self.name = name
        self.spec = spec
        self.status = status
        self.template = template
        self.user_id = user_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code_url is not None:
            result['codeUrl'] = self.code_url
        if self.code_version is not None:
            result['codeVersion'] = self.code_version
        if self.create_time is not None:
            result['createTime'] = self.create_time
        if self.id is not None:
            result['id'] = self.id
        if self.name is not None:
            result['name'] = self.name
        if self.spec is not None:
            result['spec'] = self.spec
        if self.status is not None:
            result['status'] = self.status
        if self.template is not None:
            result['template'] = self.template
        if self.user_id is not None:
            result['userId'] = self.user_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('codeUrl') is not None:
            self.code_url = m.get('codeUrl')
        if m.get('codeVersion') is not None:
            self.code_version = m.get('codeVersion')
        if m.get('createTime') is not None:
            self.create_time = m.get('createTime')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('spec') is not None:
            self.spec = m.get('spec')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('template') is not None:
            self.template = m.get('template')
        if m.get('userId') is not None:
            self.user_id = m.get('userId')
        return self


class ListWorkspacesResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
        workspaces: List[ListWorkspacesResponseBodyWorkspaces] = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.success = success
        self.total_count = total_count
        self.workspaces = workspaces

    def validate(self):
        if self.workspaces:
            for k in self.workspaces:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.max_results is not None:
            result['maxResults'] = self.max_results
        if self.next_token is not None:
            result['nextToken'] = self.next_token
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        result['workspaces'] = []
        if self.workspaces is not None:
            for k in self.workspaces:
                result['workspaces'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('maxResults') is not None:
            self.max_results = m.get('maxResults')
        if m.get('nextToken') is not None:
            self.next_token = m.get('nextToken')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('totalCount') is not None:
            self.total_count = m.get('totalCount')
        self.workspaces = []
        if m.get('workspaces') is not None:
            for k in m.get('workspaces'):
                temp_model = ListWorkspacesResponseBodyWorkspaces()
                self.workspaces.append(temp_model.from_map(k))
        return self


class ListWorkspacesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListWorkspacesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListWorkspacesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class LogPipelineJobRunResponseBodyLog(TeaModel):
    def __init__(
        self,
        content: str = None,
        more: bool = None,
    ):
        self.content = content
        self.more = more

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.content is not None:
            result['content'] = self.content
        if self.more is not None:
            result['more'] = self.more
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('content') is not None:
            self.content = m.get('content')
        if m.get('more') is not None:
            self.more = m.get('more')
        return self


class LogPipelineJobRunResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        log: LogPipelineJobRunResponseBodyLog = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.log = log
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.log:
            self.log.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.log is not None:
            result['log'] = self.log.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('log') is not None:
            temp_model = LogPipelineJobRunResponseBodyLog()
            self.log = temp_model.from_map(m['log'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class LogPipelineJobRunResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: LogPipelineJobRunResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = LogPipelineJobRunResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class LogVMDeployMachineResponseBodyDeployMachineLog(TeaModel):
    def __init__(
        self,
        aliyun_region: str = None,
        deploy_begin_time: int = None,
        deploy_end_time: int = None,
        deploy_log: str = None,
        deploy_log_path: str = None,
    ):
        self.aliyun_region = aliyun_region
        self.deploy_begin_time = deploy_begin_time
        self.deploy_end_time = deploy_end_time
        self.deploy_log = deploy_log
        self.deploy_log_path = deploy_log_path

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.aliyun_region is not None:
            result['aliyunRegion'] = self.aliyun_region
        if self.deploy_begin_time is not None:
            result['deployBeginTime'] = self.deploy_begin_time
        if self.deploy_end_time is not None:
            result['deployEndTime'] = self.deploy_end_time
        if self.deploy_log is not None:
            result['deployLog'] = self.deploy_log
        if self.deploy_log_path is not None:
            result['deployLogPath'] = self.deploy_log_path
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('aliyunRegion') is not None:
            self.aliyun_region = m.get('aliyunRegion')
        if m.get('deployBeginTime') is not None:
            self.deploy_begin_time = m.get('deployBeginTime')
        if m.get('deployEndTime') is not None:
            self.deploy_end_time = m.get('deployEndTime')
        if m.get('deployLog') is not None:
            self.deploy_log = m.get('deployLog')
        if m.get('deployLogPath') is not None:
            self.deploy_log_path = m.get('deployLogPath')
        return self


class LogVMDeployMachineResponseBody(TeaModel):
    def __init__(
        self,
        deploy_machine_log: LogVMDeployMachineResponseBodyDeployMachineLog = None,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.deploy_machine_log = deploy_machine_log
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.deploy_machine_log:
            self.deploy_machine_log.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.deploy_machine_log is not None:
            result['deployMachineLog'] = self.deploy_machine_log.to_map()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('deployMachineLog') is not None:
            temp_model = LogVMDeployMachineResponseBodyDeployMachineLog()
            self.deploy_machine_log = temp_model.from_map(m['deployMachineLog'])
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class LogVMDeployMachineResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: LogVMDeployMachineResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = LogVMDeployMachineResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class PassPipelineValidateResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class PassPipelineValidateResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: PassPipelineValidateResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = PassPipelineValidateResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class RefusePipelineValidateResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class RefusePipelineValidateResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: RefusePipelineValidateResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = RefusePipelineValidateResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ReleaseWorkspaceResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ReleaseWorkspaceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ReleaseWorkspaceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ReleaseWorkspaceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ResetSshKeyResponseBodySshKey(TeaModel):
    def __init__(
        self,
        id: int = None,
        public_key: str = None,
    ):
        self.id = id
        self.public_key = public_key

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.id is not None:
            result['id'] = self.id
        if self.public_key is not None:
            result['publicKey'] = self.public_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('publicKey') is not None:
            self.public_key = m.get('publicKey')
        return self


class ResetSshKeyResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        ssh_key: ResetSshKeyResponseBodySshKey = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.ssh_key = ssh_key
        self.success = success

    def validate(self):
        if self.ssh_key:
            self.ssh_key.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.ssh_key is not None:
            result['sshKey'] = self.ssh_key.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('sshKey') is not None:
            temp_model = ResetSshKeyResponseBodySshKey()
            self.ssh_key = temp_model.from_map(m['sshKey'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ResetSshKeyResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ResetSshKeyResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ResetSshKeyResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ResumeVMDeployOrderResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class ResumeVMDeployOrderResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ResumeVMDeployOrderResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ResumeVMDeployOrderResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class RetryPipelineJobRunResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class RetryPipelineJobRunResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: RetryPipelineJobRunResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = RetryPipelineJobRunResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class RetryVMDeployMachineResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class RetryVMDeployMachineResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: RetryVMDeployMachineResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = RetryVMDeployMachineResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class SkipPipelineJobRunResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class SkipPipelineJobRunResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: SkipPipelineJobRunResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = SkipPipelineJobRunResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class SkipVMDeployMachineResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class SkipVMDeployMachineResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: SkipVMDeployMachineResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = SkipVMDeployMachineResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class StartPipelineRunRequest(TeaModel):
    def __init__(
        self,
        params: str = None,
    ):
        self.params = params

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.params is not None:
            result['params'] = self.params
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('params') is not None:
            self.params = m.get('params')
        return self


class StartPipelineRunResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        pipeline_run_id: int = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.pipeline_run_id = pipeline_run_id
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.pipeline_run_id is not None:
            result['pipelineRunId'] = self.pipeline_run_id
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('pipelineRunId') is not None:
            self.pipeline_run_id = m.get('pipelineRunId')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class StartPipelineRunResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: StartPipelineRunResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = StartPipelineRunResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class StopPipelineJobRunResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class StopPipelineJobRunResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: StopPipelineJobRunResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = StopPipelineJobRunResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class StopPipelineRunResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class StopPipelineRunResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: StopPipelineRunResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = StopPipelineRunResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class StopVMDeployOrderResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class StopVMDeployOrderResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: StopVMDeployOrderResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = StopVMDeployOrderResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class TriggerRepositoryMirrorSyncRequest(TeaModel):
    def __init__(
        self,
        access_token: str = None,
        account: str = None,
        organization_id: str = None,
        token: str = None,
    ):
        self.access_token = access_token
        self.account = account
        self.organization_id = organization_id
        self.token = token

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_token is not None:
            result['accessToken'] = self.access_token
        if self.account is not None:
            result['account'] = self.account
        if self.organization_id is not None:
            result['organizationId'] = self.organization_id
        if self.token is not None:
            result['token'] = self.token
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessToken') is not None:
            self.access_token = m.get('accessToken')
        if m.get('account') is not None:
            self.account = m.get('account')
        if m.get('organizationId') is not None:
            self.organization_id = m.get('organizationId')
        if m.get('token') is not None:
            self.token = m.get('token')
        return self


class TriggerRepositoryMirrorSyncResponseBodyResult(TeaModel):
    def __init__(
        self,
        result: bool = None,
    ):
        self.result = result

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.result is not None:
            result['result'] = self.result
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('result') is not None:
            self.result = m.get('result')
        return self


class TriggerRepositoryMirrorSyncResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        result: TriggerRepositoryMirrorSyncResponseBodyResult = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.result = result
        self.success = success

    def validate(self):
        if self.result:
            self.result.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.result is not None:
            result['result'] = self.result.to_map()
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('result') is not None:
            temp_model = TriggerRepositoryMirrorSyncResponseBodyResult()
            self.result = temp_model.from_map(m['result'])
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class TriggerRepositoryMirrorSyncResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: TriggerRepositoryMirrorSyncResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = TriggerRepositoryMirrorSyncResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateFlowTagRequest(TeaModel):
    def __init__(
        self,
        color: str = None,
        flow_tag_group_id: int = None,
        name: str = None,
    ):
        self.color = color
        self.flow_tag_group_id = flow_tag_group_id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.color is not None:
            result['color'] = self.color
        if self.flow_tag_group_id is not None:
            result['flowTagGroupId'] = self.flow_tag_group_id
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('color') is not None:
            self.color = m.get('color')
        if m.get('flowTagGroupId') is not None:
            self.flow_tag_group_id = m.get('flowTagGroupId')
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class UpdateFlowTagResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdateFlowTagResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateFlowTagResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateFlowTagResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateFlowTagGroupRequest(TeaModel):
    def __init__(
        self,
        name: str = None,
    ):
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class UpdateFlowTagGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdateFlowTagGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateFlowTagGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateFlowTagGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateHostGroupRequest(TeaModel):
    def __init__(
        self,
        aliyun_region: str = None,
        ecs_label_key: str = None,
        ecs_label_value: str = None,
        ecs_type: str = None,
        env_id: str = None,
        machine_infos: str = None,
        name: str = None,
        service_connection_id: int = None,
        tag_ids: str = None,
        type: str = None,
    ):
        self.aliyun_region = aliyun_region
        self.ecs_label_key = ecs_label_key
        self.ecs_label_value = ecs_label_value
        self.ecs_type = ecs_type
        self.env_id = env_id
        self.machine_infos = machine_infos
        self.name = name
        self.service_connection_id = service_connection_id
        self.tag_ids = tag_ids
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.aliyun_region is not None:
            result['aliyunRegion'] = self.aliyun_region
        if self.ecs_label_key is not None:
            result['ecsLabelKey'] = self.ecs_label_key
        if self.ecs_label_value is not None:
            result['ecsLabelValue'] = self.ecs_label_value
        if self.ecs_type is not None:
            result['ecsType'] = self.ecs_type
        if self.env_id is not None:
            result['envId'] = self.env_id
        if self.machine_infos is not None:
            result['machineInfos'] = self.machine_infos
        if self.name is not None:
            result['name'] = self.name
        if self.service_connection_id is not None:
            result['serviceConnectionId'] = self.service_connection_id
        if self.tag_ids is not None:
            result['tagIds'] = self.tag_ids
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('aliyunRegion') is not None:
            self.aliyun_region = m.get('aliyunRegion')
        if m.get('ecsLabelKey') is not None:
            self.ecs_label_key = m.get('ecsLabelKey')
        if m.get('ecsLabelValue') is not None:
            self.ecs_label_value = m.get('ecsLabelValue')
        if m.get('ecsType') is not None:
            self.ecs_type = m.get('ecsType')
        if m.get('envId') is not None:
            self.env_id = m.get('envId')
        if m.get('machineInfos') is not None:
            self.machine_infos = m.get('machineInfos')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('serviceConnectionId') is not None:
            self.service_connection_id = m.get('serviceConnectionId')
        if m.get('tagIds') is not None:
            self.tag_ids = m.get('tagIds')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class UpdateHostGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdateHostGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateHostGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateHostGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdatePipelineRequestBasicInfo(TeaModel):
    def __init__(
        self,
        env_id: int = None,
        group_id: int = None,
        name: str = None,
        pipeline_id: int = None,
        tag_ids: str = None,
    ):
        self.env_id = env_id
        self.group_id = group_id
        self.name = name
        self.pipeline_id = pipeline_id
        self.tag_ids = tag_ids

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.env_id is not None:
            result['envId'] = self.env_id
        if self.group_id is not None:
            result['groupId'] = self.group_id
        if self.name is not None:
            result['name'] = self.name
        if self.pipeline_id is not None:
            result['pipelineId'] = self.pipeline_id
        if self.tag_ids is not None:
            result['tagIds'] = self.tag_ids
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('envId') is not None:
            self.env_id = m.get('envId')
        if m.get('groupId') is not None:
            self.group_id = m.get('groupId')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('pipelineId') is not None:
            self.pipeline_id = m.get('pipelineId')
        if m.get('tagIds') is not None:
            self.tag_ids = m.get('tagIds')
        return self


class UpdatePipelineRequestSettingsCaches(TeaModel):
    def __init__(
        self,
        desc: str = None,
        directory: str = None,
        disable: bool = None,
    ):
        self.desc = desc
        self.directory = directory
        self.disable = disable

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.desc is not None:
            result['desc'] = self.desc
        if self.directory is not None:
            result['directory'] = self.directory
        if self.disable is not None:
            result['disable'] = self.disable
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('desc') is not None:
            self.desc = m.get('desc')
        if m.get('directory') is not None:
            self.directory = m.get('directory')
        if m.get('disable') is not None:
            self.disable = m.get('disable')
        return self


class UpdatePipelineRequestSettingsGlobalParams(TeaModel):
    def __init__(
        self,
        key: str = None,
        mask: bool = None,
        running_config: bool = None,
        value: str = None,
    ):
        self.key = key
        self.mask = mask
        self.running_config = running_config
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['key'] = self.key
        if self.mask is not None:
            result['mask'] = self.mask
        if self.running_config is not None:
            result['runningConfig'] = self.running_config
        if self.value is not None:
            result['value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('key') is not None:
            self.key = m.get('key')
        if m.get('mask') is not None:
            self.mask = m.get('mask')
        if m.get('runningConfig') is not None:
            self.running_config = m.get('runningConfig')
        if m.get('value') is not None:
            self.value = m.get('value')
        return self


class UpdatePipelineRequestSettings(TeaModel):
    def __init__(
        self,
        caches: List[UpdatePipelineRequestSettingsCaches] = None,
        global_params: List[UpdatePipelineRequestSettingsGlobalParams] = None,
        runner_cache_mode: str = None,
    ):
        self.caches = caches
        self.global_params = global_params
        self.runner_cache_mode = runner_cache_mode

    def validate(self):
        if self.caches:
            for k in self.caches:
                if k:
                    k.validate()
        if self.global_params:
            for k in self.global_params:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        result['caches'] = []
        if self.caches is not None:
            for k in self.caches:
                result['caches'].append(k.to_map() if k else None)
        result['globalParams'] = []
        if self.global_params is not None:
            for k in self.global_params:
                result['globalParams'].append(k.to_map() if k else None)
        if self.runner_cache_mode is not None:
            result['runnerCacheMode'] = self.runner_cache_mode
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        self.caches = []
        if m.get('caches') is not None:
            for k in m.get('caches'):
                temp_model = UpdatePipelineRequestSettingsCaches()
                self.caches.append(temp_model.from_map(k))
        self.global_params = []
        if m.get('globalParams') is not None:
            for k in m.get('globalParams'):
                temp_model = UpdatePipelineRequestSettingsGlobalParams()
                self.global_params.append(temp_model.from_map(k))
        if m.get('runnerCacheMode') is not None:
            self.runner_cache_mode = m.get('runnerCacheMode')
        return self


class UpdatePipelineRequestTriggerInfoScheduled(TeaModel):
    def __init__(
        self,
        days_of_week: str = None,
        fixed_time: str = None,
        from_: str = None,
        interval: int = None,
        only_source_change: bool = None,
        to: str = None,
        type: str = None,
    ):
        self.days_of_week = days_of_week
        self.fixed_time = fixed_time
        self.from_ = from_
        self.interval = interval
        self.only_source_change = only_source_change
        self.to = to
        self.type = type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.days_of_week is not None:
            result['daysOfWeek'] = self.days_of_week
        if self.fixed_time is not None:
            result['fixedTime'] = self.fixed_time
        if self.from_ is not None:
            result['from'] = self.from_
        if self.interval is not None:
            result['interval'] = self.interval
        if self.only_source_change is not None:
            result['onlySourceChange'] = self.only_source_change
        if self.to is not None:
            result['to'] = self.to
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('daysOfWeek') is not None:
            self.days_of_week = m.get('daysOfWeek')
        if m.get('fixedTime') is not None:
            self.fixed_time = m.get('fixedTime')
        if m.get('from') is not None:
            self.from_ = m.get('from')
        if m.get('interval') is not None:
            self.interval = m.get('interval')
        if m.get('onlySourceChange') is not None:
            self.only_source_change = m.get('onlySourceChange')
        if m.get('to') is not None:
            self.to = m.get('to')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class UpdatePipelineRequestTriggerInfo(TeaModel):
    def __init__(
        self,
        scheduled: UpdatePipelineRequestTriggerInfoScheduled = None,
        webhook_enable: bool = None,
    ):
        self.scheduled = scheduled
        self.webhook_enable = webhook_enable

    def validate(self):
        if self.scheduled:
            self.scheduled.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.scheduled is not None:
            result['scheduled'] = self.scheduled.to_map()
        if self.webhook_enable is not None:
            result['webhookEnable'] = self.webhook_enable
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('scheduled') is not None:
            temp_model = UpdatePipelineRequestTriggerInfoScheduled()
            self.scheduled = temp_model.from_map(m['scheduled'])
        if m.get('webhookEnable') is not None:
            self.webhook_enable = m.get('webhookEnable')
        return self


class UpdatePipelineRequest(TeaModel):
    def __init__(
        self,
        basic_info: UpdatePipelineRequestBasicInfo = None,
        pipeline_yaml: str = None,
        settings: UpdatePipelineRequestSettings = None,
        trigger_info: UpdatePipelineRequestTriggerInfo = None,
    ):
        self.basic_info = basic_info
        self.pipeline_yaml = pipeline_yaml
        self.settings = settings
        self.trigger_info = trigger_info

    def validate(self):
        if self.basic_info:
            self.basic_info.validate()
        if self.settings:
            self.settings.validate()
        if self.trigger_info:
            self.trigger_info.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.basic_info is not None:
            result['basicInfo'] = self.basic_info.to_map()
        if self.pipeline_yaml is not None:
            result['pipelineYaml'] = self.pipeline_yaml
        if self.settings is not None:
            result['settings'] = self.settings.to_map()
        if self.trigger_info is not None:
            result['triggerInfo'] = self.trigger_info.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('basicInfo') is not None:
            temp_model = UpdatePipelineRequestBasicInfo()
            self.basic_info = temp_model.from_map(m['basicInfo'])
        if m.get('pipelineYaml') is not None:
            self.pipeline_yaml = m.get('pipelineYaml')
        if m.get('settings') is not None:
            temp_model = UpdatePipelineRequestSettings()
            self.settings = temp_model.from_map(m['settings'])
        if m.get('triggerInfo') is not None:
            temp_model = UpdatePipelineRequestTriggerInfo()
            self.trigger_info = temp_model.from_map(m['triggerInfo'])
        return self


class UpdatePipelineResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        object: int = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.object = object
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.object is not None:
            result['object'] = self.object
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('object') is not None:
            self.object = m.get('object')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdatePipelineResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdatePipelineResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdatePipelineResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdatePipelineBaseInfoRequest(TeaModel):
    def __init__(
        self,
        env_id: int = None,
        pipeline_name: str = None,
        tag_list: str = None,
    ):
        self.env_id = env_id
        self.pipeline_name = pipeline_name
        self.tag_list = tag_list

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.env_id is not None:
            result['envId'] = self.env_id
        if self.pipeline_name is not None:
            result['pipelineName'] = self.pipeline_name
        if self.tag_list is not None:
            result['tagList'] = self.tag_list
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('envId') is not None:
            self.env_id = m.get('envId')
        if m.get('pipelineName') is not None:
            self.pipeline_name = m.get('pipelineName')
        if m.get('tagList') is not None:
            self.tag_list = m.get('tagList')
        return self


class UpdatePipelineBaseInfoResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdatePipelineBaseInfoResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdatePipelineBaseInfoResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdatePipelineBaseInfoResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdatePipelineGroupRequest(TeaModel):
    def __init__(
        self,
        name: str = None,
    ):
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.name is not None:
            result['name'] = self.name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('name') is not None:
            self.name = m.get('name')
        return self


class UpdatePipelineGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdatePipelineGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdatePipelineGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdatePipelineGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateProjectMemberRequest(TeaModel):
    def __init__(
        self,
        role_identifier: str = None,
        target_identifier: str = None,
        target_type: str = None,
        user_identifier: str = None,
        user_type: str = None,
    ):
        self.role_identifier = role_identifier
        self.target_identifier = target_identifier
        self.target_type = target_type
        self.user_identifier = user_identifier
        self.user_type = user_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.role_identifier is not None:
            result['roleIdentifier'] = self.role_identifier
        if self.target_identifier is not None:
            result['targetIdentifier'] = self.target_identifier
        if self.target_type is not None:
            result['targetType'] = self.target_type
        if self.user_identifier is not None:
            result['userIdentifier'] = self.user_identifier
        if self.user_type is not None:
            result['userType'] = self.user_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('roleIdentifier') is not None:
            self.role_identifier = m.get('roleIdentifier')
        if m.get('targetIdentifier') is not None:
            self.target_identifier = m.get('targetIdentifier')
        if m.get('targetType') is not None:
            self.target_type = m.get('targetType')
        if m.get('userIdentifier') is not None:
            self.user_identifier = m.get('userIdentifier')
        if m.get('userType') is not None:
            self.user_type = m.get('userType')
        return self


class UpdateProjectMemberResponseBodyMember(TeaModel):
    def __init__(
        self,
        gmt_create: int = None,
        gmt_modified: int = None,
        id: str = None,
        role_identifier: str = None,
        target_identifier: str = None,
        target_type: str = None,
        user_identifier: str = None,
        user_type: str = None,
    ):
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.id = id
        self.role_identifier = role_identifier
        self.target_identifier = target_identifier
        self.target_type = target_type
        self.user_identifier = user_identifier
        self.user_type = user_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.id is not None:
            result['id'] = self.id
        if self.role_identifier is not None:
            result['roleIdentifier'] = self.role_identifier
        if self.target_identifier is not None:
            result['targetIdentifier'] = self.target_identifier
        if self.target_type is not None:
            result['targetType'] = self.target_type
        if self.user_identifier is not None:
            result['userIdentifier'] = self.user_identifier
        if self.user_type is not None:
            result['userType'] = self.user_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('id') is not None:
            self.id = m.get('id')
        if m.get('roleIdentifier') is not None:
            self.role_identifier = m.get('roleIdentifier')
        if m.get('targetIdentifier') is not None:
            self.target_identifier = m.get('targetIdentifier')
        if m.get('targetType') is not None:
            self.target_type = m.get('targetType')
        if m.get('userIdentifier') is not None:
            self.user_identifier = m.get('userIdentifier')
        if m.get('userType') is not None:
            self.user_type = m.get('userType')
        return self


class UpdateProjectMemberResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_msg: str = None,
        member: UpdateProjectMemberResponseBodyMember = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_msg = error_msg
        self.member = member
        self.request_id = request_id
        self.success = success

    def validate(self):
        if self.member:
            self.member.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_msg is not None:
            result['errorMsg'] = self.error_msg
        if self.member is not None:
            result['member'] = self.member.to_map()
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMsg') is not None:
            self.error_msg = m.get('errorMsg')
        if m.get('member') is not None:
            temp_model = UpdateProjectMemberResponseBodyMember()
            self.member = temp_model.from_map(m['member'])
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdateProjectMemberResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateProjectMemberResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateProjectMemberResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateResourceMemberRequest(TeaModel):
    def __init__(
        self,
        role_name: str = None,
    ):
        self.role_name = role_name

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.role_name is not None:
            result['roleName'] = self.role_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('roleName') is not None:
            self.role_name = m.get('roleName')
        return self


class UpdateResourceMemberResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdateResourceMemberResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateResourceMemberResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateResourceMemberResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateVariableGroupRequest(TeaModel):
    def __init__(
        self,
        description: str = None,
        name: str = None,
        variables: str = None,
    ):
        self.description = description
        self.name = name
        self.variables = variables

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.description is not None:
            result['description'] = self.description
        if self.name is not None:
            result['name'] = self.name
        if self.variables is not None:
            result['variables'] = self.variables
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('description') is not None:
            self.description = m.get('description')
        if m.get('name') is not None:
            self.name = m.get('name')
        if m.get('variables') is not None:
            self.variables = m.get('variables')
        return self


class UpdateVariableGroupResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        return self


class UpdateVariableGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateVariableGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateVariableGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateWorkItemRequest(TeaModel):
    def __init__(
        self,
        field_type: str = None,
        identifier: str = None,
        property_key: str = None,
        property_value: str = None,
    ):
        self.field_type = field_type
        self.identifier = identifier
        self.property_key = property_key
        self.property_value = property_value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.field_type is not None:
            result['fieldType'] = self.field_type
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.property_key is not None:
            result['propertyKey'] = self.property_key
        if self.property_value is not None:
            result['propertyValue'] = self.property_value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fieldType') is not None:
            self.field_type = m.get('fieldType')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('propertyKey') is not None:
            self.property_key = m.get('propertyKey')
        if m.get('propertyValue') is not None:
            self.property_value = m.get('propertyValue')
        return self


class UpdateWorkItemResponseBodyWorkitem(TeaModel):
    def __init__(
        self,
        assigned_to: str = None,
        category_identifier: str = None,
        creator: str = None,
        document: str = None,
        gmt_create: int = None,
        gmt_modified: int = None,
        identifier: str = None,
        logical_status: str = None,
        modifier: str = None,
        parent_identifier: str = None,
        serial_number: str = None,
        space_identifier: str = None,
        space_name: str = None,
        space_type: str = None,
        sprint_identifier: str = None,
        status: str = None,
        status_identifier: str = None,
        status_stage_identifier: str = None,
        subject: str = None,
        update_status_at: int = None,
        workitem_type_identifier: str = None,
    ):
        self.assigned_to = assigned_to
        self.category_identifier = category_identifier
        self.creator = creator
        self.document = document
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.identifier = identifier
        self.logical_status = logical_status
        self.modifier = modifier
        self.parent_identifier = parent_identifier
        self.serial_number = serial_number
        self.space_identifier = space_identifier
        self.space_name = space_name
        self.space_type = space_type
        self.sprint_identifier = sprint_identifier
        self.status = status
        self.status_identifier = status_identifier
        self.status_stage_identifier = status_stage_identifier
        self.subject = subject
        self.update_status_at = update_status_at
        self.workitem_type_identifier = workitem_type_identifier

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.assigned_to is not None:
            result['assignedTo'] = self.assigned_to
        if self.category_identifier is not None:
            result['categoryIdentifier'] = self.category_identifier
        if self.creator is not None:
            result['creator'] = self.creator
        if self.document is not None:
            result['document'] = self.document
        if self.gmt_create is not None:
            result['gmtCreate'] = self.gmt_create
        if self.gmt_modified is not None:
            result['gmtModified'] = self.gmt_modified
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.logical_status is not None:
            result['logicalStatus'] = self.logical_status
        if self.modifier is not None:
            result['modifier'] = self.modifier
        if self.parent_identifier is not None:
            result['parentIdentifier'] = self.parent_identifier
        if self.serial_number is not None:
            result['serialNumber'] = self.serial_number
        if self.space_identifier is not None:
            result['spaceIdentifier'] = self.space_identifier
        if self.space_name is not None:
            result['spaceName'] = self.space_name
        if self.space_type is not None:
            result['spaceType'] = self.space_type
        if self.sprint_identifier is not None:
            result['sprintIdentifier'] = self.sprint_identifier
        if self.status is not None:
            result['status'] = self.status
        if self.status_identifier is not None:
            result['statusIdentifier'] = self.status_identifier
        if self.status_stage_identifier is not None:
            result['statusStageIdentifier'] = self.status_stage_identifier
        if self.subject is not None:
            result['subject'] = self.subject
        if self.update_status_at is not None:
            result['updateStatusAt'] = self.update_status_at
        if self.workitem_type_identifier is not None:
            result['workitemTypeIdentifier'] = self.workitem_type_identifier
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('assignedTo') is not None:
            self.assigned_to = m.get('assignedTo')
        if m.get('categoryIdentifier') is not None:
            self.category_identifier = m.get('categoryIdentifier')
        if m.get('creator') is not None:
            self.creator = m.get('creator')
        if m.get('document') is not None:
            self.document = m.get('document')
        if m.get('gmtCreate') is not None:
            self.gmt_create = m.get('gmtCreate')
        if m.get('gmtModified') is not None:
            self.gmt_modified = m.get('gmtModified')
        if m.get('identifier') is not None:
            self.identifier = m.get('identifier')
        if m.get('logicalStatus') is not None:
            self.logical_status = m.get('logicalStatus')
        if m.get('modifier') is not None:
            self.modifier = m.get('modifier')
        if m.get('parentIdentifier') is not None:
            self.parent_identifier = m.get('parentIdentifier')
        if m.get('serialNumber') is not None:
            self.serial_number = m.get('serialNumber')
        if m.get('spaceIdentifier') is not None:
            self.space_identifier = m.get('spaceIdentifier')
        if m.get('spaceName') is not None:
            self.space_name = m.get('spaceName')
        if m.get('spaceType') is not None:
            self.space_type = m.get('spaceType')
        if m.get('sprintIdentifier') is not None:
            self.sprint_identifier = m.get('sprintIdentifier')
        if m.get('status') is not None:
            self.status = m.get('status')
        if m.get('statusIdentifier') is not None:
            self.status_identifier = m.get('statusIdentifier')
        if m.get('statusStageIdentifier') is not None:
            self.status_stage_identifier = m.get('statusStageIdentifier')
        if m.get('subject') is not None:
            self.subject = m.get('subject')
        if m.get('updateStatusAt') is not None:
            self.update_status_at = m.get('updateStatusAt')
        if m.get('workitemTypeIdentifier') is not None:
            self.workitem_type_identifier = m.get('workitemTypeIdentifier')
        return self


class UpdateWorkItemResponseBody(TeaModel):
    def __init__(
        self,
        error_code: str = None,
        error_message: str = None,
        request_id: str = None,
        success: bool = None,
        workitem: UpdateWorkItemResponseBodyWorkitem = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.request_id = request_id
        self.success = success
        self.workitem = workitem

    def validate(self):
        if self.workitem:
            self.workitem.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.error_code is not None:
            result['errorCode'] = self.error_code
        if self.error_message is not None:
            result['errorMessage'] = self.error_message
        if self.request_id is not None:
            result['requestId'] = self.request_id
        if self.success is not None:
            result['success'] = self.success
        if self.workitem is not None:
            result['workitem'] = self.workitem.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('errorCode') is not None:
            self.error_code = m.get('errorCode')
        if m.get('errorMessage') is not None:
            self.error_message = m.get('errorMessage')
        if m.get('requestId') is not None:
            self.request_id = m.get('requestId')
        if m.get('success') is not None:
            self.success = m.get('success')
        if m.get('workitem') is not None:
            temp_model = UpdateWorkItemResponseBodyWorkitem()
            self.workitem = temp_model.from_map(m['workitem'])
        return self


class UpdateWorkItemResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateWorkItemResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        self.validate_required(self.headers, 'headers')
        self.validate_required(self.status_code, 'status_code')
        self.validate_required(self.body, 'body')
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateWorkItemResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


