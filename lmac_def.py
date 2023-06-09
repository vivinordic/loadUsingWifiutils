###################################
from enum import Enum
import sys 
import subprocess 
import os 
from ctypes import *
from array import *
###################################

class LmacEventTag(Enum):
    LMAC_EVENT_RX = 0
    LMAC_EVENT_TX_DONE = 1
    LMAC_EVENT_DISCONNECTED = 2
    LMAC_EVENT_SCAN_COMPLETE = 3
    LMAC_EVENT_SCAN_ABORT_COMPLETE = 4
    LMAC_EVENT_RESET_COMPLETE = 5
    LMAC_EVENT_NOA = 6
    LMAC_EVENT_COMMAND_PROC_DONE = 7
    LMAC_EVENT_CH_PROG_DONE = 8
    LMAC_EVENT_PS_ECON_CFG_DONE = 9
    LMAC_EVENT_PS_ECON_WAKE = 10
    LMAC_EVENT_MSRMNT_COMPLETE = 11
    LMAC_EVENT_ROC_STATUS = 12
    LMAC_EVENT_FW_ERROR = 13
    LMAC_EVENT_TX_DEINIT_DONE = 14
    LMAC_EVENT_STATS = 15
    LMAC_EVENT_SLEEP_REQ = 16
    LMAC_EVENT_PWR_MON = 17

class WifiStandard(Enum):
    TESTCASE_20MHZ_11G = 1 
    TESTCASE_20MHZ_11N = 2
    TESTCASE_40MHZ_11N = 3
    TESTCASE_20MHZ_11AC = 4	
    TESTCASE_40MHZ_11AC = 5
    TESTCASE_80MHZ_11AC = 6
    TESTCASE_20MHZ_11AX = 7
    TESTCASE_40MHZ_11AX = 8

class SecurityModes(Enum):
    RPU_WEP40 = 0
    RPU_WEP104 = 1
    RPU_TKIP = 2
    RPU_CCMP = 3
    RPU_WAPI = 4
    RPU_PLAIN = 5
    RPU_TKIPMIC=6
    RPU_CCMP256=7
    RPU_GCMP=8
    RPU_GCMP256=9
    
class TestId(Enum):
    INIT = 0
    SEND_ALL_CMDS = 1
    TX = 2
    RX = 3
    TX_LOOPBACK = 4

class DataRate(Enum):
    TB_ONE_MBPS = 2
    TB_TWO_MBPS = 4
    TB_FIVEPTFIVE_MBPS = 11
    TB_ELEVEN_MBPS = 22
    TB_SIX_MBPS = 12
    TB_NINE_MBPS = 18
    TB_TWELEVE_MBPS = 24
    TB_EIGHTEEN_MBPS = 36
    TB_TWENTY_FOUR_MBPS = 48
    TB_THIRTY_SIX_MBPS = 72
    TB_FOURTYEIGHT_MBPS = 96
    TB_FIFTYFOUR_MBPS = 108
    TB_MCS0 = 128
    TB_MCS1 = 129
    TB_MCS2 = 130    
    TB_MCS3 = 131
    TB_MCS4 = 132
    TB_MCS5 = 133
    TB_MCS6 = 134
    TB_MCS7 = 135
    TB_MCS8 = 136
    TB_MCS9 = 137
    TB_MCS10 = 138
    TB_MCS11 = 139
    TB_MCS12 = 140
    TB_MCS13 = 141
    TB_MCS14 = 142
    TB_MCS15 = 143  

class ChannelSize(Enum):
    SYS_20_MHZ = 0 
    SYS_40_MHZ = 1
    SYS_80_MHZ = 2

class PacketSGI(Enum):
    LGI = 0
    SGI  = 4

class PacketFormat(Enum): 
    TX_11G_FORMAT = 0
    TX_11N_FORMAT = 8
    TX_11AC_FORMAT = 16
    TX_11HE_FORMAT = 64
    TX_11HE_ER_SU_FORMAT = 128
    
class OfdmPreamble(Enum):
    MIXED_FIELD =0
    GREEN_FIELD =1
    
class DsssPreamble(Enum):
    LONG_PREAMBLE =0
    SHORT_PREAMBLE=1
    
class SetValue(Enum):
    DISABLE =  0
    ENABLE = 1
    
class SelectValue(Enum):
    CONST = 0
    INCR = 1
    RAND = 2

class DataType(Enum):
    TYPE_8BIT=0
    TYPE_16BIT=1
    TYPE_32BIT=2

class LMAC_TB_PARAMS(Structure):
    _fields_=[('frameSrc', c_int),
    ('protectionType', c_int),
    ('tx_pkt_num', c_int),
    ('ampdu_subframe_cnt', c_int)]
 

class params(object):
    TestName        =   ''
    FrameSource     =   ''
    ProtectionType  =   ''
    TestType        =   ''
    SecurityMode    =   ''
    TxPacketNumber  =   ''
    AmpduPacketCount=   ''
    PacketType      =   ''
    PacketSize      =   ''
    DataRate        =   ''
    Aggregation     =   ''
    LDPC            =   ''
    STBC            =   ''
    ChannelBW       =   ''
    SIG             =   ''
    PacketFormat    =   ''
    DSSSPreamble    =   ''
    OFDMPreamble    =   ''
    
    
    def __init__(self):
        self.TestName           =   ''
        self.FrameSource        =   ''
        self.ProtectionType     =   ''
        self.TestType           =   ''
        self.SecurityMode       =   ''
        self.TxPacketNumber     =   ''
        self.AmpduPacketCount   =   ''
        self.PacketType         =   ''
        self.PacketSize         =   ''
        self.DataRate           =   ''
        self.Aggregation        =   ''
        self.LDPC               =   ''
        self.STBC               =   ''
        self.ChannelBW          =   ''
        self.SIG                =   ''
        self.PacketFormat       =   ''
        self.DSSSPreamble       =   ''
        self.OFDMPreamble       =   ''
    
    def updateParams(self,configDict):
        self.TestName           =   configDict['TestName']
        self.FrameSource        =   configDict['FrameSource']
        self.ProtectionType     =   configDict['ProtectionType']
        self.TestType           =   configDict['TestType']
        self.SecurityMode       =   configDict['SecurityMode']
        self.TxPacketNumber     =   configDict['TxPacketNumber']
        self.AmpduPacketCount   =   configDict['AmpduPacketCount']
        self.PacketType         =   configDict['PacketType']
        self.PacketSize         =   configDict['PacketSize']
        self.DataRate           =   configDict['DataRate']
        self.Aggregation        =   configDict['Aggregation']
        self.LDPC               =   configDict['LDPC']
        self.STBC               =   configDict['STBC']
        self.ChannelBW          =   configDict['ChannelBW']
        self.SIG                =   configDict['SIG']
        self.PacketFormat       =   configDict['PacketFormat']
        self.DSSSPreamble       =   configDict['DSSSPreamble']
        self.OFDMPreamble       =   configDict['OFDMPreamble']