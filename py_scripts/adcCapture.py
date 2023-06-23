#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     23/03/2021
# Copyright:   (c) vivi 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#from imgtec.console import *
import time
import sys

captureCount = 0x10000

def main(argv):
    probe('sp' + argv)
    all_devices = listdevices()
    s3c0v0 = all_devices[3]
    # configure capture memory and start capture
    word(0x0, 0x3000000, device=s3c0v0) # capture in one shot mode
    word(0xC, captureCount, device=s3c0v0)

    #wait for capture complete
    time.sleep(10)

    #read capture samples
    word(0x0, 0x400000, device=s3c0v0)
    samples = word(0x4000000, count=captureCount, device=s3c0v0)

    #dump samples to files
    outFileReal =  "cap_output_real.txt"
    outFileImag =  "cap_output_imag.txt"
    foReal = open(outFileReal, "w")
    foImag = open(outFileImag, "w")
    for index in range(0,captureCount):
        samplesOutReal = (samples[index]>>20)
        samplesOutImag = ((samples[index]>>4) & 0xfff)
        foReal.write('%03X\n' %samplesOutReal)
        foImag.write('%03X\n' %samplesOutImag)

    foReal.close()
    foImag.close()
    pass

if __name__ == '__main__':
    main(sys.argv[1])
