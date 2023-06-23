#-------------------------------------------------------------------------------
# Name:        ACI Detection
# Purpose:     This script will generate ED detection percentage vs signal strength for different channels.
# Author:      Avinash.Nathala
# Created:     25-07-2019
# Copyright:   Imagination Technologies Ltd
#-------------------------------------------------------------------------------

from rs import *
from iqxel import *
from common_utils import *
from input import *
from harness import *
##from CSUtils import DA
import numpy

rw_num=1
idleInterval = 100
maxPktDuration = 5000
numPkts = 1000
transmitTime = ((idleInterval+maxPktDuration)*numPkts)/(10**6) #1000 packets transmit duration

#Loop iterating for the range of amplitudes mentioned
def amplitudeLoop(dr,dutch,ch,amplitude_list,workbook,workbook_aci,worksheet,worksheet_aci,standard,cable_loss):
    global data
    global edDetection_dict
    global row_num_aci
    global row_num
    row_num_aci=2
    bold1 = workbook.add_format({'bold': 1})
    bold  = workbook_aci.add_format({'bold': 1})
    worksheet_aci.write_row('A1',['Standard','dutChannel','iqxlChannel','DataRate','AMPLITUDE','ED_CNT','CRC32_PASS_CNT','CRC32_FAIL_CNT','L1_CORR_FAIL_CNT','OFDM_S2L_FAIL_CNT','LSIG_FAIL_CNT','HTSIG_FAIL_CNT','VHTSIGA_FAIL_CNT','VHTSIGB_FAIL_CNT','DSSS_CORR_PASS_CNT','DSSS_SFD_FAIL_CNT','DSSS_HDR_FAIL_CNT'],bold1)
    worksheet.write_row('A1',['Standard','dutChannel','iqxlChannel','DataRate','AMPLITUDE','ED_CNT','CRC32_PASS_CNT','CRC32_FAIL_CNT','L1_CORR_FAIL_CNT','OFDM_S2L_FAIL_CNT','LSIG_FAIL_CNT','HTSIG_FAIL_CNT','VHTSIGA_FAIL_CNT','VHTSIGB_FAIL_CNT','DSSS_CORR_PASS_CNT','DSSS_SFD_FAIL_CNT','DSSS_HDR_FAIL_CNT'],bold1)
    axis_num=1
    for ampIdx in ampl_dict[dr]:
        data=[]
        data.append(standard)
        data.append(int(dutch))
        data.append(int(ch))
        try:
            data.append(int(dr))
        except:
            data.append(dr)
        data.append(ampIdx-cable_loss)
        equipment.set_amplitude(vsg_streams,str(ampIdx))
        equipment.rf_on_off(rf_state='off',streams=streams)
        res=dut.dut_down_up(action='up',ch=ch)
        equipment.send_packets(streams=streams,action='run')
        time.sleep(transmitTime)
        [res,per]=dut.get_phy_stats()
        if(len(res)>0):
            ed_cnt = res[0]
            if(modulation.lower()=='ofdm'):
                crc32_pass_cnt=res[1]
                crc32_fail_cnt=res[2]
            else:
                crc32_pass_cnt=res[3]
                crc32_fail_cnt=res[4]
        data.append(ed_cnt)   # ED Count
        data.append(crc32_pass_cnt)
        data.append(crc32_fail_cnt)
        data.append(res[7])  # l1_corr_fail_cnt
        data.append(res[12])  # ofdm_s2l_fail_cnt
        data.append(res[8])  # lsig_fail_cnt
        data.append(res[9])  # htsig_fail_cnt
        data.append(res[10])  # vhtsiga_fail_cnt
        data.append(res[11])  # vhtsigb_fail_cnt
        data.append(res[6])  # dsss_corr_pass_cnt
        data.append(res[15])  # dsss_sfd_fail_cnt
        data.append(res[16])  # dsss_hdr_fail_cnt
        worksheet.write_row('A'+str(row_num), data)
        worksheet_aci.write_row('A'+str(row_num_aci), data)
        edDetection_dict[dr].append(ed_cnt*100/numPkts)
        row_num=row_num+1
        row_num_aci=row_num_aci+1
        axis_num=axis_num+1
        ftime.write(time.strftime("%H-%M-%S")+"\n")
    row_num=row_num+1

#Plot ACI for single data rate sheet
def plotSigPwrVsEd(dr,workbook_aci,worksheet_aci):
    chart_dr = workbook_aci.add_chart({'type': 'line'})
    endval=len(amplitude_list)+1
    strval=2
    if((standard=='11n')or(standard=='11ac')):
        name=standard+'_'+streams_chain+'_'+freq+'_'+bw+'MHz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
        drt=str(dr)
    else:
        if(standard=='11b'):
            name=standard+'_'+streams_chain+'_'+freq+'_'+preamble+'_'+str(dr)+'Mbps'
        else:
            name=standard+'_'+streams_chain+'_'+freq+'_'+str(dr)+'Mbps'
        drt=str(dr)+'Mbps'

    chart_dr.add_series({
        'name':       dr,
        'categories': '=Sheet1!$E$2:$E$'+str(len(amplitude_list)+1),
        'values':  '=Sheet1!$F2:F'+str(len(amplitude_list)+1)
    })
    chart_dr.set_title ({'name': name})
    chart_dr.set_x_axis({'name': 'Signal Strength (dBm)','position_axis': 'on_tick'})
    chart_dr.set_y_axis({'name': 'edDetection'})
    chart_dr.set_style(10)
    worksheet_aci.insert_chart('AG2', chart_dr, {'x_offset': 5, 'y_offset': 5})

#Plot ACI tests for all cases in a single sheet
def plotAciTestResults(workbook,worksheet,ch=''):
    chart1 = workbook.add_chart({'type': 'line'})
    chart_dr = workbook.add_chart({'type': 'line'})
    endval=len(amplitude_list)+1
    strval=2
    x=2
    for dr in data_rate.split(','):
        chart_dr = workbook.add_chart({'type': 'line'})
        chart1.add_series({
            'name':       data_rate,
            'categories': '=Sheet1!$E$2:$E$'+str(len(amplitude_list)+1),
            'values':  '=Sheet1!$F'+str(strval)+':F'+str(endval)
        })
        chart_dr.add_series({
                'name':       dr,
                'categories': '=Sheet1!$D$2:$D$'+str(len(amplitude_list)+1),
                'values':  '=Sheet1!$AF'+str(strval)+':AF'+str(endval)
        })

        strval=strval+len(amplitude_list)+1
        endval=endval+len(amplitude_list)+1

        if(standard=='11ac'):
            name_dr=standard+'_'+streams_chain+'_'+freq+'_'+bw+'MHz_'+gi+'_'+coding+'_'+stbc
            drt=str(dr)
        elif(standard=='11n'):
            name_dr=standard+'_'+streams_chain+'_'+freq+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
            drt=str(dr)
        else:
            if(standard=='11b'):
                name_dr=standard+'_'+streams_chain+'_'+freq+'_'+preamble
            else:
                name_dr=standard+'_'+streams_chain+'_'+freq
            drt=str(dr)+'Mbps'
        chart_dr.set_title ({'name': name_dr})
        chart_dr.set_x_axis({'name': 'Signal Strength (dBm)','position_axis': 'on_tick'})
        chart_dr.set_y_axis({'name': 'edDetection'})
        chart_dr.set_style(10)
        worksheet.insert_chart('AG'+str(x), chart_dr, {'x_offset': 5, 'y_offset': 5})
        x=x+15
    if(standard=='11ac'):
        name=standard+'_'+streams_chain+'_'+freq+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
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
    worksheet.insert_chart('Z2', chart1, {'x_offset': 5, 'y_offset': 5})
    print 'END OF CHART'

def saveToDocFile(hdng,imag,freq,chn,bw):
    global document_path
    document_path=os.path.join(op_file_path.split(standard)[0],'RX_Interference_detection_'+release+'_'+board_num+'_'+rf_num+'.docx')
    print(document_path)
    try:
        document = Document(document_path)
    except:
        document = Document()
    paragraphs_obj=document.paragraphs
    paragraphs=[]
    for p in paragraphs_obj:
        paragraphs.append(p.text)
    if(release+" ACI Detection" not in paragraphs):
        document.add_heading(release+" ACI Detection", level=1)
    if('ACI Detection Curves' not in paragraphs):
        document.add_heading('ACI Detection Curves', level=2)
    if(standard=='11ac'):
        if("VHT - Channel-"+str(chn) not in paragraphs):
            document.add_heading("VHT - Channel-"+str(chn)+"- BW-"+str(bw), level=3)
    if(standard=='11n'):
        if("HT - "+freq+"-Channel-"+str(chn) not in paragraphs):
            document.add_heading("HT - "+freq+"-Channel-"+str(chn)+"- BW-"+str(bw), level=3)
    if(standard=='11g'):
        if("Legacy - Channel-"+str(chn) not in paragraphs):
            document.add_heading("Legacy - Channel-"+str(chn)+"- BW-"+str(bw), level=3)
    if(standard=='11a'):
        if("Legacy - Channel-"+str(chn) not in paragraphs):
            document.add_heading("Legacy - Channel-"+str(chn)+"- BW-"+str(bw), level=3)
    if(standard=='11b'):
        if("DSSS - Channel-"+str(chn) not in paragraphs):
            document.add_heading("DSSS - Channel-"+str(chn)+"- BW-"+str(bw), level=3)
    if(hdng not in paragraphs):
        document.add_heading(hdng, level=5)
    document.add_picture(imag,height=Inches(3.75),width=Inches(7.0))

    try:
        document.save(document_path)
    except:
        document.save(document_path+'_'+str(time.time())+'.docx')

def plotAciTestResultInPng():
    plot_list=[]
    fig = plt.figure()
    for amp in amplitude_list:
        plot_list.append(amp-cable_loss)
    for dtr in data_rate.split(','):
        plt.plot(plot_list,edDetection_dict[dtr],label=dtr,linewidth=3.0)
    ax=plt.gca()
    ax.invert_xaxis()
    if(standard=='11ac'):
        cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)+'_'+bw+'MHz_'+gi+'_'+coding+'_'+stbc
    elif(standard=='11n'):
        cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)+'_'+bw+'MHz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
    else:
        if(standard=='11b'):
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)+'_'+preamble
        else:
            cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+str(channel)
    plt.title(cnsl_fname)
    plt.xlabel('Signal Strength (dBm)', fontsize = 13)
    plt.ylabel('edDetection(%)', fontsize = 13)
    plt.grid()
    lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
    img_plot_path=os.path.join(op_file_path,cnsl_fname+'.png')
    plt.savefig(img_plot_path,bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
    saveToDocFile(cnsl_fname,img_plot_path,freq,str(channel),bw)
    result_log_path = os.path.abspath('../Results/')
    result_log_path=os.path.join(result_log_path,DUT_TestConfigParams.release)
    result_log_path=os.path.join(result_log_path,'result_log_path_'+release+'.txt')
    f_log_path=open(result_log_path,'a')
    f_log_path.write('\nACI_'+cnsl_fname+'->'+op_file_path)
    f_log_path.close()
    plt.close(fig)

def aciTestTop(DUT_TestConfigParams,dut1):
    global ftime
    global equipment
    global dut
    global vsg_streams
    global modulation
    global row_num
    global standard
    global streams
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
    global edDetection_dict
    global amplitude_list
    global ampl_dict
    ampl_dict = {}
    greenfield_mode=stbc=preamble=gi=coding=preamble=''
    edDetection_dict = {}
    ftime=open('total_time','a')
    ftime.write(time.strftime("%H-%M-%S")+"\n")
    row_num=2
    dut = dut1

    standard = DUT_TestConfigParams.standard
    streams=DUT_TestConfigParams.streams
    chain_sel=DUT_TestConfigParams.chain_sel
    streams_chain = streams+'_'+str(chain_sel)
    bw=DUT_TestConfigParams.bw
    data_rate=DUT_TestConfigParams.data_rate
    dutModel=DUT_TestConfigParams.dutModel
    start_amplt=DUT_TestConfigParams.start_amplt
    end_amplt=DUT_TestConfigParams.end_amplt
    step_size=DUT_TestConfigParams.step_size
    channel=int(DUT_TestConfigParams.channel)
    payload=DUT_TestConfigParams.payload
    if(standard=='11b'):
        preamble=DUT_TestConfigParams.preamble
    elif((standard=='11ac')or(standard=='11n')):
        stbc=DUT_TestConfigParams.stbc
        gi=DUT_TestConfigParams.gi
        coding=DUT_TestConfigParams.coding
        if(standard=='11n'):
            greenfield_mode=DUT_TestConfigParams.greenfield_mode

    if(int(channel)<30):
        freq='2.4GHz'
        dut_channel = 11    # DUT channel fixed to 11
    else:
        freq='5GHz'
        dut_channel = 100    # DUT channel fixed to 100
    op_file_path=BuildResultsPath(DUT_TestConfigParams)
    time.sleep(0.5)
    if(standard=='11b'):
        modulation='DSSS'
    else:
        modulation='OFDM'
    ftime.write(time.strftime("%H-%M-%S")+"\n")
    DebugPrint(create='1')
    DebugPrint('Test started')

    tester = DUT_TestConfigParams.vsg
    equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
    vsg_streams=streams
    if(stbc=='STBC_1'):
        vsg_streams='1x1'
        chain_sel=1
    if(dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,release=release,chain_sel=chain_sel)=='CONNECT_FAIL'):
        DebugPrint('CONNECT_FAIL')
        controlPowerSwitch(on_ports_list='8',off_ports_list='8')
        if(dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,release=release,chain_sel=chain_sel)=='CONNECT_FAIL'):
            DebugPrint('Switching to Serial Access')
            dutModel=dutModel.split('_')[0]
            dut=eval(dutModel)(com_port)
            equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
            dut.init_dut(standard=standard,streams=streams,channel=channel,bw=bw,release=release,chain_sel=chain_sel)

    dut.dut_down_up(action='up_down')
    DUT_functions.startTestcase()

    try:
        equipment.init_vsg_funcs(standard=standard,bw=bw,streams=vsg_streams,stbc=stbc,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,payload=payload,chain_sel=str(chain_sel))
    except Exception,e:
        DebugPrint('Equipment is not reachable')
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
        edDetection_dict[dr]=[]

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
    dut.set_dut_production_mode_settings(standard=standard,bw=bw)
    dut.set_dut_channel(dut_channel)
    equipment.apply_vsg(bw=bw,chn=channel,streams=vsg_streams)
    equipment.set_macheader()
    equipment.set_idleinterval(idleInterval)
    equipment.set_payload(standard,payload)
    if(standard=='11ac'):
        cnsl_fname=standard+'_'+streams +'_'+ str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+bw+'MHz_'+gi+'_'+coding+'_'+stbc
    elif(standard=='11n'):
        cnsl_fname=standard+'_'+streams +'_'+ str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+bw+'MHz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
    else:
        if(standard=='11b'):
            cnsl_fname=standard+'_'+streams +'_'+ str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+preamble
        else:
            cnsl_fname=standard+'_'+streams +'_'+ str(chain_sel)+'_'+freq+'_Chn'+str(channel)
    consld_fname=os.path.join(op_file_path,'ACI_Test_Consolidated_'+cnsl_fname+'.xlsx')
    DebugPrint(consld_fname)
    workbook = xlsxwriter.Workbook(consld_fname)
    worksheet = workbook.add_worksheet()
    bold1 = workbook.add_format({'bold': 1})
    for dr in data_rate.split(','):
    #dr=data_rate.split(',')[0]
        if(str(dr).lower().find('mcs')>=0):
            if(standard=='11ac'):
                fname=standard+'_'+streams+'_'+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+bw+'MHz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
            elif(standard=='11n'):
                fname=standard+'_'+streams+'_'+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+bw+'MHz_'+gi+'_'+coding+'_'+'_'+greenfield_mode+'_'+stbc+'_'+str(dr)
        else:
            if(standard=='11b'):
                fname=standard+'_'+streams+'_'+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+preamble+'_'+str(dr)+'Mbps'
            else:
                fname=standard+'_'+streams+'_'+str(chain_sel)+'_'+freq+'_Chn'+str(channel)+'_'+str(dr)+'Mbps'
        aci_file_name=os.path.join(op_file_path,'ACI_Test_'+fname+'.xlsx')
        workbook_aci = xlsxwriter.Workbook(aci_file_name)
        worksheet_aci = workbook_aci.add_worksheet()
        bold = workbook_aci.add_format({'bold': 1})
        equipment.set_datarate(modulation,standard,dr)
        equipment.generate_waveform(streams=vsg_streams)
        ftime.write("AMP LOOP START"+time.strftime("%H-%M-%S")+"\n")
        amplitudeLoop(dr,dut_channel,channel,amplitude_list,workbook,workbook_aci,worksheet,worksheet_aci,standard,cable_loss)
        ftime.write("AMP LOOP END"+time.strftime("%H-%M-%S")+"\n")
        plotSigPwrVsEd(dr,workbook_aci,worksheet_aci)
        workbook_aci.close()
    copy_file(op_dr_file_path=aci_file_name,dutModel=dutModel,release=release,standard=standard,streams=streams,stbc=stbc,coding=coding,gi=gi,greenfield_mode=greenfield_mode,preamble=preamble,ch=channel,test='rx')
    plotAciTestResults(workbook,worksheet,ch=channel)
    try:
        workbook.close()
    except:
        time.sleep(10)
        try:
            workbook.close()
        except:
            pass
    try:
        plotAciTestResultInPng()
    except Exception,e:
        print e
        pass
    equipment.rf_on_off(rf_state='off',streams=vsg_streams)
    equipment.close_vsg()
    dut.dut_close()