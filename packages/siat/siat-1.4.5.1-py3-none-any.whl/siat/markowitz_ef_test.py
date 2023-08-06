# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat import *
#------------------------------------------------------------------------------
#导入包
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as sco

#------------------------------------------------------------------------------
#获取股票数据

start='2021-01-01'
end='2021-11-30'

df = pd.DataFrame()
df = get_prices('600519.SS', start, end) 
df['p_change']=df['Close'].pct_change()
s600519 = df['p_change']
s600519.name = '600519'

df = pd.DataFrame()
df = get_prices('000651.SZ', start, end) 
df['p_change']=df['Close'].pct_change()
s000651 = df['p_change']
s000651.name = '000651'

df = pd.DataFrame()
df = get_prices('000002.SZ', start, end) 
df['p_change']=df['Close'].pct_change()
s000002 = df['p_change']
s000002.name = '000002'

df = pd.DataFrame()
df = get_prices('601318.SS', start, end) 
df['p_change']=df['Close'].pct_change()
s601318 = df['p_change']
s601318.name = '601318'

df = pd.DataFrame()
df = get_prices('601857.SS', start, end) 
df['p_change']=df['Close'].pct_change()
s601857 = df['p_change']
s601857.name = '601857'

data = pd.DataFrame({'600519':s600519,'000651':s000651,'000002':s000002, '601318':s601318,'601857':s601857})
data = data.dropna()
#------------------------------------------------------------------------------
#计算年化收益率和协方差矩阵（以一年252个交易日计算）
returns_annual = data.mean() * 252
cov_annual = data.cov() * 252

#------------------------------------------------------------------------------
"""
模拟投资组合
为了得到有效边界，我们模拟了50000个投资组合
"""

number_assets = 5
weights = np.random.random(number_assets)
weights /= np.sum(weights)

portfolio_returns = []
portfolio_volatilities = []
sharpe_ratio = []
for single_portfolio in range (50000):
      weights = np.random.random(number_assets)
      weights /= np.sum(weights) 
      returns = np.dot(weights, returns_annual)
      volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
      portfolio_returns.append(returns)
      portfolio_volatilities.append(volatility)
      sharpe = returns / volatility
      sharpe_ratio.append(sharpe)

portfolio_returns = np.array(portfolio_returns)
portfolio_volatilities = np.array(portfolio_volatilities)

"""
RandomPortfolios['sharpe_ratio']=RandomPortfolios['Returns'] / RandomPortfolios['Volatility']
sharpe_ratio = np.array(RandomPortfolios['sharpe_ratio'])
portfolio_returns = np.array(RandomPortfolios['Returns'])
portfolio_volatilities = np.array(RandomPortfolios['Volatility'])
"""

#------------------------------------------------------------------------------
#作图
plt.style.use('seaborn-dark')
plt.figure(figsize=(9, 5))
plt.scatter(portfolio_volatilities, portfolio_returns, c=sharpe_ratio,cmap='RdYlGn', edgecolors='black',marker='o') 
plt.grid(True)
plt.xlabel('expected volatility')
plt.ylabel('expected return')
plt.colorbar(label='Sharpe ratio')

#------------------------------------------------------------------------------
#找出最优组合
def statistics(weights):        
    weights = np.array(weights)
    pret = np.sum(data.mean() * weights) * 252
    pvol = np.sqrt(np.dot(weights.T, np.dot(data.cov() * 252, weights)))
    return np.array([pret, pvol, pret / pvol])

def min_func_sharpe(weights):
    return -statistics(weights)[2]

bnds = tuple((0, 1) for x in range(number_assets))
cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
opts = sco.minimize(min_func_sharpe, number_assets * [1. / number_assets,], method='SLSQP',  bounds=bnds, constraints=cons)
opts['x'].round(3)  #得到各股票权重
statistics(opts['x']).round(3)  #得到投资组合预期收益率、预期波动率以及夏普比率

#------------------------------------------------------------------------------





















