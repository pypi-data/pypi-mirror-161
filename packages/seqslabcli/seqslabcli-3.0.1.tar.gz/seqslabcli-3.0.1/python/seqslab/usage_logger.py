#!/usr/bin/env python3

from nubia.internal.usage_logger_interface import UsageLoggerInterface


class SQLBUsageLogger(UsageLoggerInterface):
    """
    Integrate CLI usage logging to platform Vector logging infrastructure.
    """

    def __init__(self, context):
        super().__init__(context)
        self._context = context

    def pre_exec(self):
        """
        Called before every command execution.
        Can be used to measure how long tasks take to execute.
        """
        pass

    def post_exec(self, cmd, params, result, is_cli):
        """
        Called after every command execution.
        Use this for timing and logging the execution results.
        :param cmd: name of supercommand or subcommand
        :param params:
        :param result: command return code (errno) following
                       Linux system exit code convention.
        :param is_cli: True if not interactive.
        """
        pass
