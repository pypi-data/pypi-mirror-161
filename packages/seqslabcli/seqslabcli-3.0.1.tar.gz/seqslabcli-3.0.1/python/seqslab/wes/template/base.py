class WorkflowParamsTemplate:

    def create(self, api_hostname: str, ex_template: dict) -> dict:
        inputs = ex_template.copy()
        inputs.pop('connections')
        inputs.pop('workflows')
        inputs.pop('configs')
        inputs.pop('operator_pipelines')
        inputs.pop('calls')
        inputs.pop('graph', None)

        inputs_connections = self.inputs_connections(inputs_connection=ex_template.get('connections', None))
        operator_pipelines = self.operator_pipelines(ex_template)

        inputs.update({"inputs": inputs_connections + operator_pipelines})
        return inputs

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
    def operator_pipelines(ex_template: dict) -> list:
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
            "pipelines": pipeline['pipelines'],
            "description": pipeline['description'],
        } for k, v in ex_template['configs'].items()
            for pipeline in ex_template['operator_pipelines'] if pipeline["id"] == v]

    @staticmethod
    def inputs_connections(inputs_connection: list = None) -> list:
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
        for item in inputs_connection:
            v = item.get('cloud', None)
            if v:
                if not isinstance(v, list):
                    item['cloud'] = [v]
                else:
                    ret1 = []
                    for e1 in v:
                        if not isinstance(e1, list):
                            ret1.append(e1)
                        else:
                            ret2 = []
                            for e2 in e1:
                                if not isinstance(e2, list):
                                    ret2.append(e2)
                                else:
                                    raise Exception(f'More than 3 layer of list is provided {v}')
                            ret1.append(ret2)
                    item['cloud'] = ret1
        return inputs_connection


def WorkflowBackendParamsTemplate(graph: str, clusters: list, workspace: str, integrity: bool, trust: bool) -> dict:
    ret = {
            "clusters": clusters,
            "workspace": workspace,
            "integrity": integrity,
            "content_trust": trust
    }
    if graph:
        ret.update({'graph': graph})
    return ret


def WorkflowBackendParamsClusterTemplate(run_time: dict, workflow_name: str) -> dict:
    run_time.update({'call': workflow_name})
    return run_time
