#!/usr/bin/env python
# coding: utf-8
#需要调用的包
default_encoding = 'utf-8'
import pandas as pd
import numpy as np
import re
from sklearn.tree import DecisionTreeClassifier
import warnings
warnings.filterwarnings("ignore")
import logging
import os
import logging.handlers
import time
from functools import wraps
from scipy.stats import ks_2samp
from statsmodels.graphics.mosaicplot import mosaic
import matplotlib.pyplot as plt
import pylab
import datetime
import itertools
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import multiprocessing as mp
import random
from sklearn.base import BaseEstimator, TransformerMixin,clone
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.exceptions import NotFittedError
from sklearn import metrics
from sklearn.utils import check_random_state, check_X_y
# from sklearn.utils.random import check_random_state
from sklearn.preprocessing import LabelBinarizer
from sklearn import tree
import xgboost as xgb
import lightgbm as lgb
import itertools
import math
from collections import defaultdict
import collections
from Automan.plugins.risk_trend_plot import risk_trend_plot,feature_ana_plot
from multiprocessing import Pool,cpu_count
from joblib import Parallel, delayed
from optbinning.binning.auto_monotonic import auto_monotonic_data,_auto_monotonic_decision
from optbinning.binning import OptimalBinning
from tqdm import tqdm
import numbers
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

_METRICS = {
    "binary": {
        "metrics": ["iv", "js", "gini", "quality_score"],
        "iv": {"min": 0, "max": np.inf},
        "gini": {"min": 0, "max": 1},
        "js": {"min": 0, "max": np.inf},
        "quality_score": {"min": 0, "max": 1}
    },
    "multiclass": {
        "metrics": ["js", "quality_score"],
        "js": {"min": 0, "max": np.inf},
        "quality_score": {"min": 0, "max": 1}
    },
    "continuous": {
        "metrics": []
    }
}

#日志设定
logging.basicConfig(level=logging.INFO,format = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
logger = logging.getLogger()  # initialize logging class

def setlogLevel(level):
    logger.setLevel(level)
    
#wwj增加
def miv_01(good, bad):
    # iv calculation
    infovalue = pd.DataFrame({'good':good,'bad':bad}) \
      .replace(0, 0.9) \
      .assign(
        DistrBad = lambda x: x.bad/sum(x.bad),
        DistrGood = lambda x: x.good/sum(x.good)
      ) \
      .assign(iv = lambda x: (x.DistrBad-x.DistrGood)*np.log(x.DistrBad/x.DistrGood)) \
      .iv
    # return iv
    return infovalue

def n0(x): return sum(x == 0)

def n1(x): return sum(x == 1)

def woe_01(good, bad):
    # woe calculation
    woe = pd.DataFrame({'good':good,'bad':bad}) \
      .replace(0, 0.9) \
      .assign(
        DistrBad = lambda x: x.bad/sum(x.bad),
        DistrGood = lambda x: x.good/sum(x.good)
      ) \
      .assign(woe = lambda x: np.log(x.DistrBad/x.DistrGood)) \
      .woe
    # return woe
    return woe

def get_orgin_ls(col_new,feature_map):
    origin_list=[]
    def orgin_ls_append(col,feature_map):
        # print (feature_map.loc[(feature_map["variable"]==col) & (feature_map["type"]==0),'type'].tolist())
        if feature_map.loc[(feature_map["variable"]==col) & (feature_map["type"]==0),'type'].tolist():
            # print ("col=",col)
            origin_list.append(col)
        else:
            for j in feature_map.loc[feature_map["variable"]==col,'relyon'].tolist():
                # print ("j=",j)
                orgin_ls_append(j,feature_map)
    for i in col_new:
        orgin_ls_append(i,feature_map)
    return sorted(list(set(origin_list)))

def ks_score(preds,trainDmatrix):
    from scipy.stats import ks_2samp 
    y_true = trainDmatrix.get_label()
    return 'ks',-ks_2samp(preds[np.array(y_true)==1], preds[np.array(y_true)!=1]).statistic

def rm_datetime_col(dat): # add more datatime types later
    datetime_cols = dat.dtypes[dat.dtypes == 'datetime64[ns]'].index.tolist()
    if len(datetime_cols) > 0:
        warnings.warn("There are {} date/time type columns are removed from input dataset. \n (ColumnNames: {})".format(len(datetime_cols), ', '.join(datetime_cols)))
        dat=dat.drop(datetime_cols, axis=1)
    # return dat
    return dat

def bin_str_format(bins, show_digits=4):
    # Auto
    show_digits = 4 if show_digits is None else show_digits
    return ["[{0:.{2}f}, {1:.{2}f})".format(bins[i], bins[i+1], show_digits)
            for i in range(len(bins)-1)]

def trend_decision(col_x,col_y,max_leaf_nodes=20,min_samples_leaf=0.02, miss_val = None):
    """趋势侦测函数

    Parameters
    ----------
    col_x:  pd.Series
        样本特征
    col_y: pd.Series
        样本因变量
    min_samples_leaf : float
        箱内最小限制，默认0.02
    max_leaf_nodes : int
        最大箱数，默认20
    miss_val : float
        缺失值，默认None

    Returns
    -------
    trend:str
        返回特征趋势："ascending","descending","peak","valley","NA"

    """
    missing_mask = np.isnan(col_x) | (col_x == miss_val)
    x_clean = col_x[~missing_mask]
    y_clean = col_y[~missing_mask]

    if len(x_clean) == 0:
        return "NA"

    clf = DecisionTreeClassifier(min_samples_leaf = min_samples_leaf,max_leaf_nodes=max_leaf_nodes)
    clf.fit(x_clean.values.reshape(-1,1),y_clean)

    thresholds =np.unique( clf.tree_.threshold )
    # print ("thresholds = ",thresholds)
    thresholds = thresholds[thresholds != -2]
    splits = sorted(thresholds.tolist())
    # print("trend_decision splits",col_x.name,splits)
    n_splits = len(splits)
    if n_splits > 1:
        indices = np.digitize(col_x, splits, right=False)
        # print ("indices",pd.value_counts(indices))
        n_bins = n_splits + 1

        n_nonevent = np.empty(n_bins).astype(np.int64)
        n_event = np.empty(n_bins).astype(np.int64)

        y0 = (col_y == 0)
        y1 = ~y0

        for i in range(n_bins):
            mask = (indices == i)
            n_nonevent[i] = np.sum(y0 & mask)
            n_event[i] = np.sum(y1 & mask)

        print(f"----{col_x.name}, n_nonevent= {n_nonevent} ,n_event = {n_event}")
        dict_data = auto_monotonic_data(n_nonevent, n_event)
        trend = _auto_monotonic_decision(dict_data, 'auto')
        print(f"trend = {trend} ----")
    else:
        trend = 'NA'
    return trend

def _check_variable_dtype(x):
    return "categorical" if x.dtype == np.object else "numerical"

def _effective_n_jobs(n_jobs):
    # Joblib check
    if n_jobs is None:
        n_jobs = 1
    elif n_jobs < 0:
        n_jobs = max(cpu_count() + 1 + n_jobs, 1)
    return n_jobs

def string_dealer_oot(process_note_sp,keep_list_sp,data_1,sep='^'):
    data_t = data_1.copy()
    for i in keep_list_sp:
        try:
            data_1[i].head(1)
        except:
            print('==================warning=====================================' )
            print('Cannot find column ['+i+'] in the test data and this may cause failure' )
            print('==============================================================' )
        try:
            # print ("i=",i,process_note_sp[i])
            if type(process_note_sp[i])==dict:
                # print('encoder')
                new_element_list = [item for item in list(data_1[i].unique()) if item not in list(process_note_sp[i].keys())]
                new_element_map = {}
                for item in new_element_list:
                    new_element_map[item]=random.choice(list(process_note_sp[i].values()))
                process_note_sp_combined = dict(process_note_sp[i],**new_element_map)
                data_t[i]=data_1[i].map(process_note_sp_combined)
            else:
                #print('dummies')
                am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None, output_file = None)
                data_t,dummy_col_dict=am.string_dealer_dummy_apply(data_t,[i],process_note_sp,sep)
        except Exception as e:
            print (e)
            print('==================warning=====================================' )
            print('An error happened when transform column ['+i+'] ' )
            print('==============================================================' )
    return data_t

def feature_check_and_derivation(data, feature_list, sep='^'):
    for i in feature_list:
        tmp_string = i.split(sep)
        test_none = re.search(r'\[(.+),(.+)\)',str(tmp_string[-1]))
        if test_none is not None :
            left=float(re.search(r'\[(.+),(.+)\)',str(tmp_string[-1])).group(1))
            right=float(re.search(r'\[(.+),(.+)\)',str(tmp_string[-1])).group(2))
            data[i]=data[tmp_string[0]].apply(lambda x: 1 if x>=left and x<right else 0)
    return data

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def col_type_checker(df, missing_rate=0.9, fill_mode=-9999):
    """配置文件生成器，自动判断数据类型并输出Automan所需配置文件 config_df

    Parameters
    ----------
    df:  DataFrame
        需要生成配置文件的数据
    missing_rate:list
        缺失检查阈值，默认"0.9"
    fill_mode : str
        缺失值填充，默认"-9999"

    Attributes
    ----------
    col_type_df :DataFrame
        根据数据生成的config_df
    """
    col_type_dic = {}
    for col in df.columns:
        try:
            df[col].astype(float)
            col_type_dic[col] = 'float'
        except:
            col_type_dic[col] = 'str'
    col_type_df = pd.DataFrame().from_dict(col_type_dic, orient='index', columns=['data_dtype'])
    col_type_df = col_type_df.reset_index().rename(columns={'index': 'feature_list'})
    col_type_df['missing_rate'] = missing_rate
    col_type_df['fill_mode'] = fill_mode
    print('Done')
    return col_type_df

def adj_sigmod(x,alpha=0.5):
    if x>=1:
        return (1/(1+np.exp(-(x-1))) - alpha)
    else:
        return -(1/(1+np.exp(-(1/(x+0.0001)-1))) -alpha)

def _check_is_fitted(self):
    if not self._is_fitted:
        raise NotFittedError("This {} instance is not fitted yet"
                             .format(self.__class__.__name__))

def get_opt_binning(col_x,col_y,name,min_one_cnt=0.02,max_n_prebins = 20 ,monotonic_trend ='ascending',user_splits = None,special_codes =None,verbose=False ,split_digits = 4):
    """单调优化分箱函数

    Parameters
    ----------
    col_x:  pd.Series
        样本特征
    col_y: pd.Series
        样本因变量
    min_one_cnt : float
        箱内最小限制，默认0.02
    max_n_prebins : int
        最大箱数，默认20
    user_splits : array-like or None, optional (default=None)
        用户自定义切点
    monotonic_trend : str
        单调性趋势要求:'ascending','descending',默认：'ascending'
    special_codes : list
        特殊切点，需要保留的特殊切点

    Returns
    -------
    optb:OptimalBinning
        返回optb对象

    """
    print("get_opt_binning feature = ",name)
    optb = OptimalBinning(
        min_prebin_size=min_one_cnt,
        name=name,
        dtype='numerical',
        max_n_prebins=max_n_prebins,
        monotonic_trend=monotonic_trend,
        verbose=verbose,
        user_splits =  user_splits,
        special_codes = special_codes,
        split_digits = split_digits
    )
    optb.fit(col_x, col_y)
    # for pickle
    if optb._optimizer is not None:
        try:
            optb._optimizer.solver_._CpSolver__lock = None
        except Exception as e:
            print (e)
        # optb._optimizer = None
    optb._class_logger = None
    optb._logger = None
    return optb

def check_y_is_series(y):
    if not isinstance(y,pd.Series):
        raise ValueError("target vairable must be pd.Series!")

def cost(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        start_time = time.time()
        print("-------{} is started!-------".format(func.__name__))
        res = func(self, *args, **kwargs)
        end_time = time.time()
        print("-------{} is ended ,cost {:.2f} seconds-------".format(func.__name__, end_time - start_time))
        return res
    return wrapped


class Automan_Data_Explore(object):
    """数据清洗与研判模块
    
    Parameters
    ----------
    config_file: pd.DataFrame or None
       建模配置文件.
    """

    def __init__(self,log_dict_flag=False,log_dict_unkeep_type=None,config_file=None, output_file = None):
        self.config_file=config_file
        self.config_df=None
        if self.config_file:
            print("self.config_file",self.config_file)
            self.config_df=self.read_config_data(self.config_file)

    # def __getstate__(self):
    #     """Return state values to be pickled."""
    #     d = self.__dict__.copy()
    #     d['logger']=None
    #     return d

    # def __setstate__(self, d):
    #     """Restore state from the unpickled state values."""
    #     d["logger"],d["log_file_name"],d["LOG_DICT"]=logger_creater(file_name = d["output_file"])
    #     self.__dict__.update(d)
    
    @cost
    def read_config_data(self,file=None):
        '''read_config_data
    
        Parameters
        ----------
        file: str
           配置文件名称
           
        Returns
        -------
        pd.DataFrame
            配置文件df

        '''
        
        if file:
            self.config_df = pd.read_csv(file, encoding='utf8', engine='python'
                                )
        else:
            self.config_df = pd.read_csv(self.config_file, encoding='utf8', engine='python'
                                )
        return self.config_df

    @cost
    def read_data(self,*args,**kwargs):
        '''read_data
    
        Parameters
        ----------
        同pd.read_csv()
           
        Returns
        -------
        pd.DataFrame
            建模数据df

        '''
        if self.config_df is not None:
            try:
                kwargs['dtype']=dict(zip(self.config_df['feature_list'],self.config_df['data_dtype'].replace({'float':float,'str':str})))
                return pd.read_csv(*args,**kwargs)
            except Exception as e:
                raise Exception('{error}'.format(error=e))
        else:
            return pd.read_csv(*args,**kwargs)

    @cost
    def auto_bool2str(self,data,data_type_dic):
        '''自动类型转换
    
        Parameters
        ----------
        data:pd.DataFrame
            分析样本
        data_type_dic:dict
            数据类型转换字典
           
        Returns
        -------
        data:pd.DataFrame
            处理后数据
        data_type_dic:dict
            数据类型转换字典

        '''
        for k,v in data_type_dic.items():
            if v == bool:
                print('Column '+k+' is bool type, has been converted to string type')
                self.data[k] = self.data[k].astype(str)
                data_type_dic[k] = str
            else:
                pass
        return data,data_type_dic

    @cost
    def duplicates_finder(self, data, fixed_col=[]):
        
        """查找重复数据
        
        Parameters
        ----------
        data : pd.DataFrame 
            数据集
        fixed_col : list 
            默认[] 允许重复的列，比如客户号，除此列以外，其余字段发现重复则提示
        
        Returns
        -------
        duplicate_index : list 
            重复的数据index
            
        """
        duplicate_index = []
        if fixed_col == []:
            duplicate_index.extend(list(data[data.duplicated(keep=False)==True].index))
        else:
            duplicate_index.extend(list(data[data.duplicated(subset=fixed_col,keep=False)==True].index))
        return duplicate_index

    @cost
    def delete_unuseful_inputs(self,data,del_col=[]):
        """剔除不可用的输入项 如果输入项不存在
        
        Parameters
        ----------
        data : pd.DataFrame 
            数据集
        del_col : list 
            默认[] 用户需输入不适合入模的变量，例如客户号，交易号等
            
        Returns
        -------
        cols : list 
            更新后的输入项列表
        """
        cols = list(data.columns)
        if del_col == []:
            pass
        else:
            for i in del_col:
                if  i in cols:
                    cols.remove(i)
                else:
                    print('Column '+ i + ' cannot be found in data' )
        return list(cols)

    @cost
    def check_y_label(self,data,label,task='two'):
        """标签检查:两分类，多分类，回归
        
        Parameters
        ----------
        data : DataFrame 
            数据集
        label : str 
            样本标签列名
        task : str 
            建模任务 二分类：'two' 多分类：'mulit' 回归：'reg' 
        
        Returns
        -------
        check_result : int
            0：检查通过 ，1：检查不通过
        """
        check_result = 0
        if data[label].dtype == 'O':
            print('Label is not numerical value')
        else:
            if len(data[label].unique()) == 2:
                if task=='two':
                    print('2 Class Label Checked')
                else:
                    print('2 Class Label Unmatched, Please Check the Label Column')
                    check_result = 1
            else:
                if task=='multi':
                        print('Mulit-Class Label Checked')
                if task=='reg':
                        print('Regression Label Checked')
                if task=='two':
                    print('Label Unmatched, Please Check the Label Column')
                    check_result = 1

        return check_result

    @cost
    def abnormal_value_finder(self,data,cols,a=1.5,b=3):
        """异常值检测
        
        Parameters
        ----------
        data : DataFrame 
            数据集
        cols : list 
            入模输入项
        a : float 
            默认1.5 看需求加，增加中位数标准差数据波动范围
        b : float 
            默认3 看需求加，增加平均值标准差数据波动范围
                
        Returns
        -------
        wrong_features  : list
            异常字段及数据index
        """
        wrong_features = {}
        if a is not None:
            for col in cols:
                if str(data[col].dtype) != 'object':
                    # 标准差上下三倍绝对中位差之间属于正常点
                    median = np.median(data[col])
                    #看需求加，增加数据波动范围
                    mad = a * np.median(np.abs(data[col] - median))
                    lower_limit = median - (3 * mad)
                    upper_limit = median + (3 * mad)
                    data_tmp = data[(data[col]<lower_limit)|(data[col]>upper_limit)][col]
                    if len(data_tmp)>0:
                        wrong_features[col] = list(data_tmp.index)
                else:
                    pass
        if b is not None:
            for col in cols:
                if str(data[col].dtype) != 'object':
                    # 平均值上下三倍标准差之间属于正常点
                    std = np.std(data[col])
                    mean = np.mean(data[col])
                    # b = 3
                    lower_limit = mean - b * std
                    upper_limit = mean + b * std
                    data_tmp = data[(data[col] < lower_limit) | (data[col] > upper_limit)][col]
                    if len(data_tmp)>0:
                        wrong_features[col] = list(data_tmp.index)
                else:
                    pass
        return wrong_features

    # @cost
    def fill_none(self,data,cols,mode=1,number_fill_mode=1,number_fill_value=-99,string_fill_mode=1,string_fill_value='-99',config_df=None):
        """缺失值填充
        
        Parameters
        ----------
        data : pd.DataFrame 
            数据集
        cols : list 
            入模输入项
        mode : int 
            默认1, 1:统一填充： 2:根据config_df配置文件里的设置填充
        number_fill_mode : int 
            默认1, 1:固定数值填充：  2:均值填充
        number_fill_value : int 
            默认-99 固定数值
        string_fill_mode : int 
            默认1 1:固定数值填充：  2:众数填充：
        string_fill_value : str 
            默认'-99' 固定数值
        config_df :  DataFrame 
            配置文件 默认None
                
        Returns
        -------
        data  : DataFrame 
            填充后的data
        """
        from pandas.api.types import is_numeric_dtype

        #value_check
        if not isinstance(data,pd.DataFrame):
            raise ValueError("data should be DataFrame!")

        if not isinstance(cols,(list,tuple)):
            raise ValueError("data should be list or tuple!")

        if mode==2:
            if not isinstance(config_df,pd.DataFrame):
                raise ValueError("config_df should be DataFrame!")
            if 'fill_mode' not in list(config_df.columns):
                raise ValueError("config_df should have fill_mode!")

        if mode==1:
            if number_fill_mode not in [1,2]:
                raise ValueError("number_fill_mode should in [1,2]")
            else:
                if number_fill_mode == 1 and  not isinstance(number_fill_value,(int,float)):
                    raise ValueError("number_fill_value should in be int or float")

            if string_fill_mode not in [1,2]:
                raise ValueError("string_fill_mode should in [1,2]")

        #start processing
        data = data.copy(deep=True)
        if mode==1:
            for col in cols:
                if is_numeric_dtype(data[col]):
                    #固定值填充
                    if number_fill_mode==1:
                        data[col].fillna(number_fill_value,inplace=True)
                    #均值填充
                    if number_fill_mode==2:
                        mean_val = data[col].mean()
                        data[col].fillna(mean_val, inplace=True)
                else:
                    #固定值填充
                    if string_fill_mode==1:
                        data[col].fillna(string_fill_value,inplace=True)
                    #众数填充
                    if string_fill_mode==2:
                        data[col].fillna(data[col].mode(), inplace=True)

        if mode==2:
            for col in cols:
                data[col].fillna(list(config_df.loc[config_df['feature_list']==col,'fill_mode'])[0],inplace=True)

        return data

    def encode_category_with_index_dict(self,data, category_col):
        """自定义labelencoder（保留映射记录）
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集
        category_col : list
            入模输入项
        
        Returns
        -------
        data  : pd.DataFrame
            labelencoder后数据集
        category_dict : dict
            转化记录
        """
        category_dict = data[category_col].value_counts()
        category_dict = pd.Series(np.arange(0, len(category_dict)), index=category_dict.index).to_dict()
        data[category_col] = data[category_col].map(category_dict).astype('int32')
        return data[category_col],category_dict

    @cost
    def string_dealer(self,data,cols,dummies_limit = 10,sep="^"):
        """输出型处理函数
        
        Parameters
        ----------
        data : DataFrame 
            数据集
        cols : list 
            入模输入项
        dummies_limit : int 
            默认10 字符变量label_encoder转化阈值，大于使用label_encoder，小于使用哑变量
        
        Returns
        -------
        data  : DataFrame
            加工后的数据
        dummies_col : list 
            转化后的输入项
        process_note : dict 
            转化映射记录
        """
        process_note = {}
    #    dummies_col = [y for y in (pass_cols+cols) if y not in [x for x in cols if x in pass_cols]]
        col_new = cols.copy()
        dummies_col=data[col_new].dtypes[data[col_new].dtypes=='object'].index.tolist()
    
        #值小于设定阈值的进行label_encoder处理
        for col in dummies_col:
            # print("col=",col)
            if len(data[col].unique())>=dummies_limit:
                data[col], procees_dic = self.encode_category_with_index_dict(data, col)
                process_note[col] = procees_dic
            elif len(data[col].unique())<dummies_limit:
                enc=LabelBinarizer()
                enc.fit(data[col].astype(str).values.reshape(-1,1))
                process_note[col]=enc
                data,dummy_col_dict=self.string_dealer_dummy_apply(data,[col],process_note,sep=sep)
                col_new.extend(dummy_col_dict[col])
                col_new.remove(col)
        print('Done')
        return data, col_new, process_note

    def string_dealer_dummy_apply(self,data,cols,process_note,sep="^"):
        """输出型处理应用函数
        
        Parameters
        ----------
        data : DataFrame 
            数据集
        cols : list 
            入模输入项
        process_note : dict 
            变量对应关系
        sep:str
            生成变量分割符号
        
        Returns
        -------
        data  : DataFrame
            加工后的数据
        dummy_col_dict : dict 
            转化映射记录
        """
        dummy_col_dict={}
        for col in cols:
            # print ("apply col=",col)
#            print ("bbb a=",data.columns.tolist())
            # print ("col a=",list(process_note.keys()))
            if col in list(process_note.keys()) and col in data.columns.tolist():
                if isinstance(process_note[col],LabelBinarizer):
                    if len(process_note[col].classes_)==2:
                        dummy_col=[col +sep + str(i) for i in process_note[col].classes_][-1:]
                        # dummy_col=[col +sep + str(i) for i in process_note[col].classes_]
                    else:
    #                    dummy_col=[col +sep + str(i) for i in range(len(process_note[col].classes_))]
                        dummy_col=[col +sep + str(i) for i in process_note[col].classes_]
                    # print('haha',data[col].astype(str).values.reshape(-1,1).shape,data[col].dtype)
                    # print('haha2',dummy_col,process_note[col].classes_,process_note[col].transform(data[col].astype(str).values.reshape(-1,1)))
                    if len(process_note[col].classes_)==2:
                        df=pd.DataFrame([1 if j == process_note[col].classes_[-1]   else 0  for j in data[col] ],columns=dummy_col,index=data.index)
                    else:
                        df=pd.DataFrame(process_note[col].transform(data[col].astype(str).values.reshape(-1,1)),columns=dummy_col,index=data.index)
                    # print ('df:',df)
                    data.drop(columns= set(df.columns) & set(data.columns),inplace=True)

                    data = pd.concat([data, df], axis=1)
                    dummy_col_dict[col]=dummy_col
        return data,dummy_col_dict

    @cost
    def tree_split(self,data,cols,target,max_bin = 5,min_binpct=0.05,nan_value=-99,split_data_rate = 0.6):
        """决策树分箱
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集 
        cols : list
            入模输入项
        target : string
            标签的字段名
        max_bin : int
            默认5 最大分箱数
        min_binpct : float
            默认 0.05 箱体的最小占比
        nan_value : int
            默认-99 缺失的映射值 
        split_data_rate : float
            默认0.6 使用总样本集的多少进行划分，默认0.6
            
        Returns
        -------
        split_list_dic : dict
            分割字典
        """
        data_tmp = data[:int(len(data) * split_data_rate)]
        split_list_dic ={}
        for col in cols:
            # print("col=",col)
            miss_value_rate = data_tmp[data_tmp[col] == nan_value].shape[0] / data_tmp.shape[0]
            # 如果缺失占比小于5%，则直接对特征进行分箱
            if miss_value_rate < 0.05:
                x = np.array(data_tmp[col]).reshape(-1, 1)
                y = np.array(data_tmp[target])
                tree = DecisionTreeClassifier(max_leaf_nodes=max_bin,
                                              min_samples_leaf=min_binpct)
                tree.fit(x, y)
                thresholds = tree.tree_.threshold
                thresholds = thresholds[tree.tree_.feature != -2]
    #             thresholds = thresholds[thresholds != _tree.TREE_UNDEFINED]
                split_list = sorted(thresholds.tolist())
            # 如果缺失占比大于5%，则把缺失单独分为一箱，剩余部分再进行决策树分箱
            else:
                max_bin2 = max_bin - 1
                x = np.array(data_tmp[~(data_tmp[col] == nan_value)][col]).reshape(-1, 1)
                y = np.array(data_tmp[~(data_tmp[col] == nan_value)][target])
                tree = DecisionTreeClassifier(max_leaf_nodes=max_bin2,
                                              min_samples_leaf=min_binpct)
                tree.fit(x, y)
#                print(tree.tree_.threshold,"feature=",tree.tree_.feature)
                thresholds = tree.tree_.threshold
                thresholds = thresholds[tree.tree_.feature != -2]
                split_list = sorted(thresholds.tolist())
                split_list.insert(0, nan_value+0.001)
            split_list.insert(0, float('-inf'))
            split_list.append(float('inf'))
            split_list_dic[col] = split_list
        return split_list_dic

    @cost
    def get_tree_cut(self,df, fea, y, max_cuts=5, min_one_cnt=0.05,miss_val=-99):
        """决策树分箱
        
        Parameters
        ----------
        df : pd.DataFrame
            数据集 
        fea : str
            入模输入项
        y : string
            标签的字段名
        max_cuts : int
            默认5 最大分箱数
        min_one_cnt : float
            默认 0.05 箱体的最小占比
        miss_val : int
            默认-99 缺失的映射值 
            
        Returns
        -------
        fea_cuts : dict
            分割字典
        """
        fea_cuts = dict()
        cuts = []
        for x in fea:
            # print (x)
            if pd.api.types.is_string_dtype(df[x]):
                pass
            else:
                # print("----in cut----")
                clf = tree.DecisionTreeClassifier(min_samples_leaf=min_one_cnt, max_leaf_nodes=max_cuts)
                trainX=df.loc[df[x]!=float(miss_val),x]
#                print ("index=",df.loc[df[x] != miss_val].index)
                trainY=df.loc[df[x]!=float(miss_val),y]
                if len(trainX.values.reshape(-1,1)) == 0:
                    fea_cuts[x] = [-np.inf,miss_val+0.001,np.inf]
                    continue
                
                clf.fit(trainX.values.reshape(-1,1), trainY.values)
                # print("haha2")
#                print (clf.tree_.threshold,"feature=",clf.tree_.feature)
                cuts=list(set(list(clf.tree_.threshold[clf.tree_.feature != -2])))
                cuts.append(float('inf'))
                cuts.append(float('-inf'))
                cuts.append(miss_val+0.001)
                cuts=sorted(list(set(map(lambda x:round(x,4) , cuts))))
                fea_cuts[x] = sorted(cuts)
                # print("fea_cuts",fea_cuts,cuts)
            # clf.fit(x.reshape(-1, 1), y)

        return fea_cuts
    
    @cost
    def get_percent_cut(self, data, col_x, perc=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], missing=-99):
        """分位数分箱
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集 
        col_x : list
            入模输入项
        perc : list
            分位数 eg: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        missing : int
            默认-99

        Returns
        -------
        fea_cuts : dict
            分割字典
        """
        fea_cuts = dict()
        cuts = []
        for i in col_x:
            # print (i)
            if pd.api.types.is_string_dtype(data[i]):
                pass
            else:
                cuts = list(data[i].quantile(perc).drop_duplicates().values)
        #        print(cuts)
                cuts=list(set(cuts))
                cuts.sort()
                if min(cuts) >= missing:
                    cuts[0] = missing +0.001
                cuts.insert(0,float('-inf'))
                cuts[-1] = float('inf')
                cuts=sorted(list(set(map(lambda x:round(x,4) , cuts))))
                fea_cuts[i] = sorted(cuts)
    #        print ("cuts=",cuts)
        return fea_cuts

    def bin_df(self,data,col,split_list,target):
        """分箱计算好坏率及woe
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集 
        col : str
            分箱的字段名
        split_list : list
            分箱列表
        target : str
            样本标签
        
        Returns
        -------
        bin_df : pd.DataFrame
            切分报告
        """
        total = data[target].count()
        bad = data[target].sum()
        good = total-bad
        bucket = pd.cut(data[col],split_list)
        group = data.groupby(bucket)
        bin_df = pd.DataFrame()
        bin_df['total'] = group[target].count()
        bin_df['bad'] = group[target].sum()
        bin_df['good'] = bin_df['total'] - bin_df['bad']
        bin_df['badattr'] = bin_df['bad'] / bad
        bin_df['goodattr'] = bin_df['good'] / good
        bin_df['goodrate'] = bin_df['good'] / bin_df['total']
        bin_df['badrate'] = bin_df['bad'] / bin_df['total']
        bin_df['binbadrate|avgbadrate'] = bin_df['badrate']/(bad/total)
        bin_df['woe'] = np.log(bin_df['badattr'] / bin_df['goodattr'])
        bin_df['bin_iv'] = (bin_df['badattr'] - bin_df['goodattr']) * bin_df['woe']
        bin_df['IV'] = bin_df['bin_iv'].sum()
        return bin_df

# 样本稳定性分析 
    @cost
    def stability_estimator(self,data,cols,split_list_dic,target,std_limit=0.1):
        """样本稳定性分析  （废弃）
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集 
        cols : list
            入模列名列表
        split_list_dic : dict
            分箱切点字典
        target : str
            样本标签
        std_limt : float
            跨样本方差检验
        
        Returns
        -------
        data : pd.DataFrame
            新数据
        new_cols : list
            新入模字段列表
        unstable_cols : list
            不稳定列名
        """
        unstable_cols = {}
        new_cols = cols.copy()
        for col in cols:
            # print(col+' start')
            bad_rate_list = []
            unstable_bins = []
            # new_cols=[]
            for i in range(len(data['data_parts'].unique())):
                if i == 0:
                    tmp_df = self.bin_df(data[data['data_parts'] == i + 1],col,split_list_dic[col],target)
                    data_bin = tmp_df['binbadrate|avgbadrate']
                else:
                    tmp_df = self.bin_df(data[data['data_parts'] == i + 1],col,split_list_dic[col],target)
                    data_bin = pd.concat([data_bin, tmp_df['binbadrate|avgbadrate']], axis=1,
                                             join_axes=[data_bin.index])
            for i in range(len(data_bin)):
                bad_rate_list.append(np.std(data_bin.iloc[i]))
                for std in bad_rate_list:
                    if std>std_limit:
                        print('column '+col+ 'has a bad rate unstable bin '+ str(data_bin.index[i]))
                        unstable_cols[col]=str(data_bin.index[i])
                        unstable_bins.append(i)
            if len(unstable_bins)>0:
                # print(col)
                ##对原变量进行哑变量加工
                data['group'] = pd.cut(data[col],split_list_dic[col],labels=[i for i in range(len(data_bin))])
                data['group'] = data['group'].apply(lambda x: '-1000' if x in unstable_bins else str(x))
                data_tmp_dummies = pd.get_dummies(data['group'].astype('str'), prefix=col, prefix_sep='_')
    
                data = pd.concat([data, data_tmp_dummies], axis=1)
                new_cols.extend(list(data_tmp_dummies.columns))
    #             print(list(data_tmp_dummies.columns))
    #             print(new_cols)
                new_cols.remove(col)
                new_cols.remove(col + '_-1000')
        return data,new_cols,unstable_cols

    @cost
    def auto_type_converter(self,data):
        """自动变量转换
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集
            
        Returns
        -------
        data : pd.DataFrame
            转换后的数据集
        """
    #     是否将数字类型的变量强制识别转换，避免成为object
    #     data = data.convert_objects(convert_numeric=True)
        for col in list(data.columns):
            if data[col].dtype == float:
                pass
            elif data[col].dtype == int:
    #             print(col+' : '+str(data[col].dtype)+' type has been convert to float type')
                data[col] = data[col].astype(float)
            else:
    #             print(col+' : '+str(data[col].dtype)+' type has been convert to string type')
                data[col] = data[col].astype(str)
        return data 

    @cost
    def split_data_for_model(self,data,orderby=False,train_ratio = 0.6,val_test_ratio=0.5,label='is_bad',random_seed = 88):
        """样本切分
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集
        orderby : str or bool
            是否根据某列将数据进行递增排序，例如根据交易时间对样本排序，默认乱序打乱重排
        train_ratio : float
            训练样本占总样本比例
        val_test_ratio : float
            验证集：测试集（总样本减去训练样本后， 剩余样本划分成验证和测试集）
        random_seed : int
            随机数种子，默认88 
        
        Returns
        -------
        data : pd.DataFrame
            重新排序后的数据
        train_data : pd.DataFrame
            训练集
        val_data : pd.DataFrame
            验证集
        test_data : pd.DataFrame
            测试集
        """
        label_rate = []
        try:
            sorted(list(data.data_split.unique()))==['test_data', 'train_data', 'val_data']
            print('data_split detected')
            train_data=data[data.data_split=='train_data']
            val_data=data[data.data_split=='val_data']
            test_data=data[data.data_split=='test_data']
        except:    
            np.random.seed(random_seed)
            if orderby=='random':           
    #             #打乱重排
                data=data.sample(frac=1,random_state = random_seed).reset_index(drop=True)
            elif orderby==False:
                pass
            else:
                #根据某列排序
                data.sort_values(by=orderby,ascending=True,inplace=True)
                data=data.reset_index(drop=True)
            # 训练数据
            train_offset = int(len(data) * train_ratio)
            train_data = data[:train_offset]
            label_rate.append(round(train_data[label].sum()/len(train_data),3))
            other_data = data[train_offset:].reset_index(drop=True)
            #验证+测试
            val_offset = int(len(other_data) * val_test_ratio)
            val_data = other_data[:val_offset]
            label_rate.append(round(val_data[label].sum()/len(val_data),3))
            test_data = other_data[val_offset:]
            label_rate.append(round(test_data[label].sum()/len(test_data),3))
            print('Data has been divided into 3 parts. \n'+'There are train_data, val_data and test_data with label rates: '+str(label_rate)+'.')
        return data,train_data,val_data,test_data

    @cost
    def split_data(self,data,orderby=False,split_ratio='6:2:2',label='is_bad',random_seed=88):
        """样本自定义切分
        
        Parameters
        ----------
        data : pd.DataFrame
            数据集 （如果样本中存在data_parts字段，则默认使用原样本的data_parts字段进行样本切分，否则根据用户输入比例切分）
        orderby : str or False
            默认 False 是否根据某列将数据进行递增排序，例如根据交易时间对样本排序，默认乱序重排
        split_ratio : str
            string 默认'6:2:2' 样本切分比例（决定跨样本检验样本份数）
        label : str
            样本标签
        random_seed : int
                默认88 随机数种子
        
        Returns
        -------
        data_new : DataFrame
            切分后的数据，子样本由data_parts字段判断
        """
        label_rate = []
        try:
            for i in sorted(list(data['data_parts'].unique())):
                data_tmp = data[data.data_parts==i]
                label_rate.append(round(data_tmp[label].sum()/len(data_tmp),3))
            print('data_prats detected')
            print('Data has been divided into ' + str(len(data['data_parts'].unique())) + ' parts. \n'+'There are ' + str(
                data['data_parts'].unique()) + ' with label rates: '+str(label_rate)+'.')
            data_new = data.copy()
        except: 
            np.random.seed(random_seed)
            if orderby=='random':
                #打乱重排
                data=data.sample(frac=1,random_state = random_seed).reset_index(drop=True)
            elif orderby==False:
                pass
            else:
                #根据某列排序
                data.sort_values(by=orderby,ascending=True,inplace=True)
                data=data.reset_index(drop=True)
            split_list = split_ratio.split(':')
            split_list_int = [int(x) for x in split_list]
            split_list_sum = sum(split_list_int)
            split_index = []
    #         label_rate = []
            temp_df = pd.DataFrame()
            data_new = pd.DataFrame()
            for i, value in enumerate(split_list_int):
                if i == 0:
                    offset = int(len(data) * (value / split_list_sum))
                    data_new = data[:offset]
                    data_new['data_parts'] = i + 1
                    label_rate.append(round(data_new[label].sum()/len(data_new),3))
                    split_index.append(offset)
                elif i != (len(split_list_int)-1):
                    offset_tmp = offset + int(len(data) * (value / split_list_sum))
                    temp_df = data[offset:offset_tmp]
                    offset = offset_tmp
                    label_rate.append(round(temp_df[label].sum() / len(temp_df),3))
                    temp_df['data_parts'] = i + 1
                    data_new = pd.concat([data_new, temp_df])
                    split_index.append(offset)
                else:
                    temp_df = data[offset:]
                    label_rate.append(round(temp_df[label].sum() / len(temp_df),3))
                    temp_df['data_parts'] = i + 1
                    data_new = pd.concat([data_new, temp_df])                
            print('Data has been divided into ' + str(len(data_new['data_parts'].unique())) + ' parts. \n'+'There are ' + str(data_new['data_parts'].unique()) +' with split index: '+ str(split_index)+' and label rates: '+str(label_rate)+'.')
        return data_new

    @cost
    def missing_checker(self,data,cols,missing_threshold=0.8,std_check=None,std_check_col=None):
        """缺失值检查
        
        Parameters
        ----------
        data : pd.DataFrame 
            数据集
        cols : list 
            入模输入项
        missing_threshold : float
            默认0.8 缺失率容忍上限 
        std_check : bool
            默认None, 多样本缺失率标准差筛选
        std_check_col : list
            默认 None 标准差检查列
            
        Returns
        -------
        keep_list_new : list
            保留建模字段列表
        df_report : pd.DataFrame
            缺失率报告
        """
        #check input Parameters
        df_report=pd.DataFrame()
        keep_list=[]
        if isinstance (missing_threshold,pd.DataFrame):
            missing_threshold=missing_threshold.reset_index(drop=False)
            if not {"feature_list","missing_rate"}.issubset( set(missing_threshold.columns)):
                raise Exception("missing_threshold has not columns [feature_list,missing_rate]")
        else:
            if not 0<= missing_threshold <=1:
                raise ValueError("missing_threshold range must be [0,1]")
        
        if std_check is not None :
            if not isinstance("std_check_col",str):
                raise ValueError("std_check_col range must string")
            if std_check_col not in list(data.columns):
                raise ValueError("std_check_col not in data.columns")
    
        #计算空值率：
        percent = data.isnull().sum() / data.shape[0]
        
        if isinstance (missing_threshold,pd.DataFrame):
            df_report=missing_threshold
        else:
            df_report=pd.DataFrame({"feature_list":list(data.columns),"missing_rate":missing_threshold})
            
        #缺失率检查
        df_report=df_report.merge(percent.reset_index(name='real_missing_rate').rename(columns={"index":"feature_list"}),on='feature_list')
        df_report["na_check_result"]=df_report["real_missing_rate"] >= df_report["missing_rate"]
        df_na_pos=pd.DataFrame({"feature_list":list(data.columns),"na_check_pos":[data[i][data[i].isnull()].index.tolist()[0:5] for i in list(data.columns)]})
        df_report=df_report.merge(df_na_pos,on='feature_list')
        
        #多样本下缺失率标准差检查
        if std_check:
            df_std_check=data.groupby([std_check_col]).apply(lambda x:x.isnull().sum()/len(x)).T.apply(lambda x:np.std(x),axis=1).reset_index(name='real_std').rename(columns={"index":"feature_list"})
            df_report=df_report.merge(df_std_check,on='feature_list')
            df_report["na_std_check_result"]=df_report["real_missing_rate"] >=std_check
            keep_list=df_report.loc[~(df_report["na_check_result"] | df_report['na_std_check_result']),"feature_list"].tolist()
        else:
            keep_list=df_report.loc[~df_report["na_check_result"],"feature_list"].tolist()
        keep_list_new = list(set(keep_list).intersection(set(cols))) 
        return keep_list_new,df_report

    @cost
    def data_type_checker(self,data,cols):
        """数据类型检查
        
        Parameters
        ----------
        data : pd.DataFrame 
            数据集
        cols : list 
            入模输入项
        config_df : DataFrame
            配置文件
            
        Returns
        -------
        keep_list : list
            保留建模字段列表
        """
        from pandas.api.types import is_string_dtype
        from pandas.api.types import is_numeric_dtype
        #type_mismatch_col = []
        keep_list=[]
        if self.config_df is not None:
            for col in cols:
        #        print ("col=",col)
                if col not in list(self.config_df["feature_list"]):
                    print('Column [' + col + '] cannot be found in the config_df.feature_list')
                else:
                    if (is_numeric_dtype(data[col]) and list(self.config_df.loc[self.config_df["feature_list"]==col,"data_dtype"])[0] in ('float',float)) or\
                       (is_string_dtype(data[col]) and list(self.config_df.loc[self.config_df["feature_list"]==col,"data_dtype"])[0] in ('str',str)):
                        keep_list.append(col)
                    else:
                        # print(str(data[col].dtype))
                        print('Column ' + col + ' has a different data type expected is {} real is {}'.format(str(list(self.config_df.loc[self.config_df["feature_list"]==col,"data_dtype"])[0]),str(data[col].dtype)))
                        #type_mismatch_col.append(col)
        else:
            print('Warning: In order to excute data_type_checker, config_df is essential')
        return keep_list

    def feature_ana(self,data,col_x,y,var_bin_dic,graph="",prefix="",var_dic={},bet=1):
        print(col_x)
        if not pd.api.types.is_string_dtype(data[col_x]):
            cuts=var_bin_dic[col_x]
            temp = pd.cut(data[col_x], cuts, right=False,precision=4)
            result_plot = pd.crosstab(data[y], temp,dropna=False).T
        else:
            temp=data[col_x]
            result_plot = pd.crosstab(data[y], temp.astype(str)).T
        result_plot = result_plot.rename(columns={0:'No',1:'Yes'})
        result_plot = result_plot.reindex(columns=['Yes', 'No'])
        iv = sum(miv_01(result_plot.No,result_plot.Yes))
        avg_risk=round(sum(result_plot.Yes) / sum(result_plot.Yes + result_plot.No),4)
        temp_df=result_plot.copy(deep=True)

        temp_df=temp_df.reset_index().rename(columns={col_x: 'group'})
        temp_df["var"]=col_x
        temp_df["p0"]=temp_df.apply(lambda x : x['No']/(x['Yes']+x['No']) if x['Yes']+x['No']>0 else avg_risk,axis=1)
        temp_df["p1"]=temp_df.apply(lambda x : x['Yes']/(x['Yes']+x['No']) if x['Yes']+x['No']>0 else avg_risk,axis=1)
        temp_df['count'] = temp_df['No'] +  temp_df['Yes']
        temp_df['count_distr'] = temp_df['count']/sum( temp_df['count'])
        temp_df['bin_iv'] = miv_01(temp_df['No'], temp_df['Yes'])
        temp_df['total_iv'] = sum(temp_df['bin_iv'])
        temp_df['woe'] = woe_01(temp_df['No'], temp_df['Yes'])
        temp_df['avg_risk'] = avg_risk
        temp_df['sum_yes'] = temp_df['Yes'].sum()
        temp_df['sum_no'] = temp_df['No'].sum()
        temp_df.loc[temp_df['count']==0,'woe']=0

        temp_df['is_monotonic'] = 1 if temp_df.loc[~temp_df.group.astype(str).str.contains('-inf, -9'),'p1'].is_monotonic_increasing \
            else 2 if temp_df.loc[~temp_df.group.astype(str).str.contains('-inf, -9'),'p1'].is_monotonic_decreasing else 0
        cut_off_bin=np.unique(list(map(float, ['-inf'] + [re.search(r'\[(.*),(.*)\)', str(grp)).group(1) for grp in temp_df.group] + ['inf'])))
        ks = pd.DataFrame()
        ks['r'] = data[y].values
        ks['x'] = pd.cut(data[col_x], bins=cut_off_bin, right=False).astype(str).map(dict(zip(temp_df['group'].astype(str), temp_df['p1']))).values
        temp_df['ks']=round(ks_2samp(ks[ks['r'] == 0]['x'], ks[ks['r'] == 1]['x']).statistic, 4)
        temp_df['bet'] = temp_df.p1/(sum(temp_df.Yes) / sum(temp_df.Yes + temp_df.No))

        # detail_df = pd.concat([
        #     detail_df,
        #     temp_df
        # ])

        # rtn_dict[col_x] = cuts
        if graph!='':
            a = result_plot.T / (result_plot.replace(0, 0.9).sum(axis=1))
            a = a.T
            labelizer_dic = {}
            for s in a.index:
                for t in a.columns:
                    labelizer_tup = (str(s), t)
                    labelizer_dic[labelizer_tup] = '%.2f%%' % (a.ix[s, t] * 100)
            labelizer = lambda k: labelizer_dic[k]
            props = lambda key: {'color': 'coral' if 'Yes' in key else 'silver'}
            # print(result_plot.stack().dtype)
            result_plot['Yes'] = result_plot['Yes'] * bet #响应率倍数
            result_plot.index=result_plot.index.astype("object")
            mosaic(result_plot.stack(), title='{}|IV={:.3f}'.format(var_dic[col_x] if col_x in var_dic.keys() else col_x ,iv), properties=props, labelizer=labelizer,label_rotation=90)
            # pylab.show()
            plt.text(1.05, 1.05, '样本量：'+'%.2f'%(len(data)) )
            plt.text(1.05, 1, '平均响应率：'+'%.2f'%(data[y].sum()/data.shape[0] ))
            pylab.savefig((graph + '{}_{}.png').format(var_dic[col_x] if col_x in var_dic.keys() else col_x,prefix),pad_inches=0.3,dpi=100,bbox_inches='tight')
            pylab.close()
        return col_x,temp_df,cuts,iv

#    @cost
    def data_feature_analysis_solo(self,data,y,ilx,var_bin_dic,order=True,graph="",prefix="",var_dic={},bet=1,dp=None,n_jobs=-1):
        '''单样本特征稳定性分析
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集
        y: str
            y变量名称
        ilx: list
            x变量list
        var_bin_dic: dict
            变量切点位置eg: {'social_cnt_diff': [-inf, -999998, -0.5, 1.5, inf],\
                            'romance_cnt_diff': [-inf, -999998, inf],\
                            'communications_cnt_diff': [-inf, -999998, -0.5, 0.5, inf]}
        
        detail:bool
            True or False 是否输出明细结果
        order :bool
            True or False 是否iv排序
        graph:str
            输出文件路径
        prefix:str
            输出文件后缀
        var_dic:dict
            变量命名映射
        bet:float
            图形响应率倍数
        
        Returns
        -------
        dict
            输出字典
        '''
        i = 0
        detail_df=pd.DataFrame()
        rtn_dict={}
        out = Parallel(n_jobs=n_jobs,backend='threading')(delayed(self.feature_ana)(data[[col_x,y]],col_x,y,var_bin_dic,graph,prefix,var_dic,bet) for col_x in ilx)

        detail_df = [k[1] for k in out]
        rtn_dict = {k[0]:k[2] for k in out}
        voi_list = pd.Series({k[0]:k[3] for k in out})
        detail_df = pd.concat(detail_df,axis=0,ignore_index=True)
        if order:
            voi_list= voi_list.sort_values(ascending=False)
    
        detail_df=detail_df.rename(columns={"group":"bin","var":"variable"})
        detail_df['bet_adj'] = detail_df['bet'].apply(adj_sigmod)
        detail_df=detail_df.reindex(columns=['variable', 'bin','count','count_distr','Yes','No','p0','p1','bin_iv','total_iv','woe','is_monotonic','ks','bet','bet_adj','avg_risk','sum_yes','sum_no'])
        detail_df['bin']=detail_df['bin'].astype(str).str.replace(" ","")
        if dp:
            return {dp:detail_df}
        else:
            return {'iv': voi_list, 'dtl': detail_df,'cut':rtn_dict}

    @cost
    def data_feature_analysis(self,data,dummies_col,split_list_dic,y,graph='',bet=1,data_parts = None,n_jobs=1):
        '''变量稳定性分析
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集
        dummies_col: list
            x变量list
        split_list_dic: dict
            变量切点位置eg: {'social_cnt_diff': [-inf, -999998, -0.5, 0.5, inf],\
                 'romance_cnt_diff': [-inf, -999998, inf],\
                 'communications_cnt_diff': [-inf, -999998, -0.5, 0.5, inf]}
        y: str
            y变量名称
        graph:str
            默认'',''代表不输出，如果配置则输出到文件路径
        bet:int
            默认1，响应率放大倍数
        data_parts:str
            data_parts输出字段
        
        Returns
        -------
        feature_ana_df:pd.DataFrame
            单变量分析报告
        '''
        feature_ana_dic={}
        feature_ana_df=pd.DataFrame()
        if data_parts:
            print (data_parts)
            # if n_jobs ==1:
            for i in data[data_parts].unique():
                # print('data_parts=',i)
                feature_ana_dic[i]=self.data_feature_analysis_solo(data[data[data_parts]==i].reset_index(drop=True)
                ,y
                ,dummies_col
                ,split_list_dic
                ,order=True
            #    ,graph='D:\\work\\study\\PYEX\\Automan\\test1\\pic\\'
                ,graph=graph
                ,prefix=str(i)
                ,var_dic={}
                ,bet=bet
                ,n_jobs=n_jobs)['dtl']
            feature_ana_df=pd.concat(feature_ana_dic).reset_index()\
                    .drop('level_1', axis=1)\
                    .rename(columns={'level_0':data_parts})
            return feature_ana_df.reset_index(drop=True)
        else:
            feature_ana_df=self.data_feature_analysis_solo(data
            ,y
            ,dummies_col
            ,split_list_dic
            ,order=True
        #    ,graph='D:\\work\\study\\PYEX\\Automan\\test1\\pic\\'
            ,graph=graph
            ,var_dic={}
            ,bet=bet
            ,n_jobs=n_jobs)['dtl']
            return feature_ana_df.reset_index(drop=True)

    @cost
    def data_feature_analysis2(self,data, dummies_col, split_list_dic,data_parts = None):
        '''无监督变量稳定分析
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集
        dummies_col: list
            x变量list
        split_list_dic: dict
            变量切点位置eg: {'social_cnt_diff': [-inf, -999998, -0.5, 0.5, inf],\
                            'romance_cnt_diff': [-inf, -999998, inf],\
                            'communications_cnt_diff': [-inf, -999998, -0.5, 0.5, inf]}
        data_parts:str
            data_parts样本划分字典，如果为None则代表单样本
        
        Returns
        -------
        feature_ana_df:pd.DataFrame
            单变量分析报告
        '''
        feature_ana_dic={}
        feature_ana_df=pd.DataFrame()
        if data_parts:
            for i in data[data_parts].unique():
                feature_ana_dic[i]=self.data_feature_analysis_solo2(data[data[data_parts]==i].reset_index(drop=True)
                ,dummies_col
                ,split_list_dic)
                feature_ana_df=pd.concat(feature_ana_dic).reset_index()\
                        .drop('level_1', axis=1)\
                        .rename(columns={'level_0':data_parts})
            return feature_ana_df
        else:
            feature_ana_df=self.data_feature_analysis_solo2(data
            ,dummies_col
            ,split_list_dic
            )
            return feature_ana_df

    @cost
    def data_feature_analysis_solo2(self,df, col_x, breaks_dic):
        '''无监督单样本变量稳定分析
        
        Parameters
        ----------
        df: pd.DataFrame
            数据集
        col_x: list
            x变量list
        breaks_dic: dict
            变量切点位置eg: {'social_cnt_diff': [-inf, -999998, -0.5, 0.5, inf],\
                            'romance_cnt_diff': [-inf, -999998, inf],\
                            'communications_cnt_diff': [-inf, -999998, -0.5, 0.5, inf]}
        
        Returns
        -------
        detail_df:pd.DataFrame
            单变量分析报告
        '''
        detail_df=pd.DataFrame()
        for x_name in  col_x:
            if pd.api.types.is_numeric_dtype(df[x_name]):
                temp = pd.cut(df[x_name], breaks_dic[x_name], right=False,precision=4)
                binning = temp.groupby(temp).count().rename('count').reset_index().rename(columns={x_name:'bin'})
                
                binning['variable'] =x_name
                binning['count_distr'] =binning['count']/binning['count'].sum()
#            print("binning",binning)
                detail_df = pd.concat([
                    detail_df,
                    binning
                ])
        detail_df['bin']=detail_df['bin'].astype(str).str.replace(" ","")
        return detail_df

    @cost
    def psi_calc(self,feature_ana_df,data_parts='data_parts'):
        '''psi计算
        
        Parameters
        ----------
        feature_ana_df: pd.DataFrame
            数据集
        data_parts:str
            默认'data_parts',样本划分字段
        
        Returns
        -------
        dt_sl_psi:pd.DataFrame
            psi计算数据集
        '''
        dt_sl_psi=feature_ana_df.pivot_table(values=['count_distr'],index=['variable','bin'],columns=data_parts)
        for i in itertools.combinations(feature_ana_df[data_parts].unique(), 2):
            # print (i[0],i[1],"_".join(map(str,[data_parts,i[0],"vs",i[1]])))
            dt_sl_psi["_".join(map(str,[data_parts,i[0],"vs",i[1]]))]=\
                (dt_sl_psi.xs(("count_distr",i[0]),axis=1).replace(0,0.01) - dt_sl_psi.xs(("count_distr",i[1]),axis=1).replace(0,0.01))\
                * np.log(dt_sl_psi.xs(("count_distr",i[0]),axis=1).replace(0,0.01) / dt_sl_psi.xs(("count_distr",i[1]),axis=1).replace(0,0.01))
            dt_sl_psi["_".join(map(str,[data_parts,i[0],"vs",i[1],"psi"]))]=dt_sl_psi["_".join(map(str,[data_parts,i[0],"vs",i[1]]))].groupby('variable').transform(sum)
        return dt_sl_psi
    
    @cost
    def feature_resp_std_check(self,feature_ana_df,cols,std_limit=0.3
                               # ,lin_limit=0.3,bin_check_mode='std'
                               ,data_apply = None,sep='^',high_lift_limit=1,low_lift_limit=1,lift_tolerance_cnt=0
                               ,corr_stablity_limit=0.5,miss_val=-99):
        '''变量稳定性检查
        
        Parameters
        ----------
        feature_ana_df: pd.DataFrame
            数据集
        cols: list
            变量列表
        std_limit: float
            默认0.1 稳定性检查参数 
        data_apply:pd.DataFrame or None
            默认None 生效数据
        sep:str
            默认"^"，衍生变量分割符
        
        Returns
        -------
        data_apply:pd.DataFrame
            生效数据集
        modeling_list:list
            入模变量列表
        used_orig_list:list
            使用原始字段
        bulid_var_list:list
            变量衍生关系列表
        split_var_list:list
            衍生字段列表
        remove_var_list:list
            删除字段列表
        feature_ana_df:pd.DataFrame
            单特征分析数据
        '''
#        feature_ana_df=feature_ana_df.copy(deep=True)
#        feature_ana_df=feature_ana_df.loc[feature_ana_df["variable"].isin(cols),:]
        data_cnts = feature_ana_df['data_parts'].nunique()
        feature_ana_df=feature_ana_df[['data_parts', 'variable', 'bin', 'count', 'count_distr', 'Yes', 'No',
       'p0', 'p1', 'bin_iv', 'total_iv', 'woe', 'is_monotonic', 'ks', 'bet','bet_adj','avg_risk','sum_yes','sum_no']].copy(deep=True)

        # feature_ana_df_std=feature_ana_df.groupby(['variable','bin']).agg({"bet_adj":{"std":np.std,
        #                                                                               "cnt":np.size,
        #                                                                               "high_lift_cnt":lambda x:sum(x>high_lift_limit),
        #                                                                               "low_lift_cnt":lambda x:sum(x<low_lift_limit),
        #                                                                               },
        #                                                                     "count":np.sum})
        feature_ana_df_std=feature_ana_df.groupby(['variable','bin']).agg({
            "bet_adj": [np.std, np.size, lambda x:sum(x>high_lift_limit), lambda x:sum(x<low_lift_limit)],
            "count": np.sum
        })
        # feature_ana_df_std.columns=feature_ana_df_std.columns.droplevel(0)
        feature_ana_df_std.columns=["std", "cnt", "high_lift_cnt", "low_lift_cnt", "sum"]
        feature_ana_df_std=feature_ana_df_std.reset_index()
        
        feature_ana_df_std["keep"]=1
        feature_ana_df_bet_corr=feature_ana_df.pivot_table(values=['bet_adj','count'],index=['variable','bin'],columns='data_parts')
        miss_bin=[i for i in set(feature_ana_df_bet_corr.index.get_level_values(1).tolist()) if i.startswith("[-inf,{}".format(str(miss_val)[0:len(str(miss_val))-1]))][0]

        #高低响应率一致性检查
        feature_ana_df_std.loc[((feature_ana_df_std["high_lift_cnt"] + lift_tolerance_cnt )<feature_ana_df_std["cnt"])\
                        & ((feature_ana_df_std["low_lift_cnt"]  + lift_tolerance_cnt )<feature_ana_df_std["cnt"]),'keep']=0

        #std检查
        feature_ana_df_std.loc[feature_ana_df_std["std"]>std_limit,'keep']=0

        #lift相关性检查
        dic={}
        for col in set(feature_ana_df_bet_corr.index.get_level_values(0).tolist()):
        # for col in ['YP_BX_TJ_TT_min']:
            dic_detail={}
            for i in itertools.combinations(set(feature_ana_df_bet_corr.columns.get_level_values(1).tolist()), 2):
                # print ("----comb----",i)
                # print (feature_ana_df_bet_corr.loc[(col),("bet",i[0])], feature_ana_df_bet_corr.loc[(col),("bet",i[1])])
                try:
                    if feature_ana_df_bet_corr.loc[(col,miss_bin),("count",i[0])] <=10 or feature_ana_df_bet_corr.loc[(col,miss_bin),("count",i[1])] <=10:
                        arr1=feature_ana_df_bet_corr.reset_index().loc[(feature_ana_df_bet_corr.reset_index()['variable']==col) &\
                                                           (feature_ana_df_bet_corr.reset_index()['bin']!=miss_bin),("bet_adj",i[0])]
                        arr2=feature_ana_df_bet_corr.reset_index().loc[(feature_ana_df_bet_corr.reset_index()['variable']==col) &\
                                                           (feature_ana_df_bet_corr.reset_index()['bin']!=miss_bin),("bet_adj",i[1])]
                        dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=np.corrcoef(arr1,arr2)[0,1]
                    else:
                        dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=np.corrcoef(feature_ana_df_bet_corr.loc[(col),("bet_adj",i[0])], feature_ana_df_bet_corr.loc[(col),("bet_adj",i[1])])[0,1]
                except:
                    print("-----except raise {}-----------".format(col))
                    dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=np.corrcoef(feature_ana_df_bet_corr.loc[(col),("bet_adj",i[0])], feature_ana_df_bet_corr.loc[(col),("bet_adj",i[1])])[0,1]
                # print("ha",dic_detail["_".join(map(str,[data_parts,i[0],"vs",i[1]]))])
                if math.isnan(dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]) :
                    dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=0
            dic[col]=dic_detail
        feature_ana_df_bet_corr_result=pd.DataFrame(dic).T
        feature_ana_df_bet_corr_result['corr_result']=feature_ana_df_bet_corr_result.apply(lambda x:x.mean(),axis=1)
        feature_ana_df_bet_corr_result=feature_ana_df_bet_corr_result.reset_index().rename(columns={"index":"variable"})
        
        # feature_ana_df_std=feature_ana_df_std.reset_index()
        feature_ana_df_std=feature_ana_df_std.merge(feature_ana_df_bet_corr_result,on='variable',how='left')
        feature_ana_df_std.loc[feature_ana_df_std["corr_result"]<=corr_stablity_limit,"keep"]=0
        
        feature_ana_df_std["keep_all"]=feature_ana_df_std.groupby('variable')['keep'].transform(lambda x:1 if sum(x==0)<=1 else 0)
        
        #变量衍生关系列表
        split_var_list=feature_ana_df_std.loc[(feature_ana_df_std["keep"]==1) & (feature_ana_df_std["keep_all"]==0),["variable",'bin']].values.tolist()
        
        #不用分段的保留变量列表
        nosplit_var_list= sorted(list(set(feature_ana_df_std.loc[feature_ana_df_std["keep_all"]==1,"variable"].tolist())))
        
        #删除的变量列表
        remove_var_list=sorted(list(set(cols) - {i[0] for i in split_var_list} - set(nosplit_var_list)))
    
        #入模的变量列表
        modeling_list=sorted(list(set(nosplit_var_list) | set([i[0]+sep+i[1] for i in split_var_list])))
    
        #衍生出的变量列表
        bulid_var_list=[i for i in modeling_list  if sep in i ]
        
        #所有使用的原始变量列表
        used_orig_list=sorted(list(set(nosplit_var_list + [i.split(sep)[0] for i in bulid_var_list])))
        
        if data_apply is not None:
        #data_apply
            data_apply=data_apply.copy(deep=True)
            for i in split_var_list:
                left=float(re.search(r'\[(.+),(.+)\)',str(i[1])).group(1))
                right=float(re.search(r'\[(.+),(.+)\)',str(i[1])).group(2))
                data_apply[i[0]+sep+i[1]] = np.where((data_apply[i[0]]>=left) & (data_apply[i[0]]<right),1,0)
        
        feature_ana_df=pd.merge(feature_ana_df,feature_ana_df_std.reset_index(),on=['variable','bin']).sort_values(by=["data_parts",'variable','bin'])
        # feature_ana_df.loc[feature_ana_df['keep_all']==1,"keep"]=1
        # del feature_ana_df['keep_all']
        return data_apply,modeling_list,used_orig_list,bulid_var_list,split_var_list,remove_var_list,feature_ana_df.reset_index(drop=True)
    
    @cost
    def feature_resp_combine(self,feature_ana_df,data_parts='data_parts'):
        '''特征分组合箱
        
        Parameters
        ----------
        feature_ana_df: pd.DataFrame
            数据集
        data_apply:str
            默认"data_parts"，样本分割字段
        
        Returns
        -------
        dt_sl_psi:pd.DataFrame
            psi计算数据集
        '''
#        feature_ana_df2=pd.merge(feature_ana_df,feature_ana_df_std.reset_index(),on=['variable','bin'])
        feature_ana_df=feature_ana_df.copy(deep=True)
        keep='keep'
        other='other'
        # print("sum(feature_ana_df[keep])",sum(feature_ana_df[keep]))
        if sum(feature_ana_df[keep])==0:
            return feature_ana_df
        else:
            feature_ana_df.loc[feature_ana_df[keep]==0,"bin"]=other
            temp_df=feature_ana_df[feature_ana_df['bin']==other].groupby([data_parts,"variable","bin"])\
            .agg({'count':np.sum,'count_distr':np.sum,'Yes':np.sum,'No':np.sum,\
                  'avg_risk':max,'sum_yes':max,'sum_no':max,'total_iv':max,\
                  'is_monotonic':max,'is_monotonic':max,'ks':max})\
            .assign(p0=lambda x:x['No']/x['count'],
                    p1=lambda x:x['Yes']/x['count'],
                    bin_iv=lambda x:miv_01(x.No,x.Yes),
                    woe=lambda x:woe_01(x.No,x.Yes),
                    )\
            .assign(bet=lambda x:x["p1"]/x["avg_risk"]).reset_index()
            
            temp_df2=pd.concat([feature_ana_df[feature_ana_df['bin']!='other'],temp_df],\
                  ignore_index=True)\
                  [[data_parts,'variable', 'bin','count','count_distr','Yes',\
                    'No','p0','p1','bin_iv','total_iv','woe','is_monotonic',\
                    'ks','bet','avg_risk','sum_yes','sum_no']]
            
            temp_df2['total_iv']=temp_df2.groupby([data_parts,'variable'])['bin_iv']\
                .transform(sum)
            temp_df2.sort_values(by=[data_parts,'variable','bin'],inplace=True)
            temp_df2.reset_index(drop=True,inplace=True)
            return temp_df2

    @cost
    def var2resp(self,data,cols,y,fillna,bin_limit=100,apply=True):
        '''字符特征转响应率
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集
        cols:list
            字段列表
        y:str
            目标标签
        fillna:float
            不满足bin_limit数量要求下的转换值
        bin_limit:int
            默认100，枚举值必须满足的下线数量，否则转换为fillna
        apply:bool
            默认True 是否在data上生效
        
        Returns
        -------
        dict_map:dict
            转换关系字典
        data:pd.DataFrame
            转换后数据
        process_col:list
            转换字段
        '''
        # print (bin_limit)
#        resp_avg=sum(data[y])/data[y].shape[0]
        col_new = cols.copy()
        process_col=data[col_new].dtypes[data[col_new].dtypes=='object'].index.tolist()
        data[process_col] = data[process_col].astype(str)
        dict_map={}
        for i in process_col:
            grp=data.groupby([i])[y].agg({"sum":np.sum,"cnt":np.size})
            grp=grp[grp["cnt"]>=bin_limit].assign(p1=lambda x:x["sum"]/x["cnt"])
        
            dict_map[i]=dict(zip(grp.index,grp["p1"].round(4)))
            if apply:
                # data=data.copy(deep=True)
                data[i]=data[i].map(dict_map[i]).fillna(fillna)
                
        return dict_map,data,process_col

    @cost
    def var2respReg(self,data,cols,y,fill_na,bin_limit=100):
        '''字符特征转响应率等多个指标
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集
        cols:list
            字段列表
        y:str
            目标标签
        fillna:float
            不满足bin_limit数量要求下的转换值
        bin_limit:int
            默认100，枚举值必须满足的下线数量，否则转换为fillna
        apply:bool
            默认True 是否在data上生效
        
        Returns
        -------
        dict_map:dict
            转换关系字典
        data:pd.DataFrame
            转换后数据
        process_col:list
            转换字段
        '''
        # print (bin_limit)
#        resp_avg=sum(data[y])/data[y].shape[0]
        col_new = cols.copy()
        process_col=data[col_new].dtypes[data[col_new].dtypes=='object'].index.tolist()
        data[process_col]=data[process_col].astype(str)
        dict_map={}
        for i in process_col:
            grp=data.groupby([i])
            feature_dict={}
            for kind,kinddata in grp:
                info={}
                info[i+'_max']=fill_na['max'] if kinddata[y].count() < bin_limit else kinddata[y].max()
                info[i+'_min']=fill_na['min'] if kinddata[y].count() < bin_limit else kinddata[y].min()
                info[i+'_median']=fill_na['median'] if kinddata[y].count() < bin_limit else kinddata[y].median()
                info[i+'_std']=fill_na['std'] if kinddata[y].count() < bin_limit else kinddata[y].std()
                info[i+'_mean']=fill_na['mean'] if kinddata[y].count() < bin_limit else kinddata[y].mean()
                info[i+'_skew']=fill_na['skew'] if kinddata[y].count() < bin_limit else kinddata[y].skew()
                info[i+'_kurt']=fill_na['kurt'] if kinddata[y].count() < bin_limit else kinddata[y].kurt()
                info[i+'_mad']=fill_na['mad'] if kinddata[y].count() < bin_limit else kinddata[y].mad()
                feature_dict[kind]=info
            dict_map[i]=pd.DataFrame(feature_dict).T.reset_index().rename(columns={"index":i})
        return dict_map,data,process_col
    
    @cost
    def var2resp_apply(self,data,cols,dict_map,fillna):
        # data=data.copy(deep=True)
        for i in cols:
            data[i]=data[i].map(dict_map[i]).fillna(fillna)
                
        return data

    def feature_ana_reg(self,data,col_x,y,var_bin_dic):
        print(col_x)
        if pd.api.types.is_string_dtype(data[col_x]):
            raise ValueError("var should by decimal!")
        cuts=var_bin_dic[col_x]
        temp=pd.cut(data[col_x], cuts, right=False,precision=4).to_frame().rename(columns={col_x:'bin'})
        temp[y]=data[y]
        temp[col_x]=data[col_x]
        temp['p1'] =  temp.groupby('bin')[y].transform(np.mean)
        temp['gap']=temp['p1'] - temp[y]
        mean_MAE=round((temp[y] - temp[y].median()).abs().sum()/len(temp[y]),4)
        # result_plot=temp.groupby('bin').agg({"gap":{"AE":lambda x:x.abs().sum(),'count':np.size},y:['mean']}).rename(columns={'mean':'p1'})
        # result_plot.columns=result_plot.columns.droplevel(0)
        result_plot=temp.groupby('bin').agg(
            {"gap": [lambda x:x.abs().sum(), np.size], y: ['mean']}
        ).rename(columns={'mean': 'p1'})
        result_plot.columns=["AE", "count", "p1"]

        result_plot['p1']=result_plot['p1'].fillna(data[y].mean())
        result_plot['MAE']=result_plot['AE']/result_plot['count'].replace([np.nan,0],1)
        result_plot['avg_risk']=data[y].mean()

        result_plot=result_plot.reset_index().rename(columns={col_x: 'bin'})
        result_plot["variable"]=col_x

        result_plot["corr"]=temp[col_x].corr(temp[y]).round(4)
        result_plot[['AE','count']]=result_plot[['AE','count']].fillna(0)
        result_plot['count_distr']=result_plot['count']/result_plot['count'].sum()
        result_plot['MAE']=result_plot['MAE'].fillna(mean_MAE)
        result_plot['mean_MAE']=mean_MAE
        result_plot['bet']=result_plot['p1']/result_plot['avg_risk'].fillna(0.001)
        result_plot['bet_adj'] = result_plot['bet'].apply(adj_sigmod)

        return col_x,result_plot,cuts

    @cost
    def data_feature_analysis_reg_solo(self,data,y,ilx,var_bin_dic,dp=None,n_jobs=-1):
        '''单样本特征稳定性分析-回归
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集
        y: str
            y变量名称
        ilx: list
            x变量list
        var_bin_dic: dict
            变量切点位置eg: {'social_cnt_diff': [-inf, -999998, -0.5, 1.5, inf],\
                            'romance_cnt_diff': [-inf, -999998, inf],\
                            'communications_cnt_diff': [-inf, -999998, -0.5, 0.5, inf]}
        
        detail:bool
            True or False 是否输出明细结果
        order :bool
            True or False 是否iv排序
        graph:str
            输出文件路径
        prefix:str
            输出文件后缀
        var_dic:dict
            变量命名映射
        bet:float
            图形响应率倍数
        
        Returns
        -------
        dict
            输出字典
        '''
        i = 0
        detail_df=pd.DataFrame()
        rtn_dict={}
        out = Parallel(n_jobs=n_jobs,backend='threading')(
            delayed(self.feature_ana_reg)(data[[col_x, y]], col_x, y, var_bin_dic) for
            col_x in ilx)

        detail_df = [k[1] for k in out]
        rtn_dict = {k[0]: k[2] for k in out}
        detail_df = pd.concat(detail_df, axis=0, ignore_index=True)
        detail_df=detail_df.reindex(columns=['variable', 'bin','count','count_distr','MAE','AE','corr','avg_risk','mean_MAE','p1','bet','bet_adj'])
        detail_df['bin']=detail_df['bin'].astype(str).str.replace(" ","")
        if dp:
            return {dp: detail_df}
        else:
            return { 'dtl': detail_df,'cut':rtn_dict}
    
    @cost
    def get_tree_cut_reg(self,df, fea, y, max_cuts=5, min_one_cnt=0.05,miss_val=-99):
        """决策树分箱-回归
        
        Parameters
        ----------
        df : pd.DataFrame
            数据集 
        fea : str
            入模输入项
        y : string
            标签的字段名
        max_cuts : int
            默认5 最大分箱数
        min_one_cnt : float
            默认 0.05 箱体的最小占比
        miss_val : int
            默认-99 缺失的映射值 
            
        Returns
        -------
        fea_cuts : dict
            分割字典
        """
        fea_cuts = dict()
        cuts = []
        for x in fea:
            print (x)
            if pd.api.types.is_string_dtype(df[x]):
                pass
            else:
                # print("----in cut----")
                clf = tree.DecisionTreeRegressor(min_samples_leaf=min_one_cnt, max_leaf_nodes=max_cuts)
                trainX=df.loc[df[x]!=float(miss_val),x]
    #                print ("index=",df.loc[df[x] != miss_val].index)
                trainY=df.loc[df[x]!=float(miss_val),y]
                if len(trainX.values.reshape(-1,1)) == 0:
                    fea_cuts[x] = [-np.inf,miss_val+0.001,np.inf]
                    continue
                
                clf.fit(trainX.values.reshape(-1,1), trainY.values)
    #                print (clf.tree_.threshold,"feature=",clf.tree_.feature)
                cuts=list(set(list(clf.tree_.threshold[clf.tree_.feature != -2])))
                cuts.append(float('inf'))
                cuts.append(float('-inf'))
                cuts.append(miss_val+0.001)
                cuts=sorted(list(set(map(lambda x:round(x,4) , cuts))))
                fea_cuts[x] = sorted(cuts)
            # clf.fit(x.reshape(-1, 1), y)
    
        return fea_cuts
    
    @cost
    def data_feature_reg_analysis(self,data,dummies_col,split_list_dic,y,data_parts = None,n_jobs=1):
        '''变量稳定性分析-回归

        Parameters
        ----------
        data: pd.DataFrame
            数据集
        dummies_col: list
            x变量list
        split_list_dic: dict
            变量切点位置eg: {'social_cnt_diff': [-inf, -999998, -0.5, 0.5, inf],\
                 'romance_cnt_diff': [-inf, -999998, inf],\
                 'communications_cnt_diff': [-inf, -999998, -0.5, 0.5, inf]}
        y: str
            y变量名称
        data_parts:str
            data_parts输出字段

        Returns
        -------
        feature_ana_df:pd.DataFrame
            单变量分析报告
        '''
        feature_ana_dic={}
        feature_ana_df=pd.DataFrame()
        if data_parts:
            for i in data[data_parts].unique():
                print('data_parts=',i)
                feature_ana_dic[i]=self.data_feature_analysis_reg_solo(data[data[data_parts]==i].reset_index(drop=True)
                ,y
                ,dummies_col
                ,split_list_dic
                ,n_jobs=n_jobs)['dtl']
                feature_ana_df=pd.concat(feature_ana_dic).reset_index()\
                        .drop('level_1', axis=1)\
                        .rename(columns={'level_0':data_parts})
            return feature_ana_df.reset_index(drop=True)
        else:
            feature_ana_df=self.data_feature_analysis_reg_solo(data
            ,y
            ,dummies_col
            ,split_list_dic)['dtl']
            return feature_ana_df.reset_index(drop=True)
    
    @cost
    def feature_resp_reg_std_check(self,feature_ana_df,cols,std_limit,data_apply = None,sep='^',high_lift_limit=1,low_lift_limit=1,lift_tolerance_cnt=0,corr_stablity_limit=0.5,miss_val=-99):
        '''变量稳定性检查-回归
        
        Parameters
        ----------
        feature_ana_df: pd.DataFrame
            数据集
        cols: list
            变量列表
        std_limit: float
            默认0.1 稳定性检查参数 
        data_apply:pd.DataFrame or None
            默认None 生效数据
        sep:str
            默认"^"，衍生变量分割符
        
        Returns
        -------
        data_apply:pd.DataFrame
            生效数据集
        modeling_list:list
            入模变量列表
        used_orig_list:list
            使用原始字段
        bulid_var_list:list
            变量衍生关系列表
        split_var_list:list
            衍生字段列表
        remove_var_list:list
            删除字段列表
        feature_ana_df:pd.DataFrame
            单特征分析数据
        '''
        feature_ana_df=feature_ana_df[['data_parts', 'variable', 'bin', 'count','count_distr', 'MAE', 'AE','corr', 'mean_MAE','avg_risk','p1','bet','bet_adj']].copy(deep=True)

        # feature_ana_df_std=feature_ana_df.groupby(['variable','bin']).agg({"bet_adj":{"std":np.std,"cnt":np.size,"high_lift_cnt":lambda x:sum(x>high_lift_limit),"low_lift_cnt":lambda x:sum(x<low_lift_limit)},"count":np.sum})
        # feature_ana_df_std.columns=feature_ana_df_std.columns.droplevel(0)

        feature_ana_df_std=feature_ana_df.groupby(['variable', 'bin']).agg(
            {
                "bet_adj": [np.std, np.size, lambda x:sum(x > high_lift_limit), lambda x:sum(x < low_lift_limit)],
                "count": np.sum
            }
        )
        feature_ana_df_std.columns=["std", "cnt", "high_lift_cnt", "low_lift_cnt", "sum"]
        feature_ana_df_std=feature_ana_df_std.reset_index()
        
        feature_ana_df_std["keep"]=1
        feature_ana_df_bet_corr=feature_ana_df.pivot_table(values=['bet_adj','count'],index=['variable','bin'],columns='data_parts')
        miss_bin=[i for i in set(feature_ana_df_bet_corr.index.get_level_values(1).tolist()) if i.startswith("[-inf,{}".format(str(miss_val)[0:len(str(miss_val))-1]))][0]

        feature_ana_df_std.loc[((feature_ana_df_std["high_lift_cnt"] + lift_tolerance_cnt )<feature_ana_df_std["cnt"])\
                               & ((feature_ana_df_std["low_lift_cnt"]  + lift_tolerance_cnt )<feature_ana_df_std["cnt"]),'keep']=0
                               
        feature_ana_df_std.loc[feature_ana_df_std["std"]>std_limit,'keep']=0

        dic={}
        for col in set(feature_ana_df_bet_corr.index.get_level_values(0).tolist()):
        # for col in ['YP_BX_TJ_TT_min']:
            dic_detail={}
            for i in itertools.combinations(set(feature_ana_df_bet_corr.columns.get_level_values(1).tolist()), 2):
                # print ("----comb----",i)
                # print (feature_ana_df_bet_corr.loc[(col),("bet_adj",i[0])], feature_ana_df_bet_corr.loc[(col),("bet_adj",i[1])])
                try:
                    if feature_ana_df_bet_corr.loc[(col,miss_bin),("count",i[0])] <=10 or feature_ana_df_bet_corr.loc[(col,miss_bin),("count",i[1])] <=10:
                        arr1=feature_ana_df_bet_corr.reset_index().loc[(feature_ana_df_bet_corr.reset_index()['variable']==col) &\
                                                           (feature_ana_df_bet_corr.reset_index()['bin']!=miss_bin),("bet_adj",i[0])]
                        arr2=feature_ana_df_bet_corr.reset_index().loc[(feature_ana_df_bet_corr.reset_index()['variable']==col) &\
                                                           (feature_ana_df_bet_corr.reset_index()['bin']!=miss_bin),("bet_adj",i[1])]
                        dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=np.corrcoef(arr1,arr2)[0,1]
                    else:
                        dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=np.corrcoef(feature_ana_df_bet_corr.loc[(col),("bet_adj",i[0])], feature_ana_df_bet_corr.loc[(col),("bet_adj",i[1])])[0,1]
                except:
                    print("-----except raise {}-----------".format(col))
                    dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=np.corrcoef(feature_ana_df_bet_corr.loc[(col),("bet_adj",i[0])], feature_ana_df_bet_corr.loc[(col),("bet_adj",i[1])])[0,1]
                # print("ha",dic_detail["_".join(map(str,[data_parts,i[0],"vs",i[1]]))])
                if math.isnan(dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]) :
                    dic_detail["_".join(map(str,["data_parts",i[0],"vs",i[1]]))]=0
            dic[col]=dic_detail
        feature_ana_df_bet_corr_result=pd.DataFrame(dic).T
        feature_ana_df_bet_corr_result['corr_result']=feature_ana_df_bet_corr_result.apply(lambda x:x.mean(),axis=1)
        feature_ana_df_bet_corr_result=feature_ana_df_bet_corr_result.reset_index().rename(columns={"index":"variable"})
        
        feature_ana_df_std=feature_ana_df_std.merge(feature_ana_df_bet_corr_result,on='variable',how='left')
        feature_ana_df_std.loc[feature_ana_df_std["corr_result"]<=corr_stablity_limit,"keep"]=0
        
        feature_ana_df_std["keep_all"]=feature_ana_df_std.groupby('variable')['keep'].transform(lambda x:1 if sum(x==0)<=1 else 0)
        
        #变量衍生关系列表
        split_var_list=feature_ana_df_std.loc[(feature_ana_df_std["keep"]==1) & (feature_ana_df_std["keep_all"]==0),["variable",'bin']].values.tolist()
        
        #不用分段的保留变量列表
        nosplit_var_list= sorted(list(set(feature_ana_df_std.loc[feature_ana_df_std["keep_all"]==1,"variable"].tolist())))

        #删除的变量列表
        remove_var_list=sorted(list(set(cols) - {i[0] for i in split_var_list} - set(nosplit_var_list)))
    
        #入模的变量列表
        modeling_list=sorted(list(set(nosplit_var_list) | set([i[0]+sep+i[1] for i in split_var_list])))

        #衍生出的变量列表
        bulid_var_list=[i for i in modeling_list  if sep in i ]
        
        #所有使用的原始变量列表
        used_orig_list=sorted(list(set(nosplit_var_list + [i.split(sep)[0] for i in bulid_var_list])))
        
        if data_apply is not None:
        #data_apply
            data_apply=data_apply.copy(deep=True)
            for i in split_var_list:
                left=float(re.search(r'\[(.+),(.+)\)',str(i[1])).group(1))
                right=float(re.search(r'\[(.+),(.+)\)',str(i[1])).group(2))
                data_apply[i[0]+sep+i[1]] = np.where((data_apply[i[0]]>=left) & (data_apply[i[0]]<right),1,0)
        
        feature_ana_df=pd.merge(feature_ana_df,feature_ana_df_std.reset_index(),on=['variable','bin']).sort_values(by=["data_parts",'variable','bin'])
        # feature_ana_df.loc[feature_ana_df['keep_all']==1,"keep"]=1
        # del feature_ana_df['keep_all']
        return data_apply,modeling_list,used_orig_list,bulid_var_list,split_var_list,remove_var_list,feature_ana_df.reset_index(drop=True)


class Str2RspTransformer(BaseEstimator, TransformerMixin):
    """字符转响应率Transformer
    
    Parameters
    ----------
    col_x: list
       特征列表.
    fillna : float
       不满足bin_limit数量填的值
    bin_limit: int
       默认100，枚举值下限，不满足填写fillna的值
    data_parts: str
       数据集切分字段.
    data_parts_use: list or None
       样本分析列表，eg:[1,2],只会分析data_parts为1和2的样本，如果为None分析整个数据集

    Attributes
    ----------
    col_new :list
        返回特征列表
    dict_map :dict
        特征映射关系字典

    Notes
    -----
    Data transform type : UPDATE

    """
    def __init__(self,col_x,fillna,bin_limit=100,
                 data_parts='data_parts',data_parts_use=None,feature_map=None):
        self.col_x=col_x
        self.fillna=fillna
        self.bin_limit=bin_limit
        self.dict_map=dict()
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.feature_map=feature_map
        self.col_new=col_x

    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身对象本身
        '''

        self.col_new=self.col_x
        if y is not None:
            check_y_is_series(y)
            if self.data_parts_use:
                data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
            # else:
            #     data=data.copy(deep=True)
            am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None)

            self.dict_map,_,_=am.var2resp(data,self.col_x,y.name,self.fillna,\
                        bin_limit=self.bin_limit,apply=False)
            # print("dict_map.shape",self.dict_map)
        return self

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)

        for i in data.columns.tolist():
            if i in self.dict_map.keys():
                data[i] = data[i].astype(str)
                data[i]=data[i].map(self.dict_map[i]).fillna(self.fillna)
#                data[i]=data[i].map(self.dict_map[i])

        return data


class Str2RspRegTransformer(BaseEstimator, TransformerMixin):
    """字符转换数值型回归版Transformer
    
    Parameters
    ----------
    col_x: list
       输入特征列表.
    bin_limit: int
       默认100，枚举值下限，不满足填写data整体的max、min、std、mean、median等值
    data_parts: str
       数据集切分字段.
    data_parts_use: list or None
       样本分析列表，eg:[1,2],只会分析data_parts为1和2的样本，如果为None分析整个数据集

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    dict_map :dict
        特征映射关系字典

    Notes
    -----
    Data transform type : UPDATE

    """
    def __init__(self,col_x,bin_limit=100,
                 data_parts='data_parts',data_parts_use=None,feature_map=None):
        self.col_x=col_x
        self.bin_limit=bin_limit
        self.dict_map=dict()
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.feature_map=feature_map
        self.default={}
        self.remove_var_list=[]
        self.col_new=col_x
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身对象本身
        '''

        self.col_new=self.col_x
        if y is not None:
            check_y_is_series(y)
            if self.data_parts_use:
                data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
            # else:
            #     data=data.copy(deep=True)
            am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None)
            # print (data.shape)
            self.default['max']=data[y.name].max()
            self.default['min']=data[y.name].min()
            self.default['mean']=data[y.name].mean()
            self.default['std']=data[y.name].std()
            self.default['median']=data[y.name].median()
            self.default['kurt']=data[y.name].kurt()
            self.default['skew']=data[y.name].skew()
            self.default['mad']=data[y.name].mad()
            self.dict_map,_,self.remove_var_list=am.var2respReg(data,self.col_x,y.name,\
                        fill_na=self.default,bin_limit=self.bin_limit)

            self.split_var_list=[]
            for k,v in self.dict_map.items():
                temp=v.columns.tolist()
                temp.remove(k)
                self.split_var_list.extend(temp)
                
            self.col_new.extend(self.split_var_list)
            
            for i in self.remove_var_list:
                self.col_new.remove(i)
                
            if self.feature_map is not None:
                dic={}
                for k2,v2 in self.dict_map.items():
                    for col in v2.columns.tolist():
                        if col == k2:
                            continue
                        else:
                            dic[col]=k2
                self.feature_map=self.feature_map.append(pd.DataFrame(dic.items(),columns=['variable','relyon']),ignore_index=True)
            
        return self

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)

        for i in data.columns.tolist():
            if i in self.dict_map.keys():
                data[i] = data[i].astype(str)
                # data[i]=data[i].map(self.dict_map[i]).fillna(self.fillna)
                if i+'_max' in data.columns.tolist():
                    del data[i+'_max']
                if i+'_min' in data.columns.tolist():
                    del data[i+'_min']
                if i+'_median' in data.columns.tolist():
                    del data[i+'_median']
                if i+'_mean' in data.columns.tolist():
                    del data[i+'_mean']
                if i+'_std' in data.columns.tolist():
                    del data[i+'_std']
                if i+'_kurt' in data.columns.tolist():
                    del data[i+'_kurt']
                if i+'_skew' in data.columns.tolist():
                    del data[i+'_skew']
                if i+'_mad' in data.columns.tolist():
                    del data[i+'_mad']
                    
                data=data.merge(self.dict_map[i],how='left',on=i)
                
                data[i+'_max']=data[i+'_max'].fillna(self.default['max'])
                data[i+'_min']=data[i+'_min'].fillna(self.default['min'])
                data[i+'_median']=data[i+'_median'].fillna(self.default['median'])
                data[i+'_mean']=data[i+'_mean'].fillna(self.default['mean'])
                data[i+'_std']=data[i+'_std'].fillna(self.default['std'])
                data[i+'_kurt']=data[i+'_kurt'].fillna(self.default['kurt'])
                data[i+'_skew']=data[i+'_skew'].fillna(self.default['skew'])
                data[i+'_mad']=data[i+'_mad'].fillna(self.default['mad'])

        return data


class FeatureStablityTransformer(BaseEstimator, TransformerMixin):
    """特征稳定性分析Transformer

    Parameters
    ----------
    col_x: list
       字段列表.
    max_cuts : float
       特征分箱最大数量
    min_one_cnt: int
       默认100，枚举值下限，不满足填写fillna的值
    miss_val: int
       缺失值
    graph: str or None
       马赛克图生成地址，指定时画图，如果为None则不画图
    bet: int
       马赛克图响应率放大倍数，默认为1
    data_parts:str
        样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list
        样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足
        data_parts=1 和 2时的样本
    std_limit:float
        特征筛选标准差要求阈值 ，默认0.3
    iv_limit:float
        特征筛选IV要求阈值 ，默认0.01(多样本都需要满足)
    high_lift_limit:float
        特征单箱内高lift要求下限，多份样本上高风险倍数必须大于此阈值，如果不满足则剔除该分箱，该值越高对特征要求越高，取值范围为[1,+∞)
    low_lift_limit:float
        特征单箱内低lift要求上限，多份样本上低风险倍数必须小于此阈值，如果不满足则剔除该分箱，该值越低对特征要求越高，取值范围为[0,1]
    lift_tolerance_cnt:int
        针对不满足high_lift_limit和low_lift_limit 样本数量的忍耐值，默认值为0
    corr_stablity_limit:
        多样本lift趋势相似度阈值，该值越大代表对特征相似度要求越高，默认0.5，不满足的特征将被删除
    sep:str
        衍生变量分割符，默认"^"
    feature_ana_df:pd.DataFrame() or None
        特征分析表，默认None，如果设置不再生成新的feature_ana_df
    dic:dict or None
        特征分割切点集合，默认None，如果配置特征切点，则沿用此切点，不再新找切点
    feature_map:pd.DataFrame() or None
        特征图配置表
    mono_dic:dict
        特征图配置表,value为1代表与目标正相关，-1为负相关，eg:{'ali_rain_score': 1,
                     'td_zhixin_score': -1,
                     'td_xyf_dq_score': 1,
                     'cl_fraud_score_ronghui': 1,
                     'umeng_score': -1,
                     'cs_lingzhi_score_fullink': -1,
                     'hds_36m_purchase_steady': 1,
                     'credit_repayment_score_bj': -1,
                     'bj_ecommerce_score': -1,
                     'credit_phone_score': -1}
    mono_perception:bool
        单调感知开关，默认True
    woe_output:bool
        woe形态输出形式，默认False

    Attributes
    ----------
    col_new:list
        输出返回特征列表
    remove_var_list:list
        删除特征列表
    feature_ana_df:pd.DataFrame()
        特征分析表
    feature_ana_df_combine:pd.DataFrame()
        合并分箱后的特征分析表
    dic:dict
        特征切点
    cut_mono_dic:dict
        单调性结果字典
    woe_df
        总表输出结果

    Notes
    -----
    Data transform type : INSERT/DELETE

    """

    def __init__(self, col_x, max_cuts=5, min_one_cnt=0.05, miss_val=-99,
                 graph='', bet=1, data_parts='data_parts', data_parts_use=None,
                 std_limit=0.2, iv_limit=0.01, high_lift_limit=1, low_lift_limit=1,
                 lift_tolerance_cnt=1, corr_stablity_limit=0.2, data_apply=None,
                 n_jobs=1,mono_dic={},mono_perception=True,verbose=False,woe_output=False,
                 sep='^', feature_ana_df=None, dic=None, feature_map=None):
        self.col_x = col_x
        self.max_cuts = max_cuts
        self.min_one_cnt = min_one_cnt
        self.miss_val = miss_val
        self.graph = graph
        self.bet = bet
        self.data_parts = data_parts
        self.std_limit = std_limit
        self.data_apply = data_apply
        self.sep = sep
        self.remove_var_list = []
        self.iv_limit = iv_limit
        self.feature_ana_df = feature_ana_df
        self.dic = dic
        self.data_parts_use = data_parts_use
        self.split_var_list = []
        self.feature_map = feature_map
        self.high_lift_limit = high_lift_limit
        self.low_lift_limit = low_lift_limit
        self.lift_tolerance_cnt = lift_tolerance_cnt
        self.corr_stablity_limit = corr_stablity_limit
        self.n_jobs = n_jobs
        self.mono_dic=mono_dic
        self.verbose=verbose
        self.woe_output = woe_output
        self.mono_perception = mono_perception

        self.cut_mono_dic={}
        self._binned_variables={}
        self.woe_df=None
        self._is_fitted = False

    def fit(self, data, y=None):
        '''fit函数

        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量

        Returns
        -------
        self:对象本身类型
        '''
        check_y_is_series(y)

        if self.data_parts_use:
            data = data.loc[data[self.data_parts].isin(self.data_parts_use), :].reset_index(drop=True).copy(deep=True)
        # else:
        # data=data.copy(deep=True)

        n_jobs = _effective_n_jobs(self.n_jobs)
        print("n_jobs", n_jobs)
        self.col_new = self.col_x

        dec_col_cnts = np.sum([0 if data[c].dtype == np.object else 1 for c in self.col_x])
        print(dec_col_cnts)
        if dec_col_cnts == 0:
            print("no decimal cols,stop fit")
            self._is_fitted = True
            return self

        am = Automan_Data_Explore(log_dict_flag=False, log_dict_unkeep_type=None, config_file=None)

        time_start = time.perf_counter()

        if self.dic is None:
            self.dic = {}
            for x in self.col_x:
                if x in self.mono_dic.keys():
                    if self.mono_dic[x] == 1:
                        self.cut_mono_dic[x] = 'ascending'
                    elif self.mono_dic[x] == -1:
                        self.cut_mono_dic[x] = 'descending'
                    else:
                        if self.mono_perception:
                            self.cut_mono_dic[x] =trend_decision(data[x],data[y.name]
                                                                 ,max_leaf_nodes=max(self.max_cuts, 2)
                                                                 ,min_samples_leaf=self.min_one_cnt/len(data) if self.min_one_cnt >=1 else self.min_one_cnt
                                                                 , miss_val = self.miss_val)
                            if self.cut_mono_dic[x] not in ['ascending','descending']:
                                self.cut_mono_dic[x] = 'auto'
                        else:
                            self.cut_mono_dic[x] = 'auto'
                else:
                    if self.mono_perception:
                        self.cut_mono_dic[x] =trend_decision(data[x],data[y.name]
                                                             ,max_leaf_nodes=max(self.max_cuts, 2)
                                                             ,min_samples_leaf=self.min_one_cnt/len(data) if self.min_one_cnt >=1 else self.min_one_cnt
                                                             , miss_val = self.miss_val)
                        if self.cut_mono_dic[x] not in ['ascending','descending']:
                            self.cut_mono_dic[x] = 'auto'
                    else:
                        self.cut_mono_dic[x] = 'auto'

            for c in tqdm(self.col_x):
                self._binned_variables[c] = get_opt_binning(col_x=data[c],
                                                            col_y=data[y.name],
                                                            min_one_cnt=self.min_one_cnt/len(data) if self.min_one_cnt >=1 else self.min_one_cnt,
                                                            name=c,
                                                            max_n_prebins=max(self.max_cuts, 2),
                                                            monotonic_trend=self.cut_mono_dic[c],
                                                            verbose=self.verbose,
                                                            special_codes=[self.miss_val]
                                                            )
                self.dic[c] = sorted(self._binned_variables[c].splits.tolist() + [-np.inf,np.inf,self.miss_val + 0.001])
                # optb._splits_optimal
            # self.dic = am.get_tree_cut(data, self.col_x, y.name, max_cuts=self.max_cuts,
            #                            min_one_cnt=self.min_one_cnt
            #                            , miss_val=self.miss_val)
        self._time_cut = time.perf_counter() - time_start
        print("_time_cut = ", self._time_cut)

        if self.feature_ana_df is None:
            time_fea_ana = time.perf_counter()
            self.feature_ana_df = am.data_feature_analysis(data, self.col_x, self.dic,
                                                           y.name, self.graph,
                                                           data_parts=self.data_parts, n_jobs=n_jobs)
            self._time_cut = time.perf_counter() - time_fea_ana
            print("time_fea_ana = ", self._time_cut)

        # print("1111",self.col_new)
        if self.data_parts and self.std_limit is not None:
            _, keep_list, self.used_orig_list, self.bulid_var_list, \
            self.split_var_list, remove_list, self.feature_ana_df = \
                am.feature_resp_std_check(self.feature_ana_df, self.col_x,
                                          std_limit=self.std_limit,
                                          data_apply=self.data_apply,
                                          sep=self.sep,
                                          high_lift_limit=self.high_lift_limit,
                                          low_lift_limit=self.low_lift_limit,
                                          lift_tolerance_cnt=self.lift_tolerance_cnt,
                                          corr_stablity_limit=self.corr_stablity_limit,
                                          miss_val=self.miss_val)
            self.col_new = keep_list
            self.remove_var_list = list(set(self.remove_var_list) | set(remove_list))
            self.feature_ana_df_combine = am.feature_resp_combine(self.feature_ana_df, self.data_parts)
            if self.feature_map is not None:
                self.feature_map = self.feature_map.append(
                    pd.DataFrame([(self.sep.join(svl), svl[0]) for svl in self.split_var_list],
                                 columns=['variable', 'relyon']), ignore_index=True)

        # print("3333",self.col_new)
        if self.iv_limit:
            remove_list = set(
                self.feature_ana_df.loc[self.feature_ana_df["total_iv"] < self.iv_limit, 'variable'].tolist())
            # print ("remove_list",remove_list)
            remove_list_iv = []
            for i in self.col_new:
                # print ("i=",i,i.split(self.sep)[0])
                if i.split(self.sep)[0] in remove_list:
                    remove_list_iv.append(i)
            # self.col_new = list(set(self.col_new) - set(remove_list_iv))
            for r in remove_list_iv:
                self.col_new.remove(r)
            self.remove_var_list = list(set(self.remove_var_list) | set(remove_list))

        # print("22222",self.col_new)
        self.woe_df = self.woe_table_build(data,y.name)
        # woe_output
        if self.woe_output:
            self.col_new_orig = self.col_new[:]
            self.col_new = [c +'_woe' for c in self.col_new]
            if self.feature_map is not None:
                self.feature_map = self.feature_map.append(\
                    pd.DataFrame([(z[0],z[1]) for z in list(zip(self.col_new,self.col_new_orig))],\
                                 columns=['variable', 'relyon']), ignore_index=True)

        self._is_fitted = True
        return self

    def woe_table_build(self,data,y):
        if len(self.feature_ana_df) == 0:
            return None
        else :
            d = self.feature_ana_df.groupby(["variable", "bin"], as_index=False).agg(
                {"count": ["sum"], "Yes": ["sum"], "No": ["sum"]})
            d.columns = [i[0] for i in d.columns]
            # woe_01(d.No,d.Yes)
            data_len = d.groupby("variable")["count"].sum().max()
            avg_risk = d.groupby("variable")["Yes"].sum().max() / data_len
            d["Yes_sum"] = d.groupby("variable")["Yes"].transform("sum")
            d["No_sum"] = d.groupby("variable")["No"].transform("sum")
            d["woe"] = d[["Yes", "No", "Yes_sum", "No_sum"]].replace(0, 0.9) \
                .assign(
                DistrBad=lambda x: x.Yes / x.Yes_sum,
                DistrGood=lambda x: x.No / x.No_sum
            ) \
                .assign(woe=lambda x: np.log(x.DistrBad / x.DistrGood)) \
                .woe
            d["p0"] = d.apply(lambda x: avg_risk if x["count"] == 0 else x["No"] / x["count"], axis=1)
            d["p1"] = d.apply(lambda x: 1 - avg_risk if x["count"] == 0 else x["Yes"] / x["count"], axis=1)
            d["type"] = 0

        #split var table build
        e = pd.DataFrame()
        if len( self.bulid_var_list)> 0:

            for i in self.split_var_list:
                left = float(re.search(r'\[(.+),(.+)\)', str(i[1])).group(1))
                right = float(re.search(r'\[(.+),(.+)\)', str(i[1])).group(2))
                data[i[0] + self.sep + i[1]] = np.where((data[i[0]] >= left) & (data[i[0]] < right), 1, 0)

            for sp in self.bulid_var_list:
                temp = data.groupby([sp])[y].agg([np.size, np.sum]).reset_index() \
                    .rename(columns={sp: "bin", "size": "count", "sum": "Yes"})
                temp["variable"] = sp
                temp["bin"] = temp["bin"].replace({1:"[0.5,inf)",0:"[-inf,0.5)"})
                e = e.append(temp)
                self.dic[sp] = [-np.inf,0.5,np.inf]

            e["No"] = e["count"] - e["Yes"]
            e["Yes_sum"] = e.groupby("variable")["Yes"].transform("sum")
            e["No_sum"] = e.groupby("variable")["No"].transform("sum")
            e["woe"] = e[["Yes", "No", "Yes_sum", "No_sum"]].replace(0, 0.9) \
                .assign(
                DistrBad=lambda x: x.Yes / x.Yes_sum,
                DistrGood=lambda x: x.No / x.No_sum
            ) \
                .assign(woe=lambda x: np.log(x.DistrBad / x.DistrGood)) \
                .woe
            e["p0"] = e.apply(lambda x: avg_risk if x["count"] == 0 else x["No"] / x["count"], axis=1)
            e["p1"] = e.apply(lambda x: 1 - avg_risk if x["count"] == 0 else x["Yes"] / x["count"], axis=1)
            e["type"] = 1
        return pd.concat([d,e],axis=0,ignore_index=True)

    def __getitem__(self, key):
        _check_is_fitted(self)
        if isinstance(key, (list, tuple)):
            return self.feature_ana_df.loc[self.feature_ana_df['variable'].isin(key)].sort_values(
                ['variable', 'bin', 'data_parts'])
        else:
            return self.feature_ana_df.loc[self.feature_ana_df['variable'] == key].sort_values(
                ['variable', 'bin', 'data_parts'])

    def plot(self, key):
        _check_is_fitted(self)
        if isinstance(key, (list, tuple)):
            plot_df = self.feature_ana_df.loc[self.feature_ana_df['variable'].isin(key)].sort_values(
                ['variable', 'bin', 'data_parts'])
        else:
            plot_df = self.feature_ana_df.loc[self.feature_ana_df['variable'] == key].sort_values(
                ['variable', 'bin', 'data_parts'])
        feature_ana_plot(plot_df, path=None, file_prefix=None, excel=None, sheet_name=None, plot_insert_excel=False,
                         if_plot=True)

    def transform(self, data):
        '''transform函数

        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集

        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data = data.copy(deep=True)
        for i in self.split_var_list:
            if i[0] in data.columns.tolist():
                left = float(re.search(r'\[(.+),(.+)\)', str(i[1])).group(1))
                right = float(re.search(r'\[(.+),(.+)\)', str(i[1])).group(2))
                data[i[0] + self.sep + i[1]] = np.where((data[i[0]] >= left) & (data[i[0]] < right), 1, 0)
                if self.woe_output:
                    s = i[0] + self.sep + i[1]
                    # print(i)
                    data[s+'_bins'] = pd.cut(data[s],self.dic[s],right=False,precision=4).astype(str).str.replace(" ","")
                    data[s + '_woe'] = \
                    data.merge(self.woe_df[self.woe_df["variable"] == s], left_on=s + '_bins', right_on="bin",
                               how='left')['woe']

                    # data[i[0] + self.sep + i[1] + '_woe'] = data.merge(self.woe_df.loc[self.woe_df['variable']==i[0] + self.sep + i[1]] ,left_on = i[0] + self.sep + i[1]\
                    #                                    ,right_on = "bin",how = 'left')['woe']
                    del data[s+'_bins']
        if self.woe_output:
            for i in data.columns.tolist():
                if i in self.col_new_orig and i not in self.bulid_var_list:
                    data[i+'_bins'] = pd.cut(data[i],self.dic[i],right=False,precision=4).astype(str).str.replace(" ","")
                    # print("2222",data.merge(self.woe_df[self.woe_df["variable"]==i],left_on = i,right_on = "bin",how = 'left'))
                    data[i + '_woe'] = data.merge(self.woe_df[self.woe_df["variable"]==i],left_on = i+'_bins',right_on = "bin",how = 'left')['woe']
                    # if i+'_bins' in data.columns:
                    del data[i+'_bins']
        return data


class FeaturePsiStablityTransformer(BaseEstimator, TransformerMixin):
    """特征PSI分析Transformer 

    Parameters
    ----------
    col_x: list
       字段列表.
    perc: list
       默认:[0.0, 0.2, 0.4, 0.6, 0.8, 1.0] 分段分位数.
    miss_val: int
       默认:-99 缺失值.
    data_parts:str
        样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list
        样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足
        data_parts=1 和 2时的样本
    psi_limit:dict
        psi检查阈值，默认psi_limit={"max":0.15,"median":0.1}，代表最大PSI不能超过0.15,中位数PSI不能超过0.1
    feature_ana_df:pd.DataFrame() or None
        特征分析表，默认None，如果设置不再生成新的feature_ana_df
    dic:dict or None
        特征分割切点集合，默认None，如果配置特征切点，则沿用此切点，不再新找切点

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    remove_var_list :list
        删除特征列表
    feature_ana_df_psi:pd.DataFrame()
        PSI特征表
    dic:dict
        特征切点

    Notes
    -----
    Data transform type : DELETE

    """
    
    def __init__(self, col_x, perc=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],miss_val=-99,
                 data_parts = 'data_parts',data_parts_use=None
                 ,psi_limit={"max":0.15,"median":0.1}
                 ,feature_ana_df=None,dic=None,feature_map=None):
        self.col_x=col_x
        self.data_parts=data_parts
        self.feature_ana_df =feature_ana_df
        self.dic =dic
        self.data_parts_use=data_parts_use
        self.perc=perc
        self.miss_val=miss_val
        self.psi_limit=psi_limit
        self.remove_var_list=[]
        self.feature_map=feature_map
        self._is_fitted=False
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            检查特征psi是否满足要求，如果不满足则剔除特征
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        # else:
        #     data=data.copy(deep=True)
        self.col_new=self.col_x
        # print("bbbb", self.col_new)
        self.remove_var_list=[]
        dec_col_cnts =np.sum([0 if data[c].dtype == np.object else 1 for c in self.col_x])
        if dec_col_cnts==0:
            print ("no decimal cols,stop fit")
            self._is_fitted = True
            return self

        am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None)
        
        if self.dic is None:
            self.dic=am.get_percent_cut(data, self.col_x,  perc=self.perc
                                     ,missing=self.miss_val)
        
        if self.feature_ana_df is None:
            self.feature_ana_df=am.data_feature_analysis2(data,dummies_col=self.col_x
                                                          ,split_list_dic=self.dic,
													      data_parts=self.data_parts)
            
        if self.psi_limit:
            self.feature_ana_df_psi=am.psi_calc(self.feature_ana_df,data_parts=self.data_parts)
            self.feature_ana_df_psi["keep"]=1
            for k,v in self.psi_limit.items():
                if k=='max':
                    self.feature_ana_df_psi["psi_max"]=self.feature_ana_df_psi.filter(regex=(self.data_parts+".*psi")).max(axis=1)
                    self.feature_ana_df_psi.loc[self.feature_ana_df_psi["psi_max"]>=v ,"keep"]=0
                elif k=='mean':
                    self.feature_ana_df_psi["psi_mean"]=self.feature_ana_df_psi.filter(regex=(self.data_parts+".*psi")).mean(axis=1)
                    self.feature_ana_df_psi.loc[self.feature_ana_df_psi["psi_mean"]>=v ,"keep"]=0
                elif k=='median':
                    self.feature_ana_df_psi["psi_median"]=self.feature_ana_df_psi.filter(regex=(self.data_parts+".*psi")).median(axis=1)
                    self.feature_ana_df_psi.loc[self.feature_ana_df_psi["psi_median"]>=v ,"keep"]=0
            # print("cccc",self.col_new)
            # self.col_new=list(set(self.feature_ana_df_psi[self.feature_ana_df_psi['keep']==1].index.get_level_values('variable').to_list()))

            tmp = self.feature_ana_df_psi[self.feature_ana_df_psi['keep']==1].index.get_level_values('variable').to_list()
            self.col_new=sorted(list(set(tmp)))
            # self.col_new.sort(key = tmp.index)
            # print("aaaa",self.col_new)
            # self.remove_var_list=list(set(self.col_x)-set(self.col_new))
            self.remove_var_list=list(np.setdiff1d(self.col_x,self.col_new))
        self._is_fitted=True
        return self

    def __getitem__(self,key):
        _check_is_fitted(self)
        return self.feature_ana_df_psi.loc[key]

    def plot(self,key):
        _check_is_fitted(self)
        if isinstance(key,(list,tuple)):
            plot_df = self.feature_ana_df.loc[self.feature_ana_df['variable'].isin(key)].sort_values(['variable','bin','data_parts'])
        else:
            plot_df = self.feature_ana_df.loc[self.feature_ana_df['variable']==key].sort_values(['variable','bin','data_parts'])
        feature_ana_plot(plot_df,path=None,file_prefix=None,excel=None,sheet_name=None,plot_insert_excel=False,if_plot=True)

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
            
        '''
        # data=data.copy(deep=True)
        return data


class FeatureNameChangeTransformer(BaseEstimator, TransformerMixin):
    """特征名称替换Transformer（xgb模型不允许出现[）
      
    Parameters
    ----------
    src: str
       需要替换的字符,默认"["
    target : str
       目标替换字符,默认"_"

    Attributes
    ----------
    col_new :list
        输出返回特征列表

    Notes
    -----
    Data transform type : UPDATE

    """
    
    def __init__(self,col_x,src='[',target='_',feature_map=None):
        self.col_x=col_x
        self.src=src
        self.target=target
        self.process_note={}
        self.feature_map=feature_map
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        self.process_note={i:i.replace(self.src,self.target) for i in self.col_x  if self.src in i }
        self.col_new=[self.process_note[i] if i in self.process_note.keys() else i for i in self.col_x]
        if self.feature_map is not None:
            self.feature_map=self.feature_map.append(pd.DataFrame(self.process_note.items(),columns=['relyon','variable']),ignore_index=True)
        return self

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)
        col_x=set(data.columns.tolist()) & set(self.process_note.keys())
        data.columns= [self.process_note[i] if  i in col_x   else i  for i in data.columns.tolist() ]
        return data


class FeatureStablityRegTransformer(BaseEstimator, TransformerMixin):
    """特征稳定性分析Transformer 
      
    Parameters
    ----------
    col_x: list
       字段列表.
    std_limit: float
       稳定性要求，越大稳定性要求越低
    max_cuts : float
       特征分析最大数量
    min_one_cnt: int
       默认100，枚举值下限，不满足填写fillna的值
    miss_val: int
       缺失值
    data_parts:str
        样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list
        样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足
        data_parts=1 和 2时的样本
    std_limit:float
        特征筛选标准差要求阈值 ，默认0.1
    corr_limit:float
        特征筛选corr要求阈值 ，默认0.2(多样本都需要满足)
    high_lift_limit:float
        特征单箱内高lift要求下限，多份样本上高风险倍数必须大于此阈值，如果不满足则剔除该分箱，该值越高对特征要求越高，取值范围为[1,+∞)
    low_lift_limit:float
        特征单箱内低lift要求上限，多份样本上低风险倍数必须小于此阈值，如果不满足则剔除该分箱，该值越低对特征要求越高，取值范围为[0,1]
    lift_tolerance_cnt:int
        针对不满足high_lift_limit和low_lift_limit 样本数量的忍耐值，默认值为0
    corr_stablity_limit:
        多样本lift趋势相似度阈值，该值越大代表对特征相似度要求越高，默认0.5，不满足的特征将被删除
    sep:str
        衍生变量分割符，默认"^"
    feature_ana_df:pd.DataFrame() or None
        特征分析表，默认None，如果设置不再生成新的feature_ana_df
    dic:dict or None
        特征分割切点集合，默认None，如果配置特征切点，则沿用此切点，不再新找切点

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    remove_var_list :list
        删除特征列表
    feature_ana_df:pd.DataFrame()
        特征分析表
    feature_ana_df_combine:pd.DataFrame()
        合并分箱后的特征分析表
    dic:dict
        特征切点

    Notes
    -----
    Data transform type : DELETE/INSERT

    """
    
    def __init__(self, col_x,std_limit, max_cuts=5, min_one_cnt=0.05,miss_val=-99,\
        graph='',bet=1,data_parts = 'data_parts',
        data_parts_use=None,
        corr_limit=0.2,high_lift_limit=1,low_lift_limit=1,
        lift_tolerance_cnt=0,corr_stablity_limit=0.2,
        data_apply = None,n_jobs=1,
        sep='^',feature_ana_df=None,dic=None,feature_map=None):
        self.col_x=col_x
        self.max_cuts=max_cuts
        self.min_one_cnt=min_one_cnt
        self.miss_val=miss_val
        self.graph=graph
        self.bet=bet
        self.data_parts=data_parts
        self.std_limit=std_limit
        self.data_apply=data_apply
        self.sep=sep
        self.remove_var_list=[]
        self.corr_limit=corr_limit
        self.feature_ana_df =feature_ana_df
        self.dic =dic
        self.data_parts_use=data_parts_use
        self.split_var_list=[]
        self.feature_map=feature_map
        self.high_lift_limit=high_lift_limit
        self.low_lift_limit=low_lift_limit
        self.lift_tolerance_cnt=lift_tolerance_cnt
        self.corr_stablity_limit=corr_stablity_limit
        self.n_jobs=n_jobs

        self._is_fitted = False
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        check_y_is_series(y)

        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        # else:
        #     data=data.copy(deep=True)
        self.col_new=self.col_x
        n_jobs = _effective_n_jobs(self.n_jobs)
        print("n_jobs",n_jobs)
        
        dec_col_cnts =np.sum([0 if data[c].dtype == np.object else 1 for c in self.col_x])
        print (dec_col_cnts)
        if dec_col_cnts==0:
            print ("no decimal cols,stop fit")
            self._is_fitted = True
            return self

        am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None)

        time_start = time.perf_counter()
        if self.dic is None:
            self.dic=am.get_tree_cut_reg(data, self.col_x, y.name, max_cuts=self.max_cuts,
                                     min_one_cnt=self.min_one_cnt,miss_val=self.miss_val)

        self._time_cut = time.perf_counter() - time_start
        print ("_time_cut = ",self._time_cut)

        # print ("dic",self.dic)
        if self.feature_ana_df is None:
            time_fea_ana = time.perf_counter()
            self.feature_ana_df=am.data_feature_reg_analysis(data,self.col_x,self.dic,
                                                     y.name,
													 data_parts=self.data_parts,n_jobs=n_jobs)
            self._time_cut = time.perf_counter() - time_fea_ana
            print ("time_fea_ana = ",self._time_cut)
													 
        # print("feature_ana_df=",self.feature_ana_df)
        if self.data_parts and self.std_limit>0  :
            _,keep_list,self.used_orig_list,self.bulid_var_list,\
            self.split_var_list,remove_list,self.feature_ana_df=\
            am.feature_resp_reg_std_check(self.feature_ana_df,self.col_x,
                                      std_limit=self.std_limit,
                                      data_apply = self.data_apply,
                                      sep=self.sep,high_lift_limit=self.high_lift_limit
                                      ,low_lift_limit=self.low_lift_limit
                                      ,lift_tolerance_cnt=self.lift_tolerance_cnt
                                      ,corr_stablity_limit=self.corr_stablity_limit,miss_val=self.miss_val)

            self.col_new=keep_list
            self.remove_var_list=list(set(self.remove_var_list) | set(remove_list))
            # self.feature_ana_df_combine=am.feature_resp_combine(self.feature_ana_df,self.data_parts)
            if self.feature_map is not None:
                self.feature_map=self.feature_map.append(pd.DataFrame([(self.sep.join(svl),svl[0]) for svl in self.split_var_list],columns=['variable','relyon']),ignore_index=True)

        self.feature_ana_df["corr"]=self.feature_ana_df["corr"].fillna(0)
        if self.corr_limit :
            remove_list=set(self.feature_ana_df.loc[self.feature_ana_df["corr"].abs()<self.corr_limit,'variable'].tolist())

            remove_list_iv=[]
            for i in self.col_new:
                if i.split(self.sep)[0] in remove_list:
                    remove_list_iv.append(i)
            # self.col_new=list(set(self.col_new) - set(remove_list_iv))
            for r in remove_list_iv:
                self.col_new.remove(r)
            self.remove_var_list=list(set(self.remove_var_list)|set(remove_list))
            self._is_fitted = True
        return self

    def __getitem__(self,key):
        _check_is_fitted(self)
        if isinstance(key,(list,tuple)):
            return self.feature_ana_df.loc[self.feature_ana_df['variable'].isin(key)].sort_values(['variable','bin','data_parts'])
        else:
            return self.feature_ana_df.loc[self.feature_ana_df['variable']==key].sort_values(['variable','bin','data_parts'])
    def plot(self,key):
        _check_is_fitted(self)
        if isinstance(key,(list,tuple)):
            plot_df = self.feature_ana_df.loc[self.feature_ana_df['variable'].isin(key)].sort_values(['variable','bin','data_parts'])
        else:
            plot_df = self.feature_ana_df.loc[self.feature_ana_df['variable']==key].sort_values(['variable','bin','data_parts'])
        feature_ana_plot(plot_df,path=None,file_prefix=None,excel=None,sheet_name=None,plot_insert_excel=False,if_plot=True)

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)
        for i in self.split_var_list:
            if i[0] in data.columns.tolist():
                left=float(re.search(r'\[(.+),(.+)\)',str(i[1])).group(1))
                right=float(re.search(r'\[(.+),(.+)\)',str(i[1])).group(2))
                data[i[0]+self.sep+i[1]] = np.where((data[i[0]]>=left) & (data[i[0]]<right),1,0)
        return data


class FillNoneTransformer(BaseEstimator, TransformerMixin):
    """缺失值填充Transformer
    
    Parameters
    ----------
    cols : list 
        入模输入项
    mode : int 
        默认1, 1:统一填充： 2:根据config_df配置文件里的设置填充
    number_fill_mode : int 
        默认1, 1:固定数值填充：  2:均值填充
    number_fill_value : int 
        默认-99 固定数值
    string_fill_mode : int 
        默认1 1:固定数值填充：  2:众数填充：
    string_fill_value : str 
        默认'-99' 固定数值
    config_df :  DataFrame 
        配置文件 默认None
    data_parts:str
        默认'data_parts'样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list or None
        默认None 样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足data_parts=1 和 2时的样本
    feature_map:pd.DataFrame
        默认None,特征图关系

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    na_perc_config :pd.DataFrame
        配置文件-缺失值表
    na_perc_na :pd.DataFrame
        na-缺失值表
    remove_var_list :ls
        被剔除的特征

    Notes
    -----
    Data transform type : UPDATE

    """
    def __init__(self,col_x,mode=1,number_fill_mode=1,number_fill_value=-99,
                 string_fill_mode=1,
                 string_fill_value='-99',
                 config_df=None,
                 data_parts='data_parts',
                 data_parts_use=None,
                 na_limit=None,
                 feature_map=None):
        self.col_x=col_x
        self.mode=mode
        self.number_fill_mode=number_fill_mode
        self.number_fill_value=number_fill_value
        self.string_fill_mode=string_fill_mode
        self.string_fill_value=string_fill_value
        #强制设置None，不支持config_df
        self.config_df=None
        self.col_new=[]
        self.feature_map=feature_map
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.na_limit=na_limit
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        # else:
        #     data=data.copy(deep=True)
            
        self.col_new=self.col_x
        self.remove_var_list=[]
        """
        if self.config_df is not None:
            nan_rate_config = data[self.col_x].isnull().sum()/len(data[self.col_x])
            self.na_perc_config = nan_rate_config.reset_index(name='msr').rename(columns={'index': 'variable'})
            self.na_perc_config=self.na_perc_config.merge(self.config_df ,how='inner',left_on='variable',right_on='feature_list')
            
            self.remove_ls_config = self.na_perc_config.loc[self.na_perc_config["msr"]>=self.na_perc_config["missing_rate"],'variable'].tolist()
            self.remove_var_list.extend(self.remove_ls_config)
        """
        
        if self.na_limit:
            nan_rate_na = data[self.col_x].isnull().sum()/len(data[self.col_x])
            self.na_perc_na = nan_rate_na.reset_index(name='msr').rename(columns={'index': 'variable'})
            self.remove_ls_na = self.na_perc_na.query(
                    '(msr >= {}) '.format(self.na_limit))['variable'].tolist()
            self.remove_var_list.extend(self.remove_ls_na)
        
        self.remove_var_list=list(set(self.remove_var_list))

        for r in self.remove_var_list:
            self.col_new.remove(r)
        # self.col_new = list(np.setdiff1d(self.col_new, self.remove_var_list))
        # self.col_new=list(set(self.col_new)- set(self.remove_var_list))
        return self

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)

        if self.config_df is not None:
            ls=set(self.config_df["feature_list"]) & set(self.col_new) & set(data.columns.tolist())
            for i in ls:
                data[i]=data[i].fillna(self.config_df.loc[self.config_df["feature_list"]==i,'fill_mode'].values[0])
        else:
            col_x=list(set(self.col_new) & set(data.columns.tolist()))
            am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None)
            data=am.fill_none(data,col_x,self.mode,self.number_fill_mode,self.number_fill_value,self.string_fill_mode,self.string_fill_value,self.config_df)
            
        return data


class DupValueCheckTransformer(BaseEstimator, TransformerMixin):
    """重复值检查Transformer
    
    Parameters
    ----------
    cols : list 
        入模输入项
    top_limit : float 
        一值率上限，默认1，取值(0,1]
    bottom_limit : 0 
        一值率下限，默认0，取值[0,1)
    data_parts:str
        默认'data_parts'样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list or None
        默认None 样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足data_parts=1 和 2时的样本
    feature_map:pd.DataFrame
        默认None,特征图关系

    Attributes
    ----------
    col_new :list
        输出返回特征列表

    Notes
    -----
    Data transform type : DELETE

    """
    def __init__(self,col_x,
                 top_limit=1,
                 bottom_limit=0,
                 data_parts='data_parts',
                 data_parts_use=None,
                 feature_map=None):
        self.col_x=col_x
        self.col_new=[]
        self.feature_map=feature_map
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.top_limit=top_limit
        self.bottom_limit=bottom_limit
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        # else:
            # data=data.copy(deep=True)
            # pass
            
        self.col_new=self.col_x
        self.remove_var_list=[]
        
        idt_rate = lambda a: a.value_counts().max() / a.size
        self.identical_perc = data[self.col_x].apply(idt_rate).reset_index(name='idr').rename(columns={'index': 'variable'})
        print ("identical_perc=",self.identical_perc)
        
        self.remove_var_list=self.identical_perc.loc[(self.identical_perc["idr"]>=self.top_limit) | (self.identical_perc["idr"]<=self.bottom_limit),'variable'].tolist()
        
        # self.col_new=list(set(self.col_new) - set(self.remove_var_list))
        for r in self.remove_var_list:
            self.col_new.remove(r)
        return self

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        # data=data.copy(deep=True)
        # rm_col_x=list(set(self.remove_var_list) & set(data.columns.tolist()))
        # data=data.drop(rm_col_x,axis=1)
        return data


class StringDealerTransformer(BaseEstimator, TransformerMixin):
    """字符型处理Transformer（LabelEncoder & Dummy）
    
    Parameters
    ----------
    cols : list 
        入模输入项
    dummies_limit : int 
        默认10 字符变量label_encoder转化阈值，大于使用label_encoder，小于使用哑变量
    sep : str 
        默认"^" 衍生字段分割符
    data_parts:str
        默认'data_parts'样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list or None
        默认None 样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足data_parts=1 和 2时的样本
    feature_map:pd.DataFrame
        默认None,特征图关系

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    process_note :dict
        特征对应关系字典

    Notes
    -----
    Data transform type : UPDATE/INSERT

    """
    def __init__(self,col_x,
                 dummies_limit=10,
                 sep="^",
                 data_parts=' ',
                 data_parts_use=None,feature_map=None):
        self.col_x=col_x
        self.dummies_limit=dummies_limit
        self.sep=sep
        self.col_new=[]
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.feature_map=feature_map
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        else:
            # data=data.copy(deep=True)
            pass
        am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None)
        # print (data.shape)
        _, self.col_new, self.process_note=am.string_dealer(data,self.col_x,self.dummies_limit,self.sep)
        
        col_new_dic={}
        for k in self.process_note.keys():
            if isinstance(self.process_note[k],LabelBinarizer):
                temp_dic={k +self.sep + str(i):k for i in self.process_note[k].classes_}
                col_new_dic=dict(col_new_dic,**temp_dic)
        # print ("****************",self.feature_map)
        if self.feature_map is not None:
            self.feature_map=self.feature_map.append(pd.DataFrame({"variable":list(col_new_dic.keys()),"relyon":list(col_new_dic.values())}),ignore_index=True)
        return self

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)
        col_x=set(data.columns.tolist()) & set(self.process_note.keys())
        data = string_dealer_oot(self.process_note,col_x,data,self.sep)
        return data


class CorrCheckTransformer(BaseEstimator,TransformerMixin):
    """相关性检查CorrCheckTransformer
    
    Parameters
    ----------
    col_x : list 
        特征列表
    corr_limit : float 
        默认0.8,相关性检查阈值，超过则删除
    data_parts:str
        默认'data_parts'样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list or None
        默认None 样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足data_parts=1 和 2时的样本
    sort:None or str
        默认None,None的情况下根据col_x的顺序选择变量，顺序在前的变量有先选择，当为'iv'的情况下，会根据iv值高低优先选择iv高的特征,当为'corr'则表示相关性顺序筛选
    miss_val:int
        默认-99,缺失值填充值

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    corr_table :pd.DataFrame()
        特征相关性表
    remove_var_list :list
        删除特征列表
    dic :dict
        删除特征列表
    iv:pd.Series()
        iv对应关系

    Notes
    -----
    Data transform type : DELETE

    """
    def __init__(self,col_x,corr_limit=0.8,
                 data_parts='data_parts',
                 data_parts_use=None,
                 sort=None,
                 miss_val=-99,feature_map=None):
        self.col_x=col_x
        self.corr_limit=corr_limit
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.sort=sort
        self.miss_val=miss_val
        self.feature_map=feature_map
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''

        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        else:
            # data=data.copy(deep=True)
            pass
            
        self.remove_var_list=set()
        self.origin_digit_ls=data[self.col_x].dtypes[data[self.col_x].dtypes!='object'].index.tolist()
        # self.other_ls=list(set(self.col_x) - set(self.origin_digit_ls))
        self.other_ls=list(np.setdiff1d(self.col_x,self.origin_digit_ls))
        if self.sort == 'iv':
            if y is None:
                raise Exception("iv mode should have y variable!")
            else:
                check_y_is_series(y)
                am=Automan_Data_Explore(log_dict_flag=False,log_dict_unkeep_type=None,config_file=None)

                self.dic=am.get_percent_cut(data, self.origin_digit_ls,  perc=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
                                         ,missing=self.miss_val)
                self.iv=am.data_feature_analysis_solo(data,y.name,self.origin_digit_ls,self.dic)['iv']

                self.corr_table=data[self.iv.index.tolist()].corr().apply(np.abs)
        elif self.sort == 'corr':
            temp_ls=data[self.origin_digit_ls].apply(lambda x:x.corr(y)).fillna(0)\
            .apply(abs).sort_values(ascending=False).index.to_list()
            self.corr_table=data[temp_ls].corr().apply(np.abs)
        else:
            self.corr_table=data[self.origin_digit_ls].corr().apply(np.abs)

        array = self.corr_table.values>=self.corr_limit
        array[np.diag_indices_from(array)]=False
        ind=np.argwhere(array)
        for i in ind:
            # print (i[0],i[1])
            if i[0] in self.remove_var_list or i[1] in self.remove_var_list:
                continue
            # print (self.remove_var_list,i.max())
            self.remove_var_list=self.remove_var_list | {i.max()}
        # self.col_new=self.corr_table.index[list(set(np.arange(len(self.origin_digit_ls))) - self.remove_var_list)]\
        #     .tolist()
        tmp_ls = list(np.setdiff1d(np.arange(len(self.origin_digit_ls)) ,self.remove_var_list))
        self.col_new=self.corr_table.index[tmp_ls].tolist()
        self.col_new.extend(self.other_ls)
        self.remove_var_list=self.corr_table.index[list(self.remove_var_list)].tolist()
        
        return self
    
    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)
        return data


class DataDiffCheckTransformer(BaseEstimator,TransformerMixin):
    """样本分布检查DataDistCheckTransformer
    
    Parameters
    ----------
    col_x : list 
        特征列表
    train_data_parts:list
        训练样本data_parts集合，例如[1,2]代表数据集中满足data_parts=1和2时的样本
    test_data_parts:list
        测试样本data_parts集合，例如[3,4]代表数据集中满足data_parts=3和4时的样本
    data_parts:str
        默认'data_parts' 样本分割标志字段，默认data_parts,必须在数据集中出现
    feature_map:pd.DataFrame
        默认None 特征图

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    remove_var_list :list
        删除特征列表
    data_diff_score:float
        样本差异评分，数值越大差异越大 <0.1差异较小， >0.6有很明显的差异 ，>0.4有明显差异
    var_diff_score:pd.Series
        样本差异评分，数值越大差异越大对差异的影响作用越大，请检查变量是否存在问题
    trace:list
        明细
    train_data_sim_score:np.ndarray(dim: train_samples * 1)
        训练样本上训练集和测试集的样本相似度得分
    test_data_sim_score:np.ndarray(dim: test_samples * 1)
        测试样本上训练集和测试集的样本相似度

    Notes
    -----
    Data transform type : None

    """
    def __init__(self,col_x,
                 train_data_parts=None,
                 test_data_parts=None,
                 data_parts='data_parts',
                 feature_map=None):
        self.col_x=col_x
        self.data_parts=data_parts
        self.train_data_parts=train_data_parts
        self.test_data_parts=test_data_parts
        self.feature_map=feature_map
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        
        '''
        self.col_new=self.col_x
        data_train=data.loc[data[self.data_parts].isin(self.train_data_parts),:].reset_index(drop=True).copy(deep=True)
        data_test=data.loc[data[self.data_parts].isin(self.test_data_parts),:].reset_index(drop=True).copy(deep=True)
        data_train['flag']=0
        data_test['flag']=1
        t=pd.concat([data_train,data_test],ignore_index=True)

        folds_2 = StratifiedKFold(n_splits=2, shuffle=True, random_state=8888)
        X_train=t[self.col_x]
        y_train=t['flag']
        oof_xgb = np.zeros(len(X_train))
        self.trace={}
        clf=xgb.XGBClassifier()
        for fold_, (trn_idx, val_idx) in enumerate(folds_2.split(X_train,y_train)):
            print("fold {}".format(fold_ + 1))
            
            trn_data = X_train.iloc[trn_idx], y_train.iloc[trn_idx]
            val_data = (X_train.iloc[val_idx], y_train.iloc[val_idx])
            
            ev = [val_data]
            clf.fit(X_train.iloc[trn_idx],y=y_train.iloc[trn_idx],
                 eval_set=ev, 
                 eval_metric=ks_score,
                 early_stopping_rounds=50, 
                 verbose=False,
                 )
            oof_xgb[val_idx] = clf.predict_proba(X_train.iloc[val_idx], ntree_limit=clf.best_ntree_limit)[:,1]

            self.trace[fold_]=[clf.best_score,pd.Series(clf.feature_importances_,index=self.col_x).sort_values(ascending=False)]

        self.remove_var_list=[]
        self.train_data_sim_score=oof_xgb[:len(data_train)]
        self.test_data_sim_score=oof_xgb[len(data_train):]
        
        self.data_diff_score=round(abs((self.trace[0][0] + self.trace[1][0])/2),4)
        self.var_diff_score=(self.trace[0][1] + self.trace[1][1])/2
        self.var_diff_score=self.var_diff_score.sort_values(ascending=False)
        return self
    
    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)
        return data


class DataTypeConvertTranformer(BaseEstimator,TransformerMixin):
    """样本分布检查DataDistCheckTransformer
    
    Parameters
    ----------
    col_x : list 
        特征列表
    config_df:pd.DataFrame
        训练样本data_parts集合，例如[1,2]代表数据集中满足data_parts=1和2时的样本
    data_parts:str
        默认'data_parts' 样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list or None
        默认None 样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足data_parts=1 和 2时的样本
    feature_map:pd.DataFrame
        默认None 特征图

    Attributes
    ----------
    col_new :list
        输出返回特征列表

    Notes
    -----
    Data transform type : UPDATE

    """
    def __init__(self,col_x,
                 config_df,
                 data_parts='data_parts',
                 data_parts_use=None,
                 feature_map=None):
        self.col_x=col_x
        self.config_df=config_df
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.feature_map=feature_map

    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        self.col_new=self.col_x
        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        else:
            # data=data.copy(deep=True)
            pass
        
        if not isinstance(self.config_df,pd.DataFrame):
            raise TypeError("config_df's type is not correct,it should be pd.DataFrame!")
            
        if 'feature_list' not in self.config_df.columns.tolist() or 'data_dtype' not in self.config_df.columns.tolist() :
            raise Exception("config_df has not feature_list or data_dtype!")
            
        if len(set(self.config_df.data_dtype.tolist()) - set(['str','float'])) != 0:
            raise Exception("config_df's dtype must be float or str!")
        
        self.dec_col=self.config_df.loc[(self.config_df['feature_list'].isin(self.col_new)) & (self.config_df['data_dtype']=='float'),'feature_list'].tolist()
        self.str_col=self.config_df.loc[(self.config_df['feature_list'].isin(self.col_new)) & (self.config_df['data_dtype']=='str'),'feature_list'].tolist()
        
        self.unmatch_col=[]
        for d in self.dec_col:
            if not is_numeric_dtype(data[d]):
                self.unmatch_col.append(d)
        
        if len(self.unmatch_col)>0:
            raise Exception("data columns {}  don't match with config's data_dtype!".format(self.unmatch_col))
            
        return self
    
    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)
        dec_ls = list(set(self.dec_col) & set(data.columns.tolist()))
        str_ls = list(set(self.str_col) & set(data.columns.tolist()))
        
        if len(dec_ls) > 0 :
            data[dec_ls]=data[dec_ls].astype(float)
        if len(str_ls) > 0 :
            data[str_ls]=data[str_ls].astype(str)
            data[str_ls].replace('nan',np.nan)
            
        return data


class MissingValueSettingTransformer(BaseEstimator,TransformerMixin):
    """缺失值设定MissingValueSettingTransformer
    
    Parameters
    ----------
    col_x : list 
        特征列表
    missing_list:list
        缺失值定义列表
    data_parts:str
        默认'data_parts' 样本分割标志字段，默认data_parts,必须在数据集中出现
    feature_map:pd.DataFrame
        默认None 特征图

    Attributes
    ----------
    col_new :list
        输出返回特征列表

    Notes
    -----
    Data transform type : UPDATE

    """
    def __init__(self,col_x,missing_list,
                 data_parts='data_parts',
                 feature_map=None):
        self.col_x=col_x
        self.missing_list=missing_list
        self.data_parts=data_parts
        self.feature_map=feature_map
        
    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身类型
        '''
        self.col_new=self.col_x

        return self
    
    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        
        data=data.copy(deep=True)
        data_col = list( set (data.columns.tolist())  & set(self.col_new))
        if len(self.missing_list)>0:
            descimal_list=[i for i in self.missing_list if isinstance(i,(int,float)) ]
            descimal_list=list(map(str,descimal_list))
            self.repl_list=descimal_list+self.missing_list
            self.repl_list=list(set(self.repl_list))
            data[data_col]=data[data_col].replace(self.repl_list,np.nan)
        return data


class ProbSmoothingStr2RspTransformer(BaseEstimator,TransformerMixin):
    """概率平滑字符转响应率Transformer

    Parameters
    ----------
    col_x: list
       特征列表.
    bin_limit : int
       类别数量限制
    smoothing: float
       平滑系数，越大平滑程度越强
    data_parts: str
       数据集切分字段.
    data_parts_use: list or None
       样本分析列表，eg:[1,2],只会分析data_parts为1和2的样本，如果为None分析整个数据集
    feature_map: pd.DataFrame
       特征图

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    dict_map :dict
        特征映射关系字典

    Notes
    -----
    Data transform type : UPDATE

    """
    def __init__(self,
                 col_x,
                 bin_limit=20,
                 smoothing=1.0,
                 data_parts='data_parts',
                 data_parts_use=None,
                 feature_map=None):
        self.col_x=col_x
        self.bin_limit=bin_limit
        self.smoothing=smoothing
        self.dict_map=dict()
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.feature_map=feature_map
        self.col_new=col_x

    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身对象本身
        '''
        self.col_new=self.col_x
        
        if y is  None:
            raise TypeError('missing argument: ''y''')
        else:
            check_y_is_series(y)
            if self.data_parts_use:
                data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
            else:
                # data=data.copy(deep=True)
                pass
                
            self.obj_cols = []
            for idx, dt in enumerate(data[self.col_x].dtypes):
                if dt == 'object' or pd.api.types.is_categorical_dtype(dt):
                    self.obj_cols.append(data[self.col_x].columns.values[idx])
            
            if len(self.obj_cols) == 0 :
                return self
            print ("self.obj_cols= ",self.obj_cols)
            # print (y.value_counts(dropna=False))
            self.sample_mean = data[y.name].mean()
            self.dict_map = {}
            # print("data.shape=",data.shape)
            data[self.obj_cols] = data[self.obj_cols].astype(str)
            for col in self.obj_cols:
                stats = data[y.name].groupby(data[col]).agg(['count', 'mean'])
                # print ("stats = ",stats)
                smoove = 1 / (1 + np.exp(-(stats['count'] - self.bin_limit) / self.smoothing))
                # print ("smoove = ",stats)
                smoothing = self.sample_mean * (1 - smoove) + stats['mean'] * smoove
                smoothing[stats['count'] == 1] = self.sample_mean
                self.dict_map[col] = smoothing
        return self

    def transform(self,data):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)

        for i in data.columns.tolist():
            if i in self.dict_map.keys():
                data[i] = data[i].astype(str)
                data[i]=data[i].map(self.dict_map[i]).fillna(self.sample_mean)
                # data[i]=data[i].map(self.dict_map[i])
        return data


class OrderStr2RspTransformer(BaseEstimator,TransformerMixin):
    """顺序Target Encoding Transformer

    Parameters
    ----------
    col_x: list
       特征列表.
    order_col : None or str
       排序字段列表，默认为None，如果为None则按照样本顺序编码，如果设置为字段则按照该字段升序编码
    sigma : None or float
       扰动系数，越大正则能力越强，默认None
    smoothing: float
       平滑系数，越大平滑程度越强，默认1
    data_parts: str
       数据集切分字段.
    data_parts_use: list or None
       样本分析列表，eg:[1,2],只会分析data_parts为1和2的样本，如果为None分析整个数据集
    feature_map: pd.DataFrame
       特征图

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    dict_map :dict
        特征映射关系字典

    Notes
    -----
    Data transform type : UPDATE

    """
    def __init__(self,
                 col_x,
                 order_col=None,
                 # sigma=None, 
                 smoothing=1,
                 # random_state=None, 
                 data_parts='data_parts',
                 data_parts_use=None,
                 feature_map=None):
        self.col_x=col_x
        self.dict_map=dict()
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.feature_map=feature_map
        self.col_new=col_x
        # self.sigma = sigma
        self.smoothing = smoothing
        # self.random_state = random_state
        
        self._is_fitted = False

    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量
        
        Returns
        -------
        self:对象本身对象本身
        '''
        self.col_new=self.col_x
        self.dict_map = {}
        
        if y is  None:
            raise TypeError('missing argument: ''y''')
        else:
            check_y_is_series(y)
            if self.data_parts_use:
                data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
                
            self.obj_cols = []
            for idx, dt in enumerate(data[self.col_x].dtypes):
                if dt == 'object' or pd.api.types.is_categorical_dtype(dt):
                    self.obj_cols.append(data[self.col_x].columns.values[idx])
            
            if len(self.obj_cols) == 0 :
                return self
            
            # print (data[y.name].value_counts(dropna=False))
            
            data[self.obj_cols] = data[self.obj_cols].astype(str)
            self.dict_map = self._fit(
                data[self.obj_cols], data[y.name],
                cols=self.obj_cols
            )
            
            self._is_fitted = True
            # X_temp = self.transform(data[self.obj_cols], y)
        return self
    
    def _fit(self, X_in, y, cols):
        X = X_in.copy(deep=True)

        self.sample_mean = y.mean()

        return {col: self._fit_column_map(X[col], y) for col in cols}

    def _fit_column_map(self, series, y):
        category = pd.Categorical(series)

        categories = category.categories
        codes = category.codes.copy()
        
        #增加缺失值
        codes[codes == -1] = len(categories)
        categories = np.append(categories, np.nan)

        return_map = pd.Series(dict([(code, category) for code, category in enumerate(categories)]))

        result = y.groupby(codes).agg(['sum', 'count'])
        return result.rename(return_map)
    
    def transform(self,data,y=None):
        '''transform函数
        
        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集
        
        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data=data.copy(deep=True)
        self._is_data_parts_existed =self.data_parts  in data.columns.tolist()
        obj_cols = list(self.dict_map.keys() & set(data.columns.tolist()))
        
        if len(obj_cols) == 0:
            return data
        else:
            data[obj_cols]  = data[obj_cols].astype(str) 
            data = self._transform(
                data, y,
                mapping={c:self.dict_map[c] for c in obj_cols},
                data_parts = self.data_parts
            )
        
        return data

    def _transform(self, X, y, mapping=None,data_parts='data_parts'):

        if y is None:
            for col, colmap in mapping.items():
                level_notunique = colmap['count'] > 1
    
                unique_train = colmap.index
                unseen_values = pd.Series([x for x in X[col].unique() if x not in unique_train], dtype=unique_train.dtype)
                is_unknown_value = X[col].isin(unseen_values.astype(str))

                level_means = ((colmap['sum'] + self.sample_mean) / (colmap['count'] + self.smoothing)).where(level_notunique, self.sample_mean)
                X[col] = X[col].map(level_means)
                
                if X[col].dtype.name == 'category'  or X[col].dtype.name  == 'object':
                    X[col] = X[col].astype(float)
                X.loc[is_unknown_value, col] = self.sample_mean
                
        elif not self._is_data_parts_existed:
            for col, colmap in mapping.items():
                
                unique_train = colmap.index
                unseen_values = pd.Series([x for x in X[col].unique() if x not in unique_train], dtype=unique_train.dtype)
                is_unknown_value = X[col].isin(unseen_values.astype(str))
                
                self.temp = y.groupby(X[col].astype(str)).agg(['cumsum', 'cumcount'])
                X[col] = (self.temp['cumsum'] - y + self.sample_mean) / (self.temp['cumcount'] + self.smoothing)
    
                if X[col].dtype.name == 'category'  or X[col].dtype.name  == 'object':
                    X[col] = X[col].astype(float)
                X.loc[is_unknown_value, col] = self.sample_mean
        elif self.data_parts_use is None:
            for col, colmap in mapping.items():
                
                unique_train = colmap.index
                unseen_values = pd.Series([x for x in X[col].unique() if x not in unique_train], dtype=unique_train.dtype)
                is_unknown_value = X[col].isin(unseen_values.astype(str))
                
                self.temp = y.groupby(X[col].astype(str)).agg(['cumsum', 'cumcount'])
                X[col] = (self.temp['cumsum'] - y + self.sample_mean) / (self.temp['cumcount'] + self.smoothing)
    
                if X[col].dtype.name == 'category'  or X[col].dtype.name  == 'object':
                    X[col] = X[col].astype(float)
                X.loc[is_unknown_value, col] = self.sample_mean
        else:
            for col, colmap in mapping.items():
                level_notunique = colmap['count'] > 1
    
                unique_train = colmap.index
                unseen_values = pd.Series([x for x in X[col].unique() if x not in unique_train], dtype=unique_train.dtype)
                is_unknown_value = X[col].isin(unseen_values.astype(str))
                
                C=X[self.data_parts].isin(self.data_parts_use)
                if any(~C):
                    level_means = ((colmap['sum'] + self.sample_mean) / (colmap['count'] + self.smoothing)).where(level_notunique, self.sample_mean)
                    X.loc[~C,col] = X.loc[~C,col].map(level_means)
                    
                if any(C):
                    self.temp = y.loc[C].groupby(X.loc[C,col].astype(str)).agg(['cumsum', 'cumcount'])
                    X.loc[C,col]  = (self.temp['cumsum'] - y.loc[C] + self.sample_mean) / (self.temp['cumcount'] + self.smoothing)

                if X[col].dtype.name == 'category'  or X[col].dtype.name  == 'object':
                    X[col] = X[col].astype(float)
                X.loc[is_unknown_value, col] = self.sample_mean

        return X

    def fit_transform(self, X, y=None, **fit_params):
        """
        Fit to data, then transform it.

        Fits transformer to X and y with optional parameters fit_params
        and returns a transformed version of X.

        Parameters
        ----------
        X : numpy array of shape [n_samples, n_features]
            Training set.

        y : numpy array of shape [n_samples]
            Target values.

        **fit_params : dict
            Additional fit parameters.

        Returns
        -------
        X_new : numpy array of shape [n_samples, n_features_new]
            Transformed array.
        """
        # non-optimized default implementation; override when a better
        # method is possible for a given clustering algorithm
        # fit method of arity 2 (supervised transformation)
        return self.fit(X, y, **fit_params).transform(X,y)


class TfidfStr2RspTransfomer(BaseEstimator, TransformerMixin):
    """频率Tfidf Encoding Transformer

    Parameters
    ----------
    col_x: list
       特征列表.
    bin_limit: int
       类别阈值.
    sigma : None or float
       扰动系数，越大正则能力越强，默认None
    smoothing: float
       平滑系数，越大平滑程度越强，默认1
    data_parts: str
       数据集切分字段.
    data_parts_use: list or None
       样本分析列表，eg:[1,2],只会分析data_parts为1和2的样本，如果为None分析整个数据集
    feature_map: pd.DataFrame
       特征图

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    dict_map :dict
        特征映射关系字典

    Notes
    -----
    Data transform type : UPDATE

    """

    def __init__(self,
                 col_x,
                 bin_limit=20,
                 data_parts='data_parts',
                 data_parts_use=None,
                 feature_map=None):
        self.col_x = col_x
        self.bin_limit = bin_limit
        self.data_parts = data_parts
        self.data_parts_use = data_parts_use
        self.feature_map = feature_map
        self.dict_map = dict()
        self.col_new = col_x

    def fit(self, data, y=None):
        '''fit函数

        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量

        Returns
        -------
        self:对象本身类型
        '''

        self.col_new = self.col_x
        if y is None:
            raise TypeError('missing argument: ''y''')
        else:
            check_y_is_series(y)
            if self.data_parts_use:
                data = data.loc[data[self.data_parts].isin(self.data_parts_use), :].reset_index(drop=True).copy(
                    deep=True)
            # else:
            #     data=data.copy(deep=True)

            self.obj_cols = []
            for idx, dt in enumerate(data[self.col_x].dtypes):
                if dt == 'object' or pd.api.types.is_categorical_dtype(dt):
                    self.obj_cols.append(data[self.col_x].columns.values[idx])

            if len(self.obj_cols) == 0:
                return self
            print("self.obj_cols= ", self.obj_cols)
            self.dict_map = {}
            self.sample_mean = data[y.name].mean()
            data[self.obj_cols] = data[self.obj_cols].astype(str)
            for col in self.obj_cols:
                states = data[y.name].groupby(data[col]).agg({'sum': np.sum, 'cnt': np.size})
                bad_num = states['sum'].sum()
                cust_cnt = data.shape[0]
                states = states[states['cnt'] >= self.bin_limit].assign(
                    tf=lambda x: x['sum'] / bad_num)
                states['idf'] = states['cnt'].apply(lambda x: math.log(cust_cnt / x))
                states['tfidf'] = states['tf'] * states['idf']
                self.dict_map[col] = dict(zip(states.index, states['tfidf'].round(4)))
            return self

    def transform(self, data):
        '''transform函数

        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集

        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data = data.copy(deep=True)

        for i in data.columns.tolist():
            if i in self.dict_map.keys():
                data[i] = data[i].astype(str)
                data[i] = data[i].map(self.dict_map[i]).fillna(self.sample_mean)
        return data


class Feature2ModelTransformer(BaseEstimator, TransformerMixin):
    """特征消歧Transformer

    Parameters
    ----------
    col_x: list
       字段列表.
    transfer_feature_type:str
        F2M转换对象，“NOT-MONO”：转换非单调特征，"ALL"：转换所有特征,None:不转换任何特征，默认："NOT_MONO"
    min_one_cnt: float
       默认0.02，单个箱体内样本数量下限
    cut_space: dict
       特征分箱参数空间
       eg:{"n_estimators":[1],
                 "max_depth": [3,4,5],
                 "min_child_weight":[1,3,5,10,20],
                 "learning_rate":[1],
                 }
    cut_iter: int
       默认5，单特征调参轮数
    miss_val: int
       缺失值,默认-99
    n_jobs: int
       并行计算数,默认-1
    exclude_col: list
       排除列表,默认None,如果配置，则列表中特征不进行F2M转换
    inculde_col: list
       转换列表,默认None,如果配置，则只有该列表中的特征进行转换
    data_parts:str
        样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list
        样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足
        data_parts=1 和 2时的样本
    data_parts_oob:list
        默认None，袋外样本列表，假设data_parts_use为[1,2,3,4],data_parts_oob为None时，[1,2,3,4]均为袋外样本，
        如果data_parts_oob为[3,4]，代表1,2是训练样本，3,4作为袋外验证模型
    user_mc_dict:dict
        默认{},用户自定义单调性字典，key代表特征，value代表趋势： 1：单调上升，-1：单调下降，0：不单调
        配置之后不会计算特征趋势，之间沿用用户定义的单调性趋势
         eg: {'study_app_cnt': -1,
         'selffill_marital_status': 0
         'td_xyf_dq_score': 1,
         'td_zhixin_score': -1,}
    verbose:boolean
        默认False，日志等级
    random_state:int
        默认0，随机数种子

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    remove_var_list :list
        删除特征列表
    mc_dict_checked:dict
        检查后单调约束特征配置字典
    cut_auc_dic:dict
        单特征模型auc结果集合
    dic:dict
        初始分箱切点
    cut_best_clf_dic:dict
        特征最优分类器字典
    _binned_variables:OptimalBinning
        oob样本分箱切点下统计数据对象

    Notes
    -----
    Data transform type : UPDATE/DELETE

    """

    def __init__(self, col_x,
                 transfer_feature_type = 'NOT-MONO',
                 min_one_cnt=0.02,
                 cut_space={"n_estimators":[5],
                 "max_depth": [3,4,5],
                 "min_child_weight":[3,5,10],
                 },
                 cut_iter=5,
                 miss_val=-99,
                 user_mc_dict={},
                 exclude_col=None,
                 include_col=None,
                 n_jobs=1,
                 random_state = 0,
                 data_parts='data_parts',
                 data_parts_oob=None,
                 data_parts_use=None,
                 verbose=False,
                 feature_map=None):
        self.col_x = col_x
        self.transfer_feature_type = transfer_feature_type
        self.min_one_cnt = min_one_cnt
        self.miss_val = miss_val
        self.data_parts = data_parts
        self.data_parts_use = data_parts_use
        self.feature_map = feature_map
        self.n_jobs = n_jobs
        self.cut_space = cut_space
        self.cut_iter=cut_iter
        self.data_parts_oob = data_parts_oob
        self.random_state = random_state
        self.user_mc_dict = user_mc_dict
        self.exclude_col = exclude_col
        self.verbose = verbose
        self.include_col = include_col

        self._binned_variables = {}
        self._variable_stats = {}
        self.remove_var_list = []
        self._is_fitted = False
        self.selection_criteria = None
        self._target_dtype = 'binary'
        self.mc_dict_checked={}
        self.f2m_col = []

    def fit(self, data, y=None):
        '''fit函数

        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量

        Returns
        -------
        self:对象本身类型
        '''

        if self.data_parts is  None:
            if self.data_parts not in data.columns():
                raise Exception("没有data_parts 字段")
            if self.data_parts_use or self.data_parts_oob:
                raise Exception("没有data_parts 字段的情况下data_parts_use 和 oob_data_parts 必须是None")
            data_oob = data.copy()
        else:
            if not self.data_parts_use  and not self.data_parts_oob :
                data_fit = data.copy()
                data_oob = data.copy()
            elif not  self.data_parts_use  and self.data_parts_oob:
                # fit_data_parts = list(set(data["data_parts"].unique()) - set(self.data_parts_oob))
                fit_data_parts = list(np.setdiff1d(data["data_parts"].unique(),self.data_parts_oob))
                if len (fit_data_parts) == 0:
                    raise Exception("fit_data_parts does not exist!")
                data_fit = data.loc[data[self.data_parts].isin(fit_data_parts)].reset_index(drop=True)
                data_oob = data.loc[data[self.data_parts].isin(self.data_parts_oob)].reset_index(drop=True)
            elif  self.data_parts_use  and not self.data_parts_oob:
                data_fit = data.loc[data[self.data_parts].isin(self.data_parts_use)].reset_index(drop=True)
                data_oob = data.loc[data[self.data_parts].isin(self.data_parts_use)].reset_index(drop=True)
            else:
                # fit_data_parts = list(set(self.data_parts_use) - set(self.data_parts_oob))
                fit_data_parts = list(np.setdiff1d(self.data_parts_use,self.data_parts_oob))
                if len (fit_data_parts) == 0:
                    raise Exception("fit_data_parts does not exist!")
                data_fit = data.loc[data[self.data_parts].isin(fit_data_parts)].reset_index(drop=True)
                data_oob = data.loc[data[self.data_parts].isin(self.data_parts_oob)].reset_index(drop=True)

            print (f"data_fit.shape = {data_fit.shape},data_oob.shape = {data_oob.shape}")

        check_y_is_series(y)
        # n_jobs = _effective_n_jobs(self.n_jobs)
        # print("n_jobs", n_jobs)
        self.col_new = self.col_x[:]
        self.dec_col = [c  for c in self.col_x if np.issubdtype(data[c].dtype, np.number) ]
        self.dec_col = np.setdiff1d (self.dec_col , self.exclude_col).tolist()
        if self.include_col:
            self.dec_col = [ic for ic in self.include_col if ic in self.dec_col]
        # self.dec_col = [c  for c in self.col_x if data[c].dtype.kind in (['i','u','f','c']) ]
        self._n_variables = len(self.dec_col)
        print(self._n_variables)
        if self._n_variables == 0:
            print("no column for f2m！")
            self._is_fitted = True
            return self

        #mc_dict setup
        for c in self.dec_col:
            if c in self.user_mc_dict.keys() :
                # if v in [-1,1]:
                self.mc_dict_checked[c] = self.user_mc_dict[c]
            else:
                _trend = trend_decision(col_x=data_fit[c],
                                                 col_y =data_fit[y.name] ,
                                                 min_samples_leaf = self.min_one_cnt,
                                                 miss_val=self.miss_val)

                if _trend == "ascending":
                    self.mc_dict_checked[c] = 1
                elif _trend == "descending":
                    self.mc_dict_checked[c] = -1
                else:
                    self.mc_dict_checked[c] = 0

        if self.transfer_feature_type == 'NOT-MONO':
            self.f2m_col = [k for k in self.mc_dict_checked.keys() if self.mc_dict_checked[k] == 0]
        elif self.transfer_feature_type == 'ALL':
            self.f2m_col = self.dec_col[:]
        else:
            self.f2m_col = []

        if self.f2m_col:
            self._fit(data_fit,data_oob,y.name)

        self._is_fitted = True
        return self

    def _fit(self,data,data_oob,col_y,**kwargs):
        time_start = time.perf_counter()

        self.dic = {}
        self.param_space = self._make_opt_param_space()
        self.cut_clf_dic={}
        for i in self.f2m_col:
            # print (i)
            self.cut_clf_dic.update( self._cut_search(i,data[[i]],data[col_y]) )

        self.cut_auc_dic = {}
        self.cut_best_clf_dic = {}
        data_oob_pred = pd.DataFrame()
        for col,clfs in self.cut_clf_dic.items():
            auc = np.zeros(self.cut_iter)
            for e,clf in enumerate(clfs):
                auc[e] = metrics.roc_auc_score(data_oob[col_y],\
                                         clf.predict_proba(data_oob[[col]])[:,1])
            self.cut_auc_dic[col] = auc
            # cov = auc.std(axis=0)/(auc.mean(axis=0) + 1e-6)
            self.cut_best_clf_dic[col] = self.cut_clf_dic[col][self.cut_auc_dic[col].argmax()]
            data_oob_pred[col] = self.cut_best_clf_dic[col].predict_proba(data_oob[[col]])[:,1]

        # data_oob_pred = pd.DataFrame( np.concatenate([self.cut_best_clf_dic[x].predict_proba(data_oob[[x]])[:,1].reshape(-1,1) for x in self.col_x],axis=1) ,columns = self.cut_clf_dic.keys())
        # print (data_oob_pred)
        self.dic ={x:list(map(lambda d:round(d,6),sorted(data_oob_pred[x].unique()))) for x in data_oob_pred.columns}
        # print("self.dic=",self.dic)
        # self._temp_df =pd.DataFrame( np.concatenate([self.cut_best_clf_dic[x].predict_proba(data[[x]])[:,1].reshape(-1,1) for x in self.dec_col],axis=1) ,columns = self.col_x)
        # self.binning_process = BinningProcess(col_x, max_n_bins=20,min_prebin_size = self.min_one_cnt,n_jobs=self.n_jobs)
        # self.binning_process.fit(data_oob_pred[self.f2m_col], data_oob[y])
        for c in tqdm(self.f2m_col):
            self._binned_variables[c] = get_opt_binning(
                col_x = data_oob_pred[c],
                col_y = data_oob[col_y],
                min_one_cnt = self.min_one_cnt,
                name=c,
                max_n_prebins=max(len(self.dic[c]) - 1,2),
                monotonic_trend = 'ascending',
                verbose=self.verbose,
            )

        self._binning_selection_criteria()

        for i in range(len(self.f2m_col)):
            if not self._support[i] or self.cut_auc_dic[self.f2m_col[i]].max()<=0.5 or len (self._binned_variables[self.f2m_col[i]].splits) <= 0:
                self.remove_var_list.append(self.f2m_col[i])

        self.col_new = np.setdiff1d(self.col_x , self.remove_var_list).tolist()
        self.f2m_col_processed = np.setdiff1d(self.f2m_col , self.remove_var_list).tolist()
        self._time_processed = time.perf_counter() - time_start
        print("_time_processed = ", self._time_processed)

    def _binning_selection_criteria(self):
        for i, name in enumerate(self.f2m_col):
            optb = self._binned_variables[name]
            optb.binning_table.build(4)

            n_bins = len(optb.splits)
            if optb.dtype == "numerical":
                n_bins += 1

            info = {"dtype": optb.dtype,
                    "status": optb.status,
                    "n_bins": n_bins}

            if self._target_dtype in ("binary", "multiclass"):
                optb.binning_table.analysis(print_output=False)

                if self._target_dtype == "binary":
                    metrics = {
                        "iv": optb.binning_table.iv,
                        "gini": optb.binning_table.gini,
                        "js": optb.binning_table.js,
                        "quality_score": optb.binning_table.quality_score}
                else:
                    metrics = {
                        "js": optb.binning_table.js,
                        "quality_score": optb.binning_table.quality_score}
            elif self._target_dtype == "continuous":
                metrics = {}

            info = {**info, **metrics}
            self._variable_stats[name] = info

        self._support_selection_criteria()

    def _support_selection_criteria(self):
        self._support = np.full(self._n_variables, True, dtype=np.bool)

        if self.selection_criteria is None:
            return

        default_metrics_info = _METRICS[self._target_dtype]
        criteria_metrics = self.selection_criteria.keys()

        binning_metrics = pd.DataFrame.from_dict(self._variable_stats).T

        for metric in default_metrics_info["metrics"]:
            if metric in criteria_metrics:
                metric_info = self.selection_criteria[metric]
                metric_values = binning_metrics[metric].values

                if "min" in metric_info:
                    self._support &= metric_values >= metric_info["min"]
                if "max" in metric_info:
                    self._support &= metric_values <= metric_info["max"]
                if all(m in metric_info for m in ("strategy", "top")):
                    indices_valid = np.where(self._support)[0]
                    metric_values = metric_values[indices_valid]
                    n_valid = len(metric_values)

                    # Auxiliary support
                    support = np.full(self._n_variables, False, dtype=np.bool)

                    top = metric_info["top"]
                    if not isinstance(top, numbers.Integral):
                        top = int(np.ceil(n_valid * top))
                    n_selected = min(n_valid, top)

                    if metric_info["strategy"] == "highest":
                        mask = np.argsort(-metric_values)[:n_selected]
                    elif metric_info["strategy"] == "lowest":
                        mask = np.argsort(metric_values)[:n_selected]

                    support[indices_valid[mask]] = True
                    self._support &= support

    def _cut_search(self,col,X,y):
        clf_ls=[]
        clf_ = xgb.XGBClassifier(
            n_estimators=1,
            random_state=0,
            eval_metric = 'auc',
            n_jobs=self.n_jobs,
            missing=self.miss_val,
            monotone_constraints=tuple([self.mc_dict_checked.get(col,0)])
        )
        # print("qiguai",X,y.sum())
        for p in self.param_space:
            estimator = clone(clf_)
            estimator.set_params(**p)
            estimator.fit(X,y)
            clf_ls.append(estimator)
        return {col:clf_ls}

    def _make_opt_param_space(self):
        """
        make opt space.
        """
        param_space = []
        self.random_state = check_random_state(self.random_state)
        for i in range(self.cut_iter):
            dic = {}
            for k,v in self.cut_space.items():
                dic[k] = self.random_state.choice(v,1)[0]
            param_space.append(dic)

        return param_space

    def transform(self, data, metric="event_rate",  show_digits=4):
        '''transform函数

        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集

        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        data =data.copy(deep=True)
        indices_selected_variables = list(set(self.f2m_col_processed) & set(data.columns))
        if len(indices_selected_variables) > 0:
            for name in indices_selected_variables:
                pred = np.zeros(data[name].shape[0])
                pred = self.cut_best_clf_dic[name].predict_proba(data[[name]])[:,1]
                optb = self._binned_variables[name]
                splits =  optb._splits_optimal
                indices = np.digitize(pred, splits, right=False)
                bins = np.concatenate([[-np.inf], splits, [np.inf]])
                bins_str = bin_str_format(bins, show_digits)
                n_bins = len(splits) + 1

                if metric in ("woe", "event_rate"):
                    # Compute event rate and WoE
                    n_records = optb._n_event + optb._n_nonevent
                    t_n_nonevent = optb._n_nonevent.sum()
                    t_n_event = optb._n_event.sum()

                    n_event = optb._n_event[:n_bins]
                    n_nonevent = optb._n_nonevent[:n_bins]
                    n_records = n_records[:n_bins]

                    # default woe and event rate is 0
                    # mask = (self.n_event > 0) & (self.n_nonevent > 0)
                    event_rate = np.zeros(len(n_records))
                    woe = np.zeros(len(n_records))
                    event_rate = n_event / n_records
                    constant = np.log(t_n_event / (t_n_nonevent + 1e-4))
                    woe = np.log(1 / event_rate - 1) + constant

                    if metric == "woe":
                        metric_value = woe
                    else:
                        metric_value = event_rate

                    for i in range(n_bins):
                        mask = (indices == i)
                        pred[mask] = metric_value[i]
                data[name] = pred
        return data


class ShuffleImpTransformer(BaseEstimator, TransformerMixin):
    """ShuffleImportance特征选择工具

    Parameters
    ----------
    col_x : list
        特征列表
    estimator : sklearn.Estimator
        分类器对象,必须具备feature_importances_属性
    space : dict
        分类器参数空间
    max_iter : int, default = 50
        最大迭代次数
    random_state : int, default=0
        随机数种子
    perc : int, default=25
        Null特征重要性阈值，越大要求越严格，范围【0,100】
    verbose : bool , default True
        日志等级
    n_jobs : int , default = 1
        并行计算数量
    threshold : float, default=-0.3
        特征重要性间的gap阈值，越大要求越严格
    data_parts:str
        样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list
        样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足
        data_parts=1 和 2时的样本
    imp_real_shrehold : float, default = None
        真实特征重要性阈值范围[0,1),如果设置，真实重要性小于该值的特征将被删除
    clf_keep : bool , default=False
        保存分类器

    Attributes
    ----------
    imp_df : pd.DataFrame()
        特征重要性表格，imp_gap代表真实特征重要性和Null的差距，imp_real代表真实特征重要性，imp_sha代表Null重要性
    clf_real_ls : sklearn.Estimator
        真Y分类器集合
    clf_sha_ls : sklearn.Estimator
        假Y分类器集合
    remove_var_list : list
        删除特征列表
    col_new : list
        保留特征列表

    Notes
    -----
    Data transform type : DELETE

    """

    def __init__(
        self, col_x,estimator,
        space = {
            "n_estimators":[50],
            "max_depth": [3,4,5,6,7],
            "min_child_samples": [20,40,60,80,100,150],
            "learning_rate":[0.1,0.05],
            'subsample': [0.6,0.7,0.8,0.9,1],
            'random_state':[i * 13 for i in range(1000)],
            'n_jobs':[-1]
        },
        max_iter=50, random_state=0, perc=25, threshold=-0.3, verbose=True,
        n_jobs=1, data_parts='data_parts', data_parts_use=None, feature_map=None, imp_real_shrehold=None,
        clf_keep=False
    ):
        self.estimator = estimator
        self.max_iter = max_iter
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.perc = perc
        self.data_parts=data_parts
        self.data_parts_use=data_parts_use
        self.feature_map=feature_map
        self.col_x=col_x
        self.col_new=col_x
        self.threshold=threshold
        self.space=space
        self.verbose=verbose
        self.imp_real_shrehold=imp_real_shrehold
        self.clf_keep=clf_keep

        self._is_lightgbm = 'lightgbm' in str(type(self.estimator))
        self._is_fitted = False

    def _check_params(self, X, y):
        """
        Check hyperparameters as well as X and y before proceeding with fit.
        """
        # check X and y are consistent len, X is Array and y is column
        X, y = check_X_y(X, y,force_all_finite=False)

    def _make_estimator(self):
        """
        Make and configure a copy of the `estimator` attribute.
        """
        estimators_ = []
        for i in range(self.max_iter):
            estimator = clone(self.estimator)
            estimator.set_params(**self.param_space[i])
            estimators_.append(estimator)

        return estimators_

    def _make_opt_param_space(self):
        """
        make opt space.
        """
        param_space = []
        self.random_state = check_random_state(self.random_state)
        for i in range(self.max_iter):
            dic = {}
            for k,v in self.space.items():
                dic[k] = self.random_state.choice(v,1)[0]
            param_space.append(dic)

        return param_space

    def fit(self, data, y, **kwargs):
        """
        Fits the feature selection with the provided estimator.
        Parameters
        ----------
        data : array-like, shape = [n_samples, n_features]
            The training input samples.
        y: pd.Series
            目标边梁
        """

        check_y_is_series(y)

        self.col_new=self.col_x
        if self.data_parts_use:
            data=data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
        return self._fit(data[self.col_x], data[y.name],**kwargs)

    def transform(self, data):
        """
        .
        Parameters
        ----------
        data : array-like, shape = [n_samples, n_features]
            The training input samples.
        """

        return data

    def _fit(self, X, y, **kwargs):
        # check input params
        self._check_params(X, y)

        print ("_get_y_sha")
        time_start = time.perf_counter()
        y_sha = self._get_y_sha(X,y)
        # self.y_sha = y_sha
        _time_get_y_sha = time.perf_counter() - time_start
        print ("_time_get_y_sha cost ",round(_time_get_y_sha,4))

        time_start = time.perf_counter()
        self.param_space = self._make_opt_param_space()
        _time_make_opt_param_space = time.perf_counter() - time_start
        print ("_time_make_opt_param_space cost ",round(_time_make_opt_param_space,4))

        # self.clf_ls = [self._make_estimator() for c in range(self.max_iter)]
        print ("_make_estimator")
        time_start = time.perf_counter()
        self.clf_real_ls = self._make_estimator()
        self.clf_sha_ls = self._make_estimator()
        _time_make_estimator = time.perf_counter() - time_start
        print ("_time_make_estimator cost ",round(_time_make_estimator,4))

        print("_get_imp_real started")
        time_start = time.perf_counter()
        self.imp_real = np.zeros([X.shape[1], self.max_iter])
        real_out = Parallel(n_jobs=self.n_jobs,backend='threading')(delayed(self._get_imp) \
                            (X, y, self.clf_real_ls[e], e,self.verbose ,**kwargs) for e in range(self.max_iter))
        for o in real_out:
            self.imp_real[:, o[0]] = o[1]
            self.clf_real_ls[o[0]] = o[2]
        self.imp_real = self.imp_real.mean(axis=1).round(6)
        _time_get_imp_real = time.perf_counter() - time_start
        print("_get_imp_real end cost",round(_time_get_imp_real,4))

        print("_get_imp_sha started")
        time_start = time.perf_counter()
        self.imp_sha = np.zeros([X.shape[1], self.max_iter])
        sha_out = Parallel(n_jobs=self.n_jobs,backend='threading')(delayed(self._get_imp) \
                            (X, y_sha[:, e], self.clf_sha_ls[e], e,self.verbose, **kwargs) for e in range(self.max_iter))
        for o in sha_out:
            self.imp_sha[:, o[0]] = o[1]
            self.clf_sha_ls[o[0]] = o[2]
        self.imp_sha = self.imp_sha.round(6)
        _time_get_imp_sha = time.perf_counter() - time_start
        print("_get_imp_sha end cost", round(_time_get_imp_sha,4))

        self.imp_gap = np.log(1e-10 + self.imp_real / (1e-10 + np.percentile(self.imp_sha, self.perc, axis=1)))
        self.imp_df = pd.DataFrame(zip(self.col_x,self.imp_gap,self.imp_real,self.imp_sha),\
                                   columns = ["variable", 'imp_gap', 'imp_real', 'imp_sha'])
        self.imp_df = self.imp_df.sort_values('imp_gap', ascending=False).reset_index(drop=True)
        self.remove_var_list = self.imp_df.loc[self.imp_df['imp_gap'] < self.threshold, "variable"].tolist()
        if self.imp_real_shrehold:
            self.remove_var_list.extend(\
                self.imp_df.loc[self.imp_df['imp_real'] <= self.imp_real_shrehold, "variable"].tolist())
            self.remove_var_list = sorted(list(set(self.remove_var_list)))
        self.col_new = np.setdiff1d(self.col_x, self.remove_var_list).tolist()
        print(self.__class__.__name__, "remove_var_list=", self.remove_var_list)

        if not self.clf_keep:
            self.clf_sha_ls = None
            self.clf_real_ls = None

        self._is_fitted = True

        return self

    def _get_shuffle(self, seq):
        self.random_state.shuffle(seq)
        return seq

    def _get_imp(self,X, y,clf, e, verbose,**kwargs):
        if verbose:
            print("_get_imp turn",e)
        clf.fit(X, y,eval_set=[(X, y)], verbose=verbose, **kwargs)
        return e, clf.feature_importances_ / np.sum(clf.feature_importances_), clf

    def _get_y_sha(self, X, y):
        y_sha = np.zeros([X.shape[0], self.max_iter])
        self.random_state = check_random_state(self.random_state)
        for i in range(self.max_iter):
            y_sha[:, i] = self._get_shuffle(np.copy(y))
            # print (np.where(y_sha[:,i] == 1))
            if self.verbose:
                print (np.sum(np.abs(y-y_sha[:, i])))
        return y_sha


class XimputeTransformer(BaseEstimator, TransformerMixin):
    """防伪特征工程工具XimputeTransformer

    Parameters
    ----------
    col_x: list
       字段列表.
    impute_dict : dict
        字典的形式出现：
            mode:必须出现，目前支持三种模式："replace"，全部用Ximputer值替代原始值；"add" 新增Ximputer值，原始值保留；自定义函数，函数需有两个参数，第一个为原始值，第二个参数为Ximpuer
            target_type:必须出现，模型类型reg（回归） or clf（分类）
            fit_exclude_value:选择出现，不需要fit的目标
            data_contidion:选择出现，不参与训练的样本，格式同pandas.query
            suffix:选择出现，model为add时出现，新增特征列的后缀名
        配置方式 : {
                       "ali_rain_score": {
                                            "mode": "replace",
                                            "target_type":"reg",
                                            "fit_exclude_value":[-99,np.nan],
                                            "data_contidion":"fpd4 == 0",
                                            "x_use_count":30,
                        },
                       "selffill_degree": {
                                            "mode": "add",
                                            "suffix":"_ximp",
                                            "target_type":DecisionTreeClassifier(random_state = 0),
                                            "fit_exclude_value":[-99,np.nan],
                                            "data_contidion":"fpd4 == 0",
                                            "x_use_count":30,
                       },
                       "selffill_marital_status": {
                                            "mode": lambda x,x_impute:x_impute if x in [-99,np.nan] else min(x,x_impute),
                                            "target_type":"clf",
                                            "fit_exclude_value":[-99,np.nan],
                                            "data_contidion":"fpd4 == 0",
                                            "x_use_count":30,
                       },
        }
    data_parts:str
        样本分割标志字段，默认data_parts,必须在数据集中出现
    data_parts_use:list
        样本分割标志字段中需要分析的样本集合，例如[1,2]代表数据集中满足
        data_parts=1 和 2时的样本
    feature_map:None or pd.Dataframe()
        特征图 ，默认None
    data_limit_at_least: int
        样本最小数量要求
    idr_rate_limit:float
        一值率上限，要求低于该值
    random_state:None
        默认None
    dic:dict or None
        特征分割切点集合，默认None，如果配置特征切点，则沿用此切点，不再新找切点

    Attributes
    ----------
    col_new :list
        输出返回特征列表
    output_impute_dict :dict
        输出impute字典

    Notes
    -----
    Data transform type : INSERT/UPDATE

    """

    def __init__(
        self,
        col_x,
        impute_dict,
        data_parts='data_parts',
        data_parts_use=None,
        feature_map=None,
        data_limit_at_least=300,
        idr_rate_limit=0.98,
        random_state=0,
    ):
        self.impute_dict = impute_dict
        self.col_x = col_x
        self.data_parts = data_parts
        self.data_parts_use = data_parts_use
        self.feature_map = feature_map
        self.data_limit_at_least = data_limit_at_least
        self.idr_rate_limit = idr_rate_limit
        self.random_state = random_state

        self.remove_var_list = []

    def fit(self, data, y=None):
        '''fit函数

        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        y: pd.Series
            目标变量

        Returns
        -------
        self:对象本身类型
        '''
        if self.data_parts_use:
            data = data.loc[data[self.data_parts].isin(self.data_parts_use), :].reset_index(drop=True).copy(deep=True)
        else:
            data=data.copy(deep=True)

        self.col_new = self.col_x[:]
        self.output_impute_dict ={}

        for x,param in self.impute_dict.items():
            print ("col=",x)
            use_col = np.setdiff1d(self.col_x ,list(self.impute_dict.keys()))
            if "exclude_col" in param.keys():
                use_col = np.setdiff1d(use_col,param["exclude_col"])

            if "data_contidion" in param.keys():
                X = data.query(param["data_contidion"])[use_col]
                Y = data.query(param["data_contidion"])[x]
            else:
                X = data[use_col]
                Y = data[x]

            print("after data_contidion",X.shape,Y.shape)

            if "fit_exclude_value" in param.keys():
                print(param["fit_exclude_value"],Y)
                Y = Y[~Y.isin(param["fit_exclude_value"])]
                # X = X.loc[~Y.isin(param["fit_exclude_value"])]
                # print(Y.index)
                X = X.loc[Y.index]
            print(X.shape,Y.shape)
            if X.shape[0] < self.data_limit_at_least:
                print (x,"exceeded idr_rate_limit!")
                break

            idr_rate = Y.value_counts().max() / Y.shape[0]
            # print(Y.value_counts().sort_values() , Y.shape[0])
            if idr_rate>=self.idr_rate_limit:
                print ("{} touch idr_rate_limit!, {} > {} ".format(x,idr_rate,self.idr_rate_limit))
                break

            if param["mode"] == 'add':
                if "suffix" not in param.keys():
                    self.col_new.append(x+"_ximp")
                    # raise Exception("suffix not in param!")
                else:
                    self.col_new.append(x+param["suffix"])

            if hasattr(param["target_type"],"fit"):
                estimator = param["target_type"]
            elif param["target_type"] == 'clf':
                estimator = lgb.LGBMClassifier(
                    **{"num_boost_round":30,
                    "random_state":self.random_state,}
                )
            else:
                estimator = lgb.LGBMRegressor(
                    **{"num_boost_round":30,
                    "random_state":self.random_state,}
                )
            estimator.fit(X,Y)
            if "x_use_count" in param.keys() and len(use_col) > param.get("x_use_count",999999):
                if not hasattr(estimator,"feature_importances_"):
                    raise ValueError("estimator must has feature_importances_ attribute!")
                temp_fi = pd.Series(
                    estimator.feature_importances_,
                    index=use_col
                )
                temp_use_col = temp_fi[temp_fi>0].sort_values(ascending=False).index.tolist()[:param["x_use_count"]]
                estimator.fit(X[temp_use_col],Y)
                fi = pd.DataFrame(
                    list(zip(temp_use_col,estimator.feature_importances_)),
                    columns=['use_col', 'fi']
                )
                self.output_impute_dict[x] = {"use_col":temp_use_col,"est":estimator,"fi":fi}
            else:
                fi = pd.DataFrame(
                    list(zip(use_col,estimator.feature_importances_)),
                    columns=['use_col', 'fi']
                )
                self.output_impute_dict[x] = {"use_col":use_col,"est":estimator,"fi":fi}

        if self.feature_map is not None:
            for k, v in self.output_impute_dict.items():
                fi_df = pd.DataFrame(
                    list(zip(v['use_col'],v['est'].feature_importances_)),
                    columns=['relyon', 'fi']
                )

                if self.impute_dict[k]['mode'] =='add':
                    fi_df['variable'] = k+self.impute_dict[k]["suffix"]
                else:
                    fi_df['variable'] = k
                fi_df = fi_df.loc[fi_df['fi']>0].reset_index(drop=True)
                self.feature_map = self.feature_map.append(fi_df[['relyon','variable']], ignore_index=True)
        return self

    def transform(self, data):
        '''transform函数

        Parameters
        ----------
        data: pd.DataFrame
            需要转换的数据集

        Returns
        -------
        data:pd.DataFrame
            转换后的数据集
        '''
        logging.info ("--Ximputer transform start!--")
        data = data.copy(deep=True)
        col_x=list(set(data.columns.tolist()) & set(self.col_new))
        col_impute_target = list(self.output_impute_dict.keys())
        logging.info(f"Ximputer col_impute_target = {col_impute_target}")

        #依据提供的字段判断是否需要推理impute特征
        transform_ls = []
        for target in col_impute_target:
            fi_df=self.output_impute_dict[target]['fi']
            logging.debug(f"{target},{fi_df},{np.setdiff1d(fi_df.loc[fi_df['fi']>0,'use_col'].tolist(),col_x)}")
            if len(np.setdiff1d(fi_df.loc[fi_df['fi']>0,"use_col"].tolist(),col_x)) ==0:
                transform_ls.append(target)

        logging.info(f"Ximputer transform_ls = {transform_ls}")
        if transform_ls:
            for c in transform_ls:
                for uc in self.output_impute_dict[c]["use_col"]:
                    if uc not in data.columns:
                        logging.debug("{} does not exist ,create dummy col".format(uc))
                        data[uc]=-99

                if callable(self.impute_dict[c]['mode']):
                    data["_pred"] =self.output_impute_dict[c]["est"].predict(data[self.output_impute_dict[c]["use_col"]])
                    logging.debug(f"func = {data[[c,'_pred']]}")
                    data[c] = data[[c,"_pred"]].apply(lambda x:self.impute_dict[c]['mode'](x[c],x["_pred"]),axis=1)
                    del data["_pred"]
                elif self.impute_dict[c]['mode'] == "replace":
                    data[c] =self.output_impute_dict[c]["est"].predict( data[self.output_impute_dict[c]["use_col"]])
                elif self.impute_dict[c]['mode'] == "add":
                    # print("!!!!",c + self.impute_dict[c]["suffix"])
                    data[c + self.impute_dict[c]["suffix"]] = self.output_impute_dict[c]["est"].predict(data[self.output_impute_dict[c]["use_col"]])
                else:
                    pass
        return data
