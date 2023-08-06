import importlib,time,sys,os
start=time.time()
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
import dorianUtils.comUtils as com
import issues
from dorianUtils.comUtils import html_table
from dorianUtils.comUtils import print_file
importlib.reload(smallPower)
importlib.reload(com)

folder_figures='/home/dorian/sylfen/programmerBible/doc/pictur/issue38/'

##### make sure the period has the 4 stacks working

def generate_df():
    import time,pandas as pd,numpy as np
    import smallpower.smallPower as smallPower
    cfg=smallPower.SmallPowerComputer()
    start=time.time()
    t0 = pd.Timestamp('2022-06-01 08:00',tz='CET')
    t1 = pd.Timestamp('2022-06-14 22:00',tz='CET')
    tags=['SEH0.L138_O2_PT_01.HM05', 'SEH01.L138_O2_FT_01.HM05']
    tags += cfg.getTagsTU('alim.*it.*hm05$')
    df = cfg.loadtags_period(t0,t1,tags,rs='10s',rsMethod="mean",closed='right')
    print(time.time()-start)
    df.to_pickle('/home/sylfen/tests/df_issue38.pkl')



cfg=smallPower.SmallPowerComputer()
df=issues.get_file_from_gaston(filename='df_issue38.pkl',dl=False)

# download_data(t0,t1,tags)

# sys.exit()
df=df[df.index>'2022-06-09']
# fig = cfg.multiUnitGraphSP(df.resample('1H',closed='right',label='right').mean())
# fig=issues.replot_colors(fig)
# fig = cfg.update_lineshape_fig(fig)
# fig.show()

import plotly.express as px
import plotly.graph_objects as go

def graphPvsQ():
    df=df[['SEH0.L138_O2_PT_01.HM05','SEH01.L138_O2_FT_01.HM05']]
    # df=df[['SEH0.L138_O2_PT_01.HM05','SEH01.L138_O2_FT_01.HM05','SEH1.STK_ALIM_01.IT_HM05']]
    # df.columns=['pression','debit','courant_stack_1']
    # df=df.set_index('pression')
    # df['SEH1.STK_ALIM_01.IT_HM05']*=-1
    df=df.set_index('SEH01.L138_O2_FT_01.HM05')

    # fig = go.Figure(
    #     go.Scatter(
    #         x = df['pression'],
    #         y = df['debit'],
    #         hovertemplate =
    #             '<i>pression</i>: %{x:.1f}'+
    #             '<br>debit: %{y:.1f}<br>'+
    #             '<b>%{text|%b-%d %H:%M:%S}</b>',
    #         text = df.index,
    #     )
    # )
    #
    # fig.add_trace(
    #     go.Scatter(
    #         x = df['pression'],
    #         y = df['courant_stack_1'],
    #         hovertemplate =
    #             '<i>courant</i>: %{y:.1f}'+
    #             '<br>pression: %{x:.1f}<br>'+
    #             '<b>%{text|%b-%d %H:%M:%S}</b>',
    #         text = df.index,
    #         marker_color='red',
    #     )
    # )

    # cfg.utils.getLayoutMultiUnit(pression)
    # dictYaxis[y] = {
    #     title:g,
    #     titlefont:{color:c},
    #     tickfont:{color:c},
    #     anchor:'free',
    #     overlaying:'y',
    #     side:s,
    #     position:p,
    #     gridcolor:c
    #     }
    # )


    # fig.update_layout(xaxis_title='pression(mbarg)',yaxis_title='debit(Nl/min)')
    px.scatter(df).show()
    fig=cfg.multiUnitGraphSP(df)
    fig.update_traces(mode='markers')
    fig.update_traces(hovertemplate='  x:%{x:.1f}<br>  y:%{y:.1f}')

    fig.show()

# def graphN2O2_vs_PQ():
df['I_total']=df[[k for k in df.columns if 'ALIM' in k]].sum(axis=1)
df['O2_out']=df['I_total']*25/(4*cfg.cst['FAR'])*cfg.cst['vlm']*60
df['N2/O2']=4*df['SEH01.L138_O2_FT_01.HM05']/(df['SEH01.L138_O2_FT_01.HM05']+df['O2_out'])

df=df[['SEH0.L138_O2_PT_01.HM05','SEH01.L138_O2_FT_01.HM05','O2_out','N2/O2']]
fig=px.density_heatmap(df,z='N2/O2',x='SEH01.L138_O2_FT_01.HM05',y='SEH0.L138_O2_PT_01.HM05',histfunc='avg')

# fig.write_html(folder_figures+'n2o2_vs_pq.html')
fig.show()
