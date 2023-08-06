#!/bin/python
# #######################
# #   GLOBAL VARIABLES  #
# # COMPUTER DEPENDENT  #
# #######################
import os,sys, time, datetime as dt,importlib,pickle,glob,re,socket,psycopg2
start=time.time()
import pandas as pd,numpy as np
from dorianUtils.utilsD import Utils
from dorianUtils.comUtils import (
    VisualisationMaster_daily,
    Configurator,
    SuperDumper_daily,
    FileSystem,
    Opcua_Client,
    SetInterval,
    timenowstd,print_file,computetimeshow
)
from dorianUtils.Simulators import SimulatorOPCUA
from dorianUtils.VersionsManager import VersionsManager_daily
from . import conf

class Indicators():
    def __init__(self):
        self.cst=conf.CONSTANTS

    def find_alpha_low_pass(self,theta,DT=1):
        '''
        - theta : durée en seconde pour converger
        - DT    : période d'échantillonnage en secondes
        returns : valeur du paramètre alpha adimensionnel et compris entre 0 et 1
        '''
        return 6*np.pi*DT/(theta+6*np.pi*DT)

    def low_pass_filter(self,x,x_1,alpha):
        '''
        x     : value at time t
        x_1   : value at time t-1
        alpha : coefficient cutoff frequency between 0 and 1
        '''
        return alpha*x+(1-alpha)*x_1
    def o2_stack_alim(self,I_conventionnel):
        ## o2out has the sign of I_conventionnel
        o2_out       = I_conventionnel*25/(4*self.cst['FAR']) ##25 cells
        o2_out_Nlmin = o2_out*self.cst['vlm']*60
        return o2_out_Nlmin
    def h2_stack_out(self,I_conventionnel):
        ## o2out has the sign of I_conventionnel
        h2_out       = I_conventionnel*25/(2*self.cst['FAR']) ##25 cells
        h2_out_Nlmin = h2_out*self.cst['vlm']*60
        return h2_out_Nlmin
    def detect_modehub(self,I_conventionel,vanneN2):
        '''4 modes:
        - SOEC, I>0
        - SOFC I>0
        - BF, I=0, vanneN2(NF) is False
        - BO, tout le reste.
        '''
        threshold=0.5
        if I_conventionel < -threshold  : mode='SOEC'
        elif I_conventionel > threshold : mode='SOFC'
        else:
            if not vanneN2:mode='BF'
            else:mode='BO'
        return mode
    def fuites_air(self,mode,o2_stack,air_in,air_out,n2_in):
        '''
        o2_stack is negative in electrolysis and positive in fuel cell mode
        Débit entrée – Débit sortie +/- fonction du courant
        Si le courant = 0 alors Si débit azote >0 alors on est en BF, sinon on est en BO
        '''
        if mode=='BF':fuiteAir = n2_in
        else:fuiteAir = air_in - o2_stack - air_out
        return fuiteAir
    def fuites_fuel(self,mode,h2stack,fuel_in,fuel_out,n2_in_fuel):
        '''
        - mode : got from self.detect_modehub
        - h2stack is taken always positive for the formula
        '''
        h2stack = np.abs(h2stack)
        if mode=='SOEC':
            fuitefuel = fuel_in + h2stack - fuel_out
        elif mode=='SOFC':
            fuitefuel = fuel_in - h2stack
        elif mode=='BF':
            fuitefuel = n2_in_fuel + fuel_in
        else:
            fuitefuel = fuel_in - fuel_out
        return fuitefuel
    def rendement_sys(self,mode,power_sys,h2_produced):
        '''power_sys in kW and h2 produced or consumed(proportionel to the stacks current) in the stack Nl/min'''
        #conversion in mol/s
        h2_mols  = np.abs(h2_produced/60/22.4)
        #take the power
        h2_power_chimique = h2_mols*self.cst['PCImol_H2']
        #remove extra power not from the system
        rendement=0
        total_power = power_sys-1000
        if mode=='SOEC':
            if total_power>0:
                rendement = h2_power_chimique/total_power
        elif mode=='SOFC':
            if h2_power_chimique>0:
                rendement = -total_power/h2_power_chimique
        return rendement*100
    def rendement_gv(self,FT_IN_GV,TT_IN_GV,TT_OUT_GV,power_elec_chauffe):
        '''
        - FT_IN_GV should be in g/min
        '''
        debitEau_gs = FT_IN_GV/60
        #calcul
        power_chauffe_eau_liq = max(0,debitEau_gs*self.cst['Cp_eau_liq']*(100-TT_IN_GV))
        power_vapo_eau        = debitEau_gs*self.cst['Cl_H2O']
        power_chauffe_vap     = max(0,debitEau_gs*self.cst['Cp_eau_vap']*(TT_OUT_GV-100))
        power_total_chauffe = power_chauffe_eau_liq + power_vapo_eau +  power_chauffe_vap
        # print(power_total_chauffe,power_elec_chauffe)
        if not power_elec_chauffe==0:
            return power_total_chauffe/power_elec_chauffe*100
        else:
            return 0
    def pertes_thermiques_stack(self,air_in_tt,air_in_ft,air_stack_tt,fuel_in_tt,fuel_in_ft,fuel_stack_tt,puissance_four):
        '''
        - _ft variables are volumetric flows in Nl/min
        - balayage should be added !
        '''
        # cp_fuel,M_fuel = self.dfConstants.loc['Cp_' + fuel,'value'],self.dfConstants.loc['Mmol_' + fuel,'value']
        cp_fuel,M_fuel = self.cst['Cp_H2'],self.cst['Mmol_H2']
        cp_air,M_air = self.cst['Cp_air'],self.cst['Mmol_Air']

        surchauffe_Air  = (air_stack_tt-air_in_tt)*cp_air*M_air*air_in_ft/22.4/60
        surchauffe_Fuel = (fuel_stack_tt-fuel_in_tt)*cp_fuel*M_fuel*fuel_in_ft/22.4/60
        # surchauffe_AirBalayage = (air_stack_tt-air_in_tt)*cp_air*M_air*debitAirBalayage_mols/22.4/60

        total_puissance_surchauffe_gaz = surchauffe_Air + surchauffe_Fuel
         # + surchauffe_AirBalayage
        if total_puissance_surchauffe_gaz>0:
            return puissance_four/total_puissance_surchauffe_gaz
        # return total_puissance_surchauffe_gaz/puissance_four
        else:
            return np.nan
    # ##############
    #       old    #
    # ##############
    def _get_tags_Istacks(self):
        return {
            'Istacks' : self.getTagsTU('STK.*IT.*HM05'),
            }
    def i_total(self,Istacks):
        return sum(Istacks)
    def fuelmodeNicolas(self,dvvv):
        # NF: False<==>fermé ; NO: False<==>ouvert
        # NF: False<==>ouvert ; NO True<==>fermé
        modeFuel = []
        # Gonflage :
        # L035 ou L040 fermées et L039 fermée et L027(NO) fermée
        if (not dvvv['vanne35'] or not dvvv['vanne40']) and (not dvvv['vanne39']) and (dvvv['vanne27']):
            modeFuel.append('gonflage')

            # Boucle fermée recirculation à froid (mode pile):
            # L026(NO) et L029 fermées, L027(NO) ouverte, L035 OU L040 fermées
            if (dvvv['vanne26']) and (not dvvv['vanne29']) and (not dvvv['vanne27']) and (not dvvv['vanne35']) or (not dvvv['vanne40']):
                modeFuel.append('recircuFroidPile')

                # Boucle ouverte (fonctionnement électrolyse ou boucle ouverte pendant les transitions) :
                # (L035 ET L040 ouvertes) ou L026(NO) ouverte ou L029 ouverte
                if (dvvv['vanne35'] and dvvv['vanne40']) or (not dvvv['vanne26']) or (dvvv['vanne29']):
                    modeFuel.append('bo_electrolyse')

                    # Fonctionnement mode gaz naturel :
                    # - L027(NO) fermée, L039 ouverte
                    if (dvvv['vanne27'] and dvvv['vanne39']):
                        modeFuel.append('gaz_nat')
                        return modeFuel
    def verifDebitmetre(self,L032,L303,L025):
        # Vérif débitmètres ligne fuel BF = L032 FT – L303 – L025
        return L032-L303-L025
    def get_tags_modeFuel(self):
        return {
                'vanne26' : self.getTagsTU('l026.*ECV'),#NO
                'vanne27' : self.getTagsTU('l027.*ECV'),#NO
                'vanne29' : self.getTagsTU('l029.*ECV'),#NF
                'vanne35' : self.getTagsTU('l035.*ECV'),#NF
                'vanne39' : self.getTagsTU('l039.*ECV'),#NF
                'vanne40' : self.getTagsTU('l040.*ECV'),#NF
        }
    def coefFuitesFuel(self,Itotal,modefuel,L303,L041,L032,L025):
        '''
        Gonflage :
        - L035 ou L040 fermées et L039 fermée et L027 fermée
        - fuites fuel BF = L303 + L041 (+ Somme i x 25 / 2F)  note : normalement dans ce mode le courant est nul.
        Boucle fermée recirculation à froid (mode pile)
        - L026 et L029 fermées, L027 ouverte, L035 OU L040 fermées
        - fuites fuel BF = L303 + L041 + Somme i x 25 / 2F
        Boucle ouverte (fonctionnement électrolyse ou boucle ouverte pendant les transitions) :
        - (L035 ET L040 ouvertes) ou L026 ouverte ou L029 ouverte
        - fuite ligne fuel BO = L303 + L041 + Somme i x 25 / 2F – L025
        Fonctionnement mode gaz naturel :
        - L027 fermée, L039 ouverte
        - fuites fuel BO = (L032 – L303) x 4 + L303 + L041 + Somme i x 25 / 2F – L025
        En résumé : trois calculs possibles du débit de fuite fuel
        Le même calcul pour les cas 1 et 2 qui sont « fermés »
        Un calcul pour le mode ouvert électrolyse ou boucle ouverte pendant les transitions
        Un calcul pour le mode gaz naturel.
        '''
        #############################
        # compute Hydrogen production
        #############################
        PH2mols = Itotal*25/(2*self.cst['FAR']) ##25 cells
        PH2Nlmin = PH2mols*self.cst['vlm']*60
        #############################
        # mode fuel
        #############################
        if modefuel=='gonflage' or modefuel=='recircuFroidPile':
            fuitesFuel = L303 + L041 + PH2Nlmin
        elif modefuel=='bo_electrolyse':
            fuitesFuel = L303 + L041 + PH2Nlmin - L025
        elif modefuel=='gaz_nat':
            fuitesFuel = (L032 - L303)*4 + L303 + L041 + PH2Nlmin - L025
        return fuitesFuel

class Simulator_beckhoff(SimulatorOPCUA):
    def __init__(self):
        SimulatorOPCUA.__init__(self,conf.ENDPOINTURL+':'+str(int(conf.PORT_BECKHOFF)),conf.BECKHOFF_PLC,conf.NAMESPACE_BECKHOFF)

class Beckhoff_client(Opcua_Client):
    def __init__(self,*args,**kwargs):
        Opcua_Client.__init__(self,
            device_name  = 'beckhoff',
            ip           = conf.IP_BECKHOFF,
            port         = conf.PORT_BECKHOFF,
            dfplc        = conf.BECKHOFF_PLC,
            nameSpace    = conf.NAMESPACE_BECKHOFF,
            *args,**kwargs
        )
        self.tags_for_indicators = conf.TAGS_FOR_INDICATORS
        self.folderPkl = conf.FOLDERPKL
        self.listdays = pd.Series(os.listdir(self.folderPkl)).sort_values(ascending=False)

        self.__set_security()
        self.indicators = Indicators()
        self.plc_indicator_tags = conf.PLC_INDICATOR_TAGS
        self.indicators_variables = conf.PLC_INDICATOR_TAGS['variable_name'].reset_index().set_index('variable_name').squeeze().to_dict()
        self.currentTime = pd.Timestamp.now(tz=conf.TZ_RECORD)
        self.buffer_indicators = self._initialize_indicators_buffer()
        self.dbParameters,self.dbTable = conf.DB_PARAMETERS,conf.DB_TABLE

    def __set_security(self):
        certif_path = conf.CONFFOLDER + 'my_cert.pem'
        key_path    = conf.CONFFOLDER + 'my_private_key.pem'
        sslString = 'Basic256Sha256,Sign,' + certif_path + ',' + key_path
        if conf.SIMULATOR:
            print_file('security check succedeed because working with SIMULATOR==>no need to enter credentials and rsa keys\n',filename=self.log_file,with_infos=False)
        else:
            try:
                self._client.set_security_string(sslString)
                self._client.set_user("Alpha")
                self._client.set_password("Alpha$01")
                print_file('beckhoff security check succeeded!',filename=self.log_file)
            except:
                print_file('beckhoff security check FAILED',filename=self.log_file)
                sys.exit()

    def get_most_recent_timestamp_val(self,tag,debug=False):
        val=0
        broken=False
        for day in self.listdays:
            tag_path=self.folderPkl+day+'/'+tag+'.pkl'
            if os.path.exists(tag_path):
                df = pd.read_pickle(tag_path).dropna()
                if not df.empty:
                    val=df.iloc[-1]
                    if debug:print_file('last value for tag :\n' + tag ,df.iloc[[-1]],'\n')
                    broken=True
                    break
        if not broken and debug:
            print_file('\n'+' '*20+'NO VALUE FOUND FOR TAG :' + tag + ' in\n',self.folderPkl)
            print_file('listfolders:\n'+'*'*60,'\n',[k for k in self.listdays],'\n'+'*'*60)
        return val

    def _initialize_indicators_buffer(self):
        tags_buffer = {var:self.get_most_recent_timestamp_val(ind) for ind,var in self.plc_indicator_tags['variable_name'].to_dict().items()}
        print_file('\ninitialization of low pass tags done!\n',filename=self.log_file,with_infos=False)
        return tags_buffer

    def compute_indicators(self,debug=False):
        '''
        - tag_for_ind_val  --> dictionnary of tag value used for computation tag_var:value
        - d_tags_hc --> dictionnary of calculated tag/value tag:[value,timestamp]
        '''
        ### gather first all values of tags needed for computation
        tag_for_ind_val = self.collectData(conf.TZ_RECORD,self.tags_for_indicators.to_list())
        # if debug:print_file('\n'.join([k.ljust(50)+' : '+str(v) for k,v in tag_for_ind_val.items()]))
        ### rename the keys with those of tags_for_computation
        tag_for_ind_val  = {ind:tag_for_ind_val[tag_ind]['value'] for ind,tag_ind in self.tags_for_indicators.to_dict().items()}
        if debug:print_file('\n'.join([k.ljust(50)+' : '+str(v) for k,v in tag_for_ind_val.items()]))
        d_tags_hc = {}
        # ================================================
        # courant en valeur absolue et convention physique
        # ================================================
        start_now = pd.Timestamp.now(tz=conf.TZ_RECORD)
        now_current=start_now
        I_indicators={ind:tag_ind for ind,tag_ind in self.tags_for_indicators.to_dict().items() if 'current_stack' in ind}
        for I_ind_stack,I_tag_ind_stack in I_indicators.items() :
            # print_file(I_ind_stack,I_tag_ind_stack)
            d_tags_hc[I_tag_ind_stack + '.HC09'] = [np.abs(tag_for_ind_val[I_ind_stack]),now_current.isoformat()]# absolute value
            d_tags_hc[I_tag_ind_stack + '.HC13'] = [-tag_for_ind_val[I_ind_stack],now_current.isoformat()]# ec convention
        # ======================
        #  courants total stack
        # ======================
        # valeur absolute
        d_tags_hc['I_absolue'] = [sum([v[0] for k,v in d_tags_hc.items() if 'IT_HM05.HC09' in k]),now_current.isoformat()]
        #convention physique
        I_conventionel = sum([v[0] for k,v in d_tags_hc.items() if 'IT_HM05.HC13' in k])
        d_tags_hc['I_conventionnel'] = [I_conventionel,now_current.isoformat()]

        # ======================
        #       modehub
        # ======================
        modehub = self.indicators.detect_modehub(I_conventionel,tag_for_ind_val['vanneBF'])

        # ======================
        #       fuite air
        # ======================
        now_air = pd.Timestamp.now(tz=conf.TZ_RECORD)
        #--- o2 out of stack
        o2_out_alim = self.indicators.o2_stack_alim(I_conventionel)
        o2_out_hm05 = tag_for_ind_val['air_out_ft'] - tag_for_ind_val['air_in_ft']
        #--- fuites
        air_in,air_out,n2_in = [tag_for_ind_val[t] for t in ['air_in_ft','air_out_ft','n2_in_air']]
        fuite_air            = self.indicators.fuites_air(modehub,o2_out_alim,air_in,air_out,n2_in)
        if not tag_for_ind_val['air_out_pt']==0:
            fuite_air_gfd        = fuite_air/tag_for_ind_val['air_out_pt']
        else:
            fuite_air_gfd =np.nan

        # ======================
        #       fuite fuel
        # ======================
        now_fuel = pd.Timestamp.now(tz=conf.TZ_RECORD)
        #--- h2 out of stack
        h2_out_alim = self.indicators.h2_stack_out(I_conventionel)
        h2_out_hm05 = tag_for_ind_val['fuel_out_ft'] - tag_for_ind_val['h2_in_ft']
        #--- fuites
        fuel_in,fuel_out,n2_in_fuel=[tag_for_ind_val[t] for t in ['h2_in_ft','fuel_out_ft','n2_in_fuel']]
        fuite_fuel = self.indicators.fuites_fuel(modehub,h2_out_alim,fuel_in,fuel_out,n2_in_fuel)
        if not tag_for_ind_val['fuel_out_pt']==0:
            fuite_fuel_gfd = fuite_fuel/tag_for_ind_val['fuel_out_pt']
        else:
            fuite_fuel_gfd = np.nan

        # ======================
        #   rendement systeme
        # ======================
        now_rendement = pd.Timestamp.now(tz=conf.TZ_RECORD)
        rendement_sys = self.indicators.rendement_sys(modehub,tag_for_ind_val['power_total'],h2_out_alim)

        # ======================
        #   rendement gv
        # ======================
        TT_IN_GV,TT_OUT_GV = [tag_for_ind_val[t] for t in ['tt_in_gv','tt_out_gv']]
        ## gv1a
        power_tags = [k for k in self.tags_for_indicators.index if 'power_gv_a' in k]
        power_elec_chauffe = sum([tag_for_ind_val[t] for t in power_tags])
        rendement_gv_a = self.indicators.rendement_gv(tag_for_ind_val['ft_in_gv_a'],TT_IN_GV,TT_OUT_GV,power_elec_chauffe)
        ## gv1b
        rendement_gv_b = self.indicators.rendement_gv(tag_for_ind_val['ft_in_gv_b'],TT_IN_GV,TT_OUT_GV,tag_for_ind_val['power_gv_b_1'])

        # ============================
        #   pertes thermiques stack
        # ============================
        now_pertes_stack = pd.Timestamp.now(tz=conf.TZ_RECORD)
        air_in_tt,air_in_ft,air_stack_tt  = [tag_for_ind_val[t] for t in ['air_in_tt','air_in_ft','air_stack_tt']]
        fuel_in_tt,h2_in_ft,fuel_stack_tt,h2_cold_loop_ft = [tag_for_ind_val[t] for t in ['fuel_in_tt','h2_in_ft','fuel_stack_tt','h2_cold_loop_ft']]
        puissance_four = sum([tag_for_ind_val['power_chauffant_'+str(k)] for k in [1,2,3]])
        fuel_in_ft     = h2_in_ft + h2_cold_loop_ft
        pertes_stack   = self.indicators.pertes_thermiques_stack(air_in_tt,air_in_ft,air_stack_tt,fuel_in_tt,fuel_in_ft,fuel_stack_tt,puissance_four)

        # ======================
        #   compteurs, cumul
        # ======================
        now_cumul = pd.Timestamp.now(tz=conf.TZ_RECORD)
        durationh = (start_now - self.currentTime).total_seconds()/3600
        self.currentTime = start_now #### update the current time
        # ------ tps fonctionnement T>600°C
        tps_T600 = self.buffer_indicators['tps_T600']
        if tag_for_ind_val['T_stacks'] > 600: tps_T600+= durationh

        # ------ h2 production/SOEC
        tps_SOEC          = self.buffer_indicators['tps_SOEC']
        tps_SOFC          = self.buffer_indicators['tps_SOFC']
        cumul_h2_produced = self.buffer_indicators['cumul_h2_produced']
        cumul_h2_consumed = self.buffer_indicators['cumul_h2_consumed']
        nbTransitions     = self.buffer_indicators['nbTransitions']
        if I_conventionel<-0.01:
            # print_file(durationh)
            # print_file(tps_SOEC)
            tps_SOEC+= durationh
            cumul_h2_produced+= h2_out_hm05*durationh*60/1000
        if I_conventionel>0.01:
            tps_SOFC+= durationh
            cumul_h2_consumed+= h2_in_ft*durationh*60/1000

        if not modehub==self.buffer_indicators['modehub']:
            if modehub=='SOEC' or modehub =='SOFC':
                nbTransitions=+1

        # ======================
        #   apply lowpassfilter
        # ======================
        now_lowpass = pd.Timestamp.now(tz=conf.TZ_RECORD)

        fuite_air      = self.indicators.low_pass_filter(fuite_air,self.buffer_indicators['fuite_air'],0.005)
        fuite_air_gfd  = self.indicators.low_pass_filter(fuite_air_gfd,self.buffer_indicators['fuite_air_gfd'],0.005)
        fuite_fuel     = self.indicators.low_pass_filter(fuite_fuel,self.buffer_indicators['fuite_fuel'],0.005)
        fuite_fuel_gfd = self.indicators.low_pass_filter(fuite_fuel_gfd,self.buffer_indicators['fuite_fuel_gfd'],0.005)
        rendement_sys  = self.indicators.low_pass_filter(rendement_sys,self.buffer_indicators['rendement_sys'],0.005)
        rendement_gv_a = self.indicators.low_pass_filter(rendement_sys,self.buffer_indicators['rendement_gv_a'],0.005)
        rendement_gv_b = self.indicators.low_pass_filter(rendement_sys,self.buffer_indicators['rendement_gv_b'],0.005)
        pertes_stack   = self.indicators.low_pass_filter(pertes_stack,self.buffer_indicators['pertes_stack'],0.005)
        power_stb      = self.indicators.low_pass_filter(tag_for_ind_val['power_enceinte_thermique'],self.buffer_indicators['power_stb'],0.005)

        # ======================
        #       update all
        # ======================
        d_tags_hc['modehub']           = [modehub,now_current.isoformat()]
        d_tags_hc['o2_out_alim']       = [np.abs(o2_out_alim),now_air.isoformat()]
        d_tags_hc['o2_out_hm05']       = [o2_out_hm05,now_air.isoformat()]
        d_tags_hc['fuite_air']         = [fuite_air,now_lowpass.isoformat()]
        d_tags_hc['fuite_air_gfd']     = [fuite_air_gfd,now_lowpass.isoformat()]
        d_tags_hc['h2_out_alim']       = [np.abs(h2_out_alim),now_fuel.isoformat()]
        d_tags_hc['h2_out_hm05']       = [h2_out_hm05,now_fuel.isoformat()]
        d_tags_hc['fuite_fuel']        = [fuite_fuel,now_lowpass.isoformat()]
        d_tags_hc['fuite_fuel_gfd']    = [fuite_fuel_gfd,now_lowpass.isoformat()]
        d_tags_hc['rendement_sys']     = [rendement_sys,now_lowpass.isoformat()]
        d_tags_hc['rendement_gv_a']    = [rendement_gv_a,now_lowpass.isoformat()]
        d_tags_hc['rendement_gv_b']    = [rendement_gv_b,now_lowpass.isoformat()]
        d_tags_hc['pertes_stack']      = [pertes_stack,now_lowpass.isoformat()]
        d_tags_hc['tps_T600']          = [tps_T600,now_cumul.isoformat()]
        d_tags_hc['tps_SOEC']          = [tps_SOEC,now_cumul.isoformat()]
        d_tags_hc['tps_SOFC']          = [tps_SOFC,now_cumul.isoformat()]
        d_tags_hc['cumul_h2_produced'] = [cumul_h2_produced,now_cumul.isoformat()]
        d_tags_hc['cumul_h2_consumed'] = [cumul_h2_consumed,now_cumul.isoformat()]
        d_tags_hc['nbTransitions']     = [nbTransitions,now_cumul.isoformat()]
        d_tags_hc['power_stb']         = [power_stb,now_lowpass.isoformat()]

        self.buffer_indicators = {ind_var:value[0] for ind_var,value in d_tags_hc.items()}
        # rename the keys of d_tags_hc using the indicator tags and not the indicator variable names

        d_tags_hc = {self.indicators_variables[ind_var]:val for ind_var,val in d_tags_hc.items()}
        return d_tags_hc

    def insert_indicators_intodb(self):
        if not self.isConnected:return
        try :
            connReq = ''.join([k + "=" + v + " " for k,v in self.dbParameters.items()])
            dbconn = psycopg2.connect(connReq)
        except:
            print_file('problem connecting to database ',self.dbParameters,);return
        cur  = dbconn.cursor()
        start=time.time()
        try:
            data = self.compute_indicators()
        except:
            print_file(timenowstd(),' : souci computing new tags');return
        for tag in data.keys():
            # print_file(data)
            sqlreq=self.generate_sql_insert_tag(tag,data[tag][0],data[tag][1],self.dbTable)
            # print_file(sqlreq)
            cur.execute(sqlreq)
        dbconn.commit()
        cur.close()
        dbconn.close()

class Config_extender():
    def __init__(self):
        self.utils       = Utils()
        self.usefulTags  = conf.USEFUL_TAGS
        self.currentTime = pd.Timestamp.now(tz=conf.TZ_RECORD)
        self.indicators          = conf.PLC_INDICATOR_TAGS['variable_name'].reset_index().set_index('variable_name').squeeze()
        self.tags_for_indicators = conf.TAGS_FOR_INDICATORS
        self.cst                 = conf.CONSTANTS
        self.freq_indicator_tags = conf.FREQ_INDICATOR_TAGS
        ### add the calculated tags in the plc ###
        self.dfplc     = pd.concat([conf.BECKHOFF_PLC,conf.PLC_INDICATOR_TAGS.iloc[:,1:]],axis=0)
        self.alltags   = list(self.dfplc.index)
        self.listUnits = self.dfplc.UNITE.dropna().unique().tolist()

class SmallPower_dumper(SuperDumper_daily,Config_extender):
    def __init__(self,log_file_name):
        DEVICES={'beckhoff':Beckhoff_client(log_file=log_file_name)}
        SuperDumper_daily.__init__(self,DEVICES,conf.FOLDERPKL,conf.DB_PARAMETERS,conf.PARKING_TIME,
            dbTable=conf.DB_TABLE,tz_record=conf.TZ_RECORD,log_file=log_file_name)
        Config_extender.__init__(self)

        ### interval for calculated tags
        self.__dumper_calcTags = SetInterval(conf.FREQ_INDICATOR_TAGS,self.devices['beckhoff'].insert_indicators_intodb)

    def start_dumping(self):
        SuperDumper_daily.start_dumping(self)
        self.__dumper_calcTags.start()

    def stop_dumping(self):
        self.__dumper_calcTags.stop()
        SuperDumper_daily.stop_dumping(self)

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
class SmallPowerComputer(VisualisationMaster_daily,Config_extender):
    def __init__(self):
        VisualisationMaster_daily.__init__(self,conf.FOLDERPKL,conf.DB_PARAMETERS,conf.PARKING_TIME,dbTable=conf.DB_TABLE,tz_record=conf.TZ_RECORD)
        Config_extender.__init__(self)
        self._imgpeintre  = Image.open(conf.CONFFOLDER + '/pictures/peintrepalette.jpeg')
        self._sylfenlogo  = Image.open(conf.CONFFOLDER +  '/pictures/logo_sylfen.png')
        self._colorPalettes      = conf.PALETTES
        self.cst                = conf.CONSTANTS
        self.dfConstants        = conf.DFCONSTANTS
        self._enumModeHUB        = conf.ENUM_MODES_HUB
        self._unitDefaultColors  = conf.UNITDEFAULTCOLORS
        self._dftagColorCode     = conf.DFTAGCOLORCODE
        self._enumModeHUB_simple = {k:v for k,v in self._enumModeHUB.items() if 'undefined' not in v}
        self._colorshades        = list(self._colorPalettes.keys())
        self.indicators         = Indicators()
        self.folder_coarse      = self.folderPkl.replace('daily','coarse')

    def auto_resample_df(self,df,max_datapoints=100000,rsMethod='mean'):
        duration=df.index.max()-df.index.min()
        nb_datapoints=len(df)*len(df.columns)
        if nb_datapoints<max_datapoints:
            return df
        max_dt_curve=max_datapoints//len(df.columns)
        new_rs_seconds=int(duration.total_seconds()/max_dt_curve)
        df2=df.resample(str(new_rs_seconds)+'s').mean()
        return df2

    def load_coarse_data(self,t0,t1,tags,rs,rsMethod='mean'):
        #### load the data
        df=pd.concat([pd.read_pickle(self.folder_coarse+'/' + rsMethod + '/' + t + '.pkl') for t in tags],axis=1)
        dfs={}
        empty_tags=[]
        for t in tags:
            filename=self.folder_coarse+'/mean/'+t+'.pkl'
            if os.path.exists(filename):
                s=pd.read_pickle(filename)
                dfs[t]=s[~s.index.duplicated(keep='first')]
            else:
                empty_tags+=[t]

        if len(dfs)==0:
            return pd.DataFrame(columns=dfs.keys())
        df=pd.concat(dfs,axis=1)
        df=df[(df.index>=t0)&(df.index<=t1)]
        for t in empty_tags:df[t]=np.nan

        #### resample again according to the right method
        if rsMethod=='min':
            df=df.resample(rs).min()
        elif rsMethod=='max':
            df=df.resample(rs).max()
        else:
            if rsMethod=='mean':
                df=df.resample(rs).mean()
            elif rsMethod=='median':
                df=df.resample(rs).median()
            elif rsMethod=='forwardfill':
                df=df.resample(rs).ffill()
            elif rsMethod=='nearest':
                df=df.resample(rs).nearest()
        return df
    # ==============================================================================
    #                   COMPUTATION FUNCTIONS
    # ==============================================================================

    def repartitionPower(self,t0,t1,*args,expand='groups',groupnorm=None,**kwargs):
        dfs=[]
        armoireTotal = ['SEH0.JT_01.JTW_HC20']
        dfPtotal = self.loadtags_period(t0,t1,armoireTotal,*args,**kwargs)
        pg = {
            'armoire': self.getTagsTU('EPB.*JTW'),
            'enceinte thermique': self.getTagsTU('STB_HER.*JTW.*HC20'),
            'chauffant stack': self.getTagsTU('STB_STK.*JTW.*HC20'),
            'alim stack': self.getTagsTU('SEH1.STK_ALIM_0..JTW_HM05'),
            'chauffant GV': self.getTagsTU('STG.*JTW'),
            'blowers': self.getTagsTU('BLR.*JTW'),
            'pompes': self.getTagsTU('PMP.*JTW'),
            'echangeurs': self.getTagsTU('CND.*JTW'),
        }
        d = pd.DataFrame.from_dict(pg,orient='index').melt(ignore_index=False).dropna()['value']
        d = d.reset_index().set_index('value')
        allTags = list(d.index)

        df = self.loadtags_period(t0,t1,allTags,*args,**kwargs)
        for t in pg['alim stack']:
            df[t]*=1000

        if expand=='tags':
            fig = px.area(df,groupnorm=groupnorm)
        elif expand=='groups':
            df = df.melt(value_name='value',var_name='tag',ignore_index=False)
            df['group']=df.tag.apply(lambda x:d.loc[x])

            fig=px.area(df,x=df.index,y='value',color='group',groupnorm=groupnorm,line_group='tag')
            fig.update_layout(legend=dict(orientation="h"))

        ###
        fig.add_traces(go.Scatter(x=dfPtotal.index,y=dfPtotal.squeeze(),name='armoire totale(W)',
            mode='lines+markers',marker=dict(color='blue')))
        fig.update_layout(yaxis_title='power in W')
        self.standardLayout(fig)
        return fig

    def compute_continuousMode_hours(df,modus=10):
        '''10:soec,20:sofc'''
        # df_modes= pd.DataFrame.from_dict(self._enumModeHUB,orient='index',columns=['mode'])
        # df_modes[df_modes['mode']==modus]
        ## fill the data every 1 minute
        dfmode=df.resample('60s',closed='right').ffill()
        ## keep only data for the corresponding mode
        dfmode=dfmode[dfmode['value']==modus]
        ## compute delta times
        deltas=dfmode.reset_index()['timestampUTC'].diff().fillna(pd.Timedelta('0 minutes'))
        ## sum the delta only if they are smaller than 1minute and 1 second
        return deltas[deltas<pd.Timedelta('1 minute,1 second')].sum()

    def compute_H2_produced(df,modus=10):
        tag_mode=['SEH1.Etat.HP41']
        tagDebitH2 = self.getTagsTU('L025.*FT.*HM05')
        tagsCurrent = self.getTagsTU('alim.*IT_HM05')

        df_etathp41=self.loadtags_period(t0,t1,tag_mode)
        dfmode = df_etathp41.resample('10s',closed='right').ffill()
        dfmode = dfmode[dfmode['value']==10]
        df_debitH2 = self.loadtags_period(t0,t1,tagDebitH2)[['value']]
        I_stacks = self.loadtags_period(t0,t1,tagsCurrent)
        Itotal = I_stacks.sum(axis=1).drop_duplicates()
        Itotal = Itotal.resample('10s').ffill().loc[dfmode.index]
        PH2mol_s = Itotal*25/(2*self.cst['FAR']) ##25 cells
        PH2Nlmin = PH2mol_s*22.4*60
        df_debit = df_debitH2.resample('10s').ffill().loc[dfmode.index] ##Nl/min
        H2_produit =(df_debit/60).sum()*10/1000 #Nm3
        H2_produit_I =(PH2Nlmin/60).sum()*10/1000 #Nm3

    def get_I_V_cara():
        tag_mode=['SEH1.Etat.HP41']
        tagsCurrent=self.getTagsTU('alim.*IT_HM05')
        tagsVoltage=self.getTagsTU('alim.*ET_HM05')
        df_etathp41=readbourinparkedtags(folderpkl,tag_mode,t0,t1)
        df_stack_sn=readbourinparkedtags(folderpkl,tagsStack_sn,t0,t1)
        h_soec,h_sofc=[compute_continuousMode_hours(df_etathp41,m) for m in [10,20]]
        df_cara = df_cara.reset_index().drop_duplicates().set_index('timestampUTC')
        df_cara = processdf(self,df_cara,rs = '60s')
        df_cara.to_pickle('df_cara.pkl')

    def plot_I_V_cara():
        ### filter time electrolysis
        tagsCurrent=self.getTagsTU('alim.*IT_HM05')
        tagsVoltage=self.getTagsTU('alim.*ET_HM05')
        df_cara=pickle.load(open('df_cara.pkl','rb'))
        df2 = df_cara.resample('300s').mean()
        fig=go.Figure()
        for i,v in zip(tagsCurrent,tagsVoltage):
            x=df2[i]
            y=df2[v]
            x=-x[x.abs()>0.1]
            x=x[x<24]
            x=x[x>-60]
            y=y[x.index]
            fig.add_trace(go.Scatter(x=x,y=y,name=i))

        fig.update_traces(mode='markers')
        fig.update_xaxes(title_text='Current (A)')
        fig.update_yaxes(range=[-5,50],title_text='Voltage (V DC)')
        fig.show()

    # ==============================================================================
    #                   graphic functions
    # ==============================================================================
    def toogle_tag_description(self,tagsOrDescriptions,toogleto='tag',return_previous_mode=False):
        '''
        -tagsOrDescriptions:list of tags or description of tags
        -toogleto: you can force to toogleto description or tags ('tag','description')
        '''
        current_names = tagsOrDescriptions
        ### automatic detection if it is a tag --> so toogle to description
        areTags = True if current_names[0] in self.dfplc.index else False
        newNames=dict(zip(current_names,current_names))
        if toogleto=='description'and areTags:
            for k in current_names:
                if re.match('.*_minmax',k) is None:
                    newNames[k]  = self.dfplc.loc[k,'DESCRIPTION']
                else:
                    newNames[k]  = self.dfplc.loc[k.strip('_minmax'),'DESCRIPTION'] +' (enveloppe)'
        elif toogleto=='tag'and not areTags:
            for k in current_names:
                if re.match('.* \(enveloppe\)',k) is None:
                    newNames[k]  = self.dfplc.index[self.dfplc.DESCRIPTION==k][0]
                else:
                    newNames[k]  = self.dfplc.index[self.dfplc.DESCRIPTION==k.replace(' (enveloppe)','')][0]+'_minmax'
        if return_previous_mode:
            if areTags:
                previous_mode='tag'
            else:
                previous_mode='description'
            return newNames,previous_mode
        else:
            return newNames

    def update_lineshape_fig(self,fig,style='default'):
        if style=='default':
            fig.update_traces(line_shape="linear",mode='lines+markers')
            for trace in fig.data:
                name        = trace.name
                dictname    = self.toogle_tag_description([name],'tag')
                tagname     = dictname[name]
                print_file(tagname)
                if 'ECV' in tagname or '.HR36' in tagname or self.getUnitofTag(tagname) in ['TOR','ETAT','CMD','Courbe']:
                # if 'ECV' in tagname or '.HR36' in tagname or self.getUnitofTag(tagname) in ['ETAT','CMD','Courbe']:
                    trace.update(line_shape="hv",mode='lines+markers')

        elif style in ['markers','lines','lines+markers']:
            fig.update_traces(line_shape="linear",mode=style)
        elif style =='stairs':
            fig.update_traces(line_shape="hv",mode='lines')
        return fig

    def updatecolortraces(self,fig):
        for tag in fig.data:
            tagcolor = self._dftagColorCode.loc[tag.name,'colorHEX']
            # print(tag.name,colName,tagcolor)
            tag.marker.color = tagcolor
            tag.line.color = tagcolor
            tag.marker.symbol = self._dftagColorCode.loc[tag.name,'symbol']
            tag.line.dash = self._dftagColorCode.loc[tag.name,'line']

    def updatecolorAxes(self,fig):
        for ax in fig.select_yaxes():
            titleAxis = ax.title.text
            if not titleAxis==None:
                unit    = titleAxis.strip()
                axColor = self._unitDefaultColors.loc[unit].squeeze()[:-1]
                # print(axColor)
                # sys.exit()
                ax.title.font.color = axColor
                ax.tickfont.color   = axColor
                ax.gridcolor        = axColor

    def multiUnitGraphShades(self,df):
        tagMapping = {t:self.getUnitofTag(t) for t in df.columns}
        fig = self.utils.multiUnitGraph(df,tagMapping)
        dfGroups = self.utils.getLayoutMultiUnit(tagMapping)[1]
        listCols = dfGroups.color.unique()
        for k1,g in enumerate(listCols):
            colname = self._colorshades[k1]
            shades = self._colorPalettes[colname]['hex']
            names2change = dfGroups[dfGroups.color==g].index
            fig.update_yaxes(selector={'gridcolor':g},
                        title_font_color=colname[:-1],gridcolor=colname[:-1],tickfont_color=colname[:-1])
            shade=0
            for d in fig.data:
                if d.name in names2change:
                    d['marker']['color'] = shades[shade]
                    d['line']['color']   = shades[shade]
                    shade+=1
            fig.update_yaxes(showgrid=False)
            fig.update_xaxes(showgrid=False)

        # fig.add_layout_image(dict(source=self._imgpeintre,xref="paper",yref="paper",x=0.05,y=1,
        #                             sizex=0.9,sizey=1,sizing="stretch",opacity=0.5,layer="below"))
        # fig.update_layout(template="plotly_white")
        fig.add_layout_image(
            dict(
                source=self._sylfenlogo,
                xref="paper", yref="paper",
                x=0., y=1.02,
                sizex=0.12, sizey=0.12,
                xanchor="left", yanchor="bottom"
            )
        )
        return fig

    def multiUnitGraphSP(self,df,tagMapping=None,**kwargs):
        if not tagMapping:tagMapping = {t:self.getUnitofTag(t) for t in df.columns}
        # print(tagMapping)
        fig = self.utils.multiUnitGraph(df,tagMapping,**kwargs)
        self.standardLayout(fig)
        self.updatecolorAxes(fig)
        self.updatecolortraces(fig)
        if df.index.max()-df.index.min()>pd.Timedelta(days=2):
            fig.update_traces(hovertemplate='  %{y:.2f}' + '<br>  %{x|%b %d %Y %H:%M}')
        return fig

    def doubleMultiUnitGraph(self,df,tags1,tags2,*args,**kwargs):
        fig = VisualisationMaster_daily.multiMultiUnitGraph(self,df,tags1,tags2,*args,**kwargs)
        self.updatecolorAxes(fig)
        self.updatecolortraces(fig)
        self.standardLayout(fig,h=None)
        return fig

    def minmaxFigure(self,t0,t1,tags,rs='600s',subplot=True):
        hex2rgb = lambda h,a:'rgba('+','.join([str(int(h[i:i+2], 16)) for i in (0, 2, 4)])+','+str(a)+')'
        df = self.loadtags_period(t0,t1,tags,rsMethod='forwardfill',rs='100ms',checkTime=True)
        dfmean=df.resample(rs,closed='right').mean()
        dfmin=df.resample(rs,closed='right').min()
        dfmax=df.resample(rs,closed='right').max()

        if subplot:rows=len(df.columns)
        else:rows=1
        fig = make_subplots(rows=rows, cols=1,shared_xaxes=True,vertical_spacing = 0.02)

        for k,tag in enumerate(df.columns):
            hexcol=self._dftagColorCode.loc[tag,'colorHEX']
            col = hex2rgb(hexcol.strip('#'),0.3)
            x = list(dfmin.index) + list(np.flip(dfmax.index))
            y = list(dfmin[tag])+list(np.flip(dfmax[tag]))
            if subplot:row=k+1
            else:row=1
            # fig.add_trace(go.Scatter(x=x,y=y,fill='toself',fillcolor=col,mode='markers+lines',marker={'color':'black'},name=tag+'_minmax'),row=row,col=1)
            fig.add_trace(go.Scatter(x=x,y=y,fill='toself',fillcolor=col,mode='none',marker={'color':'black'},name=tag+'_minmax'),row=row,col=1)
            fig.add_trace(go.Scatter(x=dfmean.index,y=dfmean[tag],mode='markers+lines',marker={'color':hexcol},name=tag),row=row,col=1)
        return fig

    def addTagEnveloppe(self,fig,tag_env):
        hex2rgb = lambda h,a:'rgba('+','.join([str(int(h[i:i+2], 16)) for i in (0, 2, 4)])+','+str(a)+')'
        #### retrieve t0,t1 and rs of the data
        xx=pd.DatetimeIndex(fig.data[0]['x'])
        t0,t1=xx.min(),xx.max()
        rs=xx.inferred_freq
        #### compute emveloppe
        df    = self.loadtags_period(t0,t1,[tag_env],rsMethod='nearest',rs='100ms')
        dfmin = df.resample(rs,label='right',closed='right').min()
        dfmax = df.resample(rs,label='right',closed='right').max()
        x = list(dfmin.index) + list(np.flip(dfmax.index))
        y = list(dfmin[tag_env])  + list(np.flip(dfmax[tag_env]))
        ### retrieve yaxis
        correctidx=[k for k in self.toogle_tag_description([k.name for k in fig.data],'tag').values()].index(tag_env)
        #### retrieve color and add transparency and add trace
        hexcol= self._dftagColorCode.loc[tag_env,'colorHEX']
        col = hex2rgb(hexcol.strip('#'),0.3)
        fig.add_trace(go.Scatter(x=x,y=y,fill='toself',fillcolor=col,mode='none',name=tag_env + '_minmax',yaxis=fig.data[correctidx]['yaxis']
            # line_shape='hv'
            ))
        return fig

class SmallPower_retro_indicators(SmallPowerComputer):
    def __init__(self,*args,**kwargs):
        SmallPowerComputer.__init__(self,*args,**kwargs)
        self.indicator_tags=conf.PLC_INDICATOR_TAGS['variable_name'].reset_index().set_index('variable_name').squeeze()
        self.tags=pd.concat([conf.TAGS_FOR_INDICATORS.drop_duplicates(),self.indicator_tags])
        self.variables=self.tags.reset_index().set_index(0).squeeze()

        tags_to_add = {
            'fuite_fuel_unfiltered':self.tags['fuite_fuel'],
            'fuite_air_unfiltered':self.tags['fuite_air'],
            'rendement_sys_unfiltered':self.tags['rendement_sys'],
            'power_gv_a':self.tags['power_gv_a_1'],
            'rendement_gv_a_unfiltered':self.tags['rendement_gv_a'],
            'rendement_gv_b_unfiltered':self.tags['rendement_gv_b'],
            'fuel_in_ft_stack':self.tags['fuel_in_ft'],
            'pertes_stack_unfiltered':self.tags['pertes_stack'],
            # 'power_stb_unfiltered':self.tags['power_stb'],
        }
        for f,c in tags_to_add.items():self.add_indicator_manually(f,copy_from=c)

    # ====================== #
    #   useful functions     #
    # ====================== #
    def apply_lowpass_filter(self,df,alpha=0.005,method='ewm'):
        if method=='ewm':
            return df.ewm(alpha=alpha).mean()
        else:
            tmp = {df.index[0]:df[0]}
            for k in range(1,len(df)):
                tm1 = df.index[k-1]
                tmp[df.index[k]] = self.indicators.low_pass_filter(df[k],tmp[tm1],alpha)
            return pd.Series(tmp)

    def park_daily_indicator(self,s):
        listdays=[k.strftime(self.format_dayFolder) for k in pd.date_range(s.index.min(),s.index.max())]
        #### in case they are several days(for example at midnight)
        for d in listdays:
            t0 = pd.Timestamp(d + ' 00:00:00',tz=self.tz_record)
            t1 = t0 + pd.Timedelta(days=1)
            s_day=s[(s.index>=t0)&(s.index<t1)]
            folderday=self.folderPkl + d +'/'
            #### create folder if necessary
            if not os.path.exists(folderday):os.mkdir(folderday)
            namefile = folderday + self.indicator_tags[s.name] + '.pkl'
            s_day.to_pickle(namefile)
        print('indicator ',s.name,'==',self.indicator_tags[s.name],'parked')

    def get_tags_for_indicator(self,variables,t0,t1):
        tags_needed=self.tags[variables].to_list()
        df=self.loadtags_period(t0,t1,tags_needed,rs='1s',rsMethod='nearest')
        df.columns=self.variables[df.columns]
        return df[variables]

    def check_indicator(self,df,names='variable',rs='300s',use_px=False):
        '''names={'variable','tag','description'}'''
        df.columns = [k if k in list(self.tags) else self.tags[k] for k in df.columns]
        df=df.resample(rs).nearest()
        if use_px:
            fig=self.utils.multiUnitGraph(df)
        else :
            fig=self.multiUnitGraphSP(df)

        if names=='variable':
            for t in fig.data:t.name = self.variables[t.name]
        elif names=='description':
            new_names = self.toogle_tag_description(tags,'description')
            for t in fig.data:t.name = new_names[t.name]
        fig.update_traces(hovertemplate='  %{y}' + '<br>  %{x}')
        fig.show()
        return fig

    def add_indicator_manually(self,new_tag,copy_from='SEH1.ETAT.HC08',color=None,dash='solid'):
        self._dftagColorCode.loc[new_tag]=self._dftagColorCode.loc[copy_from]
        if not color is None:
            self._dftagColorCode.loc[new_tag,'colorHEX']=color
            self._dftagColorCode.loc[new_tag,'symbol']='circle'
            self._dftagColorCode.loc[new_tag,'dash']=dash
        self.dfplc.loc[new_tag]=self.dfplc.loc[copy_from]
        self.tags.loc[new_tag]=new_tag
        self.variables[new_tag]=new_tag

    # ====================== #
    #  computation functions #
    # ====================== #
    def compute_currents(self,t0,t1):
        current_tags = self.tags[self.tags.index.str.contains('current_stack')]
        df_currents  = self.loadtags_period(t0,t1,current_tags.to_list(),rs='1s',rsMethod='nearest')
        # ================================================
        # courant en valeur absolue et convention physique
        # ================================================
        for tag in current_tags.to_list():
            df_currents[tag + '.HC09'] = df_currents[tag].abs()
            self.park_daily_indicator(df_currents[tag + '.HC09'])
            df_currents[tag + '.HC13'] = -df_currents[tag]
            self.park_daily_indicator(df_currents[tag + '.HC13'])

        # ======================
        #  courants total stack
        # ======================
        df_currents['I_absolue'] = (df_currents[[t for t in df_currents.columns if 'HM05.HC09' in t]]).sum(axis=1)
        self.park_daily_indicator(df_currents['I_absolue'])
        df_currents['I_conventionnel'] = (df_currents[[t for t in df_currents.columns if 'HM05.HC13' in t]]).sum(axis=1)
        self.park_daily_indicator(df_currents['I_conventionnel'])
        return df_currents
    def compute_modehub(self,t0,t1,vector=False):
        '''
        Params
        --------
        - vector [bool]: if False(default) use the function from self.indicators.detect_modehub. If true use the vectorized calculus(way faster.)
        '''
        variables=['I_conventionnel','vanneBF']
        df=self.get_tags_for_indicator(variables,t0,t1)
        if not vector:
            df['modehub'] = df[variables].apply(lambda x:self.indicators.detect_modehub(*x),axis=1)
        else:
            threshold=0.5 #Amperes
            df['modehub']='BO'
            df['modehub']=df['modehub'].mask(df['I_conventionnel'] < -threshold,'SOEC')# set to SOEC condition respected
            df['modehub']=df['modehub'].mask(df['I_conventionnel'] > threshold,'SOFC')# set to SOFC condition respected
            df['modehub']=df['modehub'].mask((df['vanneBF']==False)&(df['modehub']=='BO'),'BF')

        self.park_daily_indicator(df['modehub'])
        return df

    #############  compteurs, cumul  ##########
    def compute_tps_T600(self,t0,t1):
        df=self.get_tags_for_indicator(['T_stacks'])
        df['tps_T600'] = (df > 600).cumsum()/3600
        self.park_daily_indicator(df['tps_T600'])
        return df
    def compute_tps_SOEFC(self,t0,t1):
        df=self.get_tags_for_indicator(['modehub'])
        df['tps_SOEC'] = (df['modehub']=='SOEC').cumsum()/3600
        self.park_daily_indicator(df['tps_SOEC'])
        df['tps_SOFC'] = (df['modehub']=='SOFC').cumsum()/3600
        self.park_daily_indicator(df['tps_SOFC'])
        return df
    def compute__transitions(self,t0,t1,transition_mode='sofc2soec',explore=False):
        df=self.get_tags_for_indicator(['modehub'])

        df['mode_soefc']=df['modehub'].where(df['modehub'].str.contains('SO'),np.nan).ffill().bfill()
        self.add_indicator_manually('mode_soefc',copy_from='SEH1.ETAT.HC08')

        modes={'SOEC':2,'SOFC':1}
        tmp=df['mode_soefc'].apply(lambda x:modes[x]).diff()

        ## mode electrolyse vers mode pile
        if transition_mode=='sofc2soec':
            tmp=df['mode_soefc'].apply(lambda x:modes[x]).diff()
            tmp=tmp.where(tmp==1,0)### put to 0 everything that is not 1
            # df['nbTransitions_sofc2soec']=tmp.cumsum()

        ## mode pile vers mode electrolyse
        elif transition_mode=='soec2sofc':
            tmp=df['mode_soefc'].apply(lambda x:modes[x]).diff()
            tmp=tmp.where(tmp==-1,0).abs()### put to 0 everything that is not -1
            # df['nbTransitions_soec2sofc']=tmp.cumsum()

        ## les 2 transitions
        elif transition_mode=='both':
            tmp=df['mode_soefc'].apply(lambda x:modes[x]).diff()
            tmp=tmp.where(tmp.abs()==1,0).abs()### put to 0 everything that is not -1 or 1
            # df['nbTransitions_both']=tmp.cumsum()

        ## all mode trigger
        elif transition_mode=='all':
            modes={'SOEC':2,'SOFC':1,'BO':0,'BF':0}
            tmp=df['modehub'].apply(lambda x:modes[x]).diff()
            tmp=tmp.where(tmp==0,1)### put to 1 everything that is not 0
            # df['nbTransitions_all']=tmp.cumsum()

        df['nbTransitions']=tmp.cumsum()
        self.park_daily_indicator(df['nbTransitions'])
        if explore:
            fig=self.utils.multiUnitGraph(df.resample('300s').nearest(),dict(zip(df.columns,['mode','mode','#_transition','#_transition','#_transition','#_transition'])));
            fig.update_traces(hovertemplate='  %{y}' + '<br>  %{x}')

        return df

    #############  fuites  ##########
    def compute_fuites_air(self,t0,t1,*args,vector=False,**kwargs):
        variables=['I_conventionnel','air_out_ft','air_in_ft','modehub','n2_in_air','air_out_pt']
        df=self.get_tags_for_indicator(variables,t0,t1)

        df['o2_out_alim'] = self.indicators.o2_stack_alim(df['I_conventionnel'])
        df['o2_out_hm05'] = df['air_out_ft'] - df['air_in_ft']
        if vector:
            fuite_air = df['air_in_ft'] - df['o2_out_alim'] - df['air_out_ft']
            fuite_air.loc[df['modehub']=='BF']=df['n2_in_air'].loc[df['modehub']=='BF']
        else:
            fuite_air = df[['modehub','o2_out_alim','air_in_ft','air_out_ft','n2_in_air']].apply(lambda x:self.indicators.fuites_air(*x),axis=1)
        df['fuite_air_unfiltered'] = fuite_air
        df['fuite_air'] = self.apply_lowpass_filter(fuite_air,*args,**kwargs)

        self.park_daily_indicator(df['fuite_air'])

        df['fuite_air_gfd']=np.nan
        df['fuite_air_gfd'].loc[df['air_out_pt'].abs()>0] = fuite_air/df['air_out_pt']
        df['fuite_air_gfd']  = self.apply_lowpass_filter(df['fuite_air_gfd'],*args,**kwargs)
        self.park_daily_indicator(df['fuite_air_gfd'])
        return df

    def compute_fuites_fuel(self,t0,t1,*args,vector=False,**kwargs):
        variables=['I_conventionnel','fuel_in_ft','fuel_out_ft','modehub','n2_in_fuel','fuel_out_pt']
        df=self.get_tags_for_indicator(variables,t0,t1)

        df['h2_out_alim'] = self.indicators.h2_stack_out(df['I_conventionnel'])
        df['h2_out_hm05'] = df['fuel_out_ft'] - df['fuel_in_ft']
        if vector:
            df['h2stack'] = df['h2_out_alim'].abs()
            #### else
            fuite_fuel = df['fuel_in_ft'] - df['fuel_out_ft']
            #### SOEC
            df_soec=df[['fuel_in_ft','h2stack','fuel_out_ft']].loc[df['modehub']=='SOEC']
            fuite_fuel.loc[df['modehub']=='SOEC']=df_soec['fuel_in_ft'] + df_soec['h2stack'] - df_soec['fuel_out_ft']
            #### SOFC
            df_sofc=df[['fuel_in_ft','h2stack']].loc[df['modehub']=='SOFC']
            fuite_fuel.loc[df['modehub']=='SOFC']=df_sofc['fuel_in_ft'] - df_sofc['h2stack']
            #### BF
            df_bf=df[['n2_in_fuel','fuel_in_ft']].loc[df['modehub']=='BF']
            fuite_fuel.loc[df['modehub']=='BF']=df_bf['n2_in_fuel'] + df_bf['fuel_in_ft']
        else:
            fuite_fuel  = df[['modehub','h2_out_alim','fuel_in_ft','fuel_out_ft','n2_in_fuel']].apply(lambda x:self.indicators.fuites_fuel(*x),axis=1)
        df['fuite_fuel_unfiltered']=fuite_fuel
        df['fuite_fuel'] = self.apply_lowpass_filter(fuite_fuel,*args,**kwargs)
        self.park_daily_indicator(df['fuite_fuel'])

        df['fuite_fuel_gfd'] = np.nan
        df['fuite_fuel_gfd'].loc[df['fuel_out_pt'].abs()>0] = fuite_fuel/df['fuel_out_pt']
        df['fuite_fuel_gfd'] = self.apply_lowpass_filter(df['fuite_fuel_gfd'],*args,**kwargs)

        self.park_daily_indicator(df['fuite_fuel_gfd'])
        return df
    def compute_h2_prod_cons(self,t0,t1):
        variables=['h2_out_hm05','fuel_in_ft','modehub','I_conventionnel']
        df=self.get_tags_for_indicator(variables,t0,t1)
        df['cumul_h2_produced']=df['h2_out_hm05'].where(df['modehub']=='SOFC',0).cumsum()/60/1000
        df['cumul_h2_consumed']=df['fuel_in_ft'].where(df['modehub']=='SOEC',0).cumsum()/60/1000
        self.park_daily_indicator(df['cumul_h2_produced'])
        self.park_daily_indicator(df['cumul_h2_consumed'])
        return df
    #############  rendements  ##########
    def compute_rendement_sys(self,t0,t1,*args,vector=False,**kwargs):
        variables=['modehub','power_total','h2_out_alim']
        df=self.get_tags_for_indicator(variables,t0,t1)
        if vector:
            #conversion in mol/s
            df['h2_mols']  = df['h2_out_alim'].abs()/60/self.cst['vlm']
            #take the power
            df['h2_power_chimique'] = df['h2_mols']*self.cst['PCImol_H2']
            #remove extra power not from the system
            df['power_total']-=1000

            rendement_sys=pd.Series(0,index=df.index)
            #### SOEC
            filter_soec = (df['modehub']=='SOEC')&(df['power_total']>0)
            df_soec = df[['h2_power_chimique','power_total']].loc[filter_soec]
            rendement_sys.loc[filter_soec]=df_soec['h2_power_chimique']/df_soec['power_total']

            #### SOFC
            filter_sofc = (df['modehub']=='SOFC')&(df['h2_power_chimique']>0)
            df_sofc = df[['h2_power_chimique','power_total']].loc[filter_sofc]
            rendement_sys.loc[filter_sofc]=-df_sofc['power_total']/df_sofc['h2_power_chimique']

            rendement_sys*=100
        else:
            rendement_sys = df.apply(lambda x:self.indicators.rendement_sys(*x),axis=1)
        df['rendement_sys_unfiltered']=rendement_sys
        df['rendement_sys'] = self.apply_lowpass_filter(rendement_sys,*args,**kwargs)
        self.park_daily_indicator(df['rendement_sys'])
        return df
    def compute_rendements_gvs(self,t0,t1,*args,vector=False,**kwargs):
        variables=['tt_in_gv','tt_out_gv','power_gv_a_1','power_gv_a_2','power_gv_a_3','power_gv_b_1','ft_in_gv_a','ft_in_gv_b']
        df=self.get_tags_for_indicator(variables,t0,t1)

        df['power_gv_a'] = df[[k for k in variables if 'power_gv_a' in k]].sum(axis=1)
        if vector:
            def rendement_gv_vector(df_gv,):
                '''df_gv should have ft_in_gv,tt_in_gv,tt_out_gv columns'''
                debitEau_gs = df_gv['ft_in_gv']/60
                #calcul
                power_chauffe_eau_liq = debitEau_gs*self.cst['Cp_eau_liq']*(100-df_gv['tt_in_gv'])
                power_chauffe_eau_liq = power_chauffe_eau_liq.mask(power_chauffe_eau_liq<0,0)
                power_vapo_eau        = debitEau_gs*self.cst['Cl_H2O']
                power_chauffe_vap     = debitEau_gs*self.cst['Cp_eau_vap']*(df_gv['tt_out_gv']-100)
                power_chauffe_vap     = power_chauffe_vap.mask(power_chauffe_vap<0,0)
                df_gv['power_total_chauffe'] = power_chauffe_eau_liq + power_vapo_eau +  power_chauffe_vap

                rendement_gv = pd.Series(0,index=df_gv.index)

                df_gv_r=df_gv[['power_total_chauffe','power_elec_chauffe']].loc[df_gv['power_elec_chauffe']>0]
                return df_gv_r['power_total_chauffe']/df_gv_r['power_elec_chauffe']*100

            df_gva = df[['ft_in_gv_a','tt_in_gv','tt_out_gv','power_gv_a']]
            df_gva.columns=['ft_in_gv','tt_in_gv','tt_out_gv','power_elec_chauffe']
            rendement_gv_a = rendement_gv_vector(df_gva)

            df_gvb = df[['ft_in_gv_b','tt_in_gv','tt_out_gv','power_gv_b_1']]
            df_gvb.columns=['ft_in_gv','tt_in_gv','tt_out_gv','power_elec_chauffe']
            rendement_gv_b = rendement_gv_vector(df_gvb)
            # rendement_gv_b = df[['ft_in_gv_b','tt_in_gv','tt_out_gv','power_gv_b_1']].apply(lambda x:self.indicators.rendement_gv(*x),axis=1)
        else:
            rendement_gv_a = df[['ft_in_gv_a','tt_in_gv','tt_out_gv','power_gv_a']].apply(lambda x:self.indicators.rendement_gv(*x),axis=1)
            rendement_gv_b = df[['ft_in_gv_b','tt_in_gv','tt_out_gv','power_gv_b_1']].apply(lambda x:self.indicators.rendement_gv(*x),axis=1)

        df['rendement_gv_a_unfiltered']=rendement_gv_a
        df['rendement_gv_b_unfiltered']=rendement_gv_b
        df['rendement_gv_a'] = self.apply_lowpass_filter(rendement_gv_a)
        df['rendement_gv_b'] = self.apply_lowpass_filter(rendement_gv_b)
        self.park_daily_indicator(df['rendement_gv_a'])
        self.park_daily_indicator(df['rendement_gv_b'])
        return df

    # ==== pertes thermiques stack ========
    def compute_pertes_stack(self,t0,t1,*args,vector=False,**kwargs):
        variables=['air_in_tt','air_in_ft','air_stack_tt','fuel_in_tt','fuel_in_ft','fuel_stack_tt','power_enceinte_thermique','h2_cold_loop_ft']
        df=self.get_tags_for_indicator(variables,t0,t1)

        df['fuel_in_ft_stack'] = df['fuel_in_ft'] + df['h2_cold_loop_ft']
        if vector:
            df['surchauffe_Air']  = (df['air_stack_tt']-df['air_in_tt'])*self.cst['Cp_air']*self.cst['Mmol_Air']*df['air_in_ft']/self.cst['vlm']/60
            df['surchauffe_Fuel'] = (df['fuel_stack_tt']-df['fuel_in_tt'])*self.cst['Cp_H2']*self.cst['Mmol_H2']*df['fuel_in_ft']/self.cst['vlm']/60
            # df['surchauffe_AirBalayage'] = (air_stack_tt-air_in_tt)*cp_air*M_air*debitAirBalayage_mols/22.4/60
            df['surchauffe_AirBalayage'] = 0

            df['total_puissance_surchauffe_gaz'] = df['surchauffe_Air'] + df['surchauffe_Fuel']+df['surchauffe_AirBalayage']

            # pertes_stack=pd.Series(np.nan,index=df.index)
            # df_pertes=df[['power_enceinte_thermique','total_puissance_surchauffe_gaz']][df['total_puissance_surchauffe_gaz']>0]
            # pertes_stack.loc[df['total_puissance_surchauffe_gaz']>0]=df_pertes['power_enceinte_thermique']-df_pertes['total_puissance_surchauffe_gaz']
            pertes_stack=df['power_enceinte_thermique']-df['total_puissance_surchauffe_gaz']
        else:
            pertes_stack = df[['air_in_tt','air_in_ft','air_stack_tt','fuel_in_tt','fuel_in_ft_stack','fuel_stack_tt',
                'power_enceinte_thermique']].apply(lambda x:self.indicators.pertes_thermiques_stack(*x),axis=1)
        df['pertes_stack_unfiltered'] = pertes_stack
        df['pertes_stack'] = self.apply_lowpass_filter(pertes_stack,*args,**kwargs)
        self.park_daily_indicator(df['pertes_stack'])
        return df

    # ==== autres ========
    def compute_power_stb(self,t0,t1,*args,**kwargs):
        df['power_stb'] = self.apply_lowpass_filter(df['power_enceinte_thermique'])
        self.park_daily_indicator(df['rendement_gv_b'])
        return df

    def bilan_echangeur(self,t0,t1,tagDebit='L400',echangeur='CND_03',**kwargs):
        cdn1_tt = self.getTagsTU(echangeur + '.*TT')
        debitEau = self.getTagsTU(tagDebit + '.*FT')
        listTags = cdn1_tt + debit
        if isinstance(timeRange,list) :
            df   = self.loadtags_period(listTags,timeRange,**kwargs)
        if df.empty:
            return df
        debitEau_gs = df[debitEau]*1000/3600
        deltaT = df[cdn3_tt[3]]-df[cdn3_tt[1]]
        puissance_echangee = debitEau_gs*self.cst['Cp_eau_liq']*deltaT
        varUnitsCalculated = {
            'debit eau(g/s)':{'unit':'g/s','var':debitEau_gs},
            'delta température ' + echangeur:{'unit':'°C','var':deltaT},
            'puissance echangée ' + echangeur:{'unit':'W','var':puissance_echangee},
        }
        return df, varUnitsCalculated

    def bilan_valo(self,t0,t1,*args,**kwargs):
        '''
        - timeRange : int if realTime==True --> ex : 60*30*2
        [str,str] if not realtime --> ex : ['2021-08-12 9:00','2020-08-13 18:00']
        '''
        debit_eau = self.getTagsTU('L400.*FT')#kg/h
        cdn1_tt = self.getTagsTU('CND_01.*TT')
        cdn3_tt = self.getTagsTU('CND_03.*TT')
        hex1_tt = self.getTagsTU('HPB_HEX_01')
        hex2_tt = self.getTagsTU('HPB_HEX_02')
        vannes  = self.getTagsTU('40[2468].*TV')
        vanne_hex1, vanne_hex2, vanne_cdn3, vanne_cdn1 = vannes

        t_entree_valo='_TT_02.HM05'
        t_sortie_valo='_TT_04.HM05'
        listTags = debit_eau + cdn1_tt + cdn3_tt + hex1_tt + hex2_tt + vannes

        if isinstance(timeRange,list) :
            df   = self.loadtags_period(listTags,timeRange,*args,**kwargs)
        if df.empty:
            return df

        debitEau_gs = df[debit_eau].squeeze()*1000/3600
        nbVannes = df[vannes].sum(axis=1)##vannes NF 0=fermée
        debitUnitaire = debitEau_gs/nbVannes

        deltaT = df[cdn3_tt[3]]-df[cdn3_tt[1]]
        echange_cnd3 = debitUnitaire*self.cst['Cp_eau_liq']*deltaT

        varUnitsCalculated = {
            'debit eau(g/s)':{'unit':'g/s','var':debitEau_gs},
            'nombres vannes ouvertes':{'unit':'#','var':nbVannes},
            'debit eau unitaire':{'unit':'g/s','var':debitUnitaire},
            'delta température':{'unit':'°C','var':deltaT},
            'puissance echange condenseur 3':{'unit':'W','var':echange_cnd3},
        }
        return df, varUnitsCalculated

    def rendement_blower(self,t0,t1,*args,activePower=True,**kwargs):
        debitAir = self.getTagsTU('138.*FT')
        pressionAmont_a,pressionAmont_b = self.getTagsTU('131.*PT')
        pressionAval = self.getTagsTU('138.*PT')[0]
        puissanceBlowers = self.getTagsTU('blr.*02.*JT')
        t_aval = self.getTagsTU('l126')
        listTags = debitAir+[pressionAmont_a,pressionAmont_b]+[pressionAval]+t_aval+puissanceBlowers

        df   = self.loadtags_period(listTags,timeRange,*args,**kwargs)
        if not df.empty:
            df = df[listTags]
            debitAirNm3 = df[debitAir]/1000/60
            deltaP2a_Pa = (df[pressionAval]-df[pressionAmont_a])*100
            deltaP2b_Pa = (df[pressionAval]-df[pressionAmont_b])*100
            deltaP_moyen = (deltaP2a_Pa + deltaP2b_Pa)/2
            p_hydraulique = debitAirNm3.squeeze()*deltaP_moyen
            p_elec = df[puissanceBlowers].sum(axis=1)
            rendement_blower = p_hydraulique/p_elec
        return df

    def rendement_pumpRecircuFroid(self,t0,t1,*args,activePower=True,**kwargs):
        ### compliqué débit amont
        debitAmont   = self.getTagsTU('303.*FT')+''#???
        debitAval = self.getTagsTU('L032.*FT')
        t_aval = self.getTagsTU('L032.*TT')
        pressionAval = ''#???
        puissancePump = self.getTagsTU('gwpbh.*pmp_01.*JTW')
        listTags = debitAmont + debitAval +t_aval + pressionAval + puissancePump
        df   = self.loadtags_period(listTags,timeRange,*args,**kwargs)
        if df.empty:
            return df
        df = df[listTags]
        dfPump = pd.DataFrame()
        dfPump['debit eau total(Nm3/s)'] = (df['debit eau1(g/min)']+df['debit eau2(g/min)'])/1000000/60
        Pout = df['pressionAval(mbarg)']*100
        dfPump['puissance hydraulique(W)'] = dfPump['debit eau total(Nm3/s)']*dfPump['pression sortie(Pa)']
        dfPump['rendement pompe'] = dfPump['puissance hydraulique(W)']/df['puissance pump(W)']*100
        dfPump['cosphiPmp'] = df['puissance pump(W)']/(df['puissance pump(W)']+df['puissance pump reactive (VAR)'])
        df = pd.concat([df,dfPump],axis=1)
        return df

    def cosphi(self,t0,t1,*args,**kwargs):
        extVA = 'JTVA_HC20'
        extVAR ='JTVAR_HC20'
        extW ='JTW'
        tagsVA = self.getTagsTU(extVA)
        tagsVAR = self.getTagsTU(extVAR)
        tagsJTW = self.getTagsTU(extW)
        racineVA = [tag.split(extVA)[0] for tag in tagsVA]
        racineVAR = [tag.split(extVAR)[0] for tag in tagsVAR]
        racineW = [tag.split(extW)[0] for tag in tagsJTW]
        tags4Cosphi = list(set(racineVA)&set(racineW))

        jtvas,jtws=[],[]
        for t in tags4Cosphi:
            jtvas.append([tag for tag in tagsVA if t in tag][0])
            jtws.append([tag for tag in tagsJTW if t in tag][0])

        listTags = jtvas + jtws
        if isinstance(timeRange,list):
            df = self.loadtags_period(listTags,timeRange,*args,**kwargs)
        if df.empty:
            return df
        cosphi = {t:{'unit':'cosphi','var':df[jtva].squeeze()/df[jtw].squeeze()} for jtva,jtw,t in zip(jtvas,jtws,tags4Cosphi)}
        # cosphi = {jtva+'/'+jtw:{'unit':'cosphi','var':df[jtva].squeeze()/df[jtw].squeeze()} for jtva,jtw in zip(jtvas,jtws)}
        return df,cosphi

class SmallPower_VM(VersionsManager_daily):
    def __init__(self,**kwargs):
        VersionsManager_daily.__init__(self,conf.FOLDERPKL,conf.DIR_PLC,pattern_plcFiles='*ALPHA*.xlsm',**kwargs)
        # self.all_not_ds_history = list(pd.concat([pd.Series(dfplc.index[~dfplc.DATASCIENTISM]) for dfplc in self.df_plcs.values()]).unique())
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
