#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     16-06-2023
# Copyright:   (c) vivi 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

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

typeUnsigned32bit = 1
a = [0,0,1,1,1,2,1,3,3,3,3,0,1,1,2,4,4,5,5,5,5,5,5,5,5,5,5,5,5,5,5,1]

def main():
    address = 0x80100000
    data = a[0]
    size = 1
    for x in range(len(a)-1):
        if (a[x+1] == data):
            size += 1
        else:
            print(hex(address),data,size)
            address += size * 4
            data = a[x+1]
            size = 1
    print(hex(address),data,size)
    pass

def main1():
    address = 0
    for x in a:
        print(hex(address),x)
        address += 4

def writeBlockNew(silConnect, addr, size, data, dataType):
    siliconAddr= getMemValue(addr)
    writeData=data[0];
    if (size == 1):
        silConnect.write_wrd(siliconAddr, data)
    elif(size>1):
        tempSize=size
        if (dataType==typeUnsigned32bit):
            clumpSize = 1
            for x in range(size-1):
                if (data[x+1] == writeData):
                    clumpSize += 1
                else:
                    silConnect.write_blk(siliconAddr, writeData, 0, clumpSize)
                    siliconAddr += clumpSize * 4
                    writeData = a[x+1]
                    clumpSize = 1
            silConnect.write_blk(siliconAddr, writeData, 0, clumpSize)

if __name__ == '__main__':
    #main()
    #print(len(a),a)
    #writeBlockNew('', 0x80100000, len(a), a, typeUnsigned32bit)
    print(hex(getMemValue(0x801263d8)))
