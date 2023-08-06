import json

from config_parser.config_parser_enums.parameter_names import ParameterNames

OPTIONAL_PARAMS = {}  # Example: {'param_name', 'default value']
REQUIRED_PARAMS = {}  # Example: {'param_name', 'Error message if not present'}

'''
Base config model to hold common pattern to parse df application configs.
'''


class BaseConfigModel:
    def __init__(self, yaml_object: dict):
        self.yaml_object = yaml_object
        self.optional_params = self.get_optional_params()
        self.required_params = self.get_required_params()
        self.validate_and_init()

    '''
    Validate the config to ensure if it only has the appropriate parameters
    '''

    def validate_and_init(self):
        # Validate basic sanity of the input params
        for param_name, value in self.yaml_object.items():
            required_param = self.required_params.get(param_name)
            optional_param = self.optional_params.get(param_name)
            if required_param is None and optional_param is None:
                available_params = list(self.required_params.keys())
                available_params.append(list(self.optional_params.keys()))
                raise ValueError(f"Invalid param `{param_name}` is passed. "
                                 f"Available params are: {available_params}")
            if required_param is not None and optional_param is not None:
                raise ValueError(f"`{param_name}` is present in both required and optional param list!")

        # Validate all required params are present & set those values are present
        for param_name, set_func in self.required_params.items():
            value_from_input = self.yaml_object.get(param_name)
            if value_from_input is None:
                raise ValueError(f"Required param `{param_name}` is missing in config!")
            set_func(value_from_input)

        # Set optional params
        for param_name, set_func in self.optional_params.items():
            value_from_input = self.yaml_object.get(param_name)
            set_func(value_from_input)

    def get_required_params(self):
        raise ValueError("It must be declared in the child class!")

    def get_optional_params(self):
        raise ValueError("It must be declared in the child class!")


class ApplicationConfigModel(BaseConfigModel):
    def __init__(self, yaml_object: dict, source_path: str = None):
        super().__init__(yaml_object=yaml_object)
        self.source_path = source_path

    def get_required_params(self):
        return {
            ParameterNames.name: self.set_name,
            ParameterNames.version: self.set_version,
        }

    def get_optional_params(self):
        return {
            ParameterNames.display_name: self.set_display_name,
            ParameterNames.description: self.set_description,
            ParameterNames.state: self.set_state,
            ParameterNames.actions: self.set_actions,
            ParameterNames.authors: self.set_authors,
        }

# Required Parameter Setters

    def set_name(self, value):
        assert isinstance(value, str)
        self.name = value

    def set_version(self, value):
        assert isinstance(value, float)
        self.version = value

# Optional Parameter Setters

    def set_display_name(self, value):
        if value is None:
            value = self.name
        assert isinstance(value, str)
        self.display_name = value

    def set_description(self, value):
        if value is None:
            value = self.display_name
        assert isinstance(value, str)
        self.description = value

    def set_state(self, value):
        if value is None:
            value = 'draft'
        assert isinstance(value, str), f"For Application:`{self.name}`: `state` must be string but it's passed as {value}."
        allowed_state = ["draft", "published"]
        assert value in allowed_state, f"For Application:`{self.name}`: `state` is passed as `{value}` but must be {allowed_state}."
        self.state = value

    def set_actions(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        actions = []
        for action in value:
            action_model = ActionConfigModel(action)
            if action_model is None:
                raise ValueError(f"Action model parse failed for action: {action}")
            actions.append(action_model)
        self.actions = actions

    def set_authors(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        self.authors = value


class ActionConfigModel(BaseConfigModel):
    def __init__(self, yaml_object: dict):
        super().__init__(yaml_object=yaml_object)

    def get_required_params(self):
        return {
            ParameterNames.unique_name: self.set_unique_name,
            ParameterNames.action_reference: self.set_action_reference,
        }

    def get_optional_params(self):
        return {
            ParameterNames.charts: self.set_charts,
            ParameterNames.display_name: self.set_display_name,
            ParameterNames.description: self.set_description,
            ParameterNames.state: self.set_state,
            ParameterNames.df_tags: self.set_df_tags,
            ParameterNames.parameters: self.set_parameters,
            ParameterNames.source_type: self.set_source_type,
        }

    # Required Parameter Setters

    def set_unique_name(self, value):
        assert isinstance(value, str)
        self.unique_name = value

    def set_action_reference(self, value):
        assert isinstance(value, str)
        self.action_reference = value

    # Optional Parameter Setters

    def set_display_name(self, value):
        if value is None:
            value = self.unique_name
        assert isinstance(value, str)
        self.display_name = value

    def set_description(self, value):
        if value is None:
            value = self.display_name
        assert isinstance(value, str)
        self.description = value

    def set_state(self, value):
        if value is None:
            value = 'draft'
        assert isinstance(value, str), f"For Action:`{self.unique_name}`: `state` must be string but it's passed as {value}."
        allowed_state = ["draft", "published"]
        assert value in allowed_state, f"For Action:`{self.unique_name}`: `state` is passed as `{value}` but must be {allowed_state}."
        self.state = value

    def set_df_tags(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        self.df_tags = value

    def set_parameters(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        params = []
        for param_config in value:
            param = ParameterConfigModel(param_config)
            params.append(param)
        self.parameters = params

    def set_source_type(self, value):
        if value is None:
            value = 'macro'
        assert isinstance(value, str), f"For Action:`{self.unique_name}`: `source_type` must be string but it's passed as {value}."
        allowed_state = ["macro", "model", "python", "analyses"]
        assert value in allowed_state, f"For Action:`{self.unique_name}`: `state` is passed as `{value}` but must be {allowed_state}."
        self.source_type = value

    def set_charts(self, value):
        if value is None:
            value = []
        assert isinstance(value, list)
        charts = []

        for chart_config in value:
            chart = ChartConfigModel(chart_config)
            charts.append(chart)

        self.charts = charts

    def get_charts(self):
        charts = []
        for chart in self.charts:
            charts.append({
                'name': chart.name,
                'kind': chart.kind,
                'options': chart.options,
                'expose_data': chart.expose_data
            })
        return charts


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
