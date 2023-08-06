# -*- coding: utf-8 -*-
"""
本模块功能：中国行业板块市场
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年10月20日
最新修订日期：2020年10月21日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.bond_base import *
#==============================================================================

if __name__=='__main__':
    indicator="新浪行业"
    indicator="启明星行业"
    indicator="地域"
    indicator="行业"

def sector_list_china(indicator="新浪行业"):
    """
    功能：行业分类列表
    indicator="新浪行业","启明星行业","概念","地域","行业"
    来源网址：http://finance.sina.com.cn/stock/sl/#qmxindustry_1
    """
    #检查选项是否支持
    indicatorlist=["新浪行业","概念","地域","行业","启明星行业"]
    if indicator not in indicatorlist:
        print("#Error(sector_list_china): unsupported sectoring method",indicator)
        print("Supported sectoring methods:",indicatorlist)
        return None
    
    import akshare as ak
    try:
        df = ak.stock_sector_spot(indicator=indicator)
    except:
        print("#Error(sector_list_china): data source tentatively unavailable for",indicator)
        print("Possible reason: data source is self-updating.")
        print("Solution: have a breath of fresh air and try later.")
        return None
    
    sectorlist=list(df['板块'])
    #按照拼音排序
    sectorlist=list(set(list(sectorlist)))
    sectorlist=sort_pinyin(sectorlist)
    #解决拼音相同带来的bug：陕西省 vs 山西省
    if '陕西省' in sectorlist:
        pos=sectorlist.index('陕西省')
        if sectorlist[pos+1] == '陕西省':
            sectorlist[pos] = '山西省'
    if '山西省' in sectorlist:
        pos=sectorlist.index('山西省')
        if sectorlist[pos+1] == '山西省':
            sectorlist[pos+1] = '陕西省'
    listnum=len(sectorlist)
    
    if indicator != "行业":
        method=indicator
    else:
        method="证监会细分行业"
    print("\n===== 中国股票市场的行业/板块:",listnum,"\b个（按"+method+"划分） =====")

    if indicator in ["新浪行业","启明星行业","概念"]:
        #板块名字长度
        maxlen=0
        for s in sectorlist:        
            l=strlen(s)
            if l > maxlen: maxlen=l
        #每行打印板块名字个数
        rownum=int(80/(maxlen+2))
        
        for d in sectorlist:
            if strlen(d) < maxlen:
                dd=d+" "*(maxlen-strlen(d))
            else:
                dd=d
            print(dd,end='  ')
            pos=sectorlist.index(d)+1
            if (pos % rownum ==0) or (pos==listnum): print(' ')    

    if indicator in ["地域","行业"]:
        linemaxlen=60
        linelen=0
        for d in sectorlist:
            dlen=strlen(d)
            pos=sectorlist.index(d)+1
            #超过行长
            if (linelen+dlen) > linemaxlen:
                print(' '); linelen=0
            #是否最后一项
            if pos < listnum:
                print(d,end=', ')
            else:
                print(d+"。"); break
            linelen=linelen+dlen

    import datetime
    today = datetime.date.today()
    print("*** 信息来源：新浪财经,",today) 
    
    return df


#==============================================================================
if __name__=='__main__':
    sector_name="房地产"
    indicator="启明星行业"
    indicator="地域"
    indicator="行业"

def sector_code_china(sector_name):
    """
    功能：查找行业、板块名称对应的板块代码
    """
    import akshare as ak
    print("\n===== 查询行业/板块代码 =====")
    
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    sector_code=''; found=0
    for i in indicatorlist:
        dfi=ak.stock_sector_spot(indicator=i)
        try:
            sector_code=list(dfi[dfi['板块']==sector_name]['label'])[0]
            #记录找到的板块分类
            indicator=i
            #记录找到的板块概述
            dff=dfi[dfi['板块']==sector_name]
            
            if found > 0: print(" ")
            if indicator == "行业": indicator = "证监会行业"
            print("行业/板块名称："+sector_name)
            print("行业/板块代码："+sector_code,end='')
            print(", "+indicator+"分类")
            found=found+1
        except:
            continue
    #未找到板块代码
    if sector_name == '':
        print("#Error(sector_code_china): unsupported sector name",sector_name)
        return 
    
    return 

if __name__=='__main__':
    sector_name="房地产"
    df=sector_code_china(sector_name)
    df=sector_code_china("医药生物")
    df=sector_code_china("资本市场服务")
    
#==============================================================================
if __name__=='__main__':
    comp="xxx"
    comp="涨跌幅"
    comp="成交量"
    comp="平均价格"
    comp="公司家数"
    
    indicator="+++"
    indicator="新浪行业"
    indicator="启明星行业"
    indicator="地域"
    indicator="行业"
    num=10

def sector_rank_china(comp="涨跌幅",indicator="新浪行业",num=10):
    """
    功能：按照比较指标降序排列
    comp="涨跌幅",平均成交量（手），平均价格，公司家数
    indicator="新浪行业","启明星行业","概念","地域","行业"
    num：为正数时列出最高的前几名，为负数时列出最后几名
    """
    #检查选项是否支持
    #complist=["涨跌幅","成交量","平均价格","公司家数"]
    complist=["涨跌幅","平均价格","公司家数"]
    if comp not in complist:
        print("#Error(sector_rank_china): unsupported measurement",comp)
        print("Supported measurements:",complist)
        return None
    
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    if indicator not in indicatorlist:
        print("#Error(sector_list_china): unsupported sectoring method",indicator)
        print("Supported sectoring method:",indicatorlist)
        return None
    
    import akshare as ak
    try:
        df = ak.stock_sector_spot(indicator=indicator)  
    except:
        print("#Error(sector_rank_china): data source tentatively unavailable for",indicator)
        print("Possible reason: data source is self-updating.")
        print("Solution: have a breath of fresh air and try later.")
        return None
    
    df.dropna(inplace=True)
    #出现列名重名，强制修改列名
    df.columns=['label','板块','公司家数','平均价格','涨跌额','涨跌幅', \
                '总成交量(手)','总成交额(万元)','个股代码','个股涨跌幅','个股股价', \
                '个股涨跌额','个股名称']
    df['均价']=round(df['平均价格'].astype('float'),2)
    df['涨跌幅%']=round(df['涨跌幅'].astype('float'),2)
    #平均成交量:万手
    df['平均成交量']=(df['总成交量(手)'].astype('float')/df['公司家数'].astype('float')/10000)
    df['平均成交量']=round(df['平均成交量'],2)
    #平均成交额：亿元
    df['平均成交额']=(df['总成交额(万元)'].astype('float')/df['公司家数'].astype('float'))/10000
    df['平均成交额']=round(df['平均成交额'],2)
    stkcd=lambda x: x[2:]
    df['个股代码']=df['个股代码'].apply(stkcd)
    try:
        df['个股涨跌幅%']=round(df['个股涨跌幅'].astype('float'),2)
    except:
        pass
    try:
        df['个股股价']=round(df['个股股价'].astype('float'),2)
    except:
        pass
    try:
        df['公司家数']=df['公司家数'].astype('int')
    except:
        pass
    df2=df[['板块','涨跌幅%','平均成交量','平均成交额','均价', \
            '公司家数','label','个股名称','个股代码','个股涨跌幅','个股股价']].copy()
    df2=df2.rename(columns={'个股名称':'代表个股','label':'板块代码'})
    
    #删除无效的记录
    df2=df2.drop(df2[df2['均价'] == 0.0].index)
    
    if comp == "涨跌幅":
        df3=df2[['板块','涨跌幅%','均价','公司家数','板块代码','代表个股']]
        df3.sort_values(by=['涨跌幅%'],ascending=False,inplace=True)
    """
    if comp == "成交量":
        df3=df2[['板块','平均成交量','涨跌幅%','均价','公司家数','板块代码','代表个股']]
        df3.sort_values(by=['平均成交量'],ascending=False,inplace=True)
    """
    if comp == "平均价格":
        df3=df2[['板块','均价','涨跌幅%','公司家数','板块代码','代表个股']]
        df3.sort_values(by=['均价'],ascending=False,inplace=True)
    if comp == "公司家数":
        df3=df2[['板块','公司家数','均价','涨跌幅%','板块代码','代表个股']]
        df3.sort_values(by=['公司家数'],ascending=False,inplace=True)
    df3.reset_index(drop=True,inplace=True)
        
    #设置打印对齐
    import pandas as pd
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    if indicator == "行业":
        indtag="证监会行业"
    else:
        indtag=indicator
    
    #处理空记录
    if len(df3) == 0:
        print("#Error(sector_rank_china):data source tentatively unavailable for",comp,indicator)
        print("Possible reason: data source is self-updating.")
        print("Solution: have a breath of fresh air and try later.")
        return
    
    print("\n===== 中国股票市场：板块"+comp+"排行榜（按照"+indtag+"分类） =====")
    if num > 0:
        print(df3.head(num))
    else:
        print(df3.tail(-num))
    
    import datetime
    today = datetime.date.today()
    footnote1="*注：代表个股是指板块中涨幅最高或跌幅最低的股票"
    print(footnote1)
    print(" 板块数:",len(df),"\b, 数据来源：新浪财经,",today,"\b（信息为上个交易日）") 

    return df3

#==============================================================================
if __name__=='__main__':
    sector="new_dlhy"
    sector="xyz"
        
    num=10

def sector_detail_china(sector="new_dlhy",comp="涨跌幅",num=10):
    """
    功能：按照板块内部股票的比较指标降序排列
    sector：板块代码
    num：为正数时列出最高的前几名，为负数时列出最后几名
    """
    debug=False

    #检查选项是否支持
    complist=["涨跌幅","换手率","收盘价","市盈率","市净率","总市值","流通市值"]
    if comp not in complist:
        print("#Error(sector_detail_china): unsupported measurement",comp)
        print("Supported measurements:",complist)
        return None
    
    #检查板块代码是否存在
    import akshare as ak
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    sector_name=''
    for i in indicatorlist:
        dfi=ak.stock_sector_spot(indicator=i)
        if debug: print("i=",i)
        try:
            sector_name=list(dfi[dfi['label']==sector]['板块'])[0]
            #记录找到的板块分类
            indicator=i
            #记录找到的板块概述
            dff=dfi[dfi['label']==sector]
            break
        except:
            continue
    #未找到板块代码
    if sector_name == '':
        print("#Error(sector_detail_china): unsupported sector code",sector)
        return
    
    #板块成份股
    try:
        df = ak.stock_sector_detail(sector=sector)
    except:
        print("#Error(sector_rank_china): data source tentatively unavailable for",sector)
        print("Possible reason: data source is self-updating.")
        print("Solution: have a breath of fresh air and try later.")
        return None
    
    df.dropna(inplace=True)
    df['个股代码']=df['code']
    df['个股名称']=df['name']
    df['涨跌幅%']=round(df['changepercent'].astype('float'),2)
    df['收盘价']=round(df['settlement'].astype('float'),2)
    #成交量:万手
    df['成交量']=round(df['volume'].astype('float')/10000,2)
    #成交额：亿元
    df['成交额']=round(df['amount'].astype('float')/10000,2)
    df['市盈率']=round(df['per'].astype('float'),2)
    df['市净率']=round(df['pb'].astype('float'),2)
    #总市值：亿元
    df['总市值']=round(df['mktcap'].astype('float')/10000,2)
    #流通市值：亿元
    df['流通市值']=round(df['nmc'].astype('float')/10000,2)
    df['换手率%']=round(df['turnoverratio'].astype('float'),2)
    
    #删除无效的记录
    df=df.drop(df[df['收盘价'] == 0].index)
    df=df.drop(df[df['流通市值'] == 0].index)
    df=df.drop(df[df['总市值'] == 0].index)
    df=df.drop(df[df['市盈率'] == 0].index)
    
    df2=df[[ '个股代码','个股名称','涨跌幅%','收盘价','成交量','成交额', \
            '市盈率','市净率','换手率%','总市值','流通市值']].copy()
    
    if comp == "涨跌幅":
        df3=df2[['个股名称','个股代码','涨跌幅%','换手率%','收盘价','市盈率','市净率','流通市值']]
        df3.sort_values(by=['涨跌幅%'],ascending=False,inplace=True)
    if comp == "换手率":
        df3=df2[['个股名称','个股代码','换手率%','涨跌幅%','收盘价','市盈率','市净率','流通市值']]
        df3.sort_values(by=['换手率%'],ascending=False,inplace=True)
    if comp == "收盘价":
        df3=df2[['个股名称','个股代码','收盘价','换手率%','涨跌幅%','市盈率','市净率','流通市值']]
        df3.sort_values(by=['收盘价'],ascending=False,inplace=True)
    if comp == "市盈率":
        df3=df2[['个股名称','个股代码','市盈率','市净率','收盘价','换手率%','涨跌幅%','流通市值']]
        df3.sort_values(by=['市盈率'],ascending=False,inplace=True)
    if comp == "市净率":
        df3=df2[['个股名称','个股代码','市净率','市盈率','收盘价','换手率%','涨跌幅%','流通市值']]
        df3.sort_values(by=['市净率'],ascending=False,inplace=True)
    if comp == "流通市值":
        df3=df2[['个股名称','个股代码','流通市值','总市值','市净率','市盈率','收盘价','换手率%','涨跌幅%']]
        df3.sort_values(by=['流通市值'],ascending=False,inplace=True)
    if comp == "总市值":
        df3=df2[['个股名称','个股代码','总市值','流通市值','市净率','市盈率','收盘价','换手率%','涨跌幅%']]
        df3.sort_values(by=['总市值'],ascending=False,inplace=True)  
        
    df3.reset_index(drop=True,inplace=True)
        
    #设置打印对齐
    import pandas as pd
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    print("\n=== 中国股票市场："+sector_name+"板块，成份股排行榜（按照"+comp+"） ===")
    if num > 0:
        print(df3.head(num))
    else:
        print(df3.tail(-num))
    
    import datetime
    today = datetime.date.today()
    footnote1="*注：市值的单位是亿元人民币, "
    print(footnote1+"板块内成份股个数:",len(df))
    print(" 数据来源：新浪财经,",today,"\b（信息为上个交易日）") 

    return df2

#==============================================================================
if __name__=='__main__':
    ticker='600021'
    ticker='000661'
    ticker='999999'
    sector="new_dlhy"
    sector="yysw"
    sector="xyz"

def sector_position_china(ticker,sector="new_dlhy"):
    """
    功能：查找一只股票在板块内的百分数位置
    ticker：股票代码
    sector：板块代码
    """
    
    import akshare as ak
    import numpy as np
    import pandas as pd    
    
    #检查板块代码是否存在
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    sector_name=''
    for i in indicatorlist:
        dfi=ak.stock_sector_spot(indicator=i)
        try:
            sector_name=list(dfi[dfi['label']==sector]['板块'])[0]
            #记录找到的板块分类
            indicator=i
            #记录找到的板块概述
            dff=dfi[dfi['label']==sector]
            break
        except:
            continue
    #未找到板块代码
    if sector_name == '':
        print("#Error(sector_position_china): unsupported sector code",sector)
        return None
    
    #板块成份股
    try:
        #启明星行业分类没有成份股明细
        df = ak.stock_sector_detail(sector=sector)
    except:
        print("#Error(sector_position_china): sector detail not available for",sector,'by',indicator)
        print("Possible reason: data source is self-updating.")
        print("Solution: have a breath of fresh air and try later.")
        return None

    #清洗原始数据: #可能同时含有数值和字符串，强制转换成数值
    df['changepercent']=round(df['changepercent'].astype('float'),2)
    df['turnoverratio']=round(df['turnoverratio'].astype('float'),2)
    df['settlement']=round(df['settlement'].astype('float'),2)
    df['per']=round(df['per'].astype('float'),2)
    df['pb']=round(df['pb'].astype('float'),2)
    df['nmc']=round(df['nmc'].astype('int')/10000,2)
    df['mktcap']=round(df['mktcap'].astype('int')/10000,2)
    
    #检查股票代码是否存在
    sdf=df[df['code']==ticker]
    if len(sdf) == 0:
        print("#Error(sector_position_china): retrieving",ticker,"failed in sector",sector,sector_name)
        print("#Try later if network responses slowly.")
        return None       
    sname=list(sdf['name'])[0]
    
    #确定比较范围
    complist=['changepercent','turnoverratio','settlement','per','pb','nmc','mktcap']
    compnames=['涨跌幅%','换手率%','收盘价(元)','市盈率','市净率','流通市值(亿元)','总市值(亿元)']
    compdf=pd.DataFrame(columns=['指标名称','指标数值','板块百分位数%','板块中位数','板块最小值','板块最大值'])
    for c in complist:
        v=list(sdf[c])[0]
        vlist=list(set(list(df[c])))
        vlist.sort()
        vmin=round(min(vlist),2)
        vmax=round(max(vlist),2)
        vmedian=round(np.median(vlist),2)
        
        pos=vlist.index(v)
        pct=round((pos+1)/len(vlist)*100,2)
        
        s=pd.Series({'指标名称':compnames[complist.index(c)], \
                     '指标数值':v,'板块百分位数%':pct,'板块中位数':vmedian, \
                    '板块最小值':vmin,'板块最大值':vmax})
        compdf=compdf.append(s,ignore_index=True) 
        
    compdf.reset_index(drop=True,inplace=True)     

    print("\n======= 股票在所属行业/板块的位置分析 =======")
    print("股票: "+sname+" ("+ticker+")")
    print("所属行业/板块："+sector_name+" ("+sector+", "+indicator+"分类)")
    print("")
    
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    print(compdf.to_string(index=False))
    
    import datetime
    today = datetime.date.today()
    print("*板块内成份股个数:",len(df),"\b, 数据来源：新浪财经,",today,"\b（信息为上个交易日）")

    return df,compdf    
    

#==============================================================================

def invest_concept_china(num=10):
    """
    废弃！
    功能：汇总投资概念股票名单，排行
    来源网址：http://finance.sina.com.cn/stock/sl/#qmxindustry_1
    """
    print("\nWarning: This function might cause your IP address banned by data source!")
    print("Searching stocks with investment concepts in China, it may take long time ...")
    
    #找出投资概念列表
    import akshare as ak
    cdf = ak.stock_sector_spot(indicator="概念")
    cdf.sort_values(by=['label'],ascending=True,inplace=True)
    clist=list(cdf['label'])
    cnames=list(cdf['板块'])
    cnum=len(clist)
    
    import pandas as pd
    totaldf=pd.DataFrame()
    import time
    i=0
    #新浪财经有反爬虫，这个循环做不下去
    for c in clist:
        print("...Searching for conceptual sector",c,cnames[clist.index(c)],end='')
        try:
            sdf = ak.stock_sector_detail(c)
            sdf['板块']=cnames(clist.index(c))
            totaldf=pd.concat([totaldf,sdf],ignore_index=True)
            print(', found.')
        except:
            print(', failed:-(')
            #continue
                    #等待一会儿，避免被禁访问
        time.sleep(10)
        i=i+1
        if i % 20 == 0:
            print(int(i/cnum*100),'\b%',end=' ')
    print("...Searching completed.")
    
    if len(totaldf) == 0:
        print("#Error(sector_rank_china): data source tentatively banned your access:-(")
        print("Solutions:1) try an hour later, or 2) switch to another IP address.")
        return None
    
    #分组统计
    totaldfrank = totaldf.groupby('name')['板块','code'].count()
    totaldfrank.sort_values(by=['板块','code'],ascending=[False,True],inplace=True)
    totaldfrank['name']=totaldfrank.index
    totaldfrank.reset_index(drop=True,inplace=True)

    #更新每只股票持有的概念列表
    for i in totaldfrank.index:
        tdfsub=totaldf[totaldf['name']==totaldfrank.loc[i,"name"]]
        sectors=str(list(tdfsub['板块'])) 
        # 逐行修改列值
        totaldfrank.loc[i,"sectors"] = sectors

    #合成
    totaldf2=totaldf.drop('板块',axix=1)
    totaldf2.drop_duplicates(subset=['code'],keep='first',inplace=True)
    finaldf = pd.merge(totaldfrank,totaldf2,how='inner',on='name')
    
    return finaldf
    
    
#==============================================================================

    
    
    
    
    