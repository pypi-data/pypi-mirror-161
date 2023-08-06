# -*- coding: utf-8 -*-
"""
本模块功能：债券，应用层
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年1月8日
最新修订日期：2020年5月19日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.grafix import *
from siat.common import *
from siat.translate import *
from siat.bond_base import *
#==============================================================================
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=16
ylabel_txt_size=14
xlabel_txt_size=14
legend_txt_size=14

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
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
    curfunc=sys._getframe().f_code.co_name  #获取当前函数名
    #过滤日期
    import pandas as pd
    if fromdate.upper() != '*DEFAULT':
        #测试开始日期的合理性
        try: 
            start=pd.to_datetime(fromdate)
        except:
            print("  #Error("+curfunc+"), invalid date:",fromdate)
            return None 
        df=df.reset_index(drop = True)
        df=df.drop(df[df['releaseTime2']<start].index)
        
    if todate.upper() != '*DEFAULT':
        #测试结束日期的合理性
        try: 
            end=pd.to_datetime(todate)
        except:
            print("  #Error(interbank_bond_issue_monthly), invalid:",todate)
            return None 
        df=df.reset_index(drop = True)
        df=df.drop(df[df['releaseTime2']>end].index)
        
    #检查债券类型
    bondtype=type.upper()
    typelist=['PN','SCP','MTN','ABN','PB','CP','PRN','PB-MTN','DFI','ALL']   
    if not (bondtype in typelist):
        print("  #Error(interbank_bond_issue_monthly), unsupported bond type:",type)
        print("  Supported bond types:",typelist)
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
    titletxt=texttranslate("中国债券市场月发行量")
    if bondtype != 'ALL':
        titletxt=titletxt+"（"+bondtype+"）"
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote=texttranslate("数据来源：中国银行间市场交易商协会(NAFMII)，")+today
    plot_line(ibbim,'issueAmount',texttranslate("发行量"),texttranslate("金额(亿元)"), \
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
    footnote=texttranslate("数据来源：中国银行间市场交易商协会(NAFMII)，")+today
    plot_line(ibbim,'issueAmount',texttranslate("发行量"),texttranslate("金额(亿元)"), \
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
    try:
        df=ak.bond_spot_quote()
    except:
        print("  #Error(interbank_bond_quote): failed to capture bond quotes")
        return None
    
    #其他选项均作为默认选项
    if not option in ['1','2','3','4']: option='1'    
    if option=='1':
        df.sort_values(by=['卖出收益率'],ascending=[False],inplace=True)
        optiontxt=texttranslate("收益率从高到低")
    if option=='2':
        df.sort_values(by=['债券简称'],ascending=[True],inplace=True) 
        optiontxt=texttranslate("发行时间从早到晚")
    if option=='3':
        df.sort_values(by=['债券简称'],ascending=[False],inplace=True) 
        optiontxt=texttranslate("发行时间从晚到早")
    if option=='4':
        df.sort_values(by=['报价机构'],ascending=[True],inplace=True)
        optiontxt=texttranslate("报价机构排序")
    #重新索引
    df.reset_index(drop=True)
    
    print("\n"+texttranslate("中国银行间市场债券现券即时报价")+"（"+optiontxt+texttranslate("，前")+str(num)+texttranslate("名）"))
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    print(df.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n"+texttranslate("数据来源：中国银行间市场交易商协会(NAFMII)，")+today    
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
if __name__=='__main__':
    num=10
    option='1'
    
def interbank_bond_deal(num,option='1'):
    """
    功能：获得银行间债券市场现券成交行情
    输入：从头开始显示的个数num；选项option：默认1按照收益率从高到低排列，
    2按照发行时间从早到晚排列，3按照发行时间从晚到早排列，4按照涨跌幅从高到低，
    5按照涨跌幅从低到高。
    其他选项按照默认排列。
    """
    #抓取银行间市场债券报价，需要akshare-1.4.47版及以后
    import akshare as ak
    df=ak.bond_spot_deal()
    
    #丢弃某些列中有缺失值的行
    df.dropna(axis=0,subset=["加权收益率","涨跌","成交净价"],inplace=True)   
    
    df['加权收益率']=df['加权收益率'].astype('float')
    df['涨跌']=df['涨跌'].astype('float')
    df['成交净价']=df['成交净价'].astype('float')    
        
    #其他选项均作为默认选项
    lang=check_language()
    
    if not option in ['1','2','3','4','5','6','7']: option='1'    
    if option=='1':
        df.sort_values(by=['加权收益率'],ascending=[False],inplace=True)
        if lang == 'Chinese':
            optiontxt=texttranslate("收益率从高到低")
        else:
            optiontxt=texttranslate("Yield High to Low")
            
    if option=='2':
        df.sort_values(by=['债券简称'],ascending=[True],inplace=True) 
        if lang == 'Chinese':
            optiontxt=texttranslate("发行时间从早到晚")
        else:
            optiontxt=texttranslate("Issued Early to Late")
            
    if option=='3':
        df.sort_values(by=['债券简称'],ascending=[False],inplace=True) 
        if lang == 'Chinese':
            optiontxt=texttranslate("发行时间从晚到早")
        else:
            optiontxt=texttranslate("Issued Late to Early")
            
    if option=='4':
        df.sort_values(by=['涨跌'],ascending=[False],inplace=True)
        if lang == 'Chinese':
            optiontxt=texttranslate("涨跌幅从高到低")
        else:
            optiontxt=texttranslate("Change High to Low")
            
    if option=='5':
        df.sort_values(by=['涨跌'],ascending=[True],inplace=True)
        if lang == 'Chinese':
            optiontxt=texttranslate("涨跌幅从低到高")
        else:
            optiontxt=texttranslate("Change Low to High")
            
    if option=='6':
        df.sort_values(by=['成交净价'],ascending=[False],inplace=True)
        if lang == 'Chinese':
            optiontxt=texttranslate("价格从高到低")
        else:
            optiontxt=texttranslate("Price High to Low")

    if option=='7':
        df.sort_values(by=['成交净价'],ascending=[True],inplace=True)
        if lang == 'Chinese':
            optiontxt=texttranslate("价格从低到高")
        else:
            optiontxt=texttranslate("Price Low to High")
            
    #删除不需要的字段
    del df['加权收益率']
    del df['交易量']
    
    #重新索引
    df.reset_index(drop=True,inplace=True)
    
    if lang == 'Chinese':
        print("\n"+texttranslate("银行间债券市场现券成交价（")+optiontxt+texttranslate("，前")+str(num)+texttranslate("名）"))
    else:
        print("\nInterbank Bond Market: Deal Price ("+optiontxt+", Top "+str(num)+")\n")
        
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    
    if lang == 'English':
        df.rename(columns={'债券简称':'Bond Name','成交净价':'Price(Net)','最新收益率':'Latest Yield(bp)','涨跌':'Change(bp)'},inplace=True)
    print(df.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    if lang == 'Chinese':
        footnote1="\n"+texttranslate("注：收益率为百分比，涨跌幅为基点")
        footnote2="\n"+texttranslate("来源：银行间市场交易商协会(NAFMII)，")+today  
    else:
        footnote1=""
        footnote2="\nSource: NAFMII, "+today  
    footnote=footnote1+footnote2
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
if __name__=='__main__':
    num=10
    option='1'

def exchange_bond_deal(num,option='1'):
    """
    功能：获得沪深债券市场现券成交行情
    输入：从头开始显示的个数num；选项option：默认1按照交易时间排列，
    2按照发行时间从早到晚排列，3按照发行时间从晚到早排列，4按照涨跌幅从高到低，
    5按照涨跌幅从低到高，6按照成交量从高到低排列，7按照成交量从低到高排列。
    其他选项按照默认排列。
    """
    print(" Searching data, may take long time in low-speed network, please wait ...\n")
    #定义标准输出关闭类，在Spyder中无效
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
        print("  #Error(exchange_bond_deal)，failed in getting info for now, try later.")
        return None    
    
    #选取需要的字段
    df1=df[['代码','名称','最新价','涨跌幅','昨收','今开','最高', \
            '最低','买入','卖出','成交量']]
    #转换字符类型到数值类型
    df1['最新价']=df1['最新价'].astype("float64")
    df1['涨跌幅']=df1['涨跌幅'].astype("float64")
    df1['成交量']=df1['成交量'].astype("int")
    
    #其他选项均作为默认选项
    if not option in ['2','3','4','5','6','7']: option='2' 
    
    lang=check_language()
    """
    if option=='1':
        df1.sort_values(by=['ticktime'],ascending=[True],inplace=True)
        optiontxt=texttranslate("按照交易时间排序")
    """
    if option=='2':
        df1.sort_values(by=['名称'],ascending=[True],inplace=True) 
        if lang=='Chinese':
            optiontxt=texttranslate("按照债券名称升序排序")
        else:
            optiontxt=texttranslate("by Ascending Name")
            
    if option=='3':
        df1.sort_values(by=['名称'],ascending=[False],inplace=True) 
        if lang=='Chinese':
            optiontxt=texttranslate("按照债券名称降序排序")
        else:
            optiontxt=texttranslate("by Descending Name")
            
    if option=='4':
        df1.sort_values(by=['涨跌幅'],ascending=[False],inplace=True)
        if lang=='Chinese':
            optiontxt=texttranslate("按照涨跌幅从高到低排序")
        else:
            optiontxt=texttranslate("Change High to Low")
            
    if option=='5':
        df1.sort_values(by=['涨跌幅'],ascending=[True],inplace=True)
        if lang=='Chinese':
            optiontxt=texttranslate("按照涨跌幅从低到高排序")
        else:
            optiontxt=texttranslate("Change Low to High")
            
    if option=='6':
        df1.sort_values(by=['成交量'],ascending=[False],inplace=True)
        if lang=='Chinese':
            optiontxt=texttranslate("按照成交量从高到低排序")
        else:
            optiontxt=texttranslate("Volume High to Low")
            
    if option=='7':
        df1.sort_values(by=['成交量'],ascending=[True],inplace=True)
        if lang=='Chinese':
            optiontxt=texttranslate("按照成交量从低到高排序")
        else:
            optiontxt=texttranslate("Volume Low to High")
            
    #重新索引
    df1.reset_index(drop=True,inplace=True)
    """
    df2=df1.rename(columns={'ticktime':texttranslate('时间'),'symbol':texttranslate('债券代码'), \
            'name':texttranslate('债券名称'),'trade':texttranslate('成交价'),'pricechange':texttranslate('涨跌(元)'), \
            'open':texttranslate('开盘价'),'high':texttranslate('最高价'),'low':texttranslate('最低价'), \
            'buy':texttranslate('买入价'),'sell':texttranslate('卖出价'),'volume':texttranslate('成交量')})
    """
    df1b=df1[['代码','名称','最新价','涨跌幅','昨收','成交量']]
    if lang=='Chinese':
        df2=df1b
    else:
        df2=df1b.rename(columns={'代码':'Code','名称':'Bond Name','最新价':'Latest Price', \
                                '涨跌幅':'Change%','昨收':'Last Close','成交量':'Volume'})
    
    if lang=='Chinese':
        print("\n***",texttranslate("沪深交易所债券市场现券即时成交价（")+optiontxt+texttranslate("，前")+str(num)+texttranslate("名）***"))
    else:
        print("\nExchange Bond Market: Deal Price ("+optiontxt+", Top"+str(num)+")\n")
        
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 200) # 设置打印宽度(**重要**)
    print(df2.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    if lang=='Chinese':
        footnote="\n"+texttranslate("数据来源：新浪财经，")+today
    else:
        footnote="\n"+texttranslate("Source: Sina Finance, ")+today
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
if __name__=='__main__':
    symbol='sh019521'
    fromdate='2022-1-1'
    todate='2022-6-30'
    power=4

def exchange_bond_price(symbol,fromdate,todate,power=4):
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
        print("  #Error(exchange_bond_price), failed to get bond info of",symbol)
        return None
    
    #过滤日期期间
    """
    #解决日期比较时类型不一致问题datetime64[ns, UTC] and Timestamp
    import datetime as dt
    import pandas as pd
    df['sdate']=pd.to_datetime(df.index)
    df['s2date']=df['sdate'].dt.date
    df1=df.drop(df[df.s2date < start].index)
    df2=df1.drop(df1[df1.s2date > end].index)
    df2.drop(['sdate','s2date'],axis=1,inplace=True)
    """
    df.set_index('date',inplace=True)
    df['sdate']=pd.to_datetime(df.index)
    df['s2date']=df['sdate'].dt.date
    df1=df.drop(df[df.s2date < start].index)
    df2=df1.drop(df1[df1.s2date > end].index)
    df2.drop(['sdate','s2date'],axis=1,inplace=True)
    
    #绘图
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    lang=check_language()
    if lang=='Chinese':
        titletxt=texttranslate('沪深债券收盘价历史行情：')+codetranslate(symbol)
        footnote="\n"+texttranslate("数据来源：新浪财经，")+today 
        close_txt='收盘价'
        ylabel_txt='价格'
    else:
        titletxt='Exchange Bond Price Trend: '+codetranslate(symbol)
        footnote="Source: Sina Finance, "+today 
        close_txt='Close'
        ylabel_txt='Price'
        
    plot_line(df2,'close',texttranslate(close_txt),texttranslate(ylabel_txt),titletxt,footnote,power=power)
    
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
        print("  #Error(exchange_covbond_deal)，failed to get info, pleae try later.")
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
        optiontxt=texttranslate("按照交易时间排序")
    if option=='2':
        df1.sort_values(by=['symbol'],ascending=[True],inplace=True) 
        optiontxt=texttranslate("按照代码从小到大排序")
    if option=='3':
        df1.sort_values(by=['symbol'],ascending=[False],inplace=True) 
        optiontxt=texttranslate("按照代码从大到小排序")
    if option=='4':
        df1.sort_values(by=['pricechange'],ascending=[False],inplace=True)
        optiontxt=texttranslate("按照涨跌幅从高到低排序")
    if option=='5':
        df1.sort_values(by=['pricechange'],ascending=[True],inplace=True)
        optiontxt=texttranslate("按照涨跌幅从低到高排序")
    if option=='6':
        df1.sort_values(by=['volume'],ascending=[False],inplace=True)
        optiontxt=texttranslate("按照成交量从高到低排序")
    if option=='7':
        df1.sort_values(by=['volume'],ascending=[True],inplace=True)
        optiontxt=texttranslate("按照成交量从低到高排序")
    #重新索引
    df1.reset_index(drop=True)
    
    df2=df1.rename(columns={'ticktime':texttranslate('时间'),'symbol':texttranslate('债券代码'), \
            'name':texttranslate('债券名称'),'trade':texttranslate('成交价'),'pricechange':texttranslate('涨跌(元)'), \
            'open':texttranslate('开盘价'),'high':texttranslate('最高价'),'low':texttranslate('最低价'), \
            'buy':texttranslate('买入价'),'sell':texttranslate('卖出价'),'volume':texttranslate('成交量')})
    
    print("\n***",texttranslate("沪深交易所可转债现券即时行情（")+optiontxt+texttranslate("，前")+str(num)+texttranslate("名）***"))
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 200) # 设置打印宽度(**重要**)
    print(df2.head(num).to_string(index=False))
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n"+texttranslate("数据来源：新浪财经，")+today    
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
if __name__=='__main__':
    symbol='sz128086'
    fromdate='2021-1-1'
    todate='2021-9-16'

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
        print("  #Error(exchange_covbond_price), failed to get info of",symbol)
        return None    

    #过滤日期期间：比较时需要注意时区
    starttz=start.tz_localize('UTC')
    endtz=end.tz_localize('UTC')
    df1=df.drop(df[df.index < starttz].index)
    df2=df1.drop(df1[df1.index > endtz].index)
    
    #绘图
    titletxt=texttranslate('沪深市场可转债收盘价历史行情：')+codetranslate(symbol)
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n"+texttranslate("数据来源：新浪财经，")+today    
    plot_line(df2,'close',texttranslate('收盘价'),texttranslate('价格'),titletxt,footnote,power=4)
    
    return df
    
if __name__=='__main__':
    symbol='sh113565'
    fromdate='2020-1-1'
    todate='2020-5-6'
    ebp=exchange_covbond_price('sz128086',fromdate,todate)

#==============================================================================
if __name__=='__main__':
    country='中国'
    name='中国1年期国债'
    fromdate='2020-1-1'
    todate='2020-5-6'

def country_bond_list(country="中国"):
    """
    功能：获得各国政府债券列表
    输入：国家country
    返回：政府债券列表
    """
    import akshare as ak
    try:
        bond_dict=ak.bond_investing_global_country_name_url(country=country)
    except:
        print("  #Error(country_bond_list), bonds not found for",country)
        return None         
    
    print("***",texttranslate(country),"\b"+texttranslate("政府债券列表"),"***")
    bond_list=bond_dict.keys()
    for b in bond_list:
        print("    ",b)
    
    return
    

def country_bond_price(country,name,fromdate,todate,period="每日"):
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
        """
        #ak似乎不再支持这个函数了
        df=ak.get_country_bond(country=country,index_name=name, \
                           start_date=start_date, end_date=end_date)
        """
        df=ak.bond_investing_global(country=country, index_name=name, \
                    period=period, start_date=start_date, end_date=end_date)
    except:
        print("  #Error(country_bond_price), failed to get info on",texttranslate(country),"\b，",texttranslate(name))
        return None 
    df.sort_index(axis=0, ascending=True,inplace=True)

    #过滤日期期间
    df1=df.drop(df[df.index < start].index)
    df2=df1.drop(df1[df1.index > end].index)
    
    #绘图
    titletxt=texttranslate('全球政府债券收盘价历史行情：')+name
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    footnote="\n"+texttranslate("数据来源：英为财情，")+today    
    plot_line(df2,'收盘',texttranslate('收盘价'),texttranslate('价格'),titletxt,footnote,power=4)
    
    return df
    
if __name__=='__main__':
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
    df3=df2.rename(columns={'xLabel':texttranslate('到期收益率变化'),'YTM%':texttranslate('到期收益率%'),'Price':texttranslate('债券价格')})
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)  
    
    lang=check_language()
    if lang == 'English':
        df4=df3.rename(columns={'到期收益率变化':'YTM Change','到期收益率%':'YTM%','债券价格':'Bond Price'})
    else:
        df4=df3
    print("\n",df4.to_string(index=False))
    
    #绘图
    plt.plot(df['xLabel'],df['Price'],color='red',marker='o')
    
    #绘制虚线
    xpos=str(aytm*100)+'%'
    ymax=max(df['Price'])
    ymin=min(df['Price'])
    plt.vlines(x=xpos,ymin=ymin,ymax=p0,ls=":",colors="blue")
    
    if lang == 'Chinese':
        titletxt=texttranslate("债券价格与到期收益率的关系")
        plt.ylabel(texttranslate("债券价格"),fontsize=ylabel_txt_size)
        footnote1=texttranslate("到期收益率及其变化幅度")+"(100bp = 1%)" 
        footnote2="\n"+texttranslate("债券面值")+str(fv)+texttranslate("，票面利率")+str(round(c*100,2))+"%，"
        footnote3=texttranslate("每年付息")+str(mterm)+texttranslate("次，到期年数")+str(yper)
        footnote4=texttranslate("，到期收益率")+str(round(aytm*100,2))+"%"
    else:
        titletxt="Malkiel\'s Law 1: Relationship btw Bond Price & YTM"
        plt.ylabel("Bond Price",fontsize=ylabel_txt_size)
        footnote1="YTM(100bp = 1%) -->\n" 
        footnote2="Notes: Bond Par Value "+str(fv)+", Coupon Rate "+str(round(c*100,2))+"%.\n"
        footnote3="Annually paid interest "+str(mterm)+" time(s). "
        footnote4="Year(s) to maturity "+str(yper)+", YTM "+str(round(aytm*100,2))+"%"
        
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.title(titletxt,fontsize=title_txt_size,fontweight='bold')
    plt.xlabel(footnote,fontsize=xlabel_txt_size)    
    #plt.tick_params(labelsize=11)
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
    df3=df2.rename(columns={'Maturity':texttranslate('到期时间(年)'),'deltaPrice':texttranslate('债券价格变化')})
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**) 
    
    lang=check_language()
    if lang == 'English':
        df4=df3.rename(columns={'到期时间(年)':'Year(s) to Maturity','债券价格变化':'Bond Price Change'})
    else:
        df4=df3
    print("\n",df4.to_string(index=False))
    
    #绘图
    plt.plot(df['Maturity'],df['deltaPrice'],color='red',marker='o')
    
    #绘制虚线
    xpos=yper
    ymax=0
    ymin=min(df['deltaPrice'])
    plt.vlines(x=xpos,ymin=ymin,ymax=0,ls=":",color="blue")
    plt.axhline(y=0,ls=":",c="black")

    if lang == 'Chinese':
        titletxt=texttranslate("债券价格的变化与到期时间的关系")
        plt.ylabel(texttranslate("债券价格的变化"),fontsize=ylabel_txt_size)
        footnote1=texttranslate("到期时间(年)")+"-->" 
        footnote2="\n"+texttranslate("债券面值")+str(fv)+texttranslate("，票面利率")+str(round(c*100,2))+"%，"
        footnote3=texttranslate("每年付息")+str(mterm)+texttranslate("次，期限")+str(yper)+texttranslate("年")
        footnote4=texttranslate("，到期收益率")+str(round(aytm*100,2))+"%"
    else:
        titletxt="Malkiel\'s Law 2: Relationship btw Bond Price Change & Time to Maturity"
        plt.ylabel("Bond Price Change",fontsize=ylabel_txt_size)
        footnote1="Year(s) to Maturity -->\n" 
        footnote2="Notes: Bond Par Value "+str(fv)+", Coupon Rate "+str(round(c*100,2))+"%.\n"
        footnote3="Annualy paid interest "+str(mterm)+" time(s), Year(s) to maturity "+str(yper)
        footnote4=", YTM "+str(round(aytm*100,2))+"%."
        
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.title(titletxt,fontsize=title_txt_size,fontweight='bold')
    plt.xlabel(footnote,fontsize=xlabel_txt_size)    
    #plt.tick_params(labelsize=11)
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
    fig = plt.figure()

    lang=check_language()
    #绘制左侧纵轴
    ax = fig.add_subplot(111)
    
    if lang == 'Chinese':
        ax.plot(df['Maturity'],df['Price'],'-',label=texttranslate("债券价格"), \
                 linestyle='-',linewidth=2,color='blue')       
        ax.set_ylabel(texttranslate("债券价格"),fontsize=14)
        footnote1=texttranslate("到期时间(年)")+"-->" 
        footnote2="\n"+texttranslate("债券面值")+str(fv)+texttranslate("，票面利率")+str(round(c*100,2))+"%，"
        footnote3=texttranslate("每年付息")+str(mterm)+texttranslate("次，期限")+str(yper)+texttranslate("年")
        footnote4=texttranslate("，到期收益率")+str(round(aytm*100,2))+"%"
    else:
        ax.plot(df['Maturity'],df['Price'],'-',label="Bond Price", \
                 linestyle='-',linewidth=2,color='blue')       
        ax.set_ylabel("Bond Price",fontsize=ylabel_txt_size)
        footnote1="Year(s) to Maturity -->\n" 
        footnote2="Notes: Bond Par Value "+str(fv)+", Coupon Rate "+str(round(c*100,2))+"%.\n"
        footnote3="Annually paid interest "+str(mterm)+" time(s), Year(s) to Maturity "+str(yper)
        footnote4=", YTM "+str(round(aytm*100,2))+"%."
    
    footnote=footnote1+footnote2+footnote3+footnote4
    ax.set_xlabel(footnote,fontsize=xlabel_txt_size)
    ax.legend(loc='center left',fontsize=legend_txt_size)
    
    #绘制垂直虚线
    xpos=yper-1
    ymax=bond_eval(aytm,yper,c,fv,mterm)
    ymin=min(df['Price'])
    plt.vlines(x=xpos,ymin=ymin,ymax=ymax,ls=":",color="black")   

    #绘制右侧纵轴
    ax2 = ax.twinx()
    
    if lang == 'Chinese':
        ax2.plot(df['Maturity'],df['deltaPrice'],'-',label=texttranslate("债券价格的变化速度"), \
                 linestyle='-.',linewidth=2,color='orange')    
        ax2.set_ylabel(texttranslate("债券价格的变化速度"),fontsize=ylabel_txt_size)
    else:
        ax2.plot(df['Maturity'],df['deltaPrice'],'-',label="Bond Price Change Speed", \
                 linestyle='-.',linewidth=2,color='orange')    
        ax2.set_ylabel("Bond Price Change Speed",fontsize=ylabel_txt_size)
    
    ax2.legend(loc='center right',fontsize=legend_txt_size)
    
    if lang == 'Chinese':
        titletxt=texttranslate("债券到期时间与债券价格的变化速度") 
    else:
        titletxt="Malkiel\'s Law 3: Relationship btw Time to Maturity & Bond Price Change Speed"

    plt.title(titletxt, fontsize=title_txt_size,fontweight='bold')
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
def bond_malkiel4(aytm,yper,c,fv=100,mterm=1, \
                 bplist=[-300,-250,-200,-150,-100,-50,50,100,150,200,250,300]):
    """
    功能：计算债券的估值价格变化，演示债券估值定理四。
    输入：
    aytm: 年化折现率，年化市场利率，年化到期收益率
    yper: 距离到期日的年数
    c: 年化票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    """
    #bplist=[-5,-4,-3,-2,-1,1,2,3,4,5]
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
    lang=check_language()
    if lang == 'Chinese':
        plt.plot(df1['xLabel'],df1['deltaPrice'],color='red',marker='o', \
                 label=texttranslate("收益率下降导致的债券价格增加"))
        plt.plot(df2['xLabel'],df2['deltaPrice'],color='blue',marker='^', \
                 label=texttranslate("收益率上升导致的债券价格下降"))
        plt.plot(df3['xLabel1'],df3['deltaPrice1'],':',color='blue',marker='<', \
                 label=texttranslate("收益率上升导致的债券价格下降(两次翻折后)"))
    else:
        plt.plot(df1['xLabel'],df1['deltaPrice'],color='red',marker='o', \
                 label="Increase in bond price due to decreasing YTM")
        plt.plot(df2['xLabel'],df2['deltaPrice'],color='blue',marker='^', \
                 label=texttranslate("Decrease in bond price due to increasing YTM"))
        plt.plot(df3['xLabel1'],df3['deltaPrice1'],':',color='blue',marker='<', \
                 label=texttranslate("Decrease in bond price due to increasing YTM(after 2 folds)"))
        
    plt.axhline(y=0,ls="-.",c="black", linewidth=1)

    #绘制垂直虚线
    xpos=str(aytm*100)+'%'
    ymax=0
    ymin=min(df['deltaPrice'])
    plt.vlines(x=xpos,ymin=ymin,ymax=ymax,ls="-.",color="green",linewidth=1)     
    plt.legend(loc='best',fontsize=legend_txt_size)

    if lang == 'Chinese':
        titletxt=texttranslate("到期收益率与债券价格变化的非对称性")
        plt.ylabel(texttranslate("债券价格的变化"),fontsize=ylabel_txt_size)
        footnote1=texttranslate("到期收益率及其变化幅度")+"（100bp = 1%）" 
        footnote2="\n"+texttranslate("债券面值")+str(fv)+texttranslate("，票面利率")+str(round(c*100,2))+"%，"
        footnote3=texttranslate("每年付息")+str(mterm)+texttranslate("次，期限")+str(yper)+texttranslate("年")
        footnote4=texttranslate("，到期收益率")+str(round(aytm*100,2))+"%"
    else:
        titletxt="Malkiel\'s Law 4: Asymmetry btw YTM & Change in Bond Price"
        plt.ylabel("Change in Bond Price",fontsize=ylabel_txt_size)
        footnote1="YTM(100bp = 1%) -->\n" 
        footnote2="Notes: Bond Par Value "+str(fv)+", Coupon Rate "+str(round(c*100,2))+"%.\n"
        footnote3="Annually paid interest "+str(mterm)+" time(s), Year(s) to Maturity "+str(yper)
        footnote4=", YTM "+str(round(aytm*100,2))+"%."
        
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.xlabel(footnote,fontsize=xlabel_txt_size)    
    #plt.tick_params(labelsize=11)
    plt.xticks(rotation=30)
    plt.title(titletxt,fontsize=title_txt_size,fontweight='bold')
    plt.show(); plt.close()
    
    return    

if __name__=='__main__':
    aytm=0.08
    yper=3
    fv=100
    c=0.1
    mterm=1
    bond_malkiel4(aytm,yper,c,fv,mterm)

#==============================================================================
def bond_malkiel5(aytm,yper,c,fv=100,mterm=1, \
                  clist=[-300,-250,-200,-150,-100,-50,50,100,150,200,250,300]):
    """
    功能：计算债券的估值价格变化，演示债券估值定理五。
    输入：
    aytm: 年化折现率，年化市场利率，年化到期收益率
    yper: 距离到期日的年数
    c: 年化票面利率
    fv: 票面价值
    mterm: 每年付息期数，默认为1，期末付息
    """
    #clist=[-300,-250,-200,-150,-100,-50,50,100,150,200,250,300]
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

    lang=check_language()
    if lang == 'Chinese':
        titletxt=texttranslate("债券票息率与债券价格变化风险的关系")
        plt.ylabel(texttranslate("债券价格的变化速度"),fontsize=ylabel_txt_size)
        footnote1=texttranslate("票息率及其变化幅度")+"（100bp = 1%）-->" 
        footnote2="\n"+texttranslate("债券面值")+str(fv)+texttranslate("，票面利率")+str(round(c*100,2))+"%，"
        footnote3=texttranslate("每年付息")+str(mterm)+texttranslate("次，期限")+str(yper)+texttranslate("年")
        footnote4=texttranslate("，到期收益率")+str(round(aytm*100,2))+"%"
    else:
        titletxt="Malkiel\'s Law 5: Relationship btw Coupon Rate & Bond Price Risk"
        plt.ylabel("Bond Price Change Speed (Risk)",fontsize=ylabel_txt_size)
        footnote1="Coupon Rate(100bp = 1%) -->\n" 
        footnote2="Notes: Bond Par Value "+str(fv)+", Coupon Rate "+str(round(c*100,2))+"%,\n"
        footnote3="Annually paid interest "+str(mterm)+" time(s), Year(s) to Maturity "+str(yper)
        footnote4=", YTM "+str(round(aytm*100,2))+"%."
        
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.xlabel(footnote,fontsize=xlabel_txt_size)    
    #plt.tick_params(labelsize=11)
    plt.xticks(rotation=30)
    plt.title(titletxt,fontsize=title_txt_size,fontweight='bold')
    plt.show(); plt.close()
    
    return 

if __name__=='__main__':
    aytm=0.65
    yper=8
    fv=100
    c=0.7
    mterm=2
    dp=bond_malkiel5(aytm,yper,c,fv,mterm)

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

    return round(cf,4)

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

    return round(cf,4)

if __name__=='__main__':
    c=0.026
    v=30
    m=10
    f=2
    r=0.03
    cf_day(c,v,m)

#==============================================================================
if __name__=='__main__':
    clist=[0.02,0.0225,0.025,0.0275,0.03,0.035,0.04,0.05,0.06]
    v=30
    m=10
    f=2
    r=0.03

def cf_day_coupon_trend(clist,v,m,f=2,r=0.03):
    """
    功能：计算国债期货的转换因子。
    输入：
    clist: 债券票息率列表（年化票面利率）
    v: 到下一付息日的天数
    m: 下一付息日后剩余的付息次数
    f: 每年付息次数，默认2次
    stdrate: 标准利率，默认3%
    """

    #检查clist是否列表
    if not isinstance(clist,list):
        print("  #Error(cf_day_coupon_trend): not a list of rates from",clist)
        return None
    if len(clist) < 3:
        print("  #Error(cf_day_coupon_trend): not enough rates for showing trend",clist)
        return None
    
    #计算各个票息率的转换因子
    import pandas as pd
    df=pd.DataFrame(columns=('c','v','m','f','r','cf'))
    for c in clist:
        cf=cf_day(c,v,m,f,r)
        s=pd.Series({'c':c,'v':v,'m':m,'f':f,'r':r,'cf':cf})
        df=df.append(s, ignore_index=True)

    #按照到期收益率升序排序
    df.sort_values(by=['c'],ascending=[True],inplace=True)
    #指定索引
    df['crate']=df['c']
    df.set_index(['crate'],inplace=True)

    #打印
    print("\n***",texttranslate("债券票息率对转换因子的影响"),"***")
    print(texttranslate("名义券利率                 :"),r)
    print(texttranslate("每年付息次数               :"),f)
    print(texttranslate("到下个付息日的天数         :"),v)
    print(texttranslate("下个付息日后剩余的付息次数 :"),m)
    
    df1=df[['c','cf']].copy()
    df2=df1.rename(columns={'c':texttranslate('债券票息率'),'cf':texttranslate('转换因子')})
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)    
    print("\n",df2.to_string(index=False))
        
    #绘图    
    colname='cf'
    collabel=texttranslate('债券的转换因子')
    ylabeltxt=texttranslate('转换因子')
    titletxt=texttranslate("债券票息率对转换因子的影响")
    footnote=texttranslate('票息率')+' -->'+ \
        "\n"+texttranslate("【债券描述】名义券利率：")+str(r)+texttranslate(', 每年付息次数：')+str(f)+ \
        "\n"+texttranslate("到下个付息日的天数：")+str(v)+", "+texttranslate("下一付息日后剩余的付息次数：")+str(m)
    plot_line(df,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df

if __name__=='__main__':
    clist=[0.0225,0.025,0.0275,0.03,0.04,0.06,0.08,0.1]
    v=30
    m=10
    df=cf_day_coupon_trend(clist,v,m)

#==============================================================================
if __name__=='__main__':
    c=0.026
    v=30
    mlist=[4,6,8,10,12,14,16]
    f=2
    r=0.03

def cf_day_remain_trend(c,v,mlist,f=2,r=0.03):
    """
    功能：计算国债期货的转换因子。
    输入：
    c: 债券票息率（年化票面利率）
    v: 到下一付息日的天数
    mlist: 下一付息日后剩余的付息次数列表
    f: 每年付息次数，默认2次
    stdrate: 名义券利率，默认3%
    """

    #检查mlist是否列表
    if not isinstance(mlist,list):
        print("#Error(cf_day_remain_trend): not a list of payment times",mlist)
        return None
    if len(mlist) < 3:
        print("#Error(cf_day_remain_trend): not enough times for showing trend",mlist)
        return None
    
    #计算各个票息率的转换因子
    import pandas as pd
    df=pd.DataFrame(columns=('c','v','m','f','r','cf'))
    for m in mlist:
        cf=cf_day(c,v,m,f,r)
        s=pd.Series({'c':c,'v':v,'m':m,'f':f,'r':r,'cf':cf})
        df=df.append(s, ignore_index=True)

    #按照到期收益率升序排序
    df.sort_values(by=['m'],ascending=[True],inplace=True)
    #指定索引
    df['mtimes']=df['m']
    df.set_index(['mtimes'],inplace=True)

    #打印
    print("\n"+texttranslate("到期期限对债券转换因子的影响"))
    print(texttranslate("名义券利率         :"),r)
    print(texttranslate("债券票面利率       :"),c)
    print(texttranslate("每年付息次数       :"),f)
    print(texttranslate("到下个付息日的天数 :"),v)
    
    df1=df[['m','cf']].copy()
    df2=df1.rename(columns={'m':texttranslate('债券到期期限*'),'cf':texttranslate('转换因子')})
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)    
    print("\n",df2.to_string(index=False))
    print(texttranslate("*指下一付息日后剩余的付息次数"))
        
    #绘图    
    colname='cf'
    collabel=texttranslate('债券的转换因子')
    ylabeltxt=texttranslate('转换因子')
    titletxt=texttranslate("到期期限对债券转换因子的影响")
    footnote=texttranslate('下一付息日后剩余的付息次数')+' -->'+ \
        "\n"+texttranslate("【债券描述】名义券利率：")+str(r)+texttranslate(", 债券票面利率：")+str(c)+texttranslate(', 每年付息次数：')+str(f)+ \
        "\n"+texttranslate("到下一付息日的天数：")+str(v)
    plot_line(df,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df

if __name__=='__main__':
    df=cf_day_remain_trend(c,v,mlist)

#==============================================================================
#==============================================================================
#==============================================================================
# 以下内容来自中债信息网
#==============================================================================
import requests
import datetime
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
CHINABOND_TERM_MAP = {
    '0': '总值',
    '1': '1年以下',
    '2': '1-3年',
    '3': '3-5年',
    '4': '5-7年',
    '5': '7-10年',
    '6': '10年以上',
}

def get_chinabond_index_list():
    """
    功能：获取债券指数列表，来源：中国债券信息网
    问题：数据源网址可能已经变化，目前无法抓取数据
    """
    headers = {
        'Referer': 'https://yield.chinabond.com.cn/',
        'User-Agent': UA,
    }

    url = 'https://yield.chinabond.com.cn/cbweb-mn/indices/queryTree'
    params = {
        'locale': 'zh_CN',
    }
    try:
        r = requests.post(url, data=params, headers=headers, timeout=10)
    except requests.exceptions.RequestException:
        print("  #Error(get_chinabond_index_list): spider failed with return",r.text)
        return None

    try:
        data = r.json()
    except:
        print("  #Error(get_chinabond_index_list): failed to decode json.")
        return None
        
    indexes = [i for i in data if i['isParent'] == 'false']

    return indexes    
    
if __name__=='__main__':
    indexlist=get_chinabond_index_list()

#==============================================================================
if __name__=='__main__':
    keystr='国债'
    
def search_bond_index_china(keystr='国债',printout=True):
    """
    功能：基于关键词搜索中债指数名字
    """
    print("  Searching China bond index names with keyword",keystr,'......')

    indexlist=get_chinabond_index_list()
    if indexlist is None:
        print("  #Error(search_bond_index_china): no bond info found for",keystr)
        if printout: return
        else: return None
    
    import pandas as pd
    indexdf=pd.DataFrame(indexlist)
    
    subdf=indexdf[indexdf['name'].str.contains(keystr)]
    
    subdflen=len(subdf)
    if subdflen == 0:
        print("  Sorry, bond index name(s) not found with keyword",keystr,'\b:-(')
        keylist1=['国债','政府债','金融债','信用债','企业债','绿色债','铁路债']        
        keylist2=['利率债','路债','行债','区债','央票','短融','综合','银行间']
        keylist=keylist1+keylist2
        print("  Try one of these keywords:",keylist)
        
        if printout: return
        else: return None
    
    if printout:
        print(subdf['name'].to_string(index=False))
        print("  Found",subdflen,"China bond index names with keyword",keystr,'\b:-)')
        return
    else: return subdf
            

if __name__=='__main__':
    search_bond_index_china(keystr='国债')    
    search_bond_index_china(keystr='综合')
    search_bond_index_china(keystr='银行间')
#==============================================================================
if __name__=='__main__':
    name='中债-综合指数'
    fromdate='2020-1-1'
    todate='2021-2-8'
    graph=True
    power=6

def bond_index_china(name,fromdate,todate,graph=True,power=5):
    """
    功能：获取中债债券指数的价格，按日期升序排列
    """
    #检查日期区间的合理性
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(bond_index_china): invalid date period from",fromdate,'to',todate)
        if graph: return
        else: return None  
    
    #将债券指数名字转换成中债网的债券指数id
    subdf=search_bond_index_china(keystr=name,printout=False)
    if subdf is None:
        print("  #Error(bond_index_china): none bond index found for",name)
        if graph: return
        else: return None
    
    subdflen=len(subdf)
    #错误：未找到债券指数名字
    if subdflen == 0:
        print("  #Error(bond_index_china): empty bond index found for",name)
        if graph: return
        else: return None
    #错误：找到多个债券指数名字
    if subdflen > 1:
        print("  #Error(bond_index_china): found more than one bond indexes")
        print(subdf['name'].to_string(index=False))
        if graph: return
        else: return None    
    
    #基于指数id提取历史价格
    indexid=subdf['id'].values[0]
    indexdictlist=get_chinabond_index(indexid)
    if indexdictlist is None:
        return None
    
    import pandas as pd
    newname=name+"-总值-财富"
    for i in indexdictlist:
        if i['name'] == newname:
            idf=pd.DataFrame(i['history'])
            break

    #整理历史价格
    idf.columns=['Date','Close']
    idf['date']=pd.to_datetime(idf['Date'])
    idf.set_index(['date'],inplace=True)
    idf['Adj Close']=idf['Close']
    idf['ticker']=name
    idf['footnote']=''
    idf['source']=texttranslate('中国债券信息网')
    
    idf1=idf[idf.index >= start]
    idf2=idf1[idf1.index < end]
    
    num=len(idf2)
    print("  Successfully retrieved",num,"records for",name)
    
    #不绘图
    if not graph: return idf2
    #绘图
    colname='Close'
    collabel=name
    ylabeltxt=texttranslate('指数点数')
    titletxt=texttranslate("中国债券价格指数走势")
    
    import datetime as dt; today=dt.date.today()    
    footnote=texttranslate("数据来源：中债登/中国债券信息网，")+str(today)
    plot_line(idf2,colname,collabel,ylabeltxt,titletxt,footnote,power=power)

    return

if __name__=='__main__':
    bond_index_china('中债-综合指数','2020-1-1','2021-2-8')
    bond_index_china('中债-国债总指数','2020-1-1','2021-2-8')
    bond_index_china('中债-交易所国债指数','2020-1-1','2021-2-8')    
    bond_index_china('中债-银行间国债指数','2020-1-1','2021-2-8')
    bond_index_china('中债-银行间债券总指数','2020-1-1','2021-2-8')
    
    
#==============================================================================
#@functools.lru_cache
def get_chinabond_index_id_name_map():
    indexes = get_chinabond_index_list()
    if indexes is None:
        return None
    
    id_nam_map = {i['id']: i for i in indexes}
    return id_nam_map

if __name__=='__main__':
    indexnamelist=get_chinabond_index_id_name_map()

#==============================================================================

def get_chinabond_index(indexid):
    
    """
    基于中债指数索引编号抓取指数历史数据
    """
    
    headers = {
        #'Referer': 'http://yield.chinabond.com.cn/',
        'Referer': 'https://yield.chinabond.com.cn',
        'User-Agent': UA,
    }

    #url = 'http://yield.chinabond.com.cn/cbweb-mn/indices/singleIndexQuery'
    #url = 'https://yield.chinabond.com.cn/cbweb-mn/indices/singleIndexQuery'
    url = 'https://yield.chinabond.com.cn/cbweb-mn/indices/single_index_query?locale=zh_CN'
    params = {
        'indexid': indexid,
        'zslxt': 'CFZS',
        'qxlxt': '0,1,2,3,4,5,6',
        'lx': '1',
        'locale': 'zh_CN',
    }
    # zslxt  指数类型，可以多个
    #   CFZS    财富指数
    #   JJZS    净价指数
    #   QJZS    全价指数
    ##
    # qxlxt  期限类型
    #     0     总值
    #     1     1年以下
    #     2     1-3年
    #     3     3-5年
    #     4     5-7年
    #     5     7-10年
    #     6     10年以上
    try:
        #r = requests.post(url, data=params, headers=headers, timeout=4)
        r = requests.post(url, data=params, headers=headers, timeout=4)
    except requests.exceptions.RequestException:
        #r = requests.post(url, data=params, headers=headers, timeout=10)
        r = requests.post(url, data=params, headers=headers, timeout=10)

    try:
        data = r.json()
    except:
        print("  #Error(get_chinabond_index): inaccessible to bond index id",indexid)
        return None
    
    import datetime as dt
    indexes = []
    index_id_name_map = get_chinabond_index_id_name_map()
    index_name = index_id_name_map[indexid]['name']
    for key in data:
        if not data[key]:
            continue
        if key.startswith('CFZS_'):
            type_ = '财富'
            term = CHINABOND_TERM_MAP[key[5:]]
        else:
            continue
        name = f'{index_name}-{term}-{type_}'
        history = []
        for ts, val in data[key].items():
            ts = dt.datetime.fromtimestamp(int(ts) / 1000).strftime('%Y-%m-%d')
            history.append([ts, val])
        history.sort(key=lambda x: x[0])

        index = {
            'source': 'chinabond',
            'code': name,
            'indexid': indexid,
            'name': name,
            'history': history,
        }

        indexes.append(index)
    
    return indexes

#==============================================================================