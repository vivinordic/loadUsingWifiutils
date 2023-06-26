#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      vivi
#
# Created:     23-06-2023
# Copyright:   (c) vivi 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#from CSUtils import DA
from common_utils import *
import evaluate_variable as EV
import hal

def EvaluateSymbol(name):
    if (targetParams.target_type == QSPI):
        address = EV.EvaluateSymbol(name)
    else:
        address = DA.EvaluateSymbol(name)
    pass


def WriteMemoryBlock(mtp_address, size, elementType, value, memoryType):
    if (targetParams.target_type == QSPI):
        hal.writeBlockNew(targetParams.target, addr, size, value, dataType)
    else:
        DA.WriteMemoryBlock(mtp_address, size, elementType, value, memoryType)
    pass


def ReadMemoryBlock(mtp_address, size, elementType, memoryType):
    if (targetParams.target_type == QSPI):
        hal.readBlock(targetParams.target, addr, size, data, dataType)
    else:
        value = ReadMemoryBlock(mtp_address, size, elementType, memoryType)
    return value