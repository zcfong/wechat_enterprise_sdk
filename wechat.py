# -*- coding: utf-8 -*-

import hashlib
import requests
import cgi
from StringIO import StringIO

class Wechat(object):
	"""
	微信企业号基础类
	仅支持企业号， 公司剧情需要，抽出来作为基础类
	该工具参考wechat-python-sdk
	"""

	def __init__(self, token=None, corpid=None, corpsecret=None, access_token=None, access_token_expires_at=None, jsapi_ticket=None:
		self.token = token
		self.corpid = corpid
		self.corpsecret = corpsecret
		self.access_token_expires_at = access_token_expires_at
		self.jsapi_ticket = jsapi_ticket


	def grant_access_token(self):
		"""
		获取token , 暂时不做失败处理
		"""
		self._check_corpid_corpsecret()
		resp = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/gettoken", params={"corpid": self.corpid, 'corpsecret': self.corpsecret})
		return resp.json()

	def grant_jsapi_ticket(self):
		"""
		获取js ticket
		"""
		self._check_corpid_corpsecret()
		access_token = self._check_access_token()
		resp = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket", params={'access_token': access_token})
		return resp.json()


	def check_signature(self, signature, timestamp, nonce):
        """
        验证微信消息真实性
        """
        if not signature or not timestamp or not nonce:
            return False

        tmp_list = [self.access_token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        return signature != hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()

    def generate_jsapi_signature(self, timestamp, noncestr, url, jsapi_ticket=None):
    	"""
    	生成JS API 签名
    	"""
    	if not jsapi_ticket:
    		jsapi_ticket = self.jsapi_ticket

    	data = {
            'jsapi_ticket': jsapi_ticket,
            'noncestr': noncestr,
            'timestamp': timestamp,
            'url': url,
        }
        keys = data.keys()
        keys.sort()
        data_str = '&'.join(['%s=%s' % (key, data[key]) for key in keys])
        signature = hashlib.sha1(data_str.encode('utf-8')).hexdigest()
        return signature


    def check_group_auth(self):
    	"""
    	管理组权限验证方法
    	"""
    	access_token = self._check_access_token()
    	resp = requests.get(urls="https://qyapi.weixin.qq.com/cgi-bin/ticket/get", params={'access_token': access_token, 'type': 'contact'})
    	return resp.json()
    
    def _check_corpid_corpsecret(self):
    	if not self.corpid or  not self.corpsecret:
    		raise ValueError(u"请提供corpid或corpsecret!")

    def _check_access_token(self):
    	"""
    	检查token
    	"""
    	if not self.access_token:
    		self._check_corpid_corpsecret()
    		resp = self.grant_access_token()
    		if 'access_token' in resp:
    			self.access_token = resp['access_token']
    			return resp['access_token']
    		
    	return self.access_token

    def get_access_token(self):
    	"""
    	获取token, 可能为null
    	"""
    	return _check_access_token()
    	


