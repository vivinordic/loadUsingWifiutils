#-------------------------------------------------------------------------------
# Name:        rxvector_utils.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------

################################################
import os
import time

from common_utils import *
#from CSUtils import DA
from rxvector_regdef import *
################################################

class RxVectorHdrParams(object):
    """Class for RxVector Header Decoded Variables"""
    dsssHdrBytes = ''
    lsigBytes = ''
    htSig1Bytes = ''
    htSig2Bytes = ''
    VhtSigA1Bytes = ''
    VhtSigA2Bytes = ''
    VhtSigBBytes = ''
    HeSigA1Bytes = ''
    HeSigA2Bytes = ''
    HeSigBBytes = ''

    def __init__(self):
        self.dsssHdrBytes = ''
        self.lsigBytes = ''
        self.htSig1Bytes = ''
        self.htSig2Bytes = ''
        self.VhtSigA1Bytes = ''
        self.VhtSigA2Bytes = ''
        self.VhtSigBBytes = ''
        self.HeSigA1Bytes = ''
        self.HeSigA2Bytes = ''
        self.HeSigBBytes = ''

class DsssHeader (object):
    def __init__(self):
        self.dataRate = ''
        self.service = ''
        self.length = ''
        self.crc = ''
    def updateParams (self, dsssHdr):
        self.dataRate = dsssHdr & 0x000000FF
        self.service = (dsssHdr & 0x0000FF00) >> 8
        self.length = (dsssHdr & 0xFFFF0000) >> 16
        self.crc = (dsssHdr & 0xFFFF00000000) >> 32

class LSigHeader (object):
    def __init__(self):
        self.dataRate = ''
        self.length = ''
    def updateParams (self, lsigHdr):
        self.dataRate = lsigHdr & WLAN_HEADER_L_SIG_RATE_MASK
        self.length = (lsigHdr & WLAN_HEADER_L_SIG_LENGTH_MASK) >> WLAN_HEADER_L_SIG_LENGTH_SHIFT

class HtSig1Header (object):
    def __init__(self):
        self.mcs = ''
        self.cbw = ''
        self.htLen = ''
    def updateParams (self, htsig1Hdr):
        self.mcs = (htsig1Hdr & WLAN_HEADER_HT_SIG1_MCS_MASK) >> WLAN_HEADER_HT_SIG1_MCS_SHIFT
        self.cbw = (htsig1Hdr & 0x00000080) >> 7
        self.htLen = (htsig1Hdr & WLAN_HEADER_HT_SIG1_HT_LENGTH_MASK)>> WLAN_HEADER_HT_SIG1_HT_LENGTH_SHIFT

class HtSig2Header (object):
    def __init__(self):
        self.smoothing = ''
        self.NotSounding =  ''
        self.Aggregation = ''
        self.stbc = ''
        self.fecCoding = ''
        self.shortGI = ''
        self.NESS = ''
    def updateParams (self, htsig2Hdr):
        self.smoothing = (htsig2Hdr & WLAN_HEADER_HT_SIG2_SMOOTHING_MASK) >>WLAN_HEADER_HT_SIG2_SMOOTHING_SHIFT
        self.NotSounding =  (htsig2Hdr & WLAN_HEADER_HT_SIG2_NOT_SOUNDING_MASK) >> WLAN_HEADER_HT_SIG2_NOT_SOUNDING_SHIFT
        self.Aggregation = (htsig2Hdr & WLAN_HEADER_HT_SIG2_AGGREGATION_MASK) >> WLAN_HEADER_HT_SIG2_AGGREGATION_SHIFT
        self.stbc = (htsig2Hdr & WLAN_HEADER_HT_SIG2_STBC_MASK) >> WLAN_HEADER_HT_SIG2_STBC_SHIFT
        self.fecCoding = (htsig2Hdr & WLAN_HEADER_HT_SIG2_FEC_CODING_MASK) >> WLAN_HEADER_HT_SIG2_FEC_CODING_SHIFT
        self.shortGI = (htsig2Hdr & WLAN_HEADER_HT_SIG2_SHORT_GI_MASK) >> WLAN_HEADER_HT_SIG2_SHORT_GI_SHIFT
        self.NESS = (htsig2Hdr & WLAN_HEADER_HT_SIG2_NUM_EXT_SS_MASK) >> WLAN_HEADER_HT_SIG2_NUM_EXT_SS_SHIFT


class VhtSigA1Header (object):
    def __init__(self):
        self.bw = ''
        self.stbc = ''
        self.groupId = ''
        self.Nsts_ParAID = ''
        self.Txop_psNotAllowed = ''

    def updateParams (self, vhtHdr):
        self.bw = (vhtHdr & WLAN_HEADER_VHT_SIG_A1_BW_MASK) >> WLAN_HEADER_VHT_SIG_A1_BW_SHIFT
        self.stbc = (vhtHdr & WLAN_HEADER_VHT_SIG_A1_STBC_MASK) >> WLAN_HEADER_VHT_SIG_A1_STBC_SHIFT
        self.groupId = (vhtHdr & WLAN_HEADER_VHT_SIG_A1_GROUP_ID_MASK) >> WLAN_HEADER_VHT_SIG_A1_GROUP_ID_SHIFT
        self.Nsts_ParAID = (vhtHdr & WLAN_HEADER_VHT_SIG_A1_NSTS_PARTIAL_AID_MASK) >> WLAN_HEADER_VHT_SIG_A1_NSTS_PARTIAL_AID_SHIFT
        self.Txop_psNotAllowed = (vhtHdr & WLAN_HEADER_VHT_SIG_A1_TXOP_PS_NOT_ALLOWED_MASK) >> WLAN_HEADER_VHT_SIG_A1_TXOP_PS_NOT_ALLOWED_SHIFT

class VhtSigA2Header (object):
    def __init__(self):
        self.shortGI = ''
        self.shortGI_NsyDisAmbig = ''
        self.su_mu0_coding = ''
        self.ldpcExtraOfdmSymb = ''
        self.suVht_mu0to3_coding = ''
        self.beamformed = ''
    def updateParams (self, vhtHdr):
        self.shortGI = (vhtHdr & WLAN_HEADER_VHT_SIG_A2_SHORT_GI_MASK) >> WLAN_HEADER_VHT_SIG_A2_SHORT_GI_MASK
        self.shortGI_NsyDisAmbig = (vhtHdr & WLAN_HEADER_VHT_SIG_A2_SHORT_GI_NSYM_DISAMBIG_MASK) >> WLAN_HEADER_VHT_SIG_A2_SHORT_GI_NSYM_DISAMBIG_SHIFT
        self.su_mu0_coding = (vhtHdr & WLAN_HEADER_VHT_SIG_A2_SU_MU0_CODING_MASK) >> WLAN_HEADER_VHT_SIG_A2_SU_MU0_CODING_SHIFT
        self.ldpcExtraOfdmSymb = (vhtHdr & WLAN_HEADER_VHT_SIG_A2_LDPC_EXTRA_SYM_MASK) >> WLAN_HEADER_VHT_SIG_A2_LDPC_EXTRA_SYM_SHIFT
        self.suVHT_mu0to3_coding = (vhtHdr & WLAN_HEADER_VHT_SIG_A2_SU_VHT_MCS_MU_CODING_MASK) >> WLAN_HEADER_VHT_SIG_A2_SU_VHT_MCS_MU_CODING_SHIFT
        self.beamformed = (vhtHdr & WLAN_HEADER_VHT_SIG_A2_BEAMFORMED_MASK) >> WLAN_HEADER_VHT_SIG_A2_BEAMFORMED_SHIFT

class VhtSigBHdr_SU (object):
    length = ''

    def __init__(self):
        self.length = ''

class VhtSigBHdr_MU (object):
    length = ''
    vht_mcs = ''

    def __init__(self):
        self.length = ''
        self.vht_mcs = ''

class HESUSigA1Hdr (object):
    def __init__(self):
        self.format = ''
        self.beamChange = ''
        self.ulorDl = ''
        self.heMcs = ''
        self.dcm = ''
        self.bssColour = ''
        self.spatialReuse = ''
        self.bandwidth = ''
        self.GI_HEltfSize = ''
        self.nsts_midamblePeriodicity = ''

    def updateParams (self, heHdr):
        self.format = (heHdr & WLAN_HEADER_HE_SIG_A1_FORMAT_MASK) >> WLAN_HEADER_HE_SIG_A1_FORMAT_SHIFT
        self.beamChange = (heHdr & WLAN_HEADER_HE_SIG_A1_BEAM_CHANGE_MASK) >> WLAN_HEADER_HE_SIG_A1_BEAM_CHANGE_SHIFT
        self.ulorDl = (heHdr & WLAN_HEADER_HE_SIG_A1_UL_DL_MASK) >> WLAN_HEADER_HE_SIG_A1_UL_DL_SHIFT
        self.heMcs = (heHdr & WLAN_HEADER_HE_SIG_A1_HE_MCS_MASK) >> WLAN_HEADER_HE_SIG_A1_HE_MCS_SHIFT
        self.dcm = (heHdr & WLAN_HEADER_HE_SIG_A1_DCM_MASK) >> WLAN_HEADER_HE_SIG_A1_DCM_SHIFT
        self.bssColour = (heHdr & WLAN_HEADER_HE_SIG_A1_BSS_COLOR_MASK) >> WLAN_HEADER_HE_SIG_A1_BSS_COLOR_SHIFT
        self.spatialReuse = (heHdr & WLAN_HEADER_HE_SIG_A1_SPATIAL_REUSE_MASK) >> WLAN_HEADER_HE_SIG_A1_SPATIAL_REUSE_SHIFT
        self.bandwidth = (heHdr & WLAN_HEADER_HE_SIG_A1_BANDWIDTH_MASK) >> WLAN_HEADER_HE_SIG_A1_BANDWIDTH_SHIFT
        self.GI_HEltfSize = (heHdr & WLAN_HEADER_HE_SIG_A1_GI_PLUS_HE_LTF_SIZE_MASK) >> WLAN_HEADER_HE_SIG_A1_GI_PLUS_HE_LTF_SIZE_SHIFT
        self.nsts_midamblePeriodicity = (heHdr & WLAN_HEADER_HE_SIG_A1_NSTS_AND_MIDAMBLE_PERIODICITY_MASK) >> WLAN_HEADER_HE_SIG_A1_NSTS_AND_MIDAMBLE_PERIODICITY_SHIFT

class HESUSigA2Hdr (object):
    def __init__(self):
        self.txop = ''
        self.coding = ''
        self.ldpcExtraSymbSegment = ''
        self.stbc = ''
        self.beamformed = ''
        self.preFECPaddingFactor = ''
        self.PEDisambiguity = ''
        self.doppler = ''
        self.crc = ''

    def updateParams (self, heHdr):
        self.txop = (heHdr & WLAN_HEADER_HE_SIG_A2_TXOP_MASK) >> WLAN_HEADER_HE_SIG_A2_TXOP_SHIFT
        self.coding = (heHdr & WLAN_HEADER_HE_SIG_A2_CODING_MASK) >> WLAN_HEADER_HE_SIG_A2_CODING_SHIFT
        self.ldpcExtraSymbSegment = (heHdr & WLAN_HEADER_HE_SIG_A2_LDPC_EXTRA_SYMB_SEG_MASK) >> WLAN_HEADER_HE_SIG_A2_LDPC_EXTRA_SYMB_SEG_SHIFT
        self.stbc = (heHdr & WLAN_HEADER_HE_SIG_A2_STBC_MASK) >> WLAN_HEADER_HE_SIG_A2_STBC_SHIFT
        self.beamformed = (heHdr & WLAN_HEADER_HE_SIG_A2_BEAMFORMED_MASK) >> WLAN_HEADER_HE_SIG_A2_BEAMFORMED_SHIFT
        self.preFECPaddingFactor = (heHdr & WLAN_HEADER_HE_SIG_A2_PRE_FEC_PADDING_FACTOR_MASK) >> WLAN_HEADER_HE_SIG_A2_PRE_FEC_PADDING_FACTOR_SHIFT
        self.PEDisambiguity = (heHdr & WLAN_HEADER_HE_SIG_A2_PE_DISAMBIGUITY_MASK) >> WLAN_HEADER_HE_SIG_A2_PE_DISAMBIGUITY_SHIFT
        self.doppler = (heHdr & WLAN_HEADER_HE_SIG_A2_DOPPLER_MASK) >> WLAN_HEADER_HE_SIG_A2_DOPPLER_SHIFT
        self.crc = (heHdr & WLAN_HEADER_HE_SIG_A2_CRC_MASK) >> WLAN_HEADER_HE_SIG_A2_CRC_SHIFT


def getDsssHdr(DUT_dsssHeader):
    RXVectHdrPrint("\n DSSS Header Fields:")
    RXVectHdrPrint("DataRate = " + str(DUT_dsssHeader.dataRate))
    RXVectHdrPrint("Service = " + str(DUT_dsssHeader.service))
    RXVectHdrPrint("length = " + str(DUT_dsssHeader.length))
    RXVectHdrPrint("CRC = " + str(DUT_dsssHeader.crc))
    return DUT_dsssHeader

def getLsigHdr (DUT_lsigHeader):
    RXVectHdrPrint("\nLsig Fields:")
    RXVectHdrPrint("DataRate = " + str(DUT_lsigHeader.dataRate))
    RXVectHdrPrint("Length = " + str(DUT_lsigHeader.length))
    return DUT_lsigHeader

def printHtSig1Hdr (DUT_htsig1Header):
    RXVectHdrPrint("\nHT Sig1 Fields")
    RXVectHdrPrint("mcs = " + str(DUT_htsig1Header.mcs))
    RXVectHdrPrint("cbw = " + str(DUT_htsig1Header.cbw))
    RXVectHdrPrint("htLen = " + str(DUT_htsig1Header.htLen))

def printHtSig2Hdr (DUT_htsig2Header):
    RXVectHdrPrint("\nHT Sig2 Fields")
    RXVectHdrPrint("smoothing = " + str(DUT_htsig2Header.smoothing));
    RXVectHdrPrint("NOT Sounding = " + str(DUT_htsig2Header.NotSounding));
    RXVectHdrPrint("Aggregation = " + str(DUT_htsig2Header.Aggregation));
    RXVectHdrPrint("stbc = " + str(DUT_htsig2Header.stbc));
    RXVectHdrPrint("fecCoding = " + str(DUT_htsig2Header.fecCoding));
    RXVectHdrPrint("shortGI = " + str(DUT_htsig2Header.shortGI));
    RXVectHdrPrint("NESS = " + str(DUT_htsig2Header.NESS));

def printVhtSigA1Hdr (DUT_vhtSigA1Header):
    RXVectHdrPrint("\n VHT SigA1 Fields")
    RXVectHdrPrint("bw = " + str(DUT_vhtSigA1Header.bw))
    RXVectHdrPrint("stbc = " + str(DUT_vhtSigA1Header.stbc))
    RXVectHdrPrint("groupId = " + str(DUT_vhtSigA1Header.groupId))
    RXVectHdrPrint("Nsts_ParAID = " + str(DUT_vhtSigA1Header.Nsts_ParAID))
    RXVectHdrPrint("Txop_psNotAllowed = " + str(DUT_vhtSigA1Header.Txop_psNotAllowed))

def printVhtSigA2Hdr (DUT_vhtSigA2Header):
    RXVectHdrPrint("\n VHT SigA2 Fields")
    RXVectHdrPrint("shortGI = " + str(DUT_vhtSigA2Header.shortGI))
    RXVectHdrPrint("shortGI_NsyDisAmbig = " + str(DUT_vhtSigA2Header.shortGI_NsyDisAmbig))
    RXVectHdrPrint("su_mu0_coding = " + str(DUT_vhtSigA2Header.su_mu0_coding))
    RXVectHdrPrint("ldpcExtraOfdmSymb = " + str(DUT_vhtSigA2Header.ldpcExtraOfdmSymb))
    RXVectHdrPrint("suVht_mu0to3_coding = " + str(DUT_vhtSigA2Header.suVHT_mu0to3_coding))
    RXVectHdrPrint("beamformed = " + str(DUT_vhtSigA2Header.beamformed))

def printVhtSigBSUHdr (DUT_vhtSigBHdr):
    RXVectHdrPrint("\n VHT SigB Fields")
    RXVectHdrPrint("length = " + str(DUT_vhtSigBHdr.length))

def printVhtSigBMuHdr (DUT_vhtSigBHdr):
    RXVectHdrPrint("\n VHT SigB Fields")
    RXVectHdrPrint("length = " + str(DUT_vhtSigBHdr.length))
    RXVectHdrPrint("vht_mcs = " + str(DUT_vhtSigBHdr.vht_mcs))

def printHeSigA1Hdr(DUT_hesuSigA1Header):
    RXVectHdrPrint("\n HE SigA1 Fields")
    RXVectHdrPrint("format = " + str(DUT_hesuSigA1Header.format))
    RXVectHdrPrint("beamChange = " + str(DUT_hesuSigA1Header.beamChange))
    RXVectHdrPrint("ulorDl = " + str(DUT_hesuSigA1Header.ulorDl))
    RXVectHdrPrint("heMcs = " + str(DUT_hesuSigA1Header.heMcs))
    RXVectHdrPrint("dcm = " + str(DUT_hesuSigA1Header.dcm))
    RXVectHdrPrint("bssColour = " + str(DUT_hesuSigA1Header.bssColour))
    RXVectHdrPrint("spatialReuse = " + str(DUT_hesuSigA1Header.spatialReuse))
    RXVectHdrPrint("bandwidth = " + str(DUT_hesuSigA1Header.bandwidth))
    RXVectHdrPrint("GI_HEltfSize = " + str(DUT_hesuSigA1Header.GI_HEltfSize))
    RXVectHdrPrint("nsts_midamblePeriodicity = " + str(DUT_hesuSigA1Header.nsts_midamblePeriodicity))

def printHeSigA2Hdr(DUT_hesuSigA2Header):
    RXVectHdrPrint("\n HE SigA2 Fields")
    RXVectHdrPrint("txop = " + str(DUT_hesuSigA2Header.txop))
    RXVectHdrPrint("coding = " + str(DUT_hesuSigA2Header.coding))
    RXVectHdrPrint("ldpcExtraSymbSegment = " + str(DUT_hesuSigA2Header.ldpcExtraSymbSegment))
    RXVectHdrPrint("stbc = " + str(DUT_hesuSigA2Header.stbc))
    RXVectHdrPrint("beamformed = " + str(DUT_hesuSigA2Header.beamformed))
    RXVectHdrPrint("preFECPaddingFactor = " + str(DUT_hesuSigA2Header.preFECPaddingFactor))
    RXVectHdrPrint("PEDisambiguity = " + str(DUT_hesuSigA2Header.PEDisambiguity))
    RXVectHdrPrint("doppler = " + str(DUT_hesuSigA2Header.doppler))
    RXVectHdrPrint("crc = " + str(DUT_hesuSigA2Header.crc))


def printRxVectorParams(DUT_RxVector):
    #debugPrintRxVect("Rx Vector Fields:")
    debugPrintRxVect("mpduLength = " + str(DUT_RxVector.mpduLength));
    debugPrintRxVect("Frame Format = " + str(DUT_RxVector.frameFormat));
    debugPrintRxVect("nonHtModulation = " + str(DUT_RxVector.nonHtModulation));
    debugPrintRxVect("aggregation = " + str(DUT_RxVector.aggregation));
    debugPrintRxVect("sbw = " + str(DUT_RxVector.sbw));
    debugPrintRxVect("mcsOrRate = " + str(DUT_RxVector.mcsOrRate));
    debugPrintRxVect("timeOfArrival1 = " + str(DUT_RxVector.timeOfArrival1));
    debugPrintRxVect("timeOfArrival2 = " + str(DUT_RxVector.timeOfArrival2));
    debugPrintRxVect("rssi = " + str(DUT_RxVector.rssi));
    debugPrintRxVect("estGain = " + str(DUT_RxVector.estGain));
    debugPrintRxVect("mappedGain = " + str(DUT_RxVector.mappedGain));
    debugPrintRxVect("digitalGain = " + str(DUT_RxVector.digitalGain));
    debugPrintRxVect("cfo = " + str(DUT_RxVector.cfo));
    debugPrintRxVect("sfo = " + str(DUT_RxVector.sfo));
    debugPrintRxVect("s2lIndex = " + str(DUT_RxVector.s2lIndex));
    debugPrintRxVect("fsb = " + str(DUT_RxVector.fsb));
    debugPrintRxVect("fsbAdjust = " + str(DUT_RxVector.fsbAdjust));
    debugPrintRxVect("dc = " + str(DUT_RxVector.dc));
    debugPrintRxVect("snr = " + str(DUT_RxVector.snr));
    #debugPrintRxVect("evm = " + str(DUT_RxVector.evm));
    debugPrintRxVect("rssiHe = " + str(DUT_RxVector.rssiHe));

def printrxVectors (systemParams, matDict, DUT_RxVector):
    if(systemParams.CBW == 0):
        Fs = 2*20e6
    elif(systemParams.CBW == 1):
        Fs = 2*40e6
    elif(systemParams.CBW == 2):
        Fs = 2*80e6

    Ts = 1/Fs
    debugPrintRxVect("\nFieldName \t" + "DUT Value" + "\t" + "Matlab Value");
    debugPrintRxVect("\nmpduLength \t" + str(DUT_RxVector.mpduLength) + "\t" + str(matDict['mpduLength']));
    debugPrintRxVect("frameFormat \t " + str(DUT_RxVector.frameFormat) + "\t" + str(matDict['frameFormat']));
    debugPrintRxVect("nonHtModltn \t " + str(DUT_RxVector.nonHtModulation) + "\t" + str(matDict['nonHtModIdx']));
    debugPrintRxVect("aggregation \t " + str(DUT_RxVector.aggregation) + "\t" + str(matDict['aggregation']));
    debugPrintRxVect("sbw \t\t " + str(DUT_RxVector.sbw) + "\t" + str(matDict['sigBwIdx']));
    debugPrintRxVect("mcs \t\t " + str(DUT_RxVector.mcsOrRate) + "\t" + str(matDict['mcs']));
    debugPrintRxVect("TOA \t\t " + str(DUT_RxVector.timeOfArrival1) + "\t" + str(matDict['timeOfArrival']));
    debugPrintRxVect("TOA \t\t " + str(DUT_RxVector.timeOfArrival2) + "\t" + str(matDict['timeOfArrival']));
    debugPrintRxVect("rssi \t\t " + str(DUT_RxVector.rssi) + "\t" + str(matDict['rssi']));
    debugPrintRxVect("estGain \t " + str(DUT_RxVector.estGain) + "\t" + str(matDict['estGainDb']));
    debugPrintRxVect("mappedGain \t " + str(DUT_RxVector.mappedGain) + "\t" + str(matDict['mappedGainDb']));
    debugPrintRxVect("digitalGain \t " + str(DUT_RxVector.digitalGain) + "\t" + str(matDict['estDigitalGain']));
    if(DUT_RxVector.cfo > (pow(2,19) - 1)):
        cfo_in_hertz = ((DUT_RxVector.cfo-(pow(2,20)))/pow(2,20))*Fs #Multiply with sampling rate
        mat_cfo_hz = ((int(matDict['estCfo'])-(pow(2,20)))/pow(2,20))*Fs #Multiply with sampling rate
    else:
        cfo_in_hertz = (DUT_RxVector.cfo/pow(2,20))*Fs #Multiply with sampling rate
        mat_cfo_hz = (int(matDict['estCfo'])/pow(2,20))*Fs #Multiply with sampling rate
    cfo_in_KHz = cfo_in_hertz/1000 #Multiply with sampling rate
    mat_cfo_KHz = mat_cfo_hz/1000 #Multiply with sampling rate
    debugPrintRxVect("cfo \t\t " + str(cfo_in_KHz) + "\t" + str(mat_cfo_KHz));
    if(DUT_RxVector.sfo > (pow(2,23) - 1)):
        sfo_value = ((DUT_RxVector.sfo-(pow(2,24)))/pow(2,25))/Ts
    else:
        sfo_value = (DUT_RxVector.sfo/pow(2,24))/Ts
    debugPrintRxVect("sfo \t\t " + str(DUT_RxVector.sfo) + "\t" + str(matDict['estSfo']));
    debugPrintRxVect("s2lIndex \t " + str(DUT_RxVector.s2lIndex) + "\t" + str(matDict['s2lIndex']));
    debugPrintRxVect("fsb \t\t " + str(DUT_RxVector.fsb) + "\t" + str(matDict['fsb']));
    debugPrintRxVect("fsbAdjust \t " + str(DUT_RxVector.fsbAdjust) + "\t" + str(matDict['fsbAdjust']));
    debugPrintRxVect("dc \t\t " + str(DUT_RxVector.dc) + "\t" + str(matDict['estDcValue']));
    debugPrintRxVect("snr \t\t " + str(DUT_RxVector.snr) + "\t" + str(matDict['estSnrOnLltf']));
    #debugPrintRxVect("evm \t " + str(DUT_RxVector.evm) + "\t" + str(matDict['evmDb']));
    debugPrintRxVect("rssiHe \t " + str(DUT_RxVector.rssiHe) + "\t" + str(matDict['rssiLtf']));
    debugPrintRxVect("====================================================================");
