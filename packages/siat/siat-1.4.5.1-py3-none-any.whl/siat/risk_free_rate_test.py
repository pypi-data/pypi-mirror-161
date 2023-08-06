# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat.risk_free_rate import *
#==============================================================================
ff3=get_ff_factors("2018-1-1","2020-12-31",scope='US',factor='FF3',freq='daily')



df1=get_rf_capm('AAPL','^GSPC','2018-1-1','2020-12-31',window=60)
df1['Rf_5']=df1['Rf'].rolling(window=5).mean()
compare_rf(df1,'Rf',df1,'Rf_5','2019-1-1','2019-12-31',twinx=True)

df1['Rf_60']=df1['Rf'].rolling(window=60).mean()
compare_rf(df1,'Rf',df1,'Rf_60','2019-1-1','2019-12-31',twinx=True)

df1['Rf_cum5']=calc_rolling_cumret(df1,'Rf',period='Weekly')
df1['Rf_cum60']=calc_rolling_cumret(df1,'Rf',period='Quarterly')

df1['Rf_winsor']=winsor(df1,'Rf')
compare_rf(df1,'Rf',df1,'Rf_winsor','2018-1-1','2020-12-31')

df1=get_rf_capm('AAPL','^GSPC','2018-1-1','2020-12-31',window=60)
df2=get_rf_capm('MSFT','^GSPC','2018-1-1','2020-12-31',window=60)
df1['Rf_winsor10']=winsor(df1,'Rf',limits=[0.1,0.1])
df2['Rf_winsor10']=winsor(df2,'Rf',limits=[0.1,0.1])
df1['Rf_wa60']=df1['Rf_winsor10'].rolling(window=60).mean()
df2['Rf_wa60']=df2['Rf_winsor10'].rolling(window=60).mean()
compare_rf(df1,'Rf_wa60',df2,'Rf_wa60','2019-1-1','2020-12-31',twinx=True)


df1=get_rf_capm('AAPL','^GSPC','2018-1-1','2020-12-31',window=240)
df2=get_rf_capm('MSFT','^GSPC','2018-1-1','2020-12-31',window=240)
compare_rf(df1,'Rf',df2,'Rf','2019-1-1','2020-12-31',twinx=True)
compare_rf(df1,'Rf',df2,'Rf','2019-1-1','2020-12-31')

df1['Rf_winsor10']=winsor(df1,'Rf',limits=[0.1,0.1])
df2['Rf_winsor10']=winsor(df2,'Rf',limits=[0.1,0.1])
df1['Rf_wa21']=df1['Rf_winsor10'].rolling(window=21).mean()
df2['Rf_wa21']=df2['Rf_winsor10'].rolling(window=21).mean()
compare_rf(df1,'Rf_wa21',df2,'Rf_wa21','2019-1-1','2020-12-31',twinx=True)
compare_rf(df1,'Rf_wa21',df2,'Rf_wa21','2019-1-1','2020-12-31')


df1=get_rf_capm('^DJI','^GSPC','2018-1-1','2020-12-31',window=240)
df2=get_rf_capm('^GSPC','^DJI','2018-1-1','2020-12-31',window=240)
df1['Rf_winsor']=winsor(df1,'Rf',limits=[0.01,0.01])
df2['Rf_winsor']=winsor(df2,'Rf',limits=[0.01,0.01])
df1['Rf_wa60']=df1['Rf_winsor'].rolling(window=60).mean()
df2['Rf_wa60']=df2['Rf_winsor'].rolling(window=60).mean()
compare_rf(df1,'Rf_wa60',df2,'Rf_wa60','2019-1-1','2020-12-31',twinx=True)
compare_rf(df1,'Rf_wa60',df2,'Rf_wa60','2019-1-1','2020-12-31')






df1['Rf'].plot()


df1['Rf_5'].plot()

df1['Rf_10']=df1['Rf'].rolling(window=10).mean()
df1['Rf_10'].plot()

df1['Rf_20']=df1['Rf'].rolling(window=20).mean()
df1['Rf_20'].plot()

df1['Rf_60']=df1['Rf'].rolling(window=60).mean()
df1['Rf_60'].plot()

df1['Rf_120']=df1['Rf'].rolling(window=120).mean()
df1['Rf_120'].plot()

df1['Rf_240']=df1['Rf'].rolling(window=240).mean()
df1['Rf_240'].plot()




df2=get_rf_capm('MSFT','^GSPC','2018-1-1','2020-12-31',window=30)
df2['Rf'].plot()

df2['Rf_240']=df2['Rf'].rolling(window=240).mean()
df2['Rf_240'].plot()

compare_rf(df1,'Rf_240',df2,'Rf_240','2019-1-1','2019-12-31',twinx=True)





#==============================================================================
df1=get_rf_capm('000001.SS','000300.SS','2020-1-1','2020-12-31',window=240)
df1['Rf'].plot()

df2=get_rf_capm('399001.SZ','000300.SS','2020-1-1','2020-12-31',window=240)
df2['Rf'].plot()

#==============================================================================
df3=get_rf_capm('600519.SS','000300.SS','2020-1-1','2020-12-31',window=240)
df3['Rf'].plot()

df4=get_rf_capm('000858.SZ','000300.SS','2020-1-1','2020-12-31',window=240)
df4['Rf'].plot()

#==============================================================================
df5=get_rf_capm('AAPL','^GSPC','2020-1-1','2020-12-31',window=240)
df5['Rf'].plot()

df6=get_rf_capm('MSFT','^GSPC','2020-1-1','2020-12-31',window=240)
df6['Rf'].plot()

#==============================================================================
df7=get_rf_capm('AAPL','^GSPC','2018-1-1','2020-12-31',window=240)
df7['Rf'].plot()

df8=get_rf_capm('MSFT','^GSPC','2018-1-1','2020-12-31',window=240)
df8['Rf'].plot()

#==============================================================================


if __name__=='__main__':
    compare_rf(df7,df8,'2018-1-1','2018-12-31')

