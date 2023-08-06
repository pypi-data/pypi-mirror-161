# -*- coding: utf-8 -*-

# -- stdlib --
from functools import partial
from urllib.parse import urlparse
import argparse
import base64
import inspect
import json
import logging
import os
import socket
import sys
import threading
import time

# -- third party --
from flask import Blueprint, Flask, Response, current_app, request
from flask_cors.decorator import cross_origin
from werkzeug.exceptions import HTTPException
import accept_types
import msgpack
import requests
import uvicorn

# -- own --
from . import debug
from .common import ServingError, detect_env
from .parts import INIT_ARG_HANDLERS, PREDICT_ARG_HANDLERS
from .utils.log import init as init_logging, patch_formatter as patch_log_formatter


# -- code --
log = logging.getLogger('openbayes_serving.serv')
predict_blueprint = Blueprint('openbayes-serv-predict', __name__)


ACCEPT_MIME_TYPES = [
    'application/json',
    'application/msgpack',
    'application/x-msgpack',
    'application/vnd.msgpack',
]


def bytes2base64(obj):
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, (list, tuple)):
        return [bytes2base64(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: bytes2base64(v) for k, v in obj.items()}
    else:
        return obj


def get_accept_type(v):
    if v:
        mime = accept_types.get_best_match(v, ACCEPT_MIME_TYPES)
        if mime is None:
            raise ServingError('无效的 Accept', 406)
        if 'msgpack' in mime:
            return 'msgpack'
        elif mime == 'application/json':
            return 'json'
        else:
            raise Exception('WTF')
    else:
        return 'json'


def post_process(rst):
    if isinstance(rst, (dict, list, tuple)):
        typ = get_accept_type(request.headers.get('Accept'))
        if typ == 'json':
            return Response(json.dumps(bytes2base64(rst)), mimetype='application/json')
        elif typ == 'msgpack':
            return Response(msgpack.packb(rst), mimetype='application/msgpack')
        else:
            raise Exception('WTF')
    elif isinstance(rst, bytes):
        mimetype = 'application/octet-stream'
        if rst.startswith(b'\x89PNG'):
            mimetype = 'image/png'
        elif rst.startswith(b'\xff\xd8\xff'):
            mimetype = 'image/jpeg'
        return Response(rst, mimetype=mimetype)
    elif isinstance(rst, str):
        return Response(rst.encode('utf-8'), mimetype='text/plain')
    elif callable(rst):
        return rst
    else:
        log.error('处理请求时返回了无效的结果：%s', rst)
        log.debug('有效的结果有 dict、list 对象，会被编码成 JSON 或者 MessagePack （取决于 Accept 头）；bytes、str 对象，会直接返回给客户端。')
        return Response('', status=500)


@predict_blueprint.route('', methods=['GET'], provide_automatic_options=False)
@cross_origin(supports_credentials=True)
def get_handler():
    return {'message': 'Serving 服务正常工作，可以发送 POST 请求到此地址进行推理。'}


@predict_blueprint.route('', methods=['POST'], provide_automatic_options=False)
@cross_origin(supports_credentials=True)
def post_handler():
    try:
        obj = current_app.config['OPENBAYES_SERVING_PREDICTOR_OBJECT']
        args = current_app.config['OPENBAYES_SERVING_PREDICT_ARGS']
        kwargs = {k: args[k]() for k in args}
        rst = obj.predict(**kwargs)
        return post_process(rst)
    except ServingError as e:
        response = Response(json.dumps(bytes2base64(e.payload)), mimetype='application/json')
        response.status_code = e.status_code
        return response
    except HTTPException:
        raise
    except Exception:
        state = current_app.config.get('OPENBAYES_SERVING_DEBUGGER_STATE')
        log.exception('predict 函数发生了异常，请检查代码')
        if state:
            rv = state.collect_exception()
            log.error(f'使用浏览器打开 {rv["url"]} 调试此次失败的请求')
            return {'debug_url': rv['url']}, 500

        return Response('', status=500)


@predict_blueprint.app_errorhandler(400)
@cross_origin(supports_credentials=True)
def handle_bad_request(e):
    e
    return {'error': '无效的请求，请检查一下你的请求格式'}, 400


def make_app(predictor_cls):
    env = detect_env()
    if env == 'production':
        init_logging(logging.INFO)
    else:
        init_logging(logging.DEBUG)

    parser = argparse.ArgumentParser('openbayes-serv')
    parser.add_argument('--host', default='0.0.0.0', help='服务监听地址')

    port = 25252
    if env == 'gear':
        port = 8080
    elif env == 'production':
        port = 80

    parser.add_argument('--port', type=int, default=port, help='服务监听端口')

    app = Flask('model-serving')
    app.config['JSON_AS_ASCII'] = False

    log.info('Openbayes Serving 正在启动...')

    with app.app_context():
        params = inspect.signature(predictor_cls).parameters.values()
        clsname = getattr(predictor_cls, '__name__', repr(predictor_cls))
        handlers = []
        for arg in params:
            tag = arg.name if arg.annotation == inspect.Parameter.empty else arg.annotation
            for handler in INIT_ARG_HANDLERS:
                if handler.is_interested(tag):
                    handlers.append((arg.name, tag, handler))
                    break
            else:
                log.error(f"{clsname} 初始化失败: 不知道该如何提供 `{arg.name}`，请参考文档。")
                return

        for _, _, handler in handlers:
            handler.register_parameters(parser)

        options = parser.parse_args()
        app.config['OPENBAYES_SERVING_RUN_OPTIONS'] = options

        args = {}
        for name, tag, handler in handlers:
            args[name] = handler.resolve(tag)

        user_obj = predictor_cls(**args)
        user_predict = getattr(user_obj, 'predict', None)
        if not user_predict:
            log.error(f"{clsname} 初始化失败: 没有实现 `predict` 接口。请参考文档。")
            return

        params = inspect.signature(user_predict).parameters.values()
        resolvers = {}
        for arg in params:
            tag = arg.name if arg.annotation == inspect.Parameter.empty else arg.annotation
            for handler in PREDICT_ARG_HANDLERS:
                if handler.is_interested(tag):
                    resolvers[arg.name] = partial(handler.resolve, tag)
                    break
            else:
                log.error(f"{clsname} 执行失败: 在 `predict` 函数中，不知道该如何提供 `{arg.name}`，请参考文档。")
                return

        app.config['OPENBAYES_SERVING_PREDICTOR_OBJECT'] = user_obj
        app.config['OPENBAYES_SERVING_PREDICT_ARGS'] = resolvers

    if env == 'local':
        log.info('检测到本地开发环境，开启调试模式')
        debug.install(app)
    elif env == 'gear':
        log.info('检测到 Openbayes 算力容器环境，开启调试模式')
        prefix = None

        try:
            meta = requests.get('http://localhost:21999/gear-status').json()
            url = meta['links']['auxiliary']
            prefix = urlparse(url).path
            app.config['OPENBAYES_EXTERNAL_ROOT'] = url
            log.info('外部可访问的 URL：%s', url)
        except Exception:
            log.exception('无法获取 Openbayes 算力容器的元信息，不再进行对接，将不能正常从容器外部访问。')

        app.register_blueprint(predict_blueprint, url_prefix=prefix)
        debug.install(app, url_prefix=prefix)
    elif env == 'production':
        log.info('检测到生产环境，关闭调试模式。请求的统计信息可以在 Openbayes 的控制台上查看。')

    app.register_blueprint(predict_blueprint, url_prefix='/')

    return app


def daemon_start(app, f):
    env = detect_env()
    with app.app_context():
        try:
            f()
        except:
            log.exception('后台线程异常')
            if env == 'production':
                log.error('因处于生产环境，将直接结束当前进程并等待重启')
                os._exit(1)

            state = app.config.get('OPENBAYES_SERVING_DEBUGGER_STATE')
            if state:
                rv = state.collect_exception()
                log.error(f'使用浏览器打开 {rv["url"]} 调试异常的后台线程')

            time.sleep(86400 * 30)

    log.info('后台线程正常结束')


def run(predictor_cls):
    app = make_app(predictor_cls)
    options = app.config['OPENBAYES_SERVING_RUN_OPTIONS']

    predictor = app.config['OPENBAYES_SERVING_PREDICTOR_OBJECT']
    daemon = getattr(predictor, 'run', None)
    if callable(daemon):
        log.info(f'启动后台线程 {predictor_cls.__name__}.run ...')
        t = threading.Thread(target=daemon_start, args=[app, daemon], daemon=True)
        t.start()

    config = uvicorn.Config(app, log_level='info', interface='wsgi')
    server = uvicorn.Server(config=config)

    logger = logging.getLogger('uvicorn')
    logger.handlers[:] = []

    patch_log_formatter(logging.getLogger('uvicorn.access'))
    logging.getLogger('uvicorn.error').setLevel(logging.ERROR)

    if options.host and ":" in options.host:
        family = socket.AF_INET6
    else:
        family = socket.AF_INET

    sock = socket.socket(family=family)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # socket.SO_REUSEPORT
        sock.setsockopt(socket.SOL_SOCKET, 15, 1)
        log.info('已开启 SO_REUSEPORT，可同时运行多个实例分担压力')
    except Exception:
        pass

    try:
        sock.bind((options.host, options.port))
    except OSError:
        log.exception('无法绑定端口')
        sys.exit(1)

    log.info(f'Openbayes Serving 开始服务，本地访问地址：http://{options.host}:{options.port}')
    log.info('-' * 60)
    server.run(sockets=[sock])
