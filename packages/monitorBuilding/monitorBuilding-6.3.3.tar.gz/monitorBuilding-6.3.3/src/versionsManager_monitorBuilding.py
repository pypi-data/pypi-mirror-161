# ==============================================================================
#                           UPDATE HISTORICAL DATA
import os,sys,glob,pickle,re,importlib,datetime as dt
import subprocess as sp
import time
import pandas as pd,numpy as np
import pickle
import dorianUtils.comUtils as comutils
importlib.reload(comutils)
import dorianUtils.utilsD as ut
importlib.reload(ut)
import monitorBuildingDash.screenBuilding as screenBuilding
importlib.reload(screenBuilding)
for k in range(50):print()
utils=ut.Utils()
# mvm = screenBuilding.ScreeningBuilding_VM(loadAnyway=False)

# streamer=comUtils.Streamer()
# t0 = pd.Timestamp('2021-01')
# df=streamer.listfiles_pattern_period(t0,t1,pattern,folderpkl):

mvm = screenBuilding.ScreeningBuilding_VM([True,True,True])


# def make_compatible_v0_0to_v1_0():
t0 = pd.Timestamp('2022-02-27',tz='CET')
t1 = mvm.tmax
# period = [mvm.tmin,mvm.tmax]
period = [t0,t1]
general1 = mvm.streamer.listfiles_pattern_period(t0,t1,'GENE*-kWh-JTWH',mvm.folderData,pool=False)
# mvm.mergeTags_on_2022_01_07()
# mvm.mergeTags_B008_F003_on_2022_01_04()
map_renametag = mvm.get_renameTag_map_v0_0_to_v0_1()
replacedmap = mvm.make_it_compatible_with_renameMap(map_renametag,period=period)
general2 = mvm.streamer.listfiles_pattern_period(t0,t1,'GENE*-kWh-JTWH',mvm.folderData,pool=False)
#### check general1 vs general2
mvm = screenBuilding.ScreeningBuilding_VM([True,True,True])

map_renametag = mvm.get_renameTag_map_v0_1_to_v0_2()
a007_1 = mvm.streamer.listfiles_pattern_period(t0,t1,'A007*-kWh-JTWH',mvm.folderData,pool=False)
replacedmap = mvm.make_it_compatible_with_renameMap(map_renametag,period=period)
a007_2 = mvm.streamer.listfiles_pattern_period(t0,t1,'A007*-kWh-JTWH',mvm.folderData,pool=False)
#### check a007_1 vs a007_2
mvm = screenBuilding.ScreeningBuilding_VM([True,True,True])

map_renametag = mvm.get_renameTag_map_v0_2_to_v1_0()
pv1 = mvm.streamer.listfiles_pattern_period(t0,t1,'PV*-kWh-JTWH',mvm.folderData,pool=False)
replacedmap = mvm.make_it_compatible_with_renameMap(map_renametag,period=period)
pv2 = mvm.streamer.listfiles_pattern_period(t0,t1,'PV*-kWh-JTWH',mvm.folderData,pool=False)
#### check pv1 vs pv2
#### add missing tags as empty series
mvm.create_emptytags_version(period,mvm.df_plcs['1.0'])
mvm = screenBuilding.ScreeningBuilding_VM([True,True,True])
# mvm.show_map_of_compatibility(True)
# mvm.show_map_of_compatibility(False)
# ==============================================================================
#                           TESTS
def test_get_functions_minutely():
    folderminute  = mvm.folderData+'2021-12-15/15/00/'
    brand_newtags = map_renametag.loc[map_renametag['oldtag'].isna(),'newtag']
    dfcreate      = mvm.get_createnewtag_folderminute(folderminute,list(brand_newtags))
    map_pressenceTags=mvm.get_presenceTags_folder(folderminute)
    map_missingTags=mvm.get_missing_tags_versions(folderminute)

def test_loading_functions_daily():
    folderday  = mvm.folderData+'2022-01-05/'
    ###### list tags in a folder
    # mvm.get_listTags_folder(folderday)
    # mvm.get_lentags(folderday)
    ###### in all tags history get a list of those present in the folder
    mvm.get_presenceTags_folder(folderday)
    ###### for all tags history get the list of missing tags of a folder for all versions
    mvm.get_missing_tags_versions(folderday)
    ###### in all tags history get a map of missing tags for all versions for all folders
    mvm.load_missingTags_versions(pool=False)
    #### get a map of tags/period for the presence of tags having the pattern
    mvm.get_patterntags_folders(['2021-12-26','2022-01-02'],'F004')

    #### create a tag as empty dataframe in a folder
    mvm.get_createnewtag_folder(mvm.folderData+'2021-12-31/',['C00000017-F004-kW L3-JTW'])
    #### replace a list of old tags by a list of new tags in a folder
    tag2replace = map_renametag.set_index('oldtag').loc[['C00000016-GENERAL_ADMINISTRATIF-23-kWh-JTWH']].reset_index()
    mvm.get_replace_tags_folder(mvm.folderData+'2021-12-31/',tag2replace)

def test_show_functions():
    mvm.show_nbFolder()
    mvm.show_map_of_compatibility(True)
    mvm.show_map_of_compatibility(False)
    tags=list(pd.Series(mvm.all_tags_history).sample(n=20))
    mvm.show_map_presenceTags(tags)
