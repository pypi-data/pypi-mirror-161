import smallpower.smallPower as smallPower
from smallpower import conf
import pandas as pd,numpy as np
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
cfg=smallPower.SmallPowerComputer()
cfg.cat_tags=cfg.usefulTags.to_dict()['Pattern']

df=pd.read_pickle('/home/dorian/Downloads/courant_stacks.pkl')
### graph
df['courant_SOEC']=df['courant'].where(df['courant']>0,0)
df['courant_SOFC']=-df['courant'].where(df['courant']<0,0)

df['tensions_SOEC']=df['tensions'].where(df['courant']>0,0)
df['tensions_SOFC']=df['tensions'].where(df['courant']<0,0)

df['puissance_SOEC']=df['courant_SOEC']*df['tensions_SOEC']/1000
df['puissance_SOFC']=df['courant_SOFC']*df['tensions_SOFC']/1000

df2=df[['courant_SOEC','courant_SOFC','tensions_SOFC','tensions_SOEC','puissance_SOEC','puissance_SOFC']]

df=df[df.index>'2021-10-01']
fig = make_subplots(3,1,
    shared_xaxes=True,vertical_spacing=0.1,subplot_titles=['courants','tensions','puissances'],
    row_titles=['A','V','kW'])
fig.add_trace(go.Scatter(x=df.index,y=df['courant_SOEC'],marker_color='red',name='courants_soec'),row=1,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df['courant_SOFC'],marker_color='blue',name='courants_sofc'),row=1,col=1)

fig.add_trace(go.Scatter(x=df.index,y=df['tensions_SOEC'],marker_color='red',name='tensions_soec'),row=2,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df['tensions_SOFC'],marker_color='blue',name='tensions_sofc'),row=2,col=1)

fig.add_trace(go.Scatter(x=df.index,y=df['puissance_SOEC'],marker_color='red',name='puissances_soec'),row=3,col=1)
fig.add_trace(go.Scatter(x=df.index,y=df['puissance_SOFC'],marker_color='blue',name='puissances_sofc'),row=3,col=1)

fig.update_traces(mode='lines+markers')
fig.show()
