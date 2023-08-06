import sys
from typing import TypeVar

from nubia import context
from seqslab.trs.register.base import TRSregister
from seqslab.settings import TRS_REGISTER_BACKEND


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

register = TypeVar("register", bound=TRSregister)


class Factory:
    """Storage backend factory"""

    @staticmethod
    def load_resource() -> register:
        backend = context.get_context().args.backend
        name = TRS_REGISTER_BACKEND.get(backend)
        mod, mem = name.rsplit(".", 1)
        __import__(mod)
        module = sys.modules[mod]
        backend_class = getattr(module, mem)
        return backend_class()


_factory = Factory()


def trs_register():
    return _factory

