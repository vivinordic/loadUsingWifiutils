#-------------------------------------------------------------------------------
# Name:        playout_functions.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------

""" API's to cofigure playout and capture settings """

########################################
#from CSUtils import DA
from data_type_utils import *
########################################

##def targetSelectionPlayout(targetSel):
##    global target_selection
##    target_selection = targetSel

def configClock():
    """" clock configuration """
    DA.SelectTargetByPattern('EMULATOR')

##  Emulator configration Core clock =80MHz , DAC=40MHz and ADC=40MHz
    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x1, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_SYS_1X')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_META_MEM')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_META_2X')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_LDPC_2X')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_VIT_2X')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_IF')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10002, DUT_MemoryTypes.Default)

    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_DAC')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10002, DUT_MemoryTypes.Default)

##    Emulator configuration Core clock =60MHz , DAC=40MHz and ADC=40MHz
##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x1, DUT_MemoryTypes.Default)

##
##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_SYS_1X')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10003, DUT_MemoryTypes.Default)

##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_META_MEM')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_META_2X')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_LDPC_2X')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_VIT_2X')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x10001, DUT_MemoryTypes.Default)

##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_IF')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x20009, DUT_MemoryTypes.Default)

##    value = DA.EvaluateSymbol('KUROI.ARB_CLK_DIV_CTRL_DAC')
##    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0x20009, DUT_MemoryTypes.Default)
    DA.SelectTargetByPattern('MCU')



def configRXPlayoutInputSel():
    """" config Playout input selction """
    DA.SelectTargetByPattern('EMULATOR')
    value = DA.EvaluateSymbol('KUROI.PLAYOUT_INPUT_SELECT')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned64bit, 1, DUT_MemoryTypes.Default)
    DA.SelectTargetByPattern('MCU')


def configRXPlayout(lnaModelEnable):
    """" config Playout mode """
    DA.SelectTargetByPattern('EMULATOR')
    if (lnaModelEnable == 'YES'):
        value_ptr_1 = DA.EvaluateSymbol('KUROI.LNA_RF_CONFIG')
        value = DA.ReadMemoryBlock(value_ptr_1, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
        #Enable LNA bit in the LNA_RF_CONFIG register
        lnaRfConfig = (value[0] & 0xFFFFFFFE) | 0x1
        # Cofigure clock div value in the LNA_RF_CONFIG register
        lnaRfConfig = (lnaRfConfig & 0xFFFFFF0F) | 0x10
        DA.WriteMemoryBlock(value_ptr_1, 1, DUT_ElementTypes.typeUnsigned64bit, lnaRfConfig, DUT_MemoryTypes.Default)

    ## configure PO_MEM_REGS.xxxx by default.
    #playout memory configuration
    po_mem_config= 0x02400000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned64bit, po_mem_config, DUT_MemoryTypes.Default)
    #playout memory offset from base address
    po_offset_address = 0x00000000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_02')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, po_offset_address, DUT_MemoryTypes.Default)

    #playout memory base address
    po_base_address = 0x00000000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_03')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, po_base_address, DUT_MemoryTypes.Default)
    DA.SelectTargetByPattern('MCU')

def writeSamplesPlayout(inputSamples, numSamples, memoryType):
    """" write samples to playout memory and start playout """
    writeSamples(inputSamples, numSamples, memoryType)
    deassertMemoryMap(memoryType)
    startPlayout(numSamples)
    DA.SelectTargetByPattern('MCU')

def writeSamples(inputSamples, numSamples, memoryType):
    """" write samples to playout memory """
    DA.SelectTargetByPattern('EMULATOR')
    if (memoryType == 'shared'):
        value = 0x20000000
        DA.WriteMemoryBlock(value, numSamples, DUT_ElementTypes.typeUnsigned32bit, inputSamples, DUT_MemoryTypes.Default)
    else:
        value = 0x40000000
        DA.WriteMemoryBlock(value, (numSamples*2), DUT_ElementTypes.typeUnsigned32bit, inputSamples, DUT_MemoryTypes.Default)

def deassertMemoryMap(memoryType):
    """" deassert memory mapping """
    DA.SelectTargetByPattern('EMULATOR')
    #playout memory configuration
    if (memoryType == 'shared'):
        po_mem_config= 0x02000000
    else:
        po_mem_config= 0x02200000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned64bit, po_mem_config, DUT_MemoryTypes.Default)

def deassertMemoryMapAck(memoryType):
    """" deassert memory mapping """
    DA.SelectTargetByPattern('EMULATOR')
    #playout memory configuration
    if (memoryType == 'shared'):
        po_mem_config= 0x02040000
    else:
        po_mem_config= 0x02240000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned64bit, po_mem_config, DUT_MemoryTypes.Default)

def pollCaptureReady4Ack():
    """" deassert memory mapping """
    DA.SelectTargetByPattern('EMULATOR')

    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    captureReadyStatus = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    while((captureReadyStatus[0] & 0x1000000) == 0):
        value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
        captureReadyStatus = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
        if((captureReadyStatus[0] & 0x1000000) != 0):
            print("Playout 1 status is %d" %captureReadyStatus[0])
            break

def startPlayout(numSamples):
    """" start playout"""
    DA.SelectTargetByPattern('EMULATOR')
    #set length of memory
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_04')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned64bit, numSamples, DUT_MemoryTypes.Default)

def pollPlayoutDone():
    """" Poll for playout done """
    DA.SelectTargetByPattern('EMULATOR')
    value_ptr_1 = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
    po_end_status_1 = DA.ReadMemoryBlock(value_ptr_1, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    while(1):
        po_end_status_1 = DA.ReadMemoryBlock(value_ptr_1, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
        if(po_end_status_1[0] == 2):
            print("Playout 1 status is %d" %po_end_status_1[0])
            break
        time.sleep(1)
    clearChainOneLen()
    print("Resetting Playout Done Events")
    DA.WriteMemoryBlock(value_ptr_1, 1, DUT_ElementTypes.typeUnsigned32bit, po_end_status_1, DUT_MemoryTypes.Default)
    po_end_status_1 = DA.ReadMemoryBlock(value_ptr_1, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    print("Playout status is %d" %po_end_status_1[0])
    softResetChainOne()
    DA.SelectTargetByPattern('MCU')

def softResetChainOne():
    print("Resetting the Playout 1")
    DA.SelectTargetByPattern('EMULATOR')
    #playout memory configuration
    po_mem_config= 0x80000000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned64bit, po_mem_config, DUT_MemoryTypes.Default)

    time.sleep(2)

    po_mem_config= 0x00000000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned64bit, po_mem_config, DUT_MemoryTypes.Default)

def clearChainOneLen():
    DA.SelectTargetByPattern('EMULATOR')
    #set length of memory
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_04')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

def configTXCapture():
    """" config capture mode """
    DA.SelectTargetByPattern('EMULATOR')
    cap_mem_config= 0x03000000
    #capture mode enable
    #cap_mem_config= 0x03400000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, cap_mem_config, DUT_MemoryTypes.Default)
    #playout memory offset from base address
    cap_offset_address = 0x00000000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_02')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, cap_offset_address, DUT_MemoryTypes.Default)
    #playout memory base address
    cap_base_address = 0x00000000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_03')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, cap_base_address, DUT_MemoryTypes.Default)
    event_status_clear = 0x00000002
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, event_status_clear, DUT_MemoryTypes.Default)
    DA.SelectTargetByPattern('MCU')

def startCapture(samples2Read):
    DA.SelectTargetByPattern('EMULATOR')
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_04')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, samples2Read, DUT_MemoryTypes.Default)
    DA.SelectTargetByPattern('MCU')

def pollCaptureDone():
    DA.SelectTargetByPattern('EMULATOR')
    #poll for done
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
    po_end_status = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    while((po_end_status[0] & 0x3) != 2):
        value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
        po_end_status = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
        if((po_end_status[0] & 0x3) == 2):
            print("Playout 1 status is %d" %po_end_status[0])
            break
        time.sleep(1)
    DA.SelectTargetByPattern('MCU')

def readCaptureMemory(samples2Read):
    """ read samples in Capture memory """
    DA.SelectTargetByPattern('EMULATOR')

    cap_mem_config= 0x00400000
    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, cap_mem_config, DUT_MemoryTypes.Default)
    outBuffer = []
    value = 0x20000000
    outBuffer = DA.ReadMemoryBlock(value, samples2Read, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)
    time.sleep(1)
    DA.SelectTargetByPattern('MCU')
    return outBuffer

def getNumSamplesCaptured():
    """ read number of samples captured in Capture memory """
    DA.SelectTargetByPattern('EMULATOR')

    value = DA.EvaluateSymbol('PO_MEM_REGS.PO_CAP_MEM_GEN_CFG_02')
    numSamples = DA.ReadMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, DUT_MemoryTypes.Default)[0]
    DA.SelectTargetByPattern('MCU')
    return numSamples