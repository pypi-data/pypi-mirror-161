# -*- coding: utf-8 -*-
'''KMOS base on SKlearn 

'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
from sklearn.preprocessing import StandardScaler,MinMaxScaler
import os
from sklearn.cluster import KMeans
import joblib
import pickle
from sklearn.base import BaseEstimator,TransformerMixin

class Kmos(BaseEstimator,TransformerMixin):
    """数据清洗与研判模块
    
    Parameters
    ----------
    fill_dict: dict
       特征替换字典 ,默认None,eg :{np.nan:-1,-99:-1},代表将np.nan和-99替换为-1
    random_state : int
       随机数种子,默认None
    n_jobs: int
       计算并行数量，默认None
    max_iter: int
       计算并行数量
    n_clusters: int
       聚类数量，如果为None，通过cluster_range搜索最优聚类值，默认None，如果为具体数值直接聚类不再通过cluster_range搜索
    cluster_range: tuple
       聚类数量范围，默认（2,25），代表从2类到25类中搜索聚类效果最好的聚类模型
    scale_type: int
       标准化方式，1--StandardScaler, 2--MinMaxScaler 0--将不进行归一化，默认值为1
    threshold: str
       离群点阈值，超过该阈值的样本将视作离群点，默认90%
    
    Attributes
    ----------
    n_dist: list
       聚类数量和聚类组内平均距离的保存列表.
    dist_df : pd.DataFrame
       聚类数量和聚类组内平均距离的保存列表
    rs1: pd.DataFrame
       建模样本上每个类内的距离分布
    st: StandardScaler or MinMaxScaler
       归一化对象
    """

    def __init__(self,
                 fill_dict=None,
                 random_state=None,
                 n_jobs=None,
                 max_iter=100,
                 n_clusters=None,
                 cluster_range=(2,25),
                 scale_type=1,
                 threshold='90%'):
        self.model = None
        self.n_dist = []
        # self.dist_df = pd.DataFrame()
        self.rs1 =  None
        # self.output = None
        # self.oot_df = pd.DataFrame()
        self.st = None
        self.n_cluster = None
        self.random_state=random_state
        self.fill_dict=fill_dict
        self.n_jobs=n_jobs
        self.cluster_range=cluster_range 
        self.max_iter=max_iter 
        self.scale_type=scale_type 
        self.threshold=threshold 
        self.n_clusters=n_clusters
        
    def search_fit(self,X):
        '''search_fit函数
        
        Parameters
        ----------
        X: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        self
        
        '''
        X = X.replace(self.fill_dict)
        
        if self.scale_type==1:
            self.st = StandardScaler()
        elif self.scale_type ==2:
            self.st = MinMaxScaler()
        if self.scale_type !=1 and self.scale_type!=2  and self.scale_type!=0:
            raise ValueError('scale_type must be 1--StandardScaler, 2--MinMaxScaler')
        if self.scale_type==1 or self.scale_type==2 :
            self.st.fit_transform(X)
        
        if self.st is not None:
            X = self.st.transform(X)
        else:
            X = X.values
            
            
        self.n_dist = []
        for i in range(self.cluster_range[0],self.cluster_range[1]):
            print('Search cluster n :%d'%(i))
            model = KMeans(n_clusters=i, n_jobs=self.n_jobs, max_iter=self.max_iter,random_state=self.random_state)
            model.fit(X)
            label_dist = []
            for i_label in range(model.n_clusters):
                r1 = X[model.labels_==i_label,:] - model.cluster_centers_[i_label]
                r1_dist = np.linalg.norm(r1, axis=1)
                label_dist.append(np.mean(r1_dist))
        
            self.n_dist.append((i,np.mean(label_dist)))
        t_all = pd.DataFrame(self.n_dist)
        plt.plot(t_all[0],t_all[1])
        plt.xlabel('ncluster')
        plt.ylabel('Mean distance in cluster')
        plt.show()
        return t_all
        
    def fit(self,X,y=None):
        '''fit函数
        
        Parameters
        ----------
        X: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        self
        
        '''
        dist_df = pd.DataFrame()
        if self.n_clusters is None:
            self.search_fit(X)
            min_dist = min([i[1] for i in self.n_dist])
            n_clusters = [i[0] for i in self.n_dist if i[1] == min_dist][0]
        else:
            n_clusters = self.n_clusters
        
        X = X.replace(self.fill_dict)
        if y is None:
            y = pd.Series(1,index=range(X.shape[0]),name='label')
        
        if self.scale_type==1:
            self.st = StandardScaler()
        elif self.scale_type ==2:
            self.st = MinMaxScaler()
        if self.scale_type !=1 and self.scale_type!=2 and self.scale_type!=0:
            raise ValueError('scale_type must be 1--StandardScaler, 2--MinMaxScaler')
        if self.scale_type == 1 or self.scale_type == 2:
            self.st.fit_transform(X)
        
        if self.st is not None:
            X = self.st.transform(X)
        else:
            X = X.values
            
        self.model = KMeans(n_clusters=n_clusters, n_jobs=self.n_jobs, max_iter=self.max_iter,random_state=self.random_state)
        
        self.model.fit(X)
        # self.n_jobs = n_jobs
        # self.max_iter = max_iter
        for i_label in range(self.model.n_clusters):
            r1 = X[self.model.labels_==i_label,:] - self.model.cluster_centers_[i_label]
            r1_dist = np.linalg.norm(r1, axis=1)
            y_pred = pd.Series(self.model.labels_,index= y.index)
            temp_df = pd.DataFrame(r1_dist,index=[i for i in y_pred.index if y_pred[i]==i_label])
            temp_df['cluster']  = i_label
            dist_df = pd.concat([dist_df, temp_df])
        
        
        self.rs1= dist_df.groupby('cluster')[0].describe(percentiles=np.arange(0,1,0.01)).T
        data_all = pd.concat([dist_df, y],axis=1)
        rs2 = pd.DataFrame(self.rs1.loc[self.threshold,:]).reset_index()
        data_all = pd.merge(left=data_all, right=rs2, on='cluster')
        data_all['lof'] = np.where(data_all[0]>=data_all[self.threshold],1,0)
        # lof = data_all['lof']
        # output = data_all.copy()
        return self
    
    def predict(self,X):
        '''predict函数
        
        Parameters
        ----------
        X: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        output:pd.Series
            离群点数据标签
            
        '''
        X = X.replace(self.fill_dict)
        if self.st is not None:
            X = self.st.transform(X)
        else:
            X = X.values
            
        oot_df = pd.DataFrame()
        # lof = None
        output = None
        
        y = pd.Series(1,index=range(X.shape[0]),name='label')
        idx = y.index
        y_pred =pd.Series(self.model.predict(X),index=range(X.shape[0]))
        for i_label in range(self.model.n_clusters):
            r1 = X[y_pred==i_label,:] - self.model.cluster_centers_[i_label]
            r1_dist = np.linalg.norm(r1, axis=1)
            temp_df = pd.DataFrame(r1_dist,index=[i for i in y_pred.index if y_pred[i]==i_label])
            temp_df['cluster']  = i_label
            oot_df = pd.concat([oot_df, temp_df])
        # oot_all =  pd.concat([self.oot_df, y],axis=1)
        oot_all =  oot_df
        oot_all['index'] = idx
        #oot_all= pd.concat([oot_all, ct],axis=1)
        rs2 = pd.DataFrame(self.rs1.loc[self.threshold,:]).reset_index()
        idx = oot_all.index
        oot_all = pd.merge(left=oot_all, right=rs2, on='cluster')
        oot_all['index'] = idx
        oot_all['lof'] = np.where(oot_all[0]>=oot_all[self.threshold],1,0)
        oot_all = oot_all.set_index('index').sort_index()
        # lof = oot_all['lof'].copy()
        output = oot_all.copy()
            
        return output['lof']
