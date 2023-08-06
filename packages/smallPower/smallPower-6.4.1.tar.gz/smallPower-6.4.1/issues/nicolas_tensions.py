import time,sys,os
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
import dorianUtils.comUtils as com
from dorianUtils.comUtils import (html_table,print_file,computetimeshow)
from multiprocessing import Pool
from dorianUtils.comUtils import Streamer
import issues

cfg=smallPower.SmallPowerComputer()
class Streamer_fix(Streamer):
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
        dftags = {tag:v for tag,v in dftags.items() if not v.empty}
        if len(dftags)==0:
            return pd.DataFrame(columns=dftags.keys())
        df = pd.concat(dftags,axis=1)
        for t in empty_tags:df[t]=np.nan
        df = df[df.index>=t0]
        df = df[df.index<=t1]
        return df

cfg.streamer=Streamer_fix()
issues=issues.Issues()
start=time.time()
df=pd.read_pickle('data/stack2.pkl')
# df=df[(df.index>'2022-06-01')&(df.index<'2022-06-05')]
df=df[(df.index>'2022-06-04')&(df.index<'2022-06-09')]
fig=cfg.multiUnitGraphSP(df.resample('600s').mean())
fig.show()
sys.exit()
def generate_data_gaston():
    for nb in [1,2,3,4]:
        tags=cfg.getTagsTU('SEH1.STB_STK_0'+str(nb)+'.ET.*HM05')+['SEH1.STK_ALIM_0'+str(nb)+'.IT_HM05']
        t0=pd.Timestamp('2022-05-19 08:00',tz='CET')
        # t1=pd.Timestamp('2022-05-10 08:00',tz='CET')
        t1=pd.Timestamp.now(tz='CET')-pd.Timedelta(hours=1)
        # df=cfg.streamer.load_parkedtags_daily(t0,t1,tags,cfg.folderPkl,rs='60s',rsMethod='mean',verbose=True)
        df=cfg.loadtags_period(t0,t1,tags,rs='60s',rsMethod='mean',verbose=True)
        df.to_pickle('stack'+str(nb)+'.pkl')
        # fig=cfg.multiUnitGraphSP(df).show()
        print(time.time()-start)

folderFigures='/home/dorian/sylfen/programmerBible/doc/pictur/smallpower/'
for k in [4]:
    df=pd.read_pickle('data/stack'+str(k)+'.pkl')
    fig=cfg.multiUnitGraphSP(df.resample('600s').mean())
    # fig.show()
    issues.save_figure(fig,'tensions_stacks'+str(k),folderFigures,as_png=True)
