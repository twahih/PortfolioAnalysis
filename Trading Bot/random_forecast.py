# random_forecast.py

import numpy as np
import pandas as pd
#import Quandl   # Necessary for obtaining financial data easily

from backtest import Strategy, Portfolio

class RandomForecastingStrategy(Strategy):
    """Derives from Strategy to produce a set of signals that
    are randomly generated long/shorts. Clearly a nonsensical
    strategy, but perfectly acceptable for demonstrating the
    backtesting infrastructure!"""    
    
    def __init__(self, symbol, bars):
        """Requires the symbol ticker and the pandas DataFrame of bars"""
        self.symbol = symbol
        self.bars = bars
        
    def generate_signals(self):
        """Creates a pandas DataFrame of random signals."""
        signals = pd.DataFrame(index=self.bars.index)
        signals['signal'] = np.sign(np.random.randn(len(signals)).round())

        # The first five elements are set to zero in order to minimise
        # upstream NaN errors in the forecaster.
        signals['signal'][0:5] = np.random.randint(0,2,size=5)
        signals['signal'][0]=0
 
        return signals

class Crossover(Strategy):
    """Derives from Strategy to produce a set of signals that
    are randomly generated long/shorts. Clearly a nonsensical
    strategy, but perfectly acceptable for demonstrating the
    backtesting infrastructure!"""    
    
    def __init__(self, symbol, bars,short=5,long=15):
        """Requires the symbol ticker and the pandas DataFrame of bars"""
        self.symbol = symbol
        self.bars = bars
        self.short=short
        self.long=long
        
    def generate_signals(self):
        """Creates a pandas DataFrame of random signals."""
        signals = pd.DataFrame(index=self.bars.index)
        sma=self.bars['Open'].rolling(self.short).mean().fillna(0)
        lma=self.bars['Open'].rolling(self.long).mean().fillna(0)
        
        signals['signal'] = np.sign(sma-lma)

        # The first five elements are set to zero in order to minimise
        # upstream NaN errors in the forecaster.
        signals['signal'][0:5] = np.random.randint(0,2,size=5)
        signals['signal'][0]=0
 
        return signals

    
class MarketOnOpenPortfolio(Portfolio):
    """Inherits Portfolio to create a system that purchases 100 units of 
    a particular symbol upon a long/short signal, assuming the market 
    open price of a bar.

    In addition, there are zero transaction costs and cash can be immediately 
    borrowed for shorting (no margin posting or interest requirements). 

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, initial_capital=1000.0):
        self.symbol = symbol        
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()
        
    def generate_positions(self):
        """Creates a 'positions' DataFrame that simply longs or shorts
        100 of the particular symbol based on the forecast signals of
        {1, 0, -1} from the signals DataFrame."""
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        initial_shares=int(self.initial_capital/self.bars['Open'][0])
        
        n_shares=np.random.normal(initial_shares,1,size=len(positions))
        n_shares[0:5]=np.random.randint(0,initial_shares+1,5)
        positions['Shares'] = self.signals['signal']*n_shares.astype(int)
        Total_shares=0
        cash=self.initial_capital
        positions['Cash']=0
        for i in range(len(positions.index)):
            if positions.iloc[i,0]*self.bars.iloc[i,2]>cash:
                positions.iloc[i,0]=int(cash/self.bars.iloc[i,2])
                cash = cash - positions.iloc[i,0]*self.bars.iloc[i,2]
                Total_shares=Total_shares+positions.iloc[i,0]
                positions.iloc[i,1]=cash

            elif -positions.iloc[i,0]>Total_shares:
                positions.iloc[i,0]=-Total_shares if Total_shares !=0 else 0
                Total_shares=Total_shares+positions.iloc[i,0]
                cash=cash - positions.iloc[i,0] * self.bars.iloc[i,2]
                positions.iloc[i,1]=cash

            else:
                Total_shares=Total_shares + positions.iloc[i,0]
                cash=cash - positions.iloc[i,0] * self.bars.iloc[i,2]
                positions.iloc[i,1]=cash
 
        return positions          
                    
    def backtest_portfolio(self):
        """Constructs a portfolio from the positions DataFrame by 
        assuming the ability to trade at the precise market open price
        of each bar (an unrealistic assumption!). 

        Calculates the total of cash and the holdings (market price of
        each position per bar), in order to generate an equity curve
        ('total') and a set of bar-based returns ('returns').

        Returns the portfolio object to be used elsewhere."""

        # Construct the portfolio DataFrame to use the same index
        # as 'positions' and with a set of 'trading orders' in the
        # 'pos_diff' object, assuming market open prices.
        #portfolio = self.positions.multiply(self.bars['Open'],axis=0)
        portfolio = self.positions
        pos_diff = self.positions.diff()

        # Create the 'holdings' and 'cash' series by running through
        # the trades and adding/subtracting the relevant quantity from
        # each column
        portfolio['holdings'] = self.positions['Shares'].cumsum().multiply(self.bars['Open'],axis=0)
        portfolio['Cash'] = self.positions['Cash']

    
        # Finalise the total and bar-based returns based on the 'cash'
        # and 'holdings' figures for the portfolio 
    
    
        portfolio['total'] = portfolio['Cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()
        portfolio['Open']=self.bars['Open']
        portfolio['Total Shares']=portfolio['Shares'].cumsum()
        return portfolio        
                
    
            
    
    
    
    
    
    