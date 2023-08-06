# -*- coding: utf-8 -*-

"""
Modified from werkzeug.debug
"""

# -- stdlib --
from urllib.parse import urljoin
import mimetypes
import pkgutil
import sys
import types

# -- third party --
from flask import Blueprint, Response, current_app, request

# -- own --
from ..utils.check import check_type
from .tbtools import Traceback


# -- code --
blueprint = Blueprint("openbayes-serv-debugger", __name__)


@blueprint.route('/.debug/console/<tb>', methods=['GET'])
def debug_page(tb):
    return pkgutil.get_data(__name__, 'static/index.html')


@blueprint.route('/.debug/static/<path:filename>', methods=['GET'])
def static_files(filename):
    typ, enc = mimetypes.guess_type(filename)
    if typ and enc:
        mime = f'{typ}+{enc}'
    elif typ and not enc:
        mime = typ
    else:
        mime = 'application/octet-stream'

    return Response(
        pkgutil.get_data(__name__, f'static/{filename}'),
        mimetype=mime,
    )


@blueprint.route('/.debug/traceback/<tb>', methods=['GET'])
def traceback(tb):
    state = current_app.config['OPENBAYES_SERVING_DEBUGGER_STATE']
    if tb not in state.tracebacks:
        return {}, 404

    return state.tracebacks[tb].render()

    return tb


@blueprint.route('/.debug/frame/<frame>/exec', methods=['POST'])
def frame_exec(frame):
    state = current_app.config['OPENBAYES_SERVING_DEBUGGER_STATE']
    if frame not in state.frames:
        return {}, 404

    err = check_type({'code': str, ...: '!'}, request.json)
    if err:
        return {'error': 'Invalid input'}, 400

    frame = state.frames[frame]
    return frame.console.eval(request.json['code'])


class ManualCapture(Exception):
    pass


class DebuggerState(object):

    def __init__(self):
        self.frames = {}
        self.tracebacks = {}

    def collect_exception(self):
        exc_type, exc_value, tb = sys.exc_info()
        tb = Traceback(exc_type, exc_value, tb)
        tb.filter_hidden_frames()
        return self._save(tb)

    def collect_current(self):
        from .tbtools import Traceback
        tb = self._frame2tb(sys._getframe(1))
        e = ManualCapture("手动捕获的执行轨迹")
        tb = Traceback(type(e), e, tb)
        tb.filter_hidden_frames()
        return self._save(tb)

    def _frame2tb(self, f):
        flatted = []
        while f:
            flatted.append(f)
            f = f.f_back
        tb = None
        for f in flatted:
            tb = types.TracebackType(tb, f, f.f_lasti, f.f_lineno)

        return tb

    def _save(self, tb):
        for frame in tb.frames:
            self.frames[str(frame.id)] = frame

        tag = str(tb.id)
        self.tracebacks[tag] = tb

        root = current_app.config.get('OPENBAYES_EXTERNAL_ROOT') or request.url_root

        return {
            'id': tag,
            'url': urljoin(f'{root}/', f'.debug/console/{tag}'),
        }


def install(app, url_prefix=None):
    app.config['OPENBAYES_SERVING_DEBUGGER_STATE'] = DebuggerState()
    app.register_blueprint(blueprint, url_prefix=url_prefix)
