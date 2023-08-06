import time,sys,os
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
import dorianUtils.comUtils as com
from dorianUtils.comUtils import (html_table,print_file,computetimeshow)
import issues
from multiprocessing import Pool
import importlib
import plotly.express as px
importlib.reload(issues)

# folder_coarse='/home/sylfen/data_ext/smallpower_coarse/'
cfg=smallPower.SmallPowerComputer()
METHODS=['mean','min','max']
cfg.folder_coarse=cfg.folderPkl.replace('daily','coarse')

def park_coarse_data(df,rs='60s'):
    '''
    the dataframe should be pivoted with index as timestampz
    '''
    for tag in df.columns:
        s=df[tag]
        s_new = {}
        s_new['mean'] = s.resample(rs,closed='right',label='right').mean()
        s_new['min']  = s.resample(rs,closed='right',label='right').min()
        s_new['max']  = s.resample(rs,closed='right',label='right').max()
        for m in METHODS:
            filename=cfg.folder_coarse + m + '/' + tag + '.pkl'
            if os.path.exists(filename):
                tmp=pd.concat([pd.read_pickle(filename),s_new[m]],axis=0).sort_index()
                s_new[m]=tmp[~tmp.duplicated(keep='first')]
            s_new[m].to_pickle(filename)

listdays=cfg.getdaysnotempty()
d0,d1=listdays.min(),listdays.max()



t0=pd.Timestamp('2021-12-01',tz='CET')
t1=pd.Timestamp('2022-07-30',tz='CET')
# tags=['SEH1.STB_STK_02.ET_10.HM05','SEH1.L117_O2_TT_01.HM05','SEH1.EPB_SYS_67A1_IT_01.HM05','SEH1.STB_STK_04.ET_10.HM05']
tags=cfg.getTagsTU('GF[CD].*PT')
# tags=pd.Series(cfg.alltags).sample(n=5)
# tags=cfg.getTagsTU('L131')+cfg.getTagsTU('BLR_02')
# tags=[]
df=cfg.load_coarse_data(t0,t1,tags,rs='60s',rsMethod='max')

df2=cfg.auto_resample_df(df,500000)
print('ok')
cfg.multiUnitGraphSP(df2).show();
# cfg.utils.multiUnitGraph(df2).show();



fig2=px.scatter(df2)
cfg.standardLayout(fig2)
# fig2=cfg.updatecolorAxes(fig2)
cfg.updatecolortraces(fig2)
fig2.update_traces(mode='lines+markers')
fig2.show();
sys.exit()
import plotly.express as px
df.columns=['.'.join(t.split('.')[1:]) for t in df.columns]
fig=px.scatter_matrix(df)
fig.update_layout(font_size=10)
fig.show()
sys.exit()
