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
from iqxel import *
from wifi_radio_test import *

toneFreq = 1000000
xoValAdddress = 0xa4009324

def testGPRF():
    equipment.start_vsg()
    equipment.set_equip_default()
    equipment.setVsaGprfMode()
    pass

def main():
    """ connect to DK board """
    dut = wifiRadioTest(port = '/dev/ttyACM1', baudrate = 115200)
    status = dut.connect()
    print(status)

    """ running rx command in order to do channel programming  """
    dut.setRxMode(1)
    # Exiting RX mode
    dut.setRxMode(0)
    # Entering TX_Tone mode
    dut.setTxToneMode(1)

    # configure IQXEL
    testGPRF()

    """ 1. start xoVal from 0. measure CFO.
        2. increment xoVal by xoStep. measure CFO.
        3. if the CFO with new xoVal has the same sign as current CFO xoStep = xoStep/2
            else xoStep = -xoStep/2
        4. repeat step 2 and 3 until xoStep = 1"""
    xoVal = 0
    xoStep = 64
    xoMax = 127


    #DA.WriteMemoryBlock(xoValAdddress, 1, DUT_ElementTypes.typeUnsigned32bit , xoVal, DUT_MemoryTypes.Default)
    dut.setXoValue(xoVal)
    peak_0 = equipment.getSpectrumPeak()
    cfo_0 = peak_0 - toneFreq
    cfo_0_sign = cfo_0/abs(cfo_0)
    minCFO = cfo_0
    minCFOxo = xoVal


    prevSign = cfo_0_sign

    for i in range(6):
        xoVal = xoVal+xoStep
        print('For xo value ' + hex(xoVal))
        #DA.WriteMemoryBlock(xoValAdddress, 1, DUT_ElementTypes.typeUnsigned32bit , xoVal, DUT_MemoryTypes.Default)
        dut.setXoValue(xoVal)
        peak = equipment.getSpectrumPeak()
        cfo = peak - toneFreq
        print('cfo value is ' + str(cfo))
        if (abs(cfo) <abs(minCFO)):
            minCFO = cfo
            minCFOxo = xoVal
        cfoSign = cfo/abs(cfo)
        if (cfoSign == prevSign):
            xoStep = xoStep/2
        else:
            xoStep = -xoStep/2
        prevSign = cfoSign
    pass

    # Exiting TX Tone mode
    dut.setTxToneMode(0)

    #close serial communication
    dut.close()

    # return xo val which give min CFO
    print('min CFO is ' + str(minCFO))
    print('min CFO is acheived at XO val ' + str(minCFOxo))

if __name__ == '__main__':
    equipment = IQXEL('IQXEL_80','10.90.48.125')
    main()
