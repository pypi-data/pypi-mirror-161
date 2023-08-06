import os
import json
from sample_sheet import SampleSheet, Sample
from typing import Optional, Union, List
from pathlib import Path

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

"""
Wrapper WE2_TEMPLATE, in the format of:
{
    workflow_backend_params: {},
    operator_pipeline: [],
    cloud2local_mapping: [],
    inputs: {}
}

operator_pipeline includes a list of entries describing file handling configuration for each FQNs File, e.g.
    {
      "fqn": "actgGeneral.inFileRefSa",
      "operators": {
        "format": {
          "auth": "",
          "class": "com.atgenomix.seqslab.piper.operators.RegularFile"
        },
        "p_pipe": {
          "class": "com.atgenomix.seqslab.piper.operators.PPipe"
        }
      },
      "pipelines": {
        "call": [
          "format",
          "p_pipe"
        ]
      }
    }

cloud2local_mapping includes a list of entries describing DRS to local mapping, e.g.
    {
        "fqn": "actgGeneral.refSa",
        "cloud": ["drs://seqslabapi-dev.azurewebsites.net/drs_HfitIVV9Gwr6kzh"],
        "local": ["/anomegap2/seqslab/mnt/reference/19/HG/ref.fa.sa"]
    }

inputs includes FQN to local path mapping
"""


class AtgxTemplateContext:
    def __init__(self, template_path: str,) -> None:
        with open(template_path, 'r') as fp:
            self.template = json.load(fp)

    def get_inputs(self) -> dict:
        return self.template.get('inputs')

    def get_inputs_connection(self) -> dict:
        return self.template.get('inputs_connection')

    def get_operator_pipeline(self) -> list:
        return self.template.get('operator_pipeline')

    def get_trs_params(self) -> dict:
        return self.template.get('trs')


class SampleSheetWrapper:
    def __init__(self, sample_sheet_path: Optional[Union[Path, str]], fastq_path: str,) -> None:
        self.sample_sheet = SampleSheet(sample_sheet_path)
        self.fastq_path = fastq_path

    def filter_by_description(self, query: str) -> List[Sample]:
        ret = []
        for s in self.sample_sheet.samples:
            if s.Description.find(query) != -1:
                ret.append(s)
        return ret

    def get_experiment_name(self) -> str:
        return self.sample_sheet.Header.get('Experiment Name')

    @staticmethod
    def find_fastq_paths(sample: Sample, fastq_path: str) -> List[str]:
        return [os.path.join(root, f) for root, dirs, files in os.walk(fastq_path) for f in files
                if f.find(sample.Sample_ID) != -1 and f.find('fastq.gz') != -1]

    def get_default_tag(self, sample: Sample) -> str:
        return f"{self.sample_sheet.Header.get('Experiment Name')}/{sample.Sample_ID}"
