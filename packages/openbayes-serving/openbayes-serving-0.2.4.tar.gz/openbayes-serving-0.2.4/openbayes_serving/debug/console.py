# -*- coding: utf-8 -*-

"""
Modified from werkzeug.debug.console
"""

# -- stdlib --
from io import StringIO
from types import CodeType
import code
import sys

# -- third party --
from werkzeug.local import Local
from pprintpp import pformat

# -- own --


# -- code --
_local = Local()


class StringIO(StringIO):

    def reset(self):
        v = self.getvalue()
        self.seek(0)
        self.truncate()
        return v


class ThreadedStream(object):
    """Thread-local wrapper for sys.stdout for the interactive console."""

    @staticmethod
    def push():
        if not isinstance(sys.stdout, ThreadedStream):
            sys.stdout = ThreadedStream()
        _local.stream = StringIO()

    @staticmethod
    def fetch():
        try:
            stream = _local.stream
        except AttributeError:
            return ""
        return stream.reset()

    @staticmethod
    def displayhook(obj):
        try:
            stream = _local.stream
        except AttributeError:
            return _displayhook(obj)
        if obj is not None:
            _local._current_ipy.locals["_"] = obj
            stream.write(pformat(obj))

    def __setattr__(self, name, value):
        raise AttributeError("read only attribute %s" % name)

    def __dir__(self):
        return dir(sys.__stdout__)

    def __getattribute__(self, name):
        if name == "__members__":
            return dir(sys.__stdout__)
        try:
            stream = _local.stream
        except AttributeError:
            stream = sys.__stdout__
        return getattr(stream, name)

    def __repr__(self):
        return repr(sys.__stdout__)


# add the threaded stream as display hook
_displayhook = sys.displayhook
sys.displayhook = ThreadedStream.displayhook


class _ConsoleLoader(object):
    def __init__(self):
        self._storage = {}

    def register(self, code, source):
        if not code:
            return

        self._storage[id(code)] = source
        # register code objects of wrapped functions too.
        for var in code.co_consts:
            if isinstance(var, CodeType):
                self._storage[id(var)] = source

    def get_source_by_code(self, code):
        try:
            return self._storage[id(code)]
        except KeyError:
            pass


def _wrap_compiler(console):
    compile = console.compile

    def func(source, filename, symbol):
        code = compile(source, filename, symbol)
        console.loader.register(code, source)
        return code

    console.compile = func


class _InteractiveConsole(code.InteractiveInterpreter):
    def __init__(self, globals, locals):
        _locals = dict(globals)
        _locals.update(locals)
        locals = _locals
        locals["__loader__"] = self.loader = _ConsoleLoader()
        code.InteractiveInterpreter.__init__(self, locals)
        self.more = False
        self.buffer = []
        _wrap_compiler(self)

    def runsource(self, source):
        source = source.rstrip() + "\n"
        self.traceback = None
        ThreadedStream.push()
        try:
            source_to_eval = "".join([source])
            code.InteractiveInterpreter.runsource(
                self, source_to_eval, "<debugger>", "single"
            )
        finally:
            output = ThreadedStream.fetch()

        return {
            'code': source,
            'output': output,
            'traceback':  self.traceback,
        }

    def runcode(self, code):
        try:
            exec(code, self.locals)
        except Exception:
            self.showtraceback()

    def showtraceback(self):
        from .tbtools import get_current_traceback

        tb = get_current_traceback(skip=1)
        self.traceback = tb.render()

    def showsyntaxerror(self, filename=None):
        from .tbtools import get_current_traceback

        tb = get_current_traceback(skip=6)
        self.traceback = tb.render()

    def write(self, data):
        sys.stdout.write(data)


class Console(object):
    """An interactive console."""

    def __init__(self, globals=None, locals=None):
        if locals is None:
            locals = {}
        if globals is None:
            globals = {}
        self._ipy = _InteractiveConsole(globals, locals)

    def eval(self, code):
        _local._current_ipy = self._ipy
        old_sys_stdout = sys.stdout
        try:
            return self._ipy.runsource(code)
        finally:
            sys.stdout = old_sys_stdout
