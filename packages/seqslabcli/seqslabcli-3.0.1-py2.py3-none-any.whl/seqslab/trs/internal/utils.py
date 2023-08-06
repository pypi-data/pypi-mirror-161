import os
import uuid
from zipfile import ZipFile

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


def create_zip(target: str = None, wdl_only: bool = False) -> str:

    tf = f'/tmp/{str(uuid.uuid4())}.zip'
    with ZipFile(tf, 'w') as zf:
        for root, dirs, files in os.walk(target):
            for f in files:
                if wdl_only:
                    if f.endswith(".wdl"):
                        relative_root_path = root.replace(target, '').strip('/')
                        relative_path = os.path.join(relative_root_path, f)
                        absolute_path = os.path.join(root, f)
                        zf.write(absolute_path, relative_path)
                else:
                    if f.endswith(".wdl") or f.endswith(".json"):
                        relative_root_path = root.replace(target, '').strip('/')
                        relative_path = os.path.join(relative_root_path, f)
                        absolute_path = os.path.join(root, f)
                        zf.write(absolute_path, relative_path)

    return tf
