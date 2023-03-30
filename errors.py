import streamlit as st
import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype
import financials as fin

common_info_msg = '''Please read [the guide](/GUIDE.md)
    for more details on using this app.'''

'''
Uploads
'''

# file has header
def check_files_error_01(dfx, dfy):
    if (tuple(dfx.dtypes) != tuple(dfy.dtypes)):
        st.error('''It looks like the uploaded file includes a header.
        Please ensure no header in your file.''')
        return True
    return False

# file has extra columns
def check_files_error_02(dfx):
    if len(dfx.columns) > 3:
        st.error('''It looks like the uploaded file includes
            more than three columns. Please ensure no more
            than three columns in your file.''')
        return True
    return False

# column dtype improper
def check_files_error_03(dfx):
    first = 1
    for i in dfx.columns:
        if first:
            first = 0
            if not (is_string_dtype(dfx.loc[:, i]) or is_numeric_dtype(dfx.loc[:, i])):
                st.error('''It looks like the first column of the uploaded
                    file contains unsupported data. Please ensure it only
                    contains either textual or numerical data.''')
                return True
        else:
            if not is_numeric_dtype(dfx.loc[:, i]):
                st.error('''It looks like the second and/or third columns
                    of the uploaded file contain unsupported data.
                    Please ensure they only contain numerical data.''')
                return True
    return False


def check_files_errors():
    filepath = st.session_state.filepath
    try:
        dfx = pd.read_csv(filepath, header=None, thousands=',')
        dfy = pd.read_csv(filepath, header=0, thousands=',')
    except:
        st.error('''Something went wrong while reading your file.
        Please make sure to follow the accepted format.''')
        st.info(common_info_msg)
        return True

    if check_files_error_01(dfx, dfy):
        st.info(common_info_msg)
        return True
    
    if any([
        check_files_error_02(dfx),
        check_files_error_03(dfx)
        ]):
        st.info(common_info_msg)
        return True
    return False


'''
Entries
'''

# tickers below 2
def check_entries_error_01(df):
    if len(df) < 2:
        st.error('''Insufficient entries.
            Please type in at least two entries.''')
        return True
    return False

# any ticker is blank
def check_entries_error_02(df):
    if len(df[df['ticker'] == '']) > 0:
        st.error('''Ticker cannot be blank.
            Please type in a valid ticker or remove its entry.''')
        return True
    return False

# sum target weight is not 100%
def check_entries_error_03(df):
    if df['target_weight'].sum() != 100:
        st.error('''Incorrect target weights. Please make sure
            the sum total of all target weights equals 100%.''')
        return True
    return False

# duplicates entries
def check_entries_error_04(df):
    if df['ticker'].duplicated().any():
        st.error('''Duplicate tickers found. Please make sure
            no duplicate tickers are entered.''')
        return True
    return False

# duplicates !$ cash positions
def check_entries_error_05(df):
    if len(df.loc[df['ticker'].str.startswith('!$')]) > 1:
        st.error('''Multiple !\$-prefixed tickers found. Please make
            sure only a signle !\$-prefixed cash position is entered.''')
        return True
    return False

# no cash position and not allow_selling
def check_entries_error_06(df):
    if not st.session_state.allow_selling:
        if any(list(map(lambda x: x.startswith('$'), df['ticker']))):
            pass
        elif any(list(map(lambda x: x.startswith('!$'), df['ticker']))):
            pass
        else:
            st.error('''No cash inflow. Please enter at least one
                cash position or allow selling assets.''')
            return True
    return False

# rejected/unrecognized tickers
def check_entries_error_07(df):
    tickers_rejected = []
    for i in df[df['ticker'] != ''].index:
        ticker = df.loc[i, 'ticker']
        # reject crypto  and futures
        if '=' in ticker or '-' in ticker:
            tickers_rejected.append(ticker)
        # reject unrecognized currencies
        elif ticker.startswith('$'):
            try:
                _ = fin.get_currency_rate(currency=ticker[1:])
            except KeyError:
                tickers_rejected.append('$' + ticker[1:])
        elif ticker.startswith('!$'):
            try:
                _ = fin.get_currency_rate(currency=ticker[2:])
            except KeyError:
                tickers_rejected.append('!$' + ticker[2:])
        # reject unrecognized stocks        
        else:
            try:
                *_, exchange = fin.get_ticker_info(ticker)
            except KeyError:
                tickers_rejected.append(ticker)
    if len(tickers_rejected):
        tickers_rejected = ", ".join(str(x) for x in tickers_rejected)
        st.error(f'''Could not recognize ticker(s): {tickers_rejected}.
            Please make sure to follow Yahoo! Finance ticker symbol formatting''')
        return True
    return False

def check_entries_errors(df):
    if any([
        check_entries_error_01(df),
        check_entries_error_02(df),
        check_entries_error_03(df),
        check_entries_error_04(df),
        check_entries_error_05(df),
        check_entries_error_06(df),
        check_entries_error_07(df)
        ]):
        st.info(common_info_msg)
        return True
    return False