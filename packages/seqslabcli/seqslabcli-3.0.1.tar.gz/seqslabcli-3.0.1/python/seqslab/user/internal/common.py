import sys
from typing import TypeVar

from nubia import context
from seqslab.user.resource.azure import AzureResource
from seqslab.settings import USER_RESOURCE_BACKEND


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

Resource = TypeVar("Resource", bound=AzureResource)


class Factory:
    """Storage backend factory"""

    @staticmethod
    def load_resource() -> Resource:
        backend = context.get_context().args.backend
        name = USER_RESOURCE_BACKEND.get(backend)
        mod, mem = name.rsplit(".", 1)
        __import__(mod)
        module = sys.modules[mod]
        backend_class = getattr(module, mem)
        return backend_class()


_factory = Factory()


def get_factory():
    return _factory
