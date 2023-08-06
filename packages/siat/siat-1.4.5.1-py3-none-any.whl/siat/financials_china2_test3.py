# -*- coding: utf-8 -*-


import os; os.chdir("S:/siat")
from siat.financials_china2 import *

tickers=['000002.SZ','600383.SS','600048.SS','600266.SS','600606.SS','000031.SZ']
fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
#注意：fsdates中的财报日期需要延后一期，以便获得期初数。
df=get_fin_stmt_ak_multi(tickers,fsdates)

#====================================================================
dfs=find_fs_items(df,itemword1='资本',itemword2='')

ticker="000002.SZ"
fsdate='2021-12-31'
items1=["经营活动现金流净额","经营活动现金流入","经营活动现金流出",
        "投资活动现金流净额","投资活动现金流入","投资活动现金流出",
        "筹资活动现金流净额","筹资活动现金流入","筹资活动现金流出",
        "汇率对现金流的影响","现金流量净增加额"]
dfp1=fs_item_analysis_1(df,ticker,fsdate,items1)

#占比变动分析：近三年
fsdates1=fsdates[:3]
items3=["经营活动现金流入","营业总收入"]
dfp3=fs_item_analysis_2(df,"000002.SZ",fsdates1,items3)

items4=["经营活动现金流净额","营业利润"]
dfp3=fs_item_analysis_2(df,"000002.SZ",fsdates1,items4)

#增幅分析：近两年 
fsdates2=fsdates[:2]
items12=['经营活动现金流入','经营活动现金流出','经营活动现金流净额']
dfp12=fs_item_analysis_6(df,ticker,fsdates2,items12)

#同行比较
items14=['短期现金偿债能力%','长期现金偿债能力%']
dfp12=fs_item_analysis_8(df,tickers,fsdate,items14)

items15=['现金支付股利能力(元)','现金综合支付能力%','支付给职工的现金比率%']
dfp12=fs_item_analysis_8(df,tickers,fsdate,items15)

items16=['销售现金比率%','现金购销比率%','营业现金回笼率%']
dfp12=fs_item_analysis_8(df,tickers,fsdate,items16)

items17=['盈利现金比率%','现金流入流出比率%','资产现金回收率%']
dfp12=fs_item_analysis_8(df,tickers,fsdate,items17)
#====================================================================










items8=["存货","营业总收入"]
dfp=asset_liab_analysis_2(df,"000002.SZ",fsdates1,items8)

dfs=find_fs_items(df,itemword1='流动',itemword2='')

dfp=asset_liab_analysis_3(df,"000002.SZ",fsdates1)

dfp=asset_liab_analysis_4(df,"000002.SZ",fsdates1)

dfp=asset_liab_analysis_5(df,"000002.SZ",fsdates1)

dfs=find_fs_items(df,itemword1='应收账款',itemword2='')
fsdates2=['2021-12-31','2020-12-31']
items9=['应收账款','营业收入']
dfp=asset_liab_analysis_6(df,"000002.SZ",fsdates2,items9)

items10=['存货','营业收入']
dfp=asset_liab_analysis_6(df,"000002.SZ",fsdates2,items10)

items11=['存货','资产总计','存货占比%']
dfp=asset_liab_analysis_7(df,tickers,'2021-12-31',items11)

items12=['资产总计','负债合计','资产负债率%','流动资产合计','速动资产合计', \
         '流动负债合计','流动比率%','速动比率%']
dfp=asset_liab_analysis_8(df,tickers,'2021-12-31',items12)

if __name__=='__main__':
    asset_liab_structure(tickers,fsdates)

