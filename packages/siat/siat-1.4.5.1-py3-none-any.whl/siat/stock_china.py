# -*- coding: utf-8 -*-
"""
模块功能：借助机器学习学习方法，预测次日股票价格走势
模型：最近邻模型
算法：借助个股过去一百个交易日的资金净流入/净流出以及大盘走势变化，进行机器学习
注意：如果在当日未收盘时运行，预测的是当日个股收盘价的走势；若在收盘后运行则预测次日走势
作者：王德宏，北京外国语大学国际商学院
日期：2021-5-13
"""

import warnings; warnings.filterwarnings('ignore')
#==============================================================================
# 获得个股近一百个交易日的资金净流入数据
#==============================================================================

if __name__=='__main__':
    ticker='600519'

def get_money_flowin(ticker):
    """
    功能：抓取个股近一百个交易日的资金净流入情况，以及大盘指数的情况
    ticker：个股代码，不带后缀
    标准化方法：原始数据
    """
    import akshare as ak
    import pandas as pd
    
    #判断沪深市场
    l1=ticker[0]; market='sh'
    if l1 in ['0','2','3']: market='sz'
    #深市股票以0/2/3开头，沪市以6/9开头

    #获得个股资金流动明细
    try:
        df = ak.stock_individual_fund_flow(stock=ticker, market=market)
    except:
        print("#Error(predict_price_direction): stock code not found for",ticker)
        return

    df['ticker']=ticker
    df['date']=df['日期']
    #类型转换
    df['netFlowInAmount_main']=df['主力净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_small']=df['小单净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_mid']=df['中单净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_big']=df['大单净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_super']=df['超大单净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount']=df['netFlowInAmount_main']+df['netFlowInAmount_small']+ \
        df['netFlowInAmount_mid']+df['netFlowInAmount_big']+df['netFlowInAmount_super']

    df['netFlowInRatio%_main']=df['主力净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_small']=df['小单净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_mid']=df['中单净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_big']=df['大单净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_super']=df['超大单净流入-净占比'].apply(lambda x: float(x))
    
    #重要：删除有缺失值的记录，确保未收盘时能预测当天的收盘价涨跌方向
    df.dropna(inplace=True)

    df['Close']=df['收盘价'].apply(lambda x: float(x))
    df['Change%']=df['涨跌幅'].apply(lambda x: float(x))

    df['Date']=df['日期'].apply(lambda x: pd.to_datetime(x))  #不带时区的日期
    df.set_index('Date',inplace=True)
    
    #去掉不用的字段
    dfdroplist=['主力净流入-净额','小单净流入-净额','中单净流入-净额','大单净流入-净额', \
                '超大单净流入-净额','主力净流入-净占比','小单净流入-净占比', \
                '中单净流入-净占比','大单净流入-净占比','超大单净流入-净占比', \
                '收盘价','涨跌幅','日期']
    df.drop(labels=dfdroplist,axis=1,inplace=True)
    
    #获得大盘指数
    dpindex="sh000001"  #上证综合指数
    if market == 'sz': dpindex="sz399001"   #深圳成分指数
    dp=ak.stock_zh_index_daily(symbol=dpindex)
    dp['Date']=dp.index
    dp['Date']=dp['Date'].apply(lambda x: x.replace(tzinfo=None))   #去掉时区信息
    dp.set_index('Date',inplace=True)
    
    #去掉不用的字段
    dpdroplist=['open','high','low']
    dp.drop(labels=dpdroplist,axis=1,inplace=True)
    dp.rename(columns={'close':'dpClose','volume':'dpVolume'}, inplace = True)
    
    #合并大盘指数：索引日期均不带时区，否则出错
    dfp=pd.merge(df,dp,how='left',left_index=True,right_index=True)  
    
    """
    #取得标签/特征向量
    ydf=dfp[['Close','Change%']]
    X=dfp.drop(labels=['date','Close','Change%'],axis=1)
    
    scaler_X=preproc(X,preproctype=preproctype)
    scaler_dfp=pd.merge(scaler_X,ydf,how='left',left_index=True,right_index=True) 
    return scaler_dfp
    """
    
    return dfp

if __name__=='__main__':
    dfp=get_money_flowin('600519')

#==============================================================================
# 对特征数据进行预处理
#==============================================================================

def preprocess(X,preproctype='nop'):
    """
    功能：对特征数据X进行标准化预处理，不处理标签数据y
    df：原始数据
    preproctype：默认'nop'（不处理），
    还支持'0-1'（标准缩放法）、'min-max'（区间缩放法）和'log'（分别取对数）
    """
    typelist=['0-1','min-max','log','nop']
    if not (preproctype in typelist):
        print('  #Error(preproc): not supported for preprocess type',preproctype)
        print('  Supported preprocess types:',typelist)
        return None
    
    import pandas as pd
    collist=list(X)
    scaler_X=X.copy()
    #标准化——（0-1标准化）
    if preproctype == '0-1':
        for c in collist:
            value_min=scaler_X[c].min()
            value_max=scaler_X[c].max()
            scaler_X[c]=(scaler_X[c]-value_min)/(value_max-value_min)

    #标准化——（区间缩放法）
    if preproctype == 'min-max':
        for c in collist:
            value_mean=scaler_X[c].mean()
            value_std=scaler_X[c].std()
            scaler_X[c]=(scaler_X[c]-value_mean)/value_std

    #标准化——（对数法）
    if preproctype == 'log':
        for c in collist:
            scaler_X[c]=scaler_X[c].apply(lambda x: slog(x))

    #标准化——（不处理）
    if preproctype == 'nop': pass
        
    return scaler_X        

def slog(x):
    '''
    功能：对x取对数，正数直接取对数，负数先变为正数再取对数加负号，零不操作
    '''
    import numpy as np
    if x == np.NaN: return np.NaN
    if x == 0: return 0
    if x > 0: return np.log(x)
    if x < 0: return -np.log(-x)
    
if __name__=='__main__':
    scaler_X=preproc(X,preproctype='0-1')

#==============================================================================
# 构造适合机器学习的样本
#==============================================================================
if __name__=='__main__':
    ndays=1
    preCumTimes=1

def make_sample(dfp,ndays=1,preCumTimes=1):
    """
    功能：构造适合机器学习的样本
    ndays：预测未来几个交易日
    preCumTimes：使用过去几倍交易日的累计数据，
    使用过去交易日的实际天数=preCumTimes * ndays
    preproctype：对特征数据进行预处理的类型
    """    
    
    preDays=ndays * preCumTimes
    
    #构造过去一段时间资金净流入累加值
    dfp['netFlowInAmtCum_main']=dfp['netFlowInAmount_main'].rolling(window=preDays,min_periods=1).sum()
    dfp['netFlowInAmtCum_small']=dfp['netFlowInAmount_small'].rolling(window=preDays,min_periods=1).sum()
    dfp['netFlowInAmtCum_mid']=dfp['netFlowInAmount_mid'].rolling(window=preDays,min_periods=1).sum()
    dfp['netFlowInAmtCum_big']=dfp['netFlowInAmount_big'].rolling(window=preDays,min_periods=1).sum()
    dfp['netFlowInAmtCum_super']=dfp['netFlowInAmount_super'].rolling(window=preDays,min_periods=1).sum()
    dfp['netFlowInAmtCum']=dfp['netFlowInAmount'].rolling(window=preDays,min_periods=1).sum()
    
    #构造过去一段时间资金净流入比例均值
    dfp['netFlowInRatioAvg%_main']=dfp['netFlowInRatio%_main'].rolling(window=preDays,min_periods=1).mean()    
    dfp['netFlowInRatioAvg%_small']=dfp['netFlowInRatio%_small'].rolling(window=preDays,min_periods=1).mean() 
    dfp['netFlowInRatioAvg%_mid']=dfp['netFlowInRatio%_mid'].rolling(window=preDays,min_periods=1).mean() 
    dfp['netFlowInRatioAvg%_big']=dfp['netFlowInRatio%_big'].rolling(window=preDays,min_periods=1).mean() 
    dfp['netFlowInRatioAvg%_super']=dfp['netFlowInRatio%_super'].rolling(window=preDays,min_periods=1).mean() 

    #构造过去一段时间大盘指数的均值和标准差
    dfp['dpCloseAvg']=dfp['dpClose'].rolling(window=preDays,min_periods=1).mean()
    #dfp['dpCloseStd']=dfp['dpClose'].rolling(window=preDays,min_periods=1).std()
    dfp['dpVolumeAvg']=dfp['dpVolume'].rolling(window=preDays,min_periods=1).mean()
    #dfp['dpVolumeStd']=dfp['dpVolume'].rolling(window=preDays,min_periods=1).std()   
    
    #重要：去掉前几行，此处位置敏感
    dfp.dropna(inplace=True)
    
    #添加未来更多天的股价信息
    ylist=[]
    for nd in list(range(1,ndays+1)):
        dfp['Close_next'+str(nd)]=dfp['Close'].shift(-nd)
        ylist=ylist+['Close_next'+str(nd)]
        dfp['Change%_next'+str(nd)]=dfp['Change%'].shift(-nd)
        ylist=ylist+['Change%_next'+str(nd)]
    
    X = dfp[[
         'netFlowInAmount_main','netFlowInAmount_small','netFlowInAmount_mid', \
         'netFlowInAmount_big','netFlowInAmount_super','netFlowInAmount', \
         
         'netFlowInAmtCum_main','netFlowInAmtCum_small','netFlowInAmtCum_mid', \
         'netFlowInAmtCum_big','netFlowInAmtCum_super','netFlowInAmtCum', \
         
         'netFlowInRatio%_main','netFlowInRatio%_small','netFlowInRatio%_mid', \
         'netFlowInRatio%_big','netFlowInRatio%_super',
         
         'netFlowInRatioAvg%_main','netFlowInRatioAvg%_small','netFlowInRatioAvg%_mid', \
         'netFlowInRatioAvg%_big','netFlowInRatioAvg%_super',
         
         'dpClose','dpCloseAvg','dpVolume','dpVolumeAvg']]
    
    ydf = dfp[ylist]
    
    return X,ydf

#==============================================================================
# 训练模型，获得最优模型参数，进行预测
#==============================================================================
if __name__=='__main__':
    noday=1
    y='Close'   
    diff=0.03
    min_score=0.6
    votes=100
    max_neighbours=10
    max_RS=10
    printout=True

def train_predict_knn(X,ydf,noday=1,y='Close', \
    diff=0.03,min_score=0.6,votes=100,max_neighbours=10,max_RS=10,printout=True):
    """
    功能：训练模型，选择最优参数，预测
    X：特征矩阵
    ydf：标签矩阵
    nodays：预测未来第几天
    y：标签，默认'Close'为股价，'Change%'为涨跌幅，'Direction'为涨跌方向
    """
    ylist=['Close','Change%','Direction']
    if not (y in ylist):
        print("  #Error(train_predict_knn):",y,"not within",ylist)
    clflist=['Direction']
    reglist=['Close','Change%']
    
    #拆分训练集和测试集
    from sklearn.model_selection import train_test_split   
    XX=X[: -noday]
    import numpy as np
    if noday == 1:
        X_new=np.arrary(X[-1:])
    else:
        X_new=np.arrary(X[-noday:-noday+1])
    
    yydf=ydf[: -noday]
    yy=yydf[y+'_next'+str(noday)]
    
    
    if y in clflist:
        from sklearn.neighbors import KNeighborsClassifier
    if y in reglist:
        from sklearn.neighbors import KNeighborsRegressor

    #寻找最优模型参数
    nlist=list(range(1,max_neighbours+1))
    n_num=len(nlist)
    wlist=['uniform','distance']
    mlist1=['braycurtis','canberra','correlation','dice','hamming','jaccard']
    mlist2=['kulsinski','matching','rogerstanimoto','russellrao']
    mlist3=['sokalmichener','sokalsneath','sqeuclidean','yule','chebyshev']
    mlist4=['cityblock','euclidean','minkowski','cosine']
    mlist=mlist1+mlist2+mlist3+mlist4
    rslist=list(range(0,max_RS+1))
    results=pd.DataFrame(columns=('spread','train_score','test_score', \
                                  'neighbours','weight','metric','random','pred'))
    print('\n  Searching for best parameters of knn model in',ndays,'trading days ...')
    print('    Progress: 0%, ',end='')
    for n in nlist:
        for w in wlist:
            for m in mlist:
                for rs in rslist:    
                    X_train,X_test,y_train,y_test=train_test_split(XX,yy,random_state=rs)
                    
                    if y in clflist:
                        knn1=KNeighborsClassifier(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                    if y in reglist:
                        knn1=KNeighborsClassifier(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                    knn1.fit(X_train, y_train)
                    train_score=round(knn1.score(X_train, y_train),3)
                    test_score=round(knn1.score(X_test, y_test),3)
                    
                    prediction=knn1.predict(X_new)[0]
                    spread=abs(round(train_score-test_score,3))
                    
                    row=pd.Series({'spread':spread,'train_score':train_score, \
                                   'test_score':test_score,'neighbours':n, \
                                   'weight':w,'metric':m,'random':rs,'pred':prediction})
                    results=results.append(row,ignore_index=True)
        print(int(n/n_num*100),'\b%, ',end='')
    print('done.') 
    
    #去掉严重过拟合的结果           
    r0=results[results['train_score'] < 1]
    #去掉训练集、测试集分数不过半的模型    
    r0=r0[r0['train_score'] > min_score]
    r0=r0[r0['test_score'] > min_score]
    #去掉泛化效果差的结果
    r0=r0[r0['spread'] < diff]  #限定泛化差距
    #优先查看泛化效果最优的结果
    r1=r0.sort_values(by=['spread','test_score'],ascending=[True,False])        
    #优先查看测试分数最高的结果
    r2=r0.sort_values(by=['test_score','spread'],ascending=[False,True])

    if votes > len(r2): votes=len(r2)
    r2head=r2.head(votes)    
    
#==============================================================================
# 训练，获得最优模型参数
#==============================================================================
if __name__=='__main__':
    ndays=1
    max_neighbors=10
    max_p=6
    cv=5
    rs=0

def training_knn_clf(scaler_X,ydf,ndays=1,max_neighbors=10,max_p=6,cv=5,rs=0):
    '''
    功能：对(X,y)
    scaler_X: 特征矩阵
    y：标签矩阵
    '''
    
    #获得分类变量y
    ydf['nextChange%']=ydf['Change%'].shift(-ndays)
    ydf['nextDirection']=ydf['nextChange%'].apply(lambda x: 'Higher' if x>0 else 'Lower')
    y=ydf['nextDirection']
    
    #拆分训练集和测试集
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(scaler_X,y,random_state=rs)
    
    #定义网格搜索参数
    param_grid = [
            {  # 遍历：非加权距离
             'weights': ['uniform'], # 参数取值范围
             'n_neighbors': [i for i in range(1,max_neighbors+1)]  # 使用其他方式如np.arange()也可以
             # 这里没有p参数
             },
            {  # 遍历：加权距离
             'weights': ['distance'],
             'n_neighbors': [i for i in range(1,max_neighbors+1)],
             'p': [i for i in range(1,max_p)]
             } ]
 
    #训练训练集
    from sklearn.neighbors import KNeighborsClassifier
    knn = KNeighborsClassifier()  # 默认参数，创建空分类器

    from sklearn.model_selection import GridSearchCV  # CV，使用交叉验证方式获得模型正确率
    grid_search = GridSearchCV(knn, param_grid,scoring='accuracy',cv=cv)  # 网格搜索参数

    #grid_search.fit(X_train, y_train)  
    grid_search.fit(X,y)  
    best_knn=grid_search.best_estimator_
    train_score=best_knn.score(X_train, y_train)
    test_score=best_knn.score(X_test, y_test)
    
    best_params=grid_search.best_params_
    """
    k=best_params['n_neighbors']
    p=best_params['p']
    w=best_params['weights']
    """
    return best_params,train_score,test_score

    
#==============================================================================
# Forecasting stock price directions by money flow in/out, using knn
#==============================================================================
if __name__=='__main__':
    ticker='600519'
    ndays=1
    market='sh'
    diff=0.03
    votes=100
    max_neighbours=10
    max_RS=10

def price_direction_knn(ticker,df,ndays=1,diff=0.03,min_score=0.6,votes=100,max_neighbours=10,max_RS=10,printout=True):

    """
    功能：基于个股资金流动预测次日股票涨跌方向，涨或跌
    ticker：股票代码，无后缀
    df：个股资金净流入
    dp：大盘信息
    ndays：预测几天后的股价涨跌方向，默认1天
    market：sh-沪市，sz-深市
    diff：泛化精度，越小越好，默认0.03
    votes：软表决票数，默认100
    max_neighbours：最大邻居个数
    max_RS：最大随机数种子
    """
    import pandas as pd
    
    #构造标签
    df['nextClose']=df['Close'].shift(-ndays)
    df['nextChange%']=df['Change%'].shift(-ndays)
    df['nextDirection']=df['nextChange%'].apply(lambda x: 1 if float(x) > 0 else -1)
    
    #构造特征
    df['netFlowInChg_main']=df['netFlowInAmount_main'] - df['netFlowInAmount_main'].shift(-ndays)
    df['netFlowInChg_small']=df['netFlowInAmount_small'] - df['netFlowInAmount_small'].shift(-ndays)
    df['netFlowInChg_mid']=df['netFlowInAmount_mid'] - df['netFlowInAmount_mid'].shift(-ndays)
    df['netFlowInChg_big']=df['netFlowInAmount_big'] - df['netFlowInAmount_big'].shift(-ndays)
    df['netFlowInChg_super']=df['netFlowInAmount_super'] - df['netFlowInAmount_super'].shift(-ndays)
    df['netFlowInChg']=df['netFlowInAmount'] - df['netFlowInAmount'].shift(-ndays)
    
    df['netFlowInRatio%Chg_main']=df['netFlowInRatio%_main'] - df['netFlowInRatio%_main'].shift(-ndays)
    df['netFlowInRatio%Chg_small']=df['netFlowInRatio%_small'] - df['netFlowInRatio%_small'].shift(-ndays)
    df['netFlowInRatio%Chg_mid']=df['netFlowInRatio%_mid'] - df['netFlowInRatio%_mid'].shift(-ndays)
    df['netFlowInRatio%Chg_big']=df['netFlowInRatio%_big'] - df['netFlowInRatio%_big'].shift(-ndays)
    df['netFlowInRatio%Chg_super']=df['netFlowInRatio%_super'] - df['netFlowInRatio%_super'].shift(-ndays)

    df['dpCloseChg']=df['dpClose'] - df['dpClose'].shift(-ndays)
    df['dpVolumeChg']=df['dpVolume'] - df['dpVolume'].shift(-ndays)

    df2=df[['date','netFlowInChg_main',
       'netFlowInChg_small','netFlowInChg_mid','netFlowInChg_big', \
       'netFlowInChg_super','netFlowInChg','netFlowInRatio%Chg_main','netFlowInRatio%Chg_small', \
       'netFlowInRatio%Chg_mid','netFlowInRatio%Chg_big','netFlowInRatio%Chg_super', \
       'Close','Change%','dpCloseChg','dpVolumeChg','nextClose','nextChange%','nextDirection']]

    #记录最新指标，用于预测次日涨跌
    x_last=df2.copy().tail(1)
    today=x_last['date'].values[0]
    today_close=x_last['Close'].values[0]
    x_last.drop(labels=['date','nextClose', 'nextChange%', 'nextDirection'],axis=1,inplace=True)
    X_new = x_last.head(1).values

    #建立样本：特征序列
    df2.dropna(inplace=True)
    X=df2.drop(labels=['date','nextClose', 'nextChange%', 'nextDirection'],axis=1)

    #建立样本：标签序列
    y1=df2['nextDirection'] #二分类
    #y2=df2['nextChange%']   #回归
    #y3=df2['nextClose']     #回归

    #拆分训练集和测试集：y1
    from sklearn.model_selection import train_test_split
    #引入k近邻分类模型：
    from sklearn.neighbors import KNeighborsClassifier

    #寻找最优模型参数
    nlist=list(range(1,max_neighbours+1))
    n_num=len(nlist)
    wlist=['uniform','distance']
    mlist1=['braycurtis','canberra','correlation','dice','hamming','jaccard']
    mlist2=['kulsinski','matching','rogerstanimoto','russellrao']
    mlist3=['sokalmichener','sokalsneath','sqeuclidean','yule','chebyshev']
    mlist4=['cityblock','euclidean','minkowski','cosine']
    mlist=mlist1+mlist2+mlist3+mlist4
    rslist=list(range(0,max_RS+1))
    results=pd.DataFrame(columns=('spread','train_score','test_score', \
                                  'neighbours','weight','metric','random','pred'))
    print('\nSearching for best parameters of knn model in',ndays,'trading days ...')
    print('  Progress: 0%, ',end='')
    for n in nlist:
        for w in wlist:
            for m in mlist:
                for rs in rslist:    
                    knn1=KNeighborsClassifier(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                    X_train,X_test,y_train,y_test=train_test_split(X,y1,random_state=rs)
                    knn1.fit(X_train, y_train)
                    train_score=round(knn1.score(X_train, y_train),3)
                    test_score=round(knn1.score(X_test, y_test),3)
                    prediction=knn1.predict(X_new)[0]
                    spread=abs(round(train_score-test_score,3))
                    
                    row=pd.Series({'spread':spread,'train_score':train_score, \
                                   'test_score':test_score,'neighbours':n, \
                                   'weight':w,'metric':m,'random':rs,'pred':prediction})
                    results=results.append(row,ignore_index=True)
        print(int(n/n_num*100),'\b%, ',end='')
    print('done.') 
    
    #去掉严重过拟合的结果           
    r0=results[results['train_score'] < 1]
    #去掉训练集、测试集分数不过半的模型    
    r0=r0[r0['train_score'] > min_score]
    r0=r0[r0['test_score'] > min_score]
    #去掉泛化效果差的结果
    r0=r0[r0['spread'] < diff]  #限定泛化差距
    #优先查看泛化效果最优的结果
    r1=r0.sort_values(by=['spread','test_score'],ascending=[True,False])        
    #优先查看测试分数最高的结果
    r2=r0.sort_values(by=['test_score','spread'],ascending=[False,True])

    if votes > len(r2): votes=len(r2)
    r2head=r2.head(votes)
    
    zhang=len(r2head[r2head['pred']==1])
    die=len(r2head[r2head['pred']==-1])
    
    decision='+'
    if zhang >= die * 2.0: decision='2+'
    if zhang >= die * 3.0: decision='3+'
    
    if die > zhang: decision='-'
    if die >= zhang * 2.0: decision='2-'
    if die >= zhang * 3.0: decision='3-'
    
    if abs(zhang-die)/((zhang+die)/2) < 0.05: decision='?'

    if not printout: return decision,today_close,today

    print("  Model poll for stock price after "+str(ndays)+" trading days: Higer("+str(zhang)+'), Lower('+str(die)+')')
    print("Last close price: "+ticker+', '+str(today_close)+', '+str(today))
    print("Prediction for stock price after "+str(ndays)+" trading day: "+decision)
    return decision,today_close,today

if __name__=='__main__':
    df=price_direction_knn('600519',ndays=1,max_neighbours=5,max_RS=2)
    
#==============================================================================
if __name__=='__main__':
    ticker='600519'
    ndays=1
    market='sh'
    diff=0.03
    votes=100
    max_neighbours=3
    max_RS=2

def forecast_direction_knn(ticker,ndays=1,diff=0.03,min_score=0.6,votes=100,max_neighbours=10,max_RS=10,preproctype='0-1'):

    """
    功能：基于个股资金流动预测未来股票涨跌方向，涨或跌
    ticker：股票代码，无后缀
    ndays：预测几天后的股价涨跌方向，默认1天
    market：sh-沪市，sz-深市
    diff：泛化精度，越小越好，默认0.03
    votes：软表决票数，默认最大100
    max_neighbours：最大邻居个数，默认10个
    max_RS：最大随机数种子，默认最大为10
    """
    print("\nStart forecasting, it may take great time, please wait ...")
    
    #抓取个股资金净流入情况df和大盘指数情况dp
    df0,X,ydf=get_money_flowin(ticker)
    scaler_X=preproc(X,preproctype=preproctype)
    
    #测试用
    df=df0.copy()
    
    #预测未来股价涨跌
    decisionlist=[]
    for nd in list(range(1,ndays+1)):
        decision,today_close,today=price_direction_knn(ticker,df,ndays=nd, \
            diff=diff,min_score=min_score,votes=votes,max_neighbours=max_neighbours,max_RS=max_RS)
        decisionlist=decisionlist+[decision]

    print("\nStock information:",ticker,today_close,today)
    print("Forecasting stock prices in next",ndays,"trading days: ",end='')
    for i in decisionlist:
        print(i,'\b ',end='')
    print('\b.')
    
    return

if __name__=='__main__':
    df=forecast_direction_knn('600519',ndays=1,max_neighbours=5,max_RS=2)

#==============================================================================
# Forecasting stock prices by money flow in/out, using knn
#==============================================================================

if __name__=='__main__':
    ticker='600519'
    ndays=1
    market='sh'
    diff=0.03
    votes=100
    max_neighbours=10
    max_RS=10

def price_price_knn(ticker,df,ndays=1,diff=0.03,min_score=0.6,votes=100,max_neighbours=10,max_RS=10,printout=True):

    """
    功能：基于个股资金流动预测次日股票价格
    ticker：股票代码，无后缀
    df：个股资金净流入信息
    dp：大盘信息
    ndays：预测几天后的股价涨跌方向，默认1天
    market：sh-沪市，sz-深市
    diff：泛化精度，越小越好，默认0.03
    votes：软表决均值，默认100
    max_neighbours：最大邻居个数
    max_RS：最大随机数种子
    """
    import pandas as pd
    
    #构造标签
    df['nextClose']=df['Close'].shift(-ndays)
    df['nextChange%']=df['Change%'].shift(-ndays)
    df['nextDirection']=df['nextChange%'].apply(lambda x: 1 if float(x) > 0 else -1)
    
    #构造特征
    df['netFlowInChg_main']=df['netFlowInAmount_main']/(df['netFlowInAmount_main'].shift(ndays))
    df['netFlowInChg_small']=df['netFlowInAmount_small']/(df['netFlowInAmount_small'].shift(ndays))
    df['netFlowInChg_mid']=df['netFlowInAmount_mid']/(df['netFlowInAmount_mid'].shift(ndays))
    df['netFlowInChg_big']=df['netFlowInAmount_big']/(df['netFlowInAmount_big'].shift(ndays))
    df['netFlowInChg_super']=df['netFlowInAmount_super']/(df['netFlowInAmount_super'].shift(ndays))
    df['netFlowInChg']=df['netFlowInAmount']/(df['netFlowInAmount'].shift(ndays))

    df['dpCloseChg']=df['dpClose']/(df['dpClose'].shift(ndays))
    df['dpVolumeChg']=df['dpVolume']/(df['dpVolume'].shift(ndays))

    df2=df[['date','netFlowInChg_main',
       'netFlowInChg_small','netFlowInChg_mid','netFlowInChg_big', \
       'netFlowInChg_super','netFlowInChg','netFlowInRatio%_main','netFlowInRatio%_small', \
       'netFlowInRatio%_mid','netFlowInRatio%_big','netFlowInRatio%_super', \
       'Close','Change%','dpCloseChg','dpVolumeChg','nextClose','nextChange%','nextDirection']]

    #记录最新指标，用于预测次日涨跌
    x_last=df2.copy().tail(1)
    today=x_last['date'].values[0]
    today_close=x_last['Close'].values[0]
    x_last.drop(labels=['date','nextClose', 'nextChange%', 'nextDirection'],axis=1,inplace=True)
    X_new = x_last.head(1).values

    #建立样本：特征序列
    df2.dropna(inplace=True)
    X=df2.drop(labels=['date','nextClose', 'nextChange%', 'nextDirection'],axis=1)

    #建立样本：标签序列
    #y1=df2['nextDirection'] #二分类
    #y2=df2['nextChange%']   #回归
    y3=df2['nextClose']     #回归

    #拆分训练集和测试集：y1
    from sklearn.model_selection import train_test_split
    #引入k近邻分类模型：
    from sklearn.neighbors import KNeighborsRegressor

    #寻找最优模型参数
    nlist=list(range(1,max_neighbours+1))
    n_num=len(nlist)
    wlist=['uniform','distance']
    mlist1=['braycurtis','canberra','correlation','dice','hamming','jaccard']
    mlist2=['kulsinski','matching','rogerstanimoto','russellrao']
    mlist3=['sokalmichener','sokalsneath','sqeuclidean','chebyshev']
    mlist4=['cityblock','euclidean','minkowski','cosine']
    mlist=mlist1+mlist2+mlist3+mlist4
    rslist=list(range(0,max_RS+1))
    results=pd.DataFrame(columns=('spread','train_score','test_score', \
                                  'neighbours','weight','metric','random','pred'))
    print('\nSearching for best parameters of knn model in',ndays,'trading days ...')
    print('  Progress: 0%, ',end='')
    for n in nlist:
        for w in wlist:
            for m in mlist:
                for rs in rslist: 
                    try:
                        knn1=KNeighborsRegressor(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                        X_train,X_test,y_train,y_test=train_test_split(X,y3,random_state=rs)
                        knn1.fit(X_train, y_train)
                        train_score=round(knn1.score(X_train, y_train),3)
                        test_score=round(knn1.score(X_test, y_test),3)
                        prediction=knn1.predict(X_new)[0]
                    except:
                        print("  #Bug: n=",n,"w=",w,"m=",m,"rs=",rs)
                        break
                    spread=abs(round(train_score-test_score,3))
                    
                    row=pd.Series({'spread':spread,'train_score':train_score, \
                                   'test_score':test_score,'neighbours':n, \
                                   'weight':w,'metric':m,'random':rs,'pred':prediction})
                    results=results.append(row,ignore_index=True)
        print(int(n/n_num*100),'\b%, ',end='')
    print('done.') 
    
    #去掉严重过拟合的结果           
    r0=results[results['train_score'] < 1]
    #去掉训练集、测试集分数不过半的模型    
    r0=r0[r0['train_score'] > min_score]
    r0=r0[r0['test_score'] > min_score]
    #去掉泛化效果差的结果
    r0=r0[r0['spread'] < diff]  #限定泛化差距
    #优先查看泛化效果最优的结果
    r1=r0.sort_values(by=['spread','test_score'],ascending=[True,False])        
    #优先查看测试分数最高的结果
    r2=r0.sort_values(by=['test_score','spread'],ascending=[False,True])

    if votes > len(r2): votes=len(r2)
    r2head=r2.head(votes)
    
    
    #加权平均股价
    r2head['w_pred']=r2head['pred'] * r2head['test_score']
    w_pred_sum=r2head['w_pred'].sum()
    test_score_sum=r2head['test_score'].sum()
    decision=round(w_pred_sum / test_score_sum,2)
    decision_score=round(r2head['test_score'].mean(),2)
    
    """
    #股价中位数：偶尔出现奇怪的错误，未找到原因
    decision0=r2head['pred'].median()
    pos=list(r2head['pred']).index(decision0)
    decision_score0=list(r2head['test_score'])[pos]
    decision=round(decision0,2)
    decision_score=round(decision_score0,2)
    """
    import numpy as np
    if decision == np.nan: decision='?'
    
    if not printout: return decision,decision_score,today_close,today

    print("  Model poll for stock price after "+str(ndays)+" trading days:",decision)
    print("Last close price: "+ticker+', '+str(today_close)+', '+str(today))
    print("Prediction for stock price after "+str(ndays)+" trading day:",decision)
    return decision,decision_score,today_close,today

if __name__=='__main__':
    df=get_money_flowin(ticker)
    df=price_price_knn('600519',df,ndays=1,max_neighbours=3,max_RS=2)
    
#==============================================================================
if __name__=='__main__':
    ticker='600519'
    ndays=1
    market='sh'
    diff=0.03
    votes=100
    max_neighbours=3
    max_RS=2

def forecast_price_knn(ticker,ndays=1,diff=0.03,min_score=0.6,votes=100,max_neighbours=10,max_RS=10):

    """
    功能：基于个股资金流动预测未来股票价格
    ticker：股票代码，无后缀
    ndays：预测几天后的股价，默认1天
    market：sh-沪市，sz-深市
    diff：泛化精度，越小越好，默认0.03
    votes：软表决均值，默认最大100
    max_neighbours：最大邻居个数，默认10个
    max_RS：最大随机数种子，默认最大为10
    """
    print("\nStart forecasting, it may take great time, please wait ...")
    
    #抓取个股资金净流入情况df和大盘指数情况dp
    df0=get_money_flowin(ticker)
    
    #测试用
    df=df0.copy()
    
    #预测未来股价涨跌
    decisionlist=[]
    confidencelist=[]
    for nd in list(range(1,ndays+1)):
        decision,confidence,today_close,today=price_price_knn(ticker,df,ndays=nd, \
            diff=diff,min_score=min_score,votes=votes,max_neighbours=max_neighbours,max_RS=max_RS)
        decisionlist=decisionlist+[decision]
        confidencelist=confidencelist+[confidence]

    print("\nStock information:",ticker,today_close,today)
    print("Forecasting stock prices in next",ndays,"trading days: ",end='')
    for i in decisionlist:
        pos=decisionlist.index(i)
        conf=confidencelist[pos]
        if i == '?':
            print('?',end='')
        else:
            print(str(i)+'('+str(conf*100)+'%) ',end='')
    print('\b.')
    
    return

if __name__=='__main__':
    df=forecast_price_knn('600519',ndays=1,max_neighbours=5,max_RS=2)

#==============================================================================
#==============================================================================

#==============================================================================