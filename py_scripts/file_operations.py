#-------------------------------------------------------------------------------
# Name:        file_operations.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------
""" file read and write functions goes here """

########################################
import xlrd
import xlsxwriter
import shutil

from math import log
from common_utils import *
#from CSUtils import DA
from datetime import datetime
###########################################

def readTestConfigExcel( test_config_xlsx='WLANPHY.TestConfig.xlsx'):
    """This function reads the test config parameters from WLANPHY.TestConfig.xlsx file"""

    inputFilePath = os.path.abspath('../test_config/')
    file_name = os.path.join(inputFilePath, test_config_xlsx)
    workbook = xlrd.open_workbook(file_name)

    # Read the common Params from the workbook
    commonParamsSheet = workbook.sheet_by_name('commonParams')
    commonParamsCells = commonParamsSheet.col_slice(colx=1, start_rowx=1) # Read from 2nd row, 2nd column onwards
    commonParamsList = []
    testConfigDict = {}
    for cell in commonParamsCells:
        commonParamsList.append(cell.value)
    index = 0
    testConfigDict.update( {'target_type' : commonParamsList[index]} ); index += 1
    # Target Number is not always a number. For local simulators, it is a string.
    # The numbers in excel sheet will be raed as floating point values. Hence convert them to int and then to str.
    try:
        testConfigDict.update( {'target_number' : str(int(commonParamsList[index]))} ) # For DA-Simulators / DA-net Targets.
    except:
        testConfigDict.update( {'target_number' : commonParamsList[index]} ) # For local Simulators
    index += 1
    testConfigDict.update( {'system_config'    : commonParamsList[index]} ) ; index += 1         # System Configuration: Ex: 530_49
    testConfigDict.update( {'test_mode'        : commonParamsList[index]} ) ; index += 1         # Ex: RF | PLAYOUT
    testConfigDict.update( {'target_selection' : commonParamsList[index]} ) ; index += 1         # to select MCU or MCU2
    testConfigDict.update( {'test_type'        : commonParamsList[index]} ) ; index += 1         # Test plan type, Ex: SANITY | FUNCTIONAL | PER | CAPTURE | NOISE CAPTURE
    testConfigDict.update( {'subFuncTestPlan'  : commonParamsList[index]} ) ; index += 1         # Ex: LG | HT-MM | HT-GF | VHT | ALL
    testConfigDict.update( {'dut_operating_mode' : commonParamsList[index]} ); index += 1        # Harness test type, Ex: TX|RX|LOOP_BACK
    testConfigDict.update( {'build_config'     : commonParamsList[index].lower()} ) ; index += 1 # Ex: debug | test | release
    testConfigDict.update( {'release'          : commonParamsList[index]} ); index += 1          # Results/Dumps Folder Name
    testConfigDict.update( {'target'           : testConfigDict['target_type'] + ' ' + testConfigDict['target_number']} )
#PHY_PERFORMANCE:  release can be replaced with results_folder
    if( (testConfigDict['test_mode'] == 'RF') and (testConfigDict['target_type'] == 'Simulator')):
        printStr = 'RF/BASEBAND mode configuration doesn\'t work with simulator.\n ' + \
        'Please choose proper target and proper test mode ( RF / PLAYOUT )'
        debugPrint(printStr)
        exit(1)

    debugiqParamsSheet = workbook.sheet_by_name('testParams')
    debugiqParamsCells = debugiqParamsSheet.col_slice(colx=1,start_rowx=1) # Read from 2nd row, 2nd column onwards
    debugiqParamsList  =[]
    for cell in debugiqParamsCells:
        debugiqParamsList.append(cell.value)
    index = 0;
    testConfigDict.update( {'genTestCasesWithExe' : debugiqParamsList[index]} );      index += 1 # Generate test cases with executable? YES | NO
    testConfigDict.update( {'testCasesFileName'   : debugiqParamsList[index]} );      index += 1 # Generate test cases with executable? YES | NO
    testConfigDict.update( {'checkAllTestCases'   : debugiqParamsList[index]} );      index += 1 # Check all test cases in excel sheet? YES | NO
    testConfigDict.update( {'test_case_start'     : int(debugiqParamsList[index])} ); index += 1 # test case start
    testConfigDict.update( {'total_test_cases'    : int(debugiqParamsList[index])} ); index += 1 # test case end
    testConfigDict.update( {'num_pkts'            : int(debugiqParamsList[index])} ); index += 1 # Num of Packets in each test case
    testConfigDict.update( {'time_out_value'      : int(debugiqParamsList[index])} ); index += 1 # Time out value for MATLAB result (DEBUGIQ case)

    dutParamsSheet = workbook.sheet_by_name('dutParams')
    dutParamsCells = dutParamsSheet.col_slice(colx=1, start_rowx=1) # Read from 2nd row, 2nd column onwards
    dutParamsList = []
    for cell in dutParamsCells:
        dutParamsList.append(cell.value)
    index = 0

    testConfigDict.update( {'vsg'           : dutParamsList[index]} ); index += 1 # test case end
    testConfigDict.update( {'equip_ip'      : dutParamsList[index]} ); index += 1 # Num of Packets in each test case
    testConfigDict.update( {'dutModel'      : dutParamsList[index]} ); index += 1 # Time out value for MATLAB result (DEBUGIQ case)

    RevParamsSheet = workbook.sheet_by_name('RevParams')
    RevParamsCells = RevParamsSheet.col_slice(colx=1, start_rowx=1) # Read from 2nd row, 2nd column onwards
    RevParamsList = []
    for cell in RevParamsCells:
        RevParamsList.append(cell.value)
    index = 0

    testConfigDict.update( {'s_no'           : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'date'           : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'codebase'       : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'cl_no'          : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'targetname'     : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'toolkit'        : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'afe'            : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'matlab'         : RevParamsList[index]} ); index += 1
    testConfigDict.update( {'comments'       : RevParamsList[index]} ); index += 1


    return testConfigDict

def readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, testCaseCount):
    """ Read testcase xlsx and update system params and test params """
    global vectorDumpDir
    if (platform=='linux' or platform=='linux2'):
        vectorDumpDir = os.path.join('../matlab_exe_lin/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    else:
        vectorDumpDir = os.path.join('../matlab_exe_win/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)

    subDir2 = 'testcase_' + '{0:05d}'.format(testCaseCount)
    vectorDumpDir = os.path.join(vectorDumpDir, subDir2)
    if os.path.exists(vectorDumpDir):
        shutil.rmtree(vectorDumpDir)

    workbook = xlrd.open_workbook(testCasesFile)
    simParamsSheet = workbook.sheet_by_name(sheetName)
    keyParams = simParamsSheet.row_values(0)
    paramsValues = simParamsSheet.row_values(testCaseCount)
    testDict = {}
    # If paramsValues defined as string in test case excel sheet,
    # paramsValues comes as unicode so read parameters as a string itself.
    # If not, parameters are converted into integer and stored as keyParams.
    for i in range(len(keyParams)):
        if (type(paramsValues[i]) == unicode):
            testDict.update({keyParams[i]: (paramsValues[i]) })
        else:
            testDict.update({keyParams[i]: int(paramsValues[i])})

    sysParams = SystemParams()
    sysParams.updateParams(testDict,testConfigParams)
    return sysParams, testDict, keyParams

def readMatlabXlsx(testCasesFile, sheet, testCaseCount):
    workbook = xlrd.open_workbook(testCasesFile)
    simParamsSheet = workbook.sheet_by_name(sheet)
    keyParams = simParamsSheet.row_values(0)
    paramsValues = simParamsSheet.row_values(testCaseCount)
    caseDict = {}
    # If paramsValues defined as string in test case excel sheet,
    # paramsValues comes as unicode so read parameters as a string itself.
    # If not, parameters are converted into integer and stored as keyParams.
    for i in range(len(keyParams)):
        if (type(paramsValues[i]) == unicode):
            caseDict.update({keyParams[i]: (paramsValues[i]) })
        else:
            caseDict.update({keyParams[i]: int(paramsValues[i])})
    return paramsValues, caseDict, keyParams

def returnSimOutDir (testConfigParams, testCaseCount):

    if (platform=='linux' or platform=='linux2'):
        vectorDumpDir = os.path.join('../matlab_exe_lin/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    else:
        vectorDumpDir = os.path.join('../matlab_exe_win/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)

    subDir2 = 'testcase_' + '{0:05d}'.format(testCaseCount)
    vectorDumpDir = os.path.join(vectorDumpDir, subDir2)

    return vectorDumpDir

def selectOutputFile (testConfigParams, vectorDumpDir):

    inputFilePath = vectorDumpDir
    if (testConfigParams.lna_model_enable == 'YES'):
        file_adc_out_real = os.path.join(inputFilePath, 'rf1InputReal.txt')
        file_adc_out_imag = os.path.join(inputFilePath, 'rf1InputImag.txt')
    else:
        file_adc_out_real = os.path.join(inputFilePath, 'adc1OutputReal.txt')
        file_adc_out_imag = os.path.join(inputFilePath, 'adc1OutputImag.txt')

    return file_adc_out_real, file_adc_out_imag

def readRXSamples(file_adc_out_real, file_adc_out_imag, memoryType):
    """" Read RX input samples from file """

    file_real = open(file_adc_out_real, 'r')
    data_real = []
    data_real = file_real.readlines()
    file_imag = open(file_adc_out_imag, 'r')
    data_imag = []
    data_imag = file_imag.readlines()
    s_index = 0
    count1 = 0
    count2 = 0
    scp_in_int = []

    if(memoryType == 'shared'):
        for s_index in range(len(data_real)):
            temp_scp_in = int(data_real[s_index][0:3] + '0' + data_imag[s_index][0:3] + '0', 16)
            scp_in_int.append(temp_scp_in)
    else:
        for s_index in range(len(data_real)*2):
            if(s_index%2==0):
                temp_scp_in = int(data_real[count1][0:5]+'000', 16)<<1
                count1=count1+1
            elif (s_index%2==1):
                temp_scp_in = int(data_imag[count2][0:5]+'000', 16)<<1
                count2=count2+1
            scp_in_int.append(temp_scp_in)

    file_real.close()
    file_imag.close()

    return scp_in_int, len(data_real)

def removeSilence(removeSilenceSamples, inputSamples, memoryType):
    #multiply by 2 is required I&Q samples stored in the separate memory
    silence_to_remove = removeSilenceSamples*2
    if(memoryType == 'separate'):
        inputSamples = inputSamples[silence_to_remove:]
    return inputSamples, len(inputSamples)/2



def addSilence(adcSamplingrate, silenceTime, inputSamples, memoryType):

    silence_to_append = silenceTime * adcSamplingrate

    if(memoryType == 'shared'):
        inputSamples += silence_to_append*[0]
    else:
        inputSamples += (silence_to_append*2)*[0]

    return inputSamples, silence_to_append

def calcSilence(vectorDumpDir,file1, file2, adcSamplingrate):

    inputFilePath = vectorDumpDir

    file_agc_out = os.path.join(inputFilePath, file1)
    file_adc_out = os.path.join(inputFilePath, file2)

    file_agc = open(file_agc_out, 'r')
    data_agc = file_agc.readlines()
    file_adc = open(file_adc_out, 'r')
    data_adc = file_adc.readlines()

    sampleDiff = len(data_agc) - len(data_adc)
    silenceTime = (sampleDiff/adcSamplingrate)

    file_agc.close()
    file_adc.close()

    return(silenceTime)

def computeNumTestcases(testConfigParams, systemConfig):
    """ reads testcase xlsx to know the test bench how many test cases to run """
    inputFilePath = os.path.abspath('../testcases/' + systemConfig +'/')
    testCasesFile = 'testcases_firmware' + testConfigParams.test_type + '_' + \
    testConfigParams.subFuncTestPlan + '.xlsx'
    sheetName = testConfigParams.subFuncTestPlan + '_' + testConfigParams.dut_operating_mode
    testcases_file = os.path.join(inputFilePath, testCasesFile)
    workbook = xlrd.open_workbook(testcases_file)
    testcases_xlsx_str = 'Using ' + testCasesFile + ' file for testing.'
    debugPrint(testcases_xlsx_str)
    simParamsSheet = workbook.sheet_by_name(sheetName)

    # To run all the test cases in the excel sheet:
    if (testConfigParams.checkAllTestCases == 'YES'):
        test_cases_list = simParamsSheet.col_values(0) # Read the values in 1st column
        test_case_start = 1 # Starting test case number is 1
        testConfigParams.test_case_start = test_case_start #Updates the DUT Config Params
        total_test_cases = int(test_cases_list[-1]) # Ending test case number is the last element in the list
        testConfigParams.total_test_cases=total_test_cases
    else:
        test_case_start = testConfigParams.test_case_start
        total_test_cases = testConfigParams.total_test_cases
    test_case_count = test_case_start #Initialzes the test count
    testcase_str = '###*** Running from test case ' + str(test_case_start) + ' to ' + str(total_test_cases) + ' ***###'
    debugPrint(testcase_str)

    return test_case_count, testcases_file, sheetName

def dumpTXOutSamples(outBuffer, samples2Read, testConfigParams):
    """ Dump capture memory samples to text file """

    outFilePath = vectorDumpDir

    if not os.path.exists(outFilePath):
        os.makedirs(outFilePath)

    outFileReal =  os.path.join(outFilePath, "txscp_output_real.txt")
    outFileImag =  os.path.join(outFilePath, "txscp_output_imag.txt")
    foReal = open(outFileReal, "w")
    foImag = open(outFileImag, "w")
    for index in range(0,samples2Read):
        samplesOutReal = (outBuffer[index]>>20)
        samplesOutImag = ((outBuffer[index]>>4) & 0xfff)
        foReal.write('%03X\n' %samplesOutReal)
        foImag.write('%03X\n' %samplesOutImag)

    foReal.close()
    foImag.close()

def dumpFeedSamples(outBuffer, samples2Read):
    """ Dump feed samples to text file """

    outFileFeed =  "feed_output.txt"
    foReal = open(outFileFeed, "w")
    for index in range(0,samples2Read):
        samplesOutReal = (outBuffer[index] >> 4) & 0xff
        foReal.write('%02X\n' %samplesOutReal)
        samplesOutReal = ((outBuffer[index] >> 12) & 0xf) + ((outBuffer[index] >> 16) & 0xf0)
        foReal.write('%02X\n' %samplesOutReal)
        samplesOutReal = (outBuffer[index] >> 24) & 0xff
        foReal.write('%02X\n' %samplesOutReal)

    foReal.close()

def save2textFile(samples, idx):
    outFileFeed =  "capture_output_" + str(idx) + ".txt"
    foReal = open(outFileFeed, "w")
    for index in range(len(samples)/4):
        b1 = samples[4*index]
        b2 = samples[4*index+1]
        b3 = samples[4*index+2]

        b4 = b2 & 0xf
        b5 = (b2 >> 4) & 0xf
        w1 = (b4 << 8) + b1
        w2 = (b3 << 4) + b5

        w = (w2 << 12) + w1
        foReal.write('%06X\n' %w)

    foReal.close()


def calculateSqnr(outBuffer, samples2Read):
    dutOutComplex = outBuffer
    nc = []
    signalPower = 0
    noisePower = 0
    realOutFile =  os.path.join(vectorDumpDir, "matlabTxScp1OutputReal.txt")
    imagOutFile =  os.path.join(vectorDumpDir, "matlabTxScp1OutputImag.txt")

    file_real = open(realOutFile, 'r')
    data_real = []
    data_real = file_real.readlines()
    file_imag = open(imagOutFile, 'r')
    data_imag = []
    data_imag = file_imag.readlines()
    samples2Read = min(samples2Read,len(data_real))

    for index in range(samples2Read):
        samplesOutReal = outBuffer[index]>>20
        if (samplesOutReal >= 2**11):
            samplesOutReal -= 2**12
        samplesOutimag = (outBuffer[index]>>4) & 0xfff
        if (samplesOutimag >= 2**11):
            samplesOutimag -= 2**12
        samplesOut = complex(samplesOutReal, samplesOutimag)

        dutOutComplex[index] = samplesOut
        matlabReal = int(data_real[index][0:3], 16)
        if (matlabReal >= 2**11):
            matlabReal -= 2**12
        matlabimag = int(data_imag[index][0:3], 16)
        if (matlabimag >= 2**11):
            matlabimag -= 2**12
        matlabOutComplex = complex(matlabReal, matlabimag)

        noiseComplex = matlabOutComplex -  samplesOut
        nc.append(noiseComplex)
        signalPower = signalPower + abs(samplesOut)**2
        noisePower = noisePower + abs(noiseComplex)**2

    #debugPrint(signalPower)
    #debugPrint(noisePower)
    if (signalPower <= 0):
            signalPower = 1

    if (noisePower <= 0):
            noisePower = 1

    sqnrValue = 10*log(signalPower/(noisePower), 10)
    return sqnrValue

def generatePayload(packetLength):

    mpdu_payload_val = []
    data = []
    #response_bin_dir = os.path.abspath(vectorDumpDir)

    mpdu_payload_val=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA]

    for index in range(packetLength):    # In Matlab CRC_ENABLE bit set it as 1 If CRC_ENABLE bit is 1 the Payload = Payload -4
        # Try converting the item to an integer
        value=mpdu_payload_val[index%len(mpdu_payload_val)]
        data.append(value)

    return data[0:packetLength]

def writePayloadToFile (payloadData, payloadFileName, packetLength,nMPDUs, vectorDumpDir):
    payload_file = os.path.join(vectorDumpDir, payloadFileName)
    if os.path.exists(vectorDumpDir):
        pass
    else:
        os.makedirs(vectorDumpDir)
    if os.path.exists(payload_file):
        os.remove(payload_file)

    fid = open(payload_file, 'w')
    for i in range(nMPDUs):
        for index in range(packetLength):    # In Matlab CRC_ENABLE bit set it as 1 If CRC_ENABLE bit is 1 the Payload = Payload -4
            fid.write(str(hex(payloadData[index])))
            fid.write('\n')
    fid.close()

def logResults(testParams, sqnrValue, resultsConsld, rowNum, heading, sheet, legacyLength, fecPadding, passcount, failcount):
    resultsList = []
    for i in heading:
        if (i in testParams.keys()):
            resultsList.append(testParams[i])
    if (testParams['format'] == DUT_FrameFormat.HE_TB):
        resultsList.append(legacyLength)
        resultsList.append(fecPadding)
    resultsList.append(sqnrValue)
    if(sqnrValue == 'NA'):
        resultsList.append('MATLAB STUCK')
        failcount+=1
    elif(sqnrValue >= 40):
        resultsList.append('PASS')
        passcount+=1
    else:
        resultsList.append('FAIL')
        failcount+=1
    print(resultsList)
    resultsConsld.worksheet.write_row('A' + str(rowNum), resultsList)
    sheet.write_row('A' + str(rowNum), resultsList)
    return passcount, failcount

def logRxResults(testParams, status, resultsConsld, rowNum, heading, sheet):
    for j in status:
        testParams.append(j)
    print(testParams)
    resultsConsld.worksheet.write_row('A' + str(rowNum), testParams)
    sheet.write_row('A' + str(rowNum), testParams)

def setTestDirectory(DUT_TestConfigParams,test_plan): #PHY_PERFORMANCE - name is not reflecting what is done in this function.
    inputFilePath = os.path.abspath('../test_plan/')
    file_name = os.path.join(inputFilePath, 'WLANPHY.CharacterisationTestPlan.xlsx')
    workbook = xlrd.open_workbook(file_name)
    testSheet = workbook.sheet_by_name(test_plan)
    if (DUT_TestConfigParams.checkAllTestCases == 'YES'):
        DUT_TestConfigParams.test_case_start = 1
        DUT_TestConfigParams.total_test_cases = testSheet.nrows - 1

def setTestConfigFromDict(DUT_TestConfigParams,test_no,test_plan):
    inputFilePath = os.path.abspath('../test_plan/')
    file_name = os.path.join(inputFilePath, 'WLANPHY.CharacterisationTestPlan.xlsx')
    workbook = xlrd.open_workbook(file_name)
    testSheet = workbook.sheet_by_name(test_plan)


    DUT_TestConfigParams.test_enable = int(testSheet.cell(test_no,1).value)
    DUT_TestConfigParams.standard = str(testSheet.cell(test_no,2).value)
    DUT_TestConfigParams.streams = str(testSheet.cell(test_no,3).value)
    DUT_TestConfigParams.chain_sel = int(testSheet.cell(test_no,4).value)
    DUT_TestConfigParams.bw = str(testSheet.cell(test_no,5).value)
    DUT_TestConfigParams.data_rate = str(testSheet.cell(test_no,6).value)
    DUT_TestConfigParams.stbc = str(testSheet.cell(test_no,7).value)
    DUT_TestConfigParams.gi = str(testSheet.cell(test_no,8).value)
    DUT_TestConfigParams.coding = str(testSheet.cell(test_no,9).value)
    DUT_TestConfigParams.start_amplt = int(testSheet.cell(test_no,10).value)
    DUT_TestConfigParams.end_amplt = int(testSheet.cell(test_no,11).value)
    DUT_TestConfigParams.step_size = int(testSheet.cell(test_no,12).value)
    DUT_TestConfigParams.channel = str(testSheet.cell(test_no,13).value)
    DUT_TestConfigParams.payload = str(testSheet.cell(test_no,14).value)
    DUT_TestConfigParams.greenfield_mode = str(testSheet.cell(test_no,15).value)
    DUT_TestConfigParams.preamble = str(testSheet.cell(test_no,16).value)
    if ((test_plan == 'ACI') | (test_plan == 'AACI')):
        DUT_TestConfigParams.in_band_pkt = int(testSheet.cell(test_no,17).value)
    if ((test_plan == 'ACI_HE') | (test_plan == 'AACI_HE')):
        DUT_TestConfigParams.in_band_pkt = int(testSheet.cell(test_no,41).value)
    if (test_plan == 'TX_CFO_SFO'):
        DUT_TestConfigParams.freq_err = int(testSheet.cell(test_no,41).value)
        DUT_TestConfigParams.cfoRatio = int(testSheet.cell(test_no,42).value)
        DUT_TestConfigParams.triggerResponding = int(testSheet.cell(test_no,43).value)
    if ((test_plan == 'TX_SUBBAND') ): # | (test_plan == 'RX_FUNCTIONAL')
        sbw = str(testSheet.cell(test_no,17).value)
        if (sbw != DUT_TestConfigParams.bw):
            DUT_TestConfigParams.bw = sbw +'in' + DUT_TestConfigParams.bw
        DUT_TestConfigParams.p20_flag = int(testSheet.cell(test_no,18).value)
    if (test_plan == 'SJR'):
        DUT_TestConfigParams.jammer_amplt = int(testSheet.cell(test_no,17).value)
        DUT_TestConfigParams.jammer_tone  = int(testSheet.cell(test_no,18).value)
    if (test_plan == 'SJR_HE'):
        DUT_TestConfigParams.jammer_amplt = int(testSheet.cell(test_no,40).value)
        DUT_TestConfigParams.jammer_tone  = int(testSheet.cell(test_no,41).value)
    else:
        DUT_TestConfigParams.p20_flag              = 0
    if (test_plan == 'MULTIPATH'): # MULTIPATH
        DUT_TestConfigParams.fadingtype                = testSheet.cell(test_no,17).value
    if (DUT_TestConfigParams.standard =='11ax'):
        DUT_TestConfigParams.format 	               = int(testSheet.cell(test_no,17).value)
        DUT_TestConfigParams.doppler	               = int(testSheet.cell(test_no,18).value)
        DUT_TestConfigParams.giType	                   = int(testSheet.cell(test_no,19).value)
        DUT_TestConfigParams.dcm	                   = int(testSheet.cell(test_no,20).value)
        DUT_TestConfigParams.midamblePeriodicity       = int(testSheet.cell(test_no,21).value)
        DUT_TestConfigParams.noSigExtn	               = int(testSheet.cell(test_no,22).value)
        DUT_TestConfigParams.chBandwidth	           = int(testSheet.cell(test_no,23).value)
        DUT_TestConfigParams.heLtfType	               = int(testSheet.cell(test_no,24).value)
        DUT_TestConfigParams.nominalPacketPadding      = int(testSheet.cell(test_no,25).value)
        DUT_TestConfigParams.peDuration	               = int(testSheet.cell(test_no,26).value)
        DUT_TestConfigParams.beamChange	               = int(testSheet.cell(test_no,27).value)
        DUT_TestConfigParams.txOpDuration	           = int(testSheet.cell(test_no,28).value)
        DUT_TestConfigParams.numHeLtf	               = int(testSheet.cell(test_no,29).value)
        DUT_TestConfigParams.ruAllocation	           = int(testSheet.cell(test_no,30).value)
        DUT_TestConfigParams.userRuIndex	           = str(testSheet.cell(test_no,31).value)
        DUT_TestConfigParams.startingStsNum            = int(testSheet.cell(test_no,32).value)
        if (DUT_TestConfigParams.format == 6):
            DUT_TestConfigParams.numUser               = int(testSheet.cell(test_no,33).value)
            DUT_TestConfigParams.staIDlist	           = str(testSheet.cell(test_no,34).value)
            DUT_TestConfigParams.desiredStaIDlist	   = str(testSheet.cell(test_no,35).value)
            DUT_TestConfigParams.sigBmcs	           = int(testSheet.cell(test_no,36).value)
            DUT_TestConfigParams.sigBdcm	           = int(testSheet.cell(test_no,37).value)
            DUT_TestConfigParams.sigBcompression       = int(testSheet.cell(test_no,38).value)
            DUT_TestConfigParams.p20_flag              = int(testSheet.cell(test_no,39).value)
            DUT_TestConfigParams.comment               = str(testSheet.cell(test_no,40).value)
        elif (DUT_TestConfigParams.format == 8):
            DUT_TestConfigParams.legacyLength          = int(testSheet.cell(test_no,33).value)
            DUT_TestConfigParams.ldpcExtraSymbol	   = int(testSheet.cell(test_no,34).value)
            DUT_TestConfigParams.heLtfMode	           = int(testSheet.cell(test_no,35).value)
            DUT_TestConfigParams.heSiga2Reserved	   = int(testSheet.cell(test_no,36).value)
            DUT_TestConfigParams.triggerMethod	       = int(testSheet.cell(test_no,37).value)
            DUT_TestConfigParams.feedbackStatus	       = int(testSheet.cell(test_no,38).value)
            DUT_TestConfigParams.heTbDisambiguity	   = int(testSheet.cell(test_no,39).value)
            DUT_TestConfigParams.fecPadding            = int(testSheet.cell(test_no,40).value)
            DUT_TestConfigParams.sta20Moffset          = int(testSheet.cell(test_no,41).value)
            DUT_TestConfigParams.p20_flag              = 0

def readHetbParameters (testConfigParams, testCasesFile, testSheet, testCaseCount):
    workbook = xlrd.open_workbook(testCasesFile)
    simParamsSheet = workbook.sheet_by_name(testSheet)
    keyParams = simParamsSheet.row_values(0)
    paramsValues = simParamsSheet.row_values(testCaseCount)
    matTestParams = {}
    # If paramsValues defined as string in test case excel sheet,
    # paramsValues comes as unicode so read parameters as a string itself.
    # If not, parameters are converted into integer and stored as keyParams.
    for i in range(len(keyParams)):
        if (type(paramsValues[i]) == unicode):
            matTestParams.update({keyParams[i]: (paramsValues[i]) })
        else:
            matTestParams.update({keyParams[i]: int(paramsValues[i])})
    debugPrint("Legacy Length is: " + str( matTestParams['lgLength']))
    debugPrint("Pre FEC padding factor is: " + str(matTestParams['heTbPreFecFactor']))
    legacyLength = matTestParams['lgLength']
    heTbPreFecFactor = matTestParams['heTbPreFecFactor']
    ldpcExtraSymbol = matTestParams['ldpcExtraSymbol']

    mtp_address = DA.EvaluateSymbol('&tx_params.ldpc_extra_symbol')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, ldpcExtraSymbol, DUT_MemoryTypes.Default)

    ruAllocation = matTestParams['ruAllocation']

    mtp_address = DA.EvaluateSymbol('&tx_params.RU_allocation')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, ruAllocation, DUT_MemoryTypes.Default)

    heLtfMode = matTestParams['heLtfType']

    mtp_address = DA.EvaluateSymbol('&tx_params.HE_LTF_mode')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, heLtfMode, DUT_MemoryTypes.Default)

    numOfHeLtfs = matTestParams['numHeLtf']

    mtp_address = DA.EvaluateSymbol('&tx_params.num_HE_LTF')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, numOfHeLtfs, DUT_MemoryTypes.Default)

    heSiga2Reserved = 0 # matTestParams['heSigA2Reserved'] Not defined in excel sheet Yet.

    mtp_address = DA.EvaluateSymbol('&tx_params.heSigA2Reserved')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, heSiga2Reserved, DUT_MemoryTypes.Default)

    startingStsNum = matTestParams['numSts']

    mtp_address = DA.EvaluateSymbol('&tx_params.starting_sts')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, startingStsNum, DUT_MemoryTypes.Default)

    triggerMethod = matTestParams['hetbTrigMethod']

    mtp_address = DA.EvaluateSymbol('&tx_params.trigger_method')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, triggerMethod, DUT_MemoryTypes.Default)

    defaultPeDuration = matTestParams['peDuration']

    mtp_address = DA.EvaluateSymbol('&tx_params.PE_duration')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, defaultPeDuration, DUT_MemoryTypes.Default)

    feedbackStatus = 0 # matTestParams['feedBackStatus'] Not defined in excel sheet Yet.

    mtp_address = DA.EvaluateSymbol('&tx_params.feedback_status')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, feedbackStatus, DUT_MemoryTypes.Default)

    heTbDisambiguity = matTestParams['heTbPeDisambiguity']

    mtp_address = DA.EvaluateSymbol('&tx_params.HETB_PE_disambiguity')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, heTbDisambiguity, DUT_MemoryTypes.Default)

    return legacyLength, heTbPreFecFactor

def getJammerTestParams(DUT_TestConfigParams,test_no):
    inputFilePath = os.path.abspath('../test_plan/')
    file_name = os.path.join(inputFilePath, 'WLANPHY.CharacterisationTestPlan.xlsx')
    workbook = xlrd.open_workbook(file_name)
    testSheet = workbook.sheet_by_name('RX_JAMMER')


    DUT_TestConfigParams.test_enable = int(testSheet.cell(test_no,1).value)
    DUT_TestConfigParams.standard = str(testSheet.cell(test_no,2).value)
    DUT_TestConfigParams.streams = str(testSheet.cell(test_no,3).value)
    DUT_TestConfigParams.chain_sel = int(testSheet.cell(test_no,4).value)
    DUT_TestConfigParams.bw = str(testSheet.cell(test_no,5).value)
    DUT_TestConfigParams.data_rate = str(testSheet.cell(test_no,6).value)
    DUT_TestConfigParams.stbc = str(testSheet.cell(test_no,7).value)
    DUT_TestConfigParams.gi = str(testSheet.cell(test_no,8).value)
    DUT_TestConfigParams.coding = str(testSheet.cell(test_no,9).value)
    DUT_TestConfigParams.start_amplt = int(testSheet.cell(test_no,10).value)
    DUT_TestConfigParams.end_amplt = int(testSheet.cell(test_no,11).value)
    DUT_TestConfigParams.step_size = int(testSheet.cell(test_no,12).value)
    DUT_TestConfigParams.channel = str(testSheet.cell(test_no,13).value)
    DUT_TestConfigParams.payload = str(testSheet.cell(test_no,14).value)
    DUT_TestConfigParams.greenfield_mode = str(testSheet.cell(test_no,15).value)
    DUT_TestConfigParams.preamble = str(testSheet.cell(test_no,16).value)
    DUT_TestConfigParams.packetOn = int(testSheet.cell(test_no,17).value)
    DUT_TestConfigParams.jammerOn = int(testSheet.cell(test_no,18).value)
    DUT_TestConfigParams.jammer_amplt = int(testSheet.cell(test_no,19).value)
    DUT_TestConfigParams.jammer_tone = int(testSheet.cell(test_no,20).value)

def readFile (fileName):
    file_open = open(fileName, 'r')
    data_read = []
    data_read = file_open.readlines()
    file_open.close()
    return data_read

def storeOutputFiles(file_adc_out_real, file_adc_out_imag):
    data_real = readFile (file_adc_out_real)
    data_imag = readFile (file_adc_out_imag)

    out_file_real = open('rxsamples_out_real.txt', 'a')
    out_file_imag = open('rxsamples_out_imag.txt', 'a')
    out_file_real.writelines(str(line) for line in data_real)
    out_file_imag.writelines(str(line) for line in data_imag)

    out_file_real.close()
    out_file_imag.close()

def combine_testcases(file_adc_out_real, file_adc_out_imag, test_case_count):
    last_out_real = readFile ('rxsamples_out_real.txt')
    last_out_imag = readFile ('rxsamples_out_imag.txt')

    data_real = readFile (file_adc_out_real)
    data_imag = readFile (file_adc_out_imag)
    if test_case_count == 108:
        secondPktLen = len(data_real)
        last_out_real[8000:8000+secondPktLen] = data_real
        last_out_imag[8000:8000+secondPktLen] = data_imag
    else:
        del last_out_real[8000:]
        del last_out_imag[8000:]
        last_out_real.extend(data_real[1:])
        last_out_imag.extend(data_imag[1:])

    file_real = open(file_adc_out_real, 'w')
    file_imag = open(file_adc_out_imag, 'w')
    file_real.writelines(str(line) for line in last_out_real)
    file_imag.writelines(str(line) for line in last_out_imag)

    file_real.close()
    file_imag.close()
    os.remove('rxsamples_out_real.txt')
    os.remove('rxsamples_out_imag.txt')


def dumpMatSVDoutput():
    realOutFile =  os.path.join(vectorDumpDir, "beamformeeFeedback.txt")
    file_real = open(realOutFile, 'r')
    matsvdOutput = []
    for line in file_real:
        line1 = line.replace('\n', '')
        matsvdOutput.append(int(line1, 16))
    return matsvdOutput

def dumpDutSVDoutput(outBuffer, bytes2Read, svdOutFileName):
    """ Dump SVD output data to text file """
    outFilePath = vectorDumpDir
    if not os.path.exists(outFilePath):
        os.makedirs(outFilePath)

    svdoutFile =  os.path.join(outFilePath,svdOutFileName)
    svdOutput = open(svdoutFile, "w")
    for index in range(0,bytes2Read):
        byteOut = outBuffer[index]
        svdOutput.write('%02X\n' %byteOut)
    svdOutput.close()

def dumpMatNhOutput():
    realOutFile =  os.path.join(vectorDumpDir, "ed11kEstParams.txt")
    file_real = open(realOutFile, 'r')
    matNhOutput = []
    for line in file_real:
        line1 = line.replace('\n', '')
        matNhOutput.append(int(line1.split(':')[-1]))
    return matNhOutput

def logSummaryResults(testConfigParams, rowNum, heading, sheet, passcount, failcount, sheet1):
    status = [passcount , failcount, testConfigParams.total_test_cases]
    testConfigParams.subFuncTestPlan = [testConfigParams.subFuncTestPlan]
    for j in status:
        testConfigParams.subFuncTestPlan.append(j)
    sheet.write_row('A' + str(rowNum), testConfigParams.subFuncTestPlan)
    sheet1.write_row('A' + str(rowNum), testConfigParams.subFuncTestPlan)

def readReportfile(systemConfig, targetParams, testConfigParams):
    target = targetParams.target_type
    if target == 'Simulator':
        inputFilePath = os.path.abspath('../reports/' + systemConfig + '/sim' + '/')
    elif target == 'SysProbe':
        inputFilePath = os.path.abspath('../reports/' + systemConfig + '/emu' + '/')
    dutmode = testConfigParams.dut_operating_mode
    if dutmode == 'RX':
        reportFile = 'WLANPHY.RXfunctionalTestReport' + '.xlsx'
    elif dutmode == 'TX':
        reportFile = 'WLANPHY.TXfunctionalTestReport' + '.xlsx'
    sheetName = 'REV'
    rev_file = os.path.join(inputFilePath, reportFile)
    workbook = xlrd.open_workbook(rev_file)
    simParamsSheet = workbook.sheet_by_name(sheetName)
    return simParamsSheet

def logRevSheet(revParams, simParamsheet, sheet, cfgParamFromXls):
    keyparams = simParamsheet.row_values(0)
    sheet.write_row('A1', keyparams)
    j=1
    while(j < revParams.s_no):
        paramValues = simParamsheet.row_values(j)
        excel_date = paramValues[1]
        sheet.write_row('A' + str(j+1), excel_date)
        j=j+1
    if(cfgParamFromXls):
        revParams.date = convertTodateformat(revParams.date)
    status = [revParams.s_no, revParams.date, revParams.codebase, revParams.cl_no, revParams.targetname, revParams.toolkit, revParams.afe, revParams.matlab, revParams.comments]
    sheet.write_row('A'+ str(j+1), status)

def convertTodateformat(excel_date):
    dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(excel_date) - 2)
    year=str(dt.year)
    month=str(dt.month)
    day=str(dt.day)
    date = month + '/'+ day + '/'+ year
    return date
