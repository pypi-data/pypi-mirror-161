import re
from validators import url
from yarl import URL


class Base:

    @staticmethod
    def toolclass(name: str, description) -> dict:
        if description and not name:
            raise ValueError("toolclass_description can not be without toolclass_name")

        return {
            'name': name,
            'description': description
        } if description else {'name': name}

    @staticmethod
    def urlvalidator(url_URL: URL) -> str:
        url_string = str(url_URL)
        assert url(url_string), f"Enter a valid URL."
        return url_string

    @staticmethod
    def descriptor_type(descriptor_type: str) -> str:
        assert descriptor_type in ["CWL", "WDL", "NFL", "JNB"], f"Enter a valid descriptor_type."
        return descriptor_type

    @staticmethod
    def image(image_type: str, image_name: str, registry_host: str, size: int, checksum: str,
              checksum_type: str) -> dict:
        assert image_type.upper() in ["SINGULARITY", "DOCKER"], f"Enter a valid image_type."
        if image_type.upper() == "DOCKER":
            image_type = "Docker"
        elif image_type.upper() == "Singularity":
            image_type = "Singularity"
        return {
            "image_type": image_type,
            "image_name": image_name,
            "registry_host": registry_host,
            "size": size,
            "checksum": {
                "checksum": checksum,
                "type": checksum_type
            }
        }

    @staticmethod
    def version_id(version_id: str):
        if not isinstance(version_id, str):
            raise ValueError(f"Enter a valid version_id, version_id must be str.")
        version_id_re = re.compile(r'^\d+\.\d+(\.\d+)?$')
        assert version_id_re.match(
            version_id) is not None, f"Enter a valid version_id, version_id format is not correct"
        return version_id

    @staticmethod
    def file_type(file_type: str):
        assert file_type.upper() in ["TEST_FILE", "PRIMARY_DESCRIPTOR", "SECONDARY_DESCRIPTOR",
                                     "CONTAINERFILE", "EXECUTION_FILE", "OTHER"], \
            f"{file_type.upper()} invalid. Enter a valid file_type. "
        return file_type.upper()


class Template(Base):

    def __init__(self, trs_api):
        self.trs = trs_api

    def create(self, **kwargs) -> dict or list:
        assert self.trs in ['tool', 'toolversion', 'toolfile'], f"No such trs api"
        if self.trs == "tool":
            try:
                return Template.tool(
                    toolclass_name=kwargs.get("toolclass_name", None),
                    toolclass_description=kwargs.get("toolclass_description", None),
                    name=kwargs.get("tool_name", None),
                    description=kwargs.get("description", None),
                    aliases=kwargs.get("aliases", []),
                    checker_url=kwargs.get("checker_url", None),
                    has_checker=kwargs.get("has_checker", None),
                    id=kwargs.get("id", None)
                )
            except Exception as error:
                raise error
        elif self.trs == "toolversion":
            try:
                return Template.toolversion(
                    name=kwargs.get("version_name", None),
                    version_id=kwargs.get("version_id", None),
                    descriptor_type=kwargs.get("descriptor_type", None),
                    images=kwargs.get("images", []),
                    author=kwargs.get("author", []),
                    verified=kwargs.get("verified", False),
                    verified_source=kwargs.get("verified_source", []),
                    included_apps=kwargs.get("included_apps", []),
                    signed=kwargs.get("signed", False),
                    is_production=kwargs.get("is_production", False),
                )
            except Exception as error:
                raise error
        else:
            try:
                return Template.toolfile(toolfile_json=kwargs.get("toolfile_json", []))
            except Exception as error:
                raise error

    @staticmethod
    def tool(toolclass_name: str, toolclass_description: str, name: str, description: str, aliases: list,
             checker_url: str, has_checker: bool, id: str) -> dict:
        try:
            assert name is not None, f"Enter a valid tool_name"
            tool = {
                "name": name
            }
            if toolclass_name or toolclass_description:
                tool["toolclass"] = Base.toolclass(name=toolclass_name, description=toolclass_description)
            if description:
                tool["description"] = description
            if aliases:
                tool["aliases"] = aliases
            if has_checker:
                tool["has_checker"] = has_checker
            if id:
                id_validator = re.compile(r"^[0-9a-zA-Z\-\_]+$")
                assert id_validator.match(id), "Tool id allows only alphanumeric characters, hyphen,and underscore"
                tool["id"] = id
            if checker_url:
                try:
                    tool["checker_url"] = Base.urlvalidator(checker_url)
                except AssertionError as error:
                    raise AssertionError(f"checker_url: {error}")
        except Exception as error:
            raise error
        return tool

    @staticmethod
    def toolversion(name: str, version_id: str, descriptor_type: str, images: list,
                    author: list, verified_source: list, included_apps: list,
                    verified: bool, is_production: bool, signed: bool) -> dict:

        """
        :param: images
        images example:
        [
            {
              "image_type": "Docker",
              "image_name": "string",
              "registry_host": "string",
              "size": 0,
              "checksum": "type:checksum"
            }
        ]
        """
        validate_images = []
        name_list = []
        for element in images:
            if element['image_name'] in name_list:
                name_list.clear()
                raise ValueError(f"Enter unique image_name.")

            name_list.append(element['image_name'])
            validate_images.append(Base.image(**element))
        toolversion = {
            "images": validate_images,
            "version_id": Base.version_id(version_id=version_id),
            "descriptor_type": [Base.descriptor_type(descriptor_type=descriptor_type)],
            "is_production": is_production,
            "signed": signed
        }
        if name:
            toolversion["name"] = name
        toolversion.setdefault('author', author)
        toolversion.setdefault('verified', verified)
        toolversion.setdefault('verified_source', verified_source)
        toolversion.setdefault('included_apps', included_apps)
        return toolversion

    @staticmethod
    def toolfile(toolfile_json: list) -> list:
        """
        TODO: can add other checking ex: decription check, or data must include check
        """
        return toolfile_json


def get_template(trs):
    _template = Template(trs)
    return _template
