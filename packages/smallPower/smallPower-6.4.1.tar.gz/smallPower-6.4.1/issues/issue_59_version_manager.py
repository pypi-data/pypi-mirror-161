import os,sys,glob,re,importlib
import dorianUtils.comUtils as comutils
from dorianUtils.comUtils import html_table
import subprocess as sp, pandas as pd,numpy as np,time, pickle, os
import dorianUtils.utilsD as ut
import smallpower.smallPower as smallPower
from smallpower import conf
utils=ut.Utils()
import plotly.express as px
import plotly.graph_objects as go
from dorianUtils.VersionsManager import VersionsManager_daily
from dorianUtils.comUtils import (
    VisualisationMaster_daily,
    timenowstd,print_file,computetimeshow
)

class VersionsManager_extend(VersionsManager_daily):
    def __init__(self,*args,**kwargs):
        VersionsManager_daily.__init__(self,*args,**kwargs)
        self.versionsStart = {
            '2.14':'2021-06-23',
            '2.15':'2021-06-29',
            '2.16':'2021-07-01',
            '2.18':'2021-07-07',
            '2.19':'2021-07-20',
            '2.20':'2021-08-02',
            '2.21':'2021-08-03',
            '2.22':'2021-08-05',
            '2.23':'2021-09-23',
            '2.24':'2021-09-23',
            '2.26':'2021-09-30',
            '2.27':'2021-10-07',
            '2.28':'2021-10-12',
            '2.29':'2021-10-18',
            '2.30':'2021-11-02',
            '2.31':'2021-11-08',
            '2.32':'2021-11-24',
            '2.34':'2021-11-25',
            '2.35':'2021-11-25',
            '2.36':'2021-11-29',
            '2.37':'2021-12-09',
            '2.38':'2021-12-13',
            '2.39':'2021-12-14',
            '2.40':'2021-12-14',
            '2.42':'2022-01-10',
            '2.44':'2022-02-08',
            '2.45':'2022-02-09',
            '2.46':'2022-02-10',
            '2.47':'2022-02-14',### approximatively
            '2.48':'2022-08-01',#### previsionnellement
        }
        self.versions = {re.search(r'[vV]_?\d+(\.\d+)?',f.split('/')[-1]).group():f for f in self._versionFiles}
        self.versions = pd.DataFrame([{'file':f,'version':re.search(r'\d+(\.\d+)?',v).group()} for v,f in self.versions.items()]).set_index('version').sort_index()
        self.versions.index=self.versions.index.astype(float)

    def _load_PLC_versions(self):
        print_file('Start reading all .xlsm files....')
        df_plcs = {}
        for v,f in self.versions['file'].to_dict().items():
            print_file(f)
            df_plcs[v] = pd.read_excel(f,sheet_name='FichierConf_Jules',index_col=0)
        print_file('')
        print_file('concatenate tags of all dfplc verion')
        return df_plcs

    def show_map_of_compatibility(self,missing_tags_map,binaire=False,zmax=None):
        if zmax is None:
            zmax = missing_tags_map.max().max()
        reverse_scale=True
        # missing_tags_map=missing_tags_map.applymap(lambda x:np.random.randint(0,zmax))
        if binaire:
            missing_tags_map=missing_tags_map.applymap(lambda x:1 if x==0 else 0)
            zmax=1
            reverse_scale=False

        fig=go.Figure(go.Heatmap(z=missing_tags_map,x=['v' + str(k) for k in missing_tags_map.columns],
            y=missing_tags_map.index,colorscale='RdYlGn',reversescale=reverse_scale,
            zmin=0,zmax=zmax))
        fig.update_xaxes(side="top",tickfont_size=35)
        fig.update_layout(font_color="blue",font_size=15)
        return fig


svm = VersionsManager_extend(
    folderPkl=conf.FOLDERPKL,
    dir_plc='/home/sylfen-dorian_drevon/tests/vm_smallpower/plcs/',
    file_transition=conf.CONFFOLDER+'versionnage_tags.ods',
    pattern_plcFiles='*ALPHA*.xlsm',
    ds=True,
)

# svm.generate_versionning_data(False,True)
svm.generate_versionning_data(True,True)
fig=svm.show_map_of_compatibility(svm._load_missing_tags_map(d0='2021-08-01',v0=2.28))
fig.write_html('map_compatibility.html')

folderGaston='/home/sylfen-dorian_drevon/tests/vm_smallpower/'

# transition='2.19_2.20'
# transition='2.23_2.24'
# transition='2.29_2.30'
# transition='2.30_2.31'
transition='2.31_2.32'
# transition='2.32_2.34'
# transition='2.38_2.39'
# transition='2.39_2.40'
# transition='2.42_2.44'
# transition='2.44_2.45'
# transition='2.46_2.47'
# transition='2.47_2.48'

def test_make_period_compatible():
    # transition='2.31_2.32'
    # svm.make_period_compatible_from_transition('2022-03-01','2022-03-05',transition,False)
    # svm.make_period_compatible_from_transition('2022-03-07','2022-03-10',transition)
    # svm.create_missing_tags_period_version('2022-02-01','2022-02-10','2.31')
    # svm.get_rename_tags_map_from_rules(transition)

    sys.exit()
    df_missing_tags=svm._load_missing_tags_map()
    df_missing_tags=svm.quick_filter(df_missing_tags.T,v1=2.31)
    svm.show_map_of_compatibility(df_missing_tags)

def missing_tags(day,version):
    df=svm.df_plcs[version].loc[svm.missing_tags_versions(day,version)[version]]
    return df
    # html_table(df)

def test_map_compatibility():
    df_missing_tags=svm._load_missing_tags_map()
    df_missing_tags_f=svm.quick_filter(df_missing_tags.T,'2022-02-01','2022-04-01',2.31)
    svm.show_map_of_compatibility(df_missing_tags_f)
    svm.show_map_of_compatibility(df_missing_tags_f,True)

def test_lines():
    l=svm.get_lines()

def test_get_rename_map():
    svm.compare_plcs('2.45','2.46',None)
    transition='2.44_2.45'
    tags_renamed_map=svm.get_rename_tags_map_from_rules(transition)

def test_presence_tags():
    transition='2.31_2.32'
    fig=svm.presence_tags_transition(transition)
    fig.show()
    sys.exit()
    tags=svm.df_plcs['2.32'].sample(15).index.to_list()
    svm.presence_tags(tags).show()
    svm.are_tags_in_PLCs(tags)
    svm._create_newtags_folder(svm.folderpkl+'2022-04-15/',tags)
    df=svm.presence_tags(tags,empty_df=True)

# def test_make_sure_tags_renamed_ok():
#### check that data that were there even if they should be renamed from tags_renamed_map
# t0=pd.Timestamp('2022-03-13 4:00',tz='CET')

# svm.create_missing_tags_period_version('2021-10-01','2021-10-30','2.22')

transition='2.29_2.30'
# transition='2.38_2.39'
# transition='2.42_2.44'
# transition='2.44_2.45'
# transition='2.46_2.47'
d0,d1='2021-12-05','2022-02-09'

####### get a tag that should be renamed
df_map=svm.get_rename_tags_map_from_rules(transition)
sys.exit()
svm.make_period_compatible_from_transition(d0,d1,transition)
old_tag,new_tag=['SEH1.L211_H2OP_TT_01.HM05','SEH1.GWPBH_TT_01.HM05']


########## create dummy data
t0=pd.Timestamp('2021-10-19 4:00',tz='CET')
t1=t0+pd.Timedelta(hours=16)
d0=t0.strftime('%Y-%m-%d')
ts=pd.date_range(t0,t1,freq='1S')
s=-pd.Series(range(len(ts)),index=ts)
s.to_pickle(svm.folderpkl+d0+'/'+new_tag+'.pkl')
s2=pd.Series(0,index=ts)
s2.to_pickle(svm.folderpkl+d0+'/'+old_tag+'.pkl')
svm.presence_tags_transition(transition).show()

########## look at your data before remapping
from smallpower.smallPower import SmallPowerComputer
cfg=SmallPowerComputer()
df=cfg.loadtags_period(t0,t1,[old_tag,new_tag])
cfg.utils.multiUnitGraph(df).show()
########## remappe
svm.make_period_compatible_from_transition(d0,d0,transition)
########## look at your data after remapping
df=cfg.loadtags_period(t0,t1,[new_tag])
cfg.utils.multiUnitGraph(df).show()
