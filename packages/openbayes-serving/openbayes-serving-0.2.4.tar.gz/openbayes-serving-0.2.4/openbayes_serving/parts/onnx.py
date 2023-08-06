# -*- coding: utf-8 -*-

# -- stdlib --
import logging
import os
import sys

# -- third party --
from flask import current_app

# -- own --
from ..common import detect_env


# -- code --
log = logging.getLogger('observing.parts.onnx')


class ONNXInit:
    @staticmethod
    def is_interested(tag):
        return tag == 'onnx'

    @staticmethod
    def register_parameters(parser):
        env = detect_env()
        if env == 'local':
            path = os.getcwd()
        elif env == 'gear':
            path = os.getcwd()
        elif env == 'production':
            path = '/mnt/project'
        else:
            raise Exception('WTF!')

        parser.add_argument(
            '--model-path',
            default=path,
            help='ONNX 模型（.onnx 文件）搜索地址',
        )

    @staticmethod
    def resolve(tag):
        tag
        search_path = current_app.config['OPENBAYES_SERVING_RUN_OPTIONS'].model_path
        log.debug(f'ONNX: 在 {search_path} 搜寻 ONNX 模型...')

        path = None
        if os.path.isdir(search_path):
            for fn in os.listdir(search_path):
                if not fn.endswith('.onnx'):
                    continue
                path = os.path.join(search_path, fn)
                break
            else:
                raise Exception('没有找到 ONNX 模型')
        elif os.path.isfile(search_path):
            path = search_path
        else:
            raise Exception('没有找到 ONNX 模型')

        log.info('正在加载 ONNX 模型：%s ...', path)

        try:
            import onnxruntime
        except ImportError:
            log.exception('无法加载 onnxruntime 库，请确认已经安装了它。如果没有使用特定的包管理工具，可以通过 `pip install onnxruntime` 安装。')
            sys.exit(1)

        # TODO: plain onnxruntime object or a wrapped one?
        model = onnxruntime.InferenceSession(path)
        return model


INIT_ARG_HANDLERS = [ONNXInit]
