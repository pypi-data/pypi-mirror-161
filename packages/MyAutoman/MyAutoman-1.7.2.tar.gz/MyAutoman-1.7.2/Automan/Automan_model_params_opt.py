# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import random
import warnings
from hyperopt import hp, fmin, tpe, Trials
from matplotlib import pyplot as plt
from scipy.stats import ks_2samp
from sklearn.linear_model import LogisticRegression
from scipy import stats
import re
from pandas.api.types import is_numeric_dtype
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.metaestimators import if_delegate_has_method
from itertools import product
from joblib import Parallel, delayed
from sklearn.base import clone
import contextlib
import io
from copy import deepcopy
from sklearn.utils.validation import check_is_fitted
from shap import TreeExplainer
warnings.filterwarnings("ignore")


C_SET = ['gray', 'green', 'yellow', 'blue', 'black', 'red', 'gold', 'indigo', 'aqua', 'khaki']


def ks_score(preds, trainDmatrix):
    y_true = trainDmatrix.get_label()
    return 'ks', -ks_2samp(preds[np.array(y_true)==1], preds[np.array(y_true)!=1]).statistic


def lr_card_build(lr,col_x,woe_df,suffix = "_woe$"):
    coef_df = pd.Series(lr.coef_[0], index=[re.sub(suffix,"",i) for i in col_x]).loc[lambda x: x != 0]
    card_df = {}
    card_df["intercept"] = pd.DataFrame({'variable': "intercept", 'bin': np.nan, 'points': lr.intercept_[0]},
                                        index=np.arange(1))
    for i in coef_df.index:
        card_df[i] = woe_df.loc[woe_df.variable == i, :].assign(points=lambda x: x['woe'] * coef_df[i])[
            ["variable", "bin", "points"]]
    card = pd.concat(card_df,ignore_index=True)
    return card


# no pdo
def scorecard_apply(dt, card, only_total_score=True):
    dt = dt.copy(deep=True)
    if isinstance(card,dict):
        card=pd.concat(card,ignore_index=True)
    xs = card.loc[card.variable!='intercept' , 'variable'].unique()
    print ("xs=",xs)
    dat=dt.loc[:,list(set(dt.columns)-set(xs))]
    for i in xs :
        cardx=card.loc[card["variable"]==i,:]
        dtx_points = card_apply(dt[[i]], cardx, i, woe_points="points")
        # print ("dtx_points",dtx_points)
        dat = pd.concat([dat, dtx_points], axis=1)
    card_basepoints=list(card.loc[card.variable == 'intercept', 'points'])[0]
    dat_score = dat[xs + '_points']
    dat_score["score"]=card_basepoints + dat_score.sum(axis=1)
    dat_score["score"] = dat_score["score"].apply(lambda x: 1/(1 + np.exp(x * -1)))
    if only_total_score:
        dat_score = dat_score[['score']]
    return dat_score


def ab(points0=600, odds0=1 / 60, pdo=50):
    # two hypothesis
    # points0 = a - b*log(odds0)
    # points0 - PDO = a - b*log(2*odds0)
    b = pdo / np.log(2)
    a = points0 + b * np.log(odds0)  # log(odds0/(1+odds0))
    return {'a': a, 'b': b}


def lr_card_build_pdo(lr,woe_df, col_x,suffix = "_woe$", points0=600, odds0=1 / 19, pdo=50):
    '''
    Creating a Scorecard
    ------model

    Params
    ------
    bins: Binning information generated from `woebin` function.
    model: A LogisticRegression model object.
    points0: Target points, default 600.
    odds0: Target odds, default 1/19. Odds = p/(1-p).
    pdo: Points to Double the Odds, default 50.
    basepoints_eq0: Logical, default is FALSE. If it is TRUE, the
      basepoints will equally distribute to each variable.

    Returns
    ------
    DataFrame
        scorecard dataframe
    '''

    # coefficients
    aabb = ab(points0, odds0, pdo)
    a, b = aabb.values()
    print ("a,b=",a,b)
    # odds = pred/(1-pred); score = a - b*log(odds)

    # bins # if (is.list(bins)) rbindlist(bins)
    if isinstance(woe_df, dict):
        woe_df = pd.concat(woe_df, ignore_index=True)
    xs = [re.sub(suffix, '', i) for i in col_x]
    print ("xs=",xs)
    # coefficients
    coef_df = pd.Series(lr.coef_[0], index=np.array(xs)).loc[lambda x: x != 0]  # .reset_index(drop=True)

    print ("coef_df=",coef_df)
    # scorecard
    len_x = len(coef_df)
    basepoints = a - b * lr.intercept_[0]
    card = {}

    card['basepoints'] = pd.DataFrame({'variable': "basepoints", 'bin': np.nan, 'points': round(basepoints)},
                                      index=np.arange(1))
#        print ("card=",card)
    for i in coef_df.index:
        card[i] = woe_df.loc[woe_df['variable'] == i, ['variable', 'bin', 'woe']] \
            .assign(points=lambda x: round(-b * x['woe'] * coef_df[i])) \
            [["variable", "bin", "points"]]
    card = pd.concat(card,ignore_index=True)
    return card


def card_apply(dtx, binx, x_i, woe_points):
    '''
    Transform original values into woe or porints for one variable.

    Params
    ------

    Returns
    ------

    '''
    """
    pd.DataFrame(df["var"].str.split("%.%").tolist(),index=df["var"]).stack().reset_index()
    bbb = woe_dic["degree"].copy(deep=True)
    bbb.ix[bbb.bin == "6.无学历", "bin"] = "6.无学历%,%9.无文凭"
    ccc = pd.DataFrame(bbb['bin'].str.split('%,%').tolist(), index=bbb['bin']).stack().reset_index().drop('level_1',axis=1)
    pd.merge(ccc,bbb[['bin', 'woe']],how='left', on='bin').rename(columns={0: 'V1', "woe": 'V2'})
    """
    # print (binx)
    binx = pd.merge(
        pd.DataFrame(binx['bin'].str.split('%,%').tolist(), index=binx['bin']) \
            .stack().reset_index().drop('level_1', axis=1),
        binx[['bin', woe_points]],
        how='left', on='bin'
    ).rename(columns={0: 'V1', woe_points: 'V2'})

    # dtx
    ## cut numeric variable
    if is_numeric_dtype(dtx[x_i]):
#        binx_sv = binx.loc[lambda x: [not bool(re.search(r'\[', str(i))) for i in x.V1]]
        binx = binx.loc[lambda x: [bool(re.search(r'\[', str(i))) for i in x.V1]]
        # create bin column
        breaks_binx = np.unique(list(map(float, ['-inf'] + [re.match(r'.*\[(.*),.+\).*', str(i)).group(1) for i in
                                                                  binx['bin']] + ['inf'])))

        labels = ['[{},{})'.format(breaks_binx[i], breaks_binx[i + 1]) for i in
                  range(len(breaks_binx) - 1)]

        dtx = dtx.assign(xi_bin=lambda x: pd.cut(x[x_i], breaks_binx, right=False, labels=labels))
        dtx = dtx.astype(str)
        dtx = dtx[['xi_bin']].rename(columns={'xi_bin': x_i})

    # print (dtx,dtx.dtypes)
    dtx = dtx.fillna('missing').assign(rowid=dtx.index)
    binx.columns = ['bin', x_i, '_'.join([x_i, woe_points])]

    # merge
    dtx_suffix = pd.merge(dtx, binx, how='left', on=x_i).sort_values('rowid') \
        .set_index(dtx.index)[['_'.join([x_i, woe_points])]]
    # print ("dtx_suffix=",dtx_suffix,dtx)
    return dtx_suffix


def scorecard_pdo_apply(dt, card, only_total_score=True):
    '''
    Score Transformation
    ------
    `scorecard_ply` calculates credit score using the results from `scorecard`.

    Params
    ------
    dt: Original data
    card: Scorecard generated from `scorecard`.
    only_total_score: Logical, default is TRUE. If it is TRUE, then
      the output includes only total credit score; Otherwise, if it
      is FALSE, the output includes both total and each variable's
      credit score.
    print_step: A non-negative integer. Default is 1. If print_step>0,
      print variable names by each print_step-th iteration. If
      print_step=0, no message is print.

    Return
    ------
    DataFrame
        Credit score
    '''

    dt = dt.copy(deep=True)
    if isinstance(card, dict):
        card = pd.concat(card, ignore_index=True)
    # x variables
    xs = card.loc[card.variable != 'basepoints', 'variable'].unique()
    # length of x variables
    xs_len = len(xs)
    # initial datasets
    dat = dt.loc[:, list(set(dt.columns) - set(xs))]
    # loop on x variables
    for i in np.arange(xs_len):
        x_i = xs[i]
        # print xs
        # print(('{:' + str(len(str(xs_len))) + '.0f}/{} {}').format(i, xs_len, x_i))

        cardx = card.loc[card['variable'] == x_i]
        dtx = dt[[x_i]]
        # score transformation
        dtx_points = card_apply(dtx, cardx, x_i, woe_points="points")
        dat = pd.concat([dat, dtx_points], axis=1)
        # print ("dat=",dat)

    # set basepoints
    card_basepoints = list(card.loc[card['variable'] == 'basepoints', 'points'])[0] if 'basepoints' in card['variable'].unique() else 0
    # print ("card_basepoints",card_basepoints)
    # total score
    dat_score = dat[xs + '_points']
    dat_score.loc[:, 'score'] = card_basepoints + dat_score.sum(axis=1)
    # print ("dat_score",dat_score)
    # dat_score = dat_score.assign(score=lambda x: card_basepoints + dat_score.sum(axis=1))
    # return
    if only_total_score: dat_score = dat_score[['score']]
    return dat_score


def lr_feature_selection(dt,col_x,y ,direction = 'both',p_enter = 0.01, p_remove = 0.01, p_value_enter = 0.2,):
    """stepwise to select features

    Args:
        frame (DataFrame): dataframe that will be use to select
        target (str): target name in frame
        estimator (str): model to use for stats
        direction (str): direction of stepwise, support 'forward', 'backward' and 'both', suggest 'both'
        criterion (str): criterion to statistic model, support 'aic', 'bic'
        p_enter (float): threshold that will be used in 'forward' and 'both' to keep features
        p_remove (float): threshold that will be used in 'backward' to remove features
        intercept (bool): if have intercept
        p_value_enter (float): threshold that will be used in 'both' to remove features
        max_iter (int): maximum number of iterate
        return_drop (bool): if need to return features' name who has been dropped
        exclude (array-like): list of feature names that will not be dropped

    Returns:
        DataFrame: selected dataframe
        array: list of feature names that has been dropped
    """

    drop_list = []
    remaining = col_x[:]

    selected = []

    lr = LogisticRegression()

    order = -1 #if criterion in ['aic', 'bic'] else 1

    best_score = -np.inf * order

    iter = -1
    while remaining:
        iter += 1
        # if max_iter and iter > max_iter:
        #     break

        l = len(remaining)
        test_score = np.zeros(l)
        test_res = np.empty(l, dtype = np.object)

        if direction == 'backward':
            for i in range(l):
                test_res[i] = lr_metrics(
                    dt[ remaining[:i] + remaining[i+1:] ],
                    dt[y],
                    lr
                )
                test_score[i] = test_res[i]['criterion']

            curr_ix = np.argmax(test_score * order)
            curr_score = test_score[curr_ix]

            if (curr_score - best_score) * order < p_remove:
                break

            name = remaining.pop(curr_ix)
            drop_list.append(name)

            best_score = curr_score

        # forward and both
        else:
            for i in range(l):
                test_res[i] = lr_metrics(
                    dt[ selected + [remaining[i]] ],
                    dt[y],
                    lr
                )
                test_score[i] = test_res[i]['criterion']

            curr_ix = np.argmax(test_score * order)
            curr_score = test_score[curr_ix]

            name = remaining.pop(curr_ix)
            if (curr_score - best_score) * order < p_enter:
                drop_list.append(name)

                # early stop
                if selected:
                    drop_list += remaining
                    break

                continue

            selected.append(name)
            best_score = curr_score

            if direction == 'both':
                p_values = test_res[curr_ix]['p_value']
                drop_names = p_values[p_values > p_value_enter].index

                for name in drop_names:
                    selected.remove(name)
                    drop_list.append(name)

    # r = dt.drop(columns = drop_list)

    # res = (r,)
    # if return_drop:
    #     res += (drop_list,)

    return selected,drop_list


def t_value(pre, y, X, coef):
    n, k = X.shape
    mse = sum((y - pre) ** 2) / float(n - k)
    nx = np.dot(X.T, X)

    if np.linalg.det(nx) == 0:
        return np.nan

    std_e = np.sqrt(mse * (np.linalg.inv(nx).diagonal()))
    return coef / std_e


def p_value(t, n):
    return stats.t.sf(np.abs(t), n - 1) * 2


def SSE(y_pred, y):
    return np.sum((y_pred - y) ** 2)


def MSE(y_pred, y):
    return np.mean((y_pred - y) ** 2)


def AIC(y_pred, y, k, llf=None):
    if llf is None:
        llf = np.log(SSE(y_pred, y))

    return 2 * k - 2 * llf


def loglikelihood(pre, y, k):
    n = len(y)
    mse = MSE(pre, y)
    return (-n / 2) * np.log(2 * np.pi * mse * np.e)


def get_criterion( pre, y, k):
        llf = loglikelihood(pre, y, k)
        return AIC(pre, y, k, llf = llf)


def lr_metrics(X, y, model):
    """
    """
    X = X.copy()

    if isinstance(X, pd.Series):
        X = X.to_frame()

    model.fit(X, y)

    if hasattr(model, 'predict_proba'):
        pre = model.predict_proba(X)[:, 1]
    else:
        pre = model.predict(X)

    coef = model.coef_.reshape(-1)

    if model.intercept_ is not None:
        coef = np.append(coef, model.intercept_)
        X['intercept'] = np.ones(X.shape[0])

    n, k = X.shape

    t_v = t_value(pre, y, X, coef)
    p_v = p_value(t_v, n)
    c = get_criterion(pre, y, k)

    return {
        't_value': pd.Series(t_v, index=X.columns),
        'p_value': pd.Series(p_v, index=X.columns),
        'criterion': c
    }


def _check_boosting(model):
    """Check if the estimator is a LGBModel or XGBModel.

    Returns
    -------
    Model type in string format.
    """

    estimator_type = str(type(model)).lower()

    boost_type = ('LGB' if 'lightgbm' in estimator_type else '') + \
                 ('XGB' if 'xgboost' in estimator_type else '')

    if len(boost_type) != 3:
        raise ValueError("Pass a LGBModel or XGBModel.")

    return boost_type


def _check_param(values):
    """Check the parameter boundaries passed in dict values.

    Returns
    -------
    list of checked parameters.
    """

    if isinstance(values, (list, tuple, np.ndarray)):
        return list(set(values))
    elif 'scipy' in str(type(values)).lower():
        return values
    elif 'hyperopt' in str(type(values)).lower():
        return values
    else:
        return [values]


def _get_categorical_support(n_features, fit_params):
    """Obtain boolean mask for categorical features"""

    cat_support = np.zeros(n_features, dtype=np.bool)
    cat_ids = []

    msg = "When manually setting categarical features, " \
          "pass a 1D array-like of categorical columns indices " \
          "(specified as integers)."

    if 'categorical_feature' in fit_params:  # LGB
        cat_ids = fit_params['categorical_feature']
        if len(np.shape(cat_ids)) != 1:
            raise ValueError(msg)
        if not all([isinstance(c, int) for c in cat_ids]):
            raise ValueError(msg)

    cat_support[cat_ids] = True

    return cat_support


def _set_categorical_indexes(support, cat_support, _fit_params,
                             duplicate=False):
    """Map categorical features in each data repartition"""

    if cat_support.any():

        n_features = support.sum()
        support_id = np.zeros_like(support, dtype='int32')
        support_id[support] = np.arange(n_features, dtype='int32')
        cat_feat = support_id[np.where(support & cat_support)[0]]
        # empty if support and cat_support are not alligned

        if duplicate:  # is Boruta
            cat_feat = cat_feat.tolist() + (n_features + cat_feat).tolist()
        else:
            cat_feat = cat_feat.tolist()

        _fit_params['categorical_feature'] = cat_feat

    return _fit_params


def _shap_importances(model, X):
    """Extract feature importances from fitted boosting models
    using TreeExplainer from shap.

    Returns
    -------
    array of feature importances.
    """

    explainer = TreeExplainer(
        model, feature_perturbation="tree_path_dependent")
    coefs = explainer.shap_values(X, check_additivity=False)

    if isinstance(coefs, list):
        coefs = list(map(lambda x: np.abs(x).mean(0), coefs))
        coefs = np.sum(coefs, axis=0)
    else:
        coefs = np.abs(coefs).mean(0)

    return coefs


def _feature_importances(model):
    """Extract feature importances from fitted boosting models.

    Returns
    -------
    array of feature importances.
    """

    if hasattr(model, 'feature_importances_'):  ## booster='gblinear' (xgb)
        coefs = model.feature_importances_
    else:
        coefs = np.square(model.coef_).sum(axis=0)

    return coefs


def _write_log_file(filename, writelines, mode):
    f = open(filename, mode)
    f.writelines(writelines)
    f.close()


class tuning_llb():
    def __init__(self, train_set, valid_set, x_input, output_file='result.txt', use_x_cnt=50, if_plot=True,
                 max_iters=100, mode='ks_list', init_kwargs=None):
        self.train_set = train_set
        self.valid_set = valid_set
        self.x_input = x_input
        self.output_file = output_file
        self.use_x_cnt = use_x_cnt
        self.if_plot = if_plot
        #        self.iter_rate=iter_rate
        self.max_iters = max_iters
        self.mode = mode
        self.opt_trace = []
        self.init_kwargs = init_kwargs

    #    def __xgb_test(self, tmp_params, tmp_input,feval=None):
    def __xgb_test(self, tmp_params, tmp_input, **kwargs):
        clf = xgb.XGBClassifier(n_estimators=200,
                                max_depth=tmp_params[0],
                                subsample=tmp_params[1],
                                min_child_weight=tmp_params[2],
                                base_score=tmp_params[3],
                                reg_lambda=tmp_params[4],
                                learning_rate=tmp_params[5],
                                colsample_bytree=tmp_params[6],
                                reg_alpha=tmp_params[7],
                                nthread=8,
                                random_state=tmp_params[8],
                                missing=self.init_kwargs.get('missing'))

        if "eval_metric" in kwargs.keys():
            if not callable(kwargs['eval_metric']):
                kwargs['eval_metric'] = ks_score
        else:
            kwargs['eval_metric'] = ks_score
        # print ("__xgb_test kwargs=",kwargs)
        clf.fit(self.train_set[0][tmp_input].values
                , self.train_set[1].values
                #                ,verbose=True
                #                ,early_stopping_rounds=30
                #                ,eval_metric=feval
                , eval_set=[(k[0][tmp_input].values, k[1].values) for k in self.valid_set]
                , **kwargs)
        ks_t = [-clf.evals_result()['validation_' + str(len_eval)]['ks'][clf.best_iteration] for len_eval in
                range(self.valid_len)]
        #        tmpre={'params':tmp_params,'result':[clf.best_iteration]+ks_t,'x':','.join(sorted(tmp_input))}
        tmpre = {'params': tmp_params, 'result': [clf.best_iteration] + ks_t, 'x': [item for item in tmp_input]}

        fea_imp = pd.Series(clf.feature_importances_, index=tmp_input)
        print("clf.best_score", clf.best_score)
        return ks_t, tmpre, fea_imp

    def __imp_iter(self, x):
        if self.mode == 'ks_list':
            f = lambda x: sum(x) / len(x) if len(x) > 0 else 0.5
            return f(x)
        else:
            f = lambda a, b: 1 if len(a) == 0 else 1.1 if a[-1] > np.percentile(b, 30) else 0.9 if a[
                                                                                                       -1] < np.percentile(
                b, 30) else 1
            return f(x, self.ks_list)

    #    def start(self,feval=None,verbose=True,early_stopping_rounds=30):
    def start(self, **kwargs):
        print('init.............................')

        self.valid_len = len(self.valid_set)
        f = open(self.output_file, 'w')
        f.writelines(
            'params|best_ntree|' + str('|'.join(['ks_valid_' + str(i) for i in range(self.valid_len)])) + '|x_list\n')
        f.close()
        ax = []
        if self.if_plot:
            import matplotlib.pyplot as plt
            c_set = C_SET

            plt.scatter(0, 0)
            plt.show()
            plt.ion()
            k = 0
            for i in range(self.valid_len):
                ax.append([])
        else:
            for i in range(self.valid_len):
                ax.append([])

        k = 0
        params = [[2, 3, 4], [0.7], [20, 30, 10], [0.5, 0.7, 0.6, 0.4], [1, 5, 10, 15], [0.1, 0.08, 0.12],
                  [0.5, 0.7, 0.9], [1, 10], [i * 8 for i in range(1000)]]

        self.x_imp = pd.DataFrame(1, index=self.x_input, columns=['imp'])
        self.x_imp['ks_list'] = pd.Series([[] for i in range(len(self.x_input))], index=self.x_input)
        self.ks_list = []
        best_result = 0.0
        best_param = {}
        while k <= self.max_iters:
            k = k + 1
            self.ks_list.sort(reverse=True)

            if k <= 10:
                self.tmp_input = random.sample(self.x_input, self.use_x_cnt)
            else:
                if self.mode == 'ks_list':
                    tmp_x_imp = (np.random.rand(len(self.x_imp)) * self.x_imp.imp).sort_values(ascending=False)
                else:
                    tmp_x_imp = (np.random.rand(len(self.x_imp)) * self.x_imp.imp).sort_values(ascending=False)

                self.tmp_input = list((tmp_x_imp[:self.use_x_cnt].index))

                print(tmp_x_imp.head(5))

            tmp_params = [random.sample(params_i, 1)[0] for params_i in params]

            ks_t, tmpre, fea_imp = self.__xgb_test(tmp_params, self.tmp_input, **kwargs)
            self.opt_trace.append(tmpre)

            print(k, "tmpre['result']=", tmpre['result'])
            #            if tmpre['result'][0]==0:
            #                k=k-1
            #                continue
            self.ks_list.append(min(ks_t))
            print("params:" + str(tmp_params))

            for i in range(self.valid_len):
                ax[i].append(tmpre['result'][i + 1])
            for i in self.tmp_input:
                if self.mode == 'ks_list':
                    self.x_imp.loc[i, 'ks_list'].append((fea_imp[i] + 0.001) * min(ks_t))
                else:
                    self.x_imp.loc[i, 'ks_list'].append(min(ks_t))

            if self.mode == 'ks_list':
                self.x_imp.imp = self.x_imp.ks_list.apply(self.__imp_iter).sort_values(ascending=False)
            else:
                self.x_imp.imp.loc[self.tmp_input] = self.x_imp.imp.loc[self.tmp_input] * self.x_imp.ks_list.loc[
                    self.tmp_input].apply(self.__imp_iter)

            if best_result < sum(tmpre['result'][1:]):
                best_result = sum(tmpre['result'][1:])
                best_param = tmpre
            print('ks:' + str(tmpre['result']))
            f = open(self.output_file, 'a')
            f.writelines(str(tmpre['params']) + '|' + '|'.join([str(round(i, 4)) for i in tmpre['result']]) + '|' + str(
                self.tmp_input) + '\n')
            f.close()
            if self.if_plot:
                f.close()
                plt.cla()
                for i in range(self.valid_len):
                    plt.scatter(range(k), ax[i], c=c_set[i], label='valid_' + str(i))

                plt.legend(loc='upper right')
                plt.show()
                plt.pause(0.2)
        return best_result, best_param


class HypOpt():
    """全变量调参

    Parameters
    ----------
    train_set : list
        训练样本 eg:[train_set_x1 , train_set_y1]
    valid_set : list
        测试样本 eg: [(valid_set_x1 , valid_set_y1), (valid_set_x2 , valid_set_y2),...]
    space:dict
        参数空间，字典格式，eg:
        {'n_estimators':[200],
         "max_depth": [2,3,4],
         "base_score": [0.4,0.5,0.6,0.7],
         "reg_lambda": [1,5,10,15],
         "min_child_weight":[10,20,30],
         'learning_rate':  [0.1,0.08,0.12],
         'colsample_bytree':[0.5,0.7,0.9],
         'subsample': [0.7],#
         'reg_alpha': [1,10],
         'random_state':[i*8 for i in range(1000)],
         'scale_pos_weight':[1]
        }
    col_x:list
        输入x变量列表
    output_file:str
        模型结果输出列表文件
    if_plot:bool
        是否画图，默认True
    max_iters:int
        迭代次数，默认100
    missing:None
        xgboost缺失值参数
    verbose:bool
        是否输出细节，默认False
    early_stopping_rounds:int
        早停，默认30
    eval_metric:None or Callable
        调参函数，默认ks

    """

    def __init__(self, train_set, valid_set,
                 space, col_x, output_file='result.txt',
                 if_plot=True, max_iters=100, missing=None,
                 verbose=False, early_stopping_rounds=30,
                 eval_metric=None,
                 objective='binary:logistic',
                 init_kwargs=None,
                 **kwargs):
        self.train_set = train_set
        self.valid_set = valid_set
        self.space = space
        self.output_file = output_file
        self.if_plot = if_plot
        self.max_iters = max_iters
        #        self.mode=mode
        self.missing = missing
        self.k = 0
        self.col_x = col_x
        self.hp_space = {i: hp.choice(i, self.space[i]) for i in list(self.space.keys())}
        self.verbose = verbose
        self.early_stopping_rounds = early_stopping_rounds
        # if eval_metric is None or not callable(eval_metric):
        if eval_metric is None:
            self.eval_metric = ks_score
        else:
            self.eval_metric = eval_metric
        self.opt_trace = []
        self.objective = objective
        self.init_kwargs = init_kwargs
        print("objective=", self.objective)

    def xgb_factory(self, argsDict):
        #        global train_set,eval_set
        self.k += 1
        params = {'nthread': -1,  # 进程数
                  'n_estimators': argsDict.get('n_estimators'),
                  'max_depth': argsDict.get('max_depth'),  # 最大深度
                  'learning_rate': argsDict.get('learning_rate'),  # 学习率
                  'subsample': argsDict.get('subsample'),  # 采样数
                  'min_child_weight': argsDict.get('min_child_weight'),  # 终点节点最小样本占比的和
                  'base_score': argsDict.get('base_score'),
                  'objective': self.objective,
                  #                  'silent': 0,  # 是否显示
                  #                  'gamma': 0,  # 是否后剪枝
                  'colsample_bytree': argsDict.get('colsample_bytree'),  # 样本列采样
                  'reg_alpha': argsDict.get('reg_alpha'),  # L1 正则化
                  'reg_lambda': argsDict.get('reg_lambda'),  # L2 正则化
                  'scale_pos_weight': argsDict.get('scale_pos_weight'),  # 取值>0时,在数据不平衡时有助于收敛
                  'random_state': argsDict.get('random_state'),  # 随机种子
                  'missing': self.missing,  # 填充缺失值
                  }

        #             params = {'nthread': -1,  # 进程数
        #           'n_estimators':argsDict['n_estimators'],
        #           'max_depth': argsDict['max_depth'],  # 最大深度
        #           'learning_rate': argsDict['learning_rate'],  # 学习率
        #           'subsample': argsDict['subsample'],  # 采样数
        #           'min_child_weight': argsDict['min_child_weight'],  # 终点节点最小样本占比的和
        #           'base_score': argsDict['base_score'] ,
        #           'objective': self.objective,
        # #                  'silent': 0,  # 是否显示
        # #                  'gamma': 0,  # 是否后剪枝
        #           'colsample_bytree': argsDict['colsample_bytree'] ,  # 样本列采样
        #           'reg_alpha': argsDict['reg_alpha'] ,   # L1 正则化
        #           'reg_lambda': argsDict['reg_lambda']  ,  # L2 正则化
        #           'scale_pos_weight':  argsDict.get('scale_pos_weight') ,  # 取值>0时,在数据不平衡时有助于收敛
        #           'random_state':  argsDict['random_state'] ,  # 随机种子
        #           'missing': self.missing,  # 填充缺失值
        #           }
        print("params=", params, "self.fit_kw=", self.fit_kw.keys())
        gbm = self._fit(params, **self.fit_kw)
        #        print ("gbm.best_score=",gbm.best_score,gbm.evals_result(),gbm.best_ntree_limit)
        metric = [gbm.evals_result()['validation_' + str(len_eval)]['ks'][gbm.best_iteration] for len_eval in
                  range(len(self.valid_set))]

        tmpre = {'params': params, 'result': [gbm.best_iteration] + [i * -1 for i in metric]}

        self.opt_trace.append(tmpre)
        self.__write_log_file(tmpre)

        if self.if_plot:
            self.__plot(tmpre)

        print(metric)
        return max(metric)

    def _fit(self, params, **kwargs):
        params['objective'] = self.objective
        params.update(self.init_kwargs)
        if self.objective[0:3] != 'reg':
            gbm = xgb.XGBClassifier(**params)
        else:
            gbm = xgb.XGBRegressor(**params)
        gbm.fit(self.train_set[0], self.train_set[1]
                , **kwargs)
        return gbm

    def __create_plot(self):
        import matplotlib.pyplot as plt
        self.c_set = C_SET
        plt.scatter(0, 0)
        plt.show()
        plt.ion()
        self.ax = []
        for i in range(self.valid_len):
            self.ax.append([])

    #        print ("cre ax",self.ax)

    def __plot(self, tmpre):
        for i in range(self.valid_len):
            self.ax[i].append(tmpre['result'][i + 1])
        #        print ("plot ax",self.ax)
        plt.cla()
        for i in range(self.valid_len):
            plt.scatter(range(self.k), self.ax[i], c=self.c_set[i], label='valid_' + str(i))

        plt.legend(loc='upper right')
        plt.show()
        plt.pause(0.2)

    def __create_log_file(self):
        f = open(self.output_file, 'w')
        f.writelines(
            'params|best_ntree|' + str('|'.join(['ks_valid_' + str(i) for i in range(self.valid_len)])) + '|x_list\n')
        f.close()

    def __write_log_file(self, tmpre):
        f = open(self.output_file, 'a')
        f.writelines(str(tmpre['params']) + '|' + '|'.join([str(round(i, 4)) for i in tmpre['result']]) + '|' + str(
            self.col_x) + '\n')
        # self.opt_trace.append(str(tmpre['params'])+'|'+'|'.join([str(round(i,4)) for i in tmpre['result']])+'|'+str(self.col_x))
        f.close()

    def run(self, **kwargs):
        self.fit_kw = kwargs
        # algo = partial(tpe.suggest,n_startup_jobs=1)
        print("start!")
        self.k = 0
        self.valid_len = len(self.valid_set)
        self.__create_log_file()
        if self.if_plot:
            self.__create_plot()
        best = fmin(self.xgb_factory, self.hp_space, algo=tpe.suggest,
                    max_evals=self.max_iters)  # max_evals表示想要训练的最大模型数量，越大越容易找到最优解
        print(best)
        best_dic = {i: self.space[i][best[i]] for i in self.space.keys()}
        best_ks = self.xgb_factory(best_dic)

        gbm = self._fit(best_dic, **self.fit_kw)
        best_dic['n_estimators'] = gbm.best_ntree_limit
        return best_dic, best_ks


class HypOptLgbm():
    """全变量调参

    Parameters
    ----------
    train_set : list
        训练样本 eg:[train_set_x1 , train_set_y1]
    valid_set : list
        测试样本 eg: [(valid_set_x1 , valid_set_y1), (valid_set_x2 , valid_set_y2),...]
    space:dict
        参数空间，字典格式，eg:
        space={"n_estimators":[200000],
                    "max_depth": [3,4,5,6,7],
                    "num_leaves": [31,45,63],
                    "min_child_samples": [20,40,60,80,100,150],
                    "learning_rate":[0.1,0.05,0.03,0.01],
                    "colsample_bytree":[0.6,0.7,0.8,0.9,1],
                    'subsample': [0.6,0.7,0.8,0.9,1],
                    'reg_alpha': [0,0.18,0.35,0.75,1,2,3],
                    'reg_lambda': [0,0.18,0.35,0.75,1,2,3],
                    'min_split_gain':[0.0,0.2,0.4,0.6,0.8,1.0],
                    }
    col_x:list
        输入x变量列表
    output_file:str
        模型结果输出列表文件
    if_plot:bool
        是否画图，默认True
    max_iters:int
        迭代次数，默认100
    objective:str
        目标函数，默认binary
    metric:str
        评价函数，默认"None"
    use_missing:bool
        是否使用缺失，默认False

    """

    def __init__(self, train_set,
                 space, col_x, output_file='result.txt',
                 if_plot=True, max_iters=100, objective=None
                 , metric=None
                 , use_missing=False
                 , obj_type='reg'
                 , init_kwargs=None
                 , metric_mode="min"
                 , **kwargs):
        self.train_set = train_set
        self.valid_set = kwargs.get('eval_set')
        self.space = space
        self.output_file = output_file
        self.if_plot = if_plot
        self.max_iters = max_iters
        #        self.mode=mode
        self.k = 0
        self.col_x = col_x
        self.hp_space = {i: hp.choice(i, self.space[i]) for i in list(self.space.keys())}
        # self.verbose=verbose
        # self.early_stopping_rounds=early_stopping_rounds
        # if eval_metric is None or not callable(eval_metric):
        #     self.eval_metric=ks_score
        # else:
        # self.eval_metric=eval_metric
        self.opt_trace = []
        self.metric = metric
        self.objective = objective
        self.use_missing = use_missing
        self.obj_type = obj_type
        self.init_kwargs = init_kwargs
        self.metric_mode = metric_mode
        print("objective=", self.objective)
        print("metric=", self.metric)

    def lgb_factory(self, argsDict):
        #        global train_set,eval_set
        self.k += 1
        print("-" * 20, self.k, "-" * 20)
        params = { \
            'n_estimators': argsDict.get('n_estimators'),
            'max_depth': argsDict.get('max_depth'),  # 最大深度
            'num_leaves': argsDict.get('num_leaves'),
            'min_child_samples': argsDict.get('min_child_samples'),
            'learning_rate': argsDict.get('learning_rate'),  # 学习率
            'reg_alpha': argsDict.get('reg_alpha'),
            'reg_lambda': argsDict.get('reg_lambda'),
            'subsample': argsDict.get('subsample'),  # 采样数
            'colsample_bytree': argsDict.get('colsample_bytree'),  # 样本列采样
            # 'min_data_in_leaf': argsDict.get('min_data_in_leaf'),
            # 'feature_fraction': argsDict.get('feature_fraction'),
            # 'bagging_fraction': argsDict.get('bagging_fraction') ,
            'min_split_gain': argsDict.get('min_split_gain'),
            'subsample_freq': argsDict.get('subsample_freq'),
            'random_state': argsDict.get('random_state'),  # 随机种子
            # 'objective': self.objective,
            # 'metric': self.metric,
            # 'use_missing': self.use_missing,
        }
        # print ("params:",params)
        # print ("params=",params,"self.fit_kw=",self.fit_kw)
        # print ('params====',params)
        gbm = self._fit(params, **self.fit_kw)

        # print ("gbm.evals_result_=",gbm.evals_result_.keys())
        # print ("gbm.evals_result_valid_0=",gbm.evals_result_['valid_0'],gbm.best_iteration_,len(gbm.evals_result_['valid_0']['l1']))
        # print ("gbm.evals_result_valid_0_l1=",gbm.evals_result_['valid_0']['l1'][gbm.best_iteration_-1])
        # print("gbm.evals_result_",gbm.evals_result_.keys(),type(gbm.evals_result_))
        metric = []
        print("gbm.best_score_=", gbm.best_score_)
        for x, y in gbm.best_score_.items():
            for z in y.values():
                metric.append(round(z, 6))
        # metric=[gbm.evals_result_['valid_'+str(len_eval)]['l1'][gbm.best_iteration_-1] for len_eval in range(len(self.valid_set))]
        tmpre = {'params': params, 'result': [gbm.best_iteration_] + [i * -1 for i in metric]}

        self.opt_trace.append(tmpre)
        self.__write_log_file(tmpre)

        if self.if_plot:
            self.__plot(tmpre)

        print("metric=", metric)
        if self.metric_mode == 'min':
            return max(metric)
        else:
            return -min(metric)

    def _fit(self, params, **kwargs):
        params['objective'] = self.objective
        params['metric'] = self.metric
        params['use_missing'] = self.use_missing
        params.update(self.init_kwargs)
        print("params", params)
        if self.obj_type == 'clf':
            gbm = lgb.LGBMClassifier(**params)
        else:
            gbm = lgb.LGBMRegressor(**params)
        # print ("_fit kwargs=",kwargs.keys(),kwargs['sample_weight'].mean())
        gbm.fit(self.train_set[0], self.train_set[1], **kwargs)
        return gbm

    def __create_plot(self):
        import matplotlib.pyplot as plt
        self.c_set = C_SET
        plt.scatter(0, 0)
        plt.show()
        plt.ion()
        self.ax = []
        for i in range(self.valid_len):
            self.ax.append([])

    #        print ("cre ax",self.ax)

    def __plot(self, tmpre):
        for i in range(self.valid_len):
            self.ax[i].append(tmpre['result'][i + 1])
        #        print ("plot ax",self.ax)
        plt.cla()
        for i in range(self.valid_len):
            plt.scatter(range(self.k), self.ax[i], c=self.c_set[i], label='valid_' + str(i))

        plt.legend(loc='upper right')
        plt.show()
        plt.pause(0.2)

    def __create_log_file(self):
        f = open(self.output_file, 'w')
        f.writelines(
            'params|best_ntree|' + str('|'.join(['ks_valid_' + str(i) for i in range(self.valid_len)])) + '|x_list\n')
        f.close()

    def __write_log_file(self, tmpre):
        f = open(self.output_file, 'a')
        f.writelines(str(tmpre['params']) + '|' + '|'.join([str(round(i, 4)) for i in tmpre['result']]) + '|' + str(
            self.col_x) + '\n')
        # self.opt_trace.append(str(tmpre['params'])+'|'+'|'.join([str(round(i,4)) for i in tmpre['result']])+'|'+str(self.col_x))
        f.close()

    def run(self, **kwargs):
        # algo = partial(tpe.suggest,n_startup_jobs=1)
        self.fit_kw = kwargs
        print("start!")
        self.k = 0
        self.valid_len = len(self.valid_set)
        self.__create_log_file()
        if self.if_plot:
            self.__create_plot()
        best = fmin(self.lgb_factory, self.hp_space, algo=tpe.suggest,
                    max_evals=self.max_iters)  # max_evals表示想要训练的最大模型数量，越大越容易找到最优解

        best_dic = {i: self.space[i][best[i]] for i in self.space.keys()}

        best_ks = self.lgb_factory(best_dic)

        # print ("self.fit_kw=",self.fit_kw.keys())
        gbm = self._fit(best_dic, **self.fit_kw)
        print("best_dic=", best_dic, "bi=", gbm.best_iteration_)

        best_dic['n_estimators'] = gbm.best_iteration_
        return best_dic, best_ks


class AmFeatSelXgbClf(xgb.XGBClassifier):
    """含有固定特征选择的调参Estimater
    
    Parameters
    ----------
    x_input : list
        调参变量池
    output_file : str
        调参日志输出文件，默认'result.txt'
    use_x_cnt:int
        入模自变量数量，默认50
    if_plot:bool
        是否画图，默认True
    max_iters:int
        迭代次数，默认100

    Attributes
    ----------
    best_result :float
        最佳效果，返回所有调参测试集效果之和
    best_param :dict
        最佳参数以及效果字典
    features_select_list:list
        最终入模特征
    opt_trace:list
        保存的是模型每一轮的调参日志，每次调参过程以字典形式记录，'param'为参数，
        result第一个值为模型轮数，后面的值为调参测试集的效果，'x'代表的是入选的模型特征
        eg：{'params': [3, 0.7, 20, 0.7, 5, 0.12, 0.9, 1, 6528],
             'result': [89, 0.275087, 0.310883],
             'x': ['cust_age_x^_19.8809,22.7693)',
              'device_score_ppx^_0.2083,0.2359)',
              'shfw_bj_tt_usetime_4^_-inf,-98.999)',
              'td_3m_financing_cnt',
              'kx_location_score^_-98.999,469.0)'
              ...}
    
    """
    def __init__(self,x_input,output_file='result.txt', 
                 use_x_cnt=50, if_plot=True,
                 max_iters=100, mode='ks_list',
                 **kwargs):

        self.x_input=x_input
        self.output_file=output_file
        self.use_x_cnt=use_x_cnt
        self.if_plot=if_plot
        self.max_iters=max_iters       
        self.mode=mode
        self.opt_trace=[]
        self.init_kwargs=kwargs

        # super(AmFeatSelXgbClf, self).__init__(max_depth, learning_rate,
        #          n_estimators, silent,
        #          objective,nthread, gamma, min_child_weight,
        #          max_delta_step, subsample, 
        #          colsample_bytree, colsample_bylevel,
        #          reg_alpha, reg_lambda, scale_pos_weight,
        #          base_score, random_state, missing)
        
        super(AmFeatSelXgbClf, self).__init__(**kwargs)
#        print ("missing",self.missing)
#        print ("get_xgb_params",self.get_xgb_params)
        
    def fit(self,data,y=None,sample_weight=None, eval_set=None, eval_metric=None,
            early_stopping_rounds=None, verbose=True,**kwargs):

        tl= tuning_llb([data,y], eval_set, self.x_input, self.output_file, 
                       self.use_x_cnt, self.if_plot,self.max_iters, self.mode,init_kwargs=self.init_kwargs)
        #print ("sample_weight_eval_set=",kwargs.keys())
        self.best_result,self.best_param=tl.start(eval_metric=eval_metric
                                                  ,verbose=verbose
                                                  ,early_stopping_rounds=early_stopping_rounds
                                                  ,sample_weight=sample_weight
                                                  ,sample_weight_eval_set=kwargs.get('sample_weight_eval_set'),
                                                  )
        
        self.n_estimators=self.best_param['result'][0]+1
        self.max_depth=self.best_param['params'][0]
        self.subsample=self.best_param['params'][1]
        self.min_child_weight=self.best_param['params'][2]
        self.base_score=self.best_param['params'][3]
        self.reg_lambda=self.best_param['params'][4]
        self.learning_rate=self.best_param['params'][5]
        self.colsample_bytree=self.best_param['params'][6]
        self.reg_alpha=self.best_param['params'][7]
        self.random_state=self.best_param['params'][8]
        self.features_select_list = self.best_param['x']
        self.opt_trace=tl.opt_trace
        
#        print ("features_select_list",self.features_select_list)
#        print ("missing3",self.missing)
#        print ("objective3",self.objective)
#        print ("get_xgb_params3",self.get_xgb_params)
        super(AmFeatSelXgbClf, self).fit(data[self.features_select_list],y
             ,eval_set=[(i[0][self.features_select_list],i[1]) for i in eval_set]
             ,verbose=verbose
             ,sample_weight=sample_weight
             ,eval_metric=eval_metric
             ,sample_weight_eval_set=kwargs.get('sample_weight_eval_set'))
        
        from scipy.stats import ks_2samp 

        preds=self.predict_proba(eval_set[0][0][self.features_select_list])[:,1]
        print ("score_ks_test",ks_2samp(preds[np.array(eval_set[0][1])==1],
                                        preds[np.array(eval_set[0][1])!=1]).statistic)
        
        # print(" self.feature_importances_",self.feature_importances_)
        return self


class AmAllFeatXgbClf(xgb.XGBClassifier):
    """全变量调参的调参Estimater
    
    Parameters
    ----------
    space : dict
        参数空间
        eg:space={"n_estimators":[200],
                 "max_depth": [2,3,4],
                 "base_score": [0.4,0.5,0.6,0.7],
                 "reg_lambda": [1,5,10,15],
                 "min_child_weight":[10,20,30],
                 'learning_rate':  [0.1,0.08,0.12],
                 'colsample_bytree':[0.5,0.7,0.9],
                 'subsample': [0.7],#
                 'reg_alpha': [1,10],
                 'random_state':[i*8 for i in range(1000)],
                 'scale_pos_weight':[1]
                 }
    col_x:list
        特征列表
    output_file : str
        调参日志输出文件，默认'result.txt'
    if_plot:bool
        是否画图，默认True
    max_iters:int
        迭代次数，默认100
    objective: str
        目标函数，默认'binary:logistic'

    Attributes
    ----------
    best_param :dict
        最佳参数
    best_result :float
        最佳模型效果，调参测试集中的最小值
    opt_trace:list
        保存的是模型每一轮的调参日志，字典形式记录，'param'为参数，
        result第一个值为模型轮数，后面的值为调参测试集的效果
        eg：{'params': {'nthread': -1,
             'n_estimators': 200,
             'max_depth': 3,
             'learning_rate': 0.08,
             'subsample': 0.7,
             'min_child_weight': 20,
             'base_score': 0.5,
             'objective': 'binary:logistic',
             'colsample_bytree': 0.7,
             'reg_alpha': 10,
             'reg_lambda': 10,
             'scale_pos_weight': 1,
             'random_state': 7240,
             'missing': None},
            'result': [67, 0.257119, 0.287578]}
    """
    def __init__(self,space,col_x,max_iters=100,output_file='result.txt',objective='binary:logistic',
                 if_plot=True,**kwargs):

        self.space=space
        self.col_x=col_x
        self.output_file=output_file
        self.if_plot=if_plot
        self.max_iters=max_iters
        self.init_kwargs=kwargs
        
        super(AmAllFeatXgbClf, self).__init__(objective=objective,**kwargs)
#        print ("missing",self.missing)
#        print ("get_xgb_params",self.get_xgb_params)
        
    def fit(self,data,y=None,**kwargs):

        eval_set=kwargs.get('eval_set')
        # verbose=kwargs.get('verbose',False)
        # early_stopping_rounds=kwargs.get('early_stopping_rounds')
        # eval_metric=kwargs.get('eval_metric','auc')
        ho=HypOpt(train_set=[data,y], valid_set=eval_set,
                 space=self.space,col_x=self.col_x,output_file=self.output_file,
                 if_plot=self.if_plot,max_iters=self.max_iters,missing=self.missing,
                 init_kwargs=self.init_kwargs,**kwargs)
        
        self.best_param,self.best_result=ho.run(**kwargs)
        self.best_result=abs(self.best_result)
        self.opt_trace=ho.opt_trace
        self.set_params(**self.best_param)
        
        kwargs.pop('early_stopping_rounds',None)
        super(AmAllFeatXgbClf, self).fit(data[self.col_x],y,**kwargs)
        
        from scipy.stats import ks_2samp 
        # preds=self.predict_proba(data[self.col_x])[:,1]
        # print ("score_ks_train",ks_2samp(preds[y==1], preds[y!=1]).statistic)

        preds=self.predict_proba(eval_set[0][0][self.col_x])[:,1]
        print ("score_ks_test",ks_2samp(preds[np.array(eval_set[0][1])==1],
                                        preds[np.array(eval_set[0][1])!=1]).statistic)
        
        # print(" self.feature_importances_",self.feature_importances_)
        return self


class AmAllFeatXgbReg(xgb.XGBRegressor):
    """全变量调参的调参Estimater
    
    Parameters
    ----------
    space : dict
        参数空间
        eg:space={"n_estimators":[200],
                 "max_depth": [2,3,4],
                 "base_score": [0.4,0.5,0.6,0.7],
                 "reg_lambda": [1,5,10,15],
                 "min_child_weight":[10,20,30],
                 'learning_rate':  [0.1,0.08,0.12],
                 'colsample_bytree':[0.5,0.7,0.9],
                 'subsample': [0.7],#
                 'reg_alpha': [1,10],
                 'random_state':[i*8 for i in range(1000)],
                 'scale_pos_weight':[1]
                 }
    col_x:list
        特征列表
    output_file : str
        调参日志输出文件，默认'result.txt'
    if_plot:bool
        是否画图，默认True
    max_iters:int
        迭代次数，默认100
    objective: str
        目标函数，默认'reg:squarederror'

    Attributes
    ----------
    best_param :dict
        最佳参数
    best_result :float
        最佳模型效果，调参测试集中的最小值
    opt_trace:list
        保存的是模型每一轮的调参日志，字典形式记录，'param'为参数，
        result第一个值为模型轮数，后面的值为调参测试集的效果
        eg：{'params': {'nthread': -1,
             'n_estimators': 200,
             'max_depth': 3,
             'learning_rate': 0.08,
             'subsample': 0.7,
             'min_child_weight': 20,
             'base_score': 0.5,
             'objective': 'binary:logistic',
             'colsample_bytree': 0.7,
             'reg_alpha': 10,
             'reg_lambda': 10,
             'scale_pos_weight': 1,
             'random_state': 7240,
             'missing': None},
            'result': [67, 0.257119, 0.287578]}
    """
    def __init__(self,space,col_x,output_file='result.txt',objective='reg:squarederror',
                 if_plot=True,max_iters=100,**kwargs):

        self.space=space
        self.col_x=col_x
        self.output_file=output_file
        self.if_plot=if_plot
        self.max_iters=max_iters
        self.init_kwargs=kwargs
        
        super(AmAllFeatXgbReg, self).__init__(objective=objective,**kwargs)
        
    def fit(self,data,y=None,**kwargs):

        valid_set=kwargs.get('eval_set')
        # verbose=kwargs.get('verbose',False)
        # early_stopping_rounds=kwargs.get('early_stopping_rounds')
        # eval_metric=kwargs.get('eval_metric','mae')
        ho=HypOpt(train_set=[data,y], valid_set=valid_set,
                 space=self.space,col_x=self.col_x,output_file=self.output_file,
                 if_plot=self.if_plot,max_iters=self.max_iters,missing=self.missing,
                 objective=self.objective,init_kwargs=self.init_kwargs,**kwargs)
        
        self.best_param,self.best_result=ho.run(**kwargs)
        self.best_result=abs(self.best_result)
        self.opt_trace=ho.opt_trace
        self.set_params(**self.best_param)
        
        kwargs.pop('early_stopping_rounds',None)
        super(AmAllFeatXgbReg, self).fit(data[self.col_x],y,**kwargs)
        
        return self


class AmAllFeatLgbReg(lgb.LGBMRegressor):
    """全变量回归模型的Lgbm Estimater
    
    Parameters
    ----------
    space : dict
        参数空间
        eg:space={"n_estimators":[200000],
                    "max_depth": [3,4,5,6,7],
                    "num_leaves": [31,45,63],
                    "min_child_samples": [20,40,60,80,100,150],
                    "learning_rate":[0.1,0.05,0.03,0.01],
                    "colsample_bytree":[0.6,0.7,0.8,0.9,1],
                    'subsample': [0.6,0.7,0.8,0.9,1],
                    'reg_alpha': [0,0.18,0.35,0.75,1,2,3],
                    'reg_lambda': [0,0.18,0.35,0.75,1,2,3],
                    'min_split_gain':[0.0,0.2,0.4,0.6,0.8,1.0],
                    }
    col_x:list
        特征列表
    output_file : str
        调参日志输出文件，默认'result.txt'
    if_plot:bool
        是否画图，默认True
    max_iters:int
        迭代次数，默认100
    objective:str
        目标函数，默认regression_l1
    metric:str
        评价函数，默认"None"
    use_missing:bool
        是否使用缺失，默认False
    metric_mode:str
        评价函数优化方向，"min"，代表评价函数往小值方向优化，"max"则相反，默认为'min'

    Attributes
    ----------
    best_param :dict
        最佳参数
    best_result :float
        最佳模型效果，调参测试集中的最小值
    opt_trace:list
        保存的是模型每一轮的调参日志，字典形式记录，'param'为参数
    """
    def __init__(self,space,col_x,output_file='result.txt',
                 if_plot=True,max_iters=100,
                            objective="regression_l1",
                            metric="None",
                            use_missing=False,
                            metric_mode="min",
                            **kwargs):

        self.space=space
        self.col_x=col_x
        self.output_file=output_file
        self.if_plot=if_plot
        self.max_iters=max_iters
        if isinstance(self, lgb.LGBMRegressor):
            self.obj_type = "reg"
        elif isinstance(self, lgb.LGBMClassifier):
            self.obj_type = "clf"
        else:
            raise ValueError("Unknown Model type.")
            
        super(AmAllFeatLgbReg, self).__init__(**kwargs)
        self.objective=objective
        self.metric=metric
        self.use_missing=use_missing
        self.init_kwargs=kwargs
        self.metric_mode=metric_mode
        
    def fit(self, data, y,**kwargs):
        
        valid_set=kwargs.get('eval_set')
        ho=HypOptLgbm(train_set=[data,y], valid_set=valid_set,
                 space=self.space,col_x=self.col_x,output_file=self.output_file,
                 if_plot=self.if_plot,max_iters=self.max_iters
                 ,objective=self.objective
                 ,metric=self.metric
                 ,use_missing=self.use_missing
                 ,obj_type=self.obj_type
                 ,init_kwargs=self.init_kwargs
                 ,metric_mode=self.metric_mode
                 ,**kwargs)
        
        self.best_param,self.best_result=ho.run(**kwargs)
        print ("-"*20)
        print ("self.best_param=",self.best_param,"self.best_result=",self.best_result)
        print ("-"*20)
        # print ("123",self.best_param,self.best_result)
        self.best_result=abs(self.best_result)
        self.opt_trace=ho.opt_trace
        self.set_params(**self.best_param)
        self.space=str(self.space)
        # print("kwargs",kwargs.keys())
        
        kwargs.pop('early_stopping_rounds',None)
        super(AmAllFeatLgbReg, self).fit(data[self.col_x],y,**kwargs)
        
        return self


class AmAllFeatLgbClf(lgb.LGBMClassifier):
    """全变量分类模型的调参Lgbm  Estimater
    
    Parameters
    ----------
    space : dict
        参数空间
        eg:space={"n_estimators":[200000],
                    "max_depth": [3,4,5,6,7],
                    "num_leaves": [31,45,63],
                    "min_child_samples": [20,40,60,80,100,150],
                    "learning_rate":[0.1,0.05,0.03,0.01],
                    "colsample_bytree":[0.6,0.7,0.8,0.9,1],
                    'subsample': [0.6,0.7,0.8,0.9,1],
                    'reg_alpha': [0,0.18,0.35,0.75,1,2,3],
                    'reg_lambda': [0,0.18,0.35,0.75,1,2,3],
                    'min_split_gain':[0.0,0.2,0.4,0.6,0.8,1.0],
                    }
    col_x:list
        特征列表
    output_file : str
        调参日志输出文件，默认'result.txt'
    if_plot:bool
        是否画图，默认True
    max_iters:int
        迭代次数，默认100
    objective:str
        目标函数，默认binary
    metric:str
        评价函数，默认"None"
    use_missing:bool
        是否使用缺失，默认False
    metric_mode:str
        评价函数优化方向，"min"，代表评价函数往小值方向优化，"max"则相反，默认为'min'

    Attributes
    ----------
    best_param :dict
        最佳参数
    best_result :float
        最佳模型效果，调参测试集中的最小值
    opt_trace:list
        保存的是模型每一轮的调参日志，字典形式记录
    """
    def __init__(self,space,col_x,output_file='result.txt',
                 if_plot=True,max_iters=100,
                            objective="binary",
                            metric="None",
                            use_missing=False,
                            metric_mode="min",
                            **kwargs):

        self.space=space
        self.col_x=col_x
        self.output_file=output_file
        self.if_plot=if_plot
        self.max_iters=max_iters
        if isinstance(self, lgb.LGBMRegressor):
            self.obj_type = "reg"
        elif isinstance(self, lgb.LGBMClassifier):
            self.obj_type = "clf"
        else:
            raise ValueError("Unknown Model type.")
            
        super(AmAllFeatLgbClf, self).__init__(**kwargs)
        self.objective=objective
        self.metric=metric
        self.use_missing=use_missing
        self.init_kwargs=kwargs
        self.metric_mode=metric_mode
        
    def fit(self, data, y,**kwargs):
        
        print ("self.objective=",self.objective)
        valid_set=kwargs.get('eval_set')
        ho=HypOptLgbm(train_set=[data,y], valid_set=valid_set,
                 space=self.space,col_x=self.col_x,output_file=self.output_file,
                 if_plot=self.if_plot,max_iters=self.max_iters
                 ,objective=self.objective
                 ,metric=self.metric
                 ,use_missing=self.use_missing
                 ,obj_type=self.obj_type
                 ,metric_mode=self.metric_mode
                 ,init_kwargs=self.init_kwargs,**kwargs)
        
        self.best_param,self.best_result=ho.run(**kwargs)
        print ("-"*20)
        print ("self.best_param=",self.best_param,"self.best_result=",self.best_result)
        print ("-"*20)
        # print ("123",self.best_param,self.best_result)
        self.best_result=abs(self.best_result)
        self.opt_trace=ho.opt_trace
        self.set_params(**self.best_param)
        self.space=str(self.space)
        # print("get",self.get_params)
        kwargs.pop('early_stopping_rounds',None)
        super(AmAllFeatLgbClf, self).fit(data[self.col_x],y,**kwargs)
        
        return self


class ParameterSampler(object):
    """Generator on parameters sampled from given distributions.
    If all parameters are presented as a list, sampling without replacement is
    performed. If at least one parameter is given as a scipy distribution,
    sampling with replacement is used. If all parameters are given as hyperopt
    distributions Tree of Parzen Estimators searching from hyperopt is computed.
    It is highly recommended to use continuous distributions for continuous
    parameters.

    Parameters
    ----------
    param_distributions : dict
        Dictionary with parameters names (`str`) as keys and distributions
        or lists of parameters to try. Distributions must provide a ``rvs``
        method for random sampling (such as those from scipy.stats.distributions)
        or be hyperopt distributions for bayesian searching.
        If a list is given, it is sampled uniformly.

    n_iter : integer, default=None
        Number of parameter configurations that are produced.

    random_state : int, default=None
        Pass an int for reproducible output across multiple
        function calls.

    Returns
    -------
    param_combi : list of dicts or dict of hyperopt distributions
        Parameter combinations.

    searching_type : str
        The searching algorithm used.
    """

    def __init__(self, param_distributions, n_iter=None, random_state=None):

        self.n_iter = n_iter
        self.random_state = random_state
        self.param_distributions = param_distributions

    def sample(self):
        """Generator parameter combinations from given distributions."""

        param_distributions = self.param_distributions.copy()

        is_grid = all(isinstance(p, list)
                      for p in param_distributions.values())
        is_random = all(isinstance(p, list) or 'scipy' in str(type(p)).lower()
                        for p in param_distributions.values())
        is_hyperopt = all('hyperopt' in str(type(p)).lower()
                          or (len(p) < 2 if isinstance(p, list) else False)
                          for p in param_distributions.values())

        if is_grid:
            param_combi = list(product(*param_distributions.values()))
            param_combi = [
                dict(zip(param_distributions.keys(), combi))
                for combi in param_combi
            ]
            return param_combi, 'grid'

        elif is_random:
            if self.n_iter is None:
                raise ValueError(
                    "n_iter must be an integer >0 when scipy parameter "
                    "distributions are provided. Get None."
                )

            seed = (random.randint(1, 100) if self.random_state is None
                    else self.random_state + 1)
            random.seed(seed)

            param_combi = []
            k = self.n_iter
            for i in range(self.n_iter):
                dist = param_distributions.copy()
                combi = []
                for j, v in enumerate(dist.values()):
                    if 'scipy' in str(type(v)).lower():
                        combi.append(v.rvs(random_state=seed * (k + j)))
                    else:
                        combi.append(v[random.randint(0, len(v) - 1)])
                    k += i + j
                param_combi.append(
                    dict(zip(param_distributions.keys(), combi))
                )
            np.random.mtrand._rand

            return param_combi, 'random'

        elif is_hyperopt:
            if self.n_iter is None:
                raise ValueError(
                    "n_iter must be an integer >0 when hyperopt "
                    "search spaces are provided. Get None."
                )
            param_distributions = {
                k: p[0] if isinstance(p, list) else p
                for k, p in param_distributions.items()
            }

            return param_distributions, 'hyperopt'

        else:
            raise ValueError(
                "Parameters not recognized. "
                "Pass lists, scipy distributions (also in conjunction "
                "with lists), or hyperopt search spaces."
            )


class _BoostSearch(BaseEstimator):
    """Base class for BoostSearch meta-estimator.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self):
        pass

    def _validate_param_grid(self, fit_params):
        """Private method to validate fitting parameters."""

        if not isinstance(self.param_grid, dict):
            raise ValueError("Pass param_grid in dict format.")
        self._param_grid = self.param_grid.copy()

        for p_k, p_v in self._param_grid.items():
            self._param_grid[p_k] = _check_param(p_v)

        if 'eval_set' not in fit_params:
            raise ValueError(
                "When tuning parameters, at least "
                "a evaluation set is required.")

        # self._eval_score = np.argmax if self.greater_is_better else np.argmin
        # self._score_sign = -1 if self.greater_is_better else 1

        rs = ParameterSampler(
            n_iter=self.n_iter,
            param_distributions=self._param_grid,
            random_state=self.sampling_seed
        )
        self._param_combi, self._tuning_type = rs.sample()
        self._trial_id = 1

        if self.verbose > 0:
            n_trials = self.n_iter if self._tuning_type is 'hyperopt' \
                else len(self._param_combi)
            print("\n{} trials detected for {}\n".format(
                n_trials, tuple(self.param_grid.keys())))

    def _fit(self, X, y, fit_params, params=None):
        """Private method to fit a single boosting model and extract results."""

        model = self._build_model(params)
        if isinstance(model, _BoostSelector):
            model.fit(X=X, y=y, **fit_params)
        else:
            with contextlib.redirect_stdout(io.StringIO()):
                model.fit(X=X, y=y, **fit_params)

        results = {'params': params, 'status': 'ok'}

        if isinstance(model, _BoostSelector):
            results['booster'] = model.estimator_
            results['model'] = model
        else:
            results['booster'] = model
            results['model'] = None

        if 'eval_set' not in fit_params:
            return results

        if self.boost_type_ == 'XGB':
            # w/ eval_set and w/ early_stopping_rounds
            if hasattr(results['booster'], 'best_score'):
                results['iterations'] = results['booster'].best_iteration
            # w/ eval_set and w/o early_stopping_rounds
            else:
                valid_id = list(results['booster'].evals_result_.keys())[-1]
                eval_metric = list(results['booster'].evals_result_[valid_id])[-1]
                results['iterations'] = \
                    len(results['booster'].evals_result_[valid_id][eval_metric])
        else:
            # w/ eval_set and w/ early_stopping_rounds
            if results['booster'].best_iteration_ is not None:
                results['iterations'] = results['booster'].best_iteration_
            # w/ eval_set and w/o early_stopping_rounds
            else:
                valid_id = list(results['booster'].evals_result_.keys())[-1]
                eval_metric = list(results['booster'].evals_result_[valid_id])[-1]
                results['iterations'] = \
                    len(results['booster'].evals_result_[valid_id][eval_metric])

        if self.boost_type_ == 'XGB':
            # w/ eval_set and w/ early_stopping_rounds
            if hasattr(results['booster'], 'best_score'):
                results['loss'] = results['booster'].best_score
            # w/ eval_set and w/o early_stopping_rounds
            else:
                valid_id = list(results['booster'].evals_result_.keys())[-1]
                eval_metric = list(results['booster'].evals_result_[valid_id])[-1]
                results['loss'] = \
                    results['booster'].evals_result_[valid_id][eval_metric][-1]
        else:
            valid_id = list(results['booster'].best_score_.keys())[-1]
            eval_metric = list(results['booster'].best_score_[valid_id])[-1]
            results['loss'] = results['booster'].best_score_[valid_id][eval_metric]

        if params is not None:
            if self.verbose > 0:
                msg = "trial: {} ### iterations: {} ### eval_score: {}".format(
                    str(self._trial_id).zfill(4),
                    str(results['iterations']).zfill(5),
                    round(results['loss'], 5)
                )
                print(msg)
            if self.output_file:
                _write_log_file(
                    filename=self.output_file,
                    writelines=str(results['loss']) + '|' + str(results['booster'].get_params()) + '\n',
                    mode='a',
                )

            self._trial_id += 1
            results['loss'] *= self._score_sign

        return results

    def fit(self, X, y, trials=None, **fit_params):
        """Fit the provided boosting algorithm while searching the best subset
        of features (according to the selected strategy) and choosing the best
        parameters configuration (if provided).

        It takes the same arguments available in the estimator fit.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The training input samples.

        y : array-like of shape (n_samples,)
            Target values.

        trials : hyperopt.Trials() object, default=None
            A hyperopt trials object, used to store intermediate results for all
            optimization runs. Effective (and required) only when hyperopt
            parameter searching is computed.

        **fit_params : Additional fitting arguments.

        Returns
        -------
        self : object
        """

        self.boost_type_ = _check_boosting(self.estimator)
        self._eval_score = np.argmax if self.greater_is_better else np.argmin
        self._score_sign = -1 if self.greater_is_better else 1
        if self.output_file:
            _write_log_file(
                filename=self.output_file,
                writelines='score|params|x_list\n',
                mode='w',
            )

        if self.param_grid is None:
            results = self._fit(X, y, fit_params)

            for v in vars(results['model']):
                if v.endswith("_") and not v.startswith("__"):
                    setattr(self, str(v), getattr(results['model'], str(v)))

        else:
            self._validate_param_grid(fit_params)

            if self._tuning_type == 'hyperopt':
                if trials is None:
                    trials = Trials()
                    # raise ValueError(
                    #     "trials must be not None when using hyperopt."
                    # )

                search = fmin(
                    fn=lambda p: self._fit(
                        params=p, X=X, y=y, fit_params=fit_params
                    ),
                    space=self._param_combi, algo=tpe.suggest,
                    max_evals=self.n_iter, trials=trials,
                    rstate=np.random.RandomState(self.sampling_seed),
                    show_progressbar=False, verbose=0
                )
                all_results = trials.results

            else:
                all_results = Parallel(
                    n_jobs=self.n_jobs, verbose=self.verbose * int(bool(self.n_jobs))
                )(delayed(self._fit)(X, y, fit_params, params)
                  for params in self._param_combi)

            # extract results from parallel loops
            self.trials_, self.iterations_, self.scores_, models = [], [], [], []
            for job_res in all_results:
                self.trials_.append(job_res['params'])
                self.iterations_.append(job_res['iterations'])
                self.scores_.append(self._score_sign * job_res['loss'])
                if isinstance(job_res['model'], _BoostSelector):
                    models.append(job_res['model'])
                else:
                    models.append(job_res['booster'])

            #debug
            # self.all_results = all_results
            # get the best
            id_best = self._eval_score(self.scores_)
            self.best_params_ = self.trials_[id_best]
            self.best_iter_ = self.iterations_[id_best]
            self.best_score_ = self.scores_[id_best]
            self.estimator_ = models[id_best]

            for v in vars(models[id_best]):
                if v.endswith("_") and not v.startswith("__"):
                    setattr(self, str(v), getattr(models[id_best], str(v)))

        return self

    def predict(self, X, **predict_params):
        """Predict X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.

        **predict_params : Additional predict arguments.

        Returns
        -------
        pred : ndarray of shape (n_samples,)
            The predicted values.
        """

        check_is_fitted(self)

        if hasattr(self, 'transform'):
            X = self.transform(X)

        return self.estimator_.predict(X, **predict_params)

    @if_delegate_has_method(delegate='estimator')
    def predict_proba(self, X, **predict_params):
        """Predict X probabilities.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.

        **predict_params : Additional predict arguments.

        Returns
        -------
        pred : ndarray of shape (n_samples, n_classes)
            The predicted values.
        """

        check_is_fitted(self)

        if hasattr(self, 'transform'):
            X = self.transform(X)

        return self.estimator_.predict_proba(X, **predict_params)

    def score(self, X, y, sample_weight=None):
        """Return the score on the given test data and labels.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test samples.

        y : array-like of shape (n_samples,)
            True values for X.

        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights.

        Returns
        -------
        score : float
            Accuracy for classification, R2 for regression.
        """

        check_is_fitted(self)

        if hasattr(self, 'transform'):
            X = self.transform(X)

        return self.estimator_.score(X, y, sample_weight=sample_weight)


class BoostSearch(_BoostSearch):
    """参数搜索器

    Parameters
    ----------
    estimator : LGBModel or XGBModel
        分类器.

    param_grid : dict, default=None
        参数空间，当为None时不搜索参数

    greater_is_better : bool, default=False
        评价函数优化方向

    n_iter : int, default=None
        参数搜索轮数，随机搜索或者hyperopt搜索下模式下生效.

    sampling_seed : int, default=None
        参数采样种子，随机搜索或者hyperopt搜索下模式下生效.

    n_jobs : int, default=None
        执行进程数

    verbose : int, default=1
        输出日志程度

    output_file : str, default=None
        param trace logfile

    Attributes
    ----------
    estimator_ : estimator
        最终选择分类器

    best_params_ : dict
        最佳参数

    trials_ : list
        hyperopt的trial对象

    best_score_ : float
        最佳评分结果

    scores_ : list
        评分历史

    best_iter_ : int
        最佳树轮数

    iterations_ : list
        模型轮数历史

    boost_type_ : str
        模型历史 (LGB or XGB).
    """

    def __init__(self,
                 estimator, *,
                 param_grid,
                 greater_is_better=False,
                 n_iter=None,
                 sampling_seed=None,
                 verbose=1,
                 n_jobs=None,
                 output_file=None):
        self.estimator = estimator
        self.param_grid = param_grid
        self.greater_is_better = greater_is_better
        self.n_iter = n_iter
        self.sampling_seed = sampling_seed
        self.verbose = verbose
        self.n_jobs = n_jobs
        self.output_file = output_file

    def _build_model(self, params):
        """Private method to build model."""

        model = clone(self.estimator)
        model.set_params(**params)

        return model


class _BoostSelector(BaseEstimator, TransformerMixin):
    """Base class for feature selection meta-estimator.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self):
        pass

    def transform(self, X):
        """Reduces the input X to the features selected by Boruta.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.

        Returns
        -------
        X : array-like of shape (n_samples, n_features_)
            The input samples with only the selected features by Boruta.
        """

        check_is_fitted(self)

        shapes = np.shape(X)
        if len(shapes) != 2:
            raise ValueError("X must be 2D.")

        if shapes[1] == self.support_.shape[0]:
            if isinstance(X, np.ndarray):
                return X[:, self.support_]
            elif hasattr(X, 'loc'):
                return X.loc[:, self.support_]
            else:
                raise ValueError("Data type not understood.")
        elif shapes[1] == self.support_.sum():
            return X
        else:
            raise ValueError("feature size not matched.")


class _RFE(_BoostSelector):
    """Base class for BoostRFE meta-estimator.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self,
                 estimator, *,
                 min_features_to_select=None,
                 step=1,
                 greater_is_better=False,
                 importance_type='feature_importances',
                 train_importance=True,
                 verbose=0,
                 output_file=None):

        self.estimator = estimator
        self.min_features_to_select = min_features_to_select
        self.step = step
        self.greater_is_better = greater_is_better
        self.importance_type = importance_type
        self.train_importance = train_importance
        self.verbose = verbose
        self.output_file = output_file
        self._eval_score = np.argmax if self.greater_is_better else np.argmin
        self._score_sign = -1 if self.greater_is_better else 1

    def _check_fit_params(self, fit_params):
        """Private method to validate and check fit_params."""

        _fit_params = deepcopy(fit_params)
        estimator = clone(self.estimator)
        # add here possible estimator checks in each iteration

        _fit_params = _set_categorical_indexes(
            self.support_, self._cat_support, _fit_params)

        if 'eval_set' in _fit_params:
            _fit_params['eval_set'] = list(map(lambda x: (
                self.transform(x[0]), x[1]
            ), _fit_params['eval_set']))

        if 'feature_name' in _fit_params:  # LGB
            _fit_params['feature_name'] = 'auto'

        if 'feature_weights' in _fit_params:  # XGB  import warnings
            warnings.warn(
                "feature_weights is not supported when selecting features. "
                "It's automatically set to None.")
            _fit_params['feature_weights'] = None


        _est_params=estimator.get_params()
        if "monotone_constraints" in _est_params and _est_params["monotone_constraints"]:
            monotone_constraints_ = _est_params["monotone_constraints"]
            # print("monotone_constraints_=", monotone_constraints_)

            new_monotone_constraints_ = tuple([monotone_constraints_[m] for m in range(len(monotone_constraints_)) \
                                               if self.support_[m]])
            # print("new_monotone_constraints_=", new_monotone_constraints_)
            estimator.set_params(**{"monotone_constraints":new_monotone_constraints_})

        return _fit_params, estimator

    def _step_score(self, estimator):
        """Return the score for a fit on eval_set."""

        if self.boost_type_ == 'LGB':
            valid_id = list(estimator.best_score_.keys())[-1]
            eval_metric = list(estimator.best_score_[valid_id])[-1]
            score = estimator.best_score_[valid_id][eval_metric]
        else:
            # w/ eval_set and w/ early_stopping_rounds
            if hasattr(estimator, 'best_score'):
                score = estimator.best_score
            # w/ eval_set and w/o early_stopping_rounds
            else:
                valid_id = list(estimator.evals_result_.keys())[-1]
                eval_metric = list(estimator.evals_result_[valid_id])[-1]
                score = estimator.evals_result_[valid_id][eval_metric][-1]

        return score

    def fit(self, X, y, **fit_params):
        """Fit the RFE algorithm to automatically tune
        the number of selected features."""

        self.boost_type_ = _check_boosting(self.estimator)

        importances = ['feature_importances', 'shap_importances']
        if self.importance_type not in importances:
            raise ValueError(
                "importance_type must be one of {}. Get '{}'".format(
                    importances, self.importance_type))

        # scoring controls the calculation of self.score_history_
        # scoring is used automatically when 'eval_set' is in fit_params
        scoring = 'eval_set' in fit_params

        if not scoring:
            raise ValueError("fit_params must have eval_set ")

        if self.importance_type == 'shap_importances':
            if not self.train_importance and not scoring:
                raise ValueError(
                    "When train_importance is set to False, using "
                    "shap_importances, pass at least a eval_set.")
            eval_importance = not self.train_importance and scoring

        shapes = np.shape(X)
        if len(shapes) != 2:
            raise ValueError("X must be 2D.")
        n_features = shapes[1]

        # create mask for user-defined categorical features
        self._cat_support = _get_categorical_support(n_features, fit_params)

        if self.min_features_to_select is None:
            if scoring:
                min_features_to_select = 1
            else:
                min_features_to_select = n_features // 2
        else:
            min_features_to_select = self.min_features_to_select

        if 0.0 < self.step < 1.0:
            step = int(max(1, self.step * n_features))
        else:
            step = int(self.step)
        if step <= 0:
            raise ValueError("Step must be >0.")

        self.support_ = np.ones(n_features, dtype=np.bool)
        self.ranking_ = np.ones(n_features, dtype=np.int)
        if scoring:
            self.score_history_ = []
            eval_score = np.max if self.greater_is_better else np.min
            best_score = -np.inf if self.greater_is_better else np.inf

        while np.sum(self.support_) > min_features_to_select:
            print(f"已选特征数量:{np.sum(self.support_)},最少需要的特征数量:{min_features_to_select}")
            # remaining features
            features = np.arange(n_features)[self.support_]
            _fit_params, estimator = self._check_fit_params(fit_params)

            if self.verbose > 1:
                print("Fitting estimator with {} features".format(
                    self.support_.sum()))
            with contextlib.redirect_stdout(io.StringIO()):
                estimator.fit(self.transform(X), y, **_fit_params)

            # get coefs
            if self.importance_type == 'feature_importances':
                coefs = _feature_importances(estimator)
            else:
                if eval_importance:
                    coefs = _shap_importances(
                        estimator, _fit_params['eval_set'][-1][0])
                else:
                    coefs = _shap_importances(
                        estimator, self.transform(X))
            ranks = np.argsort(coefs)

            # eliminate the worse features
            threshold = min(step, np.sum(self.support_) - min_features_to_select)

            # compute step score on the previous selection iteration
            # because 'estimator' must use features
            # that have not been eliminated yet
            if scoring:
                score = self._step_score(estimator)
                self.score_history_.append(score)
                if best_score == score or best_score != eval_score([score, best_score]):
                    print(f"best score updated {score}! ")
                    best_score = score
                    best_support = self.support_.copy()
                    best_ranking = self.ranking_.copy()
                    best_estimator = estimator

            if self.output_file:
                if hasattr(X, "loc"):
                    tmp=X.columns.tolist()
                    col=list(filter(lambda x: self.support_[tmp.index(x)], tmp))
                else:
                    col=self.support_[:]

                _write_log_file(
                    filename=self.output_file,
                    writelines=str(score) + '|'\
                         + str(estimator.get_params()) + '|'\
                         + str(col) + '\n',
                    mode='a',
                )

            self.support_[features[ranks][:threshold]] = False
            self.ranking_[np.logical_not(self.support_)] += 1

        # set final attributes
        _fit_params, self.estimator_ = self._check_fit_params(fit_params)
        if self.verbose > 1:
            print("Fitting estimator with {} features".format(self.support_.sum()))
        with contextlib.redirect_stdout(io.StringIO()):
            self.estimator_.fit(self.transform(X), y, **_fit_params)

        # compute step score when only min_features_to_select features left
        if scoring:
            score = self._step_score(self.estimator_)
            self.score_history_.append(score)

            if self.output_file:
                if hasattr(X, "loc"):
                    tmp = X.columns.tolist()
                    col = list(filter(lambda x: self.support_[tmp.index(x)], tmp))
                else:
                    col = self.support_[:]

                _write_log_file(
                    filename=self.output_file,
                    writelines=str(score) + '|' \
                               + str(self.estimator_.get_params()) + '|' \
                               + str(col) + '\n',
                    mode='a',
                )

            if score != best_score and best_score == eval_score([score, best_score]):
                print(f"final best update! {score}")
                self.support_ = best_support
                self.ranking_ = best_ranking
                self.estimator_ = best_estimator

        self.n_features_ = self.support_.sum()
        if hasattr(X, "loc"):
            self.selected_feature_names_ = X.loc[:, self.support_].columns.tolist()

        return self


class BoostRFE(_BoostSearch, _RFE):
    """RFE

    Parameters
    ----------
    estimator : LGBModel or XGBModel
        分类器.

    step : int or float, default=1
        每部减少特征数

    min_features_to_select : int, default=None
        最少选择特征数

    importance_type : str, default='feature_importances'
         'feature_importances' or 'shap_importances'.

    train_importance : bool, default=True
        仅在'shap_importances'模式下生效，False时根据eval_set的重要性评估

    param_grid : dict, default=None
        参数空间，当为None时不搜索参数

    greater_is_better : bool, default=False
        评价函数优化方向

    n_iter : int, default=None
        参数搜索轮数，随机搜索或者hyperopt搜索下模式下生效.

    sampling_seed : int, default=None
        参数采样种子，随机搜索或者hyperopt搜索下模式下生效.

    n_jobs : int, default=None
        执行进程数

    verbose : int, default=1
        输出日志程度

    output_file : str, default=None
        param trace logfile

    Attributes
    ----------
    estimator_ : estimator
        最终选择分类器

    n_features_ : int
        最终特征数量

    ranking_ : ndarray of shape (n_features,)
        特征排名

    support_ : ndarray of shape (n_features,)
        最终特征被选标志

    score_history_ : list
        评分历史

    best_params_ : dict
        最佳参数

    trials_ : list
        hyperopt的trial对象

    best_score_ : float
        最佳评分结果

    scores_ : list
        评分历史

    best_iter_ : int
        最佳树轮数

    iterations_ : list
        模型轮数历史

    boost_type_ : str
        模型历史 (LGB or XGB).

    selected_feature_names_ : list
        最终选择特征列表.
    """

    def __init__(self,
                 estimator, *,
                 min_features_to_select=None,
                 step=1,
                 param_grid=None,
                 greater_is_better=False,
                 importance_type='feature_importances',
                 train_importance=True,
                 n_iter=None,
                 sampling_seed=None,
                 verbose=1,
                 n_jobs=None,
                 output_file=None):

        self.estimator = estimator
        self.min_features_to_select = min_features_to_select
        self.step = step
        self.param_grid = param_grid
        self.greater_is_better = greater_is_better
        self.importance_type = importance_type
        self.train_importance = train_importance
        self.n_iter = n_iter
        self.sampling_seed = sampling_seed
        self.verbose = verbose
        self.n_jobs = n_jobs
        self.output_file = output_file

    def _build_model(self, params=None):
        """Private method to build model."""

        estimator = clone(self.estimator)

        if params is None:
            model = _RFE(
                estimator=estimator,
                min_features_to_select=self.min_features_to_select,
                step=self.step,
                greater_is_better=self.greater_is_better,
                importance_type=self.importance_type,
                train_importance=self.train_importance,
                verbose=self.verbose,
                output_file=self.output_file
            )

        else:
            estimator.set_params(**params)
            model = _RFE(
                estimator=estimator,
                min_features_to_select=self.min_features_to_select,
                step=self.step,
                greater_is_better=self.greater_is_better,
                importance_type=self.importance_type,
                train_importance=self.train_importance,
                verbose=self.verbose,
                output_file=self.output_file
            )

        return model


class _SA(_BoostSelector):

    def __init__(
        self,
        estimator, *,
        min_features_to_select=None,
        greater_is_better=False,
        importance_type='feature_importances',
        train_importance=True,
        feature_select_seed=None,
        feature_select_iterations=50,
        feature_select_random_start_rounds=10,
        verbose=0,
        output_file=None,
        opt_trace_keep=False,
    ):
        self.estimator = estimator
        self.min_features_to_select = min_features_to_select
        self.greater_is_better = greater_is_better
        self.importance_type = importance_type
        self.train_importance = train_importance
        self.feature_select_seed = feature_select_seed
        self.feature_select_iterations = feature_select_iterations
        self.feature_select_random_start_rounds = feature_select_random_start_rounds
        self.verbose = verbose
        self.output_file=output_file
        self.opt_trace_keep=opt_trace_keep

        # self._eval_score = np.argmax if self.greater_is_better else np.argmin
        self._eval_score = np.argmax
        self._score_sign = -1 if self.greater_is_better else 1
        self.opt_trace_ = []

    def _step_score(self, estimator):
        """Return the score for a fit on eval_set."""

        if self.boost_type_ == 'LGB':
            valid_id = list(estimator.best_score_.keys())[-1]
            eval_metric = list(estimator.best_score_[valid_id])[-1]
            score = estimator.best_score_[valid_id][eval_metric]
        else:
            # w/ eval_set and w/ early_stopping_rounds
            if hasattr(estimator, 'best_score'):
                score = estimator.best_score
            # w/ eval_set and w/o early_stopping_rounds
            else:
                valid_id = list(estimator.evals_result_.keys())[-1]
                eval_metric = list(estimator.evals_result_[valid_id])[-1]
                score = estimator.evals_result_[valid_id][eval_metric][-1]

        # if self.metric_compare_type == 'mean':
        #     valid_id = list(estimator.evals_result_.keys())[-1]
        #     eval_metric = list(estimator.evals_result_[valid_id])[-1]
        #     eval_scores = np.abs(np.mean([v[eval_metric] for v in estimator.evals_result_.values()], axis=0))
        #     score = eval_scores[self._eval_score(eval_scores)]
        return abs(score)


    def _check_fit_params(self, fit_params):
        """Private method to validate and check fit_params."""

        _fit_params = deepcopy(fit_params)
        estimator = clone(self.estimator)

        if 'eval_set' in _fit_params:
            _fit_params['eval_set'] = list(map(lambda x: (
                x[0][self.tmp_input], x[1]
                # self.transform(x[0]), x[1]
            ), _fit_params['eval_set']))

        _est_params=estimator.get_params()
        if "monotone_constraints" in _est_params and _est_params["monotone_constraints"]:
            monotone_constraints_ = _est_params["monotone_constraints"]
            # print("monotone_constraints_=",monotone_constraints_)

            # estimator.set_params({"monotone_constraints":monotone_constraints_[self.support_]})
            # new_monotone_constraints_ = tuple([monotone_constraints_[m] for m in range(len(monotone_constraints_)) \
            #                                    if self.support_[m]])
            new_monotone_constraints_ = []
            for t in self.tmp_input:
                new_monotone_constraints_.append(monotone_constraints_[self.x_input.index(t)])
            new_monotone_constraints_=tuple(new_monotone_constraints_)
            # print("self.tmp_input=",self.tmp_input)
            # print("self.x_input=",self.x_input)
            # print("new_monotone_constraints_=",new_monotone_constraints_)
            estimator.set_params(**{"monotone_constraints":new_monotone_constraints_})

        return _fit_params, estimator

    def fit(self, X, y, **fit_params):
        """Fit the RFE algorithm to automatically tune
        the number of selected features."""

        self.boost_type_ = _check_boosting(self.estimator)

        importances = ['feature_importances', 'shap_importances']
        if self.importance_type not in importances:
            raise ValueError(
                "importance_type must be one of {}. Get '{}'".format(
                    importances, self.importance_type))

        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be pd.DataFrame")

        # scoring controls the calculation of self.score_history_
        # scoring is used automatically when 'eval_set' is in fit_params
        scoring = 'eval_set' in fit_params

        if not scoring:
            raise ValueError("fit_params must have eval_set ")

        if 'eval_metric' not in fit_params or not callable(fit_params["eval_metric"]):
            raise ValueError("fit_params must have eval_metric ,and eval_metric must be ks function! ")

        if self.importance_type == 'shap_importances':
            if not self.train_importance and not scoring:
                raise ValueError(
                    "When train_importance is set to False, using "
                    "shap_importances, pass at least a eval_set.")
            eval_importance = not self.train_importance and scoring

        shapes = np.shape(X)
        if len(shapes) != 2:
            raise ValueError("X must be 2D.")
        n_features = shapes[1]

        if self.min_features_to_select > n_features:
            raise ValueError("min_features_to_select must little than  n_features.")

        if self.feature_select_random_start_rounds > self.feature_select_iterations:
            raise ValueError("feature_select_random_start_rounds must be little than  feature_select_iterations.")

        self.x_input = X.columns.tolist()

        # create mask for user-defined categorical features
        self._cat_support = _get_categorical_support(n_features, fit_params)

        if self.min_features_to_select is None:
            if scoring:
                min_features_to_select = 1
            else:
                min_features_to_select = n_features // 2
        else:
            min_features_to_select = self.min_features_to_select

        self.ranking_ = np.ones(n_features, dtype=np.int)
        if scoring:
            self.score_history_ = []
            # eval_score = np.max if self.greater_is_better else np.min
            # best_score = -np.inf if self.greater_is_better else np.inf
            eval_score = np.max
            best_score = -np.inf
        print('init.............................')

        self.valid_len_ = len(fit_params["eval_set"])

        k = 0
        self.x_imp = pd.DataFrame(1, index=self.x_input, columns=['imp'])
        self.x_imp['ks_list'] = pd.Series([[] for i in range(len(self.x_input))], index=self.x_input)

        np.random.seed(self.feature_select_seed)
        while k < self.feature_select_iterations:
            self.support_ = np.zeros(n_features, dtype=np.bool)
            k = k + 1
            print(f"-----------feature_select_round {k} start!-----------")
            # self.ks_list.sort(reverse=True)

            if k <= self.feature_select_random_start_rounds:
                # self.tmp_input = random.sample(self.x_input, min_features_to_select)
                self.tmp_input = list(np.random.choice(self.x_input, min_features_to_select, replace=False))
            else:
                tmp_x_imp = (np.random.rand(len(self.x_imp)) * self.x_imp.imp).sort_values(ascending=False)
                self.tmp_input = list((tmp_x_imp[:min_features_to_select].index))
                # print(tmp_x_imp.head(5))
            # print(f"self.tmp_input = {self.tmp_input}")

            self.support_[[self.x_input.index(i) for i in self.tmp_input]] = True
            # for c in self.tmp_input:
            #     self.support_[self.x_input.index(c)] = True
            self.ranking_[np.logical_not(self.support_)] += 1

            _fit_params, estimator = self._check_fit_params(fit_params)
            # tmp_params = [random.sample(params_i, 1)[0] for params_i in params]

            estimator.fit(X[self.tmp_input], y, **_fit_params)
            # print(f"self.tmp_input={self.tmp_input}")
            # print(f"4444self.selected_feature_names_={X.loc[:, self.support_].columns.tolist()}")
            if scoring:
                score = self._step_score(estimator)
                self.score_history_.append(score)
                if best_score != eval_score([score, best_score]):
                    best_score = score
                    best_estimator = estimator
                    best_support = self.support_.copy()
                    best_ranking = self.ranking_.copy()
                    best_selected_feature_names_ = self.tmp_input[:]
                    print(f"best score updated {best_score}!")

            tmpre = {'estimator': estimator, 'result': score, \
                     'x': self.tmp_input, "x_imp": self.x_imp}
            if self.opt_trace_keep:
                self.opt_trace_.append(tmpre)

            if self.output_file:
                _write_log_file(
                    filename=self.output_file,
                    writelines=str(tmpre["result"]) + '|'\
                         + str(tmpre['estimator'].get_params()) + '|'\
                         + str(self.tmp_input) + '\n',
                    mode='a',
                )

            # get coefs
            if self.importance_type == 'feature_importances':
                fea_imp = _feature_importances(estimator)
            else:
                if eval_importance:
                    fea_imp = _shap_importances(
                        estimator, _fit_params['eval_set'][-1][0])
                else:
                    fea_imp = _shap_importances(
                        # estimator, self.transform(X))
                        estimator, X[self.tmp_input])
            fea_imp = pd.Series(fea_imp, index=self.tmp_input)
            for i in self.tmp_input:
                self.x_imp.loc[i, 'ks_list'].append((fea_imp[i] + 0.001) * score)
            self.x_imp.imp = self.x_imp.ks_list.apply(self.__imp_iter).sort_values(ascending=False)

            # self.ranking_[np.logical_not(self.support_)] += 1

        self.support_ = best_support
        self.ranking_ = best_ranking
        self.estimator_ = best_estimator
        self.selected_feature_names_ = best_selected_feature_names_
        print(f"self.selected_feature_names_={self.selected_feature_names_}")

        return self

    def __imp_iter(self, x):
        # f = lambda x: sum(x) / len(x) if len(x) > 0 else 0.5
        f = lambda x: np.mean(x) if len(x) > 0 else 0.5
        return f(x)


    def transform(self, X):
        """Reduces the input X to the features selected by Boruta.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.

        Returns
        -------
        X : array-like of shape (n_samples, n_features_)
            The input samples with only the selected features by Boruta.
        """

        check_is_fitted(self)

        shapes = np.shape(X)
        if len(shapes) != 2:
            raise ValueError("X must be 2D.")

        if shapes[1] == self.support_.shape[0]:
            if isinstance(X, np.ndarray):
                return X[:, self.support_]
            elif hasattr(X, 'loc'):
                return X.loc[:, self.selected_feature_names_]
            else:
                raise ValueError("Data type not understood.")
        elif shapes[1] == self.support_.sum():
            return X
        else:
            raise ValueError("feature size not matched.")


class BoostSA(_BoostSearch, _SA):
    """Simulate Anneal

    Parameters
    ----------
    estimator : LGBModel or XGBModel
        分类器.

    min_features_to_select : int, default=None
         选择特征数，默认为n_features // 2.

    importance_type : str, default='feature_importances'
         'feature_importances' or 'shap_importances'.

    train_importance : bool, default=True
        仅在'shap_importances'模式下生效，False时根据eval_set的重要性评估

    param_grid : dict, default=None
        参数空间，当为None时不搜索参数

    greater_is_better : bool, default=False
        评价函数优化方向

    n_iter : int, default=None
        参数搜索轮数，随机搜索或者hyperopt搜索下模式下生效.

    feature_select_seed : int, default=None
        特征选择种子.

    feature_select_iterations : int, default=50
        特征选择轮数.

    feature_select_random_start_rounds : int, default=10
        特征选择初始随机轮数.

    sampling_seed : int, default=None
        参数采样种子，随机搜索或者hyperopt搜索下模式下生效.

    n_jobs : int, default=None
        执行进程数

    verbose : int, default=1
        输出日志程度

    output_file : str, default=None
        param trace logfile

    Attributes
    ----------
    estimator_ : estimator
        最终选择分类器

    n_features_ : int
        最终特征数量

    ranking_ : ndarray of shape (n_features,)
        特征排名

    support_ : ndarray of shape (n_features,)
        最终特征被选标志

    score_history_ : list
        评分历史

    best_params_ : dict
        最佳参数

    trials_ : list
        hyperopt的trial对象

    best_score_ : float
        最佳评分结果

    scores_ : list
        评分历史

    best_iter_ : int
        最佳树轮数

    iterations_ : list
        模型轮数历史

    boost_type_ : str
        模型历史 (LGB or XGB).

    selected_feature_names_ : list
        最终选择特征列表.
    """

    def __init__(
        self,
        estimator, *,
        min_features_to_select=None,
        param_grid=None,
        greater_is_better=False,
        importance_type='feature_importances',
        train_importance=True,
        n_iter=None,
        sampling_seed=None,
        feature_select_seed=0,
        feature_select_iterations=50,
        feature_select_random_start_rounds=10,
        verbose=1,
        output_file=None,
        opt_trace_keep=False,
        n_jobs=None
    ):

        self.estimator = estimator
        self.min_features_to_select = min_features_to_select
        self.param_grid = param_grid
        self.greater_is_better = greater_is_better
        self.importance_type = importance_type
        self.train_importance = train_importance
        self.n_iter = n_iter
        self.sampling_seed = sampling_seed
        self.feature_select_seed = feature_select_seed
        self.feature_select_iterations = feature_select_iterations
        self.feature_select_random_start_rounds = feature_select_random_start_rounds
        self.verbose = verbose
        self.n_jobs = n_jobs
        self.output_file = output_file
        self.opt_trace_keep = opt_trace_keep

    def _build_model(self, params=None):
        """Private method to build model."""

        estimator = clone(self.estimator)

        if params is None:
            model = _SA(
                estimator=estimator,
                min_features_to_select=self.min_features_to_select,
                greater_is_better=self.greater_is_better,
                importance_type=self.importance_type,
                train_importance=self.train_importance,
                feature_select_seed = self.feature_select_seed,
                feature_select_iterations = self.feature_select_iterations,
                feature_select_random_start_rounds = self.feature_select_random_start_rounds,
                verbose=self.verbose,
                output_file=self.output_file,
                opt_trace_keep=self.opt_trace_keep,
            )

        else:
            estimator.set_params(**params)
            model = _SA(
                estimator=estimator,
                min_features_to_select=self.min_features_to_select,
                greater_is_better=self.greater_is_better,
                importance_type=self.importance_type,
                train_importance=self.train_importance,
                feature_select_seed = self.feature_select_seed,
                feature_select_iterations = self.feature_select_iterations,
                feature_select_random_start_rounds = self.feature_select_random_start_rounds,
                verbose=self.verbose,
                output_file=self.output_file,
                opt_trace_keep=self.opt_trace_keep,
            )

        return model
