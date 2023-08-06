# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat import *
#==============================================================================
beta=capm_beta('600519.SS','000001.SS','2011-1-1','2021-12-31')



#==============================================================================
beta=capm_beta('AAPL','^GSPC','2016-1-1','2020-12-31')

yearlist=gen_yearlist('2016','2020')
betas=capm_beta_yearly('AAPL','^GSPC',yearlist)
betas=capm_beta_yearly('600000.SS','000001.SS',yearlist)

#==============================================================================
portfolio=['IBM','AAPL','MSFT']
holdings=[1, 1, 3]
yearlist=gen_yearlist('2010','2020')
df=capm_beta_portfolio_yearly(portfolio,holdings,'^GSPC',yearlist)

#==============================================================================
beta=capm_beta('600000.SS','000001.SS','2011-1-1','2020-12-31')

portfolio=['IBM','AAPL','MSFT']
holdings=[1, 1, 3]
yearlist=gen_yearlist('2010','2020')
df=capm_beta_portfolio_yearly(portfolio,holdings,'^GSPC',yearlist)

from siat.beta_adjustment import *
yearlist=gen_yearlist('2011','2020')
betas=betas_dji=get_beta_ML('EDU','^DJI',yearlist)

#==============================================================================
beta=capm_beta('AAPL','^GSPC','2011-1-1','2020-12-31')

yearlist=gen_yearlist('2011','2020')
betas=capm_beta_yearly('AAPL','^GSPC',yearlist)

yearlist=gen_yearlist('2010', '2020')
betas=capm_beta_yearly('600000.SS', '000001.SS', yearlist)

yearlist=gen_yearlist('2010','2021')
betas=compare2_betas_yearly('600000.SS','600030.SS','000001.SS',yearlist)
betas

yearlist=gen_yearlist('2010','2020')
betas=compare2_betas_yearly('AMZN','BAC','^GSPC',yearlist)
