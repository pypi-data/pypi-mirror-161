from dataclasses import field
from typing import List, Any
import marshmallow_dataclass
from marshmallow import post_dump, fields, ValidationError
from marshmallow_dataclass import dataclass

from dft.models.chart_options.chart_options import ChartOptions


@dataclass
class SingleValueWithDataOptions(ChartOptions):
    value: Any = field(metadata={"required": True})
    variation: str = field(metadata={"required": False, "missing": None})

    def __init__(self, value, variation):
        self.value = value
        self.variation = variation

    @post_dump
    def clean_missing(self, data, **kwargs):
        removed_missing_fields = {k: v for (k, v) in data.items() if v is not None}
        return removed_missing_fields

    def to_dict(self):
        model_schema = marshmallow_dataclass.class_schema(SingleValueWithDataOptions)()
        return model_schema.dumps(self, many=False)
