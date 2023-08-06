# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import random
from functools import reduce
from Automan.plugins.risk_trend_plot import risk_trend_plot
from warnings import warn
from sklearn.preprocessing import OneHotEncoder,LabelEncoder
import os
from sklearn.tree import DecisionTreeClassifier
import math
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import _tree
import pickle
from tqdm import tqdm
import time

def gbl_strategy_finder(data,label='fpd4',inputx=[],bad_lift=2
                     ,good_lift=0.4,mode='ar',
                     method='gain',n_rounds=10,
                     pass_limit=0.01,reject_limit=0.01,n_cut=40,random_state = 0):
    '''
    Parameters
    ----------
    data: pd.DataFeame
        数据集
    label: str
        数据集中目标变量名称 要求两分类{0,1}
    inputx: list
        数据集中模型分列表
    bad_lift: float
        高风险倍数要求 取值(1,+∞)
    good_lift: float 
        高风险倍数要求 取值[0,1)
    mode : str
        模式：effic,risk,ar  对应 效率，风险，通过率
    method : str
        方法： union,gain 对应 取并，增益
    n_rounds : int
        执行轮数： 
    pass_limit : float
        单模型通过率要求 (0,1]
    reject_limit : float
        单模型拒绝率要求 [0,1)
    n_cut : int
        模型分分组数 (1,+∞)
    random_state : int
        随机数种子
        
    Returns
    -------
    total_data:pd.DataFrame
        策略结果
    total_dict:dict
        策略明细
        
    '''
    
    # 准备好各分数及其卡点
    score_list = []
    for s in inputx:
        # exec('''{} = sorted(list(set(data[s].quantile([(i+1)/{} for i in range({}-1)]))))'''.format(s+'_cut',n_cut,n_cut))
        # exec('''score_list.append((s,{}))'''.format(s+'_cut'))
        temp_cut = sorted(list(set(data[s].quantile([(i+1)/n_cut for i in range(n_cut-1)]))))
        score_list.append((s,temp_cut))
    
    total_data = pd.DataFrame(columns=['rule_str','risk_cnt','risk','lift','pass_cnt','AR'])
    
    data_cp = data.copy()    
    y_mean = data_cp[label].mean()
    total_cnt = data_cp.shape[0]
    
    total_dict = {}
    
    n_rounds = [random_state + (i * 47) for i in range(n_rounds)]
    start_time = time.time()
    for e,rd in enumerate(n_rounds):
        random.seed(rd)
        random.shuffle(score_list)
#         print(score_list)
        data = data_cp.copy()
        

        data_result = {}
        pass_rule = ''
        reject_rule = ''
        pass_count = 0
        reject_count = 0

        #  通过规则
        #  遍历各分数
        for score in score_list:
            
            feature = score[0]
            cut_list = score[1]

            #  该分数各卡点筛选出的样本指标
#             print(cut_list)
#             print(score[0],data.shape[0],data[data.score_add<=0.017].shape[0],total_cnt)
    
            result_data = pd.DataFrame(cut_list,columns=[feature])
            result_data['reject_risk'] = result_data[feature].apply(lambda x:data[data[feature]>x][label].mean())
            result_data['reject_risk_lift'] = result_data[feature].apply(lambda x:data[data[feature]>x][label].mean()/y_mean)
            result_data['reject_rate'] = result_data[feature].apply(lambda x:data[data[feature]>x].shape[0]/total_cnt)
            result_data['pass_risk'] = result_data[feature].apply(lambda x:data[data[feature]<=x][label].mean())
            result_data['pass_risk_lift'] = result_data[feature].apply(lambda x:data[data[feature]<=x][label].mean()/y_mean)
            result_data['pass_rate'] = result_data[feature].apply(lambda x:data[data[feature]<=x].shape[0]/total_cnt)

            result_data['lift_pass_rate'] = result_data.pass_risk_lift/result_data.pass_rate

            # 判断是否有符合筛选好人要求的卡点
            if len(result_data[(result_data.pass_risk_lift<good_lift)&(result_data.pass_rate>pass_limit)])==0:
                data_result[feature+'-pass'] = result_data
                pass
            else:
                if mode=='effic':
                    #  在符合要求的卡点中，按效率最高、风险最低去选择
                    pass_rule_curnt = feature+'<='+str(round(result_data[(result_data.pass_risk_lift<good_lift)&(result_data.pass_rate>pass_limit)].sort_values(['lift_pass_rate','pass_risk_lift']).iloc[0][feature],3))
                    pass_rule = pass_rule+(' or '*pass_count)+pass_rule_curnt
                elif mode=='ar':
                    #  在符合要求的卡点中，按通过率最高去选择
                    pass_rule_curnt = feature+'<='+str(round(result_data[(result_data.pass_risk_lift<good_lift)&(result_data.pass_rate>pass_limit)].sort_values(['pass_rate'],ascending=False).iloc[0][feature],3))
                    pass_rule = pass_rule+(' or '*pass_count)+pass_rule_curnt
                elif mode=='risk':
                    #  在符合要求的卡点中，按风险最低、通过率最高去选择
                    pass_rule_curnt = feature+'<='+str(round(result_data[(result_data.pass_risk_lift<good_lift)&(result_data.pass_rate>pass_limit)].sort_values(['pass_risk_lift','pass_rate'],ascending=[True,False]).iloc[0][feature],3))
                    pass_rule = pass_rule+(' or '*pass_count)+pass_rule_curnt
                pass_count =1


                if method=='gain':
                    #  将分析样本中，该规则通过的样本去除
                    data = data.query('not('+pass_rule_curnt+')')

#                 print((feature+'   pass   complete').center(100,'-'))
                data_result[feature+'-pass'] = result_data
            
            

        if method=='gain':
            if len(pass_rule)>0:
                data = data_cp.query(pass_rule).copy()
            else:
                data = data_cp.copy()

        #  拒绝规则  
        #  遍历各分数
        for score in score_list:
                
                feature = score[0]
                cut_list = score[1]
                result_data = pd.DataFrame(cut_list,columns=[feature])
                result_data['reject_risk_lift'] = result_data[feature].apply(lambda x:data[data[feature]>x][label].mean()/y_mean)
                result_data['reject_rate'] = result_data[feature].apply(lambda x:data[data[feature]>x].shape[0]/total_cnt)
                result_data['pass_risk_lift'] = result_data[feature].apply(lambda x:data[data[feature]<=x][label].mean()/y_mean)
                result_data['pass_rate'] = result_data[feature].apply(lambda x:data[data[feature]<=x].shape[0]/total_cnt)

                result_data['lift_reject_rate'] = result_data.reject_risk_lift/result_data.pass_rate

                if len(result_data[(result_data.reject_risk_lift>bad_lift)&(result_data.reject_rate>reject_limit)])==0:
                    pass
                else:
                    if mode=='effic':
                        #  在符合要求的卡点中，按效率最高、风险最高去选择
                        reject_rule_curnt = feature+'>'+str(round(result_data[(result_data.reject_risk_lift>bad_lift)&(result_data.reject_rate>reject_limit)].sort_values(['lift_reject_rate','reject_rate'],ascending=[False,False]).iloc[0][feature],3))
                        reject_rule = reject_rule+(' or '*reject_count)[:4]+reject_rule_curnt
                    elif mode=='ar':
                        #  在符合要求的卡点中，按风险最高、拒绝率最高去选择
                        reject_rule_curnt = feature+'>'+str(round(result_data[(result_data.reject_risk_lift>bad_lift)&(result_data.reject_rate>reject_limit)].sort_values(['reject_risk_lift','reject_rate'],ascending=[False,False]).iloc[0][feature],3))
                        reject_rule = reject_rule+(' or '*reject_count)[:4]+reject_rule_curnt
                    elif mode=='risk':
                        #  在符合要求的卡点中，按拒绝率最高去选择
                        reject_rule_curnt = feature+'>'+str(round(result_data[(result_data.reject_risk_lift>bad_lift)&(result_data.reject_rate>reject_limit)].sort_values(['reject_rate'],ascending=False).iloc[0][feature],3))
                        reject_rule = reject_rule+(' or '*reject_count)[:4]+reject_rule_curnt
                    reject_count =1

                    if method=='gain':
                        #  将分析样本中，该规则拒绝的样本去除
                        data = data.query('not('+reject_rule_curnt+')')

#                 print((feature+'   reject   complete').center(100,'-'))
                data_result[feature+'-reject'] = result_data

        #  给出最终的策略，以及在该样本上的效果·
        if len(reject_rule) != 0 and len(pass_rule) != 0:
            final_rule = pass_rule+' and not({})'.format(reject_rule)    
        elif len(reject_rule) != 0:
            final_rule = 'not({})'.format(reject_rule)
        elif len(pass_rule) != 0:
            final_rule = pass_rule
        else :
            final_rule = 'no rules !'
            
        if final_rule != 'no rules !':
            final_rule_risk = round(data_cp.query(final_rule)[label].mean(),3)
            final_rule_risk_cnt = data_cp.query(final_rule)[label].sum()
            final_rule_pass_cnt = data_cp.query(final_rule)[label].count()
            final_rule_lift = round(final_rule_risk/data_cp[label].mean(),3)
            final_rule_ar = round(data_cp.query(final_rule).shape[0]/data_cp.shape[0],3)
        else:
            final_rule_risk = np.nan
            final_rule_risk_cnt = np.nan
            final_rule_pass_cnt = np.nan
            final_rule_lift = np.nan
            final_rule_ar = np.nan

        data_final_rule = pd.DataFrame([final_rule,final_rule_risk_cnt,final_rule_risk,final_rule_lift,final_rule_pass_cnt,final_rule_ar,],index=['rule_str','risk_cnt','risk','lift','pass_cnt','AR']).T
        
        total_data = total_data.append(data_final_rule,ignore_index=True)
        total_dict[rd] = data_result
        end_time= time.time()
        print(('   round{}   complete').format(e + 1).center(100,'-'))
        
    print('花费时间：{}'.format(end_time-start_time))
    return total_data,total_dict


def get_cut_dic(data, use_var, n_cut, label, bad_lift, good_lift,missing_val_ls):

    dic_cut = {}
    use_rj = []
    use_tg = []
    for i in use_var:
        tmp_data, cut_off = risk_trend_plot(data[data[label].isin([0, 1]) & (~data[i].isin(missing_val_ls))], i, label, n_cut,
                                          trend_title='测试集分组趋势图' + str(i),
                                          bins='freq',if_plot=False)  #空值设定为9999
        dic_cut[i] = cut_off
        if tmp_data['risk_ratio'].iloc[-1] / data[data[label].isin([0, 1])][label].mean() >= bad_lift:
            use_rj.append(i)
        if tmp_data['risk_ratio'].iloc[0] / data[data[label].isin([0, 1])][label].mean() <= good_lift:
            use_tg.append(i)
    return dic_cut, use_tg, use_rj


def get_quer_str_tg(use_tg, n_pass_cut, dic_cut):

    rule_tg = '( '
    for i in use_tg:
        n = random.sample(n_pass_cut, 1)[0]
        rule_tg += str(i) + "<=" + str(round(dic_cut[i][n], 6)) + ' or '
    rule_tg = list(rule_tg)
    rule_tg[-4:-1] = ' )'
    rule_tg = ''.join(rule_tg)
    return rule_tg


def get_quer_str_rj(use_rj, n_rj_cut, dic_cut):

    rule_rj = '( '
    for i in use_rj:
        n = random.sample(n_rj_cut, 1)[0]
        rule_rj += str(i) + ">=" + str(round(dic_cut[i][n], 6)) + ' or '
    rule_rj = list(rule_rj)
    rule_rj[-4:-1] = ' )'
    rule_rj = ''.join(rule_rj)
    return rule_rj


# 计算该策略下的通过率和风险
def cal_fpd(data, label, key,by_month, tg_flag):
#    data[by_month] = data[by_month].apply(lambda x: int(x/100)) #转换成月份
    res_tg_fpd = pd.DataFrame(pd.pivot_table(data[(data[tg_flag] == 'Y') & (data[label].isin([0, 1]))], index=by_month, values=label, aggfunc=[sum]).iloc[:, 0])
    # 总样本数
    res_cnt = pd.DataFrame(pd.pivot_table(data, index=by_month, values=key, aggfunc=[len]).iloc[:, 0])
    # 通过样本数
    res2_tg_cnt = pd.DataFrame(
        pd.pivot_table(data[(data[tg_flag] == 'Y')], index=by_month,
                       values=tg_flag, aggfunc=[len]).iloc[:, 0])
    # 通过且有风险表现的
    res2_tg_cnt2 = pd.DataFrame(
        pd.pivot_table(data[(data[tg_flag] == 'Y') & (data[label].isin([0, 1]))],
                       index=by_month,
                       values=tg_flag,
                       aggfunc=[len]).iloc[:, 0])
    res = reduce(lambda x, y: pd.merge(x, y, on=by_month, how='inner'),
                 [res_tg_fpd, res2_tg_cnt, res2_tg_cnt2, res_cnt, ])
    res.columns = ['fpd', 'tg_cnt', 'tg_cnt2', 'cnt']

    res.loc[:, 'tg_rate'] = round(res.loc[:, 'tg_cnt'] / res.loc[:, 'cnt'], 5)
    res.loc[:, 'fpd%'] = round(res.loc[:, 'fpd'] / res.loc[:, 'tg_cnt2'], 5)
    return res

def n_cut_check(dic,n_cut):
    for k,v in dic.items():
        temp_cut = len(v)-1
        if temp_cut < n_cut:
            message = f'{k}变量最多只能分为{temp_cut}个箱，建议调整“n_cut”参数'
            warn(message, category=None, stacklevel=1, source=None)
            
def frdm_strategy_finder(data,groups,label,inputx,n_cut,n_rj_cut,n_pass_cut,bad_lift=3.5,good_lift=0.3,n_rounds=10,threds=[0.0063,0.34],missing_val_ls=[-99],random_state=0,if_print=False):
    """
    随机生成策略
    
    Parameters
    ----------
    data:pd.DataFrame
        分析样本：数据必须有日期变量、主键和Y变量
    groups: str
        指定切片变量
    label:str
        Y变量名，浮点型，取值为0.0,1.0，e.g: 'label'
    inputx:list 
        入模变量名列表, e.g ['regcap', 'industryco', 'empnum'],均为模型分。模型分要求：分数越高坏率越高。不可包含-99，建议将-99替换为9999。
    n_cut: int
        变量分箱数，e.g 10
    n_rj_cut:int 
        拒绝组模型分切点随机抽取的范围，该数值不可超过变量分箱数，即n_cut，e.g 如取6，则将在模型分后5个切点中随机生成策略
    n_pass_cut:int 
        通过组模型分切点随机抽取的范围，该数值不可超过变量分箱数，即n_cut，e.g 如取4，则将在模型分前3个切点中随机生成策略
    bad_lift:float (default = 3.5)
        模型高分段（最后一组）风险倍数的阈值
    good_lift:float (default = 0.3)
        模型低分段（第一组）风险倍数阈值
    n_rounds:int (default = 10)
        策略随机次数
    threds:list (default = [0.0063, 0.34])
        策略需要满足的条件[风险上线，通过率下限]
    if_print:bool
        是否打印每条策略
    random_state: int
    
    Returns
    -------
    rules:dict
        满足条件的策略字典
    
    """
    start_time = time.time()
    random.seed(random_state)
    data['id'] = data.index
    id_col = 'id'
    flg = check_dataframe(data, groups,id_col,label,inputx,missing_val_ls)
    if flg == 1:
        pass
    else:
        dic_cut, use_tg, use_rj = get_cut_dic(data, inputx, n_cut, label,bad_lift,good_lift,missing_val_ls)
        n_cut_check(dic_cut,n_cut)
        n_pass_cut = [i for i in range(1,n_pass_cut+1)]
        n_rj_cut = [-i for i in range(1,n_rj_cut+1)]
        tg_flag = 'tg_flag'
        rules = {}
        if len(use_tg) == 0 and len(use_rj) == 0:
            print('未找到符合要求的规则，请调整good_lift、bad_lift')
        elif len(use_rj) == 0 and len(use_tg) != 0 :
            print('未找到可以作拒绝规则的模型分，请向下调整bad_lift')
            for i in range(1,n_rounds+1):
                datatmp = data.copy(deep=True)
                # 随机生成策略
                a = get_quer_str_tg(use_tg, n_pass_cut, dic_cut)
                #b = get_quer_str_rj(use_rj, n_rj_cut, dic_cut)
                ab = a 
                datatmp.loc[datatmp.query(ab).index, tg_flag] = 'Y'
                datatmp[tg_flag] = datatmp[tg_flag].replace(np.nan, 'N')
                # 计算该策略下的通过率和风险指标
                res_tg = cal_fpd(datatmp, label,id_col,groups,tg_flag='tg_flag')
                # 总风险
                rsk_all = res_tg['fpd'].sum() / res_tg['tg_cnt2'].sum()
                # 总通过率
                tg_all = res_tg['tg_cnt'].sum() / res_tg['cnt'].sum()
                if if_print == True:
                    print("第{}条,风险为{},通过率为{}\n策略为{}：".format(i, round(rsk_all, 5),
                                                             round(tg_all, 5), ab))
                if (rsk_all <= threds[0]) & (tg_all >= threds[1]):
                    print("第{}条满足条件,风险为{},通过率为{}\n策略为{}\n".format(i, round(rsk_all, 5),
                                                                              round(tg_all, 5), ab))
                    print('------------------------')
                    rules[i] = ab
            if rules == {}:
                print('未找到符合要求的策略，请调整threds')
            else:
                print('花费时间：{}'.format(time.time()-start_time))
                rules = pd.DataFrame(rules,index = ['rule_str']).T
                rules = rules.reset_index(drop=True)
                return rules
        elif len(use_tg) == 0 and len(use_rj)!= 0:
            print('未找到可以作通过规则的模型分，请向上调整good_lift')
            for i in range(1,n_rounds+1):
                datatmp = data.copy(deep=True)
                # 随机生成策略
                #a = get_quer_str_tg(use_tg, n_pass_cut, dic_cut)
                b = get_quer_str_rj(use_rj, n_rj_cut, dic_cut)
                ab = 'not' + b
                datatmp.loc[datatmp.query(ab).index, tg_flag] = 'Y'
                datatmp[tg_flag] = datatmp[tg_flag].replace(np.nan, 'N')
                # 计算该策略下的通过率和风险指标
                res_tg = cal_fpd(datatmp, label,id_col,groups,tg_flag='tg_flag')
                # 总风险
                rsk_all = res_tg['fpd'].sum() / res_tg['tg_cnt2'].sum()
                # 总通过率
                tg_all = res_tg['tg_cnt'].sum() / res_tg['cnt'].sum()
                if if_print == True:
                    print("第{}条,风险为{},通过率为{}\n策略为{}：".format(i, round(rsk_all, 5),
                                                             round(tg_all, 5), ab))
                if (rsk_all <= threds[0]) & (tg_all >= threds[1]):
                    print("第{}条满足条件,风险为{},通过率为{}\n策略为{}\n".format(i, round(rsk_all, 5),
                                                                              round(tg_all, 5), ab))
                    print('------------------------')
                    rules[i] = ab
            if rules == {}:
                print('未找到符合要求的策略，请调整threds')
            else:
                print('花费时间：{}'.format(time.time()-start_time))
                rules = pd.DataFrame(rules,index = ['rule_str']).T
                rules = rules.reset_index(drop=True)
                return rules        
        else:
            for i in range(1,n_rounds+1):
                datatmp = data.copy(deep=True)
                # 随机生成策略
                a = get_quer_str_tg(use_tg, n_pass_cut, dic_cut)
                b = get_quer_str_rj(use_rj, n_rj_cut, dic_cut)
                ab = a + 'and not ' + b
                datatmp.loc[datatmp.query(ab).index, tg_flag] = 'Y'
                datatmp[tg_flag] = datatmp[tg_flag].replace(np.nan, 'N')
                # 计算该策略下的通过率和风险指标
                res_tg = cal_fpd(datatmp, label,id_col,groups,tg_flag='tg_flag')
                # 总风险
                rsk_all = res_tg['fpd'].sum() / res_tg['tg_cnt2'].sum()
                # 总通过率
                tg_all = res_tg['tg_cnt'].sum() / res_tg['cnt'].sum()
                if if_print == True:
                    print("第{}条,风险为{},通过率为{}\n策略为{}：".format(i, round(rsk_all, 5),
                                                             round(tg_all, 5), ab))
                if (rsk_all <= threds[0]) & (tg_all >= threds[1]):
                    print("第{}条满足条件,风险为{},通过率为{}\n策略为{}\n".format(i, round(rsk_all, 5),
                                                                              round(tg_all, 5), ab))
                    print('------------------------')
                    rules[i] = ab
            if rules == {}:
                print('未找到符合要求的策略，请调整threds')
            else:
                print('花费时间：{}'.format(time.time()-start_time))
                rules = pd.DataFrame(rules,index = ['rule_str']).T
                rules = rules.reset_index(drop=True)
                return rules

def check_dataframe(data, groups, id_col, label, inputx,missing_val_ls):

    print('-----开始检查数据------')
    # 检查groups类型
    flag = 0
    if pd.api.types.is_numeric_dtype(data[groups].loc[~data[groups].isin(missing_val_ls)].dtypes):
        print('groups检查正确')
    else:
        print('groups类型错误')
        flag = 1
    # 检查id_col是否唯一
    if len(data[id_col].unique()) == len(data):
        print('id_col检查正确')
    else:
        print('id_col不唯一')
        flag = 1
    # 检查label数据类型
    if pd.api.types.is_numeric_dtype(data[label].loc[data[label].isin(missing_val_ls)].dtypes):
        print('label检查正确')
    else:
        print('label类型错误')
        flag = 1
        # 检查分数是否有异常
#    if (data[inputx] == -99).sum().sum() == 0:
#        print('inputx检查正确')
#    else:
#        print('inputx分数有异常')
#        flag = 1
    print('-----数据检查完毕------')
    return flag


def tree_to_rule_classifier(tree, feature_names):
    '''用于将决策树拆解为多条规则，规则为决策树到中间节点以及最终叶节点的路径 - 分类
    
    Parameters
    ----------
    tree :sklearn.tree.DecisionTreeClassifier
        训练好的slearn.tree.DecisionTreeClassifier类
    feature_names:list
        tree对应的输入项变量名列表

    Returns
    -------
    data_rep:pd.DataFrame
        决策树拆分后、分裂节点及叶节点的0\1 样本个数、以及正样本比例

    '''
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    data_rep = pd.DataFrame([i[0] for i in tree_.value],columns=['node0','node1'])
    data_rep['bad_rate'] = data_rep['node1'] / (data_rep['node0'] + data_rep['node1'])
    left = tree_.children_left
    right = tree_.children_right
    threshold = tree_.threshold
    idx_right = np.argwhere(left == -1)[:,0]
    idx_left = np.argwhere(right == -1)[:,0]
    features = [feature_names[i] for i in tree_.feature]
    def recurse(left, right, child, lineage=None, restr=''):
        if lineage is None:
            lineage = [child]
        if child in left :
            parent = np.where(left == child)[0].item()
            split = 'l'
            sp = '<='
        else:
            parent = np.where(right == child)[0].item()
            split = 'r'
            sp = '>'
        lineage.append((parent, split, threshold[parent], features[parent]))
        restr += '({}{}{}) &'.format(features[parent], sp, threshold[parent])
        
        if parent == 0:
            lineage.reverse()
            restr = restr[:-1]
            return lineage, restr
        else:
            return recurse(left, right, parent, lineage,restr)
    
    for child in list(data_rep.index)[1:]:
        for node in recurse(left, right, child, lineage=None, restr=''):
            #print(node)
            pass
    data_rep = data_rep.reset_index()
    data_rep = data_rep[data_rep.index>0]
    data_rep['rule_str'] = data_rep['index'].apply(lambda s:recurse(left, right, int(s), lineage=None, restr='')[1])
    return data_rep



def tree_to_rule_regressor(tree, feature_names):
    '''用于将决策树拆解为多条规则，规则为决策树到中间节点以及最终叶节点的路径 - 回归
    
    Parameters
    ----------
    tree :sklearn.tree.DecisionTreeRegressor) 
        训练好的slearn.tree.DecisionTreeRegressor类
    feature_names :list
        tree对应的输入项变量名列表

    Returns
    -------
    data_rep:pd.DataFrame
        决策树拆分后、分裂节点及叶节点的样本个数、以及目标变量均值

    '''
    
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature]
    data_rep = pd.DataFrame([i[0] for i in tree_.value], columns=['node0'])
    data_rep['count'] = list(tree_.weighted_n_node_samples)
    left = tree_.children_left
    right = tree_.children_right
    threshold = tree_.threshold
    idx_right = np.argwhere(left == -1)[:,0]
    idx_left = np.argwhere(right == -1)[:,0]
    features = [feature_names[i] for i in tree_.feature]
    def recurse(left, right, child, lineage=None, restr=''):
        if lineage is None:
            lineage = [child]
        if child in left :
            parent=np.where(left == child)[0].item()
            split = 'l'
            sp = '<='
        else:
            parent = np.where(right == child)[0].item()
            split = 'r'
            sp = '>'
        lineage.append((parent, split, threshold[parent], features[parent]))
        restr += '({}{}{}) &'.format(features[parent], sp, threshold[parent])
        
        if parent == 0:
            lineage.reverse()
            restr = restr[:-1]
            return lineage,restr
        else:
            return recurse(left, right, parent, lineage, restr)
    
    for child in list(data_rep.index)[1:]:
        for node in recurse(left, right, child, lineage=None, restr=''):
            pass
    data_rep = data_rep.reset_index()
    data_rep = data_rep[data_rep.index>0]
    data_rep['str'] = data_rep['index'].apply(lambda s:recurse(left,right,int(s),lineage=None,restr='')[1])
    return data_rep


def generateRuleClassifier(data, num_feature_min, num_feature_max, inputx, label, depth, min_samples_leaf, random_state):
    '''自动生成决策树，并获得决策树生成路径上的所有规则以及对应的统计指标
    
    Parameters
    ----------
    data :pd.DataFrame
        训练集
    num_feature_min:int
        规则包含的最小变量数
    num_feature_max:int
        规则包含的最大变量数
    inputx:list
        规则生成所使用的变量空间
    y:str
        指定目标变量
    depth:int
        决策树深度，与生成的规则复杂度有关
    min_samples_leaf:int
        叶节点最小样本数
    random_state:int
        伪随机数

    Returns
    -------
    data_class:pd.DataFrame
        决策树拆分后、分裂节点及叶节点的0\1 样本个数、以及正样本比例

    '''
    if random_state is None:
        pass
    else:
        np.random.seed(random_state)
    ns = np.random.choice(range(num_feature_min,num_feature_max))
    fea = np.random.permutation(len(inputx))
    cho = [inputx[fea[i]] for i in range(ns)]
    estimator = tree.DecisionTreeClassifier(max_depth=depth, min_samples_leaf=min_samples_leaf,random_state=random_state)
    estimator.fit(data[cho], data[label])
    data_tree = tree_to_rule_classifier(estimator,cho)
    data_tree = data_tree.sort_values(by='node0')
    return data_tree


def generateRuleRegressor(data, num_feature_min, num_feature_max, inputx, label, depth, min_samples_leaf, random_state):
    '''自动生成决策树，并获得决策树生成路径上的所有规则以及对应的统计指标 - 回归
    
    Parameters
    ----------
    data :pd.DataFrame
        训练集
    num_feature_min:int
        规则包含的最小变量数
    num_feature_max:int
        规则包含的最大变量数
    inputx:list
        规则生成所使用的变量空间
    y:str
        指定目标变量
    depth:int
        决策树深度，与生成的规则复杂度有关
    min_samples_leaf:int
        叶节点最小样本数
    random_state:int
        伪随机数

    Returns
    -------
    data_class:pd.DataFrame
        决策树拆分后、分裂节点及叶节点的样本个数、以及目标变量均值

    '''
    if random_state is None:
        pass
    else:
        np.random.seed(random_state)
    ns = np.random.choice(range(num_feature_min,num_feature_max))
    fea = np.random.permutation(len(inputx))
    cho = [inputx[fea[i]] for i in range(ns)]
    estimator = tree.DecisionTreeRegressor(max_depth=depth,min_samples_leaf=min_samples_leaf)
    estimator.fit(data[cho],data[label])
    data_tree=tree_to_rule_regressor(estimator,cho)
    data_tree=data_tree.sort_values(by='node0')
    return data_tree

def atsr_rule_finder_clf(data, n_rounds, num_feature_min, num_feature_max, inputx, label='fpd4', depth=7, min_samples_leaf=500, random_state=None):
    
    '''自动生成规则，并获得所有规则对应的统计指标 - 分类
    
    Parameters
    ----------
    data :pd.DataFrame
        训练集
    n_rounds :int
        生成多少棵决策树
    num_feature_min:int
        规则包含的最小变量数
    num_feature_max:int
        规则包含的最大变量数
    inputx:list
        规则生成所使用的变量空间
    label:str
        指定目标变量
    depth:int
        决策树深度，与生成的规则复杂度有关
    min_samples_leaf:int
        叶节点最小样本数
    random_state:int
        伪随机数

    Returns
    -------
    data_class:pd.DataFrame
        生成规则、和对应的0\1 样本个数、以及正样本比例

    '''
    data_class = pd.DataFrame()
    tqdmRange = tqdm(list(range(n_rounds)))
    for i in tqdmRange:
        if random_state == None:
            random_state = None
        else:
            random_state = random_state +1
        print(random_state)
        tmp=generateRuleClassifier(data,num_feature_min=num_feature_min, num_feature_max=num_feature_max,
                                   inputx=inputx, label=label, depth=depth, min_samples_leaf=min_samples_leaf, random_state=random_state)
        data_class=pd.concat([data_class,tmp],axis=0)
        if  1:
            tqdmRange.set_description('Processing %d n_rounds'.center(20)%i)

    data_class = data_class.drop(columns='index')
    data_class = data_class.drop_duplicates()
    data_class = data_class.reset_index().drop(columns='index')
    return data_class[['rule_str','node0','node1','bad_rate']] 


def atsr_rule_finder_reg(data, n_rounds, num_feature_min, num_feature_max, inputx, label='profit', depth=7, min_samples_leaf=500, random_state=None):
    '''自动生成规则，并获得所有规则对应的统计指标 - 回归
    
    Parameters
    ----------
    data：pd.DataFrame)
        训练集
    n_rounds:int
        生成多少棵决策树
    num_feature_min :int
        规则包含的最小变量数
    num_feature_max:int
        规则包含的最大变量数
    inputx:list
        规则生成所使用的变量空间
    label :str
        指定目标变量
    depth:int
        决策树深度，与生成的规则复杂度有关
    min_samples_leaf :int
        叶节点最小样本数
    random_state:int
        伪随机数

    Returns
    -------
    data_class:pd.DataFrame
        生成规则、和对应的分裂节点及叶节点的样本个数、以及目标变量均值

    '''
    
    data_class = pd.DataFrame()
    tqdmRange = tqdm(list(range(n_rounds)))
    for i in tqdmRange:
        if random_state == None:
            random_state = None
        else:
            random_state = random_state +1
        print(random_state)
        tmp=generateRuleRegressor(data,num_feature_min=num_feature_min, num_feature_max=num_feature_max,
                                   inputx=inputx, label=label, depth=depth, min_samples_leaf=min_samples_leaf, random_state=random_state)
        data_class=pd.concat([data_class,tmp],axis=0)
        if  1:
            tqdmRange.set_description('Processing %d n_rounds'.center(20)%i)

    data_class = data_class.drop(columns='index')
    data_class = data_class.drop_duplicates()
    data_class = data_class.reset_index().drop(columns='index')
    data_class.columns = ['mean', 'count', 'rule_str']
    return data_class[['rule_str', 'count', 'mean']]
    
    

def reportRuleClassifier(rule, data, label, groups,id_col):
    '''生成规则报告-分类
    
    Parameters
    ----------
    rule :str
        规则
    data:pd.DataFrame
        数据样本集
    label:str
        指定目标变量（0、1二分类）
    groups:str
        指定切片变量，默认为'create_month'

    Returns
    -------
    data_all_data:pd.DataFrame
        规则报告

    '''
    #计算人数
    temp_sub = data.query(rule)
    data_cnt_data = pd.pivot_table(temp_sub, index=groups, values=id_col, aggfunc=len, margins=True)
    #计算违约人数
    data_y_data = pd.pivot_table(temp_sub, index=groups,values=label, aggfunc=sum, margins=True)
    data_avg_pct = pd.pivot_table(data, index=groups,values=label, aggfunc=np.mean, margins=True)
    #计算坏率
    data_all_data = pd.concat([data_cnt_data,data_y_data,data_avg_pct],axis=1,sort=True)
    data_all_data.columns = ['cnt',label,'avg_pct']
    data_all_data[label+'_pct'] = data_all_data[label]/data_all_data.cnt
    data_all_data['lift'] = data_all_data[label+'_pct']/data_all_data.avg_pct
    data_all_data.index.name = groups
    return pd.DataFrame(data_all_data.unstack(groups),columns=[rule]) 
   
def reportRuleRegressor(rule, data, label, groups,id_col):
    '''生成规则报告 - 回归
    
    Parameters
    ----------
    rule ：str
        规则
    data：pd.DataFrame
        数据样本集
    label :str
        指定目标变量（连续变量）
    groups:str
        指定切片变量，默认为'create_month'

    Returns
    -------
    data_all_data:pd.DataFrame
        规则报告

    '''
    #计算人数
    temp_sub = data.query(rule)
    data_cnt_data = pd.pivot_table(temp_sub, index=groups, values=id_col, aggfunc=len, margins=True)
    #计算违约人数
    data_y_data = pd.pivot_table(temp_sub, index=groups,values=label, aggfunc=np.mean, margins=True)
    data_avg = pd.pivot_table(data, index=groups,values=label, aggfunc=np.mean, margins=True)
    #计算坏率
    data_all_data = pd.concat([data_cnt_data,data_y_data,data_avg],axis=1)
    data_all_data.columns = ['cnt',label,'avg']
    data_all_data['lift'] = data_all_data[label] - data_all_data.avg
    data_all_data.index.name = groups
    return pd.DataFrame(data_all_data.unstack(groups),columns=[rule])        

def rule_report_clf(data, rule_df, rule_col='rule_str', label='fpd4', groups='create_month'):
    '''生成规则报告-分类
    
    Parameters
    ----------
    data :pd.DataFrame
        数据样本集
    rule_df :pd.DataFrame
        规则集
    rule_col ：str
        规则集变量，默认为'rule_str'
    label :str 
        指定目标变量（0、1二分类）,默认为'fpd4'
    groups :str
        指定切片变量，默认为'create_month'

    Returns
    -------
    data_report :pd.DataFrame
        规则报告
        
    '''
    data = data.reset_index()
    data = data.rename(columns ={'index':'id'})
    id_col = 'id'
    data_report= pd.DataFrame()
    rule_df = rule_df.reset_index().drop(columns='index')
    tqdmStr = tqdm(list(rule_df[rule_col]))
    for i in tqdmStr:
        temp = reportRuleClassifier(i, data, label, groups, id_col)
        data_report = pd.concat([data_report,temp],axis=1)
        tqdmStr.set_description('Processing %s'.center(40)%i)
    data_report = data_report.T
    return data_report[[i for i in data_report.columns if i[0] != 'avg_pct']]


def rule_report_reg(data, rule_df, rule_col='rule_str', label='profit', groups='create_month'):
    '''生成规则报告-回归
    
    Parameters
    ----------
    data :pd.DataFrame
        数据样本集
    rule_df :pd.DataFrame
        规则集
    rule_col：str
        规则集变量，默认为'rule_str'
    label :str
        指定目标变量（连续变量）,默认为'profit'
    groups：str
        指定切片变量，默认为'create_month'

    Returns
    -------
    data_report :pd.DataFrame
        规则报告
    '''
    data = data.reset_index()
    data = data.rename(columns ={'index':'id'})
    id_col = 'id'
    data_report= pd.DataFrame()
    rule_df = rule_df.reset_index().drop(columns='index')
    tqdmStr = tqdm(list(rule_df[rule_col]))
    for i in tqdmStr:
        temp = reportRuleRegressor(i, data, label, groups, id_col)
        data_report = pd.concat([data_report,temp],axis=1)
        tqdmStr.set_description('Processing %s'.center(40)%i)
    data_report = data_report.T
    return data_report[[i for i in data_report.columns if i[0] != 'avg']]


def ruledataTrans(rule_df,rule_col,index_col):
    '''生成规则报告
    
    Parameters
    ----------
    rule_df ：pd.DataFrame
        规则集
    rule_col :str
        规则集变量，默认为'rule_str'
    index_col :str
        规则标识变量

    Returns
    -------
    data: pd.DataFrame
        规则集
    
    '''
    def rule_to_data(rule):
        temp = []
        for i in rule.split('&'):
            i = i.strip().lstrip('(').rstrip().rstrip(')')
            if '<=' in i:
                temp.append((i.split('<=')[0],'<=',i.split('<=')[1]))
            elif '>'  in i :
                temp.append((i.split('>')[0],'>',i.split('>')[1]))
        return pd.DataFrame(temp,columns=['var_name','dir','threshold'])
    data=pd.DataFrame()
    for idx in range(len(rule_df)):
        temp = rule_to_data(rule_df[rule_col][idx])
        temp['ids'] = rule_df[index_col][idx]
        data=pd.concat([data,temp],axis=0)
    data=data.reset_index().drop(columns='index')
    return data


def atsrRuleVarImp(rule_df, rule_col='rule_str'):
    '''生成规则报告
    
    Parameters
    ----------
    rule_df : pd.DataFrame
        规则集
    rule_col :str
        规则集变量，默认为'rule_str'

    Returns
    -------
    feature_importance : tuple
        高频变量使用阈值
        
    '''
    rule_df = rule_df.reset_index()
    rule_df = rule_df.rename(columns={'index':'id'})
    data= ruledataTrans(rule_df,rule_col,'id')
    result = data.groupby(['var_name'])['ids'].apply(lambda s:len(set(s))).reset_index()
    result.columns = ['var_name', 'imp'] 
    data_less = data[data.dir=='<='].sort_values(by='threshold',ascending=True).reset_index().drop(columns=['index'])
    data_greater = data[data.dir=='>'].sort_values(by='threshold',ascending=False).reset_index().drop(columns=['index'])
    data_less = data_less.drop_duplicates(['ids','var_name']).reset_index().drop(columns=['index'])
    data_greater = data_greater.drop_duplicates(['ids','var_name']).reset_index().drop(columns=['index'])
    data = pd.concat([data_less,data_greater],axis=0).reset_index().drop(columns=['index'])


    data_less['threshold'] = data_less['threshold'].astype('float')
    data_greater['threshold'] = data_greater['threshold'].astype('float')
    dataLess = data_less.var_name.value_counts()
    lessList = list(dataLess[dataLess>-1].index)
    data_less = data_less.iloc[[i for i in range(len(data_less)) if data_less.var_name[i] in lessList],:].reset_index().drop(columns=['index'])
    dataGreater = data_greater.var_name.value_counts()
    GreaterList = list(dataGreater[dataGreater>-1].index)
    data_greater = data_greater.iloc[[i for i in range(len(data_greater)) if data_greater.var_name[i] in GreaterList],:].reset_index().drop(columns=['index'])
    data_less = data_less.groupby(['dir','var_name'])['threshold'].agg(lambda s:s.quantile(0.75)).reset_index()
    data_greater = data_greater.groupby(['dir','var_name'])['threshold'].agg(lambda s:s.quantile(0.25)).reset_index()
    data_rule_space = pd.concat([data_less,data_greater],axis=0).reset_index().drop(columns=['index'])
    data_rule_space['rule'] = data_rule_space.apply(lambda s:'({}{}{})'.format(s['var_name'],s['dir'],s['threshold']),axis=1)
    
    return result, data_rule_space[['var_name','dir','threshold','rule']]



