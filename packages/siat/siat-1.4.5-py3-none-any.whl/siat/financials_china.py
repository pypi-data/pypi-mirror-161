# -*- coding: utf-8 -*-
"""
本模块功能：计算财务报表比例，应用层
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月8日
最新修订日期：2020年9月15日
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
#本模块的公共引用
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.beta_adjustment_china import *
#==============================================================================
import matplotlib.pyplot as plt

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
import pandas as pd
import akshare as ak

STOCK_SUFFIX_CHINA=['SS','SZ','BJ','NQ']
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 
    
def get_fin_stmt_ak(ticker):
    """
    从akshare获取财务报表数据，合成df，限于中国A股
    获取的项目：所有原始项目
    注意：抓取所有的报表，不过滤日期
    """
    print("  Searching financial statements for",ticker,"...")
    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in STOCK_SUFFIX_CHINA):
        print("  #Error(get_fin_stmt_ak): not a stock in China",ticker)
        return None        
    
    #抓取三大报表
    try:
        fbs = ak.stock_financial_report_sina(stock=prefix, symbol="资产负债表")
        fis = ak.stock_financial_report_sina(stock=prefix, symbol="利润表")
        fcf = ak.stock_financial_report_sina(stock=prefix, symbol="现金流量表")
    except:
        print("  #Error(get_fin_stmt_ak): some financial statements unavailable for",ticker)
        return None        
    
    #若报表为空，则返回
    if fbs is None:
        print("  #Warning(get_fin_stmt_ak): balance sheets inaccessible for",ticker)
        return None 
    if fis is None:
        print("  #Warning(get_fin_stmt_ak): income statements inaccessible for",ticker)
        return None 
    if fcf is None:
        print("  #Warning(get_fin_stmt_ak): cash flow statements inaccessible for",ticker)
        return None 
    
    #若报表无数据，则返回
    if len(fbs)==0:
        print("  #Warning(get_fin_stmt_ak): zero record of balance sheets found for",ticker)
        return None  
    if len(fis)==0:
        print("  #Warning(get_fin_stmt_ak): zero record of income statements found for",ticker)
        return None        
    if len(fcf)==0:
        print("  #Warning(get_fin_stmt_ak): zero record of cash flow found for",ticker)
        return None  
        
    #去掉重复项、排序、重建索引
    fbs1=fbs.drop_duplicates(subset=['报表日期'],keep='first')
    fbs1.sort_values(by=['报表日期'],ascending=True,inplace=True)
    fbs1['date']=pd.to_datetime(fbs1['报表日期'])
    fbs1.set_index('date',inplace=True)
    
    fis1=fis.drop_duplicates(subset=['报表日期'],keep='first')
    fis1.sort_values(by=['报表日期'],ascending=True,inplace=True)
    fis1['date']=pd.to_datetime(fis1['报表日期'])
    fis1.set_index('date',inplace=True)
    
    fcf1=fcf.drop_duplicates(subset=['报表日期'],keep='first')
    fcf1.sort_values(by=['报表日期'],ascending=True,inplace=True)
    fcf1['date']=pd.to_datetime(fcf1['报表日期'])
    fcf1.set_index('date',inplace=True)

    #合成：内连接
    fs1=pd.merge(fbs1,fis1,how='inner',left_index=True,right_index=True)
    fs2=pd.merge(fs1,fcf1,how='inner',left_index=True,right_index=True)
    
    if len(fs2) == 0:
        print("  #Warning(get_fin_stmt_ak): zero reports found for",ticker)
        return None
    #按照日期升序排序
    fs2.sort_index(inplace=True)

    #数据清洗：删除因两次合并可能产生的重复列
    dup_col_list=[]
    for c in fs2.columns:
        if ('_x' in c) or ('_y' in c): 
            dup_col_list=dup_col_list+[c]
    fs2.drop(labels= dup_col_list, axis=1, inplace=True)
    
    #数据清洗：将空值替换为0
    fs3=fs2.fillna('0')
    
    #数据清洗：转换数值类型
    for i in fs3.columns:
        try:
            fs3[i]=fs3[i].astype('float')
        except:
            continue
    
    fs3['ticker']=ticker
    fs3['endDate']=fs3.index.strftime('%Y-%m-%d')
    
    return fs3

"""
['流动资产', '货币资金', '交易性金融资产', '衍生金融资产', '应收票据及应收账款',
 '应收票据', '应收账款', '应收款项融资', '预付款项', '其他应收款(合计)', '应收利息',
 '应收股利', '其他应收款', '买入返售金融资产', '存货', '划分为持有待售的资产',
 '一年内到期的非流动资产', '待摊费用', '待处理流动资产损益', '其他流动资产',
 '流动资产合计',
 '非流动资产', '发放贷款及垫款', '可供出售金融资产', '持有至到期投资', '长期应收款',
 '长期股权投资', '投资性房地产', '在建工程(合计)', '在建工程', '工程物资',
 '固定资产及清理(合计)', '固定资产净额', '固定资产清理', '生产性生物资产',
 '公益性生物资产', '油气资产', '使用权资产', '无形资产', '开发支出', '商誉',
 '长期待摊费用', '递延所得税资产', '其他非流动资产', 
 '非流动资产合计',
 '资产总计',
 '流动负债', '短期借款', '交易性金融负债', '应付票据及应付账款', '应付票据',
 '应付账款', '预收款项', '应付手续费及佣金', '应付职工薪酬', '应交税费',
 '其他应付款(合计)', '应付利息', '应付股利', '其他应付款', '预提费用', '一年内的递延收益',
 '应付短期债券', '一年内到期的非流动负债', '其他流动负债',
 '流动负债合计',
 '非流动负债', '长期借款', '应付债券', '租赁负债', '长期应付职工薪酬', '长期应付款(合计)',
 '长期应付款', '专项应付款', '预计非流动负债', '递延所得税负债', '长期递延收益',
 '其他非流动负债',
 '非流动负债合计',
 '负债合计',
 '所有者权益', '实收资本(或股本)', '资本公积', '减：库存股', '其他综合收益',
 '专项储备', '盈余公积', '一般风险准备', '未分配利润', '归属于母公司股东权益合计',
 '所有者权益(或股东权益)合计',
 '负债和所有者权益(或股东权益)总计',
 
 '一、营业总收入', '营业收入',
 '二、营业总成本', '营业成本', '营业税金及附加', '销售费用', '管理费用', '研发费用',
 '资产减值损失', '公允价值变动收益', '投资收益', '其中:对联营企业和合营企业的投资收益',
 '汇兑收益',
 '三、营业利润', '加:营业外收入', '减：营业外支出', '其中：非流动资产处置损失',
 '四、利润总额', '减：所得税费用',
 '五、净利润', '归属于母公司所有者的净利润', '少数股东损益',
 '六、每股收益', '基本每股收益(元/股)', '稀释每股收益(元/股)',
 '七、其他综合收益',
 '八、综合收益总额', '归属于母公司所有者的综合收益总额', '归属于少数股东的综合收益总额',
 '报表日期', '单位',
 
 '一、经营活动产生的现金流量', '销售商品、提供劳务收到的现金', '收到的税费返还',
 '收到的其他与经营活动有关的现金', '经营活动现金流入小计', '购买商品、接受劳务支付的现金',
 '支付给职工以及为职工支付的现金', '支付的各项税费', '支付的其他与经营活动有关的现金',
 '经营活动现金流出小计', '经营活动产生的现金流量净额',
 '二、投资活动产生的现金流量', '收回投资所收到的现金', '取得投资收益所收到的现金',
 '处置固定资产、无形资产和其他长期资产所收回的现金净额',
 '处置子公司及其他营业单位收到的现金净额', '收到的其他与投资活动有关的现金',
 '投资活动现金流入小计',
 '购建固定资产、无形资产和其他长期资产所支付的现金', '投资所支付的现金',
 '取得子公司及其他营业单位支付的现金净额', '支付的其他与投资活动有关的现金',
 '投资活动现金流出小计',
 '投资活动产生的现金流量净额',
 '三、筹资活动产生的现金流量', '吸收投资收到的现金', '其中：子公司吸收少数股东投资收到的现金',
 '取得借款收到的现金', '发行债券收到的现金', '收到其他与筹资活动有关的现金',
 '筹资活动现金流入小计',
 '偿还债务支付的现金', '分配股利、利润或偿付利息所支付的现金',
 '其中：子公司支付给少数股东的股利、利润', '支付其他与筹资活动有关的现金',
 '筹资活动现金流出小计',
 '筹资活动产生的现金流量净额',
 '四、汇率变动对现金及现金等价物的影响',
 '五、现金及现金等价物净增加额', '加:期初现金及现金等价物余额',
 '六、期末现金及现金等价物余额',
 
 '附注',
 '净利润',
 '未确认的投资损失', '资产减值准备',
 '固定资产折旧、油气资产折耗、生产性物资折旧', '无形资产摊销', '长期待摊费用摊销',
 '待摊费用的减少', '预提费用的增加', '处置固定资产、无形资产和其他长期资产的损失',
 '固定资产报废损失', '公允价值变动损失', '递延收益增加（减：减少）', '预计负债',
 '投资损失', '递延所得税资产减少', '递延所得税负债增加', '存货的减少',
 '经营性应收项目的减少', '经营性应付项目的增加', '已完工尚未结算款的减少(减:增加)',
 '已结算尚未完工款的增加(减:减少)',
 '其他',
 '经营活动产生现金流量净额',
 '债务转为资本', '一年内到期的可转换公司债券', '融资租入固定资产',
 '现金的期末余额', '现金的期初余额',
 '现金等价物的期末余额', '现金等价物的期初余额',
 '现金及现金等价物的净增加额',
 
 'ticker',
 'endDate']
"""

if __name__=='__main__':
    fstmt=get_fin_stmt_ak('600519.SS')    

#==============================================================================
if __name__=='__main__':
    endDate="2020-12-31"
    top=10
    
def liability_rank_china(endDate='latest',top=5):
    """
    获得某个报表日期资产负债率排行榜，限于中国A股
    获取的项目：所有原始项目
    注意：
    """
    error_flag=False

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Error(liability_rank_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #获取A股名单：代码，简称
    print("  Searching assets info of all A shares, it may take several hours ...")
    import akshare as ak
    a_shares= ak.stock_info_a_code_name()
    a_len=len(a_shares)
    print('\b'*99,' Collected China A-share stocks, altogether',a_len)
    
    #遍历所有A股上市公司的资产负债表，计算资产负债率
    a_share_codes=list(a_shares['code'])
    liab_df=pd.DataFrame()
    for t in a_share_codes:
        #抓取资产负债表
        try:
            #df= ak.stock_financial_report_sina(stock=t, symbol="资产负债表")
            # 上述命令运行一定次数（不到300次）后出错，无法继续！
            df = ak.stock_financial_analysis_indicator(stock=t)
        except:
            print("  #Warning(liability_rank_china): failed to get liability info of",t)
            continue
        sub1=df[df.index == endDate]
        sub2=sub1[['资产负债率(%)']]
        sub2['股票代码']=t
        liab_df=liab_df.append(sub2)
        
        #显示进度
        print_progress_percent2(t,a_share_codes,steps=10,leading_blanks=4)

    
    #获取全体股票的业绩报表，指定截止日期
    print('\b'*99," Retrieved financial info of",len(liab_df),"stocks ended on",endDate)
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    a_share_perf= ak.stock_em_yjbb(date=ak_date)
    a_share_industry=a_share_perf[['股票代码','股票简称','所处行业']]
    
    #合成
    liab_df['资产负债率(%)']=round(liab_df['资产负债率(%)'].astype('float'),2)
    alr_info_tmp=pd.merge(liab_df,a_share_industry,how='left',on='股票代码')
    alr_cols=['股票简称','股票代码','资产负债率(%)','所处行业']
    alr_info=alr_info_tmp[alr_cols]
    
    #后续处理：排序，找出资产负债率最低、最高的企业和行业
    alr_info.sort_values(by=['资产负债率(%)'],ascending=True,inplace=True)
    firm_top_lowest=alr_info.head(top)
    alr_info.sort_values(by=['资产负债率(%)'],ascending=False,inplace=True)
    firm_top_highest=alr_info.head(top)
    
    agg_cols={'资产负债率(%)':['mean','median']}
    group_df=alr_info.groupby('所处行业').agg(agg_cols)
    group_df.columns=['均值%','中位数%']
    group_df['均值%']=round(group_df['均值%'],2)
    group_df['中位数%']=round(group_df['中位数%'],2)
    
    group_df.sort_values(by=['均值%'],ascending=True,inplace=True)
    industry_lowest=group_df.head(top5)
    group_df.sort_values(by=['均值%'],ascending=False,inplace=True)
    industry_highest=group_df.head(top5)

    
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)    
    
    #打印：负债率最低最高的企业
    print("\n=== 企业排名：资产负债率，前"+str(top)+"名最低，截止"+endDate+" ===")
    print(firm_top_lowest.to_string(index=False))
    print("\n=== 企业排名：资产负债率，前"+str(top)+"名最高，截止"+endDate+" ===")
    print(firm_top_highest.to_string(index=False))

    #打印：负债率最低最高的行业
    print("\n=== 行业排名：资产负债率，前"+str(top)+"名最低，截止"+endDate+" ===")
    print(industry_top_lowest.to_string(index=False))
    print("\n=== 行业排名：资产负债率，前"+str(top)+"名最高，截止"+endDate+" ===")
    print(industry_top_highest.to_string(index=False))

    import datetime; today=datetime.date.today()
    print("\n*** 数据来源：sina/EM，"+str(today))
    
    return alr_info,group_df
    
if __name__=='__main__':
    liability_rank_china(endDate='2020-12-31')
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    start='2018-1-1'
    end='2021-11-24'
    period_type='all'

def calc_dupont_china(ticker,start,end,period_type='all'):
    """
    功能：计算股票ticker的杜邦分析项目，基于财报期末数直接计算，仅限于中国A股
    """
    fsr2=get_fin_stmt_ak(ticker)
    if fsr2 is None:
        print("  #Error(calc_dupont_china): failed to retrieved reports for",ticker)
        return None   
    
    fsr3=fsr2[(fsr2['endDate'] >= start) & (fsr2['endDate'] <= end)]
    
    #字段变换与计算
    fsr3['ROE']=fsr3['五、净利润']/fsr3['所有者权益(或股东权益)合计']
    fsr3['Profit Margin']=fsr3['五、净利润']/fsr3['一、营业总收入']
    fsr3['Total Assets Turnover']=fsr3['一、营业总收入']/fsr3['资产总计']
    fsr3['Equity Multiplier']=fsr3['资产总计']/fsr3['所有者权益(或股东权益)合计']
    
    dpidf=fsr3[['ticker','endDate','ROE','Profit Margin','Total Assets Turnover','Equity Multiplier']]    
    dpidf['pROE']=dpidf['Profit Margin']*dpidf['Total Assets Turnover']*dpidf['Equity Multiplier']
    
    return dpidf

if __name__=='__main__':
    df1=calc_dupont_china('600519.SS','2018-1-1','2021-12-31')
    df2=calc_dupont_china('600519.SS','2018-1-1','2021-12-31',period_type='annual')

#==============================================================================
if __name__=='__main__':
    ticker='600606.SS'
    start='2018-1-1'
    end='2021-11-24'
    period_type='all'

def calc_dupont_china_indicator(ticker,start,end,period_type='all'):
    """
    功能：计算股票ticker的杜邦分析项目，基于新浪、东方财富的财报指标抓取，仅限于中国A股
    """
    rates=['ROE','Profit Margin','Total Assets Turnover','Debts to Assets']
    rdf_list=prepare_fin_rate1tmr_china(ticker,rates,start,end,period_type)
    
    for rdf in rdf_list:
        if rdf is None:
            print("  #Error(calc_dupont_china): failed to retrieved reports for",ticker)
            return None   
        if len(rdf) == 0:
            print("  #Error(calc_dupont_china): zero record retrieved reports for",ticker)
            return None   
    
    #取出各项指标
    df_roe=rdf_list[rates.index('ROE')]
    df_roe['ROE']=df_roe['净资产收益率(%)']/100
    
    df_pm=rdf_list[rates.index('Profit Margin')]
    df_pm['Profit Margin']=df_pm['销售净利率(%)']/100
    
    df_tat=rdf_list[rates.index('Total Assets Turnover')]
    df_tat['Total Assets Turnover']=df_tat['总资产周转率(次)']
    
    df_em=rdf_list[rates.index('Debts to Assets')]
    df_em['Equity Multiplier']=1/(1-df_em['资产负债率(%)']/100)
    
    #多个数据表合并：合并列
    fsr=pd.concat([df_roe,df_pm,df_tat,df_em],axis=1,sort=True,join='inner')
    cols=['ROE','Profit Margin','Total Assets Turnover','Equity Multiplier']
    fsr2=fsr[cols]
    fsr2['ticker']=ticker
    fsr2['endDate']=fsr2.index.strftime('%Y-%m-%d')
    
    fsr2['month']=fsr2.index.month
    fsr2['periodType']=fsr2['month'].apply(lambda x: '年报' if x==12 else('中报' if x==6 else '季报'))
    
    #检查是否符合杜邦公式
    #fsr2['pROE']=fsr2['Profit Margin']*fsr2['Total Assets Turnover']*fsr2['Equity Multiplier']
    #注意：实际财务指标计算中，由于ROE和Profit Margin等指标中可能蕴含了加加减减等各种调整，ROE并非一定遵从杜邦公式
    
    return fsr2

if __name__=='__main__':
    df1=calc_dupont_china('600519.SS','2018-1-1','2021-12-31')
    df2=calc_dupont_china('600519.SS','2018-1-1','2021-12-31',period_type='annual')


#==============================================================================
if __name__=='__main__':
    tickerlist=['600606.SS','600519.SS','000002.SZ']
    fsdate='latest'
    scale1 = 10
    scale2 = 10
    hatchlist=['.', 'o', '\\']

def compare_dupont_china(tickerlist,fsdate='latest',scale1 = 10,scale2 = 10, \
                         hatchlist=['.', 'o', '\\'],printout=True,sort='PM'):
    """
    功能：获得tickerlist中每只股票的杜邦分析项目，绘制柱状叠加比较图
    tickerlist：股票代码列表，建议在10只以内
    fsdate：财报日期，默认为最新一期季报/年报，也可规定具体日期，格式：YYYY-MM-DD
    scale1：用于放大销售净利率，避免与权益乘数数量级不一致导致绘图难看问题，可自行调整
    scale2：用于放大总资产周转率，避免与权益乘数数量级不一致导致绘图难看问题，可自行调整
    hatchlist：绘制柱状图的纹理，用于黑白打印时区分，可自定义，
    可用的符号：'-', '+', 'x', '\\', '*', 'o', 'O', '.'    
    """
    error_flag=False
    if fsdate=='latest':
        import datetime as dt; end=str(dt.date.today())
        start=date_adjust(end, adjust=-365)
    else:
        valid=check_date(fsdate)
        if valid:
            end=fsdate
            start=date_adjust(end, adjust=-365)
        else:
            error_flag=True
    if error_flag: return None

    ticker = '公司'
    name1 = '销售净利率'
    name2 = '总资产周转率'
    name3 = '权益乘数'
    name4 = '净资产收益率'
    name5 = '财报日期'
    
    dpidflist,dpilist,fsdatelist,fstypelist=[],[],[],[]
    name1list,name2list,name3list,name4list,name5list,name6list=[],[],[],[],[],[]
    newtickerlist=[]
    for t in tickerlist:
        try:
            dpidf=calc_dupont_china(t,start,end)
            #dpidf=calc_dupont_china_indicator(t,start,end)
        except:
            print("  #Warning(compare_dupont_china): failed to get financial info for",t)
            continue
        if len(dpidf)==0:
            print("  #Warning(compare_dupont_china): lack of some accounting items for",t,'@',fsdate)
            continue
        dpi=dpidf.tail(1)
        
        newtickerlist=newtickerlist+[t]
        dpidflist=dpidflist+[dpidf]
        dpilist=dpilist+[dpi]
        fsdatelist=fsdatelist+[dpi['endDate'][0]]
        
        name1list=name1list+[dpi['Profit Margin'][0]*scale1]
        name2list=name2list+[dpi['Total Assets Turnover'][0]*scale2]
        name3list=name3list+[dpi['Equity Multiplier'][0]]
        name4list=name4list+[dpi['ROE'][0]]
        name5list=name5list+[dpi['endDate'][0]]
    
    tickerlist=newtickerlist
    raw_data = {ticker:tickerlist,
            name1:name1list,
            name2:name2list,
            name3:name3list,
            name4:name4list,
            name5:name5list,
            }

    df = pd.DataFrame(raw_data,columns=[ticker,name1,name2,name3,name4,name5])
    if sort=='PM':
        df.sort_values(name1,ascending=False,inplace=True)
    elif sort=='TAT':
        df.sort_values(name2,ascending=False,inplace=True)
    elif sort=='EM':
        df.sort_values(name3,ascending=False,inplace=True)
    else:
        df.sort_values(name1,ascending=False,inplace=True)
    
    num=len(df['公司'])
    for i in range(num):
        code=df.loc[i,'公司']
        df.loc[i,'公司']=codetranslate(code).replace("(A股)",'')
    
    f,ax1 = plt.subplots(1,figsize=(10,5))
    w = 0.75
    x = [i+1 for i in range(len(df[name1]))]
    #tick_pos = [i+(w/2.) for i in x]
    tick_pos = [i for i in x]

    ax1.bar(x,df[name3],width=w,bottom=[i+j for i,j in zip(df[name1],df[name2])], \
            label=name3,alpha=0.5,color='green',hatch=hatchlist[0], \
            edgecolor='black',align='center')
    ax1.bar(x,df[name2],width=w,bottom=df[name1],label=name2,alpha=0.5,color='red', \
            hatch=hatchlist[1], edgecolor='black',align='center')
    ax1.bar(x,df[name1],width=w,label=name1,alpha=0.5,color='blue', \
            hatch=hatchlist[2], edgecolor='black',align='center')

    plt.xticks(tick_pos,df[ticker])
    plt.ylabel("杜邦分析分解项目")
    
    endDate=df['财报日期'].values[0]        
    footnote='【财报日期】'+endDate
        
    import datetime; today=datetime.date.today()
    footnote1="【图示放大比例】"+name1+'：x'+str(scale1)+'，'+name2+'：x'+str(scale2)
    footnote2=footnote+'\n'+footnote1+'\n'+"数据来源：sina/EM，"+str(today)
    plt.xlabel(footnote2)
    
    plt.legend(loc='best')
    plt.title("杜邦分析对比图")
    plt.xlim([min(tick_pos)-w,max(tick_pos)+w])
    plt.show()    
    
    if printout:
        #设置打印对齐
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)    
        print("===== 杜邦分析分项数据表 =====")
        df[name1]=df[name1]/scale1
        df[name2]=df[name2]/scale2
    
        print(df.to_string(index=False))
        print("*** 数据来源：sina/EM，"+str(today))
    
    #合并所有历史记录
    alldf=pd.concat(dpidflist)
    alldf.dropna(inplace=True)
    #del alldf['pROE']
    
    """
    allnum=len(alldf)
    for i in range(allnum):
        code=alldf.loc[i,'periodType']
        if code == '3M': alldf.loc[i,'periodType']='Quarterly'
        else: alldf.loc[i,'periodType']='Annual'    
    """
    return alldf

if __name__=='__main__':
    tickerlist=['600606.SS','600519.SS','000002.SZ'] 
    df=compare_dupont_china(tickerlist,fsdate='latest',scale1 = 100,scale2 = 10)   

#==============================================================================
#==============================================================================
# 以上基于财报直接构造，以下基于获取的财务指标构造================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 

def get_fin_abstract_ak(ticker):
    """
    从akshare获取财报摘要，限于中国A股
    获取的项目：所有原始项目
    注意：不过滤日期
    """
    print("  Searching financial abstract for",ticker,"...")

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in STOCK_SUFFIX_CHINA):
        print("  #Warning(get_fin_abstract_ak): not a stock in China",ticker)
        return None        
    
    #财务报告摘要
    try:
        df1 = ak.stock_financial_abstract(stock=prefix)
    except:
        print("  #Warning(get_fin_abstract_ak): no financial information found for",ticker)
        return None
    """
    ['截止日期','每股净资产-摊薄/期末股数','每股现金流','每股资本公积金','固定资产合计',
     '流动资产合计','资产总计','长期负债合计','主营业务收入','财务费用','净利润']
    """
    if df1 is None:
        print("  #Warning(get_fin_abstract_ak): reports inaccessible for",ticker)
        return None
    
    if len(df1) == 0:
        print("  #Warning(get_fin_abstract_ak): zero reports found for",ticker)
        return None
    
    #数据清洗：去掉数值中的“元”字
    for c in df1.columns:
        try:
            df1[c]=df1[c].apply(lambda x: str(x).replace('元',''))
        except:
            continue

    #数据清洗：将空值替换为0
    df1b=df1.fillna('0')
    df2=df1b.replace('nan','0')
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue

    #设置索引
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    #按照日期升序排序
    df2.sort_index(inplace=True)
    
    df2['ticker']=ticker
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    
    return df2

if __name__=='__main__':
    fabs=get_fin_abstract_ak('600519.SS')    

#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 
    
def get_fin_indicator_ak(ticker):
    """
    从akshare获取财报重要指标，限于中国A股，历史数据
    获取的项目：所有原始项目
    注意：不过滤日期
    """
    print('\b'*99," Searching financial indicators for",ticker,"...")

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in STOCK_SUFFIX_CHINA):
        print("  #Warning(get_fin_indicator_ak): not a stock in China",ticker)
        return None        
    
    #财务报告重要指标
    try:
        df1 = ak.stock_financial_analysis_indicator(stock=prefix)
        print('\b'*99," Calculating financial indicators for the above stock ...")
    except:
        print('\b'*99," #Warning(get_fin_indicator_ak): failed to get financial info for",ticker)
        return None
    """
    ['摊薄每股收益(元)','加权每股收益(元)','每股收益_调整后(元)','扣除非经常性损益后的每股收益(元)',
     '每股净资产_调整前(元)','每股净资产_调整后(元)','调整后的每股净资产(元)',
     '每股经营性现金流(元)',
     '每股资本公积金(元)','每股未分配利润(元)',
     '总资产利润率(%)','总资产净利润率(%)','资产报酬率(%)',
     '主营业务利润率(%)','成本费用利润率(%)','营业利润率(%)','主营业务成本率(%)','销售净利率(%)',
     '股本报酬率(%)','净资产报酬率(%)','净资产收益率(%)','加权净资产收益率(%)',
     '投资收益率(%)',
     '主营业务收入增长率(%)','净利润增长率(%)','净资产增长率(%)','总资产增长率(%)',
     '销售毛利率(%)','主营业务利润(元)',
     '三项费用比重',
     '非主营比重','主营利润比重','股息发放率(%)',
     '扣除非经常性损益后的净利润(元)',
     '应收账款周转率(次)','应收账款周转天数(天)','存货周转天数(天)','存货周转率(次)',
     '固定资产周转率(次)','总资产周转率(次)','总资产周转天数(天)','流动资产周转率(次)',
     '流动资产周转天数(天)','股东权益周转率(次)','流动比率','速动比率','现金比率(%)',
     '利息支付倍数','长期债务与营运资金比率(%)','股东权益比率(%)','长期负债比率(%)',
     '股东权益与固定资产比率(%)','负债与所有者权益比率(%)','长期资产与长期资金比率(%)',
     '资本化比率(%)','固定资产净值率(%)','资本固定化比率(%)','产权比率(%)',
     '清算价值比率(%)','固定资产比重(%)','资产负债率(%)','总资产(元)',
     '经营现金净流量对销售收入比率(%)','资产的经营现金流量回报率(%)',
     '经营现金净流量与净利润的比率(%)','经营现金净流量对负债比率(%)','现金流量比率(%)',
     '短期股票投资(元)','短期债券投资(元)','短期其它经营性投资(元)',
     '长期股票投资(元)','长期债券投资(元)','长期其它经营性投资(元)',
     '1年以内应收帐款(元)','1-2年以内应收帐款(元)','2-3年以内应收帐款(元)',
     '3年以内应收帐款(元)',
     '1年以内预付货款(元)','1-2年以内预付货款(元)','2-3年以内预付货款(元)',
     '3年以内预付货款(元)',
     '1年以内其它应收款(元)','1-2年以内其它应收款(元)','2-3年以内其它应收款(元)',
     '3年以内其它应收款(元)']
    """
    if df1 is None:
        print('\b'*99," #Warning(get_fin_indicator_ak): reports inaccessible for",ticker)
        return None
    
    if len(df1) == 0:
        print('\b'*99," #Warning(get_fin_indicator_ak): zero reports found for",ticker)
        return None
    
    #设置索引    
    df1['截止日期']=df1.index
    df1['date']=pd.to_datetime(df1['截止日期'])
    df1.set_index('date',inplace=True)
    #按照日期升序排序
    df1.sort_index(inplace=True)
    
    #数据清洗：将空值替换为0
    df1b=df1.fillna('0')
    #数据清洗：将"--"值替换为0
    df2=df1b.replace('--','0')
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue
    
    df2['ticker']=ticker
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    
    return df2

if __name__=='__main__':
    find=get_fin_indicator_ak('600606.SS')    

#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 
    endDate="2020-12-31"
    
def get_fin_performance_ak(ticker,endDate):
    """
    从akshare获取业绩报表，限于中国A股
    获取的项目：所有原始项目
    注意：不过滤日期
    """
    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in STOCK_SUFFIX_CHINA):
        print("  #Warning(get_fin_performance_ak): not a stock in China",ticker)
        return None        
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving financial performance for",ticker,'ended on',endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Calculating financial performance in the above period ...")
    
    if df1 is None:
        print("  #Warning(get_fin_performance_ak): reports inaccessible for",ticker)
        return None
    if len(df1) == 0:
        print("  #Warning(get_fin_performance_ak): zero reports found for",ticker)
        return None
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照股票代码升序+最新公告日期降序排序
    df1b=df1a.sort_values(by=['股票代码','最新公告日期'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])
    
    #筛选特定股票的数据
    tickerdf=df2[df2['ticker'] == prefix]
    industry=tickerdf['所处行业'].values[0]
    df_industry=df2[df2['所处行业'] == industry]
    num_industry=len(df_industry)
    
    rates_industry=['每股收益','营业收入','营业收入-同比增长','营业收入-季度环比增长',
                    '净利润','净利润-同比增长','净利润-季度环比增长','每股净资产',
                    '净资产收益率','每股经营现金流量','销售毛利率']
    for r in rates_industry:
        i_min=df_industry[r].min()
        i_max=df_industry[r].max()
        i_avg=df_industry[r].mean()
        i_med=df_industry[r].median()
        
        tickerdf[r+"-行业最小值"]=i_min
        tickerdf[r+"-行业最大值"]=i_max
        tickerdf[r+"-行业均值"]=i_avg
        tickerdf[r+"-行业中位数"]=i_med
        
        x=tickerdf[r].values[0]
        x_quantile=arg_percentile(df_industry[r], x)
        tickerdf[r+"-行业分位数"]=x_quantile*100
        
        if r in ['营业收入','净利润']:
            i_sum=df_industry[r].sum()
            tickerdf[r+"-占行业份额"]=tickerdf[r]/i_sum*100
    tickerdf['同行数量']=num_industry
    
    #排序字段
    cols=list(tickerdf)
    cols.sort(reverse=False)
    tickerdf2=tickerdf[cols]
    
    return tickerdf2

"""
['endDate', 'ticker',
 '净利润', '净利润-占行业份额', '净利润-行业中位数', '净利润-行业分位数', '净利润-行业均值', 
 '净利润-行业最大值', '净利润-行业最小值',
 
 '净利润-同比增长', '净利润-同比增长-行业中位数', '净利润-同比增长-行业分位数',
 '净利润-同比增长-行业均值', '净利润-同比增长-行业最大值', '净利润-同比增长-行业最小值',
 
 '净利润-季度环比增长', '净利润-季度环比增长-行业中位数', '净利润-季度环比增长-行业分位数',
 '净利润-季度环比增长-行业均值', '净利润-季度环比增长-行业最大值', 
 '净利润-季度环比增长-行业最小值',
 
 '净资产收益率', '净资产收益率-行业中位数', '净资产收益率-行业分位数', '净资产收益率-行业均值',
 '净资产收益率-行业最大值', '净资产收益率-行业最小值',
 '序号', '截止日期', '所处行业', '最新公告日期',
 
 '每股净资产', '每股净资产-行业中位数', '每股净资产-行业分位数', '每股净资产-行业均值',
 '每股净资产-行业最大值', '每股净资产-行业最小值',
 
 '每股收益', '每股收益-行业中位数', '每股收益-行业分位数', '每股收益-行业均值',
 '每股收益-行业最大值', '每股收益-行业最小值',
 
 '每股经营现金流量', '每股经营现金流量-行业中位数', '每股经营现金流量-行业分位数',
 '每股经营现金流量-行业均值', '每股经营现金流量-行业最大值', '每股经营现金流量-行业最小值',
 '股票代码', '股票简称',
 
 '营业收入', '营业收入-占行业份额', '营业收入-行业中位数', '营业收入-行业分位数', '营业收入-行业均值', '营业收入-行业最大值',
 '营业收入-行业最小值',

 '营业收入-同比增长', '营业收入-同比增长-行业中位数', '营业收入-同比增长-行业分位数',
 '营业收入-同比增长-行业均值', '营业收入-同比增长-行业最大值', '营业收入-同比增长-行业最小值',
 
 '营业收入-季度环比增长', '营业收入-季度环比增长-行业中位数', '营业收入-季度环比增长-行业分位数',
 '营业收入-季度环比增长-行业均值', '营业收入-季度环比增长-行业最大值',
 '营业收入-季度环比增长-行业最小值',
 
 '销售毛利率', '销售毛利率-行业中位数', '销售毛利率-行业分位数', '销售毛利率-行业均值',
 '销售毛利率-行业最大值', '销售毛利率-行业最小值']
"""

if __name__=='__main__':
    fpfm=get_fin_performance_ak('600519.SS','2020-12-31')    

#==============================================================================
    
def industry_name_em():
    """
    功能：从东方财富获取行业分类名称，限于中国A股
    """
    #获取最近的报表日期
    import datetime; today=datetime.date.today()
    start=date_adjust(today, adjust=-365)
    fs_dates=cvt_fs_dates(start,today,'all')
    endDate=fs_dates[-1:][0]

    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving EM industry names ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Summerizing industry names for the above period ...")

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)

    industry_list=list(set(list(df2['所处行业'])))  
    try:
        industry_list.remove('0')
    except: pass

    #对列表中的中文字符串排序
    from pypinyin import pinyin, Style
    industry_list.sort(key = lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

    print("\n===== 行业分类：东方财富 =====\n")
    n=0
    for i in industry_list:
        n=n+1
        print(i,end=' ')
        if n==5:
            n=0
            print('')
    if n <5: print('')
    #import datetime; today=datetime.date.today()
    print("\n***来源：东方财富,",endDate)
    
    return industry_list    

if __name__=='__main__':
    df=industry_name_em()
#==============================================================================
if __name__=='__main__':
    industry="银行"
    rate="营业收入"
    top=5
    
def industry_rank_em(industry="银行",rate="oper revenue",top=5):
    """
    功能：从东方财富获取最新行业排名前几名，按照财务指标，限于中国A股
    """
    #获取最近的报表日期
    import datetime; today=datetime.date.today()
    start=date_adjust(today, adjust=-365)
    fs_dates=cvt_fs_dates(start,today,'all')
    endDate=fs_dates[-1:][0]

    rate_check=['eps','oper revenue','oper revenue growth','net earnings', 
                'earnings growth','naps','rona','oper cfps', 'gross margin']
    rate_cols=['每股收益','营业收入','营业收入-同比增长','净利润', 
                '净利润-同比增长','每股净资产','净资产收益率', 
                '每股经营现金流量', '销售毛利率']
    if not (rate in rate_check):
        print("  #Warning(industry_rank_em): unsupported financial rate",rate)
        print("  Supported ranking rates:",rate_check)
        return None
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving EM industry names ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Summerizing stock performance for industry",industry,'by',rate)
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照所处行业升序
    df1b=df1a.sort_values(by=['所处行业','股票代码'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=round(df2[c].astype('float'),2)
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])

    #筛选特定行业的股票
    industry_check=list(set(list(df2['所处行业'])))
    if not (industry in industry_check):
        print("  #Warning(industry_rank_em): unsupported em industry name",industry)
        print("  See supported industry by command: df=industry_name_em()")
        return None
        
    df3=df2[df2['所处行业'] == industry]
    rpos=rate_check.index(rate)
    rate=rate_cols[rpos]    #将财务指标名称从英文转为中文
    
    cols=['股票代码','股票简称','最新公告日期']+[rate]
    df_industry=df3[cols]
    i_min=df_industry[rate].min()
    i_max=df_industry[rate].max()
    i_avg=df_industry[rate].mean()
    i_med=df_industry[rate].median()
    i_sum=df_industry[rate].sum()
    num_industry=len(df_industry)
    
    ticker_list=list(df_industry['股票代码'])
    ticker_result=pd.DataFrame()
    for t in ticker_list:
        tickerdf=df_industry[df_industry['股票代码'] == t]
        x=tickerdf[rate].values[0]
        x_quantile=arg_percentile(df_industry[rate], x)
        tickerdf[rate+"-行业分位数%"]=x_quantile*100
        
        if rate in ['营业收入','净利润']:
            tickerdf[rate+"-占行业份额%"]=tickerdf[rate]/i_sum*100
            
        ticker_result=ticker_result.append(tickerdf)
    
    #排序：降序
    ticker_result["排名"]=ticker_result[rate].rank(ascending=False).astype('int')
    ticker_result.sort_values(by=rate,ascending=False,inplace=True) 
    for c in ticker_result.columns:
        try:
            ticker_result[c]=ticker_result[c].apply(lambda x: simple_number(x))
        except:
            continue
    
    #打印
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    if top > 0:
        rank_prefix="前"
        topn=top
        printdf=ticker_result.head(topn)
    else:
        rank_prefix="后"
        topn=-top
        printdf=ticker_result.tail(topn)
    
    print("\n===== 行业排名："+rate+"，"+rank_prefix+str(topn)+"名"+" =====")
    print("行业内企业个数 ：",num_industry)
    print("行业最小/最大值：",simple_number(i_min),'/',simple_number(i_max))
    print("行业均值/中位数：",simple_number(i_avg),'/',simple_number(i_med))
    print('')
    print(printdf.to_string(index=False))
    
    return ticker_result  

if __name__=='__main__':
    df=industry_rank_em("银行","oper revenue",top=10)
    df=industry_rank_em("银行","oper revenue",top=-10)
    
    df=industry_rank_em("银行","?",top=-10)
    
    df=industry_rank_em("银行",'eps',top=20)
    df=industry_rank_em("银行",'eps',top=-25)
    df=industry_rank_em("银行",'naps',top=20)
    df=industry_rank_em("银行",'oper cfps',top=20)
    
    df=industry_rank_em("银行",'rona',top=20)
    
    df=industry_rank_em("银行",'oper revenue growth',top=5)
    df=industry_rank_em("银行",'earnings growth',top=5)

#==============================================================================
if __name__=='__main__':
    industry="银行"
    tickers=['600036.SS','000001.SZ','601328.SS','601939.SS','601288.SS','601398.SS','601988.SS']
    rates=['eps','naps','oper cfps','oper revenue growth','earnings growth']
    
    tickers=''
    
def industry_rank_em2(tickers,rates=['eps','naps'],industry="银行",top=10):
    """
    功能：从东方财富获取某些股票在某些财务指标方面的行业排名，限于中国A股
    注意：当tickers为''时列出排名前或后top的股票
    """
    error_flag=False
    #获取最近的报表日期
    import datetime; today=datetime.date.today()
    start=date_adjust(today, adjust=-365)
    fs_dates=cvt_fs_dates(start,today,'all')
    endDate=fs_dates[-1:][0]

    if isinstance(tickers,str): tickers_selected=[tickers]
    elif isinstance(tickers,list): tickers_selected=tickers
    else:
        print("  #Warning(industry_rank_em2): unsupported stock codes",tickers)
        print("  Supporting a stock code or a list of stock codes")
        error_flag=True
    if error_flag: return
    
    stocks_selected=[]
    for t in tickers_selected:
        #是否中国股票
        result,prefix,suffix=split_prefix_suffix(t)
        if not (suffix in STOCK_SUFFIX_CHINA) and not (tickers == ''):
            print("  #Warning(industry_rank_em2): not a stock in China",t)
            error_flag=True
        stocks_selected=stocks_selected+[prefix]
    if error_flag: return
    
    rate_check=['eps','oper revenue','oper revenue growth','net earnings', 
                'earnings growth','naps','rona','oper cfps', 'gross margin']
    rate_cols=['每股收益','营业收入','营业收入-同比增长','净利润', 
                '净利润-同比增长','每股净资产','净资产收益率', 
                '每股经营现金流量', '销售毛利率']
    if isinstance(rates,str): rate_list=[rates]
    elif isinstance(rates,list): rate_list=rates
    else:
        print("  #Warning(industry_rank_em2): unsupported financial rates",rates)
        print("  Supporting a financial rate or a list of rates as follows:",rate_check)
        error_flag=True
    if error_flag: return
    
    for rate in rate_list:
        if not (rate in rate_check):
            print("  #Warning(industry_rank_em2): unsupported financial rate",rate)
            print("  Supported ranking rates:",rate_check)
            error_flag=True
    if error_flag: return
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving EM industry names ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Summerizing stock performance for industry",industry,'by',rate)
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照所处行业升序
    df1b=df1a.sort_values(by=['所处行业','股票代码'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=round(df2[c].astype('float'),2)
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])

    #检查是否支持特定行业
    industry_check=list(set(list(df2['所处行业'])))
    if not (industry in industry_check):
        print("  #Warning(industry_rank_em2): unsupported em industry name",industry)
        print("  See supported industry by command: df=industry_name_em()")
        error_flag=True
    if error_flag: return
    
    df3=df2[df2['所处行业'] == industry]

    #筛选特定行业的股票
    for r in rate_list:
        rpos=rate_check.index(r)
        rate=rate_cols[rpos]
        
        cols=['股票代码','股票简称','最新公告日期']+[rate]
        df_industry=df3[cols]
        i_min=df_industry[rate].min()
        i_max=df_industry[rate].max()
        i_avg=df_industry[rate].mean()
        i_med=df_industry[rate].median()
        i_sum=df_industry[rate].sum()
        num_industry=len(df_industry)
        
        ticker_list=list(df_industry['股票代码'])
        ticker_result=pd.DataFrame()
        for t in ticker_list:
            tickerdf=df_industry[df_industry['股票代码'] == t]
            x=tickerdf[rate].values[0]
            x_quantile=arg_percentile(df_industry[rate], x)
            tickerdf[rate+"-行业分位数%"]=x_quantile*100
            
            if rate in ['营业收入','净利润']:
                tickerdf[rate+"-占行业份额%"]=tickerdf[rate]/i_sum*100
                
            ticker_result=ticker_result.append(tickerdf)
        
        #排序：降序
        ticker_result["排名"]=ticker_result[rate].rank(ascending=False).astype('int')
        ticker_result.sort_values(by=rate,ascending=False,inplace=True) 
        for c in ticker_result.columns:
            try:
                ticker_result[c]=ticker_result[c].apply(lambda x: simple_number(x))
            except:
                continue
        
        #打印
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        
        if (len(stocks_selected) >= 1) and not (tickers == ''):
            printdf=ticker_result[ticker_result['股票代码'].isin(stocks_selected)]
        else:
            if top > 0:
                printdf=ticker_result.head(top)
            else:
                printdf=ticker_result.tail(-top)
        
        print("\n===== 行业排名："+industry+'，'+rate+" =====")
        print("行业内企业个数 ：",num_industry)
        print("行业最小/最大值：",simple_number(i_min),'/',simple_number(i_max))
        print("行业均值/中位数：",simple_number(i_avg),'/',simple_number(i_med))
        print('')
        print(printdf.to_string(index=False))
    
    return  

if __name__=='__main__':
    industry="银行"
    tickers1=['600036.SS','000001.SZ','601009.SS','001227.SZ']
    tickers2=['601328.SS','601939.SS','601288.SS','601398.SS','601988.SS']
    rates=['eps','naps','oper cfps','oper revenue growth','earnings growth']

    industry_rank_em2(tickers1+tickers2,rates,industry)
    industry_rank_em2('',rates,industry,top=5)  #每项指标的行业前几名
    
#==============================================================================
def simple_number(number):
    """
    功能：将数字表示为易读的字符化数值，并截取小数点
    """
    
    if number < 0.001:
        number1=round(number,5)
        suff=''  
    
    if number < 1:
        number1=round(number,4)
        suff=''  

    if number >= 1:
        number1=round(number,2)
        suff=''
    
    if number >= 10000:
        number1=round(number/10000,2)
        suff='万'

    if number >= 1000000:
        number1=round(number/1000000,2)
        suff='百万'

    if number >= 100000000:
        number1=round(number/100000000,2)
        suff='亿'        

    if number >= 1000000000000:
        number1=round(number/1000000000000,2)
        suff='万亿'        
        
    number2=str(number1)+suff
    
    return number2

if __name__=='__main__':
    simple_number(0.03257)
    simple_number(0.58726)
    simple_number(1.3289)
    simple_number(13283.569)
    simple_number(1234569874123)
#==============================================================================

if __name__=='__main__':
    tickers=["600606.SS","600606.SS"] 
    endDate="2020-12-31"
    
def get_fin_performance_akm(tickers,endDate):
    """
    从akshare获取业绩报表，多个股票，1个截止日期，限于中国A股
    获取的项目：所有原始项目
    注意：
    """

    #是否中国股票
    prefix_list=[]
    for t in tickers:
        result,prefix,suffix=split_prefix_suffix(t)
        if not (suffix in STOCK_SUFFIX_CHINA):
            print("  #Warning(get_fin_performance_akm): not a stock in China",t)
            return None  
        prefix_list=prefix_list+[prefix]
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving financial performance ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    print('\b'*99," Calculating financial performance for the above period")
    
    if df1 is None:
        print("  #Warning(get_fin_performance_akm): reports inaccessible for",endDate)
        return None
    if len(df1) == 0:
        print("  #Warning(get_fin_performance_akm): zero reports found for",endDate)
        return None
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照股票代码升序+最新公告日期降序排序
    df1b=df1a.sort_values(by=['股票代码','最新公告日期'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])
    
    #筛选特定股票的数据
    mtdf=pd.DataFrame()
    for prefix in prefix_list:
        tickerdf=df2[df2['ticker'] == prefix]
        industry=tickerdf['所处行业'].values[0]
        df_industry=df2[df2['所处行业'] == industry]
        num_industry=len(df_industry)
        
        rates_industry=['每股收益','营业收入','营业收入-同比增长','营业收入-季度环比增长',
                        '净利润','净利润-同比增长','净利润-季度环比增长','每股净资产',
                        '净资产收益率','每股经营现金流量','销售毛利率']
        for r in rates_industry:
            i_min=df_industry[r].min()
            i_max=df_industry[r].max()
            i_avg=df_industry[r].mean()
            i_med=df_industry[r].median()
            
            tickerdf[r+"-行业最小值"]=i_min
            tickerdf[r+"-行业最大值"]=i_max
            tickerdf[r+"-行业均值"]=i_avg
            tickerdf[r+"-行业中位数"]=i_med
            
            x=tickerdf[r].values[0]
            x_quantile=arg_percentile(df_industry[r], x)
            tickerdf[r+"-行业分位数"]=x_quantile*100
            
            if r in ['营业收入','净利润']:
                i_sum=df_industry[r].sum()
                tickerdf[r+"-占行业份额"]=tickerdf[r]/i_sum*100
        tickerdf['同行数量']=num_industry
        
        #排序字段
        cols=list(tickerdf)
        cols.sort(reverse=False)
        tickerdf2=tickerdf[cols]
        
        #加入结果数据表，用于返回
        mtdf=mtdf.append(tickerdf2)
    
    return mtdf

if __name__=='__main__':
    tickers=["600519.SS","600606.SS"] 
    mtdf=get_fin_performance_akm(tickers,'2020-12-31')
    
#==============================================================================
if __name__=='__main__':
    fin_rate="Current Ratio"
    prompt=False

def cvt_fin_rate(fin_rate,prompt=False,printout=True):
    """
    功能：查表获得财务指标的计算来源以及字段名称
    """
    
    #财务指标结构字典
    rate_dict={
        #数据源函数：get_fin_indicator_ak
        "diluted eps":("get_fin_indicator_ak","摊薄每股收益(元)"),
        "weighted eps":("get_fin_indicator_ak","加权每股收益(元)"),
        "adjusted eps":("get_fin_indicator_ak","每股收益_调整后(元)"),
        "recurring eps":("get_fin_indicator_ak","扣除非经常性损益后的每股收益(元)"),
        
        "naps":("get_fin_indicator_ak","每股净资产_调整前(元)"),
        "net assets per share":("get_fin_indicator_ak","每股净资产_调整前(元)"),
        "adjusted naps":("get_fin_indicator_ak","每股净资产_调整后(元)"),
        "capital reserve per share":("get_fin_indicator_ak","每股资本公积金(元)"),
        "undistributed profit per share":("get_fin_indicator_ak","每股未分配利润(元)"),
        
        "roa":("get_fin_indicator_ak","资产报酬率(%)"),
        
        "reward on shareholder equity":("get_fin_indicator_ak","股本报酬率(%)"),
        "reward on net assets":("get_fin_indicator_ak","净资产报酬率(%)"),
        "return on net assets":("get_fin_indicator_ak","净资产收益率(%)"),
        "rona":("get_fin_indicator_ak","净资产收益率(%)"),
        "weighted return on net assets":("get_fin_indicator_ak","加权净资产收益率(%)"),
        "weighted rona":("get_fin_indicator_ak","加权净资产收益率(%)"),
        "return on investment":("get_fin_indicator_ak","投资收益率(%)"),
        "roi":("get_fin_indicator_ak","投资收益率(%)"),
        
        "profit margin":("get_fin_indicator_ak","销售净利率(%)"),
        "gross margin":("get_fin_indicator_ak","销售毛利率(%)"),
        "oper profit share":("get_fin_indicator_ak","主营利润比重"),
        "payout ratio":("get_fin_indicator_ak","股息发放率(%)"),
        "roi":("get_fin_indicator_ak","投资收益率(%)"),
        
        "oper revenue growth":("get_fin_indicator_ak","主营业务收入增长率(%)"),
        "profit margin growth":("get_fin_indicator_ak","净利润增长率(%)"),
        "net assets growth":("get_fin_indicator_ak","净资产增长率(%)"),
        "total assets growth":("get_fin_indicator_ak","总资产增长率(%)"),
        
        "receivables turnover":("get_fin_indicator_ak","应收账款周转率(次)"),
        "inventory turnover":("get_fin_indicator_ak","存货周转率(次)"),
        "fixed assets turnover":("get_fin_indicator_ak","固定资产周转率(次)"),
        "total assets turnover":("get_fin_indicator_ak","总资产周转率(次)"),
        "current assets turnover":("get_fin_indicator_ak","流动资产周转率(次)"),
        "equity assets turnover":("get_fin_indicator_ak","股东权益周转率(次)"),
        
        "current ratio":("get_fin_indicator_ak","流动比率"),
        "quick ratio":("get_fin_indicator_ak","速动比率"),
        "cash ratio":("get_fin_indicator_ak","现金比率(%)"),
        "tie":("get_fin_indicator_ak","利息支付倍数"),
        "times interest earned":("get_fin_indicator_ak","利息支付倍数"),
        "equity to assets":("get_fin_indicator_ak","股东权益比率(%)"),
        "ltd%":("get_fin_indicator_ak","长期负债比率(%)"),
        "long-term debts%":("get_fin_indicator_ak","长期负债比率(%)"),
        "debts to equity":("get_fin_indicator_ak","负债与所有者权益比率(%)"),
        "liabilities to equity":("get_fin_indicator_ak","产权比率(%)"),
        "capitalization%":("get_fin_indicator_ak","资本化比率(%)"),
        "ppe residual":("get_fin_indicator_ak","固定资产净值率(%)"),
        "tangible assets to debts":("get_fin_indicator_ak","清算价值比率(%)"),
        "fixed assets%":("get_fin_indicator_ak","固定资产比重(%)"),
        "debts to assets":("get_fin_indicator_ak","资产负债率(%)"),
        "cash flow ratio":("get_fin_indicator_ak","现金流量比率(%)"),
        "cashflow ratio":("get_fin_indicator_ak","现金流量比率(%)"),
        "net oper cashflow to revenue":("get_fin_indicator_ak","经营现金净流量对销售收入比率(%)"),

        #数据源函数：get_fin_performance_ak，百分比
        "net earnings":("get_fin_performance_ak","净利润"),
        "earnings industry share":("get_fin_performance_ak","净利润-占行业份额"),
        "earnings industry quantile":("get_fin_performance_ak","净利润-行业分位数"),
        "earnings growth":("get_fin_performance_ak","净利润-同比增长"),
        "earnings growth industry quantile":("get_fin_performance_ak","净利润-同比增长-行业分位数"),

        "roe":("get_fin_performance_ak","净资产收益率"),
        "roe industry quantile":("get_fin_performance_ak","净资产收益率-行业分位数"),
        "naps":("get_fin_performance_ak","每股净资产"),
        "naps industry quantile":("get_fin_performance_ak","每股净资产-行业分位数"),
        "eps":("get_fin_performance_ak","每股收益"),
        "eps industry quantile":("get_fin_performance_ak","每股收益-行业分位数"),

        "oper cfps":("get_fin_performance_ak","每股经营现金流量"),
        "oper cfps industry quantile":("get_fin_performance_ak","每股经营现金流量-行业分位数"),
        
        "oper revenue":("get_fin_performance_ak","营业收入"),
        "oper revenue industry share":("get_fin_performance_ak","营业收入-占行业份额"),
        "oper revenue industry quantile":("get_fin_performance_ak","营业收入-行业分位数"),
        "oper revenue growth":("get_fin_performance_ak","营业收入-同比增长"),
        "oper revenue growth industry quantile":("get_fin_performance_ak","营业收入-同比增长-行业分位数"),

        "gross margin industry quantile":("get_fin_performance_ak","销售毛利率-行业分位数"),

        #数据源函数：get_fin_abstract_ak
        "diluted naps":("get_fin_abstract_ak","每股净资产-摊薄/期末股数"),
        "cfps":("get_fin_abstract_ak","每股现金流"),
        }

    #是否需要提示？
    if prompt or (fin_rate in ['?','？']):
        promptdf=pd.DataFrame(columns=('财务指标代码', '财务指标名称'))
        key_list=rate_dict.keys()   
        for k in key_list:
            #print(k)
            result=rate_dict.get(k)
            (source,name_cn)=result
            s=pd.Series({'财务指标代码':k, '财务指标名称':name_cn})
            promptdf=promptdf.append(s, ignore_index=True)
        promptdf.sort_values('财务指标代码',ascending=True,inplace=True)   

        #打印对齐   
        if printout:
            pd.set_option('display.max_columns', 1000)
            pd.set_option('display.width', 1000)
            pd.set_option('display.max_colwidth', 1000)
            pd.set_option('display.unicode.ambiguous_as_wide', True)
            pd.set_option('display.unicode.east_asian_width', True)
            print(promptdf.to_string(index=False))
            return None,None
        else:
            return promptdf,None
        
    #搜索字典
    rate=fin_rate.lower()
    result=rate_dict.get(rate)
    if result is None:
        return None,None
    (source,name_cn)=result
    
    return source,name_cn

if __name__=='__main__':
    cvt_fin_rate("?",prompt=True)
    cvt_fin_rate("Current Ratio")
    cvt_fin_rate("Quick Ratio")
#==============================================================================
def arg_percentile(series, x):
    """
    功能：求x在序列series中的分位数
    """
    import numpy as np
    # 分位数的启始区间
    a, b = 0, 1
    while True:
        # m是a、b的终点
        m = (a+b)/2
        # 可以打印查看求解过程
        # print(np.percentile(series, 100*m), x)
        if np.percentile(series, 100*m) >= x:
            b = m
        elif np.percentile(series, 100*m) < x:
            a = m
        # 如果区间左右端点足够靠近，则退出循环。
        if np.abs(a-b) <= 0.000001:
            break
    return m

#==============================================================================
if __name__=='__main__':
    start='2020-1-1'
    end='2021-6-30'
    period_type='all'
    period_type='annual'
    period_type='quarterly'
    period_type='semiannual'

def cvt_fs_dates(start,end,period_type='all'):
    """
    功能：基于年报类型给出期间内财报的各个截止日期列表
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(get_fs_dates): invalid period",start,end)
        return None
    
    #构造所有年报日期
    start_year=start1.year
    end_year=end1.year
    
    fs_dates_all=[]
    q1_str='-03-31'; q2_str='-06-30'; q3_str='-09-30'; q4_str='-12-31'
    for y in range(start_year,end_year+1):
        #print(y)
        fs_dates_all=fs_dates_all+[str(y)+q1_str,str(y)+q2_str,str(y)+q3_str,str(y)+q4_str]
    
    #过滤年报日期
    fs_dates=[]
    for d in fs_dates_all:
        dd=pd.to_datetime(d)
        #print(dd,start1,end1)
        if (dd < start1) or (dd > end1): continue
        
        #区分年报季报
        dd_month=dd.month
        if period_type == 'annual':
            if not (dd_month == 12): continue
        if period_type == 'semiannual':
            if not (dd_month in [6,12]): continue
        
        fs_dates=fs_dates+[d]  
              
    return fs_dates

if __name__=='__main__':
    cvt_fs_dates('2020-7-1','2021-10-1')
    cvt_fs_dates('2020-7-1','2021-10-1',period_type='annual')
    cvt_fs_dates('2020-7-1','2021-10-1',period_type='semiannual')
    cvt_fs_dates('2020-7-1','2021-10-1',period_type='quarterly')
    
#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 
    rate1='ROA'
    rate2='Oper Revenue Industry Share'
    start='2020-1-1'
    end='2021-6-30'
    period_type='all'
    
    period_type='annual'
    period_type='quarterly'
    period_type='semiannual'
    
def prepare_fin_rate1t2r_china(ticker,rate1,rate2,start,end,period_type='all'):
    """
    功能：准备财务准备，1个股票，2个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_fin_rate1t2r_china): invalid period",start,end)
        return None,None

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in STOCK_SUFFIX_CHINA):
        print("  #Warning(prepare_fin_rate1t2r_china): not a stock in China",ticker)
        return None,None        

    #检查指标是否支持
    fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    rate_list=list(fin_rates['财务指标代码'])
    if not (rate1.lower() in rate_list):
        print("  #Warning(prepare_fin_rate1t2r_china): unsupported financial rate",rate1)
        return None,None
    if not (rate2.lower() in rate_list):
        print("  #Warning(prepare_fin_rate1t2r_china): unsupported financial rate",rate2)
        return None,None    
    #--------------------------------------------------------------------------
    func1,name1=cvt_fin_rate(rate1)
    func2,name2=cvt_fin_rate(rate2)

    if func1 == 'get_fin_indicator_ak':
        find1=get_fin_indicator_ak(ticker)
        ratedf1=find1[['ticker',name1]]
        if func2 == func1:
            ratedf2=find1[['ticker',name2]]

    if func1 == 'get_fin_abstract_ak':
        fabs1=get_fin_abstract_ak(ticker)
        ratedf1=fabs1[['ticker',name1]]
        if func2 == func1:
            ratedf2=fabs1[['ticker',name2]]

    if func1 == 'get_fin_performance_ak':
        fs_dates=cvt_fs_dates(start,end,period_type)
        #合成各个财报日期
        fpfm1=pd.DataFrame()
        for enddate in fs_dates:
            tmp=get_fin_performance_ak(ticker,enddate)
            fpfm1=fpfm1.append(tmp)
        ratedf1=fpfm1[['ticker',name1,'股票简称','所处行业','同行数量']]
        if func2 == func1:
            ratedf2=fpfm1[['ticker',name2,'股票简称','所处行业','同行数量']]
    
    #若ratedf2尚未定义
    if not ('ratedf2' in locals().keys()):
        if func2 == 'get_fin_indicator_ak':
            find2=get_fin_indicator_ak(ticker)
            ratedf2=find2[['ticker',name2]]
            
        if func2 == 'get_fin_abstract_ak':
            fabs2=get_fin_abstract_ak(ticker)
            ratedf2=fabs2[['ticker',name2]]

        if func2 == 'get_fin_performance_ak':
            fs_dates=cvt_fs_dates(start,end,period_type)
            #合成各个财报日期
            fpfm2=pd.DataFrame()
            for enddate in fs_dates:
                tmp=get_fin_performance_ak(ticker,enddate)
                fpfm2=fpfm2.append(tmp)
            ratedf2=fpfm2[['ticker',name2,'股票简称','所处行业','同行数量']]
            
    #过滤起始日期：
    ratedf1b=ratedf1[(ratedf1.index >= start1) & (ratedf1.index <= end1)]
    ratedf2b=ratedf2[(ratedf2.index >= start1) & (ratedf2.index <= end1)]

    #过滤年报类型
    ratedf1b['month']=ratedf1b.index.month
    if period_type == 'annual':
        ratedf1c=ratedf1b[ratedf1b['month'] == 12]
    elif period_type == 'semiannual':
        ratedf1c=ratedf1b[ratedf1b['month'].isin([6,12])]
    else:
        ratedf1c=ratedf1b
    del ratedf1c['month']
    
    ratedf2b['month']=ratedf2b.index.month
    if period_type == 'annual':
        ratedf2c=ratedf2b[ratedf2b['month'] == 12]
        
    elif period_type == 'semiannual':
        ratedf2c=ratedf2b[ratedf2b['month'].isin([6,12])]
    else:
        ratedf2c=ratedf2b
    del ratedf2c['month']

    print("  Retrieved",len(ratedf1c),rate1,"and",len(ratedf2c),rate2,"records for",ticker)

    return ratedf1c,ratedf2c

if __name__=='__main__':
    ticker='600519.SS'
    start='2021-5-1'
    end='2021-11-30'
    df1=prepare_fin_rate1t2r_china(ticker,'ROA','ROE',start,end,period_type='all')
    df2=prepare_fin_rate1t2r_china(ticker,'ROA','CFPS',start,end,period_type='all') 
    df3=prepare_fin_rate1t2r_china(ticker,'ROA','Oper Revenue Industry Share',start,end,period_type='all') 
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    start='2021-5-1'
    end='2021-11-30'
    period_type='all'

def prepare_fin_rate1tmr_china(ticker,rates,start,end,period_type='all'):
    """
    功能：准备财务准备，1个股票，多个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_fin_rate1tmr_china): invalid period",start,end)
        return None

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in STOCK_SUFFIX_CHINA):
        print("  #Warning(prepare_fin_rate1tmr_china): not a stock in China",ticker)
        return None       
    
    #检查是否多个指标
    if isinstance(rates,str):
        mrate_list=[rates]
    elif isinstance(rates,list):
        mrate_list=rates
    else:
        print("  #Warning(prepare_fin_rate1tmr_china): invalid financial rate/rate list",rates)
        return None       
    
    #检查指标是否支持
    sup_fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    sup_rate_list=list(sup_fin_rates['财务指标代码'])
    for r in mrate_list:
        if not (r.lower() in sup_rate_list):
            print("  #Warning(prepare_fin_rate1tmr_china): unsupported financial rate",r)
            return None
    #--------------------------------------------------------------------------
    #逐个检查财务指标，若不存在则抓取，若存在则直接利用，避免重复抓取
    rdf_list=[]
    for r in mrate_list:
        func,name=cvt_fin_rate(r)
        if func == 'get_fin_indicator_ak':
            if not ('find' in locals().keys()):
                find=get_fin_indicator_ak(ticker)
            rdf=find[['ticker',name]]
    
        if func == 'get_fin_abstract_ak':
            if not ('fabs' in locals().keys()):
                fabs=get_fin_abstract_ak(ticker)
            rdf=fabs[['ticker',name]]
    
        if func == 'get_fin_performance_ak':
            if not ('fpfm' in locals().keys()):
                fs_dates=cvt_fs_dates(start,end,period_type)
                #合成各个财报日期
                fpfm=pd.DataFrame()
                for enddate in fs_dates:
                    tmp=get_fin_performance_ak(ticker,enddate)
                    fpfm=fpfm.append(tmp)
            rdf=fpfm[['ticker',name,'股票简称','所处行业','同行数量']]
        
        rdf_list=rdf_list+[rdf]
            
    rdf_list1=[]
    for rdf in rdf_list:
        #过滤起始日期：
        rdf1=rdf[(rdf.index >= start1) & (rdf.index <= end1)]

        #过滤年报类型
        rdf1['month']=rdf1.index.month
        if period_type == 'annual':
            rdf1b=rdf1[rdf1['month'] == 12]
        elif period_type == 'semiannual':
            rdf1b=rdf1[rdf1['month'].isin([6,12])]
        else:
            rdf1b=rdf1
        del rdf1b['month']
        print("  Retrieved",len(rdf1b),"records for",ticker,list(rdf1b)[1])
        
        rdf_list1=rdf_list1+[rdf1b]

    return rdf_list1

if __name__=='__main__':
    ticker='600519.SS'
    start='2021-5-1'
    end='2021-11-30'
    rates=['oper profit share','Oper Revenue Industry Share','earnings industry share']
    df1=prepare_fin_rate1tmr_china(ticker,['ROA','ROE'],start,end,period_type='all')
    df2=prepare_fin_rate1tmr_china(ticker,['ROA','CFPS'],start,end,period_type='all') 
    df3=prepare_fin_rate1tmr_china(ticker,rates,start,end,period_type='all') 
#==============================================================================
if __name__=='__main__':
    tickers=['600519.SS','600606.SS']
    rate='oper revenue industry share'
    start='2021-5-1'
    end='2021-11-30'
    period_type='all'

def prepare_fin_ratemt1r_china(tickers,rate,start,end,period_type='all'):
    """
    功能：准备财务指标，多个股票，1个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_fin_ratemt1r_china): invalid period",start,end)
        return None
    
    #检查是否多个股票
    if isinstance(tickers,str):
        mticker_list=[tickers]
    elif isinstance(tickers,list):
        mticker_list=tickers
    else:
        print("  #Warning(prepare_fin_ratemt1r_china): invalid stock/stock list",tickers)
        return None       

    #是否中国股票
    prefix_list=[]
    for t in mticker_list:
        result,prefix,suffix=split_prefix_suffix(t)
        if not (suffix in STOCK_SUFFIX_CHINA):
            print("  #Warning(prepare_fin_ratemt1r_china): not a stock in China",ticker)
            return None  
        prefix_list=prefix_list+[prefix]
        
    #检查指标是否支持
    sup_fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    sup_rate_list=list(sup_fin_rates['财务指标代码'])
    if not (rate.lower() in sup_rate_list):
        print("  #Warning(prepare_fin_ratemt1r_china): unsupported financial rate",rate)
        print("  Check supported financial rates? use command rates=cvt_fin_rate('?')")
        return None
    #--------------------------------------------------------------------------
    #逐个检查股票指标，若不存在则抓取，若存在则直接利用，避免重复抓取
    func,name=cvt_fin_rate(rate)
    rdf_list=[]
    if func in ['get_fin_indicator_ak','get_fin_abstract_ak']:
        for t in mticker_list:
            if func == 'get_fin_indicator_ak':
                find=get_fin_indicator_ak(t)
                rdf=find[['ticker',name]]
        
            if func == 'get_fin_abstract_ak':
                fabs=get_fin_abstract_ak(t)
                rdf=fabs[['ticker',name]]
            
            rdf_list=rdf_list+[rdf]

    #为了避免重复抓取，将此段独立出来
    if func == 'get_fin_performance_ak':
        fs_dates=cvt_fs_dates(start,end,period_type)
        #合成各个财报日期
        fpfm=pd.DataFrame()
        for enddate in fs_dates:
            tmp=get_fin_performance_akm(mticker_list,enddate)
            fpfm=fpfm.append(tmp)
        
        #处理各个rdf进入列表
        for prefix in prefix_list:
            rdf=fpfm[fpfm['ticker'] == prefix]
            rdf2=rdf[['ticker',name,'股票简称','所处行业','同行数量']]
            rdf_list=rdf_list+[rdf2]
            
    rdf_list1=[]
    for rdf in rdf_list:
        #过滤起始日期：
        rdf1=rdf[(rdf.index >= start1) & (rdf.index <= end1)]

        #过滤年报类型
        rdf1['month']=rdf1.index.month
        if period_type == 'annual':
            rdf1b=rdf1[rdf1['month'] == 12]
        elif period_type == 'semiannual':
            rdf1b=rdf1[rdf1['month'].isin([6,12])]
        else:
            rdf1b=rdf1
        del rdf1b['month']
        
        rdf_list1=rdf_list1+[rdf1b]

    return rdf_list1

if __name__=='__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    start='2020-5-1'
    end='2021-11-30'
    df1=prepare_fin_ratemt1r_china(tickers,'ROA',start,end,period_type='all')
    df2=prepare_fin_ratemt1r_china(tickers,'Profit Margin Growth',start,end,period_type='all') 
    df3=prepare_fin_ratemt1r_china(tickers,'oper revenue industry share',start,end,period_type='annual') 

#==============================================================================
def cn_codetranslate(ticker):
    """
    功能：将中国股票代码转换为股票简称
    注意：既能转换带后缀的股票代码，也能转换不带后缀的股票代码
    """
    result,prefix,suffix=split_prefix_suffix(ticker)
    if suffix in STOCK_SUFFIX_CHINA:
        name=codetranslate(ticker)

    if suffix =='':
        for s in STOCK_SUFFIX_CHINA:
            ticker_try=ticker+'.'+s
            name=codetranslate(ticker_try)
            print('\b'*99," Looking for the short name of stock",ticker)
            if not (name == ticker_try): break
        
    return name

if __name__=='__main__':
    cn_codetranslate('600519.SS')
    cn_codetranslate('600519')
        
#==============================================================================

if __name__=='__main__':
    tickers=['600519.SS','000858.SZ','600779.SS',]
    rate='oper revenue industry share'
    start='2021-5-1'
    end='2021-11-30'
    period_type='all'

def print_fin_ratemt1r_china(tickers,rate,start,end,period_type='all'):
    """
    功能：打印财务指标，多个股票，1个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    """
    rdf_list=prepare_fin_ratemt1r_china(tickers,rate,start,end,period_type)
    
    _,rate_name=cvt_fin_rate(rate)
    rdf_all=pd.DataFrame()
    #rdf=rdf_list[0]
    for rdf in rdf_list:
        t=rdf['ticker'].values[0]
        df_tmp=rdf[[rate_name]]
        df_tmp.rename(columns={rate_name:t},inplace=True)
        df_tmpt=df_tmp.T
        
        rdf_all=rdf_all.append(df_tmpt)
    
    rdf_all['股票代码']=rdf_all.index
    rdf_all['股票简称']=rdf_all['股票代码'].apply(lambda x: cn_codetranslate(x))
    
    cols=list(rdf_all)
    for c in cols:
        try:
            cs=c.strftime("%Y-%m-%d")
            rdf_all[cs]=round(rdf_all[c],2)
            del rdf_all[c]
        except:
            continue
    
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)    
    
    print("\n===== 财务指标对比："+rate_name+" =====")
    print(rdf_all.to_string(index=False))
    
    import datetime; today=datetime.date.today()
    print("\n*** 数据来源：sina/EM，"+str(today))
    
    return rdf_all
    
if __name__=='__main__':
    tickers=['600519.SS','000858.SZ','600779.SS',]
    rate='oper revenue industry share'
    start='2021-5-1'
    end='2021-11-30'
    
    df=print_fin_ratemt1r_china(tickers,rate,start,end,period_type='all')        
#==============================================================================
#==============================================================================
#==============================================================================
if __name__ == '__main__':
    tickers=['600606.SS','600519.SS']
    items='Current Ratio'
    start='2020-1-1'
    end='2021-11-30'
    period_type='annual'

    datatag=False
    power=0
    zeroline=False
    twinx=False

def compare_history_china(tickers,items,start,end,period_type='annual', \
                    datatag=False,power=0,zeroline=False,twinx=False):
    """
    功能：比较一只股票两个指标或两只股票一个指标的时序数据，绘制折线图
    datatag=False: 不将数值标记在图形旁
    zeroline=False：不绘制水平零线
    twinx=False：单纵轴
    """
    error_flag=False
    
    #检查股票个数
    if isinstance(tickers,str): 
        ticker_num=1; ticker1=tickers
    elif isinstance(tickers,list):
        ticker_num=len(tickers)
        if ticker_num >= 1:
            ticker1=tickers[0]
        if ticker_num >= 2:
            ticker2=tickers[1]
        if ticker_num == 0:
            print("  #Error(compare_history_china): no stock code found",tickers)
            error_flag=True

    #检查指标个数
    item_num=1
    if isinstance(items,list): 
        if len(items) >= 1: 
            item1=items[0]
        if len(items) >= 2: 
            item2=items[1]
            item_num=2
        if len(items) == 0: 
            print("  #Error(compare_history_china): no analytical item found",items)
            error_flag=True
    else:
        item1=items
        
    if error_flag: return None,None        
    
    #判断比较模式
    if (ticker_num == 1) and (item_num == 1): mode='T1I1'
    if (ticker_num == 1) and (item_num == 2): mode='T1I2'
    if (ticker_num == 2): mode='T2I1'
    
    #抓取数据
    if mode in ['T1I1','T1I2']:
        rdf_list1=prepare_fin_rate1tmr_china(ticker1,items,start,end,period_type)
        if rdf_list1 is None: error_flag=True
        else:
            for rdf in rdf_list1:
                if rdf is None: error_flg=True
                if len(rdf) == 0: error_flag=True
            if not error_flag:
                df1=rdf_list1[0]
                try: df2=rdf_list1[1]
                except: pass
    if mode in ['T2I1']:
        rdf_list2=prepare_fin_ratemt1r_china(tickers,item1,start,end,period_type)
        if rdf_list2 is None: error_flag=True
        else:
            for rdf in rdf_list2:
                if rdf is None: error_flag=True
                if len(rdf) == 0: error_flag=True
            if not error_flag:
                df1=rdf_list2[0]
                df2=rdf_list2[1]

    if error_flag: 
        print("  #Error(compare_history_china): info not found for",tickers,"on",items)
        return None,None        

    #绘图：T1I1，单折线
    import datetime; today=datetime.date.today()
    footnote9="数据来源: sina/EM, "+str(today)
    if mode == 'T1I1':
        _,colname=cvt_fin_rate(item1)
        #collabel=ectranslate(item1)
        collabel=colname
        ylabeltxt=''
        titletxt=codetranslate(ticker1)+": 财务指标历史"
        
        colmin=round(df1[colname].min(),2)
        colmax=round(df1[colname].max(),2)
        colmean=round(df1[colname].mean(),2)
        footnote=collabel+"："+ \
            str(colmin)+" - "+str(colmax)+ \
            "，均值"+str(colmean)+'\n'+footnote9
        plot_line(df1,colname,collabel,ylabeltxt,titletxt,footnote, \
                  datatag=datatag,power=power,zeroline=zeroline,resample_freq='1M')
        return df1,None

    #绘图：T1I2，单股票双折线
    if mode == 'T1I2':
        _,colname1=cvt_fin_rate(item1)
        label1=colname1
        _,colname2=cvt_fin_rate(item2)
        label2=colname2
        ylabeltxt=''
        titletxt="财务指标历史"

        colmin1=round(df1[colname1].min(),2)
        colmax1=round(df1[colname1].max(),2)
        colmean1=round(df1[colname1].mean(),2)
        colmin2=round(df2[colname2].min(),2)
        colmax2=round(df2[colname2].max(),2)
        colmean2=round(df2[colname2].mean(),2)
        footnote1=label1+"："+ \
            str(colmin1)+" - "+str(colmax1)+"，均值"+str(colmean1)
        footnote2=label2+"："+ \
            str(colmin2)+" - "+str(colmax2)+"，均值"+str(colmean2)
        footnote=footnote1+'\n'+footnote2+'\n'+footnote9
        
        plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker1,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline,twinx=twinx,resample_freq='1M')
        return df1,df2

    #绘图：T2I1，双股票双折线，单指标
    if mode == 'T2I1':
        _,colname1=cvt_fin_rate(item1)
        label1=colname1
        colname2=colname1
        label2=label1
        ylabeltxt=''
        titletxt="财务指标历史"

        colmin1=round(df1[colname1].min(),2)
        colmax1=round(df1[colname1].max(),2)
        colmean1=round(df1[colname1].mean(),2)
        colmin2=round(df2[colname2].min(),2)
        colmax2=round(df2[colname2].max(),2)
        colmean2=round(df2[colname2].mean(),2)
        footnote1=codetranslate(ticker1)+"："+ \
            str(colmin1)+" - "+str(colmax1)+"，均值"+str(colmean1)
        footnote2=codetranslate(ticker2)+"："+ \
            str(colmin2)+" - "+str(colmax2)+"，均值"+str(colmean2)
        footnote=footnote1+'\n'+footnote2+'\n'+footnote9
        
        plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline,twinx=twinx,resample_freq='1M')    
    
        return df1,df2    
    
if __name__ == '__main__':
    tickers=['600606.SS','000002.SZ']
    items=['Current Ratio','Quick Ratio']
    df1,df2=compare_history_china('600606.SS','Current Ratio','2020-1-1','2021-12-13',period_type='all')
    df1,df2=compare_history_china('600606.SS',items,'2020-1-1','2021-12-13',period_type='all')
    df1,df2=compare_history_china(tickers,'Current Ratio','2020-1-1','2021-12-13',period_type='all')
    
    df1,df2=compare_history_china(tickers,'?','2020-1-1','2021-12-13')
    
    rates=['Earnings Industry Share','Oper Revenue Industry Share']
    df1,df2=compare_history_china('600519.SS',rates,'2015-1-1','2021-12-13',period_type='annual')
    df1,df2=compare_history_china('600519.SS',rates,'2015-1-1','2021-12-13',period_type='semiannual')
    
    df1,df2=compare_history_china(['600519.SS','000858.SZ'],'Earnings Industry Share','2015-1-1','2021-12-13',period_type='annual')
    df1,df2=compare_history_china(['600519.SS','000858.SZ'],'Oper Revenue Industry Share','2015-1-1','2021-12-13',period_type='annual')

#==============================================================================
if __name__ == '__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    itemk='ROE'
    endDate='latest'
    datatag=True
    tag_offset=0.01
    graph=True
    axisamp=1.3

def compare_snapshot_china(tickers,itemk,endDate='latest',datatag=True,tag_offset=0.01,graph=True,axisamp=1.3):
    """
    功能：比较多个股票的快照数据，绘制水平柱状图，仅限中国A股
    itemk需要通过对照表转换为内部的item
    datatag=True: 将数值标记在图形旁
    tag_offset=0.01：标记的数值距离图形的距离，若不理想可以手动调节，可为最大值1%-5%
    """
    error_flag=False
    
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Warning(compare_snapshot_china): need more stock codes in",tickers)
        error_flag=True
    if len(tickers) < 2:
        print("  #Warning(compare_snapshot_china): need more stock codes in",tickers)
        error_flag=True
    if error_flag: return None
    
    #检查指标是否支持
    fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    rate_list=list(fin_rates['财务指标代码'])
    if not (itemk.lower() in rate_list):
        print("  #Warning(compare_snapshot_china): unsupported financial rate",itemk)
        error_flag=True
    if error_flag: return None

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Warning(compare_snapshot_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #依次获得各个股票的指标  
    rdf_list=prepare_fin_ratemt1r_china(tickers,itemk,endDate,endDate,period_type='all')
    #合成
    df=pd.DataFrame(columns=('ticker','item','value','name'))
    for rdf in rdf_list:
        cols=list(rdf)
        t=rdf['ticker'].values[0]
        item=cols[1]
        value=rdf[item].values[0]
        name=codetranslate(t)
        if name == t:
            name=rdf[cols[2]].values[0]
        row=pd.Series({'ticker':t,'item':item,'value':value,'name':name})
        df=df.append(row,ignore_index=True)         
    
    if len(df) == 0:
        print("  #Error(compare_snapshot_china): stock info not found in",tickers)
        error_flag=True
    if error_flag: return None
    
    #处理小数点
    try:
        df['value']=round(df['value'],3)    
    except:
        pass
    df.sort_values(by='value',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)    
    
    #绘图
    if graph:
        print("...Calculating and drawing graph, please wait ...")
        colname='value'
        titletxt="企业横向对比: 业绩指标快照"
        import datetime; today=datetime.date.today()
        footnote=item+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,datatag=datatag,tag_offset=tag_offset,axisamp=axisamp)
    
    return df

if __name__ == '__main__':
    df=compare_snapshot(tickers,itemk)

#==============================================================================
if __name__ == '__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    endDate='latest'
    graph=True
    axisamp=7
    
def compare_tax_china(tickers,endDate='latest',datatag=True,tag_offset=0.01,graph=True,axisamp=1.3):
    """
    功能：比较公司最新的实际所得税率
    """
    error_flag=False
    
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Warning(compare_tax_china): need more stock codes in",tickers)
        error_flag=True
    if len(tickers) < 2:
        print("  #Warning(compare_tax_china): need more stock codes in",tickers)
        error_flag=True
    if error_flag: return None

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Warning(compare_tax_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #获取实际所得税率
    df=pd.DataFrame(columns=('ticker','name','date','tax rate%'))
    for t in tickers:
        try:
            df0=prepare_hamada_ak(t,endDate,endDate,period_type='all')
        except:
            print("  #Error(compare_tax_china): failed to get financial info for",t)
            continue
        df1=df0.tail(1)
        name=codetranslate(t)
        reportdate=df1.index[0]
        taxrate=df1['tax rate'][0]
        row=pd.Series({'ticker':t,'name':name,'date':reportdate,'tax rate%':round(taxrate*100,2)})
        df=df.append(row,ignore_index=True)        
    
    df.sort_values(by='tax rate%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        print("  Calculating and drawing graph, please wait ...")
        colname='tax rate%'
        titletxt="企业横向对比: 实际所得税率"
        import datetime; today=datetime.date.today()
        itemk="实际所得税率%"
        footnote=ectranslate(itemk)+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,datatag=datatag,tag_offset=tag_offset,axisamp=axisamp)
    return df


#==============================================================================
if __name__ == '__main__':
    ticker='600519.SS'
    endDate='2021-09-30'

def calc_igr_sgr_china(ticker,endDate):

    rates=['ROE','ROA','Payout Ratio']
    rdf_list=prepare_fin_rate1tmr_china(ticker,rates,endDate,endDate,period_type='all')
    if rdf_list is None: return None,None
    
    roe=rdf_list[0]['净资产收益率'].values[0]/100
    roa=rdf_list[1]['资产报酬率(%)'].values[0]/100
    try:
        b=1-rdf_list[2]['股息发放率(%)'].values[0]/100
    except:
        b=1-0

    igr=round(roa*b/(1-roa*b),4)
    sgr=round(roe*b/(1-roe*b),4)
    
    return igr,sgr


#==============================================================================
if __name__ == '__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    endDate='latest'
    graph=True
    axisamp1=1.3
    axisamp2=1.6

def compare_igr_sgr_china(tickers,endDate='latest',graph=True,axisamp1=1.3,axisamp2=1.6):
    """
    功能：比较公司的IGR和SGR
    """
    error_flag=False
    
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Warning(compare_igr_sgr_china): need more stock codes in",tickers)
        error_flag=True
    if len(tickers) < 2:
        print("  #Warning(compare_igr_sgr_china): need more stock codes in",tickers)
        error_flag=True
    if error_flag: return None

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Warning(compare_igr_sgr_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #逐个获取公司信息
    df=pd.DataFrame(columns=('ticker','name','date','IGR%','SGR%'))
    for t in tickers:
        try:
            igr,sgr=calc_igr_sgr_china(t,endDate)
        except:
            print("  #Warning(compare_igr_sgr_china): stock info not available for",t)
            continue
        if igr is None or sgr is None: 
            print("  #Warning(compare_igr_sgr_china): no stock info found for",t)
            continue
        name=codetranslate(t)
        row=pd.Series({'ticker':t,'name':name,'IGR%':round(igr*100,2),'SGR%':round(sgr*100,2)})
        df=df.append(row,ignore_index=True)        
    
    #绘制IGR
    df.sort_values(by='IGR%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        colname='IGR%'
        titletxt="企业横向对比: 内部增长潜力"
        import datetime; today=datetime.date.today()
        itemk="(不依赖外部融资的)内部增长率(IGR)%"
        footnote=ectranslate(itemk)+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,axisamp=axisamp1)   
    
    #绘制SGR
    df.sort_values(by='SGR%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        print("...Calculating and drawing graph, please wait ...")
        colname='SGR%'
        titletxt="企业横向对比: 可持续增长潜力"
        import datetime; today=datetime.date.today()
        itemk="(不增加财务杠杆的)可持续增长率(SGR)%"
        footnote=ectranslate(itemk)+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,axisamp=axisamp2)         
    return df
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
