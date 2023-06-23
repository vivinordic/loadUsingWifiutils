#-------------------------------------------------------------------------------
# Name:        cca_functions.py
# Purpose:     To Validate CCA mechanism in PHY
#
# Author:      Nordic Semiconductor
#
# Created:     9/06/2021
# Copyright:   (c) Nordic Semiconductor 2021
#-------------------------------------------------------------------------------

#######################################
# Keep the imports here
import math
import DUT_functions
import file_operations
#import rxvector_functions

from common_utils import *
from SOCKET_functions import *
from MATLAB_functions import *
from datarate_snr_table import *
from rxvector_functions import *
#######################################

DSSS_PREAMBLE = 192
LEGACY_HEADER = 20
DATATIME_TOLERNCE = 0.92
NOISETIME_TOLERNCE = 0.75

def readCCAParams (testParams, testConfigParams, vectorDumpDir, memoryType, DUT_RxVector, coreClkCyclesperUs, adcSamplingrate, formatType, corruptiontype):
    """Validate Physical carrier sense mechanism (CCA) using CCA Timer values and total TX time duration"""
    #Read CCA Rising and falling edge values from ETS timer.
    #[adcTime, edTime, reTime, feTime] = DUT_functions.readCCATimerValues()
    #Read CCA Timer values
    #DUT_RxVector = RxVector()
    DUT_rxVectorHdrParams = RxVectorHdrParams()

    ccaDuration_inclkcycles = DUT_functions.readCCATimerValues()
    ccaDuration = ccaDuration_inclkcycles/coreClkCyclesperUs

    sigStatus, ofdmCorrelaionCnt, leeCount = DUT_functions.readOtherFailCnt()

    rx_stats = readRXstatsFromPeripheralRegs()
    lsigdecodefail = rx_stats[2]

    for data in FORMAT_TYPE:
        if data[0] == int(formatType):
            formatTypeStr = data[1]
    #ofdmCorrelaionCnt = DUT_functions.readCorrelationCnt()
    rssiEstimated = DUT_RxVector.rssi
    edRssi = DUT_functions.readEDRssi()
    rssiEstimated = edRssi
    print("rssiEstimated is : " + str(rssiEstimated))
    print("edRssi is : " + str(edRssi))

    if rssiEstimated == -128:
        rssiEstimated = testParams['snrdB'] + 2

    file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
    inputSamples,numSamples = file_operations.readRXSamples(file_real, file_imag, memoryType)
    if(corruptiontype == 'L_parityBit' and lsigdecodefail == 1):
        inputSamples = inputSamples[:2000]
        numSamples = len(inputSamples)/2

    txTimeCalculated = (numSamples)/(adcSamplingrate)

    return rssiEstimated, ccaDuration, txTimeCalculated, sigStatus, ofdmCorrelaionCnt, formatTypeStr


def noCorruptionCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if formatType=='11B':
        if rssiEstimated < -82:
            #print("ccaDuration is : " + str(ccaDuration))
            #print("txTimeCalculated is : " + str(txTimeCalculated))
            status = "pass" if ((0.98*(txTimeCalculated-DSSS_PREAMBLE)) <= ccaDuration <= txTimeCalculated-DSSS_PREAMBLE) else "fail"
        else:
            status = "pass" if ((DATATIME_TOLERNCE*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"

    else:
        if rssiEstimated <= -82:
            status = "pass" if ((DATATIME_TOLERNCE*(txTimeCalculated-LEGACY_HEADER)) <= ccaDuration <= txTimeCalculated-LEGACY_HEADER) else "fail"

        elif (rssiEstimated > -82) and (rssiEstimated <= -62):
            status = "pass" if ((DATATIME_TOLERNCE*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"

        elif (rssiEstimated > -62):
            status = "pass" if ((DATATIME_TOLERNCE*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"

    if (rssiEstimated <= -110) and (ccaDuration ==0):
        status = "pass"
    return status

def noiseCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if rssiEstimated <= -62:
        status = "pass" if (ccaDuration <= 0) else "fail"
    else:
        #tolerance=10
        status = "pass" if ((NOISETIME_TOLERNCE*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"
    return status

def carrierLostDuringPayload(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    status = noCorruptionCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus)
    return status

def HtVhtHeHdrFail(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if formatType == '11B':
        tolerance=DSSS_PREAMBLE
        status = "pass" if (ccaDuration<=tolerance) else "fail"
    else:
        status = noCorruptionCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus)
    return status

def LsigFailCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if rssiEstimated <= -62:
        tolerance=8
        status = "pass" if ((LEGACY_HEADER-tolerance) <= ccaDuration <= LEGACY_HEADER) else "fail"
    else:
        #tolerance=10
        status = "pass" if ((NOISETIME_TOLERNCE*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"
    return status

def SFDFailCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if rssiEstimated <= -62:
        tolerance=DSSS_PREAMBLE
        status = "pass" if (ccaDuration<=tolerance) else "fail"
    else:
        status = "pass" if ((NOISETIME_TOLERNCE*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"

    return status

switcher = {
         0: noCorruptionCase,
         'noiseSignal': noiseCase,
         'carrierLostSignal': carrierLostDuringPayload,
         'VHT_crc8Bits': HtVhtHeHdrFail,
         'HE_crc8Bits': HtVhtHeHdrFail,
         'HE_ulBit': HtVhtHeHdrFail,
         'HE_bssColorBits': HtVhtHeHdrFail,
         'HE_mcsBits': HtVhtHeHdrFail,
         'HE_UBF_staIdBits': HtVhtHeHdrFail,
         'L_parityBit': LsigFailCase,
         'forceSfdFail': SFDFailCase,
         'forceInvalidRate': SFDFailCase
}

def determinePassorFail(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus, corruptionType):
    func = switcher.get(corruptionType, lambda: "Invalid CorruptionType")
    status = func(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus)
    return status