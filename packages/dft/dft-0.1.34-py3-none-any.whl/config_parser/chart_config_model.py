from config_parser.base_config_model import BaseConfigModel
from config_parser.config_parser_enums.parameter_names import ParameterNames


class ChartConfigModel(BaseConfigModel):
    def __init__(self, yaml_object: dict):
        super().__init__(yaml_object)

    def get_required_params(self):
        return {
            ParameterNames.name: self.set_name,
            ParameterNames.kind: self.set_kind,
            ParameterNames.options: self.set_options
        }

    def get_optional_params(self):
        return {
            ParameterNames.expose_data: self.set_expose_data
        }

    def set_name(self, value):
        self.name = value

    def set_kind(self, value):
        self.kind = value

    def set_options(self, value):
        self.options = value

    def set_expose_data(self, value):
        if value is None:
            value = False

        self.expose_data = value
