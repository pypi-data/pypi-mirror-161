import uuid

import marshmallow_dataclass
from marshmallow import post_dump
from marshmallow_dataclass import dataclass


@dataclass
class ChartMetadata:
    chart_id: str
    kind: str
    name: str
    expose_data: bool

    def __init__(self, chart_id=None, kind=None, name=None, expose_data=False):
        self.chart_id = chart_id
        self.kind = kind
        self.name = name
        self.expose_data = expose_data

    def assign_random_chart_id(self):
        self.chart_id = str(uuid.uuid4())

    @post_dump
    def clean_missing(self, data, **kwargs):
        removed_missing_fields = {k: v for (k, v) in data.items() if v is not None}
        return removed_missing_fields

    def to_dict(self):
        model_schema = marshmallow_dataclass.class_schema(ChartMetadata)()
        return model_schema.dump(self, many=False)
