#! /usr/bin/env python3.8
import os
import logging
import requests
import json
import logging
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

logging.basicConfig(level=logging.INFO #设置日志输出格式
                    ,filename="request.txt" #log日志输出的文件位置和文件名
                    # ,filemode="w" #文件的写入格式，w为重新写入文件，默认是追加
                    ,format="%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s" #日志输出的格式
                    # -8表示占位符，让输出左对齐，输出长度都为8位
                    ,datefmt="%Y-%m-%d %H:%M:%S" #时间输出的格式
                    )
# const
TENANT_ACCESS_TOKEN_URI = "/open-apis/auth/v3/tenant_access_token/internal"
MESSAGE_URI = "/open-apis/im/v1/messages"


class MessageApiClient(object):
    def __init__(self, app_id, app_secret, lark_host):
        self._app_id = app_id
        self._app_secret = app_secret
        self._lark_host = lark_host
        self._tenant_access_token = ""

    @property
    def tenant_access_token(self):
        return self._tenant_access_token


    '''
    通过调用send函数，实现接收消息之后立即回复的功能
    '''
    def send_text_with_open_id(self, open_id, content):
        self.send("open_id", open_id, "text", content)

    def send(self, receive_id_type, receive_id, msg_type, content):
        # send message to user, implemented based on Feishu open api capability.(发送消息给用户，基于飞书开放API能力实现)。 doc link: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        self._authorize_tenant_access_token()
        url = "{}{}?receive_id_type={}".format(
            self._lark_host, MESSAGE_URI, receive_id_type
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }

        req_body = {
            "receive_id": receive_id,
            "content": content,
            "msg_type": msg_type,
        }

        #捕获请求的内容，根据内容进行逻辑处理
        content_dict = json.loads(content)   #得到'content':'{"text":"/text/"}', key:value,value是json格式
        if content_dict['text'] in "獬豸，xiezhi":
            req_body = {
                "receive_id": receive_id,
                "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAqPfI0dRirg\"} }",
                "msg_type": "interactive"
            }
        elif content_dict['text'] in "基线测试看板":
            req_body = {
                "receive_id": receive_id,
                "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmwSW3qsg6D\"} }",
                "msg_type": "interactive"
            }
        elif content_dict['text'] in "整车自动化新人入职指南教程":
            req_body = {
                "receive_id": receive_id,
                "content": "{\"type\": \"template\", \"data\": { \"template_id\": \"ctp_AAmc5sXrV7TL\"} }",
                "msg_type": "interactive"
            }
        # else:
        #     req_body = {
        #         "receive_id": receive_id,
        #         "content": "我是整车自动化测试智能助手，如有需要，请回复以下关键字",
        #         "msg_type": msg_type,
        #     }
        resp = requests.post(url=url, headers=headers, json=req_body)

        #加入日志
        logging.info(resp.json())
        logging.info(req_body)
        print(resp.json())

        MessageApiClient._check_error_response(resp)

    def _authorize_tenant_access_token(self):
        # get tenant_access_token and set, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal

        url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
        print("机器人恢复消息的接口", url)
        req_body = {"app_id": self._app_id, "app_secret": self._app_secret}

        response = requests.post(url, req_body)
        MessageApiClient._check_error_response(response)
        self._tenant_access_token = response.json().get("tenant_access_token")

    @staticmethod
    def _check_error_response(resp):
        # check if the response contains error information
        if resp.status_code != 200:
            resp.raise_for_status()
        response_dict = resp.json()
        code = response_dict.get("code", -1)
        if code != 0:
            logging.error(response_dict)
            raise LarkException(code=code, msg=response_dict.get("msg"))

class LarkException(Exception):
    def __init__(self, code=0, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return "{}:{}".format(self.code, self.msg)

    __repr__ = __str__
