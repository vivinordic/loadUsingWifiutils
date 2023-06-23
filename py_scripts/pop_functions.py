#-------------------------------------------------------------------------------
# Name:        pop_functions.py
# Purpose:     To Validate POP mechanism in PHY
#
# Author:      Nordic Semiconductor
#
# Created:     21/10/2021
# Copyright:   (c) Nordic Semiconductor 2021
#-------------------------------------------------------------------------------

#######################################
# Keep the imports here
import math
import DUT_functions
import file_operations
#######################################

def readPopParams(testConfigParams, vectorDumpDir, memoryType, coreClkCyclesperUs, adcSamplingrate, popCnt, testcaseParams):

    ccaDuration_inclkcycles = DUT_functions.readCCATimerValues()
    ccaDuration = ccaDuration_inclkcycles/coreClkCyclesperUs

    file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
    inputSamples,numSamples = file_operations.readRXSamples(file_real, file_imag, memoryType)
    txTimeCalculated = (numSamples)/(adcSamplingrate)

    if (popCnt == 1):
        popStatus = 'POP DETECTED'
        finalStatus = 'PASS'
    else:
        popStatus = 'POP NOT DETECTED'
        finalStatus = 'FAIL'

    # Capturing first packet format from testcaseParams.
    if type(testcaseParams[1]) == unicode:
        formatt = testcaseParams[1].split('  ')
        firPktFormat = int(formatt[0])
    # Capturing timing difference between 1st packet and 2nd packet.
    if type(testcaseParams[11]) == unicode:
        timmDiff = testcaseParams[11].split('  ')
        relTimDiff = int(timmDiff[1])

    # Second AGC trigger scenario.
    if ((firPktFormat == 2) or (firPktFormat == 4) and (relTimDiff in range(28, 33))) and (popCnt == 0):
            finalStatus = 'PASS'
    elif ((firPktFormat == 5) and (relTimDiff in range(32, 37))) and (popCnt == 0):
            finalStatus = 'PASS'
    elif ((firPktFormat == 7) and (relTimDiff in range(40, 45))) and (popCnt == 0):
            finalStatus = 'PASS'
    elif ((firPktFormat == 6) and (relTimDiff in range(40, 45))) and (popCnt == 0):
            finalStatus = 'PASS'


    return ccaDuration, txTimeCalculated, popStatus, finalStatus


