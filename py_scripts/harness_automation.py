# ----------------------------------------------------------------------------
# Name:        harness_automation.py
# Purpose:     This is the main script to be run for Harness automation.
#              Configure the WLANPHY.TestConfig.xlsx file in phy/test_config
#              folder before running this file.
#
# Author:      Imagination Technologies
#
# Created:     2020
# Copyright:   (c) 2020, Imagination Technologies Ltd.
# ----------------------------------------------------------------------------

"""
This is the main file to be run for Harness automation in different operating
mode.Configure the WLANPHY.TestConfig.xlsx file in phy/test_config folder before
running this file
"""

#######################################
# Keep the imports here
import time
import datetime
import test_mode_functions
import DUT_functions
import target_functions
import file_operations

from common_utils import *
######################################

def main():
    """ Automation test start """

    testStart = datetime.datetime.now().replace(microsecond=0)

    # Instantiate the TestConfigParams object
    targetParams = TargetParams()
    testConfigParams = TestConfigParams()
    revParams = RevParams()

    # Read the test configuration from "WLANPHY.TestConfig.xlsx" excel sheet
    testConfigDict = file_operations.readTestConfigExcel('WLANPHY.TestConfig.xlsx')
    targetParams.updateParams(testConfigDict)
    testConfigParams.updateParams(testConfigDict)
    revParams.updateParams(testConfigDict)

    createDebugLog(testConfigParams)
    createSubPlanLog(testConfigParams)
    debugPrint("=================== TEST START ===================")

    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
    DUT_functions.pollSystemReady()
    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)

    if testConfigParams.dut_operating_mode == 'RX':
        # Function call corresponding to operating mode RX
        test_mode_functions.executeOperatingMode_RX(testConfigParams, targetParams, revParams)
    elif testConfigParams.dut_operating_mode == 'TX':
        # Function call corresponding to operating mode TX
        test_mode_functions.executeOperatingMode_TX(testConfigParams, targetParams, revParams)
    elif testConfigParams.dut_operating_mode == 'LOOP_BACK':
        # Function call corresponding to operating mode LOOPBACK
        test_mode_functions.executeOperatingMode_LOOPBACK(testConfigParams, targetParams)
    elif testConfigParams.dut_operating_mode == 'FEED':
        # Function call corresponding to operating mode TX
        test_mode_functions.executeOperatingMode_FEED(testConfigParams)
    elif testConfigParams.dut_operating_mode == 'CAPTURE':
        # Function call corresponding to operating mode LOOPBACK
        test_mode_functions.executeOperatingMode_CAPTURE(testConfigParams)

    testEnd = datetime.datetime.now().replace(microsecond=0)
    duration = testEnd - testStart
    duration_str = 'Total Test duration = ' + str(duration)
    debugPrint(duration_str)
    debugPrint("=================== TEST END ===================")


if __name__ == '__main__':
    main()
    time.sleep(20)
