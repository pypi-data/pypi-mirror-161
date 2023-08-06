# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat import *
#==============================================================================
fdcstocks=['600383.SS','600048.SS','000002.SZ','600266.SS','600606.SS','000031.SZ']
df=compare_dupont_china(fdcstocks,fsdate='2021-12-31',scale1 = 10,scale2 = 10)


#==============================================================================
tickers=['600519.SS','000596.SZ','600559.SS','600702.SS','600809.SS','600059.SS',]
dpi=compare_dupont_china(tickers,fsdate='2021-12-31',scale1 = 10,scale2 = 10)

df=compare_snapshot_china(tickers,'Current Ratio',endDate='latest',axisamp=1.3)
df=compare_snapshot_china(tickers,'ROE',endDate='latest',axisamp=1.3)

df=compare_tax_china(tickers,endDate='latest',axisamp=13.5)

df=compare_igr_sgr_china(tickers,endDate='latest',axisamp1=1.3,axisamp2=1.5)

df=compare_history_china('600519.SS',['ROA','ROE'],'2015-1-1','2020-12-31',period_type='annual')
df=compare_history_china(['600519.SS','600702.SS'],'ROA','2015-1-1','2020-12-31',period_type='annual')


#==============================================================================

import akshare as ak
fdf = ak.stock_financial_report_sina(stock="600004", symbol="现金流量表")
fdf1 = ak.stock_financial_report_sina(stock="872925", symbol="资产负债表")
#==============================================================================

#检查杜邦公式三项匹配问题
find=get_fin_indicator_ak('600606.SS')
list(find)
cols=[
 '主营业务利润率(%)',
 '营业利润率(%)',
 '销售净利率(%)',
 
 '股本报酬率(%)',
 '净资产报酬率(%)',
 '资产报酬率(%)',
 '投资收益率(%)',
 '净资产收益率(%)',
 '加权净资产收益率(%)',
 
 '总资产周转率(次)',
 
 '股东权益比率(%)',
 '负债与所有者权益比率(%)',
 '资本化比率(%)',
 '产权比率(%)',
 '资产负债率(%)',
 '截止日期',
 'ticker',]

test1=find[cols]
test1['EM']=test1['负债与所有者权益比率(%)']/100+1
test1['ROE1']=test1['主营业务利润率(%)']/100 * test1['总资产周转率(次)'] * test1['EM']
test1['ROE2']=test1['营业利润率(%)']/100 * test1['总资产周转率(次)'] * test1['EM']
test1['ROE3']=test1['销售净利率(%)']/100 * test1['总资产周转率(次)'] * test1['EM']

cols2=[
'股本报酬率(%)',
 '净资产报酬率(%)',
 '资产报酬率(%)',
 '投资收益率(%)',
 '净资产收益率(%)',
 '加权净资产收益率(%)',       
 'ROE1','ROE2','ROE3',      
       ]

test2=test1[cols2]
#==============================================================================

if __name__=='__main__':
    tickerlist=['600606.SS','600519.SS','000002.SZ'] 
    df=compare_dupont_china(tickerlist,fsdate='latest',scale1 = 100,scale2 = 50)   

#==============================================================================

if __name__=='__main__':
    ticker="600606.SS" 
    period_type='annual'
    period_type='quarterly'
    period_type='all'
    
stmt=prepare_fin_stmt_ak(ticker,start,end,period_type='all')

df2=prepare_fin_indicator_ak(ticker,start,end,period_type)
df21=prepare_fin_indicator_ak(ticker,start,end,'all',additional=False)
df22=prepare_fin_indicator_ak(ticker,start,end,'semiannual',additional=False)
df23=prepare_fin_indicator_ak(ticker,start,end,'annual',additional=False)
df24=prepare_fin_indicator_ak(ticker,start,end,'all',additional=False)
#==============================================================================
#A股期末财务指标，历史***
import akshare as ak
df1 = ak.stock_financial_abstract(stock="600004")
list(df1)
"""
['截止日期',
 '每股净资产-摊薄/期末股数',
 '每股现金流',
 '每股资本公积金',
 '固定资产合计',
 '流动资产合计',
 '资产总计',
 '长期负债合计',
 '主营业务收入',
 '财务费用',
 '净利润']
"""

#A股财务指标：历史***
df2 = ak.stock_financial_analysis_indicator(stock="600004")
list(df2)
"""
['摊薄每股收益(元)',
 '加权每股收益(元)',
 '每股收益_调整后(元)',
 '扣除非经常性损益后的每股收益(元)',
 '每股净资产_调整前(元)',
 '每股净资产_调整后(元)',
 '每股经营性现金流(元)',
 '每股资本公积金(元)',
 '每股未分配利润(元)',
 '调整后的每股净资产(元)',
 '总资产利润率(%)',
 '主营业务利润率(%)',
 '总资产净利润率(%)',
 '成本费用利润率(%)',
 '营业利润率(%)',
 '主营业务成本率(%)',
 '销售净利率(%)',
 '股本报酬率(%)',
 '净资产报酬率(%)',
 '资产报酬率(%)',
 '销售毛利率(%)',
 '三项费用比重',
 '非主营比重',
 '主营利润比重',
 '股息发放率(%)',
 '投资收益率(%)',
 '主营业务利润(元)',
 '净资产收益率(%)',
 '加权净资产收益率(%)',
 '扣除非经常性损益后的净利润(元)',
 '主营业务收入增长率(%)',
 '净利润增长率(%)',
 '净资产增长率(%)',
 '总资产增长率(%)',
 '应收账款周转率(次)',
 '应收账款周转天数(天)',
 '存货周转天数(天)',
 '存货周转率(次)',
 '固定资产周转率(次)',
 '总资产周转率(次)',
 '总资产周转天数(天)',
 '流动资产周转率(次)',
 '流动资产周转天数(天)',
 '股东权益周转率(次)',
 '流动比率',
 '速动比率',
 '现金比率(%)',
 '利息支付倍数',
 '长期债务与营运资金比率(%)',
 '股东权益比率(%)',
 '长期负债比率(%)',
 '股东权益与固定资产比率(%)',
 '负债与所有者权益比率(%)',
 '长期资产与长期资金比率(%)',
 '资本化比率(%)',
 '固定资产净值率(%)',
 '资本固定化比率(%)',
 '产权比率(%)',
 '清算价值比率(%)',
 '固定资产比重(%)',
 '资产负债率(%)',
 '总资产(元)',
 '经营现金净流量对销售收入比率(%)',
 '资产的经营现金流量回报率(%)',
 '经营现金净流量与净利润的比率(%)',
 '经营现金净流量对负债比率(%)',
 '现金流量比率(%)',
 '短期股票投资(元)',
 '短期债券投资(元)',
 '短期其它经营性投资(元)',
 '长期股票投资(元)',
 '长期债券投资(元)',
 '长期其它经营性投资(元)',
 '1年以内应收帐款(元)',
 '1-2年以内应收帐款(元)',
 '2-3年以内应收帐款(元)',
 '3年以内应收帐款(元)',
 '1年以内预付货款(元)',
 '1-2年以内预付货款(元)',
 '2-3年以内预付货款(元)',
 '3年以内预付货款(元)',
 '1年以内其它应收款(元)',
 '1-2年以内其它应收款(元)',
 '2-3年以内其它应收款(元)',
 '3年以内其它应收款(元)']
"""

#A股业绩报表：全体，指定年报/季报，所在行业
df5 = ak.stock_em_yjbb(date="20210930")
list(df5)
"""
['序号',
 '股票代码',
 '股票简称',
 '每股收益',
 '营业收入-营业收入',
 '营业收入-同比增长',
 '营业收入-季度环比增长',
 '净利润-净利润',
 '净利润-同比增长',
 '净利润-季度环比增长',
 '每股净资产',
 '净资产收益率',
 '每股经营现金流量',
 '销售毛利率',
 '所处行业',
 '最新公告日期']
"""

#A股股东户数：全体，当前
df3 = ak.stock_zh_a_gdhs()
list(df3)
"""
['代码',
 '名称',
 '最新价',
 '涨跌幅',
 '股东户数-本次',
 '股东户数-上次',
 '股东户数-增减',
 '股东户数-增减比例',
 '区间涨跌幅',
 '股东户数统计截止日-本次',
 '股东户数统计截止日-上次',
 '户均持股市值',
 '户均持股数量',
 '总市值',
 '总股本',
 '公告日期']
"""

#A股股东户数：个股，历史，详情
df4 = ak.stock_zh_a_gdhs_detail_em(symbol="000002")
list(df4)
"""
['股东户数统计截止日',
 '区间涨跌幅',
 '股东户数-本次',
 '股东户数-上次',
 '股东户数-增减',
 '股东户数-增减比例',
 '户均持股市值',
 '户均持股数量',
 '总市值',
 '总股本',
 '股本变动',
 '股本变动原因',
 '股东户数公告日期',
 '代码',
 '名称']
"""





#==============================================================================

tickers=['600519.SS','000858.SZ','600779.SS','000596.SZ','603589.SS']
df=compare_dupont_china(tickers,fsdate='2020-12-31',scale1 = 10,scale2 = 10)

tickers=['600398.SS','002291.SZ','002563.SZ','002193.SZ','002029.SZ','02331.HK','02020.HK','01368.HK','01361.HK','02313.HK']
tickers=['600398.SS','002291.SZ','002563.SZ','002193.SZ','002029.SZ','02331.HK','02020.HK','01368.HK','01361.HK','02313.HK']

df=compare_dupont_china (tickers,fsdate='2020-12-31',scale1 = 10,scale2 = 10)


#==============================================================================
info=get_stock_profile("MUFG","fin_rates")

wuliu=["002352.SZ","002468.SZ","2057.HK","600233.SS","002120.SZ","603056.SS","601598.SS","603967.SS","603128.SS"]
peg=compare_snapshot(wuliu,"PEG")

tickers=["601398.SS","601988.SS","601988.SS",'601288.SS','601328.SS','601658.SS','600036.SS','000001.SZ']
isgr=compare_igr_sgr(tickers,axisamp=3)
#==============================================================================
tickers=["BABA","JD","VIPS",'PDD','AMZN','WMT','EBAY','SHOP','MELI']
isgr=compare_igr_sgr(tickers)

#==============================================================================
tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
pm=compare_snapshot(tickers,'Profit Margin')
roa=compare_snapshot(tickers,'ROA')
roe=compare_snapshot(tickers,'ROE')
pe=compare_snapshot(tickers,'Trailing PE',axisamp=1.8)
#==============================================================================
tickers=["601808.SS","600583.SS","600968.SS",'600871.SS','600339.SS','601857.SS','600028.SS','0883.HK']
isgr=compare_igr_sgr(tickers)

ticker='0883.HK'
igr,sgr=calc_igr_sgr(ticker)
#==============================================================================
tat=compare_history(['AMZN','JD'],'Total Asset Turnover')
fat=compare_history(['AMZN','JD'],'Fixed Asset Turnover')
cfps_eps=compare_history(['BABA'],['Cashflow per Share','BasicEPS'])

cr=compare_history(['BABA','JD'],'Cashflow per Share')
cr=compare_history(['BABA','PDD'],'Cashflow per Share')
cr=compare_history(['BABA','VIPS'],'Cashflow per Share')

tickers=['600519.SS','000858.SZ','600779.SS','000596.SZ','603589.SS']
df=compare_dupont(tickers,fsdate='2020-12-31',scale1 = 10,scale2 = 10)


#==============================================================================
cr=compare_history(['AAPL','MSFT'],'Current Ratio')
cr=compare_history(['601808.SS','600871.SS'],'Current Ratio')
cr=compare_history(['601808.SS','0883.HK'],'Current Ratio')

cr=compare_history(['601808.SS'],['Current Ratio','Quick Ratio'])


#==============================================================================
cosl=compare_history('601808.SS',['Current Ratio','Quick Ratio'])
cosl=compare_history('601808.SS',['Debt to Asset','Debt to Equity'])
cosl=compare_history('601808.SS',['Debt to Asset','Debt to Equity'],twinx=True)
tie=compare_history(['601808.SS'],'Times Interest Earned')
itr=compare_history(['601808.SS','600871.SS'],'Inventory Turnover')
rtr=compare_history(['601808.SS','600871.SS'],'Receivable Turnover')

rtr=compare_history(['601808.SS','600871.SS'],'Total Asset Turnover')
fat=compare_history(['601808.SS','600871.SS'],'Fixed Asset Turnover')
cr=compare_history(['601808.SS','600871.SS'],'Current Ratio')
qr=compare_history(['601808.SS','600871.SS'],'Quick Ratio')
d2a=compare_history(['601808.SS','600871.SS'],'Debt to Asset')

cfps=compare_history(['601808.SS','600871.SS'],'Cashflow per Share')

dtoe=compare_snapshot(tickers,'Dbt to Asset')

tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
dbi=compare_dupont(tickers,fsdate='latest',scale1 = 100,scale2 = 50)

tickers=['601808.SS',"600339.SS",'600583.SS','SLB','HAL']
dbi=compare_dupont(tickers,fsdate='latest',scale1 = 100,scale2 = 50)

igr=compare_snapshot(tickers,'IGR')
#==============================================================================
tickers=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','OXY','BP','RDSA.AS']
atr=compare_tax(tickers,graph=True)
dbi=compare_dupont(tickers,fsdate='latest',scale1 = 100,scale2 = 10)
ev2r=compare_snapshot(tickers,'EV to Revenue')
ev2ebitda=compare_snapshot(tickers,'EV to EBITDA')
price=compare_snapshot(tickers,'Current Price')

tickers2=["0883.HK","0857.HK","0386.HK",'XOM','2222.SR','BP','RDSA.AS']
fpe=compare_snapshot(tickers2,'Forward PE')
pb=compare_snapshot(tickers,'Price to Book')
roa=compare_snapshot(tickers,'ROA')
roe=compare_snapshot(tickers,'ROE')

pm=compare_snapshot(tickers,'ROE')

tickerlist=['IBM','DELL','WMT'] 
df=compare_dupont(tickerlist,fsdate='latest',scale1 = 100,scale2 = 10)    

tickerlist=['DELL','WMT'] 
df=compare_dupont(tickerlist,fsdate='latest',scale1 = 100,scale2 = 10) 
#==============================================================================
tickers_cn=['600398.SS','300005.SZ','002563.SZ','002193.SZ','002269.SZ']
tickers_hk=['2331.HK','2020.HK','1368.HK','3998.HK','2313.HK']
tickers=tickers_cn+tickers_hk
gmdf=compare_dupont(tickers,fsdate='2020-12-31',scale1 = 10,scale2 = 10) 

#==============================================================================
tickers=['AMZN','EBAY','SHOP','MELI','BABA','JD','VIPS','PDD']
dtoe=compare_snapshot(tickers,'Debt to Asset')
#==============================================================================

leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
tpe=compare_snapshot(leadings,'Trailing PE')

mainleadings=['JNJ','PFE','MRK','VRTX','NVS','SNY']
tests=['NBIX','REGN','PRGO']
tpe=compare_snapshot(tests + mainleadings,'Trailing PE')

#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
fpe=compare_snapshot(leadings,'Forward PE')

mainleadings=['JNJ','PFE','VRTX','NVS','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
fpe=compare_snapshot(tests + mainleadings,'Forward PE')
#==============================================================================
cp=compare_snapshot(tests+leadings,'Current Price')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
ptob=compare_snapshot(leadings,'Price to Book')

mainleadings=['JNJ','PFE','MRK','VRTX','NVS','AMGN']
tests=['NBIX','REGN','PRGO']
ptob=compare_snapshot(tests+mainleadings,'Price to Book')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
evtoebitda=compare_snapshot(leadings,'EV to EBITDA')

mainleadings=['JNJ','PFE','VRTX','NVS','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
evtoebitda=compare_snapshot(tests + mainleadings,'EV to EBITDA')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
evtoebitda=compare_snapshot(leadings,'PEG')
#==============================================================================
mainleadings=['MRK','LLY','VRTX','NVS','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
peg=compare_snapshot(tests + mainleadings,'PEG')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
ptos=compare_snapshot(leadings,'TTM Price to Sales')
#==============================================================================
mainleadings=['JNJ','PFE','MRK','LLY','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
ptos=compare_snapshot(tests + mainleadings,'TTM Price to Sales')
#==============================================================================
leadings=['JNJ','PFE','MRK','LLY','VRTX','NVS','AMGN','SNY']
evtorev=compare_snapshot(leadings,'EV to Revenue')
#==============================================================================
mainleadings=['JNJ','PFE','MRK','VRTX','AMGN','SNY']
tests=['NBIX','REGN','PRGO']
evtorev=compare_snapshot(tests + mainleadings,'EV to Revenue')




#==============================================================================
cfps_eps=compare_history('BABA',['Cashflow per Share','BasicEPS'])
cfps_eps=compare_history('JD',['Cashflow per Share','BasicEPS'])
cfps_eps=compare_history('PDD',['Cashflow per Share','BasicEPS'])
cfps_eps=compare_history('VIPS',['Cashflow per Share','BasicEPS'])

cfps_eps=compare_history('WMT',['Cashflow per Share','BasicEPS'])

cfps_eps=compare_history('QCOM',['Cashflow per Share','BasicEPS'])

cr=compare_history(['BABA','JD'],'Cashflow per Share')
cr=compare_history(['BABA','PDD'],'Cashflow per Share')
cr=compare_history(['BABA','VIPS'],'Cashflow per Share')

tickers=['AMZN','EBAY','SHOP','MELI']
cfps=compare_snapshot(tickers,'Cashflow per Share')
cr=compare_history(['AMZN'],['Cashflow per Share','BasicEPS'])
cr=compare_history(['EBAY'],['Cashflow per Share','BasicEPS'])


