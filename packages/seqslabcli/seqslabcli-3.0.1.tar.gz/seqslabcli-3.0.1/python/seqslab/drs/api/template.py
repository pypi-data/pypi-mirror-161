from yarl import URL
import re
from typing import List


class Template:

    def __init__(self, drs_type):
        self.drs_type = drs_type

    def patch(self, **kwargs):
        common = {}
        for k, v in kwargs.items():
            if k == 'checksums' and v:
                common[k] = self.checksums(checksums=v)
            elif v:
                common[k] = v
            else:
                continue
        if not common:
            raise ValueError(f'Enter a valid patch template. There is nothing to patch.')
        return common

    def create(self, name: str, mime_type, file_type: str, size=None, created_time=None,
               access_methods=None, checksums=None, **kwargs) -> dict:
        """
        :blob param: name, mimetype, file_type, description, created_time, aliases, metadata,
                     tags, size, access_method, checksum
        :bundle param: name, mimetype, file_type, description,  aliases, metadata, tags, contents
        :return: dict format for DRS api
        """
        if not name or not mime_type or not file_type:
            raise ValueError(f'Make sure name, mime_type and file_type are given.')
        common = {
            "name": name,
            "mime_type": mime_type,
            "file_type": file_type,
        }
        if kwargs:
            for k, v in kwargs.items():
                if v:
                    common[k] = v

        assert self.drs_type in ["blob", "bundle"], 'Enter a valid drs type in ["blob", "bundle"].'
        if self.drs_type == "bundle":
            try:
                contents = kwargs.get("contents")
                common['contents'] = Template.contents(contents)
            except Exception as error:
                raise error
        else:
            common['access_methods'] = self.access_methods(access_methods=access_methods)
            if not common['access_methods']:
                raise ValueError(f'{name}: access_method is Null')
            common['size'] = self.size(size)
            if not common['size']:
                raise ValueError(f'{name}: Make sure the size is not Null')
            elif common['size'] == -1:
                raise ValueError(f'{name}: Make sure the size can not be smaller than 0')
            common["created_time"] = self.time(created_time)
            if not common["created_time"]:
                raise ValueError(f'{name}: Make sure the time is exist and the format must in RFC3339')
            if kwargs.get("updated_time"):
                common["updated_time"] = self.time(kwargs.get("updated_time"))
            common["checksums"] = self.checksums(checksums=checksums)
            if not common["checksums"]:
                raise ValueError(f'{name}: Make sure the checksum format is correct.')
        return common

    @staticmethod
    def contents(contents: list) -> List[dict]:
        return [{"drs_id":id} for id in contents]

    @staticmethod
    def access_methods(access_methods: List[dict]) -> List[dict]:
        if access_methods:
            for access_method in access_methods:
                for k, v in access_method.items():
                    if k in ['type', 'access_tier', 'region', 'access_url']:
                        if k == 'access_url':
                            assert v.get('url'), f"access_url: url must exist."
                            if v.get('url'):
                                v['url'] = str(v['url'])
                            if v.get('headers'):
                                if not v.get('headers').get('Authorization'):
                                    v['headers'] = {}
                            else:
                                v['headers'] = {}
                        if k == 'type':
                            assert v in ['s3', 'abfss', 'gs', 'htsget', 'https', 'file'], \
                                f"access_url scheme type must in ['s3', 'abfss', 'gs', 'htsget', 'https', 'file']"
            return access_methods

    @staticmethod
    def size(size: int) -> int:
        if size < 0:
            return -1
        return size

    @staticmethod
    def time(time: str) -> str:
        datetime_re = re.compile(
            r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
            r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
            r'(?::(?P<second>\d{1,2})(?:[\.,](?P<microsecond>\d{1,6})\d{0,6})?)?'
            r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
        )
        if datetime_re.match(time) is not None:
            return time

    @staticmethod
    def checksums(checksums: List[dict]) -> list:
        for checksum in checksums:
            try:
                int(checksum.get('checksum'), 16)
                if not checksum.get('type') and checksum.get('checksum_type'):
                    checksum['type'] = checksum['checksum_type']
                    checksum.pop('checksum_type')
                return checksums
            except Exception as error:
                raise ValueError(f'checksums is not in correct format')


def get_template(drs_type=None):
    _template = Template(drs_type)
    return _template
