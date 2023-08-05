import pandas as pd
from monitorBuilding import (monitorBuilding,conf)
from dorianUtils import comUtils

cfg=monitorBuilding.MonitorBuildingComputer()

# ############################
# DEFINE THE PATH WHERE      #
# YOUR DAILY PARKED DATA ARE #
# LOCATED                    #
# ############################
cfg.folderPkl='/home/dorian/data/sylfenData/monitoring_daily/'

### define your time window with timestamps t0 and t1
t0=pd.Timestamp('2022-05-20 5:00',tz='CET')
t1 = t0+pd.Timedelta(days=7,hours=12)

### get all the tags where tracker appears in
tags=cfg.getTagsTU('tracker')
### load the data of the "tags" between timestamps t0 and t1.
df=cfg.loadtags_period(t0,t1,tags,rsMethod='mean',rs='60s')

### plot the data superimposed on a same graph with built-in color code
fig=cfg.multiUnitGraphSB(df)
fig.show()
