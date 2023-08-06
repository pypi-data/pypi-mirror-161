# -*- coding: utf-8 -*-
"""
功能：一次性引入SIAT的所有模块
作者：王德宏，北京外国语大学国际商学院
版权：2022(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

# 资产流动性
from siat.assets_liquidity import *

# 贝塔系数调整方法
from siat.beta_adjustment import *
from siat.beta_adjustment_china import *

# 债券
from siat.bond import *

# 资本资产定价模型
from siat.capm_beta import *

# 数字货币
from siat.cryptocurrency import *

# 宏观经济
from siat.economy import *

# ESG
from siat.esg import *

# 资产定价-多因子模型
from siat.fama_french import *

# 财务报表：雅虎源
from siat.financial_statements import *

# 财务分析：雅虎源
from siat.financials import *

# 财务分析：中国
from siat.financials_china import *

# 财务分析：中国，资产负债结构分析
from siat.financials_china2 import *

# 中国的基金
from siat.fund_china import *

# 中国的期货（内盘与部分外盘）
from siat.future_china import *

# 中国的期权
from siat.option_china import *

# 资产的持有风险
from siat.holding_risk import *

# 投资组合理论
from siat.markowitz import *

# 期权定价
from siat.option_pricing import *

# 风险调整收益
from siat.risk_adjusted_return import *

# 风险评估
from siat.risk_evaluation import *

# 中国的行业分析
from siat.sector_china import *

# 获取证券价格-套壳
from siat.security_prices import *

# 股票分析
from siat.stock import *

# 中国的股票
from siat.stock_china import *

# 证券交易-套壳
from siat.transaction import *

# 持有资产风险-模型验证
from siat.var_model_validation import *

# 机器学习-课程案例
from siat.ml_cases import *
