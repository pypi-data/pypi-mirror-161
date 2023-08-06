#!/usr/bin/env python3
import orjson
from typing import List

from nubia import argument
from nubia import command
from termcolor import cprint

from .internal.common import get_factory

"""
Copyright (C) 2022, Atgenomix Incorporated.

All Rights Reserved.

This program is an unpublished copyrighted work which is proprietary to
Atgenomix Incorporated and contains confidential information that is not to
be reproduced or disclosed to any other person or entity without prior
written consent from Atgenomix, Inc. in each and every instance.

Unauthorized reproduction of this program as well as unauthorized
preparation of derivative works based upon the program or distribution of
copies by sale, rental, lease or lending are violations of federal copyright
laws and state trade secret laws, punishable by civil and criminal penalties.
"""


class BaseRole:

    @command
    def list(self) -> int:
        """
        Display a list of existing roles on SeqsLab.
        """
        backend = get_factory().load_resource()
        ret = backend.list_role()
        if isinstance(ret, int):
            return ret
        cprint(str(orjson.dumps(ret, option=orjson.OPT_INDENT_2), encoding='utf-8'))
        return 0


@command
class Role(BaseRole):
    """Role commands"""

    def __init__(self):
        super().__init__()
