import importlib,time,sys,os
start=time.time()
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
import dorianUtils.comUtils as com
from dorianUtils.comUtils import (html_table,print_file)
importlib.reload(smallPower)
importlib.reload(com)
import issues
importlib.reload(issues)
import plotly.express as px


cfg = smallPower.SmallPowerComputer()

# def get_correct_alpha_low_pass_filterparameters():
tags=['SEH1.STB_HER_00_JTW_00_HC01']

# vm=issues.VersionsManager(cfg.folderPkl)
# vm.presence_tags(tags)
t0 = pd.Timestamp('2022-06-08 06:00',tz='CET')
t1 = t0+pd.Timedelta(hours=40)
df = cfg.loadtags_period(t0,t1,tags,rsMethod='raw')
# df2 = df.resample('1s').nearest().squeeze()

#### generate some filterings with several alpha values #
def apply_lowpass_filter(alpha):
    tmp = {df2.index[0]:df2[0]}
    for k in range(1,len(df2)):
        tm1 = df2.index[k-1]
        tmp[df2.index[k]] = bec.indicators.low_pass_filter(df2[k],tmp[tm1],alpha)
        return pd.Series(tmp)

def several_alphas():
    dff = pd.DataFrame({'filter_' +str(alpha):apply_lowpass_filter(alpha) for alpha in [1,0.005,0.0005,0.00025,0.0001,0.00005]})
    fig = px.scatter(dff.resample('60s',label='right').mean());fig.update_traces(mode='lines+markers');fig.show()

#### compare ewn,rolling mean apply_lowpass_filter function #
def compare_filters():
    alpha=0.0005;dff2=pd.DataFrame()
    dff2['exponential weighted mean_' + str(alpha)] = df2.ewm(alpha=alpha).mean()
    dff2['filter formula_' + str(alpha)] = apply_lowpass_filter(alpha)
    dff2['rolling mean_10h'] = df2.rolling('H').mean()
    fig = px.scatter(dff2.resample('60s',label='right').mean());fig.update_traces(mode='lines+markers');fig.show()

### is it possible to apply filter using the transfer function, the fft
# def fft_product_vs_lowpassfilter():

##### check the automation process
def realtime_tag():
    #### check that the power_stb is in the buffer
    dumper = smallPower.SmallPower_dumper(log_file_name=None)
    bec = dumper.devices['beckhoff']

    x=bec.buffer_indicators['power_stb']
    #### check that the tag power_enceinte_thermique to compute the new power_stb indicator are in tags_for_indicators and get the value
    bec.connectDevice()
    tag_for_ind_val = bec.collectData(conf.TZ_RECORD,bec.tags_for_indicators.to_list())
    tag_for_ind_val = {ind:tag_for_ind_val[tag_ind][0] for ind,tag_ind in bec.tags_for_indicators.to_dict().items()}
    power_enceinte_thermique = tag_for_ind_val['power_enceinte_thermique']

    df=bec.collectData('CET',conf.TAGS_FOR_INDICATORS);df=pd.DataFrame(df,index=['value','timestampz']).T
    df=bec.compute_indicators(debug=True)

    t1 = pd.Timestamp.now(tz='CET')
    t0  = t1-pd.Timedelta(seconds=5*60)
    df  = cfg._load_database_tags(t0,t1,['SEH1.STB_HER_00_JTW_00_HC06'])


# def signal_filter_ODE():
#### generate signals
def low_pass_filter(y,x,alpha):
    return alpha*x+(1-alpha)*y

# def low_pass_filter(y,x,alpha,beta):
#     return alpha*x+(1-alpha)*y

from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
## square signal
nbPts=1000
periods=10
times   = pd.date_range('9:00','18:00',periods=nbPts)
signals = pd.DataFrame()

t = np.linspace(0, 1, nbPts, endpoint=False)
signals['square'] = signal.square(2 * np.pi * periods * t)
signals['square_double'] = signal.square(2 * np.pi * periods * t)
signals['saw_tooth'] = signal.sawtooth(2 * np.pi * periods * t)

t0 = pd.Timestamp('2022-06-09 06:00',tz='CET')
t1 = t0+pd.Timedelta(hours=14)
real_data = cfg.loadtags_period(t0,t1,tags,rsMethod='raw')

# signals.plot()

dfs=[]

# alpha,beta,gamma=0.05,0.01,0.01
for alpha in [0.05,0.025,0.01,0.005]:
    for beta in [0.05,0.025,0.01,0.005]:
        print(beta)
    # for gamma in [0.05,0.025,0.01]:
        df=pd.DataFrame()
        # df['input']=signals['square']
        df['input']=real_data
        df['filter1']=np.nan
        df['filter2']=np.nan
        # df['filter3']=np.nan
        df['filter1'].iloc[0]=df['input'].iloc[0]
        df['filter2'].iloc[0]=df['filter1'].iloc[0]
        # df['filter3'].iloc[0]=df['filter2'].iloc[0]
        for k in range(1,len(df)):
            df['filter1'].iloc[k]=low_pass_filter(df['filter1'][k-1],df['input'][k],alpha)
            df['filter2'].iloc[k]=low_pass_filter(df['filter2'][k-1],df['filter1'][k],beta)
            # df['filter3'].iloc[k]=low_pass_filter(df['filter3'][k-1],df['filter2'][k],gamma)

        # df.columns=['df['input']','lowpass_'+str(alpha),'lowpass2_'+str(beta),'lowpass3_'+str(gamma)]
        df['beta']=beta
        # df['gamma']=gamma
        df['alpha']=alpha
        dfs.append(df)


df=pd.concat(dfs)
# dff=df.melt(value_name='value',value_vars=['filter1','filter2','filter3','input'],id_vars=['gamma','beta'],ignore_index=False)
dff=df.melt(value_name='value',value_vars=['input','filter1','filter2'],id_vars=['alpha','beta'],ignore_index=False)
fig=px.scatter(dff,y='value',color='variable',facet_col='beta',facet_row='alpha');fig.update_traces(mode='lines+markers');fig.show()

# df.plot()
# plt.show()
