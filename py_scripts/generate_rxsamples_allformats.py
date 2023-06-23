#-------------------------------------------------------------------------------
# Name:        generate_rxsamples_allformats
# Purpose:     RX IQ sample vector with multiple packets of different frame format
#              and bandwidth etc
#
# Author:      Nordic Semiconductor
#
# Created:     26/03/2021
# Copyright:   (c) Nordic Semiconductor 2021
#-------------------------------------------------------------------------------

#######################################
# Keep the imports here
import time
import datetime
import file_operations

from common_utils import *
from MATLAB_functions import *
from SOCKET_functions import *

######################################
class TestConfigurationParams(object):
    """ This class contains all the test configuration parameters
    required for DUT testing in different scenarios """
    #test_mode           = ''
    test_type           = ''
    subFuncTestPlan     = ''
    dut_operating_mode  = ''
    release             = ''
    lna_model_enable    = ''
    silence_period      = ''

    def updateParams(self,configDict):
        #self.test_mode             = configDict['test_mode']
        self.test_type             = configDict['test_type']
        self.subFuncTestPlan       = configDict['subFuncTestPlan']
        self.dut_operating_mode    = configDict['dut_operating_mode']
        self.release               = configDict['release']
        self.lna_model_enable      = configDict['lna_model_enable']
        self.silence_period        = configDict['silence_period']

def readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, systemConfig, testCaseCount):
    """ Read testcase xlsx and update system params and test params """
    inputFilePath = os.path.abspath('../testcases/' + systemConfig +'/')
    testcases_file = os.path.join(inputFilePath, testCasesFile)
    workbook = xlrd.open_workbook(testcases_file)
    simParamsSheet = workbook.sheet_by_name(sheetName)
    keyParams = simParamsSheet.row_values(0)
    paramsValues = simParamsSheet.row_values(testCaseCount)
    testDict = {keyParams[i]: int(paramsValues[i]) for i in range(len(keyParams))}

    test_cases_list = simParamsSheet.col_values(0) # Read the values in 1st column
    test_case_start = 1 # Starting test case number is 1
    total_test_cases = int(test_cases_list[-1]) # Ending test case number is the last element in the list

    return testDict, total_test_cases


def appendAndWriteRxsamplestoFile(file_adc_out_real, file_adc_out_imag, silence_to_append):
    """ Append noise samples at the end of input samples and write to output file in append mode """
    file_real = open(file_adc_out_real, 'r')
    data_real = []
    data_real = file_real.readlines()
    file_imag = open(file_adc_out_imag, 'r')
    data_imag = []
    data_imag = file_imag.readlines()

    NoiseFileDir = os.path.abspath('../testvectors/noiseFiles/')
    noiseFilePath_real = os.path.join(NoiseFileDir, 'real.txt')
    noiseFilePath_imag = os.path.join(NoiseFileDir, 'imag.txt')
    noise_real = open(noiseFilePath_real,'r')
    noiseSamples_real = noise_real.readlines()
    noise_imag = open(noiseFilePath_imag,'r')
    noiseSamples_imag = noise_imag.readlines()

    data_real.extend(noiseSamples_real[1:silence_to_append])
    data_imag.extend(noiseSamples_imag[1:silence_to_append])

    out_file_real = open('rxsamples_out_real.txt', 'a')
    out_file_imag = open('rxsamples_out_imag.txt', 'a')
    out_file_real.writelines(str(line) for line in data_real)
    out_file_imag.writelines(str(line) for line in data_imag)

    file_real.close()
    file_imag.close()
    out_file_real.close()
    out_file_imag.close()
    noise_real.close()
    noise_imag.close()

def main ():
    '''This file calls matlab executable to run each test case from testcases excel file and
    appends moise samples to each adcOut files generated from matlab, appends all testcases
    to create single IQ sample vector '''
    testConfigParams = TestConfigurationParams()
    subFuncTestPlan = "ALLFORMAT"
    dut_operating_mode = "RX"
    testCasesFile = "testcases_firmwareGen2_ALLFORMAT.xlsx"
    systemConfig = "530_77"
    test_type  = "Gen2"
    testcaseIdx=1
    sheetName="ALLFORMAT"
    release= "All_Results"
    time_out_value = 1200
    silence_period = 200
    testConfigDict = {'test_type' : test_type, 'subFuncTestPlan' : subFuncTestPlan,
                     'dut_operating_mode' : dut_operating_mode, 'release' : release,
                     'lna_model_enable' : 'NO', 'silence_period' : silence_period}

    #initialize debug log file in results folder
    testConfigParams.updateParams(testConfigDict)
    createDebugLog(testConfigParams)
    debugPrint("=================== GENERATION TEST START ===================")

    # Initialize Socket
    sock, portNo = socket_init()

    # Start the Matlab process
    portNo = sock.getsockname()[1]

    testParams, total_test_cases = readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, systemConfig, testcaseIdx)
    MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)

    while (testcaseIdx <= total_test_cases):
        pktIdx=1
        testParams, total_test_cases = readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, systemConfig, testcaseIdx)

        bw = testParams['rxOpBw']
        payloadFileName = "mpdu_payload.txt"
        vectorDumpDir = file_operations.returnSimOutDir (testConfigParams, testcaseIdx)

        payloadData=file_operations.generatePayload(testParams['length'] - 4) # 4 CRC bytes are deducted
        file_operations.writePayloadToFile (payloadData,payloadFileName,testParams['length'] - 4, 1, vectorDumpDir)

        debugPrint("startng test for packet " + str(pktIdx) + ", testCase" + str(testcaseIdx))

        MatlabInput =  'testcaseIdx' + ' ' + str(testcaseIdx) + ' ' + 'pktIdx' + ' ' + str(pktIdx)

        conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
        conn.setblocking(1)
        conn.send(str(Constants.get('START_TESTCASE')[0][0])+ ' ' + MatlabInput)#Give indication from python to MATLAB to start the test case
        debugPrint("Sent the trigger to Matlab to start test case " + str(testcaseIdx))
        sock.settimeout(time_out_value)#Sets the timeout value.
        conn, addr = sock.accept()
        time.sleep(2)
        testCode = conn.recv(1024)

        if (int(testCode) == Constants.get('TESTCASE_COMPLETED')[0][0]):
            debugPrint("Matlab generated input files are ready")
            file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
            noise_to_append = int(silence_period*(2*bw))
            appendAndWriteRxsamplestoFile(file_real, file_imag, noise_to_append)

        testcaseIdx = testcaseIdx + 1

    conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
    conn.setblocking(1)
    conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case

if __name__ == '__main__':
    main()
    time.sleep(20)