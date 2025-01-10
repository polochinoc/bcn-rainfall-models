"""
Provides a rich class to manipulate Seasonal Rainfall data.
"""

import fireducks.pandas as fd
import plotly.graph_objs as go

from back.rainfall.models.yearly_rainfall import YearlyRainfall
from back.rainfall.utils import Season


class SeasonalRainfall(YearlyRainfall):
    """
    Provides numerous functions to load, manipulate and export Seasonal Rainfall data.
    """

    def __init__(
        self,
        raw_data: fd.DataFrame,
        season: Season,
        *,
        start_year: int,
        round_precision: int,
    ):
        self.season: Season = season
        super().__init__(
            raw_data, start_year=start_year, round_precision=round_precision
        )

    def load_yearly_rainfall(self) -> fd.DataFrame:
        """
        Load Yearly Rainfall for instance season variable into pandas DataFrame.

        :return: A pandas DataFrame displaying rainfall data (in mm)
        for instance season according to year.
        """

        return self.load_rainfall(
            self.season.get_months()[0],
            self.season.get_months()[-1],
        )

    def get_bar_figure_of_rainfall_according_to_year(
        self,
        begin_year: int,
        end_year: int,
        *,
        figure_label: str | None = None,
        trace_label: str | None = None,
        plot_average=False,
        plot_linear_regression=False,
    ) -> go.Figure | None:
        """
        Overrides parent method by customizing figure and trace labels.
        """
        return super().get_bar_figure_of_rainfall_according_to_year(
            begin_year,
            end_year,
            figure_label=figure_label
            or f"Rainfall (mm) for {self.season.value} between {begin_year} and {end_year}",
            trace_label=f"{self.season.value.capitalize()} rainfall",
            plot_average=plot_average,
            plot_linear_regression=plot_linear_regression,
        )
