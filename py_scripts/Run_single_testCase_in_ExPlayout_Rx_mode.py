#-------------------------------------------------------------------------------
# Name:        Run_single_testCase_in_ExPlayout_Rx_mode.py
# Purpose:     This is the main file to be run single test case for Harness testing in RX mode.
#              TestMode:  PlayoutMode: EXTERNAL.
# Author:      Imagination Technologies
#
# Created:     2019
# Copyright:   (c) 2019, Imagination Technologies Ltd.
#-------------------------------------------------------------------------------
""" To run use command
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/lg"  "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/mf"  "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/vht" "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/hesu" "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/dsss" "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/lg"   "SysProbe" "288"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/mf"   "SysProbe" "288"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/vht"  "SysProbe" "62"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode.py  "../testvectors/dsss" "SysProbe" "62"
    """

'''Codescape load script'''
import array
import os
import time
import struct
import sys
from imgtec import codescape
from imgtec.codescape.da_types import LoadType
#from CSUtils import DA
from data_type_utils import *
import playout_functions

def testing_start(test_case_dir):

    playout_flag = 1;  ## 1 for playout mode 0: debugiq mode

    memoryType   = 'shared'
    lna_model_enable = 'NO'

    #memoryType = 'separate'
    #lna_model_enable = 'YES'

    #Reading I&Q samples from file and store into the buffer
    inputFilePath = os.path.abspath(test_case_dir)
    if (lna_model_enable == 'YES'):
        file_adc_out_real = os.path.join(inputFilePath, 'rf1InputReal.txt')
        file_adc_out_imag = os.path.join(inputFilePath, 'rf1InputImag.txt')
    else:
        file_adc_out_real = os.path.join(inputFilePath, 'adc1OutputReal.txt')
        file_adc_out_imag = os.path.join(inputFilePath, 'adc1OutputImag.txt')


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
            if(playout_flag == 1):
                temp_scp_in = int(data_real[s_index][0:3] + '0' + data_imag[s_index][0:3] + '0', 16)
            else:
                temp_scp_in = int(data_real[s_index][0:3] + data_imag[s_index][0:3] + '00' , 16)
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

    # Add silence period
    adcSamplingrate = 40
    silenceTime = 36
    silence_to_append = silenceTime * adcSamplingrate
    if(memoryType == 'shared'):
        scp_in_int += silence_to_append*[0]
    else:
        scp_in_int += (silence_to_append*2)*[0]

    #SCP input samples pointer
    inputSamples = scp_in_int;

    #Number of samples
    numSamples   = len(data_real);



    #Initialization of the system parameters
    bandwidth  = 0;
    p20flag    = 0;
    nrx_active = 1;
    ntx_active = 1;
    freq_band  = 1;
    channelnum = 144;
    operatingBand = 5 * 1e9


    DA.SelectTargetByPattern('MCU')
    print('Initializing system parameters')

    #Disbale AGC module
    agcModuleEnable = 0
    if(lna_model_enable == 'YES'):
        agcModuleEnable = 1

    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.agcModuleEnable')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, agcModuleEnable, DUT_MemoryTypes.Default)


    #Number of samples
    value_ptr = DA.EvaluateSymbol('&HARNESS_INPUT.rxScpInputLen')
    DA.WriteMemoryBlock(value_ptr, 1, 4, numSamples, 0)

    #Operating Band width
    value_ptr = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.BAND_WIDTH')
    DA.WriteMemoryBlock(value_ptr, 1, 4, bandwidth, 0)

    ##print p20flag
    value_ptr = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.PRIM_20_OFFSET')
    DA.WriteMemoryBlock(value_ptr, 1, 4, p20flag, 0)

    ##print nrx_active
    value_ptr = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.TB_NRX')
    DA.WriteMemoryBlock(value_ptr, 1, 4, nrx_active, 0)
    ##print ntx_active
    value_ptr = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.TB_NTX')
    DA.WriteMemoryBlock(value_ptr, 1, 4, ntx_active, 0)
    ##print freq_band
    value_ptr = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.FREQ_BAND')
    DA.WriteMemoryBlock(value_ptr, 1, 4, freq_band, 0)
    ##print channelnum
    value_ptr = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.CHANNEL_NUM')
    DA.WriteMemoryBlock(value_ptr, 1, 4, channelnum, 0)

    DA.SelectTargetByPattern('MCU')
    value_ptr = DA.EvaluateSymbol('&TEST_PARAMS.OPERATION_MODE')
    DA.WriteMemoryBlock(value_ptr, 1, 4, 1, 0)

    retune_flag=1
    value_ptr = DA.EvaluateSymbol('&TEST_PARAMS.RETUNE')
    DA.WriteMemoryBlock(value_ptr, 1, 4, retune_flag, 0)

    value_ptr = DA.EvaluateSymbol('&HARNESS_OUTPUT.dut_ready')
    dut_ready = DA.ReadMemoryBlock(value_ptr, 1, -1, 0)[0]

    while(dut_ready==0):
        dut_ready = DA.ReadMemoryBlock(value_ptr, 1, -1, 0)[0]

    print 'DUT initializations are done'

    print 'Start the test case indication'
    value_ptr = DA.EvaluateSymbol('&TEST_PARAMS.TEST_START')
    DA.WriteMemoryBlock(value_ptr, 1, 4, 1, 0)

    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
    DA.WriteMemoryBlock(value, 1, 4, 0, 0)

    numSymProcess_addr = DA.EvaluateSymbol('&HARNESS_OUTPUT.numSymInProcess')
    DA.WriteMemoryBlock(numSymProcess_addr, 1, 1, 0, 0)

    value_ptr = DA.EvaluateSymbol('&TEST_PARAMS.START_NEXT_CASE')
    DA.WriteMemoryBlock(value_ptr, 1, 4, 1, 0)

    value_ptr = DA.EvaluateSymbol('&HARNESS_OUTPUT.dut_ready2')
    dut_ready2 = DA.ReadMemoryBlock(value_ptr, 1, -1, 0)[0]

    while(dut_ready2==0):
        dut_ready2 = DA.ReadMemoryBlock(value_ptr, 1, -1, 0)[0]

    timeout = time.time() + 60 # Waiting for time_out_value (seconds)
    while(dut_ready2==0):
        time.sleep(2)
        dut_ready2 = DA.ReadMemoryBlock(value_ptr, 1,  1, 0)[0]
        if time.time() > timeout:
            break
    # clearing inication for next cas to run
    DA.WriteMemoryBlock(value_ptr, 1, 1, 0, 0)

    print 'DUT2 initializations are done'


    if(playout_flag == 1):
        ##Configure clock dividers
        playout_functions.configRXPlayoutInputSel()
        playout_functions.configClock()
        print('Playout initialization')
        playout_functions.configRXPlayout(lna_model_enable)
        print('Writing samples into playout memory')
        playout_functions.writeSamples(inputSamples, numSamples, memoryType)
        playout_functions.deassertMemoryMap(memoryType)
        playout_functions.startPlayout(numSamples)
        playout_functions.pollPlayoutDone()
    else:
        print('Writing samples into debugiq register')
        writeDebugiqSamples(inputSamples)

    DA.SelectTargetByPattern('MCU')
    playout_done = 1
    value = DA.EvaluateSymbol('&HARNESS_INPUT.playoutDone')
    DA.WriteMemoryBlock(value, 1, 1, playout_done, 0)


    timeout_count=0
    stuck_state=0
##    while(1):
##        dut_done=DA.EvaluateSymbol('HARNESS_OUTPUT.DUT_DONE')
##        if dut_done==1:
##            print 'Indicating DUT process Done'
##            break

    address = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
    state = DA.ReadMemoryBlock(address, 1, 4, 0)[0]
    timeout = time.time() + 120
    if state == 1:
        print 'Indicating DUT process Done'
    while (int(state) != 1):
        time.sleep(2)
        state = DA.ReadMemoryBlock(address, 1, 4, 0)[0]
        if time.time() > timeout:
            break

    if (state != 1):
        # Check ED status. If ED status =0, call this fucntion.
            exitRxWait = DA.EvaluateSymbol('&TEST_PARAMS.EXIT_RX_WAIT')
            DA.WriteMemoryBlock(exitRxWait, 1, 4, 1, 0)
            address = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
            state = DA.ReadMemoryBlock(address, 1, 4, 0)[0]
            timeout = time.time() + 120
            while (int(state) != 1):
                time.sleep(2)
                state = DA.ReadMemoryBlock(address, 1, 4, 0)[0]
                if time.time() > timeout:
                    break

    print 'Clear DUT done indication'
    reset_val = 0
    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
    DA.WriteMemoryBlock(value, 1, 4, reset_val, 0)

    pktStatus, edStatus = getRXStats()
    print('Packet status is ' + pktStatus)

    address = DA.EvaluateSymbol('AGG.WLAN_MAC_CTRL_AGG_CPE_RESIDUAL_CFO')
    value = DA.ReadMemoryBlock(address, 1, 4, 0)
    residual_cfo = (value[0]>>8) & 0x0000FFFF
    fc = operatingBand + (channelnum * 5 * 1e6)

    cfo , cfoInKHz, total_cfo_khz = readRXVector(residual_cfo,fc)
    ##print('ED status is ' + edStatus)
    print ('********** Testing Done ***********')
    return cfo, cfoInKHz, residual_cfo, total_cfo_khz, pktStatus

def readRXVector(residual_cfo,fc):
    DA.SelectTargetByPattern('MCU')
    value_ptr = DA.EvaluateSymbol('&rxVectorParams')
    rxvector = DA.ReadMemoryBlock(value_ptr, 20, 4, 0)
    print(str(rxvector))
    dutCfo = rxvector[6] & 0x0000FFFF
    if(dutCfo > (pow(2,15) -1)):
        dutCfo = dutCfo - pow(2,16)
    dutCfoInKHz = ((dutCfo * fc)/pow(2,29))/1e3

    if(residual_cfo > (pow(2,15) -1)):
        residual_cfo = residual_cfo - pow(2,16)
    residual_cfo_khz = ((residual_cfo * fc)/pow(2,29))/1e3

    total_cfo_khz = dutCfoInKHz + residual_cfo_khz
    return dutCfo, dutCfoInKHz, total_cfo_khz


def writeDebugiqSamples(data):
    """" Write  IQ samples into the SPC register"""
    DA.SelectTargetByPattern('MCU')

    scpCntrlval= 0x02870000
    scpCntrlreg = DA.EvaluateSymbol('SCP.SCP_CONTROL')
    DA.WriteMemoryBlock(scpCntrlreg, 1, DUT_ElementTypes.typeUnsigned32bit, scpCntrlval, DUT_MemoryTypes.Default)
    for i in range(len(data)):
        value = DA.EvaluateSymbol('SCP.SCP_STATUS')
        scp_status = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
        inputSampleEnable =  (scp_status[0] & 0x8000000) >> 27
        while(inputSampleEnable != 1):
            value = DA.EvaluateSymbol('SCP.SCP_STATUS')
            scp_status = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
            inputSampleEnable =  (scp_status[0] & 0x8000000) >> 27
            if(inputSampleEnable == 1):
                break
        value = DA.EvaluateSymbol('SCP.SCP_INPUT_SAMPLE')
        DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, data[i], DUT_MemoryTypes.Default)


def getRXStats():
    """" Get RX stats from Harness """
    DA.SelectTargetByPattern('MCU')
    value_ptr = DA.EvaluateSymbol('rx_stats')
    rxStatLength = 30
    rxStats = DA.ReadMemoryBlock(value_ptr, rxStatLength,  4, 0)
    print(rxStats)
    if (rxStats[1] >= 1):
        status = 'OFDM PACKET CRC_PASS'
    elif (rxStats[2] >= 1):
        status = 'OFDM PACKET CRC_FAIL/RX OTHER FAIL'
    elif (rxStats[3] >= 1):
        status = 'DSSS PACKET CRC_PASS'
    elif (rxStats[4] >= 1):
        status = 'DSSS PACKET CRC_FAIL'
    else:
        status = 'RX_OTHER_FAIL//RX OTHER FAIL'

    edStatus = rxStats[0]

    return status, edStatus


def clearRxStats():
    """" clear RX stats values in Harness """
    rxStatLength = 12
    value = [0]*rxStatLength
    DA.SelectTargetByPattern('MCU')
    value_ptr = DA.EvaluateSymbol('rx_stats')
    DA.WriteMemoryBlock(value_ptr, rxStatLength, 4, value, 0)

def setRXInputLength(length):
    """" Get RX input length """
    value = DA.EvaluateSymbol('&HARNESS_INPUT.rxScpInputLen')
    DA.WriteMemoryBlock(value, 1, 4, length, 0)


def loadProgramFile():
    """ Load HARNESS program file """
    harnessFile = "../harness/loader/build/smake/release_MIPSGCC/HARNESS.py"
    ##harnessFile = "../harness_mac/loader/build/smake/release_MIPSGCC/HARNESS.py"
    DA.LoadProgramFile(harnessFile, ShowProgress = True)

def runTarget():
    """ run target """
    print('RUNNING TARGET')
    DA.Run()
    while(1):
        if (DA.IsRunning() == False):
            DA.Run()
            time.sleep(3)
        if (DA.IsRunning() == True):
            break

def main(argv):

    if len(sys.argv) < 4:
    	print("The script takes atleast 2 input arguments:  1. Input single test case file full absolute path")
        print("                                             2. Target type Simulator/SysProbe/DA-net etc...")
        print("                                             3. Target name/number rpusim-echo520-main@393-internal_config0057/288 etc...")
        print("Exiting with error code -1")
    	return -1

    if os.path.isdir(str(sys.argv[1])) == False:
        print("The script takes atleaset one valid directory name")
        print("Exiting with error code -2")
    	return -2


    target_name = "{} {}".format(str(sys.argv[2]), str(sys.argv[3]))


    '''Start function'''
    probe = None
    if codescape.environment == 'standalone':
        #from CSUtils import DA
        try:
            DA.UseTarget(target_name)
        except:
            print('Not selected valid target')
            print("Exiting with error code -2")
            return -2

    target_info = DA.GetTargetInfo()
    print(str(target_info))

    DA.HardReset()
    loadProgramFile()
    runTarget()

    DA.SelectTargetByPattern('MCU')
    print('Running Target')
    DA.Run()
    time.sleep(3)
##    testcasedir = str(sys.argv[1])
##    print(testcasedir)
    totaltests = 1
    maindir = str(sys.argv[1])
    for i in range(1, totaltests+1):
        if totaltests == 1:
            cfo, cfoInKHz, residual_cfo, total_cfo_khz, pktStatus = testing_start(maindir)
            print([pktStatus ,cfoInKHz, total_cfo_khz])
        else:
            subdir = 'set_system_467_B0_29Jun_' + str(i)
            testcasedir = os.path.join(maindir, subdir)
            print(testcasedir)
            if os.path.isdir(testcasedir):
                print(testcasedir)
                cfo, cfoInKHz, residual_cfo, total_cfo_khz, pktStatus = testing_start(testcasedir)
                debugPrint(pktStatus, maindir)
                debugPrint("For packet " + str(i) + " : residualcfoInPPM is " + str(residual_cfo) + "& totalcfoInKHz is " + str(total_cfo_khz), maindir)

def debugPrint(string, maindir):
    """ Log the string to debug log file """
    print(string)
    debug_log_file = os.path.join(maindir, 'debug.log')
    #debug_log_file = os.path.join(os.getcwd(), 'debug.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()

if __name__ == "__main__":
    if codescape.environment == 'codescape':
        print "User script is not allowed"
        time.sleep(3)
        sys.exit()
    main(sys.argv[1:])
