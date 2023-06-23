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

#from imgtec.console import *
#from CSUtils import DA
from common_utils import *
#############################################



def loadnRunTarget(test_mode ,targetParams, selectPhyorMacControl):
    """ Load HARNESS script to the target and run"""

    DA.UseTarget(targetParams.target)

    #MCU or MCU2 will select based on the application build
    DA.SelectTargetByPattern(targetParams.target_selection)

    target_info = DA.GetTargetInfo()
    debugPrint(str(target_info))

    if(targetParams.target_selection =='MCU') and (targetParams.system_config == '530_77'):
        DA.HardReset()
    if(targetParams.target_selection =='MCU') and (targetParams.system_config == '610_79'):
        if(test_mode == 'PLAYOUT'):
            DA.HardReset()
    loadProgramFile(selectPhyorMacControl, targetParams.target_selection, test_mode, targetParams.system_config)
    runTarget()

def loadProgramFile(selectPhyorMacControl, target_selection, test_mode, system_config):
    """ Load HARNESS program file """
    if selectPhyorMacControl == 0:
        harnessFile = "../harness/loader/build/smake/release_MIPSGCC/HARNESS.py"
    else:
        harnessFile = "../harness_macControl/loader/build/smake/release_MIPSGCC/HARNESS.py"
    if(target_selection =='MCU') and (system_config == '530_77'):
        DA.LoadProgramFile(harnessFile, ShowProgress = True)
    if(target_selection =='MCU') and (system_config == '610_79'):
        if(test_mode == 'PLAYOUT'):
            DA.LoadProgramFile(harnessFile, ShowProgress = True)
        else:
            DA.LoadProgramFileEx(harnessFile, HardReset = False, ShowProgress=True)
    elif(target_selection =='MCU2'):
        DA.LoadProgramFileEx(harnessFile, HardReset = False, ShowProgress=True)

def runTarget():
    """ run target """
    debugPrint('RUNNING TARGET')
    DA.Run()
    while(1):
        if (DA.IsRunning() == False):
            DA.Run()
            time.sleep(3)
        if (DA.IsRunning() == True):
            break
