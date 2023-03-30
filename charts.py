import streamlit as st
import pandas as pd
import plotly.express as px

def display_pie_chart(df):
    df_aux = df.copy(deep=True)
    df_aux['ticker_type'] = df_aux['ticker_type'].str.capitalize()
    st_columns = ['left', 'middle', 'right']
    variables = ['pre_trade_weight', 'target_weight', 'post_trade_weight']
    names = ['Pre-Trade Weights', 'Target Weights', 'Post-Trade Weights']
    left, middle, right = st.columns(3)
    for st_column, variable, name in zip(st_columns, variables, names):
        df_aux[variable] = df_aux[variable] / 100
        fig = px.sunburst(df_aux, path=['ticker_type', 'base_currency', 'ticker'],
            values=variable, color='ticker_type')  
        fig.update_traces(hovertemplate='%{value:.2%}')
        fig.update_layout(autosize=False, width=390, height=300, margin = dict(l=0, r=0, t=22, b=0),
            title = {'text':name, 'y':1.0, 'x':0.5, 'xanchor':'center', 'yanchor':'top'})
        locals()[st_column].plotly_chart(fig, use_container_width=True, config= {'displayModeBar': False})