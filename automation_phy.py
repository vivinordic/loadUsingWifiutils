#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     09-06-2023
# Copyright:   (c) vivi 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#######################################
# Keep the imports here
import time
#import target_functions
#import lmac_utils
import sys
import subprocess
import os
#import file_operations
#import lmac_da_access
import lmac_wifiutils
import struct
import hal
import lmac_def
import evaluate_variable as ev

from ctypes import *
######################################

global silConnect

MCP_LOAD_TYPE_TAP = 0
MCP_LOAD_TYPE_CODESTORE = 1
MCP_LOAD_TYPE_DCL = 2
MCP_LOAD_TYPE_BUNDLED = 3
MCP_LOAD_TYPE_PRELOAD = 4

LOAD_INFO = {
    # A list of elfs to load
    "elfs": "release_MIPSGCC/HARNESS.elf"
    ,
    "shared": {

    },

    "bimgs": {
        1 : ['release_MIPSGCC/HARNESS.bimg']
    },
    "sharedBimg": {

    },

    "roms": {

    },

    "patchBins": {

    },

    "mcpElfs": {

    },
    "mcpLoadType" : MCP_LOAD_TYPE_CODESTORE,
    "preZeroMem" : False,
    "ram0Origin" : 0x80080000,
    "loadSliceSize"  : 256
}

ERRORS = []


def BinaryStringToIntLE(binString, size=4):
    '''Convert binary string to little endian integer'''
    if len(binString) != size:
        raise Exception("Little endian string length must match size")
    if 4 == size:
        hexString = "0X%04X%04X" % struct.unpack("<HH", binString[2] + binString[3] +
                                                 binString[0] + binString[1])
    elif 2 == size:
        hexString = "0X%04X" % struct.unpack("<H", binString[0] + binString[1])

    return int(hexString, 0)

def GenerateZeroList(sectionSize):
    return [0x00] * sectionSize

def BinaryStringToIntList(stream, offset, size):
    '''Convert Binary String to an integer list'''
    intList = []
    stream.seek(offset)
    for _ in xrange(0, size / 4):
        binString = stream.read(4)
        intList.append(BinaryStringToIntLE(binString))
    return intList

def LoadBimgFiles(probe=None):
    '''Load Bimg files'''
    filename = ""
    headerFiledSize32 = 4
    headerFiledSize16 = 2
    headerSizeOffset = 28
    addressLength = 4
    mcpCodeInterfaceRegs = {'MCP':{'CSTRCTRL': "ABS_SYS_MCP_CSTRCTRL_PLACEHOLDER",
                                   'CSTRDAT32': "ABS_SYS_MCP_CSTRDAT32_PLACEHOLDER"},
                            'MCP2':{'CSTRCTRL': "ABS_SYS_MCP2_CSTRCTRL_PLACEHOLDER",
                                   'CSTRDAT32': "ABS_SYS_MCP2_CSTRDAT32_PLACEHOLDER"},
                            'MCP3':{'CSTRCTRL': "ABS_SYS_MCP3_CSTRCTRL_PLACEHOLDER",
                                   'CSTRDAT32': "ABS_SYS_MCP3_CSTRDAT32_PLACEHOLDER"},
                            'MCP4':{'CSTRCTRL': "ABS_SYS_MCP4_CSTRCTRL_PLACEHOLDER",
                                   'CSTRDAT32': "ABS_SYS_MCP4_CSTRDAT32_PLACEHOLDER"},
                            'MCP5':{'CSTRCTRL': "ABS_SYS_MCP5_CSTRCTRL_PLACEHOLDER",
                                   'CSTRDAT32': "ABS_SYS_MCP5_CSTRDAT32_PLACEHOLDER"},
                            'MCP6':{'CSTRCTRL': "ABS_SYS_MCP6_CSTRCTRL_PLACEHOLDER",
                                   'CSTRDAT32': "ABS_SYS_MCP6_CSTRDAT32_PLACEHOLDER"}}

    mcps = []
##    if probe is not None:
##        mcps = [core for core in probe.GetCores() if "MCP" in str(core)]

    for coreId, filenames in (LOAD_INFO["bimgs"].items() +
                             LOAD_INFO["sharedBimg"].items()):
        try:
            for filename in filenames:
                # Load MCP image before loading the application.
                #thread = codescape.FindThread(probe=probe.name, soc=-1, core=coreId)
                if LOAD_INFO['mcpLoadType'] == MCP_LOAD_TYPE_PRELOAD:
                    print "Preloading MCP images..."
                    mcpRecords = []
                    parseBimgFiles(filename, ifPrint=False, mcpRecords=mcpRecords)
                    if mcpRecords != []:
                      PreLoadMCP(thread, mcpRecords)

                if LOAD_INFO['preZeroMem']:
                    print "PreZeroing memories..."
                    zeroRecords = []
                    parseBimgFiles(filename, ifPrint=False, zeroMemRecords=zeroRecords)
                    if zeroRecords != []:
                      PreZeroMem(thread, zeroRecords)

                f = open(filename, 'rb')
                f.seek(0)
                headerPrefix = f.read(4)
                f.seek(12)
                entryAddress = BinaryStringToIntLE(f.read(headerFiledSize32))
                #print(hex(entryAddress))
                if headerPrefix != b'\xBA\xDA\xBA\xAB':
                    raise Exception("this is not a bimg file")

                #print "Loading BIMG " + str(filename) + " on " + str(thread.core)
                print "Loading BIMG "
                startTime = time.time()
                #thread.Stop()
                #memory = thread.GetMemory()
                offset = headerSizeOffset
                while True:
                    f.seek(offset)
                    sectionSize = BinaryStringToIntLE(f.read(headerFiledSize32))
                    offset += headerFiledSize32
                    address = BinaryStringToIntLE(f.read(addressLength))
                    print(hex(address), hex(sectionSize))

                    offset += headerFiledSize32
                    commandOption = BinaryStringToIntLE(f.read(headerFiledSize16), size=2)
                    if commandOption in [1, 6]:
                        #print(1)
                        #print(address)
                        # If registers poke
                        pokeValue = sectionSize
                        #memory.Write(address, pokeValue)
                        hal.writeBlockNew(silConnect, address, 1, pokeValue,lmac_def.DataType.TYPE_32BIT)
                        offset += headerFiledSize32

                    elif commandOption in [0, 5]:
                        #print(0)
                        #print(address)
                        # If data load
                        offset += 2 * headerFiledSize16
                        f.seek(offset)
                        # Write no more than 4kB to memory in a single transaction (slow targets
                        # might time out).
                        sliceSize = LOAD_INFO["loadSliceSize"]
                        while (sectionSize > sliceSize):
                            #memory.Write(address, BinaryStringToIntList(f, offset, sliceSize))
                            inList = BinaryStringToIntList(f, offset, sliceSize)
                            if ((address & 0xff000000) == 0XB4000000):
                                intList =[]
                                for x in range(len(inList)/4):
                                    intList.append(((0xff00 & inList[4*x+1])<<16)+(inList[4*x]>>8))
                                    intList.append(((0xffff00 & inList[4*x+2])<<8)+(inList[4*x+1]>>16))
                                    intList.append((0xffffff00 & inList[4*x+3])+(inList[4*x+2]>>24))
                            else:
                                intList = inList
                            hal.writeBlockNew(silConnect, address, len(intList), intList, lmac_def.DataType.TYPE_32BIT)
                            if ((address & 0xff000000) == 0XB4000000):
                                address += len(intList)*4
                            else:
                                address += sliceSize
                            offset += sliceSize
                            sectionSize -= sliceSize
                        #memory.Write(address, BinaryStringToIntList(f, offset, sectionSize))
                        inList = BinaryStringToIntList(f, offset, sectionSize)
                        if ((address & 0xff000000) == 0XB4000000):
                            intList =[]
                            for x in range(len(inList)/4):
                                intList.append(((0xff00 & inList[4*x+1])<<16)+(inList[4*x]>>8))
                                intList.append(((0xffff00 & inList[4*x+2])<<8)+(inList[4*x+1]>>16))
                                intList.append((0xffffff00 & inList[4*x+3])+(inList[4*x+2]>>24))
                        else:
                            intList = inList
                        #if(address !=0xbfc00000):
                        hal.writeBlockNew(silConnect, address, len(intList), intList, lmac_def.DataType.TYPE_32BIT)
                        offset += sectionSize

                    elif commandOption in [4, 7]:
                        #print(4)
                        #print(address)
                        # If zero memory
                        offset += 2 * headerFiledSize16
                        f.seek(offset)
                        if not LOAD_INFO['preZeroMem']:
                          #memory.Write(address, GenerateZeroList(sectionSize), 1)
                          hal.writeZeroBlock(silConnect, address, sectionSize/4, lmac_def.DataType.TYPE_32BIT)
                          pass

                    elif commandOption == 2:
                        # If MCP code load
                        originalOffset = offset
                        originalSectionSize = sectionSize
                        mcpBitMask = (originalSectionSize & 0xff000000) >> 24
                        mask = 0b00100000
                        mcpId = ""
                        for i in range(6):
                            currentMCP = None
                            codeStoreCtrl = None
                            codeStoreDat = None
                            mcpName = "MCP"
                            if (mcpBitMask & mask) > 0:
                                # Each MCP has its own register interface
                                if (mcpBitMask & mask) > 1:
                                    mcpId = str(6 - i)
                                    mcpName = "MCP" + mcpId
                                    if LOAD_INFO['mcpLoadType'] == MCP_LOAD_TYPE_TAP:
                                        if len(mcps) >= (5 - i) + 1:
                                            currentMCP = mcps[5 - i]
                                    else:
                                        codeStoreCtrl = mcpCodeInterfaceRegs["MCP" + mcpId]['CSTRCTRL']
                                        codeStoreDat = mcpCodeInterfaceRegs["MCP" + mcpId]['CSTRDAT32']
                                else:
                                    mcpId = ""
                                    if LOAD_INFO['mcpLoadType'] == MCP_LOAD_TYPE_TAP:
                                        currentMCP = mcps[0]
                                    else:
                                        codeStoreCtrl = mcpCodeInterfaceRegs["MCP" + mcpId]['CSTRCTRL']
                                        codeStoreDat = mcpCodeInterfaceRegs["MCP" + mcpId]['CSTRDAT32']

                                # Get the code to load from the BIMG
                                sectionSize = originalSectionSize & 0x00ffffff
                                offset = originalOffset
                                offset += 2 * headerFiledSize16
                                f.seek(offset)
                                data = array.array("I")
                                data.fromfile(f, sectionSize/4)
                                offset += sectionSize

                                # The user has three options for different options for how to load MCP code
                                if LOAD_INFO['mcpLoadType'] == MCP_LOAD_TYPE_TAP:
                                    print "Loading MCP code to " + mcpName + " via MCP TAP"
                                    currentMCP.GetHardwareThreads()[0].GetMemory().Write(address, data)

                                elif LOAD_INFO['mcpLoadType'] == MCP_LOAD_TYPE_CODESTORE:
                                    print "Loading MCP code to " + mcpName + " via code store interface"

                                    # Set the base address of the write
                                    memory.Write(codeStoreCtrl, address)

                                    # Write the data through the code store register interface
                                    for d in data:
                                        memory.Write(codeStoreDat, d)

                                elif LOAD_INFO['mcpLoadType'] == MCP_LOAD_TYPE_DCL:
                                    print "Loading MCP code to " + mcpName + " via DCL"

                                    # Check we have a simulator, or SysProbe with firmware 2.6 or greater
                                    if probe.name.startswith("SysProbe"):
                                        firmwareVersion = probe.firmware_version.split(".")
                                        if int(firmwareVersion[0]) < 2 or int(firmwareVersion[1]) < 6:
                                            raise Exception("MCP loading via DCL requires SysProbe firmware >= 2.6")
                                    if probe.name.startswith("DA-net"):
                                        raise Exception("MCP loading via DCL is not supported on DA-net")

                                    # Set the base address of the write
                                    memory.Write(codeStoreCtrl, address)

                                    # Use DCL to write the data
                                    DCL_WriteManyWords(thread, codeStoreDat, data)

                                elif LOAD_INFO['mcpLoadType'] == MCP_LOAD_TYPE_BUNDLED:
                                    print "Loading MCP code to " + mcpName + " via BUNDLED"
                                    if probe.name.startswith("SysProbe"):
                                        firmwareVersion = probe.firmware_version.split(".")
                                        if int(firmwareVersion[0]) < 2 or int(firmwareVersion[1]) < 7:
                                            raise Exception("MCP loading via DCL requires SysProbe firmware >= 2.7")
                                    if probe.name.startswith("DA-net"):
                                        raise Exception("MCP loading via DCL is not supported on DA-net")

                                    # Set the base address of the write
                                    memory.Write(codeStoreCtrl, address)

                                    # Write the data through the code store register interface
                                    # for d in data:
                                    memory.Write(codeStoreDat, data, element_type=32)

                            mask = mask >> 1

                    elif commandOption == 3:
                        # End of Load
                        break

##                if not filename.endswith("shared.bimg"):
##                    thread.WriteRegister("pc", entryAddress)

                print "BIMG load complete in ", round(time.time() - startTime, 2), "seconds"

        except Exception as e:
            ERRORS.append("Could not load " + str(filename) + " because " + str(e))
            print "Could not load " + str(filename) + " because " + str(e)
            time.sleep(10)


def main():
    #we will add wifion wifi-off here
    silConnect.wifi_off()
    silConnect.wifi_on()
    #silConnect.execute_command('wifiutils write_wrd 0x0100 0x0')
    LoadBimgFiles()
##    silConnect.execute_command('wifiutils write_wrd 0x0100 0x1')
    silConnect.execute_command('wifiutils write_wrd 0x0100 0x1')
    a = raw_input('changing power to 12')
    address = ev.evaluateSymbol('&tx_params.txpower',LOAD_INFO["elfs"])
    hal.writeBlockNew(silConnect, address, 1, 12, lmac_def.DataType.TYPE_32BIT)
    address = ev.evaluateSymbol('&TEST_PARAMS.TX_PARAMS_UPDATION',LOAD_INFO["elfs"])
    hal.writeBlockNew(silConnect, address, 1, 1, lmac_def.DataType.TYPE_32BIT)
    b = raw_input('changing psdu legth to 2048')
    address = ev.evaluateSymbol('&tx_params.psdu_length',LOAD_INFO["elfs"])
    hal.writeBlockNew(silConnect, address, 1, 2048, lmac_def.DataType.TYPE_32BIT)
    address = ev.evaluateSymbol('&TEST_PARAMS.TX_PARAMS_UPDATION',LOAD_INFO["elfs"])
    hal.writeBlockNew(silConnect, address, 1, 1, lmac_def.DataType.TYPE_32BIT)
##    with open('lmac_bringup.txt') as f:
##        lines = f.readlines()
##    for line in lines:
##        silConnect.execute_command(line)
##    f.close()
    pass

if __name__ == '__main__':
    print("running using the wifiutils")
    silConnect=lmac_wifiutils.WiFiUtilsClient(port='/dev/ttyACM1')
    status=silConnect.connect()
    print(status)
    main()
