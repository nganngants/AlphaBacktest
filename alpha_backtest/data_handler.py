from typing import Optional, List

import pandas as pd
from openbb import obb


class DataHandler:
    """Data handler class for loading from OpenBB and processing data."""
    
    def __init__(self, symbols: str, start_date: str, end_date: Optional[str] = None, provider: str = "yfinance"):
        """
            Initialize the data handler
            Args:
                symbols: List of symbols to load data, consisting of comma-separated sysbols.
                start_date: Start date for the data.
                end_date: End date for
                provider: Data provider to use for loading data.
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.provider = provider

    def load_data(self) -> pd.DataFrame:
        data = obb.equity.price.historical(
                symbol=self.symbols, 
                start_date=self.start_date, 
                end_date=self.end_date, 
                provider=self.provider
            ).to_df()
        

        # Index by date
        data.reset_index(inplace=True)
        data.set_index("date", inplace=True)

        return data


if __name__ == "__main__":
    data_handler = DataHandler(symbols="AAPL,GOOGL,MSFT", start_date="2021-01-01")
    data = data_handler.load_data()
    print(data.head())