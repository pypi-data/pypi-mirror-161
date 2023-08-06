# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 22:49:18 2020

@author: Peter
"""

import os; os.chdir("S:/siat")
from siat.financial_statements import *


bs=get_balance_sheet('0883.HK')
infot=info.T

info=get_balance_sheet('PDD')
infot=info.T
cr=compare_history(['BABA','PDD'],'Quick Ratio')

#==============================================================================
info=get_income_statements('MST')
info=get_income_statements('MDT')

info=get_cashflow_statements('MDT')
info=get_cashflow_statements('MST')

info=get_balance_sheet('MST')
info=get_balance_sheet('MDT')
info=get_balance_sheet('MSFT')

info=get_financial_statements('MDT')
info=get_financial_statements('MST')
