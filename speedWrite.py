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

a = [0,0,1,1,1,2,1,3,3,3,3,0,1,1,2,4,4,5,5,5,5,5,5,5,5,5,5,5,5,5,5,1]

def main():
    address = 0
    data = a[0]
    size = 1
    for x in range(len(a)-1):
        if (a[x+1] == data):
            size += 1
        else:
            print(hex(address),data,size)
            address += size * 4
            data = a[x+1]
            size = 1
    print(hex(address),data,size)
    pass

def main1():
    address = 0
    for x in a:
        print(hex(address),x)
        address += 4

if __name__ == '__main__':
    main()
    main1()
