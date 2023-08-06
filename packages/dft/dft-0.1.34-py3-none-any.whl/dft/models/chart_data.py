import json
from typing import Dict, Any

import pandas as pd

from dft.models.chart_options.chart_options import ChartOptions


class ChartData:
    options: ChartOptions
    raw_data: pd.DataFrame

    def __init__(self, options=None, raw_data=None):
        self.options = options
        self.raw_data = raw_data

    def prepare_raw_data(self) -> Dict[str, Any]:
        result = json.loads(self.raw_data.to_json(orient="records"))
        final_result = {}
        for record in result:
            for col in record:
                final_result[col] = []
            break

        for record in result:
            for col in record:
                final_result[col].append(record[col])

        return final_result


