#-------------------------------------------------------------------------------
# Name:        tx_evm_power
# Purpose:     This script will generate EVM-Measured Power vs DUT Power .
# Author:      kranthi.kishore
# Created:     14-06-2015
# Copyright:   Imagination Technologies Ltd
#-------------------------------------------------------------------------------

#from danube import *
#from beetle import *
#from rs import *
#from toshiba import *
#from europa import *
from iqxel import *
#from CommonUtils import *
from common_utils import *
import numpy

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
#Loop iterating for the range of txpower mentioned
def dut_txpower_loop(DUT_TestConfigParams,ch,dtr):
    start_amp_list=[]
    global row_num
    global data
    global row_num_dr
    row_num_dr=2
    xlsx_top_row = ['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power','EVM(-ve)','Phase Error','Frequency Error','SymClkError','LO Leakage','Amplitude Imbalance','Phase Imbalance']
    if standard == '11b':
        xlsx_top_row += ['Lower Freq offset2','Lower Freq offset1','Upper Freq offset1','Upper Freq offset2','Lower Margin2','Lower Margin1','Upper Margin1','Upper Margin2','Spectrum status']
    else:
        xlsx_top_row += ['Lower Freq offset4','Lower Freq offset3','Lower Freq offset2','Lower Freq offset1','Upper Freq offset1','Upper Freq offset2','Upper Freq offset3','Upper Freq offset4','Lower Margin4','Lower Margin3','Lower Margin2','Lower Margin1','Upper Margin1','Upper Margin2','Upper Margin3','Upper Margin4','Spectrum status']
    if(streams=='1x1'):
        worksheet_dr.write_row('A1',xlsx_top_row,bold)
        worksheet.write_row('A1',xlsx_top_row,bold1)
    elif(streams=='2x2'):
        worksheet.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power-Stream1','Power-Stream2','EVM-Stream1(-ve)','EVM-Stream2(-ve)','Phase Error-Stream1','Phase Error-Stream2','Frequency Error-Stream1','Frequency Error-Stream2','SymClkError-Stream1','SymClkError-Stream2','LO Leakage-Stream1','LO Leakage-Stream2','Amplitude Imbalance-Stream1','Amplitude Imbalance-Stream2','Phase Imbalance-Stream1','Phase Imbalance-Stream2','Spectral Mask-Stream1','Spectral Mask-Stream2','Carrier Suppression-Stream1','Carrier Suppression-Stream2'],bold1)
        worksheet_dr.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power-Stream1','Power-Stream2','EVM-Stream1(-ve)','EVM-Stream2(-ve)','Phase Error-Stream1','Phase Error-Stream2','Frequency Error-Stream1','Frequency Error-Stream2','SymClkError-Stream1','SymClkError-Stream2','LO Leakage-Stream1','LO Leakage-Stream2','Amplitude Imbalance-Stream1','Amplitude Imbalance-Stream2','Phase Imbalance-Stream1','Phase Imbalance-Stream2','Spectral Mask-Stream1','Spectral Mask-Stream2','Carrier Suppression-Stream1','Carrier Suppression-Stream2'],bold)
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
    if(ch not in max_txpower_dict.keys()):
        max_txpower_dict[ch]={}
    if(dtr not in max_txpower_dict[ch].keys()):
        max_txpower_dict[ch][dtr]={}
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
##        temp = data
        dut.set_dut_txpower(int(txp))
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
##        if(return_data[4]==0):
##            if(dut.check_dut_stuck_state()=='alive'):
##                dut.dut_reboot()
##            else:
##                print 'DUT is stuck'
##                controlPowerSwitch(on_ports_list='8',off_ports_list='8')
##            time.sleep(reboot_time)
##            dut.init_dut(standard=standard,streams=streams,channel=int(ch),bw=bw,release=release,test='tx',chain_sel=chain_sel)
##            dut.set_dut_production_mode_settings(standard=standard,ch=int(ch),stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx')
##            dut.set_dut_channel(int(ch))
##            dut.set_dut_datarate(dtr,standard)
##            dut.set_dut_txpower(int(txp))
##            dut.pktgen_tool(DUT_TestConfigParams,'run')
##            return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2)
        data=data+return_data
        if(0):
        #if('Fail' in data):
        # if(1):
            f_name=standard+'_'+streams+'_'+str(chain_sel)+'_'+bw+'_'+dtr+'_TxPower'+str(txp)
            vsa_stats_fname=os.path.join(op_file_path,'VSA_SPECTRUM_STATS_'+f_name+'.xlsx')
            DebugPrint('Generating vsa_stats_fname : ' + vsa_stats_fname)
            workbook_vsa_stats = xlsxwriter.Workbook(vsa_stats_fname)
            worksheet_vsa_stats = workbook_vsa_stats.add_worksheet()
            bold_vsa_stats = workbook_vsa_stats.add_format({'bold': 1})
            if(streams=='1x1'):
                worksheet_vsa_stats.write_row('A1',['Frequency','Measured Spectrum','Ideal Spectrum'],bold_vsa_stats)
                worksheet_vsa_stats.write_column('A2',map(float,return_data[-3][0]))
                worksheet_vsa_stats.write_column('B2',map(float,return_data[-2][0]))
                worksheet_vsa_stats.write_column('C2',map(float,return_data[-1][0]))
            else:
                worksheet_vsa_stats.write_row('A1',['Frequency','Measured Spectrum-Stream1','Measured Spectrum-Stream2','Ideal Spectrum'],bold_vsa_stats)
                worksheet_vsa_stats.write_column('A2',map(float,return_data[-4][0]))
                worksheet_vsa_stats.write_column('B2',map(float,return_data[-3][0]))
                worksheet_vsa_stats.write_column('C2',map(float,return_data[-2][0]))
                worksheet_vsa_stats.write_column('D2',map(float,return_data[-1][0]))
            chart_vsa_stats = workbook_vsa_stats.add_chart({'type': 'line'})
            if(streams=='1x1'):
                col_names_vsa_stats=['Measured Spectrum','Ideal Spectrum']
            else:
                col_names_vsa_stats=['Measured Spectrum-Stream1','Measured Spectrum-Stream2','Ideal Spectrum']

            if(streams=='1x1'):
                column_col_vsa_stats_dict={'Measured Spectrum':'B','Ideal Spectrum':'C'}
                for col_vsa_stats in col_names_vsa_stats:
                    # print 'values  =Sheet1!$'+column_col_vsa_stats_dict[col_vsa_stats]+'2:'+column_col_vsa_stats_dict[col_vsa_stats]+str(len(return_data[-2][0])+1)
                    chart_vsa_stats.add_series({
                        'name':       col_vsa_stats,
                        'categories': '=Sheet1!$A$2:$A$'+str(len(return_data[-2][0])+1),
                        'values':  '=Sheet1!$'+column_col_vsa_stats_dict[col_vsa_stats]+'2:'+column_col_vsa_stats_dict[col_vsa_stats]+str(len(return_data[-2][0])+1)
                    })
            else:
                column_col_vsa_stats_dict={'Measured Spectrum-Stream1':'B','Measured Spectrum-Stream2':'C','Ideal Spectrum':'D'}
                for col_vsa_stats in col_names_vsa_stats:
                    # print 'values  =Sheet1!$'+column_col_vsa_stats_dict[col_vsa_stats]+'2:'+column_col_vsa_stats_dict[col_vsa_stats]+str(len(return_data[-2][0])+1)
                    chart_vsa_stats.add_series({
                        'name':       col_vsa_stats,
                        'categories': '=Sheet1!$A$2:$A$'+str(len(return_data[-2][0])+1),
                        'values':  '=Sheet1!$'+column_col_vsa_stats_dict[col_vsa_stats]+'2:'+column_col_vsa_stats_dict[col_vsa_stats]+str(len(return_data[-2][0])+1)
                    })

            chart_vsa_stats.set_title ({'name': 'Spectrum'})
            chart_vsa_stats.set_x_axis({'name': 'Frequency'})
            chart_vsa_stats.set_y_axis({'name': 'Spectrum'})
            chart_vsa_stats.set_style(10)
            worksheet_vsa_stats.insert_chart('D2', chart_vsa_stats)
            workbook_vsa_stats.close()
        #data=data[:-3]
        if(streams=='2x2'):
            data=data[:-1]
        print data
        if(streams=='1x1'):
            measured_power_1x1=data[6]
            measured_evm_1x1=data[7]
            if 'Power-Stream1' not in power_evm_dict[ch][dtr].keys():
                power_evm_dict[ch][dtr]['Power-Stream1']=[]
            power_evm_dict[ch][dtr]['Power-Stream1'].append(data[6])
            if 'EVM-Stream1' not in power_evm_dict[ch][dtr].keys():
                power_evm_dict[ch][dtr]['EVM-Stream1']=[]
            power_evm_dict[ch][dtr]['EVM-Stream1'].append(data[7])
        elif(streams=='2x2'):
            measured_power_1x1=data[6]
            measured_power_2x2=data[7]
            measured_evm_1x1=data[8]
            measured_evm_2x2=data[9]
            if 'Power-Stream1' not in power_evm_dict[ch][dtr].keys():
                power_evm_dict[ch][dtr]['Power-Stream1']=[]
            power_evm_dict[ch][dtr]['Power-Stream1'].append(data[6])
            if 'Power-Stream2' not in power_evm_dict[ch][dtr].keys():
                power_evm_dict[ch][dtr]['Power-Stream2']=[]
            power_evm_dict[ch][dtr]['Power-Stream2'].append(data[7])
            if 'EVM-Stream1' not in power_evm_dict[ch][dtr].keys():
                power_evm_dict[ch][dtr]['EVM-Stream1']=[]
            power_evm_dict[ch][dtr]['EVM-Stream1'].append(data[8])
            if 'EVM-Stream2' not in power_evm_dict[ch][dtr].keys():
                power_evm_dict[ch][dtr]['EVM-Stream2']=[]
            power_evm_dict[ch][dtr]['EVM-Stream2'].append(data[9])
        measured_power_1x1=data[4]
        measured_power_2x2=data[5]
        measured_evm_1x1=data[6]
        measured_evm_2x2=data[7]
        txpower_evm_dict[txp] = data[4:8]
        DebugPrint(data)
        worksheet.write_row('A'+str(row_num), data)
        worksheet_dr.write_row('A'+str(row_num_dr), data)
        row_num=row_num+1
        row_num_dr=row_num_dr+1
##        while (row_num < 100):
##            return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2)
##            data = temp + return_data
##            worksheet.write_row('A'+str(row_num), data)
##            row_num=row_num+1
        if(a==1):
            prev_txp=curr_txp=txp
            prev_evm_1x1=curr_evm_1x1=measured_evm_1x1
            if(streams=='2x2'):
                prev_evm_2x2=curr_evm_2x2=measured_evm_2x2
        else:
            prev_txp=curr_txp
            curr_txp=txp
            prev_evm_1x1=curr_evm_1x1
            curr_evm_1x1=measured_evm_1x1
            if(streams=='2x2'):
                prev_evm_2x2=curr_evm_2x2
                curr_evm_2x2=measured_evm_2x2
        a+=1
        #if float(measured_evm_1x1) < float(standard_evm_dict[standard][dtr]): #PHY_PERFORMANCE - updated
        if float(measured_evm_1x1) < float(standard_evm_dict[band][dtr]):
            if(evm_index_flag_1x1==2):
                if(len(power_evm_dict[ch][dtr]['Power-Stream1'])>1):
                    evm_index_flag_1x1=1
                    get_best_txpower_from_evm(DUT_TestConfigParams,ch=ch,dtr=dtr,prev_txp=prev_txp,curr_txp=txp,prev_evm=prev_evm_1x1,measured_evm=measured_evm_1x1)
        #elif (float(measured_evm_1x1) > float(standard_evm_dict[standard][dtr])):
        elif (float(measured_evm_1x1) > float(standard_evm_dict[band][dtr])):
            evm_index_flag_1x1=2
        if(streams=='2x2'):
            #if float(measured_evm_2x2) < float(standard_evm_dict[standard][dtr]):
            if float(measured_evm_2x2) < float(standard_evm_dict[band][dtr]):
                if(evm_index_flag_2x2==2):
                    evm_index_flag_2x2=1
                    get_best_txpower_from_evm(DUT_TestConfigParams,ch=ch,dtr=dtr,prev_txp=prev_txp,curr_txp=txp,prev_evm=prev_evm_2x2,measured_evm=measured_evm_2x2)
            #if float(measured_evm_2x2) > float(standard_evm_dict[standard][dtr]):
            if float(measured_evm_2x2) > float(standard_evm_dict[band][dtr]):
                evm_index_flag_2x2=2
    #dut.pktgen_tool(DUT_TestConfigParams,'kill')
        #print evm_index_flag_1x1

    if(evm_index_flag_1x1==2):
        max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1']=str(measured_power_1x1)
        max_txpower_dict[ch][dtr]['EVM-Stream1']=str(measured_evm_1x1)
    elif(evm_index_flag_1x1==0):
        max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1']='TBT'
        max_txpower_dict[ch][dtr]['EVM-Stream1']='TBT'
    if(streams=='2x2'):
        if(evm_index_flag_2x2==2):
            max_txpower_dict[ch][dtr]['MAX_TXPower-Stream2']=str(measured_power_2x2)
            max_txpower_dict[ch][dtr]['EVM-Stream2']=str(measured_evm_2x2)
        elif(evm_index_flag_2x2==0):
            max_txpower_dict[ch][dtr]['MAX_TXPower-Stream2']='TBT'
            max_txpower_dict[ch][dtr]['EVM-Stream2']='TBT'
##    dut.pktgen_tool(DUT_TestConfigParams,'kill')
    row_num=row_num+1

def save_to_doc(hdng,imag,freq,chn):
    global document_path
    document_path=os.path.join(op_file_path.split(standard)[0],'TX_Characterization_'+release+'_'+board_num+'_'+rf_num+'.docx')
    try:
        document = Document(document_path)
    except:
        document = Document()
    paragraphs_obj=document.paragraphs
    paragraphs=[]
    for p in paragraphs_obj:
        paragraphs.append(p.text)
    if(release+" TX Performance" not in paragraphs):
        document.add_heading(release+" TX Performance", level=1)
    if('Power vs EVM Curves' not in paragraphs):
        document.add_heading('Power vs EVM Curves', level=2)
    if(standard=='11ax'):
        if("HE - Channel-"+str(chn) not in paragraphs):
            document.add_heading("HE - Channel-"+str(chn), level=3)
    if(standard=='11ac'):
        if("VHT - Channel-"+str(chn) not in paragraphs):
            document.add_heading("VHT - Channel-"+str(chn), level=3)
    if(standard=='11n'):
        if("HT - "+freq+"-Channel-"+str(chn) not in paragraphs):
            document.add_heading("HT - "+freq+"-Channel-"+str(chn), level=3)
    if(standard=='11g'):
        if("Legacy - Channel-"+str(chn) not in paragraphs):
            document.add_heading("Legacy - Channel-"+str(chn), level=3)
    if(standard=='11a'):
        if("Legacy - Channel-"+str(chn) not in paragraphs):
            document.add_heading("Legacy - Channel-"+str(chn), level=3)
    if(standard=='11b'):
        if("DSSS - Channel-"+str(chn) not in paragraphs):
            document.add_heading("DSSS - Channel-"+str(chn), level=3)
    if(hdng not in paragraphs):
        document.add_heading(hdng, level=5)
    document.add_picture(imag,height=Inches(4.05),width=Inches(7.5))
    try:
        document.save(document_path)
    except:
        document.save(document_path+'_'+str(time.time())+'.docx')

def plot_power_evm_png(ch):
    for dtr in data_rate.split(','):
        if(streams=='1x1'):
            col_names=['Power-Stream1','EVM-Stream1']
        else:
            col_names=['Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2']

        for label in col_names:
            plt.plot(txpower_dict[dtr],power_evm_dict[ch][dtr][label],label=label,linewidth=3)

        if(int(ch) < 15):
            freq='2.4GHz'
        else:
            freq='5GHz'
        if(standard=='11ax'):
            cnsl_fname=pltName+'_'+str(dtr)
            drt=str(dtr)
        elif(standard=='11ac'):
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dtr)
            drt=str(dtr)
        elif(standard=='11n'):
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc+'_'+str(dtr)
            drt=str(dtr)
        else:
            if(standard=='11b'):
                cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+preamble+'_'+str(dtr)+'Mbps'
            else:
                cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+str(dtr)+'Mbps'
        plt.title(cnsl_fname)
        plt.ylabel('- EVM (dB)/VSA Power', fontsize = 13)
        plt.xlabel('DUT TX Power (dBm))', fontsize = 13)
        plt.grid()
        lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
        img_plot_path=os.path.join(op_file_path,cnsl_fname+'.png')
        plt.savefig(img_plot_path,bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
        plt.cla()
        save_to_doc(cnsl_fname,img_plot_path,freq,ch)


def plot_power_evm(ch):
    chart1 = workbook.add_chart({'type': 'line'})
    chart_dr = workbook.add_chart({'type': 'line'})
    endval=len(txpower_list)+1
    strval=2
    x=2
    for dr in data_rate.split(','):
        chart_dr = workbook.add_chart({'type': 'line'})
        if(streams=='1x1'):
            column_dict={'Power-Stream1':'G','Power-Stream2':'G','EVM-Stream1':'H','EVM-Stream2':'H'}
            col_names=['Power-Stream1','EVM-Stream1']
        else:
            column_dict={'Power-Stream1':'G','Power-Stream2':'H','EVM-Stream1':'I','EVM-Stream2':'J'}
            col_names=['Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2']

        for column in col_names:
                chart_dr.add_series({
                    'name':       column,
                    'categories': '=Sheet1!$D$2:$D$'+str(len(txpower_list)+1),
                    'values':  '=Sheet1!$'+column_dict[column]+str(strval)+':'+column_dict[column]+str(endval)
                })

        strval=strval+len(txpower_list)+1
        endval=endval+len(txpower_list)+1
        if(standard=='11ax'):
            name_dr=pltName+'_'+str(dr)
            drt=str(dr)
        elif(standard=='11ac'):
            name_dr=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
            drt=str(dr)
        elif(standard=='11n'):
            name_dr=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc+'_'+str(dr)
            drt=str(dr)
        else:
            if(standard=='11b'):
                name_dr=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+preamble+'_'+str(dr)+'Mbps'
            else:
                name_dr=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+str(dr)+'Mbps'
            drt=str(dr)+'Mbps'
        chart_dr.set_title ({'name': dr})
        chart_dr.set_x_axis({'name': 'DUT TX Power (dBm)','position_axis': 'on_tick'})
        chart_dr.set_y_axis({'name': ' - EVM (dB)'})
        chart_dr.set_style(10)
        worksheet.insert_chart('O'+str(x), chart_dr, {'x_offset': 5, 'y_offset': 5})
        x=x+strval

def get_best_txpower_from_evm(DUT_TestConfigParams,ch='',dtr='',prev_txp='',curr_txp='',prev_evm='',measured_evm=''):


    if(int(ch) < 15):
        band='2.4'
    else:
        band='5'

    evm_obtained_flag_1x1,evm_obtained_flag_2x2=0,0

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

    max_txp_findlist=range(int(prev_txp),int(curr_txp)+1)

    if(len(max_txp_findlist)>2):
        del max_txp_findlist[0]
        del max_txp_findlist[-1]
    for txp in max_txp_findlist:
        dut.set_dut_txpower(str(txp))
        return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
        if('e+37' in str(return_data[0])):
            time.sleep(3)
            return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
        if(return_data[2]==0):
            for i in range(10):
                return_data.pop()
            if(dut.check_dut_stuck_state()=='alive'):
                dut.dut_reboot()
            else:
                print 'DUT is stuck'
                controlPowerSwitch(on_ports_list='8',off_ports_list='8')
            time.sleep(reboot_time)
            dut.init_dut(standard=standard,streams=streams,channel=int(ch),bw=bw,release=release,test='tx',chain_sel=chain_sel)
            dut.set_dut_production_mode_settings(standard=standard,ch=int(ch),stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx',payload=payload)
            dut.set_dut_channel(int(ch),p20_flag)
            dut.set_dut_datarate(dtr,standard)
            dut.set_dut_txpower(str(txp))
            dut.pktgen_tool(DUT_TestConfigParams,'run')
            return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
        print return_data
        if(streams=='1x1'):
            measured_power_1x1=return_data[2]
            measured_evm_1x1=return_data[3]
        elif(streams=='2x2'):
            measured_power_1x1=return_data[2]
            measured_power_2x2=return_data[3]
            measured_evm_1x1=return_data[4]
            measured_evm_2x2=return_data[5]

        #if float(measured_evm_1x1) < float(standard_evm_dict[standard][dtr]):
        if float(measured_evm_1x1) < float(standard_evm_dict[band][dtr]):
            evm_obtained_flag_1x1=1

        if(evm_obtained_flag_1x1==1):
            if('MAX_TXPower-Stream1' not in max_txpower_dict[ch][dtr].keys()):
                max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1']=str(measured_power_1x1)
                max_txpower_dict[ch][dtr]['EVM-Stream1']=str(measured_evm_1x1)

        if(streams=='2x2'):
            #if float(measured_evm_2x2) > float(standard_evm_dict[standard][dtr]):
            if float(measured_evm_2x2) > float(standard_evm_dict[band][dtr]):
                evm_obtained_flag_2x2=1

            if(evm_obtained_flag_2x2==1):
                if('MAX_TXPower-Stream2' not in max_txpower_dict[ch][dtr].keys()):
                    max_txpower_dict[ch][dtr]['MAX_TXPower-Stream2']=str(measured_power_2x2)
                    max_txpower_dict[ch][dtr]['EVM-Stream2']=str(measured_evm_2x2)
        if(evm_obtained_flag_1x1==0):
            max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1']=str(measured_power_1x1)
            max_txpower_dict[ch][dtr]['EVM-Stream1']=str(measured_evm_1x1)
        if(streams=='2x2'):
            if(evm_obtained_flag_2x2==0):
                max_txpower_dict[ch][dtr]['MAX_TXPower-Stream2']=str(measured_power_2x2)
                max_txpower_dict[ch][dtr]['EVM-Stream2']=str(measured_evm_2x2)

def write_max_txpower():

    consld_fname=os.path.join(op_file_path,'MAX_TXPower_Consolidated_'+cnsl_fname+'.xlsx')
    workbook_maxtxpower = xlsxwriter.Workbook(consld_fname)
    worksheet_maxtxpower = workbook_maxtxpower.add_worksheet()
    bold_maxtxpower = workbook_maxtxpower.add_format({'bold': 1})
    global max_document_path
    x = txpower_evm_dict.keys()
    x.sort(reverse = True)

    max_document_path=os.path.join(op_file_path.split(standard)[0],'MAX_TXPower_Consolidated_'+release+'.docx')
    try:
        document = Document(max_document_path)
    except:
        document = Document()
    paragraphs_obj=document.paragraphs
    paragraphs=[]
    for p in paragraphs_obj:
        paragraphs.append(p.text)
    if(release+" MAX TXPower Performance" not in paragraphs):
        document.add_heading(release+" MAX TXPower Performance", level=1)
    if('MAX_TXPower_Datarates' not in paragraphs):
        document.add_heading('MAX_TXPower_Datarates', level=2)
    col_names = ['Standard','Channel','DataRate','Expected EVM','Prev Power_1','Prev EVM_1(-ve)','Curr Power_1','Curr EVM_1','Interpolated Power_1']
    col_names_tables = ['DataRate','Expected EVM','Interpolated Power_1']
    if(streams=='2x2'):
        col_names = col_names + ['Prev Power_2','Prev EVM(-ve)_2','Curr Power_2','Curr EVM_2','Interpolated Power_2','Final Power']
        col_names_tables = col_names_tables + ['Interpolated Power_2','Final Power']
    worksheet_maxtxpower.write_row('A1',col_names)

    row_num=2
    #for ch in channel.split(','):
    ch = str(channel)
    if(int(ch) < 15):
        band='2.4'
    else:
        band='5'
    if(int(ch) < 15):
        freq='2.4GHz'
    else:
        freq='5GHz'
    if(standard=='11ax'):
        hdng=pltName+'_'+stbc
    elif(standard=='11ac'):
        hdng=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
    elif(standard=='11n'):
        hdng=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
    else:
        if(standard=='11b'):
            hdng=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+preamble
        else:
            hdng=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch
    #if(hdng not in paragraphs):
    document.add_heading(hdng, level=5)
    table = document.add_table(rows=1, cols=len(col_names_tables))
    table.style = 'TableGrid'
    hdr_cells = table.rows[0].cells
    for idx, name in enumerate(col_names_tables):
        paragraph = hdr_cells[idx].paragraphs[0]
        run = paragraph.add_run(name)
        run.bold = True
    #for dtr in data_rate.split(','):
    for dtr in standard_dataRate_dict[standard][streams][bw]:
        prev_evm = 'NA'
        prev_power = 'NA'
        if(streams=='2x2'):
            prev_evm_2 = 'NA'
            prev_power_2 = 'NA'
        data=[]
        data.append(standard)
        data.append(ch)
        data.append(dtr)
        #data.append(str(standard_evm_dict[standard][dtr]))
        data.append(str(standard_evm_dict[band][dtr]))

        row_cells = table.add_row().cells
        #row_cells[0].text = str(standard)
        #row_cells[1].text = str(ch)
        row_cells[0].text = str(dtr)
        #row_cells[1].text = str(standard_evm_dict[standard][dtr])
        row_cells[1].text = str(standard_evm_dict[band][dtr])

        for k in x:
            #if (txpower_evm_dict[k][2] > float(standard_evm_dict[standard][dtr])):
            if (txpower_evm_dict[k][2] > float(standard_evm_dict[band][dtr])):
                if (prev_evm == 'NA'):
                    power = round(txpower_evm_dict[k][0],1)
                    data.append(prev_power)
                    data.append(prev_evm)
                    data.append(txpower_evm_dict[k][0])
                    data.append(txpower_evm_dict[k][2])
                    data.append(power)
                    #row_cells[4].text = str(prev_power)
                    #row_cells[5].text = str(prev_evm)
                    #row_cells[6].text = str(txpower_evm_dict[k][0])
                    #row_cells[7].text = str(txpower_evm_dict[k][2])
                    row_cells[2].text = str(power)
                else:
                    #power = round(prev_power + ((float(standard_evm_dict[standard][dtr]) - prev_evm) * (txpower_evm_dict[k][0] - prev_power )/(txpower_evm_dict[k][2] - prev_evm)),1)
                    power = round(prev_power + ((float(standard_evm_dict[band][dtr]) - prev_evm) * (txpower_evm_dict[k][0] - prev_power )/(txpower_evm_dict[k][2] - prev_evm)),1)
                    data.append(prev_power)
                    data.append(prev_evm)
                    data.append(txpower_evm_dict[k][0])
                    data.append(txpower_evm_dict[k][2])
                    data.append(power)
                    #row_cells[4].text = str(prev_power)
                    #row_cells[5].text = str(prev_evm)
                    #row_cells[6].text = str(txpower_evm_dict[k][0])
                    #row_cells[7].text = str(txpower_evm_dict[k][2])
                    row_cells[2].text = str(power)
                break
            prev_evm = txpower_evm_dict[k][2]
            prev_power = txpower_evm_dict[k][0]
        if(streams=='2x2'):
            for k in x:
                #if (txpower_evm_dict[k][3] > float(standard_evm_dict[standard][dtr])):
                if (txpower_evm_dict[k][3] > float(standard_evm_dict[band][dtr])):
                    if (prev_evm_2 == 'NA'):
                        power_2 = round(txpower_evm_dict[k][1],1)
                        data.append(prev_power_2)
                        data.append(prev_evm_2)
                        data.append(txpower_evm_dict[k][1])
                        data.append(txpower_evm_dict[k][3])
                        data.append(power)
                        data.append(min(power,power_2))
                        #row_cells[9].text = str(prev_power_2)
                        #row_cells[10].text = str(prev_evm_2)
                        #row_cells[11].text = str(txpower_evm_dict[k][1])
                        #row_cells[12].text = str(txpower_evm_dict[k][3])
                        row_cells[3].text = str(power_2)
                        row_cells[4].text = str(min(power,power_2))
                    else:
                        #power_2 = round(prev_power_2 + ((float(standard_evm_dict[standard][dtr]) - prev_evm_2) * (txpower_evm_dict[k][1] - prev_power_2 )/(txpower_evm_dict[k][3] - prev_evm_2)),1)
                        power_2 = round(prev_power_2 + ((float(standard_evm_dict[band][dtr]) - prev_evm_2) * (txpower_evm_dict[k][1] - prev_power_2 )/(txpower_evm_dict[k][3] - prev_evm_2)),1)
                        data.append(prev_power_2)
                        data.append(prev_evm_2)
                        data.append(txpower_evm_dict[k][1])
                        data.append(txpower_evm_dict[k][3])
                        data.append(power_2)
                        data.append(min(power,power_2))
                        #row_cells[9].text = str(prev_power_2)
                        #row_cells[10].text = str(prev_evm_2)
                        #row_cells[11].text = str(txpower_evm_dict[k][1])
                        #row_cells[12].text = str(txpower_evm_dict[k][3])
                        row_cells[3].text = str(power_2)
                        row_cells[4].text = str(min(power,power_2))
                    break
                prev_evm_2 = txpower_evm_dict[k][3]
                prev_power_2 = txpower_evm_dict[k][1]
        worksheet_maxtxpower.write_row('A'+str(row_num), data)
        row_num+=1

    workbook_maxtxpower.close()
    try:
        document.save(max_document_path)
    except:
        document.save(max_document_path+'_'+str(time.time())+'.docx')

def plot_power_evm_png(ch):
    for dtr in data_rate.split(','):
        if(streams=='1x1'):
            col_names=['Power-Stream1','EVM-Stream1']
        else:
            col_names=['Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2']

        for label in col_names:
            plt.plot(txpower_dict[dtr],power_evm_dict[ch][dtr][label],label=label,linewidth=3)

        if(int(ch) < 15):
            freq='2.4GHz'
        else:
            freq='5GHz'
        if(standard=='11ax'):
            cnsl_fname=pltName+'_'+str(dtr)
            drt=str(dtr)
        elif(standard=='11ac'):
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dtr)
            drt=str(dtr)
        elif(standard=='11n'):
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc+'_'+str(dtr)
            drt=str(dtr)
        else:
            if(standard=='11b'):
                cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+preamble+'_'+str(dtr)+'Mbps'
            else:
                cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+str(dtr)+'Mbps'
        plt.title(cnsl_fname)
        plt.ylabel('- EVM (dB)/VSA Power', fontsize = 13)
        plt.xlabel('DUT TX Power (dBm))', fontsize = 13)
        plt.grid()
        lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
        img_plot_path=os.path.join(op_file_path,cnsl_fname+'.png')
        plt.savefig(img_plot_path,bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
        plt.cla()
        save_to_doc(cnsl_fname,img_plot_path,freq,ch)

def tx_evm_power_analysis(DUT_TestConfigParams,dut1):
    #controlPowerSwitch(on_ports_list='8',off_ports_list='8')
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
    global workbook_dr
    global worksheet
    global worksheet_dr
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
    hetbRual = ''
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
            hetbRual = '_RUAL_' + str(DUT_TestConfigParams.ruAllocation)
        dcm = 'DCM_'*DUT_TestConfigParams.dcm
        doppler = ('doppler'+str(DUT_TestConfigParams.midamblePeriodicity)+'_')*DUT_TestConfigParams.doppler
        pltName = pktFrameFormat+hetbRual+'_Chn'+str(channel)+'_'+bw+'Mhz_'+giType+'GI_'+heLtfType+'LTF_'+dcm+doppler+tone+coding+'_'+stbc

##    if((standard=='11a')or(standard=='11g')):
##        if(len(sys.argv)  !=9):
##            print("""Usage:python rx_iqxel280.py <11a/11g> <streams> <OFDM> <BW> <data-rate> <start_amp> <End_amp> <Step_Size> <Channel> <Payload_len> <COM-Port> <RF_Port> <Release_Tag>
##                        \n\n\tEx: python rx_iqxel160.py 11a 1x1 OFDM 20 6 -30 -80 10 36 1024 COM9 RF1 TZ5000_INT_REL_33""")
##            exit(0)
##    elif(standard=='11b'):
##        if(len(sys.argv)  !=10):
##            print("""Usage:python rx_iqxel280.py <11b> <streams> <DSSS> <BW> <data-rate> <Preamble> <start_amp> <End_amp> <Step_Size> <Channel> <Payload_len> <COM-Port> <RF_Port> <Release_Tag>
##                        \n\n\tEx:python rx_iqxel160.py 11b 1x1 DSSS 20 5.5 LONG -30 -80 10 6 1024 COM9 RF1 TZ5000_INT_REL_33""")
##            exit(0)
##
##    elif(standard=='11n'):
##        if(len(sys.argv)  !=13):
##            print("""Usage:python rx_iqxel280.py <11ac> <streams> <OFDM> <BW> <data-rate> <STBC> <GI> <Coding> <Mixed/GF> <start_amp> <End_amp> <Step_Size> <Channel> <Payload_len> <COM-Port> <dutModel> <Release_Tag>
##                        \n\n\tEx: python rx_iqxel160.py 11ac 1x1 OFDM 80 MCS0 STBC SGI LDPC Mixed -30 -80 10 36 1024 COM9 RF1 TZ5000_INT_REL_33""")
##            exit(0)
##    elif(standard=='11ac'):
##        if(len(sys.argv)  !=12):
##            print("""Usage:python rx_iqxel280.py <11ac> <streams> <OFDM> <BW> <data-rate> <STBC> <GI> <Coding> <start_amp> <End_amp> <Step_Size> <Channel> <Payload_len> <COM-Port> <RF_Port> <Release_Tag>
##                        \n\n\tEx: python rx_iqxel160.py 11ac 1x1 OFDM 80 MCS0 STBC SGI LDPC -30 -80 10 36 1024 COM9 RF1 TZ5000_INT_REL_33""")
##            exit(0)
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
    if(pktFrameFormat =='HETB'):
        equipment.apply_vsa(int(ch),bw,streams,DUT_TestConfigParams.sta20Moffset)
    else:
        equipment.apply_vsa(int(ch),bw,streams)
    if(standard=='11ax'):
        cnsl_fname = pltName
    elif(standard=='11ac'):
        cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
    elif(standard=='11n'):
        cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
    else:
        if(standard=='11b'):
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+preamble
        else:
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch
    consld_fname=os.path.join(op_file_path,'TX_Consolidated_'+cnsl_fname+'.xlsx')
    DebugPrint(consld_fname)
    workbook = xlsxwriter.Workbook(consld_fname)
    worksheet = workbook.add_worksheet()
    bold1 = workbook.add_format({'bold': 1})
    result_log_path = os.path.abspath('../Results/')
    result_log_path=os.path.join(result_log_path,DUT_TestConfigParams.release)
    result_log_path=os.path.join(result_log_path,'result_log_path_'+release+'.txt')
    f_log_path=open(result_log_path,'a+')
    f_log_path.write('\nPOWER_EVM_'+cnsl_fname+'->'+op_file_path)
    f_log_path.close()

    for dr in data_rate.split(','):
        if dr not in power_evm_dict[ch].keys():
            power_evm_dict[ch][dr]={}

        if(standard=='11ax'):
            fname=pltName+'_'+str(dr)
        elif(standard=='11ac'):
            fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
        elif(standard=='11n'):
            fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc+'_'+str(dr)
        else:
            if(standard=='11b'):
                fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+preamble+'_'+str(dr)+'Mbps'
            else:
                fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+str(dr)+'Mbps'
        dr_file_name=os.path.join(op_file_path,'TX_'+fname+'.xlsx')
        workbook_dr = xlsxwriter.Workbook(dr_file_name)
        worksheet_dr = workbook_dr.add_worksheet()
        bold = workbook_dr.add_format({'bold': 1})
        dut.set_dut_datarate(dr,standard)
        if(pktFrameFormat =='HETB'):
            equipment.configVsaHETB(DUT_TestConfigParams)
        dut_txpower_loop(DUT_TestConfigParams,ch,dr)
        #f_time.write(str(time.time()))
        workbook_dr.close()
        #copy_file(op_dr_file_path=dr_file_name,dutModel=dutModel,release=release,standard=standard,streams=streams_chain,stbc=stbc,coding=coding,gi=gi,greenfield_mode=greenfield_mode,preamble=preamble,ch=ch,test='tx')
    try:
        plot_power_evm(ch)
        workbook.close()
    except Exception,e:
        print e.args
        print "plot_power_evm(ch)"
        workbook.close()
        pass
    try:
        plot_power_evm_png(ch)
    except Exception,e:
        print e.args
        print "plot_power_evm_png(ch)"
        pass
    #copy_file(op_dr_file_path=consld_fname,dutModel=dutModel,release=release,standard=standard,streams=streams_chain,stbc=stbc,coding=coding,gi=gi,greenfield_mode=greenfield_mode,preamble=preamble,ch=ch,test='tx')
    #get_best_txpower_from_evm()

    #write_max_txpower()
    #dut.pktgen_tool(DUT_TestConfigParams,'kill')
    #copy_file(op_dr_file_path=document_path,dutModel=dutModel,release=release,test='tx')
    #copy_file(op_dr_file_path=max_document_path,dutModel=dutModel,release=release,test='tx')
    equipment.close_vsg()
    dut.dut_close()