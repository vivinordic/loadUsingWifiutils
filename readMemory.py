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

from imgtec.console import *
import time
import sys

address = 0x80100000
captureCount = 0xc00


def main():
    probe('sp152')
    all_devices = listdevices()
    s1c0v0 = all_devices[1]

    samples = word(address, count=captureCount, device=s1c0v0)

    #dump samples to files
    outFileReal =  "cap_output_real.txt"
    foReal = open(outFileReal, "w")
    for index in range(0,captureCount):
        foReal.write('%08X\n' %samples[index])

    foReal.close()
    pass

if __name__ == '__main__':
    main()
