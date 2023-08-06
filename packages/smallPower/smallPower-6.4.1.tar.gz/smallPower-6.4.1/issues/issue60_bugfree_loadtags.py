import os,sys,glob,re,importlib
import subprocess as sp, pandas as pd,numpy as np,time, pickle, os
import dorianUtils.comUtils as comutils
from dorianUtils.comUtils import html_table, Streamer
import dorianUtils.utilsD as ut
import smallpower.smallPower as smallPower
from smallpower import conf
import plotly.express as px
import plotly.graph_objects as go
from dorianUtils.comUtils import (
    VisualisationMaster_daily,
    timenowstd,print_file,computetimeshow
)
from multiprocessing import Pool

class FixStreamer(Streamer):
    def load_parkedtags_daily(self,t0,t1,tags,folderpkl,*args,verbose=False,pool='auto',**kwargs):
        '''
        :Parameters:
            pool : {'tag','day','auto',False}, default 'auto'
                'auto': pool on days if more days to load than tags otherwise pool on tags
                False or any other value will not pool the loading
            **kwargs Streamer.pool_tag_daily and Streamer.load_tag_daily
        '''
        if not len(tags)>0:return pd.DataFrame()
        if pool in ['tag','day','auto']:
            # print_file('hello')
            if pool=='auto':
                nbdays=len(pd.date_range(t0,t1))
                if nbdays>len(tags):
                    n_cores=min(self.num_cpus,nbdays)
                    if verbose:print_file('pool on days with',n_cores,'cores because we have',nbdays,'days >',len(tags),'tags')
                    dftags={tag:self.pool_tag_daily(t0,t1,tag,folderpkl,ncores=n_cores,**kwargs) for tag in tags}
                else:
                    n_cores=min(self.num_cpus,len(tags))
                    if verbose:print_file('pool on tag',n_cores)
                    with Pool(n_cores) as p:
                        dftags=p.starmap(self.load_tag_daily_kwargs,[(t0,t1,tag,folderpkl,args,kwargs) for tag in tags])
                    dftags={k.name:k for k in dftags}

        else:
            dftags = {tag:self.load_tag_daily(t0,t1,tag,folderpkl,*args,**kwargs) for tag in tags}

        empty_tags=[t for t,v in dftags.items() if v.empty]
        dftags = {tags:v for tag,v in dftags.items() if not v.empty}
        if len(dftags)==0:
            return pd.DataFrame(columns=dftags.keys())
        df = pd.concat(dftags,axis=1)
        for t in empty_tags:df[t]=np.nan
        df = df[df.index>=t0]
        df = df[df.index<=t1]
        return df

cfg=smallPower.SmallPowerComputer()
cfg.streamer=FixStreamer()
cfg.num_cpus=26

nbdays=60
start=pd.Timestamp('2021-08-01',tz='CET')
end=pd.Timestamp('2022-07-26',tz='CET')-pd.Timedelta(days=nbdays)
period=pd.Series(pd.date_range(start,end))

log='/home/sylfen-dorian_drevon/tests/vm_smallpower/log_days_'+str(nbdays)+'.pkl'
pd.DataFrame(columns=['t0','t1','tags','computation_time','statut']).to_pickle(log)

def test_load_month(ndays=60):
    t0=period.sample(n=1).squeeze()
    t1=t0+pd.Timedelta(days=ndays)
    tags=pd.Series(cfg.getTagsTU('')).sample(n=25)
    start=time.time()
    try:
        df=cfg.loadtags_period(t0,t1,tags,rs='3600s',rsMethod='mean_mix')
    # df=cfg.streamer.load_parkedtags_daily(t0,t1,tags,cfg.folderPkl,rs='3600s',rsMethod='mean_mix')
        ct=time.time()-start
        statut='success'
    except:
        statut='fail'
        ct=np.nan
    return pd.Series({'t0':t0,'t1':t1,'tags':tags.to_list(),'statut':statut,'computation_time':ct}).to_frame().T

df=test_load_month(1)

sys.exit()
for k in range(100):
# for k in range(10):
    s=test_load_month(nbdays)
    s.index=[k]
    pd.concat([pd.read_pickle(log),s],axis=0).to_pickle(log)


# df=pd.read_pickle(log)
# t0,t1,tags,ct,st=df.loc[0]
# df1=cfg.loadtags_period(t0,t1,tags,rs='3600s',rsMethod='mean_mix')
