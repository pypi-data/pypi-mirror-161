# -*- coding: utf-8 -*-

# 绝对引用指定目录中的模块

import os; os.chdir("S:/siat")
from siat import *
#==============================================================================
df=etf_trend_china('510580','2022-1-1','2022-4-30',loc1='center left')


df=oef_trend_china('000592','2021-1-1','2021-3-31',trend_type='收益率',power=5)
df = mmf_rank_china()

df=mmf_trend_china('320019','2020-7-1','2020-9-30', power=1)
df=mmf_trend_china('001234','2021-1-1','2022-1-31', power=1)
df2=mmf_trend_china('004972','2021-1-1','2022-1-31', power=1)
df3=mmf_trend_china('004137','2021-1-1','2022-1-31', power=1)
df4=mmf_trend_china('002890','2021-1-1','2022-1-31', power=1)
df5=mmf_trend_china('004417','2021-1-1','2022-1-31', power=1)
df6=mmf_trend_china('005151','2021-1-1','2022-1-31', power=1)
df7=mmf_trend_china('001909','2021-1-1','2022-1-31', power=1)
df8=mmf_trend_china('001821','2021-1-1','2022-1-31', power=1)
df9=mmf_trend_china('000836','2021-1-1','2022-1-31', power=1)
df10=mmf_trend_china('000700','2021-1-1','2022-1-31', power=1)
#==============================================================================
df10 = ak.fund_em_exchange_rank()
df10s=df10[['基金代码','基金简称','单位净值','近1年']]
df10s2=df10s[df10s['近1年']!='']

df10s2['近1年']=df10s2['近1年'].astype('float')
df10s.sort_values(by=['近1年'],ascending=False, inplace=True)
df10s.reset_index(drop=True,inplace=True)
df10s.head(10)

#==============================================================================
df90_lof=ak.fund_etf_category_sina(symbol="LOF基金") #可选参数为: 封闭式基金, ETF基金, LOF基金
df90_lof_s=df90_etf_s[df90_etf_s["LOF"]==True]

df90_cef=ak.fund_etf_category_sina(symbol="封闭式基金")

df90_etf=ak.fund_etf_category_sina(symbol="ETF基金")
df90_etf_s=df90_etf[['代码','名称']]
df90_etf_s["沪深300"]= df90_etf_s["名称"].str.contains('沪深300')
df90_etf_s1=df90_etf_s[df90_etf_s["沪深300"]==True]

df90_etf_s["上证50"]= df90_etf_s["名称"].str.contains('上证50')
df90_etf_s2=df90_etf_s[df90_etf_s["上证50"]==True]

df90_etf_s["中证500"]= df90_etf_s["名称"].str.contains('中证500')
df90_etf_s3=df90_etf_s[df90_etf_s["中证500"]==True]

df90_etf_s["上证综指"]= df90_etf_s["名称"].str.contains('上证综指')
df90_etf_s5=df90_etf_s[df90_etf_s["上证综指"]==True]

df90_etf_s["标普500"]= df90_etf_s["名称"].str.contains('标普500')
df90_etf_s6=df90_etf_s[df90_etf_s["标普500"]==True]

df90_etf_s["纳斯达克"]= df90_etf_s["名称"].str.contains('纳')
df90_etf_s7=df90_etf_s[df90_etf_s["纳斯达克"]==True]

df90_etf_s["恒生"]= df90_etf_s["名称"].str.contains('恒生')
df90_etf_s8=df90_etf_s[df90_etf_s["恒生"]==True]

df90_etf_s["日经"]= df90_etf_s["名称"].str.contains('日经')
df90_etf_s9=df90_etf_s[df90_etf_s["日经"]==True]

df90_etf_s["深证成指"]= df90_etf_s["名称"].str.contains('深证成指')
df90_etf_s10=df90_etf_s[df90_etf_s["深证成指"]==True]

df90_etf_s["CAC"]= df90_etf_s["名称"].str.contains('CAC')
df90_etf_s11=df90_etf_s[df90_etf_s["CAC"]==True]

df90_etf_s["富时"]= df90_etf_s["名称"].str.contains('富时')
df90_etf_s12=df90_etf_s[df90_etf_s["富时"]==True]

df90_etf_s["债指"]= df90_etf_s["名称"].str.contains('债')
df90_etf_s13=df90_etf_s[df90_etf_s["债指"]==True]



df90 = ak.fund_etf_hist_sina(symbol="sz169103")

#==============================================================================
df=security_price("169103.SZ",'2021-7-1','2021-10-15')
df=security_price("180801.SZ",'2021-7-1','2021-10-15')

df1=fund_stock_holding_compare_china('005827.SS','2021Q1','2021Q2')
df2=fund_stock_holding_rank_china('005827')


df=reits_profile_china()
df=reits_profile_china(top = 3)
df=reits_profile_china(top = -3)
df=reits_profile_china('508056')
#==============================================================================
from siat.translate import *

#==============================================================================
from siat import *
df=oef_rank_china('单位净值','全部类型')
set(list(df['基金类型'])) #基金类别列表
set(list(df['基金代码'])) #基金个数
df=oef_trend_china('180801','2020-1-1','2021-9-30',"收益率")

import akshare as ak
df = ak.fund_em_open_fund_info(fund="710001", indicator="累计收益率走势")
df=oef_trend_china('710001','2020-1-1','2021-9-30',"收益率")
#==============================================================================
df=oef_trend_china('000592','2021-1-1','2021-3-31',trend_type='收益率',power=5)

df=mmf_trend_china('320019','2020-7-1','2020-9-30',power=1)

df=oef_trend_china('000595','2019-1-1','2020-12-31',trend_type='净值')
df=oef_trend_china('000592','2021-1-1','2021-3-31',trend_type='收益率',power=5)
df=oef_trend_china('050111','2020-9-1','2020-9-30',trend_type='排名')
df=mmf_trend_china('320019','2020-7-1','2020-9-30',power=3)
df=etf_trend_china('510580','2019-1-1','2020-9-30')

#==============================================================================

df=oef_rank_china('单位净值','全部类型')


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

amac_member_list=list(set(list(amac_member_info_df['机构类型'])))

df=etf_rank_china(info_type='单位净值',fund_type='全部类型')
df=etf_rank_china(info_type='累计净值')
df=etf_trend_china('510580','2019-1-1','2020-9-30')


from siat.fund_china import *
df=fund_summary_china()

df=pef_manager_china()
df=pef_manager_china("广东省")
df=pef_manager_china("上海市")
df=pef_manager_china("北京市")
df=pef_product_china()






