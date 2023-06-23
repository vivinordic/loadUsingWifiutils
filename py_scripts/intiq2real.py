#!/usr/bin/python3
import sys
import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Convert IQ sample data from fixed point signed integer in space separated hexadecimal format to real values where first column is the time')

parser.add_argument('--bits', '-b', help='Number of bits, default 10', default=10)
parser.add_argument('--fs', '-f', help='Sampling frequency in Hz, default 80e6', default='80e6')
parser.add_argument('infile', nargs='?', help='Input file')

args = parser.parse_args()

fs = float(args.fs)
nbits = int(args.bits)

if args.infile:
    infile = open(args.infile)
else:
    infile = sys.stdin

def signextend(x, bits=10):
    return ((x + 2**(bits-1)) & (2**bits-1)) - 2**(bits-1)

data=[]
#nbits=10

t = 0.0
tlist = []
clist = []
for line in infile.readlines():
    iqdata = [signextend(int(x, 16), nbits)/2.0**(nbits-1)
              for x in line.split()]
    clist.append(iqdata[0] + 1j*iqdata[1])
    tlist.append(t)
    t = t + 1/fs
c = np.array(clist)

crms = np.sqrt(np.average(abs(c)**2))

sys.stderr.write("RMS value = %g\n" % crms)

# Normalize signal to get an RMS value of 1
cnormalized = c / crms

for ti, ci in zip(tlist, cnormalized):
    print('%0.10g %0.10g %0.10g' % (ti, np.real(ci), np.imag(ci)))


