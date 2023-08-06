# -*- coding: utf-8 -*-

import os; os.chdir("S:/siat")
from siat import *
#==================================================================
ff3_betas=reg_ff3_betas("8146.HK",'2020-1-1','2021-10-30','China')
ff3_betas=reg_ff3_betas("08146.HK",'2020-1-1','2021-10-30','China')
ff3_betas=reg_ff3_betas("0886.HK",'2020-1-1','2021-10-30','China')



from siat.fama_french import *
#==================================================================
ff3=get_ff_factors('2016-1-1','2020-12-31','Europe','FF3','yearly')
mom=get_ff_factors('2016-1-1','2020-12-31','Europe','Mom','yearly')

get_ffc4_factors('2016-1-1','2020-1-1','Europe','yearly')
get_ffc4_factors('2016-1-1','2021-12-31','Europe','yearly')

get_ffc4_factors('2016-1-1','2021-12-31','Japan','yearly')
get_ffc4_factors('2016-1-1','2021-12-31','China','yearly')
get_ffc4_factors('2016-1-1','2021-12-31','Global','yearly')
get_ffc4_factors('2016-1-1','2021-12-31','Global_ex_US','yearly')
get_ffc4_factors('2016-1-1','2021-12-31','North_America','yearly')
#==================================================================
get_ffc4_factors('2021-9-25','2021-9-30','US','daily')
get_ffc4_factors('2021-4-1','2021-9-30','US','monthly')
get_ffc4_factors('2016-1-1','2021-12-31','US','yearly')
#==================================================================
get_ffc4_factors('2021-8-25','2021-8-31','Japan','daily')
ff3=get_ff_factors('2021-8-25','2021-8-31','Japan','FF3','daily')
Mom=get_ff_factors('2021-8-25','2021-8-31','Japan','Mom','daily')

get_ffc4_factors('2021-4-1','2021-9-30','Japan','monthly')
ff3=get_ff_factors('2021-4-1','2021-9-30','Japan','FF3','monthly')
ff3
Mom=get_ff_factors('2021-4-1','2021-9-30','Japan','Mom','monthly')
Mom
#==================================================================
get_ffc4_factors('2021-8-25','2021-8-31','Japan','daily')
get_ffc4_factors('2021-4-1','2021-9-30','Japan','monthly')
get_ffc4_factors('2016-1-1','2021-12-31','Japan','yearly')
#==================================================================
get_ffc4_factors('2021-8-25','2021-8-31','Europe','daily')
get_ffc4_factors('2021-4-1','2021-9-30','Europe','monthly')
get_ffc4_factors('2016-1-1','2021-12-31','Europe','yearly')
#==================================================================
get_ffc4_factors('2021-8-25','2021-8-31','China','daily')
get_ffc4_factors('2021-4-1','2021-9-30','China','monthly')
get_ffc4_factors('2016-1-1','2021-12-31','China','yearly')
#==================================================================
get_ffc4_factors('2018-8-25','2018-8-31','Global','daily')
get_ffc4_factors('2018-4-1','2018-9-30','Global','monthly')
get_ffc4_factors('2014-1-1','2021-12-31','Global','yearly')
#==================================================================



#==================================================================
ff3_betas=reg_ff3_betas('AAPL','2018-1-1','2019-4-30','US')
ff3_betas=reg_ff3_betas('BILI','2018-1-1','2019-4-30','US')

ff3_betas=reg_ff3_betas('BMW.DE','2018-1-1','2019-4-30','Europe')
ff3_betas=reg_ff3_betas('AEM','2018-3-1','2019-8-31','US')

reg_ffc4_betas('JD','2018-1-1','2019-4-30','US')
reg_ffc4_betas('BABA','2018-1-1','2019-4-30','US')
reg_ffc4_betas('MSFT','2018-1-1','2019-4-30','US')
reg_ffc4_betas('TAL','2018-1-1','2019-4-30','US')

get_ff5_factors('2019-5-20','2019-5-31','US','daily')
get_ff5_factors('2018-1-1','2019-4-30','US','monthly')

reg_ff5_betas('PTR','2018-1-1','2019-4-30','US')
reg_ff5_betas('QCOM','2018-1-1','2019-4-30','US')


    try:
        factor_df=ds[seq]
    except:
        extract_DESCR(ds)
        
        
def extract_DESCR(ds):
    """
    归纳：从字典的DESCR中提取年度因子信息 ，用于seq缺失1但误放置在DESCR中的情形
    """        
    descr_str=factor_df=ds['DESCR']
    wml_pos=descr_str.find("WML")
    nn_pos=descr_str.find("\n\n ")
    wml_post=descr_str[wml_pos+4:nn_pos]
    wml_post1=wml_post.replace('  ,',',')
    wml_post2=wml_post1.replace(' ,',',')
    wml_post3=wml_post2+' '
    
    #正则表达式提取配对
    import re
    wml_post_list=re.findall(r"(.+?),(.+?) ", wml_post3)    
    
    import pandas as pd
    df = pd.DataFrame(columns=('Date', 'Mom'))
    for i in wml_post_list:
        #print(i[0],i[1])
        s = pd.Series({'Date':i[0], 'Mom':float(i[1])})
        # 这里 Series 必须是 dict-like 类型
        df = df.append(s, ignore_index=True)
        # 这里必须选择ignore_index=True 或者给 Series一个index值    
    df.set_index('Date',drop=True, inplace=True)
    
    return df
    
    
    
    
    