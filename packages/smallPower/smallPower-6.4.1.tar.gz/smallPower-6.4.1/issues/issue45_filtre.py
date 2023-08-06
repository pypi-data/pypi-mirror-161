from __future__ import division
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd,sys
from scipy import signal
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
from scipy.signal.ltisys import TransferFunction as TransFun
from numpy import polymul,polyadd


##### utils
class ltimul(TransFun):
    def __neg__(self):
        return ltimul(-self.num,self.den)

    def __floordiv__(self,other):
        # can't make sense of integer division right now
        return NotImplemented

    def __mul__(self,other):
        if type(other) in [int, float]:
            return ltimul(self.num*other,self.den)
        elif type(other) in [TransFun, ltimul]:
            numer = polymul(self.num,other.num)
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    def __truediv__(self,other):
        if type(other) in [int, float]:
            return ltimul(self.num,self.den*other)
        if type(other) in [TransFun, ltimul]:
            numer = polymul(self.num,other.den)
            denom = polymul(self.den,other.num)
            return ltimul(numer,denom)

    def __rtruediv__(self,other):
        if type(other) in [int, float]:
            return ltimul(other*self.den,self.num)
        if type(other) in [TransFun, ltimul]:
            numer = polymul(self.den,other.num)
            denom = polymul(self.num,other.den)
            return ltimul(numer,denom)

    def __add__(self,other):
        if type(other) in [int, float]:
            return ltimul(polyadd(self.num,self.den*other),self.den)
        if type(other) in [TransFun, type(self)]:
            numer = polyadd(polymul(self.num,other.den),polymul(self.den,other.num))
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    def __sub__(self,other):
        if type(other) in [int, float]:
            return ltimul(polyadd(self.num,-self.den*other),self.den)
        if type(other) in [TransFun, type(self)]:
            numer = polyadd(polymul(self.num,other.den),-polymul(self.den,other.num))
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    def __rsub__(self,other):
        if type(other) in [int, float]:
            return ltimul(polyadd(-self.num,self.den*other),self.den)
        if type(other) in [TransFun, type(self)]:
            numer = polyadd(polymul(other.num,self.den),-polymul(other.den,self.num))
            denom = polymul(self.den,other.den)
            return ltimul(numer,denom)

    # sheer laziness: symmetric behaviour for commutative operators
    __rmul__ = __mul__
    __radd__ = __add__

    def to_lti(self):
        return signal.lti(self.num,self.den)

def f_transfert_latex(sys):
    num = ' + '.join([str(v)+'*s^'+str(k) for k,v in enumerate(np.flip(sys.num))])
    den = ' + '.join([str(v)+'*s^'+str(k) for k,v in enumerate(np.flip(sys.den))])
    return r'$H = \frac{'+num+'}{'+den+'}$'

def show_transfer_function(sys,nyquist=False,ws=None):
    if isinstance(sys,ltimul):
        sys=signal.lti(sys.num,sys.den)
    hname=f_transfert_latex(sys)
    w,G,a=sys.bode()
    if nyquist:
        if not ws is None:w=ws
        _,h=sys.freqresp(w)
        f=w/(2*np.pi)
        fig=go.Figure(go.Scatter(x=h.real,y=h.imag,hovertemplate=' freq = %{text:.2f} Hz <br>  x:%{x:.4f} <br>  y:%{y:.4f}',text=f))
    else:
        fig = make_subplots(rows=2, cols=1)
        f=w/(2*np.pi)
        fig.add_trace(go.Scatter(x=f,y=G,name='gain(dB)'),row=1,col=1)
        fig.add_trace(go.Scatter(x=f,y=a,name='dephasage(degrees)'),row=2,col=1)
        fig.update_xaxes(title='frequency(Hz)',showgrid=True, gridwidth=2, gridcolor='black',type='log')

    fig.update_traces(mode='lines+markers')
    fig.update_layout(title=hname)
    fig.show()
    return fig

def show_transfer_functions(systems,ws=None,names=None):
    fig = make_subplots(rows=2, cols=1)
    if names is None:names=[str(k) for k in range(len(systems))]
    for k,sys,name in zip(range(len(systems)),systems,names):
        if isinstance(sys,ltimul):
            sys=signal.lti(sys.num,sys.den)
        w,G,a=sys.bode()
        f=w/(2*np.pi)
        fig.add_trace(go.Scatter(x=f,y=G,name='gain_'+name+'(dB)'),row=1,col=1)
        fig.add_trace(go.Scatter(x=f,y=a,name='dephasage_'+name+'(degrees)'),row=2,col=1)

    fig.update_xaxes(title='frequency(Hz)',showgrid=True, gridwidth=2, gridcolor='black',type='log')
    fig.update_traces(mode='lines+markers')
    fig.update_layout(title='compare transfer functions')
    fig.show()
    return fig

def show_std_layout(fig,title):
    fig.update_layout(title=title)
    fig.update_traces(mode='lines+markers')
    fig.show()

##### demos
def s_bode_vs_freqs_vs_mano():
    b, a = signal.cheby2(4, 40, 100, 'low', analog=True)
    ##### b,a bode diagramm
    w, h = signal.freqs(b, a)
    plt.semilogx(w, 20 * np.log10(abs(h)))
    plt.title('Chebyshev Type II frequency response (rs=40)')
    plt.xlabel('Frequency [radians / second]')
    plt.ylabel('Amplitude [dB]')
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.axvline(100, color='green') # cutoff frequency
    plt.axhline(-40, color='green') # rs
    # plt.show()
    # NOTE:
    bode=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
    ##### b,a bode diagramm
    system = signal.TransferFunction(b,a, dt=0.05)
    s_bode=signal.dbode(system)
    s_bode=pd.DataFrame(s_bode,index=['frequency(Hz)','gain(Db)_db','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    s_bode.index=s_bode.index/(2*np.pi)
    fig1=px.scatter(s_bode.melt(ignore_index=False),facet_row='variable',log_x=True);fig1.update_traces(mode='lines+markers');fig1.update_yaxes(matches='x').show()
    fig2=px.scatter(bode.melt(ignore_index=False),facet_row='variable',log_x=True);fig2.update_traces(mode='lines+markers');fig2.update_yaxes(matches='x').show()

def sos_vs_ba_filter():
    b, a = signal.cheby2(4, 40, 100, 'low', analog=True)
    sos = signal.cheby2(4, 40, 100, 'low', analog=True,output='sos')

    b,a=signal.cheby2(12, 20, 17, 'hp', fs=1000, output='ba')
    sos=signal.cheby2(12, 20, 17, 'hp', fs=1000, output='sos')
    signal.dbode(b,a,10)
    b, a = signal.cheby2(4, 40, 100, 'hp', analog=True)
    w, h = signal.freqs(b, a)

# def analog_vs_digital():

def continuous_vs_discrete_bode(b,a,dt=0.05):

    s=signal.TransferFunction(b,a)
    s_d=signal.TransferFunction(b,a,dt=dt)

    x=np.logspace(-2,3,100)
    H=1/(-m*x**2+1j*b*x+k)

    # w, h = signal.freqresp(s)
    bode_c=pd.DataFrame(s.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    bode_d=pd.DataFrame(s_d.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    bode_m=pd.DataFrame([x,20*np.log10(np.abs(H)),np.angle(H)*180/np.pi],index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

    # bode_d=pd.DataFrame(signal.dbode(s_d),index=['frequency(Hz)','gain(Db)_db','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

    bode_c.index=bode_c.index/(2*np.pi)
    bode_d.index=bode_d.index/(2*np.pi)
    bode_m.index=bode_m.index/(2*np.pi)

    fig=go.Figure(go.Scatter(x=bode_c.index,y=bode_c['gain(dB)'],name='continuous'))
    fig.add_trace(go.Scatter(x=bode_m.index,y=bode_m['gain(dB)'],marker_color='red',name='manual'))
    fig.add_trace(go.Scatter(x=bode_d.index,y=bode_d['gain(dB)'],marker_color='green',name='discrete'))
    fig.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black',type='log')
    fig.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig.update_traces(mode='lines+markers')

    fig.show()

def bode_first_order():
    a=10
    b=1
    s=signal.TransferFunction([1],[a,b])
    s_d=signal.TransferFunction([1],[a,b],dt=0.0000001)

    x=np.logspace(-3,3,100)
    H=1/(1j*a*x+b)
    # w, h = signal.freqresp(massRessort)
    # bode1=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
    # bode2=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
    bode_c=pd.DataFrame(s.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    bode_d=pd.DataFrame(s_d.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    bode_m=pd.DataFrame([x,20*np.log10(np.abs(H)),np.angle(H)*180/np.pi],index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

    # bode_d=pd.DataFrame(signal.dbode(s_d),index=['frequency(Hz)','gain(Db)_db','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

    bode_c.index=bode_c.index/(2*np.pi)
    bode_d.index=bode_d.index/(2*np.pi)
    bode_m.index=bode_m.index/(2*np.pi)


    fig=go.Figure(go.Scatter(x=bode_c.index,y=bode_c['gain(dB)'],name='continuous'))
    fig.add_trace(go.Scatter(x=bode_m.index,y=bode_m['gain(dB)'],marker_color='red',name='manual'))
    fig.add_trace(go.Scatter(x=bode_d.index,y=bode_d['gain(dB)'],marker_color='green',name='discrete'))
    fig.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black',type='log')
    fig.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig.update_traces(mode='lines+markers').show()

    px.line(pd.DataFrame(s.step()).T.set_index(0)).show()
    sys.exit()
    fig1=px.scatter(bode_c.melt(ignore_index=False),facet_row='variable',log_x=True);
    fig1.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig1.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig1.update_traces(mode='lines+markers');fig1.update_yaxes(matches='x').show()

    fig2=px.scatter(bode_d.melt(ignore_index=False),facet_row='variable',log_x=True);
    fig2.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig2.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig2.update_traces(mode='lines+markers');fig2.update_yaxes(matches='x').show()

    # fig3=px.scatter(bode_m.melt(ignore_index=False),facet_row='variable',log_x=True);
    # fig3.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black')
    # fig3.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    # fig3.update_traces(mode='lines+markers');fig3.update_yaxes(matches='x').show()

def massSpring():
    url_pid= 'https://ctms.engin.umich.edu/CTMS/index.php?example=Introduction&section=ControlPID'
    m = 10  # kg
    b = 5 # N s/m
    k = 20 # N/m
    F = 20.5  # N
    massSpring=signal.lti([F],[m,b,k])
    # fig=show_transfer_function(massSpring,True)
    # fig=show_transfer_function(massSpring,False)

    times=np.linspace(0,15,1000)#seconds
    #### response to step function
    step_resp=pd.DataFrame(index=times)
    step_resp['consigne']=1
    step_resp['step,x=0']=massSpring.step(T=times)[1]
    step_resp['step,x=2']=massSpring.step(T=times,X0=[.5])[1]
    # show_std_layout(step_resp,'response to a step(echelon)')

    #### response to ramp
    ramp_resp=pd.DataFrame(index=times)
    u1=0.05*times+5
    ramp_resp['consigne1 0.05']=u1
    u2=0.005*times
    ramp_resp['consigne2 0.005']=u2
    ramp_resp['ramp1']=signal.lsim(massSpring, U=u1, T=times)[1]
    ramp_resp['ramp2']=signal.lsim(massSpring, U=u2, T=times)[1]
    # show_std_layout(ramp_resp,'response to a ramp')

    #### response to sinusoide excitation
    # times=np.linspace(0,25,10000)#seconds
    # sinus_resp=pd.DataFrame(index=times)
    # dfs=[]
    # for k in [0.05,0.1,0.25,0.5,1,5]:
    #     u=np.sin(k*2*np.pi*times)
    #     df1 = pd.DataFrame(u,index=times,columns=['value'])
    #     df1['variable']='sinus' + str(k)+' Hz'
    #     df1['frequence']=k
    #     df2 = pd.DataFrame(signal.lsim(massSpring, U=u, T=times)[1],index=times,columns=['value'])
    #     df2['variable']='resp '+str(k)
    #     df2['frequence']=k
    #     dfs.append(pd.concat([df1,df2]))
    #
    # sinus_resp=pd.concat(dfs)
    # fig=px.scatter(sinus_resp,y='value',color='variable',facet_col='frequence',facet_col_wrap=2);
    # fig=fig.update_yaxes(matches=None)
    # show_std_layout(fig,'response to a sinusoidal excitation'+f_transfert_latex(massSpring))

    #### response to square
    times=np.linspace(0,150,1000)#seconds
    #### response to step function
    square_df=pd.DataFrame(index=times)
    square_df['square']=signal.square(times*0.05)
    square_df['response']=signal.lsim(massSpring,U=square_df['square'],T=times)[1]
    # fig=px.scatter(square_df);show_std_layout(fig,'response to a square')

    #### reponse echelon en boucle ouverte du PID
    kp = 1
    ki = 1
    kd = 1
    C = signal.lti([kd,kp,ki],[1])
    #### response to step function
    C = ltimul([kd,kp,ki],[1,0])
    # C = TransFun([kd,kp,ki],[1,0])
    massSpring=ltimul([F],[m,b,k])
    BO=massSpring*C
    BF=BO/(1+BO)
    show_transfer_functions([massSpring,C,BO,BF],names=['massSpring','C','BO','BF'])

    times=np.linspace(0,25,1000)#seconds
    step_resp=pd.DataFrame(index=times)
    step_resp['consigne']=1
    step_resp['step massSpring']=massSpring.to_lti().step(T=times)[1]
    step_resp['step BO']=BO.to_lti().step(T=times)[1]
    step_resp['step BF']=BF.to_lti().step(T=times)[1]
    fig=px.scatter(step_resp);show_std_layout(fig,'response to a step(echelon)')


sys.exit()
