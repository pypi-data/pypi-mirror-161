# -*- coding: utf-8 -*-

"""
Modified from werkzeug.debug.tbtools
"""

# -- stdlib --
from types import TracebackType
from typing import Any, Optional, Tuple, Type, Union, cast
import codecs
import inspect
import os
import re
import sys
import sysconfig
import traceback

# -- third party --
from werkzeug.utils import cached_property

# -- own --
from .console import Console

# -- code --
_coding_re = re.compile(br"coding[:=]\s*([-\w.]+)")
_line_re = re.compile(br"^(.*?)$", re.MULTILINE)
_default_encoding = sys.getdefaultencoding()

def _to_str(
    x: Optional[Any],
    charset: Optional[str] = _default_encoding,
    errors: str = "strict",
    allow_none_charset: bool = False,
) -> Optional[Union[str, bytes]]:
    if x is None or isinstance(x, str):
        return x

    if not isinstance(x, (bytes, bytearray)):
        return str(x)

    if charset is None:
        if allow_none_charset:
            return x

    return x.decode(charset, errors)  # type: ignore

system_exceptions = (SystemExit, KeyboardInterrupt)
try:
    system_exceptions += (GeneratorExit,)
except NameError:
    pass


def get_current_traceback(
    ignore_system_exceptions: bool = False,
    show_hidden_frames: bool = False,
    skip: int = 0,
) -> "Traceback":
    """Get the current exception info as `Traceback` object.  Per default
    calling this method will reraise system exceptions such as generator exit,
    system exit or others.  This behavior can be disabled by passing `False`
    to the function as first parameter.
    """
    info = cast(
        Tuple[Type[BaseException], BaseException, TracebackType], sys.exc_info()
    )
    exc_type, exc_value, tb = info

    if ignore_system_exceptions and exc_type in {
        SystemExit,
        KeyboardInterrupt,
        GeneratorExit,
    }:
        raise
    for _ in range(skip):
        if tb.tb_next is None:
            break
        tb = tb.tb_next
    tb = Traceback(exc_type, exc_value, tb)
    if not show_hidden_frames:
        tb.filter_hidden_frames()
    return tb


class Traceback(object):
    """Wraps a traceback."""

    def __init__(self, exc_type, exc_value, tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.tb = tb

        exception_type = exc_type.__name__
        if exc_type.__module__ not in {"builtins", "__builtin__", "exceptions"}:
            exception_type = exc_type.__module__ + "." + exception_type
        self.exception_type = exception_type

        self.groups = []
        memo = set()
        while True:
            self.groups.append(Group(exc_type, exc_value, tb))
            memo.add(id(exc_value))
            exc_value = exc_value.__cause__ or exc_value.__context__
            if exc_value is None or id(exc_value) in memo:
                break
            exc_type = type(exc_value)
            tb = exc_value.__traceback__
        self.groups.reverse()
        self.frames = [frame for group in self.groups for frame in group.frames]

    def filter_hidden_frames(self):
        """Remove the frames according to the paste spec."""
        for group in self.groups:
            group.filter_hidden_frames()

        self.frames[:] = [frame for group in self.groups for frame in group.frames]

    @property
    def exception(self):
        """String representation of the final exception."""
        return self.groups[-1].exception

    def log(self, logfile=None):
        """Log the ASCII traceback into a file object."""
        if logfile is None:
            logfile = sys.stderr
        tb = f"{self.plaintext.rstrip()}\n"
        logfile.write(tb)

    def render_groups(self, include_title=True):
        """Render the traceback for the interactive console."""
        if not self.frames:
            frames = []
        else:
            frames = [group.render() for group in self.groups]

        return frames

    def render(self):
        return {
            "exception": self.exception,
            "exception_type": self.exception_type,
            "groups": self.render_groups(),
            "plaintext": self.plaintext,
            "id": str(self.id),
        }

    @cached_property
    def plaintext(self):
        import traceback
        return ''.join(traceback.format_exception(self.exc_type, self.exc_value, self.tb))

    @property
    def id(self):
        return id(self)


class Group(object):
    """A group of frames for an exception in a traceback. On Python 3,
    if the exception has a ``__cause__`` or ``__context__``, there are
    multiple exception groups.
    """

    def __init__(self, exc_type, exc_value, tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.has_cause = exc_value.__cause__ is not None
        self.has_context = exc_value.__context__ is not None
        self.frames = []

        while tb is not None:
            self.frames.append(Frame(exc_type, exc_value, tb))
            tb = tb.tb_next

    def filter_hidden_frames(self):
        new_frames = []
        hidden = False

        for frame in self.frames:
            hide = frame.hide
            if hide in ("before", "before_and_this"):
                new_frames = []
                hidden = False
                if hide == "before_and_this":
                    continue
            elif hide in ("reset", "reset_and_this"):
                hidden = False
                if hide == "reset_and_this":
                    continue
            elif hide in ("after", "after_and_this"):
                hidden = True
                if hide == "after_and_this":
                    continue
            elif hide or hidden:
                continue
            new_frames.append(frame)

        # if we only have one frame and that frame is from the codeop
        # module, remove it.
        if len(new_frames) == 1 and self.frames[0].module == "codeop":
            del self.frames[:]

        # if the last frame is missing something went terrible wrong :(
        elif self.frames[-1] in new_frames:
            self.frames[:] = new_frames

    @property
    def exception(self):
        """String representation of the exception."""
        buf = traceback.format_exception_only(self.exc_type, self.exc_value)
        rv = "".join(buf).strip()
        return _to_str(rv, "utf-8", "replace")

    def render(self):
        relation = 'root'
        if self.has_cause:
            relation = 'cause'
        elif self.has_context:
            relation = 'context'

        return {
            'relation': relation,
            'exception': self.exception,
            'frames': [frame.render() for frame in self.frames],
        }

    def render_text(self):
        out = []
        out.append(u"Traceback (most recent call last):")
        for frame in self.frames:
            out.append(frame.render_text())
        out.append(self.exception)
        return u"\n".join(out)


class Frame(object):
    """A single frame in a traceback."""

    def __init__(self, exc_type, exc_value, tb):
        self.lineno = tb.tb_lineno
        self.function_name = tb.tb_frame.f_code.co_name
        self.locals = tb.tb_frame.f_locals
        self.globals = tb.tb_frame.f_globals

        try:
            zelf = self.locals['self']
            class_name = zelf.__class__.__name__
            self.function_name = f'{class_name}.{self.function_name}'
        except Exception:
            pass

        fn = inspect.getsourcefile(tb) or inspect.getfile(tb)
        if fn[-4:] in (".pyo", ".pyc"):
            fn = fn[:-1]
        # if it's a file on the file system resolve the real filename.
        if os.path.isfile(fn):
            realpath = os.path.realpath(fn)
        else:
            realpath = fn

        self.filename = os.fsdecode(fn)
        self.realpath = os.fsdecode(realpath)
        self.abbrname = self.abbr_filename(self.realpath) or self.filename
        self.module = self.globals.get("__name__", self.locals.get("__name__"))
        self.loader = self.globals.get("__loader__", self.locals.get("__loader__"))
        self.code = tb.tb_frame.f_code

        # support for paste's traceback extensions
        self.hide = self.locals.get("__traceback_hide__", False)

    def render(self):
        """Render a single frame in a traceback."""
        return {
            "id": str(self.id),
            "filename": self.abbrname,
            "realpath": self.realpath,
            "lineno": self.lineno,
            "function": self.function_name,
            "context": self.render_line_context(),
            "is_library": self.is_library,
        }

    @cached_property
    def is_library(self):
        return any(
            self.filename.startswith(path) for path in sysconfig.get_paths().values()
        )

    def abbr_filename(self, fn):
        cwd = os.getcwd()
        if fn.startswith(os.getcwd()):
            return fn[len(cwd)+1:]

        if '/site-packages/' in fn:
            fn = fn.split('/site-packages/')[-1]
            fn = self._decorate_lib(fn)
            return fn

        for prefix in sysconfig.get_paths().values():
            if fn.startswith(prefix):
                return self._decorate_lib(fn[len(prefix)+1:])

        return None

    def _decorate_lib(self, fn):
        parts = fn.split('/', 1)
        if len(parts) > 1:
            fn = f'[{parts[0]}]:{parts[1]}'
        else:
            fn = f'[{parts[0]}]'

        return fn

    def render_text(self):
        return u'  File "%s", line %s, in %s\n    %s' % (
            self.filename,
            self.lineno,
            self.function_name,
            self.current_line.strip(),
        )

    def render_line_context(self):
        lines = []

        context = 5
        l, r = (self.lineno - 1) - context, (self.lineno - 1) + context + 1
        l = max(0, l)
        r = min(len(self.sourcelines), r)

        for n, line in zip(range(l, r), self.sourcelines[l:r]):
            lines.append({
                'lineno': n + 1,
                'line': line,
            })

        return lines

    def eval(self, code, mode="single"):
        """Evaluate code in the context of the frame."""
        if isinstance(code, str):
            code = compile(code, "<interactive>", mode)
        return eval(code, self.globals, self.locals)

    @cached_property
    def sourcelines(self):
        """The sourcecode of the file as list of unicode strings."""
        # get sourcecode from loader or file
        source = None
        if self.loader is not None:
            try:
                if hasattr(self.loader, "get_source"):
                    source = self.loader.get_source(self.module)
                elif hasattr(self.loader, "get_source_by_code"):
                    source = self.loader.get_source_by_code(self.code)
            except Exception:
                # we munch the exception so that we don't cause troubles
                # if the loader is broken.
                pass

        if source is None:
            try:
                with open(self.filename, mode="rb") as f:
                    source = f.read()
            except IOError:
                return []

        # already str?  return right away
        if isinstance(source, str):
            return source.splitlines()

        charset = "utf-8"
        if source.startswith(codecs.BOM_UTF8):
            source = source[3:]
        else:
            for idx, match in enumerate(_line_re.finditer(source)):
                coding_match = _coding_re.search(match.group())
                if coding_match is not None:
                    charset = coding_match.group(1).decode("utf-8")
                    break
                if idx > 1:
                    break

        # on broken cookies we fall back to utf-8 too
        charset = _to_str(charset)
        try:
            codecs.lookup(charset)
        except LookupError:
            charset = "utf-8"

        return source.decode(charset, "replace").splitlines()

    @cached_property
    def console(self):
        return Console(self.globals, self.locals)

    @property
    def current_line(self):
        try:
            return self.sourcelines[self.lineno - 1]
        except IndexError:
            return u""

    @property
    def id(self):
        return id(self)
