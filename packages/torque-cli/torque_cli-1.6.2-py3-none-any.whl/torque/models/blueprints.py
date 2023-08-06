from typing import Any, List

from torque.constants import BLUEPRINT_SOURCE_TYPE_API_MAP
from torque.base import Resource, ResourceManager


class Blueprint(Resource):
    def __init__(self, manager: ResourceManager, name: str, url: str, enabled: bool):
        super(Blueprint, self).__init__(manager)

        self.name = name
        self.url = url
        self.enabled = enabled

    @classmethod
    def json_deserialize(cls, manager: ResourceManager, json_obj: dict):
        try:
            # spec2 check
            if "details" in json_obj:
                json_obj = json_obj["details"]
            bp = Blueprint(
                manager,
                json_obj.get("blueprint_name", None) or json_obj.get("name", None),
                json_obj.get("url", None),
                json_obj.get("enabled", True),
            )
        except KeyError as e:
            raise NotImplementedError(f"unable to create object. Missing keys in Json. Details: {e}")

        # TODO(ddovbii): set all needed attributes
        bp.errors = json_obj.get("errors", [])
        bp.description = json_obj.get("description", "")
        bp.blueprint_source_type = json_obj.get("blueprint_source_type", "")
        return bp

    def json_serialize(self) -> dict:
        return {
            "name": self.name,
            "published": self.enabled,
            "source type": self.blueprint_source_type,
        }

    def table_serialize(self) -> dict:
        return {
            "name": self.name,
            "published": self.enabled,
            "source type": self.blueprint_source_type,
        }


class BlueprintsManager(ResourceManager):
    resource_obj = Blueprint

    def get(self, blueprint_name: str, source_type: str) -> Blueprint:
        bp_json = self._get_blueprint(blueprint_name, source_type)
        return Blueprint.json_deserialize(self, bp_json)

    def get_detailed(self, blueprint_name, source_type):
        return self._get_blueprint(blueprint_name, source_type)

    def _get_blueprint(self, blueprint_name, source_type):
        url = f"catalog/{blueprint_name}"
        query = None
        api_source_type = BLUEPRINT_SOURCE_TYPE_API_MAP.get(source_type, None)
        if api_source_type:
            query = {"blueprint_source_type": api_source_type}
        return self._get(url, query_params=query)

    def list(self) -> List[Blueprint]:
        url = "blueprints"
        result_json = self._list(path=url)
        return [self.resource_obj.json_deserialize(self, obj) for obj in result_json]

    def list_detailed(self) -> Any:
        url = "blueprints"
        result_json = self._list(path=url)
        return result_json

    def validate(self, blueprint: str, env_type: str = "sandbox", branch: str = None, commit: str = None) -> Blueprint:
        url = "validations/blueprints"
        params = {"blueprint_name": blueprint, "type": env_type}

        if commit and branch in (None, ""):
            raise ValueError("Since commit is specified, branch is required")

        if branch:
            params["source"] = {
                "branch": branch,
            }
            params["source"]["commit"] = commit or ""

        result_json = self._post(url, params)
        result_bp = Blueprint.json_deserialize(self, result_json)
        return result_bp
