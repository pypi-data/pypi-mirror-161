#!/bin/python
import time,sys,os
start=time.time()
import pandas as pd
from dorianUtils.comUtils import print_file
from monitorBuilding import (conf,monitorBuilding)
print('monitorBuilding loaded in ',time.time()-start,' seconds')

__appdir = os.path.dirname(os.path.realpath(__file__))
PARENTDIR = os.path.dirname(__appdir)

log_file = PARENTDIR+ '/log/dumper_monitorBuilding.log'
print_file(' '*30 + 'START MONITORING DUMPER' + '\n',filename=log_file,mode='w')
dumper_monitoring = monitorBuilding.MonitorBuilding_dumper(log_file_name=log_file)
dumper_monitoring.park_database()
dumper_monitoring.start_dumping()
