# -*- coding: utf-8 -*-
# from sklearn.inspection import permutation_importance
from sklearn.metrics import make_scorer
from sklearn.utils import check_array,Bunch,check_random_state
from sklearn.metrics import check_scoring
from joblib import Parallel,delayed
from scipy.stats import ks_2samp
import numpy as np
import pandas as pd
from itertools import combinations
# def my_score_metric(labels, preds):
#     df = pd.DataFrame({'pred': preds, 'labels': labels})
#     df = df.loc[df['pred'] <= scoring_dict["shrehold"]]
#     return ks_2samp(df.loc[df["labels"] == 1, "pred"], df.loc[df["labels"] != 1, "pred"]).statistic

# score = make_scorer(my_ks_metric, greater_is_better=True,needs_proba=True)
# score2 = make_scorer(my_binary_metric, greater_is_better=False,needs_proba=True)
# score3 = make_scorer(my_score_metric, greater_is_better=True,needs_proba=True)
# score2(lgb_clf_afs,temp_df[model_project_dict['final_ls']],data_oot[y])

def _calculate_const_scores(estimator, X, y,constant_value, col_idx,scorer,baseline_score,col):
    """Calculate cont score"""

    X_permuted = X.copy()
    if hasattr(X_permuted, "iloc"):
        # print("col_idx=",col_idx)
        inter_col = list(set(col_idx) & set(col))
        if inter_col:
            X_permuted.loc[:, inter_col] = constant_value
        else:
            return col_idx,baseline_score
    else:
        raise ValueError('input type should be DataFrame!')
    feature_score = scorer(estimator, X_permuted, y)
    print(col_idx,round(feature_score,6))
    return col_idx,feature_score

def _calculate_const_scores_grp(estimator, X, y,constant_value, item,scorer,feature_grp,baseline_score,col):
    """Calculate cont score"""

    X_permuted = X.copy()
    if hasattr(X_permuted, "iloc"):
        column = []
        for i in item:
            column = list(set(column) | set(feature_grp[i]))
        if not list(set(column) & set(col)):
            return item,baseline_score
        else:
            X_permuted.loc[:, column] = constant_value
    else:
        raise ValueError('input type should be DataFrame!')
    feature_score = scorer(estimator, X_permuted, y)
    print(item,round(feature_score,6))
    return item,feature_score


def _calculate_permutation_scores_grp(estimator, X, y, item, random_state,
                                  n_repeats, scorer, feature_grp,baseline_score,col):
    """Calculate permut grp score"""
    random_state = check_random_state(random_state)

    X_permuted = X.copy()
    scores = np.zeros(n_repeats)
    shuffling_idx = np.arange(X.shape[0])

    column = []
    for i in item:
        column = list(set(column) | set(feature_grp[i]))
    if not list(set(column) & set(col)):
        scores[:] = baseline_score
        return item,scores

    for n_round in range(n_repeats):
        random_state.shuffle(shuffling_idx)
        if hasattr(X_permuted, "iloc"):
            col = X_permuted.loc[shuffling_idx, column]
            col.index = X_permuted.index
            X_permuted.loc[:, column] = col
        else:
            raise ValueError('input type should be DataFrame!')
        feature_score = scorer(estimator, X_permuted, y)
        scores[n_round] = feature_score

    print(item,round(feature_score,6))
    return item,scores


def _calculate_permutation_scores(estimator, X, y, item, random_state,
                                  n_repeats, scorer,baseline_score,col):
    """Calculate permut grp score"""
    random_state = check_random_state(random_state)

    X_permuted = X.copy()
    scores = np.zeros(n_repeats)
    shuffling_idx = np.arange(X.shape[0])

    column = list(set(item) & set(col))
    if not column:
        scores[:] = baseline_score
        return item,scores

    for n_round in range(n_repeats):
        random_state.shuffle(shuffling_idx)
        # print("shuffling_idx=",shuffling_idx,column)
        if hasattr(X_permuted, "iloc"):
            col = X_permuted.loc[shuffling_idx, column]
            col.index = X_permuted.index
            X_permuted.loc[:, column] = col
        else:
            raise ValueError('input type should be DataFrame!')
        feature_score = scorer(estimator, X_permuted, y)
        scores[n_round] = feature_score

    print(item,round(feature_score,6))
    return item,scores

def const_importance(estimator, X, y,col,constant_value, scoring=None,
                           n_jobs=None,feature_grp = None,feature_cnt = 1):
    """const_importance

    Parameters
    ----------
    estimator : 模型

    X : DataFrame, shape (n_samples, n_features)

    y : array-like,目标变量

    col : list,入模特征

    constant_value : float or int,设定常量值

    scoring : string, callable or None, default=None，评分函数

    n_jobs : int or None, 并行任务数 default=None，`-1` means using all processors.

    feature_grp : dict or None, 如果设定，则依据特征组定义字典，如果为None，以特征为单位评估

    feature_cnt : int default 1,特征选择数量

    Returns
    -------
    result : Dict
        Dictionary-like object

    """
    if not hasattr(X, "iloc"):
        X = check_array(X, force_all_finite='allow-nan', dtype=None)

    scorer = check_scoring(estimator, scoring=scoring)
    baseline_score = scorer(estimator, X, y)

    if feature_grp:
        comb = list(combinations(feature_grp.keys(),feature_cnt))
        scores = Parallel(n_jobs=n_jobs)(delayed(_calculate_const_scores_grp)(\
            estimator, X, y, constant_value,c, scorer,feature_grp,baseline_score,col\
        ) for c in comb)
    else:
        comb = list(combinations(X.columns.tolist(),feature_cnt))
        print("comb = ",comb)
        # scores = []
        # for c in comb:
        #     print("ccc=",c)
        #     scores.append(_calculate_const_scores(estimator, X, y, constant_value,c, scorer,baseline_score,col))
        scores = Parallel(n_jobs=n_jobs,backend='threading')(delayed(_calculate_const_scores)(\
            estimator, X, y, constant_value,c, scorer,baseline_score,col\
        ) for c in comb)
        # print("scores = ",scores)

    rtn_dict = {i[0]:baseline_score - i[1] for i in scores}
    # print("!!!",rtn_dict[("credit_repayment_score_bj", "relation_contact_cnt")])
    # importances = baseline_score - np.array(scores)
    return rtn_dict

def permut_importance_grp(estimator, X, y,col, scoring=None, n_repeats=5,
                           n_jobs=None, random_state=None,feature_grp=None,feature_cnt = 1):
    """permut_importance_grp

    Parameters
    ----------
    estimator : 模型

    X : DataFrame, shape (n_samples, n_features)

    y : array-like,目标变量

    col : list,入模特征

    constant_value : float or int,设定常量值

    scoring : string, callable or None, default=None，评分函数

    n_repeats : int, default 5, 执行轮数

    n_jobs : int or None, 并行任务数 default=None，`-1` means using all processors.

    random_state : int or None, 随机数种子

    feature_cnt : int default 1,特征选择数量

    Returns
    -------
    result : Dict
        Dictionary-like object

    """
    random_state = check_random_state(random_state)
    random_seed = random_state.randint(np.iinfo(np.int32).max + 1)

    scorer = check_scoring(estimator, scoring=scoring)
    baseline_score = scorer(estimator, X, y)

    comb = list(combinations(feature_grp.keys(), feature_cnt))
    scores = Parallel(n_jobs=n_jobs, backend='threading')(delayed(_calculate_permutation_scores_grp)( \
        estimator, X, y, c, random_seed, n_repeats, scorer, feature_grp,baseline_score, col \
        ) for c in comb)

    importance_scores = {i[0]:baseline_score - i[1] for i in scores}
    importances_df = pd.DataFrame(zip(importance_scores.keys(), importance_scores.values()),columns = ['grp','importances'])
    importances_df['importances_mean'] =importances_df['importances'].apply(np.mean)
    importances_df['importances_std'] =importances_df['importances'].apply(np.std)
    return importances_df

def permut_importance(estimator, X, y,col, scoring=None, n_repeats=5,
                           n_jobs=None, random_state=None,feature_cnt = 1):

    """permut_importance

    Parameters
    ----------
    estimator : 模型

    X : DataFrame, shape (n_samples, n_features)

    y : array-like,目标变量

    col : list,入模特征

    constant_value : float or int,设定常量值

    scoring : string, callable or None, default=None，评分函数

    n_repeats : int, default 5, 执行轮数

    n_jobs : int or None, 并行任务数 default=None，`-1` means using all processors.

    random_state : int or None, 随机数种子

    feature_cnt : int default 1,特征选择数量

    Returns
    -------
    result : Dict
        Dictionary-like object

    """
    random_state = check_random_state(random_state)
    random_seed = random_state.randint(np.iinfo(np.int32).max + 1)

    scorer = check_scoring(estimator, scoring=scoring)
    baseline_score = scorer(estimator, X, y)

    comb = list(combinations(X.columns.tolist(), feature_cnt))
    scores = Parallel(n_jobs=n_jobs, backend='threading')(delayed(_calculate_permutation_scores)( \
        estimator, X, y, c, random_seed, n_repeats, scorer,baseline_score, col \
        ) for c in comb)

    # def _calculate_permutation_scores(estimator, X, y, item, random_state,
    #                                   n_repeats, scorer, baseline_score, col):
    importance_scores = {i[0]:baseline_score - i[1] for i in scores}
    # print("importance_scores=",importance_scores)
    importances_df = pd.DataFrame(zip(importance_scores.keys(), importance_scores.values()),columns = ['grp','importances'])
    importances_df['importances_mean'] =importances_df['importances'].apply(np.mean)
    importances_df['importances_std'] =importances_df['importances'].apply(np.std)
    return importances_df

def feature_permutation(clf,X,Y,scoring_dict,feature_cnt = 1,iterations=30,random_state=None,\
                        constant_value = None,n_jobs=None,feature_grp=None,na_value = 999999):
    """feature_permutation

    Parameters
    ----------
    estimator : 模型

    X : DataFrame, shape (n_samples, n_features)

    y : array-like,目标变量

    scoring_dict : dict,评价方式字典,目前支持ks,auc,lift,dist四种模式,auc和ks模式下只需要配置metric,如果是lift和dist模式下，
            需要配置mode（L代表模型头部，H代表模型尾部)、shrehold_type（C代表固定值，Q代表样本分位数）、阈值shrehold（shrehold_type为C
            的情况下设定固定值，Q的情况设定分位数，分位数取值范围为0到1）
            eg:
            1. scoring_dict = {"metric":"auc"}
            2. scoring_dict = {"metric":"ks"}
            3. scoring_dict = {"metric":"lift","mode":"L","shrehold":0.012,"shrehold_type" : 'C'}#固定cutoff下的低风险目标
            4. scoring_dict = {"metric":"lift","mode":"H","shrehold":0.95,"shrehold_type" : 'Q'}#相对cutoff下的高风险目标
            5. scoring_dict = {"metric":"dist","mode":"L","shrehold":0.012,"shrehold_type" : 'C'}#分布变化

    feature_cnt : int default 1,特征或者特征组选择数量

    iterations : int, default 30, 执行轮数

    random_state : int or None, 随机数种子

    constant_value : None or float or int  ,default = None,设定常量值

    n_jobs : int or None, 并行任务数 default=None，`-1` means using all processors.

    feature_grp : dict or None, 如果不为None，则依据特征组字典的键为单位评估，如果为None，以特征为单位评估

    na_value : int default 999999,评价函数异常时的设定值

    Returns
    -------
    result : pi_df
        重要性评估结果表

    """
    if scoring_dict["metric"] == 'auc':
        scoring = 'roc_auc'
    elif scoring_dict["metric"] == 'ks':
        def my_ks_metric(labels, preds):
            return ks_2samp(preds[np.array(labels) == 1], preds[np.array(labels) != 1]).statistic
        scoring = make_scorer(my_ks_metric, greater_is_better=True,needs_proba=True)
    elif scoring_dict["metric"] == 'lift':
        def my_binary_metric(labels, preds):
            df = pd.DataFrame({'pred': preds, 'percent': preds, 'labels': labels})
            key = scoring_dict["shrehold"] if scoring_dict["shrehold_type"] == "C" else df['percent'].quantile(scoring_dict["shrehold"])
            if scoring_dict["mode"] =='L':
                df['percent'] = df['percent'].map(lambda x: 1 if x <= key else 0)
            else:
                df['percent'] = df['percent'].map(lambda x: 1 if x >= key else 0)
            result = np.mean(df[df.percent == 1]['labels'] == 1)
            return result
        greater_is_better = False if scoring_dict["mode"] == 'L' else True
        # print (greater_is_better)
        scoring = make_scorer(my_binary_metric, greater_is_better=greater_is_better,needs_proba=True)
    elif scoring_dict["metric"] == 'dist':
        def my_binary_metric(labels, preds):
            df = pd.DataFrame({'pred': preds, 'percent': preds})
            key = scoring_dict["shrehold"] if scoring_dict["shrehold_type"] == "C" else df['percent'].quantile(scoring_dict["shrehold"])
            if scoring_dict["mode"] =='L':
                df['percent'] = df['percent'].map(lambda x: 1 if x <= key else 0)
            else:
                df['percent'] = df['percent'].map(lambda x: 1 if x >= key else 0)
            return df['percent'].mean()
        greater_is_better = False if scoring_dict["mode"] == 'L' else True
        # print (greater_is_better)
        scoring = make_scorer(my_binary_metric, greater_is_better=greater_is_better,needs_proba=True)

    if callable(scoring):
        origin_score = scoring(clf, X, Y)
        print ("origin_score",origin_score)
    #固定值模式
    if constant_value:
        # print(f"constant_value={constant_value}")
        col = X.columns[clf.feature_importances_ > 0].tolist()
        # print (f"col={col}")
        res = const_importance(estimator = clf,
                                     X=X,
                                     y=Y,
                                     col = col,
                                     scoring=scoring,
                                     constant_value=constant_value,
                                     feature_grp=feature_grp,
                                     feature_cnt = feature_cnt,
                                     )
        if feature_grp:
            zx_grp_dic = {}
            for k, v in feature_grp.items():
                for i in v:
                    zx_grp_dic[i] = k
            temp_df = pd.DataFrame(zip([zx_grp_dic.get(i) for i in X.columns], X.columns, clf.feature_importances_),
                         columns=['grp', 'variable', 'imp_in_model'])
            temp_df = temp_df.groupby("grp")['imp_in_model'].sum()/clf.feature_importances_.sum()
            # temp_df.loc[temp_df['grp'].isin(res.keys()),'imp_in_model'].sum()
            print(f"temp_df={temp_df}")
            pi_df = pd.DataFrame(zip(res.keys(),res.values(),[temp_df.loc[list(f)].sum() for f in res.keys()]),
                    columns = ["grp", "imp_mean", "imp_in_model"])
            pi_df['imp_mean'] = pi_df['imp_mean'].fillna(na_value)
            pi_df = pi_df.sort_values(
                ["imp_mean"], ascending=[False]).reset_index(drop=True)
        else:
            # print("res=",res)
            temp_df = pd.DataFrame(zip(X.columns, clf.feature_importances_/clf.feature_importances_.sum()),
                         columns=['variable', 'imp_in_model'])
            pi_df = pd.DataFrame(zip(res.keys(), res.values(),\
                                     [temp_df.loc[temp_df['variable'].isin(f),"imp_in_model"].sum() for f in res.keys()]),\
                                 columns=["variable", "imp_mean","imp_in_model"])
            pi_df['imp_mean'] = pi_df['imp_mean'].fillna(na_value)
            pi_df = pi_df.sort_values(\
                ["imp_mean"], ascending=[False]).reset_index(drop=True)
    #permutation模式
    else:
        col = X.columns[clf.feature_importances_ > 0].tolist()
        if feature_grp:
            res = permut_importance_grp(clf,
                                         X,
                                         Y,
                                         col=col,
                                         n_repeats=iterations,
                                         scoring=scoring,
                                         random_state = random_state,
                                         n_jobs = n_jobs,
                                         feature_grp=feature_grp,
                                         feature_cnt = feature_cnt,
                                         )
            zx_grp_dic = {}
            for k, v in feature_grp.items():
                for i in v:
                    zx_grp_dic[i] = k
            temp_df = pd.DataFrame(zip([zx_grp_dic.get(i) for i in X.columns], X.columns, clf.feature_importances_),
                         columns=['grp', 'variable', 'imp_in_model'])
            temp_df = temp_df.groupby("grp")['imp_in_model'].sum()/clf.feature_importances_.sum()
            print("temp_df=",temp_df)
            res['imp_in_model'] = res['grp'].apply(lambda x:temp_df[list(x)].sum())
            # pi_df = pd.DataFrame(zip(feature_grp.keys(),res['importances_mean'],res['importances_std'],\
            #                          res["importances"],[temp_df[f] for f in feature_grp.keys()]),
            #         columns = ["grp", "imp_mean",'imp_std',"imp_detail", "imp_in_model"])
            res['importances_mean'] = res['importances_mean'].fillna(na_value)
            pi_df=res.sort_values(["importances_mean", 'importances_std'], ascending=[False, False]).reset_index(drop=True)
        else:
            res = permut_importance(clf,
                                         X,
                                         Y,
                                         col = col,
                                         n_repeats=iterations,
                                         scoring=scoring,
                                         random_state = random_state,
                                         n_jobs = n_jobs,
                                         feature_cnt=feature_cnt
                                         )
            # temp_df = pd.DataFrame(zip(X.columns.tolist(),clf.feature_importances_ / clf.feature_importances_.sum()),\
            #                      columns=["variable","imp_in_model"])

            temp_df = pd.Series(clf.feature_importances_ / clf.feature_importances_.sum(),\
                                 index=X.columns.tolist())
            print("temp_df=",temp_df)
            res['imp_in_model'] = res['grp'].apply(lambda x:temp_df[list(x)].sum())
            res['importances_mean'] = res['importances_mean'].fillna(na_value)
            pi_df=res.sort_values( ["importances_mean", 'importances_std'], ascending=[False, False]).reset_index(drop=True)

    return pi_df
