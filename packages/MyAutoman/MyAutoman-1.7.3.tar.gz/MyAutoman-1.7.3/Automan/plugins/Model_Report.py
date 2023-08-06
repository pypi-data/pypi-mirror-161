# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 18:55:58 2020

@author: z00119
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import style
pd.set_option('max_row', 15)
pd.set_option('max_column', 15)
pd.set_option('display.width', 500)
import warnings
warnings.filterwarnings('ignore')
from sklearn import metrics 
import seaborn as sns
import os
import base64
from io import BytesIO
from matplotlib.figure import Figure
from IPython.display import display_html 
import pylab
pylab.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
pylab.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
import scipy.stats as st
import os
from scipy.stats import ks_2samp
from IPython.display import display

def get_model_psi(y_label,y_pred,flag,cut=None,n=10):
    temp_df = pd.DataFrame()
    temp_df['pred'] = y_pred
    temp_df['label'] = y_label
    temp_df['flag'] = flag
    if cut!=None:
        temp_df.loc[:,'group'] = pd.cut(temp_df['pred'],cut)
    else:
        x_cut,bins = pd.qcut(temp_df['pred'], n,precision=4,duplicates='drop',retbins=True)
        bins[0] = -np.inf
        bins[-1] = np.inf
        temp_df.loc[:,'group'] =  pd.cut(temp_df['pred'],bins)
        
    a = temp_df.pivot_table(index=['flag','group'],values='label',aggfunc=np.size,fill_value=0)
    a = a.unstack(level=0)
    pct = a/a.sum()
    pct['bench'] = pct.iloc[:,0]
    psi = pd.concat([(pct.iloc[:,i] - pct.iloc[:,-1])*np.log(pct.iloc[:,i] / pct.iloc[:,-1]) for i in range(pct.shape[1])],axis=1).iloc[:,:-1]
    psi.columns = a.columns.levels[1]
    psi.index = psi.index.astype('str')
    psi.loc['Total'] = psi.apply(lambda x: x.sum())
    return psi


def get_perf_table(y_label,y_pred,cut=None,n=10):
    # good bad func
    def n01(x): return round(len(x))
    def n0(x): return sum(x==0)
    def n1(x): return sum(x==1)
    
    temp_df = pd.DataFrame()
    temp_df['pred'] = y_pred
    temp_df['label'] = y_label
    if cut!=None:
        temp_df.loc[:,'group'] = pd.cut(temp_df['pred'],cut)
    else:
        x_cut,bins = pd.qcut(temp_df['pred'], n,precision=4,duplicates='drop',retbins=True)
        bins[0] = -np.inf
        bins[-1] = np.inf
        temp_df.loc[:,'group'] =  pd.cut(temp_df['pred'],bins)


    df_kslift = temp_df.groupby(['group'])['label'].agg([n01,n0,n1])\
        .reset_index().rename(columns={'n01':'total','n0':'good','n1':'bad'})\
        .assign(
          badrate=lambda x: x.bad/(x.good+x.bad),
          good_pct=lambda x: x.good/sum(x.good),   
          cumgood=lambda x: np.cumsum(x.good)/sum(x.good), 
          bad_pct=lambda x: x.bad/sum(x.bad), 
          cumbad=lambda x: np.cumsum(x.bad)/sum(x.bad), 
          cumtotal=lambda x: np.cumsum(x.total)/sum(x.total), 
          lift=lambda x: (x.bad/(x.good+x.bad))/(sum(x.bad)/sum(x.good+x.bad))
      )
      
    
    df1 = temp_df.copy()
    df1.loc[:,'group'] = 'Total'
    df_total = df1.groupby(['group'])['label'].agg([n01,n0,n1])\
        .reset_index().rename(columns={'n01':'total','n0':'good','n1':'bad'})\
        .assign(
          badrate=lambda x: x.bad/(x.good+x.bad),
          good_pct=lambda x: x.good/sum(x.good),   
          cumgood=lambda x: np.cumsum(x.good)/sum(x.good), 
          bad_pct=lambda x: x.bad/sum(x.bad), 
          cumbad=lambda x: np.cumsum(x.bad)/sum(x.bad),
          cumtotal=lambda x: np.cumsum(x.total)/sum(x.total),
          )
      
    df_total.loc[:,'lift'] = df_kslift.lift.max()
      
    perf_table = pd.concat([df_kslift,df_total]).reset_index(drop=True)
    
      
    return perf_table


def plot_model_roc(y_label,y_pred,title=''):
    """
    y_label:真实标签
    y_pred:预测概率
    plot_roc(df['label'],df['pred'])
    
    return:ROC曲线
    """
    tpr,fpr,threshold = metrics.roc_curve(y_label,y_pred) 
    AUC = metrics.roc_auc_score(y_label,y_pred) 

    plt.plot(tpr,fpr,color='blue',label='AUC=%.3f'%AUC) 
    plt.plot([0,1],[0,1],'r--')
    plt.ylim(0,1)
    plt.xlim(0,1)
    plt.title(title+'ROC Curve')
    plt.legend(loc='best')
    # plt.show()


def plot_model_ks(y_label,y_pred,title=''):
    
    """
    y_label:真实y
    y_pred:预测概率
    
    return:KS曲线
    """
    fpr, tpr, thresholds= metrics.roc_curve(y_label, y_pred)
    ks_value = max(abs(fpr-tpr))
    
    # 画图，画出曲线
    plt.plot(fpr, color='red', label='bad',alpha=0.5)
    plt.plot(tpr, color='green', label='good',alpha=0.5)
    plt.plot(abs(fpr-tpr), label='diff')
    # 标记ks
    x = np.argwhere(abs(fpr-tpr) == ks_value)[0, 0]
    plt.plot((x, x), (0, ks_value), label='ks - {:.3f}'.format(ks_value), linestyle="--",color='grey', marker='o', markerfacecolor='r', markersize=3)
    plt.scatter((x, x), (0, ks_value), color='r')
    plt.legend()
    plt.title(title+'KS Curve')
    # plt.show()
    
def plot_model_lift(perf_df,title=''):
    # sns.pointplot(perf_df.index[:-1], perf_df.lift[:-1], alpha=0.3,marker='o') 
    plt.plot(perf_df.index[:-1],perf_df.lift[:-1],label='max_lift = {:.1f}'.format(perf_df.lift.iloc[-1]),alpha=0.5,marker='o',markersize=3) 
    plt.xticks(range(len(perf_df.lift[:-1])))
    plt.axhline(y=1,ls="--",c="red",alpha=0.6)#添加水平直线
    for a, b in zip(perf_df.index[:-1], perf_df.lift[:-1]):
        plt.text(a, b, "{:.2f}".format(b), ha='center', va='bottom', fontsize=10)  # 将数值显示在图形上
    
    plt.scatter(len(perf_df.lift[:-2]), perf_df.lift.iloc[-2],color='red')
    plt.legend()
    plt.title(title+'Lift Chart')
    # plt.show()

def get_model_all(y_label,y_pred,title='',cut=None,n=10):
    perf_table = get_perf_table(y_label,y_pred,cut=cut,n=n)
    perf_table1 = perf_table.copy()

    
    T = f"<h2 style='background-color:#c7c1c1; padding:10px'>{title} 模型效果</h2>"
    perf_table1.columns = ['模型分组','总样本量', '好样本量','坏样本量','坏率','好样本占比','累积好样本占比','坏样本占比','累积坏样本占比','累积样本占比','提升度']
    perf_table_styler = perf_table1.style.format("{:.2%}",subset=['坏率','好样本占比','累积好样本占比','坏样本占比','累积坏样本占比','累积样本占比'])\
        .format("{:.3f}",subset=['提升度'])\
            .format("{:.0f}",subset=['总样本量', '好样本量','坏样本量'])\
                .bar(color='#ffc1c1',subset=pd.IndexSlice[0:19,'坏率'],align='mid')\
                    .set_table_attributes("style='display:inline';display: flex;align-items: center;text-align: center;")\
                        .set_properties(subset=['模型分组'],**{'width': '140px'})
    display_html(T+perf_table_styler._repr_html_(),raw=True)

    plist = ["plot_model_roc(y_label,y_pred, title = title)",
              "plot_model_ks(y_label,y_pred, title = title)",
              "plot_model_lift(perf_table, title = title)"]
       
    subplot_nrows = 1#np.ceil(len(plist)/4)
    subplot_ncols = 4#np.ceil(len(plist)/subplot_nrows)
    fig = plt.figure(figsize=[int(subplot_ncols*4.5), int(subplot_nrows*4)])
    for i in np.arange(len(plist)):
        plt.subplot(subplot_nrows,subplot_ncols,i+1)
        eval(plist[i])
    ax = plt.subplot(subplot_nrows,subplot_ncols,4)
    perf_table.iloc[:-1,:][['total']].plot(kind='bar', color='#a3c3d7',width = 0.8,ax = ax)
    perf_table.iloc[:-1,:]['badrate'].plot(secondary_y=True,color='red',marker='o',markersize=3,alpha=0.7,ax = ax)
    plt.axhline(y=perf_table.badrate.iloc[-1], color='grey', label='avg_risk', linestyle='--', linewidth=1)
    ax.legend_.remove()
    ax.set_title('{}\n 分组风险趋势图,样本量：{:.0f}, \n平均风险：{:.2%}'.format(title,perf_table.total.iloc[-1],perf_table.badrate.iloc[-1]), fontsize=12)
    plt.close()
    # display(fig)

    metadata={'ipub': {
      'figure': {'caption': 'a'}}
      }
    display(fig, metadata=metadata)
    # plt.close()
#     return perf_table

def color_psi(val):
    color = '#d56129' if val>=0.25 else '#9ec966' if val<=0.1 else '#e0ca53'
    return 'background-color: %s' % color


def get_var_metrics(df, y, x_input, q=10,n=0.05,dt='shouxin_date',custom_range='flag'):
    if custom_range==None:
        df['month'] = df[dt].astype('str').str[0:6]
        df['cut'] = df['month']
    elif custom_range =='flag':
        df['cut'] = df['flag']
    else:
        df[dt] = df[dt].astype(int)
        df['cut'] = pd.cut(df[dt],custom_range).astype('object')
    i = 0
    oot = pd.DataFrame()
    base = pd.DataFrame()
    vars_df = pd.DataFrame()
    for x in x_input:
#         print(i, x)   
            #     特征分箱 每份样本按照同一份分箱计算。
        if df[x].nunique()<=3 or pd.api.types.is_string_dtype(df[x]):
#             bins = auto_bin(df,x,y,q=q,n=n)[1]
#             df['x_cut'] = [xx if xx in bins else bins[-1] for xx in df[x]]
            df['x_cut'] = df[x].astype('str')
        else:
            bins = auto_bin(df,x,y,q=q,n=n)[1]
            df['x_cut'] = pd.cut(df[x],bins)   
        
        c = df.pivot_table(index=['x_cut'],values=[y],columns='cut',aggfunc=[len,np.sum,lambda l:sum(l)/len(l)],fill_value=0)
        c.columns.set_levels(['len','sum','badrate'], level=0,inplace=True)
        c = c.droplevel(level=1,axis=1)
        d = c.xs(key='len',axis=1)/c.xs(key='len',axis=1).sum()
        d.columns = pd.MultiIndex.from_product([['pct'],list(d.columns)])
        the_bins_df = pd.concat([c,d],axis=1)
        
        bb = the_bins_df.xs(key='badrate',axis=1)
        bb.index=bb.index.astype('str')
        bb = bb[~bb.index.isin(['(-inf, -99.0]','-99','-99.0'])]
        badpsi = bb.corr().iloc[0,:]
        
        pct = the_bins_df.xs(key='pct',axis=1)
        pct.index=pct.index.astype('str')
        
        missing_pct = pct[pct.index.isin(['(-inf, -99.0]','-99','-99.0'])].T
        
    
        pct = pct[~pct.index.isin(['(-inf, -99.0]','-99','-99.0'])]
        pct['bench'] =pct.iloc[:,0] 
        A = pd.concat([(pct.iloc[:,i]-pct.iloc[:,-1])*np.log(pct.iloc[:,i]/pct.iloc[:,-1]) for i in range(pct.shape[1])],axis=1)
        psi = A.sum()[:-1]
        psi.index = badpsi.index
        
        is_Monotone = bb.apply(lambda x: x.is_monotonic)*1
        
        y_list = df.groupby(df['cut'])[y].apply(lambda j:sum(j)/len(j))   
        
        iv_list = df.groupby(df['cut']).apply(lambda k: cal_iv(k['x_cut'],k[y])[0])
        
        bs = bb/y_list
        min_bs = bs.min()
        max_bs = bs.max()
        
        the_var_df = pd.concat([iv_list,is_Monotone,max_bs,min_bs,psi,badpsi,missing_pct],axis=1)
        if missing_pct.shape[1]==0:
            the_var_df['missing_pct'] = 0
        the_var_df.columns = ['IV','is_Monotone','max_bs','min_bs','psi','Badpsi','missing_pct']
        
            
        the_var_df['min_cross_IV'] = the_var_df['IV'].min()
        the_var_df['var'] = x
         
        the_oot = the_var_df.iloc[1:,:].groupby('var').agg({'IV': np.mean, 
                                                  'is_Monotone':min,
                                                  'max_bs':min,
                                                  'min_bs':max,
                                                  'missing_pct':max,
                                                  'psi':max,
                                                  'Badpsi':min,
                                                  'min_cross_IV':min}).reset_index()
        
        the_base = the_var_df.head(1).reset_index(drop=True)
        base = pd.concat([base,the_base])
        oot = pd.concat([oot,the_oot])
        vars_df = pd.concat([vars_df,the_var_df])
        
        base['max_bs'] = base['max_bs'].fillna(0)
        base['min_bs'] = base['min_bs'].fillna(100)
        base['Badpsi'] = base['Badpsi'].fillna(0)
        base['is_Monotone'] = base['is_Monotone'].fillna(0)
        
        oot['max_bs'] = oot['max_bs'].fillna(0)
        oot['min_bs'] = oot['min_bs'].fillna(100)
        oot['Badpsi'] = oot['Badpsi'].fillna(0)
        oot['is_Monotone'] = oot['is_Monotone'].fillna(0)
        
        vars_df['max_bs'] = vars_df['max_bs'].fillna(0)
        vars_df['min_bs'] = vars_df['min_bs'].fillna(100)
        vars_df['Badpsi'] = vars_df['Badpsi'].fillna(0)
        vars_df['is_Monotone'] = vars_df['is_Monotone'].fillna(0)
        
        i = i + 1
#     # base =  base.sort_values(by='IV',ascending=False)
#     if os.path.exists(output_path):
#         pass
#     else:
#         os.makedirs(output_path)
#     base.to_csv(output_path+'base_df.csv',index=0)
#     oot.to_csv(output_path+'oot_df.csv',index=0)
    return base,oot,vars_df


def get_score(vars_df):
    
    score = vars_df[['var']]
    
    score['饱和度'] = pd.cut(vars_df.missing_pct,[0,0.1,0.2,0.4,0.6,0.8,np.inf],right=False).astype('str')
    score['饱和度'] = score['饱和度'].map({'[0.0, 0.1)':150, '[0.1, 0.2)':120, '[0.2, 0.4)':90, '[0.4, 0.6)':60,'[0.6, 0.8)':30, '[0.8, inf)':0 })
    
    score['IV'] = pd.cut(vars_df.IV,[0,0.02,0.1,0.3,0.5,np.inf],right=False).astype('str')
    score['IV'] = score['IV'].map({'[0.0, 0.02)':0, '[0.02, 0.1)':60, '[0.1, 0.3)':90, '[0.3, 0.5)':120,'[0.5, inf)':150})
    
    score['max_bs'] = pd.cut(vars_df.max_bs,[0,2,3,np.inf],right=False).astype('str')
    score['max_bs'] = score['max_bs'].map({'[0.0, 2.0)':0, '[2.0, 3.0)':120, '[3.0, inf)':150,np.nan:0})
    
    score['min_bs'] = np.where((vars_df.min_bs<0.5)&(vars_df.IV>=0.02),150,0)
    
    score['单调性'] = np.where((vars_df.is_Monotone==1)&(vars_df.IV>=0.02),150,0)
    
    score['数据稳定性'] = np.where((vars_df.psi<0.1)&(vars_df.IV<=0.001),0,np.where((vars_df.psi<0.1),150,0))
    
    score['Badpsi'] = np.where((vars_df.Badpsi>=0.7),150,0)
    
    score['min_cross_IV'] = pd.cut(vars_df.min_cross_IV,[0,0.02,0.1,0.3,0.5,np.inf],right=False).astype('str')
    score['min_cross_IV'] = score['min_cross_IV'].map({'[0.0, 0.02)':0, '[0.02, 0.1)':60, '[0.1, 0.3)':90, '[0.3, 0.5)':120,'[0.5, inf)':150})
        
    score['综合评分'] = score.sum(axis=1)
    score['IV值'] = vars_df.IV
    score['缺失率'] = vars_df.missing_pct
    

    score['区分能力'] = score['IV']+score['max_bs']+score['min_bs']
    score['区分能力稳定性'] = score['min_cross_IV']+score['Badpsi']
#     score['稳定性'] = score['数据稳定性'] + score['区分能力稳定性']
    
    score = score.sort_values(by='综合评分',ascending=False)
    
    return score


def match_score(base_score,oot_score,columns):
    
    df2 = pd.merge(oot_score.reset_index(drop=True),base_score.reset_index(drop=True),how='left',on='var').fillna(0)
    df2 = pd.merge(df2,columns,how = 'left',on = 'var')
    df2['后端监控'] = (df2['区分能力_x'] + df2['单调性_x']+df2['区分能力稳定性_x']) - (df2['区分能力_y'] + df2['单调性_y']+df2['区分能力稳定性_y'])
    df2['前端监控'] = (df2['饱和度_x'] + df2['数据稳定性_x']) - (df2['饱和度_y'] + df2['数据稳定性_y'])
    
    for i in ['区分能力','单调性','区分能力稳定性','数据稳定性','饱和度']:
        df2[i+'_gap'] = df2[i+'_x']-df2[i+'_y']
        
    df2 = df2.sort_values(by='rank')
    df3 = df2[['var','rank','后端监控','前端监控']]
    df3['区分能力'] = np.where((df2['IV值_x']>=0)&(df2['IV值_x']<0.02),'无区分能力',
                           np.where((df2['IV值_x']>=0.02)&(df2['IV值_x']<0.1),'弱区分能力',
                                    np.where((df2['IV值_x']>=0.1)&(df2['IV值_x']<0.3),'中等区分能力',
                                             np.where((df2['IV值_x']>=0.3),'强区分能力','无区分能力'))))
    df3['区分能力_gap'] = np.where((df2['区分能力_gap']<-60),'; 区分效果有明显下降','')
    
    df3['高倍数能力'] = np.where((df2['max_bs_x']>0),'; 高风险区分能力好','')
    df3['低倍数能力'] = np.where((df2['min_bs_x']>0),'; 低风险区分能力好','')
    
    
    df3['区分能力稳定性'] = np.where((df2['区分能力稳定性_x']==0)&(df2['区分能力_x']>0),'; 跨时稳定性有波动',
                             np.where(((df2['min_cross_IV_x']>0)&(df2['Badpsi_x']>0)),'; 跨时稳定性好',''))
    
    df3['区分能力稳定性_gap'] = np.where((df2['区分能力稳定性_gap']<-60),'; 跨时稳定性有明显下降','')
    
    df3['单调性'] = np.where((df2['单调性_x']>0),'; 单调性良好','')
    
    df3['单调性_gap'] = np.where((df2['单调性_gap']<=-30),'; 单调性有明显下降','')
    
    df3['饱和度'] = np.where((df2['饱和度_x']>0)&(df2['饱和度_x']<=30),'饱和度低',
                           np.where((df2['饱和度_x']>30)&(df2['饱和度_x']<=60),'饱和度一般',
                                    np.where((df2['饱和度_x']>60)&(df2['饱和度_x']<=90),'饱和度中等',
                                             np.where((df2['饱和度_x']>90)&(df2['饱和度_x']<=120),'饱和度较高',
                                             np.where((df2['饱和度_x']>120),'饱和度高','饱和度很低')))))
    
    df3['饱和度_gap'] = np.where((df2['饱和度_gap']<-120),'; 饱和度有明显下降',np.where((df2['饱和度_gap']<=-30),'; 饱和度有小幅下降',''))
    
    df3['数据稳定性'] = np.where((df2['数据稳定性_x']==0),'; 稳定性差','')
    
    df3['数据稳定性_gap'] = np.where((df2['数据稳定性_gap']<=-150),'; 数据稳定性有明显下降','')
    
    df3['前端结论'] = ['{}({:.1%}){}{}{}'.format(a,b, c,d,e) for a,b,c,d,e in zip(df3['饱和度'],1-df2['缺失率_x'], df3['饱和度_gap'],df3['数据稳定性'],df3['数据稳定性_gap'])]
    df3['后端结论'] = ['{}(平均IV: {:.2f}){}{}{}{}{}{}{}'.format(a,b, c,d,e,f,g,h,i) for a,b,c,d,e,f,g,h,i in zip(df3['区分能力'],df2['IV值_x'], df3['高倍数能力'],df3['低倍数能力'],df3['区分能力_gap'],df3['区分能力稳定性'],df3['区分能力稳定性_gap'],df3['单调性'],df3['单调性_gap'])]
    
    df3 = df3[['rank','var','前端监控','前端结论','后端监控','后端结论']]
    
    df3['前端监控'] = np.where((df3['rank']<=10)&((df3['前端监控']<-90)|(df3['前端结论'].str.contains('明显下降'))),'Alert',
                           np.where(df3['前端结论'].str.contains('差'),'！','-'))
    df3['后端监控'] = np.where((df3['rank']<=10)&((df3['后端监控']<-120)|(df3['后端结论'].str.contains('明显下降'))),'Alert', 
                           np.where(df3['后端结论'].str.contains('无|差'),'！',
                                    np.where(df3['后端结论'].str.contains('好|强'),'GOOD','-')))
    return df2,df3


def auto_bin(df,x,y,q=10,n=0.05,cut=None):
    '''
        
    df: pd.DataFrame
        输入dataframe,带y

    x: string
        如：自变量特征名 如 'cust_sex', 特征不分连续型或分类型，例：x ='tag1_影音视频_comentdown_pct'

    y:string
        样本的因变量 如 'fpd4', 因变量只能为0,1的int格式输入

    q: int
        特征等频分箱的组数，默认q=10，等频分为10箱
  
    n: float
        n某一箱样本量最小占比，默认0.05（百5），可自定义。

    '''
        #定义woe计算函数
    def get_woe(num_bins):
        columns = ['min','max','count_0','count_1']
        df = pd.DataFrame(num_bins,columns=columns)
        df['total'] = df.count_0 + df.count_1
        df['pct'] = df.total/df.total.sum()
        df['bad_rate'] = df.count_1/df.total
        df['woe'] = np.log((df.count_0/df.count_0.sum())/(df.count_1/df.count_1.sum()))
        df['woe'] = df['woe'].replace(np.inf,0)
        return df
    
    # 定义单调计算函数
    def BadRateMonotone(num_bins):
        badRate = [num_bins[i][3]*1.0/(num_bins[i][2]+num_bins[i][3]) for i in range(len(num_bins))]
        if sorted(badRate) == badRate or sorted(badRate) == badRate[::-1]:
            BRMonotone = 1
        else:
            BRMonotone = 0
        return BRMonotone        
    
    # 定义IV计算函数
    def get_iv(bins_df):
        rate = ((bins_df.count_0/bins_df.count_0.sum())-(bins_df.count_1/bins_df.count_1.sum()))
        IV = np.sum(rate*bins_df.woe)
        return IV
    
    df = df[[x,y]].copy()
    
    if df[x].nunique()<=3 or pd.api.types.is_string_dtype(df[x]) or pd.api.types.is_categorical_dtype(df[x]) :
        bins = sorted(list(df[x].unique()))#[str(v) for v in sorted(list(df[x].unique()))]
        df['qcut'] = df[x]
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
    
        num_bins = [*zip(bins,bins[0:],count_y0,count_y1)] 
    elif cut!=None:
        bins = sorted(set(np.insert(cut,0,[-np.inf,np.inf])))
        df['qcut'] = pd.cut(df[x],bins)
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
    
        num_bins = [*zip(bins,bins[1:],count_y0,count_y1)] 
    else:
        bins = sorted(df[x].quantile([i/q for i in range(q+1)]).drop_duplicates().values)
#        df['qcut'],bins = pd.qcut(df[x],retbins=True,q = q,duplicates='drop')
        bins = sorted(np.insert(bins,0,[-np.inf,np.inf]))
        df['qcut'] = pd.cut(df[x],bins)
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
    
        num_bins = [*zip(bins,bins[1:],count_y0,count_y1)] 
    
    special = num_bins[0]
    if special[1]==-99 or special[1]=='-99' or special[1]=='-99.0' or str(special[0]) =='(-inf, -99.0]':
        num_bins.remove(special) 
        
    #n 空值是否要合并， 不行自动合并就设置n=0
    for i in range(len(bins)):
        if len(num_bins)>1:            
            if 0 in num_bins[0][2:] or sum(num_bins[0][2:])/df.shape[0] <= n:
                num_bins[0:2] = [(
                        num_bins[0][0],
                        num_bins[1][1],
                        num_bins[0][2]+num_bins[1][2],
                        num_bins[0][3]+num_bins[1][3],
                        )]
                continue
        

            for i in range(len(num_bins)):
                if 0 in num_bins[i][2:] or sum(num_bins[i][2:])/df.shape[0] <=n:
#                     print(num_bins)
                    num_bins[i-1:i+1] = [(
                        num_bins[i-1][0],
                        num_bins[i][1],
                        num_bins[i-1][2]+num_bins[i][2],
                        num_bins[i-1][3]+num_bins[i][3],
                        )]
                    break
            
        else:
            break
        
    # 当分组数超过5组且不单调的情况下，再进行单调判断合并。
    while len(num_bins)>5 and BadRateMonotone(num_bins)==0:
        pvs = []
        for i in range(len(num_bins)-1):
            pv = st.chi2_contingency([num_bins[i][2:], num_bins[i+1][2:]],True)[0]
            pvs.append(pv)
        i = pvs.index(min(pvs))
        num_bins[i:i+2] = [(
                        num_bins[i][0],
                        num_bins[i+1][1],
                        num_bins[i][2]+num_bins[i+1][2],
                        num_bins[i][3]+num_bins[i+1][3],
                        )]
  
    if special[1]==-99 or special[1]=='-99' or special[1]=='-99.0' or str(special[0]) =='(-inf, -99.0]':
        num_bins.insert(0,special)
        
    bins_df = get_woe(num_bins)
    bins_df['var']=x
    bins_df['IV'] = get_iv(bins_df)
    
       
    #判断badrate是否单调,空值组不参与判断
    if bins_df.iloc[0,1]==-99 or bins_df.iloc[0,1]=='-99' or bins_df.iloc[0,1]=='-99.0' or str(bins_df.iloc[0,1]) =='(-inf, -99.0]':
        badRate = [round(i,3) for i in list(bins_df.bad_rate)[1:]]
        bs = [round(i/df[y].mean(),3) for i in bins_df['bad_rate'][1:]]
        pct = list(bins_df.pct)[1:]
        missing_pct = bins_df.pct[0]
        
    else:
        badRate = [round(i,3) for i in list(bins_df.bad_rate)[0:]]
        bs = [round(i/df[y].mean(),3) for i in bins_df['bad_rate'][0:]]
        pct = list(bins_df.pct)[0:]
        missing_pct = 0
        
    # bs = [round(i/df[y].mean(),3) for i in badRate]
    
    if sorted(badRate) == badRate or sorted(badRate) == badRate[::-1]:
        BRMonotone = 1
    else:
        BRMonotone = 0
    
    # iv小于0.001 完全没有区分能力，单调性也不存在，置为0
    if get_iv(bins_df)<=0.001:
        BRMonotone = 0        

    bins_df['is_Monotone'] = BRMonotone
    
    #输出最高组，最低组风险倍数,空值组不参与判断
    bins_df['max_bs'] = max(bs) if bs else 0
    bins_df['min_bs'] = min(bs) if bs else 0
    bins_df['bs'] = [round(i/df[y].mean(),3) for i in bins_df['bad_rate']]
    
    #输出最高组，最低组占比,空值组不参与判断
    bins_df['max_bs_pct'] = pct[bs.index(max(bs))] if bs else 0
    bins_df['min_bs_pct'] = pct[bs.index(min(bs))] if bs else 0
    
    bins_df['missing_pct'] = missing_pct
    
    
#     最优切点：
    if df[x].nunique()<3 or pd.api.types.is_string_dtype(df[x]):
        bins = [num_bins[i][0] for i in range(len(num_bins)-1)]+[num_bins[-1][1]]
        
    else:
        bins = [num_bins[i][0] for i in range(len(num_bins))]+[num_bins[-1][1]]
        
    return bins_df,bins

# 作图函数
def draw_x_plt(vars_df,x,mode='kde',name=''):
    ts = vars_df[vars_df['var']==x].reset_index()
    style.use('ggplot')
    fig,(ax1,ax2,ax3,ax4) = plt.subplots(1,4,figsize=(12,3))
    fig.suptitle(x,x = 0.12, y = 1.1,ha='left',size=15,bbox = dict(facecolor = 'grey',alpha=0.1))

    ax1.set_title('变量在各样本的IV值',size=10)
    ts.IV[ts.IV>0.5]=0.5
    ax1.plot(ts['cut'],ts['IV'],marker='*',ms=10,color='coral')
    ax1.set_ylim(0,0.5)
    ax1.axhline(y=0.02,color='r',label='warning line1',linestyle='--',linewidth=1)
    ax1.axhline(y=0.1,color='yellow',label='warning line1',linestyle='--',linewidth=1)
    ax1.axhline(y=0.3,color='g',label='warning line2',linestyle='--',linewidth=1)
    for n1,n2 in zip(ts['cut'],ts['IV']):
        ax1.text(n1,n2+0.05,str(round(n2,3)),ha='center')
    ax1.set_xticklabels(list(ts['cut']),rotation=90,fontsize=9)

    ax2.set_title('变量在各样本的缺失值占比(%)',size=10)
    ax2.bar(ts['cut'],ts['missing_pct'],color='silver')
    ax2.set_ylim(0,1)
    ax2.axhline(y=0.95,color='r',label='warning line',linestyle='--',linewidth=1)
    for n1,n2 in zip(ts['cut'],ts['missing_pct']):
        ax2.text(n1,n2+0.05,str(round(n2*100,1)),ha='center')
    ax2.set_xticklabels(list(ts['cut']),rotation=90,fontsize=9)
    
    ax3.set_title('变量在各样本的PSI',size=10)
    ts.psi[ts.psi>0.4]=0.4
    ax3.plot(ts['cut'],ts['psi'],marker='*',ms=10,color='royalblue')
    ax3.set_ylim(-0.1,0.4)
    ax3.axhline(y=0.0,color='g',label='warning line1',linestyle='--',linewidth=1)
    ax3.axhline(y=0.1,color='yellow',label='warning line1',linestyle='--',linewidth=1)
    ax3.axhline(y=0.2,color='r',label='warning line2',linestyle='--',linewidth=1)
    for n1,n2 in zip(ts['cut'],ts['psi']):
        ax3.text(n1,n2+0.05,str(round(n2,3)),ha='center')
    ax3.set_xticklabels(list(ts['cut']),rotation=90,fontsize=9)
    
    ax4.set_title('变量在各样本的badrate相关性',size=10)
    ax4.plot(ts['cut'],ts['Badpsi'],marker='*',ms=10,color='r',alpha=0.7)
    ax4.set_ylim(-1,1.5)
    ax4.axhline(y=0.5,color='r',label='warning line1',linestyle='--',linewidth=1)
    ax4.axhline(y=0.7,color='yellow',label='warning line1',linestyle='--',linewidth=1)
    ax4.axhline(y=0.9,color='g',label='warning line2',linestyle='--',linewidth=1)
    for n1,n2 in zip(ts['cut'],ts['Badpsi']):
        ax4.text(n1,n2+0.05,str(round(n2,3)),ha='center')
    ax4.set_xticklabels(list(ts['cut']),rotation=90,fontsize=9)



    plt.show()


# Multi Mosaic Plot
def plt_multi_mosaic(df,x,y,bs=5,q=10,n=0.05,dt = 'shouxin_date',custom_range=None,file='out_mosaic.png',name=''):
    '''

    Parameters
    ----------
    df : pd.dataframe
        输入dataframe,需包含y，dt.
    x : string
        特征名 如'cust_sex',特征不分连续型或分类型.
    y : string
        样本的因变量 如 'fpd4', 因变量只能为0,1的int格式输入.
    bs : int , optional
        扩大倍数，当平均风险很低时看不清，放大. The default is 5.
    q : int, optional
        特征等频分箱的组数，默认q=10，等频分为10箱. The default is 10.
    n : float, optional
        n某一箱样本量最小占比，默认0.05（百5），可自定义。. The default is 0.05.
    cut : list, optional
        特征自定义切点，如：cut=[1,3,5]. The default is False.
    dt : string, optional
        样本拆分的日期，一般我们建模中常用的，建案时间，交易时间等等。格式为 20190101 数值型. The default is 'shouxin_date'.
    custom_range : list, optional
        样本拆分list，默认为None，按月拆分
        如果想看全部样本的 可定义[-np.inf,np.inf] # 不推荐，这个有直接mosiac plot 包使用，耗时短.
        list自定义 如:[-np.inf,20190101,20190601,20190901,np.inf]
        The default is None.
    file : string, optional
        file,图片保存名称,默认'out_mosaic.png'. The default is 'out_mosaic.png'.
    name : string, optional
        图片名称. The default is ''.

    Returns
    -------
    plot图片.

    '''
    if custom_range==None:
        df['month'] = df[dt].astype('str').str[0:6]
        df['cut'] = df['month']
    elif custom_range =='flag':
        df['cut'] = df['flag']
    else:
        df[dt] = df[dt].astype(int)
        df['cut'] = pd.cut(df[dt],custom_range).astype('object')
    
        #     特征分箱 每份样本按照同一份分箱计算。
    if df[x].nunique()<=3 or pd.api.types.is_string_dtype(df[x]):
        bins = auto_bin(df,x,y,q=q,n=n)[1]
        df['x_cut'] = [xx if xx in bins else bins[-1] for xx in df[x]]
    else:
        bins = auto_bin(df,x,y,q=q,n=n)[1]
        df['x_cut'] = pd.cut(df[x],bins) 
    

    y_list = df.groupby(df['cut'])[y].apply(lambda j:sum(j)/len(j))   
    num_list = df.groupby(df['cut'])[y].apply(lambda k:len(k))   
    iv_list = df.groupby(df['cut']).apply(lambda k: cal_iv(k['x_cut'],k[y])[0])
    ks_list = df.groupby(df['cut']).apply(lambda k: cal_ks(k,x,y))

    c = df.pivot_table(index=['x_cut'],values=[y],columns='cut',aggfunc=[len,np.sum,lambda l:sum(l)/len(l)],fill_value=0)
    c.columns.set_levels(['len','sum','ratio'], level=0,inplace=True)
    rate_list = c.unstack()['ratio'][y]
    pct_list = c.unstack()['len'][y]
    
    #画分时段马赛克图        

    l = sorted(set(df['cut']))
    
        
    fig = plt.figure(figsize=(5.3*len(l),4))
    fig.suptitle(x+name,x = 0.12, y = 1.03, ha='left',size=15,bbox = dict(facecolor = 'grey',alpha=0.1))
    
    
    for k in l:  
        i = l.index(k)
        bad_rate = [ii*bs if ii<0.25 else ii for ii in rate_list[k] ]
        pct = pct_list[k]/pct_list[k].sum()
        x_pos = list(np.cumsum(pct))[:-1]
        x_pos.insert(0,0)
        y_label_pos = [round(bad_rate[0]/2,4),bad_rate[0]+round((1-bad_rate[0])/2,4)]
        x_label_pos = []
        for j in range(len(list(pct))):
            if j ==0:
                x_label_pos.append(round(list(pct)[j]/2,4))
            else:
                x_label_pos.append(round((sum(list(pct)[:j])+list(pct)[j]/2),4))       
        ax = plt.subplot(1,len(l),i+1)
        ax.set_title('{}, {}, IV:{:.2f}, KS:{:.2f}'.format(k,num_list[k],iv_list[k],ks_list[k]),size = 12)
        ax.bar(x_pos,bad_rate,width=pct,align='edge',ec='w',lw=1,label='Y',color='coral',alpha=0.8)
        ax.bar(x_pos,[1-i for i in bad_rate],bottom =bad_rate, width=pct, align='edge',ec='w',lw=1,label='N',color='silver',alpha=0.8)
        ax.axhline(y =y_list[k]*bs,color='r',label='warning line1',linestyle='--',linewidth=1)
        ax.text(1,y_list[k]*bs+0.05,'avg:'+str(round(y_list[k]*100,1)),ha='center',fontsize=9,color='r')
        ax.set_xticks(x_label_pos)
        ax.set_yticks(y_label_pos)
        ax.set_xticklabels([str(x) for x in list(c.index)],rotation=90,fontsize=10)
        ax.set_yticklabels(['Y','N'])    
        for n1,n2,n3 in zip(x_label_pos,bad_rate,[i/bs for i in bad_rate]):
            ax.text(n1,n2/2,str(round(n3*100,1)),ha='center',fontsize=9)
    
    
    fig.show()
    fig.savefig(file,bbox_inches='tight')
    
    
def cal_ks(data,prob,y):
    return ks_2samp(data[prob][data[y]==1],data[prob][data[y]==0]).statistic

def cal_iv(x,y):
    df = y.groupby(x).agg(['count','sum'])
    df.columns = ['total','count_1']
    df['count_0'] = df.total - df.count_1
    df['pct'] = df.total/df.total.sum()
    df['bad_rate'] = df.count_1/df.total
    df['woe'] = np.log((df.count_0/df.count_0.sum())/(df.count_1/df.count_1.sum()))
    df['woe'] = df['woe'].replace(np.inf,0)
#    print(df)
    rate = ((df.count_0/df.count_0.sum())-(df.count_1/df.count_1.sum()))
    IV = np.sum(rate*df.woe)
    return IV,df

def get_data(data_folder,input_model,rename_rule={'mob3_k11':'label','xgb':'pred','trans_date':'dt'},special_value=[-999]):
    
    # 将该文件夹下的所有文件名存入列表
    csv_name_list = os.listdir(data_folder)
    columns = get_feature_imp(input_model)
    col = list(columns['var'])
    # 循环遍历列表中各个CSV文件名，并完成文件拼接
    df = pd.DataFrame()
    for i in range(len(csv_name_list)):
        dfi = pd.read_csv( data_folder+'/'+csv_name_list[i] )
        flag = model_check(dfi,csv_name_list[i])
        if flag == 1:
            break
        del_col = list(set(dfi.columns).intersection(set(['label','pred','dt'])))
        dfi = dfi.drop(del_col,axis=1)
        dfi = dfi.rename(columns=rename_rule)
        dfi = dfi[col+['label','pred','dt']]
        dfi['flag'] = csv_name_list[i].split('.')[0]
        df = pd.concat([df,dfi])
    if flag != 1:
        df = df.reset_index(drop=True)
        df = df.replace(special_value,-99)
    return df,flag

def get_sample(df):
    df['dt'] = df['dt'].apply(lambda dd: str(dd).replace('-','')).astype('int')
    sample = pd.DataFrame(df.groupby(df['flag'])['label'].size()).assign(
        bad=df.groupby('flag')['label'].sum(),
        bad_rate=df.groupby('flag')['label'].apply(lambda x: '{:.2%}'.format(sum(x)/len(x))),
        date_range = df.groupby('flag')['dt'].apply(lambda x: str(x.min())+'-'+ str(x.max()))
    )
    sample.columns = ['样本量','坏样本量','坏率','时间跨度']
    sample_styler = sample.style.set_properties(**{'width': '150px'})\
        .format('{:.0f}',subset=['样本量','坏样本量'])
    display_html(sample_styler._repr_html_(),raw=True)

import subprocess
import time

def save_html_report(path,current_file, model_name=''):
    time.sleep(5)
#    command = f"jupyter nbconvert --to html --template {path}\\clean_output.tpl {current_file} "+f"--output {path}\\{model_name}_model_report.html"
#    command = f"jupyter nbconvert --to html --no-input {current_file} "+f"--output {path}\\{model_name}_model_report.html"
    command = f"jupyter nbconvert --to html --TemplateExporter.exclude_input=True {current_file} "+f"--output {path}\\{model_name}_model_report.html"
    
#    print(command)
    subprocess.call(command)

def get_feature_imp(feature_imp):
    fea_imp = pd.DataFrame(pd.Series(feature_imp))
    df_imp=fea_imp.reset_index(drop=False).rename(columns = {0:'var',"index":"rank"})
    df_imp['rank']= df_imp['rank'] + 1
    return df_imp


def model_check(df,filename):
    col_list = list(df.columns)
    flag = 0
    if 'label' in col_list:
        print(filename,"数据集中有以‘label’命名的变量，请改名！")
        flag = 1
    if 'pred' in col_list:
        print(filename,"数据集中有以‘pred’命名的变量，请改名！")
        flag = 1
    if 'dt' in col_list:
        print(filename,"数据集中有以‘dt’命名的变量，请改名！")
        flag = 1
#    if flag == 0:
#        print('Model Check Pass!')
    return flag
    
def get_html_report(data_folder,feature_imp,output_path=os.getcwd(),rename_rule={'mob3_k11':'label','xgb':'pred','trans_date':'dt'},special_value=[-999],cut = None,
                    model_name = 'test',current_file=''):

    '''快速生成二分类模型的模型报告
    Parameters
    ----------
    data_folder : string       
    存放样本数据的路径。
    该路径下不可存放除样本数据以外的文件。
   
    output_path : str (default = os.getcwd())
    设置输出项路径，默认当先工作路径
    
    feature_imp : list      
    输入项列表，按重要性排序。
    
    rename_rule: dict, optional(default = {'mob3_k11':'label','xgb':'pred','trans_date':'dt'})
    固定命名规范:
     - 模型的应变量（如'mob3_k11'）统一命名为'label'
     - 模型的预测值（如'xgb'）统一命名为'pred'
     - 样本拆分的日期（如'trans_date'）统一命名为'dt'

     Note: 样本数据必须含有这三个变量。

    special_value : list, optional (default = [-999])
     列表包含样本缺失值的所有形式，如[-99,np.NaN,'null']。

    cut : list, optional (default = None)
    模型预测值的切点。

    model_name: string, optional (default = '') 
    模型的名称。
    
    current_file: string, optional (default = 'Untitled.ipynb')
    当前运行的jupyter notebook的文件名，用以生成html格式的模型报告。
    

    Returns
    ----------
    在工作目录中生成html格式的模型报告,文件名与model_name一致。
    在工作目录中生成报警特征在各份数据集上的分子风险趋势（马赛克图），文件名默认为'out_mosaic'，格式为png。

    Examples
    --------
    >>> model_name = 'demo_report'   
    >>> data_folder = './data_for_report'
    >>> output_path = './result'    
    >>> feature_imp = ['oplocdistrict','industryphy','industryco','enttype','enttypeitem','state']
    >>> cut = [ 0.000762, 0.0011,0.00235,0.0573,99]
    >>> rename_rule = {'SeriousDlqin2yrs':'label','score':'pred','date':'dt'}
    >>> special_value = [-99]
    >>>current_file = 'demo.ipynb'   
    >>>get_html_report(data_folder,output_path,feature_imp,rename_rule,special_value,
       cut,model_name,current_file)
    
    生成的报告请见'/Users/h00988/Desktop/Automan演示补充/Automan_20201113/demo.ipynb'
    '''
    df,flag = get_data(data_folder = data_folder,
              input_model = feature_imp,
              rename_rule = rename_rule,
              special_value = special_value)
    if flag == 1:
        pass
    else:
        display_html(f"<h1>{model_name}模型诊断报告</h1>",raw=True)
        
        display_html(f"<h1>1. 样本概况</h1>",raw=True)
        get_sample(df)
        
        display_html(f"<h1>2. 模型效果</h1>",raw=True)
        for f in df.flag.unique():
            get_model_all(df[df.flag==f].label,df[df.flag==f].pred,title=f+' ',cut= cut,n=10)
            
        display_html(f"<h1>3. 模型 PSI</h1>",raw=True)
        psi = get_model_psi(df.label,df.pred,df.flag,cut=cut)
        psi = psi[psi.index=='Total']
        sample_styler = psi.style.applymap(color_psi,subset=pd.IndexSlice['Total',:]).format("{:.3f}").set_properties(**{'width': '100px'})
        display_html(sample_styler._repr_html_(),raw=True)
        
        display_html(f"<h1>4. 模型变量分析</h1>",raw=True)
        inputx = sorted(set(df.columns) - set(['pred','label','flag','trans_date','event_date','shouxin_date','dt']))    
        
        display_html(f"<p>模型变量总共{len(inputx)}个</p>",raw=True)    
        display_html(f"<p>前端监控：与y无关的监控，主要看特征饱和度、特征分布稳定性PSI的指标。<br>\
                     后端监控：与y有关的监控，主要看特征在各样本的IV均值、IV最小值、最高最低组倍数、以及坏率的趋势一致性（相关性）的指标。 <br>\
                    <b>注意：只对重要性前10的特征进行报警处理</b></p>",raw=True)
        base_df,oot_df,vars_df = get_var_metrics(df, y='label', x_input = inputx, q=10,n=0.05,dt='shouxin_date',custom_range='flag')
        base_score = get_score(base_df)
        oot_score = get_score(oot_df)
        columns = get_feature_imp(feature_imp)
        vars_pk1,vars_pk2 = match_score(base_score,oot_score,columns)
        
        def color_abnormal(val):
            color = 'red' if val=='Alert' else '#008000' if val=='-'or val=='GOOD' else '#e6b528'
            return 'color: %s' % color
    
        def hover():
            return dict(selector = "tr:hover",props=[("background-color","#ffff99")])
        
        styles = [hover(),
                 dict(selector='th',props=[('border-style','solid'),
                                                     ('border-color','grey'),
                                                     ('border-width','0.1px'),
                                                     ('background-color','black'),
                                        
                                           ('color','white'),
                                                     ('font-size','120%'),
                                                     ('text-align','center')])
                 ]
        vars_pk2_styler  = vars_pk2.set_index('rank').style.set_properties(**{'border-color':'grey','border-style':'solid','border-width':'0.1px','border-collaps':'collaps'})\
            .set_table_styles(styles)\
                .set_properties(**{'font-size':'100%','text-align':'center','font-weight':'bold'},subset=['前端监控','后端监控'])\
                    .set_properties(**{'text-align':'left'},subset=['前端结论','后端结论'])\
                        .applymap(lambda x: 'white-space:nowrap')\
                            .applymap(color_abnormal,subset=['前端监控','后端监控'])
        
        display_html(vars_pk2_styler._repr_html_(),raw=True)
        
        
        plt.style.use('seaborn')
        pylab.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
        pylab.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题    
        vars_pk1['较上月变化'] = vars_pk1['综合评分_x']-vars_pk1['综合评分_y']    
        ordered_df = vars_pk1[vars_pk1['var'].isin(list(vars_pk2[(vars_pk2['前端监控']=='Alert')|(vars_pk2['后端监控']=='Alert')]['var']))].iloc[:,:-1].sort_values(by='综合评分_x')
        ordered_df = ordered_df[['var','综合评分_x','综合评分_y', '区分能力_x','区分能力_y', '数据稳定性_x','数据稳定性_y','区分能力稳定性_x','区分能力稳定性_y','单调性_x','单调性_y','饱和度_x','饱和度_y']]
        ordered_df.columns =['var']+ ['value'+str(i+1) for i in range(12)]
        my_range=range(1,len(ordered_df.index)+1)
        
        if len(ordered_df)==0:
            display_html(f"<p>重要性较高特征中无异常报警</p>",raw=True)
            save_html_report(path = output_path,current_file=current_file, model_name=model_name)
        else:
    
            t = ['综合评分','区分能力','数据稳定性','区分能力稳定性','单调性','饱和度']
            decrease = [300,150,100,150,100,100]
            plt.figure(figsize=(15,(len(ordered_df)/3)+1),dpi=96)
            for n in range(6):
                ax = plt.subplot(1,6,n+1)
                plt.yticks(my_range, ordered_df['var'])
                if n in [1,2,3,4,5]:
                    plt.tick_params(labelleft=False)
                this_month = ordered_df['value{}'.format((n+1)*2-1)]
                last_month = ordered_df['value{}'.format((n+1)*2)]
                line_color = np.where(this_month-last_month<=-decrease[n],'#f8766d',np.where(this_month-last_month>=decrease[n],'#00bfc4','grey'))
                dot_color1 = np.where(this_month-last_month==0,'#f8766d','#f8766d')
                dot_color2 = np.where(this_month-last_month==0,'#f8766d','#00bfc4')        
                plt.hlines(y=my_range, xmin=this_month, xmax=last_month, color=line_color, alpha=0.4)
                plt.scatter(this_month, my_range, color=dot_color1, alpha=0.7, label='this_month') # this month
                plt.scatter(last_month, my_range, color=dot_color2, alpha=0.7 , label='last_month') # last month
                plt.title(t[n])   
            display_html(f"<p>红点代表OOT数据集效果，蓝点代表训练集效果,红点在左侧代表效果下降。</p>",raw=True)
    
            
            display_html(f"<p>查看报警特征在各分数据集上的IV, 缺失率、PSI以及badrate相关性</p>",raw=True)
            for x in ordered_df['var'][::-1]:
                draw_x_plt(vars_df, x,mode='kde',name='')
                    
            
            display_html(f"<p>查看报警特征在各份数据集上的分子风险趋势（马赛克图）</p>",raw=True)
            for x in ordered_df['var'][::-1]:
                plt_multi_mosaic(df[(df.label.isin([0,1]))],
                                    x=x,
                                    y='label',q=10,bs=3,
                                    n=0.05,dt = 'dt',custom_range='flag',file=output_path+'\\out_mosaic.png', 
                                    name='')
            save_html_report(path = output_path,current_file=current_file, model_name=model_name)
