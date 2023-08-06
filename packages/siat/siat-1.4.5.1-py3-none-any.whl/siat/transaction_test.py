# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,r'S:\siat')
from siat import *

if __name__=='__main__':
    df=market_profile_china('SSE')
    df=market_profile_china('SZSE')


import os; os.chdir("S:/siat")

from siat import *

from siat.allin import *

from siat.bond import *
#==============================================================================
compare_security(['SPSK','^DJI'],"Close","2020-1-1","2021-5-31")
#==============================================================================
compare_security(['^IRX','^TYX'],"Close","2019-1-1","2021-5-31")
compare_security(['^IRX','^FYX'],"Close","2019-8-1","2019-8-31")
compare_security(['^IRX','^TYX'],"Close","2021-3-1","2021-5-31")

compare_security(['^IRX','^TYX'],"Close","2010-1-1","2021-5-25")
#==============================================================================
compare_security(['000001.SS','^HSI'],"Annual Ret%","2016-1-1","2020-12-31")
compare_security(['000001.SS','^HSI'],"Annual Ret%","2020-1-1","2021-3-31")
compare_security(['000001.SS','^HSI'],"Annual Ret%","2019-1-1","2021-3-31")

compare_security(['000001.SS','^DJI'],"Annual Ret%","2019-1-1","2021-3-31")
compare_security(['000001.SS','^N225'],"Annual Ret%","2019-1-1","2021-3-31")

compare_security(['000001.SS','399001.SZ'],"Exp Ret%","2019-1-1","2021-3-31")

compare_security(['000012.SS','000001.SS'],"Exp Ret%","2019-1-1","2021-3-31")

compare_security(['000001.SS','399106.SZ'],"Annual Ret Volatility%","2019-1-1","2021-3-31")

# 获得中债-综合指数行情：
from siat.bond import *
df1=bond_index_china('中债-综合指数',"2017-1-1","2021-3-31",graph=False)
# 获得上证综合指数行情：
from siat.security_prices import *
df2=get_prices('000001.SS',"2017-1-1","2021-3-31")
#比较两种指数的收益率波动风险：
from siat.transaction import *
compare_indicator(df1,df2,'Annual Ret Volatility%',"2019-1-1","2021-3-31")
compare_indicator(df1,df2,'Annual Ret Volatility%',"2019-1-1","2021-3-31",twinx=True)

compare_security(['000001.SS','399106.SZ'],"Exp Ret Volatility%","2019-1-1","2021-3-31")

# 获得中债-综合指数行情：
from siat.bond import *
df1=bond_index_china('中债-综合指数',"2017-1-1","2021-3-31",graph=False)
# 获得上证综合指数行情：
from siat.security_prices import *
df2=get_prices('000001.SS',"2017-1-1","2021-3-31")
#比较两种指数的持有收益率波动风险：
from siat.transaction import *
compare_indicator(df1,df2,'Exp Ret Volatility%',"2019-1-1","2021-3-31")

compare_security(['000001.SS','399001.SZ'],"Annual Ret LPSD%","2019-1-1","2021-3-31")

# 获得中债-综合指数行情：
from siat.bond import *
df1=bond_index_china('中债-综合指数',"2017-1-1","2021-3-31",graph=False)
# 获得上证综合指数行情：
from siat.security_prices import *
df2=get_prices('000001.SS',"2017-1-1","2021-3-31")
#比较两种指数的持有损失波动风险：
from siat.transaction import *
compare_indicator(df1,df2,'Exp Ret LPSD%',"2019-1-1","2021-3-31")
结果显示，这两种指数的持有损失风险（使用下偏标准差）指数走势图与前述案例中的持有收益率风险（使用标准差）走势图差异较小，十分相似，说明两种指数的持有损失风险分布形状与持有收益率风险分布比较接近。



#==============================================================================
df=security_price('000300.SS','2004-1-1','2020-12-31',power=6)

#==============================================================================
compare_security(["SX23.CBT","SX22.CBT"],"Close","2020-1-1","2020-6-30")
compare_security(["GCZ25.CMX","GCZ24.CMX"],"Close","2020-1-1","2020-6-30")

compare_security(["ZT=F","ZF=F"],"Close","2010-1-1","2020-6-30")

df=security_price('6BH22.CME','2020-10-1','2021-1-31',power=4)

compare_security(["GEM23.CME","GEM24.CME"],"Close","2020-1-1","2020-12-31")
#==============================================================================
compare_security(["FRI","^RUT"],"Exp Ret%","2010-1-1","2020-6-30")
compare_security(["FRI","^RUT"],"Exp Ret Volatility%","2010-1-1","2020-6-30")

compare_security(["FRI","^RUT"],"Exp Ret%","2010-1-1","2019-12-31")
compare_security(["FRI","^RUT"],"Exp Ret Volatility%","2010-1-1","2019-12-31")



#==============================================================================
compare_security(["SPY","^GSPC"],"Exp Ret%","2010-1-1","2020-6-30")
compare_security(["IVV","^GSPC"],"Exp Ret%","2010-1-1","2020-6-30")

compare_security(["SPY","^GSPC"],"Exp Ret Volatility%","2010-1-1","2020-6-30")
compare_security(["IVV","^GSPC"],"Exp Ret Volatility%","2010-1-1","2020-6-30")

compare_security(["SPY","SPYD"],"Exp Ret%","2019-1-1","2020-6-30")
compare_security(["SPY","SPYG"],"Exp Ret%","2019-1-1","2020-6-30")
compare_security(["SPY","SPYV"],"Exp Ret%","2019-1-1","2020-6-30")
compare_security(["SPY","SPYD"],"Exp Ret Volatility%","2019-1-1","2020-6-30")
compare_security(["SPY","SPYG"],"Exp Ret Volatility%","2019-1-1","2020-6-30")
compare_security(["SPY","SPYV"],"Exp Ret Volatility%","2019-1-1","2020-6-30")

compare_security(["FRI","^GSPC"],"Exp Adj Ret%","2010-1-1","2020-6-30")
compare_security(["FRI","^GSPC"],"Exp Adj Ret Volatility%","2010-1-1","2020-6-30")

compare_security(["ICF","^DJI"],"Exp Adj Ret%","2010-1-1","2020-6-30")
compare_security(["ICF","^DJI"],"Exp Adj Ret Volatility%","2010-1-1","2020-6-30")




#==============================================================================
info=security_price("ZSF22.CBT","2021-1-1","2021-3-31")

info=security_price("510210.SS","2020-4-1","2020-6-30")

info=security_price("510210.SS","2020-4-1","2020-6-30")
compare_security(["510210.SS","000001.SS"],"Close","2020-4-1","2020-6-30",twinx=True)
compare_security(["510210.SS","000001.SS"],"Close","2019-1-1","2020-12-31",twinx=True)
compare_security(["SPY","^GSPC"],"Close","2010-1-1","2020-6-30",twinx=True)
compare_security(["IVV","^GSPC"],"Close","2010-1-1","2020-6-30",twinx=True)

compare_security(["SPY","^GSPC"],"Close","2010-1-1","2020-6-30",twinx=True)


compare_security(['^DJI','000001.SS'],"Close","1991-1-1","2021-3-2",twinx=True)
compare_security(['^DJI','000001.SS'],"Close","2020-12-1","2021-3-2",twinx=True)


compare_security(['^TNX','^DJI'],"Close","1991-1-1","2021-3-2",twinx=True)
compare_security(['^TNX','^DJI'],"Close","2020-12-1","2021-3-2",twinx=True)

compare_security(['^TNX','000001.SS'],"Close","1991-1-1","2021-3-2",twinx=True)
compare_security(['000001.SS','^DJI'],"Close","1992-1-1","2021-3-2",twinx=True)


compare_security(['000001.SS','399001.SZ'],"Annual Ret%","1991-1-1","2021-2-28")
compare_security(['000002.SS','399107.SZ'],"Annual Ret%","2000-1-1","2020-12-31")
compare_security(['000003.SS','399108.SZ'],"Annual Ret%","2000-1-1","2020-12-31")

compare_security(['000002.SS','000003.SS'],"Annual Ret%","2000-1-1","2020-12-31")
compare_security(['399107.SZ','399108.SZ'],"Annual Ret%","2000-1-1","2020-12-31")

compare_security(['^HSI','000001.SS'],"Annual Ret%","2000-1-1","2020-12-31")
compare_security(['^DJI','000001.SS'],"Annual Ret%","2000-1-1","2020-12-31")
compare_security(['^N225','000001.SS'],"Annual Ret%","2000-1-1","2020-12-31")
compare_security(['^N225','^DJI'],"Annual Ret%","2000-1-1","2020-12-31")


compare_security(['000001.SS','399001.SZ'],"Exp Ret%","2010-1-1","2020-12-31")
compare_security(['000012.SS','000001.SS'],"Exp Ret%","2010-1-1","2020-12-31")

compare_security(['159926.SS','000012.SS'],"Exp Ret%","2010-1-1","2020-12-31")
import akshare as ak
fund_etf_hist_sina_df = ak.fund_etf_hist_sina(symbol="sz169103")
print(fund_etf_hist_sina_df)

compare_security(['^HSI','000001.SS'],"Exp Ret%","2010-1-1","2020-12-31")
compare_security(['^DJI','000001.SS'],"Exp Ret%","2010-1-1","2020-12-31")
compare_security(['^N225','000001.SS'],"Exp Ret%","2010-1-1","2020-12-31")
compare_security(['^N225','^DJI'],"Exp Ret%","2010-1-1","2020-12-31")


compare_security(['000001.SS','399106.SZ'],"Annual Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['399001.SZ','399012.SZ'],"Annual Ret Volatility%","2015-1-1","2020-12-31")
compare_security(['^HSI','000001.SS'],"Annual Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['^HSI','399001.SZ'],"Annual Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['^DJI','000001.SS'],"Annual Ret Volatility%","2010-1-1","2020-12-31")


compare_security(['000001.SS','399106.SZ'],"Exp Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['000001.SS','^HSI'],"Exp Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['000001.SS','^DJI'],"Exp Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['000001.SS','^N225'],"Exp Ret Volatility%","2010-1-1","2020-12-31")


compare_security(['000001.SS','^DJI'],"Annual Ret LPSD%","2010-1-1","2020-12-31")
compare_security(['000001.SS','^GSPC'],"Exp Ret LPSD%","2010-1-1","2020-12-31")
compare_security(['000001.SS','^KS11'],"Exp Ret LPSD%","2010-1-1","2020-12-31")
compare_security(['000001.SS','^BSESN'],"Exp Ret LPSD%","2010-1-1","2020-12-31")
compare_security(['^N225','^KS11'],"Exp Ret LPSD%","2010-1-1","2020-12-31")


compare_security(['000012.SS','000001.SS'],"Annual Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['000012.SS','000001.SS'],"Exp Ret Volatility%","2010-1-1","2020-12-31")
compare_security(['000012.SS','000001.SS'],"Exp Ret LPSD%","2010-1-1","2020-12-31")

#==============================================================================
from siat.transaction import *
df1=security_price('000300.SS','2004-1-1','2020-12-31',power=6)
df2=security_price('000906.SS','2004-1-1','2020-12-31',power=6)

compare_security(['000906.SS','000300.SS'],"Close","2004-1-1","2020-12-31")
compare_security(['000938.SS','000300.SS'],"Close","2004-1-1","2020-12-31")
compare_security(['000016.SS','000300.SS'],"Close","2004-1-1","2021-2-28",twinx=True)
compare_security(['000688.SS','000300.SS'],"Close","2020-1-1","2021-2-28",twinx=True)

df=security_price('000001.SS','1990-12-1','2021-2-28',power=6)

df=security_price('300401.SZ','2018-5-1','2018-5-5')

compare_security(['000043.SS','000045.SS'],"Close","2010-1-1","2021-2-28",twinx=True)
compare_security(['399001.SZ','000001.SS'],"Close","1994-1-1","2021-2-28",twinx=True)

compare_security(['^HSI','000001.SS'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['^HSCE','^HSI'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['^HSNU','^HSI'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['^TWII','000001.SS'],"Close","1997-1-1","2021-2-28",twinx=True)

compare_security(['^N225','000001.SS'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['^KS11','000001.SS'],"Close","1997-1-1","2021-2-28",twinx=True)

compare_security(['^BSESN','000001.SS'],"Close","1997-1-1","2021-2-28",twinx=True)

compare_security(['245710.KS','000001.SS'],"Close","2016-7-1","2021-2-28",twinx=True)

compare_security(['^VNIPR','000001.SS'],"Close","2016-1-1","2021-2-28",twinx=True)

compare_security(['^DJI','000001.SS'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['^GSPC','^DJI'],"Close","1990-1-1","2021-2-28",twinx=True)

compare_security(['^IXIC','^DJI'],"Close","1990-1-1","2021-2-28",twinx=True)

compare_security(['^FTSE','000001.SS'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['^GDAXI','^FTSE'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['^FCHI','^GDAXI'],"Close","1991-1-1","2021-2-28",twinx=True)

compare_security(['IMOEX.ME','000001.SS'],"Close","2013-1-1","2021-2-28",twinx=True)



compare_security(['000012.SS','000001.SS'],"Close","2002-1-1","2021-2-28",twinx=True)
compare_security(['000013.SS','000012.SS'],"Close","2003-1-1","2021-2-28",twinx=True)
compare_security(['000022.SS','000013.SS'],"Close","2008-1-1","2021-2-28",twinx=True)
compare_security(['000116.SS','000022.SS'],"Close","2013-1-1","2021-2-28",twinx=True)

#==============================================================================


from siat.bond import *
df1=bond_index_china('中债-综合指数','2002-1-1','2020-12-31',graph=False)
draw_indicator(df1,'Close','2002-1-1','2020-12-31')

from siat.security_prices import *
df2=get_prices('000001.SS','2002-1-1','2020-12-31')

from siat.transaction import *
compare_indicator(df1,df2,'Close','2002-1-1','2020-12-31',twinx=True)
compare_indicator(df1,df2,'Annual Ret%','2002-1-1','2020-12-31')
compare_indicator(df1,df2,'Annual Ret Volatility%','2002-1-1','2020-12-31')
draw_indicator(df1,'Annual Ret Volatility%','2002-1-1','2020-12-31',power=5)

compare_indicator(df1,df2,'Exp Ret Volatility%','2002-1-1','2020-12-31')
compare_indicator(df1,df2,'Exp Ret LPSD%','2002-1-1','2020-12-31')
compare_indicator(df1,'Exp Ret LPSD%','2002-1-1','2020-12-31')

hlj=bond_index_china('中债-黑龙江省地方政府债指数','2016-1-1','2020-12-31',graph=False)
gd=bond_index_china('中债-广东省地方政府债指数','2016-1-1','2020-12-31',graph=False)
compare_indicator(hlj,gd,'Close','2016-1-1','2020-12-31',twinx=True)


if __name__=='__main__':
    market_profile_china('SSE')
    market_profile_china('SZSE')

if __name__=='__main__':
    draw_indicator(df2,'Annual Ret%','2010-1-1','2020-12-31')
    compare_indicator(df1,df2,'Annual Ret%','2010-1-1','2020-12-31')
    
    compare_indicator(df1,df2,'Annual Ret Volatility%','2010-1-1','2020-12-31')
    compare_indicator(df1,df2,'Annual Ret LPSD%','2010-1-1','2020-12-31')
    
    compare_indicator(df1,df2,'Exp Ret%','2010-1-1','2020-12-31')
    compare_indicator(df1,df2,'Exp Ret LPSD%','2010-1-1','2020-12-31')
    
    from siat.bond import *
    search_bond_index_china(keystr='国债',printout=True)
    df1=bond_index_china('中债-0-1年国债指数','2018-1-1','2020-12-31',graph=False)
    df2=bond_index_china('中债-10年期国债指数','2018-1-1','2020-12-31',graph=False)
    compare_indicator(df1,df2,'Annual Ret%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Annual Ret Volatility%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Exp Ret%','2010-1-1','2020-12-31')
    
    
    
    draw_indicator(df1,'Annual Ret%','2019-7-1','2020-6-30')


#==============================================================================
import os; os.chdir("S:/siat")
from siat.transaction import *


df=security_price('600519.SS','2020-1-1','2020-12-31',power=5)

compare_security(["AAPL","MSFT"],"Annual Ret Volatility%","2020-1-1","2020-12-31")



df=security_price('600519.SS','2020-1-1','2020-12-31',power=5)

compare_security(["AAPL","MSFT"],"Daily Ret%","2020-1-1","2020-12-31")

compare_security("MSFT",["Daily Ret%","Annual Ret%"],"2020-1-1","2020-12-31")

compare_security("AAPL",["Daily Ret%","Annual Ret%"],"2020-1-1","2020-12-31")

compare_security(["AAPL","MSFT"],"Annual Ret%","2020-1-1","2020-12-31")

compare_security(["AAPL","MSFT"],"Annual Adj Ret%","2020-1-1","2020-12-31")

compare_security(["TWTR","FB"],"Annual Ret%","2020-1-1","2020-12-31")

compare_security(["600519.SS","000858.SZ"],"Annual Adj Ret%","2020-1-1","2020-12-31")

compare_security(["DAI.DE","BMW.DE"],"Annual Adj Ret%","2020-1-1","2020-12-31")

compare_security(["7203.T","7201.T"],"Annual Adj Ret%","2020-1-1","2020-12-31")

compare_security(["4911.T","4452.T"],"Annual Adj Ret%","2020-1-1","2020-12-31")

compare_security(["9983.T","7453.T"],"Annual Adj Ret%","2020-1-1","2020-12-31")







compare_security(["000001.SS","399001.SZ"],"Close","2020-1-1","2020-12-31", twinx=True)

df=security_price('000001.SS','2020-1-1','2020-12-31',power=5)

compare_security(["000001.SS","^HSI"],"Close","2020-1-1","2020-12-31", twinx=True)

compare_security(["000001.SS","^N225"],"Close","2020-1-1","2020-12-31", twinx=True)

compare_security(["000001.SS","^KS11"],"Close","2020-1-1","2020-12-31", twinx=True)

compare_security(["^KS11","^N225"],"Close","2020-1-1","2020-12-31", twinx=True)

compare_security(["000001.SS","^DJI"],"Close","2020-1-1","2020-12-31", twinx=True)

compare_security(["^DJI","^GSPC"],"Close","2020-1-1","2020-12-31", twinx=True)



df=security_price('6BH22.CME','2020-10-1','2021-1-31',power=4)

compare_security(["ZT=F","ZF=F"],"Exp Ret%","2010-1-1","2020-6-30")
compare_security(["ZN=F","ZB=F"],"Exp Ret%","2010-1-1","2020-6-30")

compare_security(["ZT=F","ZF=F"],"Exp Ret Volatility%","2010-1-1","2020-6-30")
compare_security(["ZN=F","ZB=F"],"Exp Ret Volatility%","2010-1-1","2020-6-30")


compare_security(["ES=F","^GSPC"],"Close","2020-1-1","2020-12-31")

compare_security(["ES=F","^GSPC"],"Close","2020-10-1","2020-12-31")

compare_security(["ES=F","^GSPC"],"Close","2020-12-1","2020-12-31")

compare_security(["ES=F","^GSPC"],"Close","2020-11-1","2020-12-31")


compare_security(["ES=F","^GSPC"],"Close","2020-12-1","2021-1-15")
compare_security(["ES=F","^GSPC"],"Annual Price Volatility","2020-12-1","2021-1-15")
compare_security(["ES=F","^GSPC"],"Exp Ret%","2020-12-1","2021-1-15")
compare_security(["ES=F","^GSPC"],"Exp Ret Volatility","2020-12-1","2021-1-15")



df=security_price('MSFT','2021-1-1','2021-1-31',datatag=True,power=4)

info=get_stock_profile("AAPL")
info=get_stock_profile("MSFT",info_type='officers')
info=get_stock_profile("AAPL",info_type='officers')
info=stock_info('AAPL')
sub_info=stock_officers(info)

div=stock_dividend('600519.SS','2011-1-1','2020-12-31')
split=stock_split('600519.SS','2000-1-1','2020-12-31')

ticker='AAPL'
info=stock_info(ticker)
info=get_stock_profile("AAPL",info_type='officers')

info=get_stock_profile("AAPL")

info=get_stock_profile("MSFT",info_type='officers')
info=get_stock_profile("GS",info_type='officers')

info=stock_info('JD')
sub_info=stock_officers(info)
info=get_stock_profile("JD",info_type='officers')

info=stock_info('BABA')
sub_info=stock_officers(info)
info=get_stock_profile("BABA",info_type='officers')

info=stock_info('0700.HK')
sub_info=stock_officers(info)
info=get_stock_profile("0700.HK",info_type='officers')

info=stock_info('600519.SS')
sub_info=stock_officers(info)
info=get_stock_profile("600519.SS",info_type='officers')

info=get_stock_profile("0939.HK",info_type='risk_esg')


market={'Market':('China','^HSI')}
stocks={'0700.HK':3,'9618.HK':2,'9988.HK':1}
portfolio=dict(market,**stocks)
esg=portfolio_esg2(portfolio)



