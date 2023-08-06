# -*- coding: utf-8 -*-
"""
本模块功能：中国内盘和外盘期货
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2021年9月26日
最新修订日期：2021年9月28日
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
from siat.grafix import *
#==========================================================================================
if __name__=='__main__':
    trade_date='2020-7-13'

def future_type_china_0(trade_date):
    """
    中国内盘期货：代码和品种的基础数据
    """
    #日期变换
    trade_date1=convert_date_ts(trade_date)
    
    import akshare as ak
    df=ak.futures_rule(date=trade_date1)
    
    try:
        cols = df.columns.tolist()
    except:
        return None
    cols1 = cols[2:3] + cols[1:2] + cols[0:1] + cols[3:] # 将基金代码列名放前面
    
    #改变字段顺序
    df1=df[cols1]
    
    #去掉期权项目
    df2=df1[~df1['品种'].str.contains("期权")]  
    df2.sort_values(by=['代码'],ascending=True,inplace=True)
    df2.reset_index(inplace=True)
    del df2['index']
    
    return df2

#======================================================================================
def SBC2DBC(ustring):
    """
    字符串转换：半角转全角，便于打印对齐
    """
    rstring = ''
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 0x0020:
            inside_code = 0x3000
        else:
            if not (0x0021 <= inside_code and inside_code <= 0x7e):
                rstring += uchar
                continue
        inside_code += 0xfee0
        rstring += chr(inside_code)
    return rstring
#======================================================================================
if __name__=='__main__':
    trade_date='2020-7-13'
    df=future_type_china_0(trade_date)    

def future_type_china_1(df):
    """
    列示中国内盘期货的全部代码和品种，每4个一行
    """
    print("\n===== 中国内盘期货代码品种一览表 =====\n")
    #遍历，合成一行
    itemlist=[]
    for row in df.itertuples():
        code=SBC2DBC(getattr(row,'代码'))
        name=SBC2DBC(getattr(row,'品种'))
        itemlist=itemlist+[code+'（'+name+'）']
    
    maxlen=0
    for i in itemlist:
        ilen=len(i)
        if maxlen < ilen: maxlen=ilen
    maxlen=maxlen+1
    
    rownum=0
    linetxt=''
    iteminline=3
    for i in itemlist:
        if rownum < iteminline:
            ifull=i+SBC2DBC('.')*(maxlen-len(i))
            linetxt=linetxt+ifull
            rownum=rownum+1
        else:
            print(linetxt)
            rownum=0; linetxt=''
        
    import datetime
    today = datetime.date.today()
    print('\n*** 数据来源：国泰君安,',today)
    
    return

if __name__=='__main__':
    future_type_china_1(df)     
#======================================================================================
if __name__=='__main__':
    code='BB2007'
    df=future_type_china_0(trade_date) 

def get_future_symbol(code):
    """
    获得一个具体期货合约的品种代码
    """
    code1=code.upper()
    
    letterlist=[chr(i).upper() for i in range(97,123)]
    symbol=''
    
    for ch in code1:
        if ch in letterlist:
            symbol=symbol+ch
        else:
            break
    
    return symbol
#======================================================================================

def future_type_china_2(df,code):
    """
    列示中国内盘期货的品种明细
    """
    symbol=get_future_symbol(code)
    
    df1=df[df['代码']==symbol]
    cols=list(df1)
    cols.pop()

    print("\n===== 中国内盘期货品种概况 =====\n")
    maxlen=0
    for c in cols:
        clen=hzlen(c)
        if maxlen < clen: maxlen=clen
    
    contract='合约'
    print(contract+' '*(maxlen-hzlen(contract))+':',code)
    for c in cols:
        print(c+' '*(maxlen-hzlen(c))+':',df1[c].values[0])

    import datetime
    today = datetime.date.today()
    print('\n数据来源：国泰君安,',today)
    
    return

if __name__=='__main__':
    future_type_china_2(df,'BB2007') 

#======================================================================================
if __name__=='__main__':
    code='BX2007'

def future_type_china(code=''):
    """
    综合程序：
    合约code为空或品种symbol不存在时列示中国内盘期货的全部代码，否则列示该合约品种明细
    """
    import datetime
    today = datetime.date.today()
    
    df=future_type_china_0(today)
    while df is None:
        today=date_adjust(today, adjust=-1)
        df=future_type_china_0(today)

    symbol=get_future_symbol(code)
    df1=df[df['代码']==symbol]  
    
    if len(df1)==0:
        if not (code==''):
            print("  Warning(future_type_china):",code,'not found')
        future_type_china_1(df)
        return df
    
    future_type_china_2(df,code)
    return df1

if __name__=='__main__':
    code='Bx2007'
    df=future_type_china(code) 

#======================================================================================
if __name__=='__main__':
    code='SC2110'
    start='2021-8-1'
    end='2021-9-27'
    power=0

def future_price_china(code,start,end,power=0):
    """
    综合程序：
    绘制内盘期货交易曲线：收盘价vs结算价vs成交量
    """
    print("Searching for contract "+code+", it costs great time, just take a break...")
    #日期变换
    start1=convert_date_ts(start)
    end1=convert_date_ts(end)
    
    #获得中国内盘期货品种代码
    varietydf=future_type_china_0(end1)
    #获得期货合约code的品种代码
    variety=get_future_symbol(code)
    vdf=varietydf[varietydf['代码']==variety]
    if len(vdf)==0:
        print("  #Error(future_price_china): future variety",variety,'not found')
        return None
    varietyname=vdf['品种'].values[0]
    
    #查找交易所代码
    mktname=vdf['交易所'].values[0]
    mktnamelist=['大商所','郑商所','上期所','中金所','能源中心']
    mktnamelistfull=['大连商品交易所','郑州商品交易所','上海期货交易所','中国金融期货交易所','上海国际能源交易中心']
    mktcodelist=['DCE','CZCE','SHFE','CFFEX','INE']
    pos=mktnamelist.index(mktname)
    market=mktcodelist[pos]
    mktnamefull=mktnamelistfull[pos]
    
    import akshare as ak
    p=ak.get_futures_daily(start_date=start1,end_date=end1,market=market)
    
    p1=p[p['symbol']==code]
    if len(p1)==0: 
        print("  #Error(future_price_china): future contract",code,'not found in market',market)
        contracts=set(list(p[p['variety']==variety]['symbol']))
        contracts1=sorted(contracts) 
        print("\n提示：当前可用的"+varietyname+variety+'期货合约：'+mktnamefull+', '+str(end))
        print(contracts1)
        return None        
    
    #转换日期格式
    import pandas as pd
    p1['date1']=pd.to_datetime(p1['date'])
    p2=p1.set_index('date1')
    
    import pandas as pd
    p2a=pd.DataFrame(p2['close']) #收盘价
    p2a['close']=p2a['close'].astype('float')
    
    p2b=pd.DataFrame(p2['settle']) #结算价  
    p2b['settle']=p2b['settle'].astype('float')
    
    p2c=pd.DataFrame(p2['volume']) #成交量
    p2c['volume']=p2c['volume'].astype('int64')
    
    p2d=pd.DataFrame(p2['turnover']) #成交金额
    p2d['turnover']=p2d['turnover'].astype('int64')
    
    p2e=pd.DataFrame(p2['open_interest']) #持仓量
    p2e['open_interest']=p2e['open_interest'].astype('int64')
    
    #绘图
    import datetime
    today = datetime.date.today()
    footnote="数据来源："+mktnamefull+', '+str(today)
    
    print("  Rendering trading trend graphics ...")
    titletxt="中国内盘期货交易走势分析："+varietyname+code
    #避免code被翻译
    acode=' '+code
    #"""
    #收盘价vs结算价
    plot_line2(p2a,acode,"close","收盘价", \
               p2b,acode,"settle","结算价", \
               '价格',titletxt,footnote, \
               power=power,twinx=False)
    #"""
    #收盘价vs成交量
    plot_line2(p2a,acode,"close","收盘价", \
               p2c,acode,"volume","成交量", \
               '',titletxt,footnote, \
               power=power,twinx=True)
    #"""
    #收盘价vs持仓量
    plot_line2(p2a,acode,"close","收盘价", \
               p2e,acode,"open_interest","持仓量", \
               '',titletxt,footnote, \
               power=power,twinx=True)
    #"""
    return p2

if __name__=='__main__':
    code='SC2110'
    df=future_type_china(code) 
    
#===========================================================================================
if __name__=='__main__':
    symbol="ZSD"

def future_type_foreign_0(symbol="ZSD"):
    """
    获得某个外盘期货品种symbol详情
    """
    import akshare as ak
    try:
        df=ak.futures_foreign_detail(symbol=symbol)
    except:
        print("  #Error(future_type_foreign_0): future variety",symbol,'not found')
        return None
    
    #构造df
    col1=df.iloc[0,0]; col1value=df.iloc[0,1]
    if "并非期货" in col1value:
        col1value=col1value.replace("并非期货",'')
    
    col2=df.iloc[0,2]; col2value=df.iloc[0,3]
    col3=df.iloc[0,4]; col3value=df.iloc[0,5]
    
    col4=df.iloc[1,0]; col4value=df.iloc[1,1]
    col5=df.iloc[1,2]; col5value=df.iloc[1,3]
    col6=df.iloc[1,4]; col6value=df.iloc[1,5]
    
    col7=df.iloc[2,0]; col7value=df.iloc[2,1]
    col8=df.iloc[2,2]; col8value=df.iloc[2,3]
    
    col9=df.iloc[3,0]; col9value=df.iloc[3,1]
    col10=df.iloc[3,2]; col10value=df.iloc[3,3]  
    
    future_dict={col9:col9value,col1:col1value,col10:col10value,col2:col2value, \
                 col3:col3value,col4:col4value,col5:col5value,col6:col6value, \
                     col7:col7value,col8:col8value}
    import pandas as pd
    df1=pd.DataFrame(future_dict,index=[0])
    
    return df1

if __name__=='__main__':
    df=future_type_foreign_0(symbol="ZSD")  
    print(df.T)
#===========================================================================================
if __name__=='__main__':
    symbol="ZSD"

def future_type_foreign_1():
    """
    获得中国所有外盘期货品种详情
    """
    import akshare as ak  
    varietylist=ak.futures_foreign_commodity_subscribe_exchange_symbol()
    varietylist.sort()
    
    try:
        df=future_type_foreign_0(symbol=varietylist[0])
    except:
        pass
    for v in varietylist:
        try:
            df_tmp=future_type_foreign_0(symbol=v)
            #print(v)
            df=df.append(df_tmp)
        except:
            pass
    df.drop_duplicates(inplace=True)
    
    return df
    
#===========================================================================================
if __name__=='__main__':
    symbol="ZSD"
    df=future_type_foreign_1()

def future_type_foreign_2(df,symbol="ZSD"):
    """
    打印中国外盘期货某个品种详情
    """
    
    df1=df[df['交易代码']==symbol]
    cols=list(df1)

    print("\n===== 中国外盘期货品种概况 =====\n")
    maxlen=0
    for c in cols:
        clen=hzlen(c)
        if maxlen < clen: maxlen=clen
    
    for c in cols:
        print(c+' '*(maxlen-hzlen(c))+':',df1[c].values[0])

    import datetime
    today = datetime.date.today()
    print('\n*** 数据来源：新浪财经,',today)
    
    return

if __name__=='__main__':
    future_type_foreign_2(df,symbol="ZSD")  
    
#======================================================================================
if __name__=='__main__':
    code='ZSD'

def future_type_foreign(code=''):
    """
    综合程序：
    合约code为空或不存在时列示中国外盘期货的所有品种，否则列示一个品种的明细条款
    """
    
    df=future_type_foreign_1()

    df1=df[df['交易代码']==code]  
    
    if len(df1)==0:
        if not (code==''):
            print("  Warning(future_type_foreign):",code,'not found')
        
        #设置打印对齐
        import pandas as pd
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        
        print("\n===== 中国外盘期货品种一览表 =====\n")
        df2=df[['交易代码','交易品种','上市交易所']]
        print(df2.to_string(index=False))
        
        import datetime
        today = datetime.date.today()
        print('\n*** 数据来源：新浪财经,',today)
        
        return df
    
    future_type_foreign_2(df,symbol=code)
    
    return df1

if __name__=='__main__':
    df=future_type_foreign(code='') 
    df=future_type_foreign(code='CT')
    df=future_type_foreign(code='OIL')

#====================================================================================== 
if __name__=='__main__':
    code='ZSD'
    start='2021-8-1'
    end='2021-9-27'
    power=0

def future_price_foreign(code,start,end,power=0):
    """
    综合程序：
    绘制中国外盘期货的交易趋势：收盘价vs成交量
    """
    print("Searching for contract "+code+", it costs great time, just take a break...")
    #日期变换
    flag,start1,end1=check_period(start,end)
    
    #获得中国外盘期货品种代码
    varietydf=future_type_foreign_0(symbol=code)
    #获得期货合约code的品种代码
    if len(varietydf)==0:
        print("  #Error(future_price_foreign): future variety",code,'not found')
        return None
    varietyname=varietydf['交易品种'].values[0]
    
    #查找交易所代码
    mktnamefull=varietydf['上市交易所'].values[0]
    
    import akshare as ak
    p0=ak.futures_foreign_hist(symbol=code) 
    p01=p0[p0['date']>=start1]
    p1=p01[p01['date']<=end1]
    
    if len(p1)==0: 
        print("  #Error(future_price_foreign): prices not found for",code,'from',start,'to',end)
        return None        
    
    #转换日期格式
    p2=p1.set_index('date')
    
    import pandas as pd
    p2a=pd.DataFrame(p2['close']) #收盘价
    p2a['close']=p2a['close'].astype('float')
    
    p2c=pd.DataFrame(p2['volume']) #成交量
    p2c['volume']=p2c['volume'].astype('int64')
    
    #绘图
    import datetime
    today = datetime.date.today()
    footnote="数据来源：新浪财经"+', '+str(today)
    
    titletxt="中国外盘期货交易走势分析："+varietyname+code
    
    #收盘价vs成交量
    #print("code =",code)
    #避免code被翻译
    acode=' '+code
    plot_line2(p2a,acode,"close","收盘价", \
               p2c,acode,"volume","成交量", \
               '',titletxt,footnote, \
               power=power,twinx=True)

    return p2

if __name__=='__main__':
    df=future_price_foreign('CT','2021-8-1','2021-9-28')
    
#===========================================================================================   