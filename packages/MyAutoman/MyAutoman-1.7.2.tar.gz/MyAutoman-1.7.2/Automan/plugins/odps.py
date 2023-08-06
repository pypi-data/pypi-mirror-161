import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

import matplotlib.font_manager
# from pyod.models.abod import ABOD # 基于概率
# from pyod.models. knn import KNN # 基于近邻
# from pyod.models.mcd import MCD #基于线性模型
# from pyod.models.ocsvm import OCSVM
import pandas as pd
from Automan.plugins.DDViz import out_null,auto_bin,manual_bin,out_iv,plt_multi_mosaic,plt_mosaic
from tqdm import tqdm
import joblib
import datetime
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from multiprocessing.pool import ThreadPool

class ODPS():
    def __init__(self, 
                col_x, 
                data_parts='data_parts',
                data_parts_use=None,
                algo_dict = {}, 
                num_of_round =50 , 
                num_of_compile=5, 
                play_report=True, 
                verbose=True, 
                ks_limit=0.02, 
                is_filter=True ,
                fill_dict={-99:-1}, 
                scale_type=1, 
                n_jobs = 2, 
                contamination=.2):
        '''
        Parameters
        ----------
        col_x: list
            特征列表.
        data_parts: str
            数据集切分字段.
        data_parts_use: list or None
            样本分析列表，eg:[1,2],只会分析data_parts为1和2的样本，如果为None分析整个数据集
        algo_dict : dict 
            算法列表
        num_of_round : int
            变量生成轮次 : default 50
        num_of_compile : int 
            组合变量个数 : default 5
        play_report : bool
            是否生成报告 : default True
        verbose : bool
        ks_limit : float 
            复合变量的ks下限 : default 0.02
        is_filter : bool 
            是否做变量筛选 : default True
        fill_dict : dict
            变量值映射列表 : default {-99 : -1}
        scale_type : int 
            归一化方法 : default 1
        n_jobs : int 
            进程数 : default 1
        contamination : float
            污染比例 : 0.2
        '''
        self.col_x = col_x
        self.data_parts = data_parts
        self.data_parts_use = data_parts_use
        self.dict_map=dict()
        self.algo_dict = algo_dict
        self.var_list = col_x
        self.num_of_round = num_of_round
        self.num_of_compile = num_of_compile
        self.play_report = play_report
        self.verbose = verbose
        self.ks_limit = ks_limit 
        self.is_filter = is_filter
        self.fill_dict = fill_dict
        self.scale_type = scale_type
        self.n_jobs = n_jobs
        self.contamination = contamination

    def _preprocess(self, data, training=True):
        '''变量预处理方法
        Args:
            data : pandas.DataFrame : 待处理数据集
            training : bool : 是否为测试机
        Return:
            data : pandas.DataFrame
        '''
        mem_cols = data.columns
        data = data.fillna(-99)
        data = data.replace(self.fill_dict)
        # 归一化过程训练
        if training:
            if self.scale_type == 1:
                self.st = StandardScaler()
            elif self.scale_type ==2:
                self.st = MinMaxScaler()
            if self.scale_type !=1 and self.scale_type!=2  and self.scale_type!=0:
                raise ValueError('scale_type must be 1--StandardScaler, 2--MinMaxScaler')
            if self.scale_type==1 or self.scale_type==2 :
                self.st.fit_transform(data)
        # 归一化过程演绎
        data = self.st.transform(data)
        data = pd.DataFrame(data)
        data.columns = list(mem_cols)
        return data

    def fit(self,data,y=None):
        '''fit函数
        
        Parameters
        ----------
        data: pd.DataFrame
            数据集-数据集中需要包含col_x所有字段，如果y不为None，数据集中需要包含y字段
        
        Returns
        -------
        self:对象本身对象本身
        '''
        if y is  None:
            raise TypeError('missing argument: ''y''')
        if self.data_parts_use is None and self.data_parts is not None:
            self.data_parts_use = list(data.data_parts.unique())
        if self.data_parts_use:
            self.train_X = data.loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
            self.val_X = data.loc[~data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True)
            self.train_Y = pd.DataFrame(y).loc[data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True).iloc[:,0]
            self.val_Y = pd.DataFrame(y).loc[~data[self.data_parts].isin(self.data_parts_use),:].reset_index(drop=True).copy(deep=True).iloc[:,0]
        else:
            self.train_X = data.copy(deep=True)
            self.val_X = data.copy(deep=True)
            self.train_Y = y.copy()
            self.val_Y = y.copy()
        if  len(self.val_X) == 0:
            self.val_X = data.copy(deep=True)
            self.val_Y = y.copy(deep=True)
        #self.train_Y = self.train_X.pop(y)
        #self.val_Y = self.val_X.pop(y)
        self.choose_var_dict = {}
        self.final_var_dict = {}
        self.algo_names = list(self.algo_dict.keys())
        # 训练集变量衍生数据集
        self.output_train_set = self.train_X[self.var_list].copy()
        # 验证集变量衍生数据集
        self.output_val_set = self.val_X[self.var_list].copy()
        # var to id 映射
        self.var2id = {var : idx for idx, var in enumerate(self.var_list)}
        # id to var 映射
        self.id2var = {idx : var for idx, var in enumerate(self.var_list)}
        # 变量衍生列表
        self.choose_var_list = []
        # 最终变量列表
        self.final_var_list = [] 
        self.algo_lists = []
        self.outdict = {}
        # 中间特征重要性存贮字典
        self.imp_var_dict = {}
        # 中间算法重要性存贮字典
        self.imp_algo_dict = {}
        self.ks_iv_outs = None
        # 归一化实例
        self.st = None
        # 数据集缺失值填空及归一化预处理
        if self.scale_type in [0, 1, 2]:
            self.train_X_normed = self._preprocess(self.train_X[self.var_list], True)
            self.val_X_normed = self._preprocess(self.val_X[self.var_list], False)
        else:
            self.train_X_normed = self.train_X
            self.val_X_normed = self.val_X
        # 训练集变量衍生数据集
        self.output_train_set = self.train_X.copy()
        # 验证集变量衍生数据集
        self.output_val_set = self.val_X.copy()
        def _fun_var_choice(i):
        ##for i in tqdm(range(self.num_of_round)):
            # 计算特征重要性
            var_imp_dict_rnd = self._cal_feature_importance()
            # 计算算法重要性
            algo_imp_dict_rnd = self._cal_algo_importance()
            # 特征重要性归一化
            p_algo = [algo_imp_dict_rnd[t] for t in self.algo_names]
            p_algo = p_algo / np.sum(p_algo)
            # 算法重要性归一化
            p_var = [var_imp_dict_rnd[t] for t in self.var_list]
            p_var = p_var / np.sum(p_var)
            # 按照算法重要性分布选取变量
            t_algo = np.random.choice(self.algo_names, 1, p=p_algo,replace=False)[0]
            t_clf = self.algo_dict[t_algo](contamination=self.contamination)
            # 按照特征重要性分布选取变量
            t_vars = np.random.choice(self.var_list, self.num_of_compile, p=p_var,replace=False)
            # 按变量入模顺序排序
            t_ids = sorted([self.var2id[i] for i in t_vars])
            # 合并变量id作为变量名
            t_var_name = 'odps_' + t_algo +''.join([str(i) + '_' for i in t_ids])[:-1]
            # 打印变量名
            if self.verbose:
                print(t_var_name)
            # 防止生成重复变量
            if t_var_name not in self.choose_var_list:
                # 初始化变量字典
                self.choose_var_dict[t_var_name] = []
                # 添加到变量选择列表
                self.choose_var_list.append(t_var_name)
                # 参数训练
                t_clf.fit(self.train_X_normed[t_vars])
                # 将异常算法实例添加到算法列表
                self.algo_lists.append(t_clf)
                # 变量字典t_var_name : [t_clf]
                self.choose_var_dict[t_var_name].append(t_clf)
                # 变量字典t_var_name : [t_clf, [va1, va2...]]
                self.choose_var_dict[t_var_name].append(t_vars)
                # Train
                # 训练集预测
                y_pred = t_clf.predict_proba(self.train_X_normed[t_vars])[:,0]
                # 保持已经存在的变量名
                orig = self.output_train_set.columns
                self.output_train_set[t_var_name] = y_pred
                # 生成输入iv计算器的临时数据集
                tmp_df = self.output_train_set.copy()
                tmp_df = pd.concat([tmp_df, self.train_Y], axis=1)
                tmp_df.columns = list(orig) + [t_var_name] + ['fpd4'] 
                tmp_df['dt'] = 1
                # Validation
                # 验证集预测
                y_pred = t_clf.predict_proba(self.val_X_normed[t_vars])[:,0]
                # 保持已经存在的变量名
                self.output_val_set[t_var_name] = y_pred
                # 计算本轮生成变量的KS
                tmp_ks = self._cal_ks(tmp_df, t_var_name)
                # 遍历所选用的变量
                for t_var in t_vars:
                    # 更新变量特征重要性字典
                    if t_var not in self.imp_var_dict:
                        self.imp_var_dict[t_var] = []
                    self.imp_var_dict[t_var].append(tmp_ks)
                    # 更新算法重要性字典
                if t_algo not in self.imp_algo_dict:
                    self.imp_algo_dict[t_algo] = []
                self.imp_algo_dict[t_algo].append(tmp_ks)

        with ThreadPool(processes=self.n_jobs) as pool:
            pool.map(_fun_var_choice, range(self.num_of_round))
        if self.verbose:    
            print('总共有%d个衍生变量'%len(self.algo_lists))
        # 报告生成
        if self.play_report is True:
            self._play_report()
        # 过滤KS较低变量
        if self.is_filter:
            self._filter_var()
        else:
            self.final_var_dict = self.choose_var_dict
            self.final_var_list = self.choose_var_list
        ids = []
        for k, v in self.final_var_dict.items():
            ids.extend(v[1])
        ids = list(set(ids))
        self.final_var_list_inputs = ids 
        self.col_new = list(data.columns) + list(self.final_var_dict.keys())
        # 删除无用的属性，释放空间
        del self.train_X
        del self.val_X
        del self.train_Y 
        del self.val_Y
        del self.train_X_normed 
        del self.val_X_normed
        del self.output_train_set
        del self.output_val_set

    def _cal_algo_importance(self):
        '''_cal_algo_importance函数
        
        Parameters
        ----------
        
        Returns
        -------
        algo_imp_dict_rnd : dict 
            算法重要性字典
        '''
        # 算法重要性字典容器
        algo_imp_dict_rnd = {}
        # 遍历算法列表
        for algo_name in self.algo_names:
            if algo_name not in self.imp_algo_dict:
                algo_imp_dict_rnd[algo_name] = 0.05
            elif self.imp_algo_dict[algo_name] == []:
                algo_imp_dict_rnd[algo_name] = 0.05
            else:
                algo_imp_dict_rnd[algo_name] = np.mean(self.imp_algo_dict[algo_name])
        return algo_imp_dict_rnd

    def _cal_feature_importance(self):
        '''_cal_feature_importance函数
        
        Parameters
        ----------
        
        Returns
        -------
        var_imp_dict_rnd : dict 
            变量重要性字典
        '''
        var_imp_dict_rnd = {}
        for var_name in self.var_list:
            if var_name not in self.imp_var_dict:
                var_imp_dict_rnd[var_name] = 0.05
            elif self.imp_var_dict[var_name] == []:
                var_imp_dict_rnd[var_name] = 0.05
            else:
                var_imp_dict_rnd[var_name] = np.mean(self.imp_var_dict[var_name])
        return var_imp_dict_rnd

    def _cal_ks(self, df, var_name):
        '''_cal_ks函数
        
        Parameters
        ----------
        df : pandas.DataFrame
            数据集
        var_name : string
            变量名
        Returns
        -------
        : float
            变量KS效果
        '''
        df["dt_cut"] = 'all'
        iv_ks = out_iv(df, [var_name], y='fpd4', dt='dt',dt_cut = 'dt_cut',isformat = False)
        print ("iv_ks = ", iv_ks['df_iv'])
        del df["dt_cut"]
        # return iv_ks['df_iv'][var_name]
        return iv_ks['df_iv'].loc[var_name]

    def _play_report(self):
        '''_play_report
        
        Parameters
        ----------

        Returns
        -------
        : dict
            报告
        '''
        # 结果容器
        outs = {}
        # 训练集
        df_train = pd.concat([self.output_train_set[self.choose_var_list], self.train_Y], axis=1)
        df_train.columns = self.choose_var_list + ['fpd4']
        df_train['dt']= '1'
        train_iv_ks = out_iv(df_train, self.choose_var_list, y='fpd4', dt='dt',isformat=False,dt_cut = 'dt')
        outs['train_iv'] = train_iv_ks['df_iv'].loc[self.choose_var_list]
        outs['train_ks'] = train_iv_ks['df_ks'].loc[self.choose_var_list]
        # 验证集
        df_val = pd.concat([self.output_val_set[self.choose_var_list], self.val_Y], axis=1)
        df_val.columns = self.choose_var_list + ['fpd4']
        df_val['dt']= '1'
        val_iv_ks = out_iv(df_val, self.choose_var_list, y='fpd4', dt='dt',isformat=False,dt_cut = 'dt')
        outs['val_iv'] = val_iv_ks['df_iv'].loc[self.choose_var_list]
        outs['val_ks'] = val_iv_ks['df_ks'].loc[self.choose_var_list]
        self.ks_iv_outs = outs
        return outs
    
    def _filter_var(self):
        '''_filter_var
        
        Parameters
        ----------

        Returns
        -------
        '''
        if self.ks_iv_outs is None:
            self._play_report()
        outs = self.ks_iv_outs
        # print ("!!!outs['train_ks']=!!!",outs['train_ks'])
        out_train_ks = outs['train_ks'].to_dict()[1]
        # print ("out_train_ks",out_train_ks)
        for var_name, ks in out_train_ks.items():
            if out_train_ks[var_name] >= self.ks_limit:
                self.final_var_dict[var_name] = self.choose_var_dict[var_name]
                self.final_var_list.append(var_name)


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
        test_X = data[self.var_list]
        # 数据预处理
        if self.scale_type==1 or self.scale_type==2 :  
            test_X = self._preprocess(test_X, False)
        output_df = data.copy()
        # 遍历最终变量字典
        for var_name in self.final_var_dict:
            # 单变量列表
            t_dict = self.final_var_dict[var_name]
            # 算法实例
            t_algo = t_dict[0]
            # 组合变量的单变量列表
            t_vars = t_dict[1]
            # 预测衍生
            output_df[var_name] = t_algo.predict_proba(test_X[t_vars])[:,0]
        return output_df  


            



