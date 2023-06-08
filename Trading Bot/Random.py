
import os
import time
import alpaca_trade_api as tradeapi
import Trade
from config import *
import numpy as np


BASE_URL=Trade.ENDPOINT_URL
HEADERS={'APCA-API-KEY-ID':API_KEY,'APCA-API-SECRET-KEY':SECRET_KEY}
Account_URL="{}/v2/account".format(BASE_URL)
ORDERS_URL="{}/v2/orders".format(BASE_URL)
alpaca=tradeapi.REST(API_KEY,SECRET_KEY,BASE_URL,api_version='v2')

def place_order():
    signal=np.random.randn(1)
    side=None
    qty=np.random.randint(100)
    r='No Acction'
    if signal>1:
        side='sell'
        r=alpaca.submit_order('AAPL',qty,side,'market','gtc')
        action=r.side +" "+r.qty+" "+r.symbol +" "+str(r.created_at)
    elif signal<-1:
        side='buy'
        r=alpaca.submit_order('AAPL',qty,side,'market','gtc')
        action=r.side +" "+r.qty+" "+r.symbol +" "+str(r.created_at)
    else:
        action='No Transaction'
    return action
    
    
while(True):
    time.sleep(10)
    print(place_order())
