# -*- coding: utf-8 -*-


class WechatSend(object):
    message_type = ""

    def __init__(self, agent_id, to_all=False, to_user=[], to_party=[], to_tag=[], safe=False):
        self.data = {
           "msgtype": self.message_type,
           "agentid": agent_id,
           self.message_type: {
           },
           "safe": "1" if safe else "0"
        }
        if to_all:
            self.data.update({
                "touser": "@all",
            })
        else:
            if len(to_user) > 1000:
                raise AttributeError("Can't send to more than 1000 users.")
            elif len(to_party) > 100:
                raise AttributeError("Can't send to more than 100 parties.")
            users = "|".join(to_user)
            parties = "|".join(to_party)
            tags = "|".join(to_tag)
            self.data.update({
                "touser": users,
                "toparty": parties,
                "totag": tags,
            })

    def apply(self, **kwargs):
        raise NotImplementedError()


class TextSend(WechatSend):
    """
    发送文字消息
    """
    message_type = "text"

    def apply(self, content):
        self.data[self.message_type] = {
            "content": content
        }
        return self.data


class ImageSend(WechatSend):
    """
    发送图片消息
    """
    message_type = "image"

    def apply(self, media_id):
        self.data[self.message_type] = {
            "media_id": media_id
        }
        return self.data


class VoiceSend(ImageSend):
    """
    发送声音消息
    """
    message_type = "voice"


class VideoSend(WechatSend):
    """
    发送视频消息
    """
    message_type = "video"

    def apply(self, media_id, title, description):
        self.data[self.message_type] = {
           "media_id": media_id,
           "title": title,
           "description": description,
        }
        return self.data


class FileSend(ImageSend):
    """
    发送文件消息
    """
    message_type = "file"


class Article(object):
    def __init__(self, title=None, description=None, picurl=None, url=None):
        self.title = title or ''
        self.description = description or ''
        self.picurl = picurl or ''
        self.url = url or ''

    @property
    def data(self):
        return dict(
            title=self.title,
            description=self.description,
            picurl=self.picurl,
            url=self.url,
        )


class ArticleSend(WechatSend):
    """
    发送news消息
    """
    message_type = "news"

    def apply(self, media_id, title, description):
        self.data[self.message_type] = {
           "media_id": media_id,
           "title": title,
           "description": description,
        }
        return self.data

    def __init__(self, *args, **kwargs):
        super(ArticleSend, self).__init__(*args, **kwargs)
        self._articles = []

    def add_article(self, article):
        if len(self._articles) >= 10:
            raise AttributeError("Can't add more than 10 articles in an ArticleReply")
        else:
            self._articles.append(article)

    def apply(self):
        items = []
        for article in self._articles:
            items.append(article.data)
        self.data[self.message_type] = {
           "articles": items,
        }
        return self.data



