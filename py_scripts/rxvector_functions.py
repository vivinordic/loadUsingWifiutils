#-------------------------------------------------------------------------------
# Name:        rxvector_functions.py
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
import math
import DUT_functions

from common_utils import *
#from CSUtils import DA
from rxvector_regdef import *
from rxvector_utils import *
################################################
DUT_dsssHeader = DsssHeader()
DUT_lsigHeader = LSigHeader()
DUT_htsig1Header = HtSig1Header()
DUT_htsig2Header = HtSig2Header()
DUT_vhtSigA1Header = VhtSigA1Header()
DUT_vhtSigA2Header = VhtSigA2Header()
DUT_hesuSigA1Header = HESUSigA1Hdr()
DUT_hesuSigA2Header = HESUSigA2Hdr()

def headerNonHtModulation(DUT_RxVector, DUT_rxVectorHdrParams):
    if DUT_RxVector.nonHtModulation == 0:
       #header 6 bytes
       DUT_rxVectorHdrParams.dsssHdrBytes = (DUT_RxVector.headerBytes1 & 0xFFFFFFFF) or ((DUT_RxVector.headerBytes2 & 0x000000FF) << 32)
       DUT_dsssHeader.updateParams(DUT_rxVectorHdrParams.dsssHdrBytes)
       dssshdr = getDsssHdr(DUT_dsssHeader)

    elif DUT_RxVector.nonHtModulation == 1:
        #header 3 bytes
        DUT_rxVectorHdrParams.lsigBytes = (DUT_RxVector.headerBytes1 & 0x00FFFFFF)
        DUT_lsigHeader.updateParams(DUT_rxVectorHdrParams.lsigBytes)
        lsigHdr = getLsigHdr(DUT_lsigHeader)

def headerHTmixedMode (DUT_RxVector, DUT_rxVectorHdrParams):
    print ("ht mm\n")
    # headerLsig = headr [2:0]
    DUT_rxVectorHdrParams.lsigBytes = (DUT_RxVector.headerBytes1 & 0x00FFFFFF)
    DUT_lsigHeader.updateParams(DUT_rxVectorHdrParams.lsigBytes)
    lsigHdr = getLsigHdr(DUT_lsigHeader)

    # headerhtSig = header [8:3]
    DUT_rxVectorHdrParams.htSig1Bytes = ((DUT_RxVector.headerBytes2 & 0x0000FFFF) << 8) or ((DUT_RxVector.headerBytes1 & 0xFF000000) >> 24)

    DUT_rxVectorHdrParams.htSig2Bytes =((DUT_RxVector.headerBytes3 & 0x000000FF) << 16) or ((DUT_RxVector.headerBytes2 & 0xFFFF0000) >> 16)

    DUT_htsig1Header.updateParams(DUT_rxVectorHdrParams.htSig1Bytes)
    DUT_htsig2Header.updateParams(DUT_rxVectorHdrParams.htSig2Bytes)
    printHtSig1Hdr(DUT_htsig1Header)
    printHtSig2Hdr(DUT_htsig2Header)

def headerHTgreenField (DUT_RxVector, DUT_rxVectorHdrParams):
    #  headerhtSig = header [5:0]
    DUT_rxVectorHdrParams.htSig1Bytes = ((DUT_RxVector.headerBytes1 & 0x00FFFFFF) << 0)
    DUT_rxVectorHdrParams.htSig2Bytes = ((DUT_RxVector.headerBytes2 & 0x0000FFFF) << 8) or ((DUT_RxVector.headerBytes1 & 0xFF000000) >> 24)

    DUT_htsig1Header.updateParams(DUT_rxVectorHdrParams.htSig1Bytes)
    DUT_htsig2Header.updateParams(DUT_rxVectorHdrParams.htSig2Bytes)
    printHtSig1Hdr(DUT_htsig1Header)
    printHtSig2Hdr(DUT_htsig2Header)

def headerVHTSigField (DUT_RxVector, DUT_rxVectorHdrParams):
    #  headerLsig = headr [2:0]
    DUT_rxVectorHdrParams.lsigBytes = (DUT_RxVector.headerBytes1 & 0x00FFFFFF)
    DUT_lsigHeader.updateParams(DUT_rxVectorHdrParams.lsigBytes)
    lsigHdr = getLsigHdr(DUT_lsigHeader)

    # headerVHTSigField_sigA = header [8:3]

    DUT_rxVectorHdrParams.VhtSigA1Bytes = ((DUT_RxVector.headerBytes2 & 0x0000FFFF) << 8) or ((DUT_RxVector.headerBytes1 & 0xFF000000) >> 24)
    DUT_rxVectorHdrParams.VhtSigA2Bytes = ((DUT_RxVector.headerBytes3 & 0x000000FF) << 16) or ((DUT_RxVector.headerBytes2 & 0xFFFF0000) >> 16)
    DUT_vhtSigA1Header.updateParams(DUT_rxVectorHdrParams.VhtSigA1Bytes)
    DUT_vhtSigA2Header.updateParams(DUT_rxVectorHdrParams.VhtSigA2Bytes)

    # headerVHTSigField_sigB = header [12:9]
    DUT_rxVectorHdrParams.VhtSigBBytes = ((DUT_RxVector.headerBytes4 & 0x000000FF) << 24) or ((DUT_RxVector.headerBytes3 & 0xFFFFFF00) >> 8)
    VHTSigBHeader (DUT_vhtSigA1Header, DUT_rxVectorHdrParams.VhtSigBBytes)
    printVhtSigA1Hdr (DUT_vhtSigA1Header);
    printVhtSigA2Hdr (DUT_vhtSigA2Header);

def VHTSigBHeader (DUT_vhtSigA1Header, VHTSigBHdrBytes):
    if DUT_vhtSigA1Header.groupId == 0 or DUT_vhtSigA1Header.groupId == 63:
        debugPrintRxVect("VHT Sig B Single User")
        DUT_vhtSigBHdr = VhtSigBHdr_SU()
        if DUT_vhtSigA1Header.bw == DUT_CBW.CBW_20:
            DUT_vhtSigBHdr.length = VHTSigBHdrBytes & 0x0001FFFF
        elif DUT_vhtSigA1Header.bw == DUT_CBW.CBW_40:
            DUT_vhtSigBHdr.length = VHTSigBHdrBytes & 0x0007FFFF
        else:
            DUT_vhtSigBHdr.length = VHTSigBHdrBytes & 0x001FFFFF
        printVhtSigBSUHdr (DUT_vhtSigBHdr)
    else:
        debugPrintRxVect("VHT Sig B Multi User")
        DUT_vhtSigBHdr = VhtSigBHdr_MU()
        if DUT_vhtSigA1Header.bw == DUT_CBW.CBW_20:
            DUT_vhtSigBHdr.length = VHTSigBHdrBytes & 0x0000FFFF
            DUT_vhtSigBHdr.vht_mcs = (VHTSigBHdrBytes & 0x000F0000) >> 16
        elif DUT_vhtSigA1Header.bw == DUT_CBW.CBW_40:
            DUT_vhtSigBHdr.length = VHTSigBHdrBytes & 0x0001FFFF
            DUT_vhtSigBHdr.vht_mcs = (VHTSigBHdrBytes & 0x001E0000) >> 17
        else:
            DUT_vhtSigBHdr.length = VHTSigBHdrBytes & 0x0007FFFF
            DUT_vhtSigBHdr.vht_mcs = (VHTSigBHdrBytes & 0x00780000) >> 19
        printVhtSigBMuHdr (DUT_vhtSigBHdr)

def headerHeSU (DUT_RxVector, DUT_rxVectorHdrParams):
    #  headerLsig = headr [2:0]
    # headerhe_sigA = header [8:3]
    #  headerLsig = headr [2:0]
    DUT_rxVectorHdrParams.lsigBytes = (DUT_RxVector.headerBytes1 & 0x00FFFFFF)
    DUT_lsigHeader.updateParams(DUT_rxVectorHdrParams.lsigBytes)
    lsigHdr = getLsigHdr(DUT_lsigHeader)

    # headerVHTSigField_sigA = header [8:3]

    DUT_rxVectorHdrParams.heSigA1Bytes = ((DUT_RxVector.headerBytes2 & 0x0003FFFF) << 8) or ((DUT_RxVector.headerBytes1 & 0xFF000000) >> 24)
    DUT_rxVectorHdrParams.heSigA2Bytes = ((DUT_RxVector.headerBytes3 & 0x00000FFF) << 14) or ((DUT_RxVector.headerBytes2 & 0xFFFC0000) >> 18)
    #TODO
    DUT_hesuSigA1Header.updateParams(DUT_rxVectorHdrParams.heSigA1Bytes)
    DUT_hesuSigA2Header.updateParams(DUT_rxVectorHdrParams.heSigA2Bytes)
    printHeSigA1Hdr(DUT_hesuSigA1Header)
    printHeSigA2Hdr(DUT_hesuSigA2Header)

def headerHeERSu (DUT_RxVector):
    #  headerLsig = headr [2:0]
    # headerhe_sigA = header [8:3]
    #TODO

    DUT_rxVectorHdrParams.lsigBytes = (DUT_RxVector.headerBytes1 & 0x00FFFFFF)
    DUT_lsigHeader.updateParams(DUT_rxVectorHdrParams.lsigBytes)
    lsigHdr = getLsigHdr(DUT_lsigHeader)

    # headerVHTSigField_sigA = header [8:3]

    DUT_rxVectorHdrParams.heSigA1Bytes = ((DUT_RxVector.headerBytes2 & 0x0003FFFF) << 8) or ((DUT_RxVector.headerBytes1 & 0xFF000000) >> 24)
    DUT_rxVectorHdrParams.heSigA2Bytes = ((DUT_RxVector.headerBytes3 & 0x00000FFF) << 14) or ((DUT_RxVector.headerBytes2 & 0xFFFC0000) >> 18)
    #TODO
    DUT_hesuSigA1Header.updateParams(DUT_rxVectorHdrParams.heSigA1Bytes)
    DUT_hesuSigA2Header.updateParams(DUT_rxVectorHdrParams.heSigA2Bytes)
    printHeSigA1Hdr(DUT_hesuSigA1Header)
    printHeSigA2Hdr(DUT_hesuSigA2Header)

def headerHeMU (DUT_RxVector, DUT_rxVectorHdrParams):
    #  headerLsig = headr [2:0]
    # headerhe_sigA = header [8:3]
    # headerhe_sigB = header [13:9] #common filed
    #headerhe_sigB = header[16:14] #User field for which STA-ID matches
    #TODO
    DUT_rxVectorHdrParams.lsigBytes = (DUT_RxVector.headerBytes1 & 0x00FFFFFF)
    DUT_lsigHeader.updateParams(DUT_rxVectorHdrParams.lsigBytes)
    lsigHdr = getLsigHdr(DUT_lsigHeader)
    print ("he mu\n")

def headerHeTb (DUT_RxVector):
    #TODO
    print("he tb\n")


def initRxVectorExcelSheet(rxvectorDict, testcaseIdx):
    resultsConsld = ResultsOut()
    outFile = 'WLANPHY.RXVectorReport_'+str(testcaseIdx)+'.xlsx'
    resultsConsld.prepareXlsx(outFile)
    heading = rxvectorDict.keys()
    heading += ['totalCFOInKHz']
    heading += ['matCFOInKHz']
    heading += ['pktIdx']
    heading += ['OFDM_CORRELATION_PASS_COUNT', 'LTF_CORRELATION_FAIL_COUNT', 'LSIG_DECODE_FAIL_COUNT', \
    'HT-SIG_DECODE_FAIL_COUNT', 'VHT-SIGA_DECODE_FAIL_COUNT', 'HE-SIGA_DECODE_FAIL_COUNT', \
    'HE-SIGB_DECODE_FAIL_COUNT', 'CRC32PassCount', 'CRC32FailCount', 'CRC8PassCount', 'CRC8FailCount', \
    'LG-FrameCount', 'HT-FrameCount', 'VHT-FrameCount', 'HESU-FrameCount', 'HEERSU-FrameCount', 'HEMU-FrameCount', \
    'Unsupported-FrameCount', 'OtherStaId-FrameCount', 'VHTNDP-FrameCount', 'HESUNDP-FrameCount', 'S2LTimeOutFailCount', \
    'PoPEventCount']
    resultsConsld.worksheet.write_row('A1', heading)
    rowNum = 2
    return resultsConsld, heading, rowNum


def logrxvectResults(rxvectorDict, resultsConsld, rowNum, heading, total_cfoInKhz, pktIdx, rx_stats, totalErrorsLogged, matcfoKhz):
    resultsList = []
    for i in heading:
        if (i in rxvectorDict.keys()):
            resultsList.append(str(rxvectorDict[i]))
    resultsList.append(total_cfoInKhz)
    resultsList.append(matcfoKhz)
    resultsList.append(pktIdx)
    for i in range(totalErrorsLogged):
        resultsList.append(rx_stats[i])
    print(resultsList)
    resultsConsld.worksheet.write_row('A' + str(rowNum), resultsList)

def convertRxVectasDict(testConfigParams, systemParams, DUT_RxVector, operatingBand, channelNum, snr, formattype, matDict):
    rxvectorDict = {}
    toa=0x000000
    if(systemParams.CBW == 0):
        OBW = 20e6
    elif(systemParams.CBW == 1):
        OBW = 40e6
    elif(systemParams.CBW == 2):
        OBW = 80e6

    #Ts = 1/Fs
    rxvectorDict.update ({'mpduLength' : DUT_RxVector.mpduLength})
    rxvectorDict.update ({'frameFormat' : DUT_RxVector.frameFormat})
    rxvectorDict.update ({'nonHtModulation' : DUT_RxVector.nonHtModulation})
    rxvectorDict.update ({'aggregation' : DUT_RxVector.aggregation})
    rxvectorDict.update ({'sbw' : DUT_RxVector.sbw})
    rxvectorDict.update ({'mcsOrRate' : DUT_RxVector.mcsOrRate})
    toa = DUT_RxVector.timeOfArrival1 and 0x000FFF #LSB
    toa = DUT_RxVector.timeOfArrival2 and 0xFFF000 #MSB
    rxvectorDict.update ({'timeOfArrival' : toa})
    #rxvectorDict.update ({'timeOfArrival2' : DUT_RxVector.timeOfArrival2})
    rxvectorDict.update ({'rssi' : DUT_RxVector.rssi})
    rxvectorDict.update ({'estGain' : DUT_RxVector.estGain})
    rxvectorDict.update ({'mappedGain' : DUT_RxVector.mappedGain})
    rxvectorDict.update ({'digitalGain' : DUT_RxVector.digitalGain})
    dutCfo = DUT_RxVector.cfo
    if testConfigParams.subFuncTestPlan == 'CFOMeasurements':
        matcfo = matDict['cfosigppm']
    else:
        matcfo = 0
    dutCfoInKHz, matCfoInKHz = DUT_functions.getCfoInKHz(dutCfo, matcfo, operatingBand, channelNum, formattype)
    rxvectorDict.update ({'cfo' : DUT_RxVector.cfo})
    rxvectorDict.update ({'cfoAfterConversion' : dutCfoInKHz})
    rxvectorDict.update ({'sfo' : DUT_RxVector.sfo})
    rxvectorDict.update ({'inputsnr' : snr})
    rxvectorDict.update ({'s2lIndex' : DUT_RxVector.s2lIndex})
    rxvectorDict.update ({'fsb' : DUT_RxVector.fsb})
    rxvectorDict.update ({'fsbAdjust' : DUT_RxVector.fsbAdjust})
    dc_real=(DUT_RxVector.dc&0xFFF000)>>12
    dc_imag=DUT_RxVector.dc&0x000FFF
    dc_complex = complex(dc_real,dc_imag)  #Complex real+jImag
    rxvectorDict.update ({'dc' : dc_complex})
    rxvectorDict.update ({'snr(dB)' : DUT_RxVector.snr})
    rxvectorDict.update ({'ltfrssi' : DUT_RxVector.ltfrssi})
    rxvectorDict.update ({'uplinkFlag' : DUT_RxVector.uplinkFlag})
    rxvectorDict.update ({'bssColor' : DUT_RxVector.bssColor})
    rxvectorDict.update ({'TXOP' : DUT_RxVector.TXOP})
    rxvectorDict.update ({'aidOrstaID' : DUT_RxVector.aidOrstaID})
    rxvectorDict.update ({'digitalGain2' : DUT_RxVector.digitalGain2})
    rxvectorDict.update ({'mappedGain2' : DUT_RxVector.mappedGain2})
    rxvectorDict.update ({'estGain2' : DUT_RxVector.estGain2})
    rxvectorDict.update ({'dc2' : DUT_RxVector.dc2})
    return rxvectorDict, matCfoInKHz

switcher = {
         0: headerNonHtModulation,
         1: headerHTmixedMode,
         2: headerHTgreenField,
         3: headerVHTSigField,
         4: headerHeSU,
         5: headerHeMU,
         6: headerHeERSu,
         7: headerHeTb,
}

def parseHeaderBytes(DUT_RxVector, DUT_rxVectorHdrParams):
    func = switcher.get(DUT_RxVector.frameFormat, lambda: "Invalid FrameFormat")
    func(DUT_RxVector, DUT_rxVectorHdrParams)

def calculateTxTimefromSigInfo (formatType, preambleType, payloadLength):
    print("payload length: " + str(payloadLength))
    if formatType == '11B':
        #For DSSS, length field in Header is in microseconds
        dataTime_us = math.ceil(payloadLength)
        if preambleType=='LONG':
            txTime_us = 144 + 48 + dataTime_us  # For Long preamble
        else:
            txTime_us = 72 + 48 + dataTime_us  # For Short preamble
    elif formatType == 'HESU':
        m=2   #For HESU and HETB
        dataTime_us = math.ceil(((payloadLength+3+m)/3)*4)
        txTime_us = 20 + dataTime_us
    else:
        dataTime_us = math.ceil(((payloadLength+3)/3)*4)
        txTime_us = 20 + dataTime_us

    return txTime_us

def readMatRxVectorasDict (systemParams, testConfigParams, testCaseCount, DUT_RxVector):
    matDict = {}
    if (platform == 'linux' or platform == 'linux2'):
        vectorDumpDir = os.path.join('../matlab_exe_lin/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    else:
        vectorDumpDir = os.path.join('../matlab_exe_win/simOut/firmware/' + testConfigParams.subFuncTestPlan + '/' + testConfigParams.dut_operating_mode)
    subDir2 = 'testcase_' + '{0:05d}'.format(testCaseCount)
    vectorDumpDir = os.path.join(vectorDumpDir, subDir2)
    if os.path.exists(vectorDumpDir):
        inputFilePath=vectorDumpDir
    rxvectorFile = os.path.join(inputFilePath, 'RxVector.txt')
    #resultFile = open(rxvectorFile, 'r')
    #data = resultFile.readlines()
    with open(rxvectorFile) as f:
        for line in f:
            line1 = line.replace('\x00', '')
            line2 = line1.replace('\x01', '')
            line3 = line2.replace(':', '')
            (key, val) = line3.split()
            #print (str(key) + "=" + str(val))
            matDict[str(key)] = str(val)

    if testConfigParams.subFuncTestPlan == 'CFOMeasurements':
        rxvectorFile = os.path.join(inputFilePath, 'cfoEstParams.txt')
        with open(rxvectorFile) as f:
            for line in f:
                line1 = line.replace('\x00', ' ')
                line2 = line1.replace('\x01', ' ')
                line3 = line2.replace(':', ' ')
                (key, val) = line3.split()
                #print (str(key) + "=" + str(val))
                matDict[str(key)] = str(val)

        cfosigest = matDict['ppmValueRxVec']
        cfohesigbest = matDict['cfoPpmValUpdateFromHeSigb']
        cfodata = matDict['ppmValUpdateFromData']

        cfosigest = int(cfosigest,16)
        cfodata = int(cfodata)
        matDict.update ({'cfosigppm' : cfosigest})
        matDict.update ({'cfodatappm' : cfodata})


    return matDict

def readRxVector (systemParams, DUT_RxVector, testConfigParams, test_case_count):
    """ Function called to  parse RX Vector according to header type """
    #First 16*4= 64 bytes of rx_payload_Buffer contains Rx Vector. Read this buffer from memory.
    value_ptr = DA.EvaluateSymbol('&rxVectorParams')
    rxvector = DA.ReadMemoryBlock(value_ptr, 20, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    #debugPrintRxVect("RX Vector is " + str(rxvector))
    #Store these values into structure DUT_RxVector
    DUT_RxVector.updateParams(rxvector)
    rx_aidorstaId = DUT_RxVector.aidOrstaID
    return rx_aidorstaId

def setParamsToParse(rxVectStart, NrxVectors):
    debugPrint("Setting Rx Vector Params For Parsing")
    mtp_addr = DA.EvaluateSymbol('&TEST_PARAMS.RXVEC_START_NUM')
    DA.WriteMemoryBlock(mtp_addr, 1, DUT_ElementTypes.typeUnsigned32bit, rxVectStart, DUT_MemoryTypes.Default)

    mtp_addr = DA.EvaluateSymbol('&TEST_PARAMS.N_RXVECTORS')
    DA.WriteMemoryBlock(mtp_addr, 1, DUT_ElementTypes.typeUnsigned32bit, NrxVectors, DUT_MemoryTypes.Default)

def resetRXVectorParams ():
    value_ptr = DA.EvaluateSymbol('&rxVectorParams')
    value = 20*[0]
    DA.WriteMemoryBlock(value_ptr, 20, DUT_ElementTypes.typeUnsigned32bit, value, DUT_MemoryTypes.Default)

def determineJammerPassorFail(caseparams, heading, pktStatus, s2lcount, leeCount):
    relTimingDiffParam = caseparams[heading.index('relTimingDiff')]
    if type(relTimingDiffParam) == unicode:
        relTimingDiff = []
        relTimingDiffArr = relTimingDiffParam.split('  ')
        for iVal in range(len(relTimingDiffArr)):
            relTimingDiffVal = int(relTimingDiffArr[iVal])
            relTimingDiff.append(relTimingDiffVal)
    jammerStart = relTimingDiff[0]
    sigStart = relTimingDiff[1]
    jammerDuration = caseparams[heading.index('duration')]
    sigDuration = caseparams[heading.index('length')]
    jammerPower = caseparams[heading.index('jammerPowerdBm')]
    sigPower = caseparams[heading.index('snrdB')]
    jammerThresMargin = caseparams[heading.index('jammerHeadroomEdRssiDb')]
    jammerDetThres = caseparams[heading.index('jammerDetTh')]
    
    #When Jammer and OFDM/DSSS signal are overlapping, SIg Power should be greater than ED new threshold for successful packet decoding.
    if (jammerStart+jammerDuration) > sigStart:
        ED_newThresh = jammerPower+jammerThresMargin
        if sigPower > ED_newThresh:
            if ((pktStatus == 'OFDM PACKET CRC_PASS') or (pktStatus == 'DSSS PACKET CRC_PASS')) and (s2lcount >= jammerDetThres):
                status = 'JAMMER_PASS'
            else:
                status = 'JAMMER_FAIL'
        else:
            if (s2lcount >= jammerDetThres) and (pktStatus == 'RX_OTHER_FAIL//RX OTHER FAIL'):
                status = 'JAMMER_PASS'
            else:
                status = 'JAMMER_FAIL'
    #When OFDM/DSSS signal comes after Jammer dies, irrespective of SIG Power, OFDM/DSSS should be detected and decoded correctly.
    #If SIGPower < ED New threshold, Low Energy Event occurs and signal is detected.
    elif (jammerStart+jammerDuration) < sigStart:
        #ED_newThresh = jammerPower+jammerThresMargin
        if (s2lcount >= jammerDetThres) and ((pktStatus == 'OFDM PACKET CRC_PASS') or (pktStatus == 'DSSS PACKET CRC_PASS')):
            status = 'JAMMER_PASS'
        else:
            status = 'JAMMER_FAIL'
    return status