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

    def __init__(self, token=None, corpid=None, corpsecret=None, access_token=None, access_token_expires_at=None,
                 jsapi_ticket=None):
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
        resp = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/gettoken",
                            params={"corpid": self.corpid, 'corpsecret': self.corpsecret})
        return resp.json()

    def grant_jsapi_ticket(self):
        """
        获取js ticket
        """
        self._check_corpid_corpsecret()
        access_token = self._check_access_token()
        resp = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket",
                            params={'access_token': access_token})
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
        resp = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/ticket/get",
                            params={'access_token': access_token, 'type': 'contact'})
        return resp.json()


    def _check_corpid_corpsecret(self):
        if not self.corpid or not self.corpsecret:
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
        return self._check_access_token()


    def check_member_follow(self, user_id):
        """
        成员关注企业号，二次验证
        """
        access_token = self._check_access_token()
        resp = requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/user/authsucc",
                            params={'access_token': access_token, 'userid': user_id})
        return resp.json()


    def _post_department(self, **kwargs):
        access_token = self._check_access_token()
        resp = requests.post(
            url="https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token={}".format(access_token), **kwargs)
        return resp


    def create_deparment(self, **kwargs):
        """
        创建部门
        {
           "name": "广州研发中心",
           "parentid": "1",
           "order": "1",
           "id": "1"
        }
        return :
        {
           "errcode": 0,
           "errmsg": "created",
           "id": 2
        }
        """
        return self._post_deparment(**kwargs)


    def update_department(self, **kwargs):
        """
        更新部门
        {
           "name": "广州研发中心",
           "parentid": "1",
           "order": "1",
           "id": "1"
        }
        return :
        {
           "errcode": 0,
           "errmsg": "update",
           "id": 2
        }
        """
        return self._post_deparment(**kwargs)


    def delete_department(self, _id):
        """
        删除部门
        """
        access_token = self._check_access_token()
        resp = requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/department/delete',
                            params={'access_token': access_token, 'id': _id})
        return resp.json()


    def get_departments(self, _id):
        """
        获取部门列表
        params: _id 获取指定部门及其下的子部门
        """
        access_token = self._check_access_token()
        resp = requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/department/list',
                            params={'access_token': access_token})
        return resp.json()


    def _post_user(self, **kwargs):
        access_token = self._check_access_token()
        resp = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/user/create?access_token={}'.format(access_token),
                             **kwargs)
        return resp.json()


    def create_user(self, **kwargs):
        """
        创建成员
        {
           "userid": "zhangsan",
           "name": "张三",
           "department": [1, 2],
           "position": "产品经理",
           "mobile": "15913215421",
           "gender": "1",
           "email": "zhangsan@gzdev.com",
           "weixinid": "zhangsan4dev",
           "avatar_mediaid": "2-G6nrLmr5EC3MNb_-zL1dDdzkd0p7cNliYu9V5w7o8K0",
           "extattr": {"attrs":[{"name":"爱好","value":"旅游"},{"name":"卡号","value":"1234567234"}]}
        }
        """
        return self._post_user()


    def update_user(self, **kwargs):
        """
        更新成员
        {
           "userid": "zhangsan",
           "name": "张三",
           "department": [1, 2],
           "position": "产品经理",
           "mobile": "15913215421",
           "gender": "1",
           "email": "zhangsan@gzdev.com",
           "weixinid": "zhangsan4dev",
           "avatar_mediaid": "2-G6nrLmr5EC3MNb_-zL1dDdzkd0p7cNliYu9V5w7o8K0",
           "extattr": {"attrs":[{"name":"爱好","value":"旅游"},{"name":"卡号","value":"1234567234"}]}
        }
        """
        return self._post_user()


    def delete_user(self, user_id):
        """
        删除成员
        """
        access_token = self._check_access_token()
        resp = requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/user/delete',
                            params={'access_token': access_token, 'userid': user_id})
        return resp.json()


    def delete_users(self, user_ids):
        """
        删除多个成员
        user_ids = ['a', 'b']
        """
        access_token = self._check_access_token()
        resp = requests.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/user/batchdelete?access_token={}'.format(access_token),
            params={'useridlist': user_ids})
        return resp.json()


    def get_user(self, user_id):
        """
        获取成员
        """
        access_token = self._check_access_token()
        resp = requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/user/get',
                            params={'access_token': access_token, 'userid': user_id})
        return resp.json()


    def get_simple_user(self, **kwargs):
        """
        获取部门成员
        department_id 部门ID
        fetch_child 1/0：是否递归获取子部门下面的成员， 如果不需要就不要传
        status 0获取全部成员，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加，未填写则默认为4
        """
        access_token = self._check_access_token()
        resp = requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/user/get', **kwargs)
        return resp.json()

