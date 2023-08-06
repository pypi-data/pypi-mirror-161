# -*- coding: utf-8 -*-

"""
本模块功能：计算财务报表指标，基于东方财富
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2022年5月18日
最新修订日期：2022年5月18日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#本模块的公共引用
from siat.financials_china import *
#==============================================================================
import pandas as pd
import akshare as ak

#==============================================================================
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    
    df=get_fin_stmt_ak_multi(tickers,fsdates)         
    
def get_fin_stmt_ak_multi(tickers,fsdates):
    """
    功能：获得多个股票的全部财报，基于akshare，合成，排序：股票代码+财报日期降序
    选择：仅保留fsdates日期的数据。注意：fsdates要比预计的多一项，以便计算期初数
    """
 
    #循环获取全部股票的财报，并合成
    df=pd.DataFrame()
    for t in tickers:
        dft=get_fin_stmt_ak(t)
        #按日期升序
        dft.sort_index(ascending=True,inplace=True)
        #选择指定的日期
        dfs=dft[dft['endDate'].isin(fsdates)]
        
        #列改名
        dfs.rename(columns={'所有者权益(或股东权益)合计':'所有者权益合计',
                            '一、营业总收入':'营业总收入',
                            '加:营业外收入':'营业外收入',
                            '二、营业总成本':'营业总成本',
                            '三、营业利润':'营业利润',
                            '四、利润总额':'利润总额',
                            '归属于母公司所有者的净利润':'归母净利润',
                            '减：所得税费用':'所得税费用',    
                            '处置固定资产、无形资产和其他长期资产的损失':'资产处置损失',
                            '减：营业外支出':'营业外支出',
                            
                            '经营活动产生现金流量净额':'经营活动现金流净额',
                            '经营活动现金流入小计':'经营活动现金流入',
                            '经营活动现金流出小计':'经营活动现金流出',
                            '投资活动产生的现金流量净额':'投资活动现金流净额',
                            '投资活动现金流入小计':'投资活动现金流入',
                            '投资活动现金流出小计':'投资活动现金流出',
                            '筹资活动产生的现金流量净额':'筹资活动现金流净额',
                            '筹资活动现金流入小计':'筹资活动现金流入',
                            '筹资活动现金流出小计':'筹资活动现金流出',
                            '四、汇率变动对现金及现金等价物的影响':'汇率对现金流的影响',
                            '现金及现金等价物的净增加额':'现金流量净增加额',
                            '基本每股收益(元/股)':'基本每股收益',
                            '稀释每股收益(元/股)':'稀释每股收益',
                            
                                },inplace=True)
        
        #计算指标
        dfs['应收账款占比%']=round(dfs['应收账款']/dfs['资产总计']*100,2)
        dfs['存货占比%']=round(dfs['存货']/dfs['资产总计']*100,2)
        dfs['流动比率%']=round(dfs['流动资产合计']/dfs['流动负债合计']*100,2)
        dfs['速动资产合计']=dfs['流动资产合计']-dfs['存货']
        dfs['速动比率%']=round(dfs['速动资产合计']/dfs['流动负债合计']*100,2)
        dfs['资产负债率%']=round(dfs['负债合计']/dfs['资产总计']*100,2)

        dfs['毛利润']=dfs['营业总收入']-dfs['营业成本']
        dfs['毛利润率%']=round(dfs['毛利润']/dfs['营业总收入']*100,2)
        dfs['营业利润率%']=round(dfs['营业利润']/dfs['营业总收入']*100,2)
        dfs['销售费用率%']=round(dfs['销售费用']/dfs['营业总收入']*100,2)
        dfs['管理费用率%']=round(dfs['管理费用']/dfs['营业总收入']*100,2)
        dfs['研发费用率%']=round(dfs['研发费用']/dfs['营业总收入']*100,2)
        dfs['营业外收支']=dfs['营业外收入']-dfs['营业外支出']
        dfs['税前利润']=dfs['利润总额']
        dfs['税前利润率%']=round(dfs['利润总额']/dfs['营业总收入']*100,2)
        dfs['实际所得税率%']=round(dfs['所得税费用']/dfs['利润总额']*100,2)
        dfs['净利润率%']=round(dfs['净利润']/dfs['营业总收入']*100,2)
        
        dfs['流通股股数']=round(dfs['净利润']/dfs['基本每股收益'],0)
        dfs['短期现金偿债能力%']=round(dfs['经营活动现金流净额']/dfs['流动负债合计']*100,2)
        dfs['长期现金偿债能力%']=round(dfs['经营活动现金流净额']/dfs['负债合计']*100,2)
        dfs['现金支付股利能力(元)']=round(dfs['经营活动现金流净额']/dfs['流通股股数'],2)
        dfs['现金综合支付能力%']=round(dfs['经营活动现金流净额']/dfs['所有者权益合计']*100,2)
        dfs['销售现金比率%']=round(dfs['经营活动现金流入']/dfs['营业总收入']*100,2)
        dfs['盈利现金比率%']=round(dfs['经营活动现金流净额']/dfs['净利润'],2)
        dfs['资产现金回收率%']=round(dfs['经营活动现金流净额']/dfs['资产总计']*100,2)
        dfs['现金流入流出比率%']=round(dfs['经营活动现金流入']/dfs['经营活动现金流出']*100,2)
        
        dfs['现金购销比率%']=round(dfs['购买商品、接受劳务支付的现金']/dfs['销售商品、提供劳务收到的现金']*100,2)
        dfs['营业现金回笼率%']=round(dfs['销售商品、提供劳务收到的现金']/dfs['营业总收入']*100,2)
        dfs['支付给职工的现金比率%']=round(dfs['支付给职工以及为职工支付的现金']/dfs['销售商品、提供劳务收到的现金']*100,2)
        
        #获取字段列表,增加期初项目
        col_list=list(dfs)
        for c in col_list:
            #print(c)
            dfs[c+"_期初"]=dfs[c].shift(1)
        #给字段排序，便于检查对比
        col_list_qc=list(dfs)
        col_list2=sorted(col_list_qc)
        dfs2=dfs[col_list2]
        
        #合成
        df=df.append(dfs2)

    #删除空值行
    df.dropna(inplace=True)
    
    #删除多余的列，修改列名
    del df['ticker_期初']
    df.rename(columns={'endDate_期初':'endDate_上期'},inplace=True)
    
    #标注股票简称,去掉其中的(A股)字样
    df["股票简称"]=df['ticker'].apply(lambda x: codetranslate(x).replace("(A股)",''))

    return df

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdate='2021-12-31'
    item="货币资金"
    
    select_item(df,ticker,fsdate,item)
    
def select_item(df,ticker,fsdate,item):
    """
    功能：根据股票代码、财报日期和科目(含期初)查询金额；若全为零则提示
    """
    
    col_list=['ticker',"股票简称",'endDate',"endDate_上期",item,item+"_期初"]
    dfs=df[(df['ticker']==ticker) & (df['endDate']==fsdate)][col_list]
    
    try:
        item_value=dfs[item].values[0]
        item_value_qc=dfs[item+"_期初"].values[0]
    except:
        print("  #Warning(select_item):",ticker+"的"+item+"未找到")
        nann=float("nan")
        return nann,nann,nann
    
    #全为零提示
    if (item_value==0) & (item_value_qc==0):
        print("  #Warning(select_item):",ticker+"的"+item+"及其期初数均为零")
    
    return item_value,item_value_qc,dfs
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    itemword1="固定资产"
    itemword1="资产"
    itemword2="计"
    
    dfs=find_fs_items(df,itemword1,itemword2)

def find_fs_items(df,itemword1,itemword2='',printout=True):
    """
    功能：搜索财务报表中含有关键词itemword的项目，并判断这些项目是否整列全为零
    """
    
    col_list=list(df)
    col_yes=[]
    for c in col_list:
        if (itemword1 in c) & (itemword2 in c):
            col_yes=col_yes+[c]
    
    dfs=pd.DataFrame(columns=['报表项目','是否全为零'])
    for cy in col_yes:
        allzero=(df[cy].std()==0)

        row=pd.Series({'报表项目':cy,'是否全为零':allzero})
        dfs=dfs.append(row,ignore_index=True)  
        
    if printout:
        #设置打印对齐
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)    
        
        #无序号打印
        print('')
        print(dfs.to_string(index=False))
    
    return dfs
    
#==============================================================================
if __name__=='__main__':
    title_txt="===== 重要指标的同行业对比 ====="

def title_position_original(title_txt,dfp):
    """
    废弃
    功能：对dfp直接打印时计算让标题居中的位置，通过寻找各个回车符的位置。
    """
    
    #各个记录的长度
    cuan=dfp.to_string(index=False)
    pos_prev=0
    pos=cuan.find('\n')
    rowlen=pos
    while pos != -1:
        pos_prev=pos
        pos=cuan.find('\n',pos_prev+1)
        rowlen_new=pos - pos_prev
        if rowlen_new > rowlen:
            rowlen=rowlen_new
    
    #抬头的长度
    collist=list(dfp)
    collen=0
    for c in collist:
        collen=collen+len(c)
    collen=collen+(len(collist)-1)*2
    if collen > rowlen:
        rowlen=collen
    
    blanknum=int((rowlen - len(title_txt))/2)    

    return blanknum-4
#==============================================================================
if __name__=='__main__':
    title_txt="===== 重要指标的同行业对比 ====="

def title_position(title_txt,dfp):
    """
    功能：对dfp直接打印时计算让标题居中的位置，通过寻找各个回车符的位置。
    """
    
    #各个记录的长度
    cuan=dfp.to_string(index=False)+'\n'
    pos=0
    rowlen=0
    while pos != -1:
        pos_new=cuan.find('\n',pos+1)
        sub_cuan=cuan[pos+1:pos_new]
        rowlen_new=hzlen(sub_cuan)
        #print(pos,pos_new,rowlen_new,sub_cuan)
        
        if rowlen_new > rowlen:
            rowlen=rowlen_new
        pos=pos_new
    
    title_len=hzlen(title_txt)+2
    blanknum=int((rowlen - title_len)/2)    

    return blanknum

if __name__=='__main__':
    title_txt="===== 重要指标的同行业对比 ====="
    blanknum=title_position(title_txt,dfp)
    
    print(' '*blanknum,title_txt) 
    print(dfp.to_string(index=False))

#==============================================================================
if __name__=='__main__':
    title_txt="万科A财报：重要指标的同行业对比\n（财报截止日期：2021-12-31）"
    footnote="*数据来源：新浪财经，2022年5月23日\n**股票列表第一项为分析对象\n*日期列表第一项为分析日期"
    title_break=False
    foot_break=True
    foot_center=False
    foot_start=4

def df_directprint(dfp,title_txt,footnote,title_break=True,foot_break=True,foot_center=True,foot_start=4):
    """
    功能：对dfp直接打印，让标题居中，让脚注居中或指定开始位置。
    """
    print('')
    
    #解析标题各行并居中打印
    title_txt1=title_txt+'\n'
    pos,pos_new=0,0
    while pos_new != -1:
        pos_new=title_txt1.find('\n',pos)
        linetxt=title_txt1[pos:pos_new]
        #print(linetxt)
        
        blanknum=title_position(linetxt,dfp)
        
        if linetxt != '\n':
            print(' '*blanknum,linetxt) 
            
        pos=pos_new+1
    
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)  

    #打印数据框本身    
    print(dfp.to_string(index=False))
        
    #解析标题各行并打印
    if foot_break: print('')
    footnote1=footnote+'\n'
    pos,pos_new=0,0
    while pos_new != -1:
        pos_new=footnote1.find('\n',pos)
        linetxt=footnote1[pos:pos_new]
        #print(linetxt)
        if foot_center:
            blanknum=title_position(linetxt,dfp)
        else:
            blanknum=foot_start-1
        
        if linetxt != '\n':
            if blanknum >2:
                print(' '*blanknum,linetxt) 
            else:
                print(linetxt)
            
        pos=pos_new+1

    return 

if __name__=='__main__':
    title_txt="===== 重要指标的同行业对比 ====="
#==============================================================================

if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdate='2021-12-31'
    items=["货币资金","应收票据","应收账款"]
    dfp=fs_item_analysis_1(df,ticker,fsdate,items)

def fs_item_analysis_1(df,ticker,fsdate,items):
    """
    功能：比较给定财报日期的资产项目、期初数、期末数、变动额和变动幅度%
    """
    
    #循环获取科目
    dfp=pd.DataFrame(columns=['报表项目','期初数', '期末数', '变动额', '变动幅度%'])
    yiyuan=100000000
    
    import math
    for i in items:
        i_value,i_value_qc,dft=select_item(df,ticker,fsdate,i)
        
        if not(i_value != 0 or i_value_qc != 0): 
            print("  #Warning(income_cost_analysis_1): skip zero item",i)
            continue
        
        if not math.isnan(i_value):
            i_value_yy=round(i_value/yiyuan,2)
            i_value_qc_yy=round(i_value_qc/yiyuan,2)
            i_value_chg_yy=i_value_yy - i_value_qc_yy
            if not(i_value_qc_yy==0):
                i_value_chg_pct=round(i_value_chg_yy/i_value_qc_yy*100,2)
            #对于变动幅度符号的修正
                if (i_value_chg_pct < 0) and (i_value_qc_yy < 0):
                    i_value_chg_pct=abs(i_value_chg_pct)
            else:
                i_value_chg_pct='-'
        else:
            i_value_qc_yy,i_value_yy,i_value_chg_yy,i_value_chg_pct='-','-','-','-'
        
        row=pd.Series({'报表项目':i,'期初数':i_value_qc_yy, \
                       '期末数':i_value_yy, '变动额':i_value_chg_yy, \
                       '变动幅度%':i_value_chg_pct})
        dfp=dfp.append(row,ignore_index=True)  
        
    
    #无序号打印
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：重要项目的变动情况\n（截至"+fsdate+"）"
    import datetime; today=datetime.date.today()
    footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
    df_directprint(dfp,title_txt,footnote)
    
    return dfp


#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    items=["应收账款","资产总计"]
    find_fs_items(df,itemword1="应收账款",itemword2='')
    find_fs_items(df,itemword1="资产",itemword2='计')
    
    dfp=fs_item_analysis_2(df,ticker,fsdates,items)

def fs_item_analysis_2(df,ticker,fsdates,items):
    """
    功能：比较给定财报日期的报表项目、最近几年fsdates、占比%
    """
    fsdates1=sorted(fsdates,reverse=True)
    
    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates1
    dfp=pd.DataFrame(columns=col_list)
    
    yiyuan=100000000
    import math
    
    for i in items:
        row_list=[i]
        for fd in fsdates1:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,2)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=[items[0]+"占比%"]
    for fd in fsdates1:
        rate=round(dfp[fd][0]/dfp[fd][1]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
        
    #无序号打印
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：重要项目占比的变动趋势"
    import datetime; today=datetime.date.today()
    footnote="*数据来源：新浪财经，"+str(today) 
    df_directprint(dfp,title_txt,footnote)    
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    
    dfp=fs_item_analysis_3(df,ticker,fsdates)

def fs_item_analysis_3(df,ticker,fsdates):
    """
    功能：比较给定财报日期的流动比率、最近几年fsdates
    """
    fsdates1=sorted(fsdates,reverse=True)
    
    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000

    items=['流动资产合计','流动负债合计']    
    for i in items:
        row_list=[i]
        for fd in fsdates1:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,2)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["流动比率%"]
    for fd in fsdates1:
        rate=round(dfp[fd][0]/dfp[fd][1]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
        
    #无序号打印
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：流动比率的变动趋势"
    import datetime; today=datetime.date.today()
    footnote="*数据来源：新浪财经，"+str(today) 
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    
    dfp=fs_item_analysis_4(df,ticker,fsdates)

def fs_item_analysis_4(df,ticker,fsdates):
    """
    功能：比较给定财报日期的流动比率、最近几年fsdates
    """
    fsdates1=sorted(fsdates,reverse=True)

    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    
    i='流动资产合计'
    row_list=[i]
    for fd in fsdates1:
        i_value,_,_=select_item(df,ticker,fd,i)
        row_list=row_list+[round(i_value/yiyuan,2)]
    dfp.loc[len(dfp)] = row_list
    
    i='存货'
    row_list=['其中：'+i]
    for fd in fsdates1:
        i_value,_,_=select_item(df,ticker,fd,i)
        row_list=row_list+[round(i_value/yiyuan,2)]
    dfp.loc[len(dfp)] = row_list 
    
    i='速动资产合计'
    row_list=[i]
    for fd in fsdates1:
        rate=round(dfp[fd][0]-dfp[fd][1],2)
        row_list=row_list+[rate]
    dfp.loc[len(dfp)] = row_list
    
    i='流动负债合计'
    row_list=[i]
    for fd in fsdates1:
        i_value,_,_=select_item(df,ticker,fd,i)
        row_list=row_list+[round(i_value/yiyuan,2)]
    dfp.loc[len(dfp)] = row_list
    
    last_row=["速动比率%"]
    for fd in fsdates1:
        rate=round(dfp[fd][2]/dfp[fd][3]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
    
    #无序号打印
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：速动比率的变动趋势"
    import datetime; today=datetime.date.today()
    footnote="*数据来源：新浪财经，"+str(today) 
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    
    dfp=fs_item_analysis_5(df,ticker,fsdates)

def fs_item_analysis_5(df,ticker,fsdates):
    """
    功能：比较给定财报日期的流动比率、最近几年fsdates
    """
    
    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    
    fsdates1=sorted(fsdates,reverse=True)
    items=['资产总计','负债合计']    
    for i in items:
        row_list=[i]
        for fd in fsdates1:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,2)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["资产负债率%"]
    for fd in fsdates1:
        rate=round(dfp[fd][1]/dfp[fd][0]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
    
    #无序号打印
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：资产负债率的变动趋势"
    import datetime; today=datetime.date.today()
    footnote="*数据来源：新浪财经，"+str(today) 
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31']
    items=['应收账款','营业收入']
    
    dfp=fs_item_analysis_6(df,ticker,fsdates,items)

def fs_item_analysis_6_original(df,ticker,fsdates,items):
    """
    废弃
    功能：比较给定财报日期的应收账款与营业收入增幅、最近几年fsdates
    """
    
    #循环获取科目
    items1=[]
    for i in items:
        items1=items1+[i+'(亿元)']
    
    col_list=['报表日期']+items1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    
    fsdates1=sorted(fsdates,reverse=False)
    for fd in fsdates1:
        row_list=[fd]
        for i in items:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,2)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["增幅%"]
    for i in items1:
        rate=round((dfp[i][1]/dfp[i][0]-1)*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
    
    #无序号打印
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：重要关联项目的增幅对比"
    import datetime; today=datetime.date.today()
    footnote="*数据来源：新浪财经，"+str(today) 
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31']
    items=['应收账款','营业收入']
    
    dfp=fs_item_analysis_6(df,ticker,fsdates,items)

def fs_item_analysis_6(df,ticker,fsdates,items):
    """
    功能：比较给定财报日期的应收账款与营业收入增幅、最近几年fsdates
    """
    
    col_list=['报表日期']+items
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    fsdates1=sorted(fsdates,reverse=False)
    for fd in fsdates1:
        row_list=[fd]
        for i in items:
            i_value,_,_=select_item(df,ticker,fd,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,2)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["增幅%"]
    for i in items:
        rate=round((dfp[i][1]/dfp[i][0]-1)*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
    
    #无序号打印
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：重要关联项目的增幅对比"
    import datetime; today=datetime.date.today()
    if yiyuan_foot:
        footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
    else:
        footnote="*数据来源：新浪财经，"+str(today)
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdate='2021-12-31'
    items=['存货','资产总计','存货占比%']
    
    dfp=fs_item_analysis_7(df,tickers,fsdate,items)

def fs_item_analysis_7_original(df,tickers,fsdate,items):
    """
    废弃
    功能：比较给定财报日期fsdate的项目和指标，与同业相比
    """
    
    #循环获取科目
    items1=[]
    for i in items:
        if not('%' in i):
            items1=items1+[i+'(亿元)']
        else:
            items1=items1+[i]
    
    col_list=['上市公司']+items1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    for t in tickers:
        tname=codetranslate(t).replace("(A股)",'')
        row_list=[tname]
        for i in items:
            i_value,_,_=select_item(df,t,fsdate,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,2)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list
    
    #无序号打印
    title_txt="=== 重要指标的同行业对比 ==="
    ticker=tickers[0]
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：重要指标的同行业对比\n（截至"+fsdate+"）"
    import datetime; today=datetime.date.today()
    if yiyuan_foot:
        footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
    else:
        footnote="*数据来源：新浪财经，"+str(today)
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdate='2021-12-31'
    items=['存货','资产总计','存货占比%']
    
    dfp=fs_item_analysis_7(df,tickers,fsdate,items)

def fs_item_analysis_7(df,tickers,fsdate,items):
    """
    功能：比较给定财报日期fsdate的项目和指标，与同业相比
    """
    
    col_list=['上市公司']+items
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    for t in tickers:
        tname=codetranslate(t).replace("(A股)",'')
        row_list=[tname]
        for i in items:
            i_value,_,_=select_item(df,t,fsdate,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,2)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list
    
    #无序号打印
    title_txt="=== 重要指标的同行业对比 ==="
    ticker=tickers[0]
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：重要指标的同行业对比\n（截至"+fsdate+"）"
    import datetime; today=datetime.date.today()
    if yiyuan_foot:
        footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
    else:
        footnote="*数据来源：新浪财经，"+str(today)
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdate='2021-12-31'
    items=['资产总计','资产负债率%','流动比率%','速动比率%']    
    dfp=fs_item_analysis_8(df,tickers,fsdate,items)

def fs_item_analysis_8(df,tickers,fsdate,items):
    """
    功能：比较给定财报日期fsdate的项目和指标，与同业相比
    区别：项目不带‘(亿元)’字样，避免行过长
    """
    
    #循环获取科目
    col_list=['上市公司']+items
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    for t in tickers:
        tname=codetranslate(t).replace("(A股)",'')
        row_list=[tname]
        for i in items:
            i_value,_,_=select_item(df,t,fsdate,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,2)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list
    
    #无序号打印
    ticker=tickers[0]
    ticker_name=codetranslate(ticker).replace("(A股)",'')
    title_txt=ticker_name+"财报分析：重要指标的同行业对比\n（截至"+fsdate+"）"

    import datetime; today=datetime.date.today()
    if yiyuan_foot:
        footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
    else:
        footnote="*数据来源：新浪财经，"+str(today)
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    asset_liab_structure_china(tickers,fsdates)
    
def asset_liab_structure_china(tickers,fsdates):
    """
    功能：分析上市公司的资产负债基本结构，并与同业公司对比。
    注意1：分析近三期情况，fsdates要给出四个报表日期，以便获得期初数。
    注意2：可以分析连续的年报或季报，但不能混个年报和季报。
    注意3：tickers中的第一家公司为主要分析对象。
    注意4：fsdates中的日期要降序排列，第一个日期建议为最近的财报日。
    """  
    #主要分析对象
    ticker=tickers[0]
    #最近的财报日
    fsdates=sorted(fsdates,reverse=True)
    fsdate=fsdates[0]
    
    #获取所有比较公司tickers的所有财报fsdates
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    #资产变动趋势1："货币资金","应收票据","应收账款"
    items1=["货币资金","应收票据","应收账款"]
    dfp1=fs_item_analysis_1(df,ticker,fsdate,items1)
    
    #资产变动趋势2
    items2=["货币资金","应收账款","存货","长期股权投资","固定资产净额","资产总计"]
    dfp2=fs_item_analysis_1(df,ticker,fsdate,items2)
    
    #负债变动趋势
    items3=["短期借款","长期借款","应付账款","预收款项","应交税费","应付职工薪酬","负债合计"]
    dfp3=fs_item_analysis_1(df,ticker,fsdate,items3)
    
    #所有者权益变动趋势
    items4=["实收资本(或股本)","资本公积","盈余公积","未分配利润","所有者权益合计"]
    dfp4=fs_item_analysis_1(df,ticker,fsdate,items4)
    
    #应收账款占比变动分析
    fsdates1=fsdates[:3]
    items5=["应收账款","资产总计"]
    dfp5=fs_item_analysis_2(df,ticker,fsdates1,items5)

    #应收与营业收入增幅对比    
    fsdates2=fsdates[:2]
    items6=['应收账款',"应收票据",'营业总收入']
    dfp6=fs_item_analysis_6(df,ticker,fsdates2,items6)

    #应收账款占比同行对比
    items7=['应收账款','资产总计','应收账款占比%']
    dfp7=fs_item_analysis_7(df,tickers,fsdate,items7)        

    #存货占比变动分析
    items8=["存货","资产总计"]
    dfp8=fs_item_analysis_2(df,ticker,fsdates1,items8)
    """
    items9=["存货","营业总收入"]
    dfp9=fs_item_analysis_6(df,ticker,fsdates2,items9)
    """
    #存货与营业收入增幅对比分析            
    items10=['存货','流动资产合计',"速动资产合计","资产总计"]
    dfp10=fs_item_analysis_6(df,ticker,fsdates2,items10)

    #存货占比与行业对比        
    items11=['存货','资产总计','存货占比%']
    dfp11=fs_item_analysis_7(df,tickers,fsdate,items11)

    #流动比率变动分析
    dfp12=fs_item_analysis_3(df,ticker,fsdates1)    

    #速动比率变动分析
    dfp13=fs_item_analysis_4(df,ticker,fsdates1)    

    #资产负债率变动分析
    dfp14=fs_item_analysis_5(df,ticker,fsdates1)    

    #资产负债率同行比较
    items15=['资产总计','资产负债率%','流动比率%','速动比率%']
    dfp15=fs_item_analysis_8(df,tickers,fsdate,items15)

    return    
    
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    income_cost_structure_china(tickers,fsdates)
    
def income_cost_structure_china(tickers,fsdates):
    """
    功能：分析上市公司的收入成本基本结构，并与同业公司对比。
    注意1：分析近三期情况，fsdates要给出四个报表日期，以便获得期初数。
    注意2：可以分析连续的年报或季报，但不能混个年报和季报。
    注意3：tickers中的第一家公司为主要分析对象。
    注意4：fsdates中的日期要降序排列，第一个日期建议为最近的财报日。
    """  
    #主要分析对象
    ticker=tickers[0]
    #最近的财报日
    fsdates=sorted(fsdates,reverse=True)
    fsdate=fsdates[0]
    
    #获取所有比较公司tickers的所有财报fsdates
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    #收入成本总体变动趋势
    items1=["营业总收入","营业总成本","营业成本","毛利润","营业利润","营业外收支","税前利润","所得税费用","净利润","归母净利润"]
    dfp1=fs_item_analysis_1(df,ticker,fsdate,items1)
    
    #成本变动趋势
    print('')
    items2=["营业总成本","营业成本","营业税金及附加","销售费用","管理费用","研发费用",
            "应付利息","公允价值变动损失","资产处置损失",
            "资产减值损失","营业外支出"]
    dfp2=fs_item_analysis_1(df,ticker,'2021-12-31',items2)
    
    #占比变动分析：近三年
    fsdates1=fsdates[:3]
    items3=["营业总成本","营业总收入"]
    dfp3=fs_item_analysis_2(df,ticker,fsdates1,items3)
    #====================================================================
    items4=["营业成本","营业总成本"]
    dfp4=fs_item_analysis_2(df,ticker,fsdates1,items4)
    
    items5=["营业成本","营业总收入"]
    dfp5=fs_item_analysis_2(df,ticker,fsdates1,items5)
    #====================================================================
    items6=["销售费用","营业总收入"]
    dfp6=fs_item_analysis_2(df,ticker,fsdates1,items6)
    #====================================================================
    items7=["管理费用","营业总收入"]
    dfp7=fs_item_analysis_2(df,ticker,fsdates1,items7)
    #====================================================================
    items8=["毛利润","营业总收入"]
    dfp8=fs_item_analysis_2(df,ticker,fsdates1,items8)
    #====================================================================
    items9=["营业利润","营业总收入"]
    dfp8=fs_item_analysis_2(df,ticker,fsdates1,items9)
    #====================================================================
    items10=["税前利润","营业总收入"]
    dfp9=fs_item_analysis_2(df,ticker,fsdates1,items10)
    #====================================================================
    items11=["净利润","营业总收入"]
    dfp9=fs_item_analysis_2(df,ticker,fsdates1,items11)

    #增幅分析：近两年    
    fsdates2=fsdates[:2]
    items12=['营业成本','营业总成本','营业总收入']
    dfp12=fs_item_analysis_6(df,ticker,fsdates2,items12)

    items13=['毛利润','营业利润','税前利润','净利润']
    dfp11=fs_item_analysis_6(df,ticker,fsdates2,items13)

    #同行比较
    items14=['营业总收入','销售费用率%','管理费用率%','研发费用率%']
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items14)

    #items15=['营业利润','营业利润率%','税前利润率%','实际所得税率%','净利润','净利润率%']
    items15=['毛利润率%','营业利润率%','税前利润率%','净利润率%']
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items15)

    return    

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    cash_flow_structure_china(tickers,fsdates)
    
def cash_flow_structure_china(tickers,fsdates):
    """
    功能：分析上市公司的现金流量基本结构，并与同业公司对比。
    注意1：分析近三期情况，fsdates要给出四个报表日期，以便获得期初数。
    注意2：可以分析连续的年报或季报，但不能混个年报和季报。
    注意3：tickers中的第一家公司为主要分析对象。
    注意4：fsdates中的日期要降序排列，第一个日期建议为最近的财报日。
    """  
    #主要分析对象
    ticker=tickers[0]
    #最近的财报日
    fsdates=sorted(fsdates,reverse=True)
    fsdate=fsdates[0]
    
    #获取所有比较公司tickers的所有财报fsdates
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    #总体变动趋势
    items1=["经营活动现金流净额","经营活动现金流入","经营活动现金流出",
            "投资活动现金流净额","投资活动现金流入","投资活动现金流出",
            "筹资活动现金流净额","筹资活动现金流入","筹资活动现金流出",
            "汇率对现金流的影响","现金流量净增加额"]
    dfp1=fs_item_analysis_1(df,ticker,fsdate,items1)
    
    #占比变动分析：近三年
    fsdates1=fsdates[:3]
    items3=["经营活动现金流入","营业总收入"]
    dfp3=fs_item_analysis_2(df,ticker,fsdates1,items3)

    items4=["经营活动现金流净额","营业利润"]
    dfp3=fs_item_analysis_2(df,ticker,fsdates1,items4)

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
    
    return

#==============================================================================


