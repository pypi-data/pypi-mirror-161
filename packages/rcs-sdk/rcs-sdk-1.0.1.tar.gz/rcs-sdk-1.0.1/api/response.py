"""
  模块描述：接口响应
  @author 8526
  @date 2022-04-28 9:15:33
  版权所有 Copyright www.dahantc.com
"""


class ApiResponse:
    def __init__(self, code, desc, result):
        self.code, self.desc, self.result = code, desc, result

    def __str__(self):
        return str(self.__dict__)


errorResponse = ApiResponse('98', '系统错误', None)


class MsgSendData:
    def __init__(self, messageId, time, failPhones):
        self.messageId, self.time, self.failPhones = messageId, time, failPhones

    def __str__(self):
        return str(self.__dict__)


class TemplateData:
    def __init__(self, templateId):
        self.templateId = templateId

    def __str__(self):
        return str(self.__dict__)


class MediaUploadData:
    def __init__(self, fileId, filePath, thumbnailPath, until, keyword):
        self.fileId = fileId
        self.filePath = filePath
        self.thumbnailPath = thumbnailPath
        self.until = until
        self.keyword = keyword

    def __str__(self):
        return str(self.__dict__)


def msgDataDecoder(obj):
    if obj is None:
        return None
    return MsgSendData(obj.get('messageId'), obj.get('time'), obj.get('failPhones'))


def templateDecoder(obj):
    if obj is None:
        return None
    return TemplateData(obj.get('templateId'))


def apiResponseDecoder(obj):
    result = msgDataDecoder(obj.get('result'))
    return ApiResponse(obj.get('code'), obj.get('desc'), result)


def menuResponseDecoder(obj):
    return ApiResponse(obj.get('code'), obj.get('desc'))


def uploadDetailDecoder(obj):
    if obj is None:
        return None
    return MediaUploadData(obj.get('fileId'), obj.get('filePath'), obj.get('thumbnailPath'), obj.get('until'),
                           obj.get('keyword'))


def mediaUploadDecoder(obj):
    result = uploadDetailDecoder(obj.get('result'))
    return ApiResponse(obj.get('code'), obj.get('desc'), result)
