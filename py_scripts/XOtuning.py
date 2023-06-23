#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     13/09/2022
# Copyright:   (c) vivi 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
from imgtec import codescape
from imgtec.codescape.da_types import LoadType
#from CSUtils import DA
from iqxel import *
from common_utils import *

toneFreq = 1000000
xoValAdddress = 0xa4009324
def testGPRF():
    equipment.start_vsg()
    equipment.set_equip_default()
    equipment.setVsaGprfMode()
    pass

def main():
    target_name = 'SysProbe 151'


    '''Start function'''
    probe = None
    if codescape.environment == 'standalone':
        #from CSUtils import DA
        try:
            DA.UseTarget(target_name)
        except:
            print('Not selected valid target')
            print("Exiting with error code -2")
            return -2

    target_info = DA.GetTargetInfo()
    print(str(target_info))

    #DA.HardReset()
    #loadProgramFile()
    #runTarget()

    DA.SelectTargetByPattern('MCU')
    print('Running Target')
    #DA.Run()

    testGPRF()

    """ 1. start xoVal from 0. measure CFO.
        2. increment xoVal by xoStep. measure CFO.
        3. if the CFO with new xoVal has the same sign as current CFO xoStep = xoStep/2
            else xoStep = -xoStep/2
        4. repeat step 2 and 3 until xoStep = 1"""
    xoVal = 0
    xoStep = 32
    xoMax = 63


    DA.WriteMemoryBlock(xoValAdddress, 1, DUT_ElementTypes.typeUnsigned32bit , xoVal, DUT_MemoryTypes.Default)
    peak_0 = equipment.getSpectrumPeak()
    cfo_0 = peak_0 - toneFreq
    cfo_0_sign = cfo_0/abs(cfo_0)


    prevSign = cfo_0_sign

    for i in range(6):
        xoVal = xoVal+xoStep
        print('For xo value ' + hex(xoVal))
        DA.WriteMemoryBlock(xoValAdddress, 1, DUT_ElementTypes.typeUnsigned32bit , xoVal, DUT_MemoryTypes.Default)
        peak = equipment.getSpectrumPeak()
        cfo = peak - toneFreq
        print('cfo value is ' + str(cfo))
        cfoSign = cfo/abs(cfo)
        if (cfoSign == prevSign):
            xoStep = xoStep/2
        else:
            xoStep = -xoStep/2
        prevSign = cfoSign
    pass

if __name__ == '__main__':
    equipment = IQXEL('IQXEL_80','10.90.48.121')
    main()
