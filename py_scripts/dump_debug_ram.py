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

def main(argv):
    probe('sp' + argv)
    all_devices = listdevices()
    s3c0v0 = all_devices[3]

    #dump samples to files
    f=open('dump/debug_ram.txt', 'w')

    for page in range(8):
        word(0xa501c000, page<<8, verify=False)
        f.write(str(word(0xa501c000, count=4096)) + "\n")

    f.close()


if __name__ == '__main__':
    main(sys.argv[1])