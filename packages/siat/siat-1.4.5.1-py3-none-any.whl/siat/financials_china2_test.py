# -*- coding: utf-8 -*-


import os; os.chdir("S:/siat")
from siat.financials_china2 import *

tickers=['000002.SZ','600383.SS','600048.SS','600266.SS','600606.SS','000031.SZ']
fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
#注意：fsdates中的财报日期需要延后一期，以便获得期初数。
df=get_fin_stmt_ak_multi(tickers,fsdates)

items1=["货币资金","应收票据","应收账款"]
dfp1=fs_item_analysis_1(df, "000002.SZ",'2021-12-31',items1)

items2=["货币资金","应收账款","存货","长期股权投资","固定资产净额","资产总计"]
dfp2=fs_item_analysis_1(df, "000002.SZ",'2021-12-31',items2)

dfs=find_fs_items(df,itemword1='借款',itemword2='')
dfs=find_fs_items(df,itemword1='预收',itemword2='')
dfs=find_fs_items(df,itemword1='税',itemword2='应')
dfs=find_fs_items(df,itemword1='薪',itemword2='应')
dfs=find_fs_items(df,itemword1='债',itemword2='计')
items3=["短期借款","长期借款","应付账款","预收款项","应交税费","应付职工薪酬","负债合计"]
dfp3=fs_item_analysis_1(df, "000002.SZ",'2021-12-31',items3)


dfs=find_fs_items(df,itemword1='实',itemword2='资')
dfs=find_fs_items(df,itemword1='权益',itemword2='')
dfs=find_fs_items(df,itemword1='税',itemword2='应')
dfs=find_fs_items(df,itemword1='薪',itemword2='应')
dfs=find_fs_items(df,itemword1='债',itemword2='计')
items4=["实收资本(或股本)","资本公积","盈余公积","未分配利润","所有者权益合计"]
dfp4=fs_item_analysis_1(df, "000002.SZ",'2021-12-31',items4)

fsdates1=['2021-12-31','2020-12-31','2019-12-31']
items5=["应收账款","资产总计"]
dfp=fs_item_analysis_2(df,"000002.SZ",fsdates1,items5)

items8=["存货","资产总计"]
dfp=fs_item_analysis_2(df,"000002.SZ",fsdates1,items8)

dfs=find_fs_items(df,itemword1='流动',itemword2='')

dfp=fs_item_analysis_3(df,"000002.SZ",fsdates1)

dfp=fs_item_analysis_4(df,"000002.SZ",fsdates1)

dfp=fs_item_analysis_5(df,"000002.SZ",fsdates1)

dfs=find_fs_items(df,itemword1='应收账款',itemword2='')
fsdates2=['2021-12-31','2020-12-31']
items9=['应收账款','营业收入']
dfp=fs_item_analysis_6(df,"000002.SZ",fsdates2,items9)

items10=['存货','营业收入']
dfp=fs_item_analysis_6(df,"000002.SZ",fsdates2,items10)

items11=['存货','资产总计','存货占比%']
dfp=fs_item_analysis_7(df,tickers,'2021-12-31',items11)

items12=['资产总计','负债合计','资产负债率%','流动资产合计','速动资产合计', \
         '流动负债合计','流动比率%','速动比率%']
dfp=fs_item_analysis_8(df,tickers,'2021-12-31',items12)

if __name__=='__main__':
    asset_liab_structure(tickers,fsdates)

