import streamlit as st
import pandas as pd

def add_row(row_class, label, amount, shares=0, price=0):
    html = '<tr class="record">'
    if row_class == 'header':
        html += f'<td class="{row_class}">{label}</td>'
        html += f'<td class="{row_class}">{price}</td>'
        html += f'<td class="{row_class}">{shares}</td>'
        html += f'<td class="{row_class}">{amount}</td>'
    else:
        if row_class == 'section' or row_class == 'subsection':
            html += f'<td colspan="3" class="{row_class}-labels">{label}</td>'
        else:
            html += f'<td class="{row_class}-labels">{label}</td>'
            html += f'<td class="{row_class}-values">${price:,.2f}</td>'
            html += f'<td class="{row_class}-values">{shares:,.2f}</td>'
        html += f'<td class="{row_class}-values">${amount:,.2f}</td>'
    html += '</tr>' 
    return html

def get_inflow(df):
    html = ''
    df = df.loc[((df['ticker_type'] == 'cash') | (df['output_value'] < 0)) & (df['entry_type'] != 'app')]
    for i in df.index:
        if df.loc[i, 'ticker_type'] == 'cash':
            df.loc[i, 'aux_value'] = df.loc[i, 'market_value']
            df.loc[i, 'aux_shares'] = df.loc[i, 'current_shares']
        else:
            df.loc[i, 'aux_value'] = abs(df.loc[i, 'output_value'])
            df.loc[i, 'aux_shares'] = abs(df.loc[i, 'output_shares'])
    html += add_row('section', 'Cash Inflow', df['aux_value'].sum() )
    for i in df.index:        
        html += add_row('item', df.loc[i, 'ticker'],
            df.loc[i, 'aux_value'], df.loc[i, 'aux_shares'], df.loc[i, 'last_price'])
    return html

def get_outflow(df):
    allow_groups = st.session_state.allow_groups
    df = df.loc[df['output_value'] > 0]
    html = add_row('section', 'Cash Outflow', df['output_value'].sum())
    if allow_groups:
        groups = df.loc[df['output_value'] > 0].groupby('timezone')
        for group in groups.indices:
            df = groups.get_group(group)
            html += add_row('subsection', group, df['output_value'].sum())
            for i in df.index:
                html += add_row('item', df.loc[i, 'ticker'],
                    df.loc[i, 'output_value'], df.loc[i, 'output_shares'], df.loc[i, 'last_price'])
    else:
        for i in df.index:
            html += add_row('item', df.loc[i, 'ticker'],
                df.loc[i, 'output_value'], df.loc[i, 'output_shares'], df.loc[i, 'last_price'])
    return html

def get_excess(df):
    allow_fractional = st.session_state.allow_fractional
    html = ''
    if allow_fractional:
        return html
    else:
        df = df.loc[df['excess_cash'] > 0]
        html += add_row('section', 'Cash Excess', df['excess_cash'].sum())
        for i in df.index:
            html += add_row('item', df.loc[i, 'ticker'],
                df.loc[i, 'excess_cash'], df.loc[i, 'output_shares'], df.loc[i, 'last_price'])
        return html

def create_table(df):
    html = '<table class="report">'
    html += '<colgroup><col class="labels">'
    html += '<col></colgroup>'
    html += add_row('header', '', 'Amount', 'Shares', 'Price')
    html += get_inflow(df)
    html += get_outflow(df)
    html += get_excess(df)
    html += '</table>'
    return st.markdown(html, unsafe_allow_html=True)