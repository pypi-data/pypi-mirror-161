# -*- coding: utf-8 -*-

#==============================================================================
#测试方法：先卸载siat：pip uninstall siat
import os; os.chdir('S:/siat')
from siat import *
#==============================================================================
import akshare as ak
ak.option_sina_commodity_dict(symbol=" Gold options ")






#==============================================================================
#中金所，沪深300指数期权日频行情
import akshare as ak
"""
目标地址: https://stock.finance.sina.com.cn/view/optionsCffexDP.php
描述: 获取中金所-沪深300指数-指定合约-日频行情
"""
#期权列表
df1 = ak.option_sina_cffex_hs300_list()
"""
{'沪深300指数': ['io2112', 'io2201', 'io2203', 'io2206', 'io2209', 'io2202']}
"""

#最新行情价格：可获得合约标识，例如io2206C5800
#df2 = ak.option_sina_cffex_hs300_spot(contract="io2206")
df2 = ak.option_sina_cffex_hs300_spot()

[ '看涨合约_最新价',
['看涨合约_最新价','行权价','看涨合约_标识','看跌合约_最新价','看跌合约_标识']
 '看跌合约_卖价',
 '看跌合约_卖量',
 '看跌合约_持仓量',
 '看跌合约_涨跌',
 '看跌合约_标识']
"""
"""
df2s=df2[['看涨合约_最新价','行权价','看涨合约_标识','看跌合约_最新价','看跌合约_标识']]

#日频行情：注意到期月份，过了到期月份就没有数据了
df3 = ak.option_sina_cffex_hs300_daily()
df3s=df3[['date','close']]

#标的物价格：沪深300指数
df4=get_prices("000300.SS","2021-11-1","2021-11-25")

#==============================================================================
#上交所，金融期货日频行情
#合约到期月份列表
df11 = ak.option_sina_sse_list(symbol="50ETF", exchange="null")
"""
['202112', '202201', '202203', '202206']
"""

#合约到期日：注意过了到期月份就没有数据了
df12_50etf = ak.option_sina_sse_expire_day(trade_date="202206", symbol="50ETF", exchange="null")
"""
#返回：到期日，剩余到期天数
('2022-06-22', 208)
"""
df12_300etf = ak.option_sina_sse_expire_day(trade_date="202206", symbol="300ETF", exchange="null")

#所有合约的代码
df13 = ak.option_sina_sse_codes(trade_date="202206", underlying="510300")
#所有看涨合约代码
df13[0]
"""
['10003705','10003687','10003688','10003689','10003690','10003691','10003692','10003693','10003694','10003695']
"""
#所有看跌合约代码
df13[1]
['10003706','10003696','10003697','10003698','10003699','10003700','10003701','10003702','10003703','10003704']

#合约实时价格：注意过了到期月份就没有数据了
code1="10003689"
df14 = ak.option_sina_sse_spot_price(code=code1)
rowlist14=['最新价','行权价','昨收价','主力合约标识','标的股票','期权合约简称']
df14s=df14[df14['字段'].apply(lambda x: x in rowlist14)]

#标的物的实时价格
df15 = ak.option_sina_sse_underlying_spot_price(code="sh510300")
rowlist15=['证券简称','昨日收盘价','最近成交价','行情日期']
df15s=df15[df15['字段'].apply(lambda x: x in rowlist15)]

df15b = ak.option_sina_sse_underlying_spot_price(code="sh510050")
df15bs=df15b[df15b['字段'].apply(lambda x: x in rowlist15)]

#希腊字母：仅支持上交所50ETF、300ETF期权
df16 = ak.option_sina_sse_greeks(code=code1)
rowlist16=['期权合约简称','Delta','Gamma','Theta','Vega','隐含波动率','交易代码','行权价','最新价','理论价值']
df16s=df16[df16['字段'].apply(lambda x: x in rowlist16)]

#期权行情日数据
df17 = ak.option_sina_sse_daily(code=code1)
df17s=df17[['日期','收盘']]

#==============================================================================
#商品期权：新浪，历史行情
#查看合约代码和到期月份
df20=ak.option_sina_commodity_dict(symbol="黄金期权") 
"""
{'黄金期权': ['au2202', 'au2204', 'au2206', 'au2201']}
"""

#查看合约代码
df21=ak.option_sina_commodity_contract_list(symbol="黄金期权", contract="au2201")
list(df21)
"""
['买量',
 '买价',
 '最新价',
 '卖价',
 '卖量',
 '持仓量',
 '涨跌',
 '行权价',
 '看涨期权合约',
 '买量',
 '买价',
 '最新价',
 '卖价',
 '卖量',
 '持仓量',
 '涨跌',
 '看跌期权合约']
"""
df21s=df21.drop(['买量','买价','卖价','卖量','持仓量','涨跌'], axis=1)
list(df21s)
collist=['看涨期权最新价', '行权价', '看涨期权合约', '看跌期权最新价', '看跌期权合约']
df21s.columns=collist

#合约历史行情：有的数据很少！
"""
新浪财经，商品期权
https://stock.finance.sina.com.cn/futures/view/optionsDP.php/au_o/shfe
豆粕期权：m
玉米期权：c
铁矿石期权：i
棉花期权：cf
白糖期权：sr
PTA期权：ta
甲醇期权：ma
橡胶期权：ru
沪铜期权：cu
黄金期权：au
菜籽粕期权：rm
液化石油气期权：pg
动力煤期权：zc
"""
df22 = ak.option_sina_commodity_hist(contract="au2202C392")
df22s=df22[['date','close']]

#==============================================================================
#商品期权：上海期货交易所
"""
交易所	        对应名称	上市时间
上海期货交易所	铜期权	2018-09-21
上海期货交易所	天胶期权	2019-01-28
上海期货交易所	黄金期权	2019-12-20
上海期货交易所	铝期权	2020-08-10
上海期货交易所	锌期权	2020-08-10
"""

"""
交易所	        对应名称	上市时间
大连商品交易所	豆粕期权	2017-03-31
大连商品交易所	玉米期权	2019-01-28
大连商品交易所	铁矿石期权	2019-12-09
大连商品交易所	液化石油气期权	2020-03-30
大连商品交易所	聚乙烯期权	2020-07-06
大连商品交易所	聚氯乙烯期权	2020-07-06
大连商品交易所	聚丙烯期权	2020-07-06
"""


"""
交易所	        对应名称	上市时间
郑州商品交易所	白糖期权	2017-04-19
郑州商品交易所	棉花期权	2019-01-28
郑州商品交易所	PTA期权	2019-12-16
郑州商品交易所	甲醇期权	2019-12-16
郑州商品交易所	菜籽粕期权	2020-01-16
郑州商品交易所	动力煤期权	2020-06-30

郑州商品交易所	白糖期权	2017-04-19	SR
郑州商品交易所	棉花期权	2019-01-28	CF
郑州商品交易所	PTA期权	2019-12-16	TA
郑州商品交易所	甲醇期权	2019-12-16	MA
郑州商品交易所	菜籽粕期权	2020-01-16	RM
"""
df50 = ak.option_czce_hist(symbol="RM", year="2021")
df50s=df50[['交易日期  ','合约代码   ','昨结算    ','今收盘    ','今结算    ','DELTA     ','隐含波动率']]

df50s[df50s['合约代码   ']=='RM209P2450']

#==============================================================================


#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================



#==============================================================================
#第一步：查询金融期权期权
#查看中国当前的金融期权品种
option_fin_china()

#如果希望查看更多内容：
option_fin_china(detail=True)

#查看某个金融期权品种的到期月份：以华夏上证50ETF期权为例
option="华夏上证50ETF期权"
option_fin_month_china(option)

#查看某个金融期权在某个到期月份的具体合约：以华夏上证50ETF期权2022年6月到期的看涨合约为例
end_month='2206'
direction='call'
#脚本默认是看涨期权合约
contracts=option_fin_contracts(option,end_month,direction)

#如果希望查看看跌期权合约
contracts=option_fin_contracts(option,end_month,'put')

#如果希望查看看涨和看跌期权的全部合约：发现看涨和看跌合约都是配对出现的
contracts=option_fin_contracts(option,end_month,'both')

#第二步：查找计算金融期权预期价格所需要的参数
#以2022年6月份到期的华夏上证50ETF期权合约510050C2206M02900为例
contract='510050C2206M02900'
ua,maturity,x=option_fin_contract_parms(option,end_month,contract,direction)
print("underlying asset is",ua)
print("maturity date is",maturity)
print("strike price is",x)
#其到期日是2022-6-28

#计算期权标的证券（510050.SS）价格的历史波动率：
#假定今日是2021-11-19，使用历史样本的期间长度为日历日180天(可更改)
today='2021-11-19'
hist_sample_len=180
sigma,s0,_=underlying_sigma(ua,today,days=hist_sample_len)
print("annualized_sigma is",round(sigma,5))    
print("underlying security price is",s0)    

#查找年化无风险利率：基于SHIBOR三个月期利率(3M)，默认是近30天内的最新利率
rate_period='3M'
rf=shibor_rate(today,rate_period) 
print("risk-free interest rate is",rf)

#如果未找到，可以扩大查找范围，例如扩大到近期60天内的最新利率
daysahead=60
rf=shibor_rate(today,rate_period,daysahead)

#计算当前日期距离合约到期日的天数
days,_=calc_days(today,maturity)
print("days is",days)    

#第三步：计算期权合约的预期价格
#中国目前金融期权均为无红利的欧式期权，可以直接采用Black-Scholes期权定价模型
expected_price=bs_pricing(s0,x,days,rf,sigma,direction)
#计算的预期结果：0.44，实际价格0.4411
#==============================================================================
#==============================================================================
from siat import *

#第一步：查询金融期权期权
#查看中国当前的金融期权品种
option_fin_china()

#如果希望查看更多内容：
option_fin_china(detail=True)

#查看某个金融期权品种的到期月份：以上交所沪深30050ETF期权（即华泰柏瑞沪深300ETF期权）为例
option="华泰柏瑞沪深300ETF期权"
option_fin_month_china(option)

#查看某个金融期权在某个到期月份的具体合约：
#以华泰柏瑞沪深300ETF期权2022年6月到期的看涨合约为例
end_month='2206'
direction='call'
#脚本默认是看涨期权合约
contracts=option_fin_contracts(option,end_month,direction)

#如果希望查看看跌期权合约
contracts=option_fin_contracts(option,end_month,'put')

#如果希望查看看涨和看跌期权的全部合约：发现看涨和看跌合约都是配对出现的
contracts=option_fin_contracts(option,end_month,'both')

#第二步：查找计算金融期权预期价格所需要的参数
#以2022年6月份到期的华夏上证50ETF期权合约510300C2206M04500为例
contract='510300C2206M04500'
ua,maturity,x=option_fin_contract_parms(option,end_month,contract,direction)
print("underlying asset is",ua)
print("maturity date is",maturity)
print("strike price is",x)
#其到期日是2022-6-28

#计算期权标的证券（510050.SS）价格的历史波动率：
#假定今日是2021-11-19，使用历史样本的期间长度为日历日30天(可更改）
today='2021-11-19'
hist_sample_len=30
sigma,s0,_=underlying_sigma(ua,today,days=hist_sample_len)
print("annualized_sigma is",round(sigma,5))    
print("underlying security price is",s0)    

#查找年化无风险利率：基于SHIBOR三个月期利率(3M)，默认是近30天内的最新利率
rate_period='3M'
rf=shibor_rate(today,rate_period) 
print("risk-free interest rate is",rf)

#如果未找到，可以扩大查找范围，例如扩大到近期60天内的最新利率
daysahead=60
rf=shibor_rate(today,rate_period,daysahead)

#计算当前日期距离合约到期日的天数
days,_=calc_days(today,maturity)
print("days is",days)

#第三步：计算期权合约的预期价格
#中国目前金融期权均为无红利的欧式期权，可以直接采用Black-Scholes期权定价模型
expected_price=bs_pricing(s0,x,days,rf,sigma,direction)
#计算的预期结果：0.55，实际价格0.51
#==============================================================================


# 绝对引用指定目录中的模块
import sys
sys.path.insert(0,r'S:\siat\siat')
from option_china import *
#==============================================================================
def option_fin_china():
    """
    查找中国金融期权列表
    """
    option_fin_list=['华夏上证50ETF期权','华泰柏瑞沪深300ETF期权', \
                     '嘉实沪深300ETF期权','沪深300股指期权']
    num=len(option_fin_list)

    print("  There are",num,"financial options in China mainland at present:")
    for i in option_fin_list:
        print(' ',i)
        
    return option_fin_list



import akshare as ak
#横截面数据
df1 = ak.option_finance_board(symbol="华夏上证50ETF期权", end_month="2112")
list(df1)
#['合约交易代码', '当前价', '涨跌幅', '前结价', '行权价', '数量']

df2 = ak.option_finance_board(symbol="嘉实沪深300ETF期权", end_month="2112")
list(df2)
['合约编码', '合约简称', '标的名称', '类型', '行权价', '合约单位', '期权行权日', '行权交收日']

df3 = ak.option_finance_board(symbol="华泰柏瑞沪深300ETF期权", end_month="2112")
list(df3)
#['合约交易代码', '当前价', '涨跌幅', '前结价', '行权价', '数量']

df4 = ak.option_finance_board(symbol="沪深300股指期权", end_month="2112")
list(df4)
#['instrument',
 'position',
 'volume',
 'lastprice',
 'updown',
 'bprice',
 'bamount',
 'sprice',
 'samount']








#沪深300指数期权
df10 = ak.option_sina_cffex_hs300_list()
#实时行情
df11 = ak.option_sina_cffex_hs300_spot(contract="io2112")
df12 = ak.option_sina_cffex_hs300_daily(contract="io2004C4450")

#==============================================================================
#查找中国商品期权的常见品种
df1=option_comm_china()

#查找中国黄金期权的可用合约
df2=option_comm_china('黄金')

#查找中国黄金期权au2112和au2202的具体合约（看涨/看跌合约）
df3=option_comm_china('黄金','au2112')
df3b=option_comm_china('黄金','au2202')
#同一时刻行权价对期权合约的影响：行权价越高，看涨期权合约价格越低，看跌期权合约价越高

#单一期权合约价格的运动趋势：默认不带趋势线
df4=option_comm_trend_china('au2202C364','2021-9-1','2021-9-30',power=4)

#期权方向对合约价格走势的影响：看涨/看跌期权合约的价格走势正好相反
df5=option_comm_trend_china(['au2202C364','au2202P364'],'2021-8-1','2021-9-30')

#行权价对合约价格时间序列走势的影响：看涨期权，行权价低者合约价高
df6=option_comm_trend_china(['au2112C328','au2112C364'],'2021-8-1','2021-9-30')
#行权价对合约价格时间序列走势的影响：看跌期权，行权价低者合约价低，与看涨期权正好相反
df6b=option_comm_trend_china(['au2112P328','au2112P364'],'2021-8-1','2021-9-30')

#到期时间对合约价格走势的影响：看涨期权，到期日近者合约价低（时间价值少）
df7=option_comm_trend_china(['au2112C364','au2202C364'],'2021-8-1','2021-9-30')
#到期时间对合约价格走势的影响：看跌期权，到期日近者合约价低，与看涨期权一致
df7b=option_comm_trend_china(['au2112P364','au2202P364'],'2021-8-1','2021-9-30')



#==============================================================================

import os; os.chdir('S:/siat')
from siat import *

import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    lg = bs.login()

disable_prints()
#==============================================================================
import akshare as ak
ak.option_sina_commodity_dict(symbol="黄金期权")
ak.option_sina_commodity_contract_list(symbol="黄金期权", contract="au2022")
df = ak.option_finance_board(symbol="华夏上证50ETF期权", end_month="2202")
df = ak.option_sina_commodity_contract_list(symbol="黄金期权", contract="au2012")
df=option_comm_trend_china('au2205C364','2021-9-1','2021-9-30')






