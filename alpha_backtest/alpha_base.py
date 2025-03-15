
from typing import List
import logging

_logger = logging.getLogger(__name__)

class AlphaBase:
    def initialize(self, data, valid, assets: List[str], dates: List[str]):
        """
            Args:
                assets: List of assets. If assets[0] = "AAPL", then "AAPL" has asset_id = 0
                dates: List of dates. If dates[0] = "2021-01-01", then "2021-01-01" has date_id = 0
                data: a 2D array of dict. For example, data[asset_id][date_id] = {"open": 100, "high": 110, "low": 90, "close": 105, "volume": 1000000}
        """
        self.asset_ix = assets
        self.dates = dates
        self.data = data
        self.valid = valid

    def generate_signals_for_di(self, di: int):
        # alphas is a list of signals for each asset
        self.alpha = [0.0] * len(self.asset_ix)
        self.generate(di)
        return self.alpha

    # This function should be implemented by the user
    def generate(self, di: int):
        pass