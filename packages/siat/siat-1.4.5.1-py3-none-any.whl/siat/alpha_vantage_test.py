# -*- coding: utf-8 -*-
# 绝对引用指定目录中的模块
import sys
sys.path.insert(0,r'S:\siat\siat')


#========================================================================
from alpha_vantage.timeseries import TimeSeries
ts = TimeSeries(key='J4L80CM3ATCKNONG', output_format='pandas', indexing_type='date')
data, meta_data = ts.get_daily('GOOGL', outputsize='full')
data, meta_data = ts.get_daily('FCHI', outputsize='full')



#========================================================================

