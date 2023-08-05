from pymodbus.client.sync import ModbusTcpClient as ModbusClient
client = ModbusClient(host='localhost',port=5020)
client.connect()
client.write_registers(0,[1,3,65,986,5],unit=2)
r = client.read_holding_registers(0,4,unit=2)
# r = client.read_holding_registers(0,4,unit=12)
# s= client.read_holding_registers(0,4,unit=1)
# t= client.read_holding_registers(0,4,unit=16)
client.close()
