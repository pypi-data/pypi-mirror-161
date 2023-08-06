# -*- coding: utf-8 -*-
# 绝对引用指定目录中的模块
import sys
sys.path.insert(0,r'S:\siat\siat')

from future_china import *

clist=[0.021,0.024,0.027,0.03,0.04,0.05,0.06]
df=cf_day_coupon_trend(clist,30,10,2,0.03)

#=====内盘期货=====
#列示全部品种与代码
df=future_type_china()

#列示某个期货品种的基本信息
df=future_type_china("SC")

#列示某个品种在某个时间段的所有合约
df=future_price_china("SC","2021-8-1","2022-1-31")

#列示某个合约在某个时间段的交易状况
df=future_price_china("SC2406","2021-8-1","2021-8-31")

#=====外盘期货(品种与合约合一)=====
#列示全部品种与代码
df=future_type_foreign()

#列示某个期货品种的基本信息
df=future_type_foreign("AHD")

#列示某个合约在某个时间段的交易状况
df=future_price_foreign("AHD","2021-8-1","2021-8-31")

#==========================================================================================
import akshare as ak
futures_rule_df = ak.futures_rule(date="20200713")
#==========================================================================================
