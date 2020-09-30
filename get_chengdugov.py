# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 10:39:21 2020

@author: REGGIE
"""

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
import json
from bs4 import BeautifulSoup
import random
import pandas as pd

#初始URL
data = '_template=zhaofa/cdsrs_list&_pageSize=422'
url = 'http://cdhrss.chengdu.gov.cn/es-search/search/e444eaeca74c4be6a186e84834d16a7b?{}'.format(data)

headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
       'Cookie': 'azSsQE5NvspcS=5IRe52gZqFzeloQhBPzKnxqTBzKRkn1INevZndvXgA6wUiRw.UsVP4sjN8T0dCXC3nVx_p4LFZsor1ghANwMMkA; yfx_c_g_u_id_10000063=_ck20092416065513072337771511809; yfx_f_l_v_t_10000063=f_t_1600934815290__r_t_1600996404334__v_t_1601016129352__r_c_1; azSsQE5NvspcT=5UCC3IYezbELqqqm0SrXjrAJC.ECuEuEwfIAX_u34oWopbKMbUVYLff8qMFhX.fSUQVGhcmPqiUm2BxCLXxAqsGlsrtO3doTVo7lffvI8t4329Qku9MbSZYTL6mC8.J72MaV1nATZ9yGN2.z3h6Dh7oVqlx1M0Nj2tCvY9RNgdvq.RoPFt52Og0trEOP9aegjnHnl73RM2QyGHoMZf.Eurz..VL6ahws_3QDMgbugKePtXP.W5xeH1.r8muuwqOrnL',
       'Connection': 'keep-alive',
       'Referer': 'http://cdhrss.chengdu.gov.cn/es-search/search/e444eaeca74c4be6a186e84834d16a7b?_template=zhaofa/cdsrs_list&_pageSize=422',
      'Upgrade-Insecure-Requests': '1',
      'Host': 'cdhrss.chengdu.gov.cn',
      'Cache-Control': 'max-age=0',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7,la;q=0.6,fr;q=0.5',
      'Accept-Encoding': 'gzip, deflate'
       }
try:
    res = requests.get(url,headers = headers)
    res.encoding='utf-8'
    if res.status_code == 200:
        html = res.text
except RequestException:
    print('None')


#抓取文章链接
item_url = []
soup = BeautifulSoup(html,'html.parser')
urls = soup.find_all('a')
for url in urls:
    item_url.append(url['href'])
    
#在获取数据之前，先处理获取的文章URL列表 
#删除不能打开的链接
for i in item_url:
    if 'shtml' not in i:
        item_url.remove(i)

#处理文章链接，获取基本数据
def get_info(url):
    info={}
    request = requests.get(url = url, headers=headers)
    request.encoding='utf-8'
    soup = BeautifulSoup(request.text,'html.parser')
    info['文件名称'] = soup.h1.string
    info['信息'] = soup.find_all('h3')[-1].string
    filename = str(num) + '.txt' 
    with open(filename,'w',encoding='utf-8') as f:
        for item in soup.select('.cont p') and soup.select('p'):
            data = item.get_text()
            f.write(data)       #正文写入文件
#        for item in soup.select('span'):
#            data = item.get_text()
#            f.write(data)       #正文写入文件
    return info

#处理爬取下来文章基本信息数据
def process_info(infoarray):
#    pd.options.display.max_columns = None
    df = pd.DataFrame(infoarray)
    df['文件编号'] = pd.DataFrame(data = {'文件编号':range(1,len(item_url)+1)})
    df['填报时间'] = df['信息'].str.extract('(\d{4}-\d{1,2}-\d{1,2})')
    df['责任单位'] = df['信息'].str.extract('：([\u4e00-\u9fa5]+)')
    data = df.drop('信息',axis = 1)
    columns = ['文件编号','文件名称','填报时间','责任单位']
    data = data[columns]
    data.to_csv('成都人社政策文件信息.csv',index=False,encoding='utf_8_sig')
    return data

#运行程序       
infoarray=[]
num = 0
for i in item_url:
    num += 1   #计数变量加1，统计总的下载文件数
    infoarray.append(get_info(i))
process_info(infoarray)




    
