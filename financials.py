import yfinance as yf

def get_ticker_info(ticker):
    t = yf.Ticker(ticker).info
    return t['previousClose'], t['currency'].upper(), t['timeZoneFullName'], t['exchange']

def get_currency_rate(**kwargs):
    if 'stock' in kwargs:
        base = yf.Ticker(kwargs.get('stock'))
        base_currency = '' if base.info['currency'] == 'USD' else base.info['currency']
    if 'currency' in kwargs:
        base_currency = kwargs.get('currency')
    return yf.Ticker(f'{base_currency}USD=X').info['previousClose']