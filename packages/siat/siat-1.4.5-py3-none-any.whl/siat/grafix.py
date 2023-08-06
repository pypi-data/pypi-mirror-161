# -*- coding: utf-8 -*-
"""
本模块功能：绘制折线图
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月16日
最新修订日期：2020年9月16日
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
from siat.translate import *
import pandas as pd
#==============================================================================
import matplotlib.pyplot as plt

#统一设定绘制的图片大小：数值为英寸，1英寸=100像素
plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=16
ylabel_txt_size=14
xlabel_txt_size=14
legend_txt_size=14

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=True
plt.rcParams['grid.color']='steelblue'
plt.rcParams['grid.linestyle']='dashed'
plt.rcParams['grid.linewidth']=0.5
plt.rcParams['axes.facecolor']='whitesmoke'


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
def plot_line(df0,colname,collabel,ylabeltxt,titletxt,footnote,datatag=False, \
              power=0,zeroline=False,resample_freq='H',loc='best', \
              date_range=False,date_freq=False,date_fmt='%Y-%m-%d'):
    """
    功能：绘制折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：数据表df，数据表中的列名colname，列名的标签collabel；y轴标签ylabeltxt；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    #空值判断
    if len(df0) ==0:
        print ("  #Warning(plot_line): no data to plot.")
        return
    
    #插值平滑
    try:
        df0x=df0[[colname]].astype('float')
        df=df_smooth_manual(df0x,resample_freq=resample_freq)
    except:
        df=df0
    
    #先绘制折线图
    """
    plt.plot(df.index,df[colname],'-',label=collabel, \
             linestyle='-',color='blue', linewidth=1, \
                 marker='o',markersize=2)
    """

    import matplotlib.dates as mdate
    date_start=df.index[0]
    date_end=df.index[-1]
    ax=plt.gca()       
    
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))

    plt.plot(df.index,df[colname],'-',label=collabel, \
             linestyle='-',color='blue', linewidth=2)
    #绘制数据标签
    if datatag:
        for x, y in zip(df.index, df[colname]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        
    
    #是否绘制水平线
    #if zeroline and (min(df[colname]) < 0):
    if zeroline:
        if type(zeroline) == bool:
            hline=0
        elif type(zeroline) in [int,float]:
            hline=zeroline
        else:
            hline=0
        plt.axhline(y=hline,ls=":",c="black",linewidth=1)
        
    #绘制趋势线
    #print("--Debug(plot_line): power=",power)
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df['id']=range(len(df))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df.id, df[colname], power)
            f = np.poly1d(parameter)
            plt.plot(df.index, f(df.id),"r--", label=trend_txt,linewidth=1)
        except: 
            print("  Warning(plot_line): failed to converge trend line.")
    
    plt.legend(loc=loc,fontsize=legend_txt_size)
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    #plt.xticks(rotation=45)
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size)
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    plt.close()
    return

if __name__ =="__main__":
    plot_line(df,'Close',"收盘价","价格","万科股票","数据来源：新浪/stooq",power=4)

#==============================================================================
if __name__ =="__main__":
    power=0
    datatag1=False
    datatag2=False
    yscalemax=5
    zeroline=False
    twinx=False
    yline=999
    xline=999
    resample_freq='H'

def plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=0,datatag1=False,datatag2=False,yscalemax=5, \
               zeroline=False,twinx=False,yline=999,xline=999, \
               resample_freq='H',loc1='best',loc2='best'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：默认绘制同轴折线图，若twinx=True则绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    #空值判断
    if len(df1) ==0:
        print ("  #Warning(plot_line2): no data to plot df1.")
    if len(df2) ==0:
        print ("  #Warning(plot_line2): no data to plot df2.")
    if (len(df1) ==0) and (len(df2) ==0):
        return
    
    if not twinx:            
        plot_line2_coaxial(df1,ticker1,colname1,label1, \
                           df2,ticker2,colname2,label2, \
                ylabeltxt,titletxt,footnote,power,datatag1,datatag2,zeroline, \
                yline,xline,resample_freq=resample_freq, \
                    loc1=loc1,loc2=loc2)
    else:
        plot_line2_twinx(df1,ticker1,colname1,label1, \
                         df2,ticker2,colname2,label2, \
                         titletxt,footnote,power,datatag1,datatag2, \
                         resample_freq=resample_freq, \
                             loc1=loc1,loc2=loc2)
    return


#==============================================================================
def plot2_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=0,datatag1=False,datatag2=False,yscalemax=5, \
               zeroline=False,twinx=False,yline=999,xline=999, \
               resample_freq='H',loc1='best',loc2='best', \
               date_range=False,date_freq=False,date_fmt='%Y-%m-%d'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：默认绘制同轴折线图，若twinx=True则绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    
    date_range：表示绘图横轴是否需要尽量绘制开始和结束日期
    date_freq：定义绘图横轴的日期间隔，False表示自动间隔，'1Y'表示以1年为单位间隔,
               '1M'表示间隔一个月，'3M'表示间隔3个月等
    date_fmt：定义绘图横轴日期的格式，'%Y-%m-%d'表示YYYY-mm-dd，'%Y-%m'表示YYYY-mm，
               '%Y'表示YYYY
    """
    #空值判断
    if len(df1) ==0:
        print ("  #Warning(plot_line2): no data to plot df1.")
    if len(df2) ==0:
        print ("  #Warning(plot_line2): no data to plot df2.")
    if (len(df1) ==0) and (len(df2) ==0):
        return
    
    if not twinx:            
        plot_line2_coaxial2(df1,ticker1,colname1,label1, \
                           df2,ticker2,colname2,label2, \
                ylabeltxt,titletxt,footnote,power,datatag1,datatag2,zeroline, \
                yline,xline,resample_freq=resample_freq, \
                loc1=loc1,loc2=loc2, \
                date_range=date_range,date_freq=date_freq,date_fmt=date_fmt)
    else:
        plot_line2_twinx2(df1,ticker1,colname1,label1, \
                         df2,ticker2,colname2,label2, \
                         titletxt,footnote,power,datatag1,datatag2, \
                         resample_freq=resample_freq, \
                         loc1=loc1,loc2=loc2, \
                         date_range=date_range,date_freq=date_freq,date_fmt=date_fmt)
    return


#==============================================================================


def plot_line2_coaxial(df01,ticker1,colname1,label1, \
                       df02,ticker2,colname2,label2, \
                    ylabeltxt,titletxt,footnote, \
                    power=0,datatag1=False,datatag2=False,zeroline=False, \
                    yline=999,xline=999,resample_freq='H', \
                        loc1='best',loc2='best'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制同轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """

    #插值平滑
    try:
        df01x=df01[[colname1]].astype('float')
        df1=df_smooth_manual(df01x,resample_freq=resample_freq)
    except:
        df1=df01
    try:
        df02x=df02[[colname2]].astype('float')
        df2=df_smooth_manual(df02x,resample_freq=resample_freq)
    except:
        df2=df02
    #证券1：先绘制折线图
    
    if ticker1 == '':
        label1txt=label1
    else:
        label1txt=codetranslate(ticker1)+'('+label1+')'    
    plt.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',linewidth=2)
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        

    #是否绘制水平0线
    if zeroline and ((min(df1[colname1]) < 0) or (min(df2[colname2]) < 0)):
        plt.axhline(y=0,ls=":",c="black",linewidth=1)

    #是否绘制水平线
    if yline != 999:
        plt.axhline(y=yline,ls=":",c="black",linewidth=1)        

    #是否绘制垂直线
    if xline != 999:
        plt.axvline(x=xline,ls=":",c="black",linewidth=1)   
    
    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'    
            
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df1['id']=range(len(df1))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df1.id, df1[colname1], power)
            f = np.poly1d(parameter)
            
            if ticker1 == '':
                label1txt=''
            else:
                label1txt=codetranslate(ticker1)+"("+trend_txt+")"            
                    
            plt.plot(df1.index, f(df1.id),"g--", label=label1txt,linewidth=1)
        except: pass
    
    #证券2：先绘制折线图
    if ticker2 == '':
        label2txt=label2
    else:
        label2txt=codetranslate(ticker2)+'('+label2+')'    
    plt.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',linewidth=1.5)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        
        
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'    
            
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df2['id']=range(len(df2))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df2.id, df2[colname2], power)
            f = np.poly1d(parameter)
            
            if ticker2 == '':
                label2txt=''
            else:
                label2txt=codetranslate(ticker2)+"("+trend_txt+")"            
                    
            plt.plot(df2.index, f(df2.id),"r--", label=label2txt,linewidth=1)
        except: pass
    
    # 同轴绘图时，loc1/loc2未用上！
    plt.legend(loc=loc1,fontsize=legend_txt_size)
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    #plt.xticks(rotation=45)
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size)
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    plt.close()
    return

if __name__ =="__main__":
    df1 = get_price('000002.SZ', '2020-1-1', '2020-3-16')
    df2 = get_price('600266.SS', '2020-1-1', '2020-3-16')
    ticker1='000002.SZ'; ticker2='600266.SS'
    colname1='Close'; colname2='Close'
    label1="收盘价"; label2="收盘价"
    ylabeltxt="价格"
    plot_line2_coaxial(df1,'000002.SZ','High','最高价', \
        df1,'000002.SZ','Low','最低价',"价格", \
        "证券价格走势对比图","数据来源：新浪/stooq")
    plot_line2_coaxial(df1,'000002.SZ','Open','开盘价', \
        df1,'000002.SZ','Close','收盘价',"价格", \
        "证券价格走势对比图","数据来源：新浪/stooq")

    plot_line2_coaxial(df2,'600266.SS','Open','开盘价', \
        df2,'600266.SS','Close','收盘价',"价格", \
        "证券价格走势对比图","数据来源：新浪/stooq")

#==============================================================================
def plot_line2_coaxial2(df01,ticker1,colname1,label1, \
                       df02,ticker2,colname2,label2, \
                       ylabeltxt,titletxt,footnote, \
                       power=0,datatag1=False,datatag2=False,zeroline=False, \
                       yline=999,xline=999,resample_freq='H', \
                       loc1='best',loc2='best', \
                       date_range=False,date_freq=False,date_fmt='%Y-%m-%d'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制同轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """

    #插值平滑
    try:
        df01x=df01[[colname1]].astype('float')
        df1=df_smooth_manual(df01x,resample_freq=resample_freq)
    except:
        df1=df01
    try:
        df02x=df02[[colname2]].astype('float')
        df2=df_smooth_manual(df02x,resample_freq=resample_freq)
    except:
        df2=df02
    #证券1：先绘制折线图
    
    if ticker1 == '':
        label1txt=label1
    else:
        label1txt=codetranslate(ticker1)+'('+label1+')'    

    import matplotlib.dates as mdate
    ax=plt.gca()    
    date_start=df1.index[0]
    date_end=df1.index[-1]
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))    

    plt.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',linewidth=2)
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        

    #是否绘制水平0线
    if zeroline and ((min(df1[colname1]) < 0) or (min(df2[colname2]) < 0)):
        plt.axhline(y=0,ls=":",c="black",linewidth=1)

    #是否绘制水平线
    if yline != 999:
        plt.axhline(y=yline,ls=":",c="black",linewidth=1)        

    #是否绘制垂直线
    if xline != 999:
        plt.axvline(x=xline,ls=":",c="black",linewidth=1)   
    
    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df1['id']=range(len(df1))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df1.id, df1[colname1], power)
            f = np.poly1d(parameter)
            
            if ticker1 == '':
                label1txt=''
            else:
                label1txt=codetranslate(ticker1)+"("+trend_txt+")"            
            plt.plot(df1.index, f(df1.id),"g--", label=label1txt,linewidth=1)
        except: pass
    
    #证券2：先绘制折线图
    if ticker2 == '':
        label2txt=label2
    else:
        label2txt=codetranslate(ticker2)+'('+label2+')'    

    date_start=df2.index[0]
    date_end=df2.index[-1]
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))

    plt.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',linewidth=1.5)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        
        
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df2['id']=range(len(df2))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df2.id, df2[colname2], power)
            f = np.poly1d(parameter)
            
            if ticker2 == '':
                label2txt=''
            else:
                label2txt=codetranslate(ticker2)+"("+trend_txt+")"            
            plt.plot(df2.index, f(df2.id),"r--", label=label2txt,linewidth=1)
        except: pass
    
    # 同轴绘图时，loc1/loc2未用上！
    plt.legend(loc=loc1,fontsize=legend_txt_size)
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    #plt.xticks(rotation=45)
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size)
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    plt.close()
    return

#==============================================================================
def plot_line2_twinx(df01,ticker1,colname1,label1, \
                     df02,ticker2,colname2,label2, \
                    titletxt,footnote,power=0,datatag1=False,datatag2=False, \
                    resample_freq='H',loc1='upper left',loc2='lower left'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """

    #插值平滑
    try:
        df01x=df01[[colname1]].astype('float')
        df1=df_smooth_manual(df01x,resample_freq=resample_freq)
    except:
        df1=df01
    try:
        df02x=df02[[colname2]].astype('float')
        df2=df_smooth_manual(df02x,resample_freq=resample_freq)
    except:
        df2=df02
        
    #证券1：绘制折线图，双坐标轴
    import matplotlib.dates as mdates
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    if ticker1 == '':
        label1txt=label1
    else:
        label1txt=codetranslate(ticker1)+'('+label1+')'
    ax.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',color='blue',linewidth=2)   
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            ax.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')

    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df1['id']=range(len(df1))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df1.id, df1[colname1], power)
        f = np.poly1d(parameter)

        if ticker1 == '':
            label1txt=''
        else:
            label1txt=codetranslate(ticker1)+"("+trend_txt+")"
        ax.plot(df1.index, f(df1.id),"r--", label=label1txt,linewidth=1)

    #绘证券2：建立第二y轴
    ax2 = ax.twinx()
    
    if ticker2 == '':
        label2txt=label2
    else:
        label2txt=codetranslate(ticker2)+'('+label2+')'
    ax2.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',color='orange',linewidth=1.5)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            ax2.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')
    
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df2['id']=range(len(df2))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df2.id, df2[colname2], power)
        f = np.poly1d(parameter)

        if ticker2 == '':
            label2txt=''
        else:
            label2txt=codetranslate(ticker2)+"("+trend_txt+")"
        ax2.plot(df2.index, f(df2.id),"c--", label=label2txt,linewidth=1)        
        
    ax.set_xlabel(footnote,fontsize=xlabel_txt_size)
    
    if ticker1 == '':
        label1txt=label1
    else:
        label1txt=label1+'('+codetranslate(ticker1)+')'
    ax.set_ylabel(label1txt,fontsize=ylabel_txt_size)
    ax.legend(loc=loc1,fontsize=legend_txt_size)
    
    if ticker2 == '':
        label2txt=label2
    else:
        label2txt=label2+'('+codetranslate(ticker2)+')'
    ax2.set_ylabel(label2txt,fontsize=ylabel_txt_size)
    ax2.legend(loc=loc2,fontsize=legend_txt_size)
    
    #自动优化x轴标签
    #格式化时间轴标注
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d')) 
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    
    return


if __name__ =="__main__":
    df1 = get_price('000002.SZ', '2020-1-1', '2020-3-16')
    df2 = get_price('600266.SS', '2020-1-1', '2020-3-16')
    ticker1='000002.SZ'; ticker2='600266.SS'
    colname1='Close'; colname2='Close'
    label1="收盘价"; label2="收盘价"
    ylabeltxt="价格"
    plot_line2_twinx(df1,'000002.SZ','Close','收盘价', \
        df2,'600266.SS','Close','收盘价', \
        "证券价格走势对比图","数据来源：新浪/stooq")

    plot_line2_twinx(df1,'000002.SZ','Close','收盘价', \
        df2,'600266.SS','Close','收盘价', \
        "证券价格走势对比图","数据来源：新浪/stooq",power=3)

#==============================================================================
def plot_line2_twinx2(df01,ticker1,colname1,label1, \
                     df02,ticker2,colname2,label2, \
                     titletxt,footnote,power=0,datatag1=False,datatag2=False, \
                     resample_freq='H',loc1='upper left',loc2='lower left', \
                     date_range=False,date_freq=False,date_fmt='%Y-%m-%d'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """

    #插值平滑
    try:
        df01x=df01[[colname1]].astype('float')
        df1=df_smooth_manual(df01x,resample_freq=resample_freq)
    except:
        df1=df01
    try:
        df02x=df02[[colname2]].astype('float')
        df2=df_smooth_manual(df02x,resample_freq=resample_freq)
    except:
        df2=df02
        
    #证券1：绘制折线图，双坐标轴
    import matplotlib.dates as mdate
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    if ticker1 == '':
        label1txt=label1
    else:
        label1txt=codetranslate(ticker1)+'('+label1+')'
        
    date_start=df1.index[0]
    date_end=df1.index[-1]
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))    
        
    ax.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',color='blue',linewidth=2)   
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            ax.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')

    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df1['id']=range(len(df1))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df1.id, df1[colname1], power)
        f = np.poly1d(parameter)

        if ticker1 == '':
            label1txt=''
        else:
            label1txt=codetranslate(ticker1)+"("+trend_txt+")"
        ax.plot(df1.index, f(df1.id),"r--", label=label1txt,linewidth=1)

    #绘证券2：建立第二y轴
    ax2 = ax.twinx()
    
    if ticker2 == '':
        label2txt=label2
    else:
        label2txt=codetranslate(ticker2)+'('+label2+')'
        
    date_start=df2.index[0]
    date_end=df2.index[-1]
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))        
        
    ax2.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',color='orange',linewidth=1.5)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            ax2.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')
    
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df2['id']=range(len(df2))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df2.id, df2[colname2], power)
        f = np.poly1d(parameter)

        if ticker2 == '':
            label2txt=''
        else:
            label2txt=codetranslate(ticker2)+"("+trend_txt+")"
        ax2.plot(df2.index, f(df2.id),"c--", label=label2txt,linewidth=1)        
        
    ax.set_xlabel(footnote,fontsize=xlabel_txt_size)
    
    if ticker1 == '':
        label1txt=label1
    else:
        label1txt=label1+'('+codetranslate(ticker1)+')'
    ax.set_ylabel(label1txt,fontsize=ylabel_txt_size)
    ax.legend(loc=loc1,fontsize=legend_txt_size)
    
    if ticker2 == '':
        label2txt=label2
    else:
        label2txt=label2+'('+codetranslate(ticker2)+')'
    ax2.set_ylabel(label2txt,fontsize=ylabel_txt_size)
    ax2.legend(loc=loc2,fontsize=legend_txt_size)
    
    #自动优化x轴标签
    #格式化时间轴标注
    #plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%y-%m-%d')) 
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    
    return

#==============================================================================
def draw_lines(df0,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=True,resample_freq='H',smooth=True):
    """
    函数功能：根据df的内容绘制折线图
    输入参数：
    df：数据框。有几个字段就绘制几条折现。必须索引，索引值将作为X轴标记点
    要求：df的索引为pandas的datetime日期型
    axhline_label: 水平辅助线标记。如果为空值则不绘制水平辅助线
    axhline_value: 水平辅助线的y轴位置
    y_label：y轴标记
    x_label：x轴标记
    title_txt：标题。如需多行，中间用\n分割
    
    输出：
    绘制折线图
    无返回数据
    注意：需要日期类型作为df索引
    """
    #空值判断
    if len(df0) ==0:
        print ("  #Warning(draw_lines): no data to plot.")
        return
    
    #插值平滑
    if smooth:
        try:
            df=df_smooth_manual(df0,resample_freq=resample_freq)
        except:
            df=df0
    else:
        df=df0
        
    #取得df字段名列表
    collist=df.columns.values.tolist()  
    
    #绘制折线图    
    for c in collist:
        plt.plot(df[c],label=c,linewidth=2)
        #为折线加数据标签
        if data_label==True:
            for a,b in zip(df.index,df[c]):
                plt.text(a,b+0.02,str(round(b,2)), \
                         ha='center',va='bottom',fontsize=7)
    
    #绘制水平辅助线
    if axhline_label !="":
        plt.axhline(y=axhline_value,label=axhline_label,color='black',linestyle=':',linewidth=2)  
    
    #坐标轴标记
    plt.ylabel(y_label,fontweight='bold',fontsize=ylabel_txt_size)
    if x_label != "":
        plt.xlabel(x_label,fontweight='bold',fontsize=xlabel_txt_size)
    #图示标题
    plt.title(title_txt,fontweight='bold',fontsize=title_txt_size)
    plt.xticks(rotation=30)
    plt.legend(loc='best',fontsize=legend_txt_size)
    plt.show()
    
    return    
    
if __name__=='__main__':
    title_txt="Stock Risk \nCAPM Beta Trends"
    draw_lines(df,"market line",1.0,"Beta coefficient","",title_txt)    

#==============================================================================
def draw_lines2(df0,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=False,resample_freq='6H',smooth=True, \
               date_range=False,date_freq=False,date_fmt='%Y-%m-%d'):
    """
    函数功能：根据df的内容绘制折线图
    输入参数：
    df：数据框。有几个字段就绘制几条折现。必须索引，索引值将作为X轴标记点
    要求：df的索引为pandas的datetime日期型
    axhline_label: 水平辅助线标记。如果为空值则不绘制水平辅助线
    axhline_value: 水平辅助线的y轴位置
    y_label：y轴标记
    x_label：x轴标记
    title_txt：标题。如需多行，中间用\n分割
    
    输出：
    绘制折线图
    无返回数据
    注意：需要日期类型作为df索引
    """
    #空值判断
    if len(df0) ==0:
        print ("  #Warning(draw_lines): no data to plot.")
        return
    
    #插值平滑
    if smooth:
        try:
            df=df_smooth_manual(df0,resample_freq=resample_freq)
        except:
            df=df0
    else:
        df=df0

    #定义横轴标签：显示完整开始、结束日期
    import matplotlib.dates as mdate
    ax=plt.gca()    
    date_start=df.index[0]
    date_end=df.index[-1]
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))    
        
    #取得df字段名列表
    collist=df.columns.values.tolist()  
    
    #绘制折线图    
    for c in collist:
        plt.plot(df[c],label=c,linewidth=2)
        #为折线加数据标签
        if data_label==True:
            for a,b in zip(df.index,df[c]):
                plt.text(a,b+0.02,str(round(b,2)), \
                         ha='center',va='bottom',fontsize=7)
    
    #绘制水平辅助线
    if axhline_label !="":
        plt.axhline(y=axhline_value,label=axhline_label,color='black',linestyle=':',linewidth=0.5)  
    
    #坐标轴标记
    plt.ylabel(y_label,fontweight='bold',fontsize=ylabel_txt_size)
    if x_label != "":
        plt.xlabel(x_label,fontweight='bold',fontsize=xlabel_txt_size)
    #图示标题
    plt.title(title_txt,fontweight='bold',fontsize=title_txt_size)
    plt.xticks(rotation=30)
    plt.legend(loc='best',fontsize=legend_txt_size)
    plt.show()
    
    return    

#==============================================================================
def plot_barh(df,colname,titletxt,footnote,datatag=True, \
              colors=['r','g','b','c','m','y','aquamarine','dodgerblue', \
              'deepskyblue','silver'],tag_offset=0.01,axisamp=1.3):
    """
    功能：绘制水平柱状图，并可标注数据标签。
    输入：数据集df；列名colname；标题titletxt；脚注footnote；
    是否绘制数据标签datatag，默认是；柱状图柱子色彩列表。
    输出：水平柱状图
    """
    #空值判断
    if len(df) ==0:
        print ("  #Warning(plot_barh): no data to plot.")
        return

    plt.barh(df.index,df[colname],align='center',color=colors,alpha=0.8)
    coltxt=ectranslate(colname)
    plt.xlabel(footnote,fontsize=xlabel_txt_size)
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    #xmin=int(min(df[colname]))
    xmin0=min(df[colname])
    if xmin0 > 0:
        xmin=xmin0*0.8
    else:
        xmin=xmin0*1.05
    #xmax=(int(max(df[colname]))+1)*1.1
    xmax0=max(df[colname])
    scale_max=abs((xmax0-xmin0)/xmax0)*axisamp  #经验值放大倍数
    xmax=xmax0*scale_max
    """
    if xmax0 > 0:
        xmax=xmax0*1.8
    else:
        xmax=xmax0*1.2
    """
    plt.xlim([xmin,xmax])
    
    tag_off=tag_offset * xmax
    for x,y in enumerate(list(df[colname])):
        #plt.text(y+0.1,x,'%s' % y,va='center')
        plt.text(y+tag_off,x,'%s' % y,va='center')

    """
    yticklist=list(df.index)
    yticknames=[]
    for yt in yticklist:
        ytname=codetranslate(yt)
        yticknames=yticknames+[ytname]
    """
    yticknames=list(df.index)
    plt.yticks(df.index,yticknames)

    plt.show(); plt.close()
    
    return

#==============================================================================
def plot_barh2(df,colname,titletxt,footnote):
    """
    功能：绘制水平柱状图，并在外侧标注数据标签。
    输入：数据集df；列名colname；标题titletxt；脚注footnote；
    输出：水平柱状图
    注意：在Spyder中可能工作不正常
    """
    #空值判断
    if len(df) ==0:
        print ("  #Warning(plot_barh2): no data to plot.")
        return

    import plotly_express as px
    
    fig=px.bar(
        df,
        y=df.index,
        x=df[colname],
        #color=df[colname],
        orientation='h',
        #title=titletxt,
        text=colname,
        labels={'key':'','value':footnote}
        )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        title={
            'text': titletxt,   # 标题名称
            'y':0.95,  # 位置，坐标轴的长度看做1
            'x':0.5,
            'xanchor': 'center',   # 相对位置
            'yanchor': 'top'})

    fig.show()
    
    return

#==============================================================================

#==============================================================================
#==============================================================================
def plot_2lines(df01,colname1,label1, \
                df02,colname2,label2, \
                ylabeltxt,titletxt,footnote,hline=0,vline=0,resample_freq='H', \
                date_range=False,date_freq=False,date_fmt='%Y-%m-%d'):
    """
    功能：绘制两个证券的折线图。如果hline=0不绘制水平虚线，vline=0不绘制垂直虚线
    假定：数据表有日期索引，且已经按照索引排序
    输入：
    证券1：数据表df1，列名1，列名标签1；
    证券2：数据表df2，列名2，列名标签2；
    标题titletxt，脚注footnote
    输出：绘制同轴折线图
    
    若date_range=True，尽量在横轴上标注日期的起止时间
    若date_freq不为False，可以为类似于'3m'或'1Y'等
    date_fmt可以为'%Y-%m-%d'或'%Y-%m'或'%Y'等
    
    返回值：无
    """
    #空值判断
    if len(df01) ==0:
        print ("  #Warning(plot_2lines): no data to plot df01.")
    if len(df02) ==0:
        print ("  #Warning(plot_2lines): no data to plot df02.")   
    if (len(df01) ==0) and (len(df02) ==0):
        return

    #插值平滑
    try:
        df01x=df01[[colname1]].astype('float')
        df1=df_smooth_manual(df01x,resample_freq=resample_freq)
    except:
        df1=df01
        
    try:
        df02x=df02[[colname2]].astype('float')        
        df2=df_smooth_manual(df02x,resample_freq=resample_freq)
    except:
        df2=df02
    
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    #证券1：先绘制折线图
    import matplotlib.dates as mdate
    date_start=df1.index[0]
    date_end=df1.index[-1]
    if date_range and not date_freq:
        ax=plt.gca()
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax=plt.gca()
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax=plt.gca()
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))
    
    plt.plot(df1.index,df1[colname1],label=label1,linestyle='-',linewidth=2)
    
    #证券2：先绘制折线图
    date_start=df2.index[0]
    date_end=df2.index[-1]
    if date_range and not date_freq:
        ax=plt.gca()
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax=plt.gca()
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax=plt.gca()
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))
        
    plt.plot(df2.index,df2[colname2],label=label2,linestyle='-.',linewidth=1.5)
    
    #是否绘制水平虚线
    if not (hline == 0):
        plt.axhline(y=hline,ls=":",c="black")
    #是否绘制垂直虚线
    if not (vline == 0):
        plt.axvline(x=vline,ls=":",c="black")
    
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size)
    plt.legend(loc='best',fontsize=legend_txt_size)
    plt.xticks(rotation=30)
    plt.show()
    
    return

if __name__ =="__main__":
    df1=bsm_call_maturity(42,40,[50,200],0.015,0.23,90,1.5)
    df2=bsm_put_maturity(42,40,[50,200],0.015,0.23,90,1.5)
    ticker1='A'; colname1='Option Price'; label1='A1'
    ticker2='B'; colname2='Option Price'; label2='B2'
    ylabeltxt='ylabel'; titletxt='title'; footnote='\n\n\n\n4lines'
    power=0; datatag1=False; datatag2=False; zeroline=False
    
#==============================================================================
def df_smooth(df):
    """
    功能：对df中的数值型样本进行插值，以便绘制的折线图相对平滑。
    要求：df的索引为pandas的datetime日期型
    注意1：如果样本数量较多，例如多于100个，平滑效果不明显。
    注意2：order阶数仅对'spline'和'polynomial'方法有效，其中'polynomial'方法的阶数只能为奇数。
    """
    
    #如果样本个数多于50个，其实没必要进行平滑
    if len(df) >= 50: return df
    
    #定义重采样频率
    """
    常用的采样频率：
    H: hourly, BH: business hour, T: minutely, S: secondly, B: business day, W: weekly, 
    SM: semi-month end, SMS: semi-month start, 
    BMS: business month start,BM: business month end,
    BQ: business quarter end, BQS: business quarter start,
    BA/BY: business year end, BAS/BYS: business year start.    
    
    例如：
    df2=df.resample('2D').sum()
    df2=df.resample('W').mean()
    """
    #将索引转换为Datetimeindex，不然resample会失败
    df['date']=pd.to_datetime(df.index)
    df.set_index('date',inplace=True)
    
    #重新采样
    rflag=False
    freqlist=['H','B','W','M','Q']
    for f in freqlist:
        try:
            #dfh=df.resample(f).ffill()
            dfh=df.resample(f)
        except:
            continue
        else:
            rflag=True
            break
    
    if not rflag: 
        #print('  #Warning(df_smooth): resampling failed for frequency',freqlist)
        dfh=df
    
    #插值
    methodlist=['pchip','nearest','cubic','quadratic','slinear','linear','zero','time','index', \
            'piecewise_polynomial','akima','from_derivatives','spline','polynomial']
    methodlist_order=['spline','polynomial']
    order=3
    for method in methodlist:
        if method in methodlist_order:
            try:
                dfm=dfh.interpolate(method=method,order=order)
            except:
                #print('  #Warning(df_smooth): interpolate failed for method',method,'with order',order)
                #若出错就原样返回
                return df
            else: break
        else:
            try:
                dfm=dfh.interpolate(method=method)
            except:
                #print('  #Warning(df_smooth): interpolate failed for method',method)
                return df
            else: break
    
    #成功返回经过重采样的df
    return dfm        
    
        
#==============================================================================
def df_smooth_manual(df,method='pchip',resample_freq='H',order=3):
    """
    功能：对df中的第一个数值列样本进行插值，以便绘制的折线图相对平滑。
    要求：df的索引为pandas的datetime日期型
    注意1：如果样本数量较多，例如多于100个，平滑效果不明显。
    注意2：order阶数仅对'spline'和'polynomial'方法有效，其中'polynomial'方法的阶数只能为奇数。
    注意3：pchip方法经常失败，改为cubic
    """
    
    #如果样本个数多于50个，没必要进行平滑
    if len(df) >= 50: return df
    
    #检查平滑方法是否支持
    methodlist=['quadratic','cubic','slinear','linear','zero','nearest','time','index', \
            'piecewise_polynomial','pchip','akima','from_derivatives','spline','polynomial']
    if not (method in methodlist): return df
    
    #定义重采样频率
    """
    常用的采样频率：
    H: hourly, BH: business hour, T: minutely, S: secondly, B: business day, W: weekly, 
    SM: semi-month end, SMS: semi-month start, 
    BMS: business month start,BM: business month end,
    BQ: business quarter end, BQS: business quarter start,
    BA/BY: business year end, BAS/BYS: business year start.    
    
    例如：
    df2=df.resample('2D').sum()
    df2=df.resample('W').mean()
    """
    #将索引转换为Datetimeindex，不然resample会失败
    try:
        df['date']=pd.to_datetime(df.index)
    except:
        return df
    df.set_index('date',inplace=True)    
    
    try:
        dfh=df.resample(resample_freq)
    except:
        print('  #Warning(df_smooth): resampling failed for frequency',resample_freq)
        return df
    
    #重新采样
    methodlist_o=['spline','polynomial']
    if method in methodlist_o:
        try:
            dfm=dfh.interpolate(method=method,order=order)
        except:
            print('  #Warning(df_smooth_manual): interpolate failed for method',method,'with order',order)
            #若出错就原样返回
            return df
        #成功返回经过重采样的df
        return dfm
    
    try:
        dfm=dfh.interpolate(method=method)
    except:
        print('  #Warning(df_smooth_manual): interpolate failed for method',method)
        print('   Possible reason: interpolating row must be int or float instead of string')
        """
        #改为cubic方法
        if not (method == 'cubic'):
            try:
                dfm=dfh.interpolate(method='cubic')
            except:
                print('  #Warning(df_smooth_manual): interpolate failed for method cubic')    
                return df
        else:
            return df
        """
        return df
    
    # check whether dfm becomes empty
    if len(dfm)==0:
        return df
    else:
        return dfm        
#==============================================================================
if __name__=='__main__':
    wid=5
    mu=0
    sd=1
    obs_num=100
    
def plot_norm(mu,sd,graph='pdf',obs_num=100):
    """
    绘制正态分布图形
    mu:均值
    sd:标准差
    graph:图形种类,pdf,cdf,ppf
    """
    if not (graph in ['pdf','cdf','ppf']):
        print("  #Warning(plot_norm): support pdf/cdf/ppf only")
        return
    
    #计算概率密度:连续分布用pdf,离散分布用pmf
    import scipy.stats as st
    import numpy as np
    
    if graph=='pdf':
        wid=4*sd+mu
        X=np.linspace(-wid,wid,obs_num)
        y_pdf=st.norm.pdf(X,mu,sd) 
    
    if graph=='cdf':
        wid=3*sd+mu
        X=np.linspace(-wid,wid,obs_num)        
        y_cdf=st.norm.cdf(X,mu,sd)
        
    if graph=='ppf':
        X=np.linspace(0,1,obs_num)
        y_ppf=st.norm.ppf(X,mu,sd)

    #绘图
    if graph=='pdf':
        plt.plot(X,y_pdf,c="red",label='pdf')
    if graph=='cdf':
        plt.plot(X,y_cdf,c="blue",label='cdf')
    if graph=='ppf':
        plt.plot(X,y_ppf,c="green",label='ppf')
    
    if graph=='pdf':
        wid1=5*sd+mu
        wid2=1*sd+mu
        plt.xticks(np.arange(-wid,wid1,wid2))
        plt.xlabel('分位点',fontsize=xlabel_txt_size) #x轴文本
        plt.yticks(np.arange(0,0.45,0.05))
        plt.ylabel('概率密度',fontsize=ylabel_txt_size) #y轴文本

    if graph=='cdf':
        wid1=3.5*sd+mu
        wid2=0.5*sd+mu        
        plt.xticks(np.arange(-wid,wid1,wid2))
        plt.xlabel('分位点',fontsize=xlabel_txt_size) #x轴文本
        plt.yticks(np.arange(0,1.1,0.1))
        plt.ylabel('累积概率密度',fontsize=ylabel_txt_size) #y轴文本

    if graph=='ppf':
        wid=2.5*sd+mu
        wid1=3*sd+mu
        wid2=0.5*sd+mu
        plt.yticks(np.arange(-wid,wid1,wid2))
        plt.ylabel('分位点',fontsize=ylabel_txt_size) #y轴文本
        plt.xticks(np.arange(0,1.1,0.1))
        plt.xlabel('累积概率密度',fontsize=xlabel_txt_size) #x轴文本        
        
    plt.title('正态分布示意图: $\mu$=%.1f, $\sigma$=%.1f'%(mu,sd),fontweight='bold',fontsize=title_txt_size) #标题
    plt.tight_layout()
    plt.grid() #网格
    plt.legend(loc='best',fontsize=legend_txt_size)
    plt.show() #显示图形
    
    return

if __name__=='__main__':
    plot_norm(4,mu,sd,graph='pdf')
    plot_norm(3,mu,sd,graph='cdf')
    plot_norm(3,mu,sd,graph='ppf')        
    
#==============================================================================    
    









