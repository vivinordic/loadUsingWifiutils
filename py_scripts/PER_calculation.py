#-------------------------------------------------------------------------------
# Name:        per_calculation.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------

#######################################
# Keep the imports here
import time
import datetime
import test_mode_functions
import DUT_functions
import target_functions
import file_operations
import rxvector_functions
import argparse
import math

from common_utils import *
from SOCKET_functions import *
from MATLAB_functions import *
from test_mode_functions import *
from datarate_snr_table import *
######################################

PER10 = 10            #10% PER
TOLERENCE = 4
PER10_MAX = PER10+TOLERENCE
PER10_MIN = PER10-TOLERENCE

def main (targetType,
         targetNumber,
         testMode,
         cfgParamFromXls,
         targetSelection,
         subfunctionalTestPlan,
         systemConfiguration,
         testPlanType,
         testAllCases,
         testStartFrom,
         testEndAt,
         testType,
         equipment,
         equipIp):
    """Calculate PER for numOfPkts specified. If PER is within the range sepecified (10%+/-tolerance%), continue to next testcase. Otherwise increment /decrement SNR (SNR+/- SnrStep) and continue to test for same MCS until PER (10%+/-tolernace%) within given tolerance is acheived."""
    totalpkts = 50
    numOfPkts = totalpkts
    pktIdx = 1
    snr_idx = 1
    parUpdateFromCmd = 1
    snrStep = 0.5
    rowNum = 0
    resultsConsld = []
    # Instantiate the TestConfigParams object
    targetParams = TargetParams()
    testConfigParams = TestConfigParams()
    DUT_RxVector = RxVector()

    if(cfgParamFromXls):
    # Read the test configuration from "WLANPHY.TestConfig.xlsx" excel sheet
        testConfigDict = file_operations.readTestConfigExcel('WLANPHY.TestConfig.xlsx')
    else:
        testConfigDict = {}
        testConfigDict.update( {'target_type'         : targetType} )
        testConfigDict.update( {'target_number'       : targetNumber} )
        testConfigDict.update( {'system_config'       : systemConfiguration} )
        testConfigDict.update( {'test_mode'           : testMode} )
        testConfigDict.update( {'target_selection'    : targetSelection} )
        testConfigDict.update( {'test_type'           : testPlanType} )
        testConfigDict.update( {'subFuncTestPlan'     : subfunctionalTestPlan} )
        testConfigDict.update( {'dut_operating_mode'  : testType} )
        testConfigDict.update( {'build_config'        : 'RELEASE'} )
        testConfigDict.update( {'release'             : 'ALL_functional_Results'} )
        testConfigDict.update( {'target'              : testConfigDict['target_type'] + ' ' + testConfigDict['target_number']} )
        testConfigDict.update( {'genTestCasesWithExe' : 'NO'} )
        testConfigDict.update( {'testCasesFileName'   : 'testcases_LG_RX'} )
        testConfigDict.update( {'checkAllTestCases'   : testAllCases} )
        testConfigDict.update( {'test_case_start'     : testStartFrom} )
        testConfigDict.update( {'total_test_cases'    : testEndAt} )
        testConfigDict.update( {'num_pkts'            : 1} )
        testConfigDict.update( {'time_out_value'      : 1200} )

        testConfigDict.update( {'vsg'                 : equipment} )
        testConfigDict.update( {'equip_ip'            : equipIp} )
        testConfigDict.update( {'dutModel'            : 'Harness_SSH'} )

        testConfigDict.update( {'s_no'                : 12} )
        testConfigDict.update( {'date'                : '9/23/2021'} )
        testConfigDict.update( {'codebase'            : 'Calder'} )
        testConfigDict.update( {'cl_no'               : 59034} )
        testConfigDict.update( {'targetname'          : 'image12Dec2021'} )
        testConfigDict.update( {'toolkit'             : '7.3.0'} )
        testConfigDict.update( {'afe'                 : 'RF'} )
        testConfigDict.update( {'matlab'              : '8.3.2'} )
        testConfigDict.update( {'comments'            : 'Test Completed'} )


    targetParams.updateParams(testConfigDict)
    testConfigParams.updateParams(testConfigDict)

    #initialize debug log file in results folder
    createDebugLog(testConfigParams)
    debugPrint("=================== PER TEST START ===================")
    createSubPlanLog(testConfigParams)
    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
    #Check whether Harness has reached master wait
    DUT_functions.pollSystemReady()  #wait on dutReady

    #Set DUT operating mode RX/TX/LOOPBACK
    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)

   # Initialize Socket
    sock, portNo = socket_init()
    systemConfig = targetParams.system_config

    #Give Test Start indication to DUT
    DUT_functions.startTestcase()
    testcaseIdx, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
    # Start the Matlab process
   # caseparams, heading=file_operations.readMatlabXlsx(testCasesFile, testConfigParams.subFuncTestPlan, testcaseIdx)
    caseparams, caseDict, heading=file_operations.readMatlabXlsx(testCasesFile, testConfigParams.subFuncTestPlan, testcaseIdx)
    portNo = sock.getsockname()[1]
    MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
    systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, testcaseIdx)
    resultsConsld, heading, rowNum = initializeExcelSheet (heading, testConfigParams)
    ###################Enable when testing multile test cases###################
    while (testcaseIdx <= testConfigParams.total_test_cases):
        crcPassCnt = 0
        ed_cnt = 0
        matlabCrcCnt = 0
        pktIdx = 1
        per = 0
        excelInit = 1
        snr = -100
        iterationpertestcase = 1
        matlabstuckCount = 0
        snrArray = []
        totalCFOArray = []
        totalErrorsLogged = 23
        totalErrorCount = [0]*totalErrorsLogged
        systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, testcaseIdx)
        caseparams, caseDict, heading1=file_operations.readMatlabXlsx(testCasesFile, testConfigParams.subFuncTestPlan, testcaseIdx)
        if testParams['testEnable'] == 0:
            testcaseIdx += 1
            continue

        if testConfigParams.subFuncTestPlan == 'CFOMeasurements':
            snr = caseDict['snrdB']
        else:
            #Select snrdb and mcs table corresponding to sub-fucnitonal test plan.
            SNR_DB_TABLE=SNR_DB_TABLE_IN[testConfigParams.subFuncTestPlan]
            #select mcs value corresponding to datarate from the table to test PER
            for data in SNR_DB_TABLE:
                if int(caseparams[1])==6 and int(caseparams[9])!=192:
                    if data[0]==int(testParams['mcs'][3*(testParams['desiredStaId']-1)]):
                        snr = data[1]
                else:
                    if data[0]==int(testParams['mcs']):
                        snr = data[1]
            if snr==-100:
                debugPrint("MCS not Found\n")
                return
        #Array to Log snr values to check for duplicates
        snrArray= [snr]
        DUT_functions.configSystemParams(systemParams)
        payloadFile = "mpdu_payload.txt"
        vectorDumpDir = file_operations.returnSimOutDir (testConfigParams, testcaseIdx)
        mpdu_data=file_operations.generatePayload(testParams['length'] - 4) # 4 CRC bytes are deducted
        file_operations.writePayloadToFile (mpdu_data,payloadFile,testParams['length'] - 4, 1,vectorDumpDir)
        DUT_functions.setPayloadLengthRx(testParams['length'])
        DUT_functions.setFrameFormatRx(testParams['format'])
        if(testConfigParams.subFuncTestPlan == 'AGC') or (testConfigParams.subFuncTestPlan == 'SECONDAGC') :
            memoryType = 'separate'
            DUT_functions.agcModuleEnable()
            testConfigParams.lna_model_enable = 'YES'
            agcEn  = 1
        else:
            memoryType = 'shared'
            DUT_functions.agcModuleDisbale()
            testConfigParams.lna_model_enable = 'NO'
            agcEn  = 0
        #Run RX test for numOfPkts in a loop and log rx stats for each packet.
        while (pktIdx < (numOfPkts+1)):
            if(iterationpertestcase > 10):
                resultsConsldAllSnr.workbook.close()
                break
            playout_functions.configRXPlayoutInputSel()
            debugPrint ("Snr is " + str(snr))
            debugPrint("startng test for packet " + str(pktIdx) + ", testCase " + str(testcaseIdx))
            #MatlabInput = str(testcaseIdx) + ' ' + str(pktIdx) + ' ' + str(snr_idx)
            #MatlabInput = str(testcaseIdx) + ' ' + str(pktIdx) + ' '+ str(parUpdateFromCmd) +  ' ' + str(snr)
            Matlab_input = 'testcaseIdx' + ' ' + str(testcaseIdx) + ' ' + 'pktIdx' + ' ' + str(pktIdx) + ' ' + 'firmwareAgcTestEn' + ' ' + str(agcEn) + ' ' + \
            'parUpdateFromCmd'+ ' ' + '1' +  ' ' + 'snrdB' + ' ' + str(snr)
            #Same function used from testModeFunctions to run RX for single packet analysis
            dutState = runRxSinglePacket(Matlab_input, testcaseIdx, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType, vectorDumpDir, caseDict)
            if (dutState != 'MATLAB_STUCK'):
                removeOutputFiles (testConfigParams, vectorDumpDir)
                matlabCrcCnt = readMatlabStatus(testConfigParams, testcaseIdx, matlabCrcCnt)
            else: # MATLAB_STUCK occurs
                matlabCrcCnt += 0
                numOfPkts = numOfPkts + 1
                matlabstuckCount += 1

            rxvector_functions.readRxVector (systemParams, DUT_RxVector, testConfigParams, testcaseIdx)
            matrxvectorDict = rxvector_functions.readMatRxVectorasDict(systemParams, testConfigParams, testcaseIdx, DUT_RxVector)
            rxvectorDict, matsigcfoKhz = rxvector_functions.convertRxVectasDict(testConfigParams, systemParams, DUT_RxVector, testParams['operatingBand'], testParams['channelNum'], snr, testParams['format'], matrxvectorDict)
            total_cfoInKhz, matcfoKhz = DUT_functions.calculateTotalCFO(testConfigParams, rxvectorDict['cfoAfterConversion'], testParams['operatingBand'], testParams['channelNum'], testParams['format'], matrxvectorDict, matsigcfoKhz)
            totalCFOArray.append(total_cfoInKhz)
            if (pktIdx == 1) and (excelInit == 1):
                rxvectorConsld, headingrxvect, rowNumrxvect = rxvector_functions.initRxVectorExcelSheet (rxvectorDict, testcaseIdx)
                resultsConsldAllSnr, headingAllSnr, rowNumAllSnr = initializeExcelSheetAllSnr (heading, testcaseIdx)
            #Read RX Statistics
            crcPassStatus, edStatus, popCnt, spatialReuseCnt = DUT_functions.getRXStats ()
            if (crcPassStatus == 'OFDM PACKET CRC_PASS') or (crcPassStatus == 'DSSS PACKET CRC_PASS'):
                status = 1
            else:
                status = 0
            crcPassCnt = crcPassCnt + status
            ed_cnt = ed_cnt + edStatus
            rx_stats = readCountersfromPeripheral()
            print(rx_stats)
            for i in range(totalErrorsLogged):
                totalErrorCount[i] = totalErrorCount[i] + rx_stats[i]
            print(totalErrorCount)
            DUT_functions.clearRxStats()
            debugPrint("crc pass cnt " + str(crcPassCnt))
            debugPrint("ED cnt " + str(ed_cnt))
            rxvector_functions.logrxvectResults(rxvectorDict, rxvectorConsld, rowNumrxvect, headingrxvect, total_cfoInKhz, pktIdx, rx_stats, totalErrorsLogged, matcfoKhz)
            rowNumrxvect += 1
            pktIdx = pktIdx + 1
            if (dutState == 'MATLAB_STUCK'):
                sock, portNo = socket_init()
                portNo = sock.getsockname()[1]
                time.sleep(5)
                MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)

            if pktIdx == numOfPkts+1:
                dutPer, matPer, snr_new, status = postProcessing (snr, snrStep, crcPassCnt, matlabCrcCnt, numOfPkts, matlabstuckCount, caseDict, testConfigParams)
                snrArray.append(snr_new)
                print(totalCFOArray)
                totalCFOMean, totalCFOstd = DUT_functions.calculateMeanAndStd(totalCFOArray, totalpkts)
                fixedcfo = caseDict['fixedCfoInKHz']
                cfoStatus = 'PASS'
                if abs(totalCFOMean-fixedcfo) > 0.10:
                    cfoStatus = 'FAIL'
                if totalCFOstd > 0.15:
                    cfoStatus = 'FAIL'
                rowNumAllSnr = reportPreparation (caseDict, snr, dutPer, matPer, resultsConsldAllSnr, rowNumAllSnr, headingAllSnr, totalCFOMean, totalCFOstd, cfoStatus, totalErrorCount, totalErrorsLogged)
                if status == 1:
                     #Check if already tested SNR is added again to the current array. This occurs when PER is not inside the permitted (10%+/-tolerance%) range and SNR toggles between two consecutive values.
                     duplicateSnrTest = checkForDuplicates(snrArray)
                     if duplicateSnrTest:
                        rxvectorConsld.workbook.close()
                        resultsConsldAllSnr.workbook.close()
                        if dutPer<=PER10_MAX:
                            rowNum = reportPreparation (caseDict, snr, dutPer, matPer, resultsConsld, rowNum, heading , totalCFOMean, totalCFOstd, cfoStatus, totalErrorCount, totalErrorsLogged)
                        else:
                            rowNum = reportPreparation (caseDict, snr_new, old_dutPer, old_matPer, resultsConsld, rowNum, heading, totalCFOMean, totalCFOstd, cfoStatus, totalErrorCount, totalErrorsLogged)
                     else:
                        snr = snr_new
                        old_dutPer = dutPer
                        old_matPer = matPer
                        pktIdx = 1
                        excelInit = 0
                        crcPassCnt = 0
                        matlabCrcCnt = 0
                        matlabstuckCount = 0
                        totalCFOArray = []
                        totalErrorCount = [0]*totalErrorsLogged
                        numOfPkts = totalpkts
                        iterationpertestcase += 1
                        continue
                else:
                    rxvectorConsld.workbook.close()
                    resultsConsldAllSnr.workbook.close()
                    rowNum = reportPreparation (caseDict, snr_new, dutPer, matPer, resultsConsld, rowNum, heading, totalCFOMean, totalCFOstd, cfoStatus, totalErrorCount, totalErrorsLogged)
        testcaseIdx = testcaseIdx + 1

    conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
    conn.setblocking(1)
    conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
    resultsConsld.workbook.close()

def initializeExcelSheet(keyParams, testConfigParams):
    """ Function to Initialize PER excel sheet"""
    resultsConsld = ResultsOut()
    resultsConsld.prepareXlsx('WLANPHY.RXPerTestReport.xlsx')
    heading = keyParams
    heading += ['DUT PER']
    heading += ['MATLAB PER']
    heading += ['SNR']
    heading += ['TotalCFOMean']
    heading += ['TotalCFOStdDeviation']
    heading += ['CfoStatus']
    heading += ['OFDM_CORRELATION_PASS_COUNT', 'LTF_CORRELATION_FAIL_COUNT', 'LSIG_DECODE_FAIL_COUNT', \
                'HT-SIG_DECODE_FAIL_COUNT', 'VHT-SIGA_DECODE_FAIL_COUNT', 'HE-SIGA_DECODE_FAIL_COUNT', \
                'HE-SIGB_DECODE_FAIL_COUNT', 'CRC32PassCount', 'CRC32FailCount', 'CRC8PassCount', 'CRC8FailCount', \
                'LG-FrameCount', 'HT-FrameCount', 'VHT-FrameCount', 'HESU-FrameCount', 'HEERSU-FrameCount', 'HEMU-FrameCount', \
                'Unsupported-FrameCount', 'OtherStaId-FrameCount', 'VHTNDP-FrameCount', 'HESUNDP-FrameCount', 'S2LTimeOutFailCount', \
                'PoPEventCount']
    resultsConsld.worksheet.write_row('A1', heading)
    rowNum = 2
    return resultsConsld, heading, rowNum

def initializeExcelSheetAllSnr (keyParams, testcaseIdx):
    resultsConsld = ResultsOut()
    outFile = 'WLANPHY.RXSNRReport_'+str(testcaseIdx)+'.xlsx'
    resultsConsld.prepareXlsx(outFile)
    heading = keyParams
    resultsConsld.worksheet.write_row('A1', heading)
    rowNum = 2
    return resultsConsld, heading, rowNum


def logResults(testParams, snr, dutper, matPer, resultsConsld, rowNum, heading, totalCFOMean, totalCFOstd, finalStatus, totalErrorCount, totalErrorsLogged):
    """ Function to Log Results"""
    resultsList = []
    for i in heading:
        if i in testParams.keys():
            resultsList.append(testParams[i])
    resultsList.append(dutper)
    resultsList.append(matPer)
    resultsList.append(snr)
    resultsList.append(totalCFOMean)
    resultsList.append(totalCFOstd)
    resultsList.append(finalStatus)
    for i in range(totalErrorsLogged):
        resultsList.append(totalErrorCount[i])
    print(resultsList)
    resultsConsld.worksheet.write_row('A' + str(rowNum), resultsList)

def checkForDuplicates(snrArray):
    """ Function to check duplicate SNR and return 0 or 1 accordingly"""
    if len(snrArray) == len(set(snrArray)):
        return 0
    else:
        return 1

def postProcessing (snr, snrStep, crcPassCnt, matlabCrcCnt, numOfPkts, matlabstuckCount, caseDict, testConfigParams):
    """ Post Processing Function calculate PER and increment/decrement SNR accordingly"""
    numOfPkts = numOfPkts - matlabstuckCount
    crcFailPkts = numOfPkts - crcPassCnt
    per = (crcFailPkts * 100) / numOfPkts
    debugPrint("PER is " + str(per))
    matFailPkts = numOfPkts - matlabCrcCnt
    matPer = (matFailPkts * 100) / numOfPkts
    debugPrint("Matlab PER is " + str(matPer))
    if per < PER10_MAX and per > PER10_MIN:
        status = 0
    elif per <= (PER10_MIN):
        snr = snr - snrStep
        status = 1
    elif per >= (PER10_MAX):
        snr = snr + snrStep
        status = 1
    if (testConfigParams.subFuncTestPlan == 'CFOMeasurements'): #To test for single SNR only.
        snr = caseDict['snrdB']
        status = 0
    return per, matPer, snr, status

def reportPreparation (testParams, snr, dutper, matPer, resultsConsld, rowNum, heading, totalCFOMean, totalCFOstd, finalStatus, totalErrorCount, totalErrorsLogged):
    """ Function to call for report preparation to log all final values into excel sheet"""
    logResults(testParams, snr, dutper, matPer, resultsConsld, rowNum, heading, totalCFOMean, totalCFOstd, finalStatus, totalErrorCount, totalErrorsLogged)
    rowNum += 1
    return rowNum

def removeOutputFiles(testConfigParams, vectorDumpDir):
    file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
    os.remove(file_real)
    os.remove(file_imag)
    file_agc_in_real = os.path.join(vectorDumpDir, 'rf1InputReal.txt')
    file_agc_in_imag = os.path.join(vectorDumpDir, 'rf1InputImag.txt')
    cfofile = os.path.join(vectorDumpDir, 'cfoEstParams.txt')
    os.remove(file_agc_in_real)
    os.remove(file_agc_in_imag)

def readCountersfromPeripheral():
    rx_stats1 = DUT_functions.readRXstatsFromPeripheralRegs()
    rx_stats2 = DUT_functions.readCRCcountsFromPeripheral(rx_stats1)
    rx_stats3 = DUT_functions.readFrameCountersFromPeripheral(rx_stats2)
    rx_stats = DUT_functions.readPoPCountFromPeripheral(rx_stats3)

    return rx_stats


if __name__ == '__main__':

    # Argument parser
    parser = argparse.ArgumentParser()

    # Target type used used
    parser.add_argument(
        "--targetType", "-t",
        choices = ['Simulator'    ,
                   'SysProbe'    ],
        help    = "Target type. eg.",
        default = "Simulator"
    )

    # Target number
    parser.add_argument(
        "--targetNumber", "-n",
        help    = "Target number.",
        default = "rpusim-rpu530-main@172-internal_config0077"
    )

    # System Configuration
    parser.add_argument(
        "--systemConfiguration", "-s",
        choices = ['530_49',
                   '530_77'],
        help    = "System Configuration.\neg.",
        default = '530_77'
    )


    # Test mode used
    parser.add_argument(
        "--testMode", "-m",
        choices = ['PLAYOUT',
                   'RF'],
        help    = "Test mode",
        default = 'PLAYOUT'
    )

    # Target selection
    parser.add_argument(
        "--targetSelection", "-ts",
        choices = ['MCU'    ,
                   'MCU2'    ],
        help    = "Target Selection. eg.",
        default = 'MCU'
    )


    # Test plan type.
    parser.add_argument(
        "--testPlanType",
        choices = ['CHARACTERIZATION',
                   'Sanity'          ,
                   'Functional'      ,
                   'LATENCY'         ,
                   'HARDWARE'        ,
                   'REALTIME'        ,
                   'Gen2'            ,
                   'Per'             ],
        help    = "Test plan type.",
        default = 'Gen2'
    )


    # Sub functional test plan
    parser.add_argument(
        "--subfunctionalTestPlan",
        choices = ['ALL'                           ,
                   'LG'                            ,
                   'MM'                            ,
                   'VHT'                           ,
                   '11B'                           ,
                   'STBC'                          ,
                   'HESU'                          ,
                   'HEERSU'                        ,
                   'LDPC'                          ,
                   'NOISY'                         ,
                   'LDPC+SGI'                      ,
                   'CFO+SFO'                       ,
                   'AGG'                           ,
                   'SGI'                           ,
                   'PayLoad'                       ,
                   'OFDM+DSSS'                     ,
                   'HEPAYLOAD'                     ,
                   'HESTBC'                        ,
                   'HELDPC'                        ,
                   'HETB'                          ,
                   'HEMU'                          ,
                   'AGC'                           ,
                   'SECONDAGC'                     ,
                   'RADAR'                         ,
                   'Negative'                      ,
                   'PER'                           ,
                   'SENSITIVITY'                   ,
                   'SENSITIVITY_ACROSS_CHANNELS'   ,
                   'SNR'                           ,
                   'SNR_HE'                        ,
                   'EVM'                           ,
                   'RX_FUNCTIONAL'                 ,
                   'INTERFERENCE_DETECTION'        ,
                   'MIDPACKET_DETECTION'           ,
                   'ACI'                           ,
                   'AACI'                          ,
                   'RX_JAMMER'                     ,
                   'TX_SUBBAND'                    ,
                   'PER_HE'                        ,
                   'SENSITIVITY_HE'                ,
                   'EVM_HE'                        ,
                   'SJR'                           ,
                   'SJR_HE'                        ,
                   'SUBSET'                        ,
                   'CCA'                           ,
                   'CCADISC'                       ,
                   'CCACOMBINED'                   ,
                   'CFOMeasurements'               ,
                   'CFO+SFO-DSSS'                  ,
                   'CFO-SFO-PRE-COMP'             ],
        help    = "Subfunctional test paln.",
        default = 'LG'
    )


    # Test type
    parser.add_argument(
        "--testType",
        choices = ['RX'             ,
                   'TX'            ],
        help    = "Test Type",
        default = 'RX'
    )


    # equipment type
    parser.add_argument(
        "--equipment",
        choices = ['IQXEL_80'             ,
                   'IQXEL_280'            ,
                   'RnS'                 ],
        help    = "Test Type",
        default = 'IQXEL_80'
    )

    # equipment ip
    parser.add_argument(
        "--equipIp", "-ip",
        help    = "Equipment ip.",
        default = "10.90.2.15"
    )

    # Test all cases
    parser.add_argument('--testAllCases',
                        dest='testAllCases',
                        action='store_true')
    parser.add_argument('--no-testAllCases',
                        dest='testAllCases',
                        action='store_false')
    parser.set_defaults(testAllCases=True)

    # Config Params from Xlsx
    parser.add_argument('--cfgParamFromXls',
                        dest='cfgParamFromXls',
                        action='store_true')
    parser.add_argument('--no-cfgParamFromXls',
                        dest='cfgParamFromXls',
                        action='store_false')
    parser.set_defaults(cfgParamFromXls=True)


    # Test start
    parser.add_argument(
        "--testStartFrom",
        help    = "Test start from.",
        default = "1"
    )


    # Test End
    parser.add_argument(
        "--testEndAt",
        help    = "Test End at.",
        default = "1"
    )

    args = parser.parse_args()
    print(args)

    if (args.testAllCases):
        testAll = 'YES'
    else:
        testAll = 'NO'

    main(args.targetType,
         args.targetNumber,
         args.testMode,
         args.cfgParamFromXls,
         args.targetSelection,
         args.subfunctionalTestPlan,
         args.systemConfiguration,
         args.testPlanType,
         testAll,
         int(args.testStartFrom),
         int(args.testEndAt),
         args.testType,
         args.equipment,
         args.equipIp)

    # This sleep time is an attempt to release the simulator before the
    # next test.
    time.sleep(20)