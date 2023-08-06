import os,subprocess as sp,pandas as pd
import smallpower.smallPower as smallPower

def get_file_from_gaston(filename='df_issue38.pkl',dl=True):
    folder_data=os.path.dirname(__file__)+'/data/'
    fullpath=folder_data+filename
    if dl:sp.run('scp sylfenGaston:~/smallpower/issues/data/'+filename+ ' ' + fullpath,shell=True)
    df=pd.read_pickle(fullpath)
    return df

def show_file_from_gaston(filename='df_issue38.pkl',dl=True):
    df  = get_file_from_gaston(filename,dl)
    fig = cfg.multiUnitGraphSP(df.astype(float))
    fig = cfg.update_lineshape_fig(fig)
    fig.show()



cfg = smallPower.SmallPowerComputer()

df  = get_file_from_gaston('easy_tags100_147.pkl',True)
df  = df.resample('10H',closed='right',label='right').mean()
fig = cfg.multiUnitGraphSP(df)
fig = cfg.update_lineshape_fig(fig)
fig.show()
