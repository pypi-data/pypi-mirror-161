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

folder_figures='/home/dorian/sylfen/programmerBible/doc/pictur/issue47/'

cfg = smallPower.SmallPower_retro_indicators()
# t0=pd.Timestamp('2022-02-02 00:00',tz='CET')
# t1=pd.Timestamp('2022-02-02 22:59:59',tz='CET')
t0=pd.Timestamp('2022-02-12 08:00',tz='CET')
t1=pd.Timestamp('2022-02-15 18:00:00',tz='CET')

########## check vectorization
# df=cfg.compute_modehub(t0,t1,vector=False)[['modehub']]
# df_vec=cfg.compute_modehub(t0,t1,vector=True)[['modehub']]

# df=cfg.compute_fuites_air(t0,t1,vector=False)[['fuite_air_unfiltered']]
# df_vec=cfg.compute_fuites_air(t0,t1,vector=True)[['fuite_air_unfiltered']]

# df=cfg.compute_fuites_fuel(t0,t1,vector=False)[['fuite_fuel_unfiltered']]
# df_vec=cfg.compute_fuites_fuel(t0,t1,vector=True)[['fuite_fuel_unfiltered']]

# df=cfg.compute_rendement_sys(t0,t1,vector=False)[['rendement_sys_unfiltered']]
# df_vec=cfg.compute_rendement_sys(t0,t1,vector=True)[['rendement_sys_unfiltered']]

# df_vec=cfg.compute_rendements_gvs(t0,t1,vector=True)[['rendement_gv_b_unfiltered']]
# df=cfg.compute_rendements_gvs(t0,t1,vector=False)[['rendement_gv_b_unfiltered']]

dff=cfg.compute_pertes_stack(t0,t1,alpha=0.0005,vector=True)



# dff=pd.concat([df,df_vec.add_suffix('_vectorized')],axis=1)
fig=px.scatter(dff.resample('1200s').nearest())
fig.update_traces(mode='lines',line_shape='hv')
# fig.update_traces(mode='lines')
fig.data[1].line.dash='dot'
fig.show()
