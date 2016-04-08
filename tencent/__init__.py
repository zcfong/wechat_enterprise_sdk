#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from .WXBizMsgCrypt import WXBizMsgCrypt
from .ierror import WXBizMsgCrypt_OK

class OfficialWechat(object):

    def __init__(self, token=None, corpid=None, corpsecret=None, encoding_aes_key=None, access_token=None, jsapi_ticket=None):
        self.token = token
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.encoding_aes_key = encoding_aes_key
        self.jsapi_ticket = jsapi_ticket
        self.wxcpt = WXBizMsgCrypt(token, encoding_aes_key, corpid)

    def check_signature(self, msg_signature, timestamp, nonce, echostr):
        result, echostr = self.wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        return result == WXBizMsgCrypt_OK, echostr

    def decrypt_message(self, data, msg_signature, timestamp, nonce):
        result, data = self.wxcpt.DecryptMsg(data, msg_signature, timestamp, nonce)
        return result == WXBizMsgCrypt_OK, data

    def encrypt_message(self, data, nonce, timestamp):
        result, data = self.wxcpt.DecryptMsg(data, nonce, timestamp)
        return result == WXBizMsgCrypt_OK, data

    @classmethod
    def _transcoding(cls, data):
        """编码转换
        :param data: 需要转换的数据
        :return: 转换好的数据
        """
        if not data:
            return data

        result = None
        if isinstance(data, str) and hasattr(data, 'decode'):
            result = data.decode('utf-8')
        else:
            result = data
        return result

    @classmethod
    def _transcoding_list(cls, data):
        """编码转换 for list
        :param data: 需要转换的 list 数据
        :return: 转换好的 list
        """
        if not isinstance(data, list):
            raise ValueError('Parameter data must be list object.')

        result = []
        for item in data:
            if isinstance(item, dict):
                result.append(cls._transcoding_dict(item))
            elif isinstance(item, list):
                result.append(cls._transcoding_list(item))
            else:
                result.append(item)
        return result

    @classmethod
    def _transcoding_dict(cls, data):
        """
        编码转换 for dict
        :param data: 需要转换的 dict 数据
        :return: 转换好的 dict
        """
        if not isinstance(data, dict):
            raise ValueError('Parameter data must be dict object.')

        result = {}
        for k, v in data.items():
            k = cls._transcoding(k)
            if isinstance(v, dict):
                v = cls._transcoding_dict(v)
            elif isinstance(v, list):
                v = cls._transcoding_list(v)
            else:
                v = cls._transcoding(v)
            result.update({k: v})
        return result