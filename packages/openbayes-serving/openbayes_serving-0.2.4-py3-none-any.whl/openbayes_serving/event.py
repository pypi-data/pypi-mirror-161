# -*- coding: utf-8 -*-

# -- stdlib --
import json
import logging

# -- third party --
from flask import request
import msgpack
import requests

# -- own --
from .common import detect_env


# -- code --
log = logging.getLogger('openbayes_serving.event')


def _strip_bytes(data):
    if isinstance(data, bytes):
        return '[二进制数据]'

    if isinstance(data, (tuple, list)):
        return [_strip_bytes(i) for i in data]

    if isinstance(data, dict):
        return {k: _strip_bytes(v) for k, v in data.items()}

    return data


def get_request_id():
    try:
        return int(request.headers['X-Openbayes-Serving-Request-Id'])
    except Exception:
        return 0


def emit_event(name, data, id: int=None):
    # Enconding should happen before logging,
    # to make it crash in development environments
    if isinstance(data, bytes):
        encoded = data
    elif isinstance(data, str):
        encoded = data.encode('utf-8')
    elif isinstance(data, (int, float)):
        encoded = str(data)
    else:
        encoded = json.dumps(data).encode('utf-8')

    if detect_env() != 'production':
        data = _strip_bytes(data)
        log.info('记录事件：%s -> %s', name, data)
        return

    req_id = id if id is not None else get_request_id()
    if req_id == 0:
        log.error("无法获取 Request Id，不会记录当前事件。")
        return

    try:
        requests.post('http://127.0.0.1:6666/events',
            headers={'Content-Type': 'application/msgpack'},
            data=msgpack.packb({'id': req_id, 'name': name, 'data': encoded})),
    except Exception as e:
        log.error('记录事件失败： %s', e)
        return
