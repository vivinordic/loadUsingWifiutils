# ----------------------------------------------------------------------------
# Name:        PHY_performance.py
# Purpose:     This is the main script to be run for PHY performance.

#
# Author:      Nordic Semiconductor ASA.
#
# Created:     2020
# Copyright:   (c) 2020, Imagination Technologies Ltd.
# ----------------------------------------------------------------------------

"""
This is the main file to be run for Harness testing in different operating mode.
Configure the WLANPHY.TestConfig.xlsx file in phy/test_config folder before
running this file.
"""

#######################################
# Keep the imports here
import time
import datetime
import os
import sys
import argparse

import test_mode_functions
import DUT_functions
from   common_utils import *
import target_functions
import file_operations
############################################

def main(targetType,
         targetNumber,
         testMode,
         cfgParamFromXls,
         targetSelection,
         subfunctionalTestPlan,
         systemConfiguration,
         testPlanType,
         testAllCases,
         testStartFrom,
         testEndAt,
         testType,
         equipment,
         equipIp):
    """ The main function of the Harness Control Wrapper"""
    testStart = datetime.datetime.now().replace(microsecond=0)

    # Display the IMGTEC_USER_HOME where simulators are installed.
##    if (platform == 'linux' or platform == 'linux2'):
##        print("IMGTEC_USER_HOME = " + os.environ["IMGTEC_USER_HOME"])

    test_config_xlsx = 'WLANPHY.TestConfig.xlsx'

    test_config_str = 'Using ' + test_config_xlsx + ' as input config file.'

    # Instantiate the TestConfigParams object
    revParams = RevParams()

    # Read the test configuration from "WLANPHY.TestConfig.xlsx" excel sheet and update target and
    # testConfiguration parameters
    if(cfgParamFromXls):
        testConfigDict = file_operations.readTestConfigExcel(test_config_xlsx)
    else:
        testConfigDict = {}
        testConfigDict.update( {'target_type'         : targetType} )
        testConfigDict.update( {'target_number'       : targetNumber} )
        testConfigDict.update( {'system_config'       : systemConfiguration} )
        testConfigDict.update( {'test_mode'           : testMode} )
        testConfigDict.update( {'target_selection'    : targetSelection} )
        testConfigDict.update( {'test_type'           : testPlanType} )
        testConfigDict.update( {'subFuncTestPlan'     : subfunctionalTestPlan} )
        testConfigDict.update( {'dut_operating_mode'  : testType} )
        testConfigDict.update( {'build_config'        : 'RELEASE'} )
        testConfigDict.update( {'release'             : 'ALL_functional_Results'} )
        testConfigDict.update( {'target'              : testConfigDict['target_type'] + ' ' + testConfigDict['target_number']} )
        testConfigDict.update( {'genTestCasesWithExe' : 'NO'} )
        testConfigDict.update( {'testCasesFileName'   : 'testcases_LG_RX'} )
        testConfigDict.update( {'checkAllTestCases'   : testAllCases} )
        testConfigDict.update( {'test_case_start'     : testStartFrom} )
        testConfigDict.update( {'total_test_cases'    : testEndAt} )
        testConfigDict.update( {'num_pkts'            : 1} )
        testConfigDict.update( {'time_out_value'      : 1200} )

        testConfigDict.update( {'vsg'                 : equipment} )
        testConfigDict.update( {'equip_ip'            : equipIp} )
        testConfigDict.update( {'dutModel'            : 'Harness_SSH'} )

        testConfigDict.update( {'s_no'                : 12} )
        testConfigDict.update( {'date'                : '9'} )
        testConfigDict.update( {'codebase'            : 'Calder'} )
        testConfigDict.update( {'cl_no'               : 59034} )
        testConfigDict.update( {'targetname'          : 'image12Dec2021'} )
        testConfigDict.update( {'toolkit'             : '7.3.0'} )
        testConfigDict.update( {'afe'                 : 'RF'} )
        testConfigDict.update( {'matlab'              : '8.3.2'} )
        testConfigDict.update( {'comments'            : 'Test Completed'} )

    targetParams.updateParams(testConfigDict)
    testConfigParams.updateParams(testConfigDict)
    revParams.updateParams(testConfigDict)

    createDebugLog(testConfigParams)
    createSubPlanLog(testConfigParams)
    debugPrint("=================== TEST START ===================")

    # load application on target and run
    target_functions.loadnRunTarget(testConfigParams.test_mode, targetParams, DUT_HarnessEnable.PhyEnable, targetParams.target_type)

    # check if DUT is ready to process the input
    DUT_functions.pollSystemReady()
    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)

    if testConfigParams.dut_operating_mode == 'RX':
        # Function call corresponding to operating mode RX
        test_mode_functions.executeOperatingMode_RX(testConfigParams, targetParams, revParams, cfgParamFromXls)
    elif testConfigParams.dut_operating_mode == 'TX':
        # Function call corresponding to operating mode TX
        test_mode_functions.executeOperatingMode_TX(testConfigParams, targetParams, revParams, cfgParamFromXls)
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

    # Argument parser
    parser = argparse.ArgumentParser()

    # Target type used used
    parser.add_argument(
        "--targetType", "-t",
        choices = ['Simulator'    ,
                   'SysProbe'    ],
        help    = "Target type. eg.",
        default = "Simulator"
    )

    # Target number
    parser.add_argument(
        "--targetNumber", "-n",
        help    = "Target number.",
        default = "rpusim-rpu530-main@172-internal_config0077"
    )

    # System Configuration
    parser.add_argument(
        "--systemConfiguration", "-s",
        choices = ['530_49',
                   '530_77'],
        help    = "System Configuration.\neg.",
        default = '530_77'
    )


    # Test mode used
    parser.add_argument(
        "--testMode", "-m",
        choices = ['PLAYOUT',
                   'RF'],
        help    = "Test mode",
        default = 'PLAYOUT'
    )

    # Target selection
    parser.add_argument(
        "--targetSelection", "-ts",
        choices = ['MCU'    ,
                   'MCU2'    ],
        help    = "Target Selection. eg.",
        default = 'MCU'
    )


    # Test plan type.
    parser.add_argument(
        "--testPlanType",
        choices = ['CHARACTERIZATION',
                   'Sanity'          ,
                   'Functional'      ,
                   'LATENCY'         ,
                   'HARDWARE'        ,
                   'REALTIME'        ,
                   'Gen2'            ,
                   'Per'             ],
        help    = "Test plan type.",
        default = 'Gen2'
    )


    # Sub functional test plan
    parser.add_argument(
        "--subfunctionalTestPlan",
        choices = ['ALL'                           ,
                   'LG'                            ,
                   'MM'                            ,
                   'VHT'                           ,
                   '11B'                           ,
                   'STBC'                          ,
                   'HESU'                          ,
                   'HEERSU'                        ,
                   'LDPC'                          ,
                   'NOISY'                         ,
                   'LDPC+SGI'                      ,
                   'CFO+SFO'                       ,
                   'AGG'                           ,
                   'SGI'                           ,
                   'PayLoad'                       ,
                   'OFDM+DSSS'                     ,
                   'HEPAYLOAD'                     ,
                   'HESTBC'                        ,
                   'HELDPC'                        ,
                   'HETB'                          ,
                   'HEMU'                          ,
                   'AGC'                           ,
                   'SECONDAGC'                     ,
                   'RADAR'                         ,
                   'Negative'                      ,
                   'PER'                           ,
                   'SENSITIVITY'                   ,
                   'SENSITIVITY_ACROSS_CHANNELS'   ,
                   'SNR'                           ,
                   'SNR_HE'                        ,
                   'EVM'                           ,
                   'RX_FUNCTIONAL'                 ,
                   'INTERFERENCE_DETECTION'        ,
                   'MIDPACKET_DETECTION'           ,
                   'ACI'                           ,
                   'AACI'                          ,
                   'RX_JAMMER'                     ,
                   'TX_SUBBAND'                    ,
                   'PER_HE'                        ,
                   'SENSITIVITY_HE'                ,
                   'EVM_HE'                        ,
                   'SJR'                           ,
                   'SJR_HE'                        ,
                   'SUBSET'                        ,
                   'CCA'                           ,
                   'CCADISC'                       ,
                   'CCACOMBINED'                   ,
                   'CFO+SFO-DSSS'                  ,
                   'CFO-SFO-PRE-COMP'             ],
        help    = "Subfunctional test paln.",
        default = 'LG'
    )


    # Test type
    parser.add_argument(
        "--testType",
        choices = ['RX'             ,
                   'TX'            ],
        help    = "Test Type",
        default = 'RX'
    )


    # equipment type
    parser.add_argument(
        "--equipment",
        choices = ['IQXEL_80'             ,
                   'IQXEL_280'            ,
                   'RnS'                 ],
        help    = "Test Type",
        default = 'IQXEL_80'
    )

    # equipment ip
    parser.add_argument(
        "--equipIp", "-ip",
        help    = "Equipment ip.",
        default = "10.90.2.15"
    )

    # Test all cases
    parser.add_argument('--testAllCases',
                        dest='testAllCases',
                        action='store_true')
    parser.add_argument('--no-testAllCases',
                        dest='testAllCases',
                        action='store_false')
    parser.set_defaults(testAllCases=True)

    # Config Params from Xlsx
    parser.add_argument('--cfgParamFromXls',
                        dest='cfgParamFromXls',
                        action='store_true')
    parser.add_argument('--no-cfgParamFromXls',
                        dest='cfgParamFromXls',
                        action='store_false')
    parser.set_defaults(cfgParamFromXls=True)


    # Test start
    parser.add_argument(
        "--testStartFrom",
        help    = "Test start from.",
        default = "1"
    )


    # Test End
    parser.add_argument(
        "--testEndAt",
        help    = "Test End at.",
        default = "1"
    )

    args = parser.parse_args()
    print(args)

    if (args.testAllCases):
        testAll = 'YES'
    else:
        testAll = 'NO'

    main(args.targetType,
         args.targetNumber,
         args.testMode,
         args.cfgParamFromXls,
         args.targetSelection,
         args.subfunctionalTestPlan,
         args.systemConfiguration,
         args.testPlanType,
         testAll,
         int(args.testStartFrom),
         int(args.testEndAt),
         args.testType,
         args.equipment,
         args.equipIp)

    # This sleep time is an attept to release the simulator before the
    # next test.
    time.sleep(20)
