

#######################################
# Keep the imports here
import time
import target_functions
import lmac_utils
import sys
import subprocess
import os
import file_operations
import lmac_da_access
import lmac_wifiutils

from ctypes import *
######################################

start_time=time.time()

#declaring a dict for reading target params
global targetdict
global silConnect

targetdict ={}
targetdict=file_operations.getTargetName()

if(targetdict['TargetName']=='SIM'):
    #loading fimware image into sim.
    string = "Simulator rpusim-rpu530-main@"+`int(targetdict['SimNumber'])`+"-internal_config0077"
    fileName=targetdict['elfLocation']
    #print("location of elf is " +str(targetdict['elfLocation']))
    target_functions.loadnRunTarget(string, 0, fileName)
elif (targetdict['TargetName']=='FPGA'):
    #For FPGA give ip as second argument
    string="SysProbe "+`int(targetdict['FpgaNumber'])`
    #print(string)
    location=targetdict['FPGALocation']
    #print(location)
    fileName=targetdict['elfLocation']
    # #target_functions.loadnRunTarget('Simulator rpusim-rpu530-main@194-internal_config0077Debug', 0)
    target_functions.loadnRunTarget(string, location, fileName) #SysProbe 152
elif (targetdict['TargetName']=='SILICON'):
    if (targetdict['SiliconAccessType']=='DAUtils'):
        string="SysProbe 150"
        location=targetdict['SiliconLocation']
        target_functions.loadnRunTarget(string, location, 0)
    elif(targetdict['SiliconAccessType']=='WifiUtils'):
        print("running using the wifiutils")
        silConnect=lmac_wifiutils.WiFiUtilsClient()
        status=silConnect.connect()
        print(status)
        #we will add wifion wifi-off here 
        silConnect.wifi_off() 
        silConnect.wifi_on()
        lines=[]
        with open('lmac_bringup.txt') as f:
            lines = f.readlines()
        for line in lines: 
            silConnect.execute_command(line)

"""
val=raw_input('shall we run ?')
print(val)
"""
lmac_da_access.readLoadLmacStaticParams()

#calling waitForLmacReady function
#lmac_utils.waitForLmacReady()

lmac_utils.resetCommand()

lmac_utils.wlanMacAddrConf()

lmac_utils.wlanMacVifConf()

lmac_utils.channelProg()

constParamsDict=file_operations.constantParams()
sheetSet=file_operations.setofSheets()
sheetSet.remove("ParamsToEnter")

if(constParamsDict['SheetName']=='All'):
    sheetSet.remove("InitializationParams")
    for i in sheetSet:
        lmac_utils.sendTx(i)
elif(constParamsDict['SheetName']!='ALL'):
    sheet=constParamsDict['SheetName']
    for i in range(100):
        lmac_utils.sendTx(sheet)
    """lmac_utils.sendTx(sheet)"""
print("---------%s seconds -----------------------"%((time.time()-start_time)))