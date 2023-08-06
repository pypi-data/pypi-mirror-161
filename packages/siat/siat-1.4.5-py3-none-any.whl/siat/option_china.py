# -*- coding: utf-8 -*-

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================

from siat.common import *
from siat.grafix import *
from siat.security_prices import *
from siat.option_pricing import *
from siat.fama_french import *

import pandas as pd
#==============================================================================
if __name__=='__main__':
    symbol='黄金期权'

def option_comm_dict_china(symbol):
    """
    获取中国商品期权大类合约
    显示symbol类期权的可用合约列表
    """
    import akshare as ak
    import datetime
    today = datetime.date.today()
    
    try:
        optiondict=ak.option_sina_commodity_dict(symbol=symbol)
        print("\n中国"+symbol+"的可用合约：")
        contractlist=optiondict[symbol]
        contractlist.sort(reverse=False)
        #print(contractlist)
        printlist(contractlist,numperline=8,beforehand=' '*4,separator=' ')
        print('*** 注：合约代码后四位数字为合约到期日YYMM')
        print('    每种合约还将分为看涨(C)/看跌(P)两个方向和不同的行权价')
        print('    数据来源：新浪财经,',today)
        return optiondict
    except:
        print("  #Error(option_com_china): failed to get dict info for",symbol)
        print("  Solution: upgrade siat and akshare plug-in, then try again")
        print("  If problem remains, report to the author via wechat or email.")
        return None    

if __name__=='__main__':
    df=option_comm_dict_china(symbol='黄金期权')
#==============================================================================
if __name__=='__main__':
    underlying='黄金'
    contract='au2204'
def option_comm_china(underlying='',contract=''):
    """
    获取中国商品期权大类
    若underlying=''或错误且contract=''时显示中国商品期权大类
    若underlying查到且contract=''或未查到时显示该类期权的合约列表
    若underlying查到且contract查到时显示该类期权合约的价格与持仓量分析
    """
    import akshare as ak
    import datetime
    today = datetime.date.today()
    
    underlyinglist=['豆粕','玉米','铁矿石','棉花','白糖','PTA','甲醇','橡胶','沪铜','黄金','菜籽粕','液化石油气','动力煤']
    if not (underlying in underlyinglist):
        print("\n中国商品期权的常见品种：")
        #print(underlyinglist)
        printlist(underlyinglist,numperline=6,beforehand=' '*4,separator=' ')
        print('*** 数据来源：新浪财经,',today)
        return underlyinglist
    
    symbol=underlying+'期权'
    if (underlying in underlyinglist) and (contract==''):
        optiondict=option_comm_dict_china(symbol)
        return optiondict
        
    try:
        df2=ak.option_sina_commodity_contract_list(symbol=symbol,contract=contract)
    except:
        print("  #Error(option_com_china): contract",contract,'not found in',symbol)
        optiondict=option_comm_dict_china(symbol)
        return optiondict 
    
    df2cols=['买量C','买价C','最新价C','卖价C','卖量C','持仓量C','涨跌C','行权价','看涨期权合约','买量P','买价P','最新价P','卖价P','卖量P','持仓量P','涨跌P','看跌期权合约']
    df2.columns=df2cols

    df2['最新价C']=df2['最新价C'].astype('float')
    df2['持仓量C']=df2['持仓量C'].astype('float')
    df2['最新价P']=df2['最新价P'].astype('float')
    df2['持仓量P']=df2['持仓量P'].astype('float')
    df2['行权价']=df2['行权价'].astype('float')
    df2.set_index('行权价',inplace=True)
    
    df2c=df2['看涨期权合约']
    df2c.dropna(inplace=True)
    df2clist=list(df2c)
    print("  \n中国"+symbol+contract+"的看涨期权合约：")
    printlist(df2clist,numperline=6,beforehand=' '*4,separator=' ')
    df2p=df2['看跌期权合约']
    df2p.dropna(inplace=True)
    df2plist=list(df2p)
    print("  \n中国"+symbol+contract+"的看跌期权合约：")  
    printlist(df2plist,numperline=6,beforehand=' '*4,separator=' ')

    footnote="行权价-->\n\n"+"数据来源：新浪财经，"+str(today)

    print("\nRendering graphics for the relationships btw contract and strike prices...")
    titletxt="当前期权价格与行权价的关系："+symbol+contract
    plot_line2(df2,"看涨期权",'最新价C','价格', \
                 df2,"看跌期权",'最新价P','价格', \
                 '价格',titletxt,footnote,power=0,twinx=False)
    """
    print("Rendering graphics for the relationships btw call price and open interest ...")
    titletxt="当前期权价格与持仓量的关系："+symbol+contract+'的'+"看涨期权"
    plot_line2(df2,"看涨期权",'最新价C','价格', \
                 df2,"看涨期权",'持仓量C','持仓量', \
                 '',titletxt,footnote,power=0,twinx=True)

    print("Rendering graphics for the relationships btw put price and open interest ...")
    titletxt="当前期权价格与持仓量的关系："+symbol+contract+'的'+"看跌期权"
    plot_line2(df2,"看跌期权",'最新价P','价格', \
                 df2,"看跌期权",'持仓量P','持仓量', \
                 '',titletxt,footnote,power=0,twinx=True)

    print("Rendering graphics for the relationships btw open interests ...")
    titletxt="当前期权方向与持仓量的关系："+symbol+contract
    plot_line2(df2,"看涨期权",'持仓量C','持仓量', \
                 df2,"看跌期权",'持仓量P','持仓量', \
                 '',titletxt,footnote,power=0,twinx=False)
    """
    return df2
#==============================================================================
#==============================================================================
if __name__=='__main__':
    contract='au2112C328'
    contract=['au2112C328','au2112P328']
    contract=[]
    power=0
    twinx=False
    start='2021-8-1'
    end='2021-8-31'

def option_comm_trend_china(contract,start='',end='',power=0,twinx=False):
    """
    绘制期权合约价格历史价格趋势图
    若contract为一个合约，则绘制单折线图
    若contract为多于一个合约，则绘制前两个合约的双单折线图
    """
    
    contract1=contract2=''
    if isinstance(contract,str):
        contract1=contract
        contract2=''
    
    if isinstance(contract,list):
        if len(contract)==1:
            contract1=contract
            contract2=''    
        elif len(contract)>=2:
            contract1=contract[0]
            contract2=contract[1]    
            
    if contract1=='':
        print("  #Error(option_comm_trend_china): unknown option contract",contract)
        return None

    import pandas as pd
    start1=end1=''
    if not (start==''):
        try:
            start1=pd.to_datetime(start)
        except:
            print("  #Error(option_comm_trend_china): invalid date",start)
    if not (end==''):
        try:
            end1=pd.to_datetime(end)
        except:
            print("  #Error(option_comm_trend_china): invalid date",end)
    
    import akshare as ak
    import datetime
    today = datetime.date.today()
    footnote="数据来源：新浪财经，"+str(today)
    
    #绘制单折线
    if contract2=='':
        contract1,dict1=option_comm_contract_decode_china(contract1)
        try:
            df3=ak.option_sina_commodity_hist(contract=contract1)    
        except:
            print("  #Error(option_comm_trend_china): contract",contract1,"not found")
            return None
        
        if len(df3)==0:
            print("  #Warning(option_comm_trend_china): no record found for contract",contract1)
            return None            
        
        df3['date2']=pd.to_datetime(df3['date'])
        df3.set_index('date2',inplace=True)
        df3['close']=df3['close'].astype('float')
        
        if not (start1==''):
            df3=df3.drop(df3[df3.index < start1].index)
        if not (end1==''):
            df3=df3.drop(df3[df3.index > end1].index)        

        print("  Rendering graphics for option contract price trend...")
        titletxt="期权合约价格的运动趋势："+contract1
        footnote=contract1+'：'+dict1['标的物']+dict1['期权方向']+'，'+dict1['到期日']+'到期'+'，行权价'+dict1['行权价']+'\n'+footnote
        plot_line(df3,'close','收盘价','价格',titletxt,footnote,power=power)
        return df3
    
    #绘制双折线
    contract1ok=contract2ok=True
    if not (contract2==''):
        contract1,dict1=option_comm_contract_decode_china(contract1)
        try:
            df31=ak.option_sina_commodity_hist(contract=contract1)   
            df31['date2']=pd.to_datetime(df31['date'])
            df31.set_index('date2',inplace=True)
            df31['close']=df31['close'].astype('float')
        except:
            contract1ok=False
        if contract1ok:
            if not (start1==''):
                df31=df31.drop(df31[df31.index < start1].index)
            if not (end1==''):
                df31=df31.drop(df31[df31.index > end1].index)            

            if len(df31)==0:
                #print("  #Warning(option_comm_trend_china): no record found for contract",contract1)
                contract1ok=False
        
        contract2,dict2=option_comm_contract_decode_china(contract2)
        try:
            df32=ak.option_sina_commodity_hist(contract=contract2) 
            df32['date2']=pd.to_datetime(df32['date'])
            df32.set_index('date2',inplace=True)
            df32['close']=df32['close'].astype('float')
        except:
            contract2ok=False
        if contract2ok:
            if not (start1==''):
                df32=df32.drop(df32[df32.index < start1].index)
            if not (end1==''):
                df32=df32.drop(df32[df32.index > end1].index)   

            if len(df32)==0:
                #print("  #Warning(option_comm_trend_china): no record found for contract",contract2)
                contract2ok=False
        
        if contract1ok and contract2ok:
            print("  Rendering graphics for comparing two option contract price trends...")
            titletxt="期权价格的运动趋势对比："+contract1+'与'+contract2
            footnote=contract2+'：'+dict2['标的物']+dict2['期权方向']+'，'+dict2['到期日']+'到期'+'，行权价'+dict2['行权价']+'\n'+footnote
            footnote=contract1+'：'+dict1['标的物']+dict1['期权方向']+'，'+dict1['到期日']+'到期'+'，行权价'+dict1['行权价']+'\n'+footnote
            
            plot_line2(df31,contract1,'close','收盘价', \
                   df32,contract2,'close','收盘价', \
                       '价格',titletxt,footnote,twinx=twinx)
            return df31,df32
        elif contract1ok:
            print("  Rendering graphics for option contract price trend...")
            titletxt="期权合约价格的运动趋势："+contract1
            footnote=contract1+'：'+dict1['标的物']+dict1['期权方向']+'，'+dict1['到期日']+'到期'+'，行权价'+dict1['行权价']+'\n'+footnote
            
            plot_line(df31,'close','收盘价','价格',titletxt,footnote,power=power)
            return df31            
        elif contract2ok:
            print("  Rendering graphics for option contract price trend...")
            titletxt="期权合约价格的运动趋势："+contract2
            footnote=contract2+'：'+dict2['标的物']+dict2['期权方向']+'，'+dict2['到期日']+'到期'+'，行权价'+dict2['行权价']+'\n'+footnote
            
            plot_line(df32,'close','收盘价','价格',titletxt,footnote,power=power)
            return df32  
        else:
            print("  #Warning(option_comm_trend_china): no record found for contracts",contract1,'and',contract2)
            return None
        
#==============================================================================
if __name__=='__main__':
    contract='xu2112'
    contract='au2112C328'
    
def option_comm_contract_decode_china(contract):
    """
    例：
    contract='c2111'或'cf2111'
    contract='c2111C235'或'cf2111P235'
    """
    
    prelist=['m','c','i','cf','sr','ta','ma','ru','cu','au','rm','pg','zc']
    ualist=['豆粕','玉米','铁矿石','棉花','白糖','PTA','甲醇','橡胶','沪铜','黄金','菜籽粕','液化石油气','动力煤']
    
    import string
    ucletters=list(string.ascii_uppercase)    
    lcletters=list(string.ascii_lowercase)
    
    pos=0
    contract1=contract.lower()
    for c in contract1:
        if c in lcletters:
            pos=pos+1
        else:
            break
    prefix=contract1[:pos]
    yymm=contract1[pos:pos+4]
    maturity='20'+yymm[:2]+'-'+yymm[2:] #到期年月
    
    direction=''
    strike=''
    if len(contract1)>6:
        direction=contract1[pos+4:pos+5]
        direction=direction.upper()     #期权方向
        contract2=contract1[:pos+4]+direction+contract1[pos+5:]
        strike=contract1[pos+5:]        #行权价 

        if direction=='C':
            otype="看涨期权"
        elif direction=='P':
            otype="看跌期权"
        else:
            otype="未知"
    else:
        contract2=contract1
    
    try:
        pos1=prelist.index(prefix)
        ua=ualist[pos1]                 #期权标的物类别
    except:
        print("  #Error(option_comm_contract_decode_china): contract",contract,"not found")
        return None,None
    
    contract_notes={}
    contract_notes['合约']=contract2
    contract_notes['标的物']=ua
    contract_notes['到期日']=maturity
    if not (direction==''):
        contract_notes['期权方向']=otype
    if not (strike==''):
        contract_notes['行权价']=strike
    
    
    return contract2,contract_notes
#==============================================================================
#==============================================================================
# 以上为商品期权，以下为金融期权
#==============================================================================
#==============================================================================
if __name__=='__main__':
    detail=True
    detail=False
    
# 定义中国当前金融期权的所有品种   
option_fin_list=["华夏上证50ETF期权","华泰柏瑞沪深300ETF期权","嘉实沪深300ETF期权", \
                 "沪深300股指期权"]
underlying_fin_list=["510050.SS","510300.SS","159919.SZ","000300.SS"]
    
def option_fin_china(detail=False):
    """
    功能：描述当前中国市场中的金融期权，标注日期
    """
    
    if detail:
        heading="\n***"
    else:
        heading=' '
    lead_blanks=' '*3
    
    print("===== 中国金融期权表 =====")
    #华夏上证50ETF期权
    print(heading,"华夏上证50ETF期权")
    if detail:
        print(lead_blanks,"其他名称：上证50ETF期权")
        print(lead_blanks,"类别    ：欧式期权，无红利")
        print(lead_blanks,"标的证券：华夏上证50ETF基金（510050.SS）")
        #print(lead_blanks,"行权价格：1个平值合约、4个虚值合约、4个实值合约")
        print(lead_blanks,"上市日期：2015-2-9")
        print(lead_blanks,"到期月份：当月、下月及随后两个季月（季度末月）")
        print(lead_blanks,"到期日期：到期月份的第四个星期三（节假日顺延）")
        print(lead_blanks,"交易所  ：上海证券交易所")
    
    #华泰柏瑞沪深300ETF期权
    print(heading,"华泰柏瑞沪深300ETF期权")
    if detail:
        print(lead_blanks,"其他名称：上证沪深300ETF期权")
        print(lead_blanks,"类别    ：欧式期权，无红利")
        print(lead_blanks,"标的证券：华泰柏瑞沪深300ETF基金（510300.SS）")
        print(lead_blanks,"上市日期：2019-12-23")
        #print(lead_blanks,"行权价格：1个平值合约、4个虚值合约、4个实值合约")
        print(lead_blanks,"到期月份：当月、下月及随后两个季月（季度末月）")
        print(lead_blanks,"到期日期：到期月份的第四个星期三（节假日顺延）")
        print(lead_blanks,"交易所  ：上海证券交易所")   
    
    #嘉实沪深300ETF期权
    print(heading,"嘉实沪深300ETF期权")
    if detail:
        print(lead_blanks,"其他名称：深交所沪深300ETF期权")
        print(lead_blanks,"类别    ：欧式期权，无红利")
        print(lead_blanks,"标的证券：嘉实沪深300ETF基金（159919.SZ）")
        print(lead_blanks,"上市日期：2019-12-23")
        #print(lead_blanks,"行权价格：1个平值合约、4个虚值合约、4个实值合约")
        print(lead_blanks,"到期月份：1、2、3、6月")
        print(lead_blanks,"到期日期：到期月份的第四个星期三（遇法定节假日顺延）")
        print(lead_blanks,"交易所  ：深圳证券交易所")
    
    #沪深300股指期权
    print(heading,"沪深300股指期权")
    if detail:
        print(lead_blanks,"其他名称：中金所沪深300股指期权")
        print(lead_blanks,"类别    ：欧式期权，无红利")
        print(lead_blanks,"标的证券：沪深300指数（000300.SS，399300.SZ）")
        print(lead_blanks,"上市日期：2019-12-23")
        #print(lead_blanks,"行权价格：1个平值合约、4个虚值合约、4个实值合约")
        print(lead_blanks,"到期月份：当月、下2个月、随后3个季月（季度末月）")
        print(lead_blanks,"到期日期：到期月份的第三个星期五（节假日顺延）")
        print(lead_blanks,"交易所  ：中国金融期货交易所") 
    
    import datetime as dt; today=str(dt.date.today())
    print('\n',heading,"来源：上交所/深交所/中金所,",today)
    return
 
if __name__=='__main__':
    option_fin_china()
    option_fin_china(detail=True)
#==============================================================================
if __name__=='__main__':
    date='2021-11-1'

def get_yymm(date):
    
    import datetime as dt
    d=dt.datetime.strptime(date, '%Y-%m-%d')
    year=d.strftime('%Y')
    month=d.strftime('%m')
    yymm=str(year)[2:]+str(month)    
    
    return yymm

if __name__=='__main__':
    get_yymm('2020-03-25')    
#==============================================================================

if __name__=='__main__':
    start='2021-11-1'
    start=''
    num=12

def get_yymm_list(start='',num=12):
    """
    获取一个给定日期start及其后续的YYMM年月列表，共num个
    """
    
    import datetime as dt
    if start=='':
        start=str(dt.date.today())
    
    start1=dt.datetime.strptime(start, '%Y-%m-%d')
    date_list=[start1]
    
    from datetime import timedelta
    for d in range(1,num+1):
        date=start1+timedelta(days=d*30)
        date_list=date_list+[date]
    
    yymm_list=[]
    for d in date_list:
        year=d.strftime('%Y')
        month=d.strftime('%m')
        yymm=str(year)[2:]+str(month)        
        yymm_list=yymm_list+[yymm]
    
    return yymm_list

if __name__=='__main__':
    get_yymm_list()
    get_yymm_list(num=13)
    get_yymm_list('2021-1-11')
    get_yymm_list('2021-1-11',num=13)
    
#==============================================================================

if __name__=='__main__':
    symbol="华夏上证50ETF期权"
    symbol="华泰柏瑞沪深300ETF期权"
    symbol="嘉实沪深300ETF期权"
    symbol="沪深300股指期权"
    num=12
    
def option_fin_month_china(symbol,num=12):
    """
    功能：遍历并显示一个金融期货品种的到期年月YYMM
    """
    
    if not (symbol in option_fin_list):
        print("  #Warning(option_fin_month_china): info not found for",symbol)
        return None
    
    #当前年月开始的年月列表
    import datetime as dt; today=str(dt.date.today())
    yymm_list=get_yymm_list(today,num=num)
    
    import akshare as ak
    end_month_list=[]
    for yymm in yymm_list:
        #print('Scanning',yymm)
        try:
            df = ak.option_finance_board(symbol=symbol, end_month=yymm)
        except:
            continue
        else:
            if len(df)==0: continue
            
            if symbol=="华夏上证50ETF期权":
                y2m2=df['合约交易代码'][:1].values[0][7:11]
            
            if symbol=="华泰柏瑞沪深300ETF期权":
                y2m2=df['合约交易代码'][:1].values[0][7:11]
            
            if symbol=="嘉实沪深300ETF期权":
                d1=df['期权行权日'][:1].values[0]
                d2=d1.astype('str')
                yy=d2[2:4]; mm=d2[5:7]; y2m2=yy+mm
            
            if symbol=="沪深300股指期权":
                y2m2=df['instrument'][:1].values[0][2:6]                
            
            if y2m2==yymm:
                end_month_list=end_month_list+[yymm]
    
    print("\n=== 中国金融期权品种的到期日(YYMM) ===") 
    print(symbol+':')       
    print(end_month_list)

    import datetime as dt; today=str(dt.date.today())
    print("来源：上交所/深交所/中金所,",today)
    
    return
        

if __name__=='__main__':
    option_fin_month_china("华夏上证50ETF期权")
    option_fin_month_china("嘉实沪深300ETF期权")
    option_fin_month_china("华泰柏瑞沪深300ETF期权")
    option_fin_month_china("沪深300股指期权")

#==============================================================================
if __name__=='__main__':
    end_month='2112'
    nth=4 #第四个
    wd=3 #星期三

def nth_weekday(end_month,nth,wd):
    """
    功能：给定年月end_month的第nth个星期wd，求日期
    """
    import calendar
    import datetime
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    
    myear=int('20'+end_month[:2])
    mmonth=int(end_month[2:])
    monthcal = c.monthdatescalendar(myear,mmonth)
    
    mdatelist=[]
    for mweek in monthcal:
        #print(mweek)
        for mday in mweek:
            #print(mday)
            if (mday.weekday()==(wd-1)) and (mday.month==mmonth):
                mdatelist=mdatelist+[mday]
    mdate=str(mdatelist[nth-1])
    
    return mdate

if __name__=='__main__':
    #求第四个星期三
    nth_weekday('2111',4,3)
    nth_weekday('2112',4,3)
#==============================================================================
if __name__=='__main__':
    symbol="华夏上证50ETF期权"
    symbol="华泰柏瑞沪深300ETF期权"
    symbol="嘉实沪深300ETF期权"
    symbol="沪深300股指期权"   
    end_month='2112'
    direction='call'
    printout=True
    
    
def option_fin_contracts(symbol,end_month,direction='call',printout=True):
    """
    功能：抓取指定金融期权品种和到期日年月的具体合约
    """
    
    if not (symbol in option_fin_list):
        print("  #Warning(option_fin_contracts): info not found for",symbol)
        return None
    
    import akshare as ak
    try:
        df = ak.option_finance_board(symbol=symbol, end_month=end_month)
    except:
        print("  #Error(option_fin_contracts): info unavailable for",symbol,'on maturity',end_month)
        return None
    
    #检查期权方向
    typelist=['CALL','PUT','BOTH']
    utype=direction.upper()
    if not (utype in typelist):
        print("  #Warning(option_fin_contracts): unsupported option direction",direction)
        print("  Supported option direction:",typelist)
        return None
    
    import pandas as pd
    contracts=pd.DataFrame()
    #==================================================================
    if symbol in ["华夏上证50ETF期权","华泰柏瑞沪深300ETF期权"]:
        #期权方向标志
        df['direction']=df['合约交易代码'].apply(lambda x:x[6:7])
        if utype=='CALL':
            df1=df[df['direction']=='C']
        elif utype=='PUT':
            df1=df[df['direction']=='P']
        else:
            df1=df
        
        #取交易日期
        df1['date']=df1.index[0][:8]
        contracts['date']=pd.to_datetime(df1['date'])
        
        #去掉前后空格
        df1['合约交易代码']=df1['合约交易代码'].apply(lambda x: x.strip())
        contracts['contract']=df1['合约交易代码']
        
        contracts['name']=contracts['contract']
        contracts['direction']=df1['direction']
        #contracts['Close']=df1['前结价']
        contracts['Strike']=df1['行权价']
        
        #到期日：到期月的第四个星期三
        mdate=nth_weekday(end_month,4,3)
        contracts['maturity']=mdate
        
        #标的物
        pos=option_fin_list.index(symbol)
        ua=underlying_fin_list[pos]
        contracts['underlying']=ua
        
    #=================================================================
    if symbol in ["嘉实沪深300ETF期权"]:
        #期权方向标志
        df['direction']=df['类型'].apply(lambda x:'C' if x in ["认购"] else 'P')
        if utype=='CALL':
            df1=df[df['direction']=='C']
        elif utype=='PUT':
            df1=df[df['direction']=='P']
        else:
            df1=df
        
        #去掉前后空格
        df1['合约编码']=df1['合约编码'].apply(lambda x: str(x).strip())
        contracts['contract']=df1['合约编码']
        
        contracts['name']=df1['合约简称']
        contracts['direction']=df1['direction']
        #????contracts['Close']=df1['前结价']
        try:
            contracts['Strike']=df1['行权价']
        except:
            contracts['Strike']=df1['行权价(元)']
        
        #行权日
        contracts['maturity']=df1['期权行权日'].apply(lambda x: x.strftime('%Y-%m-%d'))
        
        #标的物
        pos=option_fin_list.index(symbol)
        ua=underlying_fin_list[pos]
        contracts['underlying']=ua
        
        #取交易日期
        import datetime as dt; today=str(dt.date.today())
        contracts['date']=pd.to_datetime(today)
        
    #=================================================================
    if symbol in ["沪深300股指期权"]:
        """
        字段解读：
        instrument:合约编号
        position:持仓量
        volume:成交量
        lastprice:最新价
        updown:涨跌，涨跌=最新价-前结算价
        bprice:买价
        bamount:买量
        sprice:卖价
        samount:卖量
        """
        #期权方向标志
        df['direction']=df['instrument'].apply(lambda x:x[7:8])
        if utype=='CALL':
            df1=df[df['direction']=='C']
        elif utype=='PUT':
            df1=df[df['direction']=='P']
        else:
            df1=df
        
        #去掉前后空格
        df1['instrument']=df1['instrument'].apply(lambda x: x.strip())
        contracts['contract']=df1['instrument']
        
        contracts['name']=df1['instrument']
        contracts['direction']=df1['direction']
        #????contracts['Close']=df1['前结价']
        contracts['Strike']=df1['instrument'].apply(lambda x:x[9:13]).astype('int')
        
        #行权日:到期月份第三周的周三
        mdate=nth_weekday(end_month,3,3)
        #contracts['maturity']='20'+df1['instrument'].apply(lambda x:x[2:6])+'28'
        contracts['maturity']=mdate
        
        #标的物
        pos=option_fin_list.index(symbol)
        ua=underlying_fin_list[pos]
        contracts['underlying']=ua
        
        #取交易日期
        import datetime as dt; today=str(dt.date.today())
        contracts['date']=pd.to_datetime(today)
        
    contracts['Option']=symbol
    contracts['end_month']=end_month
    contracts.set_index('date',inplace=True)
    contracts.sort_values(by=['Strike'],ascending=True,inplace=True)
    
    #打印
    if printout:
        print("\n========= 中国金融期权合约 =========\n")
        print("期权品种：",symbol)
        print("到期年月：",end_month)
        print("合约方向：",utype)
        
        #改换中文字段栏
        collist=['contract','direction','maturity','underlying','Strike']
        collistcn=['期权合约','方向','到期日','标的证券','行权价']
        printdf=contracts[collist].copy()
        printdf.columns=collistcn
        
        #打印对齐
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
        
        print(printdf.to_string(index=False))        
        
        import datetime as dt; today=str(dt.date.today())
        print("\n来源：新浪/上交所/深交所/中金所,",today)

    return contracts    
        
if __name__=='__main__': 
    symbol="华夏上证50ETF期权"
    symbol="华泰柏瑞沪深300ETF期权"
    symbol="嘉实沪深300ETF期权"
    symbol="沪深300股指期权"   
    end_month='2112'
    direction='call'       
    df=option_fin_contracts(symbol,end_month,direction='call')        

#==============================================================================
if __name__=='__main__':
    symbol="华夏上证50ETF期权"
    symbol="华泰柏瑞沪深300ETF期权"
    symbol="嘉实沪深300ETF期权"
    symbol="沪深300股指期权"   
    
    contract='510050C2206M02900'
    contract='90000871'
    end_month='2206'
    direction='call'
    
def option_fin_contract_parms(symbol,end_month,contract,direction='call'):
    """
    功能：抓取期权合约的到期日、行权价和标的证券
    """
    
    df=option_fin_contracts(symbol=symbol,end_month=end_month, \
            direction=direction,printout=False)
    
    df1=df[df['contract']==contract]
    if len(df1)==0:
        print("  #Warning(option_fin_contract_parms): contract not found for",contract)
        return None,None,None

    underlying=df1['underlying'].values[0]
    maturity=df1['maturity'].values[0]
    strike=float(df1['Strike'].values[0])
    
    return underlying,maturity,strike

if __name__=='__main__':
    option_fin_contract_parms("华夏上证50ETF期权",'2206','510050C2206M02900',direction='call')
#=============================================================================
if __name__=='__main__': 
    underlying='510050.SS'
    date='2021-11-19'
    days=30

def underlying_sigma(underlying,date,days=30):
    """
    功能：计算标的物价格的年化标准差
    underlying：标的证券代码
    date：当前日期
    days：历史期间长度，日历日天数，默认30个日历日
    """
    
    #年度交易日天数
    annual_trading_days=252
    
    #计算历史样本的开始日期
    import pandas as pd
    try:
        end=pd.to_datetime(date)
    except:
        print("  #Error(annualized_sigma): invalid date",date)
        return None,None
    
    from datetime import timedelta
    start=end-timedelta(days=days+1)
    start1=start.strftime('%Y-%m-%d')
    
    #抓取标的物的历史价格样本
    """
    try:
        df=get_prices(underlying,start1,date)
    except:
        print("  #Error(annualized_sigma): failed to retrieve info for",underlying)
        return None,None   
    """
    df=get_prices(underlying,start1,date)
    #标的物当前价格
    s0=df[-1:]['Close'].values[0]

    """
    #采用算数收益率
    df['ret']=df['Close'].pct_change()
    """
    
    #采用对数收益率
    df['Close_lag']=df['Close'].shift(1)
    df.dropna(inplace=True)
    import numpy as np
    df['ret']=np.log(df['Close']/df['Close_lag'])
    sigma=df['ret'].std()
    annualized_sigma=sigma*np.sqrt(annual_trading_days)
    
    return annualized_sigma,s0,df

if __name__=='__main__': 
    sigma1,_,_=underlying_sigma('510050.SS','2021-11-19',days=365)
    sigma2,_,_=underlying_sigma('510050.SS','2021-11-19',days=183)
    sigma3,_,_=underlying_sigma('510050.SS','2021-11-19',days=92)  
    sigma4,_,_=underlying_sigma('510050.SS','2021-11-19',days=60)
    sigma5,_,_=underlying_sigma('510050.SS','2021-11-19',days=30)
    print(sigma1,sigma2,sigma3,sigma4,sigma5)

#=============================================================================

#=============================================================================
if __name__=='__main__': 
    start='2021-1-1'
    end='2021-10-12'

def calc_days(start,end):
    """
    计算两个日期之间的年数
    """
    
    #检查日期期间的有效性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(calc_days): date period invalid")
        return None
    
    diff=end1-start1
    #日历天数
    diff2=diff.days
    diff_in_years=diff2/365

    return diff2,round(diff_in_years,5)    

if __name__=='__main__': 
    days,_=calc_days('2020-10-31','2021-10-12')


#=============================================================================
if __name__=='__main__': 
    option="华泰柏瑞沪深300ETF期权"
    end_month='2206'
    contract='510300C2206M04500'
    direction='call'
    
    today='2021-11-19'
    sample_days=30
    
    rate_type='shibor'
    rate_period='3M'
    daysahead=30

def option_fin_pricing_china(option,end_month,contract,today,direction='call', \
                             sample_days=30,rate_type='shibor',rate_period='1Y',printout=True):
    """
    功能：将中国金融期权定价的过程整合在一起，提供默认选项，改善小白的使用体验
    注：波动率使用历史波动率
    """
    
    #第1步：查找计算金融期权预期价格所需要的参数
    ua,maturity,x=option_fin_contract_parms(option,end_month,contract,direction)
    if ua is None:
        print("  #Error(option_fin_pricing_china): info not found")
        print("  Possible reasons: one or some of the following")
        print("    Option not found for",option)
        print("    Maturity year-month not found for",end_month)
        print("    Contract not found for",contract,'as',direction.lower())
        print("    Contract not found in the above option + maturity")
        return None

    #第2步：计算标的证券价格收益率的历史波动率：
    sigma,s0,_=underlying_sigma(ua,today,days=sample_days)
    
    #第3步：查找年化无风险利率
    rate_type=rate_type.upper()
    if rate_type=='SHIBOR':
        rf=shibor_rate(today,rate_period) 
    elif rate_type=='TREASURY':
        rf=treasury_yield_china(today,rate_period)
    else:
        print("  #Error(option_fin_pricing_china): invalid rate type",rate_type.lower())
        return None
        
    #第4步：计算当前日期距离合约到期日的天数
    days,_=calc_days(today,maturity)
    #print("days is",days)
    
    #第5步：计算期权合约的预期价格
    #中国目前金融期权均为无红利的欧式期权，可以直接采用Black-Scholes期权定价模型
    expected_price=bs_pricing(s0,x,days,rf,sigma,direction,printout=False)  
    
    if printout:
        print("\n============ 中国金融期权定价 ============\n")
        
        print("*** 合约信息：")
        print("    合约代码:",contract)
        print("    期权品种:",option)
        print("    标的证券:",ua)
        print("    行权价格:",x)
        print("    到期年月:",end_month)
        print("    期权方向:",direction)
        
        print("*** 合约现状：")
        print("    定价日期:",today,'\b，标的市价:',s0)
        print("    距离到期:",days,'\b天')
        print("    历史波动率期间:",sample_days,'\b天')
        print("    历史波动率数值:",round(sigma,5))
        
        print("    无风险利率种类:",rate_type.lower(),'\b,',rate_period)
        print("    年化无风险利率:",round(rf*100,4),'\b%')
        
        print("*** 定价结果：")
        print("    定价模型: Black-Scholes")        
        print("    理论价格:",round(expected_price,5))
        
        print("\n注：历史/隐含波动率的差异是定价误差的主要原因")
        
        import datetime; pgm_date = datetime.date.today()         
        print("数据来源: 新浪/沪深所/中金所,",pgm_date)        
        
    return expected_price  
        
if __name__=='__main__': 
    option="华泰柏瑞沪深300ETF期权"
    end_month='2206'
    #看涨合约
    option_fin_contracts(option,end_month,direction='call') 
    contract='510300C2206M04500'
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y')
    #理论价格：0.5748，实际收盘价：0.5584
    #查看实际价格网址：https://stock.finance.sina.com.cn/option/quotes.html
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y') 
    #理论价格：0.5631，实际收盘价：0.5584
    
    #看跌合约   
    option_fin_contracts(option,end_month,direction='put') 
    contract='510300P2206M04500'
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')
    #理论价格：0.083，实际收盘价：0.0893  
    #查看实际价格网址：http://quote.eastmoney.com/center/gridlist.html#options_sahs300etf_rengu

    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')
    #理论价格：0.086，实际收盘价：0.0893          
    #=============================
    
    option="华夏上证50ETF期权"
    end_month='2206'
    #看涨合约
    option_fin_contracts(option,end_month,direction='call') 
    contract='510050C2206M02900'
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y')
    #理论价格：0.4264，实际收盘价：0.4411
    #查看网址：http://quote.eastmoney.com/center/gridlist.html#options_sz50etf_txbj
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y') 
    #理论价格：0.4191，实际收盘价：0.4411
    
    #看跌合约   
    option_fin_contracts(option,end_month,direction='put')
    contract='510050P2206M02900'
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')
    #理论价格：0.0505，实际收盘价：0.0441    
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')
    #理论价格：0.0524，实际收盘价：0.0441          
    #=============================

    option="嘉实沪深300ETF期权"
    end_month='2206'
    option_fin_contracts(option,end_month,direction='call')    
    #看涨合约
    contract='90000905'   
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y')
    #理论价格：0.5878，实际收盘价：0.57
    #查看网站：http://quote.eastmoney.com/center/gridlist.html#options_szetf_all
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y')        
    #理论价格：0.5766，实际收盘价：0.57
    
    #看跌合约
    option_fin_contracts(option,end_month,direction='put')
    contract='90000906'   
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')
    #理论价格：0.0692，实际收盘价：0.0848
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')        
    #理论价格：0.072，实际收盘价：0.0848
    #=============================

    option="沪深300股指期权"
    end_month='2206'
    option_fin_contracts(option,end_month,direction='call')    
    #看涨合约
    contract='IO2206-C-4200'   
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y')
    #理论价格：770.9，实际收盘价：700.6
    #查看网站：http://quote.eastmoney.com/center/gridlist.html#options_cffex_all
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='call', \
                             sample_days=90,rate_type='shibor',rate_period='1Y')        
    #理论价格：759，实际收盘价：700.6
    
    #看跌合约
    option_fin_contracts(option,end_month,direction='put')
    contract='IO2206-P-4200'   
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')
    #理论价格：40.7，实际收盘价：49.2
    eprice=option_fin_pricing_china(option,end_month,contract,today='2021-11-19', \
                             direction='put', \
                             sample_days=365,rate_type='shibor',rate_period='1Y')        
    #理论价格：42.6，实际收盘价：49.2
    
#=============================================================================
#=============================================================================
#=============================================================================
    