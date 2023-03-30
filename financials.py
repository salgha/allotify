import yfinance as yf

def get_ticker_info(ticker):
    t = yf.Ticker(ticker).fast_info
    return t['last_price'], t['currency'].upper(), t['timezone'], t['exchange']

def get_currency_rate(**kwargs):
    if 'stock' in kwargs:
        base = yf.Ticker(kwargs.get('stock'))
        base_currency = '' if base.fast_info['currency'] == 'USD' else base.fast_info['currency']
    if 'currency' in kwargs:
        base_currency = kwargs.get('currency')
    return yf.Ticker(f'{base_currency}USD=X').fast_info['last_price']

    