# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import six


class WechatException(Exception):
    pass


class WechatSDKException(WechatException):
    """SDK 错误异常（仅包含错误内容描述）"""
    def __init__(self, message=''):
        """
        :param message: 错误内容描述，可选
        """
        self.message = message

    def __str__(self):
        return self.message


class SignatureError(WechatSDKException):
    """构造参数提供不全异常"""
    pass


class NeedParamError(WechatSDKException):
    """构造参数提供不全异常"""
    pass


class ParseError(WechatSDKException):
    """解析微信服务器数据异常"""
    pass


class DecryptError(WechatSDKException):
    """解密异常"""
    pass


class EncryptError(WechatSDKException):
    """加密异常"""
    pass


class NeedParseError(WechatSDKException):
    """尚未解析微信服务器请求数据异常"""
    pass

