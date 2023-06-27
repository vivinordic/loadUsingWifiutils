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
    if (targetParams.target_type == 'QSPI'):
        elf = "../harness/loader/build/smake/release_MIPSGCC/HARNESS.elf"
        address = EV.EvaluateSymbol(name, elf)
    else:
        address = DA.EvaluateSymbol(name)
    return address


def WriteMemoryBlock(mtp_address, size, elementType, value, memoryType):
    if (targetParams.target_type == 'QSPI'):
        hal.writeBlockNew(targetParams.silConnect, mtp_address, size, value, elementType)
    else:
        DA.WriteMemoryBlock(mtp_address, size, elementType, value, memoryType)
    pass


def ReadMemoryBlock(mtp_address, size, elementType, memoryType):
    if (targetParams.target_type == 'QSPI'):
        value = hal.readBlock(targetParams.silConnect, mtp_address, size, elementType)
    else:
        value = DA.ReadMemoryBlock(mtp_address, size, elementType, memoryType)
    return value