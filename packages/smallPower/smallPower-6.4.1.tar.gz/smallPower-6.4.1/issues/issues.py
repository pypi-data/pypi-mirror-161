import time,sys,os
start=time.time()
import pandas as pd,numpy as np
import smallpower.smallPower as smallPower
from smallpower import conf
from dorianUtils.comUtils import html_table
from dorianUtils.utilsD import Utils
import subprocess as sp,os
import plotly.express as px


cfg = smallPower.SmallPowerComputer()

class Issues():

    def download_data(self,t0,t1,tags):
        listDays=[cfg.streamer.to_folderday(k)[:-1] for k in pd.date_range(t0,t1,freq='D')]
        for d in listDays:
            for t in tags:
                filename='data_ext/smallPower_daily/'+d+t+'.pkl'
                folder_final=cfg.folderPkl+d[:-1]
                if not os.path.exists(folder_final):os.mkdir(folder_final)
                # print(filename,folder_final)
                sp.run('scp sylfenGaston:'+filename + ' ' + folder_final,shell=True)

    def replot_colors(self,fig):
        colors=Utils().colors_mostdistincs
        for k,trace in enumerate(fig.data):
            trace.marker.color=colors[k]
            trace.marker.symbol='circle'
            trace.line.color=colors[k]
            trace.line.dash='solid'
        return fig

    def get_file_from_gaston(self,filename='df_issue38.pkl',dl=True,host='sylfenGastonFibre'):
        folder_data=os.path.dirname(__file__)+'/data/'
        fullpath=folder_data+filename
        if dl:sp.run('scp ' + host + ':tests/'+filename+ ' ' + fullpath,shell=True)
        df=pd.read_pickle(fullpath)
        return df

    def show_file_from_gaston(self,filename='df_issue38.pkl',dl=True):
        df  = get_file_from_gaston(filename,dl)
        fig = cfg.multiUnitGraphSP(df.astype(float))
        fig = cfg.update_lineshape_fig(fig)
        fig.show()

    def save_figure(self,fig,filename,folder_figures=None,as_png=True):
        if folder_figures is None :folder_figures='/home/dorian/sylfen/programmerBible/doc/pictur/'
        fig.write_html(folder_figures +filename +'.html')
        if as_png:
            a4_size=[210,297]
            std_screenSize=[1920,1080]
            a_ratioA4=a4_size[0]/a4_size[1]
            h=1080/2 ### it should take half the page of an A4 on a std 19/9 screen display
            w=h*a_ratioA4
            more=4
            h,w=h*more,w*more ## increase the size to improve resolution of picture when downsizing it on A4.
            fig.update_layout(font_size=12*more/1.5)
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.04,
                xanchor="left",
                x=0.01
            ))
            print(folder_figures +filename +'.png')
            fig.write_image(folder_figures +filename +'.png',height=h,width=w)
        return fig

    def push_toFolderFigures(self,df,filename,host=None,fig_generate=True,replot_cols=False,*args,**kwargs):
        df.to_pickle('data/'+filename+'.pkl')
        df.to_csv('data/'+filename+'.csv')
        if cfg is None :cfg=smallPower.SmallPowerComputer()
        if fig_generate:
            fig=cfg.multiUnitGraphSP(df);
            if replot_cols:fig=replot_colors(fig)
            save_figure(df,filename,*args,**kwargs)

        # sp.run('scp data/' + filename + '* ' + host +':'+folderGaston,shell=True)

class VersionsManager():
    def __init__(self,folderpkl):
        self.folderpkl=folderpkl

    def presence_tags(self,tags,show_res=True,recompute=True):
        listDays=os.listdir(self.folderpkl)
        df=pd.DataFrame()
        for t in tags:
            df[t] = [True if t+'.pkl' in os.listdir(self.folderpkl+d) else False for d in listDays]
        df.index=listDays
        df=df.sort_index()
        if show_res:
            html_table(df)
            px.line(df).show()
        return df
