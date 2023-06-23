#-------------------------------------------------------------------------------
# Name:        spatialReuse_functions.py
# Purpose:     To Validate Spatial Reuse functionality in PHY
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

def spatialReusePostProssesing(testConfigParams, vectorDumpDir, memoryType, coreClkCyclesperUs, adcSamplingrate, spatialReuseCnt, snrdB, PacketFormat, threshold):

    file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
    inputSamples,numSamples = file_operations.readRXSamples(file_real, file_imag, memoryType)
    calCcaDuration = (numSamples)/(adcSamplingrate)
    ccaDuration_inclkcycles = DUT_functions.readCCATimerValues()
    ccaDuration = ccaDuration_inclkcycles/coreClkCyclesperUs
    if (snrdB > -82) and (snrdB <= -70):
        # In case of VHT, CCA duration LSTF(4) + LLTF (8) + LSIG(4) + VHTSIGA (8) = 24us
        # In case of HESU, expected CCA duration is LSTF(4) + LLTF (8) + LSIG(4) + RLSIG(4) + HESIGA (8) = 28us
        # In case of HEERSU, expected CCA duration is LSTF(4) + LLTF (8) + LSIG(4) + RLSIG(4) + HESIGA (16) = 36us
        # Added 12us latency for the the CCA duration.
        if (PacketFormat == 4): # VHT
            expCcaDurationStr = '[20:36]'
            ccaCheck = (ccaDuration >= 20) and (ccaDuration <= 36)
        elif (PacketFormat == 5) or (PacketFormat == 6): # HESU and HEMU
            expCcaDurationStr = '[24:40]'
            ccaCheck = (ccaDuration >= 24) and (ccaDuration <= 40)
        elif (PacketFormat == 7): # HEERSU
            expCcaDurationStr = '[32:48]'
            ccaCheck = (ccaDuration >= 32) and (ccaDuration <= 48)
    elif (snrdB < -82):
        if (PacketFormat == 4): # VHT
            # For VHT, SNR < -82dBm, CCA (timer based) to be asserted after LSIG and gets de-asserted after spatial reuse event is asserted.
            # So, CCA duration of 8us is in the expected range.
            expCcaDurationStr = '8us'
            ccaCheck = (ccaDuration > 0) and (ccaDuration <= 8)
        elif (PacketFormat == 5) or (PacketFormat == 6): # HESU and HEMU
            # For HESU, SNR < -82dBm, CCA (timer based) to be asserted after LSIG and gets de-asserted after spatial reuse event is asserted.
            # So, CCA duration of 12us is in the expected range.
            expCcaDurationStr = '12us'
            ccaCheck = (ccaDuration > 0) and (ccaDuration <= 12)
        elif (PacketFormat == 7): # HEERSU
            # For HE-ER-SU, SNR < -82dBm, CCA is asserted immediately after ED.
            # Hence, duration is > 30us.
            expCcaDurationStr = '>30us'
            ccaCheck = (ccaDuration >= 30)
    elif (snrdB >= threshold - 5):
        # In this condition signal power will toggle across threshold level
        # CCA Duration will be the accumulated value across the packet.
        # So CCA duration will be less than calculated Tx time (Max CCA duration).
        # It's completely random based on how signal will toggle.
        expCcaDurationStr = '< ' + str(calCcaDuration)
        ccaCheck = (ccaDuration > 0) and (ccaDuration < calCcaDuration)
    elif (snrdB > -62):
        expCcaDurationStr = str(calCcaDuration)
        ccaCheck = (ccaDuration > 0) and (ccaDuration <= calCcaDuration)

    if (snrdB < threshold) and (spatialReuseCnt == 1) and ccaCheck:
        finalStatus = 'PASS'
    elif (snrdB > threshold) and (spatialReuseCnt == 0) and ccaCheck:
        finalStatus = 'PASS'
    else:
        finalStatus = 'FAIL'


    return ccaDuration, expCcaDurationStr, calCcaDuration, finalStatus


