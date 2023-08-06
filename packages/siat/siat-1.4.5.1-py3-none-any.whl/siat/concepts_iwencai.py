# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:41:28 2020

@author: Peter
"""

import urllib.request
import re
import requests

# def main():
#     # url = "http://www.iwencai.com/school/dictionary?qs=study_dictonary_stock"
#     # url='http://www.iwencai.com/yike/article-class-list?tagId=37'
#     url="http://www.iwencai.com/yike/detail/auid/716981f756614a79"
#     try:
#         data = urllib.request.urlopen(url).read()
#         content = data.decode('UTF-8')
#
#         # pattern = re.compile('<div class="term_top clearfix">.*?<a.*?point_info="title">(.*?)</a></div>.*?'
#         #                      '<div class="term_summary clearfix">(.*?)</div>',
#         #                      re.S)
#         pattern = re.compile('<div class="term_summ_acl term_summ_acl_img">*?<div>(.*?)</div></div>',
#                              re.S)
#         items = re.findall(pattern, content)
#         print(items[0])
#         # for item in items:
#         #     print(item[0],item[1])
#
#     except e:
#         print(e.code)
#         print(e.re)

def main():
    for i in range(1,300):
        con_list=getPage(i)
        for item in con_list:

            subUrl=item['URL']
            concrete=getConcrete(subUrl)
            if concrete!=None :
                if len(concrete)!=0:
                    print(item['title'])
                    concrete=concrete.replace('<div>','')
                    # concrete.replace('&nbsp;', '')
                    print(concrete.replace('&nbsp;', ''))
                    print("================================")


def getConcrete(subUrl):
    concrete_url = "http://www.iwencai.com/" + subUrl
    # print(concrete_url)
    try:
        data = urllib.request.urlopen(concrete_url).read()
        content = data.decode('UTF-8')  #
        pattern = re.compile('<div class="term_summ_acl term_summ_acl_img">(.*?)</div>',re.S)
        items = re.findall(pattern, content)
        if len(items)==0:
            pattern = re.compile('<div class="term_summ_acl ">(.*?)</div>',re.S)
            items = re.findall(pattern, content)
        return items[0]
    except:
        print("异常--------------")
    return []

#获取索引页面的内容
def getPage(pageIndex):
    siteURL="http://www.iwencai.com/yike/index-page-ajax/"
    url = siteURL + "?p=" + str(pageIndex)+"&filterTag=37"
    # request = urllib2.Request(url)
    # response = urllib2.urlopen(request)
    # return response.read().decode('gbk')
    # data = urllib.request.urlopen(url).read()
    # content = data.decode('gbk')
    # return content
    headers = {
        'Referer': 'http://www.sse.com.cn/disclosure/credibility/supervision/inquiries/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    return r.json()['list']
    # print(r.json()['list'][1]['summ'])


if __name__ == '__main__':
    main()