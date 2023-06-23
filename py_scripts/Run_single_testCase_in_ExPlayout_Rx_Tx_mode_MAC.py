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
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py "../testvectors/testcase_0001" "Simulator" "rpusim-rpu530-main@118-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Rx_mode_MAC.py  "../testvectors/testcase_0001_lg" "Simulator" "rpusim-rpu530-main@118-internal_config0077"
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

######################################
g_datarate = [12, 18, 24, 36, 48, 72, 96, 108]
n_ac_datarate = [0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f]
dsss_datarate = [2, 4, 11, 22]

######################################


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

    #SCP input samples pointer
    inputSamples = scp_in_int;

    #Number of samples
    numSamples   = len(data_real);

    DA.SelectTargetByPattern('MCU')
    print('Initializing system parameters')

   # Configure clock dividers
    playout_functions.configClock()

    print('Playout initialization')
    lna_model_enable = 'NO'
    playout_functions.configRXPlayout(lna_model_enable)

    print('Writing samples into playout memory')
    playout_functions.writeSamples(inputSamples, numSamples, memoryType)
    playout_functions.deassertMemoryMapAck(memoryType)
    playout_functions.startPlayout(numSamples)


    playout_functions.pollPlayoutDone()
    #?? Change this sleep to poll for PO_MEM_CAP_MODE=1 (i.e. detect that mode has automatically switch to capture)
    playout_functions.pollCaptureReady4Ack()

    print ('********** RX Testing Done ***********')


def debugPrint(string):
    """ Log the string to debug log file """
    print string


def dumpTXOutSamples(outBuffer, samples2Read):
    """ Dump capture memory samples to text file """
    dirName = os.path.abspath('../DUT_dumps')
    if not os.path.exists(dirName):
        os.makedirs(dirName)

    outFileReal =  "../DUT_dumps/txscp_output_real.txt"
    outFileImag =  "../DUT_dumps/txscp_output_imag.txt"

    foReal = open(outFileReal, "w")
    foImag = open(outFileImag, "w")

    for index in range(0,samples2Read):
        samplesOutReal = (outBuffer[index]>>20)
        samplesOutImag = ((outBuffer[index]>>4) & 0xfff)
        foReal.write('%03X\n' %samplesOutReal)
        foImag.write('%03X\n' %samplesOutImag)

    foReal.close()
    foImag.close()

def calculateSqnr(outBuffer, samples2Read, test_case_dir):
    dutOutComplex = outBuffer
    nc = []
    signalPower = 0
    noisePower  = 0

    inputFilePath = os.path.abspath(test_case_dir)
    realOutFile = os.path.join(inputFilePath, 'matlabTxScp1OutputReal.txt')
    imagOutFile = os.path.join(inputFilePath, 'matlabTxScp1OutputImag.txt')


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

    print(signalPower)
    print(noisePower)
    if (signalPower <= 0):
            signalPower = 1

    if (noisePower <= 0):
            noisePower = 1

    sqnrValue = 10*log(signalPower/noisePower, 10)
    return sqnrValue



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


    for  i in range(0, 1):

        #print('tx parameters configuration completed')
        #playout_functions.configTXCapture()
        #samples2Read = 0x2000000
        #playout_functions.startCapture(samples2Read)
        time.sleep(5)
        samples2Read =playout_functions.getNumSamplesCaptured()
        debugPrint(samples2Read)
        outBuffer = playout_functions.readCaptureMemory(samples2Read)
        dumpTXOutSamples(outBuffer, samples2Read)
        ##sqnrValue = calculateSqnr(outBuffer, samples2Read, str(sys.argv[1]))
        ##print("SQNR value is "+ str(sqnrValue))
        time.sleep(10)
        DA.SelectTargetByPattern('MCU')
        time.sleep(5)
        print(' TX test is completed')

        tx_state_str = '********* DUT done event recieved  *********'
        print(tx_state_str)



if __name__ == "__main__":
    if codescape.environment == 'codescape':
        print "User script is not allowed"
        time.sleep(3)
        sys.exit()
    main(sys.argv[1:])
