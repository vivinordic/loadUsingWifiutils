##########################################
from CSUtils import DA
from common_utils import *
import time
import lmac_def
import lmac_da_access
import file_operations
import hal 

import sys 
import subprocess 
import os 
from ctypes import *
from array import *
import xlrd

from lmac_def import LmacEventTag, SecurityModes
sys.path.append('../../../../build_scripts/lmac/output/images/lmac/dependencies/')
from uccpregs import *
##########################################

lmacTb = CDLL('./lmac_tb/lmac_tb.so')
cryptoTb = CDLL('./crypto_TB/cryptoTb.so')

"""
def waitForLmacReady():
    #get the address of lmacStaticParams boot status variable
    value_ptr=DA.EvaluateSymbol("&lmacStaticParams.boot_status")
    
    while (1):
        #read the value from address ptr value_ptr
        lmac_ready = DA.ReadMemoryBlock(value_ptr, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
        if (lmac_ready == 0x5a5a5a5a):
            print("LMAC is now ready")
            break
        else:
            print("LMAC is not ready yet")
        #since LMAC can't be ready once loaded, sleep for a while and check again
        time.sleep(1)
"""
def resetCommand():
    #get the size of resetCommand 
    sizeofReset=lmacTb.sizeofResetCmd()
    #print ('size of reset is ' +str(sizeofReset))
    
    #set the return type (restype) of wlanResetCmd to char type
    lmacTb.wlanResetCmd.restype=POINTER(c_ubyte)
    
    #get the pointer to return variable of wlanResetCmd
    lmacResetCmdPtr=lmacTb.wlanResetCmd()
    
    #read data from the pointer variable got in the above line till size of command
    lmacResetCmd=lmacResetCmdPtr[:sizeofReset]
    print( 'the value of cmd buf is ' +str(lmacResetCmd))
    
    #read the pop address and write the reset command at pop address
    resetCmdAddr=lmac_da_access.readPopPushAddr()
    #resetCmdAddr= (int)(resetCmdAddr, 0)
    print("reset cmd addr is " + str(hex(resetCmdAddr)))
    #DA.WriteMemoryBlock(resetCmdAddr, sizeofReset, DUT_ElementTypes.typeUnsigned8bit, lmacResetCmd, DUT_MemoryTypes.Default)
    hal.writeBlock(resetCmdAddr, sizeofReset, lmacResetCmd, lmac_def.DataType.TYPE_8BIT)
    #read the push address and write it reset command addr back to pool
    #lmac_da_access.pushAddr()
    
    #set the ISR
    lmac_da_access.setLmacIsr()
    
    #get the event complete addr
    waitForEventCmdAddr=lmac_da_access.waitEventPopAddr()
    
    #read the event data
    #eventData=DA.ReadMemoryBlock(waitForEventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[2]
    
    #waitForEventCmdAddr= (int)(waitForEventCmdAddr, 0)
    eventData=hal.readBlock(waitForEventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 2)
    #event_list = eventData.tolist() # list
    print(eventData)
    #check if its reset complete
    if eventData==LmacEventTag.LMAC_EVENT_RESET_COMPLETE.value :
        print "reset complete done"
        #push the address back to the pool
        lmac_da_access.waitEventPushAddr()
    
    
def wlanMacAddrConf():
    sizeofMacAddrConfig=lmacTb.sizeofVifctrl()
    #print ('size of Mac addr config cmd is ' +str(sizeofMacAddrConfig))
    
    constParamsDict = {}
    constParamsDict=file_operations.constantParams()
    global wlanMacAddr
    wlanMacAddr=[]
    for i in range(0,6):
        wlanMacAddr.append(constParamsDict['MacAddress'][i])
    #print(wlanMacAddr)
    
    lmacTb.wlanMacAddrConfig.argtypes = [py_object]
    lmacTb.wlanMacAddrConfig.restype=POINTER(c_ubyte)
    lmacMacAddrConfCmdPtr=lmacTb.wlanMacAddrConfig(wlanMacAddr)
    lmacMacAddrConfCmd=lmacMacAddrConfCmdPtr[:sizeofMacAddrConfig]
    
    gramCmdAddr=lmac_da_access.readPopPushAddr()
    #DA.WriteMemoryBlock(gramCmdAddr, sizeofMacAddrConfig, DUT_ElementTypes.typeUnsigned8bit, lmacMacAddrConfCmd, DUT_MemoryTypes.Default)
    hal.writeBlock(gramCmdAddr, sizeofMacAddrConfig, lmacMacAddrConfCmd, lmac_def.DataType.TYPE_8BIT)
    #lmac_da_access.pushAddr()
    
    lmac_da_access.setLmacIsr()
    
    waitForEventCmdAddr=lmac_da_access.waitEventPopAddr()
    
    #eventData=DA.ReadMemoryBlock(waitForEventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[2]
    eventData=hal.readBlock(waitForEventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 2)
    #print(eventData)
    
    if eventData==LmacEventTag.LMAC_EVENT_COMMAND_PROC_DONE.value :
        print "mac address config is done"
        lmac_da_access.waitEventPushAddr()
 
def wlanMacVifConf():
    sizeofMacVifConfig=lmacTb.sizeofVifconfig()
    print ('size of Vif config cmd is ' +str(sizeofMacVifConfig))
    lmacTb.wlanVifCfg.restype=POINTER(c_ubyte)
    wlanVifConfPtr=lmacTb.wlanVifCfg()
    wlanVifConfCmd=wlanVifConfPtr[:sizeofMacVifConfig]
    
    gramCmdAddr=lmac_da_access.readPopPushAddr()
    #DA.WriteMemoryBlock(gramCmdAddr, sizeofMacVifConfig, DUT_ElementTypes.typeUnsigned8bit, wlanVifConfCmd, DUT_MemoryTypes.Default)
    hal.writeBlock(gramCmdAddr, sizeofMacVifConfig, wlanVifConfCmd, lmac_def.DataType.TYPE_8BIT)
    
    #lmac_da_access.pushAddr()
    
    lmac_da_access.setLmacIsr()
    
    waitForEventCmdAddr=lmac_da_access.waitEventPopAddr()
    
    #eventData=DA.ReadMemoryBlock(waitForEventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[2]
    eventData=hal.readBlock(waitForEventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 2)
    
    #event_list = eventData.tolist() # list
    #print(eventData)
    
    #lmacTb.waitForEventFromRpu(5, waitEvent_popaddr)
    if eventData==LmacEventTag.LMAC_EVENT_COMMAND_PROC_DONE.value :
        print "VIF config is done"
        lmac_da_access.waitEventPushAddr()
        
def keyProg():
    sizeofKeyCmd=lmacTb.sizeofKeyCmd()
    #print ('size of Key cmd is ' +str(sizeofKeyCmd))
    lmacTb.wlanSetKeyCmd.restype=POINTER(c_ubyte)
    lmacTb.wlanSetKeyCmd.argtypes = [py_object]
    
    wlanKeyCmdPtr=lmacTb.wlanSetKeyCmd(paramsDict)
    wlanKeyCmd=wlanKeyCmdPtr[:sizeofKeyCmd]
    
    gramCmdAddr=lmac_da_access.readPopPushAddr()
    #DA.WriteMemoryBlock(gramCmdAddr, sizeofKeyCmd, DUT_ElementTypes.typeUnsigned8bit, wlanKeyCmd, DUT_MemoryTypes.Default)
    hal.writeBlock(gramCmdAddr, sizeofKeyCmd, wlanKeyCmd, lmac_def.DataType.TYPE_8BIT)
    
    #lmac_da_access.pushAddr()
    
    lmac_da_access.setLmacIsr()
    
    waitForEventCmdAddr=lmac_da_access.waitEventPopAddr()
    #eventData=DA.ReadMemoryBlock(waitForEventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[2]
    #event_list = eventData.tolist() # list
    eventData=hal.readBlock(waitForEventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 2)
    
    
    #print(eventData)
    
    #lmacTb.waitForEventFromRpu(5, waitEvent_popaddr)
    
    lmac_da_access.waitEventPushAddr()
    
    

def channelProg():
    constParamsDict = {}
    constParamsDict=file_operations.constantParams()
    
    sizeofchannelCmd=lmacTb.sizeofCmdchannel()
    #print ('size of Channel prog config cmd is ' +str(sizeofchannelCmd))
    lmacTb.wlanChannelProgram.argtypes = [py_object]
    lmacTb.wlanChannelProgram.restype=POINTER(c_ubyte)
    channelCmdPtr=lmacTb.wlanChannelProgram(constParamsDict)
    channelCmd=channelCmdPtr[:sizeofchannelCmd]
    
    gramCmdAddr=lmac_da_access.readPopPushAddr()
    #DA.WriteMemoryBlock(gramCmdAddr, sizeofchannelCmd, DUT_ElementTypes.typeUnsigned8bit, channelCmd, DUT_MemoryTypes.Default)
    hal.writeBlock(gramCmdAddr, sizeofchannelCmd, channelCmd, lmac_def.DataType.TYPE_8BIT)
    #lmac_da_access.pushAddr()
    
    lmac_da_access.setLmacIsr()
    
    waitForEventCmdAddr=lmac_da_access.waitEventPopAddr()
    
    #eventData=DA.ReadMemoryBlock(waitForEventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[2]
    eventData=hal.readBlock(waitForEventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 2)
    
    #print(eventData)
    
    #lmacTb.waitForEventFromRpu(5, waitEvent_popaddr)
    if eventData==LmacEventTag.LMAC_EVENT_CH_PROG_DONE.value :
        print "Channel programming is done"
        lmac_da_access.waitEventPushAddr()
    
    time.sleep(1)
    
    waitForEventCmdAddr=lmac_da_access.waitEventPopAddr()
    
    #eventData=DA.ReadMemoryBlock(waitForEventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[2]
    eventData=hal.readBlock(waitForEventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 2)
    
    #event_list = eventData.tolist() # list
    #print(eventData)
    
    #lmacTb.waitForEventFromRpu(5, waitEvent_popaddr)
    if eventData==LmacEventTag.LMAC_EVENT_COMMAND_PROC_DONE.value :
        print "channel prog procedure is done"
        lmac_da_access.waitEventPushAddr()

def sendTx(sheet):
    sizeofTx=lmacTb.sizeofTxCmd()
    #print ('size of Tx cmd is ' +str(sizeofTx))
    
    #setting the return type of the function to pointer char type
    lmacTb.wlanSendTxPkt.restype=POINTER(c_ubyte)
    #lmacTb.wlanSendTxPkt.argtypes = [py_object]
    lmacTb.wlanSendTxPkt.argtypes = [py_object, py_object]
    
    
    global paramsDict
    sheetinfo=file_operations.commonParamsInfo(sheet)        
    #print("row count is " +str(sheetinfo[0]))
    startrow=4 ; endrow=5 #sheetinfo[0] #row 1 is title
    #if (sheet!="Plain"):
        #keyProg()
    for row in range(startrow, endrow):
        paramsDict=file_operations.accessFile(row)
        #paramsDict=file_operations.accessFile(4)
        
        #keyProg()
        
        #print(wlanMacAddr)
        #TxCmdPtr=lmacTb.wlanSendTxPkt(paramsDict)
        TxCmdPtr=lmacTb.wlanSendTxPkt(paramsDict, wlanMacAddr)
        
        #getting tx cmd from tx cmd pointer returned by function wlanSendTxPkt
        TxCmd=TxCmdPtr[:sizeofTx]
        
        macHeader=[]
        macHeader=TxCmd[114:142]
        #print( 'the value of mac header is ' +str(macHeader))
        lmacTb.wlanTxPkt.restype=POINTER(c_uint)
        lmacTb.wlanTxPkt.argtypes = [py_object]
        txPktPtr=lmacTb.wlanTxPkt(paramsDict)
        ampdu=int(paramsDict["AmpduSubFrameCount"])
        TxLoc=txPktPtr[:ampdu]
        #print( 'the value of tx pkt ptr is ' +str(TxLoc))
        #print(" value of security case is" +str(SecurityModes.RPU_PLAIN.value))
        if (paramsDict["SecurityMode"]!=SecurityModes.RPU_PLAIN.value):
            keyProg()
            print("running security cases")
            cryptoTb.cryptoMain.restype=POINTER(c_uint)
            cryptoTb.cryptoMain.argtypes = [py_object, py_object]
            encPktPtr=cryptoTb.cryptoMain(paramsDict, macHeader)
            sizefPkt=int(paramsDict["PacketSize"])
            #sizefPkt=100
            txData=encPktPtr[:sizefPkt]
            size=sizefPkt
        else:
            size=26
            txdata2=[0x6d]*92
            txData=macHeader+txdata2
            size=size+92
            
        for i in range(ampdu):
            writeLoc=TxLoc[i]
            if(int(paramsDict["FrameSource"])==0):
                ddrmsb=TxLoc[i]>> 25
                #DA.WriteMemoryBlock(ABS_SYS_UCCP_SOC_FAB_MEM_ADDR_MSBS1, 1, DUT_ElementTypes.typeUnsigned32bit, ddrmsb, DUT_MemoryTypes.Default)
                hal.writeBlock(ABS_SYS_UCCP_SOC_FAB_MEM_ADDR_MSBS1, 1, ddrmsb, lmac_def.DataType.TYPE_32BIT)
                writeLoc =  writeLoc & 0x1ffffff
                writeLoc = writeLoc | 0xb0000000
            print('address loc is' +str(hex(writeLoc)))
            #DA.WriteMemoryBlock(writeLoc, size, DUT_ElementTypes.typeUnsigned8bit, txData, DUT_MemoryTypes.Default)
            hal.writeBlock(writeLoc, size, txData, lmac_def.DataType.TYPE_8BIT)
            
        gramCmdAddr=lmac_da_access.readPopPushAddr()
        #DA.WriteMemoryBlock(gramCmdAddr, sizeofTx, DUT_ElementTypes.typeUnsigned8bit, TxCmd, DUT_MemoryTypes.Default)
        hal.writeBlock(gramCmdAddr, sizeofTx, TxCmd, lmac_def.DataType.TYPE_8BIT)
        
        #lmac_da_access.pushAddr()
    
        lmac_da_access.setLmacIsr()
    
        waitForEventCmdAddr=lmac_da_access.waitEventPopAddr()
    
        #eventData=DA.ReadMemoryBlock(waitForEventCmdAddr, 5, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[2]
        eventData=hal.readBlock(waitForEventCmdAddr, 5, lmac_def.DataType.TYPE_32BIT, 2)
    
        #event_list = eventData.tolist() # list
        print(eventData)
    
        #lmacTb.waitForEventFromRpu(5, waitEvent_popaddr)
        if eventData==LmacEventTag.LMAC_EVENT_TX_DONE.value :
            print "Tx is done"
            lmac_da_access.waitEventPushAddr()
            file_operations.writeToFile(1,row)
        else :
            print "Tx Fail"
            file_operations.writeToFile(0,row)
            
        #index+=1; print("index is "+str(index))
    