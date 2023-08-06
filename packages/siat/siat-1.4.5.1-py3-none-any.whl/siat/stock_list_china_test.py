# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 00:20:06 2020

@author: Peter
"""

#爬虫网址：https://my.oschina.net/akshare/blog/4341023

import akshare as ak

#股票列表-A股：沪深交易所
stock_info_a_code_name_df = ak.stock_info_a_code_name()

#股票列表-上证
stock_info_sh_a_df = ak.stock_info_sh_name_code(indicator="主板A股")

stock_info_sh_b_df = ak.stock_info_sh_name_code(indicator="主板B股")

stock_info_sh_kcb_df = ak.stock_info_sh_name_code(indicator="科创板")

#股票列表-深证
stock_info_sz_a_df = ak.stock_info_sz_name_code(indicator="A股列表")

stock_info_sz_b_df = ak.stock_info_sz_name_code(indicator="B股列表")

stock_info_sz_listed_df = ak.stock_info_sz_name_code(indicator="上市公司列表")

stock_info_sz_main_df = ak.stock_info_sz_name_code(indicator="主板")

stock_info_sz_smb_df = ak.stock_info_sz_name_code(indicator="中小企业板")

stock_info_sz_cyb_df = ak.stock_info_sz_name_code(indicator="创业板")
