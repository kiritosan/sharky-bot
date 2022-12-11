import requests
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.plugin import on_keyword
from email import header
import os
from sqlite3 import paramstyle
from nonebot import get_driver
from requests import Response

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)


backend_url: str = os.getenv('URL', 'http://localhost:8000')
bots_url: str = backend_url + '/bots/'


def get_urls(event) -> list[str]:
    urls = []
    messages = event.get_message()
    for message in messages:
        if message.type == 'image':
            urls.append(message.data['url'])
    return urls


def push_to_backend(urls: list[str]):
    headers: dict[str, str] = {
        'accept': 'application/json',
    }
    params: dict[str, list[str]] = {
        'urls': urls
    }
    try:
        response: Response = requests.get(
            bots_url, params=params, headers=headers)
    except requests.exceptions.ConnectionError as e:
        print(e)
        print('------connection error------')
        return {'message': "can't connect to backend(/bots)"}
    return response


predict = on_keyword({'predict', '预测', '检测'}, priority=50)


@predict.handle()
async def predict_handle(bot: Bot, event: Event):
    urls: list[str] = get_urls(event)
    response: dict[str, str] | Response = push_to_backend(urls)

    if isinstance(response, dict):
        if response['message'] == "can't connect to backend(/bots)":
            await predict.finish(Message(f'[CQ:at,qq={event.get_user_id()}]无法连接到后端(/bots)'))
    else:
        res = response.json()
        predict_digits: list[int] = res["predict_digits"]
        processed_urls: list[str] = res["processed_urls"]
        image = MessageSegment.image(processed_urls[0])

        if response.status_code == 200 and 'message' not in response.json():
            await predict.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您方才发送图片的人头预测数值为{predict_digits}\n{image}'))
        elif response.status_code == 200 and res['message'] == 'the engine download pictures failed':
            await predict.finish(Message(f'[CQ:at,qq={event.get_user_id()}]引擎下载图片失败'))
        elif response.status_code == 200 and res['message'] == 'the engine predict failed':
            await predict.finish(Message(f'[CQ:at,qq={event.get_user_id()}]引擎预测失败'))
        elif response.status_code == 200 and res['message'] == 'the engine download pictures failed because the url is wrong':
            await predict.finish(Message(f'[CQ:at,qq={event.get_user_id()}]由于url不存在，图片下载失败'))
        elif response.status_code == 200 and res['message'] == 'the engine failed to upload processed file':
            await predict.finish(Message(f'[CQ:at,qq={event.get_user_id()}]引擎上传处理后的图片失败'))
