#!/usr/bin/env python3
import json
import webbrowser
from typing import List

from nubia import argument
from nubia import command
from termcolor import cprint
from seqslab.exceptions import exception_handler

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


class BaseUser:

    @command()
    def admin_consent(self) -> int:
        """
        [Global administrator only] Prompt to sign in and grant admin consent for SeqsLab Enterprise Applications. For headless OS, an admin consent URL is returned, and the URL must be accessed in order to proceed with the admin consent task."
        """

        def _get_platform_info():
            import platform
            uname = platform.uname()
            return uname.system.lower(), uname.release.lower()

        def can_launch_browser():
            platform_name, _ = _get_platform_info()

            if platform_name != 'linux':
                # Only Linux may have no browser
                return True

            # Using webbrowser to launch a browser is the preferred way.
            try:
                webbrowser.get()
                return True
            except webbrowser.Error:
                # Don't worry. We may still try powershell.exe.
                return False

        backend = get_factory().load_resource()
        ret = backend.admin_consent()
        if isinstance(ret, int):
            return ret

        if can_launch_browser():
            webbrowser.open(ret)
            return 0

        cprint(f'Please copy the URL to a browser to proceed with admin consent {ret}', 'yellow')
        return 0

    @command
    def list(self) -> int:
        """
        Display a list of all existing users on SeqsLab.
        """
        backend = get_factory().load_resource()
        ret = backend.list_user()
        if isinstance(ret, int):
            return ret
        cprint(json.dumps(ret, indent=4), 'yellow')
        return 0

    @command
    @argument("id",
              type=str,
              positional=False,
              description="Specify a user ID (required).")
    def get(self, id) -> int:
        """
        Display the information for a specified user on SeqsLab.
        """
        return self.get_impl(id)

    @staticmethod
    @exception_handler
    def get_impl(id) -> int:
        """
        Display the information for a specified user on SeqsLab.
        """
        backend = get_factory().load_resource()
        ret = backend.get_user(user_id=id)
        if isinstance(ret, int):
            return ret
        cprint(json.dumps(ret, indent=4), 'yellow')
        return 0

    @command
    @argument("email",
              type=str,
              positional=False,
              description="Specify the email account that is going to be added as a SeqsLab user account (required).")
    @argument("roles",
              type=List[str],
              positional=False,
              description="Specify the role the added user is going to be assigned to (required).")
    @argument("active",
              type=bool,
              positional=False,
              description="Specify whether or not to activate the registered user (optional, default = False).")
    @argument("name",
              type=str,
              positional=False,
              description="Specify the user name that you want to use (optional).")
    def add(self, email: str, roles: List[str] = [], active: bool = False, name: str = None) -> int:
        """
        Add a new user to the SeqsLab platform.
        """
        backend = get_factory().load_resource()
        ret = backend.add_user(email=email,
                               roles=roles,
                               active=active,
                               name=name)
        if isinstance(ret, int):
            return ret
        cprint(json.dumps(ret, indent=4), 'yellow')
        return 0

    @command
    @argument("id",
              type=str,
              positional=False,
              description="Specify a user ID (required).")
    @argument("email",
              type=str,
              positional=False,
              description="The email account that is going to be added as a SeqsLab user account (optional).")
    @argument("roles",
              type=List[str],
              positional=False,
              description="Specify the role the user is going to be assigned to (optional).")
    @argument("active",
              type=bool,
              positional=False,
              description="Specify whether or not to activate the registered user (optional).")
    @argument("name",
              type=str,
              positional=False,
              description="Specify the user name that you want to modify (optional).")
    def update(self, id: str, email: str = None, roles: List[str] = [], active: bool = False,
               name: str = None) -> int:
        """
        Add a new user to the SeqsLab platform.
        """
        backend = get_factory().load_resource()
        payload = {}
        if email:
            payload['email'] = email
        if roles:
            payload['roles'] = roles
        if name:
            payload['name'] = name
        if active:
            payload['is_active'] = True
        if not active:
            payload['is_active'] = False

        ret = backend.patch_user(user_id=id,
                                 payload=payload)
        if isinstance(ret, int):
            return ret
        cprint(json.dumps(ret, indent=4), 'yellow')
        return 0

    @command
    @argument("id",
              type=str,
              positional=False,
              description="Specify the user ID (required).")
    def delete(self, id) -> int:
        """
        Delete the specified user.
        """
        backend = get_factory().load_resource()
        ret = backend.delete_user(user_id=id)
        if isinstance(ret, int):
            return ret
        cprint(f'user {id} deleted.', 'yellow')
        return 0


@command
class User(BaseUser):
    """User commands"""

    def __init__(self):
        super().__init__()
