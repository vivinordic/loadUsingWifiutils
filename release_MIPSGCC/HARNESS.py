'''Codescape load script'''
import array
import os
import time
import struct
import sys
import time
import inspect
from imgtec import codescape
from imgtec.codescape.da_types import LoadType

sys.path.append(os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe()))))
from dependencies.mcppreloader import MCPPreLoader, ZeroMemPreLoader
from dependencies.bimgdump import parseBimgFiles
from dependencies.uccpregs import *

# GetCommsOptions appears in Codescape 8.5 and later
try:
    from imgtec.codescape import GetCommsOptions
except ImportError:
    def GetCommsOptions(identifier):
        from imgtec.codescape import GetDAScript
        da = GetDAScript(None)
        return da.GetCommsOptions(identifier)

MCP_LOAD_TYPE_TAP = 0
MCP_LOAD_TYPE_CODESTORE = 1
MCP_LOAD_TYPE_DCL = 2
MCP_LOAD_TYPE_BUNDLED = 3
MCP_LOAD_TYPE_PRELOAD = 4

LOAD_INFO = {
    # A list of elfs to load
    "elfs": {
        1 : "HARNESS.elf"
    },
    "shared": {

    },

    "bimgs": {
        1 : ['HARNESS.bimg']
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
    "loadSliceSize"  : 4096
}

ERRORS = []

def HardResetSoc(probe):
    '''Hard reset selected soc'''
    print "Hard resetting"
    for cs in probe.cores:
        try:
            if str(cs).strip().startswith("MCU"):
              print "Hard resetting " + str(cs)
              cs.HardReset()
              break
        except Exception as e:
            ERRORS.append("Could not hard reset target " + str(cs.name) + " because " + str(e))

    # Wait for reset to finish.
    time.sleep(1)

def LoadProgramFiles(showProgress=True, load_type=LoadType.all, probe=None):
    '''Load program files'''
    filename = ""
    try:
        # Load shared ELF(s)
        for coreId, filename in LOAD_INFO["shared"].items():
            thread = codescape.FindThread(probe=probe.name, soc=-1, core=coreId)
            print "Loading " + str(filename) + " on " + str(thread.core)
            thread.LoadProgramFile(filename,
                                   hard_reset=False,
                                   load_type=load_type,
                                   progress=showProgress)

        # Load application ELF(s)
        for coreId, filename in LOAD_INFO["elfs"].items():
            thread = codescape.FindThread(probe=probe.name, soc=-1, core=coreId)
            print "Loading " + str(filename) + " on " + str(thread.core)
            thread.LoadProgramFile(filename,
                                   hard_reset=False,
                                   load_type=load_type,
                                   progress=showProgress)

    except Exception as e:
        ERRORS.append("Could not load " + str(filename) + " because " + str(e))
        print "Could not load " + str(filename) + " because " + str(e)
        time.sleep(10)

def LoadMCPDebugInfo(showProgress=True, probe=None):
    '''Load debug info from MCP ELF files'''
    try:
        mcps = codescape.FindThreads(probe=probe.name, soc=-1, core="MCP")

        for coreId, filename in LOAD_INFO["mcpElfs"].items():
            print "Loading " + str(filename) + " on " + str(mcps[coreId].core)
            mcps[coreId].LoadProgramFile(filename,
                                         hard_reset=False,
                                         load_type=LoadType.symbols,
                                         progress=showProgress)

    except Exception as e:
        ERRORS.append("Could not load " + str(filename) + " because " + str(e))
        print "Could not load " + str(filename) + " because " + str(e)
        time.sleep(10)

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

def PreLoadMCP(thread, mcpRecords):
    '''Load MCP image before loading the application.'''
    mcpPreLoader = MCPPreLoader(mcpRecords, "uccp" + "__UCCP__")
    mcpPreLoader.LoadAllRecords(LOAD_INFO["ram0Origin"], thread)

def PreZeroMem(thread, zeroMemRecords):
    '''Zero memories before loading the application.'''
    zeroPreLoader = ZeroMemPreLoader(zeroMemRecords, "uccp" + "__UCCP__")
    zeroPreLoader.ZeroMemory(LOAD_INFO["ram0Origin"], thread)

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
    if probe is not None:
        mcps = [core for core in probe.GetCores() if "MCP" in str(core)]

    for coreId, filenames in (LOAD_INFO["bimgs"].items() +
                             LOAD_INFO["sharedBimg"].items()):
        try:
            for filename in filenames:
                # Load MCP image before loading the application.
                thread = codescape.FindThread(probe=probe.name, soc=-1, core=coreId)
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
                if headerPrefix != b'\xBA\xDA\xBA\xAB':
                    raise Exception("this is not a bimg file")

                print "Loading BIMG " + str(filename) + " on " + str(thread.core)
                startTime = time.time()
                thread.Stop()
                memory = thread.GetMemory()
                offset = headerSizeOffset
                while True:
                    f.seek(offset)
                    sectionSize = BinaryStringToIntLE(f.read(headerFiledSize32))
                    offset += headerFiledSize32
                    address = BinaryStringToIntLE(f.read(addressLength))

                    offset += headerFiledSize32
                    commandOption = BinaryStringToIntLE(f.read(headerFiledSize16), size=2)
                    if commandOption in [1, 6]:
                        # If registers poke
                        pokeValue = sectionSize
                        memory.Write(address, pokeValue)
                        offset += headerFiledSize32

                    elif commandOption in [0, 5]:
                        # If data load
                        offset += 2 * headerFiledSize16
                        f.seek(offset)
                        # Write no more than 4kB to memory in a single transaction (slow targets
                        # might time out).
                        sliceSize = LOAD_INFO["loadSliceSize"]
                        while (sectionSize > sliceSize):
                            memory.Write(address, BinaryStringToIntList(f, offset, sliceSize))
                            address += sliceSize
                            offset += sliceSize
                            sectionSize -= sliceSize
                        memory.Write(address, BinaryStringToIntList(f, offset, sectionSize))
                        offset += sectionSize

                    elif commandOption in [4, 7]:
                        # If zero memory
                        offset += 2 * headerFiledSize16
                        f.seek(offset)
                        if not LOAD_INFO['preZeroMem']:
                          memory.Write(address, GenerateZeroList(sectionSize), 1)

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

                if not filename.endswith("shared.bimg"):
                    thread.WriteRegister("pc", entryAddress)

                print "BIMG load complete in ", round(time.time() - startTime, 2), "seconds"

        except Exception as e:
            ERRORS.append("Could not load " + str(filename) + " because " + str(e))
            print "Could not load " + str(filename) + " because " + str(e)
            time.sleep(10)

def LoadPatchBins(probe):
    '''Load patch binaries into retention RAM.'''
    filename = ""
    try:
        # Load application ELF(s)
        for coreId, patchBin in LOAD_INFO["patchBins"].items():
            loadAddr = patchBin[0]
            filename = patchBin[1]
            thread = codescape.FindThread(probe=probe.name, soc=-1, core=coreId)
            print "Loading patch RAM with " + str(filename) + " at " + hex(loadAddr) + " on " + str(thread.core)
            patchData = open(filename, "rb").read()
            thread.GetMemory().WriteString(loadAddr, patchData)

    except Exception as e:
        ERRORS.append("Could not load " + str(filename) + " because " + str(e))
        print "Could not load " + str(filename) + " because " + str(e)
        time.sleep(10)

def LoadROMImagesOnSim(probe):
    '''Load binary ROM image files on a simulator by updating the sim_setup.txt file'''
    # Find the sim_setup.txt file.
    target_options  = GetCommsOptions(probe.GetName())
    setupFilename = target_options['cwd'] + "/sim_setup.txt"

    # Create the file if it doesn't exist
    if not os.path.exists(setupFilename):
        open(setupFilename, "w").close()

    # Read the file in
    with open(setupFilename) as setupFile:
        lines = setupFile.readlines()

    # Remove any existing rom_images lines
    lines = [l for l in lines if not l.startswith("rom_images")]

    # If we have ROM images, create a line that specifies them, and add it to the file
    numRomImages = len(LOAD_INFO['roms'])
    if numRomImages > 0:
        romImagesLine = "rom_images " + str(numRomImages)
        romImageDir = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))
        for rom in LOAD_INFO['roms'].values():
            romImagesLine += (" " + os.path.realpath(os.path.join(romImageDir, rom)))
        romImagesLine += "\n"
        lines.append(romImagesLine)

    # Write out the updated file
    with open(setupFilename, "w") as setupFile:
        for line in lines:
            setupFile.write(line)

def DCL_GenerateWritesToOneAddress(address, words):
    '''Generate a bunch of word writes to a single address.

    .. note :: Uses a var instead of explicit copy *0x80000, 0x9900000 statements
               because it generates a slightly shorter dcl sequence.
    '''
    lines = ['var address',
             'copy address, 0x{:8x}'.format(address)]
    lines += ['copy *address, 0x{:08x}'.format(word) for word in words]
    return '\n'.join(lines)

def DCL_WriteManyWords(thread, address, words):
    '''Write each word in `words` to `address` (e.g. all writes are written to
    the same location).

    .. note:: This is dependent on internal codescape workings, which are not yet
              public, so this code may need revisiting soon.
    '''
    DCL_NOW = 0xffffffff
    MAXWORDS = 128 # The most we can do on an emulator before the five-second DCL timeout
    if len(words) > MAXWORDS:
        DCL_WriteManyWords(thread, address, words[:MAXWORDS])
        DCL_WriteManyWords(thread, address, words[MAXWORDS:])
        return
    c = thread._Thread__context
    dcl = c.DCLAssembleCommandList(DCL_GenerateWritesToOneAddress(address, words))
    dclid = c.DCLSetupCommandList(dcl)
    try:
        c.DCLAttachCommandList(dclid, DCL_NOW)
    finally:
        c.DCLRemoveCommandList(dclid)

def enableClocks(probe):
    '''Enable clocks before loading data to memories.'''
    try:
        thread = codescape.FindThread(probe=probe.name, soc=-1, core=LOAD_INFO["elfs"].keys()[0])
        memory = thread.GetMemory()
        clock0Value = memory.Read(ABS_PMB_RPU_CLOCK_RESET_CTRL_CLOCK_STATUS_1)
        clock1Value = memory.Read(ABS_PMB_RPU_CLOCK_RESET_CTRL_CLOCK_STATUS_2)
        memory.Write(ABS_PMB_RPU_CLOCK_RESET_CTRL_CLOCK_ENABLE_1, 0x3F10F100)
        memory.Write(ABS_PMB_RPU_CLOCK_RESET_CTRL_CLOCK_ENABLE_2, 0x00000300)
        return clock0Value, clock1Value

    except Exception as e:
        ERRORS.append("Could not load " + str(e))
        print "Could not load because " + str(e)
        time.sleep(10)

def restoreClocks(probe, clock0Value, clock1Value):
    '''Restore clocks after loading data to memories.'''
    try:
        thread = codescape.FindThread(probe=probe.name, soc=-1, core=LOAD_INFO["elfs"].keys()[0])
        memory = thread.GetMemory()
        memory.Write(ABS_PMB_RPU_CLOCK_RESET_CTRL_CLOCK_ENABLE_1, clock0Value)
        memory.Write(ABS_PMB_RPU_CLOCK_RESET_CTRL_CLOCK_ENABLE_2, clock1Value)

    except Exception as e:
        ERRORS.append("Could not load " + str(e))
        print "Could not load because " + str(e)
        time.sleep(10)

def main(hardReset=True, load_type=LoadType.symbols, showProgress=True):
    '''Start function'''
    probe = None
    if codescape.environment == 'standalone':
        from CSUtils import DA
        thread = codescape.GetThreadById(DA.GetCurrentTarget())
        probe = thread.probe
    else:
        probe = codescape.GetSelectedThread().probe

    if probe.GetName().startswith("Simulator"):
        LoadROMImagesOnSim(probe)

    if hardReset is True:
        HardResetSoc(probe)

    originalClocksValue = enableClocks(probe)

    if load_type == LoadType.all or load_type == LoadType.binary:
        LoadBimgFiles(probe)
        LoadPatchBins(probe)
    if load_type == LoadType.all or load_type == LoadType.symbols:
        LoadProgramFiles(showProgress, LoadType.symbols, probe)
        LoadMCPDebugInfo(showProgress, probe)

    if originalClocksValue is not None:
        restoreClocks(probe, *originalClocksValue)

if __name__ == "__main__":
    if codescape.environment == 'codescape':
        print "User script is not allowed"
        time.sleep(3)
        sys.exit()
    main()
