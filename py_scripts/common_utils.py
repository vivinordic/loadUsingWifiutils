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
import os
import time
import xlrd
import xlsxwriter

from sys import platform
from rxvector_regdef import *


import datetime
#from CSUtils import DA
from enum import Enum
import numpy
import shutil
from docx import *
import matplotlib
matplotlib.use('Agg')   # this functions needs to be called before importing matplotlib.pyplot
# without this function when this code is run in linux platform, it will cause following error
# " _tkinter.TclError: no display name and no $DISPLAY environment variable "
# this happens because Matplotlib chooses Xwindows backend by default.
# AGG is the abbreviation of Anti-grain geometry engine
import matplotlib.pyplot as plt
from docx.shared import Inches
from math import *
from input import *


#PHY_PERFORMANCE: this should be updated as and when new stats are added.
#PHY_PERFORMANCE: use total number of stats in send_packets()
#rx_stats_offsets = Enum('ed_cnt','ofdm_crc32_pass_cnt', 'ofdm_crc32_fail_cnt', 'dsss_crc32_pass_cnt', 'dsss_crc32_fail_cnt')
PER_SIM_CALCULATION = 0

standard_evm_dict={
    '2.4':
    {
        '1':'-9','2':'-9','5.5':'-9','11':'-9',
        '6':'-5','9':'-8','12':'-10','18':'-13','24':'-16','36':'-19','48':'-22','54':'-25',
        'MCS0':'-5','MCS1':'-10','MCS2':'-13','MCS3':'-16','MCS4':'-19','MCS5':'-22','MCS6':'-25','MCS7':'-27',
        'MCS8':'-5','MCS9':'-10','MCS10':'-13','MCS11':'-16','MCS12':'-19','MCS13':'-22','MCS14':'-25','MCS15':'-27',
    },
    '5':
    {
        '6':'-5','9':'-8','12':'-10','18':'-13','24':'-16','36':'-19','48':'-22','54':'-25',
        'MCS0':'-5','MCS1':'-10','MCS2':'-13','MCS3':'-16','MCS4':'-19','MCS5':'-22','MCS6':'-25','MCS7':'-27','MCS8':'-30','MCS9':'-32'
    }
}

sensitivity_dict_range={
                    '11ac':{
                            '1x1':{
                                    '20':{
                                        'MCS0':[-55,-90],'MCS1':[-50,-85],'MCS2':[-50,-85],'MCS3':[-50,-85],
                                        'MCS4':[-40,-85],'MCS5':[-40,-75],'MCS6':[-40,-75],'MCS7':[-40,-75],
                                        'MCS8':[-30,-65]
                                        },
                                    '40':{
                                        'MCS0':[-65,-85],'MCS1':[-65,-85],'MCS2':[-65,-85],'MCS3':[-55,-85],
                                        'MCS4':[-55,-75],'MCS5':[-55,-75],'MCS6':[-55,-75],'MCS7':[-55,-75],
                                        'MCS8':[-45,-65],'MCS9':[-40,-70]
                                        },
                                    '80':{
                                        'MCS0':[-55,-85],'MCS1':[-55,-85],'MCS2':[-55,-85],'MCS3':[-55,-75],
                                        'MCS4':[-55,-75],'MCS5':[-45,-65],'MCS6':[-45,-65],'MCS7':[-45,-65],
                                        'MCS8':[-40,-60],'MCS9':[-40,-60]
                                        }
                                    },
                            '2x2':{
                                    '20':{
                                        'MCS0':[-80,-90],'MCS1':[-75,-85],'MCS2':[-75,-85],'MCS3':[-75,-85],
                                        'MCS4':[-65,-85],'MCS5':[-65,-75],'MCS6':[-65,-75],'MCS7':[-65,-75],
                                        'MCS8':[-55,-65]
                                        },
                                    '40':{
                                        'MCS0':[-75,-85],'MCS1':[-75,-85],'MCS2':[-75,-85],'MCS3':[-65,-85],
                                        'MCS4':[-65,-75],'MCS5':[-65,-75],'MCS6':[-65,-75],'MCS7':[-55,-75],
                                        'MCS8':[-55,-65],'MCS9':[-50,-70]
                                        },
                                    '80':{
                                        'MCS0':[-65,-85],'MCS1':[-65,-85],'MCS2':[-65,-85],'MCS3':[-65,-75],
                                        'MCS4':[-65,-75],'MCS5':[-55,-65],'MCS6':[-55,-65],'MCS7':[-55,-65],
                                        'MCS8':[-50,-60],'MCS9':[-50,-60]
                                        }
                                    }
                            },
                    '11n':{
                            '1x1':{
                                '20':{
                                    'MCS0':[-75,-95],'MCS1':[-70,-90],'MCS2':[-70,-90],'MCS3':[-60,-80],
                                    'MCS4':[-60,-90],'MCS5':[-60,-80],'MCS6':[-60,-80],'MCS7':[-50,-80],
                                    },
                                '40':{
                                    'MCS0':[-70,-90],'MCS1':[-70,-90],'MCS2':[-70,-90],'MCS3':[-60,-80],
                                    'MCS4':[-60,-80],'MCS5':[-50,-80],'MCS6':[-50,-80],'MCS7':[-50,-80]
                                    }
                                },
                                '2x2':{
                                '20':{
                                    'MCS8':[-80,-90],'MCS9':[-70,-90],'MCS10':[-70,-90],'MCS11':[-70,-80],
                                    'MCS12':[-70,-90],'MCS13':[-70,-80],'MCS14':[-70,-80],'MCS15':[-60,-70],
                                    },
                                '40':{
                                    'MCS8':[-80,-90],'MCS9':[-80,-90],'MCS10':[-80,-90],'MCS11':[-70,-80],
                                    'MCS12':[-70,-80],'MCS13':[-60,-80],'MCS14':[-60,-80],'MCS15':[-60,-80]
                                    }
                                }
                        },
                    '11b':{
                        '1x1':{
                            '20':{
                                '1':[-80,-100],'2':[-80,-100],'5.5':[-80,-100],'11':[-80,-90]
                                }
                            }
                        },
                    '11g':{
                        '1x1':{
                            '20':{
                                '6':[-75,-95],'9':[-70,-90],'12':[-70,-90],'18':[-70,-90],
                                '24':[-60,-90],'36':[-60,-90],'48':[-60,-80],'54':[-60,-80]
                                }
                            }
                        },
                    '11a':{
                        '1x1':{
                            '20':{
                                '6':[-75,-95],'9':[-70,-90],'12':[-70,-90],'18':[-70,-90],
                                '24':[-60,-90],'36':[-60,-90],'48':[-60,-80],'54':[-60,-80]
                                }
                            }
                        },

                    '11ax':{
                            '1x1':{
                                    '20':{
                                        'MCS0':[-70,-90],'MCS1':[-65,-85],'MCS2':[-65,-85],'MCS3':[-65,-85],
                                        'MCS4':[-55,-85],'MCS5':[-55,-75],'MCS6':[-55,-75],'MCS7':[-55,-75],
                                        'MCS8':[-45,-65],'MCS9':[-45,-75]
                                        }
                                    }
                            }
                }

snr_dict_range={
                    '11ac':{
                            '1x1':{
                                    '20':{
                                        'MCS0':[-40,35],'MCS1':[-40,35],'MCS2':[-40,35],'MCS3':[-40,35],
                                        'MCS4':[-40,35],'MCS5':[-40,35],'MCS6':[-40,35],'MCS7':[-40,35],
                                        'MCS8':[-40,35]
                                        },
                                    '40':{
                                        'MCS0':[-40,35],'MCS1':[-40,35],'MCS2':[-40,35],'MCS3':[-40,35],
                                        'MCS4':[-40,35],'MCS5':[-40,35],'MCS6':[-40,35],'MCS7':[-40,35],
                                        'MCS8':[-40,35],'MCS9':[-40,35]
                                        },
                                    '80':{
                                        'MCS0':[-40,35],'MCS1':[-40,35],'MCS2':[-40,35],'MCS3':[-40,35],
                                        'MCS4':[-40,35],'MCS5':[-40,35],'MCS6':[-40,35],'MCS7':[-40,35],
                                        'MCS8':[-40,35],'MCS9':[-40,35]
                                        }
                                    },
                            '2x2':{
                                    '20':{
                                        'MCS0':[-40,35],'MCS1':[-40,35],'MCS2':[-40,35],'MCS3':[-40,35],
                                        'MCS4':[-40,35],'MCS5':[-40,35],'MCS6':[-40,35],'MCS7':[-40,35],
                                        'MCS8':[-40,35]
                                        },
                                    '40':{
                                        'MCS0':[-40,35],'MCS1':[-40,35],'MCS2':[-40,35],'MCS3':[-40,35],
                                        'MCS4':[-40,35],'MCS5':[-40,35],'MCS6':[-40,35],'MCS7':[-40,35],
                                        'MCS8':[-40,35],'MCS9':[-40,35]
                                        },
                                    '80':{
                                        'MCS0':[-40,35],'MCS1':[-40,35],'MCS2':[-40,35],'MCS3':[-40,35],
                                        'MCS4':[-40,35],'MCS5':[-40,35],'MCS6':[-40,35],'MCS7':[-40,35],
                                        'MCS8':[-40,35],'MCS9':[-40,40]
                                        }
                                    }
                            },
                    '11n':{
                            '1x1':{
                                '20':{
                                    'MCS0':[-40,30],'MCS1':[-40,30],'MCS2':[-40,30],'MCS3':[-40,30],
                                    'MCS4':[-40,30],'MCS5':[-40,30],'MCS6':[-40,30],'MCS7':[-40,30],
                                    },
                                '40':{
                                    'MCS0':[-40,30],'MCS1':[-40,30],'MCS2':[-40,30],'MCS3':[-40,30],
                                    'MCS4':[-40,30],'MCS5':[-40,30],'MCS6':[-40,30],'MCS7':[-40,30]
                                    }
                                },
                                '2x2':{
                                '20':{
                                    'MCS8':[-40,30],'MCS9':[-40,30],'MCS10':[-40,30],'MCS11':[-40,30],
                                    'MCS12':[-40,30],'MCS13':[-40,30],'MCS14':[-40,30],'MCS15':[-40,30],
                                    },
                                '40':{
                                    'MCS8':[-40,30],'MCS9':[-40,30],'MCS10':[-40,30],'MCS11':[-40,30],
                                    'MCS12':[-40,30],'MCS13':[-40,30],'MCS14':[-40,30],'MCS15':[-40,30]
                                    }
                                }
                        },
                    '11b':{
                        '1x1':{
                            '20':{
                                '1':[-40,30],'2':[-40,30],'5.5':[-40,30],'11':[-40,30]
                                }
                            }
                        },
                    '11g':{
                        '1x1':{
                            '20':{
                                '6':[-40,30],'9':[-40,30],'12':[-40,30],'18':[-40,30],
                                '24':[-40,30],'36':[-40,30],'48':[-40,30],'54':[-40,30]
                                }
                            }
                        },
                    '11a':{
                        '1x1':{
                            '20':{
                                '6':[-40,30],'9':[-40,30],'12':[-40,30],'18':[-40,30],
                                '24':[-40,30],'36':[-40,30],'48':[-40,30],'54':[-40,30]
                                }
                            }
                        },
                    '11ax':{
                            '1x1':{
                                    '20':{
                                        'MCS0':[-40,35],'MCS1':[-40,35],'MCS2':[-40,35],'MCS3':[-40,35],
                                        'MCS4':[-40,35],'MCS5':[-40,35],'MCS6':[-40,35],'MCS7':[-40,35],
                                        'MCS8':[-40,35],'MCS9':[-40,35]
                                        }
                                    }
                            }
                }



datarate_dict = {'1' : 2, '2' : 4, '5.5' : 11, '11' : 22, '6' : 12, '9' : 18, '12' : 24, '18' : 36, '24' : 48, '36' : 72,
'48' : 96, '54' : 108, 'MCS0' : 0x80, 'MCS1' : 0x81, 'MCS2' : 0x82, 'MCS3' : 0x83,
'MCS4' : 0x84, 'MCS5' : 0x85, 'MCS6' : 0x86, 'MCS7' : 0x87, 'MCS8' : 0x88, 'MCS9' : 0x89, 'MCS10' : 0x8a,
'MCS11' : 0x8b, 'MCS12' : 0x8c, 'MCS13' : 0x8d, 'MCS14' : 0x8e, 'MCS15' : 0x8f}


class TargetParams(object):
    """ This class contains all target related parameters"""
    target_type         = ''
    target_number       = ''
    system_config       = ''
    target              = ''
    build_config        = ''
    target_selection    = ''

    def __init__(self):
        self.target_type         = ''
        self.target_number       = ''
        self.system_config       = ''
        self.target              = ''
        self.build_config        = ''
        self.target_selection    = ''

    def updateParams(self,configDict):
        self.target_type         = configDict['target_type']
        self.target_number       = configDict['target_number']
        self.system_config       = configDict['system_config']
        self.target              = configDict['target']
        self.build_config        = configDict['build_config']
        self.target_selection    = configDict['target_selection']

class EquipmentParams(object):
    """ This class contains all equipment related parameters"""
    vsg                 = ''
    equip_ip            = ''
    dutModel            = '' #PHY_PERFORMANCE

    def updateParams(self,configDict):
        self.vsg            = configDict['vsg']
        self.equip_ip       = configDict['equip_ip']
        self.dutModel       = configDict['dutModel'] #PHY_PERFORMANCE

    def __init__(self):
        self.vsg                 = ''
        self.equip_ip            = ''
        self.dutModel            = '' #PHY_PERFORMANCE

class ResultsOut(object):
    """ This class contains all equipment related parameters"""
    consldFileName      = ''
    workbook            = ''
    worksheet           = ''
    bold1               = ''

    def prepareXlsx(self,resultsXlsx):
        self.consldFileName      = os.path.join(outFilePath, resultsXlsx)
        self.workbook            = xlsxwriter.Workbook(self.consldFileName)
        self.worksheet           = self.workbook.add_worksheet()
        self.bold1               = self.workbook.add_format({'bold': 1})

    def addSheet(self, sheetName):
        self.worksheet           = self.workbook.add_worksheet(sheetName)

    def addRevSheet(self, sheetName):
        self.revsheet            = self.workbook.add_worksheet(sheetName)

    def addSummarySheet(self, sheetName):
        self.worksheet1           = self.workbook.add_worksheet(sheetName)

    def __init__(self):
        self.consldFileName      = ''
        self.workbook            = ''
        self.worksheet           = ''
        self.bold1               = ''

class TestConfigParams(object):
    """ This class contains all the test configuration parameters
    required for DUT testing in different scenarios """
    test_mode           = ''
    test_type           = ''
    subFuncTestPlan     = ''
    dut_operating_mode  = ''
    lna_model_enable    = ''
    release             = ''

    genTestCasesWithExe = ''
    testCasesFileName   = ''
    checkAllTestCases   = ''
    test_case_start     = ''
    total_test_cases    = ''
    num_pkts            = ''
    time_out_value      = ''
    status              = ''

    vsg                 = ''
    equip_ip            = ''
    dutModel            = ''
    fadingtype          = 'NA'

    def __init__(self):
        self.test_mode           = ''
        self.test_type           = ''
        self.subFuncTestPlan     = ''
        self.dut_operating_mode  = ''
        self.lna_model_enable    = ''
        self.release             = ''

        self.genTestCasesWithExe = ''
        self.testCasesFileName   = ''
        self.checkAllTestCases   = ''
        self.test_case_start     = ''
        self.total_test_cases    = ''
        self.num_pkts            = ''
        self.time_out_value      = ''
        self.status              = ''
        self.fadingtype          = 'NA'

    def updateParams(self,configDict):
        self.test_mode             = configDict['test_mode']
        self.test_type             = configDict['test_type']
        self.subFuncTestPlan       = configDict['subFuncTestPlan']
        self.dut_operating_mode    = configDict['dut_operating_mode']
        self.release               = configDict['release']

        self.genTestCasesWithExe   = configDict['genTestCasesWithExe']
        self.testCasesFileName     = configDict['testCasesFileName']
        self.checkAllTestCases     = configDict['checkAllTestCases']
        self.test_case_start       = configDict['test_case_start']
        self.total_test_cases      = configDict['total_test_cases']
        self.num_pkts              = configDict['num_pkts']
        self.time_out_value        = configDict['time_out_value']

        self.vsg                   = configDict['vsg']
        self.equip_ip              = configDict['equip_ip']
        self.dutModel              = configDict['dutModel']



class TxParams:
    """Class for results vairables"""

    test_case_count =1
    obw             =0
    sbw             =0
    channel_offset  =0
    format          =1
    mcs             =0
    length          =100
    ntx             =1
    nss             =1
    ldpc            =0
    aggregation     =0
    sgi             =0
    nMPDUs          =0
    delimiter_len   =0
    jrlEnable       =0
    jammerDetTh     =0
    jammerHeadroomEdRssiDb =0
    dynamicEdEnable =0

    def __init__(self):
        self.test_case_count =1
        self.obw             =0
        self.sbw             =0
        self.channel_offset  =0
        self.format          =1
        self.mcs             =0
        self.length          =100
        self.ntx             =1
        self.nss             =1
        self.ldpc            =0
        self.aggregation     =0
        self.sgi             =0
        self.nMPDUs          =1
        self.delimiter_len   =0
        self.jrlEnable       =1
        self.jammerDetTh     =2
        self.jammerHeadroomEdRssiDb =3
        self.dynamicEdEnable =1

    def updateParams(self, testParamsDict):
        if ('aggregationEnable' in testParamsDict.keys()):
            self.aggregation = testParamsDict['aggregationEnable']
        if ('nMpdu' in testParamsDict.keys()):
            self.nMPDUs = testParamsDict['nMpdu']
        if ('packetLength' in testParamsDict.keys()):
            self.length = testParamsDict['packetLength']
        if ('format' in testParamsDict.keys()):
            self.format = testParamsDict['format']
        if ('delimiterSpacing' in testParamsDict.keys()):
            self.delimiter_len = testParamsDict['delimiterSpacing']

class SystemParams:
    """Class for results vairables"""

    channel             = 11
    nTx                 = 1
    nRx                 = 1
    prime20Offset       = 0
    CBW                 = 0
    chainSelection      = 1
    bssColor            = 0
    partialAid          = 511
    vhtBssIdPortion     = 255
    staId               = 2046
    vif                 = 0

    def __init__(self):
        self.channel         = 11
        self.nTx             = 1
        self.nRx             = 1
        self.prime20Offset   = 0
        self.CBW             = 0
        self.chainSelection  = 1
        self.bssColor        = 0
        self.partialAid      = 511
        self.vhtBssIdPortion = 255
        self.staId           = 2046
        self.vif             = 0

    def updateParams(self, testParamsDict, testConfigParams):
        if ('channelNum' in testParamsDict.keys()):
            self.channel = testParamsDict['channelNum']
        if ('nTx' in testParamsDict.keys()):
            self.nTx = testParamsDict['nTx']
        if ('nRx' in testParamsDict.keys()):
            self.nRx = testParamsDict['nRx']
        if ('prime20Offset' in testParamsDict.keys()):
            self.prime20Offset = testParamsDict['prime20Offset']
        if ('opBW' in testParamsDict.keys()):
            self.CBW = testParamsDict['opBW']
        if ('chainSelection' in testParamsDict.keys()):
            self.chainSelection = testParamsDict['chainSelection']
        if ('bssColor' in testParamsDict.keys()):
            self.bssColor = testParamsDict['bssColor']
        if ('partialAid' in testParamsDict.keys()):
            self.partialAid = testParamsDict['partialAid']
        if ('vhtBssIdPortion' in testParamsDict.keys()):
            self.vhtBssIdPortion = testParamsDict['vhtBssIdPortion']
        if ('desiredStaId' in testParamsDict.keys()):
            self.staId = testParamsDict['desiredStaId']
        if ('vif' in testParamsDict.keys()):
            self.vif = testParamsDict['vif']


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
    ltfrssi            = ''
    digitalGain2        = ''
    mappedGain2         = ''
    estGain2            = ''
    dc2                 = ''
    headerBytes1       = ''
    headerBytes2       = ''
    headerBytes3       = ''
    headerBytes4       = ''
    serviceBytes       = ''

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

rx_report_hdngs = ['ED_CNT','CRC32_PASS_CNT','CRC32_FAIL_CNT','OFDM_CORR_PASS','DSSS_CORR_PASS',\
'L1_CORR_FAIL_CNT','LSIG_FAIL_CNT','HTSIG_FAIL_CNT','VHTSIGA_FAIL_CNT','VHTSIGB_FAIL_CNT',\
'HESIGA_FAIL_CNT','HESIGB_FAIL_CNT','DSSS_FSYNC_FAIL_CNT','DSSS_SFD_FAIL_CNT','DSSS_HDR_FAIL_CNT',\
'POP_CNT','MID_PACKET_CNT','UNSUPPORTED_CNT','OTHER_STA_CNT','SpatialReuse_CNT',\
'lgPktCnt','htPktCnt','vhtPktCnt','hesuPktCnt','hemuPktCnt','heersuPktCnt','hetbPktCnt','PER %']
num_params_to_pop=28

def debugPrint(string):
    """ Log the string to debug log file """
    print(string)
    debug_log_file = os.path.join(outFilePath, 'debug.log')
    #debug_log_file = os.path.join(os.getcwd(), 'debug.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()

def createDebugLog(testConfigParams):
    """ Create folder to store results and debug log file """
    global outFilePath
    outFilePath = os.path.abspath('../')
    outFilePath = os.path.join(outFilePath,'Results')
    outFilePath = os.path.join(outFilePath,testConfigParams.release)
    outFilePath = os.path.join(outFilePath,time.strftime("%d-%b-%Y_%H-%M-%S"))
    os.makedirs(outFilePath)

def debugPrintRxVect (string):
    """ Log rx Vector to separate debug log file """
    debug_log_file = os.path.join(outPlanPath, 'RxVector.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()

def createSubPlanLog(testConfigParams):
    """ Create folder to store results and debug log file """
    global outPlanPath
    outPlanPath = os.path.join(outFilePath,testConfigParams.subFuncTestPlan)
    os.makedirs(outPlanPath)

def RXVectHdrPrint(string):
    """ Log the string to debug log file """
    debug_log_file = os.path.join(outPlanPath, 'RXVector_Hdr.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()

#PHY_PERFORMANCE
def BuildResultsPath(DUT_TestConfigParams):
    """Get the op_file_path to keep the debug.log in the op_file_path location.
    :param release
    Name of the release
    :return op_file_path
    op_file_path will be test/Results/<release>/<date_time> directory
"""
    global op_file_path
    op_file_path=os.path.abspath('../')
    op_file_path=os.path.join(op_file_path,'Results')
    op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.release)
    # For parallel testing
    if (platform=='linux' or platform=='linux2'):
        op_file_path = os.path.join(op_file_path, DUT_TestConfigParams.subFuncTestPlan)

    if (DUT_TestConfigParams.test_mode == 'RF'):
        op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.standard)
        if((DUT_TestConfigParams.standard=='11n') or (DUT_TestConfigParams.standard=='11ac')):
            op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.streams+'_'+str(DUT_TestConfigParams.chain_sel))
            op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.stbc)
            op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.coding)
            op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.gi)
        if(DUT_TestConfigParams.standard=='11n'):
            op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.greenfield_mode)
        if(DUT_TestConfigParams.standard=='11b'):
            op_file_path=os.path.join(op_file_path,DUT_TestConfigParams.preamble)

    op_file_path=os.path.join(op_file_path,time.strftime("%d-%b-%Y_%H-%M-%S"))
    try:
        os.makedirs(op_file_path)
    except:
        pass
    return op_file_path

def DebugPrint(string='',create='0'):
    """Get the op_file_path to keep the debug.log in the op_file_path location.
    op_file_path will be Results/<Results_folder_name>/<date_time> directory
    """
    if(debug_enable=='1'):
        print(string)
    if(create=='1'):
        global fdebug
    debug_log_file = os.path.join(op_file_path, 'debug.log')
    fdebug=open(debug_log_file,'a')
    fdebug.write(str(string)+'\n')
    fdebug.close()


#Start PER
def start_per(modulation='',dr='',ch='',streams='',standard='',tester='',dut='',equipment='',wave_type='default'):
    return_data=run_per(modulation,dr,ch,streams,standard,tester,dut,equipment,wave_type)
    if('NODATA' in return_data):
        print(return_data)
        print('RETUN of NODATA')
        res=dut.dut_down_up(action='up_down',ch=ch)
        time.sleep(1)
    return return_data

def run_per(modulation='',dr='',ch='',streams='',standard='',tester='',dut='',equipment='',wave_type='default'):

    per=0
    global per_clmn
    global row_num
    global row_num_dr
    # print "Start of PER calculation....\n"
    try:
        del per_data[:]
    except:
        per_data=[]
    equipment.rf_on_off(rf_state='off',streams=streams)
    #res=dut.dut_down_up(action='up',ch=ch)
    dut.reset_phy_rx_stats()

    #dut.set_dut_ibss(channel=ch,wait='no')
    equipment.send_packets(streams=streams,action='run',wave_type=wave_type)
    #res=dut.check_dut_load_issues()
    start_time=time.time()
    end_time=time.time()
    #print 'res in cu',res
    #time.sleep(1)
##    if(('LMAC Initialization Failed' in res) or ('SIOCSIFFLAGS' in res) or ('cut here' in res) or ('Intf not ready for 1000ms' in res) or ('Spurious interrupt received' in res)):
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append('LOCKUP')
##        per_data.append(0)
##        per=float(0)
##        return per_data


    #time.sleep(4)#TODO (4)
    #End For 10000 Pkts
    execution_step=1
    est_time=1
    #print time.time()
    #equipment.send_packets(streams,'run')
    if(str(dr)=='1'):
        #est_time_tm=155
        est_time_tm=11 #PHY_PERFORMANCE: est_time_tm changed from 155 to 5
    else:
        #est_time_tm=135
        est_time_tm=7 #PHY_PERFORMANCE: est_time_tm changed from 135 to 5

    while(1):
        print ("common_utild.py..run_per(): calling get_phy_stats..\n")
        [res,per]=dut.get_phy_stats() # PHY_PERFORMANCE collected PER also. This is used to write to XLS.
        #print(res)
        #m=re.compile("ed_cnt=(.*)")
        # PHY_PERFORMANCE : all index are hardcoded..should use Enum.
        if(len(res)>0):
            ed_cnt=res[0]
            if(modulation.lower()=='ofdm'):
                crc32_pass_cnt=res[1] # ..as per new stats
                crc32_fail_cnt=res[2]
            else:
                crc32_pass_cnt=res[3]
                crc32_fail_cnt=res[4]
            actual_pkt_cnt=crc32_pass_cnt+crc32_fail_cnt
            if(actual_pkt_cnt>=1000):
                break
            if((end_time-start_time)>est_time_tm):
                break
            elif((end_time-start_time)>80):
                if(actual_pkt_cnt<100):
                    break
            if(execution_step==1):
                prev_edcnt=ed_cnt
                curr_edcnt=ed_cnt
                prev_actual_pkt_cnt=actual_pkt_cnt
                curr_actual_pkt_cnt=actual_pkt_cnt
            else:
                prev_edcnt=curr_edcnt
                curr_edcnt=ed_cnt
                prev_actual_pkt_cnt=curr_actual_pkt_cnt
                curr_actual_pkt_cnt=actual_pkt_cnt

            # if(ed_cnt>=2000):
                # if(crc32_pass_cnt+crc32_fail_cnt<=500):
                    # break
##            if((end_time-start_time)>est_time_tm):
##                break
##            elif((end_time-start_time)>10):
##                if(actual_pkt_cnt<100):
##                    break
##                print 'curr_actual_pkt_cnt-prev_actual_pkt_cnt',curr_actual_pkt_cnt-prev_actual_pkt_cnt
##                if(curr_actual_pkt_cnt-prev_actual_pkt_cnt<100):
##                        break
            execution_step+=1
        elif('FAIL' in res):
            print(res)
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append('LOCKUP')
            per_data.append(0)
            per=float(0)
            return per_data

        else:
            print((m.findall(res)))
            print(len(m.findall(res)))
            print (res)
            DebugPrint(res)
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append('NODATA')
            per_data.append(0)
            per=float(0)
            return per_data
        end_time=time.time()
        #print ed_cnt
    print(" PER calculation is done for 1000 packets. ")
    try:
        per_data.append(ed_cnt)
    except:
        ed_cnt='NODATA'
        per_data.append('NODATA')
    if(modulation.lower()=='ofdm'):
        # PHY_PERFORMANCE : all index are hardcoded..should use Enum.
        try:
            #ofdm_crc32_pass_cnt=res[2]
            ofdm_crc32_pass_cnt=res[1] #  as per new stats
            per_data.append(int(ofdm_crc32_pass_cnt))
        except:
            ofdm_crc32_pass_cnt='NODATA'
            per_data.append('NODATA')
        try:
            #ofdm_crc32_fail_cnt=res[3]
            ofdm_crc32_fail_cnt=res[2]#  as per new stats
            per_data.append(int(ofdm_crc32_fail_cnt))
        except:
            ofdm_crc32_fail_cnt='NODATA'
            per_data.append('NODATA')
    elif(modulation.lower()=='dsss'):
        try:
            dsss_crc32_pass_cnt=res[3]#  as per new stats
            per_data.append(int(dsss_crc32_pass_cnt))
        except:
            dsss_crc32_pass_cnt='NODATA'
            per_data.append('NODATA')
        try:
            dsss_crc32_fail_cnt=res[4]
            per_data.append(int(dsss_crc32_fail_cnt))
        except:
            dsss_crc32_fail_cnt='NODATA'
            per_data.append('NODATA')
    try:
        ofdm_corr_pass_cnt=res[5]
        per_data.append(int(ofdm_corr_pass_cnt))
    except:
        ofdm_corr_pass_cnt='NODATA'
        per_data.append('NODATA')
    try:
        dsss_corr_pass_cnt=res[6]
        per_data.append(int(dsss_corr_pass_cnt))
    except:
        dsss_corr_pass_cnt='NODATA'
        per_data.append('NODATA')
    try:
        l1_corr_fail_cnt=res[7]
        per_data.append(int(l1_corr_fail_cnt))
    except:
        l1_corr_fail_cnt='NODATA'
        per_data.append('NODATA')
    #try:
    #    ofdm_s2l_fail_cnt=res[12]
    #    per_data.append(int(ofdm_s2l_fail_cnt))
    #except:
    #    ofdm_s2l_fail_cnt='NODATA'
    #    per_data.append('NODATA')
    try:
        lsig_fail_cnt=res[8]
        per_data.append(int(lsig_fail_cnt))
    except:
        lsig_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        htsig_fail_cnt=res[9]
        per_data.append(int(htsig_fail_cnt))
    except:
        htsig_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        vhtsiga_fail_cnt=res[10]
        per_data.append(int(vhtsiga_fail_cnt))
    except:
        vhtsiga_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        vhtsigb_fail_cnt=res[11]
        per_data.append(int(vhtsigb_fail_cnt))
    except:
        vhtsigb_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        hesiga_fail_cnt=res[12]
        per_data.append(int(hesiga_fail_cnt))
    except:
        hesiga_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        hesigb_fail_cnt=res[13]
        per_data.append(int(hesigb_fail_cnt))
    except:
        hesigb_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        dsss_fsync_fail_cnt=res[14]
        per_data.append(int(dsss_fsync_fail_cnt))
    except:
        dsss_fsync_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        dsss_sfd_fail_cnt=res[15]
        per_data.append(int(dsss_sfd_fail_cnt))
    except:
        dsss_sfd_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        dsss_hdr_fail_cnt=res[16]
        per_data.append(int(dsss_hdr_fail_cnt))
    except:
        dsss_hdr_fail_cnt='NODATA'
        per_data.append('NODATA')
    try:
        pop_cnt=res[24]
        per_data.append(int(pop_cnt))
    except:
        pop_cnt='NODATA'
        per_data.append('NODATA')
    try:
        midPacket_cnt=res[25]
        per_data.append(int(midPacket_cnt))
    except:
        midPacket_cnt ='NODATA'
        per_data.append('NODATA')
    try:
        unsupported_cnt=res[27]
        per_data.append(int(unsupported_cnt))
    except:
        unsupported_cnt='NODATA'
        per_data.append('NODATA')
    try:
        other_STA_cnt=res[28]
        per_data.append(int(other_STA_cnt))
    except:
        other_STA_cnt ='NODATA'
        per_data.append('NODATA')
    try:
        spatialReuse_cnt=res[31]
        per_data.append(int(spatialReuse_cnt))
    except:
        spatialReuse_cnt='NODATA'
        per_data.append('NODATA')
    try:
        lgPktCnt=res[17]
        per_data.append(int(lgPktCnt))
    except:
        lgPktCnt='NODATA'
        per_data.append('NODATA')
    try:
        htPktCnt=res[18]
        per_data.append(int(htPktCnt))
    except:
        htPktCnt='NODATA'
        per_data.append('NODATA')
    try:
        vhtPktCnt=res[19]
        per_data.append(int(vhtPktCnt))
    except:
        vhtPktCnt='NODATA'
        per_data.append('NODATA')
    try:
        hesuPktCnt=res[20]
        per_data.append(int(hesuPktCnt))
    except:
        hesuPktCnt='NODATA'
        per_data.append('NODATA')
    try:
        hemuPktCnt=res[21]
        per_data.append(int(hemuPktCnt))
    except:
        hemuPktCnt='NODATA'
        per_data.append('NODATA')
    try:
        heersuPktCnt=res[22]
        per_data.append(int(heersuPktCnt))
    except:
        heersuPktCnt='NODATA'
        per_data.append('NODATA')
    try:
        hetbPktCnt=res[23]
        per_data.append(int(hetbPktCnt))
    except:
        hetbPktCnt='NODATA'
        per_data.append('NODATA')

    #PHY_PERFORMANCE : the following is commented to avoid overwriting of calculated PER percentage.
    #try:
    #    if(int(ed_cnt)<100):
    #        per=100
    #        per_data.append(100)
    #    else:
    #        if(modulation.upper().find('OFDM')>=0):
    #            if(int(ch)<15):
    #                if('iqxel' in tester.lower()):
    #                    per=((1003-ofdm_crc32_pass_cnt) * 100) / 1003
    #                else:
    #                    per=((1010-ofdm_crc32_pass_cnt) * 100) / ed_cnt
    #            else:
    #                if('iqxel' in tester.lower()):
    #                    per=((1003-ofdm_crc32_pass_cnt) * 100) / 1003
    #                else:
    #                    per=((1010-ofdm_crc32_pass_cnt) * 100) / ed_cnt
    #        else:
    #            if('iqxel' in tester.lower()):
    #                per=((1003-dsss_crc32_pass_cnt) * 100) / 1003
    #            else:
    #                per=((1010-dsss_crc32_pass_cnt) * 100) / ed_cnt
    #        if(float(per)<0):
    #            if(ed_cnt>1003):
    #
    #                if(modulation.upper().find('OFDM')>=0):
    #                    if(ofdm_crc32_pass_cnt<1000):
    #                        per=((ed_cnt-ofdm_crc32_pass_cnt) * 100) / ed_cnt
    #                    else:
    #                        per=0
    #                else:
    #                    if(dsss_crc32_pass_cnt<1000):
    #                        per=((ed_cnt-dsss_crc32_pass_cnt) * 100) / ed_cnt
    #                    else:
    #                        per=0
    #        per_data.append(float(per))
    #except Exception,E:
    #    print E.args
    #
    #    per=0
    #    per_data.append(0)
    #    print '\nDUT hard reboot'
    #    # try:
    #        # dut_hard_reboot()
    #    # except:
    #        # dut_hard_reboot()
    #    #print time.time()
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append('LOCKUP')
    #    per_data.append(0)
    #    per=float(0)
    #    return per_data
    per_data.append(int(per))  #PHY_PERFORMANCE added per
    return per_data

def get_tx_stats_from_vsa(txp,dr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2):
    # equipment.click_agc(standard,streams)
    equipment.close_vsg()
    equipment.start_vsg()

    for i in range(1):
        equipment.click_analyser(standard,streams,pkts='15')
        time.sleep(1)
        # try:
        if(1):
            power_1x1,power_2x2=equipment.save_power_values(dr,txp,ch,standard,streams,cable_loss_1x1,cable_loss_2x2)
            if(power_1x1 > 1000 or power_2x2 > 1000):
                # print '4 ',time.time()
                time.sleep(1)
                continue
            else:
                break
        # except Exception,e:
            # power_1x1=0
            # if('2x2' in streams):
                # power_2x2=0
    # exit(0)
    equipment.set_reference_level(power_1x1,power_2x2,streams)
    for i in range(1):
        # try:
        if(1):
            power_1x1,power_2x2=equipment.save_power_values(dr,txp,ch,standard,streams,cable_loss_1x1,cable_loss_2x2)
            if(power_1x1 > 1000 or power_2x2 > 1000):
                # print '4 ',time.time()
                time.sleep(1)
                continue
            else:
                break
        # except Exception,e:
            # power_1x1=0
            # if('2x2' in streams):
                # power_2x2=0
    # print power_1x1
    if(power_1x1 > 1000):
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    tx_data=[]
    freq_offset,margin,status = equipment.save_spectrum_margin(standard)
    if(0):
    # try:
        if('1x1' in streams):
            spectrum_1x1=equipment.save_spectrum_values(standard,streams)
        else:
            spectrum_1x1,spectrum_2x2=equipment.save_spectrum_values(standard,streams)
        freq_values=equipment.save_freq_values(standard,streams)
        if(standard=='11b'):
            for mf in range(len(freq_values[freq_values.index(-60000000):])-1):
                if(-625000.0 == freq_values[mf]):
                    values_at_m62 = float(spectrum_1x1[mf])
                elif(0 == freq_values[mf]):
                    values_at_zero = float(spectrum_1x1[mf])
                elif(625000.0 == freq_values[mf]):
                    values_at_p62 = float(spectrum_1x1[mf])
            carrier_suppression_1x1='Pass'
            carrier_suppression_delta_1x1=values_at_zero-((values_at_m62+values_at_p62)/2)
            DebugPrint('values_at_zero_1x1 '+str(values_at_zero))
            DebugPrint('values_at_m62_1x1 '+str(values_at_m62))
            DebugPrint('values_at_p62_1x1 '+str(values_at_p62))
            if((values_at_zero > values_at_m62) or (values_at_zero > values_at_p62)):
                carrier_suppression_1x1='Fail'
                DebugPrint('carrier_suppression_1x1 '+carrier_suppression_1x1)
        else:
            for mf in range(len(freq_values[freq_values.index(-60000000):])-1):
                if(-2187500.0 == freq_values[mf]):
                    values_at_m62 = float(spectrum_1x1[mf])
                elif(0 == freq_values[mf]):
                    values_at_zero = float(spectrum_1x1[mf])
                elif(2187500.0 == freq_values[mf]):
                    values_at_p62 = float(spectrum_1x1[mf])
            carrier_suppression_1x1='Pass'
            carrier_suppression_delta_1x1=values_at_zero-((values_at_m62+values_at_p62)/2)
            DebugPrint('values_at_zero_1x1 '+str(values_at_zero))
            DebugPrint('values_at_m62_1x1 '+str(values_at_m62))
            DebugPrint('values_at_p62_1x1 '+str(values_at_p62))
            if((values_at_zero > values_at_m62) or (values_at_zero > values_at_p62)):
                carrier_suppression_1x1='Fail'
                DebugPrint('carrier_suppression_1x1 '+carrier_suppression_1x1)
            if('2x2' in streams):
                for mf in range(len(freq_values[freq_values.index(-60000000):])-1):
                    if(-2187500.0 == freq_values[mf]):
                        values_at_m62 = float(spectrum_2x2[mf])
                    elif(0 == freq_values[mf]):
                        values_at_zero = float(spectrum_2x2[mf])
                    elif(2187500.0 == freq_values[mf]):
                        values_at_p62 = float(spectrum_2x2[mf])
                carrier_suppression_2x2='Pass'
                carrier_suppression_delta_2x2=values_at_zero-((values_at_m62+values_at_p62)/2)
                DebugPrint('values_at_zero_2x2 '+str(values_at_zero))
                DebugPrint('values_at_m62_2x2 '+str(values_at_m62))
                DebugPrint('values_at_p62_2x2 '+str(values_at_p62))
                if((values_at_zero > values_at_m62) or (values_at_zero > values_at_p62)):
                    carrier_suppression_2x2='Fail'
                    DebugPrint('carrier_suppression_2x2 '+carrier_suppression_2x2)
        # print 'carrier_suppression_1x1 ',carrier_suppression_1x1
    # except:
        # if('2x2' in streams):
            # carrier_suppression_1x1=carrier_suppression_2x2='Fail'
        # else:
            # carrier_suppression_1x1='Fail'
    # try:
    if(0):
        ideal_spectrum_hlimit_values,ideal_spectrum_freq_values=equipment.get_ideal_spectrum_values(standard,streams,ch)
        # print len(ideal_spetrum_values)
        # print (ideal_spetrum_values.keys())
        spectral_mask_index=0
        left_spectral_mask_index=0
        right_spectral_mask_index=0
        if(standard=='11b'):
            #freq_values=equipment.save_freq_values(standard,streams)
            spec_values=[]
            #DebugPrint(freq_values)
            for mf in freq_values:
                if(float(ideal_spectrum_freq_values[0]) <= float(mf) <= float(ideal_spectrum_freq_values[1])):
                    new_y=ideal_spectrum_hlimit_values[1]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[1]) < float(mf) <= float(ideal_spectrum_freq_values[2])):
                    new_y=ideal_spectrum_hlimit_values[2]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[2]) < float(mf) <= float(ideal_spectrum_freq_values[3])):
                    new_y=ideal_spectrum_hlimit_values[3]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[3]) < float(mf) <= float(ideal_spectrum_freq_values[4])):
                    new_y=ideal_spectrum_hlimit_values[4]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[4]) < float(mf) <= float(ideal_spectrum_freq_values[5])):
                    new_y=ideal_spectrum_hlimit_values[5]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[5]) < float(mf) <= float(ideal_spectrum_freq_values[6])):
                    new_y=ideal_spectrum_hlimit_values[6]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[6]) < float(mf) <= float(ideal_spectrum_freq_values[7])):
                    new_y=ideal_spectrum_hlimit_values[7]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[7]) < float(mf) <= float(ideal_spectrum_freq_values[8])):
                    new_y=ideal_spectrum_hlimit_values[8]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[8]) < float(mf) <= float(ideal_spectrum_freq_values[9])):
                    new_y=ideal_spectrum_hlimit_values[9]
                    spec_values.append(new_y)
        if((bw=='20'or (bw=='20in40')or (bw=='20in80')) and standard!='11b'):
            # ideal_spectrum_hlimit_values,ideal_spectrum_freq_values=equipment.get_ideal_spectrum_values(standard,streams)
            slope_1=(ideal_spectrum_hlimit_values[2]-ideal_spectrum_hlimit_values[1])/(ideal_spectrum_freq_values[2]-ideal_spectrum_freq_values[1])
            slope_2=(ideal_spectrum_hlimit_values[3]-ideal_spectrum_hlimit_values[2])/(ideal_spectrum_freq_values[3]-ideal_spectrum_freq_values[2])
            slope_3=(ideal_spectrum_hlimit_values[4]-ideal_spectrum_hlimit_values[3])/(ideal_spectrum_freq_values[4]-ideal_spectrum_freq_values[3])
            #freq_values=equipment.save_freq_values(standard,streams)
            spec_values=[]
            #DebugPrint(freq_values)
            for mf in freq_values:
                spectral_mask_index+=1
                if(float(ideal_spectrum_freq_values[0]) <= float(mf) < float(ideal_spectrum_freq_values[1])):
                    new_y=ideal_spectrum_hlimit_values[0]
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[1]) <= float(mf) < float(ideal_spectrum_freq_values[2])):
                    new_y=ideal_spectrum_hlimit_values[1]+(slope_1*(float(mf)-(ideal_spectrum_freq_values[1])))
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[2]) <= float(mf) < float(ideal_spectrum_freq_values[3])):
                    new_y=ideal_spectrum_hlimit_values[2]+(slope_2*(float(mf)-(ideal_spectrum_freq_values[2])))
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[3]) <= float(mf) < float(ideal_spectrum_freq_values[4])):
                    new_y=ideal_spectrum_hlimit_values[3]+(slope_3*(float(mf)-(ideal_spectrum_freq_values[3])))
                    spec_values.append(new_y)
                    left_spectral_mask_index=spectral_mask_index
                elif(float(ideal_spectrum_freq_values[4]) <= float(mf) < float(ideal_spectrum_freq_values[5])):
                    new_y=ideal_spectrum_hlimit_values[4]
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                    right_spectral_mask_index=spectral_mask_index
                elif(float(ideal_spectrum_freq_values[5]) <= float(mf) < float(ideal_spectrum_freq_values[6])):
                    new_y=ideal_spectrum_hlimit_values[5]+(-1*slope_3*(float(mf)-(ideal_spectrum_freq_values[5])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[6]) <= float(mf) < float(ideal_spectrum_freq_values[7])):
                    new_y=ideal_spectrum_hlimit_values[6]+(-1*slope_2*(float(mf)-(ideal_spectrum_freq_values[6])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[7]) <= float(mf) < float(ideal_spectrum_freq_values[8])):
                    new_y=ideal_spectrum_hlimit_values[7]+(-1*slope_1*(float(mf)-(ideal_spectrum_freq_values[7])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[8]) <= float(mf) < float(ideal_spectrum_freq_values[9])):
                    spec_values.append(ideal_spectrum_hlimit_values[8])
        elif(bw=='40'):
            slope_1=(ideal_spectrum_hlimit_values[2]-ideal_spectrum_hlimit_values[1])/(ideal_spectrum_freq_values[2]-ideal_spectrum_freq_values[1])
            slope_2=(ideal_spectrum_hlimit_values[3]-ideal_spectrum_hlimit_values[2])/(ideal_spectrum_freq_values[3]-ideal_spectrum_freq_values[2])
            slope_3=(ideal_spectrum_hlimit_values[4]-ideal_spectrum_hlimit_values[3])/(ideal_spectrum_freq_values[4]-ideal_spectrum_freq_values[3])
            #freq_values=equipment.save_freq_values(standard,streams)
            spec_values=[]
            #DebugPrint(freq_values)
            for mf in freq_values:
                spectral_mask_index+=1
                if(float(ideal_spectrum_freq_values[0]) <= float(mf) < float(ideal_spectrum_freq_values[1])):
                    spec_values.append(ideal_spectrum_hlimit_values[0])
                elif(float(ideal_spectrum_freq_values[1]) <= float(mf) < float(ideal_spectrum_freq_values[2])):
                    new_y=ideal_spectrum_hlimit_values[1]+(slope_1*(float(mf)-(ideal_spectrum_freq_values[1])))
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[2]) <= float(mf) < float(ideal_spectrum_freq_values[3])):
                    new_y=ideal_spectrum_hlimit_values[2]+(slope_2*(float(mf)-(ideal_spectrum_freq_values[2])))
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[3]) <= float(mf) < float(ideal_spectrum_freq_values[4])):
                    new_y=ideal_spectrum_hlimit_values[3]+(slope_3*(float(mf)-(ideal_spectrum_freq_values[3])))
                    spec_values.append(new_y)
                    left_spectral_mask_index=spectral_mask_index
                elif(float(ideal_spectrum_freq_values[4]) <= float(mf) < float(ideal_spectrum_freq_values[5])):
                    new_y=ideal_spectrum_hlimit_values[4]
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                    right_spectral_mask_index=spectral_mask_index
                elif(float(ideal_spectrum_freq_values[5]) <= float(mf) < float(ideal_spectrum_freq_values[6])):
                    new_y=ideal_spectrum_hlimit_values[5]+(-1*slope_3*(float(mf)-(ideal_spectrum_freq_values[5])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[6]) <= float(mf) < float(ideal_spectrum_freq_values[7])):
                    new_y=ideal_spectrum_hlimit_values[6]+(-1*slope_2*(float(mf)-(ideal_spectrum_freq_values[6])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[7]) <= float(mf) < float(ideal_spectrum_freq_values[8])):
                    new_y=ideal_spectrum_hlimit_values[7]+(-1*slope_1*(float(mf)-(ideal_spectrum_freq_values[7])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[8]) <= float(mf) < float(ideal_spectrum_freq_values[9])):
                    spec_values.append(ideal_spectrum_hlimit_values[8])
                # else:
                    # print float(ideal_spectrum_freq_values[1]) , float(mf) , float(ideal_spectrum_freq_values[2])
        elif(bw=='80'):
            slope_2=(ideal_spectrum_hlimit_values[3]-ideal_spectrum_hlimit_values[2])/(ideal_spectrum_freq_values[3]-ideal_spectrum_freq_values[2])
            slope_3=(ideal_spectrum_hlimit_values[4]-ideal_spectrum_hlimit_values[3])/(ideal_spectrum_freq_values[4]-ideal_spectrum_freq_values[3])

            spec_values=[]
            #DebugPrint(freq_values)
            for mf in freq_values:
                spectral_mask_index+=1
                if(float(ideal_spectrum_freq_values[2]) <= float(mf) < float(ideal_spectrum_freq_values[3])):
                    new_y=ideal_spectrum_hlimit_values[2]+(slope_2*(float(mf)-(ideal_spectrum_freq_values[2])))
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[3]) <= float(mf) < float(ideal_spectrum_freq_values[4])):
                    new_y=ideal_spectrum_hlimit_values[3]+(slope_3*(float(mf)-(ideal_spectrum_freq_values[3])))
                    spec_values.append(new_y)
                    left_spectral_mask_index=spectral_mask_index
                elif(float(ideal_spectrum_freq_values[4]) <= float(mf) < float(ideal_spectrum_freq_values[5])):
                    new_y=ideal_spectrum_hlimit_values[4]
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                    right_spectral_mask_index=spectral_mask_index
                elif(float(ideal_spectrum_freq_values[5]) <= float(mf) < float(ideal_spectrum_freq_values[6])):
                    new_y=ideal_spectrum_hlimit_values[5]+(-1*slope_3*(float(mf)-(ideal_spectrum_freq_values[5])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[6]) <= float(mf) < float(ideal_spectrum_freq_values[7])):
                    new_y=ideal_spectrum_hlimit_values[6]+(-1*slope_2*(float(mf)-(ideal_spectrum_freq_values[6])))
                    if(new_y > 0): new_y=new_y*-1
                    spec_values.append(new_y)
                elif(float(ideal_spectrum_freq_values[7]) <= float(mf) < float(ideal_spectrum_freq_values[8])):
                    spec_values.append(ideal_spectrum_hlimit_values[7])
        spectral_mask_margin=-0.5
        DebugPrint('left_spectral_mask_index->'+str(left_spectral_mask_index))
        DebugPrint('right_spectral_mask_index->'+str(right_spectral_mask_index))
        if('1x1' in streams):
            DebugPrint('carrier_suppression_delta_1x1 '+str(carrier_suppression_delta_1x1))
            rhs_1x1=spectral_mask_margin-carrier_suppression_delta_1x1
            if(carrier_suppression_delta_1x1<0):rhs_1x1 = spectral_mask_margin
            for m in range(len(spec_values)-1):
                if(left_spectral_mask_index<m<right_spectral_mask_index):
                    continue
                # if(float(spec_values[m])<float(spectrum_1x1[m])):
                # if(float(spectrum_1x1[m])-float(spec_values[m])>spectral_mask_margin-carrier_suppression_delta_1x1):
                if(float(spectrum_1x1[m])-float(spec_values[m])>rhs_1x1):
                    # DebugPrint('spec_values_1x1 '+str(spec_values[m]))
                    # DebugPrint('spectrum_1x1 '+str(spectrum_1x1[m]))
                    spectral_mask_1x1='Fail'
                    break
                else:
                    # DebugPrint('spec_values_1x1 '+str(spec_values[m]))
                    # DebugPrint('spectrum_1x1 '+str(spectrum_1x1[m]))
                    spectral_mask_1x1='Pass'
        else:
            rhs_1x1=spectral_mask_margin-carrier_suppression_delta_1x1
            if(carrier_suppression_delta_1x1<0):rhs_1x1 = spectral_mask_margin
            rhs_2x2=spectral_mask_margin-carrier_suppression_delta_2x2
            if(carrier_suppression_delta_2x2<0):rhs_2x2 = spectral_mask_margin
            for m in range(len(spec_values)-1):
                if(left_spectral_mask_index<m<right_spectral_mask_index):
                    continue
                if(float(spectrum_1x1[m])-float(spec_values[m])>rhs_1x1):
                    spectral_mask_1x1='Fail'
                    # DebugPrint('spec_values_1x1 '+str(spec_values[m]))
                    # DebugPrint('spectrum_1x1 '+str(spectrum_1x1[m]))
                    # DebugPrint('spectral_mask_margin '+str(spectral_mask_margin))
                    # DebugPrint('carrier_suppression_delta_1x1 '+str(carrier_suppression_delta_1x1))
                    # DebugPrint('float(spectrum_1x1[m])-float(spec_values[m]) '+str(float(spectrum_1x1[m])-float(spec_values[m])))
                    # DebugPrint('spectral_mask_margin-carrier_suppression_delta_1x1 '+str(spectral_mask_margin-carrier_suppression_delta_1x1))
                    # DebugPrint('spectral_mask_1x1 '+spectral_mask_1x1)
                    break
                else:
                    spectral_mask_1x1='Pass'
            for m in range(len(spec_values)-1):
                if(left_spectral_mask_index<m<right_spectral_mask_index):
                    continue
                if(float(spectrum_2x2[m])-float(spec_values[m])>rhs_2x2):
                    spectral_mask_2x2='Fail'
                    # DebugPrint('spec_values_2x2 '+str(spec_values[m]))
                    # DebugPrint('spectrum_2x2 '+str(spectrum_2x2[m]))
                    # DebugPrint('spectral_mask_margin '+str(spectral_mask_margin))
                    # DebugPrint('carrier_suppression_delta_2x2 '+str(carrier_suppression_delta_2x2))
                    # DebugPrint('float(spectrum_2x2[m])-float(spec_values[m]) '+str(float(spectrum_2x2[m])-float(spec_values[m])))
                    # DebugPrint('spectral_mask_margin-carrier_suppression_delta_2x2 '+str(spectral_mask_margin-carrier_suppression_delta_2x2))
                    # DebugPrint('spectral_mask_2x2 '+spectral_mask_2x2)
                    break
                else:
                    spectral_mask_2x2='Pass'
    # except:
        # if('2x2' in streams):
            # spectral_mask_1x1,spectral_mask_2x2='Fail'
        # else:
            # spectral_mask_1x1='Fail'

    # for i in range(1):
        # # equipment.click_analyser(standard,streams)
        # # time.sleep(10)
        # # try:
        # if(1):
            # power_1x1,power_2x2=equipment.save_power_values(dr,txp,ch,standard,streams,cable_loss_1x1,cable_loss_2x2)
            # if(power_1x1 > 1000):
                # print '4 ',time.time()
                # time.sleep(1)
                # continue
            # else:
                # break
        # # except Exception,e:
            # # power_1x1=0
            # # if('2x2' in streams):
                # # power_2x2=0

    if(1):
        obw_1x1=equipment.save_obw_values(standard,streams)
    # except Exception,e:
        # obw_1x1='0'

    # try:
    if(1):
        dr_1x1=equipment.save_datarate_values(standard,streams)
    # except Exception,e:
        # dr_1x1='0'
    # print obw_1x1
    # print dr_1x1
    for i in range(2):
        equipment.click_analyser(standard,streams)
        time.sleep(3)
        try:
        # if(1):
            if('2x2' in streams):
                evm_1x1,evm_2x2,phaseerr_1x1,phaseerr_2x2,freq_error_1x1,freq_error_2x2,sysclkerr_1x1,sysclkerr_2x2,lo_leakage_1x1,lo_leakage_2x2,ampimb_1x1,ampimb_2x2,phaseimb_1x1,phaseimb_2x2=equipment.save_txquality_stats(dr,txp,ch,standard,streams)
            else:
                evm_1x1,phaseerr_1x1,freq_error_1x1,sysclkerr_1x1,lo_leakage_1x1,ampimb_1x1,phaseimb_1x1=equipment.save_txquality_stats(dr,txp,ch,standard,streams)#CSV
            break
        #except:
        except Exception,e:
            print (e.args)
            if('2x2' in streams):
                evm_1x1,evm_2x2,phaseerr_1x1,phaseerr_2x2,freq_error_1x1,freq_error_2x2,sysclkerr_1x1,sysclkerr_2x2,lo_leakage_1x1,lo_leakage_2x2,ampimb_1x1,ampimb_2x2,phaseimb_1x1,phaseimb_2x2='0','0','0','0','0','0','0','0','0','0','0','0','0','0'
            else:
                evm_1x1,phaseerr_1x1,freq_error_1x1,sysclkerr_1x1,lo_leakage_1x1,ampimb_1x1,phaseimb_1x1='0','0','0','0','0','0','0'


    if(streams=='2x2'):
        #tx_data+=[obw_1x1,dr_1x1,power_1x1,power_2x2,evm_1x1,evm_2x2,phaseerr_1x1,phaseerr_2x2,freq_error_1x1,freq_error_2x2,sysclkerr_1x1,sysclkerr_2x2,lo_leakage_1x1,lo_leakage_2x2,ampimb_1x1,ampimb_2x2,phaseimb_1x1,phaseimb_2x2,spectral_mask_1x1,spectral_mask_2x2,carrier_suppression_1x1,carrier_suppression_2x2]
        tx_data+=[obw_1x1,dr_1x1,power_1x1,power_2x2,evm_1x1,evm_2x2,phaseerr_1x1,phaseerr_2x2,freq_error_1x1,freq_error_2x2,sysclkerr_1x1,sysclkerr_2x2,lo_leakage_1x1,lo_leakage_2x2,ampimb_1x1,ampimb_2x2,phaseimb_1x1,phaseimb_2x2]+freq_offset+margin+[status]

        #tx_data.append([freq_values[freq_values.index(-60000000):]])
        #tx_data.append([spectrum_1x1])
        #tx_data.append([spectrum_2x2])
        #tx_data.append([spec_values])
    else:
        #tx_data+=[obw_1x1,dr_1x1,power_1x1,evm_1x1,phaseerr_1x1,freq_error_1x1,sysclkerr_1x1,lo_leakage_1x1,ampimb_1x1,phaseimb_1x1,spectral_mask_1x1,carrier_suppression_1x1]
        tx_data+=[obw_1x1,dr_1x1,power_1x1,evm_1x1,phaseerr_1x1,freq_error_1x1,sysclkerr_1x1,lo_leakage_1x1,ampimb_1x1,phaseimb_1x1]+freq_offset+margin+[status]
        #tx_data.append([freq_values[freq_values.index(-60000000):]]) # PHY_PERFORMANCE commneted when testing EVM AC. Why is this done. this is causing errors. Adding hundreds of values to array.
        #tx_data.append([spectrum_1x1]) # PHY_PERFORMANCE commneted when testing EVM AC
        #tx_data.append([spec_values]) # PHY_PERFORMANCE commneted when testing EVM AC
    return tx_data

def copy_file(op_dr_file_path='',dutModel='',release='',standard='',streams='',stbc='',coding='',gi='',greenfield_mode='',preamble='',ch='',test='rx'):
    """ Copy the test results into \\\\hbdc1\\WLAN\\Shared\\ directory """
    shared_location_path='\\\\hbdc1'
    shared_location_path=os.path.join(shared_location_path,'WLAN')
    shared_location_path=os.path.join(shared_location_path,'PhysicalLayerDevelopment')
    shared_location_path=os.path.join(shared_location_path,'Automation_results')
    if('rx' in test):
        shared_location_path=os.path.join(shared_location_path,dutModel.split('_')[0]+"_RX_Results")
    else:
        shared_location_path=os.path.join(shared_location_path,dutModel.split('_')[0]+"_TX_Results")
    shared_location_path=os.path.join(shared_location_path,release)
    if((ch!='') or ('All_Channels_Consolidated' in op_dr_file_path)):
        shared_location_path=os.path.join(shared_location_path,standard)
        if((standard=='11n')or(standard=='11ac')):
            shared_location_path=os.path.join(shared_location_path,streams)
            shared_location_path=os.path.join(shared_location_path,stbc)
            shared_location_path=os.path.join(shared_location_path,coding)
            shared_location_path=os.path.join(shared_location_path,gi)
        if(standard=='11n'):
            shared_location_path=os.path.join(shared_location_path,greenfield_mode)
        if(standard=='11b'):
            shared_location_path=os.path.join(shared_location_path,preamble)
        if('All_Channels_Consolidated' not in op_dr_file_path):
            shared_location_path=os.path.join(shared_location_path,str(ch))
            if('Consolidated' not in op_dr_file_path):
                shared_location_path=os.path.join(shared_location_path,'Individual')
    try:
        os.makedirs(shared_location_path)
    except Exception,E:
        pass
    os.system("copy "+op_dr_file_path+" "+shared_location_path)



def svdOutputBitDiff(dutsvdOutput, matsvdOutput, nTx, nRx):
    signalPower = 0
    noisePower = 0

    dutPhiAngles, dutPsiAngles = unpackPackedAngles(dutsvdOutput, nTx, nRx)
    matPhiAngles, matPsiAngles = unpackPackedAngles(matsvdOutput[1:], nTx, nRx)

    phiBitDiff1 = numpy.subtract(dutPhiAngles, matPhiAngles)
    phiBitDiff = abs(phiBitDiff1)
    debugPrint(phiBitDiff)
    phiMaxBitDiff =  numpy.amax(phiBitDiff)

    psiBitDiff = numpy.subtract(dutPsiAngles, matPsiAngles)
    psiBitDiff = abs(psiBitDiff)
    debugPrint(psiBitDiff)
    psiMaxBitDiff = numpy.amax(psiBitDiff)
    return phiMaxBitDiff, psiMaxBitDiff


def unpackPackedAngles(packedAngles, nSts, nRx):
    fbType = 0
    cbSize = [6, 4]
    if (nSts == 2) and (nRx == 1):
        anglesOrder = [6, 4]
        nAngles = 2
        unpackAngles = unPackedAngles(packedAngles, nAngles, anglesOrder)
        phi = phiAngleConversion(unpackAngles[::nAngles], cbSize[0])
        psi = unpackAngles[1::nAngles]
        phiAngles = phi
        psiAngles = psi
    elif (nSts == 3) and (nRx == 1):
        anglesOrder = [6, 6, 4, 4]
        nAngles = 4
        unpackAngles = unPackedAngles(packedAngles, nAngles, anglesOrder)
        phi1 = phiAngleConversion(unpackAngles[::nAngles], cbSize[0])
        phi2 = phiAngleConversion(unpackAngles[1::nAngles], cbSize[0])
        psi1 = unpackAngles[2::nAngles]
        psi2 = unpackAngles[3::nAngles]
        phiAngles = [phi1, phi2]
        psiAngles = [psi1, psi2]
    elif (nSts == 4) and (nRx == 1):
        anglesOrder = [6, 6, 6, 4, 4, 4];
        nAngles = 6
        unpackAngles = unPackedAngles(packedAngles, nAngles, anglesOrder)
        unpackAngles = unPackedAngles(packedAngles, nAngles, anglesOrder)
        phi1 = phiAngleConversion(unpackAngles[::nAngles], cbSize[0])
        phi2 = phiAngleConversion(unpackAngles[1::nAngles], cbSize[0])
        phi3 = phiAngleConversion(unpackAngles[2::nAngles], cbSize[0])
        psi1 = unpackAngles[3::nAngles]
        psi2 = unpackAngles[4::nAngles]
        psi3 = unpackAngles[5::nAngles]
        phiAngles = [phi1, phi2, phi3]
        psiAngles = [psi1, psi2, psi3]

    return phiAngles, psiAngles


def unPackedAngles(packedAngles, nAngles, anglesOrder):
    iDataSc = 0
    remValue = 0
    remBits = 0
    phiPsiAngles = []
    for iAngle in range (0, len(packedAngles)):
        packedByte = packedAngles[iAngle]
        updatedByte = (packedByte << remBits) + remValue
        maskedByte = 2**anglesOrder[iDataSc % nAngles]-1
        phiPsiAngle = updatedByte & maskedByte
        phiPsiAngles.append(phiPsiAngle)
        remValue = updatedByte >> anglesOrder[iDataSc % nAngles]
        remBits = 8 + remBits - anglesOrder[iDataSc % nAngles]
        iDataSc = iDataSc + 1
        if (remBits >= anglesOrder[iDataSc % nAngles]): # If remaining bits >= number of code bits.
            maskedByte = 2**anglesOrder[iDataSc % nAngles]-1
            phiPsiAngle = remValue & maskedByte
            phiPsiAngles.append(phiPsiAngle)
            remValue = remValue >> anglesOrder[iDataSc % nAngles]
            remBits = remBits - anglesOrder[iDataSc % nAngles]
            iDataSc = iDataSc + 1

    return phiPsiAngles

def phiAngleConversion(phiArray, bitSize):
    # 1. Angles are represent in terms of 0 to 63. if bit occupancy is 6.
    # 2. Represent in terms of bit value -32:31.
    # 3. Needs to represent in terms of -32 to 31. {0 : 31} for +ve values
    #    To get {-32 to -1} from {32 to 63} by substracting 64.
    for iSc in range(0, len(phiArray)):
        if (phiArray[iSc] >= 2**(bitSize-1)):
            phiArray[iSc] = phiArray[iSc] - 2**bitSize;

    return phiArray


class RevParams(object):
    s_no       = ''
    date       = ''
    codebase   = ''
    cl_no      = ''
    targetname = ''
    toolkit    = ''
    afe        = ''
    matlab     = ''
    comments   = ''

    def __init__(self):
        self.s_no       = ''
        self.date       = ''
        self.codebase   = ''
        self.cl_no      = ''
        self.targetname = ''
        self.toolkit    = ''
        self.afe        = ''
        self.matlab     = ''
        self.comments   = ''

    def updateParams(self,configDict):
        self.s_no       = configDict['s_no']
        self.date       = configDict['date']
        self.codebase   = configDict['codebase']
        self.cl_no      = configDict['cl_no']
        self.targetname = configDict['targetname']
        self.toolkit    = configDict['toolkit']
        self.afe        = configDict['afe']
        self.matlab     = configDict['matlab']
        self.comments   = configDict['comments']
