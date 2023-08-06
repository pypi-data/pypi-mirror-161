import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from optbinning import OptimalBinning as optbin
from optbinning.binning import auto_monotonic
from sklearn import metrics 
from sklearn import preprocessing
import scipy.stats as st

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager as fm
from  matplotlib import cm
from matplotlib.pyplot import style
style.use('seaborn-white')
from statsmodels.graphics.mosaicplot import mosaic
import pylab
pylab.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
pylab.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

import re
import os
import warnings
warnings.filterwarnings('ignore')
#%%

'''
2021/07/29 z00119 张玉婷更新 ，新增plt_multi_rsk_trend 风险趋势图和multi mosaic 优化，切点有最分箱工具。
2022/01/19 黄恺睿更新 修复bug 第一组画图不显示以及ifinit格式报错
2022/01/19 黄恺睿更新 新增get_start_date函数：用于查找变量起始日期，便于排除掉全空或者空值率较多的数据
'''

# 需要用到的函数
def full_describe(df):
    cat_vars = list(df.dtypes[df.dtypes=='O'].index)
    num_vars = list(df.dtypes[df.dtypes!='O'].index)
    miss_cat = pd.DataFrame(df[cat_vars].apply(lambda x :'{:.2%}'.format(1- x.count()/x.size)),columns=['miss%'])
    miss_num = pd.DataFrame(df[num_vars].apply(lambda x :'{:.2%}'.format(1- x.count()/x.size)),columns=['miss%'])
#    top = pd.DataFrame(df[cat_vars].apply(lambda x : x.value_counts()[:7].to_dict()),columns=['top'])
    top = pd.DataFrame({x: pd.Series([str(k)+': '+str(v) for k,v in df[x].value_counts()[:7].to_dict().items()]) for x in cat_vars}).T
    top.columns = ['value'+str(i+1) for i in range(7)]
    desc = df[cat_vars].describe().T[['count','unique']]
    cat_desc = pd.concat([miss_cat,desc,top],axis=1)
    num_desc = pd.concat([miss_num,df[num_vars].describe(percentiles=[0.95]).T],axis=1)
    return cat_desc,num_desc

    
# styling
range_color=['#16934d','#57b55f','#93d067','#c7e77f','#edf7a7','#fef1a6','#fdce7b','#fa9a57','#ee613d','#d22b26']
def color_pct(val):
    if val>=0.9:
        color = range_color[-1]
    elif val>=0.8 :
        color = range_color[-2]
    elif val>=0.7:
        color = range_color[-3]
    elif val>=0.6:
        color = range_color[-4]
    elif val>=0.5:
        color = range_color[-5]
    elif val>=0.4:
        color = range_color[-6]
    elif val>=0.3:
        color = range_color[-7]
    elif val>=0.2:
        color = range_color[-8]
    elif val>=0.1:
        color = range_color[-9]
    else:
        color = range_color[0]
    return 'background-color: %s' % color

def color_pct1(val):
    if val>=0.9 or val<0.1:
        color = '#fff'
    else:
        color = 'black'
    return 'color: %s' % color

def caculate_null(df,inputx,dt = 'shouxin_date',dt_cut='month'):
    null_rate = lambda a: (a.isin([-99,'-99'])).sum()/a.size
    zero_rate = lambda a: (a.isin([0,'0'])).sum()/a.size # 有些变量会有较多的0

    df[dt] = df[dt].astype('str').str[0:10].replace('-','').astype(int)
    # 判断跨时字段
    if isinstance(dt_cut,list):
        df[dt] = df[dt].astype('str').str.replace('-','').astype(int)
        df['dt_cut'] = pd.cut(df[dt],dt_cut).astype('object')
    else:
        df['dt_cut'] = df[dt_cut]
        
        
    var_df = pd.DataFrame()
    for x in inputx:
        the_var_df = df[x].groupby(df['dt_cut'])\
                    .describe(percentiles=[])[['count']]\
                    .assign( nullpct = df[x].groupby(df['dt_cut']).apply(null_rate))\
                    .assign( zeropct = df[x].groupby(df['dt_cut']).apply(zero_rate))
        the_var_df['var'] = x
        var_df= pd.concat([var_df,the_var_df])
    var_df_null = var_df.pivot_table(index='var',columns=var_df.index,values='nullpct',fill_value=0)
    var_df_zero = var_df.pivot_table(index='var',columns=var_df.index,values='zeropct',fill_value=0)
    
    return var_df_null,var_df_zero
    
def format_null(df):
    df.columns = [str(x) for x in df.columns]
    df = df.sort_values(by=df.columns[-1],ascending=False) # 降序排列
    df = (df.style.applymap(color_pct)
         .applymap(color_pct1)
         .format("{:.2%}")
         .set_properties(**{'font-family':'console','max-width':'10px','border-color':'grey','border-style':'solid','border-width':'0.05px','border-collaps':'collaps'})
        )
        
    return df

# Null Check Heatmap
# 查看变量缺失率情况，可自定义分样本
def out_null(df,inputx,dt = 'shouxin_date',dt_cut='month',isformat=True,file='output.xlsx'):
    var_df = caculate_null(df,inputx,dt = dt,dt_cut=dt_cut)
    
    if isformat:
        df_null = format_null(var_df[0])
        df_zero = format_null(var_df[1])
    else:
        df_null = var_df[0]
        df_zero = var_df[1]
    if file !=None:
        with pd.ExcelWriter(file) as writer:
            df_null.to_excel(writer,float_format="%.2f",freeze_panes=(1,0),sheet_name='空值率分布')
            df_zero.to_excel(writer,float_format="%.2f",freeze_panes=(1,0),sheet_name='0值率分布')
    else:
        pass  
    return {'df_null':df_null,'df_zero':df_zero}


#%% 变量分箱
# Auto Binning(qcut) 自动等频分箱
def auto_bin(df,x,y,q=20,n=0.05,cut=None):
    '''
    x ='tag1_影音视频_comentdown_pct'
    y='label'
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
        IV = round(np.sum(rate*bins_df.woe),3)
        return IV
    
    df = df[[x,y]].copy()
    
    if df[x].nunique()<=3 or pd.api.types.is_string_dtype(df[x]):
        bins = sorted(list(df[x].unique()))
        df['qcut'] = df[x]
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
    
        num_bins = [*zip(bins,bins[0:],count_y0,count_y1)] 
        
    elif cut!=None:
        bins = sorted(set(np.insert(cut,0,[-np.inf,np.inf])))
        df['qcut'] = df[x]
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
        
    else:
#        bins = sorted(df[x].quantile([i/q for i in range(q+1)]).drop_duplicates().values)#
        bins = [round(i,6) for i in sorted(df[x].quantile([i/q for i in range(q+1)]).drop_duplicates().values)]
#        df['qcut'],bins = pd.qcut(df[x],retbins=True,q = q,duplicates='drop')
        bins = sorted(set(np.insert(bins,0,[-np.inf,np.inf,-99])))
        df['qcut'] = pd.cut(df[x],bins,duplicates='drop')
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
    
        num_bins = [*zip(bins,bins[1:],count_y0,count_y1)] 
    
    special = num_bins[0]
    if special[1]==-99 or special[1]=='-99' or special[1]=='-99.0':
        num_bins.remove(special) 
        
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
  
    if special[1]==-99 or special[1]=='-99' or special[1]=='-99.0':
        num_bins.insert(0,special)
        
    bins_df = get_woe(num_bins)
    bins_df['var']=x
    bins_df['IV'] = get_iv(bins_df)
    
       
    #判断badrate是否单调,空值组不参与判断
    if bins_df.iloc[0,1]==-99 or bins_df.iloc[0,1]=='-99' or bins_df.iloc[0,1]=='-99.0':
        badRate = [round(i,3) for i in list(bins_df.bad_rate)[1:]]
        pct = list(bins_df.pct)[1:]
        missing_pct = bins_df.pct[0]
        
    else:
        badRate = [round(i,3) for i in list(bins_df.bad_rate)[0:]]
        pct = list(bins_df.pct)[0:]
        missing_pct = 0
        
    bs = [round(i/df[y].mean(),3) for i in badRate]
    
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



# 自定义切点 自动分箱
def manual_bin(df,x,y,cut=[],n=0.05):
    '''
    x ='tag1_教育学习_pop_sum'
    y='label'
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
    
    # 定义IV计算函数
    def get_iv(bins_df):
        rate = ((bins_df.count_0/bins_df.count_0.sum())-(bins_df.count_1/bins_df.count_1.sum()))
        IV = round(np.sum(rate*bins_df.woe),3)
        return IV
    
    df = df[[x,y]].copy()
    if df[x].nunique()<=3 or pd.api.types.is_string_dtype(df[x]):
        bins = sorted(set(str(x) for x in list(df[x].unique())))
        df['qcut'] = df[x].astype('str')
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
    
        num_bins = [*zip(bins,bins[0:],count_y0,count_y1)] 
        
        special = num_bins[0]
        if special[1]==-99 or special[1]=='-99' or special[1]=='-99.0':
            num_bins.remove(special)
            
        for i in range(len(bins)):
            if len(num_bins)>1:            
                if 0 in num_bins[0][2:] or sum(num_bins[0][2:])/df.shape[0] <=n:
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
        
        if special[1]==-99 or special[1]=='-99' or special[1]=='-99.0':
            num_bins.insert(0,special)
        
    else:
        cut = [float(i) for i in cut]
        bins = sorted(set(np.insert(cut,0,[-np.inf,-99.0,np.inf])))
        df['qcut'] = pd.cut(df[x],bins)
        count_y0 = df.groupby(by='qcut')[y].count() - df.groupby(by='qcut')[y].sum()
        count_y1 = df.groupby(by='qcut')[y].sum()
    
        num_bins = [*zip(bins,bins[1:],count_y0,count_y1)] 
        

   
    bins_df = get_woe(num_bins)
#     print(f"{x}分{len(num_bins):2}组 IV值：", get_iv(bins_df))
    bins_df['var']=x
    bins_df['IV'] = get_iv(bins_df)
    
       
    #判断badrate是否单调,空值组不参与判断
    if bins_df.iloc[0,1]==-99 or bins_df.iloc[0,1]=='-99' or bins_df.iloc[0,1]=='-99.0':
        badRate = [round(i,3) for i in list(bins_df.bad_rate)[1:]]
        pct = list(bins_df.pct)[1:]
        missing_pct = bins_df.pct[0]
        
    else:
        badRate = [round(i, 3) for i in list(bins_df.bad_rate)[0:]]
        pct = list(bins_df.pct)[0:]
        missing_pct = 0
        
    bs = [round(i/df[y].mean(),3) for i in badRate]
    
    if sorted(badRate) == badRate or sorted(badRate) == badRate[::-1]:
        BRMonotone = 1
    else:
        BRMonotone = 0
    

    bins_df['is_Monotone'] = BRMonotone
    
    #输出最高组，最低组风险倍数,空值组不参与判断
    bins_df['max_bs'] = max(bs) if bs else 0
    bins_df['min_bs'] = min(bs) if bs else 0
    
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

#%%
def color_iv(val):
    if val>=0.5:
        color = range_color[0]
    elif val>=0.3 :
        color = range_color[1]
    elif val>=0.1:
        color = range_color[2]
    elif val>=0.05:
        color = range_color[3]
    elif val>=0.03:
        color = range_color[4]
    elif val>=0.02:
        color = range_color[5]
    elif val>=0.01:
        color = range_color[6]
    else:
        color = range_color[7]
    return 'background-color: %s' % color

def color_iv1(val):
    if val>=0.5 or val<0.01:
        color = '#fff'
    else:
        color = 'black'
    return 'color: %s' % color

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

def caculate_iv(df,inputx,y,dt = 'shouxin_date',q=10,n=0.03,dt_cut='month'):
    # 样本切分
    df[dt] = df[dt].astype('str').str[0:10].replace('-','').astype(int)
    # 判断跨时字段
    if isinstance(dt_cut,list):
        df[dt] = df[dt].astype('str').str.replace('-','').astype(int)
        df['dt_cut'] = pd.cut(df[dt],dt_cut).astype('object')
    else:
        df['dt_cut'] = df[dt_cut]
        #     特征分箱 每份样本按照同一份分箱计算。

    var_df = pd.DataFrame()
    for x in inputx:
        print(x)
        #     特征分箱 每份样本按照同一份分箱计算。
        bins = auto_bin(df,x,y,q=q,n=n)[1]
        if df[x].nunique()<=3 or pd.api.types.is_string_dtype(df[x]):
            df['x_cut'] = [x if x in bins else bins[-1] for x in df[x]]
        else:
            df['x_cut'] = pd.cut(df[x],sorted(set(bins)))
             

        iv_list = df.groupby(df['dt_cut']).apply(lambda k: cal_iv(k['x_cut'],k[y])[0])
        ks_list = df.groupby(df['dt_cut']).apply(lambda tt: cal_ks(tt,x,y))
        the_var_df = pd.DataFrame([iv_list,ks_list]).T
        the_var_df.columns = ['IV','KS']
        the_var_df['var'] = x    
        
        var_df= pd.concat([var_df,the_var_df])

    var_df_iv = var_df.pivot_table(index='var',columns=var_df.index,values='IV',fill_value=0)
    var_df_ks = var_df.pivot_table(index='var',columns=var_df.index,values='KS',fill_value=0)
    return var_df_iv,var_df_ks
    
def format_iv(df):
    df.columns = [str(x) for x in df.columns]
    df = df.sort_values(by=df.columns[-1],ascending=False) # 降序排列
    df = (df.style.applymap(color_iv)
         .applymap(color_iv1)
         .format("{:.3f}")
         .set_properties(**{'font-family':'console','max-width':'10px','border-color':'grey','border-style':'solid','border-width':'0.05px','border-collaps':'collaps'})
        )
        
    return df

# IV check Heatmap
# 基于auto_bin
def out_iv(df,inputx,y,dt = 'shouxin_date',dt_cut='month',q=10,n=0.03,isformat = True,file='output.xlsx'):
    
    var_df = caculate_iv(df,inputx,y,dt = dt,q=q,n=n,dt_cut=dt_cut)

    if isformat:
        df_iv = format_iv(var_df[0])
        df_ks = format_iv(var_df[1])
    else:
        df_iv = var_df[0]
        df_ks = var_df[1]
        
    if file !=None:
        with pd.ExcelWriter(file) as writer:
            df_iv.to_excel(writer,float_format="%.3f",freeze_panes=(1,0),sheet_name='IV值分布')
            df_ks.to_excel(writer,float_format="%.3f",freeze_panes=(1,0),sheet_name='KS值分布')
    else:
        pass  
    return {'df_iv':df_iv,'df_ks':df_ks}

def out_psi(df,inputx,y,dt,q,n,dt_cut='month'):
    '''
    将样本按时间等切成2份，以最后一份为基准，计算前1份的psi，取最大值
    由于资信接入时间不等，会导致第一份样本空值组psi大，影响判断结果。仅看非空值部分psi，
    空值的波动从空值率函数看
    '''
    psi = pd.DataFrame()
    badpsi = pd.DataFrame()
    for x in inputx:
        print(x)
        tmpdf = df[~df[x].isin([-99,'-99','-99.0'])].copy()
        
        tmpdf[dt] = tmpdf[dt].astype('str').str[0:10].replace('-','').astype(int)
        # 判断跨时字段
        if isinstance(dt_cut,list):
            tmpdf[dt] = tmpdf[dt].astype('str').str.replace('-','').astype(int)
            tmpdf['dt_cut'] = pd.cut(tmpdf[dt],dt_cut).astype('object')
        else:
            tmpdf['dt_cut'] = df[dt_cut]
    
        if len(tmpdf)<=20 or tmpdf[y].mean()==0:
            A = B = pd.DataFrame([[0]*tmpdf['dt_cut'].nunique()],columns = tmpdf['dt_cut'].unique())
            A['var'] = x
            B['var'] = x
        else:
            if pd.api.types.is_string_dtype(tmpdf[x]) and tmpdf[x].nunique()>3:
                le = preprocessing.LabelEncoder()
                le.fit(tmpdf[x])
                tmpdf[x] = le.transform(tmpdf[x])
    
            if tmpdf[x].nunique()<=3:
                tmpdf['group'] = df[x]
            else:
                bins = auto_bin(tmpdf,x,y,q,n)[1]
                tmpdf['group'] = pd.cut(tmpdf[x],bins)
            
            a = tmpdf.pivot_table(index=['dt_cut','group'],values=[x],aggfunc=np.size,fill_value=0)
    #        a.columns = ['bad']
            a = a.unstack(level=0)
            pct = a/a.sum()
    #            pct.columns=[o for o in range(len(tmp_dates)-1)]
            pct['bench'] =pct.iloc[:,0] 
            
            b = tmpdf.pivot_table(index=['dt_cut','group'],values=[y],aggfunc=np.sum,fill_value=0)
    #        b.columns = ['bad']
            b = b.unstack(level=0)
            bpct = b/b.sum()
    #            bpct.columns=[o for o in range(len(tmp_dates)-1)]
            bpct['bench'] =bpct.iloc[:,0] 
            
            A = pd.concat([(pct.iloc[:,i]-pct.iloc[:,-1])*np.log(pct.iloc[:,i]/pct.iloc[:,-1]) for i in range(pct.shape[1])],axis=1)
            A = pd.DataFrame(A.sum()).T.iloc[:,:-1]
            A.columns = a.columns.levels[1]
            A['var'] = x
            B = pd.concat([(bpct.iloc[:,i]-bpct.iloc[:,-1])*np.log(bpct.iloc[:,i]/bpct.iloc[:,-1]) for i in range(bpct.shape[1])],axis=1)
            B = pd.DataFrame(B.sum()).T.iloc[:,:-1]
            B.columns = b.columns.levels[1]
            B['var'] = x
            
        psi = pd.concat([psi,A])
        badpsi = pd.concat([badpsi,B])

    return psi,badpsi


def out_psi2(df,inputx,dt,q,n,dt_cut='month' ):
    '''
    将样本按时间等切成2份，以最后一份为基准，计算前1份的psi，取最大值
    由于资信接入时间不等，会导致第一份样本空值组psi大，影响判断结果。仅看非空值部分psi，
    空值的波动从空值率函数看
    '''
    psi = pd.DataFrame()
    for x in inputx:
        print(x)
        tmpdf = df[~df[x].isin([-99,'-99','-99.0'])].copy()
        
        tmpdf[dt] = tmpdf[dt].astype('str').str[0:10].replace('-','').astype(int)
        # 判断跨时字段
        if isinstance(dt_cut,list):
            tmpdf[dt] = tmpdf[dt].astype('str').str.replace('-','').astype(int)
            tmpdf['dt_cut'] = pd.cut(tmpdf[dt],dt_cut).astype('object')
        else:
            tmpdf['dt_cut'] = tmpdf[dt_cut]
    
        if len(tmpdf)<=20:
            A = pd.DataFrame([[0]*tmpdf['dt_cut'].nunique()],columns = tmpdf['dt_cut'].unique())
            A['var'] = x
        else:
            if pd.api.types.is_string_dtype(tmpdf[x]) and tmpdf[x].nunique()>3:
                le = preprocessing.LabelEncoder()
                le.fit(tmpdf[x])
                tmpdf[x] = le.transform(tmpdf[x])
    
            if tmpdf[x].nunique()<=3:
                tmpdf['group'] = df[x]
            else:   
                tmpdf['group'] = pd.qcut(tmpdf[x].rank(method='first'),10,duplicates='drop')
            
            a = tmpdf.pivot_table(index=['dt_cut','group'],values=[x],aggfunc=np.size,fill_value=0)
    #        a.columns = ['bad']
            a = a.unstack(level=0)
            pct = a/a.sum()
    #            pct.columns=[o for o in range(len(tmp_dates)-1)]
            pct['bench'] =pct.iloc[:,0] 
            
            A = pd.concat([(pct.iloc[:,i]-pct.iloc[:,-1])*np.log(pct.iloc[:,i]/pct.iloc[:,-1]) for i in range(pct.shape[1])],axis=1)
            A = pd.DataFrame(A.sum()).T.iloc[:,:-1]
            A.columns = a.columns.levels[1]
            A['var'] = x
            
        psi = pd.concat([psi,A])

    return psi
    

# 单马赛克图，可自定义切点
def plt_mosaic(df, y, ilx, output_path,cut=False, q=10,n=0.05,dt='shouxin_date',bs = 5, show=False,plot=False):
    '''
    x ='credit_device_score_ppx'
    y='fpd4'
    '''
    def isnum(a):
        if isinstance(a,float):
            return str(round(a,3))
        else:
            return a
            
    def get_psi(df,x,y,dt,q,n ):
        '''
        将样本按时间等切成2份，以最后一份为基准，计算前1份的psi，取最大值
        由于资信接入时间不等，会导致第一份样本空值组psi大，影响判断结果。仅看非空值部分psi，
        空值的波动从空值率函数看
        '''
        tmpdf = df[~df[x].isin([-99,'-99','-99.0'])].copy()
        if len(tmpdf)<=20 or tmpdf[y].mean()==0:
            max_psi = 0
            max_bdpsi = 0
            tmp_dates = []
            iv_list = pd.DataFrame([0])
        else:
            tmp_dates= sorted(set(df[dt].quantile([0,0.5,1]).astype(int)))
            df['m_cut'] = pd.cut(df[dt],tmp_dates,include_lowest=True).astype('str').str.replace('\.0|\.999','')
            if pd.api.types.is_string_dtype(df[x]) and df[x].nunique()>3:
                le = preprocessing.LabelEncoder()
                le.fit(df[x])
                df[x] = le.transform(df[x])
    
            if df[x].nunique()<=3:
                df['group'] = df[x]
            else:
                bins = auto_bin(df,x,y,q,n)[1]
                df['group'] = pd.cut(df[x],bins)
            
            iv_list = df.groupby(df['m_cut']).apply(lambda k: "{:.2f}".format(cal_iv(k['group'],k[y])[0]))
            iv_list = pd.DataFrame(iv_list,columns=[' '])
            iv_list.index.names=['跨时IV']
            
            tmpdf = df[~df[x].isin([-99,'-99','-99.0'])].copy()
            a = tmpdf.pivot_table(index=['m_cut','group'],values=[x],aggfunc=np.size,fill_value=0)
            a.columns = ['bad']
            a = a.unstack(level=0)
            pct = a/a.sum()
#            pct.columns=[o for o in range(len(tmp_dates)-1)]
            pct['bench'] =pct.iloc[:,-1] 
            
            b = tmpdf.pivot_table(index=['m_cut','group'],values=[y],aggfunc=np.sum,fill_value=0)
            b.columns = ['bad']
            b = b.unstack(level=0)
            bpct = b/b.sum()
#            bpct.columns=[o for o in range(len(tmp_dates)-1)]
            bpct['bench'] =bpct.iloc[:,-1] 
            
            A = pd.concat([(pct.iloc[:,i]-pct.iloc[:,-1])*np.log(pct.iloc[:,i]/pct.iloc[:,-1]) for i in range(pct.shape[1])],axis=1)
            B = pd.concat([(bpct.iloc[:,i]-bpct.iloc[:,-1])*np.log(bpct.iloc[:,i]/bpct.iloc[:,-1]) for i in range(bpct.shape[1])],axis=1)
            max_psi = max(A.sum())
            max_bdpsi = max(B.sum())
        return max_psi,max_bdpsi,tmp_dates,iv_list
    
    if os.path.exists(output_path):
        pass
    else:
        os.makedirs(output_path)
    i = 0
    bins_df = pd.DataFrame()
    vars_df = pd.DataFrame()
    for x in ilx:
        print(i, x)
        # 数据准备
        if cut:
            the_bins_df = manual_bin(df,x,y,cut=cut,n=n)[0]
        else:
            the_bins_df = auto_bin(df,x,y,q=q,n=n)[0]
        max_psi,max_bdpsi,tmp_dates,iv_list = get_psi(df,x,y,dt,q=q,n=n)
        the_bins_df['psi'] = max_psi
        the_bins_df['Badpsi'] = max_bdpsi
        the_bins_df['min_cross_IV'] = iv_list.min()[0]
        the_var_df = the_bins_df[['var','IV','is_Monotone','max_bs','min_bs','max_bs_pct','min_bs_pct','missing_pct','psi','Badpsi','min_cross_IV']].drop_duplicates()
        bins_df = pd.concat([bins_df,the_bins_df])
        vars_df = pd.concat([vars_df,the_var_df])
        
        #画图
        if plot:
            result_plot = the_bins_df[['count_1','count_0']]
            result_plot.index = ['{}_({},{}]'.format(j,isnum(m),isnum(l)) for j,m,l in zip(the_bins_df.index,the_bins_df['min'],the_bins_df['max'])]
            result_plot.columns = ['Yes','No']
            # 此处为防止以风险为因变量时，mosaic图中风险为'Y'部分太小，因此把风险在图中的效果扩大
            
            result_plot_pct = (result_plot.T / result_plot.sum(axis=1)).T
            result_plot = result_plot.reset_index()
            result_plot.loc[:,'Yes'] = result_plot['Yes']*bs
            result_plot = result_plot[(result_plot.Yes!=0)&(result_plot.No!=0)]
            
            labelizer_dic = {}
            for s in result_plot_pct.index:
                for t in result_plot_pct.columns:
                    labelizer_tup = (str(s), t)
                    labelizer_dic[labelizer_tup] = '%.2f%%' % (result_plot_pct.loc[s, t] * 100)
            labelizer = lambda k: labelizer_dic[k]            
            props = lambda key: {'color': 'coral' if 'Yes' in key else 'silver'}

            mosaic(result_plot.set_index('index').stack(), 
                   title='{}|IV={:.3f}'.format(x, the_bins_df['IV'][0]), 
                   properties=props,
                   labelizer=labelizer, 
                   gap=0.01,
                   label_rotation=90)
    #        
    #        # 图上写信息        
            plt.text(1.05, 0.95, '样本量：{}'.format(len(df)))
            plt.text(1.05, 0.85, '平均风险：{:.2%}'.format(df[y].mean())) 
            
            plt.text(1.05, 0.75, '区分能力：') 
            plt.text(1.05,0.63,'  top_倍数(占比)：\n  {:.2f} ({:.1%})'.format(the_bins_df['max_bs'][0],the_bins_df['max_bs_pct'][0]))
            plt.text(1.05,0.51,'  bottom_倍数(占比)：\n  {:.2f} ({:.1%})'.format(the_bins_df['min_bs'][0],the_bins_df['min_bs_pct'][0]))
            
            plt.text(1.05, 0.42, '稳定性：') 
            plt.text(1.05,0.37,'  psi：{:.2f}'.format(the_bins_df['psi'][0]))
            plt.text(1.05,0.32,'  badpsi：{:.2f}'.format(the_bins_df['Badpsi'][0]))
            
            plt.text(1.05,0.1,'{}'.format(iv_list))
    
    
            # 存图
            if show:
                plt.show()
            else:
                plt.savefig('{}{}_{:.3f}_{}.png'.format(output_path,
                                                        the_bins_df['is_Monotone'][0],
                                                        the_bins_df['IV'][0], 
                                                        re.sub(r"[\/\\\:\*\?\"\<\>\|]", '',x)), 
                            pad_inches=0.3, dpi=100, papertype='a4',bbox_inches='tight')
                plt.close()     
            

        i = i + 1
        
    vars_df =  vars_df.sort_values(by='IV',ascending=False)
    vars_df.to_csv(output_path+'vars_df.csv',index=0)
    bins_df.to_csv(output_path+'bins_df.csv',index=0)
    return bins_df,vars_df


def get_psi(df,x,dt,q=10,cut='month' ):
    '''
    将样本按时间等切成2份，以最后一份为基准，计算前1份的psi，取最大值
    由于资信接入时间不等，会导致第一份样本空值组psi大，影响判断结果。仅看非空值部分psi，
    空值的波动从空值率函数看
    '''
    tmpdf = df[~df[x].isin([-99,'-99','-99.0'])].copy()
    if len(tmpdf)<=20 :
        max_psi = 0
    else:
        if cut!='month':
            
            tmp_dates= sorted(set(tmpdf[dt].quantile([0,0.5,1]).astype(int)))
            tmpdf['m_cut'] = pd.cut(tmpdf[dt],tmp_dates,include_lowest=True).astype('str').str.replace('\.0|\.999','')
        else:
            tmpdf['m_cut'] = tmpdf['month']
        if pd.api.types.is_string_dtype(tmpdf[x]) and tmpdf[x].nunique()>3:
            le = preprocessing.LabelEncoder()
            le.fit(tmpdf[x])
            tmpdf[x] = le.transform(tmpdf[x])

        if tmpdf[x].nunique()<=3:
            tmpdf['group'] = tmpdf[x]
        else:
            bins = [round(i,6) for i in sorted(tmpdf[x].quantile([i/q for i in range(q+1)]).drop_duplicates().values)]
            bins = sorted(set(np.insert(bins,0,[-np.inf,np.inf])))
            tmpdf['group'] = pd.cut(tmpdf[x],bins)
        
        a = tmpdf.pivot_table(index=['create_date','group'],values=[x],aggfunc=np.size,fill_value=0)
        a.columns = ['total']
        a = a.unstack(level=0)
        pct = a/a.sum()
#            pct.columns=[o for o in range(len(tmp_dates)-1)]
        pct['bench'] =pct.iloc[:,-1] 
        
    
        A = pd.concat([(pct.iloc[:,i]-pct.iloc[:,-1])*np.log(pct.iloc[:,i]/pct.iloc[:,-1]) for i in range(pct.shape[1])],axis=1)
        max_psi = max(A.sum())
    return max_psi

#%%
    

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

        
#%%
# 适用于变量，字段； 字符型、数值型变量均会自动分箱
def plt_multi_mosaic(df,x,y='fpd4',miss_values=[-99],bs=3,
                     dt ='event_date',dt_cut='month',
                     score_cut=None,if_plot=True,output_path=None):
    '''
    Parameters
    ----------
    df : pd.dataframe
        输入dataframe,需包含y，dt.
    x : string
        模型分 如'ali_cs_duotou_score',连续值
    y : string
        样本的因变量 如 'fpd4', 因变量只能为0,1的int格式输入.
    miss_values: list
        缺失值列表，缺失值单独一箱
    bs: int
        风险过低时放大风险
    dt : string, int,optional
        样本拆分的日期，一般我们建模中常用的，建案时间，交易时间等等。格式为 20190101、2019-01-01均可. The default is 'event_date'.
    n : int, optional
        特征等频分箱的组数，默认q=10，等频分为10箱. The default is 10.
    dt_cut : list, optional
        样本拆分月自定义切点，list自定义 如:[-np.inf,20190101,20190601,20190901,np.inf]
        或者指定某一列 如'shouxin_month','month1' 等
    score_cut : list,int, optional
        默认是None 自动分箱,数字为等频分箱，list为切点分箱
    if_plot : bool 
        默认True, 默认直接画图
    output_path ： 存储地址
        默认None 时 不存图，仅展示图片

    Returns
    -------
    plot图片.
    bins -- 模型分的切点，可用在别的样本分组上
    mono 整体样本单调趋势
    '''
    def transform_dic(bins):
        l = []
        for i in range(len(bins)):
            for j in bins[i].tolist():
                temp = [j]+[i]
                l.append(temp)
        return dict(l)

    temp_df = df[[x,y,dt]]
    temp_df[dt] = df[dt].astype('str').str[0:10].replace('-','').astype(int)
    # 判断跨时字段
    if isinstance(dt_cut,list):
        temp_df[dt] = temp_df[dt].astype('str').str.replace('-','').astype(int)
        temp_df['dt_cut'] = pd.cut(temp_df[dt],dt_cut).astype('object')
    else:
        temp_df['dt_cut'] = df[dt_cut]

    temp_df[x] = temp_df[x].replace(miss_values,-99)
        
    if temp_df[x].nunique()<=8: # 数值个数8个以内不用分箱
        temp_df['group'] = temp_df[x]
        bins = sorted(temp_df[x].unique())
    else:
        if pd.api.types.is_string_dtype(temp_df[x]):# 字符型变量自动分箱
            temp_df[x] = temp_df[x].replace(miss_values,'-99')
            train_df = temp_df[temp_df[x]!='-99'].sample(frac=0.5,random_state=1)
            optb = optbin(name=x,dtype='categorical',solver='mip',special_codes=miss_values)
            optb.fit(train_df[x].values,train_df[y])
            bins = optb.splits
            temp_df[x] = optb.transform(temp_df[x],metric='indices')
            temp_df[x] = np.where(temp_df[x]>len(bins),-99,temp_df[x])
            temp_df['group'] = temp_df[x]
        elif score_cut==None:
            temp_df[x] = temp_df[x].fillna(-99)
            temp_df[x] = temp_df[x].replace(miss_values,-99)
            train_df = temp_df[temp_df[x]!=-99].sample(frac=0.5,random_state=1)
            optb = optbin(name=x,dtype='numerical',solver='cp',special_codes=miss_values)
            optb.fit(train_df[x].values,train_df[y])
            bins = optb.splits
            if temp_df[temp_df[x] == -99].shape[0] > 0:
                bins = sorted(set(np.insert(bins,0,[-np.inf,-99,np.inf])))
            else:
                bins=sorted(set(np.insert(bins,0,[-np.inf,np.inf])))
            temp_df['group'] = pd.cut(temp_df[x],bins)
        elif isinstance(score_cut,list):
            bins = sorted(set(np.insert(score_cut,0,[-np.inf,-99,np.inf])))
            temp_df['group'] = pd.cut(temp_df[x],bins)
        else:
            _,bins = pd.qcut(temp_df[x],score_cut,duplicates='drop',retbins=True)
            bins = [float(cut_) for cut_ in bins]
            bins[0] = -99
            bins[-1] = np.inf
            if temp_df[temp_df[x] == -99].shape[0] > 0:
                bins = sorted(set(np.insert(bins,0,[-np.inf,-99,np.inf])))
            else:
                bins=sorted(set(bins))
            temp_df['group'] = pd.cut(temp_df[x],bins)
# 算psi

    c = temp_df.pivot_table(index=['group'],values=[y],columns='dt_cut',aggfunc=[len],fill_value=0)
    a = c.droplevel([0,1],axis=1)
    pct = a/a.sum()
    A = pd.concat([(pct.iloc[:,i]-pct.iloc[:,0])*np.log(pct.iloc[:,i]/pct.iloc[:,0]) for i in range(pct.shape[1])],axis=1)
    A.columns = pct.columns
    psi = A.sum()
    pct = pct.fillna(0.000001)
    
    tot_size = temp_df[y].shape[0] 
    tot_y = temp_df[y].sum()/tot_size   
    tot_iv = cal_iv(temp_df['group'],temp_df[y])[0]
    tot_ks = cal_ks(temp_df,x,y)
    tot_missing = temp_df[temp_df[x].isin([-99,'-99'])].shape[0]/temp_df.shape[0]
    dt_range = (str(temp_df[dt].min()) + '~' + str(temp_df[dt].max())).replace('-','')
    tot_c= temp_df[~temp_df[x].isin([-99,'-99'])].pivot_table(index=['group'],values=[y],aggfunc=[lambda x:sum(x)/len(x)],fill_value=0)
    tot_mono = auto_monotonic.type_of_monotonic_trend(np.array(tot_c.iloc[:,-1]))
    tot_lift = tot_c/tot_y
    

    max_psi = psi.max()
    bottom_lift =tot_lift.iloc[0,-1] # 非空组的第一组均值 整体样本
    top_lift = tot_lift.iloc[-1,-1]# 非空组的最后一组 

    # 不画图的时候，输出字段在整个样本的效果情况
    out_tb = pd.DataFrame([tot_missing,max_psi,tot_iv,tot_ks,bottom_lift,top_lift,tot_mono]).T
    out_tb.columns = ['total_missing','max_psi','total_iv','total_KS','bottom_lift','top_lift','total_trend']
    out_tb['variable'] = x
    out_tb = out_tb.set_index('variable')    
    
    if if_plot:
    # 总iv， 总样本概况
        ynum_list = temp_df.groupby(temp_df['dt_cut'])[y].apply(lambda x:sum(x))
        y_list = temp_df.groupby(temp_df['dt_cut'])[y].apply(lambda x:sum(x)/len(x))   
        num_list = temp_df.groupby(temp_df['dt_cut'])[y].apply(lambda x:len(x))   
        iv_list = temp_df.groupby(temp_df['dt_cut']).apply(lambda k: cal_iv(k['group'],k[y])[0])
        ks_list = temp_df.groupby(temp_df['dt_cut']).apply(lambda k1: cal_ks(k1,x,y))
    
        c = temp_df.pivot_table(index=['group'],values=[y],columns='dt_cut',aggfunc=[len,np.sum,lambda x:sum(x)/len(x)],fill_value=0)
        c.columns.set_levels(['len','sum','ratio'], level=0,inplace=True)
        c = c.droplevel(1,axis=1)
        lift = c['ratio']/y_list
        lift.columns = pd.MultiIndex.from_product([['lift'],lift.columns])
        pct.columns = pd.MultiIndex.from_product([['pct'],pct.columns])
        c = pd.concat([c,lift,pct],axis=1).fillna(0.000001)
        #画分时段马赛克图        
        l = sorted(set(temp_df['dt_cut']))

        fig = plt.figure(figsize=(5*len(l),4))
        fig.suptitle('{},{}, 总样本量：{}, 时间跨度:{}, 总IV:{:.2f}, 总KS:{:.2f}, \n\n总空值率:{:.2%}, 总趋势:{}'.format(x,y,tot_size,dt_range,tot_iv,tot_ks,tot_missing,tot_mono), 
                     x = 0.1, y = 1.2, ha='left',size=15,bbox = dict(facecolor = 'grey',alpha=0.1))

        for k in l:  
            i = l.index(k)
            max_bs = c[('ratio',k)].iloc[-1]/y_list[k] # 最后一箱的风险
            max_pct = c['pct'][k].iloc[-1]# 最后一箱的占比
            max_badn = c[('sum',k)].iloc[-1]# 最后一箱的坏客户数
            
            if temp_df[temp_df[x] == -99].shape[0] > 0: # 判断是否有空箱
                min_bs = c[('ratio',k)].iloc[1]/y_list[k] 
                min_pct = c['pct'][k].iloc[1]# 第一箱的占比
                min_badn = c[('sum',k)].iloc[1]# 第一箱的坏客户数
            else:
                min_bs = c[('ratio',k)].iloc[0]/y_list[k]
                min_pct = c['pct'][k].iloc[0]# 第一箱的占比
                min_badn = c[('sum',k)].iloc[0]# 第一箱的坏客户数
                
            bad_rate = [i if i*bs>1 else i*bs for i in c['ratio'][k]]
            the_pct = c['pct'][k]
            x_pos =[0]+ list(np.cumsum(the_pct))[:-1]
            # y_label_pos = [round(bad_rate[0]/2,4),bad_rate[0]+round((1-bad_rate[0])/2,4)]
            x_label_pos = []
            for j in range(len(list(the_pct))):
                if j ==0:
                    x_label_pos.append(round(list(the_pct)[j]/2,4))
                else:
                    x_label_pos.append(round((sum(list(the_pct)[:j])+list(the_pct)[j]/2),4))       
            ax = plt.subplot(1,len(l),i+1)
            ax.text(0, 0.9, " 首:{:.1f}倍,{}个,占比{:.1%}; \n 尾:{:.1f}倍,{}个,占比{:.1%}".format(min_bs,min_badn,min_pct,max_bs,max_badn,max_pct),  fontdict={'size': '11', 'color': 'b'}) # 写平均风险值
            ax.set_title(' {}, 样本：{}/{}({:.2%}), \n IV:{:.2f}, KS:{:.2f}, PSI:{:.2f}'.format(str(k).replace('.0',''),ynum_list[k],num_list[k],y_list[k],iv_list[k],ks_list[k], psi[k]),size = 12) #表标题

            ax.bar(x_pos,[1]*len(bad_rate), width=the_pct, align='edge',ec='w',lw=1,label='N',color='silver',alpha=0.8)
            ax.bar(x_pos,bad_rate,width=the_pct,align='edge',ec='w',lw=1,label='Y',color='coral',alpha=0.8)
            ax.axhline(y =y_list[k]*bs,color='r',label='warning line1',linestyle='--',linewidth=1)
            ax.text(0.95,y_list[k]*bs+0.05,'avg:'+str(round(y_list[k]*100,1)),ha='center',fontsize=9,color='r')
            ax.set_xticks(x_label_pos)
            # ax.set_yticks(y_label_pos)
            ax.set_xticklabels([str(x) for x in list(c.index)],rotation=90,fontsize=10)
            # ax.set_yticklabels(['Y','N'])    
            for n1,n2,n3 in zip(x_label_pos,bad_rate,[i/bs for i in bad_rate]):
                ax.text(n1,n2/2,str(round(n3*100,1)),ha='center',fontsize=9)
    
                # 存图
        if output_path==None:

            plt.show()

        else:   
            if os.path.exists(output_path):
                pass
            else:
                os.makedirs(output_path)
            fig.savefig('{}{}_{:.3f}_{}.png'.format(output_path,
                                                        tot_mono,
                                                        tot_iv, 
                                                        re.sub(r"[\/\\\:\*\?\"\<\>\|]", '',x)), 
                            pad_inches=0.3, dpi=100, papertype='a4',bbox_inches='tight')
            plt.close()   
        
        
    return bins,out_tb


#%%
# 用于查找变量起始日期，便于排除掉全空或者空值率较多的数据

def get_start_date(df,x,dt='dt',miss_values=[-99]):
    '''
    Parameters
    ----------
    df : pd.dataframe
        输入dataframe,需包含,dt.
    x : string
        模型分 如'ali_cs_duotou_score',连续值
    miss_values: list
        缺失值列表，缺失值单独一箱
    dt : string, int,optional
        样本拆分的日期，一般我们建模中常用的，建案时间，交易时间等等。格式为 20190101、2019-01-01均可. The default is 'event_date'.

    Returns
    -------
    资信起始日期，格式为int，yyyymmdd
    '''
    temp_df = df[[x,dt]].copy()
    temp_df[dt] = temp_df[dt].apply(lambda x:int(str(x)[:10].replace('-','')))
    if pd.api.types.is_string_dtype(temp_df[x]):# 字符型变量
        temp_df[x] = temp_df[x].replace(miss_values,'-99')
        null_count = temp_df.loc[(temp_df[x]=='-99')][dt].value_counts()
        total_count = temp_df[dt].value_counts().sort_index()
        full_count = len(set(total_count.index) - set(null_count.index))
        null_count = pd.concat([null_count,pd.Series([0]*full_count,index=set(total_count.index) - set(null_count.index))])
        null_count = null_count.sort_index()
        saturation = 1-null_count/total_count
    else:
        temp_df[x] = temp_df[x].replace(miss_values,-99)
        null_count = temp_df.loc[(temp_df[x]==-99)][dt].value_counts()
        total_count = temp_df[dt].value_counts().sort_index()
        full_count = len(set(total_count.index) - set(null_count.index))
        null_count = pd.concat([null_count,pd.Series([0]*full_count,index=set(total_count.index) - set(null_count.index))])
        null_count = null_count.sort_index()
        saturation = 1-null_count/total_count
    return saturation[saturation>=0.3].sort_index().index[0] #首次出现饱和度大于30%的那天作为函数输出



#DEMO
# data = pd.read_csv('D:/上海人工智能中心/hkr/度小满联合建模/total_data.csv')
# get_start_date(df=data,x='cs_dxm_dqdz',dt='create_datetime',miss_values=[-99,np.nan])
