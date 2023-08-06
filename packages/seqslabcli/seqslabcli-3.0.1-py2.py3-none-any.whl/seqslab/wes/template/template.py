import json
from yarl import URL
import re


class Base:
    @staticmethod
    def url(url: str) -> str:
        ul = '\u00a1-\uffff'  # Unicode letters range (must not be a raw string).
        # IP patterns
        ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
        ipv6_re = r'\[[0-9a-f:.]+\]'  # (simple regex, validated later)
        # Host patterns
        hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'
        # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
        domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'
        tld_re = (
                r'\.'  # dot
                r'(?!-)'  # can't start with a dash
                r'(?:[a-z' + ul + '-]{2,63}|xn--[a-z0-9]{1,59})'  # domain label or punycode label
                                  r'(?<!-)'  # can't end with a dash
                                  r'\.?'  # may have a trailing dot
        )
        host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'
        url_re = re.compile(
            r'^(?:[a-z0-9.+-]*)://'  # scheme is validated separately
            r'(?:[^\s:@/]+(?::[^\s:@/]*)?@)?'  # user:pass authentication
            r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
                                                               r'(?::\d{2,5})?'  # port
                                                               r'(?:[/?#][^\s]*)?'  # resource path
                                                               r'\Z', re.IGNORECASE)

        assert url_re.match(url) is not None, f"Enter a valid URL."
        return url

    @staticmethod
    def operator_pipeline(operator_pipelines: list) -> list:
        return operator_pipelines

    @staticmethod
    def inputs_connection(fqn: str, local: list, cloud: list) -> dict:
        assert fqn is not None, f"Enter a valid fqn."
        inputs_connections = {
            "fqn": fqn,
            "local": local
        }
        if cloud:
            inputs_connections["cloud"] = cloud

        return inputs_connections

    @staticmethod
    def inputs(inputs_json: dict) -> dict:
        return inputs_json


class Template(Base):

    @staticmethod
    def create(inputs_connections: list, inputs_json: dict, operator_pipelines: list) -> dict:
        inputs_connection = []
        for connection in inputs_connections:
            try:
                inputs_connection.append(
                    Base.inputs_connection(
                        fqn=connection['fqn'],
                        cloud=connection['cloud'],
                        local=connection['local']
                    )
                )
            except KeyError:
                inputs_connection.append(
                    Base.inputs_connection(
                        fqn=connection['fqn'],
                        cloud=[],
                        local=connection['local']
                    )
                )
        return {
            "operator_pipeline": operator_pipelines,
            "inputs_connection": inputs_connection,
            "inputs": inputs_json
        }


def get_template():
    _template = Template()
    return _template
