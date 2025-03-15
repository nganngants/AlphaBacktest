from alpha_backtest import AlphaBase

class AlphaSMA(AlphaBase):
    def __init__(self, short_window=40, long_window=100):
        self.short_window = short_window
        self.long_window = long_window

    def generate(self, di):
        for ai in range(len(self.asset_ix)):
            if not self.valid[di][ai]:
                continue
            short_sma = self._calculate_sma(di, ai, self.short_window)
            long_sma = self._calculate_sma(di, ai, self.long_window)

            if short_sma > long_sma:
                self.alpha[ai] = 1
            else:
                self.alpha[ai] = -1

    def _calculate_sma(self, di, ai, window):
        if di < window:
            return 0
        sma = 0
        for i in range(window):
            sma += self.data[di - i][ai]["close"]
        return sma / window
