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

folder_figures='/home/dorian/sylfen/programmerBible/doc/pictur/issue36/'

##### make sure the period has the 4 stacks working

def generate_df():
    import time,pandas as pd,numpy as np
    import smallpower.smallPower as smallPower
    cfg=smallPower.SmallPowerComputer()
    start=time.time()
    tags = cfg.getTagsTU('fuel.*PT')
    tags+=cfg.getTagsTU('o2.*PT')
    tags+=cfg.getTagsTU('gf[CD].*00_PT')
    t0 = pd.Timestamp('2022-02-15 14:00',tz='CET')
    t1 = pd.Timestamp('2022-02-15 22:00',tz='CET')
    df1 = cfg.loadtags_period(t0,t1,tags,rs='10s',rsMethod="mean",closed='right')

    t0 = pd.Timestamp('2022-02-19 9:00',tz='CET')
    t1 = pd.Timestamp('2022-02-19 18:00',tz='CET')
    df2 = cfg.loadtags_period(t0,t1,tags,rs='10s',rsMethod="mean",closed='right')
    print(time.time()-start)
    df=pd.concat([df1,df2])
    df.to_pickle('/home/sylfen/tests/df_issue36.pkl')

df=issues.get_file_from_gaston(filename='df_issue36.pkl',dl=False)

cfg=smallPower.SmallPowerComputer()
df1=df[(df.index>'2022-02-15 16:00')&(df.index<'2022-02-15 18:00')]
df2=df[(df.index>'2022-02-19 9:00')&(df.index<'2022-02-19 12:00')]

fig1=cfg.multiUnitGraphSP(df1.resample('60s').mean())
fig2=cfg.multiUnitGraphSP(df2.resample('60s').mean())
fig1.update_layout(title="période de fonctionnement de l'aspirateur 1")
fig2.update_layout(title='test')
fig2.update_layout(title="période de fonctionnement de l'aspirateur 2")
def figures_to_html(figs, filename="test.html"):
    with open(filename, 'w') as dashboard:
        dashboard.write("<html><head></head><body>" + "\n")
        for fig in figs:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")

figures_to_html([fig1,fig2],folder_figures+'fonctionnementAspi.html')
# fig.write_html()
