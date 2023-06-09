#-------------------------------------------------------------------------------
# Name:        target_functions.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     05/05/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------
""" API's related to target """

############################################
import os, sys, time

from imgtec.console import *
from CSUtils import DA
#from common_utils import *
#############################################


def loadnRunTarget(target, ip, fileName):
    """ Load HARNESS script to the target and run"""

    #DA.UseTarget(target, "10.90.48.108")
    DA.UseTarget(target, ip)
    target_info = DA.GetTargetInfo()
    #debugPrint(str(target_info))
    file=fileName
    #print("file is "+str(file))
    print(str(target_info))
    from automation import targetdict
    if(targetdict['TargetName']=='FPGA'):    
        DA.HardReset()
        loadProgramFile(file)
        runTarget()

def loadProgramFile(file):
    """ Load HARNESS program file """

    harnessFile = file #"../output/images/release_MIPSGCC/LMAC_LOADER.py"
    DA.LoadProgramFile(harnessFile, ShowProgress = True)

def runTarget():
    """ run target """
    #debugPrint('RUNNING TARGET')
    print('RUNNING TARGET')
    DA.Run()
    while(1):
        if (DA.IsRunning() == False):
            DA.Run()
            time.sleep(3)
        if (DA.IsRunning() == True):
            break
