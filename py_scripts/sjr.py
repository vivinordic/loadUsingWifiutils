#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     06/09/2021
# Copyright:   (c) vivi 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import harness

from rs import *
from iqxel import *
from common_utils import *
from harness import *
import numpy
from DUT_functions import *

rw_num=1


#Loop iterating for the range of amplitudes mentioned
def amplitude_loop(dr,ch,workbook,workbook_dr,worksheet,worksheet_dr,standard,cable_loss,DUT_TestConfigParams):
    start_amp_list=[]
    global row_num
    global sjr_evenrow_dict
    sjr_evenrow_dict={}
    global sjr_oddrow_dict
    sjr_oddrow_dict={}
    global even_xaxis
    global odd_xaxis
    global data
    global row_num_dr
    row_num_dr=2
    bold1 = workbook.add_format({'bold': 1})
    bold = workbook_dr.add_format({'bold': 1})

    worksheet.write_row('A1',['Standard','Channel','DataRate','SJR']+rx_report_hdngs,bold1)
    worksheet_dr.write_row('A1',['Standard','Channel','DataRate','SJR']+rx_report_hdngs,bold)

    axis_num=1
    flg=0
    a=1

    for amp in ampl_dict[dr]:
        print "--------------------------------------------------------VSG power level",amp  #PHY_PERFORMANCE
        #PHY_PERFORMANCE: instead of hardcoding in the range of -60, the xls is updated such that these are -58 to -62 without considering cable loss.
        #print "Hardcoding power level for calder, setting power to -60, cable loss to 0\n",  #PHY_PERFORMANCE
        #amp=-60;
        #cable_loss=0
        #print "---------------------------------------------hardcoded VSG power level",amp  #PHY_PERFORMANCE
        data=[]
        data.append(standard)
        data.append(int(ch))
        try:
            data.append(int(dr))
        except:
            data.append(dr)
        data.append(amp - DUT_TestConfigParams.jammer_amplt)
        if(flg==0):
            # if(ampl_dict[dr].index(amp)==0):
                # equipment.set_amplitude(vsg_streams,str(amp))
                # start_per(modulation,dr,ch,vsg_streams,standard,tester,dut,equipment)
            equipment.set_amplitude(vsg_streams,str(amp))
            equipment.set_aci_amplitude(vsg_streams,str(DUT_TestConfigParams.jammer_amplt))
            equipment.rf_on_off_jammer(rf_state='on',streams=vsg_streams,chain_sel=2)
            data=data+start_per(modulation,dr,ch,vsg_streams,standard,tester,dut,equipment)
            if(data[4] < 800 ):# and ((ampl_dict[dr].index(amp)==0) or (ampl_dict[dr].index(amp)==1))):
                time.sleep(1)
                dut.set_dut_channel(ch)
                for i in range(num_params_to_pop):
                    data.pop()
                data=data+start_per(modulation,dr,ch,vsg_streams,standard,tester,dut,equipment)
            if((data[4] > 3000) and ('IQXEL' in tester)):
                time.sleep(1)
                for i in range(num_params_to_pop):
                    data.pop()
                data=data+start_per(modulation,dr,ch,vsg_streams,standard,tester,dut,equipment)
            DebugPrint(data)
            if(data[4]=='LOCKUP'):
                for i in range(num_params_to_pop):
                    data.pop()
                if(dut.check_dut_stuck_state()=='alive'):
                    dut.dut_reboot()
                else:
                    print 'DUT is stuck'
                    controlPowerSwitch(on_ports_list='8',off_ports_list='8')
                time.sleep(reboot_time)
                dut.init_dut(standard=standard,streams=streams,channel=ch,bw=bw,release=release,chain_sel=chain_sel)
                dut.set_dut_production_mode_settings(standard=standard,ch=ch,bw=bw)
                dut.set_dut_channel(ch)
                data=data+start_per(modulation,dr,ch,vsg_streams,standard,tester,dut,equipment)
                DebugPrint(data)
            if(a==1):
                prev_data=list(data[4:])
                curr_data=list(data[4:])
            else:
                prev_data=list(curr_data)
                curr_data=list(data[4:])
            # if((a!=1) and (not(cmp(prev_data,curr_data)))):
                # print 'COMPARED'
                # for i in range(13):
                    # data.pop()
                # data=data+start_per(modulation,dr,ch,vsg_streams,standard,dut,equipment)
            a+=1
        worksheet.write_row('A'+str(row_num), data)
        worksheet_dr.write_row('A'+str(row_num_dr), data)
        sjr_amp_dict[dr].append(float(data[-1]))
        row_num=row_num+1
        row_num_dr=row_num_dr+1
        axis_num=axis_num+1
        ftime.write(time.strftime("%H-%M-%S")+"\n")
    row_num=row_num+1

#Plot sjr for single data rate sheet
def plot_dr_sjr(dr,workbook_dr,worksheet_dr):
    chart_dr = workbook_dr.add_chart({'type': 'line'})
    endval=len(amplitude_list)+1
    strval=2
    if((standard=='11n')or(standard=='11ac')):
        name=standard+'_'+streams_chain+'_'+freq+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
        drt=str(dr)
    elif(standard=='11ax'):
        drt=str(dr)
        name=pltName+'_'+str(dr)
    else:
        if(standard=='11b'):
            name=standard+'_'+streams_chain+'_'+freq+'_'+preamble+'_'+str(dr)+'Mbps'
        else:
            name=standard+'_'+streams_chain+'_'+freq+'_'+str(dr)+'Mbps'
        drt=str(dr)+'Mbps'

    chart_dr.add_series({
        'name':       dr,
        'categories': '=Sheet1!$D$2:$D$'+str(len(amplitude_list)+1),
        'values':  '=Sheet1!$Q2:Q'+str(len(amplitude_list)+1)
    })
    chart_dr.set_title ({'name': name})
    chart_dr.set_x_axis({'name': 'Signal Strength (dBm)','position_axis': 'on_tick'})
    chart_dr.set_y_axis({'name': 'PER (%)'})
    chart_dr.set_style(10)
    worksheet_dr.insert_chart('R2', chart_dr, {'x_offset': 5, 'y_offset': 5})

#Plot sjr for all data rates in a single sheet
def plot_all_sjr(workbook,worksheet,ch=''):
    chart1 = workbook.add_chart({'type': 'line'})
    chart_dr = workbook.add_chart({'type': 'line'})
    endval=len(amplitude_list)+1
    strval=2
    x=2
    for dr in data_rate.split(','):
        chart_dr = workbook.add_chart({'type': 'line'})

        chart1.add_series({
            'name':       dr,
            'categories': '=Sheet1!$D$2:$D$'+str(len(amplitude_list)+1),
            'values':  '=Sheet1!$Q'+str(strval)+':Q'+str(endval)
        })
        chart_dr.add_series({
                'name':       dr,
                'categories': '=Sheet1!$D$2:$D$'+str(len(amplitude_list)+1),
                'values':  '=Sheet1!$Q'+str(strval)+':Q'+str(endval)
        })

        strval=strval+len(amplitude_list)+1
        endval=endval+len(amplitude_list)+1

        if((standard=='11n')or(standard=='11ac')):
            name_dr=standard+'_'+streams_chain+'_'+freq+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
            drt=str(dr)
        elif(standard=='11ax'):
            name_dr=pltName+'_'+str(dr)
            drt=str(dr)
        else:
            if(standard=='11b'):
                name_dr=standard+'_'+streams_chain+'_'+freq+'_'+preamble+'_'+str(dr)+'Mbps'
            else:
                name_dr=standard+'_'+streams_chain+'_'+freq+'_'+str(dr)+'Mbps'
            drt=str(dr)+'Mbps'
        chart_dr.set_title ({'name': name_dr})
        chart_dr.set_x_axis({'name': 'Signal Strength (dBm)','position_axis': 'on_tick'})
        chart_dr.set_y_axis({'name': 'PER (%)'})
        chart_dr.set_style(10)
        worksheet.insert_chart('X'+str(x), chart_dr, {'x_offset': 5, 'y_offset': 5})
        x=x+15

    if(standard=='11ac'):
        name=standard+'_'+streams_chain+'_'+freq+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
    elif(standard=='11ax'):
        name=pltName+'_'+str(dr)
    elif(standard=='11n'):
        name=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(ch)+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
    else:
        if(standard=='11b'):
            name=standard+'_'+streams_chain+'_'+freq+'_'+preamble
        else:
            name=standard+'_'+streams_chain+'_'+freq
    chart1.set_title ({'name': name})
    chart1.set_x_axis({'name': 'Signal Strength(dBm)','position_axis': 'on_tick'})
    chart1.set_y_axis({'name': 'PER (%)'})
    chart1.set_style(10)
    worksheet.insert_chart('R2', chart1, {'x_offset': 5, 'y_offset': 5})
    print 'END OF CHART'

def save_to_doc(hdng,imag,freq,chn):
    global document_path
    document_path=os.path.join(op_file_path.split(standard)[0],'RX_SJR_'+release+'_'+board_num+'_'+rf_num+'.docx')
    print(document_path)
    try:
        document = Document(document_path)
    except:
        document = Document()
    paragraphs_obj=document.paragraphs
    paragraphs=[]
    for p in paragraphs_obj:
        paragraphs.append(p.text)
    if(release+" RX Performance" not in paragraphs):
        document.add_heading(release+" RX Performance", level=1)
    if('SJR Bathtub Curves' not in paragraphs):
        document.add_heading('SJR Bathtub Curves', level=2)
    if(standard=='11ac'):
        if("VHT - Channel-"+str(chn) not in paragraphs):
            document.add_heading("VHT - Channel-"+str(chn), level=3)
    elif(standard=='11ax'):
        if("HE - Channel-"+str(chn) not in paragraphs):
            document.add_heading("HE - Channel-"+str(chn), level=3)
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

def plot_sjr_png(DUT_TestConfigParams):
    sjr_plot_list=[]
    fig = plt.figure()
    for amp in amplitude_list:
        sjr_plot_list.append(amp - DUT_TestConfigParams.jammer_amplt)
    for dtr in data_rate.split(','):
        plt.plot(sjr_plot_list,sjr_amp_dict[dtr],label=dtr,linewidth=3.0)
    ax=plt.gca()
    ax.invert_xaxis()
    if(standard=='11ac'):
        cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
    elif(standard=='11ax'):
        cnsl_fname=pltName
    elif(standard=='11n'):
        cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
    else:
        if(standard=='11b'):
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)+'_'+preamble
        else:
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)
    plt.title(cnsl_fname)
    plt.ylabel('PER (%)', fontsize = 13)
    plt.xlabel('Signal Strength (dBm)', fontsize = 13)
    plt.grid()
    lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
    img_plot_path=os.path.join(op_file_path,cnsl_fname+'.png')
    plt.savefig(img_plot_path,bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
    save_to_doc(cnsl_fname,img_plot_path,freq,str(channel))
    result_log_path = os.path.abspath('../Results/')
    result_log_path=os.path.join(result_log_path,release)
    result_log_path=os.path.join(result_log_path,'result_log_path_'+release+'.txt')
    f_log_path=open(result_log_path,'a')
    f_log_path.write('\nPER_'+cnsl_fname+'->'+op_file_path)
    f_log_path.close()
    plt.close(fig)
#if __name__ == "__main__":


def sjr_analysis(DUT_TestConfigParams,dut1):
    #controlPowerSwitch(on_ports_list='8',off_ports_list='8')
    global ftime
    global equipment
    global dut
    global vsg_streams
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
    global ampl_dict
    ampl_dict={}
    greenfield_mode=stbc=preamble=gi=coding=preamble=''
    ftime=open('total_time','a')
    ftime.write(time.strftime("%H-%M-%S")+"\n")
    global sjr_amp_dict
    global amplitude_list
    global tester
    global giType
    global heLtfType
    global pktFrameFormat
    global pltName

    sjr_amp_dict = {}
    row_num=2
    dut = dut1

    print "In sjr_analysis() of sjr.py\n "

##    if(len(sys.argv) ==1):
##        print("""Usage:python rx_iqxel280.py <11ac> <streams> <OFDM> <BW> <data-rate> <start_amp> <End_amp> <Step_Size> <Channel> <Payload_len> <COM-Port> <RF_Port> <Release_Tag>
##                        \n\n\tEx: python rx_iqxel280.py 11ac 1x1 OFDM 80 MCS0 SGI LDPC -30 -80 10 36 1024 COM9 RF1 TZ5000_INT_REL_33""")
##        exit(0)
    standard = DUT_TestConfigParams.standard #standard=sys.argv[1].lower()
    #streams_chain=sys.argv[2]
    streams=DUT_TestConfigParams.streams        #streams=streams_chain.split('_')[0]
    chain_sel=DUT_TestConfigParams.chain_sel    #chain_sel=streams_chain.split('_')[-1]
    streams_chain = streams+'_'+str(chain_sel)
    bw=DUT_TestConfigParams.bw                 #bw=sys.argv[3]
    data_rate=DUT_TestConfigParams.data_rate #data_rate=sys.argv[4]
    dutModel=DUT_TestConfigParams.dutModel
    start_amplt=DUT_TestConfigParams.start_amplt       #start_amplt=int(sys.argv[6])
    end_amplt=DUT_TestConfigParams.end_amplt           #end_amplt=int(sys.argv[7])
    step_size=DUT_TestConfigParams.step_size           #step_size=float(sys.argv[8])
    channel=int(DUT_TestConfigParams.channel)               #channel=sys.argv[9]
    payload=DUT_TestConfigParams.payload               #payload=sys.argv[10]
    if(standard=='11b'):
        preamble=DUT_TestConfigParams.preamble              #preamble=sys.argv[5]
    elif((standard=='11ac')or(standard=='11n')):
        stbc=DUT_TestConfigParams.stbc#stbc=sys.argv[5]
        gi=DUT_TestConfigParams.gi#gi=sys.argv[6]
        coding=DUT_TestConfigParams.coding#coding=sys.argv[7]
        if(standard=='11n'):
            greenfield_mode=DUT_TestConfigParams.greenfield_mode#greenfield_mode=sys.argv[8]
    elif(standard=='11ax'):
        stbc=DUT_TestConfigParams.stbc
        gi=DUT_TestConfigParams.gi
        coding=DUT_TestConfigParams.coding
        giType = str(0.8*(1<<DUT_TestConfigParams.giType))+'us'
        heLtfType = str((1<<DUT_TestConfigParams.heLtfType))+'x'
        tone = ''
        hemu_ru = ''
        if(DUT_TestConfigParams.format == 5):
            pktFrameFormat='HESU'
        elif(DUT_TestConfigParams.format == 6):
            pktFrameFormat='HEMU'
            ruAlloc = DUT_TestConfigParams.ruAllocation
            staId = DUT_TestConfigParams.desiredStaIDlist
            hemu_ru = 'RUAL_' + str(ruAlloc) + '_STAID_' + staId + '_'
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
        pltName = pktFrameFormat+'_Chn'+str(channel)+'_'+bw+'Mhz_'+giType+'GI_'+heLtfType+'LTF_'+dcm+doppler+tone+hemu_ru+coding+'_'+stbc


    if(int(channel)<30):
        freq='2.4GHz'
    else:
        freq='5GHz'
    op_file_path=BuildResultsPath(DUT_TestConfigParams)
    time.sleep(0.5)
    if(standard=='11b'):
        modulation='DSSS'
    else:
        modulation='OFDM'
    ftime.write(time.strftime("%H-%M-%S")+"\n")
    DebugPrint(create='1')
    DebugPrint('Started')
    #target = 'Simulator rpusim-echo520-main@393-internal_config0057'
    #dut=eval(dutModel)(target)
    tester = DUT_TestConfigParams.vsg
    #tester = "IQXEL_280"
    equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
    #equipment=eval(tester.split('_')[0])(tester,"10.90.88.137")
    DebugPrint('Trying to initialize dut in sjr Main')
    vsg_streams=streams
    if(stbc=='STBC_1'):
        vsg_streams='1x1'
        chain_sel=1

    if(dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,release=release,chain_sel=chain_sel)=='CONNECT_FAIL'):
        print 'CONNECT_FAIL'
        DebugPrint('CONNECT_FAIL in sjr Main')
        controlPowerSwitch(on_ports_list='8',off_ports_list='8')
        if(dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,release=release,chain_sel=chain_sel)=='CONNECT_FAIL'):
            print 'Switching to Serial Access'
            DebugPrint('Switching to Serial Access')
            dutModel=dutModel.split('_')[0]
            dut=eval(dutModel)(com_port)
            equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
            dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,release=release,chain_sel=chain_sel)

    dut.dut_down_up(action='up_down')
    DUT_functions.startTestcase()

    try:
        equipment.init_vsg_funcs(standard=standard,bw=bw,streams=vsg_streams,stbc=stbc,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,payload=payload,chain_sel=str(chain_sel))
        if(standard == '11ax'):
            equipment.configHE(DUT_TestConfigParams)
            print("configured HE")
        equipment.rf_on_off(rf_state='off',streams=streams)
    except Exception,e:
        print 'Equipment is not reachable'
        exit(0)
    for dr in data_rate.split(','):
        amplitude_list=[]
        steps_list=list(numpy.arange(end_amplt,start_amplt+1,step_size))
        steps_list.reverse()
        for j in steps_list:
            amplitude_list.append(j)
        # if 0 not in amplitude_list:
            # amplitude_list=[0]+amplitude_list
        ampl_dict[dr]=amplitude_list
        sjr_amp_dict[dr]=[]
    #for ch in channel.split(','):
    if(int(channel)<30):
        freq='2.4GHz'
    else:
        freq='5GHz'
    if(1 <= int(channel) <= 14):
        cable_loss_band='24G_BAND'
    if(36 <= int(channel) <= 52):
        cable_loss_band='5G_BAND1'
    elif(53 <= int(channel) <= 108):
        cable_loss_band='5G_BAND2'
    elif(109 <= int(channel) <= 132):
        cable_loss_band='5G_BAND3'
    elif(133 <= int(channel) <= 165):
        cable_loss_band='5G_BAND4'
    cable_loss_1x1=cable_loss_dict['1x1'][cable_loss_band]
    cable_loss=cable_loss_2x2=cable_loss_1x1
    if(streams=='2x2'):
        cable_loss_2x2=cable_loss_dict['2x2'][cable_loss_band]
        cable_loss=float((cable_loss_1x1+cable_loss_2x2)/2)
    dut.set_dut_production_mode_settings(standard=standard,ch=channel,bw=bw)
    dut.set_dut_channel(channel)
    equipment.apply_vsg(bw=bw,chn=channel,streams=vsg_streams)
    equipment.set_macheader()
    equipment.set_payload(standard,payload)
    if(standard=='11ac'):
        cnsl_fname=standard+'_'+ streams_chain +'_'+freq+'_Chn'+str(channel)+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
        # cnsl_fname=bw+'MHz'
    elif(standard=='11ax'):
        cnsl_fname = pltName
    elif(standard=='11n'):
        cnsl_fname=standard+'_'+ streams_chain +'_'+freq+'_Chn'+str(channel)+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
        # cnsl_fname=bw+'MHz'
    else:
        if(standard=='11b'):
            cnsl_fname=standard+'_'+streams + str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+preamble
        else:
            cnsl_fname=standard+'_'+streams + str(chain_sel)+'_'+freq+'_Chn'+str(channel)
        # cnsl_fname=''
    consld_fname=os.path.join(op_file_path,'SJR_Consolidated_'+cnsl_fname+'.xlsx')
    print(consld_fname)
    workbook = xlsxwriter.Workbook(consld_fname)
    worksheet = workbook.add_worksheet()
    bold1 = workbook.add_format({'bold': 1})
    # PHY_PERFORMANCE: is this the right place to call these? I think, this can be moved to start of this function.
##    DUT_functions.startNextCase() # PHY_PERFORMANCE - this was missing and is a bug
##    DUT_functions.startTestcase() # PHY_PERFORMANCE - this was missing and is a bug - without this DUT test wont start

    print "Test loop for different rate ...\n"
    if(standard=='11ax'):
        if (pktFrameFormat=='HEMU'):
            dut.dut_setStaID(int(DUT_TestConfigParams.desiredStaIDlist))
    for dr in data_rate.split(','):
        if(str(dr).lower().find('mcs')>=0):
            if(standard=='11ac'):
                fname=standard+'_'+streams+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
            if(standard=='11ax'):
                fname=pltName+'_'+str(dr)
            elif(standard=='11n'):
                fname=standard+'_'+streams+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+'_'+greenfield_mode+'_'+stbc+'_'+str(dr)
        else:
            if(standard=='11b'):
                fname=standard+'_'+streams+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+preamble+'_'+str(dr)+'Mbps'
            else:
                fname=standard+'_'+streams+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+str(dr)+'Mbps'
        dr_file_name=os.path.join(op_file_path,'sjr_'+fname+'.xlsx')
        workbook_dr = xlsxwriter.Workbook(dr_file_name)
        worksheet_dr = workbook_dr.add_worksheet()
        bold = workbook_dr.add_format({'bold': 1})
        print "calling set_datarate()\n"
        equipment.set_datarate(modulation,standard,dr)
        # Setting datarate for all users in case of HEMU packet
        if(standard=='11ax'):
            if (pktFrameFormat=='HEMU'):
                equipment.setDatarateAllUser(DUT_TestConfigParams.numUser, dr)

        print "calling generate_waveform()\n"
        equipment.generate_waveform(streams=vsg_streams)
        ftime.write("AMP LOOP START"+time.strftime("%H-%M-%S")+"\n")
        print "calling amplitude_loop()\n"
        equipment.configJammer(DUT_TestConfigParams)
        amplitude_loop(dr,channel,workbook,workbook_dr,worksheet,worksheet_dr,standard,cable_loss,DUT_TestConfigParams)
        ftime.write("AMP LOOP END"+time.strftime("%H-%M-%S")+"\n")
        plot_dr_sjr(dr,workbook_dr,worksheet_dr)
        workbook_dr.close()
    plot_all_sjr(workbook,worksheet,ch=channel)
    try:
        workbook.close()
    except:
        time.sleep(10)
        try:
            workbook.close()
        except:
            pass
    #copy_file(consld_fname,ch)
    try:
        plot_sjr_png(DUT_TestConfigParams)
    except Exception as e:
        print(e)
        pass
    equipment.rf_on_off(rf_state='off',streams=vsg_streams)
    equipment.close_vsg()
    dut.dut_close()