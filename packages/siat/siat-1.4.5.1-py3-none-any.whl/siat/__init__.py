# -*- coding: utf-8 -*-
"""
功能：一次性引入SIAT的所有模块
作者：王德宏，北京外国语大学国际商学院
版权：2021(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.allin import *
#==============================================================================
#同一命令行多个输出，主要用于Jupyter Notebook
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity='all'
#==============================================================================
