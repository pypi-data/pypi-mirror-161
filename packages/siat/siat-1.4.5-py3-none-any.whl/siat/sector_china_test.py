# -*- coding: utf-8 -*-


import os; os.chdir("S:\siat")
from siat.sector_china import *

df=sector_position_china('000661',"gn_swym")

df=sector_position_china('000661',"new_swzz")
df=sector_position_china('000661',"hangye_ZC27")




df=sector_list_china("新浪行业")



#数据网址：http://finance.sina.com.cn/stock/sl/#qmxindustry_1

import akshare as ak

# 板块行情
stock_industry_sina_df = ak.stock_sector_spot(indicator="新浪行业")
sectorlist=list(stock_industry_sina_df['板块'])
    num=len(sectorlist)
    for d in sectorlist:
        print(d,end='  ')
        pos=sectorlist.index(d)+1
        if (pos % 6 ==0) or (pos==num): print(' ')




stock_industry_star_df = ak.stock_sector_spot(indicator="启明星行业")

stock_industry_concept_df = ak.stock_sector_spot(indicator="概念")

stock_industry_region_df = ak.stock_sector_spot(indicator="地域")

stock_industry_industry_df = ak.stock_sector_spot(indicator="行业")
hangye_list=list(set(list(stock_industry_industry_df['label'])))
hangye_list.sort()

#板块详情：nmc-流通市值？mktcap-总市值？
#"行业"
stock_sector_zl01_df = ak.stock_sector_detail(sector="hangye_ZL01")
len(stock_sector_zl01_df)

stock_sector_zc27_df = ak.stock_sector_detail(sector="hangye_ZC27")

#"概念"
stock_sector_kc50_df = ak.stock_sector_detail(sector="gn_kc50")

#"地域"
stock_sector_440000_df = ak.stock_sector_detail(sector="diyu_440000")

#"新浪行业"
stock_sector_dlhy_df = ak.stock_sector_detail(sector="new_dlhy")

#"启明星行业"：无详情



import os; os.chdir("E:/siat")
from siat.sector_china import *

df=sector_list_china(indicator="概念")
sector_code_china("重组概念")
sector_code_china("建筑工程")
sector_code_china("资产注入")
sector_code_china("建筑节能")
sector_code_china("建筑装饰和其他建筑业")
sector_code_china("建筑安装业")






df=sector_rank_china("涨跌幅","概念",80)
df[df['板块']=='重组概念']
df1=sector_detail_china(sector="gn_zzgn",comp="涨跌幅",num=10)
df1=sector_detail_china(sector="gn_zzgn",comp="涨跌幅",num=-10)


df=sector_list_china(indicator="新浪行业")
df=sector_list_china(indicator="启明星行业")
df=sector_list_china(indicator="行业")
df=sector_list_china(indicator="概念")
df=sector_list_china(indicator="地域")









sector_code_china("资本市场服务")
sector_code_china("房地产")

df=sector_rank_china("涨跌幅","新浪行业")
df=sector_rank_china("涨跌幅","新浪行业",-10)

#df=sector_rank_china("成交量","新浪行业")
df=sector_rank_china("平均价格","新浪行业")
df=sector_rank_china("公司家数","新浪行业")
df=sector_rank_china("公司家数","新浪行业",-10)

df=sector_rank_china("涨跌幅","地域")
df=sector_rank_china("涨跌幅","地域",-10)

#df=sector_rank_china("成交量","地域")
df=sector_rank_china("平均价格","地域")

df=sector_rank_china("涨跌幅","启明星行业")
df=sector_rank_china("涨跌幅","启明星行业",-10)

df=sector_rank_china("涨跌幅","行业")
df=sector_rank_china("涨跌幅","行业",10)

df=sector_rank_china("涨跌幅","概念",-10)
df=sector_rank_china("公司家数","概念",-10)

df=sector_detail_china(sector="new_dlhy",comp="涨跌幅",num=-10)
df=sector_detail_china(sector="new_dlhy",comp="换手率",num=10)
df=sector_detail_china(sector="new_dlhy",comp="收盘价",num=10)
df=sector_detail_china(sector="new_dlhy",comp="市盈率",num=10)
df=sector_detail_china(sector="new_dlhy",comp="市净率",num=10)
df=sector_detail_china(sector="new_dlhy",comp="流通市值",num=10)
df=sector_detail_china(sector="new_dlhy",comp="总市值",num=10)
df=sector_detail_china(sector="new_dlhy",comp="流通市值",num=-10)


df=sector_position_china('600021',"new_dlhy")
df=sector_position_china('000661',"yysw")

df=sector_position_china('000661',"gn_swym")


df=sector_position_china('002504',"jzgc")
df=sector_position_china('002504',"gn_zczr")
df=sector_position_china('002504',"gn_jzjn")
df=sector_position_china('002504',"hangye_ZE50")

import seaborn as sn


