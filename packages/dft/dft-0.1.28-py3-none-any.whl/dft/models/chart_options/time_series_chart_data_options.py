from dataclasses import field
from typing import List
import marshmallow_dataclass
from marshmallow import post_dump
from marshmallow_dataclass import dataclass

from dft.models.chart_options.chart_options import ChartOptions


@dataclass
class TimeSeriesChartDataOptions(ChartOptions):
    forecasted_rows: int = field(metadata={"required": True})

    def __init__(self, forecasted_rows):
        self.forecasted_rows = forecasted_rows

    @post_dump
    def clean_missing(self, data, **kwargs):
        removed_missing_fields = {k:v for (k,v) in data.items() if v is not None}
        return removed_missing_fields

    def to_dict(self):
        model_schema = marshmallow_dataclass.class_schema(TimeSeriesChartDataOptions)()
        return model_schema.dumps(self, many=False)
