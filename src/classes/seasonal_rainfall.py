import pandas as pd

from typing import Optional

from src.classes.yearly_rainfall import YearlyRainfall
from src.enums.seasons import Season
from src.enums.months import Month


class SeasonalRainfall(YearlyRainfall):
    def __init__(self,
                 season: Season,
                 start_year: Optional[int] = None,
                 rounding_precision: Optional[int] = None,
                 yearly_rainfall: Optional[pd.DataFrame] = None):
        self.season: Season = season
        super().__init__(start_year, yearly_rainfall, rounding_precision)

    def load_yearly_rainfall(self) -> None:
        self.yearly_rainfall = self.load_rainfall(self.season.value[0].value, self.season.value[2].value + 1)

    def plot_rainfall(self, title: Optional[str] = None) -> None:
        if title is not None:
            super().plot_rainfall(title)
        else:
            super().plot_rainfall(f"Barcelona rainfall evolution and various models for {self.season.name.lower()}")

    def plot_normal(self, title: Optional[str] = None) -> None:
        if title is not None:
            super().plot_normal(title)
        else:
            super().plot_normal(f"Barcelona rainfall evolution compared to normal for {self.season.name.lower()}")
