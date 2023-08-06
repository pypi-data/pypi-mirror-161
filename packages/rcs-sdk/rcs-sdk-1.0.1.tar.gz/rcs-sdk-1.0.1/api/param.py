"""
  模块描述：接口参数
  @author 8526
  @date 2022-04-28 9:15:33
  版权所有 Copyright www.dahantc.com
"""


class BaseJsonable(object):

    def to_dict(self):
        d = {}
        d.update(self.__dict__)
        return d


# 场景发送入参
class SceneSendParam(BaseJsonable):

    def __init__(self, phone, sceneId, messageId):
        # 手机号
        self.phone = phone
        # 场景id
        self.sceneId = sceneId
        # 消息id
        self.messageId = messageId


class MediaUploadParam(BaseJsonable):
    def __init__(self, keyword, field, mode):
        # 关键词
        self.keyword = keyword
        # 自定义的素材编号
        self.field = field
        # 上传素材类型，永久素材则需填入’perm’；临时素材 temp
        self.mode = mode


# 文件下载参数
class MediaDownloadParam(BaseJsonable):
    # 文件下载路径
    def __init__(self, path):
        self.path = path


#
class SceneNodeSendParam(BaseJsonable):
    def __init__(self, phone, sceneId, messageId, nodeId, params):
        # 接收手机号码
        self.phone = phone
        # 在平台添加的场景的ID
        self.sceneId = sceneId
        # 本条消息的唯一标识
        self.messageId = messageId
        # 在平台申请的节点编号
        self.nodeId = nodeId
        # 节点配置替换参数
        self.params = params


# 模板消息创建参数
class MessageTemplateCreateParam(BaseJsonable):
    def __init__(self, templateName, label, storeSupported, smsSupported, smsContent, message):
        # 模板名称
        self.templateName = templateName
        # 标签 多个以逗号分隔
        self.label = label
        # 是否离线存储。
        self.storeSupported = storeSupported
        #  是否转短信。
        self.smsSupported = smsSupported
        # smsContent为消息回落时的消息内容，
        self.smsContent = smsContent
        # 消息内容
        self.message = message


# 模板消息发送参数
class MsgTemplateSendParam(BaseJsonable):
    def __init__(self, phone, messageId, conversationId, contributionId, inReplyTo, variables, templateId):
        # 下发号码
        self.phone = phone
        # 请求的消息ID
        self.messageId = messageId
        # 会话ID
        self.conversationId = conversationId
        # 对话ID
        self.contributionId = contributionId
        # 回复的消息的contributionId
        self.inReplyTo = inReplyTo
        # 变量模板变量信息,key 为变量名，value 为变量值
        self.variables = variables
        # 模板id
        self.templateId = templateId


# 协议发送的提交内容
class ProtocolOutBound(BaseJsonable):

    def __init__(self, phone, messageId, conversationId, contributionId, inReplyTo, storeSupported, smsSupported,
                 smsContent, reportRequest, message):
        # 下发号码
        self.phone = phone
        # 请求的消息ID
        self.messageId = messageId
        # 会话ID
        self.conversationId = conversationId
        # 对话ID
        self.contributionId = contributionId
        # 回复的消息的contributionId
        self.inReplyTo = inReplyTo
        # 是否离线存储。 false:不存也不重试，true:存，缺省true
        self.storeSupported = storeSupported
        # 否转短信。根据发送平台使用不同枚举
        self.smsSupported = smsSupported
        # smsContent为消息回落时的消息内容， smsSupported为true时，本字段有效且
        self.smsContent = smsContent
        '''
            状态事件报告列表，每个状态事件的
         * 可选值为:
         * 消息状态，主要有如下几种状态：
         * sent：消息已发送
         * failed：消息发送失败
         * delivered：消息已送达
         * displayed：消息已阅读
         * deliveredToNetwork：已转短消息已送达
         '''
        self.reportRequest = reportRequest
        # 消息内容
        self.message = message


# 标准接口消息
class Message(BaseJsonable):
    def __init__(self, contentType, contentEncoding, contentText, suggestion):
        # 消息类型
        self.contentType = contentType
        # 内容编码 utf-8 和 base64 编码
        self.contentEncoding = contentEncoding
        # 内容
        self.contentText = contentText
        # 悬浮菜单
        self.suggestion = suggestion


# 回复建议 (属性二选一)
class Suggestion(BaseJsonable):
    def __init__(self, reply, action):
        # 按钮上行回复
        self.reply = reply
        # 按钮动作
        self.action = action


# 按钮上行回复
class Reply(BaseJsonable):
    def __init__(self, displayText, postback):
        # 回复展示的文字 1 - 25 byte
        self.displayText = displayText
        # 点击反馈内容
        self.postback = postback


# 点击反馈内容
class PostBack(BaseJsonable):
    def __init__(self, data):
        # 定义返回给chatbot的内容 最大2048
        self.data = data


# 按钮行为 Action 多选一 且为必须
class Action(BaseJsonable):
    def __init__(self, displayText, postback, dialerAction, composeAction, calendarAction, urlAction, settingsAction,
                 mapAction, deviceAction):
        # 展示文字
        self.displayText = displayText
        # 点击反馈内容
        self.postback = postback
        # 拨打电话
        self.dialerAction = dialerAction
        # 混合
        self.composeAction = composeAction
        # 设置日历
        self.calendarAction = calendarAction
        # 打开链接
        self.urlAction = urlAction
        # 设置
        self.settingsAction = settingsAction
        # 地图
        self.mapAction = mapAction
        # 设备
        self.deviceAction = deviceAction


# 拨打电话操作（多种属性选一）
class DialerAction(BaseJsonable):
    def __init__(self, dialPhoneNumber, dialEnrichedCall, dialVideoCall):
        # 普通拨号
        self.dialPhoneNumber = dialPhoneNumber
        # 增强电话
        self.dialEnrichedCall = dialEnrichedCall
        # 视频电话
        self.dialVideoCall = dialVideoCall


# 电话号码
class PhoneNumber(BaseJsonable):
    def __init__(self, phoneNumber, subject):
        # 拨打的电话号码
        self.phoneNumber = phoneNumber
        # 主题 最大 60 (只在 dialEnrichedCall 中才有)
        self.subject = subject


# 写作(属性 二者选其一)
class ComposeAction(BaseJsonable):
    def __init__(self, composeTextMessage, composeRecordingMessage):
        # 写一个短信草稿
        self.composeTextMessage = composeTextMessage
        # 用媒体录音编写一份草稿信息
        self.composeRecordingMessage = composeRecordingMessage


# 短信
class ComposeTextMessage(BaseJsonable):
    def __init__(self, phoneNumber, text):
        # 电话号码
        self.phoneNumber = phoneNumber
        # 文本
        self.text = text


# 录信息
class ComposeRecordingMessage(BaseJsonable):
    def __init__(self, phoneNumber, type):
        # 电话号码
        self.phoneNumber = phoneNumber
        # AUDIO 音频 VIDEO 视频
        self.type = type


# 日历操作
class CalendarAction(BaseJsonable):
    def __init__(self, createCalendarEvent):
        # 日历创建事件
        self.createCalendarEvent = createCalendarEvent


# 日历事件
class CalendarEvent(BaseJsonable):
    def __init__(self, startTime, endTime, title, description):
        # 开始时间
        self.startTime = startTime
        # 结束时间
        self.endTime = endTime
        # 标题
        self.title = title
        # 描述
        self.description = description


# 连接操作
class UrlAction(BaseJsonable):
    def __init__(self, openUrl):
        # 打开链接
        self.openUrl = openUrl


# Rcs 打开链接操作的路径
class OpenUrl(BaseJsonable):
    def __init__(self, url, application, viewMode, parameters):
        # 打开链接地址
        self.url = url
        # 打开链接地址的应用 ["webview","browser"]
        self.application = application
        # 查看模式 ["full", "half", "tall"]
        self.viewMode = viewMode
        # 参数 1 - 200
        self.parameters = parameters


# 设置 （属性二选一）
class SettingsAction(BaseJsonable):
    def __init__(self, disableAnonymization, enableDisplayedNotifications):
        # 禁用匿名化
        self.disableAnonymization = disableAnonymization
        # 启用显示通知
        self.enableDisplayedNotifications = enableDisplayedNotifications


# 打开地图动作
class MapAction(BaseJsonable):
    def __init__(self, showLocation, requestLocationPush):
        # 展示地理位置
        self.showLocation = showLocation
        # 发送一次地理位置推送
        self.requestLocationPush = requestLocationPush


# 展示地址
class ShowLocation(BaseJsonable):
    def __init__(self, location):
        # 地理位置
        self.location = location


# 地理位置
class Location(BaseJsonable):
    def __init__(self, latitude, longitude, label, query):
        # 维度
        self.latitude = latitude
        # 经度
        self.longitude = longitude
        # 标签 1-100
        self.label = label
        # 查询地理位置（与前面的属性冲突）
        self.query = query


# 设备操作
class DeviceAction(BaseJsonable):
    def __init__(self, requestDeviceSpecifics):
        # 请求设备细节
        self.requestDeviceSpecifics = requestDeviceSpecifics


# 菜单参数
class MenuParam(BaseJsonable):
    def __init__(self, menu):
        self.menu = menu


# 菜单对象
class FirstMenu(BaseJsonable):
    def __init__(self, entries):
        # 菜单数组
        self.entries = entries


# 一级菜单entry
class FirstEntry(BaseJsonable):
    def __init__(self, menu, reply, action):
        #  二级菜单
        self.menu = menu
        # 建议回复按钮
        self.reply = reply
        # 建议操作按钮
        self.action = action


# 类描述：二级菜单
class SecondMenu(BaseJsonable):
    def __init__(self, entries, displayText):
        self.entries = entries
        self.displayText = displayText


# 二级菜单entry
class SecondEntry(BaseJsonable):
    def __init__(self, reply, action):
        self.reply = reply
        self.action = action
