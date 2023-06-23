#-------------------------------------------------------------------------------
# Name:        data_type_utils.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     23/10/2021
# Copyright:   (c) Imagination Technologies 2021
#-------------------------------------------------------------------------------
""" Global values, class etc required across multiple module should be defined
    here """

######################################
import os
import time

######################################
class ElementTypes(object):
    """
    MTP Element Types:
    ===== ==============
    Value Element Type
    ===== ==============
     1    unsigned 8-bit
     2    unsigned 16-bit
     4    unsigned 32-bit
     8    unsigned 64-bit
    -1    signed 8-bit
    -2    signed 16-bit
    -4    signed 32-bit
    -8    signed 64-bit
    32    32-bit floating point
    64    64-bit floating point (double)
    ===== ==============
    """
    # Integer Types
    typeUnsigned8bit  =  1
    typeUnsigned16bit =  2
    typeUnsigned32bit =  4
    typeUnsigned64bit =  8
    typeSigned8bit    = -1
    typeSigned16bit   = -2
    typeSigned32bit   = -4
    typeSigned64bit   = -8

    # Floating Point Types
    typeFloat32bit    = 32
    typeFloat64bit    = 64

class MemoryTypes(object):
    """ Defines the different Memory Types that are used on DUT """
    Default                 = 0
    MinimDataRam            = 1
    MinimCodeRam            = 2
    DSPRamD0RamA            = 4
    DSPRamD0RamB            = 5
    DSPRamD1RamA            = 6
    DSPRamD1RamB            = 7
    WideDataMemory          = 8
    NarrowDataMemory        = 9
    RegionAMemory           = 8
    RegionBMemory           = 9
    PeripheralMemory        = 10
    MCPSystemBusRegisters   = 12
    BulkMemory              = 13
    ComplexWideDataMemory   = 14
    ComplexRegionAMemory    = 14
    ComplexNarrowDataMemory = 15
    ComplexRegionBMemory    = 15
    JTagMemory              = 16
    RegionLMemory           = 17
    ComplexRegionLMemory    = 18
    RegionCMemory           = 21
    RegionDMemory           = 22


##############################################
# Class Object Instatiantions:
DUT_MemoryTypes      = MemoryTypes()
DUT_ElementTypes     = ElementTypes()
###############################################

##def debugPrint(string):
##    """ Log the string to debug log file """
##    print string
##    #debug_log_file = os.path.join(outFilePath, 'debug.log')
##    debug_log_file = os.path.join(os.getcwd(), 'debug.log')
##    fdebug=open(debug_log_file,'a')
##    fdebug.write(str(string)+'\n')
##    fdebug.close()

