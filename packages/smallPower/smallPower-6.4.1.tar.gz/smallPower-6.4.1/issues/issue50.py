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

folder_figures='/home/dorian/sylfen/programmerBible/doc/pictur/issue50/'

##### make sure the period has the 4 stacks working

import time,pandas as pd,numpy as np
import smallpower.smallPower as smallPower
cfg=smallPower.SmallPowerComputer()
start=time.time()
t0 = pd.Timestamp('2022-05-24 08:00',tz='CET')
t1 = pd.Timestamp('2022-06-17 22:00',tz='CET')
tags=[
    'SEH1.STB_STK_TT_00_HC20',
    'SEH1.STB_GFD_01_PT_01.HM05',
    'SEH1.STB_GFD_02_PT_01.HM05',
    'SEH1.STB_GFC_01_PT_01.HM05',
    'SEH1.STB_GFC_02_PT_01.HM05',
    'SEH1.L025_FUEL_FT_01.HM05',
    'SEH01.L138_O2_FT_01.HM05',
    'SEH1.L213_H2OPa_FT_01.HM05',
    'SEH1.L213_H2OPb_FT_01.HM05',
    'SEH01.L118_O2_FT_01.HM05',
    'SEH1.L032_FUEL_FT_01.HM05',
    'SEH1.L041_H2_FT_01.HM05',
    'SEH1.GWPBH_TNK_01_PT_01.HM05',
    'SEH1.L035_FUEL_PT_01.HM05',
    'SEH1.L036_FUEL_PT_01.HM05',
    'SEH0.L138_O2_PT_01.HM05',
    'SEH0.L118_O2_PT_01.HM05',
    'SEH1.STK_ALIM_01.IT_HM05',
    'SEH1.STK_ALIM_02.IT_HM05',
    'SEH1.STK_ALIM_03.IT_HM05',
    'SEH1.STK_ALIM_04.IT_HM05',
]
df = cfg.loadtags_period(t0,t1,tags,rs='300s',rsMethod="mean",closed='right',verbose=True)
print(time.time()-start)
# df.to_pickle('/home/sylfen/tests/df_issue50.pkl')
df.to_excel()
