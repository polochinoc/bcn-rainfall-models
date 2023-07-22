from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

import src.config as cfg
from src.decorators import plots
from src.enums.labels import Label
from src.enums.months import Month


class YearlyRainfall:
    def __init__(self,
                 start_year: Optional[int] = None,
                 rounding_precision: Optional[int] = None,
                 yearly_rainfall: Optional[pd.DataFrame] = None):
        if start_year is None:
            self.starting_year: int = cfg.get_start_year()
        else:
            self.starting_year: int = start_year
        if rounding_precision is None:
            self.rounding_precision: int = cfg.get_rounding_precision()
        else:
            self.rounding_precision: int = rounding_precision
        if yearly_rainfall is None:
            self.load_yearly_rainfall()
        else:
            self.yearly_rainfall: pd.DataFrame = yearly_rainfall

    def __str__(self):
        return self.yearly_rainfall.to_string()

    def load_yearly_rainfall(self) -> None:
        self.yearly_rainfall = self.load_rainfall(Month.JANUARY.value)

    def load_rainfall(self, start_month: int, end_month: Optional[int] = None) -> pd.DataFrame:
        monthly_rainfall: pd.DataFrame = pd.read_csv(cfg.get_dataset_url())

        years: pd.DataFrame = monthly_rainfall.iloc[:, :1]
        if end_month is not None and end_month < start_month:
            rainfall: pd.Series = pd.concat((monthly_rainfall.iloc[:, start_month:start_month + 1],
                                             monthly_rainfall.iloc[:, 1:end_month]), axis='columns')\
                .sum(axis='columns')
        else:
            rainfall: pd.Series = monthly_rainfall.iloc[:, start_month:end_month].sum(axis='columns')

        yearly_rainfall: pd.DataFrame = pd.concat((years, rainfall), axis='columns') \
            .set_axis([Label.YEAR.value, Label.RAINFALL.value],
                      axis='columns')

        if self.starting_year is not None:
            yearly_rainfall = yearly_rainfall[yearly_rainfall[Label.YEAR.value] >= self.starting_year] \
                .reset_index() \
                .drop(columns='index')

        yearly_rainfall[Label.RAINFALL.value] = round(yearly_rainfall[Label.RAINFALL.value], self.rounding_precision)

        return yearly_rainfall

    def get_yearly_rainfall(self,
                            begin_year: Optional[int] = None,
                            end_year: Optional[int] = None) -> pd.DataFrame:
        yr: pd.DataFrame = self.yearly_rainfall

        if begin_year is not None:
            yr = yr[yr[Label.YEAR.value] >= begin_year]

        if end_year is not None:
            yr = yr[yr[Label.YEAR.value] <= end_year]

        return yr

    def export_as_csv(self, path: Optional[str] = None) -> str:
        return self.yearly_rainfall.to_csv(path_or_buf=path, index=False)

    def get_average_yearly_rainfall(self,
                                    begin_year: Optional[int] = None,
                                    end_year: Optional[int] = None) -> float:
        yr: pd.DataFrame = self.get_yearly_rainfall(begin_year, end_year)

        nb_years: int = len(yr)
        if nb_years == 0:
            return 0.

        yr = yr.sum(axis='rows')

        return round(yr.loc[Label.RAINFALL.value] / nb_years, self.rounding_precision)

    def get_years_below_average(self,
                                begin_year: Optional[int] = None,
                                end_year: Optional[int] = None) -> int:
        yr: pd.DataFrame = self.get_yearly_rainfall(begin_year, end_year)

        yr = yr[yr[Label.RAINFALL.value] < self.get_average_yearly_rainfall(begin_year, end_year)]

        return yr.count()[Label.YEAR.value]

    def get_years_above_average(self,
                                begin_year: Optional[int] = None,
                                end_year: Optional[int] = None) -> int:
        yr: pd.DataFrame = self.get_yearly_rainfall(begin_year, end_year)

        yr = yr[yr[Label.RAINFALL.value] > self.get_average_yearly_rainfall(begin_year, end_year)]

        return yr.count()[Label.YEAR.value]

    def add_percentage_of_normal(self,
                                 begin_year: Optional[int] = None,
                                 end_year: Optional[int] = None) -> None:
        normal: float = self.get_average_yearly_rainfall(begin_year, end_year)
        if normal == 0.:
            return

        self.yearly_rainfall[Label.PERCENTAGE_OF_NORMAL.value] = round(
            self.yearly_rainfall[Label.RAINFALL.value] / normal * 100.0, self.rounding_precision)

    def add_linear_regression(self) -> (float, float):
        years: np.ndarray = self.yearly_rainfall[Label.YEAR.value].values.reshape(-1, 1)
        rainfalls: np.ndarray = self.yearly_rainfall[Label.RAINFALL.value].values

        reg = LinearRegression()
        reg.fit(years, rainfalls)
        self.yearly_rainfall[Label.LINEAR_REGRESSION.value] = reg.predict(years)
        self.yearly_rainfall[Label.LINEAR_REGRESSION.value] = round(
            self.yearly_rainfall[Label.LINEAR_REGRESSION.value], self.rounding_precision)

        return r2_score(rainfalls,
                        self.yearly_rainfall[Label.LINEAR_REGRESSION.value].values), \
            reg.coef_[0]

    def add_savgol_filter(self) -> None:
        self.yearly_rainfall[Label.SAVITZKY_GOLAY_FILTER.value] = signal.savgol_filter(
            self.yearly_rainfall[Label.RAINFALL.value],
            window_length=len(self.yearly_rainfall),
            polyorder=len(
                self.yearly_rainfall) // 10)

        self.yearly_rainfall[Label.SAVITZKY_GOLAY_FILTER.value] = round(
            self.yearly_rainfall[Label.SAVITZKY_GOLAY_FILTER.value], self.rounding_precision)

    @plots.legend_and_show()
    def plot_rainfall(self, title: Optional[str] = None) -> None:
        for column_label in self.yearly_rainfall.columns[1:]:
            if column_label == Label.PERCENTAGE_OF_NORMAL.value:
                continue

            plt.plot(self.yearly_rainfall[Label.YEAR.value],
                     self.yearly_rainfall[column_label],
                     label=column_label)

        if title is not None:
            plt.title(title)
        else:
            plt.title("Barcelona rainfall evolution and various models")

    @plots.legend_and_show()
    def plot_normal(self, title: Optional[str] = None) -> None:
        if Label.PERCENTAGE_OF_NORMAL.value not in self.yearly_rainfall.columns:
            return

        plt.axhline(y=100.0, color='orange', linestyle='dashed', label='Normal')
        plt.scatter(self.yearly_rainfall[Label.YEAR.value],
                    self.yearly_rainfall[Label.PERCENTAGE_OF_NORMAL.value],
                    label=Label.PERCENTAGE_OF_NORMAL.value)

        if title is not None:
            plt.title(title)
        else:
            plt.title("Barcelona rainfall evolution compared to normal")
