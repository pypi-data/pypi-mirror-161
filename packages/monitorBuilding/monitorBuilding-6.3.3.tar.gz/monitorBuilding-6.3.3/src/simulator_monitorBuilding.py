#!/bin/python
import importlib
import monitorBuildingDash.screenBuilding as screenBuilding
importlib.reload(screenBuilding)
simulatorVMUC = screenBuilding.Simulator_SB()
cfg =screenBuilding.ConfigScreenBuilding()
# ==============================================================================
#                          # TESTS
def test():
    simulatorVMUC.server_thread.start()
    for k in range(1):
    # simulatorVMUC.generateRandomData(1)
        simulatorVMUC.writeInRegisters()
            # print(simulatorVMUC.dfInstr.loc[simulatorVMUC.dfInstr.addrTCP==1,['value']])
# ==============================================================================
#                           MAIN SIMULATOR
simulatorVMUC.start()
#
