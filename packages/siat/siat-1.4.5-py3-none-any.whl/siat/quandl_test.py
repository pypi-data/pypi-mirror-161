# -*- coding: utf-8 -*-

start='2018-1-1'; end='2018-12-31'

import quandl
import quandl as qd
quandl.ApiConfig.api_key = "jPxsQBSvfxF_qhzTdydi"

# WTI Crude Oil price from the US Department of Energy
df1 = qd.get("EIA/PET_RWTC_D",start_date='2018-1-1',end_date='2021-10-31')

# 仅提取月底数值
df2 = qd.get("EIA/PET_RWTC_D",start_date='2018-1-1',end_date='2021-10-31', collapse="monthly")

# company profile and basic financial info
df3 = qd.get_table('ZACKS/FC', ticker='AAPL')

df4 = qd.get_table('ZACKS/FC', paginate=True)

df5 = quandl.get_table('ZACKS/FC', paginate=True, ticker='AAPL', qopts={'columns': ['ticker', 'per_end_date']})

df6 = quandl.get_table('ZACKS/FC', paginate=True, ticker=['AAPL', 'MSFT'], per_end_date={'gte': '2015-01-01'}, qopts={'columns':['ticker', 'per_end_date']})


df7=quandl.get('WIKI/AAPL',start_date='2018-1-1',end_date='2021-10-31')
#==============================================================================
import os
os.environ['QUANDL_API_KEY']="jPxsQBSvfxF_qhzTdydi" 

import pandas_datareader as web
df11=web.DataReader('HKEX/00700','quandl','2018-1-1','2021-10-31')
df12=web.DataReader('BSE/BOM532540','quandl','2018-1-1','2021-10-31')

# S&P Composite
df13=web.DataReader('YALE/SPCOMP','quandl','2018-1-1','2021-10-31')
df13b = quandl.get('YALE/SPCOMP',start_date='2018-1-1',end_date='2021-10-31')

quandl.ApiConfig.api_key = "jPxsQBSvfxF_qhzTdydi"
df13 = quandl.get('WIKI/AAPL',start_date='2018-1-1',end_date='2021-10-31', api_key="jPxsQBSvfxF_qhzTdydi") 
