#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      amag
#
# Created:     13/02/2023
# Copyright:   (c) amag 2023
# Licence:     <your licence>
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
    numOfPkts = 50
    pktIdx = 1
    parUpdateFromCmd = 1
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
    #resultsConsld, heading, rowNum = initializeExcelSheet (heading, testConfigParams)
    ###################Enable when testing multile test cases###################
    while (testcaseIdx <= testConfigParams.total_test_cases):
        crcPassCnt = 0
        ed_cnt = 0
        matlabCrcCnt = 0
        pktIdx = 1
        per = 0
        excelInit = 1
        matlabstuckCount = 0
        totalErrorsLogged = 23
        totalErrorCount = [0]*totalErrorsLogged
        systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, testcaseIdx)
        caseparams, caseDict, heading1=file_operations.readMatlabXlsx(testCasesFile, testConfigParams.subFuncTestPlan, testcaseIdx)
        if testParams['testEnable'] == 0:
            testcaseIdx += 1
            continue
        DUT_functions.configSystemParams(systemParams)
        payloadFile = "mpdu_payload.txt"
        vectorDumpDir = file_operations.returnSimOutDir (testConfigParams, testcaseIdx)
        mpdu_data=file_operations.generatePayload(testParams['length'] - 4) # 4 CRC bytes are deducted
        file_operations.writePayloadToFile (mpdu_data,payloadFile,testParams['length'] - 4, 1,vectorDumpDir)
        DUT_functions.setPayloadLengthRx(testParams['length'])
        memoryType = 'separate'
        DUT_functions.agcModuleEnable()
        testConfigParams.lna_model_enable = 'YES'
        agcEn  = 1
        #Run RX test for numOfPkts in a loop and log rx stats for each packet.
        while (pktIdx < (numOfPkts+1)):
            playout_functions.configRXPlayoutInputSel()
            debugPrint("startng test for packet " + str(pktIdx) + ", testCase " + str(testcaseIdx))
            Matlab_input = 'testcaseIdx' + ' ' + str(testcaseIdx) + ' ' + 'pktIdx' + ' ' + str(pktIdx) + ' ' + 'firmwareAgcTestEn' + ' ' + str(agcEn) + ' ' + \
            'parUpdateFromCmd'+ ' ' + '1'
            #Same function used from testModeFunctions to run RX for single packet analysis
            dutState = runRxSinglePacket(Matlab_input, testcaseIdx, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType, vectorDumpDir, caseDict)
            if (dutState != 'MATLAB_STUCK'):
                matlabCrcCnt = readMatlabStatus(testConfigParams, testcaseIdx, matlabCrcCnt)
            else: # MATLAB_STUCK occurs
                matlabCrcCnt += 0
                numOfPkts = numOfPkts + 1
                matlabstuckCount += 1

            rxvector_functions.readRxVector (systemParams, DUT_RxVector, testConfigParams, testcaseIdx)
            matrxvectorDict = rxvector_functions.readMatRxVectorasDict(systemParams, testConfigParams, testcaseIdx, DUT_RxVector)
            rxvectorDict, matsigcfoKhz = rxvector_functions.convertRxVectasDict(testConfigParams, systemParams, DUT_RxVector, testParams['operatingBand'], testParams['channelNum'], 0, testParams['format'], matrxvectorDict)
            if (pktIdx == 1) and (excelInit == 1):
                rxvectorConsld, headingrxvect, rowNumrxvect = initPoPPERExcelSheet (heading, rxvectorDict, testcaseIdx)
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

            debugPrint("crc pass cnt " + str(crcPassCnt))
            debugPrint("ED cnt " + str(ed_cnt))
            coreClkCyclesperUs = 80
            adcSamplingrate = 40 << testParams['opBW']
            [ccaDuration, txTimeCalculated, popStatus, finalStatus] = readPopParams(testConfigParams, vectorDumpDir, memoryType, coreClkCyclesperUs, adcSamplingrate, popCnt, caseparams, pktIdx)
            popresult = [crcPassStatus, matlabCrcCnt, edStatus, DUT_RxVector.rssi, ccaDuration, txTimeCalculated, popStatus, finalStatus]
            logPoPResults(caseDict, rxvectorDict, rxvectorConsld, rowNumrxvect, headingrxvect, pktIdx, rx_stats, totalErrorsLogged, popresult)
            DUT_functions.clearRxStats()
            rowNumrxvect += 1
            pktIdx = pktIdx + 1
            if (dutState == 'MATLAB_STUCK'):
                sock, portNo = socket_init()
                portNo = sock.getsockname()[1]
                time.sleep(5)
                MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)

            if pktIdx == numOfPkts+1:
                dutPer, matPer = postPoPProcessing (crcPassCnt, matlabCrcCnt, numOfPkts, matlabstuckCount, caseDict, testConfigParams)
                maindir = os.path.join('../Results/' + testConfigParams.release)
                debugPerPrint("For testcase " + str(testcaseIdx) + ": DUT PER is " + str(dutPer) + " and MATLAB PER is " + str(matPer), maindir)
                rxvectorConsld.workbook.close()
        testcaseIdx = testcaseIdx + 1

    conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
    conn.setblocking(1)
    conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case

def debugPerPrint(string, maindir):
    """ Log the string to debug log file """
    print(string)
    debug_log_file = os.path.join(maindir, 'PER.log')
    #debug_log_file = os.path.join(os.getcwd(), 'debug.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()

def postPoPProcessing (crcPassCnt, matlabCrcCnt, numOfPkts, matlabstuckCount, caseDict, testConfigParams):
    """ Post Processing Function calculate PER and increment/decrement SNR accordingly"""
    numOfPkts = numOfPkts - matlabstuckCount
    crcFailPkts = numOfPkts - crcPassCnt
    per = (crcFailPkts * 100) / numOfPkts
    debugPrint("PER is " + str(per))
    matFailPkts = numOfPkts - matlabCrcCnt
    matPer = (matFailPkts * 100) / numOfPkts
    debugPrint("Matlab PER is " + str(matPer))
    return per, matPer

def readCountersfromPeripheral():
    rx_stats1 = DUT_functions.readRXstatsFromPeripheralRegs()
    rx_stats2 = DUT_functions.readCRCcountsFromPeripheral(rx_stats1)
    rx_stats3 = DUT_functions.readFrameCountersFromPeripheral(rx_stats2)
    rx_stats = DUT_functions.readPoPCountFromPeripheral(rx_stats3)

    return rx_stats

def initPoPPERExcelSheet (keyParams, rxvectorDict, testcaseIdx):
    resultsConsld = ResultsOut()
    resultsConsld.prepareXlsx('WLANPHY.POPTestReport_'+str(testcaseIdx)+'.xlsx')
    heading = ['PktIdx']
    heading += keyParams
    heading += rxvectorDict.keys()
    heading += ['OFDM_CORRELATION_PASS_COUNT', 'LTF_CORRELATION_FAIL_COUNT', 'LSIG_DECODE_FAIL_COUNT', \
                'HT-SIG_DECODE_FAIL_COUNT', 'VHT-SIGA_DECODE_FAIL_COUNT', 'HE-SIGA_DECODE_FAIL_COUNT', \
                'HE-SIGB_DECODE_FAIL_COUNT', 'CRC32PassCount', 'CRC32FailCount', 'CRC8PassCount', 'CRC8FailCount', \
                'LG-FrameCount', 'HT-FrameCount', 'VHT-FrameCount', 'HESU-FrameCount', 'HEERSU-FrameCount', 'HEMU-FrameCount', \
                'Unsupported-FrameCount', 'OtherStaId-FrameCount', 'VHTNDP-FrameCount', 'HESUNDP-FrameCount', 'S2LTimeOutFailCount', \
                'PoPEventCount']
    heading += ['dutpktStatus', 'matlabpktStatus','EDstatus', 'RSSI', 'ccaduration', 'txTime', 'popStatus', 'FinalStatus']
    resultsConsld.worksheet.write_row('A1', heading)
    rowNum = 2

    return resultsConsld, heading, rowNum

def logPoPResults(testParams, rxvectorDict, resultsConsld, rowNum, heading, pktIdx, rx_stats, totalErrorsLogged, popresult):
    resultsList = []
    resultsList.append(pktIdx)
    for i in heading:
        if i in testParams.keys():
            resultsList.append(testParams[i])
    for i in heading:
        if (i in rxvectorDict.keys()):
            resultsList.append(str(rxvectorDict[i]))
    for i in range(totalErrorsLogged):
        resultsList.append(rx_stats[i])
    for i in range(8):
        resultsList.append(popresult[i])
    print(resultsList)
    resultsConsld.worksheet.write_row('A' + str(rowNum), resultsList)

def readPopParams(testConfigParams, vectorDumpDir, memoryType, coreClkCyclesperUs, adcSamplingrate, popCnt, testcaseParams, pktIdx):

    ccaDuration_inclkcycles = DUT_functions.readCCATimerValues()
    ccaDuration = ccaDuration_inclkcycles/coreClkCyclesperUs

    file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
    inputSamples,numSamples = file_operations.readRXSamples(file_real, file_imag, memoryType)
    txTimeCalculated = (numSamples)/(adcSamplingrate)
    if (popCnt == pktIdx):
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