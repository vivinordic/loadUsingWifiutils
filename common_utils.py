#-------------------------------------------------------------------------------
# Name:        common_utils.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------
""" Global values, class etc required across multiple module should be defined
    here """

######################################

import time
import os


import datetime
#from CSUtils import DA



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

class FreqBand(object):
    """Frequncy Bands of Operation (2.4GHz or 5GHz)"""
    FreqBand2p4GHz = 0
    FreqBand5GHz   = 1

class HarnessEnable(object):
     """Harness PHY or MAC Enable"""
     PhyEnable = 0
     MacEnable = 1

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

class FrameFormat(object):
    """ Defines the different Memory Types that are used on DUT """
    DSSS          = 0
    LG            = 1
    MM            = 2
    GF            = 3
    VHT           = 4
    HE_SU         = 5
    HE_MU         = 6
    HE_ERSU       = 7
    HE_TB         = 8

class ChBandWidth  (object):
    CBW_20       = 0
    CBW_40       = 1
    CBW_80       = 2
    CBW_160       = 3

class RxVector (object):
    """Class for RxVector Variables"""
    mpduLength         = 100
    frameFormat        = 0
    nonHtModulation    = 0
    aggregation        = 0
    sbw                = 2
    mcsOrRate          = ''
    timeOfArrival1     = 0
    timeOfArrival2     = ''
    rssi               = ''
    estGain            = ''
    mappedGain         = ''
    digitalGain        = ''
    cfo                = ''
    sfo                = ''
    s2lIndex           = ''
    fsb                = ''
    fsbAdjust          = ''
    dc                 = ''
    snr                = ''
    #evm                = ''
    rssiHe             = ''
    headerBytes1       = ''
    headerBytes2       = ''
    headerBytes3       = ''
    headerBytes4       = ''
    serviceBytes       = ''
    secondAgcGain      = ''

    def __init__(self):
        self.mpduLength         = 100
        self.frameFormat        = 0
        self.nonHtModulation    = 0
        self.aggregation        = 0
        self.sbw                = 2
        self.mcsOrRate          = ''
        self.timeOfArrival1     = ''
        self.timeOfArrival2     = ''
        self.rssi               = ''
        self.estGain            = ''
        self.mappedGain         = ''
        self.digitalGain        = ''
        self.uplinkFlag         = ''
        self.bssColor           = ''
        self.TXOP               = ''
        self.aidOrstaID         = ''
        self.cfo                = ''
        self.sfo                = ''
        self.s2lIndex           = ''
        self.fsb                = ''
        self.fsbAdjust          = ''
        self.dc                 = ''
        self.snr                = ''
        self.ltfrssi            = ''
        self.digitalGain2        = ''
        self.mappedGain2         = ''
        self.estGain2            = ''
        self.dc2                 = ''
        self.headerBytes1        = ''
        self.headerBytes2        = ''
        self.headerBytes3        = ''
        self.headerBytes4        = ''
        self.headerBytes5        = ''
        self.headerBytes6        = ''
        self.serviceBytes        = ''

    def updateParams(self, rxVectorDict):
        self.mpduLength       = (rxVectorDict[0] & MASK_RxVect_MPDU_LENGTH) >> SHIFT_RxVect_MPDU_LENGTH

        self.frameFormat      = (rxVectorDict[1] & MASK_RxVect_FRAME_FORMAT) >> SHIFT_RxVect_FRAME_FORMAT
        self.nonHtModulation  = (rxVectorDict[1] & MASK_RxVect_NON_HT_MOD) >> SHIFT_RxVect_NON_HT_MOD
        self.aggregation      = (rxVectorDict[1] & MASK_RxVect_AGGREGATION) >> SHIFT_RxVect_AGGREGATION
        self.sbw              = (rxVectorDict[1] & MASK_RxVect_SBW) >> SHIFT_RxVect_SBW
        self.mcsOrRate        = (rxVectorDict[1] & MASK_RxVect_MCS_OR_RATE) >> SHIFT_RxVect_MCS_OR_RATE

        self.timeOfArrival1   = (rxVectorDict[2] & MASK_RxVect_TIME_OF_ARRIVAL_LSB_BYTES) >> SHIFT_RxVect_TIME_OF_ARRIVAL_LSB_BYTES
        self.timeOfArrival2   = (rxVectorDict[3] & MASK_RxVect_TIME_OF_ARRIVAL_MSB_BYTES) >> SHIFT_RxVect_TIME_OF_ARRIVAL_MSB_BYTES

        self.rssi             = ((rxVectorDict[4] & MASK_RxVect_RSSI) >> SHIFT_RxVect_RSSI) - 256
        self.estGain          = (rxVectorDict[4] & MASK_RxVect_EST_GAIN) >> SHIFT_RxVect_EST_GAIN
        self.mappedGain       = (rxVectorDict[4] & MASK_RxVect_MAPPED_GAIN) >> SHIFT_RxVect_MAPPED_GAIN
        self.digitalGain      = (rxVectorDict[4] & MASK_RxVect_DIGI_GAIN) >> SHIFT_RxVect_DIGI_GAIN

        self.uplinkFlag       = (rxVectorDict[5] & MASK_RxVect_UPLINK_FLAG) >> SHIFT_RxVect_UPLINK_FLAG
        self.bssColor         = (rxVectorDict[5] & MASK_RxVect_BSS_COLOR) >> SHIFT_RxVect_BSS_COLOR
        self.TXOP             = (rxVectorDict[5] & MASK_RxVect_TX_OP) >> SHIFT_RxVect_TX_OP
        self.aidOrstaID       = (rxVectorDict[5] & MASK_RxVect_AID_OR_STA_ID) >> SHIFT_RxVect_AID_OR_STA_ID

        self.cfo              = (rxVectorDict[6] & MASK_RxVect_CFO) >> SHIFT_RxVect_CFO
        self.sfo              = (rxVectorDict[7] & MASK_RxVect_SFO) >> SHIFT_RxVect_SFO

        self.s2lIndex         = (rxVectorDict[8] & MASK_RxVect_S2L_INDEX) >> SHIFT_RxVect_S2L_INDEX
        self.fsb              = (rxVectorDict[8] & MASK_RxVect_FSB) >> SHIFT_RxVect_FSB
        self.fsbAdjust        = (rxVectorDict[8] & MASK_RxVect_FSB_ADJUST) >> SHIFT_RxVect_FSB_ADJUST

        self.dc               = (rxVectorDict[9] & MASK_RxVect_DC_EST) >> SHIFT_RxVect_DC_EST

        self.snr              = (rxVectorDict[10] & MASK_RxVect_SNR_EST) >> SHIFT_RxVect_SNR_EST
        self.ltfrssi          = (rxVectorDict[10] & MASK_RxVect_RSSI_LTF) >> SHIFT_RxVect_RSSI_LTF

        self.digitalGain2     = (rxVectorDict[11] & MASK_RxVect_DIGI_GAIN_2) >> SHIFT_RxVect_DIGI_GAIN_2
        self.mappedGain2      = (rxVectorDict[11] & MASK_RxVect_MAPPED_GAIN_2) >> SHIFT_RxVect_MAPPED_GAIN_2
        self.estGain2         = (rxVectorDict[11] & MASK_RxVect_EST_GAIN_2) >> SHIFT_RxVect_EST_GAIN_2

        self.dc2              = (rxVectorDict[12] & MASK_RxVect_DC_EST_2) >> SHIFT_RxVect_DC_EST_2

        self.headerBytes1     = (rxVectorDict[13] & MASK_RxVect_HEADER_BYTES) >> SHIFT_RxVect_HEADER_BYTES
        self.headerBytes2     = (rxVectorDict[14] & MASK_RxVect_HEADER_BYTES) >> SHIFT_RxVect_HEADER_BYTES
        self.headerBytes3     = (rxVectorDict[15] & MASK_RxVect_HEADER_BYTES) >> SHIFT_RxVect_HEADER_BYTES
        self.headerBytes4     = (rxVectorDict[16] & MASK_RxVect_HEADER_BYTES) >> SHIFT_RxVect_HEADER_BYTES
        self.headerBytes5     = (rxVectorDict[17] & MASK_RxVect_HEADER_BYTES) >> SHIFT_RxVect_HEADER_BYTES

        self.headerBytes6     = (rxVectorDict[18] & MASK_RxVect_HEADER_BYTES_16) >> SHIFT_RxVect_HEADER_BYTES_16

        self.serviceBytes     = (rxVectorDict[19] & MASK_RxVect_SERVICE_BYTES) >> SHIFT_RxVect_SERVICE_BYTES



##############################################
# Class Object Instatiantions:
##DUT_OperatingModes   = DUT_OPERATION_MODE()
##DUT_test_states      = TEST_STATE()
DUT_MemoryTypes      = MemoryTypes()
DUT_ElementTypes     = ElementTypes()
##DUT_BreakPointTypes  = BreakPointType()
##DUT_HardResetEnable  = HardResetEnable()
##DUT_BreakPointEnable = BreakPointEnable()
DUT_FreqBand         = FreqBand()
DUT_HarnessEnable    = HarnessEnable()
##DUT_LoadTypes        = LoadTypes()
DUT_FrameFormat       = FrameFormat()
DUT_CBW               = ChBandWidth()
##simparams_variables  = SIMPARAMS_VARIABLE()
###############################################

def debugPrint(string):
    """ Log the string to debug log file """
    print(string)
    #debug_log_file = os.path.join(outFilePath, 'debug.log')
    debug_log_file = os.path.join(os.getcwd(), 'debug.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()

def debugPrintRxVect (string):
    """ Log rx Vector to separate debug log file """
    debug_log_file = os.path.join(outPlanPath, 'RxVector.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()


def RXVectHdrPrint(string):
    """ Log the string to debug log file """
    debug_log_file = os.path.join(outPlanPath, 'RXVector_Hdr.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()
