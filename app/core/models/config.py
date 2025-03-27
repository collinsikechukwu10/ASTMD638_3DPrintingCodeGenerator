import json
from typing import Union, List, Any

from pydantic import BaseModel

from app.core.enums import ConfigType
from app.core.exceptions import ConfigTypeNotFoundError
from app.utils import label_formatter, load_json_file


class BaseConfigValue(BaseModel):
    type: ConfigType
    name: str
    initial_value: Union[int, float, bool, str]
    description: str = ""

    @property
    def config_label(self):
        return label_formatter(self.name)


class BooleanConfig(BaseConfigValue):
    initial_value: bool


class NumericConfig(BaseConfigValue):
    initial_value: Union[int, float]
    min_value: Union[int, float] = None
    max_value: Union[int, float] = None
    step: Union[int, float] = None


class CategoricalConfig(BaseConfigValue):
    choices: List[Union[int, float, str]]

    def model_post_init(self, __context: Any) -> None:
        if self.initial_value not in self.choices:
            raise ValueError(
                f"Initial value `{self.initial_value}` not included in the choices provided: {','.join(self.choices)} for field {self.name}")


class GCodeSettingSection(BaseModel):
    section_name: str
    fields: List[BaseConfigValue] = list()


class GcodeSettings(BaseModel):
    sections: List[GCodeSettingSection]
    _session = None

    def default_values(self):
        return {field.name: field.initial_value for section in self.sections for field in section.fields}

    @staticmethod
    def get_config_value_from_dict(config_object: dict):
        type_ = ConfigType.get_config_type(config_object.get("type", None))
        if type_ is ConfigType.NUMERIC:
            return NumericConfig(**config_object)
        elif type_ is ConfigType.BOOLEAN:
            return BooleanConfig(**config_object)
        elif type_ is ConfigType.CATEGORICAL:
            return CategoricalConfig(**config_object)
        else:
            raise ConfigTypeNotFoundError(f"{type_} type is not configured in the application")

    @staticmethod
    def from_json_file(file_path: str):
        list_of_config_sections_obj = load_json_file(file_path)
        sections = []
        for section in list_of_config_sections_obj:
            fields = [GcodeSettings.get_config_value_from_dict(config) for config in section["fields"]]
            sections.append(GCodeSettingSection(section_name=section["section_name"], fields=fields))

        return GcodeSettings(sections=sections)

    def save_to_json_file(self, file_path: str):
        with open(file_path, "w") as f:
            json.dump([section.dict() for section in self.sections], f)


