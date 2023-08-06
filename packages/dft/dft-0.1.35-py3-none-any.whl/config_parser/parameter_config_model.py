from config_parser.base_config_model import BaseConfigModel
from config_parser.config_parser_enums.parameter_names import ParameterNames


class ParameterConfigModel(BaseConfigModel):
    def __init__(self, yaml_object: dict):
        super().__init__(yaml_object=yaml_object)

    def get_required_params(self):
        return {
            ParameterNames.param_name: self.set_param_name,
            ParameterNames.df_param_type: self.set_df_param_type,
        }

    def get_optional_params(self):
        return {
            ParameterNames.display_name: self.set_display_name,
            ParameterNames.description: self.set_description,
            ParameterNames.default_value: self.set_default_value,
            ParameterNames.df_tags: self.set_df_tags,
            ParameterNames.single_select_options: self.set_single_select_options,
            ParameterNames.multi_select_options: self.set_multi_select_options,
            ParameterNames.user_input_required: self.set_user_input_required,
            ParameterNames.parameter_language: self.set_parameter_language
        }

    # Required Parameter Setters

    def set_param_name(self, value):
        assert isinstance(value, str)
        self.param_name = value

    def set_df_param_type(self, value):
        assert isinstance(value, str)
        # TODO: Validate the parameter types are of proper value
        self.df_param_type = value

    # Optional Parameter Setters

    def set_display_name(self, value):
        if value is None:
            value = self.param_name
        assert isinstance(value, str)
        self.display_name = value

    def set_description(self, value):
        if value is None:
            value = self.display_name
        assert isinstance(value, str)
        self.description = value

    def set_default_value(self, value):
        self.default_value = value

    def set_df_tags(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        self.df_tags = value

    def set_single_select_options(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        self.single_select_options = value

    def set_multi_select_options(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        self.multi_select_options = value

    def set_user_input_required(self, value):
        if value is None:
            value = True
        assert isinstance(value, bool)
        if not value and self.default_value is None:
            raise ValueError(f"Parameter {self.param_name}, does not have default value and it must set `user_input_required` to True")
        self.user_input_required = value

    def set_parameter_language(self, value):
        if value is None:
            value = "sql"
        self.parameter_language = value
