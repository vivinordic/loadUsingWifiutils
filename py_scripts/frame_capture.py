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

captureCount = 0x80000
captureDelay = 0xffff
MCS = 0

def main(sysProbe, pkt_format):
    probe('sp' + sysProbe)
    all_devices = listdevices()
    s3c0v0 = all_devices[3]
    # configure capture memory and start capture
    word(0x0, 0x1020000, device=s3c0v0) # capture in CONTINOUS mode
    word(0xC, captureCount, device=s3c0v0) # capture buffer length
    # FFFF  CAPTURE DELAY, B8 = 10111000 msb 1 is CAPTURE ENABLE, 111 is hetb frame format

    if (pkt_format == 'LG'):
        word(0xa5003470,0x100 + (MCS << 12) + (captureDelay<<16)) # once LG packet is discoverd stop capture after next captureCount number of samples
    elif (pkt_format == 'HT'):
        word(0xa5003470,0x300 + (MCS << 12) + (captureDelay<<16)) # once HT packet is discoverd stop capture after next captureCount number of samples
    elif (pkt_format == 'VHT'):
        word(0xa5003470,0x700 + (MCS << 12) + (captureDelay<<16)) # once VHT packet is discoverd stop capture after next captureCount number of samples
    elif (pkt_format == 'HESU'):
        word(0xa5003470,0x900 + (MCS << 12) + (captureDelay<<16)) # once HESU packet is discoverd stop capture after next captureCount number of samples
    elif (pkt_format == 'HEMU'):
        word(0xa5003470,0xb00 + (MCS << 12) + (captureDelay<<16)) # once HEMU packet is discoverd stop capture after next captureCount number of samples
    elif (pkt_format == 'HERSU'):
        word(0xa5003470,0xd00 + (MCS << 12) + (captureDelay<<16)) # once HEERSU packet is discoverd stop capture after next captureCount number of samples
    elif (pkt_format == 'HETB'):
        word(0xa5003470,0xf00 + (MCS << 12) + (captureDelay<<16)) # once HETB packet is discoverd stop capture after next captureCount number of samples
    #status = word(0xa5003424)

    #wait for capture complete
    for i in range(6):
        time.sleep(10)
        status = word(0xa5003474)
        print(hex(status))
        if status == 0x300:
            break

    writePtr = word(0x4, device=s3c0v0) # this offset - 1 is where last capture sample was written in the memory
    #read capture samples
    word(0x0, 0x400000, device=s3c0v0)
    samples = word(0x4000000, count=captureCount, device=s3c0v0)
    temp = samples[writePtr:]+samples[0:writePtr] # unwrapping capture samples
    samples = temp

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

    word(0xa5003470,0) # disabling trigger based capture mode
    pass

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])
