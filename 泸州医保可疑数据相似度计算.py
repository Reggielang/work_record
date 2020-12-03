# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 10:38:59 2020

@author: REGGIE
"""

import pandas as pd
import math
import numpy as np
import os
import  cx_Oracle as cx
from sklearn import preprocessing


def process_df(data):
    df = data.set_index(["医院编码", '就诊时间'])["患者编码"].str.split(",", expand=True).stack().reset_index(drop=True, level=-1).reset_index().rename(columns={0: "患者编码"})
    df['患者编码'] = df['患者编码'].apply(lambda x:x.replace('[','')).apply(lambda x:x.replace(']','')).apply(lambda x:x.strip())
    #重命名列名，匹配数据库表格的列名
    df.rename(columns={'医院编码':'AAZ107','就诊时间':'AAE030','患者编码':'AAC002'},inplace = True)
    #统一匹配字段的数据类型
    df['AAZ107'] = df['AAZ107'].apply(str)
    df['AAE030']=df['AAE030'].apply(str)
    return df


def process_mergedata(user,pwd,ip_port_db,df):
    #建立连接
    con  =  cx.connect(user, pwd, ip_port_db)
    #获取数据
    KC21_sql = "SELECT aaz107,aac002,aae030,akc190 FROM KC21"       
    KC21 = pd.read_sql(sql=KC21_sql, con=con)
    #获取数据
    KC22_sql = "SELECT akc226,akc190 FROM KC22"       
    KC22 = pd.read_sql(sql=KC22_sql, con=con)
    #获取数据
    KC24_sql = "SELECT aac002，akc190, akc264, yke032,akc303，akc301，akc302, akc304 FROM KC24"       
    KC24 = pd.read_sql(sql=KC24_sql, con=con)
    
    #表格合并
    big_table_1 = pd.merge(KC21,KC24,on=['AKC190','AAC002'])
    big_table = pd.merge(big_table_1,KC22,on=['AKC190'])
    
    #统一匹配字段的数据类型
    big_table_1['AAE030']=big_table_1['AAE030'].apply(str)
    big_table['AAE030']=big_table['AAE030'].apply(str)
    #合并可疑数据中的表格于数据库的对应数据
    half_result = pd.merge(df, big_table_1, on=['AAZ107', 'AAE030', 'AAC002'], how='inner')
    #计算AKC226项目数量的总数
    AKC226 = KC22[KC22.AKC190.isin(half_result.AKC190)].groupby('AKC190').count()
    AKC226 = pd.DataFrame(AKC226)
    result = pd.merge(half_result,AKC226,on=['AKC190'], how='inner')
    
    return result



def get_output(result):
    AAZ107_list = result['AAZ107'].unique().tolist()
    result = result.set_index(['AAZ107','AAE030'])
    final_result = result.copy()
    
    for i in AAZ107_list:
        standard =  result.loc[(i,slice(None)),:]
        standard = standard.iloc[:,4:].apply(lambda x : preprocessing.scale(x))
        standard['similarity'] = standard.apply(lambda x: x.sum(),axis=1)
        standard['similarity'].to_csv('half_result.csv', mode='a', header = False)
    
    similarity = pd.read_csv('half_result.csv',header=None,usecols=[2])
    final_result['similarity']=similarity.values
    final_result.reset_index(inplace=True)
    final_result = final_result.rename(columns={'AAZ107':'医院编号','AAE030':'入院时间','AAC002':'患者医疗保障号码','AKC190':'医疗业务系统就诊ID'
        ,'AKC264':'总费用','YKE032':'医保基金总支付费用','AKC303':'服务设施费','AKC301':'药品费'
        ,'AKC302':'诊疗费','AKC304':'材料费','AKC226':'诊疗项目数量','similarity':'相似度'})
    final_result.to_csv('final_result.csv',index = False,encoding='utf-8-sig')
    
    print('最终结果保存成功！请打开“final_result”CSV文件进行查看')
        

def main():
    #输入参数
    os.chdir(r'C:\Users\REGGIE\Desktop\work\泸州项目')
    data = pd.read_csv(r'test_同质化.csv',encoding='utf-8-sig')
    user = 'swjw' 
    pwd ='swjw'
    ip_port_db = '192.168.26.220:1522/EE'
    
    
    result = process_mergedata(user,pwd,ip_port_db,process_df(data))
    get_output(result)
    
    

if __name__=='__main__':
    main()
