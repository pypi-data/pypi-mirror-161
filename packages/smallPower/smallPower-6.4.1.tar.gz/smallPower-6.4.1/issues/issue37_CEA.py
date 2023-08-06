import time,sys,os
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
import dorianUtils.comUtils as com
from dorianUtils.comUtils import (html_table,print_file,computetimeshow)
import issues
from multiprocessing import Pool
import importlib
importlib.reload(issues)

folderCEA='/data2/CEA_data/'
folderFigures='/home/dorian/sylfen/programmerBible/doc/pictur/issue37/'

issue=issues.Issues()
cfg=smallPower.SmallPowerComputer()
vm=issues.VersionsManager(cfg.folderPkl)


def quick_check_aspi():
    tags=cfg.getTagsTU('BLR_03')
    df=pd.concat([pd.read_pickle('data/genvia/'+ t+'.pkl') for t in tags],axis=1)
    cfg.multiUnitGraphSP(df).show()

def get_data_gaston():
    from smallpower.smallPower import SmallPowerComputer
    cfg=SmallPowerComputer()
    t0=pd.Timestamp('2021-11-01 10:00',tz='CET')
    t1=pd.Timestamp('2022-03-01 10:00',tz='CET')
    etat_tag=['SEH1.Etat.HP41']
    df = cfg.streamer.load_parkedtags_daily(t0,t1,etat_tag,cfg.folderPkl,pool='auto',verbose=True,rs='300s',rsMethod='forwardfill',closed='right',time_debug=True)
    df.to_pickle('issue37.pkl')

# def exfiltrate_data():
import os
# df=pd.concat([pd.read_csv('data/data_cea/'+ t,index_col=0) for t in os.listdir('data/data_cea/')],axis=1)
df=pd.concat([pd.read_pickle('data/genvia/'+ t) for t in os.listdir('data/genvia/')],axis=1)
# HER_to_remove=[k for k in df.columns if 'HER' in k]
# df=df.sort_index()
# sys.exit()
# df_t=pd.concat([etat,df],axis=1).ffill().bfill()
#### filter modes
filter=df['SEH1.Etat.HP41'].ffill().bfill().astype(int).apply(lambda x:x in [10,12,14,20,21,24,44,45,50,62,63])
dff=df[filter]
#### filter aspirateur
tag=cfg.getTagsTU('BLR_03.*HR36')[0]
dff2=dff[dff[tag]<15]
deltag=['SEH1.Etat.HP41']+cfg.getTagsTU('BLR_03')
for t in deltag : del dff2[t]
# return dff

export_data(dff2,'genvia_19_mai_25_juillet')
def export_data(dff,fichier_cea='cea_data_nov2021_fev2022'):
    folder_out="data/cea_data_exfiltrate/"
    dff.to_csv(folder_out+fichier_cea+'.csv')
    cfg.dfplc.loc[dff.columns]['DESCRIPTION'].to_csv(folder_out+'description_tags.csv')
    import subprocess as sp
    password='rsoc_alpha_dd'
    sp.run('zip -e '+folder_out+fichier_cea+'.zip '+folder_out+fichier_cea+'.csv '+folder_out+'description_tags.csv',shell='True')

def get_mode_from_gaston():
    courants=issue.get_file_from_gaston('issue37_courants_HC13.pkl',False,'gastonDorianFibre')
    df2=etat.resample('1H').ffill().bfill()
    ENUM_MODES_HUB={l:v for l,v in conf.ENUM_MODES_HUB.items() if not 'undefined' in v}
    ENUM_MODES_HUB[np.nan]=np.nan
    txts=df2.applymap(lambda x:conf.ENUM_MODES_HUB[int(x)])
    import plotly.graph_objects as go
    fig = go.Figure(go.Scatter(
        x = df2.index,
        y = df2['SEH1.Etat.HP41'],
        hovertemplate =
            '<i>etat</i>: %{y:.0f}'+
            '<br>time: %{x}<br>'+
            '<b> %{text}</b>',
        text = txts,
        showlegend = False))

    fig.update_traces(line_shape='hv')
    fig.write_html(folderFigures+'exfiltrate_data.html')
    # fig=cfg.multiUnitGraphSP(df2)
    fig.show()

def easy_tags():
    import pandas as pd,numpy as np,time
    import smallpower.smallPower as smallPower
    from smallpower import conf
    from dorianUtils.comUtils import (html_table,print_file,computetimeshow)
    cfg=smallPower.SmallPowerComputer()
    infos=pd.read_excel('liste_exportALPHA_versCEA_issue37.xlsx',skiprows=7)
    tags=[t for t in infos.TAG if t in list(cfg.dfplc.index)]
    easy_tags=[k for k in tags if not 'SEH1.STB_HER' in k]
    # t0,t1 = pd.Timestamp('2021-11-01 00:00',tz='CET'),pd.Timestamp('2022-02-28 00:00',tz='CET')
    t0,t1 = pd.Timestamp('2022-05-19 00:00',tz='CET'),pd.Timestamp('2022-07-25 00:00',tz='CET')
    rs,rsMethod='60s','mean'

    # for t in easy_tags:
    # for t in cfg.getTagsTU('SEH1.STK_ALIM.*IT_HM05$'):
    # for t in ['SEH1.Etat.HP41']:
    for t in cfg.getTagsTU('BLR_03'):
        start=time.time()
        df = cfg.streamer.load_parkedtags_daily(t0,t1,[t],cfg.folderPkl,pool='auto',verbose=True,rs=rs,rsMethod=rsMethod,closed='right',time_debug=True)
        df=df.squeeze()
        df.to_pickle('genvia/'+t+'.pkl')
        print(time.time()-start)

    # issues.push_toFolderFigures(df,'issue37_easy_tags',folderCEA)

def export_easy_tags2zip():
    # df = pd.read_pickle('data/issue37_easy_tags.pkl')
    df = pd.read_pickle('data/easy_tags100_147.pkl')
    for tag in df.columns:
        df[tag].squeeze().to_csv('data/easy_tags/'+tag+'.csv')

def plot_easy_tags():
    df=pd.read_pickle('data/issue37_easy_tags.pkl')
    df=df.resample('12H',closed='right',label='right').mean()
    tags=pd.Series([k for k in df.columns if 'HC13' not in k])
    tags_groups={}
    for nbStack in range(1,5):
        tags_groups['stack'+str(nbStack)] = tags[tags.str.contains('STK_.*{:02d}'.format(nbStack))]
    tags_groups['other_tags'] = [k for k in tags if k not in list(pd.DataFrame(tags_groups.values()).T.melt().value)]
    # fig=issues.save_figure(df[tags_groups['stack1']],'stack1',as_png=False).show()
    for g,tags in tags_groups.items():
        fig=cfg.multiUnitGraphSP(df[tags]);
        fig.update_traces(hovertemplate='<b>   %{y:.2f} <br>   %{x}')
        # fig.show()
        # break;
        issues.save_figure(fig,'issue37_'+g,folderFigures)
    sys.exit()

#### courants HC13
def courant_HC13():
    tag_courant_hc13=[t for k,t in enumerate(infos.TAG.fillna('unassigned')) if 'HC13' in t]
    tags_needed=[t.strip('.HC13') for t in tag_courant_hc13]
    # t1 = pd.Timestamp('2022-02-01 00:00',tz='CET')
    # issues.download_data(t0,t1,tags_needed)
    # p=vm.presence_tags(tags_needed,True)
    # issues.download_data(t0,t1,tags_needed)
    courants_HC13 = -cfg.loadtags_period(t0,t1,tags_needed,pool='auto',rs=rs,rsMethod=rsMethod,closed='right',verbose=True)
    issues.push_toFolderFigures(courants_HC13,'issue37_courants_HC13',folderCEA)
    sys.exit()

##### other tags
idx_rows_no_tag=[k for k,t in enumerate(infos.TAG) if t not in list(cfg.dfplc.index)]
infos_otherTags=infos.loc[idx_rows_no_tag]
### debit h2O
def debitH2O():
    tags_needed=['SEH1.L213_H2OPa_FT_01.HM05','SEH1.L213_H2OPb_FT_01.HM05']
    # p=vm.presence_tags(tags_needed,True)
    # issues.download_data(t0,t1,tags_needed)
    start=time.time()
    # df_H2O_debit = cfg.loadtags_period(t0,t1,tags_needed,pool='auto',rs=rs,rsMethod=rsMethod,closed='right',verbose=True)
    # df_H2O_debit['debit H2O'] = df_H2O_debit.sum(axis=1)
    df_H2O_debit = pd.read_pickle('data/issue37_debitH2O.pkl')
    print(time.time()-start)

    l=cfg.dfplc.loc[df_H2O_debit.columns[0]]
    l.name=df_H2O_debit.columns[2]
    l.DESCRIPTION='debit H2O entrant'
    cfg.dfplc.loc[l.name]=l
    cfg.dftagColorCode.loc[l.name]=cfg.dftagColorCode.loc[df_H2O_debit.columns[0]]

    issues.push_toFolderFigures(df_H2O_debit,'issue37_debitH2O',folderCEA,cfg=cfg)
    sys.exit()

def debit_fuel_entrant():
    ###Débit Fuel entrant =Débit H2 neuf + Débit H2O+ Débit de recirculation

    tags_needed=['SEH1.L041_H2_FT_01.HM05']

def FU_SU():
    # p=vm.presence_tags(tags_needed,True)
    # issues.download_data(t0,t1,tags_needed)
    start=time.time()

    #### FU/SU

    df = cfg.loadtags_period(t0,t1,tags,rs=rs,rsMethod=rsMethod,closed='right')

    # df.to_pickle('df_issue38.pkl')
    # print(time.time()-start)
