import streamlit as st
import pandas as pd
from io import StringIO
from uuid import uuid4
import errors as err

def load_file():
    file_uploaded = st.session_state.file_uploaded
    if file_uploaded:
        content = StringIO(file_uploaded.getvalue().decode("utf-8")).read()
        filepath = f"/tmp/{uuid4()}"
        with open(filepath, "w") as f:
            f.write(content)
        st.session_state.filepath = filepath
        st.session_state.df_ss = pd.read_csv(filepath,
            names=['ticker', 'current_shares', 'target_weight'], thousands=',')
        st.session_state.df_ss = st.session_state.df_ss.fillna(0)
        st.session_state.count = len(st.session_state.df_ss)

def load_example():
    if 'filepath' in st.session_state:
        del st.session_state.filepath
    st.session_state.df_ss = pd.DataFrame(
        {'ticker': ['XOM', 'BKR', 'BP.L', '2222.SR', '$USD', '$GBP', '$SAR'],
        'current_shares': [7, 22, 1, 36, 2319.64, 2389, 331.13],
        'target_weight': [26, 18, 32, 24, 0, 0, 0]})
    st.session_state.count = 7    

def load_empty():
    if 'filepath' in st.session_state:
        del st.session_state.filepath
    st.session_state.df_ss = pd.DataFrame(
        {'ticker': [''],
        'current_shares': [0.0],
        'target_weight': [0.0]})
    st.session_state.count = 1

def add_entry():
    df_ss = st.session_state.df_ss
    df_ss.loc[st.session_state.count] = ['', 0.0, 0.0]
    st.session_state.count += 1

def del_entry(idx):
    df_ss = st.session_state.df_ss
    st.session_state.df_ss = df_ss.drop(idx)
    del st.session_state[f't_{idx}']
    del st.session_state[f's_{idx}']
    del st.session_state[f'w_{idx}']

def update_entry(idx):
    df_ss = st.session_state.df_ss
    df_ss.loc[idx, 'ticker'] = st.session_state[f't_{idx}']
    df_ss.loc[idx, 'current_shares'] = st.session_state[f's_{idx}']
    df_ss.loc[idx, 'target_weight'] = st.session_state[f'w_{idx}']

def display_row(idx):
    df_ss = st.session_state.df_ss
    col1, col2, col3, col4 = st.columns([1, 5, 5, 5])
    col1.button('&minus;', key=f'del_{idx}', on_click=del_entry, args=[idx])
    col2.text_input(
        label=f't_{idx}', value=df_ss.loc[idx, 'ticker'],
        label_visibility='collapsed', key=f't_{idx}',
        on_change=update_entry, args=[idx])
    col3.number_input(
        label=f's_{idx}', value=df_ss.loc[idx, 'current_shares'].astype(float),
        min_value=0.0, step=0.01, format='%.2f',
        label_visibility='collapsed', key=f's_{idx}',
        on_change=update_entry, args=[idx])
    col4.number_input(
        label=f'w_{idx}', value=df_ss.loc[idx, 'target_weight'].astype(float),
        min_value=0.0, step=0.01, format='%.2f',
        label_visibility='collapsed', key=f'w_{idx}',
        on_change=update_entry, args=[idx])