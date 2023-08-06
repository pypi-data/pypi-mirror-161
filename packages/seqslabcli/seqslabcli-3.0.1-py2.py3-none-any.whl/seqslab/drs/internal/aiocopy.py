import asyncio
import aiofiles
import os
import json

from typing import List, NamedTuple, Literal
from yarl import URL

from .common import get_factory
import hashlib
from seqslab.drs.api.biomimetype import get_mime_type
import datetime

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

checksum_type = "sha256"
lock = {}


class CopyResult(NamedTuple):
    name: str
    mime_type: str
    file_type: str
    size: int
    created_time: str
    access_methods: list
    checksums: list
    status: Literal["complete", "partial", "failed"]
    exceptions: str
    description: str = None
    metadata: dict = {}
    tags: list = []
    aliases: list = []
    id: str = None

    @staticmethod
    def checksum(checksum, type):
        return {
            "checksum": checksum,
            "type": type
        }

    @staticmethod
    def access_method(access_methods_type, access_tier, dst, region, Authorization=None):
        return {
            "type": access_methods_type,
            "access_url": {
                "url": dst,
                "headers": {"Authorization": Authorization}
            },
            "access_tier": access_tier,
            "region": region
        }

    def __str__(self):
        return json.dumps(
            {
                'id': self.id,
                'name': self.name,
                'mime_type': self.mime_type,
                'file_type': self.file_type,
                'description': self.description,
                'created_time': self.created_time,
                'size': self.size,
                'access_methods': self.access_methods,
                'checksums': self.checksums,
                'metadata': self.metadata,
                'tag': self.tags,
                'aliases': self.aliases,
                'status': self.status,
                'exceptions': self.exceptions
            }
        )


async def readfile(file_path: str, chunk_size: int, sha256_hash, queue: asyncio.Queue) -> None:
    while True:
        f, position, size = await queue.get()
        f.seek(position)
        content = f.read(size)
        index = int(position / chunk_size)
        while True:
            await asyncio.sleep(1)
            if not index:
                sha256_hash.update(content)
                lock[file_path] = [index]
                break
            elif index - 1 in lock[file_path]:
                sha256_hash.update(content)
                lock[file_path].append(index)
                break
            else:
                pass
        queue.task_done()


async def get_checksum(src: str, chunk_size: int = 4 * 1024 * 1024) -> hex:
    tasks = []
    file_size = os.stat(src).st_size
    queue = asyncio.Queue()
    sha256_hash = hashlib.new(checksum_type)
    f = open(src, mode='rb')
    for start in range(0, file_size, chunk_size):
        size = min(chunk_size, file_size - start)
        queue.put_nowait((f, start, size))
    for _ in range(256):
        task = asyncio.create_task(
            readfile(file_path=src, chunk_size=chunk_size, sha256_hash=sha256_hash, queue=queue)
        )
        tasks.append(task)
    await queue.join()
    f.close()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    return sha256_hash.hexdigest()


def bio_filetype(filename: str) -> str:
    try:
        checker, file_extension = filename.split('.')[-2:]
        if file_extension in ['gz', 'gzip']:
            if checker in ['fastq', 'fq', 'fasta', 'fa', 'vcf', 'tar']:
                file_extension = '.'.join((checker, file_extension))
    except ValueError:
        file_extension = None
    return file_extension


def argument_setting(files: list, **kwargs) -> tuple:
    multiprocessing = min(len(files), int(kwargs.get("multiprocessing", 1)))
    optargs = {"chunk_size": kwargs.get("chunk_size", 16 * 1024 * 1024),
               "md5_check": kwargs.get("md5_check", True),
               "proxy": kwargs.get("proxy")}
    if kwargs.get("concurrency"):
        # memory_usage = max_concurrency * chunk_size * multiprocessing
        optargs["max_concurrency"] = kwargs.get("concurrency")
    else:
        # memory control 512MB per time, not setting too big because of request timeout problem
        max_concurrency = int(512 * 1024 * 1024 / optargs['chunk_size'] / multiprocessing)
        # handle file too much problem
        if max_concurrency < 1:
            max_concurrency = 1
            multiprocessing = int(512 * 1024 * 1024 / optargs['chunk_size'])
        optargs["max_concurrency"] = max_concurrency
    return multiprocessing, optargs


async def result_setting(status: list, files: List[URL], resp_list: list, **kwargs) -> List[dict]:
    results = []
    for i, sent in enumerate(status):
        file_path = str(files[i])
        size = os.stat(file_path).st_size
        file_extension = bio_filetype(os.path.basename(file_path))
        mime_type = get_mime_type().mime_type(file_extension)
        checksum = None
        if sent != 0:
            if sent == size:
                checksum = await get_checksum(file_path)
                status = "complete"
            else:
                status = "partial"
        else:
            if sent == size:
                checksum = await get_checksum(file_path)
                status = "complete"
            else:
                status = "failed"
        results.append(
            _create_copyresult(
                sent=sent, resp=resp_list[i], mime_type=mime_type, file_extension=file_extension,
                checksum=checksum, type=checksum_type, status=status))
    return results


def _create_copyresult(sent: int, resp: dict, mime_type: str, file_extension: str, checksum: str, type: str,
                       status: Literal["complete", "partial", "failed"]) -> dict:
    checksums = [CopyResult.checksum(checksum=checksum, type=type)]
    access_methods = [CopyResult.access_method(
        access_methods_type=resp["access_methods_type"][i] if resp.get("access_methods_type") else None,
        access_tier='hot', dst=dst, region=resp["region"]) for i, dst in enumerate(resp['dst'])]
    return CopyResult(
        name=os.path.basename(resp["dst"][0]),
        mime_type=mime_type,
        file_type=file_extension,
        created_time=resp["created_time"],
        size=sent,
        access_methods=access_methods if status == "complete" else None,
        checksums=checksums if status == "complete" else None,
        status=status,
        exceptions=f"{resp.get('exceptions')}" if resp.get('exceptions') else None
    )._asdict()


def concat_checksum(checksums: List[str]) -> str or None:
    if len(checksums):
        checksums = [checksum for checksum in checksums if checksum]
        checksums.sort()
        encode_text = ''.join(map(str, checksums)).encode()
        checksum = hashlib.sha256(encode_text).hexdigest()
        return checksum
    else:
        return None


async def result_setting_download(resp_list: list, size: list, **kwargs) -> dict:
    file_list = []
    total_size = 0
    checksums = []
    template = {
        'src': kwargs.get('self_uri'),
        'checksum_type': checksum_type,
        'files': file_list
    }
    for i, resp in enumerate(resp_list):
        file_path = resp["dst"]
        rent = resp['position']
        checksum = None
        if rent != 0:
            if rent == size[i]:
                checksum = await get_checksum(file_path)
                status = "complete"
            else:
                status = "partial"
        else:
            if rent == size[i]:
                checksum = await get_checksum(file_path)
                status = "complete"
            else:
                status = "failed"
        total_size += rent
        file = {
            "dst": file_path,
            "status": status,
            "size": rent
        }
        if resp['exception']:
            file['errors'] = resp['exception'].__str__()
        template['files'].append(file)
        checksums.append(checksum)
    if kwargs.get('folder'):
        template['checksum'] = concat_checksum(checksums=checksums)
    else:
        template['checksum'] = checksums[0]
    template['size'] = total_size
    return template


async def file_to_blob(
        files: List[URL], dst: URL, **kwargs
) -> List[dict]:
    """
    Copy local files to the blob storage
    """
    async with get_factory().load_storage(kwargs.get("workspace")) as store:
        status = []
        progress = 0
        resp_list = []
        uri = dst
        multiprocessing, optargs = argument_setting(files, **kwargs)
        while progress < len(files):
            tasks = []
            count = min(multiprocessing, len(files) - progress)
            # cache token first
            try:
                store.get_token(os.path.dirname(str(uri)))
            except Exception as error:
                await asyncio.sleep(1)
                return [{"execptions": str(error), "status": "failed"}]

            for p in range(progress, progress + count):
                if str(dst).endswith('/'):
                    uri = URL(os.path.join(str(dst), os.path.basename(files[p].path)))
                tasks.append(store.upload(uri, files[p].path, **optargs))
            resp = await asyncio.gather(*tasks, return_exceptions=True)
            for r in resp:
                try:
                    if isinstance(r, dict):
                        status.append(r["position"])
                    else:
                        status.append(0)
                except RuntimeError:
                    pass

            progress += count
            resp_list.extend(resp)

        resps = []
        for i, resp in enumerate(resp_list):
            if isinstance(resp, dict):
                resps.append(resp)
            else:
                resps.append({
                    "position": 0,
                    "dst": [f'cloud/{os.path.basename(str(files[i]))}'],
                    "created_time": None,
                    "region": None,
                    "access_methods_type": None,
                    "exceptions": resp
                })
        assert len(status) == len(files), f"internal error: " \
                                          f"# of status {len(status)} " \
                                          f"not equal to # of files " \
                                          f"{len(files)}"
        results = await result_setting(status, files, resps)
        return results


async def dir_to_blob(
        dir: URL, dst: URL, **kwargs
) -> List[dict]:
    """
    Copy local directory trees to the cloud storage
    """
    async with get_factory().load_storage(kwargs.get("workspace")) as store:
        status = []
        files = []
        relpath = []
        progress = 0
        resp_list = []
        white_list = []
        wl = kwargs.get("white_list")
        if wl:
            with open(wl) as file:
                for line in file:
                    white_list.append(URL(line.rstrip()))

        root_path = os.path.basename(str(dir))

        for root, dirlist, filelist in os.walk(str(dir)):
            if filelist:
                for file in filelist:
                    absolute_path = os.path.join(root, file)
                    relative_path = os.path.relpath(absolute_path, str(dir))
                    if not white_list or URL(absolute_path) in white_list:
                        files.append(URL(absolute_path))
                        relpath.append(os.path.join(root_path, relative_path))
        multiprocessing, optargs = argument_setting(files, **kwargs)
        while progress < len(files):
            count = min(multiprocessing, len(files) - progress)
            tasks = []
            for p in range(progress, progress + count):
                uri = dst.with_path(os.path.join(dst.path.strip("/"), relpath[p].strip("/")))
                tasks.append(store.upload(uri, files[p].path, **optargs))

            resp = await asyncio.gather(*tasks, return_exceptions=True)
            for r in resp:
                try:
                    if isinstance(r, dict):
                        status.append(r["position"])
                    else:
                        status.append(0)
                except RuntimeError:
                    pass

            progress += count
            resp_list.extend(resp)
        resps = []
        for i, resp in enumerate(resp_list):
            if isinstance(resp, dict):
                resps.append(resp)
            else:
                resps.append({
                    "position": 0,
                    "dst": [f'cloud/{os.path.basename(str(files[i]))}'],
                    "created_time": None,
                    "region": None,
                    "access_methods_type": None,
                    "exceptions": resp
                })
        assert len(status) == len(files), f"internal error: " \
                                          f"# of status {len(status)} " \
                                          f"not equal to # of files " \
                                          f"{len(files)}"
        results = await result_setting(status, files, resps)
        return results


async def blobfile_to_dir(
        src: URL, dir: URL, **kwargs
) -> dict:
    """
    Copy cloud file to the local directory
    """
    async with get_factory().load_storage(kwargs.get("workspace")) as store:
        tasks = []
        file = f"{str(dir)}/{os.path.basename(src.path)}"
        file_size = kwargs.get('size')[0]
        chunk_size = kwargs.get("chunk_size")
        max_concurrency = int(file_size / chunk_size)
        if file_size % chunk_size:
            max_concurrency += 1
        optargs = {"chunk_size": chunk_size,
                   "md5_check": kwargs.get("md5_check", True),
                   "proxy": kwargs.get("proxy"),
                   'size': file_size,
                   'max_concurrency': max_concurrency,
                   'bandwidth': kwargs.get('bandwidth'),
                   'overwrite': kwargs.get('overwrite'),
                   'token': kwargs.get('token')}

        tasks.append(
            store.download(uri=src, file=str(file), **optargs))
        resps = await asyncio.gather(*tasks, return_exceptions=True)
        if isinstance(resps[0], Exception):
            return {"errors": resps[0].__str__(), "status": "failed"}
        results = await result_setting_download(resp_list=resps, size=kwargs.get('size'),
                                                self_uri=kwargs.get('self_uri'))
        return results


async def blobfile_to_file(
        src: URL, file: URL, **kwargs
) -> dict:
    """
    Copy cloud file to the local file
    """
    async with get_factory().load_storage(kwargs.get("workspace")) as store:
        tasks = []
        file_size = kwargs.get('size')[0]
        chunk_size = kwargs.get("chunk_size")
        max_concurrency = int(file_size / chunk_size)
        if file_size % chunk_size:
            max_concurrency += 1
        optargs = {"chunk_size": chunk_size,
                   "md5_check": kwargs.get("md5_check", True),
                   "proxy": kwargs.get("proxy"),
                   'size': file_size,
                   'max_concurrency': max_concurrency,
                   'bandwidth': kwargs.get('bandwidth'),
                   'overwrite': kwargs.get('overwrite'),
                   'token': kwargs.get('token')}
        tasks.append(
            store.download(uri=src, file=str(file), **optargs))
        resps = await asyncio.gather(*tasks, return_exceptions=True)
        if isinstance(resps[0], Exception):
            return {"execptions": resps[0].__str__(), "status": "failed"}
        results = await result_setting_download(resp_list=resps, size=kwargs.get('size'),
                                                self_uri=kwargs.get('self_uri'))
        return results


async def blobdir_to_dir(
        srcs: List[URL], dir: URL, **kwargs
) -> dict:
    """
    Copy cloud directory tree to the local directory
    """
    async with get_factory().load_storage(kwargs.get("workspace")) as store:
        status = []
        progress = 0
        resp_list = []
        multiprocessing = min(len(srcs), int(kwargs.get("multiprocessing", 1)))
        optargs = {"chunk_size": kwargs.get("chunk_size", 16 * 1024 * 1024),
                   "md5_check": kwargs.get("md5_check", True),
                   "proxy": kwargs.get("proxy"),
                   'bandwidth': kwargs.get('bandwidth'),
                   'overwrite': kwargs.get('overwrite'),
                   'token': kwargs.get('token')}

        while progress < len(srcs):
            tasks = []
            count = min(multiprocessing, len(srcs) - progress)
            for p in range(progress, progress + count):
                max_concurrency = int(kwargs.get('size')[p] / kwargs.get("chunk_size")) + 1
                optargs['max_concurrency'] = max_concurrency
                optargs['size'] = kwargs.get('size')[p]
                rel_path = os.path.relpath(str(srcs[p]), str(kwargs.get('access_url')))
                file = f"{str(dir)}/{os.path.basename(str(kwargs.get('access_url').strip('/')))}/{rel_path}"
                os.makedirs(os.path.dirname(file), exist_ok=True)
                tasks.append(
                    store.download(uri=srcs[p], file=file, **optargs))
            resp = await asyncio.gather(*tasks, return_exceptions=True)
            for r in resp:
                try:
                    if isinstance(r["position"], int):
                        status.append(r["position"])
                    else:
                        status.append(0)
                except RuntimeError:
                    pass
                except TypeError or NotADirectoryError:
                    return {"execptions": r.__str__(), "status": "failed"}
            progress += count
            resp_list.extend(resp)
        assert len(status) == len(srcs), f"internal error: " \
                                         f"# of status {len(status)} " \
                                         f"not equal to # of files " \
                                         f"{len(srcs)}"
        results = await result_setting_download(resp_list=resp_list, size=kwargs.get('size'),
                                                self_uri=kwargs.get('self_uri'), folder=True)
        return results
