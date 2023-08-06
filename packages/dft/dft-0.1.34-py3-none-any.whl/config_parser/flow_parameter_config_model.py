from config_parser.base_config_model import BaseConfigModel
from config_parser.config_parser_enums.parameter_names import ParameterNames


class FlowParameterConfigModel(BaseConfigModel):
    def get_optional_params(self):
        return {
            ParameterNames.global_parameter: self.set_global_parameter,
            ParameterNames.default_value: self.set_default_value,
            ParameterNames.source_action: self.set_source_action
        }

    def get_required_params(self):
        return {
            ParameterNames.param_name: self.set_param_name,
        }

    def set_param_name(self, value):
        self.parameter_name = value

    def set_global_parameter(self, value):
        self.global_parameter = value

    def set_default_value(self, value):
        self.default_value = value

    def set_source_action(self, value):
        self.source_action = value

