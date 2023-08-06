#!/usr/bin/env python3

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

import sys

from nubia import Nubia, Options

from seqslab import auth, drs, wes, trs, workspace, user, role
from seqslab.plugin import SQLBPlugin


def main():
    plugin = SQLBPlugin()
    shell = Nubia(
        name="seqslab-cli",
        command_pkgs=[auth, drs, wes, trs, workspace, user, role],
        plugin=plugin,
        options=Options(
            persistent_history=False,
            auto_execute_single_suggestions=False
        ),
    )
    sys.exit(shell.run())


if __name__ == "__main__":
    main()
