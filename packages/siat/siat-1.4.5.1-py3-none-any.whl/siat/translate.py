# -*- coding: utf-8 -*-
"""
本模块功能：SIAT公共转换函数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2021年5月16日
最新修订日期：
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
from siat.common import *
#==============================================================================
def ectranslate(eword):
    """
    翻译证券词汇为证券名称，基于语言环境决定中英文。
    输入：证券词汇英文
    """
    
    lang=check_language()
    if lang == 'English':
        return ectranslate_e(eword)
    else:
        return ectranslate_c(eword)

#==============================================================================
def ectranslate_c(eword):
    """
    翻译英文专业词汇至中文，便于显示或绘图时输出中文而不是英文。
    输入：英文专业词汇。输出：中文专业词汇
    """
    import pandas as pd
    ecdict=pd.DataFrame([
        ['High','最高价'],['Low','最低价'],['Open','开盘价'],['Close','收盘价'],
        ['Current Price','现时股价'],
        ['Volume','成交量'],['Adj Close','调整收盘价'],['Daily Ret','日收益率'],
        ['Daily Ret%','日收益率%'],['Daily Adj Ret','调整日收益率'],
        ['Daily Adj Ret%','调整日收益率%'],['log(Daily Ret)','对数日收益率'],
        ['log(Daily Adj Ret)','对数调整日收益率'],['Weekly Ret','周收益率'],
        ['Weekly Ret%','周收益率%'],['Weekly Adj Ret','周调整收益率'],
        ['Weekly Adj Ret%','周调整收益率%'],['Monthly Ret','月收益率'],
        ['Monthly Ret%','月收益率%'],['Monthly Adj Ret','月调整收益率'],
        ['Monthly Adj Ret%','月调整收益率%'],['Quarterly Ret','季度收益率'],
        ['Quarterly Ret%','季度收益率%'],['Quarterly Adj Ret','季度调整收益率'],
        ['Quarterly Adj Ret%','季度调整收益率%'],['Annual Ret','年收益率'],
        ['Annual Ret%','年收益率%'],['Annual Adj Ret','年调整收益率'],
        ['Annual Adj Ret%','年调整收益率%'],['Exp Ret','持有收益率'],
        ['Exp Ret%','持有收益率%'],['Exp Adj Ret','持有调整收益率'],
        ['Exp Adj Ret%','持有调整收益率%'],
        
        ['Weekly Price Volatility','周股价波动风险'],
        ['Weekly Adj Price Volatility','周调整股价波动风险'],
        ['Monthly Price Volatility','月股价波动风险'],
        ['Monthly Adj Price Volatility','月调整股价波动风险'],
        ['Quarterly Price Volatility','季股价波动风险'],
        ['Quarterly Adj Price Volatility','季调整股价波动风险'],
        ['Annual Price Volatility','年股价波动风险'],
        ['Annual Adj Price Volatility','年调整股价波动风险'],  
        ['Exp Price Volatility','持有股价波动风险'], 
        ['Exp Adj Price Volatility','持有调整股价波动风险'],
        
        ['Weekly Ret Volatility','周收益率波动风险'],
        ['Weekly Ret Volatility%','周收益率波动风险%'],
        ['Weekly Adj Ret Volatility','周调整收益率波动风险'],
        ['Weekly Adj Ret Volatility%','周调整收益率波动风险%'],
        ['Monthly Ret Volatility','月收益率波动风险'],
        ['Monthly Ret Volatility%','月收益率波动风险%'],
        ['Monthly Adj Ret Volatility','月调整收益波动风险'],
        ['Monthly Adj Ret Volatility%','月调整收益波动风险%'],
        ['Quarterly Ret Volatility','季收益率波动风险'],
        ['Quarterly Ret Volatility%','季收益率波动风险%'],
        ['Quarterly Adj Ret Volatility','季调整收益率波动风险'],
        ['Quarterly Adj Ret Volatility%','季调整收益率波动风险%'],
        ['Annual Ret Volatility','年收益率波动风险'],
        ['Annual Ret Volatility%','年收益率波动风险%'],
        ['Annual Adj Ret Volatility','年调整收益率波动风险'], 
        ['Annual Adj Ret Volatility%','年调整收益率波动风险%'], 
        ['Exp Ret Volatility','持有收益率波动风险'], 
        ['Exp Ret Volatility%','持有收益率波动风险%'],
        ['Exp Adj Ret Volatility','持有调整收益率波动风险'],        
        ['Exp Adj Ret Volatility%','持有调整收益率波动风险%'],
        
        ['Weekly Ret LPSD','周收益率波动损失风险'],
        ['Weekly Ret LPSD%','周收益率波动损失风险%'],
        ['Weekly Adj Ret LPSD','周调整收益率波动损失风险'],
        ['Weekly Adj Ret LPSD%','周调整收益率波动损失风险%'],
        ['Monthly Ret LPSD','月收益率波动损失风险'],
        ['Monthly Ret LPSD%','月收益率波动损失风险%'],
        ['Monthly Adj Ret LPSD','月调整收益波动损失风险'],
        ['Monthly Adj Ret LPSD%','月调整收益波动损失风险%'],
        ['Quarterly Ret LPSD','季收益率波动损失风险'],
        ['Quarterly Ret LPSD%','季收益率波动损失风险%'],
        ['Quarterly Adj Ret LPSD','季调整收益率波动损失风险'],
        ['Quarterly Adj Ret LPSD%','季调整收益率波动损失风险%'],
        ['Annual Ret LPSD','年收益率波动损失风险'],
        ['Annual Ret LPSD%','年收益率波动损失风险%'],
        ['Annual Adj Ret LPSD','年调整收益率波动损失风险'], 
        ['Annual Adj Ret LPSD%','年调整收益率波动损失风险%'], 
        ['Exp Ret LPSD','持有收益率波动损失风险'], 
        ['Exp Ret LPSD%','持有收益率波动损失风险%'],
        ['Exp Adj Ret LPSD','持有调整收益率波动损失风险'],        
        ['Exp Adj Ret LPSD%','持有调整收益率波动损失风险%'],
        
        ['roll_spread','罗尔价差比率'],['amihud_illiquidity','阿米胡德非流动性'],
        ['ps_liquidity','P-S流动性'],    
        
        ['Gross Domestic Product','国内生产总值'],['GNI','国民总收入'],    
        
        ['zip','邮编'],['sector','领域'],
        ['fullTimeEmployees','全职员工数'],['Employees','全职员工数'],
        ['longBusinessSummary','业务介绍'],['city','城市'],['phone','电话'],
        ['state','州/省'],['country','国家/地区'],['companyOfficers','高管'],
        ['website','官网'],['address1','地址1'],['industry','行业'],
        ['previousClose','上个收盘价'],['regularMarketOpen','正常市场开盘价'],
        ['twoHundredDayAverage','200天均价'],['fax','传真'], 
        ['trailingAnnualDividendYield','年化股利率TTM'],
        ['payoutRatio','股息支付率'],['volume24Hr','24小时交易量'],
        ['regularMarketDayHigh','正常市场日最高价'],
        ['averageDailyVolume10Day','10天平均日交易量'],['totalAssets','总资产'],
        ['regularMarketPreviousClose','正常市场上个收盘价'],
        ['fiftyDayAverage','50天平均股价'],
        ['trailingAnnualDividendRate','年化每股股利金额TTM'],['open','当日开盘价'],
        ['averageVolume10days','10日平均交易量'],['expireDate','失效日'],
        ['yield','收益率'],['dividendRate','每股股利金额'],
        ['exDividendDate','股利除息日'],['beta','贝塔系数'],
        ['startDate','开始日期'],['regularMarketDayLow','正常市场日最低价'],
        ['priceHint','价格提示'],['currency','交易币种'],
        ['trailingPE','市盈率TTM'],['regularMarketVolume','正常市场交易量'],
        ['marketCap','市值'],['averageVolume','平均交易量'],
        ['priceToSalesTrailing12Months','市销率TTM'],
        ['TTM Price to Sales','市销率TTM'],
        ['dayLow','当日最低价'],
        ['ask','卖出价'],['askSize','卖出价股数'],['volume','当日交易量'],
        ['fiftyTwoWeekHigh','52周最高价'],['forwardPE','预期市盈率'],
        ['fiveYearAvgDividendYield','5年平均股利率'],
        ['fiftyTwoWeekLow','52周最低价'],['bid','买入价'],
        ['tradeable','今日是否可交易'],['dividendYield','股利率'],
        ['bidSize','买入价股数'],['dayHigh','当日最高价'],
        ['exchange','交易所'],['shortName','简称'],['longName','全称'],
        ['exchangeTimezoneName','交易所时区'],
        ['exchangeTimezoneShortName','交易所时区简称'],['quoteType','证券类别'],
        ['symbol','证券代码'],['messageBoardId','证券留言板编号'],
        ['market','证券市场'],['annualHoldingsTurnover','一年內转手率'],
        ['enterpriseToRevenue','市售率(EV/Revenue)'],['EV to Revenue','市售率(EV/Revenue)'],        
        ['Price to Book','市净率'],['beta3Year','3年贝塔系数'],
        ['profitMargins','净利润率'],['enterpriseToEbitda','企业价值/EBITDA'],
        ['EV to EBITDA','企业价值倍数（EV/EBITDA)'],
        ['52WeekChange','52周股价变化率'],['morningStarRiskRating','晨星风险评级'],
        ['forwardEps','预期每股收益'],['revenueQuarterlyGrowth','季营收增长率'],
        ['sharesOutstanding','流通在外股数'],['fundInceptionDate','基金成立日'],
        ['annualReportExpenseRatio','年报费用比率'],['bookValue','每股净资产'],
        ['sharesShort','卖空股数'],['sharesPercentSharesOut','卖空股数/流通股数'],
        ['lastFiscalYearEnd','上个财年截止日期'],
        ['heldPercentInstitutions','机构持股比例'],
        ['netIncomeToCommon','归属普通股股东净利润'],['trailingEps','每股收益'],
        ['lastDividendValue','上次股利价值'],
        ['SandP52WeekChange','标普指数52周变化率'],['priceToBook','市净率'],
        ['heldPercentInsiders','内部人持股比例'],['priceToBook','市净率'],
        ['nextFiscalYearEnd','下个财年截止日期'],
        ['mostRecentQuarter','上个财季截止日期'],['shortRatio','空头净额比率'],
        ['sharesShortPreviousMonthDate','上月做空日期'],
        ['floatShares','可交易股数'],['enterpriseValue','企业价值'],
        ['threeYearAverageReturn','3年平均回报率'],['lastSplitDate','上个拆分日期'],
        ['lastSplitFactor','上次拆分比例'],
        ['earningsQuarterlyGrowth','季盈余增长率'],['dateShortInterest','做空日期'],
        ['pegRatio','市盈率与增长比率'],['shortPercentOfFloat','空头占可交易股票比例'],
        ['sharesShortPriorMonth','上月做空股数'],
        ['fiveYearAverageReturn','5年平均回报率'],['regularMarketPrice','正常市场价'],
        ['logo_url','商标图标网址'],     ['underlyingSymbol','曾用代码'],     
        ['timeZoneShortName','时区简称'],['timeZoneFullName','时区全称'],
        ['exchangeName','交易所名称'],['currentPrice','当前价格'],
        ['ratingYear','评估年度'],['ratingMonth','评估月份'],
        ['currencySymbol','币种符号'],['recommendationKey','投资建议'],
        ['totalInsiderShares','内部人持股数'],['financialCurrency','财报币种'],
        ['currentRatio','流动比率'],['quickRatio','速动比率'],
        ['debtToEquity','负债-权益比%'],['ebitdaMargins','EBITDA利润率'],
        ['operatingMargins','经营利润率'],['grossMargins','毛利润率'],
        ['returnOnAssets','资产回报率'],['returnOnEquity','净资产回报率'],
        ['ROA','资产回报率'],['ROE','净资产回报率'],
        ['revenuePerShare','每股销售收入'],['totalCashPerShare','每股总现金'],
        ['revenueGrowth','销售收入增长率'],['earningsGrowth','盈余增长率'],
        ['totalDebt','总负债'],['totalRevenue','总销售收入'],
        ['grossProfits','毛利润'],['ebitda','EBITDA'],
        ['operatingCashflow','经营现金流'],['freeCashflow','自由现金流'],
        ['totalCash','总现金流'],
        ['Total Asset Turnover','总资产周转率'],['Fixed Asset Turnover','固定资产周转率'],
        ['PPE Residual','固定资产成新率'],
        ['Current Ratio','流动比'],['Quick Ratio','速动比'],['Debt to Equity','负债-权益比%'],
        ['Debt to Asset','资产负债比'],['Times Interest Earned','利息保障倍数'],
        ['Inventory Turnover','存货周转率'],['Receivable Turnover','应收帐款周转率'],
        ['BasicEPS','基本每股收益'],['Cashflow per Share','每股现金流量'],
        ['Profit Margin','净利润率'],['Gross Margin','毛利润率'],
        ['EBITDA Margin','EBITDA利润率'],['Operating Margin','营业利润率'],
        ['Trailing EPS','每股收益TTM'],['Trailing PE','市盈率TTM'],['Forward PE','预期市盈率'],
        ['Revenue Growth','销售收入增长率'],['Earnings Growth','年度盈余增长率'],
        ['Earnings Quarterly Growth','季度盈余增长率'],
        ['IGR','内部增长率(IGR)'],['SGR','可持续增长率(SGR)'],
        
        ['overallRisk','总风险指数'],
        ['boardRisk','董事会风险指数'],['compensationRisk','薪酬风险指数'],
        ['shareHolderRightsRisk','股东风险指数'],['auditRisk','审计风险指数'],
        
        ['totalEsg','ESG总分数'],['Total ESG','ESG总分数'],
        ['esgPerformance','ESG业绩评价'],
        ['peerEsgScorePerformance','ESG同业分数'],
        ['environmentScore','环保分数'],['Environment Score','环保分数'],
        ['peerEnvironmentPerformance','环保同业分数'],
        ['socialScore','社会责任分数'],['Social Score','社会责任分数'],
        ['peerSocialPerformance','社会责任同业分数'],
        ['governanceScore','公司治理分数'],['Governance Score','公司治理分数'],
        ['peerGovernancePerformance','公司治理同业分数'],['peerGroup','同业分组'],
        ['relatedControversy','相关焦点'],['Social Supply Chain Incidents','供应链事件'],
        ['Customer Incidents','客户相关事件'],['Business Ethics Incidents','商业道德事件'],
        ['Product & Service Incidents','产品与服务相关事件'],
        ['Society & Community Incidents','社会与社区相关事件'],
        ['Employee Incidents','雇员相关事件'],['Operations Incidents','运营相关事件'],
        ['peerCount','同业个数'],['percentile','同业所处分位数'],  
        
        ['ESGscore','ESG风险'],['ESGpercentile','ESG风险行业分位数%'],
        ['ESGperformance','ESG风险评价'],['EPscore','环保风险'],
        ['EPpercentile','环保风险分位数%'],['CSRscore','社会责任风险'],
        ['CSRpercentile','社会责任风险分位数%'],['CGscore','公司治理风险'],
        ['CGpercentile','公司治理风险分位数%'],
        ['Peer Group','业务分类'],['Count','数目'],     
        
        ['China','中国'],['Japan','日本'],['USA','美国'],['India','印度'],
        ['Russia','俄罗斯'],['Korea','韩国'],
        
        ['Gross Domestic Product','国内生产总值'],['GDP','国内生产总值'],  
        ['CNP GDP','GDP（美元不变价格）'],['Constant GDP','GDP（本币不变价格）'],
        ['Current Price Gross Domestic Product','国内生产总值'],
        ['Constant GDP Per Capita','人均GDP（本币不变价格）'],
        ['CNP GDP Per Capita','人均GDP（美元不变价格）'],
        ['Constant Price GDP Per Capita','人均GDP'],
        ['GNP','国民生产总值'],['GNP Ratio','GNP(GNI)与GDP的比例'],
        ['GNI/GDP Ratio','GNP(GNI)与GDP的比例'],
        ['Ratio of GNP to GDP','GNP(GNI)与GDP之间的比例关系'],
        
        ['CPI','消费者价格指数'],['YoY CPI','CPI%（同比）'],
        ['MoM CPI','CPI%（环比）'],['Constant CPI','CPI%（本币不变价格）'],
        ['Consumer Price Index','消费者价格指数'],
        ['Consumer Price Index: All Items','消费者价格指数'],
        ['Consumer Price Index: All Items Growth Rate','消费者价格指数增速'],
        ['PPI','生产者价格指数'],['YoY PPI','PPI%（同比）'],
        ['MoM PPI','PPI%（环比）'],['Constant PPI','PPI%（本币不变价格）'],
        ['Producer Prices Index: Industrial Activities','工业活动PPI'],
        ['Producer Prices Index: Total Industrial Activities','全部工业活动PPI'],
        
        ['Exchange Rate','汇率'],
        ['M0','流通中现金M0供应量'],['M1','狭义货币M1供应量'],['M2','广义货币M2供应量'],
        ['M3','金融货币M3供应量'],
        ['Constant M0','流通中现金M0相对数'],['Constant M1','狭义货币M1相对数'],
        ['Constant M2','广义货币M2相对数'],['Constant M3','金融货币M3相对数'],
        
        ['National Monetary Supply M0','流通中现金M0供应量'],
        ['National Monetary Supply M1','狭义货币M1供应量'],
        ['National Monetary Supply M2','广义货币M2供应量'],
        ['National Monetary Supply M3','金融货币M3供应量'],
        
        ['Discount Rate','贴现率%'],
        ['Central Bank Discount Rate','中央银行贴现率'],
        
        ['Immediate Rate','即期利率%'],
        ['Immediate Rates: Less than 24 Hours: Interbank Rate','银行间即期利率（24小时内）'],  
        
        ['Local Currency/USD Foreign Exchange Rate','本币/美元汇率'],  
        ['USD/Local Currency Foreign Exchange Rate','美元/本币汇率'],['Euro','欧元'],
        
        ['Daily','日'],['Monthly','月'],['Quarterly','季'],['Annual','年'],
        
        ['Stock Market Capitalization to GDP','基于股市总市值的经济金融深度'],
        ['SMC to GDP','股市总市值/GDP'],
        
        ['Currency Value','货币价值'],['Currency Purchasing Power Based on CPI','基于CPI的货币购买力'],
        
        ['Portfolio','投资组合'],['Portfolio_EW','等权重组合'],['Portfolio_OMCap','流通市值权重组合'],
        ['Portfolio_MSR','MSR组合'],['Portfolio_GMV','GMV组合'],
        
        ], columns=['eword','cword'])

    try:
        cword=ecdict[ecdict['eword']==eword]['cword'].values[0]
    except:
        #未查到翻译词汇，返回原词
        cword=eword
   
    return cword

if __name__=='__main__':
    eword='Exp Adj Ret'
    print(ectranslate('Annual Adj Ret%'))
    print(ectranslate('Annual*Adj Ret%'))

    eword='Constant M1'
    print(ectranslate(eword))
    print(ectranslate('Annual*Adj Ret%'))

#==============================================================================
def ectranslate_e(eword):
    """
    翻译英文专业词汇至英文，便于显示或绘图时输出英文。绝大多数英文专业词汇无需翻译
    输入：英文专业词汇
    """
    import pandas as pd
    ecdict=pd.DataFrame([
        
        ['roll_spread','Roll Spread'],['amihud_illiquidity','Amihud Illiquidity'],
        ['ps_liquidity','P-S Liquidity'],    
        
        ['Gross Domestic Product','GDP'], 
        
        ['zip','Zip'],['sector','Sector'],
        ['fullTimeEmployees','Employees'],['Employees','Employees'],
        ['longBusinessSummary','Long business summary'],['city','City'],['phone','Phone'],
        ['state','State/Province'],['country','Country/Region'],['companyOfficers','Company officers'],
        ['website','Website'],['address1','Address'],['industry','Industry'],
        ['previousClose','Prev close'],['regularMarketOpen','Regular market open'],
        ['twoHundredDayAverage','200-day average'],['fax','Fax'], 
        ['trailingAnnualDividendYield','Annual Div Yield TTM'],
        ['payoutRatio','Payout ratio'],['volume24Hr','Volume 24-hour'],
        ['regularMarketDayHigh','Regular market high'],
        ['averageDailyVolume10Day','10-day avg daily volume'],['totalAssets','Total Assets'],
        ['regularMarketPreviousClose','Regular market prev close'],
        ['fiftyDayAverage','50-day average'],
        ['trailingAnnualDividendRate','Annual div rate TTM'],['open','Open'],
        ['averageVolume10days','10-day avg volume'],['expireDate','Expire date'],
        ['yield','Yield'],['dividendRate','Dividend rate'],
        ['exDividendDate','Ex-dividend date'],['beta','Beta'],
        ['startDate','Start date'],['regularMarketDayLow','Regular market day low'],
        ['priceHint','Price hint'],['currency','Currency'],
        ['trailingPE','PE TTM'],['regularMarketVolume','Regular market volume'],
        ['marketCap','Market capitalization'],['averageVolume','Average volume'],
        ['priceToSalesTrailing12Months','Price-to-sales TTM'],
        ['TTM Price to Sales','Price-to-sales TTM'],
        ['dayLow','Day low'],
        ['ask','Ask/sell'],['askSize','Ask size'],['volume','Volume'],
        ['fiftyTwoWeekHigh','52-week high'],['forwardPE','Forward PE'],
        ['fiveYearAvgDividendYield','5-year Avg div yield'],
        ['fiftyTwoWeekLow','52-week low'],['bid','Bid/Buy-in'],
        ['tradeable','Tradeable'],['dividendYield','Dividend yield'],
        ['bidSize','Bid size'],['dayHigh','Day high'],
        ['exchange','Exchange'],['shortName','Short name'],['longName','Fullname'],
        ['exchangeTimezoneName','Exchange timezone name'],
        ['exchangeTimezoneShortName','Exchange timezone short name'],['quoteType','Quote type'],
        ['symbol','Symbol'],['messageBoardId','Message board id'],
        ['market','Market'],['annualHoldingsTurnover','Annual holdings turnover'],
        ['enterpriseToRevenue','EV/Revenue'],['EV to Revenue','EV/Revenue'],        
        ['Price to Book','Price-to-book'],['beta3Year','3-year beta'],
        ['profitMargins','Profit margin'],['enterpriseToEbitda','EV/EBITDA'],
        ['EV to EBITDA','EV/EBITDA'],
        ['52WeekChange','52-week change'],['morningStarRiskRating','Morningstar risk rating'],
        ['forwardEps','Forward EPS'],['revenueQuarterlyGrowth','Revenue quarterly growth'],
        ['sharesOutstanding','Shares outstanding'],['fundInceptionDate','Fund inception date'],
        ['annualReportExpenseRatio','Annual report expense ratio'],['bookValue','Book value per share'],
        ['sharesShort','Shares short (sell)'],['sharesPercentSharesOut','Shares percent shares-out(Shares short/outstanding)'],
        ['lastFiscalYearEnd','Last fiscal year end'],
        ['heldPercentInstitutions','Held percent by institutions'],
        ['netIncomeToCommon','Netincome to common'],['trailingEps','EPS TTM'],
        ['lastDividendValue','Last dividend value'],
        ['SandP52WeekChange','52-week S&P500 change'],['priceToBook','Price-to-book'],
        ['heldPercentInsiders','Held percent by insiders'],
        ['nextFiscalYearEnd','Next fiscal year end'],
        ['mostRecentQuarter','Most recent quarter'],['shortRatio','空头净额比率'],
        ['sharesShortPreviousMonthDate','上月做空日期'],
        ['floatShares','可交易股数'],['enterpriseValue','Enterprise value'],
        ['threeYearAverageReturn','3年平均回报率'],['lastSplitDate','上个拆分日期'],
        ['lastSplitFactor','上次拆分比例'],
        ['earningsQuarterlyGrowth','Earnings growth(quarterly)'],['dateShortInterest','做空日期'],
        ['pegRatio','PEG ratio'],['shortPercentOfFloat','空头占可交易股票比例'],
        ['sharesShortPriorMonth','上月做空股数'],
        ['fiveYearAverageReturn','5年平均回报率'],['regularMarketPrice','正常市场价'],
        ['logo_url','商标图标网址'],     ['underlyingSymbol','曾用代码'],     
        ['timeZoneShortName','时区简称'],['timeZoneFullName','时区全称'],
        ['exchangeName','Exchange name'],['currentPrice','Current price'],
        ['ratingYear','评估年度'],['ratingMonth','评估月份'],
        ['currencySymbol','币种符号'],['recommendationKey','Recommendation'],
        ['totalInsiderShares','Total insider shares'],['financialCurrency','Currency'],
        ['currentRatio','Current ratio'],['quickRatio','Quick ratio'],
        ['debtToEquity','Debt-to-equity%'],['ebitdaMargins','EBITDA margins'],
        ['operatingMargins','Operating margins'],['grossMargins','Gross margins'],
        ['returnOnAssets','Return on assets'],['returnOnEquity','Return on equity'],
        ['ROA','Return on assets'],['ROE','Return on equity'],
        ['revenuePerShare','Revenue per share'],['totalCashPerShare','Cashflow per share'],
        ['revenueGrowth','Revenue growth(annual)'],['earningsGrowth','Earnings growth(annual)'],
        ['totalDebt','Total debt'],['totalRevenue','Total revenue'],
        ['grossProfits','Gross profits'],['ebitda','EBITDA'],
        ['operatingCashflow','Operating cashflow'],['freeCashflow','Free cashflow'],
        ['totalCash','Total cash'],
        ['Total Asset Turnover','Total asset turnover'],['Fixed Asset Turnover','Fixed asset turnover'],
        ['PPE Residual','PPE Residual'],
        ['Current Ratio','Current ratio'],['Quick Ratio','Quick ratio'],['Debt to Equity','Debt-to-Equity%'],
        ['Debt to Asset','Debt to assets'],['Times Interest Earned','Times interest earned'],
        ['Inventory Turnover','Inventory turnover'],['Receivable Turnover','Receivable turnover'],
        ['BasicEPS','Basic EPS'],['Cashflow per Share','Cashflow per share'],
        ['Profit Margin','Profit margins'],['Gross Margin','Gross margins'],
        ['EBITDA Margin','EBITDA margins'],['Operating Margin','Operating margins'],
        ['Trailing EPS','EPS TTM'],['Trailing PE','PE TTM'],['Forward PE','Forward PE'],
        ['Revenue Growth','Revenue growth'],['Earnings Growth','Earnings growth(annual)'],
        ['Earnings Quarterly Growth','Earnings growth(quarterly)'],
        ['IGR','Internal growth rate'],['SGR','Sustainable growth rate'],
        
        ['overallRisk','Overall risk'],
        ['boardRisk','Board risk'],['compensationRisk','Compensation risk'],
        ['shareHolderRightsRisk','Shareholder rights risk'],['auditRisk','Audit risk'],
        
        ['totalEsg','Total ESG risk'],['Total ESG','Total ESG risk'],
        ['esgPerformance','ESG performance'],
        ['peerEsgScorePerformance','Peer ESG score performance'],
        ['environmentScore','Environment risk score'],['Environment Score','Environment risk score'],
        ['peerEnvironmentPerformance','Peer environment performance'],
        ['socialScore','CSR risk score'],['Social Score','CSR risk score'],
        ['peerSocialPerformance','Peer CSR performance'],
        ['governanceScore','Governance risk score'],['Governance Score','Governance risk score'],
        ['peerGovernancePerformance','Peer governance performance'],['peerGroup','Peer group'],
        ['relatedControversy','Related controversy'],['Social Supply Chain Incidents','Social supply chain incidents'],
        ['Customer Incidents','Customer incidents'],['Business Ethics Incidents','Business ethics incidents'],
        ['Product & Service Incidents','Product & service incidents'],
        ['Society & Community Incidents','Society & community incidents'],
        ['Employee Incidents','Employee incidents'],['Operations Incidents','Operations incidents'],
        ['peerCount','Peer count'],['percentile','Peer percentile'],  
        
        ['ESGscore','ESG risk score'],['ESGpercentile','ESG risk percentile%'],
        ['ESGperformance','ESG risk performance'],['EPscore','Environment risk score'],
        ['EPpercentile','Environment risk percentile%'],['CSRscore','CSR risk score'],
        ['CSRpercentile','CSR risk percentile%'],['CGscore','Governance risk score'],
        ['CGpercentile','Governance risk percentile%'],
        ['Peer Group','Peer Group'],['Count','Peer count'],     
        
        ['Gross Domestic Product','GDP'],
        ['Current Price Gross Domestic Product','GDP'],
        ['GNP Ratio','GNP(GNI)/GDP Ratio'],
        
        ['Consumer Price Index','CPI'],
        ['Consumer Price Index: All Items','CPI-All Items'],
        ['Consumer Price Index: All Items Growth Rate','CPI-All Items Growth Rate'],
        ['PPI','PPI'],['YoY PPI','YoY PPI%'],
        ['MoM PPI','MoM PPI%'],['Constant PPI','Constant PPI%'],
        ['Producer Prices Index: Industrial Activities','PPI-Industrial Activities'],
        ['Producer Prices Index: Total Industrial Activities','PPI-Total Industrial Activities'],
        
        ['National Monetary Supply M0','Outstanding Cash Supply M0'],
        ['National Monetary Supply M1','Monetary Supply M1'],
        ['National Monetary Supply M2','Monetary Supply M2'],
        ['National Monetary Supply M3','Monetary Supply M3'],
        
        ['Immediate Rate','Immediate Rate%'],
        ['Immediate Rates: Less than 24 Hours: Interbank Rate','Interbank Immediate Rates(in 24-hour)'],  
        
        ['Local Currency/USD Foreign Exchange Rate','Local/USD Exch Rate'],  
        ['USD/Local Currency Foreign Exchange Rate','USD/Local Exch Rate'],['Euro','Euro'],
        
        ['Stock Market Capitalization to GDP','Economic Depth in Finance Based on Stock Market Capitalization'],
        ['SMC to GDP','Total Market Cap/GDP'],
        
        ['Currency Value','Currency Value'],['Currency Purchasing Power Based on CPI','Currency Purchasing Power Based on CPI'],
        
        ['Portfolio','Portfolio'],['Portfolio_EW','Portfolio_EW'],['Portfolio_OMCap','Portfolio_OMCap'],
        ['Portfolio_MSR','Portfolio_MSR'],['Portfolio_GMV','Portfolio_GMV'],
        
        ['权益乘数','Equity Multiplier'],['销售净利率','Profit Margins'],['总资产周转率','Total Asset Turnover'],
        ['公司','Company'],['净资产收益率','ROE'],['财报日期','End Date'],['财报类型','Report Type'],
        
        ], columns=['eword','cword'])

    try:
        cword=ecdict[ecdict['eword']==eword]['cword'].values[0]
    except:
        #未查到翻译词汇，返回原词
        cword=eword
   
    return cword

if __name__=='__main__':
    eword='Exp Adj Ret'
    print(ectranslate('Annual Adj Ret%'))
    print(ectranslate('Annual*Adj Ret%'))

    eword='Constant M1'
    print(ectranslate(eword))
    print(ectranslate('Annual*Adj Ret%'))

#==============================================================================
def codetranslate(codelist):
    """
    翻译证券代码为证券名称，基于语言环境决定中英文。
    输入：证券代码列表。输出：证券名称列表
    """
    
    lang=check_language()
    if lang == 'English':
        return codetranslate_e(codelist)
    else:
        return codetranslate_c(codelist)

#==============================================================================
if __name__=='__main__':
    codelist=['601398.SS','01398.HK']
    code='601398.SS'
    code='01398.HK'

#在common中定义
#SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']
    
def codetranslate_e(codelist):
    """
    翻译证券代码为证券名称英文。
    输入：证券代码列表。输出：证券名称列表
    """
    
    if isinstance(codelist,list):
        namelist=[]
        for code in codelist:
            if not code in ['USA','UK']:
                name=codetranslate1(code)
            else:
                name=code
                
            name1=name
            result,prefix,suffix=split_prefix_suffix(code)
            if suffix in SUFFIX_LIST_CN:
                if not ('A' in name):
                    name1=name
            elif suffix in ['HK']:
                if not ('HK' in name):
                    name1=name+'(HK)'            
            else:
                name1=name
            namelist=namelist+[name1]
        return namelist
    elif isinstance(codelist,str):
        code=codelist
        if not code in ['USA','UK']:
            name=codetranslate1(code)
        else:
            name=code
            
        if name==code:
            return name
        name1=name
        result,prefix,suffix=split_prefix_suffix(code)
        if suffix in SUFFIX_LIST_CN:
            if not ('A' in name) and not('Index' in name):
                name1=name
        if suffix in ['HK']:
            if not ('HK' in name):
                name1=name+'(HK)'            
        return name1
    else:
        return codelist
            
if __name__=='__main__':
    codetranslate(['601398.SS','01398.HK','JD','BABA'])
    codetranslate('601398.SS')
    codetranslate('01398.HK')
    codetranslate('JD')
    codetranslate('AMZN')
    codetranslate('AAPL')
    codetranslate('XYZ')
#==============================================================================
if __name__=='__main__':
    codelist=['601398.SS','01398.HK']
    code='601398.SS'
    code='01398.HK'

#在common中定义
#SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']
    
def codetranslate_c(codelist):
    """
    翻译证券代码为证券名称中文。
    输入：证券代码列表。输出：证券名称列表
    """
    
    if isinstance(codelist,list):
        namelist=[]
        for code in codelist:
            name=codetranslate0(code)
            name1=name
            result,prefix,suffix=split_prefix_suffix(code)
            if suffix in SUFFIX_LIST_CN:
                if not ('A' in name):
                    name1=name
            elif suffix in ['HK']:
                if not ('港股' in name):
                    name1=name+'(港股)'            
            else:
                name1=name
            namelist=namelist+[name1]
        return namelist
    elif isinstance(codelist,str):
        code=codelist
        name=codetranslate0(code)
        if name==code:
            return name
        name1=name
        result,prefix,suffix=split_prefix_suffix(code)
        if suffix in SUFFIX_LIST_CN:
            if not ('A' in name) and not('指数' in name):
                name1=name
        if suffix in ['HK']:
            if not ('港股' in name):
                name1=name+'(港股)'            
        return name1
    else:
        return codelist
            
if __name__=='__main__':
    codetranslate(['601398.SS','01398.HK','JD','BABA'])
    codetranslate('601398.SS')
    codetranslate('01398.HK')
    codetranslate('JD')
    codetranslate('AMZN')
    codetranslate('AAPL')
    codetranslate('XYZ')

#==============================================================================

def codetranslate0(code):
    """
    翻译证券代码为证券名称中文。
    输入：证券代码。输出：证券名称
    """
    #不翻译情况:以空格开头，去掉空格返回
    if code[:1]==' ':
        return code[1:]
    
    import pandas as pd
    codedict=pd.DataFrame([
            
        #股票：地产
        ['000002.SZ','万科A'],['600266.SS','城建发展'],['600376.SS','首开股份'],
        ['600340.SS','华夏幸福'],['600606.SS','绿地控股'],
        
        #股票：白酒
        ['600519.SS','贵州茅台'],['000858.SZ','五粮液'],['000596.SZ','古井贡酒'],
        ['000568.SZ','泸州老窖'],['600779.SS','水井坊'],['002304.SZ','洋河股份'],
        ['000799.SZ','酒鬼酒'],['603589.SS','口子窖'],['600809.SS','山西汾酒'],
        
        #股票：银行
        ['601398.SS','工商银行A股'],['601939.SS','建设银行A股'],
        ['601288.SS','农业银行A股'],['601988.SS','中国银行A股'],
        ['600000.SS','浦发银行'],['601328.SS','交通银行'],
        ['600036.SS','招商银行'],['000776.SZ','广发银行'],
        ['601166.SS','兴业银行'],['601169.SS','北京银行'],
        ['600015.SS','华夏银行'],['601916.SS','浙商银行'],
        ['600016.SS','民生银行'],['000001.SZ','平安银行'],
        ['601818.SS','光大银行'],['601998.SS','中信银行'],
        ['601229.SS','上海银行'],['601658.SS','邮储银行'],
        
        ['01398.HK','工商银行港股'],['00939.HK','建设银行港股'],
        ['01288.HK','农业银行港股'],['00857.HK','中国石油港股'],
        ['00005.HK','港股汇丰控股'],['02888.HK','港股渣打银行'],
        ['03988.HK','中国银行港股'],['BANK OF CHINA','中国银行'],
        
        ['CICHY','中国建设银行美股'],['CICHF','中国建设银行美股'],
        ['ACGBY','中国农业银行美股'],['ACGBF','中国农业银行美股'],
        ['IDCBY','中国工商银行美股'],['IDCBF','中国工商银行美股'],
        ['BCMXY','交通银行美股'],
        
        ['BAC','美国银行'],['Bank of America Corporation','美国银行'],
        ['JPM','摩根大通'],['JP Morgan Chase & Co','摩根大通'],
        ['WFC','富国银行'],
        ['MS','摩根示丹利'],['Morgan Stanley','摩根示丹利'],
        ['USB','美国合众银行'],['U','美国合众银行'],
        ['TD','道明银行'],['Toronto Dominion Bank','道明银行'],
        ['PNC','PNC金融'],['PNC Financial Services Group','PNC金融'],
        ['BK','纽约梅隆银行'],['The Bank of New York Mellon Cor','纽约梅隆银行'],    
        ['GS','高盛'],['C','花旗集团'],
        
        ['8306.T','三菱日联金融'],['MITSUBISHI UFJ FINANCIAL GROUP','三菱日联金融'],
        ['8411.T','日股瑞穗金融'],['MIZUHO FINANCIAL GROUP','瑞穗金融'],
        ['7182.T','日本邮政银行'],['JAPAN POST BANK CO LTD','日本邮政银行'], 

        ['00005.HK','港股汇丰控股'],['HSBC HOLDINGS','汇丰控股'],
        ['02888.HK','港股渣打银行'],['STANCHART','渣打银行'],  
        
        ['UBSG.SW','瑞士瑞银'],        

        #股票：高科技
        ['AAPL','苹果'],['Apple','苹果'],['DELL','戴尔'],['IBM','国际商用机器'],
        ['MSFT','微软'],['Microsoft','微软'],['HPQ','惠普'],['AMD','超威半导体'],
        ['NVDA','英伟达'],['INTC','英特尔'],['QCOM','高通'],['BB','黑莓'],
        
        #股票：电商、互联网        
        ['AMZN','亚马逊'],['Amazon','亚马逊'],
        ['SHOP','Shopify'],['MELI','美客多'],
        ['EBAY','易贝'],['eBay','易贝'],['FB','脸书'],['ZM','ZOOM'],
        ['GOOG','谷歌'],['TWTR','推特'],
        ['VIPS','唯品会'],['Vipshop','唯品会'],
        ['PDD','拼多多'],['Pinduoduo','拼多多'],        
        ['BABA','阿里巴巴美股'],['Alibaba','阿里巴巴美股'],
        ['JD','京东美股'],
        ['SINA','新浪网'],['BIDU','百度'],['NTES','网易'],
        
        ['00700.HK','腾讯港股'],['TENCENT','腾讯控股'],
        ['09988.HK','阿里巴巴港股'],['BABA-SW','阿里巴巴港股'],
        ['09618.HK','京东港股'],['JD-SW','京东港股'], 
        
        #股票：石油、矿业
        ['SLB','斯伦贝谢'],['BKR','贝克休斯'],['HAL','哈里伯顿'],
        ['WFTLF','威德福'],['WFTUF','威德福'],
        ['OXY','西方石油'],['COP','康菲石油'],
        ['FCX','自由港矿业'], ['AEM','伊格尔矿业'],   
        ['XOM','美孚石油'],['2222.SR','沙特阿美'],
        ['BP','英国石油'],['RDSA.AS','壳牌石油'],
        ['1605.T','国际石油开发帝石'],['5020.T','新日本石油'],['5713.T','住友金属矿山'],
        
        ['NEM','纽蒙特矿业'],['SCCO','南方铜业'],
        ['RGLD','皇家黄金'],['AA','美铝'],['CLF','克利夫兰-克利夫斯矿业'],
        ['BTU','皮博迪能源'],        
        
        ['601857.SS','中国石油A股'],['PTR','中石油美股'],
        ['00857.HK','中国石油港股'],['PETROCHINA','中国石油'],
        
        ['00883.HK','中国海油港股'],['601808.SS','中海油服A股'],
        ['02883.HK','中海油服港股'],['600583.SS','海油工程A股'],['600968.SS','海油发展A股'],
        
        ['600028.SS','中国石化A股'],['00386.HK','中国石化港股'],
        ['600871.SS','石化油服A股'],['01033.HK','石化油服港股'],
        
        ['600339.SS','中油工程A股'],
        
        ['03337.HK','安东油服港股'],['603619.SS','中曼石油A股'],['002476.SZ','宝莫股份A股'],
        ['002828.SZ','贝肯能源A股'],['300164.SZ','通源石油A股'],['300084.SZ','海默科技A股'],
        ['300023.SZ','宝德股份A股'],
        
        #股票：汽车
        ['F','福特汽车'],['GM','通用汽车'],['TSLA','特斯拉'],
        ['7203.T','日股丰田汽车'],['7267.T','日股本田汽车'],['7201.T','日股日产汽车'], 
        ['DAI.DE','德国奔驰汽车'],['BMW.DE','德国宝马汽车'],
        ['XPEV','小鹏汽车'],['LI','理想汽车'],['00175.HK','吉利汽车'],
        ['02238.HK','广汽'],['000625.SZ','长安汽车'],['600104.SS','上汽'],['NIO','蔚来'],        
        
        #股票：制药
        ['LLY','礼来制药'],['Eli','礼来制药'],
        ['JNJ','强生制药'],['Johnson','强生制药'],
        ['VRTX','福泰制药'],['Vertex','福泰制药'],
        ['PFE','辉瑞制药'],['Pfizer','辉瑞制药'],
        ['MRK','默克制药'],['Merck','默克制药'],
        ['NVS','诺华制药'],['Novartis','诺华制药'],
        ['AMGN','安进制药'],['Amgen','安进制药'],
        ['SNY','赛诺菲制药'],['Sanofi','赛诺菲制药'],
        ['AZN','阿斯利康制药'],['MRNA','莫德纳生物'],
        ['NBIX','神经分泌生物'],['Neurocrine','神经分泌生物'],
        ['REGN','再生元制药'],['Regeneron','再生元制药'],
        ['PRGO','培瑞克制药'],['Perrigo','培瑞克制药'],
        ['TEVA','梯瓦制药'],['SNDX','Syndax制药'],
        ['BPTH','Bio-Path'],
        
        #股票：教育、视频
        ['BILI','哔哩哔哩'],['TAL','好未来'],['EDU','新东方'],['RYB','红黄蓝'],       
        ['IQ','爱奇艺'],['HUYA','虎牙'],['01024.HK','快手港股'],
        
        #股票：服饰，鞋帽，化妆品，体育，奢侈品
        ['002612.SZ','朗姿股份'],['002832.SZ','比音勒芬'],
        ['002291.SZ','星期六'],['600398.SS','海澜之家'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],
        ['603877.SS','太平鸟'],['002563.SZ','森马服饰'],
        ['002154.SZ','报喜鸟'],['002029.SZ','七匹狼'],
        ['601566.SS','九牧王'],['600107.SS','美尔雅'],
        ['603116.SS','红蜻蜓'],['002503.SZ','搜于特'],
        ['002193.SZ','如意集团'],['603001.SS','奥康国际'],
        ['300979.SZ','C华利'],['002269.SZ','美邦服饰'],
        ['600884.SS','杉杉股份'],['600177.SS','雅戈尔'],
        ['300526.SZ','中潜股份'],['601718.SS','际华集团'],
        ['603157.SS','拉夏贝尔A股'],['600295.SS','鄂尔多斯'],
        ['002293.SZ','罗莱生活'],['603587.SS','地素时尚'],
        ['002404.SZ','嘉欣丝绸'],['600612.SS','老凤祥'],
        ['300577.SZ','开润股份'],['600137.SS','浪莎股份'],
        
        ['02331.HK','李宁'],['02020.HK','安踏体育'],['01368.HK','特步国际'],
        ['01361.HK','361度'],['06116.HK','拉夏贝尔港股'],['03306.HK','江南布衣'],
        ['02298.HK','都市丽人'],['01388.HK','安莉芳'],['01749.HK','杉杉品牌'],
        ['01234.HK','中国利郎'],['02030.HK','卡宾'],['00709.HK','佐丹奴国际'],
        ['03998.HK','波司登'],['00592.HK','堡狮龙'],['02313.HK','申洲国际'],
        ['06110.HK','滔博'],['03813.HK','宝胜国际'],['06288.HK','迅销'],
        ['01913.HK','普拉达'],['00551.HK','裕元集团'],['02399.HK','虎都'],
        ['02232.HK','晶苑国际'],['01146.HK','中国服饰控股'],
        
        ['4911.T','日股资生堂'],['4452.T','日股花王'],
        ['9983.T','日股优衣库'],['7453.T','日股无印良品'],   
        
        ['CDI.PA','法国迪奥'],['DIO.F','法国迪奥'],['HMI.F','法国爱马仕'],
        
        #股票：其他
        ['PG','宝洁'],['KO','可口可乐'],['PEP','百事可乐'],
        ['BRK.A','伯克希尔'],['BRK.B','伯克希尔'],['Berkshire','伯克希尔'],
        ['COST','好事多'],['WMT','沃尔玛'],['DIS','迪士尼'],['BA','波音'],
        ['DPW','Ault Global'],['RIOT','Riot Blockchain'],['MARA','Marathon Digital'],['NCTY','9th City'],

        ['000651.SZ','格力电器A股'],['000333.SZ','美的集团A股'],

        ['00992.HK','港股联想'],['LENOVO GROUP','联想集团'],
        ['01810.HK','港股小米'],
        ['01166.HK','港股星凯控股'],['00273.HK','港股茂宸集团'],

        ['2330.TW','台积电'],['2317.TW','鸿海精密'],['2474.TW','可成科技'],
        ['3008.TW','大立光'],['2454.TW','联发科'],  
        
        ['6758.T','日股索尼'],
        
        ['005930.KS','三星电子'],
        
        ['TCS.NS','印度塔塔咨询'],
        
        #股票：指数==============================================================
        ['000300.SS','沪深300指数'],['399300.SS','沪深300指数'],
        ['000001.SS','上证综合指数'],['399001.SZ','深证成份指数'],
        ['000016.SS','上证50指数'],['000132.SS','上证100指数'],
        ['000133.SS','上证150指数'],['000010.SS','上证180指数'],
        ['000688.SS','科创板50指数'],['000043.SS','上证超大盘指数'],
        ['000044.SS','上证中盘指数'],['000046.SS','上证中小盘指数'],
        ['000045.SS','上证小盘指数'],['000004.SS','上证工业指数'],
        ['000005.SS','上证商业指数'],['000006.SS','上证地产指数'],
        ['000007.SS','上证公用指数'],['000038.SS','上证金融指数'],
        ['000057.SS','上证全指成长指数'],['000058.SS','上证全指价值指数'],
        ['000019.SS','上证治理指数'],['000048.SS','上证责任指数'],
        
        ['000002.SS','上证A股指数'],['000003.SS','上证B股指数'],
        ['399107.SZ','深证A股指数'],['399108.SZ','深证B股指数'],
        ['399106.SZ','深证综合指数'],['399004.SZ','深证100指数'],
        ['399012.SZ','创业板300指数'],
        
        ['399232.SZ','深证采矿业指数'],['399233.SZ','深证制造业指数'],
        ['399234.SZ','深证水电煤气指数'],['399236.SZ','深证批发零售指数'],
        ['399237.SZ','深证运输仓储指数'],['399240.SZ','深证金融业指数'],
        ['399241.SZ','深证房地产指数'],['399244.SZ','深证公共环保指数'],
        
        ['000903.SS','中证100指数'],['399903.SZ','中证100指数'],
        ['000904.SS','中证200指数'],['399904.SZ','中证200指数'],
        ['000905.SS','中证500指数'],['399905.SZ','中证500指数'],
        ['000907.SS','中证700指数'],['399907.SZ','中证700指数'],
        ['000906.SS','中证800指数'],['399906.SZ','中证800指数'],
        ['000852.SS','中证1000指数'],['399852.SZ','中证1000指数'],
        ['000985.SS','中证全指指数'],['399985.SZ','中证全指指数'],
        
        ['000012.SS','上证国债指数'],['000013.SS','上证企业债指数'],
        ['000022.SS','上证公司债指数'],['000061.SS','上证企债30指数'],
        ['000116.SS','上证信用债100指数'],['000101.SS','上证5年期信用债指数'],

        ['^GSPC','标普500指数'],['^DJI','道琼斯工业指数'],
        ['WISGP.SI','富时新加坡指数'], ['^STI','新加坡海峡时报指数'],
        ['^IXIC','纳斯达克综合指数'],['^FTSE','英国富时100指数'],
        ['FVTT.FGI','富时越南指数'],['^RUT','罗素2000指数'],
        ['^HSI','恒生指数'],['^N225','日经225指数'],
        ['WIKOR.FGI','富时韩国指数'],['^KS11','韩国综合指数'],
        ['^KOSPI','韩国综合指数'],['^BSESN','印度孟买敏感指数'],
        ['^FCHI','法国CAC40指数'],['^GDAXI','德国DAX30指数'], 
        ['^CAC','法国CAC40指数'],['^DAX','德国DAX30指数'], 
        ['IMOEX.ME','MOEX俄罗斯指数'],['^MOEX','MOEX俄罗斯指数'], 
        ['^RTS','RTS俄罗斯指数（美元标价）'],
        ['^VIX','VIX恐慌指数'],
        
        ['^HSCE','恒生H股指数'],['^HSNC','恒生工商业指数'],['^HSNU','恒生公用行业指数'], 
        ['^TWII','台湾加权指数'], 
        
        ['^XU100','伊斯坦堡100指数'], ['10TRY.B','土耳其10年期国债收益率%'],
        
        #债券==================================================================
        ['sh019521','15国债21'],['sz128086','国轩转债'],['sz123027','蓝晓转债'],
        ['^IRX','三个月美债收益率%'],['^FVX','五年美债收益率%'],
        ['^TNX','十年期美债收益率%'],['^TYX','三十年美债收益率%'],
        
        #基金==================================================================
        ['000595','嘉实泰和混合基金'],['000592','建信改革红利股票基金'],
        ['050111','博时信债C'],['320019','诺安货币B基金'],
        ['510580','易方达中证500ETF'],['510210.SS','上证综指ETF'],
        ["510050.SS",'华夏上证50ETF基金'],['510880.SS','上证红利ETF基金'],
        ["510180.SS",'上证180ETF基金'],['159901.SZ','深证100ETF基金'],
        ["159902.SZ",'深证中小板ETF基金'],['159901.SZ','深证100ETF基金'],
        ["159919.SZ",'嘉实沪深300ETF基金'],["510300.SS",'华泰柏瑞沪深300ETF基金'],
        
        ["004972",'长城收益宝货币A基金'],["004137",'博时合惠货币B基金'],
        ["002890",'交银天利宝货币E基金'],["004417",'兴全货币B基金'],
        ["005151",'红土创新优淳货币B基金'],["001909",'创金合信货币A基金'],
        ["001821",'兴全天添益货币B基金'],["000836",'国投瑞银钱多宝货币A基金'],
        ["000700",'泰达宏利货币B基金'],["001234",'国金众赢货币基金'],
        ["100051",'富国可转债A基金'],["217022",'招商产业债券A基金'],
        
        
        ["SPY",'SPDR SP500 ETF'],['SPYD','SPDR SP500 Div ETF'],
        ["SPYG",'SPDR SP500 Growth ETF'],['SPYV','SPDR SP500 Value ETF'],
        ["VOO",'Vanguard SP500 ETF'],['VOOG','Vanguard SP500 Growth ETF'],
        ["VOOV",'Vanguard SP500 Value ETF'],['IVV','iShares SP500 ETF'],        
        ["DGT",'SPDR Global Dow ETF'],['ICF','iShares C&S REIT ETF'], 
        ["FRI",'FT S&P REIT Index Fund'],['IEMG','iShares核心MSCI新兴市场ETF'],    
        ['245710.KS','KINDEX越南VN30指数ETF'],['02801.HK','iShares核心MSCI中国指数ETF'],
        
        #基金REITs
        ['180801.SZ','首钢绿能REIT'],['180201.SZ','广州广河REIT'],
        ['508001.SS','浙江杭徽REIT'],['508006.SS','首创水务REIT'],
        ['508056.SS','普洛斯REIT'],['508027.SS','东吴苏园REIT'],
        ['508000.SS','张江REIT'],['180101.SZ','蛇口产园REIT'],
        ['180301.SZ','盐港REIT'],
        
        ['FFR','富时美国REITs指数'],
        ['AMT','美国电塔REIT'],['CCI','Crown Castle REIT'],
        ['EQUIX','Equinix REIT'],['LAMR','Lamar Advertising REIT'],
        ['OUT','Outfront Media REIT'],['CIO','City Office REIT'],
        ['NYC','New York City REIT'],['REIT','ALPS Active REIT'],
        ['EARN','Ellington RM REIT'], ['VNQ','Vanguard ETF REIT'],  
        
        ['00823.HK','领展房产REIT'], ['02778.HK','冠君产业REIT'], 
        ['087001.HK','汇贤产业REIT'], ['00808.HK','泓富产业REIT'], 
        ['01426.HK','春泉产业REIT'], ['00435.HK','阳光房地产REIT'], 
        ['00405.HK','越秀房产REIT'], ['00778.HK','置富产业REIT'], 
        ['01275.HK','开元产业REIT'], ['01881.HK','富豪产业REIT'], 
        ['01503.HK','招商局商房REIT'], ['02191.HK','顺丰房托REIT'],
        
        ['3283.T','日本安博REIT'],
        
        ['C38U.SI','凯德商业信托REIT'],['N2IU.SI','枫树商业信托REIT'],
        ['T82U.SI','Suntec REIT'],['HMN.SI','雅诗阁公寓REIT'],

        #期货==================================================================
        ["HG=F",'COMEX铜矿石期货'],["CL=F",'NYM原油期货'],
        ["S=F",'CBT大豆期货'],["C=F",'CBT玉米期货'],
        ["ES=F",'CME标普500指数期货'],["YM=F",'CBT道指期货'],
        ["NQ=F",'CME纳指100期货'],["RTY=F",'罗素2000指数期货'],
        ["ZB=F",'10年期以上美债期货'],["ZT=F",'2年期美债期货'],
        ["ZF=F",'5年期美债期货'],["ZN=F",'10年期美债期货'],        
        
        #======================================================================
        #=新加入
        #======================================================================
        # 白酒行业
        ['603589.SS','口子窖'],['000568.SZ','泸州老窖'],['000858.SZ','五粮液'],
        ['600519.SS','贵州茅台'],['000596.SZ','古井贡酒'],['000799.SZ','酒鬼酒'],
        ['600809.SS','山西汾酒'],['600779.SS','水井坊'],

        # 房地产行业
        ['000002.SZ','万科A'],['600048.SS','保利地产'],['600340.SS','华夏幸福'],
        ['000031.SZ','大悦城'],['600383.SS','金地集团'],['600266.SS','城建发展'],
        ['600246.SS','万通发展'],['600606.SS','绿地控股'],['600743.SS','华远地产'],
        ['000402.SZ','金融街'],['000608.SZ','阳光股份'],['600376.SS','首开股份'],
        ['000036.SZ','华联控股'],['000620.SZ','新华联'],['600663.SS','陆家嘴'],

        # 银行业
        ['601328.SS','交通银行'],['601988.SS','中国银行'],['600015.SS','华夏银行'],
        ['601398.SS','工商银行'],['601169.SS','北京银行'],['601916.SS','浙商银行'],
        ['601288.SS','农业银行'],['601229.SS','上海银行'],['600016.SS','民生银行'],
        ['601818.SS','光大银行'],['601658.SS','邮储银行'],['600000.SS','浦发银行'],
        ['601939.SS','建设银行'],['601998.SS','中信银行'],['601166.SS','兴业银行'],
        ['600036.SS','招商银行'],['002142.SZ','宁波银行'],['000001.SZ','平安银行'],

        # 纺织服装行业
        ['002612.SZ','朗姿股份'],['601566.SS','九牧王'],['002269.SZ','美邦服饰'],
        ['600398.SS','海澜之家'],['600137.SS','浪莎股份'],['603001.SS','奥康国际'],
        ['603116.SS','红蜻蜓'],['002291.SZ','星期六'],['002832.SZ','比音勒芬'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],['603877.SS','太平鸟'],
        ['002563.SZ','森马服饰'],['002154.SZ','报喜鸟'],['600177.SS','雅戈尔'],
        ['002029.SZ','七匹狼'],

        # 物流行业
        ['002352.SZ','顺丰控股'],['002468.SZ','申通快递'],['600233.SS','圆通速递'],
        ['002120.SZ','韵达股份'],['603128.SS','华贸物流'],['603056.SS','德邦股份'],
        ['601598.SS','中国外运'],['603967.SS','中创物流'],['603128.SS','华贸物流'],

        # 券商行业
        ['601995.SS','中金公司'],['601788.SS','光大证券'],['300059.SZ','东方财富'],
        ['600030.SS','中信证券'],['601878.SS','浙商证券'],['600061.SS','国投资本'],
        ['600369.SS','西南证券'],['600837.SS','海通证券'],['601211.SS','国泰君安'],
        ['601066.SS','中信建投'],['601688.SS','华泰证券'],['000776.SZ','广发证券'],
        ['000166.SZ','申万宏源'],['600999.SS','招商证券'],['002500.SZ','山西证券'],
        ['601555.SS','东吴证券'],['000617.SZ','中油资本'],['600095.SS','湘财股份'],
        ['601519.SS','大智慧'],

        # 中国啤酒概念股
        ['600600.SS','青岛啤酒'],['600132.SS','重庆啤酒'],['002461.SZ','珠江啤酒'],
        ['000729.SZ','燕京啤酒'],['600573.SS','惠泉啤酒'],['000929.SZ','兰州黄河'],
        ['603076.SS','乐惠国际'],

        # 建筑工程概念股
        ['601186.SS','中国铁建'],['601668.SS','中国建筑'],['601800.SS','中国交建'],
        ['601789.SS','宁波建工'],['601669.SS','中国电建'],['000498.SZ','山东路桥'],
        ['600170.SS','上海建工'],['600248.SS','陕西建工'],['600502.SS','安徽建工'],
        ['600284.SS','浦东建设'],['603815.SS','交建股份'],['600039.SS','四川路桥'],

        # 民用航空概念股
        ['600221.SS','海南航空'],['603885.SS','吉祥航空'],['600115.SS','中国东航'],
        ['600029.SS','南方航空'],['601021.SS','春秋航空'],['601111.SS','中国国航'],
        ['002928.SZ','华夏航空'],

        # 家电概念股
        ['600690.SS','海尔智家'],['600060.SS','海信视像'],['000333.SZ','美的集团'],
        ['000404.SZ','长虹华意'],['000651.SZ','格力电器'],['000521.SZ','长虹美菱'],
        ['603868.SS','飞科电器'],['600839.SS','四川长虹'],['000921.SZ','海信家电'],
        ['002035.SZ','华帝股份'],['002242.SZ','九阳股份'],['600336.SS','澳柯玛'],
        ['600854.SS','春兰股份'],['000418.SZ','小天鹅A'],['002508.SZ','老板电器'],
        ['000810.SZ','创维数字'],['603551.SS','奥普家居'],['002959.SZ','小熊电器'],
        ['000100.SZ','TCL科技'],['002032.SZ','苏泊尔'],['000016.SZ','深康佳A'],
        ['600690.SS','青岛海尔'],['000541.SZ','佛山照明'],['603515.SS','欧普照明'],

        # 体育用品概念股
        ['02020.HK','安踏体育'],['02331.HK','李宁'],['01368.HK','特步国际'],
        ['01361.HK','361度'],['ADS.DE','ADIDAS'],['NKE','NIKE'],
        ['8022.T','MIZUNO'],['PUM.DE','PUMA SE'],['FILA.MI','FILA'],
        ['SKG.L','Kappa'],['7936.T','ASICS'],

        # 新加坡著名股票
        ['D05.SI','星展银行DBS'],['Z74.SI','新加坡电信'],['O39.SI','华侨银行'],
        ['U11.SI','大华银行'],['C6L.SI','新加坡航空'],['CC3.SI','Starhub'],
        ['S08.SI','新加坡邮政'],['F34.SI','WILMAR'],['C31.SI','CapitaLand'],  
        
        
        ], columns=['code','codename'])
    
    codename=code
    try:
        codename=codedict[codedict['code']==code]['codename'].values[0]
    except:
        #未查到翻译词汇，查找证券字典文件，需要定期更新
        codename=get_names(code)
        if not (codename is None): return codename
        
        """
        #未查到翻译词汇，先用akshare查找中文名称
        #不是国内股票或中文名称未查到
        try:
            codename=securities_name(code)
        except:
            pass
        """
    else:
        return codename

if __name__=='__main__':
    code='GOOG'
    print(codetranslate('000002.SZ'))
    print(codetranslate('09988.HK'))
#==============================================================================

def codetranslate1(code):
    """
    翻译证券代码为证券名称英文。
    输入：证券代码。输出：证券名称
    """
    #不翻译情况:以空格开头，去掉空格返回
    if code[:1]==' ':
        return code[1:]
    
    import pandas as pd
    codedict=pd.DataFrame([
            
        #股票：地产
        ['000002.SZ','Wanke A'],['600266.SS','城建发展'],['600376.SS','首开股份'],
        ['600340.SS','华夏幸福'],['600606.SS','绿地控股'],
        
        #股票：白酒
        ['600519.SS','Moutai'],['000858.SZ','Wuliangye'],['000596.SZ','Gujinggong'],
        ['000568.SZ','Luzhou Laojiao'],['600779.SS','Suijingfang'],['002304.SZ','Yanghe'],
        ['000799.SZ','Jiuguijiu'],['603589.SS','Kouzijiao'],['600809.SS','Shanxi Fenjiu'],
        
        #股票：银行
        ['601398.SS','ICBC(A)'],['601939.SS','CCB(A)'],
        ['601288.SS','ABC(A)'],['601988.SS','BOC(A)'],
        ['600000.SS','浦发银行'],['601328.SS','交通银行'],
        ['600036.SS','招商银行'],['000776.SZ','广发银行'],
        ['601166.SS','兴业银行'],['601169.SS','北京银行'],
        ['600015.SS','华夏银行'],['601916.SS','浙商银行'],
        ['600016.SS','民生银行'],['000001.SZ','平安银行'],
        ['601818.SS','光大银行'],['601998.SS','中信银行'],
        ['601229.SS','上海银行'],['601658.SS','邮储银行'],
        
        ['01398.HK','ICBC(HK)'],['00939.HK','CCB(HK)'],
        ['01288.HK','ABC(HK)'],['00857.HK','Petro China(HK)'],
        ['00005.HK','HSBC(HK)'],['02888.HK','Standard Chartered(HK)'],
        ['03988.HK','BOC(HK)'],['BANK OF CHINA','中国银行'],
        
        ['CICHY','CCB(US)'],['CICHF','CCB(US)'],
        ['ACGBY','ABC(US)'],['ACGBF','ABC(US)'],
        ['IDCBY','ICBC(US)'],['IDCBF','ICBC(US)'],
        ['BCMXY','BCM(US)'],
        
        ['BAC','Bank of America'],['Bank of America Corporation','Bank of America'],
        ['JPM','JP Morgan'],['JP Morgan Chase & Co','JP Morgan'],
        ['WFC','Wells Fargo'],
        ['MS','Morgan Stanley'],['Morgan Stanley','Morgan Stanley'],
        ['USB','US Bancorp'],['U','US Bancorp'],
        ['TD','Toronto Dominion'],['Toronto Dominion Bank','Toronto Dominion'],
        ['PNC','PNC Financial'],['PNC Financial Services Group','PNC Financial'],
        ['BK','NY Mellon'],['The Bank of New York Mellon Cor','NY Mellon'],    
        ['GS','Goldman Sachs'],['C','Citigroup'],
        
        ['8306.T','MITSUBISHI UFJ'],['MITSUBISHI UFJ FINANCIAL GROUP','MITSUBISHI UFJ'],
        ['8411.T','MIZUHO FINANCIAL'],['MIZUHO FINANCIAL GROUP','MIZUHO FINANCIAL'],
        ['7182.T','JAPAN POSTBANK'],['JAPAN POST BANK CO LTD','JAPAN POSTBANK'], 

        ['00005.HK','HSBC(HK)'],['HSBC HOLDINGS','HSBC'],
        ['02888.HK','Standard Chartered(HK)'],['STANCHART','Standard Chartered'],  
        
        ['UBSG.SW','UBS(SW)'],        

        #股票：高科技
        ['AAPL','Apple'],['Apple','Apple'],['DELL','DELL'],['IBM','IBM'],
        ['MSFT','Microsoft'],['Microsoft','Microsoft'],['HPQ','HP'],['AMD','AMD'],
        ['NVDA','NVidia'],['INTC','Intel'],['QCOM','Qualcomm'],['BB','Blackberry'],
        
        #股票：电商、互联网        
        ['AMZN','Amazon'],['Amazon','Amazon'],
        ['SHOP','Shopify'],['MELI','Mercado Libre'],
        ['EBAY','eBay'],['eBay','eBay'],['FB','Facebook'],['ZM','ZOOM'],
        ['GOOG','Google'],['TWTR','Twitter'],
        ['VIPS','Vipshop'],['Vipshop','Vipshop'],
        ['PDD','Pinduoduo'],['Pinduoduo','Pinduoduo'],        
        ['BABA','Alibaba(US)'],['Alibaba','Alibaba'],
        ['JD','JD(US)'],
        ['SINA','Sina'],['BIDU','Baidu'],['NTES','Netease'],
        
        ['00700.HK','Tencent(HK)'],['TENCENT','Tencent'],
        ['09988.HK','Alibaba(HK)'],['BABA-SW','Alibaba(HK)'],
        ['09618.HK','JD(HK)'],['JD-SW','JD(HK)'], 
        
        #股票：石油、矿业
        ['SLB','Schlumberger'],['BKR','Baker-Hughes'],['HAL','Halliburton'],
        ['WFTLF','Weatherford'],['WFTUF','Weatherford'],
        ['OXY','Occidental Petroleum'],['COP','Conoco Phillips'],
        ['FCX','Freeport-McMoRan'], ['AEM','Agnico Eagle Mines'],   
        ['XOM','Exxon Mobil'],['2222.SR','Saudi Aramco'],
        ['BP','British Petroleum'],['RDSA.AS','Shell Oil'],['SOEX','Shell Oil'],
        ['1605.T','INPEX(JP)'],['5020.T','Nippon Oil(JP)'],['5713.T','Sumitomo Metalmining(JP)'],
        
        ['NEM','Newmont Mining'],['SCCO','Southern Copper'],
        ['RGLD','Royal Gold'],['AA','Alcoa'],['CLF','Cleveland-Cliffs'],
        ['BTU','Peabody Energy'],        
        
        ['601857.SS','Petro China(A)'],['PTR','Petro China(US)'],
        ['00857.HK','Petro China(HK)'],['PETROCHINA','Petro China'],
        
        ['00883.HK','CNOOC(HK)'],['601808.SS','COSL(A)'],
        ['02883.HK','COSL(HK)'],['600583.SS','CNOOC Engineering(A)'],['600968.SS','CNOOC Development(A)'],
        
        ['600028.SS','Sinopec(A)'],['00386.HK','Sinopec(HK)'],
        ['600871.SS','Sinopec Oilfield(A)'],['01033.HK','Sinopec Oilfield(HK)'],
        
        ['600339.SS','CNPC Engineering(A)'],
        
        ['03337.HK','安东油服港股'],['603619.SS','中曼石油A股'],['002476.SZ','宝莫股份A股'],
        ['002828.SZ','贝肯能源A股'],['300164.SZ','通源石油A股'],['300084.SZ','海默科技A股'],
        ['300023.SZ','宝德股份A股'],
        
        #股票：汽车
        ['F','Ford Motors'],['GM','General Motors'],['TSLA','Tesla Motors'],
        ['7203.T','Toyota Motors(JP)'],['7267.T','Honda Motors(JP)'],['7201.T','Nissan Motors(JP)'], 
        ['DAI.DE','Mercedes-Benz'],['BMW.DE','BMW'],
        ['XPEV','XPENG Auto'],['LI','LI Auto'],['00175.HK','Geely Auto'],
        ['02238.HK','GAGC Auto'],['000625.SZ','Changan Auto'],['600104.SS','SAIC Auto'],['NIO','NIO Auto'],        
        
        #股票：制药
        ['LLY','Eli Lilly'],['Eli','Eli Lilly'],
        ['JNJ','Johnson Pharm'],['Johnson','Johnson Pharm'],
        ['VRTX','Vertex Pharm'],['Vertex','Vertex Pharm'],
        ['PFE','Pfizer'],['Pfizer','Pfizer'],
        ['MRK','Merck Pharm'],['Merck','Merck Pharm'],
        ['NVS','Novartis Pharm'],['Novartis','Novartis Pharm'],
        ['AMGN','Amgen'],['Amgen','Amgen'],
        ['SNY','Sanofi-Aventis'],['Sanofi','Sanofi-Aventis'],
        ['AZN','AstraZeneca'],['MRNA','Moderna Bio'],
        ['NBIX','Neurocrine Bio'],['Neurocrine','Neurocrine Bio'],
        ['REGN','Regeneron Pharm'],['Regeneron','Regeneron Pharm'],
        ['PRGO','Perrigo'],['Perrigo','Perrigo'],
        ['TEVA','Teva Pharm'],['SNDX','Syndax Pharm'],
        ['BPTH','Bio-Path'],
        
        #股票：教育、视频
        ['BILI','Bilibili'],['TAL','TAL Education'],['EDU','New Oriental'],['RYB','RYB Education'],       
        ['IQ','IQIYI'],['HUYA','Huya'],['01024.HK','Kuashou(HK)'],
        
        #股票：服饰，鞋帽，化妆品，体育，奢侈品
        ['002612.SZ','朗姿股份'],['002832.SZ','比音勒芬'],
        ['002291.SZ','星期六'],['600398.SS','海澜之家'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],
        ['603877.SS','太平鸟'],['002563.SZ','森马服饰'],
        ['002154.SZ','报喜鸟'],['002029.SZ','七匹狼'],
        ['601566.SS','九牧王'],['600107.SS','美尔雅'],
        ['603116.SS','红蜻蜓'],['002503.SZ','搜于特'],
        ['002193.SZ','如意集团'],['603001.SS','奥康国际'],
        ['300979.SZ','C华利'],['002269.SZ','美邦服饰'],
        ['600884.SS','杉杉股份'],['600177.SS','雅戈尔'],
        ['300526.SZ','中潜股份'],['601718.SS','际华集团'],
        ['603157.SS','拉夏贝尔A股'],['600295.SS','鄂尔多斯'],
        ['002293.SZ','罗莱生活'],['603587.SS','地素时尚'],
        ['002404.SZ','嘉欣丝绸'],['600612.SS','老凤祥'],
        ['300577.SZ','开润股份'],['600137.SS','浪莎股份'],
        
        ['02331.HK','Lining Sports(HK)'],['02020.HK','Anta Sports(HK)'],['01368.HK','Xtep Intl(HK)'],
        ['01361.HK','361°(HK)'],['06116.HK','La Chapelle(HK)'],['03306.HK','JNBY(HK)'],
        ['02298.HK','Cosmo Lady(HK)'],['01388.HK','Embry Form(HK)'],['01749.HK','FIRS(HK)'],
        ['01234.HK','Lilanz(HK)'],['02030.HK','Cabbeen Fashion(HK)'],['00709.HK','Giordano(HK)'],
        ['03998.HK','Bosideng(HK)'],['00592.HK','Bossini(HK)'],['02313.HK','Shenzhou Intl(HK)'],
        ['06110.HK','Topsports Intl(HK)'],['03813.HK','Pou Sheng Intl(HK)'],['06288.HK','Fast Retailing(HK)'],
        ['01913.HK','PRADA(HK)'],['00551.HK','Yue Yuen(HK)'],['02399.HK','China Fordoo(HK)'],
        ['02232.HK','Crystal Intl(HK)'],['01146.HK','China Outfitters(HK)'],
        
        ['4911.T','Shiseido(JP)'],['4452.T','Kao(JP)'],
        ['9983.T','Fast Retailing(JP)'],['7453.T','Muji(HK)'],   
        
        ['CDI.PA','Dior(F)'],['DIO.F','Dior(F)'],['HMI.F','Hermes(F)'],
        
        #股票：其他
        ['PG','P&G'],['KO','Coca Cola'],['PEP','Pepsi-Cola'],
        ['BRK.A','Berkshire A'],['BRK.B','Berkshire B'],['Berkshire','伯克希尔'],
        ['COST','Costco'],['WMT','Wal Mart'],['DIS','Disney'],['BA','Boeing'],
        ['DPW','Ault Global'],['RIOT','Riot Blockchain'],['MARA','Marathon Digital'],['NCTY','9th City'],

        ['000651.SZ','Gree Electric(A)'],['000333.SZ','Midea(A)'],

        ['00992.HK','Lenovo(HK)'],['LENOVO GROUP','Lenovo'],
        ['01810.HK','Xiaomi(HK)'],
        ['01166.HK','Solartech(HK)'],['00273.HK','Mason Group(HK)'],

        ['2330.TW','TSMC(TW)'],['2317.TW','Hon Hai Precision(TW)'],['2474.TW','Catcher Tech(TW)'],
        ['3008.TW','Largan(TW)'],['2454.TW','MediaTek(TW)'],  
        
        ['6758.T','SONY(JP)'],
        
        ['005930.KS','Samsung(KS)'],
        
        ['TCS.NS','TCS(IN)'],
        
        #股票：指数==============================================================
        ['000300.SS','CSI300 Index'],['399300.SS','CSI300 Index'],
        ['000001.SS','SSE Composite Index'],['399001.SZ','SZE Component Index'],
        ['000016.SS','SSE50 Index'],['000132.SS','SSE100 Index'],
        ['000133.SS','SSE150 Index'],['000010.SS','SSE180 Index'],
        ['000688.SS','STAR50 Index'],['000043.SS','SSE Supercap Index'],
        ['000044.SS','SSE Midcap Index'],['000046.SS','SSE Mid-small Cap Index'],
        ['000045.SS','SSE Smallcap Index'],['000004.SS','上证工业指数'],
        ['000005.SS','SSE Commercial Index'],['000006.SS','SSE Realestate Index'],
        ['000007.SS','SSE Utility Index'],['000038.SS','SSE Financial Index'],
        ['000057.SS','SSE Growth Index'],['000058.SS','SSE Value Index'],
        ['000019.SS','SSE Governance Index'],['000048.SS','SSE CSR Index'],
        
        ['000002.SS','SSE A Index'],['000003.SS','SSE B Index'],
        ['399107.SZ','SZE A Index'],['399108.SZ','SZE B Index'],
        ['399106.SZ','SZE Composite Index'],['399004.SZ','SZE100 Index'],
        ['399012.SZ','GEM300 Index'],
        
        ['399232.SZ','SZE Mining Index'],['399233.SZ','SZE Manufacturing Index'],
        ['399234.SZ','SZE Utility Index'],['399236.SZ','SZE Commercial Index'],
        ['399237.SZ','SZE Logistics Index'],['399240.SZ','SZE Financial Index'],
        ['399241.SZ','SZE Realestate Index'],['399244.SZ','SZE EP Index'],
        
        ['000903.SS','CSI100 Index'],['399903.SZ','CSI100 Index'],
        ['000904.SS','CSI200 Index'],['399904.SZ','CSI200 Index'],
        ['000905.SS','CSI500 Index'],['399905.SZ','CSI500 Index'],
        ['000907.SS','CSI700 Index'],['399907.SZ','CSI700 Index'],
        ['000906.SS','CSI800 Index'],['399906.SZ','CSI800 Index'],
        ['000852.SS','CSI1000 Index'],['399852.SZ','CSI1000 Index'],
        ['000985.SS','CSI Composite Index'],['399985.SZ','CSI Composite Index'],
        
        ['000012.SS','SSE T-Bond Index'],['000013.SS','SSE Ent Bond Index'],
        ['000022.SS','SSE Corpbond Index'],['000061.SS','SSE Entbond30 Index'],
        ['000116.SS','SSE Creditbond100 Index'],['000101.SS','SSE 5-year Creditbond Index'],

        ['^GSPC','S&P500 Index'],['^DJI','Dow Jones Index'],
        ['WISGP.SI','FTSE Singapore Index'], ['^STI','Straits Times Index'],
        ['^IXIC','Nasdaq Composite Index'],['^FTSE','FTSE 100 Index'],
        ['FVTT.FGI','FTSE Viernam Index'],['^RUT','Russell 2000 Index'],
        ['^HSI','Hang Seng Index'],['^N225','Nikkei 225 Index'],
        ['WIKOR.FGI','FTSE Korea Index'],['^KS11','Korea Composite Index'],
        ['^KOSPI','Korea Composite Index'],['^BSESN','SENSEX Index'],
        ['^FCHI','CAC40 Index'],['^GDAXI','DAX30 Index'], 
        ['^CAC','CAC40 Index'],['^DAX','DAX30 Index'], 
        ['IMOEX.ME','MOEX Index'],['^MOEX','MOEX Index'], 
        ['^RTS','RTS(USD) Index'],
        ['^VIX','VIX Index'],
        
        ['^HSCE','Hang Seng H-share Index'],['^HSNC','Hang Seng Commercial Index'],
        ['^HSNU','Hang Seng Utility Index'], 
        ['^TWII','Taiwan Weighted Index'], 
        
        ['^XU100','ISE National-100 index'], ['10TRY.B','Turkey 10-year Treasurybond Yield%'],
        
        #债券==================================================================
        ['sh019521','15国债21'],['sz128086','国轩转债'],['sz123027','蓝晓转债'],
        ['^IRX','13-week Treasury Yield%'],['^FVX','5-year Treasury Yield%'],
        ['^TNX','10-year Treasury Yield%'],['^TYX','30-year Treasury Yield%'],
        
        #基金==================================================================
        ['000595','嘉实泰和混合基金'],['000592','建信改革红利股票基金'],
        ['050111','博时信债C'],['320019','诺安货币B基金'],
        ['510580','Yifangda CSI500 ETF'],['510210.SS','SSE Composite Index ETF'],
        ["510050.SS",'Huaxia CSI50 ETF'],['510880.SS','SSE Dividend ETF'],
        ["510180.SS",'SSE180 ETF'],['159901.SZ','SZE100 ETF'],
        ["159902.SZ",'SZE SMB ETF'],['159901.SZ','SZE100 ETF'],
        ["159919.SZ",'Jiashi CSI300 ETF'],["510300.SS",'Huaxia Borui CSI300 ETF'],
        
        ["004972",'长城收益宝货币A基金'],["004137",'博时合惠货币B基金'],
        ["002890",'交银天利宝货币E基金'],["004417",'兴全货币B基金'],
        ["005151",'红土创新优淳货币B基金'],["001909",'创金合信货币A基金'],
        ["001821",'兴全天添益货币B基金'],["000836",'国投瑞银钱多宝货币A基金'],
        ["000700",'泰达宏利货币B基金'],["001234",'国金众赢货币基金'],
        ["100051",'富国可转债A基金'],["217022",'招商产业债券A基金'],
        
        
        ["SPY",'SPDR SP500 ETF'],['SPYD','SPDR SP500 Div ETF'],
        ["SPYG",'SPDR SP500 Growth ETF'],['SPYV','SPDR SP500 Value ETF'],
        ["VOO",'Vanguard SP500 ETF'],['VOOG','Vanguard SP500 Growth ETF'],
        ["VOOV",'Vanguard SP500 Value ETF'],['IVV','iShares SP500 ETF'],        
        ["DGT",'SPDR Global Dow ETF'],['ICF','iShares C&S REIT ETF'], 
        ["FRI",'FT S&P REIT Index Fund'],['IEMG','iShares核心MSCI新兴市场ETF'],    
        ['245710.KS','KINDEX越南VN30指数ETF'],['02801.HK','iShares核心MSCI中国指数ETF'],
        
        #基金REITs
        ['180801.SZ','首钢绿能REIT'],['180201.SZ','广州广河REIT'],
        ['508001.SS','浙江杭徽REIT'],['508006.SS','首创水务REIT'],
        ['508056.SS','普洛斯REIT'],['508027.SS','东吴苏园REIT'],
        ['508000.SS','张江REIT'],['180101.SZ','蛇口产园REIT'],
        ['180301.SZ','盐港REIT'],
        
        ['FFR','FTSE USA REITs Index'],
        ['AMT','美国电塔REIT'],['CCI','Crown Castle REIT'],
        ['EQUIX','Equinix REIT'],['LAMR','Lamar Advertising REIT'],
        ['OUT','Outfront Media REIT'],['CIO','City Office REIT'],
        ['NYC','New York City REIT'],['REIT','ALPS Active REIT'],
        ['EARN','Ellington RM REIT'], ['VNQ','Vanguard ETF REIT'],  
        
        ['00823.HK','领展房产REIT'], ['02778.HK','冠君产业REIT'], 
        ['087001.HK','汇贤产业REIT'], ['00808.HK','泓富产业REIT'], 
        ['01426.HK','春泉产业REIT'], ['00435.HK','阳光房地产REIT'], 
        ['00405.HK','越秀房产REIT'], ['00778.HK','置富产业REIT'], 
        ['01275.HK','开元产业REIT'], ['01881.HK','富豪产业REIT'], 
        ['01503.HK','招商局商房REIT'], ['02191.HK','SF REIT'],
        
        ['3283.T','日本安博REIT'],
        
        ['C38U.SI','凯德商业信托REIT'],['N2IU.SI','枫树商业信托REIT'],
        ['T82U.SI','Suntec REIT'],['HMN.SI','雅诗阁公寓REIT'],

        #期货==================================================================
        ["HG=F",'COMEX铜矿石期货'],["CL=F",'NYM原油期货'],
        ["S=F",'CBT大豆期货'],["C=F",'CBT玉米期货'],
        ["ES=F",'CME标普500指数期货'],["YM=F",'CBT道指期货'],
        ["NQ=F",'CME纳指100期货'],["RTY=F",'罗素2000指数期货'],
        ["ZB=F",'10年期以上美债期货'],["ZT=F",'2年期美债期货'],
        ["ZF=F",'5年期美债期货'],["ZN=F",'10年期美债期货'],        
        
        #======================================================================
        #=新加入
        #======================================================================
        # 白酒行业
        ['603589.SS','口子窖'],['000568.SZ','泸州老窖'],['000858.SZ','五粮液'],
        ['600519.SS','贵州茅台'],['000596.SZ','古井贡酒'],['000799.SZ','酒鬼酒'],
        ['600809.SS','山西汾酒'],['600779.SS','水井坊'],

        # 房地产行业
        ['000002.SZ','万科A'],['600048.SS','保利地产'],['600340.SS','华夏幸福'],
        ['000031.SZ','大悦城'],['600383.SS','金地集团'],['600266.SS','城建发展'],
        ['600246.SS','万通发展'],['600606.SS','绿地控股'],['600743.SS','华远地产'],
        ['000402.SZ','金融街'],['000608.SZ','阳光股份'],['600376.SS','首开股份'],
        ['000036.SZ','华联控股'],['000620.SZ','新华联'],['600663.SS','陆家嘴'],

        # 银行业
        ['601328.SS','交通银行'],['601988.SS','中国银行'],['600015.SS','华夏银行'],
        ['601398.SS','工商银行'],['601169.SS','北京银行'],['601916.SS','浙商银行'],
        ['601288.SS','农业银行'],['601229.SS','上海银行'],['600016.SS','民生银行'],
        ['601818.SS','光大银行'],['601658.SS','邮储银行'],['600000.SS','浦发银行'],
        ['601939.SS','建设银行'],['601998.SS','中信银行'],['601166.SS','兴业银行'],
        ['600036.SS','招商银行'],['002142.SZ','宁波银行'],['000001.SZ','平安银行'],

        # 纺织服装行业
        ['002612.SZ','朗姿股份'],['601566.SS','九牧王'],['002269.SZ','美邦服饰'],
        ['600398.SS','海澜之家'],['600137.SS','浪莎股份'],['603001.SS','奥康国际'],
        ['603116.SS','红蜻蜓'],['002291.SZ','星期六'],['002832.SZ','比音勒芬'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],['603877.SS','太平鸟'],
        ['002563.SZ','森马服饰'],['002154.SZ','报喜鸟'],['600177.SS','雅戈尔'],
        ['002029.SZ','七匹狼'],

        # 物流行业
        ['002352.SZ','顺丰控股'],['002468.SZ','申通快递'],['600233.SS','圆通速递'],
        ['002120.SZ','韵达股份'],['603128.SS','华贸物流'],['603056.SS','德邦股份'],
        ['601598.SS','中国外运'],['603967.SS','中创物流'],['603128.SS','华贸物流'],

        # 券商行业
        ['601995.SS','中金公司'],['601788.SS','光大证券'],['300059.SZ','东方财富'],
        ['600030.SS','中信证券'],['601878.SS','浙商证券'],['600061.SS','国投资本'],
        ['600369.SS','西南证券'],['600837.SS','海通证券'],['601211.SS','国泰君安'],
        ['601066.SS','中信建投'],['601688.SS','华泰证券'],['000776.SZ','广发证券'],
        ['000166.SZ','申万宏源'],['600999.SS','招商证券'],['002500.SZ','山西证券'],
        ['601555.SS','东吴证券'],['000617.SZ','中油资本'],['600095.SS','湘财股份'],
        ['601519.SS','大智慧'],

        # 中国啤酒概念股
        ['600600.SS','青岛啤酒'],['600132.SS','重庆啤酒'],['002461.SZ','珠江啤酒'],
        ['000729.SZ','燕京啤酒'],['600573.SS','惠泉啤酒'],['000929.SZ','兰州黄河'],
        ['603076.SS','乐惠国际'],

        # 建筑工程概念股
        ['601186.SS','中国铁建'],['601668.SS','中国建筑'],['601800.SS','中国交建'],
        ['601789.SS','宁波建工'],['601669.SS','中国电建'],['000498.SZ','山东路桥'],
        ['600170.SS','上海建工'],['600248.SS','陕西建工'],['600502.SS','安徽建工'],
        ['600284.SS','浦东建设'],['603815.SS','交建股份'],['600039.SS','四川路桥'],

        # 民用航空概念股
        ['600221.SS','海南航空'],['603885.SS','吉祥航空'],['600115.SS','中国东航'],
        ['600029.SS','南方航空'],['601021.SS','春秋航空'],['601111.SS','中国国航'],
        ['002928.SZ','华夏航空'],

        # 家电概念股
        ['600690.SS','海尔智家'],['600060.SS','海信视像'],['000333.SZ','美的集团'],
        ['000404.SZ','长虹华意'],['000651.SZ','格力电器'],['000521.SZ','长虹美菱'],
        ['603868.SS','飞科电器'],['600839.SS','四川长虹'],['000921.SZ','海信家电'],
        ['002035.SZ','华帝股份'],['002242.SZ','九阳股份'],['600336.SS','澳柯玛'],
        ['600854.SS','春兰股份'],['000418.SZ','小天鹅A'],['002508.SZ','老板电器'],
        ['000810.SZ','创维数字'],['603551.SS','奥普家居'],['002959.SZ','小熊电器'],
        ['000100.SZ','TCL科技'],['002032.SZ','苏泊尔'],['000016.SZ','深康佳A'],
        ['600690.SS','青岛海尔'],['000541.SZ','佛山照明'],['603515.SS','欧普照明'],

        # 体育用品概念股
        ['02020.HK','Anta Sports(HK)'],['02331.HK','Li-Ning(H)'],['01368.HK','Xtep Intl(HK)'],
        ['01361.HK','361°(HK)'],['ADS.DE','ADIDAS(DE)'],['NKE','NIKE'],
        ['8022.T','Mizuno(JP)'],['PUM.DE','PUMA(DE)'],['FILA.MI','FILA(MI)'],
        ['SKG.L','Kappa(LSE)'],['7936.T','ASICS(JP)'],

        # 新加坡著名股票
        ['D05.SI','DBS(SI)'],['Z74.SI','Singtel(SI)'],['O39.SI','OCBC(SI)'],
        ['U11.SI','UOB(SI)'],['C6L.SI','Singapore Airlines(SI)'],['CC3.SI','Starhub(SI)'],
        ['S08.SI','Singpost(SI)'],['F34.SI','WILMAR(SI)'],['C31.SI','CapitaLand(SI)'],  
        
        
        ], columns=['code','codename'])
    
    codename=code
    try:
        codename=codedict[codedict['code']==code]['codename'].values[0]
    except:
        #未查到翻译词汇，查找证券字典文件，需要定期更新
        codename=get_names(code)
        if not (codename is None): return codename
        
        """
        #未查到翻译词汇，先用akshare查找中文名称
        #不是国内股票或中文名称未查到
        try:
            codename=securities_name(code)
        except:
            pass
        """
    else:
        return codename

if __name__=='__main__':
    code='GOOG'
    print(codetranslate('000002.SZ'))
    print(codetranslate('09988.HK'))


#==============================================================================
if __name__=='__main__':
    symbol='00700.HK'
    
def get_names(symbol):
    """
    从文件中查询证券代码的短名称
    """
    
    symbol2=symbol
    result,prefix,suffix=split_prefix_suffix(symbol)
    
    #若后缀是港股、前缀为五位数且首位为0，则去掉首位0
    if (suffix=='HK') and (len(prefix)==5):
        if prefix[:1]=='0':
            symbol2=prefix[1:]+'.'+suffix
    
    #查询现有数据库
    import pickle
    import siat
    import os
    siatpath=siat.__path__
    file_path = os.path.join(siatpath[0], 'stock_info.pickle')
    with open(file_path,'rb') as test:
        df = pickle.load(test)  
        
    df1=df[df['SYMBOL']==symbol2]
    
    #查询结果
    lang=check_language()
    name=symbol
    if not (len(df1)==0):
        #查到了
        if lang == 'Chinese':
            name=df1['CNAME'].values[0]
        else:
            name=df1['ENAME'].values[0]
    else:
        #未查到
        #若为A股，直接取股票名称
        if suffix in SUFFIX_LIST_CN:
            import akshare as ak
            
            try:
                allnames_cn=ak.stock_zh_a_spot_em()
                name=allnames_cn[allnames_cn['代码']==prefix]['名称'].values[0]
            except:
                pass
            
            #沪深京：股票代码-名称，有点慢
            try:
                allnames_cn=ak.stock_info_a_code_name()
                name=allnames_cn[allnames_cn['code']==prefix]['name'].values[0]
            except:
                pass
    
    #从结果中去掉某些子串
    droplist=["公司","集团","有限","责任","股份"]
    for w in droplist:
        name=name.replace(w,'')
    
    #如果名称中含有"指数"字样，则去掉"(A股)"\"(港股)"\"(美股)"
    droplist2=["(A股)","(港股)","(美股)"]
    if "指数" in name:
        for w in droplist2:
            name=name.replace(w,'')
    
    return name

if __name__=='__main__':
    get_names('00700.HK')
    get_names('0700.HK')
#==============================================================================
def str_replace(str1):
    """
    删除给定字符串中的子串
    """
    replist=['Ltd.','Ltd','Co.','LTD.','CO.',' CO','LTD','Inc.','INC.', \
             'CORPORATION','Corporation','LIMITED','Limited','Company', \
             'COMPANY','(GROUP)','Corp.','CORP','GROUP','Group']
    
    for rc in replist:
        str2=str1.replace(rc, '')
        str1=str2
    
    twlist=[' ',',','，']    
    for tw in twlist:
        str2 = str2.strip(tw)
    
    return str2
    
#==============================================================================
def get_all_stock_names():
    """
    获得股票代码和名称：中国A股、港股、美股。需要定期更新
    """
    import akshare as ak
    import pandas as pd
    
    #上证A股
    df_ss=ak.stock_info_sh_name_code()
    df_ss.rename(columns={'COMPANY_ABBR':'CNAME','ENGLISH_ABBR':'ENAME','LISTING_DATE':'LISTING'},inplace=True)
    df_ss['SYMBOL']=df_ss['COMPANY_CODE']+'.SS'
    df_ss_1=df_ss[['SYMBOL','CNAME','ENAME','LISTING']]    
    
    #深证A股
    df_sz=ak.stock_info_sz_name_code(indicator="A股列表")
    df_sz['SYMBOL']=df_sz['A股代码']+'.SZ'
    df_sz.rename(columns={'A股简称':'CNAME','英文名称':'ENAME','A股上市日期':'LISTING'},inplace=True)
    df_sz_1=df_sz[['SYMBOL','CNAME','ENAME','LISTING']]    
    
    #美股
    df_us=ak.get_us_stock_name()
    df_us['LISTING']=' '
    df_us.rename(columns={'symbol':'SYMBOL','name':'ENAME','cname':'CNAME'},inplace=True)
    df_us_1=df_us[['SYMBOL','CNAME','ENAME','LISTING']] 
    
    #港股
    df_hk=ak.stock_hk_spot()
    df_hk['LISTING']=' '
    last4digits=lambda x:x[1:5]
    df_hk['symbol1']=df_hk['symbol'].apply(last4digits)
    df_hk['SYMBOL']=df_hk['symbol1']+'.HK'
    df_hk.rename(columns={'name':'CNAME','engname':'ENAME'},inplace=True)
    df_hk_1=df_hk[['SYMBOL','CNAME','ENAME','LISTING']] 
    
    #合成
    df=pd.concat([df_ss_1,df_sz_1,df_us_1,df_hk_1])
    df.sort_values(by=['SYMBOL'], ascending=True, inplace=True )
    df.reset_index(drop=True,inplace=True)
    
    rep=lambda x:str_replace(x)
    df['CNAME']=df['CNAME'].apply(rep)
    df['ENAME']=df['ENAME'].apply(rep)
    
    #保存:应保存在文件夹S:/siat/siat中，重新生成siat轮子
    df.to_pickle('stock_info.pickle')

    """
    #读出文件
    with open('stock_info.pickle','rb') as test:
        df = pickle.load(test)
    """
    
    return df
#==============================================================================
def securities_name(code):
    """
    功能：搜索证券代码的名称，先中文后英文
    """
    codename=code
    
    #搜索国内股票的曾用名
    import akshare as ak
    suffix=code[-3:]
    stock=code[:-3]
    if suffix in ['.SS','.SZ']:
        try:
            names = ak.stock_info_change_name(stock=stock)
            if not (names is None):
                #列表中最后一个为最新名称
                codename=names[-1]
                return codename
        except:
            pass
        
    #不是国内股票或中文名称未查到
    if not (suffix in ['.SS','.SZ']) or (codename==code):
        try:
            import yfinance as yf
            tp=yf.Ticker(code)
            dic=tp.info
            codename=dic["shortName"]  
                
            #若倒数第2位是空格，最后一位只有一个字母，则截取
            if codename[-2]==' ':
                codename=codename[:-2]
                
            #若最后几位在下表中，则截取
            sl1=['Inc.','CO LTD','CO LTD.','CO. LTD.']
            sl2=['Co.,Ltd','Co.,Ltd.','Co., Ltd','Limited']
            sl3=['CO','Corporation']
            suffixlist=sl1+sl2+sl3
            for sl in suffixlist:
                pos=codename.find(sl)
                if pos <= 0: continue
                else:
                    codename=codename[:pos-1]
                    #print(codename)
                    break 
        except:
            pass
        
        return codename

if __name__=='__main__':
    securities_name('000002.SZ')
    securities_name('002504.SZ')
    securities_name('002503.SZ')
    securities_name('XPEV')
    securities_name('IBM')
    securities_name('NIO')
    securities_name('600519.SS')
    securities_name('601519.SS')
    securities_name('MSFT')

#==============================================================================
#==============================================================================


#==============================================================================
def texttranslate(code):
    """
    翻译文字为中文或英文。
    输入：文字。输出：翻译成中文或英文
    """
    import pandas as pd
    codedict=pd.DataFrame([
            
        ['数据来源: 新浪/stooq,','Source: sina/stooq,'],['数据来源: 雅虎财经,','Source: Yahoo Finance,'],
        ["证券快照：","证券快照："],
        ["证券价格走势图：","证券价格走势图："],
        ["证券收益率波动损失风险走势图：","证券收益率波动损失风险走势图："],
        ["证券指标走势对比图：","证券指标走势对比图："],
        ["证券价格走势蜡烛图演示：","证券价格走势蜡烛图演示："],
        ["股票分红历史","Stock Dividend History"],
        ["股票:","Stock: "],["历史期间:","Period: "],
        ['序号','Seq'],['日期','Date'],['星期','Weekday'],['股息','Div amount/share'],
        ["股票分拆历史","Stock Split History"],
        ['分拆比例','Split Ratio'],
        ["公司基本信息","Company Profile"],
        ["公司高管信息","Company Senior Management"],["公司高管:","Senior Management:"],
        ["基本财务比率","Key Financial Ratios"],["基本财务比率TTM","Key Financial Ratios TTM"],
        ["财报主要项目","Financial Statement Overview"],
        ["基本市场比率","Key Market Ratios"],
        ["一般风险指数","General Risk Indicators"],
        ["(指数越小风险越低)","(Smaller value indicates lower risk)"],
        ["可持续发展风险","Risk of Sustainable Development"],
        ["(分数越小风险越低)","(Smaller score indicates lower risk)"],
        ['\b岁 (生于','years old(born @'],
        ['总薪酬','Total compensation'],["均值","average "],
        ["投资组合的可持续发展风险","投资组合的可持续发展风险"],
        ["投资组合:","投资组合:"],
        ["ESG评估分数:","ESG risk score:"],
        ["   EP分数(基于","   EP risk score(based on"],
        ["   CSR分数(基于","   CSR risk score(based on"],
        ["   CG分数(基于","   CG risk score(based on"],
        ["   ESG总评分数","   Total ESG risk score"],
        ["注：分数越高, 风险越高.","Note: the higher the score, the higher the risk."],
        
        [": 基于年(季)报的业绩历史对比",": Performance Comparison Based on Annual(Quarterly) Reports"],
        [": 基于年(季)报的业绩历史",": Performance History Based on Annual(Quarterly) Reports"],
        
        ["中国债券市场月发行量","中国债券市场月发行量"],
        ["数据来源：中国银行间市场交易商协会(NAFMII)，","数据来源：中国银行间市场交易商协会(NAFMII)，"],
        ["发行量","发行量"],["金额(亿元)","金额(亿元)"],
        ["中国银行间市场债券现券即时报价","中国银行间市场债券现券即时报价"],
        ["，前","，前"],["名）***","名）***"],
        ["中国债券市场月发行量","中国债券市场月发行量"],
        ["价格","价格"],["成交量","成交量"],
        
        ["按照收益率从高到低排序","按照收益率从高到低排序"],
        ["按照发行时间从早到晚排序","按照发行时间从早到晚排序"],
        ["按照发行时间从晚到早排序","按照发行时间从晚到早排序"],
        ["按照报价机构排序","按照报价机构排序"],
        ["按照涨跌幅从高到低排序","按照涨跌幅从高到低排序"],
        ["按照涨跌幅从低到高排序","按照涨跌幅从低到高排序"],
        ["按照交易时间排序","按照交易时间排序"],
        ["按照成交量从高到低排序","按照成交量从高到低排序"],
        ["按照成交量从低到高排序","按照成交量从低到高排序"],
        ['时间','时间'],['债券代码','债券代码'],
        
        ['债券名称','债券名称'],['成交价','成交价'],['涨跌(元)','涨跌(元)'],
        ['开盘价','开盘价'],['最高价','最高价'],['最低价','最低价'],
        ['买入价','买入价'],['卖出价','卖出价'],['收盘价','收盘价'],
        ["沪深交易所债券市场现券即时成交价（","沪深交易所债券市场现券即时成交价（"],
        
        ["数据来源：新浪财经，","数据来源：新浪财经，"],
        ['沪深债券收盘价历史行情：','沪深债券收盘价历史行情：'],
        ["按照代码从小到大排序","按照代码从小到大排序"],
        ["按照代码从大到小排序","按照代码从大到小排序"],
        ["沪深交易所可转债现券即时行情（","沪深交易所可转债现券即时行情（"],
        ['沪深市场可转债收盘价历史行情：','沪深市场可转债收盘价历史行情：'],
        ["政府债券列表","政府债券列表"],
        ['中国','中国'],['美国','美国'],['日本','日本'],['韩国','韩国'],
        ['泰国','泰国'],['越南','越南'],['印度','印度'],['德国','德国'],
        ['法国','法国'],['英国','英国'],['意大利','意大利'],['西班牙','西班牙'],
        ['俄罗斯','俄罗斯'],['加拿大','加拿大'],['澳大利亚','澳大利亚'],
        ['新西兰','新西兰'],['新加坡','新加坡'],['马来西亚','马来西亚'],
        
        ['全球政府债券收盘价历史行情：','全球政府债券收盘价历史行情：'],
        ["数据来源：英为财情，","数据来源：英为财情，"],
        ['到期收益率变化','到期收益率变化'],
        ['到期收益率%','到期收益率%'],
        ['债券价格','债券价格'],
        ["债券价格与到期收益率的关系","债券价格与到期收益率的关系"],
        ["债券价格","债券价格"],
        ["到期收益率及其变化幅度","到期收益率及其变化幅度"],
        ["债券面值","债券面值"],
        ["，票面利率","，票面利率"],
        ["每年付息","每年付息"],
        ["次，到期年数","次，到期年数"],
        ["，到期收益率","，到期收益率"],
        ['到期时间(年)','到期时间(年)'],
        ['债券价格变化','债券价格变化'],
        ["债券价格的变化与到期时间的关系","债券价格的变化与到期时间的关系"],
        ["债券价格的变化","债券价格的变化"],
        ["次，期限","次，期限"],
        ["年","年"],
        ["债券价格的变化速度","债券价格的变化速度"],
        
        ["债券到期时间与债券价格的变化速度","债券到期时间与债券价格的变化速度"],
        ["收益率下降导致的债券价格增加","收益率下降导致的债券价格增加"],
        ["收益率上升导致的债券价格下降","收益率上升导致的债券价格下降"],
        ["收益率上升导致的债券价格下降(两次翻折后)","收益率上升导致的债券价格下降(两次翻折后)"],
        ["到期收益率与债券价格变化的非对称性","到期收益率与债券价格变化的非对称性"],
        ["到期收益率及其变化幅度","到期收益率及其变化幅度"],
        ["数据来源：中债登/中国债券信息网，","数据来源：中债登/中国债券信息网，"],
        ['中国债券信息网','中国债券信息网'],
        ["中国债券价格指数走势","中国债券价格指数走势"],
        ["到期期限对债券转换因子的影响","到期期限对债券转换因子的影响"],
        ["名义券利率         :","名义券利率         :"],
        ["债券票面利率       :","债券票面利率       :"],
        ["每年付息次数       :","每年付息次数       :"],
        ["到下个付息日的天数 :","到下个付息日的天数 :"],
        ['债券到期期限*','债券到期期限*'],
        ['转换因子','转换因子'],
        
        ["*指下一付息日后剩余的付息次数","*指下一付息日后剩余的付息次数"],
        ['债券的转换因子','债券的转换因子'],
        ["到期期限对债券转换因子的影响","到期期限对债券转换因子的影响"],
        ['下一付息日后剩余的付息次数','下一付息日后剩余的付息次数'],
        ["【债券描述】名义券利率：","【债券描述】名义券利率："],
        [", 债券票面利率：",", 债券票面利率："],
        [', 每年付息次数：',', 每年付息次数：'],
        ["到下一付息日的天数：","到下一付息日的天数："],
        ["债券票息率对转换因子的影响","债券票息率对转换因子的影响"],
        ["名义券利率                 :","名义券利率                 :"],
        ["每年付息次数               :","每年付息次数               :"],
        ["到下个付息日的天数         :","到下个付息日的天数         :"],
        ["下个付息日后剩余的付息次数 :","下个付息日后剩余的付息次数 :"],
        ['债券票息率','债券票息率'],
        ["债券票息率对转换因子的影响","债券票息率对转换因子的影响"],
        ['票息率','票息率'],
        ["下一付息日后剩余的付息次数：","下一付息日后剩余的付息次数："],
        ["债券票息率与债券价格变化风险的关系","债券票息率与债券价格变化风险的关系"],
        ["票息率及其变化幅度","票息率及其变化幅度"],
        ["债券面值","债券面值"],
        
        ["，票面利率","，票面利率"],
        ["每年付息","每年付息"],
        ["次，期限","次，期限"],
        ["，到期收益率","，到期收益率"],
        
        ["======= 中国公募基金种类概况 =======","======= 中国公募基金种类概况 ======="],
        ["公募基金总数：","公募基金总数："],
        ["其中包括：","其中包括："],
        ["数据来源：东方财富/天天基金,","数据来源：东方财富/天天基金,"],
        ["\n===== 中国开放式基金排名：单位净值最高前十名 =====","\n===== 中国开放式基金排名：单位净值最高前十名 ====="],
        ["\n===== 中国开放式基金排名：累计净值最高前十名 =====","\n===== 中国开放式基金排名：累计净值最高前十名 ====="],
        ["\n===== 中国开放式基金排名：手续费最高前十名 =====","\n===== 中国开放式基金排名：手续费最高前十名 ====="],
        ["共找到披露净值信息的开放式基金数量:","共找到披露净值信息的开放式基金数量:"],
        ["基金类型:","基金类型:"],
        ["  净值日期:","  净值日期:"],
        ['单位净值','单位净值'],
        ['累计净值','累计净值'],
        ['净值','净值'],
        ["开放式基金的净值趋势：","开放式基金的净值趋势："],
        ['累计收益率%','累计收益率%'],
        ['收益率%','收益率%'],
        ["开放式基金的累计收益率趋势：","开放式基金的累计收益率趋势："],
        ['同类排名','同类排名'],
        ['同类排名百分比','同类排名百分比'],
        ["开放式基金的近三个月收益率排名趋势：","开放式基金的近三个月收益率排名趋势："],
        ['开放式基金总排名','开放式基金总排名'],
        ["\n======= 中国货币型基金排名：7日年化收益率最高前十名 =======","\n======= 中国货币型基金排名：7日年化收益率最高前十名 ======="],
        ["共找到披露收益率信息的货币型基金数量:","共找到披露收益率信息的货币型基金数量:"],
        ["收益率日期:","收益率日期:"],
        ['7日年化%','7日年化%'],
        ["货币型基金的7日年化收益率趋势：","货币型基金的7日年化收益率趋势："],
        ["\n===== 中国ETF基金排名：单位净值最高前十名 =====","\n===== 中国ETF基金排名：单位净值最高前十名 ====="],
        ["\n===== 中国ETF基金排名：累计净值最高前十名 =====","\n===== 中国ETF基金排名：累计净值最高前十名 ====="],
        ["\n===== 中国开放式基金排名：市价最高前十名 =====","\n===== 中国开放式基金排名：市价最高前十名 ====="],
        ["共找到披露净值信息的ETF基金数量:","共找到披露净值信息的ETF基金数量:"],
        ["基金类型:","基金类型:"],
        
        ["  净值日期:","  净值日期:"],
        ["  数据来源：东方财富/天天基金,","  数据来源：东方财富/天天基金,"],
        ['人民币元','人民币元'],
        ["ETF基金的净值趋势：","ETF基金的净值趋势："],
        ["\n===== 中国基金投资机构概况 =====","\n===== 中国基金投资机构概况 ====="],
        ["机构（会员）数量：","机构（会员）数量："],
        ["其中包括：","其中包括："],
        ["数据来源：中国证券投资基金业协会","数据来源：中国证券投资基金业协会"],
        ["\n===== 中国基金投资机构会员代表概况 =====","\n===== 中国基金投资机构会员代表概况 ====="],
        ["会员代表人数：","会员代表人数："],
        ["其中工作在：","其中工作在："],
        ["\n===== 中国私募基金管理人角色分布 =====","\n===== 中国私募基金管理人角色分布 ====="],
        ["地域：","地域："],
        ["法定代表人/执行合伙人数量：","法定代表人/执行合伙人数量："],
        ['\b, 占比全国','\b, 占比全国'],
        ["其中, 角色分布：","其中, 角色分布："],
        ["\n== 中国私募基金管理人地域分布概况 ==","\n== 中国私募基金管理人地域分布概况 =="],
        ["其中分布在：","其中分布在："],
        ["上述地区总计占比:","上述地区总计占比:"],
        ["\n== 中国私募基金管理人的产品与运营概况 ==","\n== 中国私募基金管理人的产品与运营概况 =="],
        ["产品数量：","产品数量："],
        ["产品的运营方式分布：","产品的运营方式分布："],
        ["产品的运营状态分布：","产品的运营状态分布："],
        ["\n===== 中国推出产品数量最多的私募基金管理人 =====","\n===== 中国推出产品数量最多的私募基金管理人 ====="],
        ["上述产品总计占比:","上述产品总计占比:"],
        ["\n===== 中国私募基金管理人的产品托管概况 =====","\n===== 中国私募基金管理人的产品托管概况 ====="],
        ["上述金融机构托管产品总计占比:","上述金融机构托管产品总计占比:"],
        ["\n===== 股票分红历史 =====","\n===== 股票分红历史 ====="],
        ["\n===== 股票分拆历史 =====","\n===== 股票分拆历史 ====="],
        ["\n===== 投资组合的可持续发展风险 =====","\n===== 投资组合的可持续发展风险 ====="],
        
        ["杜邦分析分解项目","DuPont Identity Items"],
        ["财报日期及类型","End date & report type"],
        ["【图示放大比例】","[Barchart multiplier]"],
        ["杜邦分析对比图","DuPont Identity Comparison"],
        ["杜邦分析分项数据表","DuPont Identity Item Datasheet"],
        ["企业横向对比: 实际税率","Company Comparison: Actual Tax Rate"],
        ["实际所得税率%","Actual Income Tax Rate%"],
        ["杜邦分析分项数据表","DuPont Identity Item Datasheet"],
        
        
        ], columns=['code','codename'])

    try:
        codename=codedict[codedict['code']==code]['codename'].values[0]
    except:
        #未查到翻译文字，返回原文
        codename=code
   
    return codename

if __name__=='__main__':
    code='数据来源：新浪/stooq，'
    print(texttranslate(code))

#==============================================================================


def tickertranslate(code):
    """
    套壳函数
    输入：证券代码。输出：证券名称
    """
    codename=codetranslate(code)
    return codename

if __name__=='__main__':
    code='GOOG'
    print(tickertranslate('000002.SZ'))
    print(tickertranslate('09988.HK'))

#==============================================================================
if __name__=='__main__':
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio)
    leading_blanks=2

def print_tickerlist_sharelist(tickerlist,sharelist,leading_blanks=2):
    """
    功能：纵向打印投资组合的成份股和持股比例
    输入：
    tickerlist：成份股列表
    sharelist：持股份额列表
    leading_blanks：打印前导空格数
    注意：放在本文件中的原因是需要使用函数codetranslate
    """
    #检查成份股与持仓比例个数是否一致
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

#==============================================================================
#==============================================================================
