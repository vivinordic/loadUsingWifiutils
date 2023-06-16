'''Module for Pre loading MCP image before loading the application. '''
import os
import sys
import time
import array
import struct
import inspect
from imgtec import codescape
from uccpregs import *

class ZeroMemPreLoader(object):
    '''Pre loader module for zero-ing out memories.
       We load some MIPS instructions to zero BIMG records that
       are immediately placed after themselves.'''
    def __init__(self, zeroMemRecords, uccpString):
        self.zeroMemRecords = zeroMemRecords
        self.startAddr = 0x80000000 # Where we put the MIPS instructions.

    def ZeroMemory(self, startAddr, thread):
        '''Zero memories from zero records and return the size of memory needed
           to perform the instructions.'''
        self.startAddr = startAddr
        thread.Stop()
        memory = thread.GetMemory()
        # The instruction that takes the length of the loop
        dir_path = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))
        if os.environ.get('UCC_INST_ROOT') is not None:
            zeroLibPath = os.path.join(os.environ.get('UCC_INST_ROOT'), 'lib')
            if os.path.exists(os.path.join(zeroLibPath, "zero_memory_text")):
                dir_path = zeroLibPath
        f = open(os.path.join(dir_path, "zero_memory_text"), 'rb')
        sectData = f.read()
        f.close()
        mipsInstructions = []
        sectLength = len(sectData) / 4
        for x in xrange(sectLength):
            mipsInstructions.append(struct.unpack(">L", sectData[x*4 : x*4+4])[0])

        self.PokeInstructionSize(mipsInstructions)
        self.AddZeroRecordsInfo(mipsInstructions)
        padNum = 0x100 - len(mipsInstructions)
        mipsInstructions.extend([0] * padNum)
        memory.Write(ABS_SYS_SLEEP_CTRL_DATA_0, 0)
        memory.Write(self.startAddr, mipsInstructions)
        thread.WriteRegister('pc', self.startAddr)
        # The assembly code needs to know the PC value.
        thread.WriteRegister('ra', self.startAddr)

        thread.Run()
        while memory.Read(ABS_SYS_SLEEP_CTRL_DATA_0) != 0xfffff:
            thread.Run()
            time.sleep(0.5)
            continue
        thread.Stop()
        self.ZeroInstructionMemory(mipsInstructions, memory)

    def ZeroInstructionMemory(self, mipsInstructions, memory):
        '''If the memory where we put instructions to zero memories are memories that need
           zeroing, make sure they are zeroed.'''
        insMemEndAddr = self.startAddr + 4 * len(mipsInstructions)
        for record in self.zeroMemRecords:
            recordEndAddr = record.destination + record.size
            if record.destination >= self.startAddr and recordEndAddr <= insMemEndAddr:
                memory.Write(record.destination, [0x00] * record.size, element_type=1)

    def AddZeroRecordsInfo(self, mipsInstructions):
        '''Append the addresses and sizes of zero records to the end of the instructions.'''
        for record in self.zeroMemRecords:
            mipsInstructions.append(record.destination)
            mipsInstructions.append(record.size / 4)

    def PokeInstructionSize(self, mipsInstructions):
        '''The instructions need to know the size of itself.'''
        # The 4th and 5th instructions need the offset of the end of the
        # instructions, where BIMG records are appended.
        mipsInstructions[3] += len(mipsInstructions) * 4
        mipsInstructions[4] += len(mipsInstructions) * 4 + 4

class MCPPreLoader(object):
    '''Pre loader module for loading MCP images.'''
    def __init__(self, mcpRecords, uccpString):
        self.mcpRecords = mcpRecords
        self.mcpIndexToInfo = {}
        self.startAddr = 0x80000000

    def LoadAllRecords(self, startAddr, thread):
        '''Load all MCP records.'''
        thread.Stop()
        self.startAddr = startAddr
        def getMCPIndex(mcpBitMask):
            '''Get the MCP index from its bit mask.'''
            i = 0
            for x in xrange(6):
                if ((mcpBitMask >> x) & 1) == 1:
                    return i
                else:
                    i += 1

            print "Wrong bit mask from corrupted BIMG ", hex(mcpBitMask)
            time.sleep(5)
            sys.exit()

        allWords = []
        lastAddress = startAddr + 0x400
        for record in self.mcpRecords:
            mcpIndex = getMCPIndex(record.mcpBitMask)
            mcpWords = self.ConvertToWordList(record.payload)
            mcpWords = self.PadMCPWords(mcpWords)
            allWords.extend(mcpWords)
            size = len(mcpWords) # Size in words
            address = lastAddress
            self.mcpIndexToInfo[mcpIndex] = (address, size)
            lastAddress += size * 4

        self.LoadMCPCodeMCU(allWords, thread)

    def ConvertToWordList(self, payload):
        '''Convert byte array to a list of 32-bit words.'''
        wordList = []
        length = len(payload)
        if length % 4 != 0:
            print "Error: corrupted BIMG file."
            time.sleep(5)
            sys.exit()
        payLoadArray = array.array('I', payload)
        return payLoadArray.tolist()

    def FillPlaceHolders(self, mipsInstructions):
        '''Fill the place holders with required information. Please refer
           to mcp_load.S for the information to be filled. '''
        mipsInstructions[0] = ABS_SYS_MCP_CSTRCTRL
        mipsInstructions[1] = ABS_SYS_MCP_CSTRDAT32
        mipsInstructions[2] = ABS_SYS_MCP2_CSTRCTRL
        mipsInstructions[3] = ABS_SYS_MCP2_CSTRDAT32
        mipsInstructions[4] = ABS_SYS_MCP3_CSTRCTRL
        mipsInstructions[5] = ABS_SYS_MCP3_CSTRDAT32

        for mcp, info in self.mcpIndexToInfo.items():
            if mcp not in [0, 1, 2]:
                print "Error: MCP index ", mcp, "not supported"
                time.sleep(5)
                sys.exit()

            mipsInstructions[6 + mcp*2] = info[0]
            mipsInstructions[7 + mcp*2] = info[0] + info[1] * 4

        for i, ins in enumerate(mipsInstructions):
            if hex(ins).replace('L', '').endswith("dead"):
                mipsInstructions[i] = (ins & 0xffff0000) | (self.startAddr & 0xffff)

    def PadMCPWords(self, mcpWords):
        '''Pad MCP words to be multiple of 12.'''
        if len(mcpWords) % 12 != 0:
            padNum = 12 - (len(mcpWords) % 12)
            mcpWords.extend([0] * padNum)
        return mcpWords

    def LoadMCPCodeMCU(self, mcpImage, thread):
        '''Load MCP code in MCU'''
        memory = thread.GetMemory()
        # The instruction that takes the length of the loop
        dir_path = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))
        if os.environ.get('UCC_INST_ROOT'):
            mcpLoaderLibPath = os.path.join(os.environ.get('UCC_INST_ROOT'), 'lib')
            if os.path.exists(os.path.join(mcpLoaderLibPath, "mcp_loader_text")):
                dir_path = mcpLoaderLibPath
        f = open(os.path.join(dir_path, "mcp_loader_text"), 'rb')
        sectData = f.read()
        f.close()
        mipsInstructions = []
        sectLength = len(sectData) / 4
        for x in xrange(sectLength):
            mipsInstructions.append(struct.unpack(">L", sectData[x*4 : x*4+4])[0])

        self.FillPlaceHolders(mipsInstructions)
        padNum = 0x100 - len(mipsInstructions)
        mipsInstructions.extend([0] * padNum)

        dataToLoad = mipsInstructions + mcpImage
        memory.Write(ABS_SYS_SLEEP_CTRL_DATA_0, 0)
        memory.Write(self.startAddr, dataToLoad)
        thread.WriteRegister('pc', 0x80000030)
        thread.Run()

        while memory.Read(ABS_SYS_SLEEP_CTRL_DATA_0) != 0xfffff:
            thread.Run()
            time.sleep(0.5)
            continue
