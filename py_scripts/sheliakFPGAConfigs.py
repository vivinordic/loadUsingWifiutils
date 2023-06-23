#-------------------------------------------------------------------------------
# Name:        sheliakFPGAConfigs
# Purpose:     Script to perform configurations required in Sheliak FPGA case.
#
# Author:      Nordic Semiconductor
#
# Created:     29/11/2021
# Copyright:   (c) Nordic Semiconductor 2021
#-------------------------------------------------------------------------------

#from imgtec.console import *
import sys

def main(argv):
    probe('sp' + argv)
    all_devices = listdevices()
    s2c0v0 = all_devices[2]
    # To read Date & Time stamp registers
    word(0x10818, device=s2c0v0)
    word(0x1081C, device=s2c0v0)

    #Set QSPI Clock Write/Read Frequencies
    word(0x10600, 0, device=s2c0v0)
    word(0x10604, 1, device=s2c0v0)

    #LVDS Tx, Rx Enable
    word(0x6088, 0x39, device=s2c0v0)
    word(0x6084, 0x1B, device=s2c0v0)
    
    #Set IDELAY for each lane    
    word(0x10100, 0x40, device=s2c0v0)
    word(0x10104, 0x40, device=s2c0v0)
    word(0x10108, 0x40, device=s2c0v0)
    word(0x1010C, 0x40, device=s2c0v0)
    
   
    #Set ODELAY for each lane
    word(0x10200, 0x0, device=s2c0v0)
    word(0x10204, 0x0, device=s2c0v0)
    word(0x10208, 0x0, device=s2c0v0)
    word(0x1020C, 0x0, device=s2c0v0)
    word(0x10210, 0x0, device=s2c0v0)
    word(0x10214, 0x0, device=s2c0v0)
    word(0x10218, 0x0, device=s2c0v0)


if __name__ == '__main__':
    main(sys.argv[1])
