#!/bin/python
import sys, glob, re, os, time, datetime as dt,importlib,pickle,glob
import pandas as pd,numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dorianUtils.utilsD import Utils
from dorianUtils import comUtils
from dorianUtils.comUtils import (
    Configurator,
    SuperDumper_daily,
    ModbusDevice,Meteo_Client,
    VisualisationMaster_daily,
)
from dorianUtils.VersionsManager import VersionsManager_daily
from monitorBuilding import conf
importlib.reload(comUtils)
class MonitorBuilding_dumper(SuperDumper_daily):
    def __init__(self,log_file_name):
        DEVICES={}
        for device_name in conf.ACTIVE_DEVICES:
            device=conf.DF_DEVICES.loc[device_name]
            if device.protocole=='modebus':
                DEVICES[device_name] = ModbusDevice(
                    device_name=device_name,ip=device['IP'],port=device['port'],
                    dfplc=conf.PLCS[device_name],
                    modbus_map=conf.MODEBUS_MAPS[device_name],
                    freq=device['freq'],
                    bo=device['byte_order'],
                    wo=device['word_order'],
                    log_file=log_file_name)
            elif device_name=='meteo':
                DEVICES['meteo'] = Meteo_Client(conf.DF_DEVICES.loc['meteo'].freq,log_file=log_file_name)
        self.dfplc = pd.concat([v for k,v in conf.PLCS.items() if k in conf.ACTIVE_DEVICES])
        self.alltags = list(self.dfplc.index)
        SuperDumper_daily.__init__(self,DEVICES,conf.FOLDERPKL,conf.DB_PARAMETERS,conf.PARKING_TIME,
            tz_record=conf.TZ_RECORD,dbTable=conf.DB_TABLE,log_file=log_file_name)

class MonitorBuildingComputer(VisualisationMaster_daily):
    def __init__(self,**kwargs):
        VisualisationMaster_daily.__init__(self,conf.FOLDERPKL,conf.DB_PARAMETERS,conf.PARKING_TIME,
            tz_record=conf.TZ_RECORD,dbTable=conf.DB_TABLE,**kwargs)

        self.utils = Utils()
        self.conf  = conf

        tag_cats={}
        self.usefulTags = conf.USEFUL_TAGS
        self.dfplc      = conf.DF_PLC
        self.alltags    = list(self.dfplc.index)
        self.listUnits  = self.dfplc.UNITE.dropna().unique().tolist()

        for cat in self.usefulTags.index:
            tag_cats[cat] = self.getTagsTU(self.usefulTags.loc[cat,'Pattern'])
        tag_cats['SLS niveau0 puissances']=[k for k in tag_cats['SLS puissances'] if k not in tag_cats['SLS niveau1 puissances']]
        tag_cats['SLS niveau0 compteurs']=[k for k in tag_cats['SLS compteurs'] if k not in tag_cats['SLS niveau1 compteurs']]
        self.tag_categories = tag_cats
        self.compteurs      = conf.COMPTEURS

        self.listComputation = ['power enveloppe','consumed energy','energyPeriodBarPlot']

    def getUsefulTags(self,tagcat):
        return self.usefulTags.loc[tagcat]

    def get_description_tags_compteurs(self,tags):
        counts=[k.split('-')[1] for k in tags]
        return [self.compteurs.loc[k,'description'] for k in counts]

    def diffABCD_E(self):
        '''
        différence entre ABCD_E
        '''
        tags=self.getTagsTU('A007-kW sys-JTW')
        subcounts=[k for k in self.tag_categories['SLS niveau0 puissances'] if len(re.findall('-[ABD]00\d-',k))>0]
        df = self.loadtags_period(t0,t1,subcounts+tags,rsMethod='forwardfill',rs='10s')
        dff=df[tags]
        dff['sumsubcounts']=df[subcounts].sum(axis=1)
        fig=px.scatter(dff)
        fig.update_traces(mode='lines+markers')
        fig.show()
    # ==========================================================================
    #                       COMPUTATIONS FUNCTIONS
    # ==========================================================================
    def computePowerEnveloppe(self,timeRange,compteur = 'EM_VIRTUAL',rs='auto'):
        listTags = self.getTagsTU(compteur+'.+[0-9]-JTW','kW')
        df = self.df_loadTimeRangeTags(timeRange,listTags,rs='5s')
        L123min = df.min(axis=1)
        L123max = df.max(axis=1)
        L123moy = df.mean(axis=1)
        L123sum = df.sum(axis=1)
        df = pd.concat([df,L123min,L123max,L123moy,L123sum],axis=1)

        from dateutil import parser
        ts=[parser.parse(t) for t in timeRange]
        deltaseconds=(ts[1]-ts[0]).total_seconds()
        if rs=='auto':rs = '{:.0f}'.format(max(1,deltaseconds/1000)) + 's'
        df = df.resample(rs).apply(np.mean)
        dfmin = L123min.resample(rs).apply(np.min)
        dfmax = L123max.resample(rs).apply(np.max)
        df = pd.concat([df,dfmin,dfmax],axis=1)
        df.columns=['L1_mean','L2_mean','L3_mean','PminL123_mean','PmaxL123_mean',
                    'PmoyL123_mean','PsumL123_mean','PminL123_min','PmaxL123_max']
        return df

    def compute_kWhFromPower(self,timeRange,compteurs=['B001'],rs='raw'):
        generalPat='('+'|'.join(['(' + c + ')' for c in compteurs])+')'
        listTags = self.getTagsTU(generalPat+'.*sys-JTW')

        df = self.df_loadTimeRangeTags(timeRange,listTags,rs=rs,applyMethod='mean',pool=True)
        dfs=[]
        for tag in listTags:
            dftmp = self._integratePowerCol(df,tag,True)
            if not dftmp.empty:dfs.append(dftmp)

        try : df=pd.concat(dfs,axis=1)
        except : df = pd.DataFrame()
        return df.ffill().bfill()

    def compute_kWhFromCompteur(self,timeRange,compteurs=['B001']):
        generalPat='('+'|'.join(['(' + c + ')' for c in compteurs])+')'
        listTags = self.getTagsTU(generalPat+'.+kWh-JTWH')
        df = self.df_loadTimeRangeTags(timeRange,listTags,rs='raw',applyMethod='mean')
        df = df.drop_duplicates()
        dfs=[]
        for tag in listTags:
            x1=df[df.tag==tag]
            dfs.append(x1['value'].diff().cumsum()[1:])
        try :
            df = pd.concat(dfs,axis=1)
            df.columns = listTags
        except : df = pd.DataFrame()
        return df.ffill().bfill()

    def plot_compare_kwhCompteurvsPower(self,timeRange,compteurs=['B001'],rs='600s'):
        dfCompteur = self.compute_kWhFromCompteur(timeRange,compteurs)
        dfPower = self.compute_kWhFromPower(timeRange,compteurs)
        df = self.utils.prepareDFsforComparison([dfCompteur,dfPower],
                            ['energy from compteur','enery from Power'],
                            group1='groupPower',group2='compteur',
                            regexpVar='\w+-\w+',rs=rs)

        fig=px.line(df,x='timestamp',y='value',color='compteur',line_dash='groupPower',)
        fig=self.utils.quickLayout(fig,'energy consumed from integrated power and from energy counter',ylab='kWh')
        fig.update_layout(yaxis_title='energy consommée en kWh')
        return fig

    def energyPeriodBarPlot(self,timeRange,period='1d',compteurs = ['A003','B001']):
        dfCompteur   = self.compute_kWhFromCompteur(timeRange,compteurs)
        df = dfCompteur.resample(period).first().diff()[1:]
        fig = px.bar(df,title='répartition des énergies consommées par compteur')
        fig.update_layout(yaxis_title='énergie en kWh')
        fig.update_layout(bargap=0.5)
        return fig
    # ==========================================================================
    #                       for website monitoring
    # ==========================================================================
    # def getListTagsAutoConso(self,compteurs):
    #     pTotal = [self.getTagsTU(k + '.*sys-JTW')[0] for k in compteurs]
    #     pvPower = self.getTagsTU('PV.*-JTW-00')[0]
    #     listTagsPower = pTotal + [pvPower]
    #     energieTotale = [self.getTagsTU(k + '.*kWh-JTWH')[0] for k in compteurs]
    #     pvEnergie = self.getTagsTU('PV.*-JTWH-00')[0]
    #     listTagsEnergy = energieTotale + [pvEnergie]
    #     return pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy
    #
    # def computeAutoConso(self,timeRange,compteurs,formula='g+f-e+pv'):
    #     pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
    #     # df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'600s','mean')
    #     df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'600s','mean')
    #     if formula=='g+f-e+pv':
    #         g,e,f = [self.getTagsTU(k+'.*sys-JTW')[0] for k in ['GENERAL','E001','F001',]]
    #         df['puissance totale'] = df[g] + df[f] - df[e] + df[pvPower]
    #     elif formula=='sum-pv':
    #         df['puissance totale'] = df[pTotal].sum(axis=1) - df[pvPower]
    #     elif formula=='sum':
    #         df['puissance totale'] = df[pTotal].sum(axis=1)
    #
    #     df['diffPV']=df[pvPower]-df['puissance totale']
    #     dfAutoConso = pd.DataFrame()
    #     df['zero'] = 0
    #     dfAutoConso['part rSoc']     = 0
    #     dfAutoConso['part batterie'] = 0
    #     dfAutoConso['part Grid']     = -df[['diffPV','zero']].min(axis=1)
    #     dfAutoConso['Consommation du site']      = df['puissance totale']
    #     dfAutoConso['surplus PV']    = df[['diffPV','zero']].max(axis=1)
    #     dfAutoConso['part PV']       = df[pvPower]-dfAutoConso['surplus PV']
    #     # dfAutoConso['Autoconsommation'] = df[pvPower]-dfAutoConso['PV surplus']
    #     return dfAutoConso
    #
    # def consoPowerWeek(self,timeRange,compteurs,formula='g+f-e+pv'):
    #     pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
    #     # df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'1H','mean')
    #     df = self.df_loadTimeRangeTags(timeRange,listTagsPower,'1H','mean')
    #
    #     if formula=='g+f-e+pv':
    #         g,e,f = [self.getTagsTU(k+'.*sys-JTW')[0] for k in ['GENERAL','E001','F001',]]
    #         df['puissance totale'] = df[g] + df[f] - df[e] + df[pvPower]
    #     elif formula=='sum-pv':
    #         df['puissance totale'] = df[pTotal].sum(axis=1) - df[pvPower]
    #     elif formula=='sum':
    #         df['puissance totale'] = df[pTotal].sum(axis=1)
    #
    #     df = df[['puissance totale',pvPower]]
    #     df.columns = ['consommation bâtiment','production PV']
    #     return df
    #
    # def compute_EnergieMonth(self,timeRange,compteurs,formula='g+f-e+pv'):
    #     pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
    #     # df = self.df_loadTimeRangeTags(timeRange,listTagsEnergy,rs='raw',applyMethod='mean')
    #     df = self.df_loadTimeRangeTags(timeRange,listTagsEnergy,rs='raw',applyMethod='mean')
    #     df = df.drop_duplicates()
    #
    #     df=df.pivot(columns='tag',values='value').resample('1d').first().ffill().bfill()
    #     newdf=df.diff().iloc[1:,:]
    #     newdf.index = df.index[:-1]
    #     if formula=='g+f-e+pv':
    #         g,e,f = [self.getTagsTU(k + '.*kWh-JTWH')[0] for k in ['GENERAL','E001','F001',]]
    #         newdf['energie totale'] = newdf[g] + newdf[f] - newdf[e] + newdf[pvEnergie]
    #     elif formula=='sum-pv':
    #         newdf['energie totale'] = newdf[pTotal].sum(axis=1) - newdf[pvEnergie]
    #     elif formula=='sum':
    #         newdf['energie totale'] = newdf[energieTotale].sum(axis=1)
    #
    #     newdf = newdf[['energie totale',pvEnergie]]
    #     newdf.columns = ['kWh consommés','kWh produits']
    #     return newdf
    #
    # def get_compteur(self,timeDate,compteurs,formula='g+f-e+pv'):
        timeRange = [k.isoformat() for k in [timeDate - dt.timedelta(seconds=600),timeDate]]
        pTotal,pvPower,listTagsPower,energieTotale,pvEnergie,listTagsEnergy = self.getListTagsAutoConso(compteurs)
        df = self.df_loadTimeRangeTags(timeRange,listTagsEnergy,rs='20s',applyMethod='mean')
        g,e,f = [self.getTagsTU(k + '.*kWh-JTWH')[0] for k in ['GENERAL','E001','F001',]]
        if formula=='g+f-e+pv':
            df['energie totale'] = df[g] + df[f] - df[e] + df[pvEnergie]
        elif formula=='sum':
            df['energie totale'] = df[energieTotale].sum(axis=1)
        return df.iloc[-1,:]
    # ==============================================================================
    #                   GRAPHICAL FUNCTIONS
    # ==============================================================================
    def multiUnitGraphSB(self,df,tagMapping=None,**kwargs):
        if not tagMapping:tagMapping = {t:self.getUnitofTag(t) for t in df.columns}
        fig = self.utils.multiUnitGraph(df,tagMapping,**kwargs)
        return fig

class MonitorBuilding_VM(VersionsManager_daily):
    def __init__(self,*args,**kwargs):
        Config_extender.__init__(self)
        VersionManager_daily.__init__(self,FOLDERPKL,conf.CONFFOLDER + "/PLC_config/",*args,**kwargs)
        self.count_ids_0_0_to_O_1 = {
            '8-A004-':'9-A004-',
            'b-A005-':'c-A005-',
            '0f-A006-':'11-A006-',
            'd-B002-':'e-B002-',
            '7-B003-':'8-B003-',
            'e-B004-':'f-B004-',
            'a-D001-':'b-D001-',
            '9-D002-':'a-D002-',
            '10-E001-':'12-E001-',
            '11-E002-':'13-E002-',
            '12-F001-':'14-F001-',
            '13-F002-':'15-F002-',
            'c-F003-':'d-F003-'
        }

    def mergeTags_on_2022_01_07(self):
        '''on that day tags with 2 different count ids where dumped. Data look like :
        C000000c-F003-... and C00000d-F003. Need to be merged.
        -WORKS ONLY IF DATA OF 2022-01-07 ARE PRESENT
        '''
        folderday = self.folderData + '2022-01-07/'
        for oldcount,newcount in self.count_ids_0_0_to_O_1.items():
            ltags = pd.Series(self.fs.listfiles_pattern_folder(folderday,oldcount))
            # print(ltags)
            for tagold in ltags:
                tagnew = tagold.replace(oldcount,newcount)
                df1 = pickle.load(open(folderday + tagold,'rb'))
                df2 = pickle.load(open(folderday + tagnew,'rb'))
                # print(df1,df2)
                df = pd.concat([df1,df2]).sort_index()
                # print(df)
                df.to_pickle(folderday + tagnew)
                os.remove(folderday + tagold)
                print(tagold,' and ',tagnew,' were merged and ', tagold,' was removed.')

    def mergeTags_B008_F003_on_2022_01_04(self):
        '''on that day B008 and F003 were dumped. Data look like :
        -WORKS ONLY IF DATA OF 2022-01-04 ARE PRESENT
        '''
        folderday = self.folderData + '2022-01-04/'
        ltags = pd.Series(self.fs.listfiles_pattern_folder(folderday,'-B008'))
        # print(ltags)
        for tagold in ltags:
            tagnew = tagold.replace('-B008','-F003')
            df1 = pickle.load(open(folderday + tagold,'rb'))
            df2 = pickle.load(open(folderday + tagnew,'rb'))
            # print(df1,df2)
            df = pd.concat([df1,df2]).sort_index()
            # print(df)
            df.to_pickle(folderday + tagnew)
            os.remove(folderday + tagold)
            print(tagold,' and ',tagnew,' were merged and ', tagold,' was removed.')

    def get_renameTag_map_v0_0_to_v0_1(self):
        '''some counts had their ids temporarily decremented in december 2021
            correctly reincremented on the 2022-01-07.
            -WORKS ONLY IF DATA OF 2022-01-06 ARE PRESENT'''
        folderday = self.folderData + '2022-01-06/'
        count_ids=self.count_ids_0_0_to_O_1.copy()
        count_ids['14-GENE']='16-GENE'
        df_renametagsmap = {}
        for oldcount,newcount in count_ids.items():
            ltags = pd.Series(self.fs.listfiles_pattern_folder(folderday,oldcount))
            # print(ltags)
            ltags = [k.replace('.pkl','') for k in ltags]
            for oldtag in ltags:
                df_renametagsmap[oldtag] = oldtag.replace(oldcount,newcount)
        df_renametagsmap=pd.DataFrame({'oldtag':df_renametagsmap.keys(),'newtag':df_renametagsmap.values()})
        return df_renametagsmap

    def get_renameTag_map_v0_1_to_v0_2(self):
        '''
            - GENERAL-ADMINISTRATIF renamed in A007(on the 2022-01-07)
            - B008 was renamed in F003 (rename on the 2022-01-04)
            - E003, F004 counts were added (on the 2022-01-07)
            - B005,SIS,EM_VIRTUAL suppressed (on the 2022-01-07)
        '''
        df_renametagsmap = {}
        oldtags = list(self.df_plcs['0.1'].index)
        for oldtag in oldtags:
            newtag   = oldtag
            newtag   = newtag.replace('GENERAL_ADMINISTRATIF','A007')
            newtag   = newtag.replace('-B008','-F003')
            if len([k for k in ['-B005-','-EM_VIRTUAL-','SIS-'] if k in oldtag])>0:
                newtag=None
            df_renametagsmap[oldtag] = newtag
        df_renametagsmap = pd.DataFrame({'oldtag':df_renametagsmap.keys(),'newtag':df_renametagsmap.values()})

        newtags = list(self.df_plcs['0.2'].index)
        brand_newtags = [t for t in newtags if t not in list(df_renametagsmap['newtag'])]
        brand_newtags = pd.DataFrame([(None,k) for k in brand_newtags],columns=['oldtag','newtag'])
        df_renametagsmap=pd.concat([df_renametagsmap,brand_newtags])
        return df_renametagsmap[~df_renametagsmap.apply(lambda x: x['oldtag']==x['newtag'],axis=1)]

    def get_renameTag_map_v0_2_to_v1_0(self):
        '''
            - point de comptage are removed in tag names :
                ex : C0000000d-F003-13-kWh-JTWH ====> C0000000d-F003-kWh-JTWH
            - 00 at the end of PV00000001 removed.
            - XM meteo data for le cheylas added
        '''
        df_renametagsmap = {}
        oldtags=list(self.df_plcs['0.2'].index)
        for oldtag in oldtags:
            tagsplit = oldtag.split('-')
            newtag   = oldtag
            if not re.match('C[0-9a-f]{8}',oldtag) is None:
                newtag = '-'.join(tagsplit[0:2]+tagsplit[3:])

            newtag= newtag.replace('PV00000001-centrale SLS 80kWc-JTW-00','PV00000001-centrale SLS 80kWc-kW-JTW')
            newtag= newtag.replace('PV00000001-centrale SLS 80kWc-JTWH-00','PV00000001-centrale SLS 80kWc-kWh-JTWH')
            df_renametagsmap[oldtag] = newtag
        df_renametagsmap=pd.DataFrame({'oldtag':df_renametagsmap.keys(),'newtag':df_renametagsmap.values()})

        newtags=list(self.df_plcs['1.0'].index)
        brand_newtags = [t for t in newtags if t not in list(df_renametagsmap['newtag'])]
        brand_newtags = pd.DataFrame([(None,k) for k in brand_newtags],columns=['oldtag','newtag'])
        df_renametagsmap=pd.concat([df_renametagsmap,brand_newtags])
        return df_renametagsmap
