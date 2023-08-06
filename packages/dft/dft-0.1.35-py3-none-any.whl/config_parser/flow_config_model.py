from config_parser.base_config_model import BaseConfigModel
from config_parser.config_parser_enums.parameter_names import ParameterNames
from config_parser.flow_action_config_model import FlowActionConfigModel
from config_parser.parameter_config_model import ParameterConfigModel


class FlowConfigModel(BaseConfigModel):

    def get_required_params(self):
        return {
            ParameterNames.flow_actions: self.set_flow_actions,
            ParameterNames.unique_name: self.set_unique_name
        }

    def get_optional_params(self):
        return {
            ParameterNames.display_name: self.set_display_name,
            ParameterNames.parameters: self.set_parameters,
            ParameterNames.description: self.set_description
        }

    def set_flow_actions(self, value):
        if value is None:
            value = []

        assert isinstance(value, list), "list"
        flow_actions = []

        for action_config in value:
            action = FlowActionConfigModel(action_config)
            flow_actions.append(action)

        self.flow_actions = flow_actions

    def set_display_name(self, value):
        if value is None:
            value = self.unique_name

        assert isinstance(value, str)

        self.display_name = value

    def set_unique_name(self, value):
        assert isinstance(value, str)

        self.unique_name = value

    def set_parameters(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)

        params = []
        for flow_parameter_config in value:
            flow_parameter = ParameterConfigModel(flow_parameter_config)
            params.append(flow_parameter)

        self.parameters = params

    def set_description(self, value):
        if value is None:
            value = self.display_name

        self.description = value


