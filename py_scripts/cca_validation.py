#-------------------------------------------------------------------------------
# Name:        cca_validation.py
# Purpose:     To Validate CCA mechanism in PHY
#
# Author:      Nordic Semiconductor
#
# Created:     9/06/2021
# Copyright:   (c) Nordic Semiconductor 2021
#-------------------------------------------------------------------------------

#######################################
# Keep the imports here
import time
import datetime
import math
import test_mode_functions
import DUT_functions
import target_functions
import file_operations
#import rxvector_functions

from common_utils import *
from SOCKET_functions import *
from MATLAB_functions import *
from datarate_snr_table import *
from rxvector_functions import *
#######################################

def main ():
    """Validate Physical carrier sense mechanism (CCA) using CCA Timer values and total TX time duration"""
    resultsConsld = []
    # Instantiate the TestConfigParams object
    targetParams = TargetParams()
    testConfigParams = TestConfigParams()
    DUT_RxVector = RxVector()
    DUT_rxVectorHdrParams = RxVectorHdrParams()

    # Read the test configuration from "WLANPHY.TestConfig.xlsx" excel sheet
    testConfigDict = file_operations.readTestConfigExcel('WLANPHY.TestConfig.xlsx')
    targetParams.updateParams(testConfigDict)
    testConfigParams.updateParams(testConfigDict)

    #initialize debug log file in results folder
    createDebugLog(testConfigParams)
    debugPrint("=================== CCA TEST START ===================")
    createSubPlanLog(testConfigParams)
    target_functions.loadnRunTarget(targetParams)
    DUT_functions.pollSystemReady()

    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
    # Initialize Socket
    sock, portNo = socket_init()
    systemConfig = targetParams.system_config

    #Give Test Start indication to DUT
    DUT_functions.startTestcase()
    testcaseIdx, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
    # Start the Matlab process
    portNo = sock.getsockname()[1]
    MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
    systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, testcaseIdx)
    resultsConsld, heading, rowNum = initializeExcelSheet (keyParams)
    ###################Enable when testing multile test cases###################
    while (testcaseIdx <= testConfigParams.total_test_cases):
        crcPassCnt = 0
        ed_cnt = 0
        matlabCrcCnt = 0
        pktIdx = 1
        excelInit = 1
        length = 0
        systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, testcaseIdx)
        DUT_functions.configSystemParams(systemParams)
        payloadFile = "mpdu_payload.txt"
        vectorDumpDir = file_operations.returnSimOutDir (testConfigParams, testcaseIdx)
        payloadData=file_operations.generatePayload(testParams['length'] - 4) # 4 CRC bytes are deducted
        file_operations.writePayloadToFile (payloadData, payloadFile, testParams['length'] - 4,1, vectorDumpDir)
        DUT_functions.setPayloadLengthRx(testParams['length'])

        #Enable LNA and AGC for CCA testing
        if (testConfigParams.subFuncTestPlan == 'CCA') or (testConfigParams.subFuncTestPlan == 'CCADISC'):
            memoryType = 'separate'
            DUT_functions.agcModuleEnable()
            testConfigParams.lna_model_enable = 'YES'
            agcEn  = 1
        else:
            memoryType = 'shared'
            testConfigParams.lna_model_enable = 'NO'
            agcEn  = 0

        #Run RX test for numOfPkts in a loop and log rx stats for each packet.
        debugPrint("startng test for testCase" + str(testcaseIdx))
        MatlabInput =  'testcaseIdx' + ' ' + str(testcaseIdx) + ' ' + 'pktIdx' + ' ' + str(pktIdx) + ' ' + 'firmwareAgcTestEn' + ' ' + str(agcEn)
        #Same function used from testModeFunctions to run RX for single packet analysis
        dutState = test_mode_functions.runRxSinglePacket(MatlabInput, testcaseIdx, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType, vectorDumpDir)
        if (dutState == 'MATLAB_STUCK'):
            KillSubProcess(MtlbExeProcess)
            portNo = sock.getsockname()[1]
            MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
            testcaseIdx = testcaseIdx + 1
            continue
        #Read CCA Rising and falling edge values from ETS timer.
        #[adcTime, edTime, reTime, feTime] = DUT_functions.readCCATimerValues()
        #Read CCA Timer values
        ccaDuration_inclkcycles = DUT_functions.readCCATimerValues()
        ccaDuration = ccaDuration_inclkcycles/160

        crcPassStatus, edStatus, popCnt, spatialReuseCnt = DUT_functions.getRXStats ()
        if (crcPassStatus == 'OFDM PACKET CRC_PASS') or (crcPassStatus == 'DSSS PACKET CRC_PASS'):
            crcStatus = 1
        else:
            crcStatus = 0
        crcPassCnt = crcPassCnt + crcStatus
        ed_cnt = ed_cnt + edStatus
        sigStatus = DUT_functions.readOtherFailCnt()
        DUT_functions.clearRxStats()
        debugPrint("crc pass cnt " + str(crcPassCnt))
        debugPrint("ED cnt " + str(ed_cnt))
        matlabCrcCnt = readMatlabStatus(testConfigParams, testcaseIdx, matlabCrcCnt)
        #Raead RX Vector values from memory
        readRxVector (systemParams, DUT_RxVector, testConfigParams, testcaseIdx)
        rxvectorDict = convertRxVectasDict(systemParams, DUT_RxVector)
        parseHeaderBytes(DUT_RxVector, DUT_rxVectorHdrParams)
        #Read length feild of header/Lsig from RXVector for TX time calculation.
        for data in FORMAT_TYPE:
            if data[0] == testParams['format']:
                formatType = data[1]
        if formatType=='11B':
            dssshdr=getDsssHdr(DUT_dsssHeader)
            length=dssshdr.length
            preambleType = 'LONG' if testParams['shortGi']==0 else 'SHORT'
        else:
            lsigHdr = getLsigHdr(DUT_lsigHeader)
            length = lsigHdr.length
            preambleType = 0

        rssiEstimated = DUT_RxVector.rssi
        print ("rssi estimated is: " + str(rssiEstimated))
        edRssi = DUT_functions.readEDRssi()
        print ("ed rssi is: " + str(edRssi))
        if rssiEstimated == -256:
            #rssiEstimated = testParams['snrdB'] - 15
            rssiEstimated = testParams['snrdB'] + 2
        corruptionType = testParams['corruptionType']
        #print (corruptionType)
        #if corruptionType == 'noiseSignal':
        file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
        inputSamples,numSamples = file_operations.readRXSamples(file_real, file_imag, memoryType)
        if corruptionType == 'noiseSignal':
            txTimeCalculated = numSamples/(2*40) #no of samples/40
        else:
            if formatType=='11B':
                txTimeCalculated = (numSamples-544)/(2*40)
            else:
                txTimeCalculated = (numSamples-784)/(2*40)
        print ("mumber of samples: " + str(numSamples))
        #Determine Pass or fail and Log results to excel sheet
        resultStatus = determinePassorFail(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus, corruptionType)
        status = [rssiEstimated, ccaDuration, txTimeCalculated, sigStatus, resultStatus]
        rowNum = logResults (testParams, status, resultsConsld, rowNum, heading)
        resetRXVectorParams()
        if (dutState == 'DUT_STUCK'):
            target_functions.loadnRunTarget(targetParams)
            DUT_functions.pollSystemReady()
            DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
            DUT_functions.startTestcase()
        testcaseIdx = testcaseIdx + 1

    conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
    conn.setblocking(1)
    conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
    resultsConsld.workbook.close()

def noCorruptionCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if formatType=='11B':
        if rssiEstimated < -82:
            tolerance=4
            status = "pass" if ((txTimeCalculated-144-48-tolerance) <= ccaDuration <= txTimeCalculated-144-48+tolerance) else "fail"
        else:
            tolerance=10
            status = "pass" if ((txTimeCalculated-tolerance) <= ccaDuration <= txTimeCalculated) else "fail"

    else:
        if rssiEstimated <= -82:
            tolerance=3
            status = "pass" if ((txTimeCalculated-20-tolerance) <= ccaDuration <= txTimeCalculated-20+tolerance) else "fail"

        elif (rssiEstimated > -82) and (rssiEstimated <= -62):
            tolerance=2
            status = "pass" if ((txTimeCalculated-8) <= ccaDuration <= txTimeCalculated) else "fail"

        elif (rssiEstimated > -62):
            tolerance=2
            status = "pass" if ((txTimeCalculated-8) <= ccaDuration <= txTimeCalculated) else "fail"

    if (rssiEstimated <= -110) and (ccaDuration ==0):
        status = "pass"
    return status

def noiseCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if rssiEstimated <= -62:
        status = "pass" if (ccaDuration <= 0) else "fail"
    else:
        #tolerance=10
        status = "pass" if ((0.75*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"
    return status

def carrierLostDuringPayload(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    status = noCorruptionCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus)
    return status

def HtVhtHeHdrFail(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if formatType == '11B':
        tolerance=196
        status = "pass" if (ccaDuration<=tolerance) else "fail"
    else:
        status = noCorruptionCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus)
    return status

def LsigFailCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if rssiEstimated <= -62:
        tolerance=8
        status = "pass" if ((20-tolerance) <= ccaDuration <= 20) else "fail"
    else:
        #tolerance=10
        status = "pass" if ((0.75*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"
    return status

def SFDFailCase(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus):
    if rssiEstimated <= -62:
        tolerance=196
        status = "pass" if (ccaDuration<=tolerance) else "fail"
    else:
        status = "pass" if ((0.75*txTimeCalculated) <= ccaDuration <= txTimeCalculated) else "fail"

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

def logResults(testParams, status, resultsConsld, rowNum, heading):
    """ Function to Log Results"""
    resultsList = []
    for i in heading:
        if (i in testParams.keys()):
            resultsList.append(testParams[i])
    for j in status:
        resultsList.append(j)
    print(resultsList)
    resultsConsld.worksheet.write_row('A' + str(rowNum), resultsList)
    rowNum = rowNum+1
    return rowNum

def initializeExcelSheet(keyParams):
    """ Function to Initialize PER excel sheet"""
    resultsConsld = ResultsOut()
    resultsConsld.prepareXlsx('WLANPHY.RXCCATestReport.xlsx')
    heading = keyParams
    heading += ['rssiEstimated']
    heading += ['CCA Duration']
    heading += ['TX Time Calculated']
    heading += ['sigStatus']
    heading += ['Result']
    resultsConsld.worksheet.write_row('A1', heading)
    rowNum = 2
    return resultsConsld, heading, rowNum

if __name__ == '__main__':
    main()
    time.sleep(20)