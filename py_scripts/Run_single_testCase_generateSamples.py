#-------------------------------------------------------------------------------
# Name:        Run_single_testCase_generateSamples.py.py
# Purpose:     This is the main file to be run single test case for Harness testing in TX mode.
#              TestMode:  PlayoutMode: EXTERNAL.
# Author:      Imagination Technologies
#
# Created:     2019
# Copyright:   (c) 2019, Imagination Technologies Ltd.
#-------------------------------------------------------------------------------
""" To run use command
    Command: python Run_single_testCase_generateSamples.py "../payLoad/lg" "../testvectors/lg" "Simulator" "rpusim-rpu530-main@196-internal_config0077"
    Command: python Run_single_testCase_generateSamples.py "../payload/mf" "../testvectors/mf" "Simulator" "rpusim-rpu530-main@196-internal_config0077"
    Command: python Run_single_testCase_generateSamples.py "../payload/vht" "../testvectors/vht" "Simulator" "rpusim-rpu530-main@196-internal_config0077"
    Command: python Run_single_testCase_generateSamples.py "../payload/hesu" "../testvectors/hesu" "Simulator" "rpusim-rpu530-main@196-internal_config0077"
    Command: python Run_single_testCase_generateSamples.py "../payload/heersu" "../testvectors/heersu" "Simulator" "rpusim-rpu530-main@196-internal_config0077"
    Command: python Run_single_testCase_generateSamples.py "../payload/dsss" "../testvectors/dsss" "Simulator" "rpusim-rpu530-main@196-internal_config0077"
                                                           
    Command: python Run_single_testCase_generateSamples.py "../payload/lg" "../testvectors/lg" "SysProbe" "270"
    Command: python Run_single_testCase_generateSamples.py "../payload/mf" "../testvectors/mf" "SysProbe" "270"
    Command: python Run_single_testCase_generateSamples.py "../payload/vht" "../testvectors/mf" "SysProbe" "270"
    Command: python Run_single_testCase_generateSamples.py "../payload/hesu" "../testvectors/hesu" "SysProbe" "270"
    Command: python Run_single_testCase_generateSamples.py "../payload/heersu" "../testvectors/heersu" "SysProbe" "270"
    Command: python Run_single_testCase_generateSamples.py "../payload/dsss" "../testvectors/dsss" "SysProbe" "270"
"""

'''Codescape load script'''
import array
import os
import time
import struct
import sys
import time
from math import log
from imgtec import codescape
from imgtec.codescape.da_types import LoadType
#from CSUtils import DA
from data_type_utils import *
import playout_functions




######################################
g_datarate = [12, 18, 24, 36, 48, 72, 96, 108]
n_ac_datarate = [0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f]
dsss_datarate = [2, 4, 11, 22]

######################################
class TXPARAMS_VARIABLE:
    """Class for results vairables"""
    test_case_count =1
    obw             =0
    sbw             =0
    channel_offset  =0
    FrameFormat     =1
    mcs             =0
    pl_len          =100
    ntx             =1
    nss             =1
    stbc            =0
    ldpc            =0
    aggre           =0
    sgi             =0

    def __init__(self):
        self.test_case_count =1
        self.obw             =0
        self.sbw             =0
        self.channel_offset  =0
        self.FrameFormat     =1
        self.mcs             =0
        self.pl_len          =100
        self.ntx             =1
        self.nss             =1
        self.stbc            =0
        self.ldpc            =0
        self.aggre           =0
        self.sgi             =0


DUT_MemoryTypes      = MemoryTypes()
DUT_ElementTypes     = ElementTypes()
txparams_variables   = TXPARAMS_VARIABLE()

dataBytes = []

# TX parameters configuration
# per packet based parameters
# able changes the parameters appropriatly and re-run test case
# below configurations are tx parametes as well as system parameters

def configTXParams(test_case_dir):

    global txparams_variables
    prepare_params=[]
    system_params=[]
    data = []

    #Per Packets Configuration Parameters ( MAIN PARAMETERS)
    FRAME_FORMAT      = 1    #DSSS= 0, LG=1, MF=2, GF=3, VHT=4, HESU=5 and HEERSU = 7
    RATE_R_MCS_INDEX  = 0     ##rate_or_index     #LG=0to7,MF&GF=0to8,VHT=0to9
    AGGREATION_ENABLE = 0    #ENABLE = 1, DISABLE = 0

    #Reading payload bytes  from file and store into the buffer
    inputFilePath = os.path.abspath(test_case_dir)
    file_payload = os.path.join(inputFilePath, 'mac_payload.txt')
    payloadFile = open(file_payload, 'r')
    data = payloadFile.readlines()
    MPDU_LENGTH = len(data)
    data_list = []
    for i in range(MPDU_LENGTH):
      data_temp= int(data[i], 16)
      data_list.append(data_temp)

    # System Configuration Parameters
    FREQUENCY_BAND  = 2.4   #Frequency band =5.0/2.4
    N_TX            = 1     # N transmission antennas = 1/2
    N_RX            = 1     # N receiving antennas = 1/2
    CHAIN_SELECTION = 1     # Chain Selection 1/2

    #Per Packets Configuration Parameters ( MAIN PARAMETERS)
    CHANNEL_BW        = 0    #20MHZ= 0, 40MHZ =1, 80MHZ=2
    SIGNAL_BW         = 0    #20MHZ= 0, 40MHZ =1, 80MHZ=2
    OFFSET_BW         = 0    #20 LOWER =-1 20UPPER =1, BAND0 =-2, BAND1 =-1 BAND2 =1 BAND3=-2
    STBC_ENABLE       = 0    #ENABLE = 1, DISABLE = 0
    LDPC_ENABLE       = 0    #ENABLE = 1, DISABLE = 0
    NUM_MPDUS         = 1    #NUMBER OF MPDU 1 to 64 ( but for testing perpose only 1 recomended)
    SHORT_GI          = 0    #ENABLE = 1, DISABLE = 0
    NUM_STREAMS       = 1    #SPACIAL STREAMS =1/2 depends on N_TX and STBE
    NDP_ENABLE        = 0    #ENABLE = 1, DISABLE = 0 ( for tesing perpose not support)
    #===========================================================

    if(FRAME_FORMAT == 0 or FRAME_FORMAT == 1):
        mode = 0
    elif(FRAME_FORMAT == 2 or FRAME_FORMAT == 3):
        mode = 0x8
    elif(FRAME_FORMAT == 4 ):
        mode = 0x10
    elif(FRAME_FORMAT == 5):
        mode = 0x18
    elif(FRAME_FORMAT == 6):
        mode = 0x20
    elif(FRAME_FORMAT == 7):
        mode = 0x28
    elif(FRAME_FORMAT == 8):
        mode = 0x30
    else:
        print 'Wrong Format'

    #1) ENABLE_11G_MODE = 0,  ENABLE_11N_MODE = 0x8,  ENABLE_11AC_MODE= 0x10
    prepare_params.append(mode)

    #2) ENABLE_20_MHZ = 0 , ENABLE_40_MHZ = 0x1, ENABLE_80_MHZ = 0X2
    prepare_params.append(SIGNAL_BW)
    #3) BAND1 = 0,  BAND2,  BAND3,  BAND4, FULL
    primary_band = 4
    prepare_params.append(primary_band)

    if(FREQUENCY_BAND==2.4):
        channel_num=11
        FREQUENCY_BAND=0
    elif(FREQUENCY_BAND==5.0):
        FREQUENCY_BAND=1
        channel_num=36
    else:
        print "Wrong frequency band"

    payload_length = MPDU_LENGTH
    #4) Payload Length
    prepare_params.append(payload_length)

    #TB_ONE_MBPS = 2, TB_TWO_MBPS = 4, TB_FIVEPTFIVE_MBPS = 11, TB_ELEVEN_MBPS = 22, TB_SIX_MBPS = 12,
	#TB_NINE_MBPS = 18, TB_TWELEVE_MBPS = 24, TB_EIGHTEEN_MBPS = 36, TB_TWENTY_FOUR_MBPS = 48, TB_THIRTY_SIX_MBPS = 72,
	#TB_FOURTYEIGHT_MBPS = 96, TB_FIFTYFOUR_MBPS = 108, TB_MCS0 = 0x80, TB_MCS1 = 0x81, TB_MCS2 = 0x82, TB_MCS3 = 0x83,
	#TB_MCS4 = 0x84, TB_MCS5 = 0x85, TB_MCS6 = 0x86, TB_MCS7 = 0x87, TB_MCS8 = 0x88, TB_MCS9 = 0x89, TB_MCS10 = 0x8a,
	#TB_MCS11 = 0x8b, TB_MCS12 = 0x8c, TB_MCS13 = 0x8d, TB_MCS14 = 0x8e, TB_MCS15 = 0x8f

    if(FRAME_FORMAT==0):
        rate_r_mcs =  dsss_datarate[RATE_R_MCS_INDEX]
    if(FRAME_FORMAT==1):
        rate_r_mcs =  g_datarate[RATE_R_MCS_INDEX]

    if((FRAME_FORMAT==2 or FRAME_FORMAT==3) and RATE_R_MCS_INDEX == 32):
        rate_r_mcs =n_ac_datarate[0]
    elif(FRAME_FORMAT==2 or FRAME_FORMAT==3 or FRAME_FORMAT==4 ):
        rate_r_mcs =n_ac_datarate[RATE_R_MCS_INDEX]

    elif(FRAME_FORMAT >= 5):
        rate_r_mcs = n_ac_datarate[RATE_R_MCS_INDEX]


    #5) Data rate or MCS
    prepare_params.append(rate_r_mcs)

    #6) SGI_DISABLE = 0x0, SGI_ENABLE  = 0x1
    prepare_params.append(SHORT_GI)

    #7) Number of streams
    prepare_params.append(NUM_STREAMS)

    #8) ENABLE = 1, DISABLE =  0
    prepare_params.append(STBC_ENABLE)

    #9) ENABLE = 1, DISABLE =  0
    prepare_params.append(LDPC_ENABLE)

    enable_green_field = 0
    #10) ENABLE = 1, DISABLE =  0
    prepare_params.append(enable_green_field)

    #11) Aggregation : ENABLE = 1, DISABLE =  0
    prepare_params.append(AGGREATION_ENABLE)

    #12) Number of MPDUs
    prepare_params.append(NUM_MPDUS)

    beamforming_enable = 0
    #13) ENABLE = 1, DISABLE =  0
    prepare_params.append(beamforming_enable)

    #14) Number of transmitting antennas
    prepare_params.append(N_TX)


    tx2tx_enable =0
    #15) tx2tx flag enable, default setting zero, need to add how to do from xls
    prepare_params.append(tx2tx_enable)
    enable_mcs32 =0
    #16) enable_mcs32 flag enable, default setting zero, need to add how to do from xls
    prepare_params.append(enable_mcs32)

    sounding_enable = 1
    #17) not sounding bit setting
    prepare_params.append(sounding_enable)

    smoothing_enable = 1
    #18) smoothing enable
    prepare_params.append(smoothing_enable)

    #19) TxPower
    txpower=20
    prepare_params.append(txpower)

    num_mode_params=19
    value = DA.EvaluateSymbol('&tx_params.MODE')
    DA.WriteMemoryBlock(value,  num_mode_params, DUT_ElementTypes.typeSigned32bit, prepare_params,DUT_MemoryTypes.Default )

    #21 partial_aid
    partial_aid = 0
    value = DA.EvaluateSymbol('&tx_params.partial_aid')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, partial_aid, DUT_MemoryTypes.Default )

    #22 no_signal_extension
    no_signal_extension = 1
    value = DA.EvaluateSymbol('&tx_params.no_signal_extension')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, no_signal_extension, DUT_MemoryTypes.Default )

    #23 TX_OP_duration;
    TX_OP_duration = 0
    value = DA.EvaluateSymbol('&tx_params.TX_OP_duration')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned16bit, TX_OP_duration, DUT_MemoryTypes.Default )

    #24 DCM
    DCM = 0
    value = DA.EvaluateSymbol('&tx_params.DCM')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, DCM, DUT_MemoryTypes.Default )


    #25 doppler;
    doppler = 0
    value = DA.EvaluateSymbol('&tx_params.doppler')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, doppler, DUT_MemoryTypes.Default )

    #26 packet_padding
    packet_padding = 0
    value = DA.EvaluateSymbol('&tx_params.packet_padding')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, packet_padding, DUT_MemoryTypes.Default )

    #27 HE_LTF_type
    HE_LTF_type = 0
    value = DA.EvaluateSymbol('&tx_params.HE_LTF_type')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, HE_LTF_type, DUT_MemoryTypes.Default )

    #28 bss_color;
    bss_color = 0
    value = DA.EvaluateSymbol('&tx_params.bss_color')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, bss_color, DUT_MemoryTypes.Default )

    #29 uplink_flag
    uplink_flag = 0
    value = DA.EvaluateSymbol('&tx_params.uplink_flag')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, uplink_flag, DUT_MemoryTypes.Default )

    #30 midamble_periodicity
    midamble_periodicity = 10
    value = DA.EvaluateSymbol('&tx_params.midamble_periodicity')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, midamble_periodicity, DUT_MemoryTypes.Default )


	#31 trigger_responding;
    trigger_responding = 0
    value = DA.EvaluateSymbol('&tx_params.trigger_responding')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, trigger_responding, DUT_MemoryTypes.Default )

    #32 ldpc_extra_symbol
    ldpc_extra_symbol = 0
    value = DA.EvaluateSymbol('&tx_params.ldpc_extra_symbol')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, ldpc_extra_symbol, DUT_MemoryTypes.Default )

    #33 RU_allocation
    RU_allocation = 192
    value = DA.EvaluateSymbol('&tx_params.RU_allocation')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, RU_allocation, DUT_MemoryTypes.Default )

    #34 HE_LTF_mode;
    HE_LTF_mode = 0
    value = DA.EvaluateSymbol('&tx_params.HE_LTF_mode')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, HE_LTF_mode, DUT_MemoryTypes.Default )

    #35 num_HE_LTF
    num_HE_LTF = 1
    value = DA.EvaluateSymbol('&tx_params.num_HE_LTF')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, num_HE_LTF, DUT_MemoryTypes.Default )


    #37 heSigA2Reserved;
    heSigA2Reserved = 0
    value = DA.EvaluateSymbol('&tx_params.heSigA2Reserved')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, heSigA2Reserved, DUT_MemoryTypes.Default )

    #38 starting_sts
    starting_sts = 0
    value = DA.EvaluateSymbol('&tx_params.starting_sts')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, starting_sts, DUT_MemoryTypes.Default )

    #39 trigger_method
    trigger_method = 0
    value = DA.EvaluateSymbol('&tx_params.trigger_method')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, trigger_method, DUT_MemoryTypes.Default )

    #40 PE_duration;
    PE_duration = 0
    value = DA.EvaluateSymbol('&tx_params.PE_duration')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, PE_duration, DUT_MemoryTypes.Default )

    #41 feedback_status
    feedback_status = 0
    value = DA.EvaluateSymbol('&tx_params.feedback_status')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, feedback_status, DUT_MemoryTypes.Default )

    #42 RU_tone_index
    RU_tone_index = 0
    value = DA.EvaluateSymbol('&tx_params.RU_tone_index')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, RU_tone_index, DUT_MemoryTypes.Default )


    #43 HETB_PE_disambiguity;
    HETB_PE_disambiguity = 0
    value = DA.EvaluateSymbol('&tx_params.HETB_PE_disambiguity')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, HETB_PE_disambiguity, DUT_MemoryTypes.Default )

    #44 L_length
    L_length = 0
    value = DA.EvaluateSymbol('&tx_params.L_length')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, L_length, DUT_MemoryTypes.Default )

    #45 pre_fec_padding
    pre_fec_padding = 0
    value = DA.EvaluateSymbol('&tx_params.pre_fec_padding')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, pre_fec_padding, DUT_MemoryTypes.Default )

    #46 CFO;
    CFO = 0
    value = DA.EvaluateSymbol('&tx_params.CFO')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned32bit, CFO, DUT_MemoryTypes.Default )

    #47 SFO
    SFO = 0
    value = DA.EvaluateSymbol('&tx_params.SFO')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned32bit, SFO, DUT_MemoryTypes.Default )

    #48 non_ht_cbw
    non_ht_cbw = 0
    value = DA.EvaluateSymbol('&tx_params.non_ht_cbw')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeUnsigned8bit, non_ht_cbw, DUT_MemoryTypes.Default )

    #System parameters Configuration
    primary_flag = 0
    system_params.append(CHANNEL_BW)
    system_params.append(primary_flag)
    system_params.append(N_RX)
    system_params.append(N_TX)
    system_params.append(FREQUENCY_BAND)
    system_params.append(channel_num)
    system_params.append(CHAIN_SELECTION)
    system_params_length = 7
    address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.BAND_WIDTH')
    DA.WriteMemoryBlock(address,system_params_length, DUT_ElementTypes.typeSigned32bit , system_params, DUT_MemoryTypes.Default)
    return data_list


def startTestcase():
    """" Enable start next case in TEST_PARAMS """
    debugPrint("Starting the Test")
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.TEST_START')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

def startNextCase():
    """" Enable start next case in TEST_PARAMS """
    debugPrint("Starting the Next case")
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.START_NEXT_CASE')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

def updateTXParams():
    """" Enable TX_PARAMS_UPDATION in TEST_PARAMS """
    tx_params_updation =1
    value = DA.EvaluateSymbol('&TEST_PARAMS.TX_PARAMS_UPDATION')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, tx_params_updation , DUT_MemoryTypes.Default)

def enableRetune():
    """" Enable retune in TEST_PARAMS """
    retune = 1
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.RETUNE')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, retune, DUT_MemoryTypes.Default)

def wait4DutDone(time_out_value):
    """ Wait for HARNESS_OUTPUT.DUT_DONE indication is set from harness to know the test case is done
    """
    address = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
    state = DA.ReadMemoryBlock(address, 1, DUT_ElementTypes.typeSigned32bit, DUT_MemoryTypes.Default)[0]
    timeout = time.time() + time_out_value
    while (int(state) != 1):
        time.sleep(5)
        state = DA.ReadMemoryBlock(address, 1, DUT_ElementTypes.typeSigned32bit, DUT_MemoryTypes.Default)[0]
        if time.time() > timeout:
            break

    return state

def clearTestDoneIndication():
    """" Clear DUT done indication """
    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

    numSymProcess_addr = DA.EvaluateSymbol('&HARNESS_OUTPUT.numSymInProcess')
    DA.WriteMemoryBlock(numSymProcess_addr, 1, DUT_ElementTypes.typeUnsigned8bit, 0, DUT_MemoryTypes.Default)

def pollSystemReady():
    """" Check whether Harness has reached master wait """
    valuePtr = DA.EvaluateSymbol('&HARNESS_OUTPUT.dut_ready')
    dutReady = DA.ReadMemoryBlock(valuePtr, 1, DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]

    while(dutReady==0):
        time.sleep(5)
        dutReady = DA.ReadMemoryBlock(valuePtr, 1, DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]

    DA.WriteMemoryBlock(valuePtr, 1, DUT_ElementTypes.typeUnsigned8bit, 0, DUT_MemoryTypes.Default)

def pollTestReady(time_out_value):
    """" Check whether Harness has entered test loop """
    value_ptr = DA.EvaluateSymbol('&HARNESS_OUTPUT.dut_ready2')
    dut_ready2 = DA.ReadMemoryBlock(value_ptr, 1,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]
    timeout = time.time() + time_out_value # Waiting for time_out_value (seconds)
    while(dut_ready2==0):
        time.sleep(5)
        dut_ready2 = DA.ReadMemoryBlock(value_ptr, 1,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]
        if time.time() > timeout:
            break
    # clearing inication for next cas to run
    DA.WriteMemoryBlock(value_ptr, 1, DUT_ElementTypes.typeUnsigned8bit, 0, DUT_MemoryTypes.Default)


def debugPrint(string):
    """ Log the string to debug log file """
    print string


def dumpTXOutSamples(outBuffer, samples2Read, test_case_dir):
    """ Dump capture memory samples to text file """

    outputFilePath = os.path.abspath(test_case_dir)
    outFileReal = os.path.join(outputFilePath, 'adc1OutputReal.txt')
    outFileImag = os.path.join(outputFilePath, 'adc1OutputImag.txt')

    foReal = open(outFileReal, "w")
    foImag = open(outFileImag, "w")

    for index in range(0,samples2Read):
        samplesOutReal = (outBuffer[index]>>20)
        samplesOutImag = ((outBuffer[index]>>4) & 0xfff)
        foReal.write('%03X\n' %samplesOutReal)
        foImag.write('%03X\n' %samplesOutImag)

    foReal.close()
    foImag.close()


def loadProgramFile():
    """ Load HARNESS program file """
    harnessFile = "../harness/loader/build/smake/release_MIPSGCC/HARNESS.py"
    DA.LoadProgramFile(harnessFile, ShowProgress = True)

def runTarget():
    """ run target """
    debugPrint('RUNNING TARGET')
    DA.Run()
    while(1):
        if (DA.IsRunning() == False):
            DA.Run()
            time.sleep(3)
        if (DA.IsRunning() == True):
            break

def feedPayload(dataBytes):
    """ Feed payload bytes to Harness """
    TX_VECTOR_SIZE = 42
    DA.SelectTargetByPattern('MCU')
    value_ptr = DA.EvaluateSymbol('tx_payload_buff')
    DA.WriteMemoryBlock(value_ptr + TX_VECTOR_SIZE, len(dataBytes), DUT_ElementTypes.typeUnsigned8bit, dataBytes, DUT_MemoryTypes.Default)

def main(argv):


    if len(sys.argv) < 4:
    	print("The script takes atleast 3 input arguments:  1. Input single test case file full absolute path")
        print("                                             2. Target type Simulator/SysProbe/DA-net etc...")
        print("                                             3. Target name/number rpusim-echo520-main@393-internal_config0057/288 etc...")
        print("Exiting with error code -1")
    	return -1

    if os.path.isdir(str(sys.argv[1])) == False:
        print("The script takes atleaset one valid directory name for payload ")
        print("Exiting with error code -2")
    	return -2

    if os.path.isdir(str(sys.argv[2])) == False:
        print("The script takes atleaset one valid directory name for samples")
        print("Exiting with error code -2")
    	return -2

    target_name = "{} {}".format(str(sys.argv[3]), str(sys.argv[4]))


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
    debugPrint(str(target_info))

    DA.HardReset()
    loadProgramFile()
    runTarget()

    DA.SelectTargetByPattern('MCU')
    print('Running Target')
    DA.Run()
    time.sleep(3)

   # Configure clock dividers
    playout_functions.configClock()

    DA.SelectTargetByPattern('MCU')
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.OPERATION_MODE')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

    startTestcase()

    for  i in range(0, 1):
        enableRetune()
        dataBytes = configTXParams(str(sys.argv[1]))
        feedPayload(dataBytes)
        updateTXParams()
        #print('tx parameters configuration completed')
        playout_functions.configTXCapture()
        samples2Read = 0x2000000
        playout_functions.startCapture(samples2Read)
        clearTestDoneIndication()
        startNextCase()
        pollTestReady(60)
        state = wait4DutDone(120)
        debugPrint("DUT done state is " + str(state))
        samples2Read = playout_functions.getNumSamplesCaptured()
        debugPrint(samples2Read)
        outBuffer = playout_functions.readCaptureMemory(samples2Read)
        dumpTXOutSamples(outBuffer, samples2Read,str(sys.argv[2]))
        time.sleep(10)
        DA.SelectTargetByPattern('MCU')
        time.sleep(5)
        print(' TX test is completed')

        if state==1:
            tx_state_str = '********* DUT done event recieved  *********'
        else:
            tx_state_str = '********* DUT done event is not recieved  *********'
        print(tx_state_str)


if __name__ == "__main__":
    main(sys.argv[1:])
