# -*- coding: utf-8 -*-
"""
本模块功能：SIAT公共基础函数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2019年7月16日
最新修订日期：2020年3月28日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')

#==============================================================================
#设置全局语言环境
import pickle

def check_language():
    """
    查询全局语言设置
    """
    try:
        with open('siat_language.pkl','rb') as file:
            lang=pickle.load(file)
    except:
        lang='Chinese'
        
    return lang

def set_language(lang='Chinese'):
    """
    修改全局语言设置
    """
    
    if lang in ['English','Chinese']:
        with open('siat_language.pkl','wb') as file:
            pickle.dump(lang,file)
        print("  Global language is set to",lang)
    else:
        print("  Warning: undefined language",lang)
        
    return

#==============================================================================
SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']
import pandas as pd
#==============================================================================
#==============================================================================
def ticker_check(ticker, source="yahoo"):
    """
    检查证券代码，对于大陆证券代码、香港证券代码和东京证券代码进行修正。
    输入：证券代码ticker，数据来源source。
    上交所证券代码后缀为.SS或.SH或.ss或.sh，深交所证券代码为.SZ或.sz
    港交所证券代码后缀为.HK，截取数字代码后4位
    东京证交所证券代码后缀为.T，截取数字代码后4位
    source：yahoo或tushare
    返回：字母全部转为大写。若是大陆证券返回True否则返回False。
    若选择yahoo数据源，上交所证券代码转为.SS；
    若选择tushare数据源，上交所证券代码转为.SH
    """
    #测试用，完了需要注释掉
    #ticker="600519.sh"
    #source="yahoo"
    
    #将字母转为大写
    ticker1=ticker.upper()
    #截取字符串最后2/3位
    suffix2=ticker1[-2:]
    suffix3=ticker1[-3:]
    
    #判断是否大陆证券
    if suffix3 in ['.SH', '.SS', '.SZ']:
        prc=True
    else: prc=False

    #根据数据源的格式修正大陆证券代码
    if (source == "yahoo") and (suffix3 in ['.SH']):
        ticker1=ticker1.replace(suffix3, '.SS')        
    if (source == "tushare") and (suffix3 in ['.SS']):
        ticker1=ticker1.replace(suffix3, '.SH')  

    #若为港交所证券代码，进行预防性修正，截取数字代码后4位，加上后缀共7位
    if suffix3 in ['.HK']:
        ticker1=ticker1[-7:]     

    #若为东交所证券代码，进行预防性修正，截取数字代码后4位，加上后缀共6位
    if suffix2 in ['.T']:
        ticker1=ticker1[-6:]  
    
    #返回：是否大陆证券，基于数据源/交易所格式修正后的证券代码
    return prc, ticker1        

#测试各种情形
if __name__=='__main__':
    prc, ticker=ticker_check("600519.sh","yahoo")
    print(prc,ticker)
    print(ticker_check("600519.SH","yahoo"))    
    print(ticker_check("600519.ss","yahoo"))    
    print(ticker_check("600519.SH","tushare"))    
    print(ticker_check("600519.ss","tushare"))    
    print(ticker_check("000002.sz","tushare"))
    print(ticker_check("000002.sz","yahoo"))
    print(ticker_check("00700.Hk","yahoo"))
    print(ticker_check("99830.t","yahoo"))

#==============================================================================
def tickers_check(tickers, source="yahoo"):
    """
    检查证券代码列表，对于大陆证券代码、香港证券代码和东京证券代码进行修正。
    输入：证券代码列表tickers，数据来源source。
    上交所证券代码后缀为.SS或.SH或.ss或.sh，深交所证券代码为.SZ或.sz
    港交所证券代码后缀为.HK，截取数字代码后4位
    东京证交所证券代码后缀为.T，截取数字代码后4位
    source：yahoo或tushare
    返回：证券代码列表，字母全部转为大写。若是大陆证券返回True否则返回False。
    若选择yahoo数据源，上交所证券代码转为.SS；
    若选择tushare数据源，上交所证券代码转为.SH
    """
    #检查列表是否为空
    if tickers[0] is None:
        print("*** 错误#1(tickers_check)，空的证券代码列表:",tickers)
        return None         
    
    tickers_new=[]
    for t in tickers:
        _, t_new = ticker_check(t, source=source)
        tickers_new.append(t_new)
    
    #返回：基于数据源/交易所格式修正后的证券代码
    return tickers_new

#测试各种情形
if __name__=='__main__':
    tickers=tickers_check(["600519.sh","000002.sz"],"yahoo")
    print(tickers)
#==============================================================================
def check_period(fromdate, todate):
    """
    功能：根据开始/结束日期检查日期与期间的合理性
    输入参数：
    fromdate：开始日期。格式：YYYY-MM-DD
    enddate：开始日期。格式：YYYY-MM-DD
    输出参数：
    validity：期间合理性。True-合理，False-不合理
    start：开始日期。格式：datetime类型
    end：结束日期。格式：datetime类型
    """
    import pandas as pd
    
    #测试开始日期的合理性
    try:
        start=pd.to_datetime(fromdate)
    except:
        print("*** #Error(check_period), invalid date:",fromdate)
        return None, None, None         
    
    #测试结束日期的合理性
    try:
        end=pd.to_datetime(todate)
    except:
        print("  #Error(check_period): invalid date:",todate)
        return None, None, None          
    
    #测试日期期间的合理性
    if start > end:
        print("  #Error(check_period): invalid period: from",fromdate,"to",todate)
        return None, None, None     

    return True, start, end

if __name__ =="__main__":
    check_period('2020-1-1','2020-2-4')
    check_period('2020-1-1','2010-2-4')

#==============================================================================
def date_adjust(basedate, adjust=0):
    """
    功能：将给定日期向前或向后调整特定的天数
    输入：基础日期，需要调整的天数。
    basedate: 基础日期。
    adjust：需要调整的天数，负数表示向前调整，正数表示向后调整。
    输出：调整后的日期。
    """
    #检查基础日期的合理性
    import pandas as pd    
    try:
        bd=pd.to_datetime(basedate)
    except:
        print("  #Error(date_adjust): invalid:",basedate)
        return None

    #调整日期
    from datetime import timedelta
    nd = bd+timedelta(days=adjust)    
    
    #重新提取日期
    newdate=nd.date()   
    return str(newdate)
 
if __name__ =="__main__":
    basedate='2020-3-17' 
    adjust=-365    
    newdate = date_adjust(basedate, adjust)
    print(newdate)    

#==============================================================================
if __name__ =="__main__":
    portfolio={'Market':('US','^GSPC'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}

def decompose_portfolio(portfolio):
    """
    功能：将一个投资组合字典分解为股票代码列表和份额列表
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合
    输出：市场，市场指数，股票代码列表和份额列表
    """
    #从字典中提取信息
    keylist=list(portfolio.keys())
    scope=portfolio[keylist[0]][0]
    mktidx=portfolio[keylist[0]][1]
    
    slist=[]
    plist=[]
    for key,value in portfolio.items():
        slist=slist+[key]
        plist=plist+[value]
    stocklist=slist[1:]    
    portionlist=plist[1:]

    return scope,mktidx,stocklist,portionlist    

if __name__=='__main__':
    portfolio1={'Market':('US','^GSPC'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    scope,mktidx,tickerlist,sharelist=decompose_portfolio(portfolio1)
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio1)

def portfolio_name(portfolio):
    """
    功能：解析一个投资组合的名字
    输入：投资组合
    输出：投资组合的自定义名称，未定义的返回"投资组合"
    注意：为了维持兼容性，特此定义此函数
    """
    #从字典中提取信息
    keylist=list(portfolio.keys())
    try:
        name=portfolio[keylist[0]][2]
    except:
        name="投资组合"

    return name    

if __name__=='__main__':
    portfolio={'Market':('US','^GSPC','我的组合001'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    portfolio_name(portfolio)
    
#==============================================================================
def calc_monthly_date_range(start,end):
    """
    功能：返回两个日期之间各个月份的开始和结束日期
    输入：开始/结束日期
    输出：两个日期之间各个月份的开始和结束日期元组对列表
    """
    #测试用
    #start='2019-01-05'
    #end='2019-06-25'    
    
    import pandas as pd
    startdate=pd.to_datetime(start)
    enddate=pd.to_datetime(end)

    mdlist=[]
    #当月的结束日期
    syear=startdate.year
    smonth=startdate.month
    import calendar
    sdays=calendar.monthrange(syear,smonth)[1]
    from datetime import date
    slastday=pd.to_datetime(date(syear,smonth,sdays))

    if slastday > enddate: slastday=enddate
    
    #加入第一月的开始和结束日期
    import bisect
    bisect.insort(mdlist,(startdate,slastday))
    
    #加入结束月的开始和结束日期
    eyear=enddate.year
    emonth=enddate.month
    efirstday=pd.to_datetime(date(eyear,emonth,1))   
    if startdate < efirstday:
        bisect.insort(mdlist,(efirstday,enddate))
    
    #加入期间内各个月份的开始和结束日期
    from dateutil.relativedelta import relativedelta
    next=startdate+relativedelta(months=+1)
    while next < efirstday:
        nyear=next.year
        nmonth=next.month
        nextstart=pd.to_datetime(date(nyear,nmonth,1))
        ndays=calendar.monthrange(nyear,nmonth)[1]
        nextend=pd.to_datetime(date(nyear,nmonth,ndays))
        bisect.insort(mdlist,(nextstart,nextend))
        next=next+relativedelta(months=+1)
    
    return mdlist

if __name__=='__main__':
    mdp1=calc_monthly_date_range('2019-01-01','2019-06-30')
    mdp2=calc_monthly_date_range('2000-01-01','2000-06-30')   #闰年
    mdp3=calc_monthly_date_range('2018-09-01','2019-03-31')   #跨年
    
    for i in range(0,len(mdp1)):
        start=mdp1[i][0]
        end=mdp1[i][1]
        print("start =",start,"end =",end)


#==============================================================================
def calc_yearly_date_range(start,end):
    """
    功能：返回两个日期之间各个年度的开始和结束日期
    输入：开始/结束日期
    输出：两个日期之间各个年度的开始和结束日期元组对列表
    """
    #测试用
    #start='2013-01-01'
    #end='2019-08-08'    
    
    import pandas as pd
    startdate=pd.to_datetime(start)
    enddate=pd.to_datetime(end)

    mdlist=[]
    #当年的结束日期
    syear=startdate.year
    from datetime import date
    slastday=pd.to_datetime(date(syear,12,31))

    if slastday > enddate: slastday=enddate
    
    #加入第一年的开始和结束日期
    import bisect
    bisect.insort(mdlist,(startdate,slastday))
    
    #加入结束年的开始和结束日期
    eyear=enddate.year
    efirstday=pd.to_datetime(date(eyear,1,1))   
    if startdate < efirstday:
        bisect.insort(mdlist,(efirstday,enddate))
    
    #加入期间内各个年份的开始和结束日期
    from dateutil.relativedelta import relativedelta
    next=startdate+relativedelta(years=+1)
    while next < efirstday:
        nyear=next.year
        nextstart=pd.to_datetime(date(nyear,1,1))
        nextend=pd.to_datetime(date(nyear,12,31))
        bisect.insort(mdlist,(nextstart,nextend))
        next=next+relativedelta(years=+1)
    
    return mdlist

if __name__=='__main__':
    mdp1=calc_yearly_date_range('2013-01-05','2019-06-30')
    mdp2=calc_yearly_date_range('2000-01-01','2019-06-30')   #闰年
    mdp3=calc_yearly_date_range('2018-09-01','2019-03-31')   #跨年
    
    for i in range(0,len(mdp1)):
        start=mdp1[i][0]
        end=mdp1[i][1]
        print("start =",start,"end =",end)

#==============================================================================

def sample_selection(df,start,end):
    """
    功能：根据日期范围start/end选择数据集df的子样本，并返回子样本
    """
    flag,start2,end2=check_period(start,end)
    df_sub=df[df.index >= start2]
    df_sub=df_sub[df_sub.index <= end2]
    
    return df_sub
    
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':1.0}
    market,mktidx,tickerlist,sharelist=decompose_portfolio(portfolio)
    start='2020-1-1'; end='2020-3-31'
    pfdf=get_portfolio_prices(tickerlist,sharelist,start,end)
    start2='2020-1-10'; end2='2020-3-18'
    df_sub=sample_selection(pfdf,start2,end2)    
    
#==============================================================================
def init_ts():
    """
    功能：初始化tushare pro，登录后才能下载数据
    """
    import tushare as ts
    #设置token
    token='49f134b05e668d288be43264639ac77821ab9938ff40d6013c0ed24f'
    pro=ts.pro_api(token)
    
    return pro
#==============================================================================
def convert_date_ts(y4m2d2):
    """
    功能：日期格式转换，YYYY-MM-DD-->YYYYMMDD，用于tushare
    输入：日期，格式：YYYY-MM-DD
    输出：日期，格式：YYYYMMDD
    """
    import pandas as pd
    try: date1=pd.to_datetime(y4m2d2)
    except:
        print("  #Error(convert_date_ts): invalid date:",y4m2d2)
        return None 
    else:
        date2=date1.strftime('%Y')+date1.strftime('%m')+date1.strftime('%d')
    return date2

if __name__ == '__main__':
    convert_date_ts("2019/11/1")
#==============================================================================
def gen_yearlist(start_year,end_year):
    """
    功能：产生从start_year到end_year的一个年度列表
    输入参数：
    start_year: 开始年份，字符串
    end_year：截止年份
    输出参数：
    年份字符串列表    
    """
    #仅为测试使用，完成后应注释掉
    #start_year='2010'
    #end_year='2019'    
    
    import numpy as np
    start=int(start_year)
    end=int(end_year)
    num=end-start+1    
    ylist=np.linspace(start,end,num=num,endpoint=True)
    
    yearlist=[]
    for y in ylist:
        yy='%d' %y
        yearlist=yearlist+[yy]
    #print(yearlist)
    
    return yearlist

if __name__=='__main__':
    yearlist=gen_yearlist('2013','2019')
#==============================================================================
def print_progress_bar(current,startnum,endnum):
    """
    功能：打印进度数值，每个10%打印一次，不换行
    """
    for i in [9,8,7,6,5,4,3,2,1]:
        if current == int((endnum - startnum)/10*i)+1: 
            print(str(i)+'0%',end=' '); break
        elif current == int((endnum - startnum)/100*i)+1: 
            print(str(i)+'%',end=' '); break
    if current == 2: print('0%',end=' ')

if __name__ =="__main__":
    startnum=2
    endnum=999
    L=range(2,999)
    for c in L: print_progress_bar(c,startnum,endnum)

#==============================================================================
def save_to_excel(df,filedir,excelfile,sheetname="Sheet1"):
    """
    函数功能：将df保存到Excel文件。
    如果目录不存在提示出错；如果Excel文件不存在则创建之文件并保存到指定的sheet；
    如果Excel文件存在但sheet不存在则增加sheet并保存df内容，原有sheet内容不变；
    如果Excel文件和sheet都存在则追加df内容到已有sheet的末尾
    输入参数：
    df: 数据框
    filedir: 目录
    excelfile: Excel文件名，不带目录，后缀为.xls或.xlsx
    sheetname：Excel文件中的sheet名
    输出：
    保存df到Excel文件
    无返回数据
    
    注意：如果df中含有以文本表示的数字，写入到Excel会被自动转换为数字类型保存。
    从Excel中读出后为数字类型，因此将会与df的类型不一致
    """

    #检查目录是否存在
    import os
    try:
        os.chdir(filedir)
    except:
        print("Error #1(save_to_excel): folder does not exist")        
        print("Information:",filedir)  
        return
                
    #取得df字段列表
    dflist=df.columns
    #合成完整的带目录的文件名
    filename=filedir+'/'+excelfile
    
    import pandas as pd
    try:
        file1=pd.ExcelFile(excelfile)
    except:
        #不存在excelfile文件，直接写入
        df.to_excel(filename,sheet_name=sheetname, \
                       header=True,encoding='utf-8')
        print("***Results saved in",filename,"@ sheet",sheetname)
        return
    else:
        #已存在excelfile文件，先将所有sheet的内容读出到dict中        
        dict=pd.read_excel(file1, None)
    file1.close()
    
    #获得所有sheet名字
    sheetlist=list(dict.keys())
    
    #检查新的sheet名字是否已存在
    try:
        pos=sheetlist.index(sheetname)
    except:
        #不存在重复
        dup=False
    else:
        #存在重复，合并内容
        dup=True
        #合并之前可能需要对df中以字符串表示的数字字段进行强制类型转换.astype('int')
        df1=dict[sheetlist[pos]][dflist]
        dfnew=pd.concat([df1,df],axis=0,ignore_index=True)        
        dict[sheetlist[pos]]=dfnew
    
    #将原有内容写回excelfile    
    result=pd.ExcelWriter(filename)
    for s in sheetlist:
        df1=dict[s][dflist]
        df1.to_excel(result,s,header=True,index=True,encoding='utf-8')
    #写入新内容
    if not dup: #sheetname未重复
        df.to_excel(result,sheetname,header=True,index=True,encoding='utf-8')
    try:
        result.save()
        result.close()
    except:
        print("Error #2(save_to_excel): writing file permission denied")
        print("Information:",filename)  
        return
    print("***Results saved in",filename,"@ sheet",sheetname)
    return       
#==============================================================================
def set_df_period(df,df_min,df_max):
    """
    功能： 去掉df中日期范围以外的记录
    """
    df1=df[df.index >= df_min]
    df2=df1[df1.index <= df_max]
    return df2

if __name__=='__main__':
    import siat.security_prices as ssp
    df=ssp.get_price('AAPL','2020-1-1','2020-1-31')    
    df_min,df_max=get_df_period(df)    
    df2=set_df_period(df,df_min,df_max)

#==============================================================================
def sigstars(p_value):
    """
    功能：将p_value转换成显著性的星星
    """
    if p_value >= 0.1: 
        stars="   "
        return stars
    if 0.1 > p_value >= 0.05:
        stars="*  "
        return stars
    if 0.05 > p_value >= 0.01:
        stars="** "
        return stars
    if 0.01 > p_value:
        stars="***"
        return stars

#==============================================================================

def regparms(results):
    """
    功能：将sm.OLS回归结果生成数据框，包括变量名称、系数数值、t值、p值和显著性星星
    """
    import pandas as pd
    #取系数
    params=results.params
    df_params=pd.DataFrame(params)
    df_params.columns=['coef']
    
    #取t值
    tvalues=results.tvalues
    df_tvalues=pd.DataFrame(tvalues)
    df_tvalues.columns=['t_values']

    #取p值
    pvalues=results.pvalues
    df_pvalues=pd.DataFrame(pvalues)
    df_pvalues.columns=['p_values']            

    #生成星星
    df_pvalues['sig']=df_pvalues['p_values'].apply(lambda x:sigstars(x))
    
    #合成
    parms1=pd.merge(df_params,df_tvalues, \
                    how='inner',left_index=True,right_index=True)
    parms2=pd.merge(parms1,df_pvalues, \
                    how='inner',left_index=True,right_index=True)

    return parms2
#==============================================================================
if __name__=='__main__':
    txt='QDII-指数'

def strlen(txt):
    """
    功能：计算中英文混合字符串的实际长度
    注意：有时不准
    """
    lenTxt = len(txt) 
    lenTxt_utf8 = len(txt.encode('utf-8')) 
    size = int((lenTxt_utf8 - lenTxt)/2 + lenTxt)    

    return size

#==============================================================================

def sort_pinyin(hanzi_list): 
    """
    功能：对列表中的中文字符串按照拼音升序排序
    """
    from pypinyin import lazy_pinyin       
    hanzi_list_pinyin=[]
    hanzi_list_pinyin_alias_dict={}
    
    for single_str in hanzi_list:
        py_r = lazy_pinyin(single_str)
        # print("整理下")
        single_str_py=''
        for py_list in py_r:
            single_str_py=single_str_py+py_list
        hanzi_list_pinyin.append(single_str_py)
        hanzi_list_pinyin_alias_dict[single_str_py]=single_str
    
    hanzi_list_pinyin.sort()
    sorted_hanzi_list=[]
    
    for single_str_py in hanzi_list_pinyin:
        sorted_hanzi_list.append(hanzi_list_pinyin_alias_dict[single_str_py])
    
    return sorted_hanzi_list


#==============================================================================
if __name__=='__main__':
    end_date='2021-11-18'
    pastyears=1

def get_start_date(end_date,pastyears=1):
    """
    输入参数：一个日期，年数
    输出参数：几年前的日期
    """

    import pandas as pd
    try:
        end_date=pd.to_datetime(end_date)
    except:
        print("  #Error(get_start_date): invalid date,",end_date)
        return None
    
    from datetime import datetime,timedelta
    start_date=datetime(end_date.year-pastyears,end_date.month,end_date.day)
    start_date2=start_date-timedelta(days=1)
    # 日期-1是为了保证计算收益率时得到足够的样本数量
    
    start_date3=str(start_date2.year)+'-'+str(start_date2.month)+'-'+str(start_date2.day)
    return start_date3
    
#==============================================================================
def get_ip():
    """
    功能：获得本机计算机名和IP地址    
    """
    #内网地址
    import socket
    hostname = socket.gethostname()
    internal_ip = socket.gethostbyname(hostname)
    
    #公网地址

    return hostname,internal_ip

if __name__=='__main__':
    get_ip()
#==============================================================================
def check_date(adate):
    """
    功能：检查一个日期是否为有效日期
    输入参数：一个日期
    输出：合理日期为True，其他为False
    """
    #仅为测试使用，测试完毕需要注释掉
    #adate='2019-6-31'

    result=True
    import pandas as pd
    try:    
        bdate=pd.to_datetime(adate)
    except:
        print("  #Error(check_date): invalid date",adate)
        #print("Variable(s):",adate)
        result=False
        
    return result

if __name__ =="__main__":
    print(check_date('2019-6-31'))


#==============================================================================
def check_start_end_dates(start,end):
    """
    功能：检查一个期间的开始/结束日期是否合理
    输入参数：开始和结束日期
    输出：合理为True，其他为False
    """
    #仅为测试使用，测试完毕需要注释掉
    #adate='2019-6-31'

    if not check_date(start):
        print("Error #1(check_start_end_dates): invalid start date")
        print("Variable(s):",start)
        return False

    if not check_date(end):
        print("Error #2(check_start_end_dates): invalid end date")
        print("Variable(s):",end)
        return False       
    
    if start > end:
        print("Error #3(check_start_end_dates): irrational start/end dates")
        print("Variable(s): from",start,"to",end)
        return False
        
    return True

if __name__ =="__main__":
    print(check_start_end_dates('2019-1-1','2019-8-18'))

#==============================================================================
if __name__=='__main__':
    txt="上市公司/家"        
        
def hzlen(txt):
    """
    功能：计算含有汉字的字符串的长度
    """
    #strlen=int((len(txt.encode('utf-8')) - len(txt)) / 2 + len(txt))
    #strlen=int((len(txt.encode('gb18030')) - len(txt)) / 2 + len(txt))
    
    import unicodedata
    #Unicode字符有不同的类别
    txtlist=list(unicodedata.category(c) for c in txt)
    strlen=0
    for t in txtlist:
        #类别Lo表示一个非拉丁文字
        if t == 'Lo':
            strlen=strlen+2
        else:
            strlen=strlen+1
    
    return strlen

#==============================================================================
def int10_to_date(int10):
    """
    功能：将10位数字的时间戳转换为日期。
    输入：10位数字的时间戳int10。
    返回：日期字符串。
    """
    import time
    tupTime = time.localtime(int10)
    y4m2d2 = time.strftime("%Y-%m-%d", tupTime)    
    return y4m2d2

if __name__ =="__main__":
    int10=9876543210
    print(int10_to_date(int10))    
#==============================================================================
def equalwidth(string,maxlen=20):
    """
    输入：字符串，中英文混合
    输出：设定等宽度，自动补齐
    """
    reallen=hzlen(string)
    if maxlen < reallen:
        maxlen = reallen
    return string+'.'*(maxlen-reallen)+'：'

if __name__ =="__main__":
    equalwidth("中文1英文abc",maxlen=20)
#==============================================================================
if __name__ =="__main__":
    longlist=['豆粕', '玉米', '铁矿石', '棉花', '白糖', 'PTA', '甲醇', '橡胶', '沪铜', '黄金', '菜籽粕', '液化石油气', '动力煤']
    numperline=5
    beforehand=' '*4
    separator=' '
    
def printlist(longlist,numperline=5,beforehand='',separator=' '):
    """
    打印长列表，每numperline个一行，超过换行，分隔符为separator
    """
    listlen=len(longlist)
    if listlen==0:
        print("  #Warning(printlist): print list is empty")
        return
    
    counter=0
    print(beforehand,end='')
    for l in longlist:
        counter=counter+1
        if counter <=numperline:
            print(l,end=separator)
        else:
            print('')
            print(beforehand,end='')
            counter=0
    print('')
    return        

#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='AAPL'

def split_prefix_suffix(ticker):
    """
    将证券代码拆分为前后两部分
    """
    ticker=ticker.upper()
    result=False
    try:
        pos=ticker.index('.')
        prefix=ticker[:pos]
        suffix=ticker[pos+1:]
        result=True
    except:
        prefix=ticker
        suffix=''
        
    return result,prefix,suffix

if __name__=='__main__':
    split_prefix_suffix('600519.SS')
    split_prefix_suffix('600519.ss')
    split_prefix_suffix('AAPL')
    split_prefix_suffix('aapl')
#==================================================================================
if __name__=='__main__': 
    start='2021-11-1'
    end='2021-11-15'

shibor_period_list=['ON','1W','2W','1M','3M','6M','9M','1Y']

def get_shibor_rates_bs(start,end,rate_period='3M'):
    """
    功能：基于Baostock获得指定期间和期限的shibor利率
    start：开始日期
    end：结束日期
    rate_period：利率类型
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """
    #检查日期期间
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(get_shibor_rates): invalid date period from",start,"to",end)
        return None
    
    #检查利率类型
    if not (rate_period in shibor_period_list):
        print("  #Error(get_shibor_rates): unsupported rate period",rate_period)
        print("  Supported shibor rate periods:",shibor_period_list)
        return None
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    import pandas as pd
    import baostock as bs
    # 登陆系统：不显示信息login success!
    with HiddenPrints():
        lg = bs.login()
    # 登陆失败处理
    if not (lg.error_code=='0'):
        print('  Baostock: login respond error_code:'+lg.error_code)
        print('  Baostock: login respond error_msg:'+lg.error_msg)
        return None

    # 获取银行间同业拆放利率
    rs = bs.query_shibor_data(start_date=start,end_date=end)
    if not (rs.error_code=='0'):
        print('  Baostock: query_shibor_data error_code:'+rs.error_code)
        print('  Baostock: query_shibor_data respond  error_msg:'+rs.error_msg)
        return None

    # 登出系统：不显示信息
    with HiddenPrints():
        lo=bs.logout()
    
    #提取数据，生成pandas格式
    rs_data=rs.data
    data_list = []
    for l in rs_data:
        data_list.append(l)

    rs_fields=rs.fields
    result = pd.DataFrame(data_list, columns=rs.fields)
    
    result['Date']=pd.to_datetime(result['date'])
    result.set_index(['Date'],inplace=True)
    
    result['rate']=round(result['shibor'+rate_period].astype('float')/100,5)
    result['period']=rate_period
    result1=result[['date','rate','period']]
    
    return result1
    
if __name__=='__main__': 
    get_shibor_rates_bs('2021-10-1','2021-11-28')   
    
#=============================================================================
if __name__=='__main__': 
    date='2021-11-19'
    rate_period='3M'
    daysahead=30

def shibor_rate(date,rate_period='3M',daysahead=60):
    """
    获取指定日期和期限的shibor利率
    若无最新利率，则取最近日期的利率替代
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """    
    
    #检查日期有效性
    valid_date=check_date(date)
    if not valid_date:
        print("  #Error(shibor_rate): invalid date",date)
        return None
    start=date_adjust(date, adjust=-daysahead)
    
    rate_period=rate_period.upper()
    
    #检查利率期间有效性
    if not (rate_period in shibor_period_list):
        print("  #Error(shibor_rate): invalid shibor rate period",rate_period)
        print("  Supported shibor rate periods:",shibor_period_list)
        return None
    
    df=get_shibor_rates_bs(start,date,rate_period) 
    
    try:
        rate=float(df[-1:]['rate'].values[0])
    except:
        print("  #Error(shibor_rate): shibor rate period not found for",rate_period)
        return None
    
    return rate
    
if __name__=='__main__': 
    shibor_rate('2021-11-19',rate_period='3M')
    shibor_rate('2021-11-19',rate_period='ON')
#==============================================================================        
if __name__=='__main__':
    start='2020-1-1'
    end='2021-11-30'
    term='1Y'
    
def treasury_yields_china(start,end,term='1Y'):
    """
    功能：抓取指定期间和期限的国债收益率
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """
    #检查日期期间
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(treasury_yields_china): invalid date period from",start,"to",end)
        return None
    
    #检查利率期间有效性
    term_list=['3M','6M','1Y','3Y','5Y','7Y','10Y','30Y']
    if not (term in term_list):
        print("  #Error(treasury_yields_china): invalid rate period",term)
        print("  Supported rate periods:",term_list)
        return None
    
    #抓取中债国债收益率
    import akshare as ak
    df = ak.bond_china_yield(start_date=start,end_date=end)
    
    df1=df[df['曲线名称']=='中债国债收益率曲线']
    df1.columns=['curve','date']+term_list
    df1.sort_values(by=['date'],ascending=['True'],inplace=True)
    
    df1['Date']=pd.to_datetime(df1['date'])
    df1.set_index(['Date'],inplace=True)    
    
    df1['rate']=df1[term]/100
    df1['period']=term
    df2=df1[['date','rate','period']]
    
    return df2

if __name__=='__main__':
    treasury_yields_china('2021-11-1','2021-11-28',term='1Y')
    
    
if __name__=='__main__':
    today='2021-11-20'
    term='1Y'
    daysahead=30
    
def treasury_yield_china(today,term='1Y',daysahead=60):
    """
    功能：抓取指定日期和期限的国债收益率
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """
    #检查日期
    valid=check_date(today)
    if not valid:
        print("  #Error(treasury_yield_china): invalid date",today)
        return None
    start = date_adjust(today, adjust=-daysahead)

    #检查利率期间有效性
    term_list=['3M','6M','1Y','3Y','5Y','7Y','10Y','30Y']
    if not (term in term_list):
        print("  #Error(treasury_yield_china): invalid rate period",term)
        print("  Supported rate periods:",term_list)
        return None
    
    rates=treasury_yields_china(start,today,term=term)
    rate=rates[-1:]['rate'].values[0]
        
    return rate
        
if __name__=='__main__':
    treasury_yield_china('2021-11-20',term='1Y')  
    treasury_yield_china('2021-11-18')
#==============================================================================
if __name__=='__main__':
    start='2019-1-1'
    end='2020-12-31'
    rate_period='1Y'
    rate_type='treasury'
    
def rf_daily_china(start,end,rate_period='1Y',rate_type='shibor'):
    """
    功能：抓取指定期间和期限的无风险利率
    
    注意：这里得到的是日利率，不带百分号，不是年化利率！（日利率=年化利率/365）
    """
    rate_type1=rate_type.upper()
    
    if rate_type1=="TREASURY":
        if rate_period in ['3M','6M','1Y']:
            #使用国债收益率
            df=treasury_yields_china(start,end,rate_period)
        else:
            #使用shibor收益率
            df=get_shibor_rates_bs(start,end,rate_period)
    elif rate_type1=="SHIBOR":
        #使用shibor收益率
        df=get_shibor_rates_bs(start,end,rate_period)
        if len(df)==0:
            #未能获取数据，Baostock获取的shibor利率一般滞后一个月左右
            start1=date_adjust(start,adjust=-60)
            df=get_shibor_rates_bs(start1,end,rate_period)
    else:
        print("  #Warning(): invalid rf rate type",rate_type)
        print("  Only support 2 types of rf: shibor rate, treasury yield")
        return None
    
    #使用最近日期的利率填补空缺的日期
    latest_date=df['date'][-1:].values[0]
    lastest_rate=df['rate'][-1:].values[0]
    period=df['period'][-1:].values[0]

    collist=list(df)
    df_temp = pd.DataFrame(columns=collist)
    end_dt=pd.to_datetime(end)
    for i in range(100):
        date1=date_adjust(latest_date,adjust=i+1)
        date1_dt=pd.to_datetime(date1)
        if date1_dt <=end_dt:
            df_temp=df_temp.append({'date':date1,'rate':lastest_rate,'period':period},ignore_index=True)
        else:
            break
    
    df_temp['Date']=pd.to_datetime(df_temp['date'])
    df_temp.set_index(['Date'],inplace=True)    

    df1=df.append(df_temp)
    df1.sort_values(by=['date'],ascending=[True],inplace=True)
    
    df1['rf_daily']=df1['rate']/365
    
    return df1
    
if __name__=='__main__':
    rfd=rf_daily_china('2021-10-1','2021-11-28',rate_period='1Y',rate_type='shibor')
    rfd=rf_daily_china('2021-11-1','2021-11-28',rate_period='3M',rate_type='shibor')
    rfd=rf_daily_china('2021-11-1','2021-11-28',rate_period='1Y',rate_type='treasury')
    
#==============================================================================
if __name__=='__main__':
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    leading_blanks=2

def print_tickerlist_sharelist(tickerlist,sharelist,leading_blanks=2):
    """
    功能：纵向打印投资组合的成分股和持股比例
    输入：
    tickerlist：成分股列表
    sharelist：持股份额列表
    leading_blanks：打印前导空格数
    """
    #检查成分股与持仓比例个数是否一致
    if not (len(tickerlist) == len(sharelist)):
        print("  #Error(): numbers of tickers and shares are not same")
        return
    
    #计算最长的代码长度，便于对齐
    max_ticker_len=0
    for t in tickerlist:
        tlen=len(t)
        #print(t,tlen)
        if tlen > max_ticker_len: #if的执行语句放在这里可能有bug
            max_ticker_len=tlen
    
    # 将原投资组合的权重存储为numpy数组类型，为了合成投资组合计算方便
    import numpy as np
    sharelist_array = np.array(sharelist)
    total_shares=sharelist_array.sum()
    weights=sharelist_array/total_shares 
    
    import pandas as pd
    df=pd.DataFrame(columns=['证券代码','证券名称','持仓比例'])
    for t in tickerlist:
        pos=tickerlist.index(t)
        tname=codetranslate(t)
        tweight=weights[pos]
        
        row=pd.Series({'证券代码':t,'证券名称':tname,'持仓比例':tweight})
        df=df.append(row,ignore_index=True)          
    
    #按持仓比例降序
    df.sort_values(by='持仓比例',ascending=False,inplace=True)
    """
    #打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    print(df.to_string(index=False,header=False))
    """
    
    #打印
    df.reset_index(inplace=True) #必须，不然排序不起作用
    for i in range(len(df)):
        rows = df.loc[[i]]
        tcode=rows['证券代码'].values[0]
        tname=rows['证券名称'].values[0]
        tweight=rows['持仓比例'].values[0]
        print(' '*leading_blanks,tcode+' '*(max_ticker_len-len(tcode))+':',tname,'\b,',round(tweight,4)) 
        """
        values = rows.to_string(index=False,header=False)
        """
    
    return
    
if __name__=='__main__':
    print_tickerlist_sharelist(tickerlist,sharelist,leading_blanks=2)
#==============================================================================
if __name__=='__main__':
    current=1500
    total=5000
    steps=5
    leading_blanks=4

def print_progress_percent(current,total,steps=5,leading_blanks=4):
    """
    功能：打印进度百分比
    current：当前完成个数
    total：总个数
    steps：分成几个进度点显示
    leading_blanks：前置空格数
    """
    
    #间隔区间
    fraction=int(total/steps)
    
    #生成进度个数点位
    point_list=[]
    pct_list=[]
    for s in range(steps):
        #print("step=",s+1)
        point_list=point_list+[fraction*(s+1)-1]
        pct_list=pct_list+[str(int(100/steps*(s+1)))+'%']
    
    #当前完成第一个数时显示，其他时候不显示
    if current == 0: #range函数产生的第一个数是0
        print(' '*(leading_blanks - 1),"Progress...",end=' ')
    
    #打印当前进度百分比：到达点位时打印，否则无显示
    for p in point_list:
        if current == p:
            pos=point_list.index(p)
            pct=pct_list[pos]
            
            if pct=="100%":
                print("100% completed")
            else:
                print(pct,end=' ')
    
    return

if __name__=='__main__':
    for i in range(total): print_progress_percent(i,total,steps=5,leading_blanks=4)
    for i in range(total): print_progress_percent(i,total,steps=10,leading_blanks=4)

#==============================================================================
if __name__=='__main__':
    current='1'
    total_list=[str(x) for x in range(1000)]
    steps=5
    leading_blanks=4

def print_progress_percent2(current,total_list,steps=5,leading_blanks=4):
    """
    功能：打印进度百分比
    current：当前完成
    total：需要完成的列表
    steps：分成几个进度点显示
    leading_blanks：前置空格数
    """
    
    #间隔区间
    fraction=int(len(total_list)/steps)
    
    #生成进度个数点位
    point_list=[]
    pct_list=[]
    for s in range(steps):
        #print("step=",s+1)
        point_list=point_list+[fraction*(s+1)-1]
        pct_list=pct_list+[str(int(100/steps*(s+1)))+'%']
    
    #当前完成第一个数时显示，其他时候不显示
    pos=total_list.index(current)
    if pos == 0: #range函数产生的第一个数是0
        print(' '*(leading_blanks - 1),"Progress...",end=' ')
    
    #打印当前进度百分比：到达点位时打印，否则无显示
    for p in point_list:
        if pos == p:
            pos=point_list.index(p)
            pct=pct_list[pos]
            
            if pct=="100%":
                print("100% completed")
            else:
                print(pct,end=' ')
    
    return

if __name__=='__main__':
    for i in total_list: print_progress_percent2(i,total_list,steps=5,leading_blanks=4)
    for i in total_list: print_progress_percent2(i,total_list,steps=10,leading_blanks=4)

#==============================================================================
#==============================================================================
