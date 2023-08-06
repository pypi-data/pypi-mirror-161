# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 16:16:42 2021

@author: y00816
"""

from sklearn.tree import DecisionTreeClassifier
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve   
import copy  
import logging
from matplotlib import pyplot as plt

class TrAdaboost:
    '''类功能
    迁移学习类
    '''
    def __init__(self, base_classifier=DecisionTreeClassifier(), N=100 , use_threshold = True, output_mode=1,random_state=None,if_plot=False):
        '''函数功能
        初始化迁移学习类
        
        Args:
        base_classifier (class) : 选用的算法，注意需要带有predict及predict_prob 函数的类,以及必须带有sample_weights参数
        N (int) : 迭代次数
        use_threshold (bool) : 是否采用正样本比例来调节实际的bad_rate
        output_mode (int) : 模型结果计算方法 output_mode=1 会根据最好的一轮结果输出，output_mode = 2 根据第best_round/2-best_round 轮结果的平均值
        random_state(int) : 随机数种子
        if_plot (bool) : 是否展示模型效果图
        
        '''
        
        #基模型
        self.base_classifier = base_classifier
        #训练轮次
        self.N = N
		#可变beta列表
        self.beta_all = np.zeros([1, self.N])
		#模型列表
        self.classifiers = []
		#最佳ks
        self.best_ks = -1      
        #最优基模型数量          
        self.best_round = -1    
        #最优模型      
        self.best_model = -1 
        #样本权重
        self.mat_weights=[]
        #是否用样本实际的坏率调整error-RATE
        self.use_threshold = use_threshold
        #最佳样本权重
        self.best_sample_weights = []
        #计算结果方式
        self.output_mode = 1
        #随机数种子
        self.random_state = random_state
        #是否展示模型效果
        self.if_plot = if_plot

    #迁移学习模型训练
    def fit(self, x_source, x_target, y_source, y_target,x_test,y_test,early_stopping_rounds=30):
        '''函数功能
        训练迁移学习
        
        Args：
        x_source (pd.DataFrame/np.array) : 辅助数据集
        x_target (pd.DataFrame/np.array) : 目标数据集
        y_source (list/np.array) : 辅助域目标变量
        y_target (list/np.array) : 目标域目标变量
        x_test (pd.DataFrame/np.array) : 调参数据集
        y_test (list/np.array) : 调参集目标变量
        early_stopping_rounds(int) : 早停轮次
        '''
        
        
        self._data_check_x(x_source)
        self._data_check_x(x_target)
        self._data_check_x(x_test)
        self._data_check_y(y_source)
        self._data_check_y(y_target)
        self._data_check_y(y_test)
        self._data_check_duplicate_y(x_source,y_source)
        self._data_check_duplicate_y(x_target,y_target)
        
        self._data_check_nan(x_source)
        self._data_check_nan(x_target)
        self._data_check_all_empty(x_source)
        self._data_check_all_empty(x_target)
        
        if self.random_state is not None:
            seed = self.random_state
        else:
            seed = int(np.random.uniform(10000))
        
        
        x_source = np.array(x_source)
        x_target = np.array(x_target)
        x_test = np.array(x_test)
        y_test= np.array(y_test)
        x_train = np.concatenate((x_source, x_target), axis=0)
        y_train = np.concatenate((y_source, y_target), axis=0)
        x_train = np.asarray(x_train, order='C')
        y_train = np.asarray(y_train, order='C')
        y_source = np.asarray(y_source, order='C')
        y_target = np.asarray(y_target, order='C')

        row_source = x_source.shape[0]
        row_target = x_target.shape[0]

        # 初始化权重
        weight_source = np.ones([row_source, 1]) 
        weight_target = np.ones([row_target, 1])
        weights = np.concatenate((weight_source, weight_target), axis=0)

        beta = 1 / (1 + np.sqrt(2 * np.log(row_source / self.N)))

        result = np.ones([row_source + row_target, self.N])
        for i in range(self.N):
            weights = self._calculate_weight(weights)
            model = copy.deepcopy(self.base_classifier)
            model.random_state = seed
            self.mat_weights.append(list(weights[:,0]))
            
            model.fit(x_train, y_train, sample_weight=weights[:, 0])
            #self.base_classifier.fit(x_train, y_train, sample_weight=weights[:, 0])
            #self.classifiers.append(self.base_classifier)
            self.classifiers.append(model)
            #print([k.train_score_.mean() for k in self.classifiers])
            #result[:, i] = self.base_classifier.predict_proba(x_train)[:,1]
            result[:, i] = model.predict_proba(x_train)[:,1]
            if self.use_threshold :
                score_H = result[row_source:row_source + row_target, i]  
                print(score_H)
                pctg = np.sum(y_train)/len(y_train)     # 按照正负样本的比例划分预测label
                print(pctg)
                thred = pd.DataFrame(score_H).quantile(1-pctg)[0]    
                print(thred)
                label_H = self._put_label(score_H,thred)
                print(sum(label_H))
            else :                
                label_H = model.predict_proba(x_target)[:,1]
            error_rate = self._calculate_error_rate(y_target,
                                                    np.array(label_H),
                                                    weights[row_source:row_source + row_target, :])

            print("Error Rate in target data: ", round(error_rate, 4), 'round:', i, 'all_round:', self.N)
            
            if error_rate > 0.5:
                error_rate = 0.5
            if error_rate == 0:
                self.N = i
                print("Early stopping...")
                break
            self.beta_all[0, i] = error_rate / (1 - error_rate)

            # 调整 target 样本权重 正确样本权重变大
            for t in range(row_target):
                weights[row_source + t] = weights[row_source + t] * np.power(self.beta_all[0, i], -np.abs(result[row_source + t, i] - y_target[t]))
            # 调整 source 样本 错分样本变大
            for s in range(row_source):
                weights[s] = weights[s] * np.power(beta, np.abs(result[s, i] - y_source[s]))
                
            #y_pred = self.base_classifier.predict_proba(x_test)[:,1] 
            
            
            #y_pred = model.predict_proba(x_test)[:,1] 
            #fpr_lr_train,tpr_lr_train,_ = roc_curve(y_test,y_pred)      
            #train_ks = abs(fpr_lr_train - tpr_lr_train).max()      
            #print('test_ks : ',train_ks,'当前第',i+1,'轮')  
            
            #y_pred = model.predict_proba(x_train)[:,1] 
            #fpr_lr_train,tpr_lr_train,_ = roc_curve(y_train,y_pred)      
            #train_ks = abs(fpr_lr_train - tpr_lr_train).max()      
            #print('train_ks : ',train_ks,'当前第',i+1,'轮')              
            
            
            test_ks = self._calculate_ks( x_test, y_test)
            print('源数据检验样本_ks : ',test_ks,'当前第',i+1,'轮')
            
            train_ks = self._calculate_ks( x_train, y_train)
            print('源数据以及辅助数据训练样本_ks : ',train_ks,'当前第',i+1,'轮')
            
            train_ks_S = self._calculate_ks( x_source, y_source)
            print('辅助数据训练样本KS : ', train_ks_S, '当前第',i+1,'轮' )
            
            train_ks_T = self._calculate_ks( x_target, y_target)
            print('源数据训练样本KS : ', train_ks_T, '当前第',i+1,'轮' )
            
                
            
            
            # 不再使用后一半学习器投票，而是只保留效果最好的逻辑回归模型 clz
            ks_diff = -abs(train_ks-test_ks)*0.5 + 0.5 * test_ks
            if  ks_diff > self.best_ks :      
                self.best_ks = ks_diff      
                self.best_round = i      
                self.best_model = model
            #if  test_ks > self.best_ks :      
            #    self.best_ks = test_ks      
            #    self.best_round = i      
            #    self.best_model = model
                #self.best_weights=copy.deepcopy(weights)
                
            # 当超过eadrly_stopping_rounds轮KS不再提升后，停止训练  
            if self.best_round < i - early_stopping_rounds:  
                break  
        
        if self.output_mode == 1:          
            self.best_sample_weights =  list(pd.DataFrame(self.mat_weights).T.iloc[:,self.best_round])
        else:
            self.best_sample_weights =list(np.mean(pd.DataFrame(self.mat_weights).T.iloc[:,int(self.best_round/2):self.best_round + 1], axis=1))
            
        final_train_pred = self.predict_proba(x_train)
        final_test_pred = self.predict_proba(x_test)
        final_s_pred = self.predict_proba(x_source)
        final_t_pred = self.predict_proba(x_target)
        
        fpr_train, tpr_train, _ = roc_curve(y_train, final_train_pred)
        fpr_test, tpr_test, _ = roc_curve(y_test, final_test_pred)
        fpr_s, tpr_s, _ = roc_curve(y_source, final_s_pred)
        fpr_t, tpr_t, _ = roc_curve(y_target, final_t_pred)
        if  self.if_plot:
            plt.plot(fpr_train, tpr_train, label='train curve')
            plt.plot(fpr_test, tpr_test, label='test curve')
            plt.plot(fpr_s, tpr_s, label='source curve')
            plt.plot(fpr_t, tpr_t, label='target curve')
            plt.plot([0,1], [0,1], 'k--')
            plt.xlabel('False positive rate')
            plt.ylabel('True positive rate')
            plt.title('ROC Curve')
            plt.legend(loc='best')
            plt.show()
        final_test_ks = abs(fpr_test - tpr_test).max()      
        final_train_ks = abs(fpr_train - tpr_train).max()      
        print('test_ks final',final_test_ks,'train_ks final', final_train_ks)
        
        
        
        return self

    def cal_weights(self):
        '''函数功能
        计算最终样本权重
        
        Args：
        
        '''
        if self.output_mode == 1:          
            self.best_sample_weights =  list(pd.DataFrame(self.mat_weights).T.iloc[:,self.best_round])
        else:
            self.best_sample_weights =list(np.mean(pd.DataFrame(self.mat_weights).T.iloc[:,int(self.best_round/2):self.best_round + 1], axis=1))
        return self.best_sample_weights   
        
    def _data_check_x(self,x):
        print('检查入模变量类型')
        assert isinstance(x,pd.DataFrame) or isinstance(x, np.ndarray) , '输入项必须是DataFrame 或者 array'
    
    def _data_check_y(self,y):
        print('检查目标变量类型')
        assert isinstance(y, list) or isinstance(y, np.ndarray), '目标变量必须是list 或者 array'
        assert set(y) == {1,0}, '目标变量必须是0，1 二分类'
        
    def _data_check_duplicate_y(self,x,y):
        print('检查数据集是否含有高相关性目标变量')
        x = pd.DataFrame(x)
        y = pd.Series(y)
        d = pd.concat([x,y], axis=1)
        corr_data = d.corr()
        corr_y = corr_data.iloc[:,-1]
        thre_y = sum(corr_y>0.95)
        if thre_y > 1:
            logging.warning('数据集中有可能存在重复的目标变量')
        else:
            pass
        

    def predict(self, x_test):           
        '''函数功能
        预测结果
        
        Args：
        x_test (np.array) : 待预测数据集
        '''
        if self.output_mode == 1:
            predict = list(self.classifiers[self.best_round].predict(x_test))
            return predict
        else:            
            result_left = np.ones([x_test.shape[0], self.N + 1])
            result_right = np.ones([x_test.shape[0], self.N + 1])
            predict = []
    
            i = 0
            for classifier in self.classifiers[:self.best_round + 1]:
                y_pred = classifier.predict_proba(x_test)[:,0]
                result_left[:, i] = y_pred
                y_pred = classifier.predict_proba(x_test)[:,1]
                result_right[:, i] = y_pred
                i += 1
            i= i - 1
            #print(i)
            for t in range(x_test.shape[0]):
                left = result_left[t,int(i/2):i + 1].mean()
    
                right = result_right[t,int(i/2):i + 1].mean()
    
                if left >= right:
                    predict.append(0)
                else:
                    predict.append(1)
            return predict

    def predict_proba(self, x_test):
        '''函数功能
        预测概率
        
        Args：
        x_test (np.array) : 待预测数据集
        '''
        if self.output_mode == 1:
            predict = list(self.classifiers[self.best_round].predict_proba(x_test)[:,-1])
            return predict
        else:
            result = np.ones([x_test.shape[0], self.N + 1])
            predict = []
    
            i = 0
            for classifier in self.classifiers[:self.best_round + 1]:
                y_pred = classifier.predict_proba(x_test)[:,-1]
                result[:, i] = y_pred
                i += 1
            i= i - 1
            #print(i)
            for t in range(x_test.shape[0]):
                #predict.append( np.sum(result[t, int(np.ceil(self.N/2)):i] * np.log(1/self.beta_all[0, int(np.ceil(self.N/2)): self.N])))
                predict.append(result[t,int(i/2):i + 1].mean())
            return predict

    def _calculate_weight(self, weights):
        sum_weight = np.sum(weights)
        return np.asarray(weights, order='C')

    def _calculate_error_rate(self, y_target, y_predict, weight_target):
        sum_weight = np.sum(weight_target)
        return np.sum(weight_target[:, 0] / sum_weight * np.abs(y_target - y_predict))

    def _put_label(self,score_H,thred):      
        new_label_H = []      
        for i in score_H:      
            if i <= thred:      
                new_label_H.append(0)      
            else:      
                new_label_H.append(1)      
        return new_label_H  
    
    def _calculate_ks(self, x, y):
        pred = self.classifiers[-1].predict_proba(x)[:,1] 
        fpr_lr_train,tpr_lr_train,_ = roc_curve(y,pred)      
        train_ks = abs(fpr_lr_train - tpr_lr_train).max()      
        return round(train_ks,4)
    
    def _data_check_nan(self,x):
        print('检查数据集是否含有空值')
        nan_list = [ i for i in range(x.shape[1]) if (np.isnan(x)).any(axis=0)[i] ]
        if  len(nan_list) != 0:
            logging.warning('these cols has nan value%s'%str(nan_list))
        
    def _data_check_all_empty(self,x):
        print('检查数据集是否含有全空列')
        empty_list =  [ i for i in range(x.shape[1]) if (x == -99).all(axis=0)[i] ]
        if  len(empty_list) != 0:
            logging.warning('these cols is all -99 %s'%str(empty_list))
    