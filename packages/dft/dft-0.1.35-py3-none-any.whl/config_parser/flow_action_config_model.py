from config_parser.base_config_model import BaseConfigModel
from config_parser.config_parser_enums.parameter_names import ParameterNames
from config_parser.flow_parameter_config_model import FlowParameterConfigModel


class FlowActionConfigModel(BaseConfigModel):

    def get_required_params(self):
        return {
            ParameterNames.action_reference: self.set_action_reference,
            ParameterNames.parameters: self.set_parameters
        }

    def get_optional_params(self):
        return {
            ParameterNames.display_name: self.set_display_name,
            ParameterNames.stage_name: self.set_stage_name
        }

    def set_action_reference(self, value):
        assert isinstance(value, str), "Action Reference in flow action should be a string"
        self.action_reference = value


    def set_parameters(self, value):
        assert isinstance(value, list), "Parameters inside flow action should be a list"

        params = []
        for flow_parameter_config in value:
            flow_parameter = FlowParameterConfigModel(flow_parameter_config)
            params.append(flow_parameter)

        self.parameters = params

    def set_display_name(self, value):
        self.display_name = value

    def set_stage_name(self, value):
        if value is None:
            value = "DBT Flow stage"

        self.stage_name = value
