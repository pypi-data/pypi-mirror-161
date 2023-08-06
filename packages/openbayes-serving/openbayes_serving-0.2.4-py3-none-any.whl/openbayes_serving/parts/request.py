# -*- coding: utf-8 -*-

# -- stdlib --
import json
import re

# -- third party --
from flask import request
import msgpack

# -- own --
from ..common import ServingError


# -- code --
def parse_type(tp):
    if not tp or tp == '*/*':
        return 'octet-stream'

    m = re.match(r'^application/([a-z0-9\.\-]+)', tp)
    if not m:
        return 'octet-stream'

    enc, *_ = m.groups()

    COALESCE = {
        'octet-stream':    'octet-stream',
        'msgpack':         'msgpack',
        'x-msgpack':       'msgpack',
        'vnd.msgpack':     'msgpack',
        'vnd.messagepack': 'msgpack',
        'json':            'json',
    }

    return COALESCE.get(enc, 'octet-stream')



def get_payload():
    tp = parse_type(request.mimetype)

    if not tp:
        raise ServingError("无效的 Content-Type", 415)

    if tp == 'msgpack':
        try:
            payload = msgpack.unpackb(request.get_data(), raw=False)
        except Exception as e:
            raise ServingError("无法解析输入的 MessagePack 消息", 400) from e
    elif tp == 'json':
        try:
            payload = json.loads(request.get_data())
        except Exception as e:
            raise ServingError("无法解析输入的 JSON 消息", 400) from e
    elif tp == 'octet-stream':
        payload = request.get_data()
    else:
        raise Exception(f'BUG: unknown mime type {tp}')

    return tp, payload


def get_json():
    tp, payload = get_payload()
    if tp not in ('msgpack', 'json'):
        raise ServingError('输入必须是 JSON 或者 MessagePack 格式')

    return payload


class SimpleArgHandler:
    def __init__(self, tag, func):
        self.tag = tag
        self.func = func

    def is_interested(self, tag):
        return tag == self.tag

    def resolve(self, tag):
        tag
        return self.func()



PREDICT_ARG_HANDLERS = [
    SimpleArgHandler('data', lambda: request.data),
    SimpleArgHandler('json', get_json),
    SimpleArgHandler('payload', lambda: get_payload()[1]),
    SimpleArgHandler('params', lambda: request.args),
    SimpleArgHandler('args', lambda: request.args),
    SimpleArgHandler('headers', lambda: request.headers),
    SimpleArgHandler('request', lambda: request),
]
