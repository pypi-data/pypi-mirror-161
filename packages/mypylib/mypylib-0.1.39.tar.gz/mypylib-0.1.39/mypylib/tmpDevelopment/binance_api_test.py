
from binance.cm_futures import CMFutures

cm_futures_client = CMFutures()

# get server time
print(cm_futures_client.time())


key = 'pDd6UbK3bHJjR2ZpHhg5Pmg2Iog7ajDEDrFW2cLwzrRJlN3lzr92Msf96hPbdBl1'
secret = 'tUZ9gnauoRW6dp519bd8UxDOOAxZMiUhep7JTL2pjxUXChZW4doR7vtRAsWpMK9I'

cm_futures_client = CMFutures(key=key, secret=secret)

# Get account information
print(cm_futures_client.account())

# Post a new order
params = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': 0.002,
    'price': 59808
}

response = cm_futures_client.new_order(**params)
print(response)
