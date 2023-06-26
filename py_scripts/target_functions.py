#-------------------------------------------------------------------------------
# Name:        target_functions.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     05/05/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------
""" API's related to target """

############################################

import target_functions_CS as tfcs
import target_functions_QSPI as tfQSPI
#############################################



def loadnRunTarget(test_mode ,targetParams, selectPhyorMacControl, target_type):
    print(target_type)
    if (target_type == 'QSPI'):
        tfQSPI.loadnRunTarget(test_mode, selectPhyorMacControl)
    else:
        tfcs.loadnRunTarget(test_mode ,targetParams, selectPhyorMacControl)



