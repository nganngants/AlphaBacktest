# AlphaBacktest

AlphaBacktest is a simulator to test your quantiative trading algorithms on historical data.

## NOTE
This backtest system is for educational purpose only. It is simple and definitely not suitable for production use.

## Installation

### Prerequisites
- Python 3.9 or higher
- uv package manager (https://github.com/astral-sh/uv)

## Building Source

1. Clone the repository:
   ```bash
   git clone https://github.com/nganngants/AlphaBacktest.git
   cd AlphaBacktest
   ```

2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Sync the dependencies:
   ```bash
   uv sync
   ```

## Usage 

### Prepare Data

You need to have an assets file which lists the assets symbol you want to backtest, each on a line. Note that the historical data will be fetched from Yahoo Finance by default. You can change data provider directly in `alpha_backtest/data_handler.py` file. Maybe I will add a config for this in the future.

### Writing an Alpha

Please refer to `examples/` for examples of writing an alpha. Basically, your alpha is a class which inherits alpha_backtest.AlphaBase. You need to implement `generate(self, di):` method to set the signal to `self.alpha`. 

The data used in this system is price-volume data. In your alpha, by accessing `self.data[di][ai]` (where di is the data index and ai is the asset index), you will have a dict which contains price-volume data of the ai-th asset

### Prepare Config

You need to have a config file which specifies the alpha class the start and end date of the backtest. Please refer to `alpha_config.yml` for example

### Run Backtest

```bash
python3 backtest.py
```

For full of the options, please run `python3 backtest.py --help`

