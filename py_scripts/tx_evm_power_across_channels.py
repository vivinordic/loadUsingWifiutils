#-------------------------------------------------------------------------------
# Name:        tx_evm_power_across_channels
# Purpose:     This script will generate EVM and Measured Power vs DUT Power across various channels.
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

op_file_path=""

#Loop iterating for the range of txpower mentioned
def dut_txpower_loop(DUT_TestConfigParams,ch,dr):
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

	for txp in txpower_dict[dr]:
		if txp not in channel_power_evm_dict[dr].keys():
			channel_power_evm_dict[dr][txp]={}
		if dr+'_'+str(txp) not in worksheet_main_dr_dict.keys():
			#print 'KEYS hand======'+dr+'_'+str(txp)
			worksheet_txp = workbook_cons.add_worksheet(dr+'_TXPower-'+str(txp))
			worksheet_main_dr_dict[dr+'_'+str(txp)]={'object':'','row_num':''}
			worksheet_main_dr_dict[dr+'_'+str(txp)]['object']=worksheet_txp
			worksheet_main_dr_dict[dr+'_'+str(txp)]['row_num']=2
			if(streams=='1x1'):
				#PHY_PERFORMANCE: bugfix
				#worksheet_txp.write_row('A1',['Standard','Channel','DataRate','TXPower','Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2','SymClkError-Stream1','SymClkError-Stream2','AmpImb-Stream1','AmpImb-Stream2','PhImb-Stream1','PhImb-Stream2'],bold1_cons)
				 worksheet_txp.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power','EVM(-ve)','Phase Error','Frequency Error','SymClkError','LO Leakage','Amplitude Imbalance','Phase Imbalance','Spectral Mask','Carrier Suppression'],bold)
			elif(streams=='2x2'):
				#PHY_PERFORMANCE: bugfix
				#worksheet_txp.write_row('A1',['Standard','Channel','DataRate','TXPower','Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2','SymClkError-Stream1','SymClkError-Stream2','AmpImb-Stream1','AmpImb-Stream2','PhImb-Stream1','PhImb-Stream2'],bold1_cons)
				worksheet_txp.write_row('A1',['Standard','Channel','Set DataRate','TXPower','Bandwidth','Measured DataRate','Power-Stream1','Power-Stream2','EVM-Stream1(-ve)','EVM-Stream2(-ve)','Phase Error-Stream1','Phase Error-Stream2','Frequency Error-Stream1','Frequency Error-Stream2','SymClkError-Stream1','SymClkError-Stream2','LO Leakage-Stream1','LO Leakage-Stream2','Amplitude Imbalance-Stream1','Amplitude Imbalance-Stream2','Phase Imbalance-Stream1','Phase Imbalance-Stream2','Spectral Mask-Stream1','Spectral Mask-Stream2','Carrier Suppression-Stream1','Carrier Suppression-Stream2'],bold)

		data=[]
		data.append(standard)
		data.append(int(ch))
		try:
			data.append(int(dr))
		except:
			data.append(dr)
		data.append(txp)
		dut.set_dut_txpower(str(txp))
		#return_data=get_tx_stats_from_vsa(txp,dr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2)  #PHY_PERFORMANCE - bugfix
		return_data=get_tx_stats_from_vsa(txp,dr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
		if('e+37' in str(return_data[0])):
			dut.set_dut_channel(int(ch))
			time.sleep(10)
			dut.pktgen_tool(DUT_TestConfigParams,'update')
			dut.pktgen_tool(DUT_TestConfigParams,'run')
			#return_data=get_tx_stats_from_vsa(txp,dr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2)  #PHY_PERFORMANCE - bugfix
			return_data=get_tx_stats_from_vsa(txp,dr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)

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
			dut.pktgen_tool(DUT_TestConfigParams,'update')
			dut.set_dut_datarate(dr,standard)
			dut.set_dut_txpower(str(txp))
			dut.pktgen_tool(DUT_TestConfigParams,'run')
			#return_data=get_tx_stats_from_vsa(txp,dr,ch,streams,standard,equipment,cable_loss_1x1,cable_loss_2x2) #mural ..bugfix
			return_data=get_tx_stats_from_vsa(txp,dr,ch,streams,standard,bw,equipment,cable_loss_1x1,cable_loss_2x2)
			print data


		data=data+return_data
		print data
		if 'Power-Stream1' not in power_evm_dict[ch][dr].keys():
			power_evm_dict[ch][dr]['Power-Stream1']=[]
		power_evm_dict[ch][dr]['Power-Stream1'].append(data[4])
		if 'Power-Stream2' not in power_evm_dict[ch][dr].keys():
			power_evm_dict[ch][dr]['Power-Stream2']=[]
		power_evm_dict[ch][dr]['Power-Stream2'].append(data[5])
		if 'EVM-Stream1' not in power_evm_dict[ch][dr].keys():
			power_evm_dict[ch][dr]['EVM-Stream1']=[]
		power_evm_dict[ch][dr]['EVM-Stream1'].append(data[6])
		if 'EVM-Stream2' not in power_evm_dict[ch][dr].keys():
			power_evm_dict[ch][dr]['EVM-Stream2']=[]
		power_evm_dict[ch][dr]['EVM-Stream2'].append(data[7])
		if 'Power-Stream1' not in channel_power_evm_dict[dr][txp].keys():
			channel_power_evm_dict[dr][txp]['Power-Stream1']=[]
		channel_power_evm_dict[dr][txp]['Power-Stream1'].append(data[4])
		if 'Power-Stream2' not in channel_power_evm_dict[dr][txp].keys():
			channel_power_evm_dict[dr][txp]['Power-Stream2']=[]
		channel_power_evm_dict[dr][txp]['Power-Stream2'].append(data[5])

		if 'EVM-Stream1' not in channel_power_evm_dict[dr][txp].keys():
			channel_power_evm_dict[dr][txp]['EVM-Stream1']=[]
		channel_power_evm_dict[dr][txp]['EVM-Stream1'].append(data[6])
		if 'EVM-Stream2' not in channel_power_evm_dict[dr][txp].keys():
			channel_power_evm_dict[dr][txp]['EVM-Stream2']=[]
		channel_power_evm_dict[dr][txp]['EVM-Stream2'].append(data[7])

		DebugPrint(data)
		worksheet.write_row('A'+str(row_num), data)
		worksheet_dr.write_row('A'+str(row_num_dr), data)
		row_num=row_num+1
		row_num_dr=row_num_dr+1
		worksheet_main_dr_dict[dr+'_'+str(txp)]['object'].write_row('A'+str(worksheet_main_dr_dict[dr+'_'+str(txp)]['row_num']), data)
		worksheet_main_dr_dict[dr+'_'+str(txp)]['row_num']=worksheet_main_dr_dict[dr+'_'+str(txp)]['row_num']+1
	#dut.pktgen_tool(DUT_TestConfigParams,'kill')
	row_num=row_num+1

def save_to_doc(hdng,imag,freq,chn):
	global document_path
	document_path=os.path.join(op_file_path.split(standard)[0],'TX_Characterization_Across_Channels_'+release+'_'+board_num+'_'+rf_num+'.docx')
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
	if('DUT Power vs EVM/VSA Power Across Channels' not in paragraphs):
		document.add_heading('DUT Power vs EVM/VSA Power Across Channels', level=2)
	if(freq not in paragraphs):
		document.add_heading(freq, level=3)
	if(hdng not in paragraphs):
		document.add_heading(hdng, level=4)
	document.add_picture(imag,height=Inches(4.05),width=Inches(7.5))
	try:
		document.save(document_path)
	except:
		document.save(document_path+'_'+str(time.time())+'.docx')


def plot_power_evm_cons_png():
	if(standard=='11ac'):
		cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc
	elif(standard=='11n'):
		cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc
	else:
		if(standard=='11b'):
			cnsl_fname=standard+'_'+streams_chain+'_'+freq+'_'+preamble
		else:
			cnsl_fname=standard+'_'+streams_chain+'_'+freq
	for dtr in data_rate.split(','):
		result_log_path = os.path.abspath('../Results/')
		result_log_path=os.path.join(result_log_path,DUT_TestConfigParams.release)
		result_log_path=os.path.join(result_log_path,'result_log_path_'+release+'.txt')
		f_log_path=open(result_log_path,'a')
		f_log_path.write('\nPOWER_EVM_ACROSS_CHANNELS_'+cnsl_fname+'_'+dtr+'->'+op_file_path)
		f_log_path.close()
		for txp in txpower_dict[dtr]:

			if(streams=='2x2'):
				for label in ['Power-Stream1','Power-Stream2']:
					if('Power-Stream1' in label):
						plt.plot(range(len(channels_list)),channel_power_evm_dict[dtr][txp][label],'ro',label=label,linewidth=3)
					else:
						plt.plot(range(len(channels_list)),channel_power_evm_dict[dtr][txp][label],'bo',label=label,linewidth=3)
			else:
				for label in ['Power-Stream1']:
					plt.plot(range(len(channels_list)),channel_power_evm_dict[dtr][txp][label],'ro',label=label,linewidth=3)
			plt.title('TXPower-'+str(txp))
			plt.ylabel('VSA Power', fontsize = 13)
			plt.xlabel('Channel', fontsize = 13)
			plt.grid()
			channels_list_int=map(int,channels_list)
			plt.yticks(np.arange(0, 23, 1))
			plt.xticks(range(len(channels_list)),channels_list,rotation='vertical')
			lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
			plt.savefig(op_file_path+'\\'+cnsl_fname+'_'+dtr+'TXPower-'+str(txp)+'_MeasuredPower.png',bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
			plt.cla()
			save_to_doc(cnsl_fname+'_'+dtr+'_TXPower-'+str(txp)+'_MeasuredPower',op_file_path+'\\'+cnsl_fname+'_'+dtr+'TXPower-'+str(txp)+'_MeasuredPower.png',freq,'')
			if(streams=='2x2'):
				for label in ['EVM-Stream1','EVM-Stream2']:
					if('EVM-Stream1' in label):
						plt.plot(range(len(channels_list)),channel_power_evm_dict[dtr][txp][label],'ro',label=label,linewidth=3)
					else:
						plt.plot(range(len(channels_list)),channel_power_evm_dict[dtr][txp][label],'bo',label=label,linewidth=3)
			else:
				for label in ['EVM-Stream1']:
					plt.plot(range(len(channels_list)),channel_power_evm_dict[dtr][txp][label],'ro',label=label,linewidth=3)
			plt.title('TXPower-'+str(txp))
			plt.ylabel('- EVM (dB)', fontsize = 13)
			plt.xlabel('Channel', fontsize = 13)
			plt.grid()
			plt.yticks(np.arange(0, 40, 2))
			#plt.xticks(channels_list_int,channels_list_int)
			plt.xticks(range(len(channels_list)),channels_list,rotation='vertical')
			lgd=plt.legend(loc=9, bbox_to_anchor=(1.2, 1), ncol=1)
			plt.savefig(op_file_path+'\\'+cnsl_fname+'_'+dtr+'TXPower-'+str(txp)+'_EVM.png',bbox_extra_artists=(lgd,), bbox_inches='tight',dpi=70)
			plt.cla()
			save_to_doc(cnsl_fname+'_'+dtr+'_TXPower-'+str(txp)+'_EVM',op_file_path+'\\'+cnsl_fname+'_'+dtr+'TXPower-'+str(txp)+'_EVM.png',freq,'')
def plot_power_evm(ch):
	chart1 = workbook.add_chart({'type': 'line'})
	chart_dr = workbook.add_chart({'type': 'line'})
	endval=len(txpower_list)+1
	strval=2
	x=2
	column_dict={'Power-Stream1':'E','Power-Stream2':'F','EVM-Stream1':'G','EVM-Stream2':'H'}
	for dr in data_rate.split(','):
		chart_dr = workbook.add_chart({'type': 'line'})
		if(streams=='2x2'):
			for column in ['Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2']:
				chart_dr.add_series({
					'name':       column,
					'categories': '=Sheet1!$D$2:$D$'+str(len(txpower_list)+1),
					'values':  '=Sheet1!$'+column_dict[column]+str(strval)+':'+column_dict[column]+str(endval)
				})
		else:
			for column in ['Power-Stream1','EVM-Stream1']:
				chart_dr.add_series({
					'name':       column,
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

def plot_power_evm_cons():
	column_dict={'Power-Stream1':'E','Power-Stream2':'F','EVM-Stream1':'G','EVM-Stream2':'H'}
	for dr in data_rate.split(','):
		for txp in txpower_dict[dr]:
			chart_cons = workbook_cons.add_chart({'type': 'line'})
			for column in ['Power-Stream1','Power-Stream2','EVM-Stream1','EVM-Stream2']:
				chart_cons.add_series({
					'name':       column,
					'categories': '='+'\''+dr+'_TXPower-'+str(txp)+'\''+'!$B$2:$B$'+str(len(channels_list)+1),
					'values':  '='+'\''+dr+'_TXPower-'+str(txp)+'\''+'!$'+column_dict[column]+'2:'+column_dict[column]+str(len(channels_list)+1)
				})
			chart_cons.set_title ({'name': "TXPower-"+str(txp)})
			chart_cons.set_x_axis({'name': 'Channel','position_axis': 'on_tick'})
			chart_cons.set_y_axis({'name': ' - EVM (dB)\\ VSA Power'})
			chart_cons.set_style(10)
			worksheet_main_dr_dict[dr+'_'+str(txp)]['object'].insert_chart('O2', chart_cons, {'x_offset': 5, 'y_offset': 5})

##if __name__ == "__main__":
def tx_evm_power_analysis_across_channels(DUT_TestConfigParams,dut1):
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
	global channel_power_evm_dict
	global worksheet_main_dr_dict
	global workbook_cons
	global bold1_cons
	global channels_list
	global tester
	global payload


##	global channel_power_evm_dict
##	global worksheet_main_dr_dict
	greenfield_mode=stbc=preamble=gi=coding=preamble=''
	strt_time=time.time()
	txpower_dict={}
	worksheet_main_dr_dict={}
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
	#controlPowerSwitch(on_ports_list='8',off_ports_list='8')

	if(int(channel.split(',')[-1])<30):
		freq='2.4GHz'
	else:
		freq='5GHz'
	steps_list=list(numpy.arange(start_txpower,end_txpower+1,step_size))
	op_file_path=BuildResultsPath(DUT_TestConfigParams)
	time.sleep(0.5)
	power_evm_dict={}
	channel_power_evm_dict={}
	DebugPrint(create='1')
#	dut=eval(dutModel)(com_port)
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
		equipment.init_vsa_funcs(standard=standard,bw=bw,streams=streams,stbc=stbc,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,chain_sel=str(chain_sel))
	except Exception,e:
		print 'Equipment is not reachable'
		DebugPrint('Equipment is not reachable')
		exit(0)
	dut.pktgen_tool(DUT_TestConfigParams,'write')
	workbook_cons = xlsxwriter.Workbook(op_file_path+'\Consolidated_Channels.xlsx')
	bold1_cons = workbook_cons.add_format({'bold': 1})
	for dr in data_rate.split(','):
		txpower_list=[]
		steps_list=list(numpy.arange(start_txpower,end_txpower+1,step_size))
		for j in steps_list:
			txpower_list.append(j)
		DebugPrint(txpower_list)
		txpower_dict[dr]=txpower_list
	#dut.pktgen_tool(DUT_TestConfigParams,'run')
	channels_list=channel.split(',')
	for ch in channel.split(','):
		if ch not in power_evm_dict.keys():
			power_evm_dict[ch]={}
		row_num=2
		if(int(ch)<30):
			freq='2.4GHz'
		else:
			freq='5GHz'
##		dut.pktgen_tool(DUT_TestConfigParams,'kill')
		dut.set_dut_production_mode_settings(standard=standard,ch=int(ch),stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test='tx',payload=payload)
		dut.set_dut_channel(int(ch))
		#dut.pktgen_tool(DUT_TestConfigParams,'run') # PHY_PERFORMANCE commented. This is not expected as per the sequence of EVM test. Never enable this. this is a bug.
		dut.dut_down_up('down',ch)
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
		consld_fname=os.path.join(op_file_path,'TX_Consolidated_Channels_'+cnsl_fname+'.xlsx')
		DebugPrint(consld_fname)
		workbook = xlsxwriter.Workbook(consld_fname)
		worksheet = workbook.add_worksheet()
		bold1 = workbook.add_format({'bold': 1})

		for dr in data_rate.split(','):
			if dr not in power_evm_dict[ch].keys():
				power_evm_dict[ch][dr]={}
			if dr not in channel_power_evm_dict.keys():
				channel_power_evm_dict[dr]={}
			if(standard=='11ac'):
				fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+stbc+'_'+str(dr)
			elif(standard=='11n'):
				fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+bw+'Mhz_'+gi+'_'+coding+'_'+greenfield_mode+'_'+stbc+'_'+str(dr)
			else:
				if(standard=='11b'):
					fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+preamble+'_'+str(dr)
				else:
					fname=standard+'_'+streams_chain+'_'+freq+'_Chn'+ch+'_'+str(dr)
			dr_file_name=os.path.join(op_file_path,'TX_Channels_'+fname+'.xlsx')
			workbook_dr = xlsxwriter.Workbook(dr_file_name)
			worksheet_dr = workbook_dr.add_worksheet()
			bold = workbook_dr.add_format({'bold': 1})
			dut.set_dut_datarate(dr,standard)
			dut_txpower_loop(DUT_TestConfigParams,ch,dr)
			#f_time.write(str(time.time()))
			workbook_dr.close()
			copy_file(op_dr_file_path=dr_file_name,dutModel=dutModel,release=release,standard=standard,streams=streams,stbc=stbc,coding=coding,gi=gi,greenfield_mode=greenfield_mode,preamble=preamble,ch=ch,test='tx')
		try:
			plot_power_evm(ch)
			workbook.close()
		except  Exception,e:
			print e.args
			workbook.close()
			pass
	try:
		plot_power_evm_cons_png()
		workbook_cons.close()
	except  Exception,e:
		print e.args
		workbook_cons.close()

 	#PHY_PERFORMANCE - bugfix
	document_path=""
	document_path=os.path.join(op_file_path.split(standard)[0],'TX_Characterization_Across_Channels_'+release+'_'+board_num+'_'+rf_num+'.docx')
	try:
		document = Document(document_path)
	except:
		document = Document()

	copy_file(op_dr_file_path=consld_fname,dutModel=dutModel,release=release,standard=standard,streams=streams,stbc=stbc,coding=coding,gi=gi,greenfield_mode=greenfield_mode,preamble=preamble,ch=ch,test='tx')
	dut.pktgen_tool(DUT_TestConfigParams,'kill')
	copy_file(op_dr_file_path=document_path,dutModel=dutModel,release=release,test='tx')
	equipment.close_vsg()
	dut.dut_close()