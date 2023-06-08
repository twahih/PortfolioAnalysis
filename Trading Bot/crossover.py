import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
import alpaca_trade_api as tradeapi
from config import *
import os
import time

#SET ALAPACA API ENVIRONMENT VARIABLES 
HEADERS={'APCA-API-KEY-ID':API_KEY,'APCA-API-SECRET-KEY':SECRET_KEY}
alpaca=tradeapi.REST(API_KEY,SECRET_KEY,BASE_URL,api_version='v2')

#SET ALPHA VINTAGE ENVIRONMENT VARIABLES 
ts=TimeSeries(key=ALPHA_API_KEY,output_format='pandas')
sympol='DAL'

def place_order():
    data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='compact')
    Account=alpaca.get_account()
    BuyPwr=float(Account.buying_power)/float(Account.initial_margin)
    
    try:
        SellPwr=alpaca.get_position(symbol).qty
    except:
        SellPwr =0
        
    MA10=data['4. close'].rolling(10).mean()[-1]
    MA20=data['4. close'].rolling(20).mean()[-1]
    qty=np.random.randint(100)
    r='No Acction'
    if MA10>MA20 and BuyPwr>0:
        side='buy'
        qty= qty if qty<BuyPwr else int(BuyPwr)
        r=alpaca.submit_order(sympol,qty,side,'market','gtc')
        Account=alpaca.get_account()
        status=r.side +" "+r.qty+" "+r.symbol+" at $"+Account.initial_margin +" Acct Val:"+Account.portfolio_value
    elif MA10<MA20 and SellPwr>0 :
        side='sell'
        qty = qty if qty<=SellPwr else SellPwr
        r=alpaca.submit_order(symbol,qty,side,'market','gtc')
        Account=alpaca.get_account()
        status=r.side +" "+r.qty+" "+r.symbol+" at $"+Account.initial_margin +" Acct Val:"+Account.portfolio_value
    else:
        Account=alpaca.get_account()
        Status='No Transaction'+ " [INFO] Acct Val: $ " + Account.portfolio_value +" "+str(MA10>MA20) + " "+str(SellPwr) +" Sell Pwr"
    return Status

while(True):
    time.sleep(60)
    print(place_order())