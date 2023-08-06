from dataclasses import field
import marshmallow_dataclass
from marshmallow import post_dump
from marshmallow_dataclass import dataclass

from dft.models.chart_options.chart_options import ChartOptions


@dataclass
class GaugeSingleValueOptions(ChartOptions):
    value: float = field(metadata={"required": True})
    minimum: float = field(metadata={"required": True})
    maximum: float = field(metadata={"required": True})
    threshold_1: float = field(metadata={"required": False}, default=None)
    threshold_2: float = field(metadata={"required": False}, default=None)

    def __init__(self, value, minimum, maximum, threshold_1=None, threshold_2=None):
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.threshold_1 = threshold_1
        self.threshold_2 = threshold_2

    @post_dump
    def clean_missing(self, data, **kwargs):
        removed_missing_fields = {k:v for (k,v) in data.items() if v is not None}
        return removed_missing_fields

    def to_dict(self):
        model_schema = marshmallow_dataclass.class_schema(GaugeSingleValueOptions)()
        return model_schema.dumps(self, many=False)
