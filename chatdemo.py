#-*- coding: UTF-8 -*-
#!/usr/bin/env python


import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import datetime

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),

        ]
        settings = dict(
            debug = True,

            #定义cookie  的加密密钥
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            #模板 和静态文件的路径设置
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #防范 crsf 跨域攻击
            xsrf_cookies=True,
        )
        #调用原来的__init__ 方法吧 handlers 和 settings  加入Application 里面去
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache, clients=ChatSocketHandler.waiters, username= "游客%d" % ChatSocketHandler.client_id)
#tornado的websocket.WebSocketHandler  处理websocket 服务设置
class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    #保存所有在线的 websocket 连接
    waiters = set()
    #所有用户聊天记录  缓存
    cache = []
    #最大缓存上限
    cache_size = 200
    #默认的用户id
    client_id = 0


    #每一个websocket 在开始的时候都会运行这个open（）函数
    def open(self):
        #获取类属性
        self.client_id = ChatSocketHandler.client_id
        ChatSocketHandler.client_id = ChatSocketHandler.client_id + 1
        self.username = "游客%d" % self.client_id
        #添加一个 新建的websocket 连接
        ChatSocketHandler.waiters.add(self)
        #获取需要的基本信息
        chat = {
            "id": str(uuid.uuid4()),
            "type": "online",
            "client_id": self.client_id,
            "username": self.username,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        #将这些登录连接 信息发送给没一个在 waiters 里的websocket 连接
        ChatSocketHandler.send_updates(chat)
#在关闭连接的时候使用
    def on_close(self):
        ChatSocketHandler.waiters.remove(self)
        chat = {
            "id": str(uuid.uuid4()),
            "type": "offline",
            "client_id": self.client_id,
            "username": self.username,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ChatSocketHandler.send_updates(chat)

#处理缓存超过 上限的情况
    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)
#接受来自客户端的消息
    def on_message(self, message):
        logging.info("got message %r", message)
        #使用 tornado.escape 转译操作对 客户端的 json 转译成 python dict
        parsed = tornado.escape.json_decode(message)
        print 'json_decode----',parsed
        self.username = parsed["username"]
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            "type": "message",
            "client_id": self.client_id, 
            "username": self.username,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))
        print 'chat--------',chat
        ChatSocketHandler.update_cache(chat)
        ChatSocketHandler.send_updates(chat)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
