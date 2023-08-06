#!/usr/bin/env python3
import ast
import re

from pygments.token import Token

from nubia import context
from nubia import statusbar
from pathlib import Path


def get_version() -> str:
    sqlb_py = Path(__file__).parent / "__init__.py"
    _version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")
    with open(sqlb_py, "r", encoding="utf8") as f:
        match = _version_re.search(f.read())
        version = match.group("version") if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


class SQLBStatusBar(statusbar.StatusBar):

    def __init__(self, context):
        super().__init__(context)
        self._last_status = None

    def get_rprompt_tokens(self):
        if self._last_status:
            return [(Token.RPrompt, "Error: {}".format(self._last_status))]
        return []

    def set_last_command_status(self, status):
        self._last_status = status

    def get_tokens(self):
        spacer = (Token.Spacer, "    ")
        if context.get_context().verbose:
            is_verbose = (Token.Warn, "ON")
        else:
            is_verbose = (Token.Info, "OFF")
        return [
            (Token.Toolbar, "Atgenomix SeqsLab V3"),
            spacer,
            (Token.Toolbar, get_version()),
            spacer,
            (Token.Toolbar, "Verbose "),
            spacer,
            is_verbose,
        ]
