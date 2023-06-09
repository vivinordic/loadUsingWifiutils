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
from CSUtils import DA
from common_utils import *
from file_operations import *
import lmac_def
import lmac_wifiutils

def getMemValue(addrInput):
    #print("input address is "+str(addrInput))
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
    elif ((addrInput & 0xff000000) == 0xa4000000):
        addr = (addrInput & 0xffffff) | 0x000000 #SYS bus
    elif ((addrInput & 0xff000000) == 0xa5000000):
        addr = (addrInput & 0xffffff) | 0x040000 #PERIP bus
    #print("addr on silicon is "+str(hex(addr)))
    return addr

def readBlock(addr, size, dataType, elementNum):
    from automation import targetdict
    #print(targetdict['TargetName'])
    readList=[]
    if (targetdict['TargetName']=='FPGA'):
        if(dataType==lmac_def.DataType.TYPE_32BIT):
            if (isinstance(elementNum, int)):
                readbyte=DA.ReadMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[elementNum]
                return readbyte
            else:
                readList=DA.ReadMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
                #print(readList)
                return readList
    elif(targetdict['TargetName']=='SILICON'):
        #lmacRead=lmac_wifiutils.WiFiUtilsClient()
        if (targetdict['SiliconAccessType']=='DAUtils'):
            if (isinstance(elementNum, int)):
                readbyte=DA.ReadMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[elementNum]
                return readbyte
            else:
                readList=DA.ReadMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
                print(readList)
                return readList
        elif(targetdict['SiliconAccessType']=='WifiUtils'):
            siliconAddr= getMemValue(addr)
            print("the address on silicon is "+str(hex(siliconAddr)))
            from automation import silConnect
            if(dataType==lmac_def.DataType.TYPE_32BIT):
                if (isinstance(elementNum, int)):
                    #print("extracting single byte" )
                    elementNum*=4
                    siliconAddr+=elementNum
                    #print(hex(siliconAddr)+" is type " + str(type(siliconAddr)))
                    readbyte=silConnect.read_wrd(siliconAddr)
                    #print("read byte is "+str(readbyte))
                    return readbyte
                else:
                    for i in range(0,55):
                        readList.append(silConnect.read_wrd(siliconAddr))
                        print(readList[i])
                        siliconAddr+=4
                    return readList
        #print("null")

def empty_readblk(addr, size, dataType, elementNum):
    siliconAddr= getMemValue(addr)
    from automation import silConnect
    readbyte=silConnect.empty_read_wrd(siliconAddr)   

def writeBlock(addr, size, data, dataType):
    from automation import targetdict
    #print("writing to "+str(targetdict['TargetName']))
    if (targetdict['TargetName']=='FPGA'):
        if(dataType==lmac_def.DataType.TYPE_32BIT):
            DA.WriteMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned32bit, data, DUT_MemoryTypes.Default)
        if(dataType==lmac_def.DataType.TYPE_8BIT):
            DA.WriteMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned8bit, data, DUT_MemoryTypes.Default)    
    elif(targetdict['TargetName']=='SILICON'):
        if (targetdict['SiliconAccessType']=='DAUtils'):
            if(dataType==lmac_def.DataType.TYPE_32BIT):
                DA.WriteMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned32bit, data, DUT_MemoryTypes.Default)
            if(dataType==lmac_def.DataType.TYPE_8BIT):
                DA.WriteMemoryBlock(addr, size, DUT_ElementTypes.typeUnsigned8bit, data, DUT_MemoryTypes.Default) 
        elif(targetdict['SiliconAccessType']=='WifiUtils'):
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
    