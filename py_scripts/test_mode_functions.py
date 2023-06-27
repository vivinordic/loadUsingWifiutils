#-------------------------------------------------------------------------------
# Name:        test_mode_functions.py
# Purpose:
#
# Author:      Imagination Technologies
#
# Created:     17/04/2020
# Copyright:   (c) Imagination Technologies 2020
#-------------------------------------------------------------------------------
""" API's to cofigure and read dut parameters """

########################################
import file_operations
import DUT_functions
import playout_functions
import target_functions
import harness
import rxvector_functions
#import cca_functions
import pop_functions
import spatialReuse_functions

from harness import *

from tx_evm_power import tx_evm_power_analysis
from tx_evm_power_across_channels import tx_evm_power_analysis_across_channels
from tx_evm_power_across_datarates import tx_evm_power_analysis_across_datarates
from per import per_analysis
from sensitivity import sensitivity_analysis
from sensitivity_across_channels import sensitivity_analysis_across_channels
from rx_functional_testing import rx_analysis
from rx_negative_cases import rx_negative_analysis
from rx_jammer_cases import rx_jammer_analysis
from snr import snr_analysis
from tx_cfo_sfo import tx_cfo_sfo_analysis
from sjr import sjr_analysis
from aci import aci_analysis
from aaci import aaci_analysis
from pop import pop_analysis
from aci_detection import aciTestTop


from common_utils import *
from SOCKET_functions import *
#from MATLAB_functions import *
from mpdu_functions import formAmpduData
###########################################


def executeOperatingMode_RX(testConfigParams, targetParams, revParams, cfgParamFromXls):
    #====================================test_mode  RX PLAYOUT =====================================
    """ Configure for RX test mode """
    systemConfig = targetParams.system_config
    if (testConfigParams.test_mode == 'PLAYOUT'):
        RXresultsConsld = ResultsOut()
        RXresultsConsld.prepareXlsx('WLANPHY.RXfunctionalTestReport.xlsx')
        ResultSummary = ResultsOut()
        ResultSummary.prepareXlsx('RX_Summary_Consolidated.xlsx')
        heading1 = ['SubFuncTestPlan']
        RXresultsConsld.addRevSheet('REV')
        RXresultsConsld.addSummarySheet('Summary')
        rowNum = initializeSummarySheet(heading1, ResultSummary.worksheet, RXresultsConsld.worksheet1)
        passcount = 0
        failcount = 0
        if (testConfigParams.subFuncTestPlan == 'ALL'):
            simParamsheet = file_operations.readReportfile(systemConfig, targetParams, testConfigParams)
            file_operations.logRevSheet(revParams, simParamsheet, RXresultsConsld.revsheet, cfgParamFromXls)
            if (systemConfig == "530_77"):
                if (targetParams.target_type == 'SysProbe'):
                    subPlan = ['11B', 'LG', 'MM', 'VHT', 'SGI', 'PayLoad', 'STBC', 'OFDM+DSSS', 'HESU', 'HEERSU', 'HEPAYLOAD', 'HESTBC', 'HEMU', 'CFO+SFO', 'AGC', 'SECONDAGC', \
                    'POP', 'JAMMER', 'BEAMFORMEE', 'CCA', 'CCADISC', 'CCACOMBINED', 'FTM', 'SPATIAL-REUSE', 'HEMU20IN4080', 'ED-11K', 'RXLatency']
                else:
                    subPlan = ['11B', 'LG', 'MM', 'VHT', 'SGI', 'PayLoad', 'STBC', 'OFDM+DSSS', 'HESU', 'HEERSU', 'HEPAYLOAD', 'HESTBC', 'HEMU', 'CFO+SFO', 'AGC', 'SECONDAGC', \
                    'POP', 'JAMMER', 'BEAMFORMEE', 'HEMU20IN4080', 'ED-11K']
            elif (systemConfig == "610_79"):
                if (targetParams.target_type == 'SysProbe'):
                    subPlan = ['LDPC', 'LDPC+SGI', 'HELDPC', 'HEMU+LDPC', '11B', 'LG', 'MM', 'VHT', 'SGI', 'PayLoad', 'PayLoad+LDPC', 'HEPAYLOAD+LDPC', 'STBC', 'OFDM+DSSS', 'HESU', 'HEERSU', 'HEPAYLOAD', 'HESTBC', 'HEMU', 'CFO+SFO', 'AGC', 'SECONDAGC', \
                    'POP', 'JAMMER', 'BEAMFORMEE', 'CCA', 'CCADISC', 'CCACOMBINED', 'FTM', 'SPATIAL-REUSE', 'HEMU20IN4080', 'ED-11K', 'RXLatency']
                else:
                    subPlan = ['LDPC', 'LDPC+SGI', 'HELDPC', 'HEMU+LDPC', '11B', 'LG', 'MM', 'VHT', 'SGI', 'PayLoad', 'PayLoad+LDPC', 'HEPAYLOAD+LDPC', 'STBC', 'OFDM+DSSS', 'HESU', 'HEERSU', 'HEPAYLOAD', 'HESTBC', 'HEMU', 'CFO+SFO', 'AGC', 'SECONDAGC', \
                    'POP', 'JAMMER', 'BEAMFORMEE', 'HEMU20IN4080', 'ED-11K']
            for subTestPlan in subPlan:
                testConfigParams.subFuncTestPlan = subTestPlan
                # Initialize Socket
                sock, portNo = socket_init()
                DUT_functions.startTestcase()
                test_case_count, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
                # Start the Matlab process
                portNo = sock.getsockname()[1]
                MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
                #MtlbExeProcess = ''
                RXresultsConsld.addSheet(testConfigParams.subFuncTestPlan)
                passcount, failcount = executeRXPlayout(testConfigParams,sock,MtlbExeProcess, testCasesFile, sheetName, test_case_count, RXresultsConsld.worksheet, targetParams, passcount, failcount)
                conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
                conn.setblocking(1)
                conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
                file_operations.logSummaryResults(testConfigParams, rowNum, heading1, ResultSummary.worksheet, passcount, failcount, RXresultsConsld.worksheet1)
                rowNum = rowNum + 1
        else:
            # Initialize Socket
            sock, portNo = socket_init()
            #sock = ""
            DUT_functions.startTestcase()
            test_case_count, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
            # Start the Matlab process
            portNo = sock.getsockname()[1]
            MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
            #MtlbExeProcess = ''
            RXresultsConsld.addSheet(testConfigParams.subFuncTestPlan)
            passcount, failcount = executeRXPlayout(testConfigParams,sock,MtlbExeProcess, testCasesFile, sheetName, test_case_count, RXresultsConsld.worksheet, targetParams, passcount, failcount)
            conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
            conn.setblocking(1)
            conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
            file_operations.logSummaryResults(testConfigParams, rowNum, heading1, ResultSummary.worksheet, passcount, failcount, RXresultsConsld.worksheet1)
            rowNum = rowNum + 1
        ResultSummary.workbook.close()
        RXresultsConsld.workbook.close()
#PHY_PERFORMANCE
    #=======================================test_mode  RX RF =======================================
    elif (testConfigParams.test_mode == 'RF'):

        dut=Harness_SSH(targetParams.target)
        #dut=Harness_SSH("SysProbe 149") # PHY_PERFORMANCE - remove hardcoding
        if  (testConfigParams.test_type == 'CHARACTERIZATION'):
            sub_test_plans = testConfigParams.subFuncTestPlan.split(',')
            if (sub_test_plans[0] == 'ALL'):
                sub_test_plans = ['SENSITIVITY', 'SENSITIVITY_HE', 'SNR', 'SNR_HE', 'PER', 'PER_HE', 'RX_FUNCTIONAL', 'SENSITIVITY_ACROSS_CHANNELS', 'SENSITIVITY_ACROSS_CHANNELS_HE']
            elif (sub_test_plans[0] == 'SUBSET'):
                sub_test_plans = ['SENSITIVITY', 'SNR', 'SNR_HE', 'PER', 'SENSITIVITY_ACROSS_CHANNELS']
            if  ('PER' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'PER')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'PER')
                    if(testConfigParams.test_enable == 1):
                        per_analysis(testConfigParams,dut)
                    test_no +=1
                #dut_run_per_test_with_vsg(testConfigParams)
            if  ('PER_LDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'PER_LDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'PER_LDPC')
                    if(testConfigParams.test_enable == 1):
                        per_analysis(testConfigParams,dut)
                    test_no +=1
            if  ('PER_HE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'PER_HE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'PER_HE')
                    if(testConfigParams.test_enable == 1):
                        per_analysis(testConfigParams,dut)
                    test_no +=1
            if  ('PER_HELDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'PER_HELDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'PER_HELDPC')
                    if(testConfigParams.test_enable == 1):
                        per_analysis(testConfigParams,dut)
                    test_no +=1
            if('SNR' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SNR')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SNR')
                    if(testConfigParams.test_enable == 1):
                        snr_analysis(testConfigParams,dut)
                    test_no +=1
            if('SNR_LDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SNR_LDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SNR_LDPC')
                    if(testConfigParams.test_enable == 1):
                        snr_analysis(testConfigParams,dut)
                    test_no +=1
            if('SNR_HE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SNR_HE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SNR_HE')
                    if(testConfigParams.test_enable == 1):
                        snr_analysis(testConfigParams,dut)
                    test_no +=1
            if('SNR_HELDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SNR_HELDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SNR_HELDPC')
                    if(testConfigParams.test_enable == 1):
                        snr_analysis(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITY' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITY')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITY')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITY_LDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITY_LDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITY_LDPC')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITY_HE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITY_HE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITY_HE')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITY_HELDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITY_HELDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITY_HELDPC')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITY_ACROSS_CHANNELS' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITY_ACROSS_CHANNELS')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITY_ACROSS_CHANNELS')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis_across_channels(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITYACROSSCHANNELS_LDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITYACROSSCHANNELS_LDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITYACROSSCHANNELS_LDPC')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis_across_channels(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITY_ACROSS_CHANNELS_HE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITY_ACROSS_CHANNELS_HE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITY_ACROSS_CHANNELS_HE')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis_across_channels(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITYACROSCHANNELS_HELDPC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITYACROSCHANNELS_HELDPC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITYACROSCHANNELS_HELDPC')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_analysis_across_channels(testConfigParams,dut)
                    test_no +=1
            if('SENSITIVITY_MAXPOWER' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SENSITIVITY_MAXPOWER')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SENSITIVITY_MAXPOWER')
                    if(testConfigParams.test_enable == 1):
                        sensitivity_maxpower_analysis(testConfigParams,dut)
                    test_no +=1
            if('AGC' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'AGC')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'AGC')
                    if(testConfigParams.test_enable == 1):
                        agc_gain_analysis(testConfigParams,dut)
                    test_no +=1
            if('ACI' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'ACI')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'ACI')
                    if(testConfigParams.test_enable == 1):
                        aci_analysis(testConfigParams,dut)
                    test_no +=1
            if('ACI_HE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'ACI_HE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'ACI_HE')
                    if(testConfigParams.test_enable == 1):
                        aci_analysis(testConfigParams,dut)
                    test_no +=1
            if('INTERFERENCE_DETECTION' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'INTERFERENCE_DETECTION')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'INTERFERENCE_DETECTION')
                    if(testConfigParams.test_enable == 1):
                        aciTestTop(testConfigParams,dut)
                    test_no +=1
            if('AACI' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'AACI')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'AACI')
                    if(testConfigParams.test_enable == 1):
                        aaci_analysis(testConfigParams,dut)
                    test_no +=1
            if('AACI_HE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'AACI_HE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'AACI_HE')
                    if(testConfigParams.test_enable == 1):
                        aaci_analysis(testConfigParams,dut)
                    test_no +=1
            if('MIDPACKET_DETECTION' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'MIDPACKET_DETECTION')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'MIDPACKET_DETECTION')
                    if(testConfigParams.test_enable == 1):
                        midPktTestTop(testConfigParams,dut)
                    test_no +=1
            if('RX_FUNCTIONAL' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'RX_FUNCTIONAL')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'RX_FUNCTIONAL') # RX_FUNCTIONAL
                    if(testConfigParams.test_enable == 1):
                        rx_analysis(testConfigParams,dut,test_no)
                    test_no +=1
            if('RX_NEGATIVE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'RX_NEGATIVE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'RX_NEGATIVE')
                    if(testConfigParams.test_enable == 1):
                        rx_negative_analysis(testConfigParams,dut,test_no)
                    test_no +=1
            if('RX_JAMMER' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'RX_JAMMER')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.getJammerTestParams(testConfigParams,test_no)
                    if(testConfigParams.test_enable == 1):
                        rx_jammer_analysis(testConfigParams,dut)
                    test_no +=1
            if('SJR' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SJR')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SJR')
                    if(testConfigParams.test_enable == 1):
                        sjr_analysis(testConfigParams,dut)
                    test_no +=1
            if('SJR_HE' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'SJR_HE')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'SJR_HE')
                    if(testConfigParams.test_enable == 1):
                        sjr_analysis(testConfigParams,dut)
                    test_no +=1
            if  ('POP' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'POP')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'POP')
                    if(testConfigParams.test_enable == 1):
                        pop_analysis(testConfigParams,dut)
                    test_no +=1
            if  ('MULTIPATH' in sub_test_plans):
                file_operations.setTestDirectory(testConfigParams,'MULTIPATH')
                test_no = testConfigParams.test_case_start
                while (test_no <= testConfigParams.total_test_cases ):
                    file_operations.setTestConfigFromDict(testConfigParams,test_no,'MULTIPATH')
                    if(testConfigParams.test_enable == 1):
                        #multipath_analysis(testConfigParams,dut)
                        per_analysis(testConfigParams,dut)
                        testConfigParams.start_amplt = -50
                        testConfigParams.end_amplt = -90
                        testConfigParams.step_size = 20
                        sensitivity_analysis(testConfigParams,dut)
                    test_no +=1
        # elif(testConfigParams.test_type == 'FUNCTIONAL'):
        #     dut_run_rx_functional_test_with_vsg(testConfigParams)
        elif(testConfigParams.test_type == 'CAPTURE'):
            get_rx_debug_captures(testConfigParams)
        elif(testConfigParams.test_type == 'NOISE CAPTURE'):
            dut_get_noise_captures(testConfigParams)
        #elif(testConfigParams.test_type == 'ADC OUT CAPTURE'):
        #    dut_get_adc_out_captures_for_rf(testConfigParams)
        #dut.dut_close()
    elif(testConfigParams.test_mode == 'BASEBAND'):
        dut_bb_analysis(equipment, testConfigParams)
        dut_get_adc_out_captures_for_bb(equipment, testConfigParams)
        equipment.close_vsg()
        #dut.dut_close()
    else:
        DebugPrint('Wrong Test Mode given. Please choose from RF / BASEBAND / MEMCPY /SCP DEBUGIQ testing')
        exit(-1)

def executeOperatingMode_TX(testConfigParams, targetParams, revParams, cfgParamFromXls):
    # ==================================test_mode = TX PLAYOUT======================================
    """ Configure for TX test mode """
    systemConfig = targetParams.system_config
    if (testConfigParams.test_mode == 'PLAYOUT'):
##        # Create test cases excel sheets
##        testCasesFilesList = Generate_testcases(testConfigParams, sock)
        TXresultsConsld = ResultsOut()
        TXresultsConsld.prepareXlsx('WLANPHY.TXfunctionalTestReport.xlsx')
        ResultSummary = ResultsOut()
        ResultSummary.prepareXlsx('TX_Summary_Consolidated.xlsx')
        heading1 = ['SubFuncTestPlan']
        TXresultsConsld.addRevSheet('REV')
        TXresultsConsld.addSummarySheet('Summary')
        rowNum = initializeSummarySheet(heading1, ResultSummary.worksheet, TXresultsConsld.worksheet1)
        PassCount = 0
        FailCount = 0
        if (testConfigParams.subFuncTestPlan == 'ALL'):
            simParamsheet = file_operations.readReportfile(systemConfig, targetParams, testConfigParams)
            file_operations.logRevSheet(revParams, simParamsheet, TXresultsConsld.revsheet, cfgParamFromXls)
            if (systemConfig == "530_77"):
                subPlan = ['11B', 'LG', 'MM', 'VHT', 'SGI', 'PayLoad', 'AGG', 'OFDM+DSSS', 'HESU', 'HEERSU', 'HEPAYLOAD', 'HETB', 'CFO-SFO-PRE-COMP', 'HETB-SUBBAND', 'HETBPAYLOAD']
            elif (systemConfig == "610_79"):
                subPlan = ['11B', 'LG', 'MM', 'VHT', 'LDPC', 'SGI', 'LDPC+SGI', 'PayLoad', 'PayLoad+LDPC', 'HEPAYLOAD+LDPC', 'AGG', 'OFDM+DSSS', 'HESU', 'HEERSU', 'HEPAYLOAD', 'HETB', 'HELDPC', 'HETB+LDPC', 'CFO-SFO-PRE-COMP', 'HETB-SUBBAND', 'HETBPAYLOAD', 'HETBPAYLOAD+LDPC']
            for subTestPlan in subPlan:
                # Initialize Socket
                sock, portNo = socket_init()
                portNo = sock.getsockname()[1]
                testConfigParams.subFuncTestPlan = subTestPlan
                test_case_count, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
                MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
                # Start the Matlab process
                #MtlbExeProcess = ''
                TXresultsConsld.addSheet(subTestPlan)
                PassCount, FailCount = executeTXCapture(testConfigParams, sock, MtlbExeProcess, testCasesFile, sheetName, test_case_count, targetParams, TXresultsConsld.worksheet, PassCount, FailCount)
                conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
                conn.setblocking(1)
                conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
                file_operations.logSummaryResults(testConfigParams, rowNum, heading1, ResultSummary.worksheet, PassCount, FailCount, TXresultsConsld.worksheet1)
                rowNum = rowNum + 1
        else:
            # Initialize Socket
            sock, portNo = socket_init()
            portNo = sock.getsockname()[1]
            test_case_count, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
            MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, systemConfig)
            # Start the Matlab process
            #MtlbExeProcess = ''
            TXresultsConsld.addSheet(testConfigParams.subFuncTestPlan)
            PassCount, FailCount = executeTXCapture(testConfigParams, sock, MtlbExeProcess, testCasesFile, sheetName, test_case_count, targetParams, TXresultsConsld.worksheet, PassCount, FailCount)
            conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
            conn.setblocking(1)
            conn.send(str(Constants.get('TEST_COMPLETED')[0][0]))#Give indication from python to MATLAB to start the test case
            file_operations.logSummaryResults(testConfigParams, rowNum, heading1, ResultSummary.worksheet, PassCount, FailCount, TXresultsConsld.worksheet1)
            rowNum = rowNum + 1
        ResultSummary.workbook.close()
        TXresultsConsld.workbook.close()
#PHY_PERFORMANCE
    # =====================================test mode TX RF========================================

    elif (testConfigParams.test_mode == 'RF'):

        dut=Harness_SSH(targetParams.target)

        test_plans = testConfigParams.subFuncTestPlan.split(',')
        if (test_plans[0] == 'ALL'):
            test_plans = ['EVM', 'EVM_HE']
        #dut_operating_mode_TX_testmode_RF(testConfigParams,sock,MtlbExeProcess, timeout,test_cases_count,test_cases_file)
        if ('EVM' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'EVM')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'EVM')
                if(testConfigParams.test_enable == 1):
                    #-----------------------------------------
                    testConfigParams.status = 'TX_EVM_TESTING'
                    tx_evm_power_analysis(testConfigParams,dut)
                    exit(0)
                    #-----------------------------------------
                test_no +=1
                # In case DUT process haven't completed succesfuly reload executable before starting next case
                if (testConfigParams.status == 'TX_EVM_ERROR'):
                    test_no -=1
                    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
                    DUT_functions.pollSystemReady()
                    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
        if ('EVM_LDPC' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'EVM_LDPC')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'EVM_LDPC')
                if(testConfigParams.test_enable == 1):
                    #-----------------------------------------
                    testConfigParams.status = 'TX_EVM_TESTING'
                    tx_evm_power_analysis(testConfigParams,dut)
                    #-----------------------------------------
                test_no +=1
                # In case DUT process haven't completed succesfuly reload executable before starting next case
                if (testConfigParams.status == 'TX_EVM_ERROR'):
                    test_no -=1
                    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
                    DUT_functions.pollSystemReady()
                    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
        if ('EVM_HE' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'EVM_HE')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'EVM_HE')
                if(testConfigParams.test_enable == 1):
                    #-----------------------------------------
                    testConfigParams.status = 'TX_EVM_TESTING'
                    tx_evm_power_analysis(testConfigParams,dut)
                    #-----------------------------------------
                test_no +=1
                # In case DUT process haven't completed succesfuly reload executable before starting next case
                if (testConfigParams.status == 'TX_EVM_ERROR'):
                    test_no -=1
                    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
                    DUT_functions.pollSystemReady()
                    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
        if ('EVM_HELDPC' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'EVM_HELDPC')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'EVM_HELDPC')
                if(testConfigParams.test_enable == 1):
                    #-----------------------------------------
                    testConfigParams.status = 'TX_EVM_TESTING'
                    tx_evm_power_analysis(testConfigParams,dut)
                    #-----------------------------------------
                test_no +=1
                # In case DUT process haven't completed succesfuly reload executable before starting next case
                if (testConfigParams.status == 'TX_EVM_ERROR'):
                    test_no -=1
                    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
                    DUT_functions.pollSystemReady()
                    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
        if ('TX_CFO_SFO' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'TX_CFO_SFO')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'TX_CFO_SFO')
                if(testConfigParams.test_enable == 1):
                    #-----------------------------------------
                    testConfigParams.status = 'TX_EVM_TESTING'
                    tx_cfo_sfo_analysis(testConfigParams,dut)
                    #-----------------------------------------
                test_no +=1


        if ('TX_SUBBAND' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'TX_SUBBAND')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'TX_SUBBAND')
                if(testConfigParams.test_enable == 1):
                    tx_evm_power_analysis(testConfigParams,dut)
                test_no +=1
        elif ('EVM_ACROSS_CHANNELS' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'EVM_ACROSS_CHANNELS')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'EVM_ACROSS_CHANNELS')
                if(testConfigParams.test_enable == 1):
                    tx_evm_power_analysis_across_channels(testConfigParams,dut)
                test_no +=1
        elif ('EVM_ACROSS_DATARATES' in test_plans):
            file_operations.setTestDirectory(testConfigParams,'EVM_ACROSS_DATARATES')
            test_no = testConfigParams.test_case_start
            while (test_no <= testConfigParams.total_test_cases ):
                file_operations.setTestConfigFromDict(testConfigParams,test_no,'EVM_ACROSS_DATARATES')
                if(testConfigParams.test_enable == 1):
                    tx_evm_power_analysis_across_datarates(testConfigParams,dut)
                test_no +=1
    else:
        DebugPrint('Wrong Test Mode given. Please choose from RF / BASEBAND / MEMCPY /SCP DEBUGIQ testing')
        exit(-1)

def executeOperatingMode_LOOPBACK(testConfigParams, targetParams):
    """ Configure for LOOPBACK test mode """
    systemConfig = targetParams.system_config
    if (testConfigParams.test_mode == 'PLAYOUT'):
        DUT_functions.startTestcase()
        test_case_count, testCasesFile, sheetName = file_operations.computeNumTestcases(testConfigParams, systemConfig)
        rowNum = 2

        if (testConfigParams.lna_model_enable == 'NO'):
            memoryType = 'shared'
        else:
            memoryType = 'separate'

        while (test_case_count <= testConfigParams.total_test_cases):
            systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, test_case_count)
            ##TX initialization
            print(testParams)
            txParams = TxParams()
            txParams.updateParams(testParams)
            payloadFile="mpdu_payload.txt"
            vectorDumpDir = file_operations.returnSimOutDir (testConfigParams, test_case_count)
            if ('aggregationEnable' in testParams.keys()):
                mpdu_data = file_operations.generatePayload(testParams['packetLength'] - 4) # 4 CRC bytes are deducted
                file_operations.writePayloadToFile (mpdu_data,payloadFile,testParams['packetLength'] - 4, testParams['nMpdu'], vectorDumpDir)
            else:
                mpdu_data = file_operations.generatePayload(testParams['packetLength'] - 4) # 4 CRC bytes are deducted
                file_operations.writePayloadToFile (mpdu_data,payloadFile,testParams['packetLength'] - 4, 1, vectorDumpDir)
            data_bytes_out = []
            formAmpduData(txParams, data_bytes_out, mpdu_data)
            #print(data_bytes_out)
            DUT_functions.feedPayload(data_bytes_out)
            DUT_functions.configSystemParams(systemParams)
            DUT_functions.enableRetune()
            DUT_functions.clearTestDoneIndication()
            DUT_functions.configTXParams(testParams)
            DUT_functions.updateTXParams()
            # Configure clock dividers
            playout_functions.configClock()
            playout_functions.configTXCapture()
            samples2Read = 0x2000000
            playout_functions.startCapture(samples2Read)
            ##TX Start
            DUT_functions.startNextCase()
            ##Wait for TX DUT done
            state = DUT_functions.wait4DutDone(120)
            samples2Read = playout_functions.getNumSamplesCaptured()
            outBuffer = playout_functions.readCaptureMemory(samples2Read)
            file_operations.dumpTXOutSamples(outBuffer, samples2Read, testConfigParams)
            ## Start RX
            DUT_functions.setPayloadLengthRx(testParams['packetLength'])
            DUT_functions. setFrameFormatRx(testParams['format'])
            DUT_functions.setRXInputLength(samples2Read)
            ## Wait for RX configuration
            DUT_functions.pollTestReady(60)
            playout_functions.configRXPlayout(testConfigParams.lna_model_enable)
            inputSamples = adjustSamples(outBuffer, memoryType)
            playout_functions.writeSamplesPlayout(inputSamples, samples2Read+2000, memoryType)
            playout_functions.pollPlayoutDone()
            DUT_functions.indicatePlayoutDone()
            time.sleep(3)
            ## Wait for RX DUT done
            state = DUT_functions.wait4DutDone(120)
            pktStatus, edStatus, popCnt, spatialReuseCnt = DUT_functions.getRXStats()
            debugPrint('Packet status is ' + pktStatus)
            debugPrint('ED status is ' + edStatus)
            if (test_case_count == testConfigParams.test_case_start):
                resultsConsld = ResultsOut()
                resultsConsld.prepareXlsx('LB_Sanity_Results_Consolidated.xlsx')
                heading = keyParams
                heading += ['Status']
                resultsConsld.worksheet.write_row('A1', heading)
            file_operations.logRxResults(testParams, pktStatus, resultsConsld, rowNum, heading, resultsConsld.worksheet)
            rowNum += 1
            if (test_case_count == testConfigParams.total_test_cases):
                resultsConsld.workbook.close()
##            DA.SelectTargetByPattern('MCU')
##            target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
##            DUT_functions.pollSystemReady()
##            DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
##            DUT_functions.startTestcase()
            DUT_functions.clearRxStats()
            test_case_count = test_case_count + 1

def executeOperatingMode_FEED(testConfigParams):
    if (testConfigParams.test_mode == 'PLAYOUT'):
        DUT_functions.startTestcase()
        #mpdu_data = file_operations.generatePayload(4096, 1)
        data = [0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff] *256
        DUT_functions.feedPayload(data)
        # Configure clock dividers
        playout_functions.configClock()
        playout_functions.configTXCapture()
        samples2Read = 0x2000000
        playout_functions.startCapture(samples2Read)
        feedParams = [len(data), 1024, 1]
        DUT_functions.configFeedParams(feedParams)
        DUT_functions.bypassRxscp('BYPASS')
        DUT_functions.clearTestDoneIndication()
        DUT_functions.startNextCase()
        DUT_functions.pollTestReady(60)
    ##    DUT_functions.exitFeed()
    ##    time.sleep(3)
        state = DUT_functions.wait4DutDone(120)
        #debugPrint("DUT done state is " + str(state))
        samples2Read = playout_functions.getNumSamplesCaptured()
        debugPrint(samples2Read)
        outBuffer = playout_functions.readCaptureMemory(samples2Read)
        file_operations.dumpFeedSamples(outBuffer, samples2Read)
    else:
        channel = input('Enter channel')
        DUT_functions.setChannel(channel)
        DUT_functions.startTestcase()

        # Setting TXSCP in bypass mode
        DUT_functions.bypassTxscp('BYPASS') # BYPASS or NORMAL

        file_real = 'adc1OutputReal.txt'
        file_imag = 'adc1OutputImag.txt'
        # Reading input samples
        feedSamples1, numSamples1 = file_operations.readRXSamples(file_real, file_imag, 'shared')
        opBW = 0 # 20MHz
        silenceTime = 25 # in us
        feedSamples,numSamples = file_operations.addSilence(opBW, silenceTime, feedSamples1, 'shared')


        feedParams = [numSamples, numSamples, 0] # input length, period length, repeat count

        # Configure Feed sample length, Period length and repeat count
        DUT_functions.configFeedParams(feedParams)

        txPower = 1 # EVM drops for high txPower
        mtp_address = DA.EvaluateSymbol('&feed_signal_params.txPower')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, txPower, DUT_MemoryTypes.Default)

        # To manipulate gainI and gainQ uncomment the following lines

##        mtp_address = DA.EvaluateSymbol('&feed_signal_params.sinGenParams.gainI')
##        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 0x100, DUT_MemoryTypes.Default)
##
##        mtp_address = DA.EvaluateSymbol('&feed_signal_params.sinGenParams.gainQ')
##        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 0x100, DUT_MemoryTypes.Default)

        DUT_functions.startNextCase()
        time.sleep(5)
        #mtp_address = 0xb500aab0
        mtp_address = DA.EvaluateSymbol('edc_buffer_tx_payload.addr32')
        DA.WriteMemoryBlock(mtp_address, numSamples, DUT_ElementTypes.typeUnsigned32bit, feedSamples, DUT_MemoryTypes.Default)

        pass

def executeOperatingMode_CAPTURE(testConfigParams):

    if (testConfigParams.test_mode == 'PLAYOUT'):
        DUT_functions.startTestcase()
        memoryType = 'shared'
        # Configure clock dividers
        playout_functions.configClock()
        playout_functions.configRXPlayout(testConfigParams.lna_model_enable)
        #inputSamples,numSamples = file_operations.readRXSamples(testConfigParams, memoryType)
        mpdu_data = [0x00000000, 0x11001100, 0x22002200, 0x33003300, 0x44004400, 0x55005500, 0x66006600, 0x77007700, 0x88008800, 0x99009900, 0xaa00aa00, 0xbb00bb00, 0xcc00cc00, 0xdd00dd00, 0xee00ee00, 0xff00ff00] *256
        numSamples = len(mpdu_data)
        DUT_functions.startNextCase()
        DUT_functions.pollTestReady(60)
        playout_functions.writeSamplesPlayout(mpdu_data, numSamples, memoryType)
        playout_functions.pollPlayoutDone()
        payloadBuff = DUT_functions.readRxPayloadBuffer(numSamples*3)
        file_operations.save2textFile(payloadBuff, 1)
    else:
        channel = input('Enter channel')
        DUT_functions.setChannel(channel)
        DUT_functions.startTestcase()

        mode = input('Enter SCP mode 0 for BYPASS_MODE & 1 for NORMAL_MODE')
        mtp_address = DA.EvaluateSymbol('&capture_signal_params.blockControl')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, mode, DUT_MemoryTypes.Default)

        numSamples = input('Enter capture length. Should be less than 12000')
        mtp_address = DA.EvaluateSymbol('&capture_signal_params.inputLength')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, numSamples, DUT_MemoryTypes.Default)

        idx = 1
        nCapture = 5
##        while (nCapture > 1):
        while (1):

            cond = raw_input('Start Capture (y/n) ')
            if (cond.lower() == 'n'):
                break
            DUT_functions.startNextCase()

            time.sleep(10)

            valuePtr = DA.EvaluateSymbol('buffer_address_gram')
            print(valuePtr)
            payloadBuff = DUT_functions.readRxPayloadBuffer(numSamples*3)
            file_operations.save2textFile(payloadBuff, idx)
            idx += 1
            nCapture -= 1
    pass

def executeRXPlayout(testConfigParams, sock, MtlbExeProcess, testCasesFile, sheetName, test_case_count, sheet, targetParams, passcount, failcount):
    """ Run RX playout test case """

    # test cases loop
    pkt_idx = 1 # To support for multiple packets
    snr_idx = 1
    passcount = 0
    failcount = 0
    while (test_case_count <= testConfigParams.total_test_cases):
        try:
            systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, test_case_count)
           # caseparams, heading=file_operations.readMatlabXlsx(testCasesFile, testConfigParams.subFuncTestPlan, test_case_count)
            caseparams, caseDict, heading=file_operations.readMatlabXlsx(testCasesFile, testConfigParams.subFuncTestPlan, test_case_count)
            DUT_functions.configSystemParams(systemParams)
            if (testConfigParams.subFuncTestPlan == 'SPATIAL-REUSE'):
                DUT_functions.configureSpatialReuseDUT(caseparams, heading)
            payloadFile = "mpdu_payload.txt"
            vectorDumpDir = file_operations.returnSimOutDir (testConfigParams, test_case_count)
            # If payloadParam comes as string from excel sheet, will convert
            # into an integer array and find maximum value to generate
            # "mpdu_payload.txt" file.
            payLoadParam = testParams ['packetLength']
            if type(payLoadParam) == unicode:
                payloadLens = []
                payLoadArr = payLoadParam.split('  ')
                for iVal in range(len(payLoadArr)):
                    payloadLen = int(payLoadArr[iVal])
                    payloadLens.append(payloadLen)
                testParams ['packetLength'] = max(payloadLens)
            if ('aggregationEnable' in testParams.keys()):
                mpdu_data = file_operations.generatePayload(testParams ['packetLength'] - 4) # 4 CRC bytes are deducted
                file_operations.writePayloadToFile (mpdu_data, payloadFile, testParams ['packetLength'] - 4,testParams['nMpdu'], vectorDumpDir)
            else:
                mpdu_data = file_operations.generatePayload(testParams ['packetLength'] - 4) # 4 CRC bytes are deducted
                file_operations.writePayloadToFile (mpdu_data,payloadFile,testParams ['packetLength'] - 4, 1,vectorDumpDir)
            lnaEnableTestPlans = ['AGC', 'SECONDAGC', 'CCA', 'CCADISC', 'ED-11K', 'CCACOMBINED', 'JAMMER', 'POP', \
                                  'BEAMFORMEE', 'FTM', 'SPATIAL-REUSE', 'RXLatency']

            if(testConfigParams.subFuncTestPlan is testConfigParams.subFuncTestPlan in lnaEnableTestPlans):
                memoryType = 'separate'
                DUT_functions.agcModuleEnable()
                testConfigParams.lna_model_enable = 'YES'
                agcEn  = 1
            else:
                memoryType = 'shared'
                DUT_functions.agcModuleDisbale()
                testConfigParams.lna_model_enable = 'NO'
                agcEn  = 0

            if(testConfigParams.subFuncTestPlan == 'BEAMFORMEE'):
                DUT_functions.svdModuleEnable()
            else:
                DUT_functions.svdModuleDisbale()

            if(testConfigParams.subFuncTestPlan == 'ED-11K'):
                DUT_functions.configNhParams(caseparams[13], caseparams[14], caseparams[15])

            DUT_functions. setPayloadLengthRx(testParams['packetLength'])
            #DUT_functions. setFrameFormatRx(testParams['format'])
            #Palyout Input selection bit has to set before time counter enable
            playout_functions.configRXPlayoutInputSel()
            if(testConfigParams.subFuncTestPlan == 'CCACOMBINED'):
                dutState = runRxCombinedPacket(test_case_count, pkt_idx, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType, vectorDumpDir, agcEn, caseDict)
            else:
                Matlab_input = 'testcaseIdx' + ' ' + str(test_case_count) + ' ' + 'pktIdx' + ' ' + str(pkt_idx) + ' ' + 'firmwareAgcTestEn' + ' ' + str(agcEn)
                dutState = runRxSinglePacket(Matlab_input, test_case_count, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType, vectorDumpDir, caseDict)

            if(dutState == 'CCA_BREAK'):
                if (test_case_count == testConfigParams.test_case_start) :
                    resultsConsld, rowNum = initializeExcelSheet(heading, sheet, testConfigParams)
                test_case_count = test_case_count+1
                continue

            elif(dutState == 'MATLAB_STUCK'):
                KillSubProcess(MtlbExeProcess)
                portNo = sock.getsockname()[1]
                MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, targetParams.system_config)
                pktStatus = 'NA'
                edStatus1 = 'NA'
                matlabresult = 'MATLAB STUCK'

            else:
                DUT_RxVector = RxVector()
                rx_aidorstaId = rxvector_functions.readRxVector (systemParams, DUT_RxVector, testConfigParams, test_case_count)
                matDict = rxvector_functions.readMatRxVectorasDict (systemParams, testConfigParams, test_case_count, DUT_RxVector)

                pktStatus, edStatus, popCnt, spatialReuseCnt = DUT_functions.getRXStats()
                coreClkFreq = 80.0 #MHz
                pktDuration = DUT_functions.computePktDuration()
                RXLatency = DUT_functions.computeRXLatency(coreClkFreq)
                debugPrint('Packet status is ' + pktStatus)
                if(edStatus > 0):
                    edStatus1= 'ED detected'
                else:
                    edStatus1= 'ED not detected'

                debugPrint('ED status is ' + edStatus1)

                matlabcrc = readMatlabStatus(testConfigParams, test_case_count, 0)
                if (matlabcrc == 1):
                    matlabresult = 'CRC PASS'
                else:
                    matlabresult = 'CRC FAIL'

                if(testConfigParams.subFuncTestPlan == 'CCA') or (testConfigParams.subFuncTestPlan == 'CCADISC') or (testConfigParams.subFuncTestPlan == 'CCACOMBINED'):
                    formatType = caseparams [heading.index('format')]
                    corruptionType = caseparams [heading.index('corruptionType')]
                    coreClkCyclesperUs = 80
                    adcSamplingrate = 40 << testParams['opBW']
                    [rssiEstimated, ccaDuration, txTimeCalculated, sigStatus, ofdmCorrelaionCnt, formatTypeStr] = cca_functions.readCCAParams(testParams, testConfigParams, vectorDumpDir, memoryType, DUT_RxVector, coreClkCyclesperUs, adcSamplingrate, formatType, corruptionType)
                elif (testConfigParams.subFuncTestPlan == 'POP'):
                    coreClkCyclesperUs = 80
                    adcSamplingrate = 40 << testParams['opBW']
                    [ccaDuration, txTimeCalculated, popStatus, finalStatus] = pop_functions.readPopParams(testConfigParams, vectorDumpDir, memoryType, coreClkCyclesperUs, adcSamplingrate, popCnt, caseparams)

            if (test_case_count == testConfigParams.test_case_start) :
                resultsConsld, rowNum = initializeExcelSheet(heading, sheet, testConfigParams)

            if(testConfigParams.subFuncTestPlan == 'AGC'):
                diff = int(DUT_RxVector.estGain) - int(matDict['estGainDb'])
                if diff >= -2 and diff <= 2:
                    agcstatus = 'PASS'
                    passcount = passcount + 1
                else:
                    agcstatus = 'FAIL'
                    failcount = failcount + 1
                status = [pktStatus, matlabresult, edStatus1, RXLatency, DUT_RxVector.rssi, DUT_RxVector.mappedGain, DUT_RxVector.estGain,  matDict['mappedGainDb'], matDict['estGainDb'], agcstatus]
            elif(testConfigParams.subFuncTestPlan == 'SECONDAGC'):
                diff = int(DUT_RxVector.estGain2) - int(matDict['estGainDb2'])
                if diff >= -2 and diff <= 2:
                    agcstatus2 = 'PASS'
                    passcount = passcount + 1
                else:
                    agcstatus2 = 'FAIL'
                    failcount = failcount + 1
                secondAgcStatus = DUT_functions.secondAgcStatus()
                status = [pktStatus, matlabresult, edStatus1, RXLatency, DUT_RxVector.rssi, DUT_RxVector.mappedGain, DUT_RxVector.estGain, DUT_RxVector.estGain2, secondAgcStatus, matDict['mappedGainDb'], matDict['estGainDb'], matDict['estGainDb2'], agcstatus2]
            elif(testConfigParams.subFuncTestPlan == 'CCA') or (testConfigParams.subFuncTestPlan == 'CCADISC') or (testConfigParams.subFuncTestPlan == 'CCACOMBINED'):
                #Determine Pass or fail and Log results to excel sheet
                resultStatus = cca_functions.determinePassorFail(formatType, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus, corruptionType)
                if resultStatus == 'pass':
                    passcount += 1
                else:
                    failcount += 1
                status = [pktStatus, matlabresult, edStatus1, RXLatency, ofdmCorrelaionCnt, rssiEstimated, ccaDuration, txTimeCalculated, sigStatus, resultStatus]
            elif(testConfigParams.subFuncTestPlan == 'ED-11K'):
                nhAccumVal = DUT_functions.getNhAccumVal()
                nhAccumCnt = DUT_functions.getNhAccumCnt()
                anpiEstdBm = DUT_functions.getAnpiEstdBm(nhAccumVal, nhAccumCnt)
                matNhOutput = file_operations.dumpMatNhOutput()
                diff = int(nhAccumCnt) - int(matNhOutput[2])
                if diff >= -100 and diff <= 100:
                    finalstatus = 'Pass'
                    passcount += 1
                else:
                    finalstatus = 'Fail'
                    failcount += 1
                status = [pktStatus, matlabresult, edStatus1, RXLatency, DUT_RxVector.rssi, nhAccumVal, matNhOutput[1], nhAccumCnt, matNhOutput[2], anpiEstdBm, matNhOutput[0], finalstatus]
            elif(testConfigParams.subFuncTestPlan == 'CFO+SFO') or (testConfigParams.subFuncTestPlan == 'CFO+SFO-DSSS'):
                dutCfo, matCfo = DUT_functions.getCfoInKHz(DUT_RxVector.cfo, int(matDict['estCfo']), testParams['operatingBand'], testParams['channelNum'], caseDict['format'])
                DUT_functions.getCfoInKHz(DUT_RxVector.cfo, int(matDict['estCfo']), testParams['operatingBand'], testParams['channelNum'], caseDict['format'])
                cfoStatus = DUT_functions.getCfoStatus(dutCfo , caseparams[9])
                if(cfoStatus == 1):
                    cfoStatus1 = "PASS"
                    passcount += 1
                else:
                    cfoStatus1 = "FAIL"
                    failcount += 1
                status = [pktStatus, matlabresult, edStatus1, RXLatency ,dutCfo, matCfo, cfoStatus1 ]

            elif(testConfigParams.subFuncTestPlan == 'JAMMER'):
                sigStatus, correlationCnt, leeCount = DUT_functions.readOtherFailCnt()
                s2lcount = DUT_functions.readS2LFailCnt()
                jammerStatus= rxvector_functions.determineJammerPassorFail(caseparams, heading, pktStatus, s2lcount, leeCount)
                if jammerStatus == 'JAMMER_PASS':
                    passcount = passcount + 1
                else:
                    failcount = failcount + 1
                status = [pktStatus, matlabresult, edStatus1, RXLatency, correlationCnt, sigStatus, s2lcount, leeCount, jammerStatus]
            elif(testConfigParams.subFuncTestPlan == 'POP'):
                if finalStatus == 'PASS':
                    passcount = passcount + 1
                else:
                    failcount = failcount + 1
                status = [pktStatus, matlabresult, edStatus,  RXLatency, DUT_RxVector.rssi, ccaDuration, txTimeCalculated, popStatus, finalStatus]
            elif(testConfigParams.subFuncTestPlan == 'BEAMFORMEE'):
                svdoutBuffer, svdDMAlength = DUT_functions.readsvdOutBuffer()
                svdOutFileName = "svd_output.txt"
                file_operations.dumpDutSVDoutput(svdoutBuffer, svdDMAlength, svdOutFileName)
                matoutBuffer= file_operations.dumpMatSVDoutput()
                ## To compare between matlab svd output and dut svd output with unpacking data
                phiMaxBitDiff, psiMaxBitDiff = svdOutputBitDiff(svdoutBuffer, matoutBuffer, testParams['nTx'], testParams['nRx'])
                formattype = int(caseDict['format'])
                ndpCount = DUT_functions.readndpCount(formattype)
                debugPrint("phiMaxBitDiff is "+ str(phiMaxBitDiff))
                debugPrint("psiMaxBitDiff is "+ str(psiMaxBitDiff))

                if(phiMaxBitDiff <= 3) and (psiMaxBitDiff <= 1):
                    svdStatus = "PASS"
                    passcount += 1
                else:
                    svdStatus = "FAIL"
                    failcount += 1
                status = [pktStatus, matlabresult, edStatus1, RXLatency, phiMaxBitDiff, psiMaxBitDiff, svdStatus, int(ndpCount)]
            elif(testConfigParams.subFuncTestPlan == 'FTM'):
                diffTimeEstimationMsb, diffTimeEstimationLsb = DUT_functions.ftmTimeEstimation()
                if (diffTimeEstimationMsb == 0) and (diffTimeEstimationLsb >= 0) and (diffTimeEstimationLsb <= 200):
                    ftmStatus = "PASS"
                    passcount += 1
                else:
                    ftmStatus = "FAIL"
                    failcount += 1
                status = [pktStatus, matlabresult, edStatus1, RXLatency, diffTimeEstimationLsb, ftmStatus]
            elif(testConfigParams.subFuncTestPlan == 'SPATIAL-REUSE'):
                threshold = -62  # Hardcoded this paramter while runnig SPR cases.
                snrdB = testParams ['snrdB']
                formatIdx = heading.index('format')
                PacketFormat = caseparams [formatIdx]
                coreClkCyclesperUs = 80
                adcSamplingrate = 40 << testParams['opBW']

                ccaDuration, expCcaDurationStr, calCcaDuration, finalStatus = \
                      spatialReuse_functions.spatialReusePostProssesing(testConfigParams, vectorDumpDir, memoryType, \
                                            coreClkCyclesperUs, adcSamplingrate, spatialReuseCnt, snrdB, PacketFormat, threshold)
                if finalStatus == 'PASS':
                    passcount = passcount + 1
                else:
                    failcount = failcount + 1

                status = [pktStatus, matlabresult, edStatus1, RXLatency, spatialReuseCnt, ccaDuration, expCcaDurationStr, calCcaDuration, finalStatus]
            elif(testConfigParams.subFuncTestPlan == 'RXLatency'):
                TxTime = DUT_functions.calculatePktDuration(DUT_RxVector, caseDict)
                TxtimePktdurationDiff = DUT_functions.calculateTxtimePktdurationDiff(pktDuration,TxTime,coreClkFreq)
                formattype = int(caseDict['format'])
                if formattype == 0:
                    symbolOffset = 44/coreClkFreq #2 symbols offset
                    RXLatency = RXLatency + symbolOffset

                if (formattype == 5) or (formattype == 6):
                    latencythreshold = 8 + 10.5 - TxtimePktdurationDiff #Subtracting TxtimePktdurationDiff due to SCP snapshot read delay
                else:
                    latencythreshold = 10.5 - TxtimePktdurationDiff

                if (RXLatency >= 0) and (RXLatency <= latencythreshold):
                    finalStatus = 'PASS'
                    passcount = passcount + 1
                else:
                    finalStatus = 'FAIL'
                    failcount = failcount + 1

                status = [pktStatus, matlabresult, edStatus1, RXLatency, finalStatus, (pktDuration/coreClkFreq), TxTime, TxtimePktdurationDiff]
            else:
                if(testConfigParams.subFuncTestPlan == 'HEMU'):
                    status = [pktStatus, matlabresult, edStatus1, RXLatency, rx_aidorstaId]
                else:
                    status = [pktStatus, matlabresult, edStatus1, RXLatency]
                if pktStatus == 'OFDM PACKET CRC_PASS':
                    passcount = passcount + 1
                elif pktStatus == 'DSSS PACKET CRC_PASS':
                    passcount = passcount + 1
                else:
                    failcount = failcount + 1

            file_operations.logRxResults(caseparams, status, resultsConsld, rowNum, heading, sheet)
            rowNum += 1
            if (test_case_count == testConfigParams.total_test_cases):
                resultsConsld.workbook.close()
            DUT_functions.clearRxStats()
            rxvector_functions.resetRXVectorParams()
            # In case DUT process haven't completed succesfuly reload executable before starting next case
            if (dutState == 'DUT_STUCK'):
                target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
                DUT_functions.pollSystemReady()
                DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
                DUT_functions.startTestcase()
        except socket.error as e:
            debugPrint(str(e))
            debugPrint("********************************************************MATLAB Time out in Test Case No. "+str(test_case_count)+" Procceding to next test case ********************************************************************")
            KillSubProcess(MtlbExeProcess)
            portNo = sock.getsockname()[1]
            MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, targetParams.system_config)
            if (test_case_count == testConfigParams.test_case_start):
                resultsConsld = ResultsOut()
                resultsConsld.prepareXlsx('RX_'+ testConfigParams.subFuncTestPlan +'_Results_Consolidated.xlsx')
                #heading = keyParams
                heading += ['DUT result', 'MATLAB result', 'ED status']
                resultsConsld.worksheet.write_row('A1', heading)
                sheet.write_row('A1', heading)
                rowNum = 2
            status = ['NA', 'MATLAB STUCK', 'NA']
            failcount = failcount+1
            file_operations.logRxResults(caseparams, status, resultsConsld, rowNum, heading, sheet)
            rowNum += 1
            if (test_case_count == testConfigParams.total_test_cases):
                resultsConsld.workbook.close()
        test_case_count = test_case_count + 1
    return passcount, failcount

def initializeExcelSheet(heading, sheet, testConfigParams):
    resultsConsld = ResultsOut()
    resultsConsld.prepareXlsx('RX_'+ testConfigParams.subFuncTestPlan +'_Results_Consolidated.xlsx')
    #heading = keyParams
    heading += ['DUT result', 'MATLAB result', 'ED status', 'RX Latency (us)']
    if(testConfigParams.subFuncTestPlan == 'AGC') :
        heading += ['rssi', 'agcMappedGain', 'firstAgcGain','matlabgcMappedGain', 'matlabFirstAgcGain', 'Status']
    elif(testConfigParams.subFuncTestPlan == 'SECONDAGC'):
        heading += ['rssi', 'agcMappedGain', 'firstAgcGain', 'secondAgcGain','secondAgcSatus','matlabgcMappedGain', 'matlabFirstAgcGain', 'matlabSecondAgcGain', 'Status']
    elif(testConfigParams.subFuncTestPlan == 'CCA') or (testConfigParams.subFuncTestPlan == 'CCADISC') or (testConfigParams.subFuncTestPlan == 'CCACOMBINED'):
        heading += ['ofdmCorrelaionCnt', 'rssiEstimated', 'CCA Duration','TX Time Calculated', 'sigStatus', 'CCA Result']
    elif(testConfigParams.subFuncTestPlan == 'JAMMER') :
        heading += ['ofdmCorrelaionCnt','SIG Status', 's2lcount', 'leeCount', 'jammer Status']
    elif(testConfigParams.subFuncTestPlan == 'CFO+SFO') :
        heading += ['dutCfoInKHz ', 'matCfoInKHz', 'cfoStatus']
    elif(testConfigParams.subFuncTestPlan == 'BEAMFORMEE') :
        heading += ['phiMaxBitDiff', 'psiMaxBitDiff ', 'svdStatus', 'ndpCount']
    elif(testConfigParams.subFuncTestPlan == 'ED-11K'):
        heading += ['rssi', 'dutNhAccumVal', 'matNhAccumVal', 'dutNhAccumCnt', 'matNhAccumCnt', 'dutAnpiEstdBm', 'matAnpiEstdBm', 'Status']
    elif(testConfigParams.subFuncTestPlan == 'POP'):
        heading += ['rssi','CCA Duration','TX Time Calculated', 'popStatus', 'finalStatus']
    elif(testConfigParams.subFuncTestPlan == 'FTM'):
        heading += ['diffTimeEstimation','ftmStatus']
    elif(testConfigParams.subFuncTestPlan == 'SPATIAL-REUSE'):
        heading += ['SpatialReuseEvent', 'ccaDuration', 'expCcaDuration', 'calTxTime', 'finalStatus']
    elif(testConfigParams.subFuncTestPlan == 'RXLatency') or (testConfigParams.subFuncTestPlan == 'HESU-Latency'):
        heading += ['Status', 'PktDuration(us)', 'TxTime(us)', 'TxtimePktdurationDiff(us)']
    elif(testConfigParams.subFuncTestPlan == 'HEMU'):
        heading += ['Decoded AidOrStaID']

    resultsConsld.worksheet.write_row('A1', heading)
    sheet.write_row('A1', heading)
    rowNum = 2
    return resultsConsld, rowNum

def readAndFeedRXSamplesToDUT (testConfigParams, file_real, file_imag, testParams, keyParams, memoryType, vectorDumpDir, caseDict):

        # Configure clock dividers
        playout_functions.configClock()
        playout_functions.configRXPlayout(testConfigParams.lna_model_enable)
         # in case Matlab fail to generate complete samples add silence equivalent to packet length
        adcSamplingrate = 40 << testParams['opBW']
        silenceTime = file_operations.calcSilence(vectorDumpDir,'rf1InputReal.txt','adc1OutputReal.txt',adcSamplingrate)

        silenceTime += 25 # time in us
        inputSamples1,numSamples1 = file_operations.readRXSamples(file_real, file_imag, memoryType)

        if(testConfigParams.subFuncTestPlan == 'FTM' or testConfigParams.subFuncTestPlan == 'RXLatency'):
        #Based on waveform 180 silence samples are removed and this value vary based on matlab generation
            removeSilenceSamples = 180
            inputSamples1,numSamples1 = file_operations.removeSilence(removeSilenceSamples, inputSamples1, memoryType)

        if(testConfigParams.subFuncTestPlan == 'CCA'):
            if(caseDict['corruptionType'] == 'L_parityBit'):
                inputSamples1 = inputSamples1[:2000]
                numSamples1 = len(inputSamples1)/2

        inputSamples,numSilenceSamples = file_operations.addSilence(adcSamplingrate, silenceTime, inputSamples1, memoryType)
        numSamples = numSamples1 + numSilenceSamples
        playout_functions.writeSamplesPlayout(inputSamples, numSamples, memoryType)
        playout_functions.pollPlayoutDone()
        DUT_functions.indicatePlayoutDone()
        if(testConfigParams.subFuncTestPlan == 'ED-11K'):
            time.sleep(3)
            exitRxWaitLoop()
        state = DUT_functions.wait4DutDone(120)
        if (state != 1):
        # Check ED status. If ED status =0, call this fucntion.
            DUT_functions.exitRxWaitLoop()
            state = DUT_functions.wait4DutDone(120)

        return state

def runRxSinglePacket(Matlab_input, test_case_count, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType, vectorDumpDir, caseDict):

    testCode = generateMatlabFiles (Matlab_input, test_case_count, testConfigParams, sock, MtlbExeProcess)
    if (int(testCode) == Constants.get('TESTCASE_COMPLETED')[0][0]):
        debugPrint("Matlab generated input files are ready")
        file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)

        DUT_functions.configureDUT(testConfigParams, testParams)
        state = readAndFeedRXSamplesToDUT (testConfigParams, file_real, file_imag, testParams, keyParams, memoryType, vectorDumpDir, caseDict)

        time.sleep(3)
        if (state == 1):
            return "DUT_DONE"
        else:
            return "DUT_STUCK"
    else:
        debugPrint("Matlab stuck")
        return "MATLAB_STUCK"

def runRxCombinedPacket(test_case_count, pkt_idx, testConfigParams, sock, MtlbExeProcess, testParams, keyParams, memoryType, vectorDumpDir, agcEn, caseDict):
    Matlab_input = 'testcaseIdx' + ' ' + str(test_case_count) + ' ' + 'pktIdx' + ' ' + str(pkt_idx) + ' ' + 'firmwareAgcTestEn' + ' ' + str(agcEn)
    testCode = generateMatlabFiles (Matlab_input, test_case_count, testConfigParams, sock, MtlbExeProcess)
    if (int(testCode) == Constants.get('TESTCASE_COMPLETED')[0][0]):
        debugPrint("Matlab generated input files are ready")
        file_real, file_imag = file_operations.selectOutputFile(testConfigParams, vectorDumpDir)
        if test_case_count%2 == 1:
            file_operations.storeOutputFiles(file_real, file_imag)
            return "CCA_BREAK"
        else:
            file_operations.combine_testcases(file_real, file_imag, test_case_count)
    else:
        debugPrint("Matlab stuck")
        return "MATLAB_STUCK"

    DUT_functions.configureDUT(testConfigParams, testParams)
    state = readAndFeedRXSamplesToDUT (testConfigParams, file_real, file_imag, testParams, keyParams, memoryType, vectorDumpDir, caseDict)
    time.sleep(3)
    if (state == 1):
        return "DUT_DONE"
    else:
        return "DUT_STUCK"


def executeTXCapture(testConfigParams, sock, MtlbExeProcess, testCasesFile, sheetName, test_case_count, targetParams, sheet, passcount, failcount):
    """ Run TX playout test case """
    DUT_functions.startTestcase()
    pkt_idx = 1 # To support for multiple packets
    snr_idx = 1
    passcount = 0
    failcount = 0
    testParams = {}
    while (test_case_count <= testConfigParams.total_test_cases):
        for iteration in range(testConfigParams.num_pkts):
            try:
                if (iteration == 0):
                    systemParams, testParams, keyParams = file_operations.readTestcaseXlsx(testConfigParams, testCasesFile, sheetName, test_case_count)
                print(iteration)
                txParams = TxParams()
                txParams.updateParams(testParams)
                payloadFile = "mpdu_payload.txt"
                vectorDumpDir = file_operations.returnSimOutDir (testConfigParams, test_case_count)
                if ('aggregationEnable' in testParams.keys()):
                    mpdu_data = file_operations.generatePayload(testParams['packetLength'] - 4) # 4 CRC bytes are deducted
                    file_operations.writePayloadToFile (mpdu_data,payloadFile,testParams['packetLength'] - 4, testParams['nMpdu'], vectorDumpDir)
                else:
                    mpdu_data = file_operations.generatePayload(testParams['packetLength'] - 4) # 4 CRC bytes are deducted
                    file_operations.writePayloadToFile (mpdu_data,payloadFile,testParams['packetLength'] - 4, 1, vectorDumpDir)
                data_bytes_out = []
                dataLength = formAmpduData(txParams, data_bytes_out, mpdu_data)
                setPayloadLength(dataLength)
                #print(data_bytes_out)
                DUT_functions.feedPayload(data_bytes_out)
                #Matlab_input = str(test_case_count) + ' ' + str(pkt_idx)
                Matlab_input = 'testcaseIdx' + ' ' + str(test_case_count) + ' ' + 'pktIdx' + ' ' + str(pkt_idx)
                if (iteration == 0):
                    conn, addr = sock.accept()# If MATLAB doesn't respond within timeout, kill the MATLAB process by using the socket.timeout error
                    conn.setblocking(1)
                    conn.send(str(Constants.get('START_TESTCASE')[0][0])+ ' ' + Matlab_input)#Give indication from python to MATLAB to start the test case
                    debugPrint("Sent the trigger to Matlab to start test case " + str(test_case_count))
                    sock.settimeout(testConfigParams.time_out_value)#Sets the timeout value.
                    conn, addr = sock.accept()
                    time.sleep(2)
                    testCode = conn.recv(1024)
                else:
                    testCode == Constants.get('TESTCASE_COMPLETED')[0][0]

                DUT_functions.configSystemParams(systemParams)
                DUT_functions.enableRetune()
                DUT_functions.configTXParams(testParams)
                DUT_functions.updateTXParams()

                if (testParams['format'] == DUT_FrameFormat.HE_TB):
                    testSheets = sheetName.split('_')
                    [legacyLength, fecPadding] = file_operations.readHetbParameters(testConfigParams, testCasesFile, testSheets[0], test_case_count)
                    DUT_functions.setLegacyLength(legacyLength)
                    DUT_functions.setFecPaddingFactor(fecPadding)
                else:
                    legacyLength = 'NA'
                    fecPadding = 'NA'
                # Configure clock dividers
                playout_functions.configClock()
                playout_functions.configTXCapture()
                samples2Read = 0x2000000
                playout_functions.startCapture(samples2Read)
                DUT_functions.clearTestDoneIndication()
                DUT_functions.startNextCase()
                DUT_functions.pollTestReady(60)
                state = DUT_functions.wait4DutDone(120)
                debugPrint("DUT done state is " + str(state))
                samples2Read = playout_functions.getNumSamplesCaptured()
                debugPrint(samples2Read)
                outBuffer = playout_functions.readCaptureMemory(samples2Read)
                file_operations.dumpTXOutSamples(outBuffer, samples2Read, testConfigParams)
                if (int(testCode) == Constants.get('TESTCASE_COMPLETED')[0][0]):
                    if (test_case_count == testConfigParams.test_case_start):
                        resultsConsld = ResultsOut()
                        resultsConsld.prepareXlsx('TX_'+ testConfigParams.subFuncTestPlan +'_Results_Consolidated.xlsx')
                        heading = keyParams
                        if (testParams['format'] == DUT_FrameFormat.HE_TB):
                            heading += ['Legacy Length', 'FEC Padding', 'SQNR', 'Results']
                        else:
                            heading += ['SQNR', 'Results']
                        resultsConsld.worksheet.write_row('A1', heading)
                        sheet.write_row('A1', heading)
                        rowNum = 2
                    sqnrValue = file_operations.calculateSqnr(outBuffer, samples2Read)
                    debugPrint("SQNR value is "+ str(sqnrValue))
                    passcount, failcount = file_operations.logResults(testParams, sqnrValue, resultsConsld, rowNum, heading, sheet, legacyLength, fecPadding, passcount, failcount)
                    rowNum += 1
                    if (test_case_count == testConfigParams.total_test_cases):
                        resultsConsld.workbook.close()
                # In case DUT process haven't completed succesfuly reload executable before starting next case
                if (state == 0):
                    target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
                    DUT_functions.pollSystemReady()
                    DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
                    DUT_functions.startTestcase()
            except socket.error as e:
                debugPrint(str(e))
                debugPrint("********************************************************MATLAB Time out in Test Case No. "+str(test_case_count)+" Procceding to next test case ********************************************************************")
                KillSubProcess(MtlbExeProcess)
                portNo = sock.getsockname()[1]
                MtlbExeProcess = Run_matlab_exe(testConfigParams, testCasesFile, portNo, targetParams.system_config)
                if (test_case_count == testConfigParams.test_case_start):
                    resultsConsld = ResultsOut()
                    resultsConsld.prepareXlsx('TX_'+ testConfigParams.subFuncTestPlan +'_Results_Consolidated.xlsx')
                    heading = keyParams
                    heading += ['SQNR', 'Results']
                    resultsConsld.worksheet.write_row('A1', heading)
                    sheet.write_row('A1', heading)
                    rowNum = 2
                passcount, failcount = file_operations.logResults(testParams, 'NA', resultsConsld, rowNum, heading, sheet, legacyLength, fecPadding, passcount, failcount)
                rowNum += 1
                if (test_case_count == testConfigParams.total_test_cases):
                    resultsConsld.workbook.close()
    ##        target_functions.loadnRunTarget(targetParams, DUT_HarnessEnable.PhyEnable)
    ##        DUT_functions.pollSystemReady()
    ##        DUT_functions.setOperatingMode(testConfigParams.dut_operating_mode)
    ##        DUT_functions.startTestcase()
            if (iteration == testConfigParams.num_pkts - 1):
                test_case_count = test_case_count + 1
    return passcount, failcount

def adjustSamples(outBuffer, memoryType):
    outSamples = []
    if (memoryType == 'shared'):
        outSamples = outBuffer + ([0]*2000)
    else:
        for i in range(len(outBuffer)):
            temp =  (outBuffer[i] & 0xfff00000)
            outSamples.append(temp)
            temp =  (outBuffer[i] & 0xffff) << 16
            outSamples.append(temp)
        outSamples = outSamples + ([0]*4000)

    return outSamples

def initializeSummarySheet(heading, sheet, sheet1):
    heading += ['PassCount', 'FailCount', 'Total TestCases']
    sheet.write_row('A1', heading)
    sheet1.write_row('A1', heading)
    rowNum = 2
    return rowNum