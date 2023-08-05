import pandas as pd
CONFFOLDER = '/home/dorian/sylfen/screeningBuilding/monitorBuildingDash/confFiles'
df_gtc = pd.read_excel(CONFFOLDER+'/new/ALSTOM_MODBUS_MBA_SYLFEN.xlsx',sheet_name='ALSTOM_MODBUS_MBA_SYLFEN')
def parse_object_name(x):
    m=re.match(r"(?P<description>[\w\s°]+) (?P<address>[0-9A-F]{4}h) (?P<unit>\w+ \w+) / PASSERELLE MODBUS (?P<passerelle>[\w\s]+)", x)
    if m is None:
        return [x,'','','']
    else:
        return [m.group('description'),m.group('address'),m.group('unit'),m.group('passerelle')]

len_parsed_df=df_gtc['object-name'].apply(lambda x:len(parse_object_name(x)))
parsed_df=df_gtc['object-name'].apply(lambda x:parse_object_name(x))
idxbugs=len_parsed_df[len_parsed_df==0].index
print(idxbugs)
# pr    int(df_gtc.loc[idxbugs[0],'object-name'])
# if len(idxbugs)>0:
parsed_df=parsed_df.drop(idxbugs)
dfInstr=pd.DataFrame(parsed_df.tolist(), index= parsed_df.index,columns=['description','address?','unit','passerelle'])

dfInstr['adresse']     = df_gtc.loc[dfInstr.index,'Adresse MODBUS']
dfInstr['intAddress']  = dfInstr['adresse']
dfInstr['type']        = 'IEEE754'
dfInstr['size(mots)']  = 2
dfInstr['size(bytes)'] = dfInstr['size(mots)']*2
dfInstr['scale']       = 1
dfInstr['addrTCP']     = 1
dfInstr['point de comptage'] = 'F004_'
dfInstr.index = dfInstr['point de comptage']+[str(k) for k in dfInstr.index]

########################
# decoding registers
########################
import struct
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
c=ModbusClient('192.168.194.152')
c.connect()
regs = c.read_holding_registers(0,2,unit=1).registers
struct.unpack('<f',struct.pack(">2H",*regs))[0]
# d=fs.flatten([c.read_holding_registers(k*127,127,unit=1).registers for k in range(0,1)])
nbvals=100
df_test = dfInstr.copy().iloc[:nbvals//2,:]
regs = c.read_holding_registers(0,nbvals,unit=1).registers
decodes=[]
for k_reg in range(len(regs)//2):
    regs2=[regs[2*k_reg],regs[2*k_reg+1]]
    decodes.append(struct.unpack('<f',struct.pack(">2H",*regs2))[0])
df_test['values']=['{:.2f}'.format(k) for k in decodes]
df_test[['description','address?','unit','passerelle','intAddress','type','values']]
# gtc_alstom = comUtils.ModeBusDFInstr(device_name='gtc_alstom',endpointUrl='192.168.194.152',port=502,dfplc=)
#         COMPTEURS,VARIABLES,'dfplc_gtcAlstom.pkl',freq=10,
#         dfInstr=dfInstr,generatePLC=False)

# res=gtc_alstom.getPtComptageValues(1,bo='>')
# print(res)
