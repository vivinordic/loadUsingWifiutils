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
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py  "../testvectors/lg"  "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py  "../testvectors/HESU_3x1_AWGN_2GI_2xHELTF"  "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py  "../testvectors/HESU_3x1_TGnD_2GI_2xHELTF"  "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py  "../testvectors/HESU_4x1_AWGN_2GI_2xHELTF"  "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py  "../testvectors/HESU_4x1_TGnD_2GI_2xHELTF"  "Simulator" "rpusim-rpu530-main@210-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py  "../testvectors/lg"  "SysProbe" "62"
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
import playout_functions


def testing_start(test_case_dir):


    #Reading I&Q samples from file and store into the buffer
    inputFilePath = os.path.abspath(test_case_dir)
    file_adc_out_real = os.path.join(inputFilePath, 'adc1OutputReal.txt')
    file_adc_out_imag = os.path.join(inputFilePath, 'adc1OutputImag.txt')

    file_real = open(file_adc_out_real, 'r')
    data_real = []
    data_real = file_real.readlines()
    file_imag = open(file_adc_out_imag, 'r')
    data_imag = []
    data_imag = file_imag.readlines()
    s_index = 0
    scp_in_int = []
    memoryType   = 'shared'
    if(memoryType == 'shared'):
        for s_index in range(len(data_real)):
            temp_scp_in = int(data_real[s_index][0:3] + '0' + data_imag[s_index][0:3] + '0', 16)
            scp_in_int.append(temp_scp_in)

    #Add silence period
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

    DA.SelectTargetByPattern('MCU')
    print('Initializing system parameters')

   # Configure clock dividers
    playout_functions.configRXPlayoutInputSel()
    playout_functions.configClock()

    print('Playout initialization')
    lna_model_enable = 'NO'
    playout_functions.configRXPlayout(lna_model_enable)

    print('Writing samples into playout memory')
    playout_functions.writeSamples(inputSamples, numSamples, memoryType)
    playout_functions.deassertMemoryMap(memoryType)
    playout_functions.startPlayout(numSamples)


    playout_functions.pollPlayoutDone()


    print ('********** Testing Done ***********')


def loadProgramFile():
    """ Load HARNESS program file """
    harnessFile = "../harness/loader/build/smake/release_MIPSGCC/HARNESS.py"
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

    #DA.HardReset()
    #loadProgramFile()
    #runTarget()

    DA.SelectTargetByPattern('MCU')
    print('Running Target')
    #DA.Run()
    time.sleep(3)
    #for  i in range(0, 1):
    testing_start(str(sys.argv[1]))

if __name__ == "__main__":
    if codescape.environment == 'codescape':
        print "User script is not allowed"
        time.sleep(3)
        sys.exit()
    main(sys.argv[1:])
