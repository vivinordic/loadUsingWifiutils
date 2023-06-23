#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      viju.vijayakumar
#
# Created:     04/12/2018
# Copyright:   (c) viju.vijayakumar 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import shutil
# TX_results with_calib_en
paths = ['..\\Results\\ALL_functional_Results\\11ac\\1x1_1\\STBC_0\\BCC\\LGI','..\\Results\\ALL_functional_Results\\11b\\LONG',
         '..\\Results\\ALL_functional_Results\\11n\\1x1_1\\STBC_0\\BCC\\LGI\\Mixed','..\\Results\\ALL_functional_Results\\11g','..\\Results\\ALL_functional_Results\\11ax']

#paths = ['Results\REL_AMD_5247447\\11b\\LONG','Results\REL_AMD_5247447\\11g']

#paths = ['..\\Results\\MAIN_2x2_06APR_FIX_RA03_303\\11n\\1x1_1\STBC_0\BCC\LGI','..\\Results\\MAIN_2x2_06APR_FIX_RA03_303\\11n\\1x1_1\STBC_0\BCC\LGI']
#paths = ['..\\MAIN_2x2_06APR_FIX_RA03_303\\11n\\2x2_1\\STBC_0\\BCC\\LGI\\Mixed','..\\MAIN_2x2_06APR_FIX_RA03_303\\11ac\\2x2_1\\STBC_0\\BCC\\LGI']
def main():
    base = os.getcwd()
    destination = os.path.join(base,'copy')
    if not os.path.exists(destination):
        os.mkdir(destination)
    for path in paths:
        base_path = os.path.join(base,path)
        if  os.path.exists(base_path):
            files_in_cwd= os.listdir(base_path)
            for i in files_in_cwd:
                file_path = os.path.join(base_path,i)
                if os.path.isdir(file_path):
                    file_list = os.listdir(file_path)
                    for j in file_list:
                        if 'TX_Consolidated' in j:
                            src = os.path.join(file_path,j)
                            dest = os.path.join(destination,j)
                            shutil.copyfile(src,dest)



if __name__ == '__main__':
    main()
