import streamlit as st
import pandas as pd
import yfinance as yf
import entries as ent
import errors as err
import equations as eqn
import tables as tbl
import charts as cht

app_title = 'Allotify'
st.set_page_config(page_title=app_title)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title(app_title)
st.write('''Rebalance stock portfolio through periodic contributions.''')

if 'instantiated' not in st.session_state:
    ent.load_empty()
    df_ss = st.session_state.df_ss
    # st.session_state.reject_uploaded_file = False
    st.session_state.instantiated = True

st.write('''Add any stock available in Yahoo! Finance in accordance with
    their [ticker symbol formatting](https://finance.yahoo.com/lookup). Add one
    or multiple cash positions using the prefix \$ followed by
    the 3-letter currency code (e.g. $USD).''')


ribbon_col1, ribbon_col2, ribbon_col3 = st.columns([3, 1, 1])
if ribbon_col1.button('Load Portfolio From CSV File', use_container_width=True):
    st.write('''Accepted format is comma-delimited raw values with no header. The columns
        should be in the same order; *Ticker*, *Current Shares*, and *Target Weight*.''')
    file_uploaded = st.file_uploader('Upload a file', type='CSV', key='file_uploaded',
        label_visibility='collapsed', on_change=ent.load_file)
ribbon_col2.button('See Example', on_click=ent.load_example, use_container_width=True)
ribbon_col3.button('Clear & Reset', on_click=ent.load_empty, use_container_width=True)

st.write('') #spacing

if 'filepath' in st.session_state:
    if err.check_files_errors():
        st.stop()

_, header_col2, header_col3, header_col4 = st.columns([1, 5, 5, 5])
header_col2.write('**Ticker Symbol**')
header_col3.write('**Current Shares (x)**')
header_col4.write('**Target Weight (%)**')

df_ss = st.session_state.df_ss

for i in df_ss.index:
    ent.display_row(i)

target_sum = df_ss['target_weight'].sum()
target_sum_color = 'red' if target_sum != 100 else 'green'

footer_col1, footer_col2, _, footer_col4  = st.columns([1, 5, 5, 5])
footer_col1.button('&plus;', on_click=ent.add_entry)
footer_col4.markdown(f'Total **:{target_sum_color}[{target_sum}%]**')

st.write('') #spacing

settings_col1, settings_col2, settings_col3 = st.columns([13, 14, 14])

allow_selling = settings_col1.checkbox(
    'Allow selling assets', value=False, key='allow_selling',
    help='Selling overweight assets. If disabled, only buying  underweight assets.')

allow_fractional = settings_col2.checkbox(
    'Allow fractional shares', value=False, key='allow_fractional',
    help='Distributing on fractional shares. If disabled, distributing on maximum whole shares possible.')

allow_groups = settings_col3.checkbox(
    'Allow grouping by region', value=True, key='allow_groups',
    help='''Grouping is done at final report for aesthetics. Not part of any core calculations.
        Disable if you see inaccurate or inconsistent grouping results.''')


# submit_disabled = err.check_entries_errors(df_ss)

submitted = st.button('Submit', disabled=False, type='primary', use_container_width=True)

if submitted:
    with st.spinner('Checking for errors...'):
        if err.check_entries_errors(df_ss):
            st.stop()
    with st.spinner('Working on allocations...'):
        df = eqn.compute_allocations(df_ss.copy(deep=True))
        st.write('#') 
        cht.display_pie_chart(df) 
        tbl.create_table(df)
        st.write('###')
        st.caption('''App uses delayed prices when making calculations. Stock prices or currency
            rates might be slightly different. The app does not take into account stock trading
            fees, currency conversion fees, money transfer fees, or any other fees. Allow some
            "buffer zone" in cash positions to account for that.''')