#-------------------------------------------------------------------------------
# Name:		tx_evm_power_across_datarates
# Purpose:	 This script will generate EVM-Measured Power vs DUT Power across data rates.
# Author:	  kranthi.kishore
# Created:	 14-06-2015
# Copyright:   Imagination Technologies Ltd
#-------------------------------------------------------------------------------

#from danube import *
#from beetle import *
#from rs import *
#from toshiba import *
#from europa import *

from iqxel import *
from common_utils import *
import numpy

rw_num=1

op_file_path=""
#Loop iterating for the range of txpower mentioned
def dut_txpower_loop(DUT_TestConfigParams,ch,dtr):
	start_amp_list=[]
	global row_num
	global data
	global row_num_dr
	row_num_dr=2
#PHY_PERFORMANCE: bug-fix
#	if(streams=='1x1'):
#		worksheet_dr.write_row('A1',['Standard','Channel','DataRate','TXPower','Power','EVM','Spectral Flatness','Spectrum Mask'],bold)
#		worksheet.write_row('A1',['Standard','Channel','DataRate','TXPower','Power','EVM','Spectral Flatness','Spectrum Mask'],bold1)
#	elif(streams=='2x2'):
#		worksheet.write_row('A1',['Standard','Channel','DataRate','TXPower','Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2','SymClkError-Stream1','SymClkError-Stream2','AmpImb-Stream1','AmpImb-Stream2','PhImb-Stream1','PhImb-Stream2'],bold1)
#		worksheet_dr.write_row('A1',['Standard','Channel','DataRate','TXPower','Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2','SymClkError-Stream1','SymClkError-Stream2','AmpImb-Stream1','AmpImb-Stream2','PhImb-Stream1','PhImb-Stream2'],bold)
	if(streams=='1x1'):
		worksheet_dr.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power','EVM(-ve)','Phase Error','Frequency Error','SymClkError','LO Leakage','Amplitude Imbalance','Phase Imbalance','Spectral Mask','Carrier Suppression'],bold)
		worksheet.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power','EVM(-ve)','Phase Error','Frequency Error','SymClkError','LO Leakage','Amplitude Imbalance','Phase Imbalance','Spectral Mask','Carrier Suppression'],bold1)
	elif(streams=='2x2'):
		worksheet.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power-Stream1','Power-Stream2','EVM-Stream1(-ve)','EVM-Stream2(-ve)','Phase Error-Stream1','Phase Error-Stream2','Frequency Error-Stream1','Frequency Error-Stream2','SymClkError-Stream1','SymClkError-Stream2','LO Leakage-Stream1','LO Leakage-Stream2','Amplitude Imbalance-Stream1','Amplitude Imbalance-Stream2','Phase Imbalance-Stream1','Phase Imbalance-Stream2','Spectral Mask-Stream1','Spectral Mask-Stream2','Carrier Suppression-Stream1','Carrier Suppression-Stream2'],bold1)
		worksheet_dr.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power-Stream1','Power-Stream2','EVM-Stream1(-ve)','EVM-Stream2(-ve)','Phase Error-Stream1','Phase Error-Stream2','Frequency Error-Stream1','Frequency Error-Stream2','SymClkError-Stream1','SymClkError-Stream2','LO Leakage-Stream1','LO Leakage-Stream2','Amplitude Imbalance-Stream1','Amplitude Imbalance-Stream2','Phase Imbalance-Stream1','Phase Imbalance-Stream2','Spectral Mask-Stream1','Spectral Mask-Stream2','Carrier Suppression-Stream1','Carrier Suppression-Stream2'],bold)

	dut.pktgen_tool(DUT_TestConfigParams,'run') #PHY_PERFORMANCE - should this be commented?
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
	for txp in txpower_dict[dtr]:
		data=[]
		data.append(standard)
		data.append(int(ch))
		try:
			data.append(int(dtr))
		except:
			data.append(dtr)
		data.append(txp)
		dut.set_dut_txpower(str(txp))
		#return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2) #PHY_PERFORMANCE bugfix
		return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
		if('e+37' in str(return_data[0])):
			dut.set_dut_channel(int(ch))
			time.sleep(10)
			#dut.pktgen_tool(DUT_TestConfigParams,'update')  # PHY_PERFORMANCE . this is missing compared to EVM across channels.
			dut.pktgen_tool(DUT_TestConfigParams,'run')
			#return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2) #PHY_PERFORMANCE bugfix
			return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
		if(return_data[4]==0):
			if(dut.check_dut_stuck_state()=='alive'):
				dut.dut_reboot()
			else:
				print 'DUT is stuck'
				controlPowerSwitch(on_ports_list='8',off_ports_list='8')
			time.sleep(reboot_time)
			dut.init_dut(standard=standard,streams=streams,channel=int(ch),bw=bw,release=release,test='tx',chain_sel=chain_sel)
			dut.set_dut_production_mode_settings(standard=standard,ch=int(ch),stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx',payload=payload)
			dut.set_dut_channel(int(ch))
			dut.pktgen_tool(DUT_TestConfigParams,'update')# PHY_PERFORMANCE . this is missing compared to EVM across channels
			dut.set_dut_datarate(dtr,standard)
			dut.set_dut_txpower(str(txp))
			dut.pktgen_tool(DUT_TestConfigParams,'run')
			#return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2) #PHY_PERFORMANCE bug fix
			return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
		data=data+return_data
		print data

#PHY_PERFORMANCE bugfix  - VSA is not returning 2nd stream info
#		if 'Power-Stream1' not in power_evm_dict[ch][dtr].keys():
#			power_evm_dict[ch][dtr]['Power-Stream1']=[]
#		power_evm_dict[ch][dtr]['Power-Stream1'].append(data[4])
#		if 'Power-Stream2' not in power_evm_dict[ch][dtr].keys():
#			power_evm_dict[ch][dtr]['Power-Stream2']=[]
#		power_evm_dict[ch][dtr]['Power-Stream2'].append(data[5])
#		if 'EVM-Stream1' not in power_evm_dict[ch][dtr].keys():
#			power_evm_dict[ch][dtr]['EVM-Stream1']=[]
#		power_evm_dict[ch][dtr]['EVM-Stream1'].append(data[6])
#		if 'EVM-Stream2' not in power_evm_dict[ch][dtr].keys():
#			power_evm_dict[ch][dtr]['EVM-Stream2']=[]
#		power_evm_dict[ch][dtr]['EVM-Stream2'].append(data[7])
#		measured_power_1x1=data[4]
#		measured_evm_1x1=data[6]
#		measured_evm_2x2=data[7]


		if 'Power-Stream1' not in power_evm_dict[ch][dtr].keys():
			power_evm_dict[ch][dtr]['Power-Stream1']=[]
		power_evm_dict[ch][dtr]['Power-Stream1'].append(data[6])
		#if 'Power-Stream2' not in power_evm_dict[ch][dtr].keys():
		#	power_evm_dict[ch][dtr]['Power-Stream2']=[]
		#power_evm_dict[ch][dtr]['Power-Stream2'].append(data[5])
		if 'EVM-Stream1' not in power_evm_dict[ch][dtr].keys():
			power_evm_dict[ch][dtr]['EVM-Stream1']=[]
		power_evm_dict[ch][dtr]['EVM-Stream1'].append(data[7])
		#if 'EVM-Stream2' not in power_evm_dict[ch][dtr].keys():
		#	power_evm_dict[ch][dtr]['EVM-Stream2']=[]
		#power_evm_dict[ch][dtr]['EVM-Stream2'].append(data[7])
		measured_power_1x1=data[6]
		measured_evm_1x1=data[7]
		print " measured_power_1x1=",measured_power_1x1
		print " measured_evm_1x1=",measured_evm_1x1
		measured_evm_2x2=0

		DebugPrint(data)
		worksheet.write_row('A'+str(row_num), data)
		worksheet_dr.write_row('A'+str(row_num_dr), data)
		row_num=row_num+1
		row_num_dr=row_num_dr+1
		if(a==1):
			prev_txp=curr_txp=txp
			prev_evm_1x1=curr_evm_1x1=measured_evm_1x1
			prev_evm_2x2=curr_evm_2x2=measured_evm_2x2
		else:
			prev_txp=curr_txp
			curr_txp=txp
			prev_evm_1x1=curr_evm_1x1
			curr_evm_1x1=measured_evm_1x1
			prev_evm_2x2=curr_evm_2x2
			curr_evm_2x2=measured_evm_2x2
		# print'TXP->',txp
		# print 'EVM_IND_FLG->',evm_index_flag_1x1
		# print 'MEAS_PWR_1x1->',measured_power_1x1
		# print 'MEAS_EVM_1x1->',measured_evm_1x1
		# print 'STD_EVM_1x1->',standard_evm_dict[band][dtr]
		a+=1
		if float(measured_evm_1x1) < float(standard_evm_dict[band][dtr]):
			if(evm_index_flag_1x1==2):
				if(len(power_evm_dict[ch][dtr]['Power-Stream1'])>1):
					evm_index_flag_1x1=1
					get_best_txpower_from_evm(ch=ch,dtr=dtr,prev_txp=prev_txp,curr_txp=txp,prev_evm=prev_evm_1x1,measured_evm=measured_evm_1x1)
		elif (float(measured_evm_1x1) > float(standard_evm_dict[band][dtr])):
			evm_index_flag_1x1=2
		if(streams=='2x2'):
			if float(measured_evm_2x2) < float(standard_evm_dict[band][dtr]):
				if(evm_index_flag_2x2==2):
					evm_index_flag_2x2=1
					get_best_txpower_from_evm(ch=ch,dtr=dtr,prev_txp=prev_txp,curr_txp=txp,prev_evm=prev_evm_2x2,measured_evm=measured_evm_2x2)
			if float(measured_evm_2x2) > float(standard_evm_dict[band][dtr]):
				evm_index_flag_2x2=2
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
	# print 'FINAL_PWR_1x1->',max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1']
	# print 'FINAL_EVM_1x1->',max_txpower_dict[ch][dtr]['EVM-Stream1']
	#dut.pktgen_tool(DUT_TestConfigParams,'kill') #PHY_PERFORMANCE. this should be commented as per EVM and EVM across channels
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
		if(standard=='11ac'):
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
	column_dict={'Power-Stream1':'E','Power-Stream2':'F','EVM-Stream1':'G','EVM-Stream2':'H'}
	for dr in data_rate.split(','):
		chart_dr = workbook.add_chart({'type': 'line'})
		if(streams=='1x1'):
			col_names=['Power-Stream1','EVM-Stream1']
		else:
			col_names=['Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2']

		for column in col_names:
				chart_dr.add_series({
					'name':	   column,
					'categories': '=Sheet1!$D$2:$D$'+str(len(txpower_list)+1),
					'values':  '=Sheet1!$'+column_dict[column]+str(strval)+':'+column_dict[column]+str(endval)
				})

		strval=strval+len(txpower_list)+1
		endval=endval+len(txpower_list)+1
		if(standard=='11ac'):
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

def get_best_txpower_from_evm(ch='',dtr='',prev_txp='',curr_txp='',prev_evm='',measured_evm=''):
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
		return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2)
		if('e+37' in str(return_data[0])):
			time.sleep(3)
			return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2)
		if(return_data[2]==0):
			for i in range(10):
				return_data.pop()
			if(dut.check_dut_stuck_state()=='alive'):
				dut.dut_reboot()
			else:
				print 'DUT is stuck'
				controlPowerSwitch(on_ports_list='8',off_ports_list='8')
			time.sleep(reboot_time)
			dut.init_dut(standard=standard,streams=streams,channel=int(ch),bw=bw,release=release,test='tx')
			dut.set_dut_production_mode_settings(standard=standard,ch=int(ch),stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx',payload=payload)
			dut.set_dut_channel(int(ch))
			dut.set_dut_datarate(dtr,standard)
			dut.set_dut_txpower(str(txp))
			dut.pktgen_tool(DUT_TestConfigParams,'run')
			return_data=get_tx_stats_from_vsa(txp,dtr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2)
		print return_data
		measured_power_1x1=return_data[0]
		measured_power_2x2=return_data[1]
		measured_evm_1x1=return_data[2]
		measured_evm_2x2=return_data[3]

		if float(measured_evm_1x1) < float(standard_evm_dict[band][dtr]):
			evm_obtained_flag_1x1=1
		# print'GET TXP->',txp
		# print 'GET EVM_OBT_FLG->',evm_obtained_flag_1x1
		# print 'GET MEAS_PWR_1x1->',measured_power_1x1
		# print 'GET MEAS_EVM_1x1->',measured_evm_1x1
		# print 'GET STD_EVM_1x1->',standard_evm_dict[band][dtr]
		if(evm_obtained_flag_1x1==1):
			if('MAX_TXPower-Stream1' not in max_txpower_dict[ch][dtr].keys()):
				max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1']=str(measured_power_1x1)
				max_txpower_dict[ch][dtr]['EVM-Stream1']=str(measured_evm_1x1)

		if(streams=='2x2'):
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
	col_names = ['Standard','Channel','DataRate','Expected EVM','MAX_TXPower-Stream1','EVM-Stream1']
	if(streams=='2x2'):
		col_names.append('MAX_TXPower-Stream2')
		col_names .append('EVM-Stream2')
	worksheet_maxtxpower.write_row('A1',col_names)

	row_num=2
	for ch in channel.split(','):
		if(int(ch) < 15):
			band='2.4'
		else:
			band='5'
		if(int(ch) < 15):
			freq='2.4GHz'
		else:
			freq='5GHz'
		if(standard=='11ac'):
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
		table = document.add_table(rows=1, cols=len(col_names))
		table.style = 'TableGrid'
		hdr_cells = table.rows[0].cells
		for idx, name in enumerate(col_names):
			paragraph = hdr_cells[idx].paragraphs[0]
			run = paragraph.add_run(name)
			run.bold = True
		for dtr in data_rate.split(','):
			data=[]
			data.append(standard)
			data.append(ch)
			data.append(dtr)
			data.append(str(standard_evm_dict[band][dtr]))
			data.append(max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1'])
			data.append(max_txpower_dict[ch][dtr]['EVM-Stream1'])

			row_cells = table.add_row().cells
			row_cells[0].text = str(standard)
			row_cells[1].text = str(ch)
			row_cells[2].text = str(dtr)
			row_cells[3].text = str(standard_evm_dict[band][dtr])
			row_cells[4].text=max_txpower_dict[ch][dtr]['MAX_TXPower-Stream1']
			row_cells[5].text=max_txpower_dict[ch][dtr]['EVM-Stream1']
			if(streams=='2x2'):
				data.append(max_txpower_dict[ch][dtr]['EVM-Stream2'])
				data.append(max_txpower_dict[ch][dtr]['MAX_TXPower-Stream2'])
				row_cells[6].text=max_txpower_dict[ch][dtr]['MAX_TXPower-Stream2']
				row_cells[7].text=max_txpower_dict[ch][dtr]['EVM-Stream2']
			worksheet_maxtxpower.write_row('A'+str(row_num), data)
			row_num+=1

	workbook_maxtxpower.close()
	try:
		document.save(max_document_path)
	except:
		document.save(max_document_path+'_'+str(time.time())+'.docx')

def plot_power_evm_png(ch):
	for dtr in data_rate.split(','):
		plt.plot(txpower_dict[dtr],power_evm_dict[ch][dtr]['EVM-Stream1'],label='EVM-Stream1'+'_'+str(dtr),linewidth=3)
		if(int(ch) < 15):
			freq='2.4GHz'
		else:
			freq='5GHz'
		if(standard=='11ac'):
			cnsl_fname=standard+'_Chain1_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
			drt=str(dtr)
		elif(standard=='11n'):
			cnsl_fname=standard+'_Chain1_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
			drt=str(dtr)
		else:
			if(standard=='11b'):
				cnsl_fname=standard+'_Chain1_'+freq+'_Chn'+ch+'_'+preamble+'_'+str(dtr)+'Mbps'
			else:
				cnsl_fname=standard+'_Chain1_'+freq+'_Chn'+ch+'_'+str(dtr)+'Mbps'
		plt.title(cnsl_fname)
		plt.ylabel('- EVM (dB)/VSA Power', fontsize = 13)
		plt.xlabel('DUT TX Power (dBm))', fontsize = 13)
		plt.grid()
		lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
		img_plot_path=os.path.join(op_file_path,cnsl_fname+'.png')
	plt.savefig(img_plot_path,bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
	plt.cla()
	save_to_doc(cnsl_fname,img_plot_path,freq,ch)
	if(streams=='2x2'):
		for dtr in data_rate.split(','):
			plt.plot(txpower_dict[dtr],power_evm_dict[ch][dtr]['EVM-Stream2'],label='EVM-Stream2'+'_'+str(dtr),linewidth=3)
			if(int(ch) < 15):
				freq='2.4GHz'
			else:
				freq='5GHz'
			if(standard=='11ac'):
				cnsl_fname=standard+'_Chain2_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
				drt=str(dtr)
			elif(standard=='11n'):
				cnsl_fname=standard+'_Chain2_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
				drt=str(dtr)
			else:
				if(standard=='11b'):
					cnsl_fname=standard+'_Chain2_'+freq+'_Chn'+ch+'_'+preamble+'_'+str(dtr)+'Mbps'
				else:
					cnsl_fname=standard+'_Chain2_'+freq+'_Chn'+ch+'_'+str(dtr)+'Mbps'
			plt.title(cnsl_fname)
			plt.ylabel('- EVM (dB)/VSA Power', fontsize = 13)
			plt.xlabel('DUT TX Power (dBm))', fontsize = 13)
			plt.grid()
			lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
			img_plot_path=os.path.join(op_file_path,cnsl_fname+'.png')
		plt.savefig(img_plot_path,bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
		plt.cla()
		save_to_doc(cnsl_fname,img_plot_path,freq,ch)


##if __name__ == "__main__":
def tx_evm_power_analysis_across_datarates(DUT_TestConfigParams,dut1):
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
	global tester
	global payload
	greenfield_mode=stbc=preamble=gi=coding=preamble=''
	strt_time=time.time()
	txpower_dict={}

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
	channel=DUT_TestConfigParams.channel
	payload=int(DUT_TestConfigParams.payload)
	if(standard=='11b'):
		preamble=DUT_TestConfigParams.preamble

	elif((standard=='11ac')or(standard=='11n')):
		stbc=DUT_TestConfigParams.stbc
		gi=DUT_TestConfigParams.gi
		coding=DUT_TestConfigParams.coding
		if(standard=='11n'):
			greenfield_mode=DUT_TestConfigParams.greenfield_mode

	if(int(channel.split(',')[-1])<30):
		freq='2.4GHz'
	else:
		freq='5GHz'
	op_file_path=BuildResultsPath(DUT_TestConfigParams)
	time.sleep(0.5)
	power_evm_dict={}
	max_txpower_dict={}
	DebugPrint(create='1')
##	dut=eval(dutModel)(com_port)
	tester = DUT_TestConfigParams.vsg
	equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
	DebugPrint('Trying to initialize dut in PER Main')
	if(dut.init_dut(standard=standard,streams=streams,channel=int(channel.split(',')[-1]),bw=bw,release=release,test='tx',chain_sel=chain_sel)=='CONNECT_FAIL'):
		print 'CONNECT_FAIL'
		DebugPrint('CONNECT_FAIL in PER Main')
		controlPowerSwitch(on_ports_list='8',off_ports_list='8')
		if(dut.init_dut(standard=standard,streams=streams,channel=int(channel.split(',')[-1]),bw=bw,release=release,test='tx',chain_sel=chain_sel)=='CONNECT_FAIL'):
			print 'Switching to Serial Access'
			DebugPrint('Switching to Serial Access')
			dutModel=dutModel.split('_')[0]
			dut=eval(dutModel)(com_port)
			equipment=eval(tester.split('_')[0])(tester,DUT_TestConfigParams.equip_ip)
			dut.init_dut(standard=standard,streams=streams,channel=int(channel.split(',')[-1]),bw=bw,release=release,test='tx',chain_sel=chain_sel)
	try:
		#equipment.init_vsa_funcs(standard=standard,bw=bw,streams=streams,stbc=stbc,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,chain_sel=chain_sel)
		equipment.init_vsa_funcs(standard=standard,bw=bw,streams=streams,stbc=stbc,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,chain_sel=str(chain_sel)) #PHY_PERFORMANCE: bugfix
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
	dut.set_dut_production_mode_settings(standard=standard,ch=int(channel.split(',')[-1]),stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx',payload=payload)
	for ch in channel.split(','):
		if ch not in power_evm_dict.keys():
			power_evm_dict[ch]={}
		row_num=2
		if(int(ch)<30):
			freq='2.4GHz'
		else:
			freq='5GHz'
#		dut.pktgen_tool(DUT_TestConfigParams,'kill')
		#dut.set_dut_production_mode_settings(standard=standard,ch=int(ch),stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx',payload=payload)
		dut.set_dut_channel(int(ch))
		dut.dut_down_up(action='down',ch=ch)
		equipment.apply_vsa(ch,bw,streams)
		if(standard=='11ac'):
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
		f_log_path=open(result_log_path,'a')
		f_log_path.write('\nPOWER_EVM_'+cnsl_fname+'->'+op_file_path)
		f_log_path.close()

		for dr in data_rate.split(','):
			if dr not in power_evm_dict[ch].keys():
				power_evm_dict[ch][dr]={}

			if(standard=='11ac'):
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
#			dut_txpower_loop(ch,dr)
			dut_txpower_loop(DUT_TestConfigParams,ch,dr) #PHY_PERFORMANCE - bugfix
			#f_time.write(str(time.time()))
			workbook_dr.close()
			copy_file(op_dr_file_path=dr_file_name,dutModel=dutModel,release=release,standard=standard,streams=streams_chain,stbc=stbc,coding=coding,gi=gi,greenfield_mode=greenfield_mode,preamble=preamble,ch=ch,test='tx')
		try:
			plot_power_evm(ch)
			workbook.close()
		except Exception,e:
			print e.args
			workbook.close()
			pass
		try:
			plot_power_evm_png(ch)
		except Exception,e:
			print e.args
			pass
		copy_file(op_dr_file_path=consld_fname,dutModel=dutModel,release=release,standard=standard,streams=streams_chain,stbc=stbc,coding=coding,gi=gi,greenfield_mode=greenfield_mode,preamble=preamble,ch=ch,test='tx')
	#get_best_txpower_from_evm()

	write_max_txpower()
	dut.pktgen_tool(DUT_TestConfigParams,'kill')
	copy_file(op_dr_file_path=document_path,dutModel=dutModel,release=release,test='tx')
	copy_file(op_dr_file_path=max_document_path,dutModel=dutModel,release=release,test='tx')
	equipment.close_vsg()
	dut.dut_close()