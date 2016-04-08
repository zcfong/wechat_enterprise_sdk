#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'justinfong'

from wechat_enterprise_sdk.wechat import *
import unittest


class TestCase(unittest.TestCase):
    def setUp(self):
        self.wechat = WechatEnterprise(token='token', corpid='appid',
                                       corpsecret='secret', encoding_aes_key=None)

    def tearDown(self):
        pass

    def test_auth_succ(self):
        resp = self.wechat.auth_succ('justinfong')
        self.assertEqual(resp['errcode'], 0)

    def test_department(self):
        params = {'name': "部门一号", 'parentid': 1}
        resp = self.wechat.create_department(**params)
        self.assertEqual(resp['errcode'], 0)
        _id = resp['id']

        params.update({'id': _id})
        resp_update = self.wechat.update_department(**params)
        self.assertEqual(resp_update['errcode'], 0)

        resp_list = self.wechat.get_departments(1)
        self.assertEqual(resp_list['errcode'], 0)

        resp_del = self.wechat.delete_department(_id)
        self.assertEqual(resp_del['errcode'], 0)

    def test_user(self):
        _id = 'zhangsanseess'
        params = {'userid': _id, 'name': '张三', 'department': [1], 'mobile': '13800138000',
                  'gender': 1}
        params['email'] = ''
        params['weixinid'] = None
        params['avatar_mediaid'] = None

        resp = self.wechat.create_user(**params)
        self.assertEqual(resp['errcode'], 0)

        params['userid'] = 'zhangsanseess'
        resp = self.wechat.update_user(**params)
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.get_user(_id)
        self.assertEqual(resp['errcode'], 0)

        kw = {'department_id': 1, 'fetch_child': 0, 'status': 0}
        resp = self.wechat.get_simple_user(**kw)
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.get_user_list(**kw)
        self.assertEqual(resp['errcode'], 0)

        # resp = self.wechat.delete_user(_id)
        # self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.invite_user(_id)
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.delete_users([_id])
        self.assertEqual(resp['errcode'], 0)

    def test_tag(self):
        params = {'tagname': 'ui'}
        resp = self.wechat.create_tag(**params)
        self.assertEqual(resp['errcode'], 0)
        _id = resp['tagid']

        params['tagid'] = _id
        resp = self.wechat.update_tag(**params)
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.get_tag(_id)
        self.assertEqual(resp['errcode'], 0)

        params = {'tagid': _id, 'partylist': None, 'userlist': ['netboy']}
        resp = self.wechat.add_tag_users(**params)
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.delete_tag_users(**params)
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.get_tag_list()
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.delete_tag(_id)
        self.assertEqual(resp['errcode'], 0)

    def test_agent(self):
        params = {"agentid": "7", "report_location_flag": "0", "logo_mediaid": None, 'name': "ffffukkk",
                  'description': "desc", "redirect_domain": "http://www.baidu.com", "isreportuser": 0,
                  "isreportenter": 0, "home_url": "http://www.baidu.com"}

        resp = self.wechat.set_agent(**params)
        self.assertEqual(resp['errcode'], 0)

        resp = self.wechat.get_agent_list()
        self.assertEqual(resp['errcode'], 0)

    def test_batch_invite_user(self):
        params = {'touser': "justinfong", 'toparty': None, 'totag': None}
        resp = self.wechat.batch_invite_user(**params)
        self.assertEqual(resp['errcode'], 0)

    def test_menu_create(self):
        params = {}
        params["button"] = []
        menu = {"type": "view", "name": '搜索', 'url': 'http://www.baidu.com'}
        params["button"].append(menu)
        resp = self.wechat.create_menu(params, 0)
        self.assertEqual(resp['errcode'], 0)

    def test_menu_get(self):
        resp = self.wechat.get_menu(0)
        # 这里是返回菜单，没有对应的errorcode
        resp = self.wechat.delete_menu(0)
        self.assertEqual(resp['errcode'], 0)
