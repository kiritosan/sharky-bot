from email import header
import os
from sqlite3 import paramstyle
from nonebot import get_driver

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

from nonebot.plugin import on_keyword
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message
import requests

backend_url: str = os.getenv('URL', 'http://localhost:8000')
bots_url: str = backend_url + '/bots/'

def get_urls(event) ->list [str]:
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

    params = {
        'urls': urls
    }
    try:
        response = requests.get(bots_url, headers=headers)
    except requests.exceptions.ConnectionError as e:
        print(e)
        print('------connection error------')
        return None

    # error catch
    if response.status_code != 200:
        print('------status code is not 200------')
        return None

    res = response.json()
    print(res)
    return res

predict = on_keyword({'predict','预测', '检测'}, priority=50)
@predict.handle()
async def predict_handle(bot: Bot, event: Event):
    urls = get_urls(event)
    res = push_to_backend(urls)
    print(res)
    if res is not None:
        await predict.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您方才发送图片的人头预测数值为{res["predict_number"]}'))