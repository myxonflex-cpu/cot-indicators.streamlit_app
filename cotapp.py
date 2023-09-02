#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import matplotlib.pyplot as plt
import datetime
import pandas as pd
from dash import Dash 
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
TODAY = datetime.date.today()
today_day = TODAY.strftime('%Y-%m-%d')


st.set_page_config(layout="wide", page_title="Cot App")
tab1, tab4, = st.tabs(["COT REPORTS", "INDICATORS"])

##########  CREATING DATASETS ###############
cot_reports = pd.read_hdf('./data/dash_main.h5', key='filtered_cot_reports',)
forex = pd.read_hdf('./data/dash_main.h5', key='filtered_oanda_2', )
forex_4h = pd.read_hdf("./data/dash_main_4h.h5", key='filtered_oanda_4')



# Convert date indexes to format "%Y-%m-%d"
cot_reports.index = cot_reports.index.set_levels(pd.to_datetime(cot_reports.index.levels[1], format="%Y-%m-%d"), level=1)
forex.index = forex.index.set_levels(pd.to_datetime(forex.index.levels[1], format="%Y-%m-%d"), level=1)


# Get the date range of the forex dataframe
starting_date = forex.index.get_level_values('date').min()
ending_date = forex.index.get_level_values('date').max()
date_range = pd.date_range(starting_date, ending_date)


com_date_range = pd.date_range("2020.06.20", "2023.01.01" )#com_starting_date, com_ending_date)


# Reindex the cot_reports dataframe to match the date range of forex
cot_reports = cot_reports.reindex(pd.MultiIndex.from_product([cot_reports.index.levels[0], date_range], names=['ticker', 'date']))

# Forward fill missing values in cot_reports
cot_reports = cot_reports.groupby(level=0,group_keys=False).apply(lambda x: x.ffill().fillna(method='bfill'))



########## CREATE SIDEBAR ############

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background: linear-gradient(to bottom, #A0BFE0  0%,#4A55A2 100%);
background-position: top left;
}}

        
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

.stTabs [data-testid="stMarkdownContainer"] p {{
 background-color:"green"}}

.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
    font-size:1.5rem;
    font:"serif";
    }}

[data-testid="stSidebar"] >  div:first-child {{
background: linear-gradient(to bottom, #4A55A2  0%,#352F44  100%); 
background-position: top left;
background-attachment: fixed;
}}

[data-testid="st.tabs"] >  div:first-child {{
<h3></h3>
}}

</style>
"""

st.markdown(  """
  <style>
  .css-16idsys.e16nr0p34 {
    background-color: #A0BFE0; 
            
    
  }
  </style>
""", unsafe_allow_html=True)

#side bar
st.sidebar.image("data/logo1.png")
st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown("""
            <style>
                .css-18e3th9 {
                        padding-top: 0rem;
                        padding-bottom: 0rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
                .css-1d391kg {
                        padding-top: 0rem;
                        padding-right: 1rem;
                        padding-bottom: 0rem;s
                        padding-left: 1rem;
                    }
            </style>
        """, unsafe_allow_html=True)

library =   {
            
            "AUD": "Australian D",
            "MXN": "Mexican Peso",
            "CAD": "Canadian D",
            "BRL": "Brazilian Real",
            "CHF": "Swiss Frank",
            "EUR": "Euro",
            "USD": "US Dollar",
            "JPY": "Japanese Yen",
            "GBP": "British Pound",
            "NZD": "New Zealand D",
            }


css = """
<style>
    .stTabs [data-baseweb="tab-highlight"] {
        background-color:transparent;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)
### ### ### ### ### ### ### Sidebar ### ### ### ### ### ### ###


today = datetime.date.today()
column = st.sidebar.columns((1, 1))
selected = ["Dealer Longs", "Dealers Longs vs O.I.",
            "Dealer Shorts", "Dealers Nets vs O.I.",
            "Net Dealers", "Total Net", "WILLCO 126",
            "D.N Yearly Stoc","Total.N Yearly Stoc"]
with column[0]:
    forex_pair = st.sidebar.selectbox("**TICKER**", (forex.index.get_level_values("ticker").unique()), label_visibility = "collapsed")

val1, val2 = [library[currency] for currency in forex_pair.split("_")]
cot_instrument = val1                            
second = val2                                   

with column[1]:
    cot_report = st.sidebar.selectbox("**COT Ind selected**",(selected), label_visibility = "collapsed")

with column[0]:
    start_date = st.date_input(label = "**FROM**", value= pd.to_datetime("2020-06-20", format="%Y-%m-%d"), label_visibility = "collapsed")

with column[1]:
    end_date = st.date_input(label = "**TO**", value = today, label_visibility = "collapsed")
    cot_indicator = st.sidebar.selectbox("**COT Ind full**",(cot_reports.columns ), label_visibility = "collapsed")



with tab1:
############# TOP CHART (PAIR PRICE) ###############

    forex_coin = forex.loc[forex_pair]["close"]
    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.12,  row_heights=[0.40, 0.3, 0.3])
    fig.add_trace(go.Scatter(x=forex_coin.index, y = forex_coin,fill='tozeroy',
                             line = dict(color='#4A55A2', width=2),
                             name = f"{forex_pair.upper()}"),row=1, col=1)
    
    start_time = pd.to_datetime(start_date, format="%Y-%m-%d")
    end_time = pd.to_datetime(end_date, format="%Y-%m-%d")
    mask_forex = (forex_coin.index > str(start_time)) & (forex_coin.index <= str(end_time))
    max_close = forex_coin.loc[mask_forex].max()
    min_close = forex_coin.loc[mask_forex].min()
    fig.update_layout(yaxis_range=[min_close, max_close,], uniformtext_minsize=12)
    fig.add_annotation(text=f"{forex_pair}",
                      xref="paper", yref="paper", font=dict(size=50, color="white"), opacity=0.4,
                      x=0, y=1, showarrow=False)
    fig.update_layout(xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False))

    
########## PLOT 2 #############

    cot_coin_1 = cot_reports.loc[cot_instrument]
    cot_coin_second_1 = cot_reports.loc[second]
    diff_of_df = cot_coin_1[cot_report] - cot_coin_second_1[cot_report]

    start_time = pd.to_datetime(start_date, format="%Y-%m-%d")
    end_time = pd.to_datetime(end_date, format="%Y-%m-%d")
    mask_diff = (diff_of_df.index > str(start_time)) & (diff_of_df.index <= str(end_time))
    max_diff = diff_of_df.loc[mask_diff].max()
    min_diff = diff_of_df.loc[mask_diff].min()

    fig.add_trace(go.Scatter(x=diff_of_df.index, y=diff_of_df, fill='tozeroy', 
                             name=cot_report, line=dict(color='rgb(203,2013,232)', width=2)), row=2, col=1)

    fig.update_yaxes(range=[min_diff, max_diff ], row=2, col=1)
    fig.update_xaxes(range=[start_date, end_date])
    fig.update_layout(showlegend=False )
    fig.add_annotation(text=f"Diff of {cot_report}",
                      xref="paper", yref="paper", font=dict(size=30, color="white"), opacity=0.4,
                      x=0.0, y=0.38, showarrow=False)


######## PLOT 3 ###########

    cot_coin_extra = cot_reports.loc[cot_instrument]
    cot_coin_second_extra =  cot_reports.loc[second]
    diff_of_coins2 = (cot_coin_extra[cot_indicator] - cot_coin_second_extra[cot_indicator])

    mask_extra = (diff_of_coins2.index > str(start_time)) & (diff_of_coins2.index <= str(end_time))
    max_extra = diff_of_coins2.loc[mask_extra].max()
    min_extra = diff_of_coins2.loc[mask_extra].min()

    diff_of_coins2 = (cot_coin_extra[cot_indicator] - cot_coin_second_extra[cot_indicator])
    fig.add_trace(go.Scatter(x=diff_of_coins2.index, y=diff_of_coins2,  fill='tozeroy',
                              name=f"DIFF of {cot_instrument} and {second} in {cot_indicator}",
                              line=dict(color='rgb(180,151,231)', width=2)), row=3, col=1)
                         
    
    fig.update_xaxes(range=[start_date, end_date])
    fig.update_yaxes(range=[min_extra, max_extra ], row=3, col=1)

    fig.add_annotation(text=f"Diff of {cot_indicator}",
                      xref="paper", yref="paper", font=dict(size=30, color="white"), opacity=0.4,
                      x=0.0, y=0.0, showarrow=False)


    fig.update_layout(  paper_bgcolor='rgb(0,0,0,0)', 
                        plot_bgcolor='rgb(0,0,0,0)' )
    fig.update_layout(  hovermode="x unified", 
                        height = 1000  )
    fig.update_traces(  xaxis='x1'  )

    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(showgrid=False))
    st.plotly_chart(fig, use_container_width=True)


start_date = "2020-06-20"
end_date = end_date
start_date = pd.to_datetime(start_date, format="%Y-%m-%d")
end_date = pd.to_datetime(end_date, format="%Y-%m-%d")
mask = (forex_4h.index.get_level_values(1) >= start_date) & (forex_4h.index.get_level_values(1) <= end_date)
subset_forex_4h = forex_4h.loc[mask]

with tab4:
    ind_tab4 = "Alpha 66V.1"

    forex_coin_4H = subset_forex_4h.loc[forex_pair]

    fig9 = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.12, row_heights=[0.4, 0.3, 0.3])
    
    fig9.add_trace(go.Scatter(x=forex_coin_4H.index, y=forex_coin_4H["close"], 
                              line=dict(color='black', width=1),name = f"{forex_pair.upper()}"), row=1, col=1)
    
    fig9.add_trace(go.Scatter(x=forex_coin_4H.index, y=forex_coin_4H["Alpha 31V.1"].rolling(30).mean() -0.5,
                              line=dict(color='blue', width=1),name = "Alpha 31V.1",), row=2, col=1)
    
    fig9.add_trace(go.Scatter(x=forex_coin_4H.index, y= -forex_coin_4H["Alpha 39V.1"].rolling(30).mean(),
                              line=dict(color='rgb(203,2013,232)', width=1),name="Alpha 39V.1",), row=2, col=1)
    
    fig9.add_trace(go.Scatter(x=forex_coin_4H.index, y= forex_coin_4H[ind_tab4], line=dict(color='rgb(180,151,231)', width=1), name=f"{ind_tab4}",), row=3, col=1)

    fig9.update_traces(hovertemplate="%{x|%Y-%m-%d}", hoverinfo="skip")
            
    fig9.update_layout(hovermode="x unified", width=800, height=1000)

    fig9.update_traces(xaxis='x1')
    fig9.update_layout(paper_bgcolor='rgb(0,0,0,0)', plot_bgcolor='rgb(0,0,0,0)', showlegend=False)
    fig9.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig9.for_each_yaxis(lambda x: x.update(showgrid=False))

    st.plotly_chart(fig9, use_container_width=True)