# from logging.handlers import SocketHandler

import websocket, json, pprint
import sys, os, config, csv
import numpy as np
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.enums import SIDE_BUY,SIDE_SELL,ORDER_TYPE_LIMIT,ORDER_TYPE_MARKET,TIME_IN_FORCE_GTC
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
client = Client(config.API_KEY, config.API_SECRET)
balance = client.get_asset_balance(asset='USDT')
cash = (balance["free"])
cash_int = float(cash)
prices = client.get_all_tickers()
cp = (prices[11]["price"])
cp_int = float(cp)
begins = []

# quan = ((cash_int)/cp_int)
# new = "%.5f" % quan
# quantity = float(new)
# print(quantity)


def on_open(ws):
    print('open connection')

def on_close(ws, close_status_code, close_msg):
    print("closed connection")


def on_message(ws, message):
    global begins,in_position

    json_message = json.loads(message)
   
    price_info = json_message["k"]["c"]
    begins.append(float(price_info))
    initial_price = begins[0]
    array = np.array(begins)
    spread = array - initial_price
    max_value = np.max(spread)
    min_value = np.min(spread)
    quan = (11/begins[-1])
    new = "%.5f" % quan
    quantity = float(new)
    # print("quantity",quantity)
    print(spread[-1])
    if max_value > 2000:
        gain = max_value
        if spread[-1] < (gain - 400):
            print("sell", spread[-1])
         
            try:
              client.order_market_sell(symbol='BTCUSDT',quantity=quantity) 
            except Exception as e:
              print(e.message, "error")
              f = open('error.csv', 'w')
              writer = csv.writer(f)
              writer.writerow(e.message)
            os.execl(sys.executable, sys.executable, *sys.argv)

    if min_value < -2000:
        loss = min_value
        if spread[-1] > (loss + 400):
            print("buy", spread[-1])
            try:
               client.order_market_buy(symbol='BTCUSDT',quantity= quantity) 
            except Exception as e:
                print(e.message, "error")
                f = open('error.csv', 'w')
                writer = csv.writer(f)
                writer.writerow(e.message)
            os.execl(sys.executable, sys.executable, *sys.argv)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()