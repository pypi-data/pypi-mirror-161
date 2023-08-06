# -*- coding: utf-8 -*-
"""
本模块功能：基金与衍生品函数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年1月18日
最新修订日期：2020年5月25日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
def interbank_bond_issue_monthly(df,fromdate='*DEFAULT',todate='*DEFAULT',type='ALL'):
    """
    功能：获得银行间债券市场发行金额，按月累计
    输入：债券发行记录明细df，开始日期fromdate，截止日期todate；
    债券类型type，默认所有类型
    类型：SCP 超短期融资券，CP 短期融资券（短融），PPN 定向工具（私募券），
    MTN 中期票据（中票），ABN 资产支持票据，PRN 项目收益票据，SMECN 中小集合票据
    PB指的就是熊猫债。熊猫债是指境外和多边金融机构等在华发行的人民币债券。
    DFI债务融资工具，PN/PPN定向工具(私募券)。
    """
    #过滤日期
    import pandas as pd
    if fromdate.upper() != '*DEFAULT':
        #测试开始日期的合理性
        try: 
            start=pd.to_datetime(fromdate)
        except:
            print("*** Error(interbank_bond_issue_monthly), invalid date:",fromdate)
            return None 
        df=df.reset_index(drop = True)
        df=df.drop(df[df['releaseTime2']<start].index)
        
    if todate.upper() != '*DEFAULT':
        #测试结束日期的合理性
        try: 
            end=pd.to_datetime(todate)
        except:
            print("*** Error(interbank_bond_issue_monthly), invalid:",todate)
            return None 
        df=df.reset_index(drop = True)
        df=df.drop(df[df['releaseTime2']>end].index)
        
    #检查债券类型
    bondtype=type.upper()
    typelist=['PN','SCP','MTN','ABN','PB','CP','PRN','PB-MTN','DFI','ALL']   
    if not (bondtype in typelist):
        print("...Error(interbank_bond_issue_monthly), unsupported bond type:",type)
        print("   Supported bond types:",typelist)
        return None      
    
    #过滤债券类型
    ibbid=df
    if bondtype != 'ALL':
        ibbid=df.drop(df[df['regPrdtType']!=bondtype].index)
        ibbid=ibbid.reset_index(drop = True)    
    
    #统计每月债券发行量
    lway=lambda x: x[0:7]
    ibbid['Year_Month']=ibbid['releaseDate'].map(lway).astype('str')
    ibbid['issueAmount']=ibbid['firstIssueAmount'].astype('float64')
    import pandas as pd
    ibbim=pd.DataFrame(ibbid.groupby(by=['Year_Month'])['issueAmount'].sum())
    #升序排列
    ibbim.sort_values(by=['Year_Month'],ascending=[True],inplace=True)
    
    #绘图
    titletxt="中国债券市场月发行量"
    if bondtype != 'ALL':
        titletxt=titletxt+"（"+bondtype+"）"
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="数据来源：中国银行间市场交易商协会(NAFMII)，"+today
    plot_line(ibbim,'issueAmount',"发行量","金额(亿元)", \
              titletxt,footnote,power=4)
    
    return ibbim

    
if __name__=='__main__':
    fromdate='2010-1-1'    
    todate='2019-12-31'
    ibbi=interbank_bond_issue_detail(fromdate,todate)
    save_to_excel(ibbi,"S:/siat","bond_issue_monthly_2012_2019.xlsx")
    
    import pandas as pd
    io=r"S:/siat/bond_issue_monthly_2012_2019.xlsx"
    ibbi=pd.read_excel(io)
    del ibbi['Unnamed: 0']
    df=ibbi
    
    fromdate='2018-1-1'; todate='2020-12-31'; type='SCP'
    ibbim=interbank_bond_issue_monthly(ibbi,fromdate,todate)
    ibbim=interbank_bond_issue_monthly(ibbi,fromdate,todate,type='SCP')
    ibbim=interbank_bond_issue_monthly(ibbi,fromdate,todate,type='CP')
    ibbim=interbank_bond_issue_monthly(ibbi,fromdate,todate,type='MTN')
    ibbim=interbank_bond_issue_monthly(ibbi,fromdate,todate,type='ABN')
    ibbim=interbank_bond_issue_monthly(ibbi,fromdate,todate,type='PN')

#==============================================================================
def interbank_bond_issue_yearly(df,type='ALL'):
    """
    功能：获得银行间债券市场发行金额，按月累计
    输入：债券发行记录明细df；
    债券类型type，默认所有类型
    类型：SCP 超短期融资券，CP 短期融资券（短融），PPN 定向工具（私募券），
    MTN 中期票据（中票），ABN 资产支持票据，PRN 项目收益票据，SMECN 中小集合票据
    PB指的就是熊猫债。熊猫债是指境外和多边金融机构等在华发行的人民币债券。
    DFI债务融资工具，PN/PPN定向工具(私募券)。
    """
    
    #检查债券类型
    bondtype=type.upper()
    typelist=['PN','SCP','MTN','ABN','PB','CP','PRN','PB-MTN','DFI','ALL']   
    if not (bondtype in typelist):
        print("...Error(interbank_bond_issue_monthly), unsupported bond type:",type)
        print("   Supported bond types:",typelist)
        return None      
    
    #过滤债券类型
    ibbid=df
    if bondtype != 'ALL':
        ibbid=df.drop(df[df['regPrdtType']!=bondtype].index)
        ibbid=ibbid.reset_index(drop = True)    
    
    #统计每年债券发行量
    ibbid['issueAmount']=ibbid['firstIssueAmount'].astype('float64')
    import pandas as pd
    ibbim=pd.DataFrame(ibbid.groupby(by=['releaseYear'])['issueAmount'].sum())
    #升序排列
    ibbim.sort_values(by=['releaseYear'],ascending=[True],inplace=True)
    
    #绘图
    titletxt="中国债券市场年发行量"
    if bondtype != 'ALL':
        titletxt=titletxt+"（"+bondtype+"）"
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="数据来源：中国银行间市场交易商协会(NAFMII)，"+today
    plot_line(ibbim,'issueAmount',"发行量","金额(亿元)", \
              titletxt,footnote,power=4)
    
    return ibbim
    
if __name__=='__main__':
    fromdate='2010-1-1'    
    todate='2019-12-31'
    ibbim=interbank_bond_issue_detail(fromdate,todate)
    save_to_excel(ibbim,"S:/siat","bond_issue_monthly_2012_2019.xlsx")
    
    import pandas as pd
    io=r"S:/siat/bond_issue_monthly_2012_2019.xlsx"
    ibbi=pd.read_excel(io)
    del ibbi['Unnamed: 0']
    
    ibbiy=interbank_bond_issue_yearly(ibbi,type='SCP')
    ibbiy=interbank_bond_issue_yearly(ibbi,type='CP')
    

#==============================================================================
def interbank_bond_quote(num,option='1'):
    """
    功能：获得银行间债券市场现券报价
    输入：从头开始显示的个数num；选项option：默认1按照收益率从高到低排列，
    2按照发行时间从早到晚排列，3按照报价机构排列。其他选项按照默认排列。
    """
    #抓取银行间市场债券报价
    import akshare as ak
    df=ak.bond_spot_quote()
    
    #其他选项均作为默认选项
    if not option in ['1','2','3','4']: option='1'    
    if option=='1':
        df.sort_values(by=['买入/卖出收益率(%)'],ascending=[False],inplace=True)
        optiontxt="按照收益率从高到低排序"
    if option=='2':
        df.sort_values(by=['债券简称'],ascending=[True],inplace=True) 
        optiontxt="按照发行时间从早到晚排序"
    if option=='3':
        df.sort_values(by=['债券简称'],ascending=[False],inplace=True) 
        optiontxt="按照发行时间从晚到早排序"
    if option=='4':
        df.sort_values(by=['报价机构'],ascending=[True],inplace=True)
        optiontxt="按照报价机构排序"
    #重新索引
    df.reset_index(drop=True)
    
    print("\n*** 中国银行间市场债券现券即时报价（"+optiontxt+"，前"+str(num)+"名）***")
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    print(df.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n    数据来源：中国银行间市场交易商协会(NAFMII)，"+today    
    print(footnote)
    
    return df

if __name__=='__main__':
    num=10
    option='1'
    ibbq=interbank_bond_quote(num,option)   
    option='2'
    ibbq=interbank_bond_quote(num,option) 
    option='6'
    ibbq=interbank_bond_quote(num,option) 

#==============================================================================
def interbank_bond_deal(num,option='1'):
    """
    功能：获得银行间债券市场现券成交行情
    输入：从头开始显示的个数num；选项option：默认1按照收益率从高到低排列，
    2按照发行时间从早到晚排列，3按照发行时间从晚到早排列，4按照涨跌幅从高到低，
    5按照涨跌幅从低到高。
    其他选项按照默认排列。
    """
    #抓取银行间市场债券报价
    import akshare as ak
    df=ak.bond_spot_deal()
    
    #其他选项均作为默认选项
    if not option in ['1','2','3','4','5']: option='1'    
    if option=='1':
        df.sort_values(by=['最新收益率(%)'],ascending=[False],inplace=True)
        optiontxt="按照收益率从高到低排序"
    if option=='2':
        df.sort_values(by=['债券简称'],ascending=[True],inplace=True) 
        optiontxt="按照发行时间从早到晚排序"
    if option=='3':
        df.sort_values(by=['债券简称'],ascending=[False],inplace=True) 
        optiontxt="按照发行时间从晚到早排序"
    if option=='4':
        df.sort_values(by=['涨跌(BP)'],ascending=[False],inplace=True)
        optiontxt="按照涨跌幅从高到低排序"
    if option=='5':
        df.sort_values(by=['涨跌(BP)'],ascending=[True],inplace=True)
        optiontxt="按照涨跌幅从低到高排序"
    #删除空值段
    del df["交易量(亿)"]
    del df["加权收益率(%)"]
    #重新索引
    df.reset_index(drop=True)
    
    print("\n*** 中国银行间市场债券现券即时成交价（"+optiontxt+"，前"+str(num)+"名）***")
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    print(df.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n    数据来源：中国银行间市场交易商协会(NAFMII)，"+today    
    print(footnote)
    
    return df

if __name__=='__main__':
    num=10
    option='1'
    ibbd=interbank_bond_deal(num,option)   
    option='2'
    ibbd=interbank_bond_deal(num,option) 
    option='6'
    ibbd=interbank_bond_deal(num,option) 


#==============================================================================


import os, sys

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
#==============================================================================
def exchange_bond_deal(num,option='1'):
    """
    功能：获得沪深债券市场现券成交行情
    输入：从头开始显示的个数num；选项option：默认1按照交易时间排列，
    2按照发行时间从早到晚排列，3按照发行时间从晚到早排列，4按照涨跌幅从高到低，
    5按照涨跌幅从低到高，6按照成交量从高到低排列，7按照成交量从低到高排列。
    其他选项按照默认排列。
    """
    print("开始搜索互联网，可能需要较长时间，请耐心等候......")
    #定义标准输出关闭类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    import pandas as pd
    df=pd.DataFrame()
    #抓取银行间市场债券报价
    import akshare as ak
    with HiddenPrints():
        try:
            df=ak.bond_zh_hs_spot()
        except:
            pass
    if len(df)==0: 
        print("...错误(exchange_bond_deal)，抓取信息中途失败，信息可能不完整，请稍候再试")
        return None    
    
    #选取需要的字段
    df1=df[['ticktime','symbol','name','trade','pricechange','open','high', \
            'low','buy','sell','volume']]
    #转换字符类型到数值类型
    df1['trade']=df1['trade'].astype("float64")
    df1['pricechange']=df1['pricechange'].astype("float64")
    df1['volume']=df1['volume'].astype("int")
    
    #其他选项均作为默认选项
    if not option in ['1','2','3','4','5','6','7']: option='1'    
    if option=='1':
        df1.sort_values(by=['ticktime'],ascending=[True],inplace=True)
        optiontxt="按照交易时间排序"
    if option=='2':
        df1.sort_values(by=['name'],ascending=[True],inplace=True) 
        optiontxt="按照发行时间从早到晚排序"
    if option=='3':
        df1.sort_values(by=['name'],ascending=[False],inplace=True) 
        optiontxt="按照发行时间从晚到早排序"
    if option=='4':
        df1.sort_values(by=['pricechange'],ascending=[False],inplace=True)
        optiontxt="按照涨跌幅从高到低排序"
    if option=='5':
        df1.sort_values(by=['pricechange'],ascending=[True],inplace=True)
        optiontxt="按照涨跌幅从低到高排序"
    if option=='6':
        df1.sort_values(by=['volume'],ascending=[False],inplace=True)
        optiontxt="按照成交量从高到低排序"
    if option=='7':
        df1.sort_values(by=['volume'],ascending=[True],inplace=True)
        optiontxt="按照成交量从低到高排序"
    #重新索引
    df1.reset_index(drop=True)
    
    df2=df1.rename(columns={'ticktime':'时间','symbol':'债券代码', \
            'name':'债券名称','trade':'成交价','pricechange':'涨跌(元)', \
            'open':'开盘价','high':'最高价','low':'最低价', \
            'buy':'买入价','sell':'卖出价','volume':'成交量'})
    
    print("\n*** 沪深交易所债券市场现券即时成交价（"+optiontxt+"，前"+str(num)+"名）***")
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 200) # 设置打印宽度(**重要**)
    print(df2.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n    数据来源：新浪财经，"+today    
    print(footnote)
    
    return df1

if __name__=='__main__':
    num=10
    option='1'
    ebd=exchange_bond_deal(num,option)   
    option='4'
    ebd=exchange_bond_deal(num,option) 
    option='6'
    ebd=exchange_bond_deal(num,option) 

#==============================================================================
def exchange_bond_price(symbol,fromdate,todate):
    """
    功能：获得沪深债券市场历史成交行情
    输入：沪深债券代码symbol，起始日期fromdate，截止日期todate。
    返回：历史价格df
    输出：折线图
    """
    #检查日期期间的合理性
    result,start,end=check_period(fromdate, todate)
    if result is None: return None
    
    #抓取历史行情
    import akshare as ak
    try:
        df=ak.bond_zh_hs_daily(symbol=symbol)
    except:
        print("...Error(exchange_bond_price), 抓取债券信息失败：",symbol)
        return None
    
    #过滤日期期间
    df1=df.drop(df[df.index < start].index)
    df2=df1.drop(df1[df1.index > end].index)
    
    #绘图
    titletxt='沪深债券收盘价历史行情：'+symbol
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n    数据来源：新浪财经，"+today    
    plot_line(df2,'close','收盘价','价格(元)',titletxt,footnote,power=4)
    
    return df
    
if __name__=='__main__':
    symbol='sh143595'
    fromdate='2019-1-1'
    todate='2020-3-30'
    ebp=exchange_bond_price('sh019521',fromdate,todate)

#==============================================================================
def exchange_covbond_deal(num,option='1'):
    """
    功能：获得沪深债券市场可转券即时行情
    输入：从头开始显示的个数num；选项option：默认1按照交易时间排列，
    2按照债券代码从小到大排列，3按照债券代码从大到小排列，4按照涨跌幅从高到低，
    5按照涨跌幅从低到高，6按照成交量从高到低排列，7按照成交量从低到高排列。
    其他选项按照默认排列。
    """
    print("开始搜索互联网，可能需要一点时间，请耐心等候......")
    #定义标准输出关闭类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    import pandas as pd
    df=pd.DataFrame()
    #抓取银行间市场债券报价
    import akshare as ak
    with HiddenPrints():
        try:
            df=ak.bond_zh_hs_cov_spot()
        except:
            pass
    if len(df)==0: 
        print("...错误(exchange_covbond_deal)，抓取信息中途失败，请稍候再试")
        return None    
    
    #选取需要的字段
    df1=df[['ticktime','symbol','name','trade','pricechange','open','high', \
            'low','buy','sell','volume']]
    #转换字符类型到数值类型
    df1['trade']=df1['trade'].astype("float64")
    df1['pricechange']=df1['pricechange'].astype("float64")
    df1['volume']=df1['volume'].astype("int")
    
    #其他选项均作为默认选项
    if not option in ['1','2','3','4','5','6','7']: option='1'    
    if option=='1':
        df1.sort_values(by=['ticktime'],ascending=[True],inplace=True)
        optiontxt="按照交易时间排序"
    if option=='2':
        df1.sort_values(by=['symbol'],ascending=[True],inplace=True) 
        optiontxt="按照代码从小到大排序"
    if option=='3':
        df1.sort_values(by=['symbol'],ascending=[False],inplace=True) 
        optiontxt="按照代码从大到小排序"
    if option=='4':
        df1.sort_values(by=['pricechange'],ascending=[False],inplace=True)
        optiontxt="按照涨跌幅从高到低排序"
    if option=='5':
        df1.sort_values(by=['pricechange'],ascending=[True],inplace=True)
        optiontxt="按照涨跌幅从低到高排序"
    if option=='6':
        df1.sort_values(by=['volume'],ascending=[False],inplace=True)
        optiontxt="按照成交量从高到低排序"
    if option=='7':
        df1.sort_values(by=['volume'],ascending=[True],inplace=True)
        optiontxt="按照成交量从低到高排序"
    #重新索引
    df1.reset_index(drop=True)
    
    df2=df1.rename(columns={'ticktime':'时间','symbol':'债券代码', \
            'name':'债券名称','trade':'成交价','pricechange':'涨跌(元)', \
            'open':'开盘价','high':'最高价','low':'最低价', \
            'buy':'买入价','sell':'卖出价','volume':'成交量'})
    
    print("\n*** 沪深交易所可转债现券即时行情（"+optiontxt+"，前"+str(num)+"名）***")
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 200) # 设置打印宽度(**重要**)
    print(df2.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n    数据来源：新浪财经，"+today    
    print(footnote)
    
    return df1

if __name__=='__main__':
    num=10
    option='1'
    ebd=exchange_covbond_deal(num,option)   
    option='4'
    ebd=exchange_covbond_deal(num,option) 
    option='5'
    ebd=exchange_covbond_deal(num,option) 
    option='6'
    ebd=exchange_covbond_deal(num,option) 
    option='7'
    ebd=exchange_covbond_deal(num,option) 


#==============================================================================
def exchange_covbond_price(symbol,fromdate,todate):
    """
    功能：获得沪深市场可转债历史成交行情
    输入：沪深债券代码symbol，起始日期fromdate，截止日期todate。
    返回：历史价格df
    输出：折线图
    """
    #检查日期期间的合理性
    result,start,end=check_period(fromdate, todate)
    if result is None: return None
    
    #抓取历史行情
    import akshare as ak
    try:
        df=ak.bond_zh_hs_cov_daily(symbol=symbol)
    except:
        print("...Error(exchange_covbond_price), 抓取债券信息失败：",symbol)
        return None    

    #过滤日期期间
    df1=df.drop(df[df.index < start].index)
    df2=df1.drop(df1[df1.index > end].index)
    
    #绘图
    titletxt='沪深市场可转债收盘价历史行情：'+symbol
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n    数据来源：新浪财经，"+today    
    plot_line(df2,'close','收盘价','价格(元)',titletxt,footnote,power=4)
    
    return df
    
if __name__=='__main__':
    symbol='sh113565'
    fromdate='2020-1-1'
    todate='2020-5-6'
    ebp=exchange_covbond_price('sz128086',fromdate,todate)

#==============================================================================
def country_bond_price(country,name,fromdate,todate):
    """
    功能：获得全球政府债券市场历史成交行情
    输入：国家country，政府债券名称name，起始日期fromdate，截止日期todate。
    返回：历史价格df
    输出：折线图
    """
    #检查日期期间的合理性
    result,start,end=check_period(fromdate, todate)
    start_date=start.strftime("%Y/%m/%d")
    end_date=end.strftime("%Y/%m/%d")
    
    if result is None: return None
    
    #抓取历史行情
    import akshare as ak
    try:
        df=ak.get_country_bond(country=country,index_name=name, \
                           start_date=start_date, end_date=end_date)
    except:
        print("...Error(country_bond_price), 抓取债券信息失败：",country,"\b，",name)
        return None 

    #过滤日期期间
    df1=df.drop(df[df.index < start].index)
    df2=df1.drop(df1[df1.index > end].index)
    
    #绘图
    titletxt='全球政府债券收盘价历史行情：'+name
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n    数据来源：英为财情，"+today    
    plot_line(df2,'收盘','收盘价','价格',titletxt,footnote,power=4)
    
    return df
    
if __name__=='__main__':
    country='中国'
    name='中国1年期国债'
    fromdate='2020-1-1'
    todate='2020-5-6'
    cbp=country_bond_price(country,name,fromdate,todate)

#==============================================================================
def bond_eval(aytm,yper,c,fv=100,mterm=1):
    """
    功能：计算债券的估值价格，即现值
    输入：
    aytm: 年化折现率，年化市场利率
    yper: 距离到期日的年数
    c: 票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    """
    #每期折现率
    rate=aytm/mterm
    #每期票息
    pmt=fv*c/mterm
    
    #循环计算现值
    bvalue=0.0
    for t in range(1,yper*mterm+1):
        bvalue=bvalue+pmt/((1+rate)**t)
    bvalue=bvalue+fv/((1+rate)**(yper*mterm))
    
    return bvalue

if __name__=='__main__':
    aytm=0.08
    yper=3
    fv=100
    c=0.1
    bvalue=bond_eval(aytm,yper,c,fv=100,mterm=1)

#==============================================================================
def bond_malkiel1(aytm,yper,c,fv=100,mterm=1, \
                  bp=[-100,-50,-20,-10,-5,5,10,20,50,100]):
    """
    功能：计算债券的估值价格，即现值。演示债券估值定理一。
    输入：
    aytm: 年化折现率，年化市场利率，年化到期收益率
    yper: 距离到期日的年数
    c: 年化票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    bp: 到期收益率变化的基点数列表，100 bp = 1%
    """
    import pandas as pd
    df=pd.DataFrame(columns=('bp','YTM','Price','xLabel'))
    p0=round(bond_eval(aytm,yper,c,fv,mterm),2)
    s=pd.Series({'bp':0,'YTM':aytm,'Price':p0,'xLabel':str(aytm*100)+'%'})
    df=df.append(s, ignore_index=True)
    
    #计算基点变化对于债券估计的影响
    for b in bp:
        ay=aytm + b/10000.0
        pb=round(bond_eval(ay,yper,c,fv,mterm),2)
        
        if b < 0:
            xl='-'+str(abs(b))+'bp'
        elif b > 0:
            xl='+'+str(b)+'bp'
        else:
            xl=str(aytm*100)+'%'
        s=pd.Series({'bp':b,'YTM':ay,'Price':pb,'xLabel':xl})
        df=df.append(s, ignore_index=True)

    #按照到期收益率升序排序
    df.sort_values(by=['YTM'],ascending=[True],inplace=True)
    #指定索引
    df.reset_index(drop=True,inplace=True)
    
    #显示
    df1=df.copy()
    df1['YTM%']=round(df1['YTM']*100,2)
    df2=df1[['xLabel','YTM%','Price']]
    df3=df2.rename(columns={'xLabel':'到期收益率变化','YTM%':'到期收益率%','Price':'债券价格'})
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)    
    print("\n",df3.to_string(index=False))
    
    #绘图
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    plt.rcParams['axes.unicode_minus'] = False      

    plt.plot(df['xLabel'],df['Price'],color='red',marker='o')
    
    #绘制虚线
    xpos=str(aytm*100)+'%'
    ymax=max(df['Price'])
    ymin=min(df['Price'])
    plt.vlines(x=xpos,ymin=ymin,ymax=p0,ls=":",colors="blue")
    
    titletxt="债券价格与到期收益率的关系"
    plt.title(titletxt,fontsize=12)
    plt.ylabel("债券价格")
    footnote1="到期收益率及其变化幅度（100bp = 1%）" 
    footnote2="\n债券"+"面值"+str(fv)+"，票面利率"+str(round(c*100,2))+"%，"
    footnote3="每年付息"+str(mterm)+"次，"+"到期年数"+str(yper)
    footnote4="，到期收益率"+str(round(aytm*100,2))+"%"
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.xlabel(footnote,fontsize=9)    
    plt.tick_params(labelsize=8)
    plt.xticks(rotation=30)
    
    plt.show(); plt.close()
    
    return    

if __name__=='__main__':
    aytm=0.08
    yper=3
    fv=100
    c=0.1
    mterm=1
    bplist=[-100,-50,-20,-10,-5,5,10,20,50,100]
    bond_malkiel1(aytm,yper,c,fv=100,mterm=1,bp=bplist)

#==============================================================================
def bond_malkiel2(aytm,yper,c,fv=100,mterm=1, \
                  yperlist=[1,2,5,10,20,50,100]):
    """
    功能：计算债券估值价格的变化，演示债券估值定理二。
    输入：
    aytm: 年化折现率，年化市场利率，年化到期收益率
    yper: 距离到期日的年数
    c: 年化票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    yperlist: 债券的不同期限年数列表
    """
    import pandas as pd
    df=pd.DataFrame(columns=('Maturity','YTM','Price','deltaPrice','xLabel'))
    p0=round(bond_eval(aytm,yper,c,fv,mterm),2)
    s=pd.Series({'Maturity':yper,'YTM':aytm,'Price':p0,'deltaPrice':0, \
                 'xLabel':str(yper)+'年'})
    df=df.append(s, ignore_index=True)
    
    #计算基点变化对于债券估计的影响
    for y in yperlist:
        pb=round(bond_eval(aytm,y,c,fv,mterm),2)

        s=pd.Series({'Maturity':y,'YTM':aytm,'Price':pb,'deltaPrice':(pb-p0), \
                 'xLabel':str(y)+'年'})
        df=df.append(s, ignore_index=True)

    #按照到期收益率升序排序
    df.sort_values(by=['Maturity'],ascending=[True],inplace=True)
    #指定索引
    df.reset_index(drop=True,inplace=True)
    
    #显示
    df1=df.copy()
    df2=df1[['Maturity','deltaPrice']]
    df3=df2.rename(columns={'Maturity':'债券期限变化(年)','deltaPrice':'债券价格变化'})
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)    
    print("\n",df3.to_string(index=False))
    
    #绘图
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False      

    plt.plot(df['Maturity'],df['deltaPrice'],color='red',marker='o')
    
    #绘制虚线
    xpos=yper
    ymax=0
    ymin=min(df['deltaPrice'])
    plt.vlines(x=xpos,ymin=ymin,ymax=0,ls=":",color="blue")
    plt.axhline(y=0,ls=":",c="black")
    
    titletxt="债券价格的变化与债券期限长短的关系"
    plt.title(titletxt,fontsize=12)
    plt.ylabel("债券价格的变化")
    footnote1="债券期限（年）" 
    footnote2="\n债券"+"面值"+str(fv)+"，票面利率"+str(round(c*100,2))+"%，"
    footnote3="每年付息"+str(mterm)+"次，"+"期限"+str(yper)+"年"
    footnote4="，到期收益率"+str(round(aytm*100,2))+"%"
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.xlabel(footnote,fontsize=9)    
    plt.tick_params(labelsize=8)
    plt.xticks(rotation=30)
    
    plt.show(); plt.close()
    
    return    

if __name__=='__main__':
    aytm=0.08
    yper=3
    fv=100
    c=0.1
    mterm=1
    yperlist=[1,2,5,10,15,30]
    bond_malkiel2(aytm,yper,c,fv,mterm,yperlist=yperlist)

#==============================================================================
def bond_malkiel3(aytm,yper,c,fv=100,mterm=1):
    """
    功能：计算债券的估值价格变化的速度，演示债券估值定理三。
    输入：
    aytm: 年化折现率，年化市场利率，年化到期收益率
    yper: 距离到期日的年数
    c: 年化票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    """
    yperlist=list(range(1,yper*2+2))
    
    import pandas as pd
    df=pd.DataFrame(columns=('Maturity','Price'))
    #计算期限变化对于债券价格的影响
    for y in yperlist:
        pb=round(bond_eval(aytm,y,c,fv,mterm),2)
        s=pd.Series({'Maturity':str(y),'Price':pb})
        df=df.append(s, ignore_index=True)

    #价格变化
    df['deltaPrice']=df['Price'].shift(-1)-df['Price']
    df.dropna(inplace=True)
    
    #价格与价格变化风险双轴折线图
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False      
    fig = plt.figure()

    #绘制左侧纵轴
    ax = fig.add_subplot(111)
    ax.plot(df['Maturity'],df['Price'],'-',label="债券价格", \
             linestyle='-',linewidth=2,color='blue')       
    ax.set_ylabel("债券价格")
    footnote1="债券期限（年）" 
    footnote2="\n债券"+"面值"+str(fv)+"，票面利率"+str(round(c*100,2))+"%，"
    footnote3="每年付息"+str(mterm)+"次，"+"期限"+str(yper)+"年"
    footnote4="，到期收益率"+str(round(aytm*100,2))+"%"
    footnote=footnote1+footnote2+footnote3+footnote4
    ax.set_xlabel(footnote)
    ax.legend(loc='center left')
    
    #绘制垂直虚线
    xpos=yper-1
    ymax=bond_eval(aytm,yper,c,fv,mterm)
    ymin=min(df['Price'])
    plt.vlines(x=xpos,ymin=ymin,ymax=ymax,ls=":",color="black")   

    #绘制右侧纵轴
    ax2 = ax.twinx()
    ax2.plot(df['Maturity'],df['deltaPrice'],'-',label="债券价格变化的速度", \
             linestyle='-.',linewidth=2,color='orange')    
    ax2.set_ylabel("债券价格变化的速度")
    ax2.legend(loc='center right')
    
    titletxt="债券价格受债券期限影响的波动风险"    
    plt.title(titletxt, fontsize=12)
    plt.show(); plt.close()
    
    return    

if __name__=='__main__':
    aytm=0.08
    yper=8
    fv=100
    c=0.1
    mterm=2
    bond_malkiel3(aytm,yper,c,fv,mterm)

#==============================================================================
def bond_malkiel4(aytm,yper,c,fv=100,mterm=1):
    """
    功能：计算债券的估值价格变化，演示债券估值定理四。
    输入：
    aytm: 年化折现率，年化市场利率，年化到期收益率
    yper: 距离到期日的年数
    c: 年化票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    """
    bplist=[-5,-4,-3,-2,-1,1,2,3,4,5]
    import pandas as pd
    df=pd.DataFrame(columns=('bp','YTM','Price','xLabel','deltaPrice'))
    p0=bond_eval(aytm,yper,c,fv,mterm)
    s=pd.Series({'bp':0,'YTM':aytm,'Price':p0,'xLabel':str(aytm*100)+'%','deltaPrice':0})
    df=df.append(s, ignore_index=True)
    
    #计算基点变化对于债券估计的影响
    for b in bplist:
        ay=aytm + b/10000.0
        pb=bond_eval(ay,yper,c,fv,mterm)
        
        if b < 0:
            xl='-'+str(abs(b))+'bp'
        elif b > 0:
            xl='+'+str(b)+'bp'
        else:
            xl=str(aytm*100)+'%'
        s=pd.Series({'bp':b,'YTM':ay,'Price':pb,'xLabel':xl,'deltaPrice':(pb-p0)})
        df=df.append(s, ignore_index=True)

    #按照到期收益率升序排序
    df.sort_values(by=['YTM'],ascending=[True],inplace=True)
    #指定索引
    df.reset_index(drop=True,inplace=True)

    #拆分为收益率降低/上升两部分
    df1=df[df['deltaPrice'] >= 0]
    df2=df[df['deltaPrice'] <= 0]
    
    #将df2“两次翻折”，便于与df1比较
    df3=df2.copy()
    df3['deltaPrice1']=-df3['deltaPrice']
    df3.sort_values(by=['YTM'],ascending=[False],inplace=True)
    df3.reset_index(drop=True,inplace=True)
    df3['xLabel1']=df3['xLabel'].apply(lambda x: x.replace('+','-'))

    #绘图
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    plt.rcParams['axes.unicode_minus'] = False      

    plt.plot(df1['xLabel'],df1['deltaPrice'],color='red',marker='o', \
             label="收益率下降导致的债券价格增加")
    plt.plot(df2['xLabel'],df2['deltaPrice'],color='blue',marker='^', \
             label="收益率上升导致的债券价格下降")
    plt.plot(df3['xLabel1'],df3['deltaPrice1'],':',color='blue',marker='<', \
             label="收益率上升导致的债券价格下降(两次翻折后)")
    plt.axhline(y=0,ls="-.",c="black", linewidth=1)

    #绘制垂直虚线
    xpos=str(aytm*100)+'%'
    ymax=0
    ymin=min(df['deltaPrice'])
    plt.vlines(x=xpos,ymin=ymin,ymax=ymax,ls="-.",color="green",linewidth=1)     
    plt.legend(loc='best')

    titletxt="到期收益率与债券价格变化的非对称性"
    plt.title(titletxt,fontsize=12)
    plt.ylabel("债券价格的变化")
    footnote1="到期收益率及其变化幅度（100bp = 1%）" 
    footnote2="\n债券"+"面值"+str(fv)+"，票面利率"+str(round(c*100,2))+"%，"
    footnote3="每年付息"+str(mterm)+"次，"+"期限"+str(yper)+"年"
    footnote4="，到期收益率"+str(round(aytm*100,2))+"%"
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.xlabel(footnote,fontsize=9)    
    plt.tick_params(labelsize=8)
    plt.xticks(rotation=30)
    
    plt.show(); plt.close()
    
    return    

if __name__=='__main__':
    aytm=0.08
    yper=3
    fv=100
    c=0.1
    mterm=1
    bond_malkiel4(aytm,yper,c,fv=100,mterm=1)

#==============================================================================
def bond_malkiel5(aytm,yper,c,fv=100,mterm=1):
    """
    功能：计算债券的估值价格变化，演示债券估值定理五。
    输入：
    aytm: 年化折现率，年化市场利率，年化到期收益率
    yper: 距离到期日的年数
    c: 年化票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    """
    clist=[-300,-250,-200,-150,-100,-50,50,100,150,200,250]
    import pandas as pd
    df=pd.DataFrame(columns=('bp','c','Price','xLabel'))
    p0=bond_eval(aytm,yper,c,fv,mterm)
    s=pd.Series({'bp':0,'c':c,'Price':p0,'xLabel':str(c*100)+'%'})
    df=df.append(s, ignore_index=True)
    
    #计算基点变化对于债券估计的影响
    for b in clist:
        cb=c + b/10000.0
        if cb <= 0: continue
        pb=bond_eval(aytm,yper,cb,fv,mterm)
        
        if b < 0:
            xl='-'+str(abs(b))+'bp'
        elif b > 0:
            xl='+'+str(b)+'bp'
        else:
            xl=str(c*100)+'%'

        s=pd.Series({'bp':b,'c':cb,'Price':pb,'xLabel':xl})
        df=df.append(s, ignore_index=True)

    #按照到期收益率升序排序
    df.sort_values(by=['c'],ascending=[True],inplace=True)
    #指定索引
    df.reset_index(drop=True,inplace=True)
    #计算价格变化率
    df['deltaPrice']=df['Price']-df['Price'].shift(1)
    df['deltaPrice%']=df['Price'].pct_change()*100.0
    df.dropna(inplace=True)

    #绘图
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    plt.rcParams['axes.unicode_minus'] = False      
    
    df1=df[df['bp'] <= 0]
    df2=df[df['bp'] >= 0]
    plt.plot(df1['xLabel'],df1['deltaPrice%'],color='red',marker='<')    
    plt.plot(df2['xLabel'],df2['deltaPrice%'],color='green',marker='>')

    #绘制垂直虚线
    xpos=str(c*100)+'%'
    ymax=df[df['xLabel']==xpos]['deltaPrice%'].values[0]
    ymin=min(df['deltaPrice%'])
    plt.vlines(x=xpos,ymin=ymin,ymax=ymax,ls="-.",color="blue",linewidth=1)     
    #plt.legend(loc='best')

    titletxt="债券票息率与债券价格变化风险的关系"
    plt.title(titletxt,fontsize=12)
    plt.ylabel("债券价格的变化%")
    footnote1="票息率%及其变化幅度（100bp = 1%）" 
    footnote2="\n债券"+"面值"+str(fv)+"，票面利率"+str(round(c*100,2))+"%，"
    footnote3="每年付息"+str(mterm)+"次，"+"期限"+str(yper)+"年"
    footnote4="，到期收益率"+str(round(aytm*100,2))+"%"
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.xlabel(footnote,fontsize=9)    
    plt.tick_params(labelsize=8)
    plt.xticks(rotation=30)
    
    plt.show(); plt.close()
    
    return 

if __name__=='__main__':
    aytm=0.65
    yper=8
    fv=100
    c=0.7
    mterm=2
    dp=bond_malkiel5(aytm,yper,c,fv,mterm=mterm)

#==============================================================================
def cf_month(c,x,n,f=2,r=0.03):
    """
    功能：计算国债期货的转换因子。
    输入：
    c: 可交割国债的票面利率
    x: 交割月到下一付息月的月份数
    n: 剩余付息次数
    f: 每年付息次数，默认2次
    r: 5年期国债期货合约票面利率，默认3%
    """
    p1=(1+r/f)**(x*f/12)
    p2=c/f
    p3=c/r
    p4=1-p3
    p5=(1+r/f)**(n-1)
    p6=1-x*f/12
    
    cf=(1/p1)*(p2+p3+p4/p5)-p2*p6

    return cf

if __name__=='__main__':
    c=0.026
    x=1
    n=11
    f=2
    r=0.03
    cf_month(c,x,n)
#==============================================================================
def cf_day(c,v,m,f=2,r=0.03):
    """
    功能：计算国债期货的转换因子。
    输入：
    c: 年化票面利率
    v: 到下一付息日的天数
    m: 下一付息日后剩余的付息次数
    f: 每年付息次数，默认2次
    stdrate: 标准利率，默认3%
    """
    #基本折现因子
    p=1/(1+r/f)
    a=p**(v*f/365)
    e=(c/f)*(p*(1-p**m))/(1-p)
    d=p**m
    b=(1-v*f/365)*(c/f)
    
    #假定票面价值为1元
    cf=a*(c/f+e+d)-b

    return cf

if __name__=='__main__':
    c=0.026
    v=30
    m=10
    f=2
    r=0.03
    cf_day(c,v,m)
