## Monitor building
Monitoring of energy consumption and production of the SLS actiparc site.
Version : 6.3.2


The whole program dumps electrical consumption and production data from different modbus servers (using a PLC_configuration file .xlsx).
- the dumper can be started(for those who have access to the private git project) with :
```
python src/dumper_monitorBuilding.py
```
## pre-requisites

### postgresSQL
- postgressql server should be active running on port 5432(user:postgres,password:sylfenbdd) containing a **jules** database with a **realtimedata** table(default settings).
- do not forget to cofnigure pg_hba.conf correctly.
- you change password of user postgres with :
```shell
alter user <postgres> password '<newpassword>';
```  

This is also needed to run the function loadtags_period and read realtime_data. If you do not have this configuration it is still possible to load data using the function
```python
cfg = MonitorBuilding_computer()
df = cfg.streamer.load_parkedtags_daily(t0,t1,tags,cfg.folderPkl)

```
### data acquisition
- it uses the python package dorianUtils==6.3.1 Please install it with pip:
```
pip install dorianUtils==6.3.1
```
- to change the default settings of the application, update the file *parameters_conf.py* in the folder monitorBuilding_user folder in your home and this will overwrite the default parameters.
- conf.py has a function generate_conf_small_power to regenerate the configuration and load the new configuration file. It builds also the tag_color_code and the list of indicators.

```
pip install monitorBuilding
```
or in the folder of the project.
```
pip install -e .
```
