import errno
import json
import logging
import math
import os
import random
import time
import zipfile
from functools import lru_cache

import requests
from nubia import argument
from nubia import command
from nubia import context
from requests_toolbelt.multipart.encoder import MultipartEncoder
from seqslab.auth.commands import BaseAuth
from seqslab.runsheet.runsheet import RunSheet, Run
from seqslab.trs.register.common import trs_register
from seqslab.trs.register.base import TRSregister
from seqslab.wes import __version__, API_HOSTNAME
from tenacity import retry, wait_fixed, stop_after_attempt
from termcolor import cprint

from .internal.common import get_factory

from .template.base import WorkflowParamsTemplate, WorkflowBackendParamsTemplate, WorkflowBackendParamsClusterTemplate

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


class BaseJobs:
    WES_PARAMETERS_URL = f"https://{API_HOSTNAME}/wes/{__version__}/schedules/parameters/"
    OPERATOR_PIPELINE_URL = f"https://{API_HOSTNAME}/wes/{__version__}/operator-pipelines/{{pipeline_id}}/"

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
    @lru_cache(maxsize=16)
    def parameter(primary_descriptor: str, zip_file: str):
        token = BaseAuth.get_token().get('tokens').get('access')
        files = {'file': (f"{os.path.basename(zip_file)}",
                          open(zip_file, 'rb'),
                          'application/zip'),
                 "PRIMARY_DESCRIPTOR": ("", primary_descriptor)}
        with requests.patch(url=BaseJobs.WES_PARAMETERS_URL,
                            files=files,
                            headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(response.text)
            return json.loads(response.content)

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
    @lru_cache(maxsize=16)
    def get_operator_pipeline(pipeline_id: str):
        token = BaseAuth.get_token().get('tokens').get('access')
        with requests.patch(url=BaseJobs.OPERATOR_PIPELINE_URL.format(pipeline_id=pipeline_id),
                            headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError()
            return json.loads(response.content)

    @property
    def proxy(self) -> str:
        """web proxy server"""
        return context.get_context().args.proxy

    @argument("execs_json",
              type=str,
              description="Specify the absolute file path for execs.json. ")
    @argument("runtimes",
              type=str,
              description="Key:value pairs indicating workflow name -> SeqsLab supported runtime_options names. "
                          "Multiple configuration pairs can be provided with ':' as separator, "
                          "e.g. main=acu-m8:subworkflow=acu-m4 "
                          "(Default = None, indicating running the whole workflow.wdl using acu-m16 for "
                          "single node cluster on Azure backend).")
    @argument("integrity",
              type=bool,
              description="Specify whether to enable data and container runtime integrity check for the workflow "
                          "engine.(optional, default = False).")
    @argument("trust",
              type=bool,
              description="Specify whether to enable content trust for container runtime "
                          "(optional, default = False).")
    @argument("workspace",
              type=str,
              description="Specify the workspace based on the signed in account (required).")
    def _workflow_backend_params(self,
                                 execs_json: str,
                                 workspace: str,
                                 runtimes: str = None,
                                 integrity: bool = False,
                                 trust: bool = False,
                                 ) -> dict:
        """
        Create workflow_backend_params.json.
        """
        if not os.path.isfile(execs_json):
            cprint(f"{execs_json} does not exist", "red")
            return errno.ENOENT
        try:
            with open(execs_json, 'r') as f:
                execs = json.loads(f.read())
                workflow = execs.get('workflows')
                primary_obj = [item for item in workflow if item.get('file_type') == 'PRIMARY_DESCRIPTOR'][0]
                primary_workflow_name = primary_obj.get('workflow_name') if primary_obj.get(
                    'workflow_name') else primary_obj.get('name').replace('.wdl', '')
                call_names_list = execs.get('calls', None)
                # use sub-workflow names if no call section given
                if not call_names_list:
                    calls = [item.get('name').replace('.wdl', '') for item in workflow
                             if item.get('file_type') == 'SECONDARY_DESCRIPTOR'] + [primary_workflow_name]
                else:
                    calls = call_names_list
        except json.JSONDecodeError as error:
            cprint(f"{error}", "red")
            return errno.EPIPE

        rt_dict = {}
        if not runtimes:
            rt_dict = {primary_workflow_name: 'acu-m16'}
        else:
            rtcs = runtimes.split(':')
            for rtc in rtcs:
                c = rtc.split('=')
                rt_dict[c[0]] = c[1]

        resource = get_factory().load_resource(workspace)
        clusters = []
        for k, v in rt_dict.items():
            if k not in calls:
                raise RuntimeError(f'given call name {k} not in TRS registered call name list {calls}!')
            clusters.append(WorkflowBackendParamsClusterTemplate(run_time=resource.get_runtime_setting(v),
                                                                 workflow_name=k))

        bk_template = WorkflowBackendParamsTemplate(
            graph=execs.get('graph'),
            clusters=clusters,
            workspace=workspace,
            integrity=integrity,
            trust=trust,
        )
        return bk_template

    @command
    @argument("working_dir",
              type=str,
              positional=False,
              description="Specify the working directory path that contains request.json (required)."
              )
    @argument("response_path",
              type=str,
              positional=False,
              description="Specify the path of response.json in relation to the working directory (optional)."
              )
    @argument("workspace",
              type=str,
              description="Specify the workspace based on the signed in account (required).")
    def run(self,
            working_dir: str,
            workspace: str,
            response_path: str = 'response.json'
            ) -> int:
        """
        Run a workflow by calling seqslab-api/wes/runs API.
        """

        if not os.path.isdir(working_dir):
            logging.error("working dir is not a directory")
            cprint("working dir is not a directory", "red")
            return errno.EINVAL

        reqs = [os.path.join(working_dir, f) for f in os.listdir(working_dir) if
                os.path.isfile(os.path.join(working_dir, f)) and f.endswith('request.json')]

        run_list = []

        for value in enumerate(reqs):
            # add random delay, based on reqs.index for run submission to avoid overloading SeqsLab-API server
            if value[0]:
                floor = math.log((value[0] + 1), 2)
                step = (value[0] + 1) * 0.1
                time.sleep(random.uniform(floor, floor + step))

            try:
                with open(value[1], 'r') as f:
                    request = json.load(f)
            except json.decoder.JSONDecodeError as e:
                cprint(f"given request not in json format - {e}", "red")

            mp = MultipartEncoder(
                fields={
                    "name": request.get('name'),
                    "workflow_type": request.get('workflow_type'),
                    "workflow_type_version": request.get('workflow_type_version'),
                    "workflow_url": request.get('workflow_url'),
                    'workflow_params': json.dumps(request.get('workflow_params')),
                    'workflow_backend_params': json.dumps(request.get('workflow_backend_params'))
                }
            )
            resource = get_factory().load_resource(workspace)
            ret = resource.sync_run_jobs(data=mp,
                                         headers={'Content-Type': mp.content_type},
                                         run_request_id=None,
                                         run_name=request.get('name'))
            res = json.loads(ret.content.decode('utf-8'))
            res['run_name'] = request.get('name')
            run_list.append(res)
            cprint(f"{res}", "yellow")

        with open(os.path.join(working_dir, response_path), 'w') as f:
            json.dump(run_list, f, indent=4)
        return 0

    @command
    @argument("run_request_id",
              type=str,
              positional=False,
              description="Specify a previously scheduled run request ID (required). "
              )
    @argument("schedule_tag",
              type=str,
              positional=False,
              description="Specify a tag marked on previously uploaded samples for a scheduled job (required)."
              )
    @argument("workspace",
              type=str,
              description="Specify the workspace based on the signed in account (required).")
    def schedule(self,
                 run_request_id: str,
                 schedule_tag: str,
                 workspace: str
                 ) -> int:
        """
        Run a job based on a previously registered run request. Typically, the run request
        is designed for a scheduled job, where the FQN-DRS connection of sequencing samples
        are left blank for future runtime sample-resolving. Thus, by specifying a sample-resolving rule,
        the run request can be used to serve a scheduled job use case.
        """
        mp = MultipartEncoder(fields={})
        resource = get_factory().load_resource(workspace)
        ret = resource.sync_run_jobs(data=mp,
                                     headers={'Content-Type': mp.content_type},
                                     run_request_id=run_request_id,
                                     run_name=schedule_tag)
        cprint(f"{ret.content.decode('utf-8')}", "yellow")
        return 0

    @command(aliases=["state"])
    @argument("run_id",
              type=str,
              positional=False,
              description="Specify a previously executed WES run ID (required)."
              )
    @argument("workspace",
              type=str,
              description="Specify the workspace based on the signed in account (required).")
    def run_state(self, run_id: str, workspace: str) -> int:
        """
        Get WES run information based on run ID.
        """
        result = get_factory().load_resource(workspace).get_run_status(run_id)
        cprint(json.dumps(result), "yellow")

        return 0

    @argument("execs_json",
              type=str,
              description="The file path of execs.json. ")
    def _workflow_params(self, execs_json: str) -> dict:
        """
            Create workflow_params.json.
        """
        # TODO: write DRS id to workflow_params based run_sheet content
        if not os.path.isfile(execs_json):
            cprint(f"{execs_json} does not exist", "red")
            return errno.ENOENT

        try:
            with open(execs_json, 'r') as f:
                t_content = json.loads(f.read())

            params = WorkflowParamsTemplate().create(
                ex_template=t_content,
                api_hostname=API_HOSTNAME
            )
            return params
        except zipfile.BadZipfile as error:
            cprint(f"{error}", "red")
            return errno.EPIPE
        except json.JSONDecodeError as error:
            cprint(f"{error}", "red")
            return errno.EPIPE
        except KeyError as error:
            cprint(f"{error}", "red")
            return errno.ESRCH
        except LookupError as error:
            cprint(f"{error}", "red")
            return errno.ESRCH

    @command(aliases=["runsheet"])
    @argument("working_dir",
              type=str,
              description="Specify the absolute output directory for generated jobs params (required). ",
              aliases=["o"])
    @argument("run_sheet",
              type=str,
              description="Specify the absolute output path for Run Sheet (required). ",
              aliases=["r"])
    @argument("execs",
              type=str,
              description="Specify the execs.json needed for the create WES request.  If not given, the command will "
                          "get the execs.json from the TRS object specified by the workflow_url.  If given, the given "
                          "execs.json will be used to create all the WES run requests specified in the run_sheet "
                          "(optional, default = None).")
    @argument("integrity",
              type=bool,
              description="Specify whether to enable data and runtime integrity check for the workflow engine "
                          "(optional, default = False).")
    @argument("trust",
              type=bool,
              description="Specify whether to enable content trust for container runtime "
                          "(optional, default = False).")
    def request_runsheet(self,
                         working_dir: str,
                         run_sheet: str,
                         execs: str = None,
                         integrity: bool = False,
                         trust: bool = False,
                         ):
        """
        Parse run_sheet.csv and create a job execution request.json file for each job run.
        """
        if not os.path.isdir(working_dir):
            logging.error("working dir is not a directory")
            cprint("working dir is not a directory", "red")
            return errno.EINVAL
        run_sheet = RunSheet(run_sheet)
        for run in run_sheet.runs:
            self._runs_routine(run=run, working_dir=working_dir, execs=execs, integrity=integrity, trust=trust)
        return 0

    def _runs_routine(self, run: Run, working_dir: str, execs: str = None,
                      integrity: bool = False, trust: bool = False):
        execs_path = f'{working_dir}/{run.run_name}-execs.json'
        request_path = f'{working_dir}/{run.run_name}-request.json'
        wf_info = run.workflow_url.split('versions')[1].strip('/').split('/')

        if not execs:
            trs_register().load_resource().get_execs_json(
                workflow_url=run.workflow_url,
                download_path=execs_path
            )
        else:
            execs_path = f'{working_dir}/{execs}'

        params = self._workflow_params(execs_path)
        if not isinstance(params, dict):
            raise Exception(f'Unable to generate workflow_params based on given exec_path, with error code {params}')

        request = {
            "name": run.run_name,
            'workflow_params': params,
            'workflow_backend_params': self._workflow_backend_params(execs_path, run.runtimes, integrity, trust),
            'workflow_url': run.workflow_url,
            "workflow_type_version": wf_info[0],
            'workflow_type': wf_info[1],
        }
        with open(request_path, 'w') as f:
            json.dump(request, f, indent=4)

    @command
    @argument("run_name",
              type=str,
              description="Define the run name for a single run (required). ",
              aliases=["name"])
    @argument("working_dir",
              type=str,
              description="Specify the working directory that contains execs.json (required). ",
              aliases=["dir"])
    @argument("workflow_url",
              type=str,
              description="Specify a TRS URL used for a single run (required). ",
              aliases=["url"])
    @argument("execs",
              type=str,
              description="Specify the execs.json needed to create a WES request.  If not given, the command will "
                          "get the execs.json from the TRS object specified by the workflow_url "
                          "(optional, default = None).")
    @argument("runtimes",
              type=str,
              description="Key:value pairs indicating the workflow name -> SeqsLab supported runtime_options names. "
                          "Multiple configuration pairs can be provided using ':' as separator, "
                          "e.g. main=acu-m8:subworkflow=acu-m4 "
                          "(optional, default = None, which indicates running the whole workflow.wdl using acu-m16 for "
                          "a single node cluster on the Azure backend).")
    @argument("integrity",
              type=bool,
              description="Specify whether to enable data and runtime integrity check for the workflow engine "
                          "(optional, default = False).")
    @argument("trust",
              type=bool,
              description="Specify whether to enable content trust for container runtime "
                          "(optional, default = False).")
    def request(self, run_name: str, working_dir: str, workflow_url: str,
                execs=None, runtimes=None, integrity=False,
                trust=False):
        """
        Create WES run request.
        """
        if not os.path.isdir(working_dir):
            logging.error("working dir is not a directory")
            cprint("working dir is not a directory", "red")
            return errno.EINVAL
        single_run = Run(list(), run_name, workflow_url, runtimes)
        self._runs_routine(run=single_run, working_dir=working_dir, execs=execs, integrity=integrity, trust=trust)
        return 0

    @command
    @argument("run_id",
              type=str,
              positional=False,
              description="Specify a previously executed WES run ID (required)."
              )
    @argument("workspace",
              type=str,
              description="Specify the workspace based on the signed in account (required).")
    def get(self, run_id: str, workspace: str) -> int:
        """
        Get WES run information based on run ID.
        """
        result = get_factory().load_resource(workspace).get_run_id(run_id)
        cprint(json.dumps(result, indent=4), "yellow")

        return 0


@command
class Jobs(BaseJobs):
    """Workflow execution commands"""

    @command
    @argument("working_dir",
              type=str,
              positional=False,
              description="Specify the working directory path that contains request.json (required)."
              )
    @argument("workspace",
              type=str,
              description="Specify the workspace based on the signed in account (required).")
    def dryrun(self,
               working_dir: str,
               workspace:str
               ) -> int:
        """
        Workflow dry run to see if the given request.json files are properly configured by calling seqslab-api/wes/runs/dryrun and seqslab-api/wes/runs/files API.
        """
        if not os.path.isdir(working_dir):
            logging.error("working dir is not a directory")
            cprint("working dir is not a directory", "red")
            return errno.EINVAL

        reqs = [os.path.join(working_dir, f) for f in os.listdir(working_dir) if
                os.path.isfile(os.path.join(working_dir, f)) and f.endswith('request.json')]

        for value in enumerate(reqs):
            try:
                with open(value[1], 'r') as f:
                    request = json.load(f)
            except json.decoder.JSONDecodeError as e:
                cprint(f"given request not in json format - {e}", "red")

            # wes/${run_id}/dryrun
            mp = MultipartEncoder(
                fields={
                    "name": request.get('name'),
                    "workflow_type": request.get('workflow_type'),
                    "workflow_type_version": request.get('workflow_type_version'),
                    "workflow_url": request.get('workflow_url'),
                    'workflow_params': json.dumps(request.get('workflow_params')),
                    'workflow_backend_params': json.dumps(request.get('workflow_backend_params'))
                }
            )
            resource = get_factory().load_resource(workspace)
            dry_ret = resource.dry_run(data=mp,
                                       headers={'Content-Type': mp.content_type},
                                       run_request_id=None,
                                       run_name=request.get('name'))
            dry_res = json.loads(dry_ret.content.decode('utf-8'))

            # wes/${run_id}/files
            res = resource.wes_files(dry_res['run_id'])

            with open(os.path.join(working_dir, f'{dry_res["run_id"]}_files.json'), 'w') as f:
                json.dump(res, f, indent=4)

            cprint(f"{request.get('name')} verified with dryrun id {dry_res['run_id']}", "yellow")

        return 0
