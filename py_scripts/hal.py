"""
HAL for automation
we use 3 ways of implementation now: 1. DA access; 2. wifi utils; 3. devmem
set this param is input or in excel sheet

Read_gram

read(0xb7000000,0) // GRAM
read(0xb0000000,0) // PKTRAM
PERIP ( 0xa4)
sysbus ( 0xa5)

===========================================
Sheliak memory map
===========================================
SysBus : 0x000000 - 0x03ffff (65536 words)
PBus : 0x040000 - 0x07ffff (65536 words)
PKTRAM : 0x0c0000 - 0x0f0fff (50176 words)
GRAM : 0x080000 - 0x092000 (18432 words)
LMAC_ROM : 0x100000 - 0x134000 (53248 words)
LMAC_RET_RAM : 0x140000 - 0x14c000 (12288 words)
LMAC_SCR_RAM : 0x180000 - 0x190000 (16384 words)
UMAC_ROM : 0x200000 - 0x261800 (99840 words)
UMAC_RET_RAM : 0x280000 - 0x2a4000 (36864 words)
UMAC_SCR_RAM : 0x300000 - 0x338000 (57344 words)

"""

import sys
import os
#from CSUtils import DA
from common_utils import *
from file_operations import *
import lmac_wifiutils

def getMemValue(addrInput):
    #print("input address is "+hex(addrInput))
    #print("type of input is"+str(type(addrInput)))
    if not isinstance(addrInput, int):
        if isinstance(addrInput, long):
            addrInput=(int)(addrInput)
        else:
            addrInput=(int)(addrInput, 0)
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
    elif ((addrInput & 0xfff00000) == 0xbfc00000):
        addr = (addrInput & 0x0fffff) | 0x150 #MIPS_MCU_BOOT_EXCP_INSTR_0
    #print("addr on silicon is "+str(hex(addr)))
    return addr

def readBlock(silConnect, addr, size, dataType):
    readList=[]
    siliconAddr= getMemValue(addr)
    #print("the address on silicon is "+str(hex(siliconAddr)))
    if(dataType==DUT_ElementTypes.typeUnsigned32bit):
        value = silConnect.read_blk(siliconAddr,size)
    elif(dataType==DUT_ElementTypes.typeUnsigned8bit):
        tempAddr  = (siliconAddr>>2)<<2
        offset    = siliconAddr % 4
        tempValue = silConnect.read_blk(tempAddr,size)[0]
        value     = [(tempValue >> ((offset)*8)) & 0xff]
    elif(dataType==DUT_ElementTypes.typeUnsigned16bit):
        tempAddr  = (siliconAddr>>2)<<2
        offset    = siliconAddr % 4
        tempValue = silConnect.read_blk(tempAddr,size)[0]
        value     = [(tempValue >> ((offset)*8)) & 0xffff]
    return value

def empty_readblk(addr, size, dataType, elementNum):
    siliconAddr= getMemValue(addr)
    from automation import silConnect
    readbyte=silConnect.empty_read_wrd(siliconAddr)

def writeBlock(addr, size, data, dataType):
    from automation import targetdict
    #print("writing to "+str(targetdict['TargetName']))
    siliconAddr= getMemValue(addr)
    writeData=0; i=0 #inilization
    from automation import silConnect
    if (size==1):
        silConnect.write_wrd(siliconAddr, data)
    elif(size>1):
        tempSize=size
        for x in data:
            if (dataType==lmac_def.DataType.TYPE_32BIT):
                silConnect.write_wrd(siliconAddr, x)
                siliconAddr+=4
            if(dataType==lmac_def.DataType.TYPE_8BIT):
                if(i<3):
                    writeData+=x<<(i*8); i+=1 #increment i by 1
                    print("in if loop write data is"+str(hex(writeData)))
                    if tempSize!= i:
                        continue
                elif (tempSize > i):
                    writeData+=x<<(i*8) #here i=3
                print("wirte data is "+str(hex(writeData)))
                silConnect.write_wrd(siliconAddr, writeData)
                siliconAddr+=4; tempSize-=4; #decrease tempSize by 4 bytes, used in the loop
                writeData=0; i=0 #final reset for next word
                #print("after the write" +str(writeData))

def writeBlockNew(silConnect, addr, size, data, dataType):
    siliconAddr= getMemValue(addr)
    if (size == 1):
        if (dataType==DUT_ElementTypes.typeUnsigned32bit):
            silConnect.write_wrd(siliconAddr, data)
        elif (dataType==DUT_ElementTypes.typeUnsigned8bit):
            readValue = readBlock(silConnect, addr, size, dataType)[0]
            tempAddr  = (siliconAddr>>2)<<2
            offset    = siliconAddr % 4
            if (offset == 0):
                writeValue = (readValue & 0xffffff00)| data
            elif (offset == 1):
                writeValue = (readValue & 0xffff00ff)| (data << 8)
            elif (offset == 2):
                writeValue = (readValue & 0xff00ffff)| (data <<16)
            elif (offset == 3):
                writeValue = (readValue & 0x00ffffff)| (data <<24)
            silConnect.write_wrd(tempAddr, writeValue)
    elif(size>1):
        writeData=data[0]
        if (dataType==DUT_ElementTypes.typeUnsigned32bit):
            clumpSize = 1
            for x in range(size-1):
                if (data[x+1] == writeData):
                    clumpSize += 1
                else:
                    silConnect.write_blk(siliconAddr, writeData, 0, clumpSize)
                    siliconAddr += clumpSize * 4
                    writeData = data[x+1]
                    clumpSize = 1
            silConnect.write_blk(siliconAddr, writeData, 0, clumpSize)

def writeZeroBlock(silConnect, addr, sectionSize, dataType):
    siliconAddr= getMemValue(addr)
    writeData=0; i=0 #inilization
    #from automation_phy import silConnect
    if (sectionSize==1):
        silConnect.write_wrd(siliconAddr, 0)
    elif(sectionSize>1):
        offset = 0
        # Write no more than 1kB to memory in a single transaction (slow targets
        # might time out).
        sliceSize = 256
        if (dataType==DUT_ElementTypes.typeUnsigned32bit):
            while (sectionSize > sliceSize):
                silConnect.write_blk(siliconAddr + offset, 0x00, 0, sliceSize)
                offset += sliceSize * 4 # byte address
                sectionSize -= sliceSize
            silConnect.write_blk(siliconAddr + offset, 0x00, 0, sectionSize)