from flask import Flask,Blueprint,request,session,render_template,send_file
from subprocess import check_output
import json,os,sys,glob,time,traceback
import numpy as np,pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from string import ascii_letters,digits
from monitorBuilding import (monitorBuilding,conf)
import dorianUtils.utilsD as utilsD
from dorianUtils.comUtils import (timenowstd,computetimeshow)

cfg=monitorBuilding.MonitorBuildingComputer()
cfg.methods_list=cfg.methods_list[5:6]+cfg.methods_list[:5]+cfg.methods_list[6:]
cfg.styles = ['default'] + cfg.utils.styles

# #####################
#    MANAGE LOGS      #
# #####################
__appdir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.dirname(__appdir)
infofile_name  = log_dir+'app.log';
start_msg=timenowstd() + ' '*10+ 'starting monitorbuilding dash\n'.upper()+'*'*60+'\n'
with open(infofile_name,'w') as logfile:logfile.write(start_msg)
errorfile_name = log_dir+'app.err';
with open(errorfile_name,'w') as logfile:logfile.write(start_msg)
def log_info(msg):
    with open(infofile_name,'a') as loginfo_file:
        loginfo_file.write('-'*60 +'\n'+ msg +'\n')
        loginfo_file.write('-'*60+'\n')

def notify_error(tb,error):
    with open(errorfile_name,'a') as logerror_file:
        logerror_file.write('-'*60 +'\n'+timenowstd()+' '*10 + error['msg']+'\n')
        traceback.print_exception(*tb,file=logerror_file)
        logerror_file.write('-'*60+'\n')

# ###################
#    FUNCTIONS      #
# ###################
def exportDataOnClick(fig,baseName='data'):
    dfs = [pd.Series(trace['y'],index=trace['x'],name=trace['name']) for trace in fig['data']]
    df = pd.concat(dfs,axis=1)

    t0,t1=fig['layout']['xaxis']['range']
    df = df[(df.index>t0) & (df.index<t1)]

    dateF=[pd.Timestamp(t).strftime('%Y-%m-%d %H_%M') for t in [t0,t1]]
    filename = 'static/tmp/' + baseName +  '_' + dateF[0]+ '_' + dateF[1]+'.xlsx'
    df.to_excel(filename)
    return filename

app = Flask(__name__)
fig_wh=780
# ###############
#    ROUTING    #
# ###############
@app.route('/monitorBuilding', methods=['GET'])
def main_viewport():
    return render_template('monitoring_dash.html')

@app.route('/init', methods=['GET'])
def init():
    return json.dumps({
                'all_tags':cfg.getTagsTU(''),
                'styles':cfg.styles,
                'categories':cfg.usefulTags.index.to_list(),
                'rsMethods':cfg.methods_list,
                'initalTags':['PV00000001-centrale SLS 80kWc-kW-JTW','XM_le_cheylas_temp','XM_le_cheylas_clouds']
                })

@app.route('/generate_fig', methods=['POST'])
def generate_fig():
    debug=True
    # try:
    start=time.time()
    data=request.get_data()
    parameters=json.loads(data.decode())
    if debug:
        print('+'*100 + '\n')
        for k,v in parameters.items():print(k,':',v)
        print('+'*100 + '\n')

    t0,t1=[pd.Timestamp(t,tz='CET') for t in parameters['timerange'].split(' - ')]
    # t0=pd.Timestamp('2022-02-20 10:00',tz='CET')
    # t0,t1=[t-pd.Timedelta(days=47) for t in [t0,t1]]

    if debug:print('t0,t1:',t0,t1)
    tags = parameters['tags']
    if parameters['categorie'] in cfg.tag_categories.keys():
        tags+=cfg.tag_categories[parameters['categorie']]
    if debug:print('alltags:',tags)
    rs,rsMethod=parameters['rs_time'],parameters['rs_method']
    df = cfg.loadtags_period(t0,t1,tags,rsMethod=rsMethod,rs=rs,checkTime=False)
    if debug:print(df)
    fig=cfg.multiUnitGraphSB(df)
    fig.update_layout(width=1260,height=750,legend_title='tags')
    log_info(computetimeshow('fig generated ',start))
    return fig.to_json(),200
    # except:
    #     error={'msg':'impossible to generate figure','code':1}
    #     notify_error(sys.exc_info(),error)
    #     fig=go.Figure()
    # return error,201

@app.route('/export2excel', methods=['POST'])
def export2excel():
    try:
        data=request.get_data()
        fig=json.loads(data.decode())
        file_xslsx=exportDataOnClick(fig)
        # log_info(computetimeshow('.xlsx downloaded',start))
        return file_xslsx
    except:
        error={'msg':'service export2excel not working','code':3}
        notify_error(sys.exc_info(),error)
        return error

@app.route('/send_description_names',methods=['POST'])
def send_names():
    data=request.get_data()
    data=json.loads(data.decode())
    new_names=cfg.toogle_tag_description(data['tags'],data['mode'])
    print(data['mode'])
    return pd.Series(new_names).to_json()

app.run(host='0.0.0.0',port=35001,debug=True)
