#################################################
import time
import os
import shutil
import subprocess
import scipy.io as spio
import xlsxwriter
import xlrd

from math import log
#from CSUtils import DA
from math import sin, cos, pi
from subprocess import call
from common_utils import *
from DUT_functions import *

LOG_BASE_2 = 2
###################################################
if (platform=='win32' or platform=='win64'):
    inputFilePath = os.path.abspath('../matlab_exe_win/')
    matfile = '../matlab_exe_win/loadConstants.mat'
elif (platform=='linux' or platform=='linux2'):
    inputFilePath = os.path.abspath('../matlab_exe_lin/')
    matfile = '../matlab_exe_lin/loadConstants.mat'
Constants = spio.loadmat(matfile)
###################################################

def Compare_svd_output(sysConfig='520_49'):
    cwd = os.getcwd()
    os.chdir(inputFilePath)
    svd_exe = 'compare_beamforming_feedback.exe' + ' ' + 'DecodedData_TxDump' + ' ' + 'ch_taps_buf_ndp' + ' ' + 'svd_snr_output_buf' + ' ' + 'svd_angle_output_buf' + ' ' + sysConfig
    debugPrint("Running MATLAB Executable for SVD comparision...")
    os.system(svd_exe)
    file = open('svd_comparision_out.txt', 'r')
    print file.read()
    os.chdir(cwd)

def generateMatlabFiles (Matlab_input, test_case_count, testConfigParams, sock, MtlbExeProcess):
    """ Provide MATLAB with testcase input and TEST Start using socket communication to generate MATLAB output files"""
    conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
    conn.setblocking(1)
    conn.send(str(Constants.get('START_TESTCASE')[0][0])+ ' ' + Matlab_input)#Give indication from python to MATLAB to start the test case
    debugPrint("Sent the trigger to Matlab to start test case " + str(test_case_count))
    sock.settimeout(testConfigParams.time_out_value)#Sets the timeout value.
    conn, addr = sock.accept()
    time.sleep(2)
    testCode = conn.recv(1024)

    return testCode

def Run_matlab_exe(testConfigParams, testCasesFile, socketIdx,systemConfig):
    """This function RUNs the Matlab executable to generate the debugiq dump files
    and Returns MtlbExeProcess ID and updated timeout value.
    :param  file_mode
         This is the file operation mode for stdout.txt and stderr.txt ffiles.
         Valid arguments are 'wb'/'w' (write mode) or 'ab'/'a' (append mode)
    :param  time_out_value
         Time out value in seconds
    :param testCasesFile
           testcases excel file name
    :return  MtlbExeProcess
         sim_top.exe process ID.
    :return  timeout
         Updated timeout value. This value is used in order to kill the Matlab exe,
         if it hasn't responded properly in the mentioned timeout period.

    NOTE:
         This function needs the executable path (inputFilePath) to be updated
         in dut_debugiq_test_loop() function.
    """
    enSocketComm = 1
    if not '.xlsx' in testCasesFile:
        testCasesFile = testCasesFile + '.xlsx'

    cwd = os.getcwd()
    os.chdir(inputFilePath)

    if (platform == 'linux' or platform == 'linux2'):
        ##MCR_ROOT = '/pro/ensigma/systems/tools/mcr/v80'
        MCR_ROOT = '/cad/matlab/Compiler_runtime/R2020b/v99'
        matlab_exe = './run_matlab_sim_top.sh' + ' ' + MCR_ROOT
        testFile = '../testcases/'+ systemConfig +'/testcases_firmware' + testConfigParams.test_type + '_' + testConfigParams.subFuncTestPlan
        testcaseDir = os.path.join('../matlab_exe_lin/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    else:
        matlab_exe = 'matlab_sim_top.exe'
        testFile = '../testcases/'+ systemConfig +'/testcases_firmware' + testConfigParams.test_type + '_' + testConfigParams.subFuncTestPlan
        testcaseDir = os.path.join('../matlab_exe_win/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    inArgs    = ' simMode ' + ' firmware ' + \
                ' testGroup ' + testConfigParams.subFuncTestPlan + \
                ' opMode ' + testConfigParams.dut_operating_mode +  \
                ' testcaseFile ' +  testFile + \
                ' portNum '      + str(socketIdx) + \
                ' enSocketComm ' + str(enSocketComm)
    matlab_exe = matlab_exe + inArgs

    # Unique test vector directory is created if it does not exist.
    tvDir   = os.path.abspath(testcaseDir)
    if not os.path.exists(tvDir): os.makedirs(tvDir)

    # Clean up old stdout.txt and stderr.txt files. Start Matlab and move
    # back to original directory.
    stdOutFile = os.path.join(tvDir, 'stdout.txt')
    stdErrFile = os.path.join(tvDir, 'stderr.txt')
    if os.path.isfile(stdOutFile): os.remove(stdOutFile)
    if os.path.isfile(stdErrFile): os.remove(stdErrFile)

    debugPrint("Running MATLAB Executable :\n" + matlab_exe + "\n" + \
               "stdOut : " + stdOutFile + "\n" \
               "stdErr : " + stdErrFile + "\n")
    with open(stdOutFile, 'wb') as out, open(stdErrFile, 'wb') as err:
        MtlbExeProcess = subprocess.Popen(matlab_exe, stdout = out, stderr =
        err, shell=True)

    os.chdir(cwd)
    time.sleep(3)
    return MtlbExeProcess

def Prepare_payload():
    """ Copies files required for Matlab executable """
    Total_NTx=1
    if (platform=='linux' or platform=='linux2'):
        fid = open('../matlab_exe_lin/UCCP_Testing/Total_NTx.txt', 'w')
    else:
        fid = open('../matlab_exe_win/UCCP_Testing/Total_NTx.txt', 'w')
    fid.write(str(Total_NTx))
    fid.close()

    SIGBWbasedIFFT_val=1
    if (platform=='linux' or platform=='linux2'):
        fid = open('../matlab_exe_lin/UCCP_Testing/SIGBWbasedIFFT.txt', 'w')
    else:
        fid = open('../matlab_exe_win/UCCP_Testing/SIGBWbasedIFFT.txt', 'w')
    fid.write(str(SIGBWbasedIFFT_val))
    fid.close()


def Rx_evm_analysis(sock, DUT_TestConfigParams, op_file_path, test_case_count, sub_fun_plan, simparams_variables):
    """
    Collects the MCP dumps and computes the EVM.
    The dumps collected will be
        1. last 8 symbol cpe compensated data (RXP input)
        2. channel estimate
    The dumps will be saved to matlab_exe folder.

    :param release
         Results folder name given in WLANPHY.TestConfig.xlsx sheet.
    :param system_config
         System configuration: '420_37' | '450_55' | '520_55' etc
    :param build_config
         Build/Compile configuration: 'debug' | 'test' | 'release'
    :param Num_symbols_in
         Num of valid symbols in CPE Compensated Data dump file.
         Max Num_symbols_in = 8 (Taken care inside the function), because last 8 symbol cpe compensated data is captured for this analysis.
    :param test_case_count
         Test Case Number in Matlab test_cases.xlsx sheet.

    :return EVM
         Returns EVM array.
         The Num of elements in the array is same as the parameter nrx_active.

    """
    FECtype_str  = 'BCC'  if (simparams_variables.ldpc == 0) else 'LDPC'
    GItype_str   = 'LGI'  if (simparams_variables.sgi == 0)  else 'SGI'
    STBCtype_str = 'STBC' if (simparams_variables.stbc == 1)    else 'NORMAL'
    system_config=DUT_TestConfigParams.system_config
    build_config=DUT_TestConfigParams.build_config,
    obw=(20* 2**simparams_variables.obw)
    sbw=(20*2**simparams_variables.sbw)
    p20flag=simparams_variables.p20Flag
    FrameFormatIndx=simparams_variables.FrameFormat
    MCS_DR_Indx=simparams_variables.mcs
    nrx_active=simparams_variables.nrx
    ntx_active=simparams_variables.ntx
    Nss=simparams_variables.nss
    FECtype=FECtype_str
    STBCtype=STBCtype_str
    gi_type=GItype_str

    # Select Master MCP
    target_inf = DA.GetTargetInfo()

    mcp_vector_address = DA.EvaluateSymbol('OFDM_NSYM_VARIABLE')
    mcp_vector_32bit = DA.ReadMemoryBlock(mcp_vector_address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.RegionBMemory)
    Num_symbols_in = [(mcp_vector_32bit[index] >> 8) for index in range(len(mcp_vector_32bit))][0]


    # Save Required Binary Files
    single_element_bytes = 4

    FFstrList = ['dsss','lg','mm','gf','vht']
    FFstr = FFstrList[FrameFormatIndx]

    file_str = FFstr + '_nrx' + str(nrx_active) + '_ntx' + str(ntx_active) + '_obw' + str(obw) + \
    '_sbw' + str(sbw) + '_p20flag' + str(p20flag) + '_mcs' + str(MCS_DR_Indx) + '_' + \
    str(FECtype.lower()) + '_' + str(gi_type.lower())

    stbc_flag = 0
    if (STBCtype.upper() == 'STBC'):
        file_str = file_str + '_' + str(STBCtype.lower())
        stbc_flag = 1

    cpe_comp_data_size_bytes = 4096 * single_element_bytes  # 8 * (256+256) * 4; str1 and str2 are interleaved, each 8*256
    if (stbc_flag ==1):
        channel_taps_size_bytes  = 2 * 1024 * single_element_bytes
    else:
        channel_taps_size_bytes  = 1024 * single_element_bytes

    binFilePath = os.path.join(op_file_path,  "BinFiles" + sub_fun_plan)
    if not os.path.exists(binFilePath):
        os.makedirs(binFilePath)

    cpe_comp_data_file = os.path.join(binFilePath, file_str + '_data_' + str(test_case_count) + '.bin')
    ch_taps_file       = os.path.join(binFilePath, file_str + '_chan_' + str(test_case_count) + '.bin')

    DA.SaveBinaryFile(cpe_comp_data_file, 'RX_OFDM_CPE_COMP_OUT_STR1_1_BUF', cpe_comp_data_size_bytes, False, DUT_MemoryTypes.RegionDMemory)
    if (stbc_flag ==1):
        if (obw==80) or (FrameFormatIndx<4):
            DA.SaveBinaryFile(ch_taps_file, 'OFDM_SIG_CH_SMOOTH_TAPS_h11_BUF', channel_taps_size_bytes , False, DUT_MemoryTypes.RegionDMemory)
        else:
            DA.SaveBinaryFile(ch_taps_file, 'OFDM_CH_EST_TAPS_h11_BUF', channel_taps_size_bytes , False, DUT_MemoryTypes.RegionDMemory)
    else:
        DA.SaveBinaryFile(ch_taps_file, 'OFDM_CH_EST_TAPS_h11_BUF', channel_taps_size_bytes , False, DUT_MemoryTypes.RegionDMemory)

    time.sleep(1)

    fileformat = 32
    Num_symbols_in = 8 if (Num_symbols_in > 8) else Num_symbols_in
    oper_bw = int(log(obw/20, LOG_BASE_2))
    sig_bw  = int(log(sbw/20, LOG_BASE_2))
    IsLegacyIndx = 1 if (FrameFormatIndx == 1) else 0

    data_file = os.path.join(binFilePath, file_str + '_data_' + str(test_case_count))
    chan_file = os.path.join(binFilePath, file_str + '_chan_' + str(test_case_count))

    # The following tweak is a workaround for compute_mcp_rx_evm.exe
    # In HT MM/GF cases, the MCS in 2 stream case should be given as MCS in 1 stream case
    if ((FrameFormatIndx == 2) or (FrameFormatIndx == 3)):
        MCS_DR_Indx = MCS_DR_Indx & 0x7

    # In case of legacy, the packet should be treated as sig_bw = 20 MHz.
    # Hence, Give sig_bw = 1 to represent 20MHz
    if (FrameFormatIndx == 1):
        sig_bw = 0

    computeEvmArgs = data_file +" "+ chan_file +" "+ str(fileformat) +" "+ str(MCS_DR_Indx) +" "+ \
    str(Nss) +" "+ str(nrx_active) +" "+ str(oper_bw) +" "+ str(Num_symbols_in) + " " + \
    str(sig_bw) + " " + str(p20flag) + " " + str(IsLegacyIndx) + " " + str(stbc_flag) + " " + system_config


    conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
    conn.setblocking(1)
    conn.send(str(Constants.get('COMPUTE_EVM')[0][0])+ ' ' + computeEvmArgs) #Give indication from python to MATLAB to start the test case
    debugPrint("Sent the trigger to Matlab to start EVM computation for testCase  " + str(test_case_count))
    sock.settimeout(DUT_TestConfigParams.time_out_value)#Sets the timeout value.
    conn, addr = sock.accept()
    time.sleep(2)
    testCode = conn.recv(1024)
    if (int(testCode) == Constants.get('EVM_COMPUTED')[0][0]):
        # Read EVM values from EVM.txt file:
        EVM_file = os.path.join(simparams_variables.matDumDirct, 'EVM.txt')
        EVM = []
        if os.path.exists(EVM_file):
            dutresultfile = open(EVM_file, "r")
            evmresult = dutresultfile.readlines()
            dutresultfile.close()
        else:
            EVM.append(str(0))
            if (nrx_active == 2):
                EVM.append(str(0))
        evmStr1 = evmresult[0].split("\n")[0]
##        if (evmStr1 == 'NaN'):
##            evmStr1=0
        EVM.append(evmStr1)
        debugPrint('DUT_EVM_stream1 = ' + str(EVM[0]) + ' dB')
        if (nrx_active == 2) or (stbc_flag==1):
            evmStr2 = evmresult[1].split("\n")[0]
##            if (evmStr2 == 'NaN'):
##                evmStr2=0
            EVM.append(evmStr2)
            debugPrint('DUT_EVM_stream2 = ' + str(EVM[1]) + ' dB')

    return EVM

def KillSubProcess(ProcessID):
    """
    Kills the subProcess with given processID.
    The process that is going to be killed should be opened by subprocess.Popen() command.

    :param ProcessID
           sub process identifier (returned by subprocess.Popen() command)
    """
    try:
        ProcessID.kill()
    except Exception as killProcessError:
        debugPrint('Unable to kill the process')
        debugPrint(type(killProcessError))
        debugPrint(killProcessError)
        try:
            ProcessID.kill()
        except:
            debugPrint('Unable to kill the process again')
        else: # If there is no exception then execute this block.
            debugPrint('Process killed successfully in 2nd trail')
    else: # If there is no exception then execute this block.
        debugPrint('Process killed successfully')
        time.sleep(3)
    return

def ReadMatlabTestStatus(sub_fun_plan, simparams_variables, testCaseNo):
    MatlabResults=[]
    matlabResultFilePath = simparams_variables.matDumDirct + "//result_firmware_" + sub_fun_plan
    resultFileName = "result_" + str(testCaseNo) + ".txt"
    resultFile = os.path.join(matlabResultFilePath, resultFileName)
    if os.path.exists(resultFile):
        matlabresultfile = open(resultFile, "r")
        MatlabStatus = matlabresultfile.readline()
        matlabresultfile.close()
        os.remove(resultFile)
        MatlabResults = MatlabStatus.split(",")
    else:
        MatlabResults.append('NA')
        MatlabResults.append('NA')
        MatlabResults.append('NA')
        MatlabResults.append('NA')
        MatlabResults.append('NA')
    debugPrint('Matlab CRC status = '+str(MatlabResults[-4]))
    return MatlabResults

def Read_matlab_evm(MatlabResults):
    """ Reads Matlab EVM from MatlabResults structure"""
    global simparams_variables
    MTLB_EVM = []
    MTLB_EVM.append(MatlabResults[-3])
    debugPrint('MTLB_EVM_stream1 = ' + str(MTLB_EVM[0]))
    if (simparams_variables.nrx == 2) or (simparams_variables.stbc == 1):
        MTLB_EVM.append(MatlabResults[-2].split("\n")[0])
        debugPrint('MTLB_EVM_stream2 = ' + str(MTLB_EVM[1]))

    return MTLB_EVM

def Generate_testcases(DUT_TestConfigParams):
    """
    Generate testcases.xlsx file for given test configuration and system capabilities.
    Successful run of create_functional_test_cases.exe will generate
    testcases_*.xlsx files based on requirement.
    :param DUT_TestConfigParams
        An object of class TestConfigParams
    """
    system_config   = DUT_TestConfigParams.system_config
    test_type       = DUT_TestConfigParams.test_type
    subFuncTestPlan1 = DUT_TestConfigParams.subFuncTestPlan
    RxTxTest        = DUT_TestConfigParams.dut_operating_mode
    lnaEnableStr    = DUT_TestConfigParams.lna_model_enable
    if (lnaEnableStr == 'YES'):
        lnaEnable = 1
    else:
        lnaEnable = 0


    cwd = os.getcwd()
    testplan_file_names= []
    testConfigPath  = os.path.abspath('../test_config')
    testCaseExePath = os.path.abspath('../matlab_exe_win/config')
    testPlanPath    = os.path.abspath('../test_plan')

    sysCapabilityFile     = os.path.join(testConfigPath,  'WLANPHY.SystemCapabilities.xlsx')
    sysCapabilityFile2    = os.path.join(testCaseExePath, 'WLANPHY.SystemCapabilities.xlsx')
    funcTestPlanFile      = os.path.join(testPlanPath,    'WLANPHY.FunctionalTestPlan.xlsx')
    funcTestPlanFile2     = os.path.join(testCaseExePath, 'WLANPHY.FunctionalTestPlan.xlsx')
    sanityTestPlanFile    = os.path.join(testPlanPath,    'WLANPHY.SanityTestPlan.xlsx'    )
    sanityTestPlanFile2   = os.path.join(testCaseExePath, 'WLANPHY.SanityTestPlan.xlsx'    )
    realTestPlanFile      = os.path.join(testPlanPath,    'WLANPHY.RealTimeTestPlan.xlsx'  )
    realTestPlanFile2     = os.path.join(testCaseExePath, 'WLANPHY.RealTimeTestPlan.xlsx'  )
    hardwareTestPlanFile  = os.path.join(testPlanPath,    'WLANPHY.HardWareTestPlan.xlsx'  )
    hardwareTestPlanFile2 = os.path.join(testCaseExePath, 'WLANPHY.HardWareTestPlan.xlsx'  )


    if not os.path.exists(sysCapabilityFile2):
        debugPrint('Copying WLANPHY.SystemCapabilities.xlsx to ' + testCaseExePath)
        shutil.copy(sysCapabilityFile, testCaseExePath)
        time.sleep(1)

    if not os.path.exists(funcTestPlanFile2):
        debugPrint('Copying WLANPHY.FunctionalTestPlan.xlsx to ' + testCaseExePath)
        shutil.copy(funcTestPlanFile, testCaseExePath)
        time.sleep(1)

    if not os.path.exists(sanityTestPlanFile2):
        debugPrint('Copying WLANPHY.SanityTestPlan.xlsx to ' + testCaseExePath)
        shutil.copy(sanityTestPlanFile, testCaseExePath)
        time.sleep(1)

    if not os.path.exists(realTestPlanFile2):
        debugPrint('Copying WLANPHY.RealTimeTestPlan.xlsx to ' + testCaseExePath)
        shutil.copy(realTestPlanFile, testCaseExePath)
        time.sleep(1)

    if not os.path.exists(hardwareTestPlanFile2):
        debugPrint('Copying WLANPHY.HardWareTestPlan.xlsx to ' + testCaseExePath)
        shutil.copy(hardwareTestPlanFile, testCaseExePath)
        time.sleep(1)

    # ----- Reading sheet names from test plan ------------- #
    if ((test_type == 'FUNCTIONAL') or (test_type == 'SANITY')):
        testPlanWorkBook = xlrd.open_workbook(funcTestPlanFile)
        sheet_names = testPlanWorkBook.sheet_names()
        testplan_sheet_names = map(str, sheet_names)
        testplan_sheet_names.remove('Rev')
    elif((test_type == 'REALTIME')):
        testPlanWorkBook = xlrd.open_workbook(realTestPlanFile)
        sheet_names = testPlanWorkBook.sheet_names()
        testplan_sheet_names = map(str, sheet_names)
        testplan_sheet_names.remove('Rev')
    elif((test_type == 'HARDWARE')):
        testPlanWorkBook = xlrd.open_workbook(hardwareTestPlanFile)
        sheet_names = testPlanWorkBook.sheet_names()
        testplan_sheet_names = map(str, sheet_names)
        testplan_sheet_names.remove('Rev')
    # -------------------------------------------- #
    if (DUT_TestConfigParams.genTestCasesWithExe == 'YES'):
        os.chdir(testCaseExePath)
        debugPrint("Running Generate Test cases executable...")
        subFuncTestPlans = subFuncTestPlan1.split(',')

        for subFuncTestPlan in subFuncTestPlans:
            GenTestCasesExeWithArgs = 'create_testcases.exe ' + ' '  + \
            test_type.lower() + ' '  + subFuncTestPlan + ' ' + RxTxTest.upper() + ' ' + str(lnaEnable)
            with open("stdout_testcases.txt", 'wb') as out, open("stderr_testcases.txt", 'wb') as err:
                GenTestCasesExeProcess = subprocess.Popen(GenTestCasesExeWithArgs, stdout = out, stderr = err)
                GenTestCasesExeProcessRetCode = GenTestCasesExeProcess.wait()

            if(GenTestCasesExeProcessRetCode == -1):
                stderr_file = os.path.join(testCaseExePath, 'stderr_testcases.txt')
                printStr = '\nTestCases Excel sheets are \"NOT\" generated successfully.\n' + \
                'Pls look into ' + stderr_file + ' file for details.\n'
            else:
                printStr = '\nTestCases Excel sheets are generated successfully.\n'

        line = 100 * '*'
        printStr = line + printStr + line
        debugPrint(printStr)

        files_in_dir = os.listdir(testCaseExePath)
        xl_file_names = []
        xl_sheet_names = []
        for file_name in files_in_dir:
            if ((file_name.find('testcases_') == 0) and (file_name.find('.xlsx'))):
                xl_file_names.append(file_name)
                xl_sheet_name = file_name.split('_')[1]
                xl_sheet_names.append(xl_sheet_name)

        #----- Arranging Xls files based on TestPlan ------ #
        for index in range(0,len(testplan_sheet_names)):
            for index1 in range(0,len(xl_sheet_names)):
                if (testplan_sheet_names[index] == xl_sheet_names[index1]):
                    testplan_file_names.append(xl_file_names[index1])

        # Copy/Move the testcases_*.xlsx files to phy/test/matlab_exe folder
        # If the file already exists in matlab_exe folder, remove the file and copy again (overwrite).
        for xl_file_name in testplan_file_names:
            xl_file_in_matlab_exe = os.path.join(inputFilePath, xl_file_name)
            if (os.path.exists(xl_file_in_matlab_exe)):
                os.remove(xl_file_in_matlab_exe)
            shutil.move(xl_file_name, inputFilePath) # We can use copy/move
        # Sleep for 5 seconds (Buffer time for copying/moving)
        time.sleep(5)
        os.chdir(cwd)
    else:
        testCaseSheets = DUT_TestConfigParams.testCasesFileName.split(',')
        for testCaseSheet in testCaseSheets:
            if not '.xlsx' in testCaseSheet:
                testCasesFileName = testCaseSheet + '.xlsx'
                testplan_file_names.append(testCasesFileName)
            else:
                testplan_file_names.append(testCaseSheet)

    debugPrint(testplan_file_names)
    return testplan_file_names

def Write_debug_config_params_for_matlab(DUT_TestConfigParams, sub_fun_plan):
    """This function writes the test parametrs to the mcp_debug_config.txt
    file located in phy/test/matlab_exe folder. """

    mcp_debug_config_file_path = os.path.join(inputFilePath, 'UCCP_Testing')
    mcp_debug_config_file = os.path.join(mcp_debug_config_file_path, 'mcp_debug_config.txt')

    build_config=DUT_TestConfigParams.build_config
    mcp_debugging_enable = 1
    matlab_only_tb = 0
    build_config_num = 0 if (build_config.lower() == 'debug') else ( 1 if (build_config.lower() == 'test') else 2 )
    mcp_test_mtlb_start_pkt_idx = 1
    playout_enable = 0
    debug_params = []
    debug_params.append(mcp_debugging_enable)
    debug_params.append(DUT_TestConfigParams.target_type)
    debug_params.append(DUT_TestConfigParams.target_number)
    debug_params.append(DUT_TestConfigParams.test_case_start)
    debug_params.append(DUT_TestConfigParams.total_test_cases)
    debug_params.append(DUT_TestConfigParams.num_pkts)
    debug_params.append(build_config_num)
    debug_params.append(matlab_only_tb)
    debug_params.append(DUT_TestConfigParams.time_out_value)
    debug_params.append(mcp_test_mtlb_start_pkt_idx)
    debug_params.append(playout_enable)
    debug_params.append(DUT_TestConfigParams.system_config)
    if(DUT_TestConfigParams.system_config.find('520_') == 0):
        debug_params.append('MCU')
    else:
        debug_params.append('MTP')
    if (sub_fun_plan=='Beamformee'):
        svd_test_flag=1
    else:
        svd_test_flag=0
    debug_params.append(svd_test_flag)

    fid = open(mcp_debug_config_file, 'w')
    for index in range(len(debug_params)):
        fid.write(str(debug_params[index]))
        fid.write('\n')
    fid.close()
    return debug_params

def readMatlabStatus (testConfigParams, testCaseCount, matlabCrcCnt):
    if (platform == 'linux' or platform == 'linux2'):
        vectorDumpDir = os.path.join('../matlab_exe_lin/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    else:
        vectorDumpDir = os.path.join('../matlab_exe_win/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    subDir2 = 'testcase_' + '{0:05d}'.format(testCaseCount)
    vectorDumpDir = os.path.join(vectorDumpDir, subDir2)
    if os.path.exists(vectorDumpDir):
        inputFilePath=vectorDumpDir
    matlabResultFile = os.path.join(inputFilePath, 'matlabResult.txt')
    resultFile = open(matlabResultFile, 'r')
    data = resultFile.readlines()

    if (int(data[0][-2])== 1):
        status = "CRC PASS"
        matlabCrcCnt = matlabCrcCnt+1
    elif(int(data[0][-2]) == 0):
        status = "CRC FAIL"
    else:
        status = "RX OTHER FAIL"
    debugPrint("Matlab CRC Status is: " + str(status))
    return matlabCrcCnt

