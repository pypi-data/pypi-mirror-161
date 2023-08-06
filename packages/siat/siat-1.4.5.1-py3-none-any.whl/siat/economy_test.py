# -*- coding: utf-8 -*-


import os; os.chdir("S:/siat")
from siat import *

#==============================================================================
tickers=['China','Japan']
measures='Constant CPI'
fromdate='2022-1-1'
todate='2022-1-1'
power=0
twinx=False
loc1='upper left';loc2='lower right'




cn_jp=compare_economy(['China','Japan'],'Constant CPI','2010-1-1','2022-1-1')






cn_jp=compare_economy(['China','Japan'],'Currency Value','2010-1-1','2022-1-1',loc1='upper right')
internal_growth_rate(cn_jp)

cn_usa=compare_economy(['China','USA'],'Currency Value','2010-1-1','2022-1-1',loc1='upper right')
internal_growth_rate(cn_usa)

cn_fr=compare_economy(['China','France'],'Currency Value','2010-1-1','2022-1-1',loc1='upper right')
internal_growth_rate(cn_fr)

cn_uk=compare_economy(['China','UK'],'Currency Value','2010-1-1','2022-1-1',loc1='upper right')
internal_growth_rate(cn_uk)

cn_in=compare_economy(['China','India'],'Currency Value','2010-1-1','2022-1-1',loc1='upper right')
internal_growth_rate(cn_in)

df=compare_security(['^IRX','^TYX'],"Close","2015-1-1","2022-12-31")

#==============================================================================
cn_usa=compare_economy(['China','USA'],'M2','1999-12-1','2022-4-1',twinx=True)
cn_usa=compare_economy(['China','USA'],'Constant M2','1999-12-1','2022-4-1')
cn_usa=compare_economy('China',['Constant M1','Constant M2'],'1999-12-1','2022-4-1')


cn=economy_trend('2010-1-1','2020-1-1','China','MoM CPI',power=4,zeroline=True)
cn=economy_trend('2010-1-1','2020-1-1','China','Constant CPI',power=4)
cn_jp=compare_economy(['China','Japan'],'Constant CPI','2010-1-1','2020-1-1')


#==============================================================================
cn_usa=compare_economy(['China','USA'],'Immediate Rate','2010-1-1','2021-5-25')
cn_jp=compare_economy(['China','Japan'],'Immediate Rate','2010-1-1','2021-1-1')
cn_uk=compare_economy(['China','LIBOR'],'Immediate Rate','2010-1-1','2021-1-1')
#==============================================================================
cn_usa=compare_economy(['China','USA'],'CNP GDP Per Capita','2010-1-1','2020-1-1')
cn_usa=compare_economy(['China','USA'],'CNP GDP Per Capita','2010-1-1','2020-1-1',twinx=True)

df=pmi_china('2008-1-1','2021-3-31')


c_cn=economy_trend('2010-1-1','2020-1-1','China','Constant GDP',power=3)
internal_growth_rate(c_cn)

usa_cn=compare_economy(['USA','China'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(usa_cn)

jp_cn=compare_economy(['Japan','China'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)

df=pmi_china('2020-1-1','2020-10-1')

cn_jp=compare_economy(['China','Japan'],'Currency Value','2000-1-1','2021-1-1')
cn_us=compare_economy(['China','USA'],'Currency Value','1993-1-1','2021-1-1')

jp_us=compare_economy(['Japan','USA'],'Currency Value','1993-1-1','2021-1-1')
internal_growth_rate(cn_jp)

cn_uk=compare_economy(['China','LIBOR'],'Immediate Rate','2000-1-1','2020-1-1')

cn=economy_trend('2000-1-1','2020-8-31','China','Exchange Rate')

cn=econ_fin_depth('2000-1-1','2020-6-30','China',power=3)

cn=compare_economy(['China','USA'],'SMC to GDP','2000-1-1','2020-1-1')

cn1=economy_security('China','1999-1-1','2019-12-31','GDP','000001.SS')
cn2=economy_security('China','1999-1-1','2019-12-31','CNP GDP','000001.SS')
cn3=economy_security('China','1999-1-1','2019-12-31','CNP GDP Per Capita','000001.SS')
cn4=economy_security('China','1999-1-1','2019-12-31','GNI','000001.SS')

df=get_econ_factors0(start,end,scope,factor)


cn_usa=compare_economy(['China','USA'],'Currency Value','2010-1-1','2021-1-1')
cn_jp=compare_economy(['China','Japan'],'Currency Value','2010-1-1','2021-5-25')

cn_sg=compare_economy(['China','Korea'],'Currency Value','2010-1-1','2021-1-1')
cn_sg=compare_economy(['China','Russia'],'Currency Value','2010-1-1','2021-1-1')
cn_sg=compare_economy(['China','India'],'Currency Value','2010-1-1','2021-1-1')


cn=compare_economy(['China','USA'],'GNP Ratio','1995-1-1','2010-1-1')
cn_usa=compare_economy(['China','USA'],'GNP Ratio','1999-1-1','2019-1-1')
cn_jp=compare_economy(['China','Japan'],'GNP Ratio','1999-1-1','2019-1-1')
us_jp=compare_economy(['USA','Japan'],'GNP Ratio','1999-1-1','2019-1-1')
cn_in=compare_economy(['China','India'],'GNP Ratio','1999-1-1','2020-1-1')




cn=economy_trend('1990-1-1','2020-1-1','China','GNI',power=3)
cn_gdp_gni=compare_economy('China',['GDP','GNI'],'1990-1-1','2020-1-1')
cn_gdp_gni=compare_economy('China',['GDP','GNI'],'2010-1-1','2020-1-1',twinx=True)


cn1=economy_security('China','1999-1-1','2019-12-31','GDP','000001.SS')
cn2=economy_security('China','1999-1-1','2019-12-31','CNP GDP','000001.SS')
cn2=economy_security('China','1999-1-1','2019-12-31','Constant GDP','000001.SS')

cn3=economy_security('China','1999-1-1','2019-12-31','CNP GDP Per Capita','000001.SS')
cn4=economy_security('China','1999-1-1','2019-12-31','GNI','000001.SS')

jp1=economy_security('Japan','1980-1-1','2019-12-31','CNP GDP','^N225')
us1=economy_security('USA','1980-1-1','2019-12-31','CNP GDP','^GSPC')
us2=economy_security('USA','1980-1-1','2019-12-31','CNP GDP','^DJI')


cn=econ_fin_depth('2000-1-1','2020-6-30','China',power=3)
cn,jp=compare_efd('2000-1-1','2020-8-31',['China','Japan'])
cn,kr=compare_efd('2000-1-1','2020-8-31',['China','Korea'])
cn,us=compare_efd('2000-1-1','2020-8-31',['China','USA'])

cn=compare_economy(['China','USA'],'SMC to GDP','2000-1-1','2020-1-1')




cn_usa=compare_economy(['China','USA'],'CNP GDP Per Capita','2010-1-1','2020-1-1')
cn_usa=compare_economy(['China','USA'],'CNP GDP Per Capita','2010-1-1','2020-1-1' ,twinx=True)
internal_growth_rate(cn_usa)

cn_jp=compare_economy(['China','Japan'],'CNP GDP Per Capita','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_jp)

cn_in=compare_economy(['China','India'],'CNP GDP Per Capita','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_in)

cn=economy_trend('2010-1-1','2021-5-25','China','Constant CPI',power=4)

cn_usa=compare_economy(['China','USA'],'Constant CPI','2010-1-1','2021-5-25')
internal_growth_rate(cn_usa)

cn_jp=compare_economy(['China','Japan'],'Constant CPI','2010-1-1','2021-5-25')
internal_growth_rate(cn_jp)

cn_ru=compare_economy(['China','Russia'],'Constant CPI','2010-1-1','2020-1-1')
internal_growth_rate(cn_ru)

cn_in=compare_economy(['China','India'],'Constant CPI','2010-1-1','2020-1-1')
internal_growth_rate(cn_in)




c_cn=economy_trend('2010-1-1','2020-1-1','China','Constant GDP',power=3)
internal_growth_rate(c_cn)

usa_cn=compare_economy(['USA','China'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(usa_cn)

jp_cn=compare_economy(['Japan','China'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(jp_cn)

in_cn=compare_economy(['India','China'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(in_cn)

cn_gdp_c=economy_trend('2010-1-1','2020-1-1','China','Constant GDP')
internal_growth_rate(cn_gdp_c)

cn_gdp_cp=economy_trend('2010-1-1','2020-1-1','China','GDP')
internal_growth_rate(cn_gdp_cp)


cn_gdp_cnp=economy_trend('2010-1-1','2020-1-1','China','CNP GDP')
internal_growth_rate(cn_gdp_cnp)




cn=economy_trend('2010-1-1','2020-1-1','China','GDP',power=3)
internal_growth_rate(cn)

cn_cnp=compare_economy('China',['GDP','CNP GDP'],'2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_cnp)

cn_cpi=compare_economy('China',['GDP','Constant CPI'],'2010-1-1','2020-1-1',power=4,twinx=True)
internal_growth_rate(cn_cpi)

cn_c=economy_trend('2010-1-1','2020-1-1','China','Constant GDP',power=4)
internal_growth_rate(cn_c)




cn_usa=compare_economy(['China','USA'],'Constant CPI','2010-1-1','2020-1-1')
internal_growth_rate(cn_usa)

cn=economy_trend('2010-1-1','2020-1-1','China','Constant CPI',power=4,zeroline=True)
internal_growth_rate(cn)


cn=economy_trend('2010-1-1','2020-1-1','China','MoM CPI',power=4,zeroline=True)


cn_usa=compare_economy(['China','USA'],'Constant GDP','2010-1-1','2019-1-1',twinx=True)
internal_growth_rate(cn_usa)





cn_usa=compare_economy(['China','USA'],'Constant GDP Per Capita','2010-1-1','2020-1-1')
internal_growth_rate(cn_usa)

cn_jp=compare_economy(['China','Japan'],'Constant GDP Per Capita','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_jp)

cn_india=compare_economy(['China','India'],'Constant GDP Per Capita','2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_india)

cn_usa=compare_economy(['China','USA'],'Constant CPI','2010-1-1','2020-1-1')
internal_growth_rate(cn_usa)

cn_jp=compare_economy(['China','Japan'],'Constant CPI','2010-1-1','2020-1-1')
internal_growth_rate(cn_jp)

cn_ru=compare_economy(['China','Russia'],'Constant CPI','2010-1-1','2020-1-1')
internal_growth_rate(cn_ru)

cn_in=compare_economy(['China','India'],'Constant CPI','2010-1-1','2020-1-1')
internal_growth_rate(cn_in)

cn=economy_trend('2010-1-1','2020-1-1','China','GDP',power=3)
internal_growth_rate(cn)

cn=compare_economy('China',['GDP','CNP GDP'],'2010-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn)

cn=compare_economy('China',['GDP','Exchange Rate'],'2010-1-1','2020-8-31',twinx=True)
internal_growth_rate(cn)


cn=compare_economy(['China','USA'],'Immediate Rate','2000-1-1','2020-1-1')
cn_jp=compare_economy(['China','Japan'],'Immediate Rate','2000-1-1','2020-1-1')
cn_kr=compare_economy(['China','Korea'],'Immediate Rate','2000-1-1','2020-1-1')
cn_uk=compare_economy(['China','LIBOR'],'Immediate Rate','2000-1-1','2020-1-1')

cn=economy_trend('2000-1-1','2021-2-27','China','Exchange Rate')
euro=economy_trend('2000-1-1','2020-8-30','Euro','Exchange Rate',power=4)



cn1=compare_economy('China',['M0','M1'],'2000-1-1','2020-1-1')
internal_growth_rate(cn1)
df=economy_trend('2010-1-1','2020-1-1','China','M1',power=4)

cn=compare_economy('China',['M1','M2'],'2000-1-1','2020-1-1')
internal_growth_rate(cn)

cn=compare_economy('China',['M2','M3'],'2000-1-1','2020-1-1')
internal_growth_rate(cn)

cn=compare_economy('Japan',['M2','M3'],'2000-1-1','2018-1-1')
internal_growth_rate(cn)

cn_usa=compare_economy(['China','USA'],'M2','2000-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_usa)

cn_jp=compare_economy(['China','Japan'],'M2','2000-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_jp)

cn_kr=compare_economy(['China','Korea'],'M2','2000-1-1','2020-1-1',twinx=True)
internal_growth_rate(cn_kr)


cn=economy_trend('2000-1-1','2020-1-1','China','Discount Rate',power=0)






df=pmi_china('2020-1-1','2021-2-26')

df=pmi_china('2019-1-1','2021-2-26')

cn=economy_trend('2010-1-1','2020-1-1','China','MoM CPI',power=4,zeroline=True)

cn=economy_trend('2010-1-1','2020-1-1','China','Constant CPI',power=4)
cn=compare_economy(['China','USA'],'Constant CPI','2010-1-1','2020-1-1')
cn=compare_economy(['China','Japan'],'Constant CPI','2010-1-1','2020-1-1')
cn=compare_economy(['China','Russia'],'Constant CPI','2010-1-1','2020-1-1')
cn=compare_economy(['China','India'],'Constant CPI','2010-1-1','2020-1-1')

n=economy_trend('2010-1-1','2015-1-1','China','YoY PPI',power=4,zeroline=True)
n=economy_trend('2010-1-1','2015-1-1','China','Constant PPI',power=4,zeroline=True)




cn=economy_trend('2010-1-1','2020-1-1','China','GDP',power=3)
cn=compare_economy('China',['GDP','CNP GDP'],'2010-1-1','2020-1-1',twinx=True)

cn=compare_economy('China',['GDP','CPI'],'2010-1-1','2020-8-31',power=4,twinx=True)

cn=compare_economy('China',['GDP','Exchange Rate'],'2010-1-1','2020-8-31',twinx=True)

cn=economy_trend('2010-1-1','2020-1-1','China','Constant GDP',power=4)

cn=compare_economy(['China','USA'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)

cn=compare_economy(['China','Japan'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)


cn=compare_economy(['China','India'],'Constant GDP','2010-1-1','2020-1-1',twinx=True)

cn=compare_economy(['China','USA'],'Constant GDP Per Capita','2010-1-1','2020-1-1')

cn=compare_economy(['China','USA'],'Constant GDP Per Capita','2010-1-1','2020-1-1' ,twinx=True)

cn=compare_economy(['China','Japan'],'Constant GDP Per Capita','2010-1-1','2021-2-26',twinx=True)
cn=compare_economy(['China','Japan'],'Constant GDP Per Capita','2010-1-1','2021-2-26')
cn=economy_trend('2010-1-1','2020-1-1','China','Constant GDP Per Capita')
cn=economy_trend('2010-1-1','2020-1-1','Japan','Constant GDP Per Capita')
cn=economy_trend('2010-1-1','2020-1-1','USA','Constant GDP Per Capita')

cn=compare_economy(['China','India'],'Constant GDP Per Capita','2010-1-1','2020-1-1',twinx=True)

cn=compare_economy(['China','USA'],'GNP Ratio','1995-1-1','2010-1-1')

cn=compare_economy(['China','Japan'],'GNP Ratio','1995-1-1','2010-1-1')

cn=compare_economy(['USA','Japan'],'GNP Ratio','1995-1-1','2010-1-1')
cn2=compare_economy(['USA','Japan'],'GNP Ratio','1995-1-1','2010-12-31')




cn=compare_economy(['China','USA'],'GNP','1995-1-1','2020-1-1')
cn=compare_economy(['China','Japan'],'GNP','1995-1-1','2010-1-1')
cn=compare_economy(['USA','Japan'],'GNP','1995-1-1','2010-1-1')


df=pmi_china('2020-1-5','2020-10-1')

df=pmi_china('2019-1-5','2020-10-31')

