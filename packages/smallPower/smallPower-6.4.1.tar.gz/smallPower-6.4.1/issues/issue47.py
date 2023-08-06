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
t0=pd.Timestamp('2022-02-15 00:00',tz='CET')
t1=pd.Timestamp('2022-02-19 18:59:59',tz='CET')


# variables=['I_conventionnel']
# df=self.get_tags_for_indicator(variables,t0,t1)

# df=cfg.compute_fuites_fuel(t0,t1,method='ewm')
# df=cfg.compute_h2_prod_cons(t0,t1)
# df=cfg.compute_rendement_sys(t0,t1)
# df=cfg.compute_rendements_gvs(t0,t1)
# df=cfg.compute_pertes_stack(t0,t1)


# fig=cfg.check_indicator(df[df.index>'2022-02-15'],use_px=False);
# fig.write_html(folder_figures+'pertes_thermiques_stack.html')


########## check vectorization
df=cfg.compute_modehub(t0,t1,vector=False)[['modehub']]
df_vec=cfg.compute_modehub(t0,t1,vector=True)[['modehub']]
dff=pd.concat([df,df_vec.add_suffix('_vectorized')],axis=1)

fig=px.scatter(dff.resample('1200s').nearest())
fig.update_traces(mode='lines',line_shape='hv')
fig.data[1].line.dash='dot'
fig.show()
