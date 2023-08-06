#!/usr/bin/env python3

from nubia import SessionLogger


class SQLBSessionLogger(SessionLogger):
    """
    Integrate CLI session logging to platform Vector logging infrastructure.
    All command stdout in interactive session can be intercepted and logged.
    """

    def __init__(self, file):
        super().__init__(file)

    def log_command(self, cmd):
        super().log_command(cmd)

    def write(self, data):
        super().write(data)
