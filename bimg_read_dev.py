#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     28-11-2022
# Copyright:   (c) vivi 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

'''Bimg file dump tool'''
import struct

ifPrint = 1

RECORDS = []
USAGE = {"Core": 0, "GRAM" : 0, "ExtRAM" : 0}
RANGES = {"Core": (None, None), "GRAM" : (None, None), "ExtRAM" : (None, None)}

class Record(object):
    '''Record class contains the content of a BIMG record.'''
    def __init__(self, command, destination, size, payload):
        self.command = command
        self.destination = destination
        self.size = size
        self.payload = payload

def binaryStringToHexString(binString, size=4):
    '''Convert binary string to hexadecimal string'''
    if len(binString) != size:
        raise Exception("Hex String length must match size")
    if size == 4:
        hexString = "0x%04x%04x" % struct.unpack("<HH", binString[2] + binString[3] +
                                                 binString[0] + binString[1])
    elif size == 2:
        hexString = "0x%04x" % struct.unpack("<H", binString[0] + binString[1])
    return hexString

def binaryStringToInt(binString, size=4):
    '''Convert binary string to integer'''
    if len(binString) != size:
        raise Exception("Integer String length must match size")
    if size == 4:
        hexString = "0X%04X%04X" % struct.unpack("<HH", binString[2] + binString[3] +
                                                 binString[0] + binString[1])
    elif size == 2:
        hexString = "0X%04X" % struct.unpack("<H", binString[0] + binString[1])
    return int(hexString, 0)

def payloadBinaryToInt(binString, size=4):
    payload = []
    for i in range(len(binString)/size):
        payload.append(binaryStringToInt(binString[i*size:(i+1)*size],size))

    return payload

def getMemValue(addrInput):

    #print("input address is "+str(addrInput))

    #print("type of input is"+str(type(addrInput)))

    if not isinstance(addrInput, int):

        if isinstance(addrInput, long):

            addrInput=(int)(addrInput)

        else:

            addrInput=(int)(addrInput, 0)

    if (addrInput == 0xbfc00000):
        addrInput = 0xa4000150

    if ((addrInput & 0xff000000) == 0xb0000000):

        addr = (addrInput & 0xffffff) | 0x0c0000 #PKTRAM

    elif ((addrInput & 0xff000000) == 0xb7000000):

        addr = (addrInput & 0xffffff) | 0x080000 #GRAM

    elif ((addrInput & 0xff000000) == 0xb4000000):

        addr = (addrInput & 0xffffff) | 0x080000 #GRAM

    elif ((addrInput & 0xff000000) == 0xa4000000):

        addr = (addrInput & 0xffffff) | 0x000000 #SYS bus

    elif ((addrInput & 0xff000000) == 0xa5000000):

        addr = (addrInput & 0xffffff) | 0x040000 #PERIP bus

    elif ((addrInput & 0xfff00000) == 0x80100000):

        addr = (addrInput & 0x0fffff) | 0x300000 #UMAC scratch Mem

    #print("addr on silicon is "+str(hex(addr)))

    return addr

def main():
    # open .bimg
    filename = "release_MIPSGCC/HARNESS.bimg"
    output = []
    f = open(filename, 'rb')

    localMcpRecords = []
    localZeroRecords = []

    # read header
    offset = 0
    f.seek(offset)
    headerPrefix = f.read(4)
    if ifPrint:
        print (headerPrefix)

    if headerPrefix != b"\xBA\xDA\xBA\xAB":
        raise Exception("this is not a bimg file")
    output.append(("Header Prefix: ", str(binaryStringToHexString(headerPrefix))))
    offset += 4
    f.seek(offset)
    versionMinor = f.read(2)
    output.append(("Version Minor: ", str(binaryStringToHexString(versionMinor, 2))))
    offset += 2
    versionMajor = f.read(2)
    output.append(("Version Major: ", str(binaryStringToHexString(versionMajor, 2))))
    offset += 2
    dataSize = f.read(4)
    output.append(("Data Size: ", str(binaryStringToHexString(dataSize))))
    offset += 4
    entryAddress = f.read(4)
    output.append(("Execution Address: ", str(binaryStringToHexString(entryAddress))))
    offset += 4
    optionFlags = f.read(4)
    output.append(("Options/flags: ", str(binaryStringToHexString(optionFlags))))
    offset += 4
    dataCrc = f.read(4)
    output.append(("Data CRC: ", str(binaryStringToHexString(dataCrc))))
    offset += 4
    headerCrc = f.read(4)
    output.append(("Header CRC: ", str(binaryStringToHexString(headerCrc)) + '\n'))
    offset = 28

    if ifPrint:
        for line in output:
            print "{0:<19s} {1:<16s}".format(*line)

    output = []

    def updateUsage(address, size):
        '''Update our tracking of the use of each memory region.'''
        addressPrefix = binaryStringToInt(address) >> 24
        addressOffsetBytes = binaryStringToInt(address) & 0x00ffffff
        endOffsetBytes = addressOffsetBytes + size
        rangeKey = None

        if addressPrefix == 0x80:
            # Core memory
            rangeKey = "Core"
            USAGE[rangeKey] += size
        elif addressPrefix in [0xb4, 0xb5, 0xb6]:
            # Expanded GRAM
            rangeKey = "GRAM"
            USAGE[rangeKey] += (size*3)/4
            addressOffsetBytes *= (3/4)
            endOffsetBytes *= (3/4)
        elif addressPrefix in [0xb7, 0x97]:
            # Packed GRAM
            rangeKey = "GRAM"
            USAGE[rangeKey] += size
        elif addressPrefix in [0xb0, 0x90]:
            # External RAM
            rangeKey = "ExtRAM"
            USAGE[rangeKey] += size

        # Track the start and end offsets of used memory so we can report usage including
        # (e.g.) alignment gaps.
        if rangeKey != None:
            if RANGES[rangeKey][0] is None or RANGES[rangeKey][0] > addressOffsetBytes:
                RANGES[rangeKey] = (addressOffsetBytes, RANGES[rangeKey][1])

            if RANGES[rangeKey][1] is None or RANGES[rangeKey][1] < endOffsetBytes:
                RANGES[rangeKey] = (RANGES[rangeKey][0], endOffsetBytes)

    while True:
        f.seek(offset)
        sectionSizeStr = f.read(4)
        sectionSize = binaryStringToInt(sectionSizeStr)
        offset += 4
        address = f.read(4)

        offset += 4

        commandNum = binaryStringToInt(f.read(2), size=2)
        if commandNum == 1:
            # If registers poke
            output.append(("Register Poke:", "pokeAddress:", str(binaryStringToHexString(address)),
                           "pokeValue:", str(binaryStringToHexString(sectionSizeStr))))
            offset += 4
            RECORDS.append(Record(commandNum, int(binaryStringToHexString(address), 16),
                                  int(binaryStringToHexString(sectionSizeStr), 16), None))
        elif commandNum == 0:
            # If data load
            output.append(("Data Load:", "Section Address:", str(binaryStringToHexString(address)),
                           "Section Size:", str(binaryStringToHexString(sectionSizeStr))))
            offset += 2 * 2
            f.seek(offset)
            if (sectionSize % 4) == 0:
                offset += sectionSize
            else:
                offset += sectionSize +  (4 - sectionSize % 4)
            RECORDS.append(Record(commandNum, int(binaryStringToHexString(address), 16),
                                  int(binaryStringToHexString(sectionSizeStr), 16),
                                  payloadBinaryToInt(f.read(int(binaryStringToHexString(sectionSizeStr), 16)))))
            updateUsage(address, sectionSize)
            #print "{0:<19} {1:<16} {2:<10} {3:<13} {4:<10}".format(*output[-1])
            #print RANGES
        elif commandNum == 2:
            # If MCP code load
            # This section size comes in first 24bits of the command argument. Last 4 bits are reserved for the MCP id.
            mcpBitMask = (sectionSize >> 24) & 0xff
            sectionSize = sectionSize & 0x00ffffff
            output.append(("MCP Code Load:", "Section Address:", str(binaryStringToHexString(address)),
                           "Section Size:", '0x' + str(format((sectionSize), 'x')).zfill(8)))
            offset += 2 * 2
            f.seek(offset)
            localMcpRecords.append(MCPRecord(commandNum, int(binaryStringToHexString(address), 16),
                                        sectionSize, f.read(sectionSize), mcpBitMask))
            if (sectionSize % 4) == 0:
                offset += sectionSize
            else:
                offset += sectionSize +  (4 - sectionSize % 4)

            updateUsage(address, sectionSize)
            #print "{0:<19} {1:<16} {2:<10} {3:<13} {4:<10}".format(*output[-1])
            #print RANGES
        elif commandNum == 4:
            # If zero memory
            offset += 2 * 2
            f.seek(offset)
            output.append(("Zero Command:", "Section Address:", str(binaryStringToHexString(address)),
                           "Section Size:", str(binaryStringToHexString(sectionSizeStr))))
            updateUsage(address, sectionSize)
            zeroRecord = Record(commandNum, int(binaryStringToHexString(address), 16),
                                  int(binaryStringToHexString(sectionSizeStr), 16),
                                  '\x00' * int(binaryStringToHexString(sectionSizeStr), 16))
            RECORDS.append(zeroRecord)
            localZeroRecords.append(zeroRecord)

        elif commandNum == 5:
            # If retained data load
            output.append(("Retained Data Load:", "Section Address:", str(binaryStringToHexString(address)),
                           "Section Size:", str(binaryStringToHexString(sectionSizeStr))))
            offset += 2 * 2
            f.seek(offset)
            if 0 == (sectionSize % 4):
                offset += sectionSize
            else:
                offset += sectionSize +  (4 - sectionSize % 4)
            updateUsage(address, sectionSize)
            #print "{0:<19} {1:<16} {2:<10} {3:<13} {4:<10}".format(*output[-1])
            #print RANGES
        if commandNum == 6:
            # If cold boot poke
            output.append(("Cold Boot Poke:", "pokeAddress:", str(binaryStringToHexString(address)),
                           "pokeValue:", str(binaryStringToHexString(sectionSizeStr))))
            offset += 4
        elif commandNum == 7:
            # if retained zero memory
            offset += 2 * 2
            f.seek(offset)
            zeroRecord = Record(commandNum, int(binaryStringToHexString(address), 16),
                                  int(binaryStringToHexString(sectionSizeStr), 16),
                                  '\x00' * int(binaryStringToHexString(sectionSizeStr), 16))
            localZeroRecords.append(zeroRecord)
            output.append(("Retained Zero Command:", "Section Address:", str(binaryStringToHexString(address)),
                           "Section Size:", str(binaryStringToHexString(sectionSizeStr))))
            updateUsage(address, sectionSize)
            #print "{0:<19} {1:<16} {2:<10} {3:<13} {4:<10}".format(*output[-1])
            #print RANGES

        elif commandNum == 3:
            # End of Load
            break

    # .bimg close
    f.close()

    # print mem regions and size
    ii = 0
    if ifPrint:
        for line in output:
            fo.write("###########################################################\n")
            print "{0:<19} {1:<16} {2:<10} {3:<13} {4:<10}".format(*line)
            fo.write("{0:<19} {1:<16} {2:<10} {3:<13} {4:<10}\n".format(*line))
            fo.write("###########################################################\n")
##            print RECORDS[ii].command
            print hex(RECORDS[ii].destination)
            fo.write(hex(RECORDS[ii].destination)+'\n')
            print hex(getMemValue(RECORDS[ii].destination))
            fo.write(hex(getMemValue(RECORDS[ii].destination))+'\n')
            fo.write(hex(RECORDS[ii].size)+'\n')
            fo.write("***********\n")
            if RECORDS[ii].payload:
                if (RECORDS[ii].payload[0] != '\x00'):
                    print hex(RECORDS[ii].payload[0])
                    for jj in range(len(RECORDS[ii].payload)):
                        fo.write('%08X\n' %RECORDS[ii].payload[jj])

##            print RECORDS[ii].size
            ii += 1
    fo.close()
    pass

if __name__ == '__main__':

    outFile =  "txscp_output_real.txt"
    fo = open(outFile, "w")

##    for index in range(0,samples2Read):
##        samplesOutReal = (outBuffer[index]>>20)
##        samplesOutImag = ((outBuffer[index]>>4) & 0xfff)
##        foReal.write('%03X\n' %samplesOutReal)
##        foImag.write('%03X\n' %samplesOutImag)
    main()
