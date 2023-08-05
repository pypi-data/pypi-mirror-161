import os
DB_TABLE='realtimedata'
TZ_RECORD='UTC'
ACTIVE_DEVICES = [
    'vmuc',
    'smartlogger',
    'site_sls',
    'meteo'
    'tracker_okwind',
    # 'gtc_alstom',
]
SIMULATOR=False
FOLDERPKL = os.getenv('HOME')+'/monitorbuilding_user/monitoring_daily/'
PARKING_TIME  = 1*3600
DB_PARAMETERS = {
    'host'     : "localhost",
    'port'     : "5432",
    'dbname'   : "bigbrother",
    'user'     : "postgres",
    'password' : "sylfenbdd"
    }
