#!/usr/bin/env python
from pymodbus.server.sync import ModbusTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading

allTCPid=range(0,23)
slaves={}
for k in allTCPid:
    slaves[k]  = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [k]*128))
context = ModbusServerContext(slaves=slaves, single=False)
server=ModbusTcpServer(context, address=("", 5020))
#
# server.serve_forever()
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()
