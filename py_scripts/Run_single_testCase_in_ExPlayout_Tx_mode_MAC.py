#-------------------------------------------------------------------------------
# Name:        Run_single_testCase_in_ExPlayout_Tx_mode.py
# Purpose:     This is the main file to be run single test case for Harness testing in TX mode.
#              TestMode:  PlayoutMode: EXTERNAL.
# Author:      Imagination Technologies
#
# Created:     2019
# Copyright:   (c) 2019, Imagination Technologies Ltd.
#-------------------------------------------------------------------------------
""" To run use command
    Command: python Run_single_testCase_in_ExPlayout_Tx_mode.py "../MATLAB_dumps/lg" "Simulator" "rpusim-rpu530-main@118-internal_config0077"
    Command: python Run_single_testCase_in_ExPlayout_Tx_mode.py "../MATLAB_dumps/lg" "SysProbe" "270"
"""

'''Codescape load script'''
import array
import os
import time
import struct
import sys
import time
from math import log

import playout_functions



from imgtec import codescape
from imgtec.codescape.da_types import LoadType
#from CSUtils import DA


######################################
g_datarate = [12, 18, 24, 36, 48, 72, 96, 108]
n_ac_datarate = [0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f]
dsss_datarate = [2, 4, 11, 22]

######################################

class ElementTypes(object):
    """
    MTP Element Types:
    ===== ==============
    Value Element Type
    ===== ==============
     1    unsigned 8-bit
     2    unsigned 16-bit
     4    unsigned 32-bit
     8    unsigned 64-bit
    -1    signed 8-bit
    -2    signed 16-bit
    -4    signed 32-bit
    -8    signed 64-bit
    32    32-bit floating point
    64    64-bit floating point (double)
    ===== ==============
    """
    # Integer Types
    typeUnsigned8bit  =  1
    typeUnsigned16bit =  2
    typeUnsigned32bit =  4
    typeUnsigned64bit =  8
    typeSigned8bit    = -1
    typeSigned16bit   = -2
    typeSigned32bit   = -4
    typeSigned64bit   = -8

    # Floating Point Types
    typeFloat32bit    = 32
    typeFloat64bit    = 64

######################################
class MemoryTypes(object):
    """ Defines the different Memory Types that are used on DUT """
    Default                 = 0
    MinimDataRam            = 1
    MinimCodeRam            = 2
    DSPRamD0RamA            = 4
    DSPRamD0RamB            = 5
    DSPRamD1RamA            = 6
    DSPRamD1RamB            = 7
    WideDataMemory          = 8
    NarrowDataMemory        = 9
    RegionAMemory           = 8
    RegionBMemory           = 9
    PeripheralMemory        = 10
    MCPSystemBusRegisters   = 12
    BulkMemory              = 13
    ComplexWideDataMemory   = 14
    ComplexRegionAMemory    = 14
    ComplexNarrowDataMemory = 15
    ComplexRegionBMemory    = 15
    JTagMemory              = 16
    RegionLMemory           = 17
    ComplexRegionLMemory    = 18
    RegionCMemory           = 21
    RegionDMemory           = 22

#-------------------------------------------------------------------------------
# Name:        SystemCapabilities.py
# Purpose:     Class for system capabilities
#
# Author:      Imagination Technologies
#
# Created:     2016
# Copyright:   (c) 2016, Imagination Technologies Ltd.
#-------------------------------------------------------------------------------

data_bytes = [0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa, \
    0x11,0x22,0x33,0x44,0x55,0x66,0x8b,0x54,0xd7,0x3b ]


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
    debugPrint(str(target_info))

##    DA.HardReset()
##    loadProgramFile()
##    runTarget()

    DA.SelectTargetByPattern('MCU')
    print('Running Target')
#    DA.Run()
    time.sleep(3)

   # Configure clock dividers
    playout_functions.configClock()


    for  i in range(0, 1):

        #print('tx parameters configuration completed')
        playout_functions.configTXCapture()
        samples2Read = 0x2000000
        playout_functions.startCapture(samples2Read)
        input = raw_input('Enter yes when ready ')
        debugPrint("DUT done state is" )
        samples2Read = playout_functions.getNumSamplesCaptured()
        debugPrint(samples2Read)
        outBuffer = playout_functions.readCaptureMemory(samples2Read)
        dumpTXOutSamples(outBuffer, samples2Read)
        sqnrValue = calculateSqnr(outBuffer, samples2Read, str(sys.argv[1]))
        print("SQNR value is "+ str(sqnrValue))

        time.sleep(10)
        DA.SelectTargetByPattern('MCU')
        time.sleep(5)
        print(' TX test is completed')

        tx_state_str = '********* DUT done event recieved  *********'
        print(tx_state_str)


if __name__ == "__main__":
    main(sys.argv[1:])
