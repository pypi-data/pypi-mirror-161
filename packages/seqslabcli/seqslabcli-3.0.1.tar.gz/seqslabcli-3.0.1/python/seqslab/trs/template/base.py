import pydot
from seqslab.wes.commands import BaseJobs

from .template import get_template


class TrsCreateTemplate:

    def create(self, inputs_json: dict, primary_descriptor: str, zip_file: str, **kwargs) -> dict:
        parameter = BaseJobs.parameter(primary_descriptor=primary_descriptor, zip_file=zip_file)
        workflow = self.desc_template(parameter)
        calls = self.call_template(parameter)
        inputs_connections = self.inputs_connections(parameter=parameter, inputs_json=inputs_json)
        return get_template().create(
            graph=parameter.get('graph'),
            inputs_connections=inputs_connections,
            inputs_json=inputs_json,
            parameters=parameter,
            workflow=workflow,
            calls=calls
        )

    @staticmethod
    def dot_cleaning(gs: str) -> str:
        import re
        rx = r';[\w;="]+'
        return re.sub(rx, "", gs)

    @staticmethod
    def add_nodes(graph: pydot.Dot) -> set:
        calls = set()
        for node in graph.get_nodes():
            if node.get_name().startswith('CALL_'):
                calls.add(node.get_name().replace('CALL_', ""))

        for subgraph in graph.get_subgraphs():
            for node in subgraph.get_nodes():
                if node.get_name().startswith('CALL_'):
                    calls.add(node.get_name().replace('CALL_', ""))
        return calls

    def call_template(self, parameter: dict) -> list:
        calls = [pydot.graph_from_dot_data(TrsCreateTemplate.dot_cleaning(parameter['graph']))[0].get_name()]
        for workflow in [parameter['calls'][v] for _, v in enumerate(parameter['calls'])]:
            for _, k in enumerate(workflow):
                calls += workflow[k]
        return calls

    def desc_template(self, parameter: dict):
        workflow = parameter['workflows']
        inputs_json = {"path": "inputs.json", "file_type": "TEST_FILE"}
        execs_tmp_json = {"path": "execs.json", "file_type": "EXECUTION_FILE"}
        workflow.append(inputs_json)
        workflow.append(execs_tmp_json)
        return workflow

    def _flat_list(self, v: list, r: list = [], layer: int = 1) -> dict:
        sub_v = []
        for element in v:
            if isinstance(element, list):
                sub_v.extend(element)
            else:
                r.append(element)
        if sub_v:
            layer += 1
            return self._flat_list(sub_v, r, layer)
        return {"list": r, "layer": layer}

    @staticmethod
    def operator_pipelines(parameter: dict) -> list:
        """
        :param: parameter: parameter API response
        :return:
            [{
                "fqn":"e2e.alignmentRun.Bwa.in_file_fastq_r1"
                "operators": {
                    "format": {
                        "class": "com.atgenomix.seqslab.piper.operators.GenericFormat"
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
            }]
        """
        return [{
            "fqn": k,
            "operators": pipeline['operators'],
            "pipelines": pipeline['pipelines']
        } for k, v in parameter['configs'].items()
            for pipeline in parameter['operator_pipelines'] if pipeline["id"] == v]

    @staticmethod
    def inputs_connections(parameter: dict, inputs_json: dict) -> list:
        """
        :param:
            parameter = parameter API response
            inputs_json = {
                "e2e.ref_sa": "local_path1",
                "e2e.primer_bedpe": "local_path2",
            }
        :return:
            input_connections = [{
                "fqn": "andyfqn",
                "local": [["local_path1","local_path2"]]
            },
            {
                "fqn": "andyfqn2",
                "local": ["local_path1"]
            }]
        """
        inputs = []
        inputs_json_keys = [k for k, v in inputs_json.items()]
        error_mapping = [k for k, v in parameter['inputs'].items()
                         if "optional" not in v and k not in inputs_json_keys]
        if 0 == len(error_mapping):
            for k, v in inputs_json.items():
                if k in parameter['inputs'] and "File" in parameter['inputs'][k]:
                    local_path = v
                    if not isinstance(v, list):
                        local_path = [v]
                    inputs.append(
                        {
                            "fqn": k,
                            "local": local_path,
                            "cloud": []
                        }
                    )
        else:
            error_mapping_str = ", ".join(error_mapping)
            raise LookupError(f'Keys: {error_mapping_str} do not exist in provided inputs.')
        return inputs


class TrsInfoTemplate:
    @staticmethod
    def create(primary_descriptor: str, zip_file: str) -> list:
        parameter = BaseJobs.parameter(primary_descriptor=primary_descriptor,
                                   zip_file=zip_file)
        return list(map(lambda x: {**x, **{'image_name': ""}} if x.get('type').find('DESCRIPTOR') != -1 else x,
                        parameter['workflow']))


class TrsImagesTemplate:
    @staticmethod
    def create(container_registry_info: dict) -> dict:
        image_list = []
        cr = container_registry_info.get('login_server')
        for repo in container_registry_info.get('repositories', []):
            name = repo.get('name')
            for tag in repo.get('tags'):
                pass
                image_list.append({
                    "image_type": tag.get('type'),
                    "image_name": f"{name}:{tag.get('name')}",
                    "registry_host": cr,
                    "size": tag.get('size'),
                    "checksum": tag.get('digest')
                })
        return image_list
