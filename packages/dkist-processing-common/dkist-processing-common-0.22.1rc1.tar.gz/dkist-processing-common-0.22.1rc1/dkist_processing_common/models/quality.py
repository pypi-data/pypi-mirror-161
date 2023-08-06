"""Support classes used to create a quality report."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel


class Plot2D(BaseModel):
    """Support class use to hold the data for creating a 2D plot in the quality report."""

    xlabel: str
    ylabel: str
    series_data: Dict[str, List[List[Any]]]
    series_name: Optional[str] = None
    ylabel_horizontal: Optional[bool] = False


class SimpleTable(BaseModel):
    """Support class to hold a simple table to be inserted into the quality report."""

    rows: List[List[Any]]
    header_row: Optional[bool] = True
    header_column: Optional[bool] = False


class ModulationMatrixHistograms(BaseModel):
    """Support class for holding the big ol' grid of histograms that represent the modulation matrix fits."""

    modmat_list: List[List[List[float]]]


class EfficiencyHistograms(BaseModel):
    """Support class for holding 4 histograms that correspond to efficiencies of the 4 stokes components."""

    efficiency_list: List[List[float]]


class PlotHistogram(BaseModel):
    """Support class to hold 1D data for plotting a histogram."""

    xlabel: str
    series_data: Dict[str, List[float]]
    series_name: Optional[str] = None
    vertical_lines: Optional[Dict[str, float]]


class PlotRaincloud(BaseModel):
    """Support class to hold data series for fancy-ass violin plots."""

    xlabel: str
    ylabel: str
    categorical_column_name: str
    distribution_column_name: str
    dataframe_json: str
    hue_column_name: Optional[str]
    ylabel_horizontal: Optional[bool]


class ReportMetric(BaseModel):
    """
    A Quality Report is made up of a list of metrics with the schema defined by this class.

    Additionally, this class can produce a Flowable or List of Flowables to be render the metric in the PDF Report
    """

    name: str
    description: str
    statement: Optional[str] = None
    plot_data: Optional[Plot2D] = None
    histogram_data: Optional[PlotHistogram] = None
    table_data: Optional[SimpleTable] = None
    modmat_data: Optional[ModulationMatrixHistograms] = None
    efficiency_data: Optional[EfficiencyHistograms] = None
    raincloud_data: Optional[PlotRaincloud] = None
    warnings: Optional[List[str]] = None
