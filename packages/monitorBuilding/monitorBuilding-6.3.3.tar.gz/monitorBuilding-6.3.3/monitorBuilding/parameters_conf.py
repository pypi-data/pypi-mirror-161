import os
DB_TABLE='realtimedata'
TZ_RECORD='UTC'
ACTIVE_DEVICES = [
    'vmuc',
    'smartlogger',
    'site_sls',
    'meteo',
    'tracker_okwind',
    # 'Centrale_PV_batiment_H',
    # 'gtc_alstom',
]
SIMULATOR=False
FOLDERPKL = '/home/dorian/data/sylfenData/monitoring_daily'
PARKING_TIME  = 1*3600
DB_PARAMETERS = {
    'host'     : "localhost",
    'port'     : "5432",
    'dbname'   : "bigbrother",
    'user'     : "postgres",
    'password' : "sylfenbdd"
    }
