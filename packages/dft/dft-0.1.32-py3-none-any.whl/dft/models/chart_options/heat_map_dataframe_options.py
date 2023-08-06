from dataclasses import field
from typing import List
import marshmallow_dataclass
from marshmallow import post_dump
from marshmallow_dataclass import dataclass

from dft.models.chart_options.chart_options import ChartOptions


@dataclass
class HeatMapDataframeOptions(ChartOptions):
    y: str = field(metadata={"required": True})
    x_columns: List[str] = field(metadata={"required": True}, default_factory=list)

    def __init__(self, y, x_columns):
        self.y = y
        self.x_columns = x_columns

    @post_dump
    def clean_missing(self, data, **kwargs):
        removed_missing_fields = {k:v for (k,v) in data.items() if v is not None}
        return removed_missing_fields

    def to_dict(self):
        model_schema = marshmallow_dataclass.class_schema(HeatMapDataframeOptions)()
        return model_schema.dumps(self, many=False)
