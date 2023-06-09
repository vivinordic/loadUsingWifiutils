#!/usr/bin/env python2
'''Bimg file dump tool'''
import struct
import sys
import glob
import os
uccToolkitEnv = os.environ.get('UCC_INST_ROOT')
if uccToolkitEnv is not None:
    if os.path.exists(uccToolkitEnv):
        sys.path.append(os.path.join(uccToolkitEnv, 'bin'))
        from elftools.elf.elffile import ELFFile
        from elftools.elf.constants import SH_FLAGS
    else:
        print "UCC_INST_ROOT {0:s} does not exist".format(uccToolkitEnv)
        sys.exit()

class Record(object):
    '''Record class contains the content of a BIMG record.'''
    def __init__(self, command, destination, size, payload):
        self.command = command
        self.destination = destination
        self.size = size
        self.payload = payload

class MCPRecord(Record):
    '''MCPRecord class contains the content of a BIMG MCP direct load record.'''
    def __init__(self, command, destination, size, payload, mcpBitMask):
        super(MCPRecord, self).__init__(command, destination, size, payload)
        self.mcpBitMask = mcpBitMask


RECORDS = []
USAGE = {"Core": 0, "GRAM" : 0, "ExtRAM" : 0}
RANGES = {"Core": (None, None), "GRAM" : (None, None), "ExtRAM" : (None, None)}

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

def parseBimgFiles(filename, ifPrint=True, mcpRecords=None, zeroMemRecords=None):
    '''Parse Bimg files'''
    # pylint: disable=too-many-statements
    # pylint: disable=too-many-locals
    localMcpRecords = []
    localZeroRecords = []
    try:
        output = []
        f = open(filename, 'rb')
        offset = 0
        f.seek(offset)
        headerPrefix = f.read(4)
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
                                      f.read(int(binaryStringToHexString(sectionSizeStr), 16))))
                updateUsage(address, sectionSize)
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

            elif commandNum == 3:
                # End of Load
                break
        f.close()

        if ifPrint:
            for line in output:
                print "{0:<19} {1:<16} {2:<10} {3:<13} {4:<10}".format(*line)


    except Exception as e:
        print "Could not parse " + str(filename) + " because " + str(e)
        sys.exit()

    if mcpRecords is not None:
        mcpRecords.extend(localMcpRecords)

    if zeroMemRecords is not None:
        zeroMemRecords.extend(localZeroRecords)

def clearUsageAndRanges():
    '''Clear usages and ranges.'''
    # Notice that we can only do this by referening those variables. We cannot
    # use assignment as that would create local variables rather than changing the
    # global variable values.
    # Defining USAGE = {"Core": 0, "GRAM" : 0, "ExtRAM" : 0} here would create a local
    # variable USAGE and that has nothing to do with the global variable USAGE.
    # If using the assignment operator, make sure to specify the global attribute.
    # e.g. global USAGE. Then USAGE = {"Core": 0, "GRAM" : 0, "ExtRAM" : 0} would work.
    USAGE["Core"] = 0
    USAGE["GRAM"] = 0
    USAGE["ExtRAM"] = 0
    RANGES["Core"] = (None, None)
    RANGES["GRAM"] = (None, None)
    RANGES["ExtRAM"] = (None, None)

def printMemUsage():
    '''Output memory usage statistics'''
    print   # Empty line
    print "Region     Start offset (bytes)    End offset (bytes)    Memory used (bytes)"
    print "----------------------------------------------------------------------------"
    for region in USAGE:
        if RANGES[region][0] is not None:
            startOffset = RANGES[region][0]
        else:
            startOffset = 0
        if RANGES[region][1] is not None:
            endOffset = RANGES[region][1]
        else:
            endOffset = 0
        print ("{name:<10s} 0x{startOffset:08x}              0x{endOffset:08x}            " +
               "0x{usage:08x} ({usageKb:d} kB)").format(name=region,
                                                        usage=USAGE[region],
                                                        usageKb=USAGE[region]/1024,
                                                        startOffset=startOffset,
                                                        endOffset=endOffset)

def metaExecToData(address):
    '''Convert a meta execution view address to load view address'''
    offset = 0
    if (address & 0xFFF00000) == 0x80900000:
        offset = (address - 0x80900000) / 2 + 0x82000000
    elif (address & 0xFFF00000) == 0x80B00000:
        offset = (address - 0x80B00000) / 2 + 0x82080000
    elif (address & 0xFFF00000) == 0x80D00000:
        offset = (address - 0x80D00000) / 2 + 0x82100000
    else:
        pass # Already a loadable address

    return offset

def mergeRecords(records, sectAddrToSize):
    '''Merge records that belong to the same section.'''
    # the records which do not belong to an ELF section and
    # are immediately following this ELF section record (record
    # that has same address as an ELF section).

    # A map of record that has the same address as an ELF section
    # to the records that are following this section record in address.
    sectRecordToFollowingRecords = {}
    currentRecord = None
    for record in records:
        if record.destination in sectAddrToSize:
            currentRecord = record
        else:
            if currentRecord is not None:
                if currentRecord not in sectRecordToFollowingRecords:
                    sectRecordToFollowingRecords[currentRecord] = [record]
                else:
                    sectRecordToFollowingRecords[currentRecord].append(record)

    # Iterate through following records, coalesce them with section records if
    # the accumulated size is smaller than the Elf section size (when this section
    # has been split into different LDR/BIMG records).
    # Then remove the records that have been coalesced into the section records.
    for sectRecord in sectRecordToFollowingRecords:
        for followingRecord in sectRecordToFollowingRecords.get(sectRecord):
            sectSize = sectAddrToSize.get(sectRecord.destination)
            # Padding section size to be 4-words aligned because that's what Meta does.
            sectSize += (16 - (sectSize % 16))
            if followingRecord.size + sectRecord.size <= sectSize:
                sectRecord.size += followingRecord.size
                sectRecord.payload += followingRecord.payload
                records.remove(followingRecord)

def generatePatchBinary(outputDir, binfile, funcNames, fileSize, patchRamBase):
    '''Generate patch binary from patch BIMG file.'''
    def removeSuffix(name):
        '''global section and library section have _glb0 and _lib0 suffix, we need to remove them.'''
        if name.endswith("_gbl0") or name.endswith("_lib0"):
            return name[:-5]
        else:
            return name

    codeSize = 0 # The actuall code size without padding 0s to the end.
    dataPatchRamBase = 0x82000000 + int(str(patchRamBase), 16)
    sects = []
    sectAddrToSize = {}
    secNames = [".text", ".data", ".patchdata"]
    for func in funcNames:
        secNames.append("." + func)
    elfFiles = glob.glob(os.path.join(outputDir, "*.elf"))
    elfFiles = [elf for elf in elfFiles if elf.endswith("_t0.elf") or elf.endswith("_t1.elf")]
    for elffile in elfFiles:
        with open(elffile, 'r') as f:
            ef = ELFFile(f)
            sections = list(ef.iter_sections())
            for section in sections:
                if section['sh_flags'] & SH_FLAGS.SHF_ALLOC:
                    # We include the sections that are only code and data that originate from
                    # patch C source files. The patch binary file should include all sections
                    # whose names end with "_text". Because Meta compilers sometimes generate
                    # sections with this name when global elf or shared libraries are used.
                    if removeSuffix(section.name) in secNames or section.name.endswith("_text"):
                        if section['sh_flags'] & SH_FLAGS.SHF_EXECINSTR:
                            sectAddr = metaExecToData(section['sh_addr'])
                            sects.append(sectAddr)
                            sectAddrToSize[sectAddr] = section['sh_size'] / 2
                        else:
                            sectAddr = (section['sh_addr'] & 0xfffff) + 0x82000000
                            sects.append(sectAddr)
                            sectAddrToSize[sectAddr] = section['sh_size']

    sects = list(set([sec for sec in sects if sec >= dataPatchRamBase]))
    sects.sort()
    bimgData = {}
    f = open(binfile, 'wb')

    # Combine separated contiguous records.
    sortedRecords = sorted(RECORDS, key=lambda r: r.destination)

    mergeRecords(sortedRecords, sectAddrToSize)

    for record in sortedRecords:
        bimgData[record.destination] = record.payload

    # Write and pad sections.
    for i in xrange(len(sects) - 1):
        if sects[i] in bimgData.keys():
            f.write(bimgData[sects[i]])
            if sects[i + 1] - sects[i] != len(bimgData[sects[i]]):
                f.write('\x00' * (sects[i + 1] - sects[i] - len(bimgData[sects[i]])))

    # Write the last section.
    if sects[-1] in bimgData.keys():
        f.write(bimgData[sects[-1]])
    codeSize = f.tell()
    f.write('\x00' * (fileSize - f.tell()))

    f.close()

    return codeSize

def main():
    '''Entry point.'''
    if len(sys.argv) <= 1:
        print "Please input the filenames"
        print "e.g. bimgdump.py filename1 filename2"

    for arg in sys.argv[1:]:
        parseBimgFiles(arg)
        printMemUsage()
        clearUsageAndRanges()

if __name__ == '__main__':
    main()
