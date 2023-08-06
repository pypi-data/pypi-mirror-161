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
import plotly.graph_objects as go

folder_figures='/home/dorian/sylfen/programmerBible/doc/pictur/issue49/'

cfg = smallPower.SmallPowerComputer()
t0=pd.Timestamp('2022-02-15 00:00',tz='CET')
t1=pd.Timestamp('2022-02-19 18:59:59',tz='CET')


fig=cfg.repartitionPower(t0,t1,rs='600s',rsMethod='mean',closed='right')

fig.show()
# fig.write_html(folder_figures+'power_repartition_group.html')
