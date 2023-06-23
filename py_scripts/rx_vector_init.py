#-------------------------------------------------------------------------------
# Name:        rx_vector_init.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------

#######################################
# Keep the imports here

import os
import time
import datetime
import DUT_functions
import target_functions
import file_operations
import rxvector_functions

from common_utils import *
from SOCKET_functions import *
from MATLAB_functions import *
#from CSUtils import DA
#from MATLAB_functions import *
from test_mode_functions import *
from datarate_snr_table import *

######################################

def main ():

    # Instantiate the TestConfigParams object
    targetParams = TargetParams()
    testConfigParams = TestConfigParams()

    # Read the test configuration from "WLANPHY.TestConfig.xlsx" excel sheet
    testConfigDict = file_operations.readTestConfigExcel('WLANPHY.TestConfig.xlsx')
    targetParams.updateParams(testConfigDict)
    testConfigParams.updateParams(testConfigDict)

    createDebugLog(testConfigParams)
    debugPrint("=================== RX Vector Initialisation===================")

    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
    DUT_functions.pollSystemReady()  #wait on dutReady

    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)

   # Initialize Socket
    # sock, portNo = socket_init()
    RXresultsConsld = ResultsOut()
    RXresultsConsld.prepareXlsx('WLANPHY.RXfunctionalTestReport.xlsx')

    if (testConfigParams.subFuncTestPlan == 'ALL'):
        #subPlan = ['11B', 'LG', 'MM', 'VHT', 'LDPC', 'SGI', 'LDPC+SGI', 'PayLoad', 'AGG', 'OFDM+DSSS']
        #subPlan = ['LG', 'MM', 'VHT', 'SGI',  'PayLoad', 'OFDM+DSSS', '11B']
        subPlan = ['LG', 'MM', 'VHT', '11B']
        for subTestPlan in subPlan:
            testConfigParams.subFuncTestPlan = subTestPlan
            createSubPlanLog(testConfigParams)
            # Initialize Socket
            sock, portNo = socket_init()
            systemConfig = targetParams.system_config
            #sock = ""
    ##        # Create test cases excel sheets
    ##        #testCasesFilesList = Generate_testcases(testConfigParams)
            DUT_functions.startTestcase()
            test_case_count, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
            # Start the Matlab process
            portNo = sock.getsockname()[1]
            MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
            #MtlbExeProcess = ''
            RXresultsConsld.addSheet(testConfigParams.subFuncTestPlan)
            executeRXP(testConfigParams,targetParams, sock,MtlbExeProcess, testCasesFile, sheetName, test_case_count, RXresultsConsld.worksheet)
            conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
            conn.setblocking(1)
            conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
    else:
        createSubPlanLog(testConfigParams)
        # Initialize Socket
        sock, portNo = socket_init()
        systemConfig = targetParams.system_config
        #sock = ""
##        # Create test cases excel sheets
##        #testCasesFilesList = Generate_testcases(testConfigParams)
        DUT_functions.startTestcase()
        test_case_count, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
        # Start the Matlab process
        portNo = sock.getsockname()[1]
        MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
        #MtlbExeProcess = ''
        RXresultsConsld.addSheet(testConfigParams.subFuncTestPlan)
        executeRXP(testConfigParams,targetParams, sock,MtlbExeProcess, testCasesFile, sheetName, test_case_count, RXresultsConsld.worksheet)
        conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
        conn.setblocking(1)
        conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
    RXresultsConsld.workbook.close()


def executeRXP(testConfigParams, targetParams, sock, MtlbExeProcess, testCasesFile, sheetName, test_case_count, sheet):
    pkt_idx = 1 # To support for multiple packets
    snr_idx = 1
    DUT_RxVector = RxVector()
    while (test_case_count <= testConfigParams.total_test_cases):
        try:
            systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, test_case_count)
            DUT_functions.configSystemParams(systemParams)
            if ('aggregationEnable' in testParams.keys()):
                mpdu_data = file_operations.generatePayload(testParams['packetLength'] - 4, testParams['nMpdu']) # 4 CRC bytes are deducted
            else:
                mpdu_data = file_operations.generatePayload(testParams['packetLength'] - 4, 1) # 4 CRC bytes are deducted

            if (testConfigParams.lna_model_enable == 'NO'):
                memoryType = 'shared'
            else:
                memoryType = 'separate'

            DUT_functions. setPayloadLengthRx(testParams['packetLength'])
            #DUT_functions. setFrameFormatRx(testParams['format'])
            Matlab_input = 'testcaseIdx' + ' ' + str(test_case_count) + ' ' + 'pktIdx' + ' ' + str(pkt_idx)
            dutState = runRxSinglePacket(Matlab_input, test_case_count, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType)
            rxvector_functions.readRxVector (systemParams, DUT_RxVector, testConfigParams, test_case_count)
            rxvectorDict = rxvector_functions.convertRxVectasDict(systemParams, DUT_RxVector)
            pktStatus, edStatus, popCnt, spatialReuseCnt = DUT_functions.getRXStats()
            debugPrint('Packet status is ' + pktStatus)
            if(edStatus > 0):
                edStatus1= 'ED detected'
            else:
                edStatus1= 'ED not detected'

            debugPrint('ED status is ' + edStatus1)

            matlabcrc = readMatlabStatus(testConfigParams, test_case_count, 0)
            if (matlabcrc == 1):
                matlabresult = 'CRC PASS'
            else:
                matlabresult = 'CRC FAIL'

            if (test_case_count == testConfigParams.test_case_start):
                resultsConsld = ResultsOut()
                rxvectorConsld, headingrxvect, rowNumrxvect = rxvector_functions.initRxVectorExcelSheet (rxvectorDict)
                resultsConsld.prepareXlsx('RX_'+ testConfigParams.subFuncTestPlan +'_Results_Consolidated.xlsx')
                heading = keyParams
                heading += ['DUT result', 'MATLAB result', 'ED status']
                resultsConsld.worksheet.write_row('A1', heading)
                sheet.write_row('A1', heading)
                rowNum = 2
            status = [pktStatus, matlabresult, edStatus1]
            file_operations.logRxResults(testParams, status, resultsConsld, rowNum, heading, sheet)
            rxvector_functions.logrxvectResults(rxvectorDict, rxvectorConsld, rowNumrxvect, headingrxvect)
            rowNum += 1
            rowNumrxvect += 1
            if (test_case_count == testConfigParams.total_test_cases):
                resultsConsld.workbook.close()
                rxvectorConsld.workbook.close()
            DUT_functions.clearRxStats()
            # In case DUT process haven't completed succesfuly reload executable before starting next case
            if (dutState == 'DUT_STUCK'):
                target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
                DUT_functions.pollSystemReady()
                DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
                DUT_functions.startTestcase()
        except socket.error as e:
            debugPrint(str(e))
            debugPrint("********************************************************MATLAB Time out in Test Case No. "+str(test_case_count)+" Procceding to next test case ********************************************************************")
            KillSubProcess(MtlbExeProcess)
            portNo = sock.getsockname()[1]
            MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, targetParams.system_config)
            if (test_case_count == testConfigParams.test_case_start):
                resultsConsld = ResultsOut()
                resultsConsld.prepareXlsx('RX_'+ testConfigParams.subFuncTestPlan +'_Results_Consolidated.xlsx')
                heading = keyParams
                ##heading += ['Status']
                heading += ['DUT result', 'MATLAB result', 'ED status']
                resultsConsld.worksheet.write_row('A1', heading)
                sheet.write_row('A1', heading)
                rowNum = 2
            status = ['NA', 'MATLAB STUCK', 'NA']
            file_operations.logRxResults(testParams, status, resultsConsld, rowNum, heading, sheet)
            rowNum += 1
            if (test_case_count == testConfigParams.total_test_cases):
                resultsConsld.workbook.close()
        test_case_count = test_case_count + 1
    pass

if __name__ == '__main__':
    main()
    time.sleep(20)