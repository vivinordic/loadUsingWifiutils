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

addressList = [[0x80100000, 0xc00],
[0xbfc00000, 0x10],
[0x80100c00, 0x21200],
[0x80121e00, 0x40],
[0x80121e40, 0x18],
[0x80121e58, 0x18],
[0x80121e70, 0x2abc],
[0x80124930, 0x1378],
[0x80125ca8, 0x14c],
[0x80125df4, 0x108],
[0x80125f00, 0x3510],
[0x80129410, 0x1f10],
[0xb4000000, 0x680],
[0xb7001008, 0x10408]]

address1 = 0x80100000
captureCount1 = 0xc00

address2 = 0x80100c00
captureCount2 = 0x21200

def main():
    probe('sp152')
    all_devices = listdevices()
    s1c0v0 = all_devices[1]

    #dump samples to files
    outFileReal =  "cap_output_real.txt"
    foReal = open(outFileReal, "w")

    foReal.write('###########################################################\n')
    foReal.write('Data Load:          Section Address: %08X Section Size: 0x00000c00\n' %address1)
    foReal.write('###########################################################\n')
    foReal.write('%08X\n' %address1)
    foReal.write('%03X\n' %captureCount1)
    foReal.write('***********\n')

    samples = word(address1, count=captureCount1, device=s1c0v0)

    for index in range(0,captureCount1):
        foReal.write('%08X\n' %samples[index])

    foReal.write('###########################################################\n')
    foReal.write('Data Load:          Section Address: %08X Section Size: 0x00021200\n' %address2)
    foReal.write('###########################################################\n')
    foReal.write('%08X\n' %address2)
    foReal.write('%05X\n' %captureCount2)
    foReal.write('***********\n')

    samples = word(address2, count=captureCount2, device=s1c0v0)

    for index in range(0,captureCount2):
        foReal.write('%08X\n' %samples[index])

    foReal.close()
    pass

def memRead():
    probe('sp152')
    all_devices = listdevices()
    s1c0v0 = all_devices[1]

    #dump samples to files
    outFileReal =  "cap_output_real.txt"
    foReal = open(outFileReal, "w")

    for data in addressList:
        writeFile(foReal, data[0], data[1], s1c0v0)

    foReal.close()
    pass


def writeFile(foReal, address, captureCount, s1c0v0):

    foReal.write('###########################################################\n')
    foReal.write('Data Load:          Section Address: {:#08X} Section Size: {:#08X}\n'.format(address,captureCount))
    foReal.write('###########################################################\n')
    foReal.write('0x%08X\n' %address)
    foReal.write('0x%X\n' %captureCount)
    foReal.write('***********\n')

    if ((address ==0x80125df4) or (address ==0x80125f00)):
        return

    samples = word(address, count=captureCount/4, device=s1c0v0)

    for index in range(0,captureCount/4):
        foReal.write('%08X\n' %samples[index])

if __name__ == '__main__':
    memRead()
