#-------------------------------------------------------------------------------
# Name:        iqxel
# Purpose:     This module has all the APIs(SCPI commands) for configurint Litepoint iQxel-160/280 VSG/VSA.
# Author:      kranthi.kishore
# Created:     14-06-2015
# Copyright:   Imagination Technologies Ltd
#-------------------------------------------------------------------------------
from   socket import *
import time

from common_utils import *
from input import *

datarate_dict={
                '11a':{'6':'MCS 0','9':'MCS 1','12':'MCS 2','18':'MCS 3','24':'MCS 4','36':'MCS 5','48':'MCS 6','54':'MCS 7'},
                '11n':{'MCS0':'MCS 0','MCS1':'MCS 1','MCS2':'MCS 2','MCS3':'MCS 3','MCS4':'MCS 4','MCS5':'MCS 5','MCS6':'MCS 6','MCS7':'MCS 7',
                        'MCS8':'MCS 8','MCS9':'MCS 9','MCS10':'MCS 10','MCS11':'MCS 11','MCS12':'MCS 12','MCS13':'MCS 13','MCS14':'MCS 14','MCS15':'MCS 15'},
                '11g':{'6':'MCS 0','9':'MCS 1','12':'MCS 2','18':'MCS 3','24':'MCS 4','36':'MCS 5','48':'MCS 6','54':'MCS 7'},
                '11b':{'1':'DRAT RATE1','2':'DRAT RATE2','5.5':'DRAT RATE5_5','11':'DRAT RATE11'},
                '11ac':{'MCS0':'MCS 0','MCS1':'MCS 1','MCS2':'MCS 2','MCS3':'MCS 3','MCS4':'MCS 4','MCS5':'MCS 5','MCS6':'MCS 6','MCS7':'MCS 7',
                        'MCS8':'MCS 8','MCS9':'MCS 9'},
                '11ax':{'MCS0':'MCS 0','MCS1':'MCS 1','MCS2':'MCS 2','MCS3':'MCS 3','MCS4':'MCS 4','MCS5':'MCS 5','MCS6':'MCS 6','MCS7':'MCS 7',
                        'MCS8':'MCS 8','MCS9':'MCS 9','MCS10':'MCS 10','MCS11':'MCS 11'}
                }
class IQXEL:
    def __init__(self,tester,equip_ip):
        self.tester=tester.split('_')[-1]
        self.hostName = equip_ip
        self.port = 24000
#Start VSG
    def start_vsg(self):
        """Establish a socket connection to VSG."""
        # print "\nConfiguring IQXEL ", self.tester
        DebugPrint("\nConfiguring IQXEL " + self.tester)
        global cntrl_sckt
        ADDR = (self.hostName,self.port)
        cntrl_sckt = socket(AF_INET, SOCK_STREAM)   # Create and
        cntrl_sckt.connect(ADDR)
        time.sleep(1)

    #Close VSG
    def close_vsg(self):
        """Close the socket connection to VSG"""
        DebugPrint('Closing VSG')
        cntrl_sckt.close()
        time.sleep(1)

    #802.11a Initialization settings
    def config_11a(self):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:STAN A\n')

    #802.11b Initialization settings
    def config_11b(self):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:STAN B\n')

    #802.11g Initialization settings
    def config_11g(self):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:STAN A\n')

    #802.11n Initialization settings
    def config_11n(self):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:STAN N\n')

    #802.11ac Initialization settings
    def config_11ac(self):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:STAN AC\n')

    #802.11ax Initialization settings
    def config_11ax(self):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:STAN AX\n')

    #Set Default
    def set_equip_default(self):
        # print "\nSetting VSA to default"
        DebugPrint("\nSetting VSA to default")
        cntrl_sckt.sendall('*RST\n')
        if(self.tester.lower()=='280'):
            cntrl_sckt.sendall('MROUT1;PORT:RES RF1A,OFF\n')
            cntrl_sckt.sendall('MROUT2;PORT:RES RF2A,OFF\n')
            cntrl_sckt.sendall('SYS;MVSA:DEL\n')
            cntrl_sckt.sendall('SYS;MVSG:DEL\n')
            cntrl_sckt.sendall('SYS;MROUT:DEL\n')
        elif(self.tester.lower()=='160'):
            cntrl_sckt.sendall('*RST\n')
            cntrl_sckt.sendall('MROUT1;PORT:RES RF1A,OFF\n')
            cntrl_sckt.sendall('MROUT2;PORT:RES RF2A,OFF\n')
            cntrl_sckt.sendall('SYS;MVSA:DEL\n')
            cntrl_sckt.sendall('SYS;MVSG:DEL\n')
            cntrl_sckt.sendall('SYS;MROUT:DEL\n')
        time.sleep(1)

    #Modulation Type
    def set_modulation(self,standard):
        # print "\nSetting "+standard+" in VSA"
        DebugPrint("\nSetting "+standard+" in VSA")
        eval('self.config_'+standard+'()')


    #Setting Datarate
    def set_datarate(self,modulation,standard,data_rate):
        # print "\nSetting data rate ",data_rate
        DebugPrint("\n----------------------------------------------------------------------------------Setting data rate "+data_rate)
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:'+modulation+':'+datarate_dict[standard][data_rate]+'\n')

    #Setting Payload
    def set_payload(self,standard,payload):
        # print "\nSetting payload ",payload
        DebugPrint("\nSetting payload "+str(payload))
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:NBYT '+payload+'\n')

    #Setting MAC Header OFF
    def set_macheader(self):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:MACH OFF\n')

    #Setting Channel
    def apply_vsg(self,bw='',chn='',streams='2x2',p20_flag = 0):
        DebugPrint('Applying VSG channel '+str(chn)+' and BW '+str(bw))
        if (bw=='20') :
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(chn)+'\n')
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 20000000\n')#20MHz
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 20000000\n')#20MHz
        elif (bw=='20in40') :
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn - (p20_flag )*4))+'\n')
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 40000000\n')#20MHz
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 40000000\n')#20MHz
        elif (bw=='20in80'):
            # each channel is 5MHz apart to shift centre frequency(CF) by 20MHz shift channel by 4
            # for p20 offset 0 VSG CF is 30 MHz higher than DUT CF shift +6
            # for p20 offset 1 VSG CF is 10 MHz higher than DUT CF shift +2
            # for p20 offset 2 VSG CF is 10 MHz lower than DUT CF shift -2
            # for p20 offset 3 VSG CF is 30 MHz lower than DUT CF shift -6
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn + (1.5 - p20_flag)*4))+'\n')
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 80000000\n')#20MHz
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 80000000\n')#80MHz
        elif(bw=='40'):
##          if str(chn) in prime_20_sec_20_flags_dict[bw].keys():
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(chn)+'\n')#For Plus
##          else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)-2)+'\n')#For Minus
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 40000000\n')#40MHz
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 40000000\n')#20MHz
        elif(bw=='40in80'):
##          if str(chn) in prime_20_sec_20_flags_dict[bw].keys():
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(chn)+'\n')#For Plus
##          else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn-2 + (p20_flag -1.5)*4))+'\n')#For Minus
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 40000000\n')#40MHz
        elif(bw=='80'):
##          if(prime_20_sec_20_flags_dict[bw][str(chn)]=='l'):
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)-6)+'\n')#For Minus
##          elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='lr'):
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)+2)+'\n')
##          elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='rl'):
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)-2)+'\n')
##          elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='r'):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn))+'\n')#For Plus
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 80000000\n')#80MHz
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 80000000\n')#80MHz
        if(int(chn)<20):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:BAND 2G4\n')
        else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:BAND 5G\n')
        if(streams=='1x1'):
            cntrl_sckt.sendall('CHAN1;WIFI; HSET:ALL VSG1'+chain_sel_scpi_cmd+'\n')
        elif(streams=='2x2'):
            cntrl_sckt.sendall('CHAN1;WIFI; HSET:ALL MVSGALL\n')

    #Setting Amplitude
    def set_amplitude(self,streams,ampl):
        # print "\nSetting amplitude ",ampl
        DebugPrint("\nSetting amplitude "+str(ampl))
        if(streams=='1x1'):
            cntrl_sckt.sendall("VSG1"+chain_sel_scpi_cmd+";POW "+ampl+"\n")
        elif(streams=='2x2'):
            cntrl_sckt.sendall("MVSGALL;POW "+ampl+"\n")

    #Set Bandwidth 20/40 MHz
    def set_bandwidth(self,standard='',bw=''):
        DebugPrint('Setting BW '+str(bw))
        if(bw=='20') or (bw=='20in40') or (bw=='20in80'):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 20000000\n')#20MHz
        elif(bw=='40'):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 40000000\n')#40MHz
        elif(bw=='80'):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:CBW 80000000\n')#80MHz

    #Setting Wavegap/Idle Interval
    def set_idleinterval(self,intv):
        # print "\nSetting interval ",intv
        DebugPrint("\nSetting wavegap interval "+str(intv))
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:GAP '+str(float(intv)/1000000)+'\n')


    #Set Spatial Streams
    def set_streams(self,standard,streams):
        # print "\nSetting streams ",streams
        DebugPrint("\nSetting streams "+streams)
        if(streams=='1x1'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:NSST 1\n")#1x1
        elif(streams=='2x2'):
            if(standard =='11ac' or standard =='11ax'):
                cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:NSST 2\n")#2x2

    #Set Guard Interval
    def set_guardinterval(self,gi):
        # print "\nSetting Guard Interval ",gi
        DebugPrint("\nSetting Guard Interval "+gi)
        if(gi.lower()=='sgi'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:SGI ON\n")#SGI
        elif(gi.lower()=='lgi'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:SGI OFF\n")#LGI

    #Set STBC
    def set_stbc(self,stbc):
        # print "\nSetting STBC ",stbc
        DebugPrint("\nSetting STBC "+stbc)
        cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:STBC "+str(stbc)[-1]+"\n")

    #Set Coding Type
    def set_coding(self,coding):
        # print "\nSetting Coding Technique ",coding
        DebugPrint("\nSetting Coding Technique "+coding)
        if(coding.lower()=='ldpc'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:COD LDPC\n")#LDPC
        elif(coding.lower()=='bcc'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:COD BCC\n")#BCC

    #Set Greenfield Mode
    def set_greenfield(self,greenfield_mode):
        # print "\nSetting Greenfield Mode ",greenfield_mode
        DebugPrint("\nSetting Greenfield Mode "+greenfield_mode)
        if(greenfield_mode.lower()=='greenfield'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:GRE ON\n")#Greenfield
        elif(greenfield_mode.lower()=='mixed'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:OFDM:GRE OFF\n")#Mixed

    #Set Preamble
    def set_preamble(self,preamble):
        # print "\nSetting preamble ",preamble
        DebugPrint("\nSetting preamble "+preamble)
        if(preamble.lower=='short'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:DSSS:PRE SHORT\n")#Short
        elif(preamble.lower=='long'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:WAVE:DSSS:PRE LONG\n")#Long

    #RF ON/OFF
    def rf_on_off(self,rf_state='on',streams='2x2'):
        # print "\nSetting RF ",rf_state
        DebugPrint("\nSetting RF "+rf_state)
        if(rf_state=='off'):
            if(streams=='1x1'):
                cntrl_sckt.sendall("VSG1"+chain_sel_scpi_cmd+";POW:STAT"+" "+"OFF\n")
            elif(streams=='2x2'):
                cntrl_sckt.sendall("MVSGALL;POW:STAT"+" "+"OFF\n")
        elif(rf_state=='on'):
            if(streams=='1x1'):
                cntrl_sckt.sendall("VSG1"+chain_sel_scpi_cmd+";POW:STAT"+" "+"ON\n")
            elif(streams=='2x2'):
                cntrl_sckt.sendall("MVSGALL;POW:STAT"+" "+"ON\n")

    #Generate Waveform
    def generate_waveform(self,streams='2x2',count='1000'):
        # print "\nGenerating waveform "
        DebugPrint("\nGenerating waveform ")
        print "\n number of packets generated in VSG ",count
        # cntrl_sckt.sendall("CHAN1;WIFI\n")
        # cntrl_sckt.sendall('wave:gen:mmem "\//user/wf.iqvsg", "WIFI wave generation from GUI"\n')
        #return
        if(streams=='1x1'):
            #cntrl_sckt.sendall('*wai;VSG1 ;wave:load "\//user/wf.iqvsg";wave:exec on\n')
            cntrl_sckt.sendall('VSG1'+chain_sel_scpi_cmd+';WLIS:COUN '+count+'\n')
            #cntrl_sckt.sendall('VSG1 ;wave:exec off;WLIST:WSEG1:DATA "\//user/wf.iqvsg";wlist:wseg1:save;WLIST:COUNT:ENABLE WSEG1;WAVE:EXEC ON, WSEG1\n')
        elif(streams=='2x2'):
            #
            cntrl_sckt.sendall('MVSGALL;WLIS:COUN '+count+'\n')
            #cntrl_sckt.sendall('MVSGALL ;wave:exec off;WLIST:WSEG1:DATA "\//user/wf.iqvsg";wlist:wseg1:save;WLIST:COUNT:ENABLE WSEG1;WAVE:EXEC ON, WSEG1\n')

    #Start Pumping
    def send_packets(self,streams='2x2',action='run',wave_type='default'):
        # print 'send packets'

        DebugPrint('send packets... ')

        self.rf_on_off(rf_state='on',streams=streams)
        if(wave_type=='default'):
            cntrl_sckt.sendall("CHAN1;WIFI\n")
            cntrl_sckt.sendall('wave:gen:mmem "user/wf.iqvsg", "WIFI wave generation from GUI"\n')
            if(action=='run'):
                if(streams=='1x1'):
                    cntrl_sckt.sendall('VSG1'+chain_sel_scpi_cmd+';WLIS:COUN 1000\n') # PHY_PERFORMANCE . should come as input
                    cntrl_sckt.sendall('*wai;VSG1'+chain_sel_scpi_cmd+' ;wave:load "user/wf.iqvsg";wave:exec on\n')
                    cntrl_sckt.sendall('VSG1'+chain_sel_scpi_cmd+' ;wave:exec off;WLIST:WSEG1:DATA "user/wf.iqvsg";wlist:wseg1:save;WLIST:COUNT:ENABLE WSEG1;WAVE:EXEC ON, WSEG1\n')
                elif(streams=='2x2'):
                    cntrl_sckt.sendall('MVSGALL;WLIS:COUN 1000\n') # PHY_PERFORMANCE . should come as input
                    cntrl_sckt.sendall('*wai;MVSGALL ;wave:load "user/wf.iqvsg";wave:exec on\n')
                    cntrl_sckt.sendall('MVSGALL ;wave:exec off;WLIST:WSEG1:DATA "user/wf.iqvsg";wlist:wseg1:save;WLIST:COUNT:ENABLE WSEG1;WAVE:EXEC ON, WSEG1\n')
            elif(action=='disable'):
                if(streams=='1x1'):
                    cntrl_sckt.sendall('VSG1'+chain_sel_scpi_cmd+'; WAVE:EXEC OFF;WLIST:COUNT:DISABLE WSEG1\n')
                elif(streams=='2x2'):
                    cntrl_sckt.sendall('MVSGALL; WAVE:EXEC OFF;WLIST:COUNT:DISABLE WSEG1\n')
        else:
            self.load_degrade_waveform(streams=streams,action=action)

    #Set RF Port on VSA
    def set_rf(self,streams='2x2',test='rx',chain_sel='1'):
        global chain_sel_scpi_cmd
        chain_sel_scpi_cmd=""
        print 'Setting RF Port in ',self.tester
        DebugPrint('Setting RF Port in '+self.tester)
        if(test=='rx'):
            if(self.tester.lower()=='80'):
                if(streams=='1x1'):
                    if(chain_sel=='1'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF1,VSG1\n")#RF1
                    elif(chain_sel=='2'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF2,VSG1\n")#RF1
            elif(self.tester.lower()=='160'):
                    if(streams=='1x1'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF1A,VSG11\n")#RF1
                    elif(streams=='2x2'):
                        cntrl_sckt.sendall("MVSG:DEF:ADD VSG11\n")#RF1
                        cntrl_sckt.sendall("MVSG:DEF:ADD VSG12\n")#RF2
                        cntrl_sckt.sendall("MROUT:DEF:ADD ROUT11\n")
                        cntrl_sckt.sendall("MROUT:DEF:ADD ROUT12\n")#Adding Module
                        time.sleep(2)
                        cntrl_sckt.sendall('MROUT1;PORT:RES RF1A,VSG11\n')#Adding Module
                        cntrl_sckt.sendall('MROUT2;PORT:RES RF2A,VSG12\n')

            elif(self.tester.lower()=='280'):
                if(streams=='1x1'):
                    if(chain_sel=='1'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF1A,VSG11\n")#RF1
                        chain_sel_scpi_cmd=chain_sel
                    elif(chain_sel=='2'):
                        cntrl_sckt.sendall("ROUT12;PORT:RES RF1B,VSG12\n")#RF1
                        chain_sel_scpi_cmd=chain_sel
                elif(streams=='2x2'):
                    cntrl_sckt.sendall("MVSG:DEF:ADD VSG11\n")#RF1
                    cntrl_sckt.sendall("MVSG:DEF:ADD VSG12\n")#RF2
                    cntrl_sckt.sendall("MROUT:DEF:ADD ROUT11\n")
                    cntrl_sckt.sendall("MROUT:DEF:ADD ROUT12\n")#Adding Module
                    time.sleep(2)
                    cntrl_sckt.sendall('MROUT1;PORT:RES RF1B,VSG12\n')#Adding Module
                    cntrl_sckt.sendall('MROUT2;PORT:RES RF1A,VSG11\n')
                    cntrl_sckt.sendall('MROUT1;PORT:RES RF1A,VSG11\n')
                    cntrl_sckt.sendall('MROUT2;PORT:RES RF1B,VSG12\n')
        elif(test=='tx'):
            if(self.tester.lower()=='80'):
                if(streams=='1x1'):
                    if(chain_sel=='1'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF1,VSA1\n")#RF1
                    elif(chain_sel=='2'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF2,VSA1\n")#RF1
            elif(self.tester.lower()=='160'):
                if(streams=='1x1'):
                    if(chain_sel=='1'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF1A,VSA11\n")#RF1
                    elif(chain_sel=='2'):
                        cntrl_sckt.sendall("ROUT12;PORT:RES RF1B,VSA12\n")#RF1
                elif(streams=='2x2'):
                    cntrl_sckt.sendall("MVSA:DEF:ADD VSA11\n")#RF1
                    cntrl_sckt.sendall("MVSA:DEF:ADD VSA12\n")#RF2
                    cntrl_sckt.sendall("MROUT:DEF:ADD ROUT11\n")#ADD ROUT11
                    cntrl_sckt.sendall("MROUT:DEF:ADD ROUT12\n")#Adding Module
                    time.sleep(2)
                    cntrl_sckt.sendall('MROUT2;PORT:RES RF2A,VSA12\n')
                    cntrl_sckt.sendall('MROUT1;PORT:RES RF1A,VSA11\n')
            elif(self.tester.lower()=='280'):
                if(streams=='1x1'):
                    chain_sel_scpi_cmd=chain_sel
                    if(chain_sel=='1'):
                        cntrl_sckt.sendall("ROUT1;PORT:RES RF1A,VSA11\n")#RF1
                    elif(chain_sel=='2'):
                        cntrl_sckt.sendall("ROUT12;PORT:RES RF1B,VSA12\n")#RF1
                elif(streams=='2x2'):
                    cntrl_sckt.sendall("MVSA:DEF:ADD VSA11\n")#RF1
                    cntrl_sckt.sendall("MVSA:DEF:ADD VSA12\n")#RF2
                    cntrl_sckt.sendall("MROUT:DEF:ADD ROUT11\n")
                    cntrl_sckt.sendall("MROUT:DEF:ADD ROUT12\n")#Adding Module
                    time.sleep(2)
                    cntrl_sckt.sendall('MROUT1;PORT:RES RF1B,VSA12\n')#Adding Module
                    cntrl_sckt.sendall('MROUT2;PORT:RES RF1A,VSA11\n')
                    cntrl_sckt.sendall('MROUT1;PORT:RES RF1A,VSA11\n')
                    cntrl_sckt.sendall('MROUT2;PORT:RES RF1B,VSA12\n')

    def generate_degrade_waveform(self,awgn_snr='200',bw='20'):
        # print 'Generating noise wave'
        cntrl_sckt.sendall("CHAN1;GPRF;WAVE:DEGR:AWGN:SBW "+bw+"000000\n")
        cntrl_sckt.sendall("CHAN1;WIFI\n")

        cntrl_sckt.sendall('wave:gen:mmem "/user/wf.iqvsg", "WIFI wave generation from GUI"\n')
        cntrl_sckt.sendall("CHAN1;GPRF;WAVE:DEGR:AWGN:SNR ("+awgn_snr+7*(','+awgn_snr)+")\n")
        cntrl_sckt.sendall('GPRF;WAVE:DEGR:APPL "/user/wf_degrade.iqvsg","/user/wf.iqvsg"\n')

    def load_degrade_waveform(self,streams='2x2',action='run'):
        # print 'Loading noise wave'
        if(streams=='1x1'):
            cntrl_sckt.sendall('VSG1; WAVE:LOAD "/user/wf_degrade.iqvsg"\n')
        elif(streams=='2x2'):
            cntrl_sckt.sendall('MVSGALL; WAVE:LOAD "/user/wf_degrade.iqvsg"\n')

        if(action=='run'):
            if(streams=='1x1'):
                #VSG1 ;wave:exec off;WLIST:WSEG1:DATA "/user/deg.iqvsg";wlist:wseg1:save;WLIST:COUNT:ENABLE WSEG1;WAVE:EXEC ON, WSEG1

                cntrl_sckt.sendall('VSG1'+chain_sel_scpi_cmd+';WLIS:COUN 1000\n')
                cntrl_sckt.sendall('*wai;VSG1'+chain_sel_scpi_cmd+' ;wave:load "user/wf_degrade.iqvsg";wave:exec on\n')
                cntrl_sckt.sendall('VSG1'+chain_sel_scpi_cmd+' ;wave:exec off;WLIST:WSEG1:DATA "user/wf_degrade.iqvsg";wlist:wseg1:save;WLIST:COUNT:ENABLE WSEG1;WAVE:EXEC ON, WSEG1\n')
            elif(streams=='2x2'):
                cntrl_sckt.sendall('MVSGALL;WLIS:COUN 1000\n')
                cntrl_sckt.sendall('*wai;MVSGALL ;wave:load "user/wf_degrade.iqvsg";wave:exec on\n')
                cntrl_sckt.sendall('MVSGALL ;wave:exec off;WLIST:WSEG1:DATA "user/wf_degrade.iqvsg";wlist:wseg1:save;WLIST:COUNT:ENABLE WSEG1;WAVE:EXEC ON, WSEG1\n')
        elif(action=='disable'):
            if(streams=='1x1'):
                cntrl_sckt.sendall('VSG1'+chain_sel_scpi_cmd+'; WAVE:EXEC OFF;WLIST:COUNT:DISABLE WSEG1\n')
            elif(streams=='2x2'):
                cntrl_sckt.sendall('MVSGALL; WAVE:EXEC OFF;WLIST:COUNT:DISABLE WSEG1\n')

    def init_vsg_funcs(self,standard='11ac',bw='20',streams='2x2',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',test='rx',chain_sel='1'):
        self.start_vsg()
        self.set_equip_default()
        self.set_rf(streams=streams,test=test,chain_sel=chain_sel)
        self.set_modulation(standard)
        self.set_bandwidth(bw=bw,standard=standard)
        self.set_idleinterval(250)
        #self.set_idleinterval(1000) #PHY_PERFORMANCE dont update to 10000. this cause fails because capture times are reduced.
        if((standard=='11n')or(standard=='11ac')):
            self.set_streams(standard,streams)
            self.set_stbc(stbc)
            self.set_guardinterval(gi)
            self.set_coding(coding)
        if(standard=='11ax'):
            self.set_streams(standard,streams)
            self.set_stbc(stbc)
            self.set_coding(coding)
            #self.set_guardinterval(gi)
        if(standard=='11n'):
            self.set_greenfield(greenfield_mode)
        if(standard=='11b'):
            self.set_preamble(preamble)
        self.generate_waveform(streams=streams)
        self.rf_on_off(rf_state='on',streams=streams)

    #Modulation Type
    def set_vsa_modulation(self,standard):
        DebugPrint('Setting VSA Modulation as '+modulation)
        if(standard=='11b'):
            modulation='dsss'
        else:
            modulation='ofdm'
        print "\nSetting "+modulation+" in VSA"
        cntrl_sckt.sendall("CHAN1;WIFI;CONF:STAN "+modulation.upper()+"\n")
        if(standard=='11b'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:STAN DSSS\n")

    #Setting Capture Length
    def set_capturelength(self,len,streams):
        print "\nSetting capture length ",len
        DebugPrint("\nSetting capture length "+str(len))
        if(streams=='1x1'):
            cntrl_sckt.sendall('VSA1'+chain_sel_scpi_cmd+';CAPT:TIME '+str(float(len)/1000)+'\n')
        elif(streams=='2x2'):
            cntrl_sckt.sendall('MVSAALL;CAPT:TIME '+str(float(len)/1000)+'\n')

    #Apply to VSA
    def apply_vsa(self,chn='',bw='',streams='2x2',sta20_flag = 0):
        print "\nApply settings to VSA",chn
        DebugPrint("\nApply settings to VSA"+str(chn))
        if(bw=='20'):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(chn)+'\n')
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 20000000\n')#20MHz
        elif (bw=='20in40'):
            # each channel is 5MHz apart to shift centre frequency(CF) by 20MHz shift channel by 4
            # VSA when configured for 40MHz bandwidth it adds a 10MHz shift in CF
            # while ch 144 20MHz BW CF is set as 5720MHz,  ch 144 40MHz BW CF is 5730MHz for VSA
            # for p20 offset 0 VSA CF needs to be 0 MHz higher than DUT CF shift 0
            # for p20 offset 1 VSA CF needs to be 20 MHz lower than DUT CF shift -4
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(chn- (sta20_flag*4))+'\n')
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 40000000\n')#40MHz
        elif (bw=='20in80'):
            # each channel is 5MHz apart to shift centre frequency(CF) by 20MHz shift channel by 4
            # for p20 offset 0 VSA CF needs to be 30 MHz higher than DUT CF shift +6
            # for p20 offset 1 VSA CF needs to be 10 MHz higher than DUT CF shift +2
            # for p20 offset 2 VSA CF needs to be 10 MHz lower than DUT CF shift -2
            # for p20 offset 3 VSA CF needs to be 30 MHz lower than DUT CF shift -6
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(chn + (1.5 - sta20_flag)*4)+'\n')
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 80000000\n')#80MHz
        elif (bw=='40'):
##          if str(chn) in prime_20_sec_20_flags_dict[bw].keys():
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(chn)+'\n')#For Plus
##          else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)-2)+'\n')#For Minus
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 40000000\n')#40MHz
        elif(bw=='80' ):
##          if(prime_20_sec_20_flags_dict[bw][str(chn)]=='l'):
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)-6)+'\n')#For Minus
##          elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='lr'):
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)+2)+'\n')
##          elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='rl'):
##              cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn)-2)+'\n')
##          elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='r'):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:IND1 '+str(int(chn))+'\n')#For Plus
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:CHAN:CBW 80000000\n')#80MHz
        if(int(chn)<20):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:BAND 2G4\n')
        else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:BAND 5G\n')
        if(streams=='1x1'):
            cntrl_sckt.sendall('CHAN1;WIFI; HSET:ALL VSA1'+chain_sel_scpi_cmd+'\n')
        elif(streams=='2x2'):
            cntrl_sckt.sendall('CHAN1;WIFI; HSET:ALL MVSAALL\n')

    #Save Power Values
    def save_power_values(self,dr,txp,ch,standard,streams,cable_loss_1x1,cable_loss_2x2):
        DebugPrint('Saving Power Values')
        cntrl_sckt.sendall('WIFI\n')
        if(standard=='11b'):
            cntrl_sckt.sendall('CALC:POW 0,1\n')
        else:
            cntrl_sckt.sendall('CALC:POW 0,30\n')
        cntrl_sckt.sendall('FETCh:POW:SIGN1:AVER?\n')
        result=cntrl_sckt.recv(200)
        DebugPrint(result)
        power_1x1=result.split(',')[-1]
        power_2x2=result.split(',')[-1]
        DebugPrint(power_1x1)
        if(streams=='2x2'):
            cntrl_sckt.sendall('FETCh:POW:SIGN2:AVER?\n')
            time.sleep(1)
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            power_2x2=result.split(',')[-1]
            DebugPrint(power_2x2)
        return float(power_1x1)+float(cable_loss_1x1),float(power_2x2)+float(cable_loss_2x2)

    #Save tx Stats
    def save_txquality_stats(self,dr,txp,ch,standard,streams):
        # print('Saving TX Quality Values')
        DebugPrint('Saving TX Quality Stats')
        if(standard=='11b'):
            evm_1x1=self.save_evm_txquality_stats(dr,txp,ch,standard,streams)
            if(evm_1x1=='#10\n'):
                evm_1x1=0
            phaseerr_1x1=self.save_phaseerr(dr,txp,standard,streams)
            freq_error_1x1=self.save_freqerr(dr,txp,standard,streams)
            sysclkerr_1x1=self.save_sysclkerr(dr,txp,standard,streams)
            lo_leakage_1x1=self.save_lo_leakage(dr,txp,standard,streams)
            ampimb_1x1=self.save_ampimb(dr,txp,standard,streams)
            phaseimb_1x1=self.save_phaseimb(dr,txp,standard,streams)
            return round(float(evm_1x1),2),float(phaseerr_1x1),float(freq_error_1x1),float(sysclkerr_1x1),float(lo_leakage_1x1),float(ampimb_1x1),float(phaseimb_1x1)
        if(streams=='1x1'):
            evm_1x1=self.save_evm_txquality_stats(dr,txp,ch,standard,streams)
            if(evm_1x1=='#10\n'):
                evm_1x1=0
            phaseerr_1x1=self.save_phaseerr(dr,txp,standard,streams)
            freq_error_1x1=self.save_freqerr(dr,txp,standard,streams)
            sysclkerr_1x1=self.save_sysclkerr(dr,txp,standard,streams)
            lo_leakage_1x1=self.save_lo_leakage(dr,txp,standard,streams)
            ampimb_1x1=self.save_ampimb(dr,txp,standard,streams)
            phaseimb_1x1=self.save_phaseimb(dr,txp,standard,streams)
            return round(float(evm_1x1),2),float(phaseerr_1x1),float(freq_error_1x1),float(sysclkerr_1x1),float(lo_leakage_1x1),float(ampimb_1x1),float(phaseimb_1x1)
        evm_1x1,evm_2x2=self.save_evm_txquality_stats(dr,txp,ch,standard,streams)
        phaseerr_1x1,phaseerr_2x2=self.save_phaseerr(dr,txp,standard,streams)
        freq_error_1x1,freq_error_2x2=self.save_freqerr(dr,txp,standard,streams)
        sysclkerr_1x1,sysclkerr_2x2=self.save_sysclkerr(dr,txp,standard,streams)
        lo_leakage_1x1,lo_leakage_2x2=self.save_lo_leakage(dr,txp,standard,streams)
        ampimb_1x1,ampimb_2x2=self.save_ampimb(dr,txp,standard,streams)
        phaseimb_1x1,phaseimb_2x2=self.save_phaseimb(dr,txp,standard,streams)
        return round(float(evm_1x1),2),round(float(evm_2x2),2),float(phaseerr_1x1),float(phaseerr_2x2),float(freq_error_1x1),float(freq_error_2x2),float(sysclkerr_1x1),float(sysclkerr_2x2),float(lo_leakage_1x1),float(lo_leakage_2x2),float(ampimb_1x1),float(ampimb_2x2),float(phaseimb_1x1),float(phaseimb_2x2)

    #Save OBW
    def save_obw_values(self,standard,streams):
        # print('Saving OBW Values')
        DebugPrint('Saving OBW Values')
        if(standard=='11b'):
            obw_1x1='20000000'
        else:
            cntrl_sckt.sendall('FETCH:TXQuality:OFDM:INFO:CBW?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            obw_1x1=result.split(',')[1]
        # If unable to read OBW first time try again
        if (obw_1x1 =='9.91E+37'):
            obw_1x1=result.split(',')[3]
        return str(int(obw_1x1)/1000000)

    #Save Data Rate Values
    def save_datarate_values(self,standard,streams):
        # print('Saving data rate Values')
        DebugPrint('Saving data rate Values')
        if(standard=='11b'):
            cntrl_sckt.sendall('FETCH:TXQuality:DSSS:INFO:DRATE?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            dr_1x1=result.split(',')[1].rstrip()
        elif(standard=='11g' or standard=='11a'):
            cntrl_sckt.sendall('FETCH:TXQuality:OFDM:INFO:DRATE?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            dr_1x1=result.split(',')[1].rstrip()
        else:
            cntrl_sckt.sendall('FETCH:TXQuality:OFDM:INFO:MCS?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            dr_1x1=result.split(',')[1].rstrip()
        if(standard=='11n' or standard =='11ac' or standard =='11ax'):
            dr_1x1='MCS'+dr_1x1
        return dr_1x1

    def save_freq_values(self,standard,streams):
        # print('Saving frequency Values')
        cntrl_sckt.sendall('FORM:READ:DATA ASC\n')
        cntrl_sckt.sendall('FETCh:SEGMent1:SPECtrum:OFRequency?\n')
        time.sleep(2)
        result=cntrl_sckt.recv(500000)
        freq_values=result.split(',')
        freq_values=[float(fv.rstrip().replace('\n0','')) for fv in freq_values]
        m60000000_index_1x1=freq_values.index(-60000000)
        p60000000_index_1x1=freq_values.index(60000000)+1
        # print 'freq_values',freq_values
        # print 'freq_values m p',freq_values[m60000000_index_1x1:p60000000_index_1x1]
        # print len(freq_values[m60000000_index:p60000000_index+1])
        return freq_values[m60000000_index_1x1:p60000000_index_1x1]

    def save_spectrum_values(self,standard,streams):
        # print('Saving spectrum Values')
        cntrl_sckt.sendall('FORM:READ:DATA ASC\n')
        cntrl_sckt.sendall('FETCh:SPECtrum:Signal1?\n')
        time.sleep(1)
        result=cntrl_sckt.recv(5000000)
        spectrum_values_1x1=result.split(',')
        spectrum_values_2x2=result.split(',')
        spectrum_values_1x1=[sv.rstrip() for sv in spectrum_values_1x1]
        spectrum_values_2x2=[sv.rstrip() for sv in spectrum_values_2x2]
        zero_index_list_1x1=[i for i in range(len(spectrum_values_1x1)) if(spectrum_values_1x1[i]=='0')]
        zero_index_list_2x2=[i for i in range(len(spectrum_values_2x2)) if(spectrum_values_2x2[i]=='0')]
        # print zero_index_list_1x1
        # print spectrum_values_1x1
        if(streams=='1x1'):
            if(len(zero_index_list_1x1)==1):
                return spectrum_values_1x1[zero_index_list_1x1[0]+1:]
            return spectrum_values_1x1[zero_index_list_1x1[-2]+1:zero_index_list_1x1[-1]]
        cntrl_sckt.sendall('FETCh:SPECtrum:Signal2?\n')
        time.sleep(1)
        result=cntrl_sckt.recv(5000000)
        spectrum_values_2x2=result.split(',')
        spectrum_values_2x2=[sv.rstrip() for sv in spectrum_values_2x2]
        zero_index_list_2x2=[i for i in range(len(spectrum_values_2x2)) if(spectrum_values_2x2[i]=='0')]
        if(len(zero_index_list_1x1)==1):
            return spectrum_values_1x1[zero_index_list_1x1[0]+1:],spectrum_values_2x2[zero_index_list_2x2[0]+1:]
        return spectrum_values_1x1[zero_index_list_1x1[-2]+1:zero_index_list_1x1[-1]],spectrum_values_2x2[zero_index_list_2x2[-2]+1:zero_index_list_2x2[-1]]

    def save_spectrum_margin(self, standard):
        if (standard == '11ax'):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:SPEC:HLIM:TYPE 11AX\n')
        cntrl_sckt.sendall('FORM:READ:DATA ASC\n')
        cntrl_sckt.sendall('FETC:SEGM1:SPEC:AVER:MARG:OFR?\n')
        time.sleep(1)
        result=cntrl_sckt.recv(5000)
        DebugPrint(result)
        freq =result.split(',')
        cntrl_sckt.sendall('FETC:SEGM1:SPEC:AVER:MARG?\n')
        time.sleep(1)
        result=cntrl_sckt.recv(5000)
        margin =result.split(',')
        if margin[0] == '0':
            status = 'Spectrum mask pass'
        else:
            status = 'Spectrum mask failure'

        DebugPrint(result)
        return freq[1:],margin[1:],status

    #Save EVM Stats
    def save_evm_txquality_stats(self,dr,txp,ch,standard,streams):
        DebugPrint('Saving EVM Values')
        #cntrl_sckt.sendall('CHAN1;WIFI; HSET:ALL VSA1\n')
        cntrl_sckt.sendall('FORM:READ:DATA ASC\n')
        if(standard=='11b'):
            cntrl_sckt.sendall('FETC:TXQuality:DSSS:AVER?\n')
            result=cntrl_sckt.recv(300)
            DebugPrint(result)
            evm_1x1=result.split(',')[1]
            #DebugPrint('802.11b')
            #print "evm=",evm_1x1
            return round(float(evm_1x1)*-1,2)
        else:
            cntrl_sckt.sendall('FETC:OFDM:EVM:DATA:ALL:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            evm_1x1=result.split(',')[1]
            # print 'evm_1x1',evm_1x1
            if(evm_1x1=='#10\n'):
                evm_1x1=0
            if(streams=='1x1'):
                return round(float(evm_1x1)*-1,2)
            evm_2x2=result.split(',')[2]
            return round(float(evm_1x1)*-1,2),round(float(evm_2x2)*-1,2)

    #Save Freq Err
    def save_freqerr(self,dr,txp,standard,streams):
        DebugPrint('Saving Freq ERR Values')
        if(standard=='11b'):
            cntrl_sckt.sendall('FETCh:TXQuality:DSSS:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            freq_error_1x1=result.split(',')[4]
            return float(freq_error_1x1)
        else:
            cntrl_sckt.sendall('FETC:OFDM:FERR:ALL:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            freq_error_1x1=result.split(',')[1]
            #print 'freq_error_1x1',freq_error_1x1
            if(streams=='1x1'):
                return freq_error_1x1
            freq_error_2x2=result.split(',')[2]
        #print  float(freq_error_1x1),float(freq_error_2x2)
        return float(freq_error_1x1),float(freq_error_2x2)

    #Save Phase Err
    def save_phaseerr(self,dr,txp,standard,streams):
        DebugPrint('Saving Phase ERR Values')
        if(standard=='11b'):
            cntrl_sckt.sendall('FETCh:TXQuality:DSSS:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            phaseerr_1x1=result.split(',')[3]
            return float(phaseerr_1x1)
        else:
            cntrl_sckt.sendall('FETC:OFDM:PERR:ALL:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            phaseerr_1x1=result.split(',')[1]
            # print 'phaseerr_1x1',phaseerr_1x1
            if(streams=='1x1'):
                return phaseerr_1x1
            phaseerr_2x2=result.split(',')[2]
        #print  float(phaseerr_1x1),float(phaseerr_2x2)
        return float(phaseerr_1x1),float(phaseerr_2x2)

    #Save Sys Clk Err
    def save_sysclkerr(self,dr,txp,standard,streams):
        DebugPrint('Saving SYSCLKERR Values')
        if(standard=='11b'):
            cntrl_sckt.sendall('FETCh:TXQuality:DSSS:AVER?\n')
            result=cntrl_sckt.recv(300)
            DebugPrint(result)
            sysclkerr_1x1=result.split(',')[6]
            return float(sysclkerr_1x1)
        else:
            cntrl_sckt.sendall('FETC:OFDM:SCER:ALL:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            sysclkerr_1x1=result.split(',')[1]
            # print 'sysclkerr_1x1',sysclkerr_1x1
            if(streams=='1x1'):
                return sysclkerr_1x1
            sysclkerr_2x2=result.split(',')[2]
        #print float(sysclkerr_1x1),float(sysclkerr_2x2)
        return float(sysclkerr_1x1),float(sysclkerr_2x2)

    #Save Gain Imb
    def save_ampimb(self,dr,txp,standard,streams):
        DebugPrint('Saving GainImb Values')
        if(standard=='11b'):
            cntrl_sckt.sendall('FETCh:TXQuality:DSSS:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            ampimb_1x1=result.split(',')[8]
            return ampimb_1x1
        else:
            cntrl_sckt.sendall('FETC:OFDM:AIMB:ALL:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            ampimb_1x1=result.split(',')[1]
            # print 'ampimb_1x1',ampimb_1x1
            if(streams=='1x1'):
                return ampimb_1x1
            ampimb_2x2=result.split(',')[2]
        return float(ampimb_1x1),float(ampimb_2x2)

    #Save Phase Imb
    def save_phaseimb(self,dr,txp,standard,streams):
        DebugPrint('Saving PhaseImb Values')
        if(standard=='11b'):
            cntrl_sckt.sendall('FETCh:TXQuality:DSSS:AVER?\n')
            result=cntrl_sckt.recv(300)
            DebugPrint(result)
            phaseimb_1x1=result.split(',')[9]
            return phaseimb_1x1
        else:
            cntrl_sckt.sendall('FETC:OFDM:PIMB:ALL:AVER?\n')
            result=cntrl_sckt.recv(200)
            DebugPrint(result)
            phaseimb_1x1=result.split(',')[1]
            # print 'phaseimb_1x1',phaseimb_1x1
            if(streams=='1x1'):
                return phaseimb_1x1
            phaseimb_2x2=result.split(',')[2]
        #print '-------------'
        #print  float(phaseimb_1x1),float(phaseimb_2x2)
        return float(phaseimb_1x1),float(phaseimb_2x2)



    #Save LO Leakage
    def save_lo_leakage(self,dr,txp,standard,streams):
        return 1.0 # PHY_PERFORMANCE ..stuck observed . so returning non-zero value
        #DebugPrint('Saving lo_leakage Values')
        ## print('Saving lo_leakage Values')
        #if(standard=='11b'):
        #    cntrl_sckt.sendall('FETC:DSSS:LOLeakage:ALL:AVER?\n')
        #    result=cntrl_sckt.recv(200)
        #    DebugPrint(result)
        #    lo_leakage_1x1=result.split(',')[6]
        #    return lo_leakage_1x1
        #else:
        #    cntrl_sckt.sendall('FETC:OFDM:LOLeakage:ALL:AVER?\n')
        #    result=cntrl_sckt.recv(200)
        #    DebugPrint(result)
        #    lo_leakage_1x1=result.split(',')[1]
        #    # print 'lo_leakage_1x1',lo_leakage_1x1
        #    if(streams=='1x1'):
        #        return lo_leakage_1x1
        #    lo_leakage_2x2=result.split(',')[2]
        #return float(lo_leakage_1x1),float(lo_leakage_2x2)

    def get_ideal_spectrum_values(self,standard,streams,ch):
        DebugPrint('Saving get_ideal_spectrum_values ')
        # print('Saving get_ideal_spectrum_values ')
        cntrl_sckt.sendall('FORM:READ:DATA ASC\n')
        cntrl_sckt.sendall('FETCh:SPECtrum:OFRequency:CORNer?\n')
        result=cntrl_sckt.recv(20000)
        ideal_spectrum_freq_values=result.split(',')[1:11]
        cntrl_sckt.sendall('FORM:READ:DATA ASC\n')
        cntrl_sckt.sendall('FETCh:SPECtrum:HLIMit:CORNer?\n')
        result=cntrl_sckt.recv(2000)
        ideal_spectrum_hlimit_values=result.split(',')[1:11]
        ideal_spectrum_hlimit_values=[float(hlim.split('\n')[0]) for hlim in ideal_spectrum_hlimit_values]
        if(int(ch)<15):
            ideal_spectrum_hlimit_values=[ideal_spectrum_hlimit_values[0]-5]+[ideal_spectrum_hlimit_values[1]-5]+ideal_spectrum_hlimit_values[2:-2]+[ideal_spectrum_hlimit_values[-2]-5]+[ideal_spectrum_hlimit_values[-1]-5]
        ideal_spectrum_freq_values=[float(freq.split('\n')[0]) for freq in ideal_spectrum_freq_values]
        return ideal_spectrum_hlimit_values,ideal_spectrum_freq_values

    #Click AGC Button
    def click_agc(self,standard,streams):
        DebugPrint('Click AGC')
        if(streams=='2x2'):
            cntrl_sckt.sendall('MVSAALL ;RLEVel:AUTO\n')
        else:
            cntrl_sckt.sendall('VSA1'+chain_sel_scpi_cmd+' ;RLEVel:AUTO\n')
        cntrl_sckt.sendall('CHAN1\n')
        if(streams=='2x2'):
            cntrl_sckt.sendall('MVSAALL ;init\n')
        else:
            cntrl_sckt.sendall('VSA1'+chain_sel_scpi_cmd+' ;init\n')
        cntrl_sckt.sendall('WIFI\n')
        if(standard=='11b'):
            cntrl_sckt.sendall('calc:pow 0, 1\n')
            cntrl_sckt.sendall('calc:txq 0, 1\n')
            cntrl_sckt.sendall('calc:ccdf 0, 1\n')
            cntrl_sckt.sendall('calc:spec 0, 1\n')
        else:
            cntrl_sckt.sendall('calc:pow 0, 30\n')
            cntrl_sckt.sendall('calc:txq 0, 30\n')
            cntrl_sckt.sendall('calc:ccdf 0, 30\n')
            cntrl_sckt.sendall('calc:spec 0, 30\n')

    #Start Packet Analyses
    def click_analyser(self,standard,streams,pkts='30'):
        DebugPrint('Click Analyser')
        # if(streams=='1x1'):
            # cntrl_sckt.sendall('CHAN1;WIFI; HSET:ALL VSA1'+chain_sel_scpi_cmd+'\n')
        # elif(streams=='2x2'):
            # cntrl_sckt.sendall('CHAN1;WIFI; HSET:ALL MVSAALL\n')
        cntrl_sckt.sendall('CHAN1\n')
        if(streams=='2x2'):
            cntrl_sckt.sendall('MVSAALL ;init\n')
        else:
            cntrl_sckt.sendall('VSA1'+chain_sel_scpi_cmd+' ;init\n')
        cntrl_sckt.sendall('WIFI\n')
        if(standard=='11b'):
            cntrl_sckt.sendall('calc:pow 0, 1\n')
            cntrl_sckt.sendall('calc:txq 0, 1\n')
            cntrl_sckt.sendall('calc:ccdf 0, 1\n')
            cntrl_sckt.sendall('calc:spec 0, 1\n')
        else:
            cntrl_sckt.sendall('calc:pow 0, '+pkts+'\n')
            cntrl_sckt.sendall('calc:txq 0, '+pkts+'\n')
            cntrl_sckt.sendall('calc:ccdf 0, '+pkts+'\n')
            cntrl_sckt.sendall('calc:spec 0, '+pkts+'\n')

    #Modulation Type
    def set_vsa_modulation(self,standard):
        DebugPrint('Setting VSA standard '+standard)
        if(standard=='11b'):
            modulation='dsss'
        else:
            modulation='ofdm'
        print "\nSetting "+modulation+" in VSA"
        DebugPrint("\nSetting "+modulation+" in VSA")
        cntrl_sckt.sendall("CHAN1;WIFI;CONF:STAN "+modulation.upper()+"\n")
        if(standard=='11b'):
            cntrl_sckt.sendall("CHAN1;WIFI;CONF:STAN DSSS\n")

    def init_vsa_funcs(self,standard='11ac',bw='20',streams='2x2',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',chain_sel='1'):
        self.start_vsg()
        self.set_equip_default()
        self.set_rf(streams=streams,test='tx',chain_sel=chain_sel)
        self.set_vsa_modulation(standard)
        if(tx_continuous_enable=='1'):
            capture_length=75
        else:
            #capture_length=600 #PHY_PERFORMANCE: why is this huge value?
            capture_length=200
            print "-------------------------------------------------capture length changed to \n",capture_length
        self.set_capturelength(capture_length,streams)
    def config_adj_11a(self):
        return

    #802.11b Initialization settings
    def config_adj_11b(self):
        return
    #802.11g Initialization settings
    def config_adj_11g(self):
        return

    #802.11n Initialization settings
    def config_adj_11n(self):
        return

    #802.11ac Initialization settings
    def config_adj_11ac(self):
        return


    #Modulation Type
    def set_adj_modulation(self,standard):
        print "\nSetting "+standard+" in VSA"
        return

    #Setting Payload
    def set_adj_payload(self,standard,payload):
        # print "\nSetting payload ",payload
        return


    #Setting MAC Header OFF
    def set_adj_macheader(self):
        # print 'Set adj MACHeader'
        return

    #Setting Channel
    def apply_adjacent_vsg(self,bw='',chn='',streams='2x2',config='adj'):
        print 'apply_adjacent_vsg'
        return

    #Setting Adj Amplitude
    def set_adj_amplitude(self,streams,ampl):
        print "\nSetting adj amplitude ",ampl
        return

    def set_adj_bandwidth(self,standard='',bw=''):
        print 'set_adj_bandwidth'
        return

    #RF ON/OFF
    def rf_on_off_adj(self,rf_state='on',streams='1x1'):
        print "\nSetting RF ",rf_state
        return

    def set_pop_trigger(self,packet_delay='',packet_cnt='2000'):
        print 'Setting packet delay ',packet_delay
        return

    def set_reference_level(self,power_1x1=10,power_2x2=10,streams='1x1'):
        # cntrl_sckt.sendall('VSA11;RLEV 30\n')
        if(streams=='2x2'):
            cntrl_sckt.sendall('MVSAALL ;RLEV '+str(power_1x1+8)+'\n')
        else:
            # print ('VSA1'+chain_sel_scpi_cmd+' ;RLEV '+str(power_1x1+8)+'\n')
            cntrl_sckt.sendall('VSA1'+chain_sel_scpi_cmd+' ;RLEV '+str(power_1x1+8)+'\n')
        # if(streams=='1x1'):

            # cntrl_sckt.sendall('VSA1;RLEV '+str(power_1x1+8)+'\n')
        # else:
            # print ('set_reference_level 1x1'+str(power_1x1+8))
            # cntrl_sckt.sendall('VSA1;RLEV '+str(power_1x1+8)+'\n')

    def vsgEnableSuFrame(self):
        """ Sets the packet format for the generated packet as HESU."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:PFOR SU\n')

    def vsgEnableErsuFrame(self):
        """ Sets the packet format for the generated packet as HEERSU."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:PFOR ERAN\n')

    def vsgEnableTriggerFrame(self):
        """ Sets the packet format for the generated packet as HETB."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:PFOR TRIG\n')

    def vsgEnableResponseTriggerFrame(self):
        """ Enable response trigger packet """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:CPAR:TFR ON\n')
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:TFR:STAT ON\n')

    def vsgDisableResponseTriggerFrame(self):
        """ Disable response trigger packet """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:CPAR:TFR OFF\n')
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:TFR:STAT OFF\n')

    def vsgEnableDisambiguity(self):
        """ Enable PE Disambiguity bit while generating packet """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:TFR:PED ON\n')

    def vsgDisableDisambiguity(self):
        """ Disable PE Disambiguity bit while generating packet """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:TFR:PED OFF\n')

    def vsaEnableDisambiguity(self):
        """ Sets the PE-disambiguity bit for analysis of 802.11ax trigger-based PPDU packets."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:PED ON\n')

    def vsaDisableDisambiguity(self):
        """ Resets the PE-disambiguity bit for analysis of 802.11ax trigger-based PPDU packets."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:PED OFF\n')

    def setVsaGiLtfType(self, GiLtfType):
        """ Sets the combination of HE-LTF size and GI time for analysis of 802.11ax trigger-based PPDU packets
            0 :	GI1 data (0.8us) and 1x HE LTF (SU and ER-SU), GI1 data (0.8us) and 4x HE LTF (MU), GI1 data (1.6us) and 1x HE LTF (trigger-based PPDU)
            1 :	GI1 data (0.8us) and 2x HE LTF (SU, ER-SU and MU), GI1 data (1.6us) and 2x HE LTF (trigger-based PPDU)
            2 :	GI2 data (1.6us) and 2x HE LTF (SU, ER-SU and MU), GI1 data (3.2us) and 4x HE LTF (trigger-based PPDU)
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:GILT GILTF' + str(GiLtfType) + '\n')

    def setVsgGiLtfType(self, GiLtfType):
        """ Sets the combination of HE-LTF size and GI time
                0 :	GI1 data (0.8us) and 1x HE LTF (SU and ER-SU), GI1 data (0.8us) and 4x HE LTF (MU), GI1 data (1.6us) and 1x HE LTF (trigger-based PPDU)
                1 :	GI1 data (0.8us) and 2x HE LTF (SU, ER-SU and MU), GI1 data (1.6us) and 2x HE LTF (trigger-based PPDU)
                2 :	GI2 data (1.6us) and 2x HE LTF (SU, ER-SU and MU), GI1 data (3.2us) and 4x HE LTF (trigger-based PPDU)
                3 :	GI4 data (3.2us) and 4x HE LTF (SU, ER-SU and MU), GI1 data (0.8us) and 4x HE LTF (when both the DCM and STBC fields are set to 1)
         """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:GILT GILTF' + str(GiLtfType) + '\n')

    def vsaEnableLdpcExtraSymbol(self):
        """ Sets the state of LDPC extra symbol for analysis of 802.11ax trigger-based PPDU packets """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:ESLD ON\n')

    def vsaDisableLdpcExtraSymbol(self):
        """ Resets the state of LDPC extra symbol for analysis of 802.11ax trigger-based PPDU packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:ESLD OFF\n')

    def vsgEnableLdpcExtraSymbol(self):
        """ Sets the LDPC extra symbol for 802.11ax packet generation """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:ESLD ON\n')

    def vsgDisableLdpcExtraSymbol(self):
        """ Resets the LDPC extra symbol for 802.11ax packet generation """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:ESLD OFF\n')

    def setVsaNumLtf(self, numLtf):
        """ Sets the number of HE-LTF symbols for analysis of 802.11ax trigger-based PPDU packets
            numLtf : 1,2,4,6,8
         """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:NLTF ' + str(numLtf) + '\n')

    def setVsgNumLtf(self, numLtf):
        """ Sets the number of extra OFDM symbols of the HE-LTF field to be used for 802.11ax packet generation.
        The total number of HE-LTF symbols can only take the values 1, 2, 4, 6, or 8.
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:ELTF ' + str(numLtf - 1) + '\n')

    def setVsaUserCodingStandard(self, user, standard):
        """ Sets the coding type for the optionally specified user for analysis of 802.11ax trigger-based PPDU packets.
            standard = 'BCC' | 'LDPC'
        """
        #if (user == 'ALL'):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:COD:user' + str(user) + ' ' + standard +'\n')

    def setVsgUserCodingStandard(self, user, standard):
        """ Sets the Coding type for WiFi 11ax/ac/n/a/g/p wave generation. Settings are for the optionally specified user in case of MU.
            standard = 'BCC' | 'LDPC'
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:COD:USER' + str(user) + ' ' + standard +'\n')

    def setVsaUserRuIdx(self, user, ruIdx):
        """ Sets the RU Index for the optionally specified user for analysis of 802.11ax trigger-based PPDU packets.
            ruIdx = 0 to 68
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:RUIN:user' + str(user) + ' ' + str(ruIdx) +'\n')

    def setVsgUserRuIdx(self, user, ruIdx):
        """ Sets the RU Allocation Index for the optionally specified user. Only applies to 802.11ax trigger-based PPDU.
            ruIdx = 0 to 68
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:RUIN:USER' + str(user) + ' ' + str(ruIdx) +'\n')

    def setVsaPreFecfactor(self, fecFactor):
        """ Sets the A-factor for analysis of 802.11ax trigger-based PPDU packets.
            fecFactor = 1 to 4
         """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:AFAC ' + str(fecFactor) +'\n')

    def setVsgPreFecfactor(self, fecFactor):
        """ Sets the PreFecfactor for 802.11ax packet generation. Only applies to HE trigger-based PPDU .
            fecFactor = 1 to 4
         """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:AFAC ' + str(fecFactor) +'\n')

##    def setVsgPreFecfactor(self, fecFactor):
##        #DebugPrint("\n disabling trigger frame)
##        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:AFAC ' + str(fecFactor) +'\n')

    def vsaEnableDcm(self, user):
        """ Sets the DCM value for the optionally specified user for analysis of 802.11ax trigger-based PPDU packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:DCM:USER' + str(user) +' ON\n')

    def vsaDisableDcm(self, user):
        """ Resets the DCM value for the optionally specified user for analysis of 802.11ax trigger-based PPDU packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:DCM:USER' + str(user) +' OFF\n')

    def vsgEnableDcm(self, user):
        """ Sets whether DCM is enabled for WiFi 11ax wave generation. Settings are for the optionally specified user in case of MU."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:DCM:USER' + str(user) +' ON\n')

    def vsgDisableDcm(self, user):
        """ Resets whether DCM is enabled for WiFi 11ax wave generation. Settings are for the optionally specified user in case of MU."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:DCM:USER' + str(user) +' OFF\n')

    def setVsaNumUser(self, numUser):
        """Sets the number of users for analysis of 802.11ax trigger-based PPDU packets.
            numUser = 1 to 138
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:NUS ' + str(numUser) + '\n')

    def setMuNumUser(self, numUser):
        """Sets the number of users for generation of OFDM-based packets.
            numUser = 1 to 138
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:MU:NUS ' + str(numUser) + '\n')

    def setMuUserStaid(self, StaidList):
        """Sets the number of users for generation of OFDM-based packets.
            numUser = 1 to 138
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:STA:AUS ' + StaidList + '\n')

    def setHetbNumUser(self, numUser):
        """Sets the number of users for purpose of 802.11ax trigger frame generation.
            numUser = 1 to 138
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:TFR:NUS ' + str(numUser) + '\n')

    def vsgEnableMultiuser(self):
        """Sets the multi-user state for generation of OFDM-based packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:MU:STAT ON\n')

    def vsgDisableMultiuser(self):
        """Resets the multi-user state for generation of OFDM-based packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:MU:STAT OFF\n')

    def vsaEnableDoppler(self):
        """Sets the doppler bit to ON or OFF for analysis of 802.11ax trigger-based PPDU packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:DOPP ON\n')

    def vsaDisableDoppler(self):
        """Resets the doppler bit to ON or OFF for analysis of 802.11ax trigger-based PPDU packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:DOPP OFF\n')

    def vsgEnableDoppler(self):
        """Sets the doppler state for generation of 11ax packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGA:DOPP ON\n')

    def vsgDisableDoppler(self):
        """Resets the doppler state for generation of 11ax packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGA:DOPP OFF\n')

    def setVsaMidamplePeriodicity(self, midample):
        """Sets the midamble periodicity for analysis of 802.11ax trigger-based PPDU packets
            midample = 10 or 20
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:MPER ' + str(midample) +'\n')

    def setVsgMidamplePeriodicity(self, midample):
        """Sets the midamble periodicity for 802.11ax waveform generation.
            midample = 10 or 20
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGA:MPER ' + str(midample) +'\n')

    def vsaEnableLtfMode(self):
        """Sets the MU-MIMO HE-LTF Mode for analysis of 802.11ax trigger-based PPDU packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:LTFM ON\n')

    def vsaDisableLtfMode(self):
        """ReSets the MU-MIMO HE-LTF Mode for analysis of 802.11ax trigger-based PPDU packets"""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:LTFM OFF\n')

    def vsgEnableLtfMode(self):
        """Sets the MU-MIMO HE-LTF Mode for 802.11ax packet generation. Only applies to HE trigger-based full BW PPDU."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:LTFM ON\n')

    def vsgDisableLtfMode(self):
        """ReSets the MU-MIMO HE-LTF Mode for 802.11ax packet generation. Only applies to HE trigger-based full BW PPDU."""
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:LTFM OFF\n')

    def setVsaUserDatarate(self, user, datarate):
        """Sets the MCS for the optionally specified user for analysis of 802.11ax trigger-based PPDU packets.
            datarate = 0 to 13
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:MCS:USER' + str(user) + ' ' + str(datarate) +'\n')

    def setVsgUserDatarate(self, user, datarate):
        """Sets the Modulation and Coding Scheme for WiFi 11ax/ac/n/a/g/p wave generation. For 20 MHz 11a/g/p,
            the mapping from MCS value to data rate is as follows:
            0: 6 Mbps, 1: 9 Mbps, 2: 12 Mbps, 3: 18 Mbps, 4: 24 Mbps, 5: 36 Mbps, 6: 48 Mbps, 7: 54 Mbps.
            datarate = 0 to 102
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:MCS:USER' + str(user) + ' ' + str(datarate) +'\n')

    def setDatarateAllUser(self, numUser, datarate):
        """Sets the Modulation and Coding Scheme for WiFi 11ax/ac/n/a/g/p wave generation. For 20 MHz 11a/g/p,
            the mapping from MCS value to data rate is as follows:
            0: 6 Mbps, 1: 9 Mbps, 2: 12 Mbps, 3: 18 Mbps, 4: 24 Mbps, 5: 36 Mbps, 6: 48 Mbps, 7: 54 Mbps.
            datarate = 0 to 102
        """
        datarateList = (datarate[-1] + ',')*(numUser - 1) + datarate.split('MCS')[1]
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:MCS:AUSers ('+ datarateList +')\n')
        print('CHAN1;WIFI;CONF:WAVE:OFDM:MCS:AUSers ('+ datarateList +')\n')

    def setVsgUserNss(self, user, nss):
        """ Sets the number of spatial streams for WiFi 11ax/ac/n/a/g/p wave generation. Settings are for the optionally specified user in case of MU.
        nss = 1 to 8
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:NSST:USER' + str(user) + ' ' + str(nss) +'\n')

    def setVsaUserNss(self, user, nss):
        """ Sets the number of spatial streams for the optionally specified user for analysis of 802.11ax trigger-based PPDU packets
        nss = 1 to 8
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:OFDM:NSST:USER' + str(user) + ' ' + str(nss) +'\n')

    def setVsgBssColor(self, bssColor):
        """ Sets the BSS color, as defined in the HE-SIG-A fields. Only applies to 802.11ax.
        bssColor = 0 to 63
        """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:BSSC ' + str(bssColor) +'\n')

    def setVsgExRangeRuType(self, ruType):
        """ Sets whether the generated Extended Range HE PPDU consists of right 106 tone RU or full BW 242 tone RU.
        Only applies to 802.11ax HE Extended Range PPDU generation.
        ruType = 106 or 242
        """
        if (ruType ==106):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:ERAN:RUTY RU106\n')
        else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:ERAN:RUTY FULL\n')

    def setVsgMuRuAllocation(self, cBit, ruDistribution):
        """ Sets the HE-SIG-B common bits as defined in 802.11ax and the number of users per resource unit (RU).
             The HE-SIG-B common bits should be 8 bits for 20MHz, 16 bits for 40MHz and 32 bits for 80MHz and 64 Bits for 160MHz bandwidths respectively.
             This setting is only applicable for HE MU PPDU packet format The input is in form of unquoted string of 0s and 1s with MSB first.
             RU allocation is the number of users allocated per RU """
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:CBIT:ASC ' + cBit + '\n')
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:RUAL ('+ ruDistribution +')\n')
        print('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:CBIT:ASC ' + cBit + '\n')
        print('CHAN1;WIFI;CONF:WAVE:OFDM:RUAL ('+ ruDistribution +')\n')

    #Setting MU MAC Header
    def set_userMacheader(self, user):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:MACH:ADDR1:USER'+str(user)+ ' 0'+ str(user)+'0000C0FFEE\n')

    def set_sigbDCM(self, sigBdcm):
        if (sigBdcm == 1):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:DCM ON\n')
        else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:DCM OFF\n')

    def set_sigbDatarate(self, datarate):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:MCS ' + str(datarate) + '\n')

    def set_sigbCompression(self, sigBcomp):
        if (sigBcomp == 1):
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:COMP ON\n')
        else:
            cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:COMP OFF\n')

    def set_sigbCentral26ToneRu(self, CRU):
        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:SIGB:CRU26 ' + CRU + '\n')

    def configHE(self,configParams):
        if (configParams.format == 6):
            self.vsgEnableMultiuser()
            self.setMuNumUser(configParams.numUser)
            cBit = binBit(configParams.ruAllocation,configParams.bw)
            #ruDistri = ruDistribution (userIdx, numRu)
            self.setVsgMuRuAllocation(cBit,configParams.userRuIndex)
        else:
            self.vsgDisableMultiuser()
        if (configParams.format == DUT_FrameFormat.HE_SU):
            self.vsgEnableSuFrame()
        elif (configParams.format == DUT_FrameFormat.HE_ERSU):
            self.vsgEnableErsuFrame()
        elif (configParams.format == DUT_FrameFormat.HE_TB):
            self.vsgEnableTriggerFrame()
        if (configParams.format != DUT_FrameFormat.HE_MU):
            self.setVsgUserNss(1, 1)
            self.setVsgUserCodingStandard(1, configParams.coding)
            if (configParams.dcm == 1):
                self.vsgEnableDcm(1)
            else:
                self.vsgDisableDcm(1)
            if (configParams.doppler == 1):
                self.vsgEnableDoppler()
            else:
                self.vsgDisableDoppler()
            self.setVsgMidamplePeriodicity(configParams.midamblePeriodicity)
            if ((configParams.format == DUT_FrameFormat.HE_SU) or (configParams.format == DUT_FrameFormat.HE_ERSU)):
                if ((configParams.giType == 0) and (configParams.heLtfType == 0)):
                    GiLtfType = 0
                elif ((configParams.giType == 0) and (configParams.heLtfType == 1)):
                    GiLtfType = 1
                elif ((configParams.giType == 1) and (configParams.heLtfType == 1)):
                    GiLtfType = 2
                elif ((configParams.giType == 2) and (configParams.heLtfType == 2)):
                    GiLtfType = 3
            self.setVsgGiLtfType( GiLtfType)
##            datarate = configParams.data_rate.split('MCS')[-1]
##            self.setVsgUserDatarate(1, datarate)
            if ((configParams.format == DUT_FrameFormat.HE_ERSU) and (configParams.chBandwidth == 0)):
                self.setVsgExRangeRuType(242)
            else:
                self.setVsgExRangeRuType(106)
            if (configParams.format == DUT_FrameFormat.HE_TB):
                self.vsgDisableLdpcExtraSymbol()
                self.setVsgNumLtf(numLtf)
                self.setVsgUserRuIdx(1, ruIdx)
                self.setVsgPreFecfactor(fecFactor)
                self.vsgDisableDisambiguity()
                self.vsgEnableLtfMode()
        else:
            if ((configParams.giType == 0) and (configParams.heLtfType == 2)):
                GiLtfType = 0
            elif ((configParams.giType == 0) and (configParams.heLtfType == 1)):
                GiLtfType = 1
            elif ((configParams.giType == 1) and (configParams.heLtfType == 1)):
                GiLtfType = 2
            elif ((configParams.giType == 2) and (configParams.heLtfType == 2)):
                GiLtfType = 3
            self.setVsgGiLtfType( GiLtfType)
##            self.setVsgNumLtf(numLtf)
            staidList = '(' + configParams.staIDlist +')'
            self.setMuUserStaid(staidList)
            self.set_sigbDCM(configParams.sigBdcm)
            self.set_sigbDatarate(configParams.sigBmcs)
            self.set_sigbCompression(configParams.sigBcompression)
            for ii in range(configParams.numUser):
                user = ii+1
                self.setVsgUserCodingStandard(user, configParams.coding)
##                self.setVsgUserDatarate(user, configParams.data_rate)
                if (configParams.dcm == 1):
                    self.vsgEnableDcm(user)
                else:
                    self.vsgDisableDcm(user)
            if (configParams.doppler == 1):
                self.vsgEnableDoppler()
            else:
                self.vsgDisableDoppler()
            self.setVsgMidamplePeriodicity(configParams.midamblePeriodicity)

    def configVsaHETB(self,configParams):
        self.setVsaGiLtfType(configParams.giType)
        self.setVsaUserDatarate(1, configParams.data_rate)
        if (configParams.heTbDisambiguity  == 1):
            self.vsaEnableDisambiguity()
        else:
            self.vsgDisableDisambiguity()
        self.setVsaUserRuIdx(1, configParams.ruAllocation)
        self.setVsaUserCodingStandard(1, configParams.coding)
        self.setVsaPreFecfactor(configParams.fecPadding)
        self.setVsaNumLtf(configParams.numHeLtf)
        if (configParams.ldpcExtraSymbol  == 1):
            self.vsaEnableLdpcExtraSymbol()
        else:
            self.vsaDisableLdpcExtraSymbol()

    def setVsaGprfMode(self):
        cntrl_sckt.sendall('CHAN1;GPRF\n')
        cntrl_sckt.sendall('CHAN1;GPRF;ROUT1;PORT:RES:ADD RF1A,VSA1\n')
        cntrl_sckt.sendall('CHAN1;GPRF;CONF:SPEC:RBW 40000\n')
        cntrl_sckt.sendall('VSA1;FREQ:cent 5720000000\n')

    def getSpectrumPeak(self):
        cntrl_sckt.sendall('VSA1;init\n')
        cntrl_sckt.sendall('GPRF\n')
        cntrl_sckt.sendall('calc:pow 0,0.001\n')
        cntrl_sckt.sendall('calc:spec 0,0.001\n')
        cntrl_sckt.sendall('calc:psh 0,0.001\n')
        cntrl_sckt.sendall('FORM:READ:DATA ASC\n')
        cntrl_sckt.sendall('FETC:SEGM1:SPEC:PEAK:OFR?\n')
        #cntrl_sckt.sendall('FETC:SEGM2:SPEC:OFR?\n')
        time.sleep(1)
        result = cntrl_sckt.recv(50)
        result = int(float(result.split(',')[1].split('\n')[0]))
        return result

def binBit(ruAllocation,bw):
    string = bin(ruAllocation)
    value = string[2:]
    if (bw =='20'):
        cbitString = '0'* (8-len(value))+value
    elif ((bw =='40') or (bw =='20in40')):
        cbitString = '0'* (16-len(value))+value
    elif ((bw =='80') or (bw =='20in80')):
        cbitString = '0'* (32-len(value))+value
    return cbitString

def ruDistribution (userIdx, numRu):
    ruDistribution = ''
    for i in range(numRu-1):
        temp = i+1
        if (temp in userIdx):
            ruDistribution += '1,'
        else:
            ruDistribution += '0,'
    if (numRu in userIdx):
        ruDistribution += '1'
    else:
        ruDistribution += '0'
    return ruDistribution