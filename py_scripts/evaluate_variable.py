#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     21-06-2023
# Copyright:   (c) vivi 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import subprocess
import re
import os
import sys

def gdb_print_address(variable, elf_file):

    read, write = os.pipe()

    cmd = "gdb -q " + elf_file

    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    cmd = "printf \"0x%x\", {}".format(variable)
    cmd += "\n"
    cmd += "quit"
    # os.write(write, cmd)

    out,err = p.communicate(cmd)
    return out

def EvaluateSymbol(variable, elf_file, print_debug=False):
    """Evaluate ELF symbol address using gdb"""

    if not os.path.isfile(elf_file):
        print_err("While tring to evaluate symbol. The ELF file \"{}\" does not exist".format(elf_file))
        sys.exit(1)

    value = gdb_print_address(variable, elf_file).strip()
    print(value)

    try:
        # Extract hexademical string
        address = re.findall(r'0x[0-9A-Fa-f]+', value, re.I)[0]
    except IndexError:
        print("Unable to evaluate symbol \"{}\" - symbol not found!".format(variable))
        sys.exit(1)

    if print_debug:
        print("Evaluating symbol {} : {}".format(variable, address))

    return int(address, 16)

