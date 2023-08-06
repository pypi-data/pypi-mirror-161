# cli code
import uuid
from os.path import abspath, dirname
# python module
from unittest.mock import patch

import arrow
from seqslab.runsheet.runsheet import RunSheet, Run
from seqslab.trs.register.azure import AzureTRSregister
# cli code
from seqslab.wes.commands import BaseJobs
from seqslab.wes.resource.azure import AzureResource


def random_string(char_num: int = 25):
    if char_num <= 16:
        return uuid.uuid4().hex[:char_num]
    total_acc = char_num - 16
    random_str = ''
    while total_acc > 0:
        random_str += uuid.uuid4().hex[:total_acc]
        total_acc -= 32
    return random_str + str(int(arrow.utcnow().timestamp() * 1000000))


run_request_id = uuid.uuid4().hex
run_id = uuid.uuid4().hex
wes_data_location = f'{dirname(abspath(__file__))}'
working_dir = f'{wes_data_location}/working-dir/'
fixture_run_name = '2022-03-30_HCG398_BGZF'
fixture_run_sheet_csv = f'{working_dir}request-runsheet/run_info_398-fixture.csv'
fixture_execs_fixture_json = '2022-03-30_HCG398_BGZF-execs-fixture.json'
ans_request_json = f'{working_dir}request/2022-03-30_HCG398_BGZF-request-fixture.json'
ans_request_runsheet_json = f'{working_dir}request-runsheet/2022-03-30_HCG398_BGZF-request-fixture.json'
host_name = "dev-api.seqslab.net"
tool_id = "trs_test_4QLix7cSvY"
run_name = random_string()
workflow_url = f"https://{host_name}/trs/v2/tools/{tool_id}/versions/1.0/WDL/files/"


class MockResource(AzureResource):

    def get_run_id(self, run_id) -> dict:
        run_state = "UNKNOWN"
        content = {
            "id": run_id,
            "name": run_name,
            "outputs": [],
            "logs": [],
            "state": run_state,
            "request": {
                "id": 11350,
                "name": run_name,
                "description": None,
                "workflow_type": "WDL",
                "workflow_type_version": "1.0",
                "workflow_params": {
                    "inputs": [
                        {
                            "fqn": "NIPT.refBwt",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.fasta.bwt"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.bwt"
                            ]
                        },
                        {
                            "fqn": "NIPT.refAmb",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.fasta.amb"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.amb"
                            ]
                        },
                        {
                            "fqn": "NIPT.refFa",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.fasta"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.fasta"
                            ]
                        },
                        {
                            "fqn": "NIPT.inputReference",
                            "cloud": [
                                "mnt/storage/reference/RAPIDR_reference/NSBRef200N_GC.RData",
                                "mnt/storage/reference/RAPIDR_reference/NSBRef200N.RData"
                            ],
                            "local": [
                                "/mnt/storage/reference/RAPIDR_reference/NSBRef200N_GC.RData",
                                "/mnt/storage/reference/RAPIDR_reference/NSBRef200N.RData"
                            ]
                        },
                        {
                            "fqn": "NIPT.inFileSpecificRegion",
                            "cloud": [
                                "mnt/storage/reference/ref_doc/Specific_region_new.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/ref_doc/Specific_region_new.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.inFileRegion",
                            "cloud": [
                                "mnt/storage/reference/ref_doc/20K.region.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/ref_doc/20K.region.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.inFileGcContent",
                            "cloud": [
                                "mnt/storage/reference/ref_doc/gcContent.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/ref_doc/gcContent.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.refPac",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.fasta.pac"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.pac"
                            ]
                        },
                        {
                            "fqn": "NIPT.inFileCallSexPostiveZxZy",
                            "cloud": [
                                "mnt/storage/reference/ref_doc/callSex_postive_zXzY.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/ref_doc/callSex_postive_zXzY.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.inputBaseline",
                            "cloud": [
                                "mnt/storage/reference/RAPIDR_reference/NSBRef200N_GC_binned.ratio.per.region.csv",
                                "mnt/storage/reference/RAPIDR_reference/NSBRef200N_binned.ratio.per.region.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/RAPIDR_reference/NSBRef200N_GC_binned.ratio.per.region.csv",
                                "/mnt/storage/reference/RAPIDR_reference/NSBRef200N_binned.ratio.per.region.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.refAnn",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.fasta.ann"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.ann"
                            ]
                        },
                        {
                            "fqn": "NIPT.refSa",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.fasta.sa"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.sa"
                            ]
                        },
                        {
                            "fqn": "NIPT.inFileDataDivide",
                            "cloud": [
                                "mnt/storage/reference/ref_doc/NIPT_data_divid_by_chr_addcounts_autoscan.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/ref_doc/NIPT_data_divid_by_chr_addcounts_autoscan.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.inFileBrks",
                            "cloud": [
                                "mnt/storage/reference/ref_doc/brks.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/ref_doc/brks.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.inFileZxZyCase",
                            "cloud": [
                                "mnt/storage/reference/ref_doc/zXzY_case.csv"
                            ],
                            "local": [
                                "/mnt/storage/reference/ref_doc/zXzY_case.csv"
                            ]
                        },
                        {
                            "fqn": "NIPT.refDict",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.dict"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.dict"
                            ]
                        },
                        {
                            "fqn": "NIPT.inputRead",
                            "cloud": [],
                            "local": [
                                "/mnt/storage/NextSeq550/2021_11_23/FASTQ/21110518_S15_R1_001.fastq.gz"
                            ]
                        },
                        {
                            "fqn": "NIPT.rGcContentRdata",
                            "cloud": [
                                "mnt/storage/reference/RAPIDR_reference/gcContent.RData"
                            ],
                            "local": [
                                "/mnt/storage/reference/RAPIDR_reference/gcContent.RData"
                            ]
                        },
                        {
                            "fqn": "NIPT.refFaFai",
                            "cloud": [
                                "mnt/storage/reference/bwa-index_hg19/hg19.fasta.fai"
                            ],
                            "local": [
                                "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.fai"
                            ]
                        },
                        {
                            "fqn": "NIPT.AutoScan.inFileDataDivide",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.AutoScan.inFileSpecificRegion",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.AutoScan.inFileZscorePerRegion",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bin.inFileBam",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.inFileFastq",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.refAmb",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.refAnn",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.refBwt",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.refFa",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.refFaFai",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.refPac",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Bwa.refSa",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.CNVScan.inFileBaseline",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.CNVScan.inFileBinnedCountsExclBins",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.CNVScan.inFileRegion",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.CNVScan.inFileSpecificRegion",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.DP1WithMNV.inFileVcfGz",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.DP30WithMNV.inFileVcfGz",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FFOnlySnpGC.inFileBrks",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FFOnlySnpGC.inFileGcContent",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FFOnlySnpGC.inFileVCF",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FFOnlySnpGC2DB.inFileVCF",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FFSnp.inFileVCF",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FilterMutectCalls.inFileVcfGz",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FilterMutectCalls.inFileVcfStats",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FilterMutectCalls.inFileVcfTbi",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FilterMutectCalls.refDict",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.FilterMutectCalls.refFaFai",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Mutect2.inFileBam",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Mutect2.refDict",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Mutect2.refFa",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.Mutect2.refFaFai",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.RAPIDR.inFileBin",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.RAPIDR.inFileGcContentRdata",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.RAPIDR.inFileRefRdata",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.ReadCount.inFileBam",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.ReadCount.inFileStats",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.SamtoolsFilter.inFileBam",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.SamtoolsStats.inFileBam",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.ZxZyPlot.inFileCallSexPostiveZxZy",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.ZxZyPlot.inFileTestResults",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        },
                        {
                            "fqn": "NIPT.ZxZyPlot.inFileZxZyCase",
                            "operators": {
                                "format": {
                                    "class": "com.atgenomix.seqslab.piper.operators.format.SingularFormat"
                                },
                                "p_pipe": {
                                    "class": "com.atgenomix.seqslab.piper.operators.pipe.PPipe"
                                }
                            },
                            "pipelines": {
                                "call": [
                                    "format",
                                    "p_pipe"
                                ]
                            }
                        }
                    ],
                    "NIPT.refFa": "/mnt/storage/reference/bwa-index_hg19/hg19.fasta",
                    "NIPT.refPac": "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.pac",
                    "NIPT.sampleType": "NIPT",
                    "NIPT.inputRead": "/mnt/storage/NextSeq550/2021_11_23/FASTQ/21110518_S15_R1_001.fastq.gz",
                    "NIPT.refSa": "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.sa",
                    "NIPT.refAnn": "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.ann",
                    "NIPT.barcode": "~{NIPT.inputRead:sample.Order_Overall}",
                    "NIPT.refBwt": "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.bwt",
                    "NIPT.inFileZxZyCase": "/mnt/storage/reference/ref_doc/zXzY_case.csv",
                    "NIPT.rGcContentRdata": "/mnt/storage/reference/RAPIDR_reference/gcContent.RData",
                    "NIPT.folderBin": "bin/",
                    "NIPT.inputBaseline": [
                        "/mnt/storage/reference/RAPIDR_reference/NSBRef200N_GC_binned.ratio.per.region.csv",
                        "/mnt/storage/reference/RAPIDR_reference/NSBRef200N_binned.ratio.per.region.csv"
                    ],
                    "NIPT.inFileGcContent": "/mnt/storage/reference/ref_doc/gcContent.csv",
                    "NIPT.refFaFai": "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.fai",
                    "NIPT.folderNIPT": "NIPT2.0/",
                    "NIPT.outPathAutoScan": "NIPT2.0/NSBRef200N_GC/AutoScan/",
                    "NIPT.inFileDataDivide": "/mnt/storage/reference/ref_doc/NIPT_data_divid_by_chr_addcounts_autoscan.csv",
                    "NIPT.inFileSpecificRegion": "/mnt/storage/reference/ref_doc/Specific_region_new.csv",
                    "NIPT.folderRAPIDR": "RAPIDR/",
                    "NIPT.heapSizeInGb": "5",
                    "NIPT.plate": "NextSeq550",
                    "NIPT.inFileBrks": "/mnt/storage/reference/ref_doc/brks.csv",
                    "NIPT.refDict": "/mnt/storage/reference/bwa-index_hg19/hg19.dict",
                    "NIPT.inFileRegion": "/mnt/storage/reference/ref_doc/20K.region.csv",
                    "NIPT.refAmb": "/mnt/storage/reference/bwa-index_hg19/hg19.fasta.amb",
                    "NIPT.runDate": "~{NIPT.inputRead:header.Date}",
                    "NIPT.inFileCallSexPostiveZxZy": "/mnt/storage/reference/ref_doc/callSex_postive_zXzY.csv",
                    "NIPT.inputReference": [
                        "/mnt/storage/reference/RAPIDR_reference/NSBRef200N_GC.RData",
                        "/mnt/storage/reference/RAPIDR_reference/NSBRef200N.RData"
                    ],
                    "NIPT.sampleName": "~{NIPT.inputRead:sample.Sample_ID}"
                },
                "workflow_backend_params": {
                    "workspace": "seqslabwu2",
                    "clusters": [
                        {
                            "id": 2,
                            "call": "NIPT",
                            "name": "acu-m8",
                            "description": "Memory optimized 8-core cluster compute (Runtime 2.0, Spark 3.3, Python 3.8, Java 1.8.0, Cromwell 63)",
                            "settings": {
                                "type": "batch.core.windows.net",
                                "vm_size": "Standard_D13_v2",
                                "workers": {
                                    "spot": 0,
                                    "dedicated": 1
                                },
                                "auto_scale": False,
                                "worker_on_master": True
                            },
                            "options": [
                                "spark.driver.cores 1",
                                "spark.driver.memory 536870912",
                                "spark.executor.cores 1",
                                "spark.executor.memory 7g",
                                "spark.dynamicAllocation.enabled true",
                                "spark.shuffle.service.enabled true",
                                "spark.dynamicAllocation.minExecutors 1",
                                "spark.kryo.registrator org.bdgenomics.adam.serialization.ADAMKryoRegistrator",
                                "spark.local.dir /mnt"
                            ]
                        }
                    ],
                    "integrity": True,
                    "content_trust": False,
                    "debug_mode": True
                },
                "workflow_url": workflow_url,
                "tags": []
            },
            "start_time": None,
            "end_time": None
        }

        return content

    def get_run_status(self, run_id) -> dict:
        run_state = "UNKNOWN"
        return {
            "run_id": run_id,
            "state": run_state
        }

    def sync_run_jobs(self, data, headers, run_request_id, run_name, retries=5):
        class ReturnR:
            def __init__(self, data):
                self.data = data

            @property
            def content(self):
                return str({}).encode('utf-8')

        response = ReturnR(data=headers)
        return response


class MockTrsResource(AzureTRSregister):
    # trs mock
    @staticmethod
    def get_execs_json(workflow_url: str, download_path: str):
        pass


class MockJobs(BaseJobs):
    """
    Mock Job commands
    """

    def _workflow_backend_params(self,
                                 exec_json: str,
                                 runtimes: str = None,
                                 integrity: bool = False,
                                 trust: bool = False,
                                 ) -> dict:
        return {
            "graph": "digraph GermlineSnpsIndelsGatk4 {\n  #rankdir=LR;\n  compound=true;\n\n  # Links\n  CALL_PreProcessingForVariantDiscovery_GATK4 -> CALL_GenotypeGVCFs\n  CALL_HaplotypeCallerGvcf_GATK4 -> CALL_GenotypeGVCFs\n  CALL_PreProcessingForVariantDiscovery_GATK4 -> CALL_HaplotypeCallerGvcf_GATK4\n  CALL_PreProcessingForVariantDiscovery_GATK4 -> CALL_IndexBam\n\n  # Nodes\n  CALL_GenotypeGVCFs [label=\"call GenotypeGVCFs\"]\n  CALL_PreProcessingForVariantDiscovery_GATK4 [label=\"call PreProcessingForVariantDiscovery_GATK4\";shape=\"oval\";peripheries=2]\n  CALL_HaplotypeCallerGvcf_GATK4 [label=\"call HaplotypeCallerGvcf_GATK4\";shape=\"oval\";peripheries=2]\n  CALL_IndexBam [label=\"call IndexBam\"]\n}",
            "clusters": [
                {
                    "id": 2,
                    "name": "acu-m8",
                    "description": "Memory optimized 8-core cluster compute (Runtime 2.0, Spark 3.3, Python 3.8, Java 1.8.0, Cromwell 63)",
                    "settings": {
                        "type": "batch.core.windows.net",
                        "vm_size": "Standard_D13_v2",
                        "workers": {
                            "spot": 0,
                            "dedicated": 1
                        },
                        "auto_scale": False,
                        "worker_on_master": True
                    },
                    "options": [
                        "spark.driver.cores 1",
                        "spark.driver.memory 2g",
                        "spark.executor.cores 1",
                        "spark.executor.memory 9g",
                        "spark.dynamicAllocation.enabled true",
                        "spark.shuffle.service.enabled true",
                        "spark.dynamicAllocation.minExecutors 1",
                        "spark.kryo.registrator org.bdgenomics.adam.serialization.ADAMKryoRegistrator",
                        "spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version 2",
                        "spark.local.dir /mnt"
                    ],
                    "call": "GermlineSnpsIndelsGatk4"
                }
            ],
            "workspace": "test",
            "integrity": integrity,
            "trust": trust
        }


class MockRunSheet(RunSheet):
    def __init__(self, path=None) -> None:
        self._runs = []
        self._parse_run()


class MockRun(Run):
    def __init__(self, path=None) -> None:
        self._runs = []
        self._parse_run()


job_patch = patch('seqslab.wes.commands.Jobs', MockJobs)
resource_patch = patch('seqslab.wes.resource.base.BaseResource', MockResource)
resource_trs_patch = patch('seqslab.trs.register.azure.AzureTRSregister', MockTrsResource)

run_sheet_patch = patch('seqslab.runsheet.runsheet.RunSheet', MockRunSheet)
run_patch = patch('seqslab.runsheet.runsheet.kRun', MockRun)
from unittest import TestCase
from seqslab.tests.util import TestShell


class BasicTest(TestCase):
    mock_command = MockJobs()
    workspace = 'test'
    shell = TestShell

    @staticmethod
    def get_loop():
        import asyncio
        # because there are no current event loop in thread 'MainThread' in pytest, we need to add the loop to initial new loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        except:
            pass


@job_patch
@resource_patch
class CommandSpecTest(BasicTest):

    def test_get_run_info(self):
        self.get_loop()
        run_id = 'run_' + random_string(15)
        shell = self.shell(commands=[self.mock_command.get])
        exit_code = shell.run_cli_line(f"test_shell get --run-id {run_id} --workspace test")
        assert exit_code == 0

    def test_run(self):
        shell = self.shell(commands=[self.mock_command.run])
        exit_code = shell.run_cli_line(f"test_shell run --working-dir {working_dir} --workspace test")
        assert exit_code == 0

    def test_schedule(self):
        self.get_loop()
        shell = self.shell(commands=[self.mock_command.schedule])
        exit_code = shell.run_cli_line(f"test_shell schedule --run-request-id {run_request_id} "
                                       f"--schedule-tag {run_request_id} --workspace test")
        assert exit_code == 0

    def test_run_state(self):

        self.get_loop()
        shell = self.shell(commands=[self.mock_command.run_state])
        exit_code = shell.run_cli_line(f"test_shell run-state --run-id {run_id} --workspace test")
        assert exit_code == 0


@job_patch
@resource_patch
@resource_trs_patch
class CreateJobsTest(BasicTest):
    mock_command = MockJobs()

    @staticmethod
    def req_validate(query_path, ans_path):
        import json
        with open(query_path, 'r') as f:
            query_json = json.load(f)
        with open(ans_path, 'r') as f:
            ans_json = json.load(f)
        TestCase().assertDictEqual(query_json, ans_json)

    def test_request_runsheet(self):
        self.get_loop()
        shell = self.shell(commands=[self.mock_command.request_runsheet])
        exit_code = shell.run_cli_line(
            f"test_shell request-runsheet --run-sheet {fixture_run_sheet_csv} --working-dir "
            f"{working_dir}request-runsheet --execs {fixture_execs_fixture_json}")
        self.req_validate(f'{working_dir}request-runsheet/{fixture_run_name}-request.json', ans_request_runsheet_json)
        assert exit_code == 0

    def test_request(self):
        self.get_loop()
        shell = self.shell(commands=[self.mock_command.request])
        exit_code = shell.run_cli_line(
            f"test_shell request --workflow-url {workflow_url} --run-name {fixture_run_name} "
            f"--working-dir {working_dir}request --execs {fixture_execs_fixture_json}")
        self.req_validate(f'{working_dir}request/{fixture_run_name}-request.json', ans_request_json)
        assert exit_code == 0


if __name__ == "__main__":
    test = CommandSpecTest()
    test.setUp()
    test.test_get_run_info()
    test.test_schedule()
    test.test_run()
    test.test_run_state()

    job_test = CreateJobsTest()
    job_test.test_request()
    job_test.test_request_runsheet()
