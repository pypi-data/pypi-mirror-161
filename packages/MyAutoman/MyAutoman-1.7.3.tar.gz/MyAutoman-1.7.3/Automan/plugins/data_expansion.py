# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 14:59:33 2019

@author: d00642
"""

def data_expansion(data,var_input,y_input,sampling_strategy,expansion_mode=0):
    '''自动类型转换

    Parameters
    ----------
    data:pd.DataFrame
        需要进行新增的样本数据集，数据集必须包含“var_input”中所有变量
    var_input:list
        list里面的每一个元素必须为连续型变量，且list包含的变量数不宜太多，变量数量小于10个较好
    y_input:str
        目标变量必须为0和1的二分类，其中“1”为少数类，“0”为多数类
    sampling_strategy:dict
        1.例：sampling_strategy={1:1000}，表示y变量为1的样本新增至1000条；\
        2.新增后的条数（1000）必须大于等于原样本条数 \
        3.只对二分类中的少数类进行新增
    expansion_mode:int
        三种新增样本算法，据已观测的数据，算法“0”会比其余两种好。

    Returns
    -------
    new_data:pd.DataFrame
        新增样本后的数据集

    '''

    import pandas as pd
    from imblearn.over_sampling import SMOTE
    from imblearn.over_sampling import BorderlineSMOTE

    X=data[var_input]
    y=data[y_input]
    
    if expansion_mode == 0:
        sm = SMOTE(sampling_strategy=sampling_strategy,random_state=1)
        X,y=sm.fit_sample(X, y)
        new_data=pd.DataFrame(X,columns=var_input)
        new_data.loc[:,y_input]=y
               
    elif expansion_mode == 1:
        sm = BorderlineSMOTE(kind='borderline-1',sampling_strategy=sampling_strategy,random_state=2)
        X,y=sm.fit_sample(X, y)
        new_data=pd.DataFrame(X,columns=var_input)
        new_data.loc[:,y_input]=y
        
    elif expansion_mode == 2:
        sm = BorderlineSMOTE(kind='borderline-2',sampling_strategy=sampling_strategy,random_state=2)
        X,y=sm.fit_sample(X, y)
        new_data=pd.DataFrame(X,columns=var_input)
        new_data.loc[:,y_input]=y
    else:
        return'expansion_mode error'
      
        
    return new_data
    

    
    
    
    
    
    
    
    
    
    
    
    



