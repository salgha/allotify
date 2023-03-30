import streamlit as st
import pandas as pd
import financials as fin

def compute_allocations(df):
    allow_selling = st.session_state.allow_selling
    allow_fractional = st.session_state.allow_fractional

    # add columns ['last_price', 'base_currency', 'ticker_type'] and get their values
    try:
        for i in df.index:
            ticker = df.loc[i, 'ticker']
            if ticker.startswith('$'):
                df.loc[i, 'last_price'] = fin.get_currency_rate(currency=ticker[1:])
                df.loc[i, 'base_currency'] = ticker[1:]
                df.loc[i, 'ticker_type'] = 'cash'
            elif ticker.startswith('!$'):
                df.loc[i, 'last_price'] = fin.get_currency_rate(currency=ticker[2:])
                df.loc[i, 'base_currency'] = ticker[2:]
                df.loc[i, 'ticker_type'] = 'cash'
            else:
                price, currency, timezone, _ = fin.get_ticker_info(ticker)
                df.loc[i, 'last_price'] = price * fin.get_currency_rate(stock=ticker)
                df.loc[i, 'base_currency'] = currency
                df.loc[i, 'timezone'] = timezone
                df.loc[i, 'ticker_type'] = 'stock'
    except:
        st.error('''Something went wrong while obtaining financial data from Yahoo! Finance.
            Please try again after sometime.''')
        st.stop()

    # make some adjustments prior to calculations
    df['ticker'] = df['ticker'].str.upper()
    df['timezone'] = df['timezone'].fillna('Global')
    df['entry_type'] = 'user'

    # add tiny amount of cash when user allow_selling and has none cash position
    # this is to smooth calculations and to store excess cash if any
    if allow_selling and 'cash' not in df['ticker_type'].values:
        df.loc[len(df)] = ['$USD', 0.0001, 0, 1, 'USD', 'Global', 'cash', 'app']

    # add and compute new columns ['market_value', 'pre_trade_weight']
    df['market_value'] = df['current_shares'] * df['last_price']
    df['pre_trade_weight'] = 100 * df['market_value'] / df['market_value'].sum()

    # 'cash' is handheld differently from stocks;
    #     1. Store 'cash' total amount in variable outside of dataframe
    #     2. Set its dataframe 'market_value' to 0
    #     3. While computing, simulatie purchasing 'cash' to meet 'target_weight', if any
    #     4. Add excess cash, if any

    # if 'cash' in df.ticker_type.values:
    # sum cash and store for later use
    cash_values = df.loc[df['ticker_type'] == 'cash', 'market_value']
    cash_sum = cash_values.sum()

    # set 'market_value' for all 'cash' entries to 0
    df.loc[df['ticker_type'] == 'cash', 'market_value'] = 0

    # compute difference; return absolute difference between current 'market_value'
    # and what it should be to meet 'target_weight' regardless of any conditions
    df['difference'] = (cash_sum + df['market_value'].sum()) * (df['target_weight']/100) - df['market_value']

    # set all negative 'difference' values to 0 for allow_selling == False
    if not allow_selling:
        df.loc[df['difference'] < 0, 'difference'] = 0

    # compute 'fractional_value' for allow_fractional == True,
    # and use it to compute 'whole_value' for allow_fractional == False
    df['fractional_value'] = cash_sum * (df['difference'] / df['difference'].sum())
    df['whole_value'] = (df['fractional_value'] // df['last_price']) * df['last_price']

    # assign output_value according to choice (either fractional or whole)
    # if choice == whole shares
    if not allow_fractional:
        df['output_value'] =  df['whole_value']
        excess_cash = df['fractional_value'].sum() - df['whole_value'].sum()
        
        # distributie excess cash
        # dump all excess cash in !$ cash position if present
        if len(df[df['ticker'].str.startswith('!$')]):
            i = df.loc[df['ticker'].str.startswith('!$')].index
            df.loc[i, 'excess_cash'] = excess_cash
        # distributie excess cash between all cash positions according to their pre_trade_weight
        else:
            df.loc[df['ticker_type'] == 'cash', 'excess_cash'] = excess_cash \
                    * (df['pre_trade_weight']/df.loc[df['ticker_type'] == 'cash', 'pre_trade_weight'].sum())

        df['excess_cash'] = df['excess_cash'].fillna(0)

    # if choice == fractional shares
    else:
        df['output_value'] = df['fractional_value']
        excess_cash = 0
        df['excess_cash'] = 0

    # compute output_shares
    df['output_shares'] = (df['output_value'] + df['excess_cash']) / df['last_price']

    # compute post_trade_weight
    df['post_trade_weight'] = 100 * (
        df['market_value'] + df['output_value'] + df['excess_cash']) / (
            df['market_value'].sum() + df['output_value'].sum() + df['excess_cash'].sum())

    # reassign pre-stored cash market_value for final reporting
    # not related to any calculations, aesthetics only
    df.loc[df['ticker_type'] == 'cash', 'market_value'] = cash_values

    # drop entries by app above for fractional shares  
    # this is so there are not part of the final reporting
    # not related to any calculations, aesthetics only
    if allow_fractional:
        df = df[df['entry_type'] != 'app']

    return df