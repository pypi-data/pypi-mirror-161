from marshmallow_dataclass import dataclass

from dft.models.chart_data import ChartData
from dft.models.chart_metadata import ChartMetadata


@dataclass
class ChartConfig:
    metadata: ChartMetadata
    data: ChartData

    def __init__(self, metadata=None, data=None):
        self.metadata = metadata
        self.data = data
