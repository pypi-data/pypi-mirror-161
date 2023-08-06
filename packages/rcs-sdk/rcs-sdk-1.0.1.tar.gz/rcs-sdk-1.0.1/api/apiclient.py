"""
  模块描述：业务方法封装client
  @author 8526
  @date 2022-04-28 9:15:33
  版权所有 Copyright www.dahantc.com
"""
import json

import requests

from api import conf
from api import response
from api import util


# 场景发送类
class SceneSendClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def scene_send(self, params):
        try:
            url = conf.Base_Url + conf.SEND_BY_SCENE + self.authInfo.chatbotId
            header_dict = util.getAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            param_json = json.dumps(params.to_dict())
            result = requests.post(url, headers=header_dict, data=param_json)
            return response.apiResponseDecoder(json.loads(result.content))
        except Exception as e:
            print(e)
            return response.errorResponse


# 场景节点发送类
class SceneNodeSendClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def scene_node_send(self, params):
        try:
            param_dict = params.to_dict()
            url = conf.Base_Url + conf.SEND_BY_SCENENODE + self.authInfo.chatbotId + "/" + param_dict.get(
                'sceneId') + "/" + param_dict.get('nodeId');
            header_dict = util.getAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            param_json = json.dumps(param_dict)
            result = requests.post(url, headers=header_dict, data=param_json)
            return response.apiResponseDecoder(json.loads(result.content))
        except Exception as e:
            print(e)
            return response.errorResponse


# 菜单更新类
class MenuUpdateClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def update_menu(self, params):
        try:
            url = conf.Base_Url + conf.MENU_UPDATE + self.authInfo.chatbotId
            header_dict = util.getAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            param_json = json.dumps(params.to_dict())
            result = requests.post(url, headers=header_dict, data=param_json)
            return response.menuResponseDecoder(json.loads(result.content))
        except Exception as e:
            print(e)
            return response.errorResponse


# 协议消息下发
class ProtocolOutBoundClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def protocol_out_bound(self, params):
        try:
            url = conf.Base_Url + conf.SEND_BY_PROTOCOL + self.authInfo.chatbotId
            header_dict = util.getAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            param_json = json.dumps(params.to_dict())
            result = requests.post(url, headers=header_dict, data=param_json)
            return response.apiResponseDecoder(json.loads(result.content))
        except Exception as e:
            print(e)
            return response.errorResponse


# 模板消息创建类
class TemplateMsgCreateClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def template_create(self, params):
        try:
            url = conf.Base_Url + conf.MESSAGE_TEMPLATE_CREATE + self.authInfo.chatbotId
            header_dict = util.getAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            param_json = json.dumps(params.to_dict())
            result = requests.post(url, headers=header_dict, data=param_json)
            return response.apiResponseDecoder(json.loads(result.content))
        except Exception as e:
            print(e)
            return response.errorResponse


# 模板消息发送
class TemplateMsgSendClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def template_send(self, params):
        try:
            url = conf.Base_Url + conf.SEND_BY_TEMPLATE + self.authInfo.chatbotId
            header_dict = util.getAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            param_json = json.dumps(params.to_dict())
            result = requests.post(url, headers=header_dict, data=param_json)
            return response.apiResponseDecoder(json.loads(result.content))
        except Exception as e:
            print(e)
            return response.errorResponse


# 素材上传
class MediaUploadClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def media_upload(self, params, files):
        try:
            url = conf.Base_Url + conf.UPLOAD_MEDIA + self.authInfo.chatbotId
            header_dict = util.getFileAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            result = requests.post(url, headers=header_dict, data=params.to_dict(), files=files, verify=False)
            return response.mediaUploadDecoder(json.loads(result.content))
        except Exception as e:
            print(e)
            return response.errorResponse


# 素材下载
class MediaDownloadClient:

    def __init__(self, authInfo):
        self.authInfo = authInfo

    def media_download(self, params):
        try:
            url = conf.Base_Url + conf.DOWNLOAD_FILE + self.authInfo.chatbotId
            header_dict = util.getFileAuthHeaders(self.authInfo.account, self.authInfo.pwd)
            header_dict['path'] = params.to_dict().get('path')
            result = requests.get(url, headers=header_dict, verify=False, stream=True)
            return result
        except Exception as e:
            print(e)
            return response.errorResponse
