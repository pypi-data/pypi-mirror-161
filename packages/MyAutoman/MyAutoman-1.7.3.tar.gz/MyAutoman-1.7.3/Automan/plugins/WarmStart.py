# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 16:15:52 2019

@author: d00633
"""
#WarmStart.py


import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import ks_2samp 
from hyperopt import hp,fmin,tpe
from matplotlib import pyplot as plt
import time
import warnings
warnings.filterwarnings("ignore")

def ks_score(preds,trainDmatrix):
    """返回ks的相反数"""
    y_true = trainDmatrix.get_label()
    return 'ks',-ks_2samp(preds[np.array(y_true)==1], preds[np.array(y_true)!=1]).statistic


class HypOpt():
    """
    Parameters
    ----------
    train_set : 训练样本 eg:[train_set_x1 , train_set_y1]
    valid_set : 测试样本 eg: [(valid_set_x1 , valid_set_y1), (valid_set_x2 , valid_set_y2),...]
    space:参数空间，字典格式，eg:
        {'n_estimators':[200],
        "max_depth": [2,3,4],
     "base_score": [0.4,0.5,0.6,0.7],
     "reg_lambda": [1,5,10,15],
     "min_child_weight":[10,20,30],
     'learning_rate':  [0.1,0.08,0.12],
     'colsample_bytree':[0.5,0.7,0.9],
     'subsample': [0.7],#
     'reg_alpha': [1,10],
     'seed':[i*8 for i in range(1000)],
     'scale_pos_weight':[1]
     }
    col_x:输入x变量列表
    output_file:模型结果输出列表文件
    if_plot:是否画图
    max_iters：迭代次数
    missing：xgboost缺失值参数

    Returns
    -------
    字典格式：模型最佳参数,最佳KS
    """
    def __init__(self, train_set, valid_set,space,col_x,output_file='result.txt',if_plot=True,max_iters=300,gama=0.4,missing=None,xgb_model=None):
        self.train_set=train_set
        self.valid_set=valid_set
        self.space=space
        self.output_file=output_file
        self.if_plot=if_plot
        self.max_iters=max_iters       
#        self.mode=mode
        self.missing=missing
        self.k=0
        self.col_x=col_x
        self.hp_space={i:hp.choice(i,self.space[i]) for i in list(self.space.keys())}
        self.xgb_model = xgb_model
        self.gama=gama

    def xgb_factory(self,argsDict):
#        global train_set,eval_set
        self.k+=1
        params = {k:v for k,v in argsDict.items()}
        params['nthread'] = -1
        params['missing'] = self.missing
        
        gbm = xgb.XGBClassifier(**params)
        gbm.fit(self.train_set[0],self.train_set[1]
                ,verbose=False
                ,early_stopping_rounds=30\
                ,eval_metric=ks_score\
                ,eval_set=self.valid_set,xgb_model=self.xgb_model)
        metric=[gbm.evals_result()['validation_'+str(len_eval)]['ks'][gbm.best_iteration] for len_eval in range(len(self.valid_set))]
        params['n_estimators'] = gbm.best_ntree_limit
        tmpre={'params':params,'result':[gbm.best_iteration] + [i * -1 for i in metric]}
#        print('tmpre:',tmpre)
        self.__write_log_file(tmpre)
        
        if self.if_plot:
            self.__plot(tmpre)
            
#        print (metric)
        return (max(metric))
    
    def __create_plot(self):
        import matplotlib.pyplot as plt
        self.c_set=['gray','green','yellow','blue','black','red']
        plt.scatter(0,0)
        plt.show()
        plt.ion()
        self.ax=[]
        for i in range(self.valid_len):
            self.ax.append([])
#        print ("cre ax",self.ax)
            
    def __plot(self,tmpre):
        for i in range(self.valid_len):
            self.ax[i].append(tmpre['result'][i+1])       
#        print ("plot ax",self.ax)   
        plt.cla() 
        for i in range(self.valid_len):
            plt.scatter(range(self.k),self.ax[i],c=self.c_set[i], label='valid_'+str(i))

        plt.legend()
        plt.show()
        plt.pause(0.2)

    def __create_log_file(self):
        f=open(self.output_file,'w')
        f.writelines('params|best_ntree|'+str('|'.join(['ks_valid_'+str(i) for i in range(self.valid_len)]))+'|x_list\n')
        f.close()

    def __write_log_file(self,tmpre):
        f=open(self.output_file,'a')
        f.writelines(str(tmpre['params'])+'|'+'|'.join([str(round(i,4)) for i in tmpre['result']])+'|'+str(self.col_x)+'\n')
        f.close()
        
    def run(self):
        #algo = partial(tpe.suggest,n_startup_jobs=1)
        print ("start!")
        self.k=0
        self.valid_len=len(self.valid_set)
        self.__create_log_file()
        if self.if_plot:
            self.__create_plot()
        best = fmin(self.xgb_factory,self.hp_space,algo=tpe.suggest,max_evals=self.max_iters)#max_evals表示想要训练的最大模型数量，越大越容易找到最优解
        print (best)
#        best_dic={i:self.space[i][best[i]] for i in self.space.keys()}
#        best_ks=self.xgb_factory(best_dic)
        
        all_param = pd.read_csv(self.output_file,sep='|')
        params = all_param[['params']+['ks_valid_'+str(i) for i in range(self.valid_len)]]
        params['params'] = params['params'].apply(lambda x:eval(x))
        params['max_ks'] = params[['ks_valid_'+str(i) for i in range(self.valid_len)]].max(axis=1)
        params['min_ks'] = params[['ks_valid_'+str(i) for i in range(self.valid_len)]].min(axis=1)
        params['f_score'] = params[['max_ks','min_ks']].apply(lambda x:(2*x['max_ks']*x['min_ks'])/(x['max_ks']+x['min_ks'])-self.gama*abs(x['max_ks']-x['min_ks']),axis=1)
        
        best_dic = params[params['f_score']==params['f_score'].max()]['params'].values[0]
        eval_ks = params[params['f_score']==params['f_score'].max()][['ks_valid_'+str(i) for i in range(self.valid_len)]]
        best_ks = eval_ks.values[0][self.valid_len-1] #以最后一份验证集的KS作为最佳KS
        
        return best_dic,best_ks



def warm_start(train,
               valid,
               input_x,
               y,
               unstable_x,
               param_space_1,
               param_space_2,
               max_iters=100,
               gama=0.4,
               if_plot=True,
               output_file_1='param_1.txt',
               output_file_2='param_2.txt',
               first_round_model='first_round_model'):
    """
    函数功能：利用WarmStart方法训练模型
    
    ----
    返回：返回tuple类型，(model_1,model_2)
    return model_1,model_2
    model_1:不包含不稳定变量的最佳模型
    model_2:利用WarmStart方法训练返回的最佳模型
    
    ----
    生成文件：
    param_1.txt：存储调参时从参数空间1选中的参数组合及KS效果.
    param_2.txt：存储调参时从参数空间2选中的参数组合及KS效果.
    first_round_model：不包含不稳定变量的模型，.model类型.
    文件保存路径：调用WarmStart模块的python文件的工作路径.
    ----
    
    参数
    ----
    train : DataFrame,训练集，含X，y.
    
    valid : DataFrame,验证集，含X，y.
    
    input_x ：list,元素为入模变量的变量名称.
    
    y : string,目标变量名.
    
    unstable_x : list,元素为不稳定变量的变量名称.
    
    param_space_1 ：Dict，参数空间1.
                    Dict的keys与xgboost.XGBClassifier()对象的参数名称一致.
                    Dict的value为列表类型，元素与xgboost.XGBClassifier()的参数范围、类型一致.
                
    param_space_2 : Dict，参数空间2.
                    Dict的keys与xgboost.XGBClassifier()对象的参数名称一致.
                    Dict的value为列表类型，元素与xgboost.XGBClassifier()的参数范围、类型一致.
                    注意：不支持用户自定义subsample、colsample_bytree参数，subsample、colsample_bytree默认值均为1.
    
    output_file_1 ： string，默认值param_1.txt.
                     表示存储调参时从参数空间1选中的参数组合及KS效果的txt文件名称.
                     
    output_file_2 ： string，默认值param_2.txt.
                     表示存储调参时从参数空间2选中的参数组合及KS效果的txt文件名称.
                     
    if_plot ： bool，默认值False.
               是否在调参时显示训练集和验证集每组参数对应的KS的散点图，False表示不显示.
               
    max_iters ： int,默认值100，表示调参次数.
                 值越大，获得最佳参数的可能性越大，但耗时越长(当train.shape=(5906,56),valid.shape=(1985,56),max_iters=50时，平均训练时间为1200秒).
                 
    first_round_model ：string,默认值'first_round_model'，表示不包含不稳定变量的模型名称.
    
    gama ：float，默认值0.4，取值范围[0,1].
           gama为评价函数的惩罚系数，当训练集和验证集的KS差异越大时，gama值越大，惩罚越大，可以防止过拟合、欠拟合.
    
    
    示例
    ----
    train
             a           b     c      d      e  y_label
    0   142601    0.906177  17.0    9.0   12.0        0
    1   510525 -999.000000  17.0    5.0   11.0        0
    2   220702    0.916667  11.0 -999.0    8.0        0
    3   510321    0.638889  14.0    3.0    7.0        0
    4   500221    0.873786   8.0    2.0    6.0        0
    5   500228    0.538149  12.0    7.0    4.0        1
    6   330327    0.839725  12.0    2.0    9.0        0
    7   350521 -999.000000  11.0    1.0    3.0        1
    8   510802    0.498362   4.0    5.0    2.0        0
    9   232324 -999.000000  16.0 -999.0    8.0        0
    10  320522    0.774446  12.0 -999.0    3.0        1
    11  222424    0.461586   2.0 -999.0    1.0        0
    12  445221    0.000000   4.0    2.0 -999.0        0
    13  152104    0.649922   7.0    2.0    6.0        1
    14  410901    0.458624   3.0 -999.0    2.0        1
    15  460007    0.675270   2.0    3.0    1.0        0
    16  211103    0.881981  18.0 -999.0    4.0        0
    17  430723    0.219133  11.0 -999.0    7.0        0
    18  422130    0.838092   7.0 -999.0    3.0        0
    19  431281    0.951724   9.0    5.0    4.0        0
    
    
    valid 
            a           b     c     d     e  y_label
    0  330382    0.887893  14.0   8.0  10.0        1
    1  230106    0.562827   8.0  10.0   7.0        0
    2  220581 -999.000000  17.0   1.0  11.0        0
    3  210106    0.602937   7.0   3.0   4.0        0
    4  321023    0.000000  14.0   1.0   9.0        0
    5  620522    0.802197  11.0   7.0   5.0        1
    6  640221    0.826864   3.0   7.0   2.0        0
    7  620102    0.597784   6.0   3.0   5.0        0
    8  152923    0.373446   5.0   6.0   1.0        0
    9  350681    0.857829  11.0   8.0   5.0        1
    
    
    input_x = ['a','b','c','d','e']
    y ='y_label'
    unstable_x = ['a','b']
    
    param_space_1 = {'n_estimators':[300],
                   "max_depth": [3,4],
                   "base_score": [0.2,0.3,0.4,0.6],
                   "reg_lambda": [10,15],
                   "min_child_weight":[10,20,30],
                   'learning_rate':  [0.1,0.08,0.12],
                   'reg_alpha': [1,10],
                   'scale_pos_weight':[1]
                  }
    
    param_space_2 = {'n_estimators':[100],
                   "max_depth": [3,4,5],
                   "base_score": [0.2,0.3,0.4,0.6],
                   "reg_lambda": [1,5,10,15],
                   "min_child_weight":[10,20,30],
                   'learning_rate':  [0.1,0.08,0.12],
                   'reg_alpha': [1,10],
                   'scale_pos_weight':[1]
                  }
    
    model_1,model_2 = WarmStart.warm_start(train=train,      
                                           valid=valid,               
                                           input_x,              
                                           y=y,                    
                                           unstable_x=unstable_x,          
                                           param_space_1,        
                                           param_space_2,        
                                           max_iters=3          
                                           )
    """
    
    time_start = time.time()
    #第1轮训练    
    #将不稳定变量置空
    train_1 = train.copy()
    valid_1 = valid.copy()
    train_1[unstable_x] = -9999    
    valid_1[unstable_x] = -9999
    
    eval_set = [(train[input_x],train[y]),(valid[input_x],valid[y])]
    eval_set_1 = [(train_1[input_x],train_1[y]),(valid_1[input_x],valid_1[y])]

    #选第1轮调参
    ho = HypOpt([train_1[input_x],train_1[y]],
                eval_set_1 ,
                param_space_1,
                input_x,
                output_file=output_file_1,
                if_plot=if_plot,
                max_iters=max_iters,
                gama=gama,
                xgb_model=None)
    best_param,best_ks = ho.run()
        
    model_1 = xgb.XGBClassifier(**best_param)
    model_1.fit(train_1[input_x],train_1[y])
    
    #保存model_1
    model_1.get_booster().save_model('{}.model'.format(first_round_model))

    #第2轮训练

    #第2轮训练不支持用户自定义subsample、colsample_bytree，默认值为1
    if param_space_2.get('subsample',0):
        param_space_2['subsample'] = [1]
    if param_space_2.get('colsample_bytree',0):
        param_space_2['colsample_bytree'] = [1]
    
    #第2轮调参
    ho = HypOpt([train[input_x],train[y]],
                eval_set,
                param_space_2,
                input_x,
                output_file=output_file_2,
                if_plot=if_plot,
                max_iters=max_iters,
                gama=gama,
                xgb_model='{}.model'.format(first_round_model))
    
    best_param,best_ks = ho.run()    
    
    model_2 = xgb.XGBClassifier(**best_param)
    model_2.fit(train[input_x],train[y],xgb_model='{}.model'.format(first_round_model))  
    
    time_end = time.time()
    print('共耗时：{} 秒'.format(time_end-time_start))
    return model_1,model_2
    
