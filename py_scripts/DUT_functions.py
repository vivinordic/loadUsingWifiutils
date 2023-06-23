#-------------------------------------------------------------------------------
# Name:        DUT_functions.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------
""" API's to cofigure and read dut parameters """

############################################
import os, sys, time
import math

#from imgtec.console import *
#from CSUtils import DA
from common_utils import *
from rxvector_utils import *
#############################################

LG_N_DBPS_TABLE = {(0,24), (1,36), (2,48), (3,72), (4,96), (5,144), (6,192), (7,216)}


PMB_WLAN_ED_11K_TX_ON_MASK                   = 0x00000001
PMB_WLAN_ED_11K_TX_ON_SHIFT                  = 0
PMB_WLAN_ED_11K_VIRTUAL_CHANNEL_BUSY_MASK    = 0x00000002
PMB_WLAN_ED_11K_VIRTUAL_CHANNEL_BUSY_SHIFT   = 1
PMB_WLAN_ED_11K_DEBUG_MODE_EN_MASK           = 0x00000008
PMB_WLAN_ED_11K_DEBUG_MODE_EN_SHIFT          = 3


def setOperatingMode(operatingMode):
    """" Set DUT operating mode RX/TX/LOOPBACK """
    debugPrint('Setting DUT in ' + operatingMode.upper() + ' mode')
    mtp_op_mode_address = DA.EvaluateSymbol('&TEST_PARAMS.OPERATION_MODE')

    if (operatingMode.upper() == 'TX'): #PHY_PERFORMANCE - how to avoid hardcodes and use WLAN_PHY_MODE_E available in C?
        dut_operating_mode_flag = 0
    elif (operatingMode.upper() == 'RX'):
        dut_operating_mode_flag = 1
    elif (operatingMode.upper() == 'LOOP_BACK'):
        dut_operating_mode_flag = 2
    elif (operatingMode.upper() == 'FEED'):
        dut_operating_mode_flag = 7
    elif (operatingMode.upper() == 'CAPTURE'):
        dut_operating_mode_flag = 8
    DA.WriteMemoryBlock(mtp_op_mode_address, 1, DUT_ElementTypes.typeUnsigned32bit, dut_operating_mode_flag, DUT_MemoryTypes.Default)

def configSystemParams(systemParams):
    """" Config all system Params """
    setChannel(systemParams.channel)
    setnTx(systemParams.nTx)
    setnRx(systemParams.nRx)
    setP20Offset(systemParams.prime20Offset)
    setChannelBandWidth(systemParams.CBW)
    setVif(systemParams.vif)
    setStationID(systemParams.staId)
    setBssColor(systemParams.bssColor)
    setPartialAid(systemParams.partialAid)
    pass

def setChannel(channel):
    """ set channel and frequency band """
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.CHANNEL_NUM')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, channel, DUT_MemoryTypes.Default)

    # Decide the frequncy band based on channel number:
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.FREQ_BAND')
    if(channel <= 14):
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit , DUT_FreqBand.FreqBand2p4GHz, DUT_MemoryTypes.Default)
    else:
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit , DUT_FreqBand.FreqBand5GHz, DUT_MemoryTypes.Default)
    pass

def setnTx(ntx_active):
    """ set Number of transmitting Antenne """
    # If nTx comes as string from excel sheet (which happens when no. of siganl generation sources > 1), then
    # no. of ntx_active should be minimum of two source values. As per our current implemention, min of nTx is 1.
    if type(ntx_active) == unicode:
        ntx_active = 1
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.TB_NTX')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, ntx_active, DUT_MemoryTypes.Default)

def setnRx(nrx_active):
    """ set Number of receiving Antenne """
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.TB_NRX')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, nrx_active, DUT_MemoryTypes.Default)

def setP20Offset(p20Flag):
    """ set P20offset """
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.PRIM_20_OFFSET')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, p20Flag, DUT_MemoryTypes.Default)
    pass

def setChannelBandWidth(cbw):
    """ set channel band width 0: 20MHz, 0: 40MHz, 0: 80MHz"""
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.BAND_WIDTH')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, cbw, DUT_MemoryTypes.Default)
    pass

def setChainSelection(chainSelection):
    """ set chain selection """
    debugPrint('Selecting antenna ' + str(chainSelection))
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.CHAIN_SELECTION')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, chainSelection, DUT_MemoryTypes.Default)

def setVif(vif):
    if type(vif) == int:
        mtp_address = DA.EvaluateSymbol('&(WLAN_HARNESS_SYS_PARAMS_CONFIG.vifCntrl[0])')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, vif, DUT_MemoryTypes.Default)
    else:
        vif = vif.split('  ')
        vif_list = [int(vif[0]), int(vif[1]), int(vif[2]), int(vif[3])]
        mtp_address = DA.EvaluateSymbol('&(WLAN_HARNESS_SYS_PARAMS_CONFIG.vifCntrl[0])')
        DA.WriteMemoryBlock(mtp_address, 4, DUT_ElementTypes.typeUnsigned8bit, vif_list, DUT_MemoryTypes.Default)

def setStationID(staId):
    """" SET station ID """
    if type(staId) == int:
        mtp_address = DA.EvaluateSymbol('&(WLAN_HARNESS_SYS_PARAMS_CONFIG.staId[0])')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned16bit, staId, DUT_MemoryTypes.Default)
    else:
        staId = staId.split('  ')
        staId_list = [int(staId[0]), int(staId[1]), int(staId[2]), int(staId[3])]
        mtp_address = DA.EvaluateSymbol('&(WLAN_HARNESS_SYS_PARAMS_CONFIG.staId[0])')
        DA.WriteMemoryBlock(mtp_address, 4, DUT_ElementTypes.typeUnsigned16bit, staId_list, DUT_MemoryTypes.Default)


def setBssColor(bssColor):
    """ set BSS Color """
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.bssColor[0]')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, bssColor, DUT_MemoryTypes.Default)

def setPartialAid(partialAid):
    """ set VHT partial AID """
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.partialAid')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned16bit, partialAid, DUT_MemoryTypes.Default)
def configureDUT(testConfigParams, testParams):
    """ Configure DUT and start next Testcase"""
    enableRetune()
    clearTestDoneIndication()
    startNextCase()
    pollTestReady(60)

def configFeedParams(feedParams):

    mtp_address = DA.EvaluateSymbol('&feed_signal_params.inputLength')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, feedParams[0], DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&feed_signal_params.periodLength')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, feedParams[1], DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&feed_signal_params.repeatCount')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, feedParams[2], DUT_MemoryTypes.Default)

##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.gainI')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, feedParams[3], DUT_MemoryTypes.Default)
##
##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.gainQ')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, feedParams[4], DUT_MemoryTypes.Default)
##
##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.gainAngleIQ')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, feedParams[5], DUT_MemoryTypes.Default)
##
##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.dcOffsetI')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, feedParams[6], DUT_MemoryTypes.Default)

##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.dcOffsetQ')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, feedParams[7], DUT_MemoryTypes.Default)
##
##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.sinusoidFreq')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned8bit, feedParams[8], DUT_MemoryTypes.Default)

##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.txPower')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned8bit, feedParams[9], DUT_MemoryTypes.Default)

##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.initPhaseI')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, feedParams[10], DUT_MemoryTypes.Default)
##
##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.initPhaseQ')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, feedParams[11], DUT_MemoryTypes.Default)

##    mtp_address = DA.EvaluateSymbol('&feed_signal_params.blockControl')
##    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, feedParams[12], DUT_MemoryTypes.Default)

def bypassTxscp(mode):
    """" Bypass TX SCp module """
    if (mode == 'BYPASS' ):
        debugPrint("Bypassing TXSCP module")
        mtp_address = DA.EvaluateSymbol('&feed_signal_params.blockControl')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)
    else:
        debugPrint("Enabling TXSCP module")
        mtp_address = DA.EvaluateSymbol('&feed_signal_params.blockControl')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

def exitFeed():
    mtp_address = DA.EvaluateSymbol('exitFeedLoop')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, 1, DUT_MemoryTypes.Default)

def configCaptureSignalParams(captureParams):

    mtp_address = DA.EvaluateSymbol('&capture_signal_params.inputLength')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, captureParams[0], DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&capture_signal_params.discardSampCount')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, captureParams[1], DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&capture_signal_params.repeatCount')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, captureParams[2], DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&capture_signal_params.lnaGain')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, captureParams[3], DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&capture_signal_params.bbGain')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, captureParams[4], DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&capture_signal_params.blockControl')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned16bit, captureParams[5], DUT_MemoryTypes.Default)
    pass

def configTXParams(txParams):
    """" Config tx params """
    if ('format' in txParams.keys()):
        setFrameFormat(txParams['format'])
    if ('sigBW' in txParams.keys()):
        setSignalBandWidth(txParams['sigBW'])
    if ('chBandwidth' in txParams.keys()):
        if (txParams['format'] >= DUT_FrameFormat.HE_SU):
            setSignalBandWidth(txParams['chBandwidth'])
    if ('packetLength' in txParams.keys()):
        if ('aggregationEnable' in txParams.keys()):
            if (txParams['aggregationEnable'] == 1):
                setAggregation(txParams['aggregationEnable'])
                value = DA.EvaluateSymbol('&tx_params.mpdu_length')
                DA.WriteMemoryBlock(value, txParams['nMpdu'], DUT_ElementTypes.typeSigned32bit, txParams['nMpdu']*[txParams['packetLength']], DUT_MemoryTypes.Default )
            else:
                setPayloadLength(txParams['packetLength'])
                setAggregation(0)

        else:
            setPayloadLength(txParams['packetLength'])
            setAggregation(0)
    if ('mcs' in txParams.keys()):
        setDataRate(txParams['mcs'], txParams['format'])
    if ('sgiEnable' in txParams.keys()):
        setGaurdIntervel(txParams['sgiEnable'])
    if ('giType' in txParams.keys()):
        if (txParams['format'] >= DUT_FrameFormat.HE_SU):
            setGaurdIntervel(txParams['giType'])
    else:
        setGaurdIntervel(0)
    if ('ldpcEnable' in txParams.keys()):
        setCodingStandard(txParams['ldpcEnable'])
    if ('fecCoding' in txParams.keys()):
        if (txParams['format'] >= DUT_FrameFormat.HE_SU):
            setCodingStandard(txParams['fecCoding'])
    else:
        setCodingStandard(0)
    if ('cwOffsetIdx' in txParams.keys()):
        setPrimaryBand(txParams['cwOffsetIdx'], txParams['opBW'])
    if ('nTx' in txParams.keys()):
        ntx = txParams['nTx']
    if ('nSs' in txParams.keys()):
        nss = txParams['nSs']
    else:
        nss = 1
        ntx = 1

    mtp_address = DA.EvaluateSymbol('&tx_params.num_streams')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, nss, DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&tx_params.n_tx')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, ntx, DUT_MemoryTypes.Default)

    mtp_address = DA.EvaluateSymbol('&tx_params.smoothing_enable')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

    if ('dcm' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.DCM')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, txParams['dcm'], DUT_MemoryTypes.Default)

    if ('doppler' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.doppler')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, txParams['doppler'], DUT_MemoryTypes.Default)

    if ('midamblePeriodicity' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.midamble_periodicity')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, (txParams['midamblePeriodicity']/10)-1 , DUT_MemoryTypes.Default)

##    if ('giType' in txParams.keys()):
##        mtp_address = DA.EvaluateSymbol('&tx_params.n_tx')
##        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, txParams['dcm'], DUT_MemoryTypes.Default)
    if ('heLtfType' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.HE_LTF_type')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, txParams['heLtfType'], DUT_MemoryTypes.Default)


##    if ('beamformed' in txParams.keys()):
##        mtp_address = DA.EvaluateSymbol('&tx_params.beamformed')
##        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, txParams['beamformed'], DUT_MemoryTypes.Default)
##
##    if ('beamChange' in txParams.keys()):
##        mtp_address = DA.EvaluateSymbol('&tx_params.beamChange')
##        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, txParams['beamChange'], DUT_MemoryTypes.Default)

    if ('nominalPacketPadding' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.packet_padding')
        if (txParams['nominalPacketPadding'] == 0):
            nominalPacketPadding = 0
        elif (txParams['nominalPacketPadding'] == 8):
            nominalPacketPadding = 1
        elif (txParams['nominalPacketPadding'] == 16):
            nominalPacketPadding = 2
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, nominalPacketPadding, DUT_MemoryTypes.Default)

    if ('peDuration' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.PE_duration')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, txParams['peDuration'], DUT_MemoryTypes.Default)

    if ('noSigExtn' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.no_signal_extension')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, txParams['noSigExtn'], DUT_MemoryTypes.Default)

    if ('cfoRatio' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.CFO')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned32bit, txParams['cfoRatio'], DUT_MemoryTypes.Default)

    if('triggerResponding' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.trigger_responding')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned32bit, txParams['triggerResponding'], DUT_MemoryTypes.Default)

    if('txOpDuration' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.TX_OP_duration')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned16bit, txParams['txOpDuration'], DUT_MemoryTypes.Default)




def setFrameFormat(frameFormat):
    """ Set frame format of the packet 0: 11B 1: legacy 2: Mixed Mode 3: Green Field 4: VHT """
    if(frameFormat == DUT_FrameFormat.DSSS or frameFormat == DUT_FrameFormat.LG):
        mode = 0             # 11g
    elif(frameFormat == DUT_FrameFormat.MM or frameFormat == DUT_FrameFormat.GF):
        mode = 0x8           # 11n
    elif(frameFormat == DUT_FrameFormat.VHT ):
        mode = 0x10          # 11ac
    elif(frameFormat == DUT_FrameFormat.HE_SU ):
        mode = 0x18          # 11ax
    elif(frameFormat == DUT_FrameFormat.HE_MU ):
        mode = 0x20          # 11ax
    elif(frameFormat == DUT_FrameFormat.HE_ERSU ):
        mode = 0x28          # 11ax
    elif(frameFormat == DUT_FrameFormat.HE_TB ):
        mode = 0x30          # 11ax
    else:
        mode = 0x10          # 11ac
        debugPrint( 'Wrong Format')

    value = DA.EvaluateSymbol('&tx_params.MODE')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, mode, DUT_MemoryTypes.Default )

def setSignalBandWidth(txSigbwIdx):
    """ set signal band width 0: 20MHz, 1: 40MHz, 2: 80MHz"""
    value = DA.EvaluateSymbol('&tx_params.sbw')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, txSigbwIdx, DUT_MemoryTypes.Default )

def setAggregation(aggregation):
    """ Set aggregation """
    value = DA.EvaluateSymbol('&tx_params.AGGREGATION')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, aggregation, DUT_MemoryTypes.Default )

def setPayloadLength(length):
    """ Set payload length """
    value = DA.EvaluateSymbol('&tx_params.psdu_length')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, length, DUT_MemoryTypes.Default )

def setDataRate(mcs, frameFormat):
    """ set data rate """
    g_datarate = [12, 18, 24, 36, 48, 72, 96, 108]   # 6mbps - 54mbps
    n_ac_datarate = [0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f] #MCS0 - MCS15
    dsss_datarate = [2, 4, 11, 22]  # 1mbps - 11mbps
    if(frameFormat == DUT_FrameFormat.DSSS):
        rate_r_mcs =  dsss_datarate[mcs]
    if(frameFormat == DUT_FrameFormat.LG):
        rate_r_mcs =  g_datarate[mcs]

    if((frameFormat == DUT_FrameFormat.MM or frameFormat == DUT_FrameFormat.GF) and mcs == 32):
        rate_r_mcs = n_ac_datarate[0]
    elif(frameFormat == DUT_FrameFormat.MM or frameFormat == DUT_FrameFormat.GF or frameFormat == DUT_FrameFormat.VHT ):
        rate_r_mcs = n_ac_datarate[mcs]
    elif(frameFormat >= DUT_FrameFormat.HE_SU):
        rate_r_mcs = n_ac_datarate[mcs]

    value = DA.EvaluateSymbol('&tx_params.RATE_R_MCS')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, rate_r_mcs, DUT_MemoryTypes.Default )

def setGaurdIntervel(shortGi):
    """ Set gaurd intervel 0: long gaurd, 1: short gaurd """
    value = DA.EvaluateSymbol('&tx_params.SGI')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, shortGi, DUT_MemoryTypes.Default )

def setCodingStandard(coding):
    """ Set coding standard 0: BCC, 1: LDPC """
    value = DA.EvaluateSymbol('&tx_params.LDPC')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, coding, DUT_MemoryTypes.Default )

def setLegacyLength(length):
    """ Set Legacy length for HETB cases """
    value = DA.EvaluateSymbol('&tx_params.L_length')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, length, DUT_MemoryTypes.Default )

def setFecPaddingFactor(fecPadding):
    """ Set Pre FEC padding factor for HETB cases """
    value = DA.EvaluateSymbol('&tx_params.pre_fec_padding')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, fecPadding, DUT_MemoryTypes.Default )

def setPrimaryBand(cwOffsetIdx, txOpBw):
    """ Set primary band """
    if (cwOffsetIdx==0):
        primary_band = 0
    elif (cwOffsetIdx==-1 and txOpBw==1):
        primary_band = 0
    elif (cwOffsetIdx==1 and txOpBw==1):
        primary_band = 1
    elif (cwOffsetIdx==-2 and txOpBw==2):
        primary_band = 0
    elif (cwOffsetIdx==-1 and txOpBw==2):
        primary_band = 1
    elif (cwOffsetIdx==1 and txOpBw==2):
        primary_band = 2
    elif (cwOffsetIdx==2 and txOpBw==2):
        primary_band = 3

    value = DA.EvaluateSymbol('&tx_params.primary_band')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, primary_band, DUT_MemoryTypes.Default )

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
    """ Wait for HARNESS_OUTPUT.DUT_DONE indication is set from harness to know the test case is done """
    address = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
    state = DA.ReadMemoryBlock(address, 1, DUT_ElementTypes.typeSigned32bit, DUT_MemoryTypes.Default)[0]
    timeout = time.time() + time_out_value
    while (int(state) != 1):
        time.sleep(2)
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
        time.sleep(2)
        dutReady = DA.ReadMemoryBlock(valuePtr, 1, DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]

    DA.WriteMemoryBlock(valuePtr, 1, DUT_ElementTypes.typeUnsigned8bit, 0, DUT_MemoryTypes.Default)

def pollTestReady(time_out_value):
    """" Check whether Harness has entered test loop """
    value_ptr = DA.EvaluateSymbol('&HARNESS_OUTPUT.dut_ready2')
    dut_ready2 = DA.ReadMemoryBlock(value_ptr, 1,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]
    timeout = time.time() + time_out_value # Waiting for time_out_value (seconds)
    while(dut_ready2==0):
        time.sleep(2)
        dut_ready2 = DA.ReadMemoryBlock(value_ptr, 1,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]
        if time.time() > timeout:
            break
    # clearing inication for next cas to run
    DA.WriteMemoryBlock(value_ptr, 1, DUT_ElementTypes.typeUnsigned8bit, 0, DUT_MemoryTypes.Default)

def indicatePlayoutDone():
    """" Indicate playout done to DUT """
    value = DA.EvaluateSymbol('&HARNESS_INPUT.playoutDone')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

def getRXStats():
    """" Get RX stats from Harness """
    value_ptr = DA.EvaluateSymbol('rx_stats')
    rxStatLength = 40
    rxStats = DA.ReadMemoryBlock(value_ptr, rxStatLength,  DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    print(rxStats)
    if (rxStats[1] >= 1):
        status = 'OFDM PACKET CRC_PASS'
    elif (rxStats[2] == 1):
        status = 'OFDM PACKET CRC_FAIL/RX OTHER FAIL'
    elif (rxStats[3] == 1):
        status = 'DSSS PACKET CRC_PASS'
    elif (rxStats[4] == 1):
        status = 'DSSS PACKET CRC_FAIL'
    else:
        status = 'RX_OTHER_FAIL//RX OTHER FAIL'

    edStatus = rxStats[0]
    popCnt = rxStats[24]
    spatialReuseCnt = rxStats[31]

    return status, edStatus, popCnt, spatialReuseCnt

def readOtherFailCnt():
    """ Get Lsig Pass/Fail count"""
    value_ptr = DA.EvaluateSymbol('rx_stats')
    rxStatLength = 30
    rxStats = DA.ReadMemoryBlock(value_ptr, rxStatLength,  DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    #print(rxStats)
    if (rxStats[8] == 1):
        status = 'LSIG FAIL'
    elif (rxStats[9] == 1):
        status = 'HT SIG FAIL'
    elif (rxStats[10] == 1):
        status = 'VHT SIGA FAIL'
    elif (rxStats[12] == 1):
        status = 'HE SIGA FAIL'
    elif (rxStats[13] == 1):
        status = 'HE SIGB FAIL'
    elif (rxStats[15] == 1):
        status = 'DSSS SFD FAIL'
    elif (rxStats[16] == 1):
        status = 'DSSS HDR FAIL'
    else:
        status, edcnt, popCnt, spatialReuseCnt = getRXStats()

    leeCount = rxStats[27]
    print status
    return status, rxStats[5], leeCount


def clearRxStats():
    """" clear RX stats values in Harness """
    rxStatLength = 30 #PHY_PERFORMANCE. Dont hard code. Use define. Or if possible access from C code
    value = [0]*rxStatLength
    value_ptr = DA.EvaluateSymbol('rx_stats')
    DA.WriteMemoryBlock(value_ptr, rxStatLength, DUT_ElementTypes.typeUnsigned32bit, value, DUT_MemoryTypes.Default)

def setRXInputLength(length):
    """" Get RX input length """
    value = DA.EvaluateSymbol('&HARNESS_INPUT.rxScpInputLen')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, length, DUT_MemoryTypes.Default)

def feedPayload(data_bytes_out):
    """ Feed payload bytes to Harness """
    TX_VECTOR_SIZE = 42
    value_ptr = DA.EvaluateSymbol('tx_payload_buff')
    DA.WriteMemoryBlock(value_ptr + TX_VECTOR_SIZE, len(data_bytes_out), DUT_ElementTypes.typeUnsigned8bit, data_bytes_out, DUT_MemoryTypes.Default)

def readRxPayloadBuffer(length):
    #value_ptr = DA.EvaluateSymbol('rx_payload_Buffer')
    value_ptr = DA.EvaluateSymbol('buffer_address_gram')
    payload = DA.ReadMemoryBlock(value_ptr, length,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)
    return payload

def setPayloadLengthRx(length):
    value = DA.EvaluateSymbol('&HARNESS_INPUT.rxPayloadLength')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, length, DUT_MemoryTypes.Default )

def setFrameFormatRx(formatt):
    value = DA.EvaluateSymbol('&HARNESS_INPUT.rxFrameFormat')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, formatt, DUT_MemoryTypes.Default )

def setAggregationRx(aggregation):
    value = DA.EvaluateSymbol('&HARNESS_INPUT.aggregation')
    DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned32bit, aggregation, DUT_MemoryTypes.Default )
#PHY_PERFORMANCE
def Start_calibration():
    """
    :param calib_flag
           Calibration required or not: 1 if required, 0 if not required.
    """
    # Decide whether calibration required or not:
    calib_flag = 1
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.CALIB_STATE_INFO')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, calib_flag, DUT_MemoryTypes.Default)


def Set_chain_selection(antenna_sel = ''):
    """ This function Selects the RX/TX CHAIN in SINGLE RX (SISO) case

    :param antenna_sel
         antenna_selction in SINGLE RX/TX case
    """
    DebugPrint('Selecting antenna ' + str(antenna_sel))

    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.CHAIN_SELECTION')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, antenna_sel, DUT_MemoryTypes.Default)

##    # Perform Retune and Calibration
##    Start_retune() #Generally retune_flag = 1 is required
##    Start_calibration() #Generally calib_flag = 1 is required

def stop_tx_continuous():
    stop_tx_count = 1
    value = DA.EvaluateSymbol('&TEST_PARAMS.STOP_TX_CONTINUOUS')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, stop_tx_count, DUT_MemoryTypes.Default)


def Start_retune():
    """Retune in harness.
    """
    # Perform Retune only if calibration is not enabled.
    retune = 1
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.RETUNE')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, retune, DUT_MemoryTypes.Default)

    exitRxWaitLoop()

def Clear_test_done_indication():
    """Indicates DUT that next matlab test case can be started.
    (Matlab exe waits for DUT to give this indication to proceed to next test case)"""
    #DebugPrint("Clearing the dut run done indication")
    # Give start_next_test_case = 1 in DUT for next case usage
    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.DUT_DONE')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

    numSymProcess_addr = DA.EvaluateSymbol('&HARNESS_OUTPUT.numSymInProcess')
    DA.WriteMemoryBlock(numSymProcess_addr, 1, DUT_ElementTypes.typeUnsigned8bit, 0, DUT_MemoryTypes.Default)

def Tx_start_indication():

    """ Initializes all TX test params"""

    value = DA.EvaluateSymbol('&TEST_PARAMS.TEST_STOP')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('&TEST_PARAMS.CALIB_STATE_INFO')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('&TEST_PARAMS.RETUNE')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

    packetstotransmit =0xffffffff
    value = DA.EvaluateSymbol('&TEST_PARAMS.NUM_PKTS')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeSigned32bit, packetstotransmit , DUT_MemoryTypes.Default)

    tx_params_updation =1
    value = DA.EvaluateSymbol('&TEST_PARAMS.TX_PARAMS_UPDATION')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, tx_params_updation , DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('&TEST_PARAMS.START_NEXT_CASE')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('&TEST_PARAMS.TEST_START')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

def Tx_end_indication():

    value = DA.EvaluateSymbol('&TEST_PARAMS.START_NEXT_CASE')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('&TEST_PARAMS.TEST_START')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)
    test_stop=1
    value = DA.EvaluateSymbol('&TEST_PARAMS.TEST_STOP')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, test_stop, DUT_MemoryTypes.Default)
    return test_stop

def stop_tx_continuous():
    stop_tx_count = 1
    value = DA.EvaluateSymbol('&TEST_PARAMS.STOP_TX_CONTINUOUS')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, stop_tx_count, DUT_MemoryTypes.Default)


def wait_retune_done():

#Waiting for retune done event from harness and the while loop come out if retune done event is not comming with in 60sec time.
    retune_address = DA.EvaluateSymbol('&TEST_PARAMS.RETUNE')
    retune_flag = DA.ReadMemoryBlock(retune_address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    counter = 0
    while (retune_flag[0] == 1):
        time.sleep(1)
        retune_flag = DA.ReadMemoryBlock(retune_address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
        counter += 1
        if(counter > 30):
            break




def Read_rx_stats(totalPktCount):
    """ This function reads the PHY RX Stats and computes PER,
    returns RX Stats and PER.
    Waits for the ed_cnt to become 2000 or 10 seconds, whichever is lesser"""

    time_for_search = 6 #6 # PHY_PERFORMANCE time_for_search changed from 10 to 20 in seconds
    start_time = time.time()
    end_time = time.time()

    ed_cnt = 0
    print "DUT_functions.py..Read_rx_stats(): PER calculcated after capturing data for packets ",totalPktCount

    rx_stats_ptr = DA.EvaluateSymbol('rx_stats')
    rxStatLength = 40
    rx_stats = DA.ReadMemoryBlock(rx_stats_ptr, rxStatLength, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    ed_cnt = rx_stats[rx_stats_offsets.ed_cnt.index]

    while ed_cnt < totalPktCount:
        # Wait for 1 seconds to collect the stats
        time.sleep(1)
        rx_stats = DA.ReadMemoryBlock(rx_stats_ptr, rxStatLength, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
        # Accessing PHY RX stats with offsets declared in Enum datatype rx_stats_offsets
        ed_cnt = rx_stats[rx_stats_offsets.ed_cnt.index]
        end_time = time.time()
        #print("ed_cnt = "+ str(ed_cnt) + ",  delta_time = "+ str(end_time - start_time))
        # Break the while loop after "time_for_search" sec
        if ((end_time - start_time) > time_for_search):
            break

    # Accessing PHY RX stats with offsets declared in Enum datatype rx_stats_offsets
    ed_cnt              = rx_stats[rx_stats_offsets.ed_cnt.index]
    ofdm_crc32_pass_cnt = rx_stats[rx_stats_offsets.ofdm_crc32_pass_cnt.index]
    dsss_crc32_pass_cnt = rx_stats[rx_stats_offsets.dsss_crc32_pass_cnt.index]

    # Compute PER
    if (ed_cnt == 0):
        per = 100.0 #'NaN'
    else:
        # Rounding PER to 1 values after decimal
        num_values_after_decimal = 1
        per = round( ((float(totalPktCount - ofdm_crc32_pass_cnt - dsss_crc32_pass_cnt) * 100.0) / float(totalPktCount)) , num_values_after_decimal )
        if (per < 0):  # To avoid PER becoming negative due to stray packet detection
            per = 0

    DebugPrint("ed_cnt = "+ str(ed_cnt) + ",  ofdm_crc32_pass_cnt = "+ str(ofdm_crc32_pass_cnt)+ ",dsss_crc32_pass_cnt = "+ str(dsss_crc32_pass_cnt)+ ",  per = "+str(per)+ "%")

    return rx_stats, per

def readRXstatsFromPeripheralRegs():
    """ Reads TMFD registers for RX stats """
    rx_stats_ptr = DA.EvaluateSymbol('TMFD.WLAN_RTM_FD_STATS_COUNTER_0')
    rxStatLength = 7
    rx_stats1 = DA.ReadMemoryBlock(rx_stats_ptr, rxStatLength, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    rx_stats = []
    for index in range(rxStatLength):
        rx_stats.append(rx_stats1[index]>>8)
    return rx_stats

def readCRCcountsFromPeripheral(rx_stats1):
    rx_stats_ptr = DA.EvaluateSymbol('DEAGG.WLAN_MAC_CTRL_DEAGG_CRC32PASS_CNT')
    rxStatLength = 4
    rx_stats2 = DA.ReadMemoryBlock(rx_stats_ptr, rxStatLength, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    for index in range(rxStatLength):
        rx_stats1.append(rx_stats2[index]>>8)

    return rx_stats1

def readFrameCountersFromPeripheral(rx_stats2):
    rx_stats_ptr = DA.EvaluateSymbol('TMFD.WLAN_RTM_FD_FRAME_COUNTER_0')
    rxStatLength = 11
    rx_stats3 = DA.ReadMemoryBlock(rx_stats_ptr, rxStatLength, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    for index in range(rxStatLength):
        rx_stats2.append(rx_stats3[index]>>8)
    return rx_stats2

def readPoPCountFromPeripheral(rx_stats3):
    rx_stats_ptr = DA.EvaluateSymbol('TMTD.WLAN_RTM_TD_STATS_COUNTER_1')
    rxStatLength = 1
    rx_stats4 = DA.ReadMemoryBlock(rx_stats_ptr, rxStatLength, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    for index in range(rxStatLength):
        rx_stats3.append(rx_stats4[index]>>8)
    return rx_stats3

def reset_rxStats():
    """Reset the rx stats
    """
    flag = 1;
    rxstatsResetFlag = DA.EvaluateSymbol('&TEST_PARAMS.rxstatsResetFlag')
    DA.WriteMemoryBlock(rxstatsResetFlag, 1, DUT_ElementTypes.typeUnsigned32bit, flag, DUT_MemoryTypes.Default)

    exitRxWaitLoop()

def exitRxWaitLoop():
    """ Indicate harness app to exit RX loop """
    exitRxWait = DA.EvaluateSymbol('&TEST_PARAMS.EXIT_RX_WAIT')
    DA.WriteMemoryBlock(exitRxWait, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)


def agcModuleEnable():
    """" Enable AGC module in TEST_PARAMS """
    agcModuleEnable = 1
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.agcModuleEnable')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, agcModuleEnable, DUT_MemoryTypes.Default)

def agcModuleDisbale():
    """" Disable AGC module in TEST_PARAMS """
    agcModuleEnable = 0
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.agcModuleEnable')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, agcModuleEnable, DUT_MemoryTypes.Default)

def readEDStatus ():
    address = DA.EvaluateSymbol('ED.WLAN_ED_STATUS_REGISTER')
    edStatus = DA.ReadMemoryBlock(address, 1, DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]

    return edStatus

def readndpCount(formattype):
    if formattype == 4:
        address = DA.EvaluateSymbol('TMFD.WLAN_RTM_FD_FRAME_COUNTER_8')
    elif formattype == 5:
        address = DA.EvaluateSymbol('TMFD.WLAN_RTM_FD_FRAME_COUNTER_9')
    ndpcount = DA.ReadMemoryBlock(address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    ndpcount = ndpcount[0] >> 8
    return ndpcount

def readEDRssi ():
    address = DA.EvaluateSymbol('&HARNESS_OUTPUT.edRssi')
    #address = DA.EvaluateSymbol('&TEST_PARAMS.edRssi')
    edRssi = DA.ReadMemoryBlock(address, 1, DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)[0]
    if edRssi > 127:
        edRssi = edRssi-256
    else:
        edRssi = edRssi
    return edRssi

def secondAgcStatus():

    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.secondAgcStatus')
    secondAgcStatus = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    return secondAgcStatus

def readCCATimerValues():
    """ Read CCA Duration Value """
    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.ccaDuration')
    ccaDuration = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    return ccaDuration


def configNhParams(anpiMaxAccmLen, anpiTxOn, anpiChanBusy):
    """" confiurataion paramets of the NH module"""

    anpiDebugModeEn = 0
    if(anpiTxOn == 1) or (anpiChanBusy == 2):
       anpiDebugModeEn = 1

    if(anpiChanBusy == 2):
       anpiChanBusy = 1

    mtp_address = DA.EvaluateSymbol('ED.WLAN_ED_IEEE802_11K_SETTINGS')
    val = DA.ReadMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    val=  val >> 8
    val = (val & ~ PMB_WLAN_ED_11K_TX_ON_MASK) | (int(anpiTxOn) << PMB_WLAN_ED_11K_TX_ON_SHIFT)
    val = (val & ~ PMB_WLAN_ED_11K_VIRTUAL_CHANNEL_BUSY_MASK)   | (int(anpiChanBusy) << PMB_WLAN_ED_11K_VIRTUAL_CHANNEL_BUSY_SHIFT)
    val = (val & ~ PMB_WLAN_ED_11K_DEBUG_MODE_EN_MASK)          | (int(anpiDebugModeEn) << PMB_WLAN_ED_11K_DEBUG_MODE_EN_SHIFT);
    val=  val << 8
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, val, DUT_MemoryTypes.Default)

    val = DA.EvaluateSymbol('&HARNESS_INPUT.anpiMaxAccmLen')
    DA.WriteMemoryBlock(val, 1, DUT_ElementTypes.typeUnsigned32bit, anpiMaxAccmLen, DUT_MemoryTypes.Default)



def getNhAccumVal():
    """" ANPI Accumulator value"""
    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.nhAccumValue')
    nhAccumValue = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    nhAccumValue = nhAccumValue - pow(2,24)
    return nhAccumValue

def getNhAccumCnt():
    """" ANPI Accumulator count"""
    value = DA.EvaluateSymbol('&HARNESS_OUTPUT.nhAccumCount')
    nhAccumCount = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    return nhAccumCount

def getAnpiEstdBm(nhAccumValue, nhAccumCount):
    """" ANPI Estimation in dBm"""

    #nhAccumValue = nhAccumValue - pow(2,24)
    ##Left shift by 4 required to get orignal value
    nhAccumValue = nhAccumValue * 16
    if(nhAccumCount == 0):
        nhAccumCount =1
    anpiEstdBm   = nhAccumValue/nhAccumCount
    return anpiEstdBm

def getCfoInKHz(dutCfo, matlabCfo, operatingBand, channelNum, formattype):
    """" Convert from PPM into CFO in KHz"""
    fc= operatingBand + (channelNum * 5 * 1e6)
    if(dutCfo > (pow(2,15) -1)):
        dutCfo = dutCfo - pow(2,16)
    if formattype == 0:
        # CFO not in PPM for DSSS pkts.
        dutCfoInKHz = (dutCfo * 11e6)/(pow(2,20))/1e3
    else:
        dutCfoInKHz = ((dutCfo * fc)/pow(2,29))/1e3

    if(matlabCfo > (pow(2,15) -1)):
        matlabCfo = matlabCfo - pow(2,16)
    if formattype == 0:
        matCfoInKHz = (matlabCfo * 11e6)/(pow(2,20))/1e3
    else:
        matCfoInKHz =  ((matlabCfo * fc)/pow(2,29))/1e3
    return dutCfoInKHz, matCfoInKHz

def getCfoStatus(dutCfo , refCfo):
    """" CFO status """
    errVal = (dutCfo - refCfo)* 1e3
    if(errVal > 2000) or (errVal < -2000):
        cfoStatus = 0
    else:
        cfoStatus = 1
    return cfoStatus


def readS2LFailCnt():
    """ Read S2L Fail Count from counter"""
    mtp_address = DA.EvaluateSymbol('TMFD.WLAN_RTM_FD_STATS_COUNTER_7')
    s2lFailCnt = DA.ReadMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    return (s2lFailCnt >> 8)

def setHemuP20Offset(prime20Flag):
    """" Indicate playout done to DUT """
    value = DA.EvaluateSymbol('&HARNESS_INPUT.prime20Flag')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, prime20Flag, DUT_MemoryTypes.Default)


def readsvdOutBuffer():
    """" Read SVD output buffer """
    svdDMAlengthPtr = DA.EvaluateSymbol('SVD.WLAN_SVD_DMA_LENGTH')
    svdDMAlength1 = DA.ReadMemoryBlock(svdDMAlengthPtr, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    svdDMAlength  = svdDMAlength1[0] >> 8
    value_ptr = DA.EvaluateSymbol('tx_payload_buff')
    svdoutBuffer = DA.ReadMemoryBlock(value_ptr, svdDMAlength,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)
    return svdoutBuffer, svdDMAlength

def svdModuleEnable():
    """" Enable SVD module in TEST_PARAMS """
    svdModuleEnable = 1
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.svdModuleEnable')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, svdModuleEnable, DUT_MemoryTypes.Default)

def svdModuleDisbale():
    """" Disable SVD module in TEST_PARAMS """
    svdModuleEnable = 0
    mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.svdModuleEnable')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, svdModuleEnable, DUT_MemoryTypes.Default)

def ftmTimeEstimation():
    """" FTM time estimation """

    mtp_address = DA.EvaluateSymbol('&HARNESS_OUTPUT.timeOfArrivalLSBytes')
    timeOfArrivalLSBytes = DA.ReadMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    debugPrint("timeOfArrivalLSBytes is: "+ str(timeOfArrivalLSBytes[0]))

    mtp_address = DA.EvaluateSymbol('&HARNESS_OUTPUT.timeOfArrivalMSBytes')
    timeOfArrivalMSBytes = DA.ReadMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    debugPrint("timeOfArrivalMSBytes is: "+ str(timeOfArrivalMSBytes[0]))


    timeOfAdcFirstSampleLsbPtr = DA.EvaluateSymbol('WLAN_CTRL.WLAN_CTRL_ADC_FIRST_SAMPLE_SNAPSHOT_LSB')
    timeOfAdcFirstSampleLsb    = DA.ReadMemoryBlock(timeOfAdcFirstSampleLsbPtr, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    timeOfAdcFirstSampleLsb    = timeOfAdcFirstSampleLsb[0] >> 8
    debugPrint("timeOfAdcFirstSampleLsb is: "+ str(timeOfAdcFirstSampleLsb))

    timeOfAdcFirstSampleMsbPtr = DA.EvaluateSymbol('WLAN_CTRL.WLAN_CTRL_ADC_FIRST_SAMPLE_SNAPSHOT_MSB')
    timeOfAdcFirstSampleMsb    = DA.ReadMemoryBlock(timeOfAdcFirstSampleMsbPtr, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    timeOfAdcFirstSampleMsb    = timeOfAdcFirstSampleMsb[0] >> 8
    debugPrint("timeOfAdcFirstSampleMsb is: "+ str(timeOfAdcFirstSampleMsb))

    diffTimeEstimationLsb = timeOfArrivalLSBytes[0] - timeOfAdcFirstSampleLsb;
    diffTimeEstimationMsb = timeOfArrivalMSBytes[0] - timeOfAdcFirstSampleMsb;
    debugPrint("diffTimeEstimationLsb is: "+ str(diffTimeEstimationLsb))


    return diffTimeEstimationMsb, diffTimeEstimationLsb

def configureSpatialReuseDUT(caseparams, heading):

    """"  configuring Spatial Reuse Parameters  """

    partialAidIdx = heading.index('partialAid')
    partialAidVal = caseparams[partialAidIdx]
    snrdBIndex = heading.index('snrdB')
    groupIdIdx = heading.index('groupId')
    formatIdx = heading.index('format')
    bssColorIdx = heading.index('bssColor')
    srgEnableIdx = heading.index('srgEnable')
    # Set BSS CHECK disable  field as 0 to run SR cases.
    bssCheckEnable = 1 # This value is inverted before configuring to the register
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.bssCheckEnable')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, bssCheckEnable, DUT_MemoryTypes.Default)

    # Corrupting BSS Color
    setBssColor((caseparams[bssColorIdx] + 1) % 64)
    if (caseparams[srgEnableIdx] == 0):
        nonSrgObssPdSrEnable = 1
        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.nonSrgObssPdSrEnable')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, nonSrgObssPdSrEnable, DUT_MemoryTypes.Default)
    elif (caseparams[srgEnableIdx] == 1):
        srgObssPdSrEnable = 1
        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.srgObssPdSrEnable')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, srgObssPdSrEnable, DUT_MemoryTypes.Default)

    threshold = -62
    nonSrgObssPdLevel = 256 + threshold
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.nonSrgObssPdLevel')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, nonSrgObssPdLevel, DUT_MemoryTypes.Default)

    srgObssPdLevel = 256 + threshold
    mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.srgObssPdLevel')
    DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, srgObssPdLevel, DUT_MemoryTypes.Default)
    if (caseparams[srgEnableIdx] == 1):
        if (caseparams[formatIdx] == 4):
            srgPartialIdBitMap = [0, 0, 0, 0, 0, 0, 0, 0]
            if (partialAidVal >= 0) and (partialAidVal <= 7):
                srgPartialIdBitMap[0] = 2**partialAidVal
            elif (partialAidVal >= 8) and (partialAidVal <= 15):
                srgPartialIdBitMap[1] = 2**(partialAidVal % 8)
            elif (partialAidVal >= 16) and (partialAidVal <= 23):
                srgPartialIdBitMap[2] = 2**(partialAidVal % 16)
            elif (partialAidVal >= 24) and (partialAidVal <= 31):
                srgPartialIdBitMap[3] = 2**(partialAidVal % 24)
            elif (partialAidVal >= 32) and (partialAidVal <= 39):
                srgPartialIdBitMap[4] = 2**(partialAidVal % 32)
            elif (partialAidVal >= 40) and (partialAidVal <= 47):
                srgPartialIdBitMap[5] = 2**(partialAidVal % 40)
            elif (partialAidVal >= 48) and (partialAidVal <= 55):
                srgPartialIdBitMap[6] = 2**(partialAidVal % 48)
            elif (partialAidVal >= 58) and (partialAidVal <= 63):
                srgPartialIdBitMap[7] = 2**(partialAidVal % 58)
            mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.srgPartialIdBitMap')
            DA.WriteMemoryBlock(mtp_address, 6, DUT_ElementTypes.typeUnsigned8bit, srgPartialIdBitMap, DUT_MemoryTypes.Default)
        else:
            bssColorVal   = caseparams[bssColorIdx]
            srgBssColorBitMap = [0, 0, 0, 0, 0, 0, 0, 0]
            if (bssColorVal >= 0) and (bssColorVal <= 7):
                srgBssColorBitMap[0] = 2**bssColorVal
            elif (bssColorVal >= 8) and (bssColorVal <= 15):
                srgBssColorBitMap[1] = 2**(bssColorVal % 8)
            elif (bssColorVal >= 16) and (bssColorVal <= 23):
                srgBssColorBitMap[2] = 2**(bssColorVal % 16)
            elif (bssColorVal >= 24) and (bssColorVal <= 31):
                srgBssColorBitMap[3] = 2**(bssColorVal % 24)
            elif (bssColorVal >= 32) and (bssColorVal <= 39):
                srgBssColorBitMap[4] = 2**(bssColorVal % 32)
            elif (bssColorVal >= 40) and (bssColorVal <= 47):
                srgBssColorBitMap[5] = 2**(bssColorVal % 40)
            elif (bssColorVal >= 48) and (bssColorVal <= 55):
                srgBssColorBitMap[6] = 2**(bssColorVal % 48)
            elif (bssColorVal >= 58) and (bssColorVal <= 63):
                srgBssColorBitMap[7] = 2**(bssColorVal % 58)

            mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.srgBssColorBitMap')
            DA.WriteMemoryBlock(mtp_address, 6, DUT_ElementTypes.typeUnsigned8bit, srgBssColorBitMap, DUT_MemoryTypes.Default)

    if (caseparams[formatIdx] == 4) and (caseparams[groupIdIdx] == 63):
        vhtPartialBssColor = 1
        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.vhtBssColorEnable')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, vhtPartialBssColor, DUT_MemoryTypes.Default)

        setPartialAid(partialAidVal - 1)

def configDigVdd(vdd):
    """ configs digital vdd for C0 board (work around remove later)"""
    DA.WriteMemoryBlock(0xA4019014, 1, DUT_ElementTypes.typeUnsigned32bit, vdd, DUT_MemoryTypes.Default)

def computePktDuration():

    value_ptr = DA.EvaluateSymbol('&HARNESS_OUTPUT.pktduration_lsb')
    duration = DA.ReadMemoryBlock(value_ptr, 2,  DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)

    if (duration[1] == 0):
        pkt_duration = duration[0]
    else:
        pkt_duration = -1 # This condition indicates MSB of pkt_duration is not 0 and needs to be calculated.

    return pkt_duration


def computeRXLatency(coreClkFreq):

    value_ptr = DA.EvaluateSymbol('&HARNESS_OUTPUT.rxLatency_lsb')
    latency = DA.ReadMemoryBlock(value_ptr, 2,  DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)

    if (latency[1] == 0):
        rx_latency = latency[0]/coreClkFreq
    else:
        rx_latency = -1 # This condition indicates MSB of RXLatency is not 0 and needs to be calculated.

    return rx_latency

def calculatePktDuration(DUT_RxVector, caseDict):
    #This function is to calculate packet duration for various formats.
    frameformat = int(caseDict['format'])
    Length = calculateLength(DUT_RxVector, frameformat)


    if frameformat == 0:
        shortGi = int(caseDict['shortGi'])
        #For DSSS, length field in Header is in microseconds
        dataTime_us = math.ceil(Length)
        if shortGi == 0:
            txTime_us = 144 + 48 + dataTime_us  # For Long preamble
        else:
            txTime_us = 72 + 24 + dataTime_us

    elif frameformat == 1:
        mcs = int(caseDict['mcs'])
        for data in LG_N_DBPS_TABLE:
            if data[0]==mcs:
                n_dbps = data[1]

        n_ofdm = math.ceil((16 + (8*Length) + 6)/float(n_dbps))
        txTime_us = 20 + (n_ofdm*4)

    elif (frameformat == 2) or (frameformat == 4):
        dataTime_us = math.ceil(((Length+3)/3.0)*4)
        txTime_us = 20 + dataTime_us

    else:
        if (frameformat == 6) or (frameformat == 7):
            m = 1
        else:
            m = 2
        dataTime_us = math.ceil(((Length+3+m)/3.0)*4)
        txTime_us = 20 + dataTime_us

    return txTime_us

def calculateLength(DUT_RxVector, frameformat):
    # This function finds out the length info from DSSS Header & L-SIG Header respectively.
    if frameformat == 0:
        #header 6 bytes
        dsssbytes = (DUT_RxVector.headerBytes1 & 0xFFFFFFFF) or ((DUT_RxVector.headerBytes2 & 0x000000FF) << 32)
        DUT_dsssHeader = DsssHeader()
        DUT_dsssHeader.updateParams(dsssbytes)
        Length = DUT_dsssHeader.length
    else:
        #header 3 bytes
        lsigBytes = (DUT_RxVector.headerBytes1 & 0x00FFFFFF)
        DUT_lsigHeader = LSigHeader()
        DUT_lsigHeader.updateParams(lsigBytes)
        Length = DUT_lsigHeader.length
    return Length

def calculateTxtimePktdurationDiff(pktDuration, TxTime, coreClkFreq):
    #This function is to know if TD snapshot starts exactly at the end of the packet.
    TxTime_cycles = TxTime*coreClkFreq
    diff = pktDuration - TxTime_cycles
    diff_us = diff/coreClkFreq
    return diff_us

def calculateTotalCFO(testConfigParams, sigestcfo, operatingBand, channelNum, formattype, matDict, matsigcfokhz):
    #address = 0xa5020d3c
    address = DA.EvaluateSymbol('AGG.WLAN_MAC_CTRL_AGG_CPE_RESIDUAL_CFO')
    value = DA.ReadMemoryBlock(address, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    residual_cfo = (value[0]>>8) & 0x0000FFFF
    if testConfigParams.subFuncTestPlan == 'CFOMeasurements':
        residual_cfoInKhz, matdatacfokhz = getCfoInKHz(residual_cfo, matDict['cfodatappm'], operatingBand, channelNum, formattype)
    else:
        residual_cfoInKhz, matdatacfokhz = getCfoInKHz(residual_cfo, 0, operatingBand, channelNum, formattype)
    total_cfo = residual_cfoInKhz + sigestcfo
    matcfokhz = matsigcfokhz + matdatacfokhz
    return total_cfo, matcfokhz

def calculateMeanAndStd(totalArray, totalpkts):

   mean = sum(totalArray)/totalpkts
   deviations = [[(i - mean)**2] for i in totalArray]
   deviationsum = 0
   for i in range(totalpkts):
        deviationsum = deviationsum + deviations[i][0]

   var = deviationsum/totalpkts
   std = math.sqrt(var)

   return mean, std

def readRFWokingChannelParams():
    value_ptr = DA.EvaluateSymbol('&RF_WORKING_CHAN_COMP_PARAMS[0].rx_calib_res[0].rxDcocCalibRes.lnaGainDcoffsetI')
    lnaGainDcoffsetI = DA.ReadMemoryBlock(value_ptr, 5,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)
    value_ptr = DA.EvaluateSymbol('&RF_WORKING_CHAN_COMP_PARAMS[0].rx_calib_res[0].rxDcocCalibRes.lnaGainDcoffsetQ')
    lnaGainDcoffsetQ = DA.ReadMemoryBlock(value_ptr, 5,  DUT_ElementTypes.typeUnsigned8bit, DUT_MemoryTypes.Default)
    value_ptr = DA.EvaluateSymbol('&RF_WORKING_CHAN_COMP_PARAMS[0].rx_calib_res[0].rxDcocCalibRes.residualDcI')
    residualDcI = DA.ReadMemoryBlock(value_ptr, 5,  DUT_ElementTypes.typeSigned16bit, DUT_MemoryTypes.Default)
    value_ptr = DA.EvaluateSymbol('&RF_WORKING_CHAN_COMP_PARAMS[0].rx_calib_res[0].rxDcocCalibRes.residualDcQ')
    residualDcQ = DA.ReadMemoryBlock(value_ptr, 5,  DUT_ElementTypes.typeSigned16bit, DUT_MemoryTypes.Default)
    print(lnaGainDcoffsetI)
    print(lnaGainDcoffsetQ)
    print(residualDcI)
    print(residualDcQ)