import importlib,time,sys,os
start=time.time()
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
from monitorBuilding import (monitorBuilding,conf)

import reflex.reflex as reflex
from reflex import conf

cfg=smallPower.SmallPowerComputer()
cfg2=monitorBuilding.MonitorBuildingComputer()
cfg3=reflex.ReflexComputer(log_file=None)
cfg3.dfplc=pd.read_excel(conf.FILE_CONF_REFLEX,sheet_name='full_plc',index_col=0)
tags=['SEH11_JTW_05']

t0=pd.Timestamp('2022-07-08 6:00',tz='CET')
t1=t0+pd.Timedelta(hours=17)
rs='30s'
rsMethod='mean'

def get_data():
    alpha_total = ['SEH0.JT_01.JTW_HC20']
    df1 = cfg.loadtags_period(t0,t1,alpha_total,rs=rs,rsMethod=rsMethod,closed='right',verbose=True)

    sylfen_total=['C00000003-B001-kW sys-JTW']
    df2 = cfg2.loadtags_period(t0,t1,sylfen_total,rs=rs,rsMethod=rsMethod,closed='right',verbose=True)

    df=pd.concat([df1/1000,df2],axis=1)
    df.to_pickle('issue_58.pkl')

    fig = cfg.repartitionPower(t0,t1,rs=rs,rsMethod=rsMethod,closed='right',verbose=True)
    fig.write_html('issue_58.html')



df3 = cfg3.streamer.load_parkedtags_daily(t0,t1,tags,cfg3.folderPkl,rs=rs,pool=True,rsMethod=rsMethod,closed='right')
df=pd.read_pickle('data/issue_58.pkl')
df=pd.concat([df,df3],axis=1)
import plotly.express as px
px.line(df).show()
