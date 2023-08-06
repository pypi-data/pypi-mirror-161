# -*- coding: utf-8 -*-
"""
本模块功能：债券，基础层函数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年1月8日
最新修订日期：2020年5月10日
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
#==============================================================================
def macD0(c,y,F,n):
    """
    功能：计算债券的麦考莱久期期数
    输入参数：
    1、每期票面利率c
    2、每期到期收益率y，市场利率，贴现率
    3、票面价值F
    3、到期期数n
    输出：麦考莱久期的期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(n+1)))
    
    #计算未来票息和面值的现值
    p=sum(c*F/(1+y)**t)+F/(1+y)**len(t)
    #计算未来票息和面值的加权现值
    wp=sum(c*F*t/(1+y)**t)+F*len(t)/(1+y)**len(t)
    
    return wp/p    

if __name__=='__main__':
    c=0.08/2; y=0.1/2; n=6; F=100
    print(macD0(c,y,F,n))
#==============================================================================
def macD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的麦考莱久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：麦考莱久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算麦考莱久期期数
    d=macD0(c,y,F,n)
    #转换为麦考莱久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,2)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(macD(cr,ytm,nyears))

#==============================================================================
def MD0(c,y,F,n):
    """
    功能：计算债券的修正久期期数
    输入参数：
    1、每期票面利率c
    2、每期到期收益率y，市场利率，贴现率
    3、票面价值F
    4、到期期数n
    输出：修正久期期数（不一定是年数）
    """
    #修正麦考莱久期
    md=macD0(c,y,F,n)/(1+y)
    
    return md

if __name__=='__main__':
    c=0.08/2; y=0.1/2; n=6; F=100
    print(MD0(c,y,F,n))    
    
#==============================================================================
def MD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的修正久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：修正久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=MD0(c,y,F,n)
    #转换为久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,2)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(MD(cr,ytm,nyears))


    
#==============================================================================
def DD0(c,y,F,n):
    """
    功能：计算债券的美元久期期数
    输入参数：
    1、每期票面利率c
    2、每期到期收益率y，市场利率，贴现率
    3、票面价值F
    4、到期期数n
    输出：美元久期期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(n+1)))
    
    #计算现值
    p=sum(c*F/(1+y)**t)+F/(1+y)**len(t)
    #美元久期期数
    dd=MD0(c,y,F,n)*p
    
    return dd

if __name__=='__main__':
    c=0.08/2; y=0.1/2; n=6; F=100
    print(DD0(c,y,F,n))    
    
#==============================================================================    
def DD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的美元久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：美元久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=DD0(c,y,F,n)
    #转换为久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,2)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(DD(cr,ytm,nyears))

#==============================================================================    
def ED0(c,y,F,n,per):
    """
    功能：计算债券的有效久期期数
    输入参数：
    1、每期票面利率c
    2、每期到期收益率y，市场利率，贴现率
    3、票面价值F
    4、到期期数n
    5、到期收益率的变化幅度，1个基点=0.01%=0.0001
    输出：有效久期期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(n+1)))
    
    #计算到期收益率变化前的现值
    p0=sum(c*F/(1+y)**t)+F/(1+y)**len(t)
    #计算到期收益率增加一定幅度后的现值
    p1=sum(c*F/(1+y+per)**t)+F/(1+y+per)**len(t)
    #计算到期收益率减少同等幅度后的现值
    p2=sum(c*F/(1+y-per)**t)+F/(1+y-per)**len(t)
    #久期期数
    ed=(p2-p1)/(2*p0*per)
    
    return ed

if __name__=='__main__':
    c=0.08/2; y=0.1/2; n=6; F=100; per=0.001/2
    print(ED0(c,y,F,n,per))    
    
#==============================================================================    
def ED(cr,ytm,nyears,peryear,ctimes=2,fv=100):
    """
    功能：计算债券的有效久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、年到期收益率变化幅度peryear
    5、每年付息次数ctimes
    6、票面价值fv
    输出：有效久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; per=peryear/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=ED0(c,y,F,n,per)
    #转换为久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,2)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100; peryear=0.001
    print(ED(cr,ytm,nyears,peryear))
    
    cr=0.095; ytm=0.1144; nyears=8; ctimes=2; fv=1000; peryear=0.0005
    print(ED(cr,ytm,nyears,peryear))    
#==============================================================================    
def CFD0(c,y,F,n):
    """
    功能：计算债券的封闭式久期期数
    输入参数：
    1、每期票面利率c
    2、每期到期收益率y，市场利率，贴现率
    3、票面价值F
    4、到期期数n
    输出：久期期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(n+1)))
    
    #计算到期收益率变化前的现值
    p=sum(c*F/(1+y)**t)+F/(1+y)**len(t)
    
    #计算分子第1项
    nm1=(c*F) * ((1+y)**(n+1)-(1+y)-y*n) / ((y**2)*((1+y)**n))
    #计算分子第2项
    nm2=F*(n/((1+y)**n))
    
    #计算封闭式久期
    cfd=(nm1+nm2)/p
    
    return cfd

if __name__=='__main__':
    c=0.095/2; y=0.1144/2; n=16; F=1000
    print(CFD0(c,y,F,n))    
#==============================================================================    
def CFD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的封闭式年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=CFD0(c,y,F,n)
    #转换为久期年数：年数=期数/每年付息次数
    cfd=round(d/ctimes,2)
    
    return cfd                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(CFD(cr,ytm,nyears))
#==============================================================================    
def C0(c,y,F,n):
    """
    功能：计算债券的凸度期数
    输入参数：
    1、每期票面利率c
    2、每期到期收益率y，市场利率，贴现率
    3、票面价值F
    4、到期期数n
    输出：到期收益率变化幅度为per时债券价格的变化幅度
    """    
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(n+1)))
    
    #计算未来现金流的现值
    p=sum(c*F/(1+y)**t)+F/(1+y)**len(t)
    #计算未来现金流的加权现值：权重为第t期的(t**2+t)
    w2p=sum(c*F*(t**2+t)/(1+y)**t)+F*(len(t)**2+len(t))/(1+y)**len(t)
    #计算凸度
    c0=w2p/(p*(1+y)**2)
    
    return c0

if __name__=='__main__':
    c=0.08/2; y=0.1/2; n=6; F=100
    print(C0(c,y,F,n)) 
#==============================================================================    
def convexity(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的凸度年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：凸度（年数）
    """
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算凸度期数
    c=C0(c,y,F,n)
    #转换为凸度年数：年数=期数/每年付息次数**2
    cyears=round(c/ctimes**2,2)
    
    return cyears                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(convexity(cr,ytm,nyears))
#==============================================================================    
def ytm_risk(cr,ytm,nyears,peryear,ctimes=2,fv=100):
    """
    功能：计算债券的利率风险，即市场利率（到期收益率）变动将带来的债券价格变化率
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每期到期收益率（市场利率）变化的幅度per，100个基点=1%
    5、每年付息次数ctimes
    6、票面价值fv
    输出：到期收益率变化幅度导致的债券价格变化率
    """
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算到期收益率变化对债券价格的影响：第1部分
    b0=-MD0(c,y,F,n)/2*peryear
    #计算到期收益率变化对债券价格的影响：第2部分
    b1=(0.5*C0(c,y,F,n)/ctimes**2)*peryear**2
    #债券价格的变化率
    p_pct=round(b0+b1,4)
        
    return p_pct

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; peryear=0.01
    print(ytm_risk(cr,ytm,nyears,peryear))        

#==============================================================================    
#==============================================================================    
def interbank_bond_issue_detail(fromdate,todate):
    """
    功能：获得银行间债券市场发行明细
    输入：开始日期fromdate，截止日期todate
    """
    #检查期间的合理性
    result,start,end=check_period(fromdate, todate)
    if result is None:
        print("...Error(interbank_bond_issue_detail), invalid period:",fromdate,todate)
        return None
    
    #####银行间市场的债券发行数据
    import akshare as ak
    #获得债券发行信息第1页
    print("\n...Searching for bond issuance: ",end='')
    bond_issue=ak.get_bond_bank(page_num=1)    

    import pandas as pd
    from datetime import datetime
    #获得债券发行信息后续页
    maxpage=999
    for pn in range(2,maxpage):
        print_progress_bar(pn,2,maxpage)
        try:
            #防止中间一次失败导致整个过程失败
            bi=ak.get_bond_bank(page_num=pn)
            bond_issue=bond_issue.append(bi)
        except:
            #后续的网页已经变得无法抓取
            print("...Unexpected get_bond_bank(interbank_bond_issue_detail), page_num",pn)
            break        
        
        #判断是否超过了开始日期
        bistartdate=bi.tail(1)['releaseTime'].values[0]
        bistartdate2=pd.to_datetime(bistartdate)
        if bistartdate2 < start: break
    print(" Done!")        
    
    #删除重复项，按日期排序
    bond_issue.drop_duplicates(keep='first',inplace=True)
    bond_issue.sort_values(by=['releaseTime'],ascending=[False],inplace=True)    
    #转换日期项
    lway1=lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
    bond_issue['releaseTime2']=bond_issue['releaseTime'].apply(lway1)    
    
    #提取年月日信息
    lway2=lambda x: x.year
    bond_issue['releaseYear']=bond_issue['releaseTime2'].map(lway2).astype('str')
    lway3=lambda x: x.month
    bond_issue['releaseMonth']=bond_issue['releaseTime2'].map(lway3).astype('str')
    lway4=lambda x: x.day
    bond_issue['releaseDay']=bond_issue['releaseTime2'].map(lway4).astype('str')
    lway5=lambda x: x.weekday() + 1
    bond_issue['releaseWeekDay']=bond_issue['releaseTime2'].map(lway5).astype('str')
    lway6=lambda x: x.date()
    bond_issue['releaseDate']=bond_issue['releaseTime2'].map(lway6).astype('str')
    
    #过滤日期
    bond_issue=bond_issue.reset_index(drop = True)
    bond_issue1=bond_issue.drop(bond_issue[bond_issue['releaseTime2']<start].index)
    bond_issue1=bond_issue1.reset_index(drop = True)
    bond_issue2=bond_issue1.drop(bond_issue1[bond_issue1['releaseTime2']>end].index)
    bond_issue2=bond_issue2.reset_index(drop = True)
    #转换字符串到金额
    bond_issue2['issueAmount']=bond_issue2['firstIssueAmount'].astype('float64')
    
    return bond_issue2
    
if __name__=='__main__':
    fromdate='2020-4-25'    
    todate='2020-4-28'
    ibbi=interbank_bond_issue_detail(fromdate,todate)
    
#==============================================================================
