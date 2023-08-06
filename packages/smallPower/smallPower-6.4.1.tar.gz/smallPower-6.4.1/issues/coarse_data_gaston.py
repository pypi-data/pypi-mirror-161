import time,sys,os
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
import dorianUtils.comUtils as com
from dorianUtils.comUtils import Streamer
from dorianUtils.comUtils import (html_table,print_file,computetimeshow)
from multiprocessing import Pool

cfg=smallPower.SmallPowerComputer()

class Streamer_fix(Streamer):

    def load_raw_day_tag(self,day,tag,folderpkl,rs,rsMethod,closed,showTag_day=True):
        # print(folderpkl, day,'/',tag,'.pkl')

        filename = folderpkl +'/'+ day+'/'+tag+'.pkl'
        if os.path.exists(filename):
            s= pd.read_pickle(filename)
        else :
            s=  pd.Series(dtype='float')
        if showTag_day:print_file(filename + ' read',filename=self.log_file)
        s = self.process_tag(s,rs=rs,rsMethod=rsMethod,closed=closed)
        return s

cfg.streamer=Streamer_fix()

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

rs='60s'
if not os.path.exists(cfg.folder_coarse):os.mkdir(cfg.folder_coarse)
for m in METHODS:
    if not os.path.exists(cfg.folder_coarse+m):os.mkdir(cfg.folder_coarse+m)

# for tag in cfg.getTagsTU(''):
for tag in cfg.getTagsTU('')[499:]:
    print_file('tag is ',tag)
    d=d0
    ### par groupe de 20 jours
    while d<d1:
    # while d<d0+pd.Timedelta(days=140):
        t0=pd.Timestamp(d)
        t1=t0+pd.Timedelta(days=20)
        d=t1
        print('period is ',t0,t1)
        start=time.time()
        for m in METHODS[1:]:
            s = cfg.streamer.load_parkedtags_daily(t0,t1,[tag],cfg.folderPkl,pool='auto',rs=rs,rsMethod=m,closed='right')
            if s.empty:s=pd.Series(name=tag,dtype=cfg.dataTypes[cfg.dfplc.loc[tag,'DATATYPE']])
            else:s=s[tag]
            filename=cfg.folder_coarse + m + '/' + tag + '.pkl'
            if os.path.exists(filename):
                old_s=pd.read_pickle(filename)
                s=pd.concat([old_s,s],axis=0).sort_index()
            s=s[~s.index.duplicated(keep='first')]
            s.to_pickle(filename)
        print(time.time()-start)



sys.exit()
t0=pd.Timestamp('2021-07-19 01:00:00+0200', tz='CET')
t1=pd.Timestamp('2021-08-08 01:00:00+0200', tz='CET')
tag=cfg.getTagsTU('')[499]
s = cfg.streamer.load_parkedtags_daily(t0,t1,[tag],cfg.folderPkl,pool='auto',rs=rs,rsMethod='mean',closed='right')
s = cfg.streamer.pool_tag_daily(t0,t1,tag,cfg.folderPkl,rs=rs,rsMethod='mean',closed='right',verbose=True)

# s = cfg.streamer.load_tag_daily(t0,t1,tag,cfg.folderPkl,verbose=True,rs=rs,rsMethod='mean',closed='right',verbose=True)

day='2021-08-03'
cfg.streamer.load_raw_day_tag(day,tag,cfg.folderPkl,rs=rs,rsMethod='mean',closed='right',showTag_day=True)
