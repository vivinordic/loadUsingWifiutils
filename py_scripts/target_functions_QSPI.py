#-------------------------------------------------------------------------------
# Name:        target_functions.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     05/05/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------
""" API's related to target """

############################################
import os, sys, time

import lmac_wifiutils
import hal
import struct
from common_utils import *
#############################################


def loadnRunTarget(test_mode, selectPhyorMacControl):
    """ Load HARNESS script to the target and run"""
    print("running using the wifiutils")
    #silConnect=lmac_wifiutils.WiFiUtilsClient(port=targetParams.target_number)
    targetParams.silConnect.wifi_off()
    targetParams.silConnect.wifi_on()
    LoadBimgFiles()
    runTarget(targetParams.silConnect)

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

def LoadBimgFiles():
    '''Load Bimg files'''
    filenames = ["../harness/loader/build/smake/release_MIPSGCC/HARNESS.bimg"]
    headerFiledSize32 = 4
    headerFiledSize16 = 2
    headerSizeOffset = 28
    addressLength = 4
    ERRORS = []
    silConnect = targetParams.silConnect


    try:
        for filename in filenames:

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
                    hal.writeBlockNew(silConnect, address, 1, pokeValue,DUT_ElementTypes.typeUnsigned32bit)
                    offset += headerFiledSize32

                elif commandOption in [0, 5]:
                    #print(0)
                    #print(address)
                    # If data load
                    offset += 2 * headerFiledSize16
                    f.seek(offset)
                    # Write no more than 4kB to memory in a single transaction (slow targets
                    # might time out).
                    sliceSize = 1024
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
                        hal.writeBlockNew(silConnect, address, len(intList), intList, DUT_ElementTypes.typeUnsigned32bit)
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
                    hal.writeBlockNew(silConnect, address, len(intList), intList, DUT_ElementTypes.typeUnsigned32bit)
                    offset += sectionSize

                elif commandOption in [4, 7]:
                    #print(4)
                    #print(address)
                    # If zero memory
                    offset += 2 * headerFiledSize16
                    f.seek(offset)
                    hal.writeZeroBlock(silConnect, address, sectionSize/4, DUT_ElementTypes.typeUnsigned32bit)

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


def runTarget(silConnect):
    """ run target """
    debugPrint('RUNNING TARGET')
    silConnect.execute_command('wifiutils write_wrd 0x0100 0x1')
