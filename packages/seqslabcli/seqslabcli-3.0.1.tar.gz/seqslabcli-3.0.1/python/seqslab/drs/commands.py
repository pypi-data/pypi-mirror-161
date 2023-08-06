import asyncio
import glob
import json
import logging
import operator
import os
import sys
import time
from functools import reduce
from io import StringIO
from typing import List, Dict, Optional

import requests
from nubia import argument
from nubia import command
from nubia import context
from sample_sheet import SampleSheet, Sample
from seqslab.exceptions import async_exception_handler, exception_handler
from seqslab.runsheet.runsheet import RunSheet
from tabulate import tabulate
from termcolor import cprint
from yarl import URL

from . import __version__, API_HOSTNAME
from .api.common import drs_register
from .internal import aiocopy
from .internal import utils
from .internal.common import get_factory
import csv
import errno

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


class BaseDatahub:
    DRS_SEARCH_URL = f"https://{API_HOSTNAME}/ga4gh/drs/{__version__}/objects/search/"

    @property
    def proxy(self) -> str:
        """web proxy server"""
        return context.get_context().args.proxy

    @staticmethod
    @exception_handler
    def _upload(src: URL, dst: URL, recursive: bool, **kwargs) -> list:
        # copy from local to cloud
        paths = glob.glob(src.path)
        if not len(paths):
            raise FileNotFoundError("--src Enter a valid src path. ")

        if 1 == len(paths):
            if os.path.isdir(paths[0]):
                if not recursive:
                    raise OSError("--recursive (-r) is Required.")
                coro = aiocopy.dir_to_blob(URL(*paths), dst, **kwargs)
            else:
                coro = aiocopy.file_to_blob([URL(*paths)], dst, **kwargs)
        else:
            if os.path.splitext(str(dst))[1]:
                raise OSError('--dst Enter a valid dst path.')
            files = []
            dirs = []
            for p in paths:
                if os.path.isfile(p):
                    files.append(URL(p))
                else:
                    dirs.append(URL(p))
            if len(dirs) != 0:
                for dir_path in dirs:
                    for root, folderlist, filelist in os.walk(str(dir_path)):
                        if filelist:
                            abs_paths = [URL(os.path.join(root, file)) for file in filelist]
                            files.extend(abs_paths)
            coro = aiocopy.file_to_blob(files, dst, **kwargs)

        results = asyncio.run(coro)
        for result in results:
            if result['status'] != 'complete':
                raise ValueError(json.dumps(results, indent=4))
        return results

    @staticmethod
    def _stdout(results: List[dict], output: str) -> int:
        """
            stdout:: support different format [json, tsv, table]
        """
        if output == "tsv":
            s = StringIO()
            writer = csv.DictWriter(s, fieldnames=list(results[0].keys()))
            writer.writeheader()
            for result in results:
                writer.writerow(result)
            s.seek(0)
            content = s.read().replace(',', '\t')
            cprint(content)
        elif output == 'table':
            table_header = list(results[0].keys())
            table_datas = [result.values() for result in results]
            cprint(tabulate(
                tabular_data=table_datas,
                headers=table_header,
                tablefmt='pipe'
            ))
        else:
            cprint(json.dumps(results, indent=4))
        return 0

    @staticmethod
    def _stdin() -> list:
        payload = sys.stdin.readlines()
        try:
            jsons = json.loads(''.join(payload))
            if not isinstance(jsons, list):
                jsons = [jsons]
            return jsons
        except json.JSONDecodeError:
            raise ValueError(
                f'Stdin format only supports json. Please read the document and make sure the format is valid.')

    @command(aliases=["copy"])
    @argument("workspace",
              type=str,
              positional=False,
              description="Specify the workspace based on the signed in account (required).", )
    @argument("src",
              type=URL,
              positional=False,
              description="Specify the source directory, file path, or DRS URL (required).")
    @argument("dst",
              type=URL,
              positional=False,
              description="Specify the destination directory, file path, or DRS URL (optional, default =' /'). ")
    @argument("recursive",
              type=bool,
              positional=False,
              description="Copy an entire directory tree (optional, default = False).",
              aliases=["r"])
    @argument("concurrency",
              type=int,
              positional=False,
              description="Specify the transmission concurrency in file uploading. The upload bandwidth "
                          "can be modified using the formula concurrency * chunk_size * multiprocessing "
                          "(default = 64).")
    @argument("multiprocessing",
              type=int,
              positional=False,
              description="Specify the number of files that you want to upload at any given time. "
                          "Changing the default value is not recommended (default = 1).")
    @argument("chunk_size",
              type=str,
              positional=False,
              description="Specify the size of each file that you want to upload in megabytes (MB). "
                          "Changing the default value is not recommended (default = 8MB).",
              choices=['8', '16'])
    @argument("output",
              type=str,
              positional=False,
              description="Specify the stdout format (default = json).",
              choices=['json', 'table', 'tsv'])
    @argument("white_list",
              type=Optional[str],
              positional=False,
              description="Specify a list of directories that you want to upload. "
                          "A list can contain multiple folder paths (optional).")
    def upload(
            self, workspace: str, src: URL, dst: URL = URL('/'), recursive: bool = False, output: str = 'json',
            concurrency: int = 0, multiprocessing: int = 1, chunk_size: str = '8',
            white_list: Optional[str] = None
    ) -> int:
        """
        Upload data from the local file system to a SeqsLab Data Hub cloud service.
        """

        def __log(results: List[dict], output: str):
            self._stdout(results=results, output=output)
            for _, r in enumerate(results):
                msg = "Copy {name} {size}) is {status}".format(
                    name=r.get('name'), size=r.get('size'), status=r.get('status')
                )
                if r.get('status') == "failed":
                    logging.error(msg)
                elif r.get('status') == "partial":
                    logging.error(msg)
                else:
                    logging.info(msg)

        size = {
            '8': 8 * 1024 * 1024,
            '16': 16 * 1024 * 1024,
        }
        if not workspace:
            logging.error("Invalid workspace name")
            cprint("Enter a valid workspace name.", "red")
            return errno.EINVAL

        if str(dst).isspace() or len(str(dst)) == 0:
            logging.error("Invalid dst path")
            cprint("Enter a valid dst path.", "red")
            return errno.EINVAL

        if os.path.isdir(str(src)):
            if not str(dst).endswith('/'):
                dst = URL(f'{str(dst)}/')
            if str(src).endswith('/'):
                src = URL(f'{str(src).rstrip("/")}')

        result = self._upload(src=src, dst=dst, recursive=recursive, workspace=workspace,
                              multiprocessing=multiprocessing, concurrency=concurrency,
                              chunk_size=size[chunk_size], proxy=self.proxy, white_list=white_list)
        if isinstance(result, int):
            return result
        __log(result, output)
        return 0

    @command
    @argument("workspace",
              type=str,
              positional=False,
              description="Specify the workspace based on the signed in account (required).", )
    @argument("id",
              type=str,
              positional=False,
              description="A DRS object ID (required if there is no self URI).")
    @argument("uri",
              type=URL,
              positional=False,
              description="A DRS self URI (required if there is no DRS ID).")
    @argument("dst",
              type=str,
              positional=False,
              description="Show the destination directory or file path (required).")
    @argument("concurrency",
              type=int,
              positional=False,
              description="Specify the numbers of chunks that can be transferred concurrently. The download bandwidth "
                          "can be estimated using the formula concurrency * chunk_size. "
                          "Changing the default value is not recommended (optional, default = 120).",
              )
    @argument("multiprocessing",
              type=int,
              positional=False,
              description="Specify the number of files that you want to upload at any given time. "
                          "Changing the default value is not recommended (default = 1).")
    @argument("chunk_size",
              type=str,
              positional=False,
              description="Specify the size of chunk in the chunked downloading process. "
                          "If the specified size is greater than 4MB, the md5 hashes are not checked. "
                          "Changing the default value is not recommended (optional, default = 4MB).",
              choices=['4', '8', '16', '32'])
    @argument("output",
              type=str,
              positional=False,
              description="Specify the output format of the stdout file (optional, default = json).",
              choices=['json', 'table', 'tsv'])
    @argument("overwrite",
              type=bool,
              positional=False,
              description="Overwrite the existing files (optional, default = false).")
    def download(self, workspace: str, dst: str, id: str = None, uri: URL = None, overwrite: bool = False,
                 output: str = 'json', chunk_size: str = '4', concurrency: int = 120, multiprocessing: int = 1) -> int:
        """
        Download the content of a DRS object to a file or directory path.
        """

        def __log(results: List[dict], output: str):
            self._stdout(results=results, output=output)
            for _, r in enumerate(results):
                for _, f in enumerate(r['files']):
                    msg = "Copy {uri}({size}) is {status}".format(
                        uri=f['dst'], size=f['size'], status=f['status']
                    )
                    if f['status'] == "failed":
                        logging.error(msg)
                    elif f['status'] == "partial":
                        logging.error(msg)
                    else:
                        logging.info(msg)

        size = {
            '4': 4 * 1024 * 1024,
            '8': 8 * 1024 * 1024,
            '16': 16 * 1024 * 1024,
            '32': 32 * 1024 * 1024
        }
        if not workspace:
            logging.error("Invalid workspace name")
            cprint("Invalid workspace name", "red")
            return errno.EINVAL

        tasks = []
        kwargs = {}
        if not id:
            if not uri:
                logging.error("Invalid executions, Enter a valid drs_ids or a valid self_uris.")
                cprint("Invalid executions, Enter a valid drs_ids or a valid self_uris.", "red")
                return errno.EINVAL
            else:
                id = uri.name
                if uri.host:
                    kwargs['self_uri_host'] = uri.host
        else:
            if uri:
                logging.error("Invalid executions, Enter a valid drs_ids or a valid self_uris,"
                              "not both given.")
                cprint("Invalid executions, Enter a valid drs_ids or a valid self_uris,"
                       "not both given.", "red")
                return errno.EINVAL

        tasks.append(
            self._download(drs_id=id, dst=dst, workspace=workspace, chunk_size=size[chunk_size],
                           bandwidth=concurrency, proxy=self.proxy, overwrite=overwrite,
                           multiprocessing=multiprocessing, **kwargs))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results, _ = loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        for r in results:
            if isinstance(r.result(), int):
                return r.result()
            result = [r.result()]
        __log(result, output)
        return 0

    @staticmethod
    @async_exception_handler
    async def _download(drs_id: str, dst: str, **kwargs):
        backend = get_factory().load_storage(kwargs.get('workspace'))
        download_info = await backend.expand_blob(drs_id=drs_id, **kwargs)
        dst = os.path.abspath(os.path.expanduser(dst))
        files = download_info['files']
        kwargs['size'] = [file['size'] for file in files]
        kwargs['access_url'] = download_info['access_url']
        kwargs['token'] = download_info['token']['Authorization']
        kwargs['self_uri'] = download_info['self_uri']
        if download_info['access_url'] == files[0]['path']:
            if os.path.isdir(dst):
                coro = await aiocopy.blobfile_to_dir(src=URL(files[0]['path']), dir=URL(dst), **kwargs)
            else:
                coro = await aiocopy.blobfile_to_file(src=URL(files[0]['path']), file=URL(dst), **kwargs)

        else:
            coro = await aiocopy.blobdir_to_dir(srcs=[URL(file['path']) for file in files], dir=URL(dst), **kwargs)
        for result in coro['files']:
            if result['status'] != 'complete':
                raise ValueError(json.dumps(coro, indent=4))
        return coro

    @command
    @argument("workspace",
              type=str,
              positional=False,
              description="Specify the workspace based on the signed in account (required).", )
    @argument("type",
              type=str,
              positional=True,
              description="If you want to register a file as a blob , please choose a file-blob. "
                          "If you want to register a folder as a blob , please choose a folder-blob. "
                          "(Required)",
              choices=['file-blob', 'folder-blob'])
    @argument("name",
              type=str,
              description="Specify the name of the object that you want to register "
                          "(must not be in stdin mode, otherwise required).", )
    @argument("file_type",
              type=str,
              description="Specify the file type of the object that you want to register "
                          "(must not be in stdin mode, otherwise required). "
                          "For example, application/json.", )
    @argument("mime_type",
              type=str,
              description="Specify the MIME type of the object that you want to register "
                          "(must not be in stdin mode, otherwise required). "
                          "For example, application/json.", )
    @argument("description",
              type=str,
              description="Specify the description of the object that you want to register "
                          "(optional).")
    @argument("aliases",
              type=List[str],
              description="Specify the aliases of the object that you want to register "
                          "(optional).")
    @argument("tags",
              type=List[str],
              positional=False,
              description="Specify the tags that you want to use for the object that you want to register "
                          "(optional).", )
    @argument("created_time",
              type=str,
              positional=False,
              description="Provide the timestamp of when an object was first created in the storage location. "
                          "The time format must be in RFC3339. "
                          "If the DRS type is blob, this argument is required (must not be in stdin mode). "
                          "For example, 2021-09-13 02:54:03.636044+00:00.")
    @argument("updated_time",
              type=str,
              positional=False,
              description="Provide the timestamp of when an object was updated. "
                          "The time format must be in RFC3339. "
                          "If the DRS type is blob, this argument is required (must not be in stdin mode). "
                          "For example, 2021-09-13 02:54:03.636044+00:00.")
    @argument("size",
              type=int,
              positional=False,
              description="Specify the size of the object that you want to register. "
                          "(must not be in stdin mode, otherwise required).", )
    @argument("urls",
              type=List[URL],
              description="Specify the absolute path of object that you want to register. "
                          "(must not be in stdin mode, otherwise required).")
    @argument("access_tiers",
              type=str,
              description="Specify the access tier that you want to use for the object that you want to register. "
                          "If the DRS type is bundle, do not use this argument (must not be in stdin mode).",
              choices=['Hot', 'Cool', 'Archive'])
    @argument("regions",
              type=List[str],
              description="Specify the region for the storage location where you want to store the object."
                          "(must not be in stdin mode, otherwise required). "
                          "For example, you can use local, westus, eastjp, or other regions.")
    @argument("Authorizations",
              type=List[str],
              description="Provide the authorization credentials for the storage location "
                          "where you want to store the object (optional, must not be in stdin mode).")
    @argument("checksum",
              type=str,
              positional=False,
              description="Specify the checksum of the object that you want to register. "
                          "The checksum type must be sha256. "
                          "If the DRS type is blob, this argument is required "
                          "(must not be in stdin mode, otherwise required).")
    @argument("checksum_type",
              type=str,
              positional=False,
              description="Specify the type of checksum (must not be in stdin mode, otherwise required). "
                          "At the moment, only sha256 is supported.",
              choices=['sha256'])
    @argument("metadata",
              type=str,
              positional=False,
              description="Specify a JSON string describing the metadata of the object you want to register "
                          "(optional).")
    @argument("stdin",
              type=bool,
              positional=False,
              description="Specify whether or not you want to enable stdin mode (optional). "
                          "Selecting stdin prevents you from enabling any of the other options and the json object "
                          "must therefore contain all the required keys [name, file_type, mime_type, description, "
                          "aliases, tags, created_time, updated_time, size, urls, access_tiers, regions, "
                          "Authorizations, checksum, checksum_type, metadata].")
    @argument("output",
              type=str,
              positional=False,
              description="Specify the output format of the stdout file (optional, default = json).",
              choices=['json', 'table', 'tsv'])
    @argument("id",
              type=str,
              positional=False,
              description="Specify a custom object ID (optional).")
    def register_blob(self, workspace: str, type: str, output: str = 'json', stdin: bool = False, **kwargs) -> int:
        """
            Register a DRS object as a blob.
        """

        def __log(results: List[dict], output: str):
            self._stdout(results=results, output=output)
            for r in results:
                msg = f"Register {r['id']}  is complete."
                logging.info(msg)

        if not workspace:
            cprint('Enter a valid workspace', 'red')
            return errno.EINVAL

        results = self._register_blob(drs_type=type, stdin=stdin, workspace=workspace, **kwargs)
        if isinstance(results, int):
            return results
        __log(results=results, output=output)
        return 0

    @staticmethod
    @exception_handler
    def _register_blob(drs_type: str, stdin: bool, workspace: str, **kwargs) -> List[dict]:
        backend = drs_register().load_register(workspace)
        if stdin:
            if len(kwargs):
                raise ValueError(f'Stdin mode does not support these commands {kwargs.keys()}.')
            payloads = backend.create_payload(stdin=BaseDatahub._stdin(), type=drs_type, **kwargs)
        else:
            payloads = [{
                "name": kwargs.get('name'),
                "mime_type": kwargs.get('mime_type'),
                "file_type": kwargs.get('file_type'),
                "created_time": kwargs.get('created_time'),
                "updated_time": kwargs.get('updated_time') if kwargs.get('updated_time') else kwargs.get(
                    'created_time'),
                "size": kwargs.get('size'),
                "access_methods": [
                    {'type': url.scheme,
                     'access_url': {
                         'url': url,
                         'headers': {
                             "Authorization": kwargs.get('Authorizations')[i] if kwargs.get('Authorizations') else None
                         }
                     },
                     "access_tier": kwargs.get('access_tiers'),
                     "region": kwargs.get('regions')[i]} for i, url in enumerate(kwargs.get('urls'))
                ] if kwargs.get('urls') else [],
                "checksums": [{
                    "checksum": kwargs.get('checksum'),
                    "checksum_type": kwargs.get('checksum_type'),
                }],
                "description": kwargs.get('description'),
                "aliases": kwargs.get('aliases'),
                "metadata": json.loads(kwargs.get('metadata')) if kwargs.get('metadata') else None,
                "tags": kwargs.get('tags'),
                "id": kwargs.get('id')
            }]

        results = backend.create_drsobjects(drs_type='blob', payloads=payloads)
        return results

    @command
    @argument("workspace",
              type=str,
              positional=False,
              description="Specify the workspace based on the signed in account (required).", )
    @argument("drs_id",
              type=List[str],
              positional=False,
              description="Specify the object ID that will be registered in the bundle (required).")
    @argument("name",
              type=str,
              description="Specify the name of the bundle that you want to register "
                          "(must not be in stdin mode, otherwise required).", )
    @argument("description",
              type=str,
              description="Specify the description of the bundle that you want to register "
                          "(optional).")
    @argument("aliases",
              type=List[str],
              description="Specify the aliases of the bundle that you want to register "
                          "(optional).")
    @argument("tags",
              type=List[str],
              positional=False,
              description="Specify the tags that you want to use for the bundle that you want to register "
                          "(optional).")
    @argument("metadata",
              type=str,
              positional=False,
              description="Specify a JSON string describing the metadata of the bundle you want to register "
                          "(optional).")
    @argument("id",
              type=str,
              positional=False,
              description="Specify a custom object ID (optional).")
    @argument("output",
              type=str,
              positional=False,
              description="Specify the output format of the stdout file (default = json, optional).",
              choices=['json', 'table', 'tsv'])
    def register_bundle(self, name: str, workspace: str, drs_id: List[str], output: str = 'json', **kwargs):
        """
            Register a DRS object as a bundle.
        """

        def __log(results: List[dict], output: str):
            self._stdout(results=results, output=output)
            for r in results:
                msg = f"{r['id']}  has been registered."
                logging.info(msg)

        if not workspace:
            cprint('Enter a valid workspace', 'red')
            return errno.EINVAL

        results = self._register_bundle(name=name, drs_ids=drs_id, workspace=workspace, **kwargs)
        if isinstance(results, int):
            return results
        __log(results=results, output=output)
        return 0

    @staticmethod
    @exception_handler
    def _register_bundle(name: str, drs_ids: List[str], workspace: str, stdin: bool = False, **kwargs) -> List[dict]:
        backend = drs_register().load_register(workspace)
        if stdin:
            raise NotImplementedError("This function is not yet available.")
        else:
            payloads = [{
                "name": name,
                "mime_type": "application/octet",
                "file_type": "bundle",
                "description": kwargs.get('description'),
                "aliases": kwargs.get('aliases'),
                "metadata": json.loads(kwargs.get('metadata')) if kwargs.get('metadata') else None,
                "tags": kwargs.get('tags'),
                "id": kwargs.get('id'),
                "contents": drs_ids
            }]

        results = backend.create_drsobjects(drs_type='bundle', payloads=payloads)

        return results

    @command(aliases=["clean"])
    @argument("names",
              type=List[str],
              positional=False,
              description="Generate a list of DRS object names "
                          "(optional).")
    @argument("tags",
              type=List[str],
              positional=False,
              description="Specify the label of the DRS object that you want to delete "
                          "(optional).")
    def delete(
            self,
            tags: List[str] = [],
            names: List[str] = [],
    ) -> int:
        """
        Delete DRS objects either by name or by tag.
        """
        if not names and not tags:
            cprint("Either give names or tags to do drs query", "red")
            return errno.ENOENT

        asyncio.run(utils.drs_delete(names, tags))

        return 0

    @command
    @argument("names",
              type=List[str],
              positional=False,
              description="Locate a DRS object using a list of names "
                          "(optional).")
    @argument("tags",
              type=List[str],
              positional=False,
              description="Locate a DRS object using a list of labels "
                          "(optional).")
    def search(
            self,
            tags: List[str] = [],
            names: List[str] = [],
    ) -> int:
        """
        Locate DRS objects either by name or by tag. Do not combine names and labels in a single query.
        """
        if not names and not tags:
            cprint("Either give names or tags to do drs query", "red")
            return errno.ENOENT
        if names and tags:
            cprint("Search condition names and tags cannot be given at the same time", "red")
            return errno.ENOENT

        result = asyncio.run(utils.drs_search(names, tags))
        cprint(json.dumps(result, indent=4))

        return 0

    @staticmethod
    def find_fastq_paths(sample: Sample, fastq_path: str) -> List[str]:
        return [os.path.join(root, f) for root, dirs, files in os.walk(fastq_path) for f in files
                if f.find(f'{sample.Sample_ID}') != -1 and f.rfind('fastq.gz') != -1]

    @staticmethod
    def find_fqs(
            fastq_path: str,
            run_sheet_path: str
    ) -> list:
        """
        Create an upload list based on the Run Sheet and FASTQ path information.
        """
        run_sheet = RunSheet(run_sheet_path)
        hdr_meta = {k.replace(' ', '_'): v for k, v in run_sheet.Header.items()}
        overall_idx = 0
        upload_info = []
        for s in run_sheet.samples:
            overall_idx += 1
            sample_meta = {k.replace(' ', '_'): v for k, v in s.to_json().items()}
            sample_meta.update({"Order_Overall": str(overall_idx)})
            id_rule = s.get('Drs_ID', None)

            fq_paths = BaseDatahub.find_fastq_paths(s, fastq_path)
            if run_sheet.is_single_end:
                assert len(fq_paths) == 1
                upload_info.append({
                    "src": fq_paths[0],
                    "dst": fq_paths[0],
                    "tags": [f"{s.get('Run_Name', run_sheet.Header.Date)}/{s.get('Read1_Tag', '')}"],
                    "metadata": {"header": hdr_meta, "sample": sample_meta, "file": {"Pair": "1"}}
                })
                if id_rule:
                    upload_info[-1]['id'] = BaseDatahub._gen_drs_id(id_rule, upload_info[-1]['metadata'])

            if run_sheet.is_paired_end:
                assert len(fq_paths) == 2
                fq_paths.sort()
                upload_info.append({
                    "src": fq_paths[0],
                    "dst": fq_paths[0],
                    "tags": [f"{s.get('Run_Name', run_sheet.Header.Date)}/{s.get('Read1_Tag', '')}"],
                    "metadata": {"header": hdr_meta, "sample": sample_meta, "file": {"Pair": "1"}}
                })
                upload_info.append({
                    "src": fq_paths[1],
                    "dst": fq_paths[1],
                    "tags": [f"{s.get('Run_Name', run_sheet.Header.Date)}/{s.get('Read2_Tag', '')}"],
                    "metadata": {"header": hdr_meta, "sample": sample_meta, "file": {"Pair": "2"}}
                })
                if id_rule:
                    upload_info[-1]['id'] = BaseDatahub._gen_drs_id(id_rule, upload_info[-1]['metadata'])
                    upload_info[-2]['id'] = BaseDatahub._gen_drs_id(id_rule, upload_info[-2]['metadata'])

        return upload_info

    @staticmethod
    def _gen_drs_id(rule: str, meta: dict, separator='-', bracket='{}') -> str:
        content = []
        for kw in rule.split(separator):
            i = kw.strip(bracket)
            try:
                val = reduce(operator.getitem, i.split('.'), meta).replace('/', '-')
                content.append(val)
            except:
                raise RuntimeError('Illegal tag rule - rule must start with either header or sample')

        return '_'.join(filter(None, content))

    @command(aliases=["runsheet"])
    @argument("workspace",
              type=str,
              positional=False,
              description="Specify the workspace based on the signed in account (required).", )
    @argument("input_dir",
              type=str,
              positional=False,
              description="Specify the FASTQ file path (required).")
    @argument("upload_dst",
              type=str,
              positional=False,
              description="Specify the upload destination path (optional, default = input_dir).")
    @argument("run_sheet",
              type=str,
              positional=False,
              description="Specify the Run Sheet file path (required).")
    @argument("concurrency",
              type=int,
              positional=False,
              description="Specify the transmission concurrency in file uploading. The upload bandwidth "
                          "can be modified using the formula concurrency * chunk_size * multiprocessing "
                          "(default = 64).")
    @argument("multiprocessing",
              type=int,
              positional=False,
              description="Specify the number of files that you want to upload at any given time. "
                          "Changing the default value is not recommended (optional, default = 1).")
    def upload_runsheet(self, workspace, input_dir: str, run_sheet: str, upload_dst: str = None,
                        concurrency: int = 0, multiprocessing: int = 1) -> int:
        """
        Upload samples based on the Run Sheet and FASTQ path information.
        """
        if not workspace:
            logging.error("Invalid workspace name")
            cprint("Invalid workspace name", "red")
            return errno.EINVAL
        failed = False
        upload_payload = BaseDatahub.find_fqs(input_dir, run_sheet)
        ret = []
        for payload in upload_payload:
            dst = upload_dst if upload_dst else payload.get('dst')
            result = self._upload(src=URL(payload.get('src')),
                                  dst=URL(dst),
                                  recursive=False,
                                  workspace=workspace,
                                  multiprocessing=multiprocessing,
                                  concurrency=concurrency,
                                  proxy=self.proxy)[0]
            result['metadata'] = payload.get('metadata')
            result['tags'] = payload.get('tags')
            if payload.get('id'):
                result['id'] = payload.get('id')
            ret.append(result)
            if result['status'] != 'complete':
                failed = True
        cprint(json.dumps(ret, indent=4), 'yellow')

        # use non-zero return code to indicate upload failed scenario
        if failed:
            return -1
        return 0

    @command(aliases=["patch"])
    @argument("workspace",
              type=str,
              positional=False,
              description="Specify the workspace based on the signed in account (required).")
    @argument("id",
              type=str,
              positional=True,
              description="Specify the DRS object ID (required).")
    @argument("name",
              type=str,
              positional=False,
              description="Specify the DRS object name (optional).")
    @argument("tags",
              type=List[str],
              positional=False,
              description="Locate a DRS object using a list of tags (optional).")
    @argument("metadata",
              type=dict,
              positional=False,
              description="Locate a DRS object using its metadata (optional).")
    @argument("checksum",
              type=str,
              positional=False,
              description="Locate a DRS object using the checksum (required when checksum_type is given).")
    @argument("checksum_type",
              type=str,
              positional=False,
              description="Locate a DRS object using the checksum type (required when checksum is given).",
              choices=['sha256'])
    @argument("updated_time",
              type=str,
              positional=False,
              description="Locate a DRS object using the timestamp of when an object was updated. "
                          "The time format must be in RFC3339. "
                          "For example, 2021-09-13 02:54:03.636044+00:00.")
    @argument("stdin",
              type=bool,
              positional=False,
              description="Locate a DRS object using the stdin mode (optional). "
                          "Selecting stdin prevents you from enabling any of "
                          "the other options and the json object must therefore contain all the required keys "
                          "[name, tags, metadata, checksum, checksum_type, updated_time].")
    def update(self, workspace: str, id: str, stdin: bool = False, **kwargs) -> int:
        """
         Update a DRS object.
        """
        if not workspace:
            cprint('Enter a valid workspace', 'red')
            return errno.EINVAL

        if stdin:
            if len(kwargs) > 0:
                cprint(f'Stdin mode not support {list(kwargs.keys())}')
                return errno.EINVAL
            else:
                kwargs = self._stdin()
                if len(kwargs) > 1:
                    cprint(f'Enter a valid Json not a list of Json.')
                    return errno.EINVAL
                kwargs = kwargs[0]
        kwargs['workspace'] = workspace

        def __log(results: dict):
            self._stdout(results=[results], output='json')
            msg = f"Register {results['id']}  is complete."
            logging.info(msg)

        results = self._change(id, **kwargs)
        if isinstance(results, int):
            return results
        __log(results=results)
        return 0

    @staticmethod
    @exception_handler
    def _change(object_id: str, **kwargs) -> dict:
        api_backend = drs_register().load_register(kwargs.get('workspace'))
        return api_backend.change(drs_id=object_id, **kwargs)

    @command(aliases=["retrieve"])
    @argument("workspace",
              type=str,
              positional=False,
              description="Specify the workspace based on the signed in account (required).")
    @argument("id",
              type=str,
              positional=True,
              description="drs object id.(Required)")
    def get(self, workspace: str, id: str) -> int:
        """
        Get a DRS object.
        """
        if not workspace:
            cprint('Enter a valid workspace', 'red')
            return errno.EINVAL

        def __log(results: dict):
            self._stdout(results=[results], output='json')
            msg = f"Get {results['id']}  completely."
            logging.info(msg)

        results = self._get(id, workspace)
        if isinstance(results, int):
            return results
        __log(results=results)
        return 0

    @staticmethod
    @exception_handler
    def _get(id: str, workspace: str):
        api_backend = drs_register().load_register(workspace)
        return api_backend.get_drs(drs_id=id)


@command
class Datahub(BaseDatahub):
    """Data Hub commands"""

    def __init__(self):
        super().__init__()
