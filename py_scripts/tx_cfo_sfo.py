#-------------------------------------------------------------------------------
# Name:        tx_evm_power
# Purpose:     This script will interduce CFO and measure Frequence offset error/PPM error.
# Author:      Basheer Ahammad
# Created:     13-09-2021
# Copyright:   Imagination Technologies Ltd
#-------------------------------------------------------------------------------

from iqxel import *
from common_utils import *
import numpy
from openpyxl import *

rw_num=1

standard_dataRate_dict = {
                    '11ac':{
                            '1x1':{
                                    '20':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7',
                                        'MCS8'
                                        ],
                                    '40':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7',
                                        'MCS8','MCS9'
                                        ],
                                    '80':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7',
                                        'MCS8','MCS9'
                                        ]
                                    },
                            '2x2':{
                                    '20':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7',
                                        'MCS8'
                                        ],
                                    '40':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7',
                                        'MCS8','MCS9'
                                        ],
                                    '80':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7',
                                        'MCS8','MCS9'
                                        ]
                                    }
                            },
                    '11n':{
                            '1x1':{
                                '20':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7'
                                    ],
                                '40':[
                                        'MCS0','MCS1','MCS2','MCS3',
                                        'MCS4','MCS5','MCS6','MCS7'
                                    ]
                                },
                                '2x2':{
                                '20':[
                                    'MCS8','MCS9','MCS10','MCS11',
                                    'MCS12','MCS13','MCS14','MCS15',
                                    ],
                                '40':[
                                    'MCS8','MCS9','MCS10','MCS11',
                                    'MCS12','MCS13','MCS14','MCS15'
                                    ]
                                }
                        },
                    '11b':{
                        '1x1':{
                            '20':[
                                '1','2','5.5','11'
                                ]
                            }
                        },
                    '11g':{
                        '1x1':{
                            '20':[
                                '6','9','12','18',
                                '24','36','48','54'
                                ]
                            }
                        },
                    '11a':{
                        '1x1':{
                            '20':[
                                '6','9','12','18',
                                '24','36','48','54'
                                ]
                            }
                        }
                }

op_file_path=""

#Configuraing the CFO value into tx_parms and generate the packets from DUT.
#Taking frequency error from VSA and comparing to the refence value.
def dut_cfo_sfo_est(DUT_TestConfigParams,ch,dtr):
    start_amp_list=[]
    global row_num
    global data
    global row_num_dr
    row_num_dr=2
    if(int(ch) < 15):
        band='2.4'
    else:
        band='5'
    a=1
    if(1 <= int(ch) <= 14):
        cable_loss_band='24G_BAND'
    if(36 <= int(ch) <= 52):
        cable_loss_band='5G_BAND1'
    elif(53 <= int(ch) <= 108):
        cable_loss_band='5G_BAND2'
    elif(109 <= int(ch) <= 132):
        cable_loss_band='5G_BAND3'
    elif(133 <= int(ch) <= 165):
        cable_loss_band='5G_BAND4'
    cable_loss_1x1=cable_loss_dict['1x1'][cable_loss_band]
    cable_loss_2x2=cable_loss_1x1
    if(streams=='2x2'):
        cable_loss_2x2=cable_loss_dict['2x2'][cable_loss_band]

    evm_index_flag_1x1,evm_index_flag_2x2=0,0
    dut.pktgen_tool(DUT_TestConfigParams,'run')
    for txp in txpower_dict[dtr]:
        data=[]
        data.append(standard)
        data.append(int(ch))
        try:
            data.append(int(dtr))
        except:
            data.append(dtr)
        data.append(txp)
        data.append(DUT_TestConfigParams.freq_err)
        dut.set_dut_txpower(int(txp))
        dut.set_dut_cfo_sfo_settings(DUT_TestConfigParams.cfoRatio, DUT_TestConfigParams.triggerResponding)
        dut.pktgen_tool(DUT_TestConfigParams,'update')

        # time.sleep(1)
        for i in range(3):
            return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
##            DebugPrint(return_data)
            if(('e+37' not in str(return_data[0])) and (0 not in return_data[2:])):
                break
            #print return_data
            equipment.close_vsg()
            equipment.start_vsg()
            DUT_TestConfigParams.status = 'TX_EVM_ERROR'
        data=data+return_data
        print data[-5]
        #print data
        freqErr = (-DUT_TestConfigParams.freq_err * 1000) - data[-5]
        if(freqErr < 2000) & (freqErr > -2000):
            data.append('PASS')
        else:
            data.append('FAIL')

        DebugPrint(data)
        worksheet.append(data)
        row_num=row_num+1
    row_num=row_num+1

#Interduce CFO value in DUT and measured the frequency offset error
#and ppm error at VSA output.
def tx_cfo_sfo_analysis(DUT_TestConfigParams,dut1):
    global ftime
    global equipment
    global dut
    global modulation
    global row_num
    global standard
    global streams_chain
    global freq
    global bw
    global gi
    global stbc
    global coding
    global data_rate
    global cable_loss
    global greenfield_mode
    global channel
    global op_file_path
    global preamble
    global streams
    global chain_sel
    global workbook
    global worksheet
    global bold
    global bold1
    global max_txpower_dict
    global txpower_dict
    global power_evm_dict
    global cnsl_fname
    global txpower_list
    global payload
    global p20_flag
    global txpower_evm_dict
    global giType
    global heLtfType
    global pktFrameFormat
    global pltName


    greenfield_mode=stbc=preamble=gi=coding=preamble=''
    strt_time=time.time()
    txpower_dict={}
    txpower_evm_dict={}
    dut = dut1
    standard = DUT_TestConfigParams.standard
    streams=DUT_TestConfigParams.streams
    chain_sel = DUT_TestConfigParams.chain_sel
    streams_chain = streams+'_'+str(chain_sel)
    bw = DUT_TestConfigParams.bw
    data_rate = DUT_TestConfigParams.data_rate
    dutModel=DUT_TestConfigParams.dutModel
    start_txpower=DUT_TestConfigParams.start_amplt
    end_txpower=DUT_TestConfigParams.end_amplt
    step_size=DUT_TestConfigParams.step_size
    channel=int(DUT_TestConfigParams.channel)
    payload=int(DUT_TestConfigParams.payload)
    p20_flag = DUT_TestConfigParams.p20_flag
    pktFrameFormat=''
    if(standard=='11b'):
        preamble=DUT_TestConfigParams.preamble

    if((standard=='11ac')or(standard=='11n')or(standard=='11ax')):
        stbc=DUT_TestConfigParams.stbc
        gi=DUT_TestConfigParams.gi
        coding=DUT_TestConfigParams.coding
        if(standard=='11n'):
            greenfield_mode=DUT_TestConfigParams.greenfield_mode

    if(standard=='11ax'):
        giType = str(0.8*(1<<DUT_TestConfigParams.giType))+'us'
        heLtfType = str((1<<DUT_TestConfigParams.heLtfType))+'x'
        greenfield_mode=DUT_TestConfigParams.format
        tone = ''
        if(DUT_TestConfigParams.format == 5):
            pktFrameFormat='HESU'
        elif(DUT_TestConfigParams.format == 6):
            pktFrameFormat='HEMU'
        elif(DUT_TestConfigParams.format == 7):
            pktFrameFormat='HEERSU'
            if (DUT_TestConfigParams.chBandwidth ==0):
                tone = '242Tone_'
            else:
                tone = '106Tone_'
        elif(DUT_TestConfigParams.format == 8):
            pktFrameFormat='HETB'
        dcm = 'DCM_'*DUT_TestConfigParams.dcm
        doppler = ('doppler'+str(DUT_TestConfigParams.midamblePeriodicity)+'_')*DUT_TestConfigParams.doppler
        pltName = pktFrameFormat+'_Chn'+str(channel)+'_'+bw+'Mhz_'+giType+'GI_'+heLtfType+'LTF_'+dcm+doppler+tone+coding+'_'+stbc

    if(channel<30):
        freq='2.4GHz'
    else:
        freq='5GHz'
    op_file_path=BuildResultsPath(DUT_TestConfigParams)
    time.sleep(0.5)
    power_evm_dict={}
    max_txpower_dict={}
    DebugPrint(create='1')
    #dut=eval(dutModel)(com_port)
    tester = DUT_TestConfigParams.vsg
    equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
    DebugPrint('Trying to initialize dut in PER Main')
    if(dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,greenfield_mode=greenfield_mode,release=release,test='tx',chain_sel=chain_sel)=='CONNECT_FAIL'):
        print 'CONNECT_FAIL'
        DebugPrint('CONNECT_FAIL in PER Main')
        controlPowerSwitch(on_ports_list='8',off_ports_list='8')
        if(dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,greenfield_mode=greenfield_mode,release=release,test='tx',chain_sel=chain_sel)=='CONNECT_FAIL'):
            print 'Switching to Serial Access'
            DebugPrint('Switching to Serial Access')
            dutModel=dutModel.split('_')[0]
            dut=eval(dutModel)(com_port)
            equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
            dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,release=release,test='tx',chain_sel=chain_sel)
    try:
        equipment.init_vsa_funcs(standard=standard,bw=bw,streams=streams,stbc=stbc,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,chain_sel=str(chain_sel))
    except Exception,e:
        print 'Equipment is not reachable'
        DebugPrint('Equipment is not reachable')
        exit(0)
    dut.pktgen_tool(DUT_TestConfigParams,'write')

    for dr in data_rate.split(','):
        txpower_list=[]
        steps_list=list(numpy.arange(start_txpower,end_txpower+1,step_size))
        for j in steps_list:
            txpower_list.append(j)
        DebugPrint(txpower_list)
        txpower_dict[dr]=txpower_list
    #dut.pktgen_tool(DUT_TestConfigParams,'run')
    dut.set_dut_production_mode_settings(standard=standard,ch=channel,stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx',payload=payload)
    if(standard=='11ax'):
        if ((DUT_TestConfigParams.format == 5) or (DUT_TestConfigParams.format == 7)):
            dut.setHesuParams(DUT_TestConfigParams)
        elif (DUT_TestConfigParams.format == 8):
            dut.setHetbParams(DUT_TestConfigParams)
    #for ch in channel:
    ch = str(channel)
    if ch not in power_evm_dict.keys():
        power_evm_dict[ch]={}
    row_num=2
    if(int(ch)<30):
        freq='2.4GHz'
    else:
        freq='5GHz'
##    dut.pktgen_tool(DUT_TestConfigParams,'kill')
    #dut.set_dut_production_mode_settings(standard=standard,ch=ch,stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx')
    dut.set_dut_channel(int(ch),p20_flag)
    equipment.apply_vsa(ch,bw,streams)

    consld_fname=os.path.join(op_file_path.split(standard)[0],'TX_CFO_SFO_Consolidated_results.xlsx')
    if os.path.exists(consld_fname):
        workbook= load_workbook(consld_fname)
        worksheet = workbook.active
    else:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(['Standard','Channel','Set DataRate','TXPower', 'Set freqErrinKHz',\
        'Bandwidth','Measured DataRate','Power','EVM(-ve)','Phase Error','Frequency Error',\
        'SymClkError','LO Leakage','Amplitude Imbalance','Phase Imbalance','Status'])
        bold_font = styles.Font(bold=True)
        for cell in worksheet["1:1"]:
            cell.font = bold_font
    DebugPrint(consld_fname)

    for dr in data_rate.split(','):
        if dr not in power_evm_dict[ch].keys():
            power_evm_dict[ch][dr]={}

        dut.set_dut_datarate(dr,standard)
        if(pktFrameFormat =='HETB'):
            equipment.configVsaHETB(DUT_TestConfigParams)
        dut_cfo_sfo_est(DUT_TestConfigParams,ch,dr)
    try:
        workbook.save(consld_fname)
    except Exception,e:
        print e.args
        print "plot_power_evm(ch)"
        workbook.save(consld_fname)
        pass

    equipment.close_vsg()
    dut.dut_close()