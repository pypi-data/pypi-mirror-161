from dataclasses import field
from typing import List
import marshmallow_dataclass
from marshmallow import post_dump
from marshmallow_dataclass import dataclass

from dft.models.chart_options.chart_options import ChartOptions


@dataclass
class MultipleSegmentsTwoDChartOptions(ChartOptions):
    x: str = field(metadata={"required": True})
    y: str = field(metadata={"required": True})
    segments: str = field(metadata={"required": True})

    def __init__(self, x, y, segments):
        self.x = x
        self.y = y
        self.segments = segments

    @post_dump
    def clean_missing(self, data, **kwargs):
        removed_missing_fields = {k:v for (k,v) in data.items() if v is not None}
        return removed_missing_fields

    def to_dict(self):
        model_schema = marshmallow_dataclass.class_schema(MultipleSegmentsTwoDChartOptions)()
        return model_schema.dumps(self, many=False)
