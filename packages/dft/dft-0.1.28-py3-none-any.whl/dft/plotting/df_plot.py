"""
Why only static method?

Why global state?

"""
from typing import List

from dft.models.chart_config import ChartConfig
from dft.models.chart_data import ChartData
from dft.models.chart_metadata import ChartMetadata
from dft.models.chart_options.gauge_single_value_options import GaugeSingleValueOptions
from dft.models.chart_options.heat_map_dataframe_options import HeatMapDataframeOptions
from dft.models.chart_options.multiple_segments_twoD_plot_options import MultipleSegmentsTwoDChartOptions
from dft.models.chart_options.single_dimension_with_legends_options import SingleDimensionWithLegendsOptions
from dft.models.chart_options.single_value_with_data_options import SingleValueWithDataOptions
from dft.models.chart_options.stacked_bar_data_options import StackedBarDataOptions
from dft.models.chart_options.time_series_chart_data_options import TimeSeriesChartDataOptions
from dft.models.chart_options.twoD_chart_data_options import TwoDChartDataOptions

df_chart_config = []

"""
Reset should be called primarily in the context of unittest to avoid race condition
 as chart_config is a global variable for this class.
"""


def reset():
    global df_chart_config
    df_chart_config = []


def bar_chart(name, x, y, data, expose_data=False):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="bar",
                name=name,
                expose_data=expose_data
            ),
            data=ChartData(
                options=TwoDChartDataOptions(
                    x=x,
                    y=y,
                ),
                raw_data=data
            )
        )
    )


def scatter_chart(name, x, y, data, expose_data=False):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="scatter",
                name=name,
                expose_data=expose_data
            ),
            data=ChartData(
                raw_data=data,
                options=TwoDChartDataOptions(
                    x=x,
                    y=y
                )
            )
        )
    )


def pie_chart(name, legends, y, data):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="pie",
                name=name
            ),
            data=ChartData(
                raw_data=data,
                options=SingleDimensionWithLegendsOptions(
                    y=y,
                    legends=legends
                )
            )
        )
    )


def line_chart(name, x, y, data, expose_data=False):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="line",
                name=name,
                expose_data=expose_data
            ),
            data=ChartData(
                raw_data=data,
                options=TwoDChartDataOptions(
                    x=x,
                    y=y
                )
            )
        )
    )


def single_value(name, value, variation=None):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="single_value",
                name=name,
            ),
            data=ChartData(
                options=SingleValueWithDataOptions(
                    value=value,
                    variation=variation
                )
            )
        )
    )


def segment_line_chart(name, x, y, segment_column, data):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="segment",
                name=name,
            ),
            data=ChartData(
                options=MultipleSegmentsTwoDChartOptions(
                    x=x,
                    y=y,
                    segments=segment_column
                ),
                raw_data=data
            )
        )
    )


def time_series_forecast(name, forecasted_rows, data):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="time_series",
                name=name,
            ),
            data=ChartData(
                options=TimeSeriesChartDataOptions(
                    forecasted_rows=forecasted_rows
                ),
                raw_data=data
            )
        )
    )


def gauge_single_value(name, value, minimum, maximum, threshold_1=None, threshold_2=None):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="single_value_gauge",
                name=name,
            ),
            data=ChartData(
                options=GaugeSingleValueOptions(
                    value=value,
                    minimum=minimum,
                    maximum=maximum,
                    threshold_1=threshold_1,
                    threshold_2=threshold_2
                )
            )
        )
    )


def radial_polar_chart(name, x, y, segment_column, data):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="radial_polar_chart",
                name=name,
            ),
            data=ChartData(
                options=MultipleSegmentsTwoDChartOptions(
                    x=x,
                    y=y,
                    segments=segment_column
                ),
                raw_data=data
            )
        )
    )


def stacked_histogram(name, x, y_columns: List[str], data):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="stacked_histogram",
                name=name,
            ),
            data=ChartData(
                options=StackedBarDataOptions(
                    x=x,
                    y_columns=y_columns
                ),
                raw_data=data
            )
        )
    )


def clubbed_histogram(name, x, y_columns: List[str], data):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="clubbed_histogram",
                name=name,
            ),
            data=ChartData(
                options=StackedBarDataOptions(
                    x=x,
                    y_columns=y_columns
                ),
                raw_data=data
            )
        )
    )


def heat_map_dataframe(name, y, x_columns: List[str], data):
    df_chart_config.append(
        ChartConfig(
            metadata=ChartMetadata(
                kind="heat_map_dataframe",
                name=name,
            ),
            data=ChartData(
                options=HeatMapDataframeOptions(
                    x_columns=x_columns,
                    y=y
                ),
                raw_data=data
            )
        )
    )
