from pandas import DataFrame

from typing import AnyStr, Dict


class TimeSeriesDataFrame(DataFrame):
    
    def __init__(self, time_col: AnyStr, *args, **kwargs):
        self._time_col = time_col
        super().__init__(*args, **kwargs)

    @property
    def time_col(self):
        return self._time_col