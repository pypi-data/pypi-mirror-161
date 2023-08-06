# -*- coding: utf-8 -*-

import os; os.chdir('S:/siat')

from siat import *

portfolio={'Market':("China","000001.SS"),'300782.SZ':1}
portfolio_rets_curve(portfolio,'2022-1-1','2022-4-18')
e,r=get_ES_portfolio(portfolio,'2022-4-18',5,0.99,model='historical')

portfolio2={'Market':("China","000001.SS"),'300782.SZ':0.3,'300563.SZ':0.7}
portfolio_rets_curve(portfolio2,'2022-1-1','2022-4-18')
e,r=get_ES_portfolio(portfolio2,'2022-4-18',5,0.99,model='historical')