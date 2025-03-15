# The user should be able to input assets file and alpha config as argument. This code need to create Backtester object and run the backtest. 

import argparse
from alpha_backtest.backtester import Backtester
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description='Backtest your alpha')
    parser.add_argument('--assets', type=str, help='Path to assets file', default="assets.txt")
    parser.add_argument('--alpha', type=str, help='Path to your alpha config file', default="alpha_config.yml")
    parser.add_argument('--initial_capital', type=float, help='Initial capital', default=10000.0)
    parser.add_argument('--commission_pct', type=float, help='Commission percentage', default=0.001)
    parser.add_argument('--commission_fixed', type=float, help='Fixed commission', default=1.0)
    parser.add_argument('--plot', action='store_true', help='Plot the backtest result')
    parser.add_argument('--path-to-save', type=str, help='Path to save the plot', default="backtest_result.png")
    args = parser.parse_args()

    backtester = Backtester(
        alpha_config_file=args.alpha, 
        assets_file=args.assets,
        initial_capital=args.initial_capital,
        commission_pct=args.commission_pct,
        commission_fixed=args.commission_fixed
    )

    backtester.run_backtest()
    backtester.evaluate(args.plot, args.path_to_save)

if __name__ == "__main__":
    main()
