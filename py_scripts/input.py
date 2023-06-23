#########################################
#Release Name
#########################################
release='MAIN'

#########################################
#DUT Base Board Number
#########################################
board_num='CALDER_WLAN'

#########################################
#DUT RF Board Number
#########################################
rf_num='C0_RF'

#########################################
#DUT Reboot Time
#########################################
reboot_time=30

#########################################
#DUT Proc stats directory
#Ex: rpu,uccp420
#########################################
stats_dir='rpu'
# stats_dir='uccp420'

################################################################
#####################    SSH ACCESS    #########################
################################################################
#Below params are mandatory if execution of DUT is with SSH
dut_mgmt_ip='10.90.1.9'
dut_username='root'
dut_password='root'
################################################################
#####################    SSH ACCESS    #########################
################################################################
#Web Power switch details
#EX: For Power switch which is access using browser     : wps_10.90.2.3
#	 For Power switch which is access using telnet(APC) : apc_10.90.2.3
#    If power switch is not connected : wps_no
#########################################
web_power_switch='apc_10.90.88.98'
#web_power_switch='wps_no'
#########################################
#Cable Loss of both the cabled in the channels where production calibration is performed
# '24G_BAND':2, #All 2.4G Channels
# '5G_BAND1':2, #All 5G Channels from 36-52
# '5G_BAND2':2, #All 5G Channels from -108
# '5G_BAND3':2, #All 5G Channels from -132
# '5G_BAND4':2  #All 5G Channels from -165
#########################################
cable_loss_dict={'1x1':
					{
						'24G_BAND':0.8,
						'5G_BAND1':1.5,    # cable loss (2dB) + PCB loss (1.9dB) + Antenna connector loss (0.6dB)
						'5G_BAND2':1.5,
						'5G_BAND3':1.5,
						'5G_BAND4':1.5
					},
				'2x2':
					{
						'24G_BAND':0.8,
						'5G_BAND1':1.5,    # cable loss (2dB) + PCB loss (1.9dB) + Antenna connector loss (0.6dB)
						'5G_BAND2':1.5,
						'5G_BAND3':1.5,
						'5G_BAND4':1.5
					}
				}

#########################################
#Splitter Loss
#########################################
splitter_loss=8

debug_enable='1'
tx_continuous_enable='0'