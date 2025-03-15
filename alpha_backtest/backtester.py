
from alpha_backtest.data_handler import DataHandler
from alpha_backtest.alpha_config import AlphaConfig
from alpha_backtest.evaluation import (
    calculate_total_return,
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_maximum_drawdown,
)
import pandas as pd
import logging
import matplotlib.pyplot as plt
from typing import Dict
from tqdm import tqdm

_logger = logging.getLogger(__name__)

class Backtester:
    def __init__(
            self,
            alpha_config_file: str, # path to alpha config file
            assets_file: str, # path to file containing list of assets
            initial_capital: float = 10000.0,
            commission_pct: float = 0.001,
            commission_fixed: float = 1.0,
        ):
        """Initialize the backtester with initial capital and commission fees."""
        self.initial_capital: float = initial_capital
        self.commission_pct: float = commission_pct
        self.commission_fixed: float = commission_fixed        
        
        self.dates = []
        self.assets_ix = []
        self.data = [[]]
        self.alpha_config = None
        self.data_handler = None
        self.portfolio = {}
        self.portfolio_history = {}
        self.daily_portfolio_value = []
        self.valid = None
        self.initialize(assets_file, alpha_config_file)

    def initialize(self, assets_file, alpha_config_file):
        """
            Load data using the data handler and prepare the data for backtesting.
            We need to prepare 2 essential lists and 1 matrix:
                - self.asset_ix: List of assets. If assets[0] = "AAPL", then "AAPL" has asset_id = 0
                - self.dates: List of dates in format "YYYY-MM-DD", needed to convert from datetime to this format. If dates[0] = "20210101", then "2021/01/01" has date_id = 0
                - self.data: a 2D array of dict. For example, data[date_id][asset_id] = {"open": 100, "high": 110, "low": 90, "close": 105, "volume": 1000000}
        """

        with open(assets_file, "r") as f:
            self.assets_ix = f.read().splitlines()
        
        self.alpha_config = AlphaConfig(alpha_config_file)

        # Prepare data
        self.data_handler = DataHandler(
            symbols=",".join(self.assets_ix),
            start_date=self.alpha_config.start_sim_date,
            end_date=self.alpha_config.end_sim_date
        )

        _logger.info(f"Loading data for assets: {self.assets_ix} from {self.alpha_config.start_sim_date} to {self.alpha_config.end_sim_date}")
        self.data_df = self.data_handler.load_data()

        # self.dates will be a list of dates following the ascending order
        self.dates = self.data_df.index.unique().tolist()

        self.data = [[] for _ in range(len(self.dates))]
        self.valid = [[] for _ in range(len(self.dates))]
        for di in range(len(self.dates)):
            for ai in range(len(self.assets_ix)):
                row = self.data_df.loc[self.dates[di]]
                row = row[row["symbol"] == self.assets_ix[ai]]
                if len(row) == 0:
                    self.data[di].append({
                        "open": float("nan"),
                        "high": float("nan"),
                        "low": float("nan"),
                        "close": float("nan"),
                        "volume": float("nan")
                    })
                    self.valid[di].append(False)
                row = row.iloc[0]
                self.data[di].append({
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": int(row["volume"])
                })
                self.valid[di].append(True)
        
        _logger.info(f"Data prepared with {len(self.dates)} dates and {len(self.assets_ix)} assets")

        # Prepare portfolio and portfolio_history
        for ai in range(len(self.assets_ix)):
            self.portfolio[ai] = {
                "cash": self.initial_capital / len(self.assets_ix),
                "positions": 0
            }

            self.portfolio_history[ai] = []
        
        _logger.info(f"Portfolio prepared with {len(self.assets_ix)} assets. Initial cash for each asset: {self.initial_capital / len(self.assets_ix)}")

        # Load the alpha module
        _logger.info(f"Loading alpha module from {self.alpha_config.alpha}")
        self.alpha_path = self.alpha_config.alpha
        import importlib
        try:
            self.alpha_module = importlib.import_module(self.alpha_path).Alpha()
            self.alpha_module.initialize(self.data, self.valid, self.assets_ix, self.dates)
        except Exception as e:
            _logger.error(f"Error loading alpha module: {e}")
            raise e

        _logger.info(f"Alpha module loaded successfully")


    def _update_portfolio(self, ai, price):
        self.portfolio[ai]["positions_value"] = (
            self.portfolio[ai]["positions"] * price
        )

        self.portfolio[ai]["total_value"] = (
            self.portfolio[ai]["cash"] + self.portfolio[ai]["positions_value"]
        )

        self.portfolio_history[ai].append(self.portfolio[ai]["total_value"])

    def _execute_trade(self, di, signals):
        for ai in range(len(self.assets_ix)):
            signal = signals[ai]
            price = self.data[di][ai]["close"]

            if signal > 0 and self.portfolio[ai]["cash"] > 0:  # Buy
                trade_value = self.portfolio[ai]["cash"]
                commission = self.calculate_commission(trade_value)
                shares_to_buy = (trade_value - commission) / price
                self.portfolio[ai]["positions"] += shares_to_buy
                self.portfolio[ai]["cash"] -= trade_value
            elif signal < 0 and self.portfolio[ai]["positions"] > 0:  # Sell
                trade_value = self.portfolio[ai]["positions"] * price
                commission = self.calculate_commission(trade_value)
                self.portfolio[ai]["cash"] += trade_value - commission
                self.portfolio[ai]["positions"] = 0
            
            self._update_portfolio(ai, price)
    
    def calculate_commission(self, trade_value):
        return max(
            self.commission_fixed,
            self.commission_pct * trade_value
        )

    def calculate_portfolio_value(self):
        portofolio_value = 0
        for ai in range(len(self.assets_ix)):
            portofolio_value += self.portfolio[ai]["total_value"]
        return portofolio_value

    def run_backtest(self):
        _logger.info("Running backtest from {} to {}".format(self.alpha_config.start_sim_date, self.alpha_config.end_sim_date))
        for di in tqdm(range(len(self.dates))):
            signals = self.alpha_module.generate_signals_for_di(di)
            self._execute_trade(di, signals)
            self.daily_portfolio_value.append(self.calculate_portfolio_value())

    def evaluate(self, plot=True, path_to_save="performance.png"):
        portfolio_values = pd.Series(self.daily_portfolio_value, index=self.dates)
        daily_returns = portfolio_values.pct_change()
        total_return = calculate_total_return(portfolio_values.iloc[-1], self.initial_capital)
        annualized_return = calculate_annualized_return(
            total_return, len(portfolio_values)
        )
        annualized_volatility = calculate_annualized_volatility(daily_returns)
        sharpe_ratio = calculate_sharpe_ratio(annualized_return, annualized_volatility)
        sortino_ratio = calculate_sortino_ratio(daily_returns, annualized_return)
        max_drawdown = calculate_maximum_drawdown(portfolio_values)

        # print out the stats with 3 decimal places
        _logger.info(f"Total Return: {total_return:.3f}")
        _logger.info(f"Annualized Return: {annualized_return:.3f}")
        _logger.info(f"Annualized Volatility: {annualized_volatility:.3f}")
        _logger.info(f"Sharpe Ratio: {sharpe_ratio:.3f}")
        _logger.info(f"Sortino Ratio: {sortino_ratio:.3f}")
        _logger.info(f"Max Drawdown: {max_drawdown:.3f}")

        if plot:
            self.plot_performance(portfolio_values, daily_returns, path_to_save)

    def plot_performance(self, portfolio_values: Dict, daily_returns: pd.DataFrame, path_to_save: str = "performance.png"):
        """Plot the performance of the trading strategy."""
        plt.figure(figsize=(10, 6))

        plt.subplot(2, 1, 1)
        plt.plot(portfolio_values, label="Portfolio Value")
        plt.title("Portfolio Value Over Time")
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(daily_returns, label="Daily Returns", color="orange")
        plt.title("Daily Returns Over Time")
        plt.legend()

        plt.tight_layout()
        plt.savefig(path_to_save)
        _logger.info(f"Performance plot saved to {path_to_save}")
