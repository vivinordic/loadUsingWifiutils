####################################
from CSUtils import DA
from common_utils import *
import lmac_utils 
from ctypes import *
import lmac_def
import hal
from unicodedata import numeric
####################################

readingSerialCnt=0

def readLoadLmacStaticParams():
    global lmacStaticParams
    lmacStaticParams={}; lmacStaticList=[]
    sizeofLmacStaticParams=lmac_utils.lmacTb.sizeofLmacConfigParams()
    addrLmacStaticParams=0xb7000d50
    #value_ptr=DA.EvaluateSymbol("&lmacStaticParams.boot_status")
    
    #lmacStaticList=DA.ReadMemoryBlock(addrLmacStaticParams, sizeofLmacStaticParams, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    #lmacStaticList=DA.ReadMemoryBlock(addrLmacStaticParams, sizeofLmacStaticParams, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    lmacStaticList=hal.readBlock(addrLmacStaticParams, sizeofLmacStaticParams, lmac_def.DataType.TYPE_32BIT, all)
    global readingSerialCnt
    readingSerialCnt+=1
    #print(lmacStaticList)
    lmacStaticParams.update({'Bootstatus' : lmacStaticList[0]})
    lmacStaticParams.update({'FreeCmdPtrQPopAddr' : lmacStaticList[15]})
    lmacStaticParams.update({'CmdPtrQPushAddr' : lmacStaticList[21]})
    lmacStaticParams.update({'SetLmacIsr' : lmacStaticList[52]})
    lmacStaticParams.update({'EventPtrQPopAddr' : lmacStaticList[25]})
    print(lmacStaticParams)

def readPopPushAddr():
    global lmacAddressPop
    global commandAddr
    global lmacAddressPush
    
    #popping from free cmd ptr queue
    lmacAddressPop=lmacStaticParams['FreeCmdPtrQPopAddr']
    #print( 'the value of lmac addr pop is' +str(lmacAddressPop))
    #lmacAddressPop= (int)(lmacAddressPop, 0) #letting python know the base of the number before converting 
    lmacAddressPop=lmacAddressPop | 0xa5000000
    print( 'the value of lmac addr pop is ' +str(hex(lmacAddressPop)))
    
    #print("read count is"+str(readingSerialCnt))
    from automation import targetdict
    if(targetdict['SiliconAccessType']=='WifiUtils'):
        commandAddr=hal.empty_readblk(lmacAddressPop, 1, lmac_def.DataType.TYPE_32BIT, 0)
    #commandAddr=DA.ReadMemoryBlock(lmacAddressPop, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    commandAddr=hal.readBlock(lmacAddressPop, 1, lmac_def.DataType.TYPE_32BIT, 0) 
    global readingSerialCnt
    readingSerialCnt+=1
    
    print('the value of cmd gram add to pop is ' + str(hex(commandAddr)))
    #DA.WriteMemoryBlock(lmacAddressPop, 1, DUT_ElementTypes.typeUnsigned32bit, commandAddr, DUT_MemoryTypes.Default)
    hal.writeBlock(lmacAddressPop, 1, commandAddr, lmac_def.DataType.TYPE_32BIT)
    #pushing to cmd ptr queue
    lmacAddressPush = lmacStaticParams['CmdPtrQPushAddr']
    #print( 'the value of lmac reset add push is' +str(hex(lmacAddressPush)))
    #lmacAddressPush= (int)(lmacAddressPush, 0) 
    lmacAddressPush=lmacAddressPush | 0xa5000000
    #print('the value of cmd gram add to push is ' + str(hex(commandAddr)))
    #print( 'the value of push address is' +str(hex(lmacAddressPush)))
    #DA.WriteMemoryBlock(lmacAddressPush, 1, DUT_ElementTypes.typeUnsigned32bit, commandAddr, DUT_MemoryTypes.Default)
    hal.writeBlock(lmacAddressPush, 1, commandAddr, lmac_def.DataType.TYPE_32BIT)
    
    return commandAddr


def setLmacIsr():
    lmacIsr = lmacStaticParams['SetLmacIsr']
    #lmacIsr= (int)(lmacIsr, 0)
    lmacIsr=(lmacIsr|0xa4000000)
    #print('lmac isr address is ' +str(hex(lmacIsr)))
    isr=0xff
    #DA.WriteMemoryBlock(lmacIsr, 1, DUT_ElementTypes.typeUnsigned8bit, isr, DUT_MemoryTypes.Default)
    hal.writeBlock(lmacIsr, 1, isr, lmac_def.DataType.TYPE_8BIT)
    
    
def waitEventPopAddr():
    global waitForeventCmdAddr
    #time.sleep(10)
    waitEvent_popaddr = lmacStaticParams['EventPtrQPopAddr']
    #waitEvent_popaddr= (int)(waitEvent_popaddr, 0)
    waitEvent_popaddr=waitEvent_popaddr | 0xa5000000
    print( 'the value of wait event pop address is ' +str(hex(waitEvent_popaddr)))
    from automation import targetdict
    if(targetdict['SiliconAccessType']=='WifiUtils'):
        waitForeventCmdAddr=hal.empty_readblk(waitEvent_popaddr, 1, lmac_def.DataType.TYPE_32BIT, 0)
    
    while (1):
        #waitForeventCmdAddr=DA.ReadMemoryBlock(waitEvent_popaddr, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
        waitForeventCmdAddr=hal.readBlock(waitEvent_popaddr, 1, lmac_def.DataType.TYPE_32BIT, 0)
        global readingSerialCnt
        readingSerialCnt+=1
        if (waitForeventCmdAddr!=0):
            print("event done")
            break
        else:
            print("event not done yet")
        
    time.sleep(10)
    
    #waitForeventCmdAddr= (int)(waitForeventCmdAddr, 0)
    print('the value of wait for event cmd gram add is ' + str(hex(waitForeventCmdAddr)))
    #DA.WriteMemoryBlock(waitEvent_popaddr, 1, DUT_ElementTypes.typeUnsigned32bit, waitForeventCmdAddr, DUT_MemoryTypes.Default)
    hal.writeBlock(waitEvent_popaddr, 1, waitForeventCmdAddr, lmac_def.DataType.TYPE_32BIT)
    return waitForeventCmdAddr
    
def waitEventPushAddr():
    #pushAddrEventdone=DA.ReadMemoryBlock(waitForeventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[3]
    pushAddrEventdone=hal.readBlock(waitForeventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 3)
    global readingSerialCnt
    readingSerialCnt+=1
    #pushAddrEventdone= (int)(pushAddrEventdone, 0)    
    pushAddrEventdone=pushAddrEventdone | 0xa5000000
    #print('the value of wait for event cmd gram add is ' + str(hex(waitForeventCmdAddr)))
    #print('the value of wait for event push addr is ' + str(hex(pushAddrEventdone)))
    #DA.WriteMemoryBlock(pushAddrEventdone, 1, DUT_ElementTypes.typeUnsigned32bit, waitForeventCmdAddr, DUT_MemoryTypes.Default)
    hal.writeBlock(pushAddrEventdone, 1, waitForeventCmdAddr, lmac_def.DataType.TYPE_32BIT)
    