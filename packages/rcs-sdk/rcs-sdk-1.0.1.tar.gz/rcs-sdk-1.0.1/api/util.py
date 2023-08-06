"""
  模块描述：工具
  @author 8526
  @date 2022-04-28 9:15:33
  版权所有 Copyright www.dahantc.com
"""
import base64
import datetime
import hashlib


# 根据未加密的账号密码计算Authorization
def getAuthByTextPassword(account, date, pwd):
    hl = hashlib.md5()
    hl.update(pwd.encode(encoding='utf8'))
    pwdmd5 = hl.hexdigest()

    content = date + pwdmd5
    h2 = hashlib.md5()
    h2.update(content.encode(encoding='utf-8'))
    pdmd5 = h2.hexdigest()
    authstr = account + ':' + pdmd5
    return str(base64.b64encode(authstr.encode("utf-8")), "utf-8")


# 根据账号密码获取请求header头
def getAuthHeaders(account, pwd):
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    authorization = getAuthByTextPassword(account, date, pwd)
    return {"Content-Type": "application/json; chsarset=utf8", "Date": date, "Authorization": authorization}


def getFileAuthHeaders(account, pwd):
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    authorization = getAuthByTextPassword(account, date, pwd)
    return {"Charset": "UTF-8", "Connection": "Keep-Alive", "Date": date, "Authorization": authorization}
