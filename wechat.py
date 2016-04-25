# -*- coding: utf-8 -*-

import hashlib
import requests
import json
import cgi
from .lib.parser import XMLStore
from .tencent import OfficialWechat
from .exceptions import ParseError, DecryptError, EncryptError, NeedParseError
from .messages import UnknownMessage, MESSAGE_TYPES
from .reply import TextReply, ImageReply, VoiceReply, VideoReply, MusicReply, Article, ArticleReply
from .send import TextSend, ImageSend, VoiceSend, VideoSend, FileSend, Article as Article2, ArticleSend


class WechatEnterprise(OfficialWechat):
    """
    微信企业号基础类
    仅支持企业号， 公司剧情需要，抽出来作为基础类
    该工具参考wechat-python-sdk
    """

    def __init__(self, *args, **kwargs):
        super(WechatEnterprise, self).__init__(*args, **kwargs)
        self.__is_parse = False
        self.__content = None

    def grant_access_token(self):
        """
        获取token , 暂时不做失败处理
        """
        self._check_corpid_corpsecret()
        return requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/gettoken",
                            params={"corpid": self.corpid, 'corpsecret': self.corpsecret}).json()

    def get_user_info(self, code):
        """
        根据code 获取用户资料
        """
        access_token = self._check_access_token()
        return requests.get(
            url='https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={}&code={}'.format(access_token,
                                                                                                      code)).json()


    def grant_jsapi_ticket(self):
        """
        获取js ticket
        """
        self._check_corpid_corpsecret()
        access_token = self._check_access_token()
        return requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket",
                            params={'access_token': access_token}).json()

    def parse_data(self, data=None, msg_signature=None, timestamp=None, nonce=None):
        """
        解析微信服务器发送过来的数据并保存类中
        :param data: HTTP Request 的 Body 数据
        :param msg_signature: EncodingAESKey 的 msg_signature
        :param timestamp: EncodingAESKey 用时间戳
        :param nonce: EncodingAESKey 用随机数
        :raises ParseError: 解析微信服务器数据错误, 数据不合法
        """
        if type(data) not in [str, unicode]:
            raise ParseError()
        data = data.encode('utf-8')
        ok, data = self.decrypt_message(data, msg_signature, timestamp, nonce)
        if not ok:
            raise DecryptError()
        try:
            xml = XMLStore(xmlstring=data)
        except Exception:
            raise ParseError()
        result = xml.xml2dict
        result['raw'] = data
        result['type'] = result.pop('MsgType').lower()
        message_type = MESSAGE_TYPES.get(result['type'], UnknownMessage)
        self.__content = {
            'message': message_type(result),
            'msg_signature': msg_signature,
            'timestamp': timestamp,
            'nonce': nonce,
        }
        self.__is_parse = True

    @property
    def message(self):
        self._check_parse()
        return self.__content['message']

    def _check_parse(self):
        """
        检查是否成功解析微信服务器传来的数据
        :raises NeedParseError: 需要解析微信服务器传来的数据
        """
        if not self.__is_parse:
            raise NeedParseError()

    def _encrypt_response(self, response):
        response = response.encode('utf-8')
        ok, encrypt_msg = self.encrypt_message(response, self.__content['nonce'], self.__content['timestamp'])
        if not ok:
            raise EncryptError()
        return encrypt_msg

    def response_text(self, content, escape=False):
        """
        将文字信息 content 组装为符合微信服务器要求的响应数据
        :param content: 回复文字
        :param escape: 是否转义该文本内容 (默认不转义)
        :return: 符合微信服务器要求的 XML 响应数据
        """
        self._check_parse()
        content = self._transcoding(content)
        if escape:
            content = cgi.escape(content)

        response = TextReply(message=self.__content['message'], content=content).render()
        return self._encrypt_response(response)

    def response_image(self, media_id):
        """
        将 media_id 所代表的图片组装为符合微信服务器要求的响应数据
        :param media_id: 图片的 MediaID
        :return: 符合微信服务器要求的 XML 响应数据
        """
        self._check_parse()

        response = ImageReply(message=self.__content['message'], media_id=media_id).render()
        return self._encrypt_response(response)

    def response_voice(self, media_id):
        """
        将 media_id 所代表的语音组装为符合微信服务器要求的响应数据
        :param media_id: 语音的 MediaID
        :return: 符合微信服务器要求的 XML 响应数据
        """
        self._check_parse()

        response = VoiceReply(message=self.__content['message'], media_id=media_id).render()
        return self._encrypt_response(response)

    def response_video(self, media_id, title=None, description=None):
        """
        将 media_id 所代表的视频组装为符合微信服务器要求的响应数据
        :param media_id: 视频的 MediaID
        :param title: 视频消息的标题
        :param description: 视频消息的描述
        :return: 符合微信服务器要求的 XML 响应数据
        """
        self._check_parse()
        title = self._transcoding(title)
        description = self._transcoding(description)

        response = VideoReply(message=self.__content['message'], media_id=media_id, title=title,
                              description=description).render()
        return self._encrypt_response(response)

    def response_music(self, music_url, title=None, description=None, hq_music_url=None, thumb_media_id=None):
        """
        将音乐信息组装为符合微信服务器要求的响应数据
        :param music_url: 音乐链接
        :param title: 音乐标题
        :param description: 音乐描述
        :param hq_music_url: 高质量音乐链接, WIFI环境优先使用该链接播放音乐
        :param thumb_media_id: 缩略图的 MediaID
        :return: 符合微信服务器要求的 XML 响应数据
        """
        self._check_parse()
        music_url = self._transcoding(music_url)
        title = self._transcoding(title)
        description = self._transcoding(description)
        hq_music_url = self._transcoding(hq_music_url)

        response = MusicReply(message=self.__content['message'], title=title, description=description,
                              music_url=music_url,
                              hq_music_url=hq_music_url, thumb_media_id=thumb_media_id).render()
        return self._encrypt_response(response)

    def response_news(self, articles):
        """
        将新闻信息组装为符合微信服务器要求的响应数据
        :param articles: list 对象, 每个元素为一个 dict 对象, key 包含 `title`, `description`, `picurl`, `url`
        :return: 符合微信服务器要求的 XML 响应数据
        """
        self._check_parse()
        for article in articles:
            if article.get('title'):
                article['title'] = self._transcoding(article['title'])
            if article.get('description'):
                article['description'] = self._transcoding(article['description'])
            if article.get('picurl'):
                article['picurl'] = self._transcoding(article['picurl'])
            if article.get('url'):
                article['url'] = self._transcoding(article['url'])

        news = ArticleReply(message=self.__content['message'])
        for article in articles:
            article = Article(**article)
            news.add_article(article)
        response = news.render()
        return self._encrypt_response(response)

    def _post_message(self, data):
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/message/send', data)


    def send_text(self, content, escape=False, **kwargs):
        """
        将文字信息 content 组装为符合微信服务器要求的响应数据
        :param content: 回复文字
        :param escape: 是否转义该文本内容 (默认不转义)
        :param agent_id: 企业应用的id，整型
        :param to_all: 是否发送给所有人
        :param to_user: 成员ID列表，最多支持1000个
        :param to_party:    部门ID列表，最多支持100个
        :param to_tag: 标签ID列表
        :param safe: 是否加密
        """
        content = self._transcoding(content)
        if escape:
            content = cgi.escape(content)

        data = TextSend(**kwargs).apply(content=content)
        return self._post_message(data)

    def send_image(self, media_id, **kwargs):
        """
        将 media_id 所代表的图片组装为符合微信服务器要求的响应数据
        :param media_id: 图片的 MediaID
        :param agent_id: 企业应用的id，整型
        :param to_all: 是否发送给所有人
        :param to_user: 成员ID列表，最多支持1000个
        :param to_party:    部门ID列表，最多支持100个
        :param to_tag: 标签ID列表
        :param safe: 是否加密
        """
        data = ImageSend(**kwargs).apply(media_id=media_id)
        return self._post_message(data)

    def send_voice(self, media_id, **kwargs):
        """
        将 media_id 所代表的语音组装为符合微信服务器要求的响应数据
        :param media_id: 语音的 MediaID
        :param agent_id: 企业应用的id，整型
        :param to_all: 是否发送给所有人
        :param to_user: 成员ID列表，最多支持1000个
        :param to_party:    部门ID列表，最多支持100个
        :param to_tag: 标签ID列表
        :param safe: 是否加密
        """
        data = VoiceSend(**kwargs).apply(media_id=media_id)
        return self._post_message(data)

    def send_video(self, media_id, title=None, description=None, **kwargs):
        """
        将 media_id 所代表的视频组装为符合微信服务器要求的响应数据
        :param media_id: 视频的 MediaID
        :param title: 视频消息的标题
        :param description: 视频消息的描述
        :param agent_id: 企业应用的id，整型
        :param to_all: 是否发送给所有人
        :param to_user: 成员ID列表，最多支持1000个
        :param to_party:    部门ID列表，最多支持100个
        :param to_tag: 标签ID列表
        :param safe: 是否加密
        """
        title = self._transcoding(title)
        description = self._transcoding(description)

        data = VideoSend(**kwargs).apply(media_id=media_id, title=title, description=description)
        return self._post_message(data)

    def send_file(self, media_id, **kwargs):
        """
        将文件信息组装为符合微信服务器要求的响应数据
        :param media_id: 语音的 MediaID
        :param agent_id: 企业应用的id，整型
        :param to_all: 是否发送给所有人
        :param to_user: 成员ID列表，最多支持1000个
        :param to_party:    部门ID列表，最多支持100个
        :param to_tag: 标签ID列表
        :param safe: 是否加密
        """
        data = FileSend(**kwargs).apply(media_id=media_id)
        return self._post_message(data)

    def send_news(self, articles, **kwargs):
        """
        将新闻信息组装为符合微信服务器要求的响应数据
        :param articles: list 对象, 每个元素为一个 dict 对象, key 包含 `title`, `description`, `picurl`, `url`
        :param agent_id: 企业应用的id，整型
        :param to_all: 是否发送给所有人
        :param to_user: 成员ID列表，最多支持1000个
        :param to_party:    部门ID列表，最多支持100个
        :param to_tag: 标签ID列表
        :param safe: 是否加密
        """
        self._check_parse()
        for article in articles:
            if article.get('title'):
                article['title'] = self._transcoding(article['title'])
            if article.get('description'):
                article['description'] = self._transcoding(article['description'])
            if article.get('picurl'):
                article['picurl'] = self._transcoding(article['picurl'])
            if article.get('url'):
                article['url'] = self._transcoding(article['url'])

        news = ArticleSend(**kwargs)
        for article in articles:
            article = Article2(**article)
            news.add_article(article)
        data = news.apply()
        return self._post_message(data)

    def create_menu(self, menu_data, agent_id):
        """
        详情参考 http://qydev.weixin.qq.com/wiki/index.php?title=%E5%88%9B%E5%BB%BA%E5%BA%94%E7%94%A8%E8%8F%9C%E5%8D%95
        :param menu_data: Python 字典
        :param agent_id: 企业应用的id，整型
        :return: 返回的 JSON 数据包
        """
        return requests.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/menu/create?access_token={}&agentid={}'.format(self.access_token,
                                                                                                    agent_id),
            data=json.dumps(menu_data).decode('unicode-escape').encode("utf-8")).json()

    def get_menu(self, agent_id):
        """
        查询自定义菜单
        详情参考 http://qydev.weixin.qq.com/wiki/index.php?title=%E8%8E%B7%E5%8F%96%E8%8F%9C%E5%8D%95%E5%88%97%E8%A1%A8
        :param agent_id: 企业应用的id，整型
        :return: 返回的 JSON 数据包
        """
        return requests.get(
            'https://qyapi.weixin.qq.com/cgi-bin/menu/get?access_token={}&agentid={}'.format(self.access_token,
                                                                                             agent_id)).json()

    def delete_menu(self, agent_id):
        """
        删除自定义菜单
        详情参考 http://qydev.weixin.qq.com/wiki/index.php?title=%E5%88%A0%E9%99%A4%E8%8F%9C%E5%8D%95
        :param agent_id: 企业应用的id，整型
        :return: 返回的 JSON 数据包
        """
        return requests.get(
            'https://qyapi.weixin.qq.com/cgi-bin/menu/delete?access_token={}&agentid={}'.format(self.access_token,
                                                                                                agent_id)).json()

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
        return requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/ticket/get",
                            params={'access_token': access_token, 'type': 'contact'}).json()

    def _post(self, url, kwargs):
        """上传处理"""
        access_token = self._check_access_token()

        _url = "{}?access_token={}".format(url, access_token)
        resp = requests.post(url=_url, data=json.dumps(kwargs).decode('unicode-escape').encode("utf-8"))
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


    def auth_succ(self, user_id):
        """
        成员关注企业号，二次验证
        """
        access_token = self._check_access_token()
        return requests.get(url="https://qyapi.weixin.qq.com/cgi-bin/user/authsucc",
                            params={'access_token': access_token, 'userid': user_id}).json()


    def create_department(self, **kwargs):
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
        return self._post("https://qyapi.weixin.qq.com/cgi-bin/department/create", kwargs)


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
        return self._post("https://qyapi.weixin.qq.com/cgi-bin/department/update", kwargs)


    def delete_department(self, _id):
        """
        删除部门
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/department/delete',
                            params={'access_token': access_token, 'id': _id}).json()


    def get_departments(self, _id):
        """
        获取部门列表
        params: _id 获取指定部门及其下的子部门
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/department/list',
                            params={'access_token': access_token}).json()

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
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/user/create', kwargs)


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
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/user/update', kwargs)


    def delete_user(self, user_id):
        """
        删除成员
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/user/delete',
                            params={'access_token': access_token, 'userid': user_id}).json()


    def delete_users(self, user_ids):
        """
        删除多个成员
        user_ids = ['a', 'b']
        """
        access_token = self._check_access_token()
        return requests.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/user/batchdelete?access_token={}'.format(access_token),
            json={'useridlist': user_ids}).json()


    def get_user(self, user_id):
        """
        获取成员
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/user/get',
                            params={'access_token': access_token, 'userid': user_id}).json()


    def get_simple_user(self, **kwargs):
        """
        获取部门成员
        department_id 部门ID
        fetch_child 1/0：是否递归获取子部门下面的成员， 如果不需要就不要传
        status 0获取全部成员，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加，未填写则默认为4
        """
        access_token = self._check_access_token()
        return requests.get(
            url='https://qyapi.weixin.qq.com/cgi-bin/user/simplelist?access_token={}'.format(access_token),
            params=kwargs).json()


    def get_user_list(self, **kwargs):
        """
        department_id 部门ID
        fetch_child 1/0：是否递归获取子部门下面的成员， 如果不需要就不要传
        status 0获取全部成员，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加，未填写则默认为4
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={}'.format(access_token),
                            data=kwargs).json()


    def invite_user(self, user_id):
        """
        邀请成员关注
        ---
        该方法已过期，微信不支持发送邀请信息
        """
        # data = {'userid': user_id}
        # return self._post('https://qyapi.weixin.qq.com/cgi-bin/invite/send', data)
        pass


    def create_tag(self, **kwargs):
        """
        创建标签
        {
           "tagname": "UI",
           "tagid": id
        }
        """
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/tag/create', kwargs)


    def update_tag(self, **kwargs):
        """
        更新标签
        {
           "tagname": "UI",
           "tagid": id
        }
        """
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/tag/update', kwargs)


    def delete_tag(self, tag_id):
        """
        删除标签
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/tag/delete',
                            params={'access_token': access_token, 'tagid': tag_id}).json()

    def get_tag(self, tag_id):
        """
        获取标签
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/tag/get',
                            params={'access_token': access_token, 'tagid': tag_id}).json()


    def add_tag_users(self, **kwargs):
        """
        增加标签成员
        {
           "tagid": "1",
           "userlist":[ "user1","user2"],
           "partylist": [4]
        }
        """
        return self._post("https://qyapi.weixin.qq.com/cgi-bin/tag/addtagusers", kwargs)


    def delete_tag_users(self, **kwargs):
        """
        删除标签成员
        {
           "tagid": "1",
           "userlist":[ "user1","user2"],
           "partylist":[2,4]
        }
        """
        return self._post("https://qyapi.weixin.qq.com/cgi-bin/tag/deltagusers", kwargs)


    def get_tag_list(self):
        """
        获取标签列表
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/tag/list',
                            params={'access_token': access_token}).json


    def batch_invite_user(self, **kwargs):
        """
        异步接口
        邀请成员关注
        {
            "touser":"xxx|xxx",
            "toparty":"xxx|xxx",
            "totag":"xxx|xxx",
            "callback":
            {
                "url": "xxx",
                "token": "xxx",
                "encodingaeskey": "xxx"
            }
        }
        """
        return self._post("https://qyapi.weixin.qq.com/cgi-bin/batch/inviteuser", kwargs)


    def batch_sync_user(self, **kwargs):
        """
        增量更新成员
        refer: http://qydev.weixin.qq.com/wiki/index.php?title=%E5%BC%82%E6%AD%A5%E4%BB%BB%E5%8A%A1%E6%8E%A5%E5%8F%A3
        {
            "media_id":"xxxxxx",
            "callback":
            {
                "url": "xxx",
                "token": "xxx",
                "encodingaeskey": "xxx"
            }
        }
        """
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/batch/syncuser', kwargs)


    def batch_replace_user(self, **kwargs):
        """
        全量覆盖成员
        {
            "media_id":"xxxxxx",
            "callback":
            {
                "url": "xxx",
                "token": "xxx",
                "encodingaeskey": "xxx"
            }
        }
        """
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/batch/replaceuser', kwargs)


    def batch_replace_party(self, **kwargs):
        """
        全量覆盖部门
        {
            "media_id":"xxxxxx",
            "callback":
            {
                "url": "xxx",
                "token": "xxx",
                "encodingaeskey": "xxx"
            }
        }
        """
        return self._post("https://qyapi.weixin.qq.com/cgi-bin/batch/replaceparty", kwargs)


    def get_batch_result(self, job_id):
        """
        获取异步任务结果
        返回结果根据 type 而定义
        refer: http://qydev.weixin.qq.com/wiki/index.php?title=%E5%BC%82%E6%AD%A5%E4%BB%BB%E5%8A%A1%E6%8E%A5%E5%8F%A3
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/batch/getresult',
                            params={'access_token': access_token, 'jobid': job_id}).json()


    def convert_2_open_id(self, **kwargs):
        """
        user id 转换 open id
        {
           "userid": "zhangsan",
           "agentid": 1
        }
        """
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_openid', kwargs)


    def convert_2_user_id(self, open_id):
        """
        open id 转换 user id 
        """
        data = {'openid': open_id}
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_userid', data)


    def get_agent(self, agent_id):
        """
        获取企业号应用
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/agent/get',
                            params={'access_token': access_token, 'agentid': agent_id}).json()


    def set_agent(self, **kwargs):
        """
        设置企业号
        {
           "agentid": "5",
           "report_location_flag": "0",
           "logo_mediaid": "xxxxx",
           "name": "NAME",
           "description": "DESC",
           "redirect_domain": "xxxxxx",
           "isreportuser":0,
           "isreportenter":0,
           "home_url":"http://www.qq.com"
        }
        """
        return self._post('https://qyapi.weixin.qq.com/cgi-bin/agent/set', kwargs)

    def get_agent_list(self):
        """
        获取应用概况列表
        """
        access_token = self._check_access_token()
        return requests.get(url='https://qyapi.weixin.qq.com/cgi-bin/agent/list', params={'access_token': access_token})
