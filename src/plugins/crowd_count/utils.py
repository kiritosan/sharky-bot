import os
import requests
from requests import Response

backend_url: str = os.getenv('BACKEND_URL', 'http://localhost:8000')
bots_url: str = backend_url + '/bots'


def get_urls(event) -> list[str]:
    urls: list[str] = []
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
        return {'message': "can't connect to backend"}
    return response
