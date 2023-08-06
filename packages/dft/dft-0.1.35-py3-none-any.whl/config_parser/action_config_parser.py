from config_parser.base_config_model import BaseConfigModel
from config_parser.chart_config_model import ChartConfigModel
from config_parser.config_parser_enums.parameter_names import ParameterNames
from config_parser.parameter_config_model import ParameterConfigModel


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
