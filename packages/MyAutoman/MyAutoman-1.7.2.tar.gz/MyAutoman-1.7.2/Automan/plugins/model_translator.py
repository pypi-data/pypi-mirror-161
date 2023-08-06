# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 12:00:52 2020

@author: h00987
"""
import m2cgen as m2c
import lightgbm as lgb
import xgboost as xgb

def translator(model,language = 'python',output = 'model_translator.txt'):
    '''模型翻译工具，将训练好的机器学习模型转译为原代码
    
    Parameters
    ----------
    model : class      
        支持Autman,XGB,LGBM等机器学习模型

    language: str, optional(default = 'python')
        模型转译后原代码的语言，默认为jpython语言
        - 'python', 转译为python语言
        - 'java', 转译为java语言
        - 'c', 转译为C语言

    output : str, optional
        记事本保存名称，默认名称为 model_translator.txt
    
    Returns
    -------
        模型转移后的原代码，str
        在工作目录中生成模型转移后的原代码，文件格式为txt
        
    '''
    if type(model).__name__ == 'AmAllFeatLgbClf': 
        lgb_clf = lgb.LGBMClassifier()
        lgb_clf.__dict__ = model.__dict__.copy() 
        model = lgb_clf
    elif type(model).__name__ == 'AmAllFeatXgbClf':
        xgb_clf = xgb.XGBClassifier()
        xgb_clf.__dict__ = model.__dict__.copy() 
        model = xgb_clf
    elif type(model).__name__ == 'AmFeatSelXgbClf':
        xgb_Sel_clf = xgb.XGBClassifier()
        xgb_Sel_clf.__dict__ = model.__dict__.copy() 
        model = xgb_Sel_clf
    elif type(model).__name__ == 'AmAllFeatXgbReg':
        xgb_reg = xgb.XGBRegressor()
        xgb_reg.__dict__ = model.__dict__.copy() 
        model = xgb_reg
    elif type(model).__name__ == 'AmAllFeatLgbReg':
        lgb_reg = lgb.LGBMRegressor()
        lgb_reg.__dict__ = model.__dict__.copy() 
        model = lgb_reg
        
    if language == 'python':
        trans_code = m2c.export_to_python(model)
    elif language == 'java':
        trans_code = m2c.export_to_java(model)
    elif language == 'c':
        trans_code = m2c.export_to_c(model)
        
    output = open(output, 'w', encoding='utf-8')
    output.write(trans_code)
    output.close()
    return trans_code














