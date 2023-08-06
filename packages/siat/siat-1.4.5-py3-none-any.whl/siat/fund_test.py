# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 20:02:52 2020

@author: Peter
"""

import os; os.chdir("S:/siat")
from siat.fund import *

df=pof_list_china()


df=oef_rank_china('单位净值','全部类型')
df=oef_rank_china('累计净值','全部类型')
df=oef_rank_china('手续费','全部类型')


df=oef_rank_china('单位净值','股票型')
df=oef_rank_china('累计净值','股票型')


df=oef_rank_china('单位净值','债券型')
df=oef_rank_china('累计净值','债券型')

df=oef_trend_china('519035','2019-1-1','2020-10-16',trend_type='净值')

df=oef_trend_china('519035','2020-5-1','2020-10-16',trend_type='收益率',power=5)

df=oef_trend_china('519035','2020-9-1','2020-9-30',trend_type='排名')


df=oef_trend_china('000595','2019-1-1','2020-10-16',trend_type='净值')
df=oef_trend_china('000592','2020-7-1','2020-9-30',trend_type='收益率',power=5)
df=oef_trend_china('050111','2020-9-1','2020-9-30',trend_type='排名')

df = ak.fund_em_money_fund_daily()
df = mmf_rank_china()

df=mmf_trend_china('320019','2020-7-1','2020-9-30',power=1)
