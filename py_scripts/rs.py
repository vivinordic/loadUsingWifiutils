#-------------------------------------------------------------------------------
# Name:        rs
# Purpose:     This module has all the APIs(SCPI commands) for configurint RnS VSG.
# Author:      kranthi.kishore
# Created:     14-06-2015
# Copyright:   Imagination Technologies Ltd
#-------------------------------------------------------------------------------

from   socket import *
import time
from common_utils import *

"""prime20, sec20, sec40 flags dictionary:
    This dictionary contains whether the sec20 and sec40 are located to the
    left/right of prim20 for the given channel numbers for 40MHz and 80MHz cases."""
prime_20_sec_20_flags_dict={
                            '40':{
                                '1':'r','2':'r','3':'r','4':'r',
                                '36':'r','44':'r',
                                '52':'r','60':'r',
                                '100':'r','108':'r',
                                '116':'r','124':'r',
                                '132':'r','140':'r',
                                '149':'r','157':'r',
                                },
                            '80':{'36':'r','40':'lr','44':'rl','48':'l',
                                '52':'r','56':'lr','60':'rl','64':'l',
                                '100':'r','104':'lr','108':'rl','112':'l',
                                '116':'r','120':'lr','124':'rl','128':'l',
                                '132':'r','136':'lr','140':'rl','144':'l',
                                '149':'r','153':'lr','157':'rl','161':'l'
                                }
                            }
legacy_datarate_dict={
                    '6':['BPSK','1D2'],'9':['BPSK','3D4'],'12':['QPSK','1D2'],'18':['QPSK','3D4'],
                    '24':['QAM16','1D2'],'36':['QAM16','3D4'],'48':['QAM64','2D3'],'54':['QAM64','3D4']

                    }
class RnS:
    def __init__(self,tester='rssmw200',equip_ip = '10.90.3.131'):
        self.tester='rssmw200'
        if(self.tester=='rssmw200'):
            self.hostName = equip_ip # 'rssmw200a101537'
            self.port = 5025
    #Start VSG
    def start_vsg(self):
        """Establish a socket connection to VSG."""
        print "\nConfiguring ",self.tester
        DebugPrint("\nConfiguring "+self.tester)
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
    def config_11a(self,chain_sel=1):
        """Configure 802.11a in VSG"""
        DebugPrint('Configure 802.11a in VSG')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STANdard WAG\n')

    #802.11b Initialization settings
    def config_11b(self,chain_sel=1):
        """Configure 802.11b in VSG"""
        DebugPrint('Configure 802.11b in VSG')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STANdard WBG\n')

    #802.11g Initialization settings
    def config_11g(self,chain_sel=1):
        """Configure 802.11g in VSG"""
        DebugPrint('Configure 802.11g in VSG')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STANdard WAG\n')

    #802.11n Initialization settings
    def config_11n(self,chain_sel=1):
        """Configure 802.11n (HT) in VSG"""
        DebugPrint('Configure 802.11n in VSG')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STANdard WN\n')

    #802.11ac Initialization settings
    def config_11ac(self,chain_sel=1):
        """Configure 802.11ac (VHT) in VSG"""
        DebugPrint('Configure 802.11ac in VSG')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STANdard WAC\n')

    #802.11ax Initialization settings
    def config_11ax(self,chain_sel=1):
        """Configure 802.11ax (HE) in VSG"""
        DebugPrint('Configure 802.11ax in VSG')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STANdard WAX\n')

    #Set Default
    def set_equip_default(self):
        """Setting Equipment to default state """
        print "\nSetting RnS to default state"
        DebugPrint("\nSetting RnS to default state")
        cntrl_sckt.send('*RST\n')

    #Modulation Type
    def set_modulation(self,standard='',run='per',chain_sel=1):
        """Configure the Wi-Fi Standard 802.11a/b/g/n/ac in VSG"""
        print "\nSetting "+standard+" in VSG"
        DebugPrint("\nSetting "+standard+" in VSG")
        if(run!='per'):
            eval('self.config_aci_'+standard+'()')
        else:
            eval('self.config_'+standard+'(chain_sel)')
        cntrl_sckt.send('SOURce'+str(chain_sel)+':FSIMulator:BYPass:STATe 1\n')

    #Setting Datarate
    def set_datarate(self,modulation,standard,data_rate,chain_sel=1):
        """Set the data rate in VSG"""
        print "\nSetting data rate ",data_rate
        DebugPrint("\nSetting data rate "+str(data_rate))
        if((standard=='11n')or(standard=='11ac')or(standard=='11ax')):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:MCS '+data_rate+'\n')
        elif(standard=='11b'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:PSDU:BRATe '+data_rate+'000000\n')
        else:
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:MODulation1 '+legacy_datarate_dict[data_rate][0]+'\n')
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:CODing:RATE CR'+legacy_datarate_dict[data_rate][1]+'\n')

    def set_aci_datarate(self,modulation,standard,data_rate):
        print "\nSetting adj data rate ",data_rate
        if((standard=='11n')or(standard=='11ac')or(standard=='11ax')):
            cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:MCS '+data_rate+'\n')
        elif(standard=='11b'):
            cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:PSDU:BRATe '+data_rate+'000000\n')
        else:
            cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:MODulation1 '+legacy_datarate_dict[data_rate][0]+'\n')
            cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:CODing:RATE CR'+legacy_datarate_dict[data_rate][1]+'\n')

    #Setting Payload
    def set_payload(self,standard,payload,chain_sel=1):
        """Set the payload in VSG """
        print "\nSetting payload ",payload
        DebugPrint("\nSetting payload "+str(payload))
        if((standard=='11ac')or(standard=='11ax')):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:MPDU1:DATA:LENGth '+payload+'\n')
        else:
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:DATA:LENGth '+payload+'\n')


    #Setting MAC Header OFF
    def set_macheader(self,chain_sel=1):
        """Set the MAC Header in VSG """
        DebugPrint('Set the MAC Header in VSG ')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:MAC:STATe 1\n')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:MAC:FCS:STATe 1\n')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:MAC:ADDRess1 #HABCDEFABCDEF,48\n')
        time.sleep(3)

    #Setting Channel for production test
    def apply_vsg(self,bw='',chn='',streams='1x1',chain_sel=1,p20_flag=0):
        """Set the Channel and Frequency band in VSG """
        DebugPrint('Applying VSG channel '+str(chn)+' and BW '+str(bw))
        if(bw=='20'):
            if(chn < 14):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str((chn*5)+2407)+'000000\n')
            elif(chn == 14):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW 2484000000\n')
            else:
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str((chn*5)+5000)+'000000\n')
        elif(bw=='40'):
            if(chn<15):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn-1)*5)+2412)+'000000\n')
##                if str(chn) in prime_20_sec_20_flags_dict[bw].keys():
##                    cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn+1)*5)+2412)+'000000\n')
##                else:
##                    cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn-3)*5)+2412)+'000000\n')
            else:
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn)*5)+5000)+'000000\n')
##                if str(chn) in prime_20_sec_20_flags_dict[bw].keys():
##                    cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn+2)*5)+5000)+'000000\n')
##                else:
##                    cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn-2)*5)+5000)+'000000\n')
        elif(bw=='80'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn)*5)+5000)+'000000\n')
##            if(prime_20_sec_20_flags_dict[bw][str(chn)]=='l'):
##                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn-6)*5)+5000)+'000000\n')
##            elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='lr'):
##                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn+2)*5)+5000)+'000000\n')
##            elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='rl'):
##                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn-2)*5)+5000)+'000000\n')
##            elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='r'):
##                cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str(((chn+6)*5)+5000)+'000000\n')

        if(streams=='2x2'):
            if(bw=='20'):
                if(chn < 14):
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str((chn*5)+2407)+'000000\n')
                elif(chn == 14):
                    cntrl_sckt.send(':SOURce2:FREQuency:CW 2484000000\n')
                else:
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str((chn*5)+5000)+'000000\n')
            elif(bw=='40'):
                if(chn<15):
                    if str(chn) in prime_20_sec_20_flags_dict[bw].keys():
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+1)*5)+2412)+'000000\n')
                    else:
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-3)*5)+2412)+'000000\n')
                else:
                    if str(chn) in prime_20_sec_20_flags_dict[bw].keys():
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+2)*5)+5000)+'000000\n')
                    else:
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-2)*5)+5000)+'000000\n')
            elif(bw=='80'):
                if(prime_20_sec_20_flags_dict[bw][str(chn)]=='l'):
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-6)*5)+5000)+'000000\n')
                elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='lr'):
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+2)*5)+5000)+'000000\n')
                elif(prime_20_sec_20_flags_dict[bw][str(chn)]=='rl'):
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-2)*5)+5000)+'000000\n')
                if(prime_20_sec_20_flags_dict[bw][str(chn)]=='r'):
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+6)*5)+5000)+'000000\n')

    #Setting Channel for RX Harness
    def apply_vsg_harness(self,bw='',chn='',streams='1x1',chain_sel=1):
        """Set the Channel and Frequency band in VSG for RX Harness """
        DebugPrint('Applying VSG channel '+str(chn)+' and BW '+str(bw)+' for RX Harness')
        if(chn < 14):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str((chn*5)+2407)+'000000\n')
        elif(chn == 14):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW 2484000000\n')
        else:
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':FREQuency:CW '+str((chn*5)+5000)+'000000\n')
        if(streams=='2x2'):
            if(chn < 14):
                cntrl_sckt.send(':SOURce2:FREQuency:CW '+str((chn*5)+2407)+'000000\n')
            elif(chn == 14):
                cntrl_sckt.send(':SOURce2:FREQuency:CW 2484000000\n')
            else:
                cntrl_sckt.send(':SOURce2:FREQuency:CW '+str((chn*5)+5000)+'000000\n')


    #Setting Amplitude
    def set_amplitude(self,streams,ampl,chain_sel=1):
        """Set the amplitude of the Signal in VSG """
        print "\nSetting amplitude ", str(ampl)
        DebugPrint("\nSetting amplitude "+str(ampl))
        if(streams=='1x1'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':POWer:LEVel:IMMediate:AMPLitude '+ampl+'\n')
        elif(streams=='2x2'):
            cntrl_sckt.send(':SOURce1:POWer:LEVel:IMMediate:AMPLitude '+ampl+'\n')
            cntrl_sckt.send(':SOURce2:POWer:LEVel:IMMediate:AMPLitude '+ampl+'\n')

    #Setting delay for Pop packet
    def set_pop_delay(self,delay):
        """ setting delay for POP packet """
        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:OBASeband:DELay '+ str(delay) +'\n')

    #Set Bandwidth 20/40 MHz
    def set_bandwidth(self,standard='',bw='',chain_sel=1):
        """Set the Channel Bandwidth in VSG """
        DebugPrint('Setting BW '+str(bw))
        if(standard=='11b'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:TMODe CCK\n')
        elif((standard=='11a') or (standard=='11g')):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:TMODe L20\n')
        elif(standard=='11n'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:BWidth BW'+bw+'\n')
            if(bw=='20'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:TMODe HT20\n')
            elif(bw=='40'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:TMODe HT40\n')
        elif((standard=='11ac')or(standard=='11ax')):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:BWidth BW'+bw+'\n')
            if(bw=='20'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:TMODe V20\n')
            elif(bw=='40'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:TMODe V40\n')
            elif(bw=='80'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:TMODe V80\n')

    #Setting Wavegap/Idle Interval
    def set_idleinterval(self,intv,chain_sel=1):
        """ Set the idle interval between each packet in VSG
        :param intv
        idle interval in micro sec
        :param chain_sel
        chain_sel in RnS. Should be 1 or 2.
        1 selects port A, 2 selects Port B
        """
        print "\nSetting idle interval ", intv
        DebugPrint("\nSetting idle interval "+ str(intv))
        # If the intv is computed as str(float(intv/1e6)),
        # value is returned as exponential type, which is not allowed to give to RnS
        # Eg: str(float(30/1e6)) = '3e-05'
        intv_str = '%f' % (float(intv)/float(1e6))
        # Removing the 0 at the end for x*10 type intervals
        # Eg: 30 us %f --> 0.000030, we are giving it as 0.00003
        #  If 25 us %f --> 0.000025, we are giving it as 0.000025
        if ((intv_str[-2:] == '00')):
            intv_str = intv_str[0:-2]
        elif (intv_str[-1] == '0'):
            intv_str = intv_str[0:-1]
        print ':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:ITIMe '+intv_str+'\n'
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:ITIMe '+intv_str+'\n')

    #Setting Wavegap/Idle Interval for ACI
    def set_aci_idleinterval(self,intv):
        """ Sets the idle interval between each packet in VSG
        :param intv
        idle interval in micro sec
        """
        print "\nSetting ACI idle interval ", intv
        DebugPrint("\nSetting ACI idle interval "+ str(intv))
        # If the intv is computed as str(float(intv/1e6)),
        # value is returned as exponential type, which is not allowed to give to RnS
        # Eg: str(float(30/1e6)) = '3e-05'
        intv_str = '%f' % (float(intv)/float(1e6))
        # Removing the 0 at the end for x*10 type intervals
        # Eg: 30 us %f --> 0.000030, we are giving it as 0.00003
        #  If 25 us %f --> 0.000025, we are giving it as 0.000025
        if ((intv_str[-2:] == '00')):
            intv_str = intv_str[0:-2]
        elif (intv_str[-1] == '0'):
            intv_str = intv_str[0:-1]
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:ITIMe '+intv_str+'\n')

    #Set Spatial Streams
    def set_streams(self,standard,streams='1x1',chain_sel=1):
        """Sets Number of Spatial Streams in VSG"""
        print "\nSetting streams ",streams
        DebugPrint("\nSetting streams "+streams)
        if(streams=='1x1'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:SSTReam 1\n') #1x1
        elif(streams=='2x2'):
            cntrl_sckt.send(':SCONfiguration:MODE ADV\n')
            cntrl_sckt.send(':SCONfiguration:BASeband:SOURce COUP\n')
            cntrl_sckt.send(':SCONfiguration:FADing MIMO2X2\n')
            cntrl_sckt.send(':SCONfiguration:APPLy\n')
            cntrl_sckt.send(':SCONfiguration:APPLy\n')
            time.sleep(2)
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:SSTReam 2\n')#2x2
        time.sleep(5)

    #Set Guard Interval
    def set_guardinterval(self,gi,chain_sel=1):
        """Set the Guard Interval (LGI/SGI) in VSG """
        print "\nSetting Guard Interval ",gi
        DebugPrint("\nSetting Guard Interval "+gi)
        if(gi.lower()=='sgi'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:GUARd SHOR\n') #SGI
        elif(gi.lower()=='lgi'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:GUARd LONG\n') #LGI

    #Set STBC Type
    def set_stbc(self,stbc,chain_sel=1):
        """Set the STBC Type (STBC Employed or not) in VSG """
        print "\nSetting STBC ",stbc
        DebugPrint("\nSetting STBC "+stbc)
        if(stbc.lower()=='stbc_1'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STSTream 2\n')
        elif(stbc.lower()=='stbc_0'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STSTream 1\n')

    #Set STBC in NRX 2 case
    def set_stbc_nrx2(self,chain_sel=1):
        print "\nSetting streams ",streams
        print "\nSetting STBC ",stbc
        cntrl_sckt.send(':SCONfiguration:MODE ADV\n')
        cntrl_sckt.send(':SCONfiguration:BASeband:SOURce COUP\n')
        cntrl_sckt.send(':SCONfiguration:FADing MIMO2X2\n')
        cntrl_sckt.send(':SCONfiguration:APPLy\n')
        cntrl_sckt.send(':SCONfiguration:APPLy\n')
        time.sleep(2)
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:SSTReam 1\n') # NSS=1 in 2x2
        time.sleep(2)
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:STSTream 2\n')
        time.sleep(2)

    #Set Coding Type
    def set_coding(self,coding,chain_sel=1):
        """Set the Coding Technique (BCC/LDPC) in VSG """
        print "\nSetting Coding Technique ",coding
        DebugPrint("\nSetting Coding Technique "+coding)
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:CODing:TYPE '+coding.upper()+'\n')#BCC/LDPC
        # if(coding.lower()=='ldpc'):
            # #print ':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:CODing:TYPE LDPC\n'
            # cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:CODing:TYPE LDPC\n')#LDPC
        # elif(coding.lower()=='bcc'):
            # cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:CODing:TYPE BCC\n')#BCC

    #Set Greenfield Mode
    def set_greenfield(self,greenfield_mode,chain_sel=1):
        """Set the Greenfield/Mixed Mode for 802.11n standard in VSG """
        print "\nSetting 11n Mode ",greenfield_mode
        DebugPrint("\nSetting 11n Mode "+greenfield_mode)
        if (greenfield_mode.lower() == 'mixed'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:PMODe MIX\n')# Mixed Mode
        elif(greenfield_mode.lower()=='greenfield'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:PMODe GFI\n')# Green Field
        return

    #Set Preamble
    def set_preamble(self,preamble,chain_sel=1):
        """Set the preamble (LONG/SHORT) for DSSS case in VSG """
        print "\nSetting preamble ",preamble
        DebugPrint("\nSetting preamble "+preamble)
        if(preamble.lower=='short'):
            cntrl_sckt.send() #Short
        elif(preamble.lower=='long'):
            cntrl_sckt.send() #Long

    #RF ON/OFF
    def rf_on_off(self,rf_state='on',streams='1x1',chain_sel=1):
        """Set RF ON/OFF in VSG """
        print "\nSetting RF ",rf_state.upper()
        DebugPrint("\nSetting RF "+rf_state.upper())
        if(rf_state=='off'):
            if(streams=='1x1'):
                cntrl_sckt.send(':OUTPut'+str(chain_sel)+':STATe 0\n')
            elif(streams=='2x2'):
                cntrl_sckt.send(':OUTPut1:STATe 0\n')
                cntrl_sckt.send(':OUTPut2:STATe 0\n')
        elif(rf_state=='on'):
            if(streams=='1x1'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:STATe 1\n')
                cntrl_sckt.send(':OUTPut'+str(chain_sel)+':STATe 1\n')
            elif(streams=='2x2'):
                cntrl_sckt.send(':SOURce1:BB:WLNN:STATe 1\n')
                cntrl_sckt.send(':SOURce2:BB:WLNN:STATe 1\n')
                cntrl_sckt.send(':OUTPut1:STATe 1\n')
                cntrl_sckt.send(':OUTPut2:STATe 1\n')
        time.sleep(5)

    def rf_on_off_jammer(self,rf_state='on',streams='1x1',chain_sel=1):
        if(rf_state=='off'):
            cntrl_sckt.send(':OUTPut'+str(chain_sel)+':STATe 0\n')
        if(rf_state=='on'):
            cntrl_sckt.send(':OUTPut'+str(chain_sel)+':STATe 1\n')

    #Generate ACI Waveform
    def generate_aci_waveform(self,streams='2x2',count='1002',chain_sel=1):
        """Generate Waveform in VSG."""
        print "\nGenerating waveform "
        DebugPrint("\nGenerating waveform ")
        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:SEQuence AUTO\n')
        #cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:TRIGger:SLUNit SEQ\n')
##        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:SOURce INTA\n')
##        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:SLENgth '+count+'\n')


    #Generate POP Waveform
    def generate_pop_waveform(self,streams='2x2',count='1002',chain_sel=1):
        """Generate Waveform in VSG."""
        print "\nGenerating waveform "
        DebugPrint("\nGenerating waveform ")
        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:SEQuence RETR\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:SEQuence SING\n')
        #cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:TRIGger:SLUNit SEQ\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:SOURce INTA\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:TRIGger:SLENgth '+count+'\n')

    #Generate Waveform
    def generate_waveform(self,streams='2x2',count='1002',chain_sel=1):
        """Generate Waveform in VSG."""
        print "\nGenerating waveform "
        DebugPrint("\nGenerating waveform ")
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:TRIGger:SEQuence SING\n')
        #cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:TRIGger:SLUNit SEQ\n')
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:TRIGger:SLENgth '+count+'\n')

    #Start Pumping
    def send_packets(self, streams, action, pkt_count=1000, chain_sel=1,wave_type=''):
        """Start Pumping the packets in VSG"""
        print 'Start Pumping'
        DebugPrint('Start Pumping')
        self.rf_on_off(rf_state='on',streams=streams,chain_sel=chain_sel)
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:TRIGger:EXECute\n')


    #Start Pumping
    def send_packets_continuously(self, streams, action, pkt_count=1000, chain_sel=1):
        """Start Pumping the packets in VSG"""
        self.send_packets(streams, action, pkt_count=pkt_count, chain_sel=chain_sel)


    #Start Pumping Baseband Packets
    def send_bb_packets(self, streams, action, chain_sel=1):
        """Start Pumping Baseband Packets Continuosly (Disable Count) """
        print 'Start Pumping Baseband Packets'
        DebugPrint('Start Pumping Baseband Packets')
        return


    def init_vsg_funcs(self,standard='11ac',bw='20',streams='2x2',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',run='per',chain_sel=1):
        """Configures the VSG to generate the required signal.
        :param standard
            To set the wi-fi standard 802.11a/b/g/n/ac
        :param bw
            To set the operating Bandwidth (Channel Bandwidth)
        :param streams
            To decide SISO(1x1) | MIMO(2x2) case
        :param stbc
            STBC Type (STBC Employed or not): 'STBC_0' | 'STBC_1'
        :param gi
            GI Type: 'LGI' | 'SGI'
        :param coding
            FEC Coding Type: 'BCC' | 'LDPC'
        :param greenfield_mode
            Greenfield/Mixed mode: 'Mixed' | 'Greenfield'
        :param preamble
            Preamble type in DSSS: 'LONG' | 'SHORT'
        :param payload
            Payload length. Integer value needs to be given as a string type argument. Eg: '4095'
        :param run
            Run type: 'per' | 'aci'
        :param chain_sel
            chain selection in case of SISO. In MIMO case chain_sel will be defaulted to 1.
        """
        self.start_vsg()
        self.set_equip_default()
        chain_sel = 1 if (streams == '2x2') else chain_sel
        self.set_modulation(standard,run,chain_sel=chain_sel)
        self.set_bandwidth(bw=bw,standard=standard,chain_sel=chain_sel)
        if((standard=='11n')or(standard=='11ac')or(standard=='11ax')):
            self.set_streams(standard,streams,chain_sel=chain_sel)
            self.set_stbc(stbc,chain_sel=chain_sel)
            self.set_guardinterval(gi,chain_sel=chain_sel)
            self.set_coding(coding,chain_sel=chain_sel)
        if(standard=='11n'):
            self.set_greenfield(greenfield_mode,chain_sel=chain_sel)
        if(standard=='11b'):
            self.set_preamble(preamble,chain_sel=chain_sel)
        self.set_idleinterval(250,chain_sel=chain_sel)
        self.generate_waveform(streams=streams,chain_sel=chain_sel)
        self.rf_on_off(rf_state='off',streams=streams,chain_sel=chain_sel)

    #802.11a Initialization settings
    def config_aci_11a(self):
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:STANdard WAG\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:STANdard WAG\n')

    #802.11b Initialization settings
    def config_aci_11b(self):
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:STANdard WBG\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:STANdard WBG\n')
    #802.11g Initialization settings
    def config_aci_11g(self):
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:STANdard WAG\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:STANdard WAG\n')

    #802.11n Initialization settings
    def config_aci_11n(self):
        #print(':SOURce1:BB:WLNN:FBLock1:STANdard WN\n')
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:STANdard WN\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:STANdard WN\n')

    #802.11ac Initialization settings
    def config_aci_11ac(self):
        #print ':SOURce1:BB:WLNN:FBLock1:STANdard WAC\n'
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:STANdard WAC\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:STANdard WAC\n')


    #Modulation Type
    def set_aci_modulation(self,standard):
        print "\nSetting "+standard+" in VSA"
        eval('self.config_aci_'+standard+'()')
        cntrl_sckt.send('SOURce1:FSIMulator:BYPass:STATe 1\n')
        cntrl_sckt.send('SOURce2:FSIMulator:BYPass:STATe 1\n')

    #Setting Payload
    def set_aci_payload(self,standard,payload):
        print "\nSetting payload ",payload
        if((standard=='11ac')or(standard=='11ax')):
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:MPDU1:DATA:LENGth '+payload+'\n')
            cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:MPDU1:DATA:LENGth '+payload+'\n')
        else:
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:DATA:LENGth '+payload+'\n')
            cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:DATA:LENGth '+payload+'\n')


    #Setting MAC Header OFF
    def set_aci_macheader(self):
        print 'Set ACI MACHeader'
        #print ':SOURce1:BB:WLNN:FBLock1:MAC:STATe 1\n'
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:MAC:STATe 1\n')
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:MAC:FCS:STATe 1\n')
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:MAC:ADDRess1 #HABCDEFABCDEF,48\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:MAC:STATe 1\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:MAC:FCS:STATe 1\n')
        cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:MAC:ADDRess1 #HABCDEFABCDEF,48\n')

    #Setting Channel
    def apply_aci_vsg(self,bw='',chn='',streams='2x2'):
        if(streams=='1x1'):
            if(bw=='20'):
                if(chn<15):
                    if(chn==1):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+4)*5)+2412)+'000000\n')#Equals to chn 6 which is ACI OF CH1
                    elif(chn==6):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+4)*5)+2412)+'000000\n')#Equals to chn 11 which is ACI OF CH6
                    elif(chn==11):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-6)*5)+2412)+'000000\n')#Equals to chn 6 which is ACI OF CH11
                else:
                    #print ':SOURce1:FREQuency:CW '+str((chn*5)+5000)+'000000\n'
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-4)*5)+5000)+'000000\n')
            elif(bw=='40'):
                if(chn<15):
                    if(chn==1):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+7)*5)+2412)+'000000\n')#Equals to chn 9 which is ACI OF CH1
                    elif(chn==11):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-9)*5)+2412)+'000000\n')#Equals to chn 3 which is ACI OF CH11
                else:
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-8)*5)+5000)+'000000\n')
            elif(bw=='80'):
                cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-16)*5)+5000)+'000000\n')

    def apply_aaci_vsg(self,bw='',chn='',streams='2x2'):
        if(streams=='1x1'):
            if(bw=='20'):
                if(chn<15):
                    if(chn==1):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+7)*5)+2412)+'000000\n')#Equals to chn 6 which is ACI OF CH1
                    elif(chn==6):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+7)*5)+2412)+'000000\n')#Equals to chn 11 which is ACI OF CH6
                    elif(chn==11):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-9)*5)+2412)+'000000\n')#Equals to chn 6 which is ACI OF CH11
                else:
                    #print ':SOURce1:FREQuency:CW '+str((chn*5)+5000)+'000000\n'
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-8)*5)+5000)+'000000\n')
            elif(bw=='40'):
                if(chn<15):
                    if(chn==1):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+15)*5)+2412)+'000000\n')#Equals to chn 11 which is ACI OF CH1
                    elif(chn==11):
                        cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn+15)*5)+2412)+'000000\n')#Equals to chn 1 which is ACI OF CH11
                else:
                    cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-16)*5)+5000)+'000000\n')
            elif(bw=='80'):
                cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(((chn-32)*5)+5000)+'000000\n')


    #Setting ACI Amplitude
    def set_aci_amplitude(self,streams,ampl):
        #print "\nSetting ACI amplitude ",ampl
        DebugPrint("\nSetting amplitude "+str(ampl))
        if(streams=='1x1'):
            cntrl_sckt.send(':SOURce2:POWer:LEVel:IMMediate:AMPLitude '+ampl+'\n')
        #time.sleep(0.5)

    def set_aci_bandwidth(self,standard='',bw=''):
        if(standard=='11b'):
            cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:TMODe CCK\n')
        elif((standard=='11a') or (standard=='11g')):
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:TMODe L20\n')
        elif(standard=='11n'):
            cntrl_sckt.send(':SOURce2:BB:WLNN:BWidth BW'+bw+'\n')
            if(bw=='20'):
                cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:TMODe HT20\n')
            elif(bw=='40'):
                cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:TMODe HT40\n')
        elif((standard=='11ac')or(standard=='11ax')):
            cntrl_sckt.send(':SOURce2:BB:WLNN:BWidth BW'+bw+'\n')
            if(bw=='20'):
                #print ':SOURce2:BB:WLNN:FBLock1:TMODe V20\n'
                cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:TMODe V20\n')
            elif(bw=='40'):
                #print(':SOURce2:BB:WLNN:FBLock1:TMODe V40\n')
                cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:TMODe V40\n')
            elif(bw=='80'):
                cntrl_sckt.send(':SOURce2:BB:WLNN:FBLock1:TMODe V80\n')

    #RF ON/OFF
    def rf_on_off_aci(self,rf_state='on',streams='1x1'):
        print "\nSetting RF ",rf_state
        if(rf_state=='off'):
            if(streams=='1x1'):
                cntrl_sckt.send(':OUTPut1:STATe 0\n')
            elif(streams=='2x2'):
                cntrl_sckt.send(':OUTPut1:STATe 0\n')
                cntrl_sckt.send(':OUTPut2:STATe 0\n')
        elif(rf_state=='on'):
            if(streams=='1x1'):
                cntrl_sckt.send(':SOURce1:BB:WLNN:STATe 1\n')
                cntrl_sckt.send(':SOURce2:BB:WLNN:STATe 1\n')
                cntrl_sckt.send(':OUTPut1:STATe 1\n')
                cntrl_sckt.send(':OUTPut2:STATe 1\n')
        time.sleep(2)

    def init_bb_vsg_funcs(self,standard='11ac',bw='20',streams='2x2',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',chain_sel=1):
        """Configures the VSG (Baseband ports) according to given input parameters
        :param standard
            To set the wi-fi standard 802.11a/b/g/n/ac
        :param bw
            To set the operating Bandwidth (Channel Bandwidth)
        :param streams
            To decide SISO(1x1) | MIMO(2x2) case
        :param stbc
            STBC Type (STBC Employed or not): 'STBC_0' | 'STBC_1'
        :param gi
            GI Type: 'LGI' | 'SGI'
        :param coding
            FEC Coding Type: 'BCC' | 'LDPC'
        :param greenfield_mode
            Greenfield/Mixed mode: 'Mixed' | 'Greenfield'
        :param preamble
            Preamble type in DSSS: 'LONG' | 'SHORT'
        :param payload
            Payload length. Integer value needs to be given as a string type argument. Eg: '4095'
        :param chain_sel
            chain selection in case of SISO. In MIMO case chain_sel will be defaulted to 1.
        """
        DebugPrint('Initialize VSG functions for Baseband processing')
        self.start_vsg()
        self.set_equip_default()
        chain_sel = 1 if (streams == '2x2') else chain_sel
        self.set_modulation(standard,chain_sel=chain_sel)
        self.set_bandwidth(bw=bw,standard=standard,chain_sel=chain_sel)
        self.set_idleinterval(50000,chain_sel=chain_sel)
        if((standard=='11n')or(standard=='11ac')or(standard=='11ax')):
            self.set_streams(standard,streams,chain_sel=chain_sel)
            self.set_stbc(stbc,chain_sel=chain_sel)
            self.set_guardinterval(gi,chain_sel=chain_sel)
            self.set_coding(coding,chain_sel=chain_sel)
        if(standard=='11n'):
            self.set_greenfield(greenfield_mode,chain_sel=chain_sel)
        if(standard=='11b'):
            self.set_preamble(preamble,chain_sel=chain_sel)
        self.generate_waveform(streams=streams,chain_sel=chain_sel)
        # Turn ON BaseBand before turning ON the clock, as if done later,
        # RnS will turn on IQ Modulation also, which in turn ruins the
        # sinusoid required for the clock
        self.bb_on_off(bb_state='on',streams=streams,chain_sel=chain_sel)
        time.sleep(1)
        # Clock should be generated from VSG in order to do base band analysis
        # Hence tun off baseband output, and Feed the clock from RnS and
        # then set the baseband settings (I/Q analog voltages, I/Q voltage etc).
        self.reset_bb_settings() # Turns OFF the Baseband Output from VSG
        self.set_bb_settings(streams=streams,chain_sel=chain_sel)


    def reset_bb_settings(self):
        """ Resets the BB settings (Turns OFF the BB VSG)"""
        # Turn OFF I/Q Analog A,B
        cntrl_sckt.send(':SOURce1:IQ:OUTPut:ANALog:STATe 0\n')
        cntrl_sckt.send(':SOURce2:IQ:OUTPut:ANALog:STATe 0\n')
        time.sleep(1)
        #cntrl_sckt.send(':SOURce1:IQ:OUTPut:ANALog:BIAS:COUPling:STATe 0\n')
        #cntrl_sckt.send(':SOURce2:IQ:OUTPut:ANALog:BIAS:COUPling:STATe 0\n')


    #VSG settings required for baseband processing
    def set_bb_settings(self, streams='1x1',chain_sel=1):
        """Applies the following VSG settings required for baseband processing:
            1. Sets the 52MHz clock from RF port A of RnS
            2. Sets BB Ports of VSG based on the streams and chain_sel set(Turns ON BB VSG)
            3. Turn ON I/Q Analaog Outputs
            4. Choose Differential Mode (DIFF)
            5. Choose Variable Mode voltage (VAR)
            6. Sets the IQ VOltage of 1.4V
            7. Turns on Couple IQ Bias
            8. Set I/Q Bias volatge = 560 mV
            9. Turn OFF Digital Imparments
        :param streams
            To decide SISO(1x1) | MIMO(2x2) case
        :param chain_sel
            chain selection in case of SISO. In MIMO case chain_sel will be defaulted to 1.
        """
        DebugPrint('VSG settings for Baseband processing')
        # Set the 52MHz clock required for DUT
        self.set_clock()
        #self.bb_on_off(bb_state='on',streams=streams)
        iq_voltage = 1.4
        # Settings defined here are common for 1x1 and 2x2
        # Extra settings for 2x2 are defined in if condition

        # Turn ON I/Q Analaog Outputs
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':IQ:OUTPut:ANALog:STATe 1\n')
        # Choose Differential Mode (DIFF), For Singular Mode use SING instead of DIFF
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':IQ:OUTPut:ANALog:TYPE DIFF\n')
        # Choose Variable Mode voltage (VAR), For fixed mode, use FIX instaed of VAR
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':IQ:OUTPut:ANALog:MODE VAR\n')
        # Set I/Q Voltage Level to 1.4
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':IQ:OUTPut:LEVel '+str(iq_voltage)+'\n')
        # Turn On Couple I/Q BIAS
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':IQ:OUTPut:ANALog:BIAS:COUPling:STATe 1\n')
        # Set I/Q Bias Voltage as 560mV = 0.56V
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':IQ:OUTPut:ANALog:BIAS:I 0.56\n')
        # Turn OFF Digital Imparments
        cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:IMPairment:IQOutput1:STATe 0\n')
        time.sleep(1)

        if(streams == '2x2'):
            # Turn ON I/Q Analaog Outputs
            cntrl_sckt.send(':SOURce2:IQ:OUTPut:ANALog:STATe 1\n')
            # Choose Differential Mode (DIFF), For Singular Mode use SING instead of DIFF
            cntrl_sckt.send(':SOURce2:IQ:OUTPut:ANALog:TYPE DIFF\n')
            # Choose Variable Mode voltage (VAR), For fixed mode, use FIX instaed of VAR
            cntrl_sckt.send(':SOURce2:IQ:OUTPut:ANALog:MODE VAR\n')
            # Set I/Q Voltage Level to 1.4
            cntrl_sckt.send(':SOURce2:IQ:OUTPut:LEVel '+str(iq_voltage)+'\n')
            # Turn On Couple I/Q BIAS
            cntrl_sckt.send(':SOURce2:IQ:OUTPut:ANALog:BIAS:COUPling:STATe 1\n')
            # Set I/Q Bias Voltage as 560mV = 0.56V
            cntrl_sckt.send(':SOURce2:IQ:OUTPut:ANALog:BIAS:I 0.56\n')
            # Turn OFF Digital Imparments
            cntrl_sckt.send(':SOURce2:BB:IMPairment:IQOutput1:STATe 0\n')
            time.sleep(1)

    def set_clock(self):
        """ Generate 52MHz sinusoid signal as Clock for DUT from RF Port A """
        print "Generating 52MHz clock from RF Port A of RnS"
        DebugPrint('Generating 52MHz clock from RF Port A of RnS')
        cntrl_sckt.send(':SOURce1:FREQuency:CW 52000000\n')
        # RF1 ON, RF2 OFF
        cntrl_sckt.send(':OUTPut1:STATe 1\n')
        cntrl_sckt.send(':OUTPut2:STATe 0\n')
        # Turn I/Q Modulation OFF (Since, we are feeding clock from RnS)
        cntrl_sckt.send(':SOURce1:IQ:STATe 0\n')
        cntrl_sckt.send(':SOURce2:IQ:STATe 0\n')
        # Set Clock amplitude at 0 dBm
        cntrl_sckt.send(':SOURce1:POWer:LEVel:IMMediate:AMPLitude 0\n')
        time.sleep(1)


    #BB SIGNAL ON/OFF
    def bb_on_off(self, bb_state='on',streams='2x2',chain_sel=1):
        print "\nSetting Baseband ", bb_state.upper()
        DebugPrint("\nSetting Baseband " + bb_state.upper())
        if(bb_state=='off'):
            if(streams=='1x1'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:STATe 0\n')
            elif(streams=='2x2'):
                cntrl_sckt.send(':SOURce1:BB:WLNN:STATe 0\n')
                #cntrl_sckt.send(':SOURce2:BB:WLNN:STATe 0\n')
        elif(bb_state=='on'):
            # By pass the Fading Simulator, if Fading is OFF
            cntrl_sckt.send('SOURce'+str(chain_sel)+':FSIMulator:BYPass:STATe 1\n')
            if(streams=='1x1'):
                cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:STATe 1\n')
                # Turn OFF IQ modulations
                cntrl_sckt.send(':SOURce1:IQ:STATe 0\n')
                cntrl_sckt.send(':SOURce2:IQ:STATe 0\n')
            elif(streams=='2x2'):
                cntrl_sckt.send(':SOURce1:BB:WLNN:STATe 1\n')
                #cntrl_sckt.send(':SOURce2:BB:WLNN:STATe 1\n')
                # Turn OFF IQ modulations
                cntrl_sckt.send(':SOURce1:IQ:STATe 0\n')
                cntrl_sckt.send(':SOURce2:IQ:STATe 0\n')
        time.sleep(2)

    def generate_baseband_signal(self,standard='11ac',bw='20',streams='2x2',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',chain_sel=1):
        """Configures the VSG (Baseband ports) to generate Baseband Signal.
        :param standard
            To set the wi-fo standard 802.11a/b/g/n/ac
        :param bw
            To set the operating Bandwidth (Channel Bandwidth)
        :param streams
            To decide SISO(1x1) | MIMO(2x2) case
        :param stbc
            STBC Type (STBC Employed or not): 'STBC_0' | 'STBC_1'
        :param gi
            GI Type: 'LGI' | 'SGI'
        :param coding
            FEC Coding Type: 'BCC' | 'LDPC'
        :param greenfield_mode
            Greenfield/Mixed mode: 'Mixed' | 'Greenfield'
        :param preamble
            Preamble type in DSSS: 'LONG' | 'SHORT'
        :param payload
            Payload length. Integer value needs to be given as a string type argument. Eg: '4095'
        :param chain_sel
            chain selection in case of SISO. In MIMO case chain_sel will be defaulted to 1.
        """
        DebugPrint('Generating Baseband Signal')
        chain_sel = 1 if (streams == '2x2') else chain_sel
        eval('self.config_'+standard+'(chain_sel)') # Don't call self.set_modulation(standard) here
        if(standard=='11n'):
            self.set_greenfield(greenfield_mode,chain_sel=chain_sel)
        self.set_bandwidth(bw=bw,standard=standard,chain_sel=chain_sel)
        self.set_idleinterval(100,chain_sel=chain_sel)
        self.set_macheader()
        if((standard=='11n')or(standard=='11ac')or(standard=='11ax')):
            self.set_spatial_streams(standard,streams,chain_sel=chain_sel)
            self.set_stbc(stbc,chain_sel=chain_sel)
            self.set_guardinterval(gi,chain_sel=chain_sel)
            self.set_coding(coding,chain_sel=chain_sel)
        elif(standard=='11b'):
            self.set_preamble(preamble,chain_sel=chain_sel)
        self.generate_waveform(streams=streams, chain_sel=chain_sel)
        time.sleep(1)


    def set_spatial_streams(self,standard,streams,chain_sel=1):
        """ Sets the Number of Spatial Streams"""
        print "\nSetting Number of Spatial Streams = ",streams
        if(streams=='1x1'):
            cntrl_sckt.send(':SOURce'+str(chain_sel)+':BB:WLNN:FBLock1:SSTReam 1\n') #1x1
        elif(streams=='2x2'):
            #cntrl_sckt.send(':SCONfiguration:MODE ADV\n')
            #cntrl_sckt.send(':SCONfiguration:BASeband:SOURce COUP\n')
            #cntrl_sckt.send(':SCONfiguration:FADing MIMO2X2\n')
            #cntrl_sckt.send(':SCONfiguration:APPLy\n')
            #cntrl_sckt.send(':SCONfiguration:APPLy\n')
            #time.sleep(0.5)
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:SSTReam 2\n')#2x2
        time.sleep(1)

    def vsgEnableSuFrame(self):
        """ Sets the packet format for the generated packet as HESU."""
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:PFORmat SU\n')

    def vsgEnableErsuFrame(self):
        """ Sets the packet format for the generated packet as HEERSU."""
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:PFORmat SUEX\n')

    def vsgEnableTriggerFrame(self):
        """ Sets the packet format for the generated packet as HETB."""
        debugPrint('R&S does not support trigger frame')
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:PFORmat SU\n')

    def vsgEnableResponseTriggerFrame(self):
        """ Enable response trigger packet """
        debugPrint('R&S does not support trigger frame')

    def vsgDisableResponseTriggerFrame(self):
        """ Disable response trigger packet """
        debugPrint('R&S does not support trigger frame')

    def vsgEnableDisambiguity(self):
        """ Enable PE Disambiguity bit while generating packet """
        pass

    def vsgDisableDisambiguity(self):
        """ Disable PE Disambiguity bit while generating packet """
        pass

    def setVsgGiLtfType(self, Gi, Ltf):
        """ Sets the combination of HE-LTF size and GI time
                0 :	GI1 data (0.8us) and 1x HE LTF
                1 :	GI2 data (1.6us) and 2x HE LTF
                2 :	GI4 data (3.2us) and 4x HE LTF
         """
        giType = 8 << Gi
        ltfType = 32 << Ltf
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:GUARd GD' +str(giType) + '\n')
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:SYMDuration SD' +str(ltfType) + '\n')

    def vsgEnableLdpcExtraSymbol(self):
        """ Sets the LDPC extra symbol for 802.11ax packet generation """
        pass

    def vsgDisableLdpcExtraSymbol(self):
        """ Resets the LDPC extra symbol for 802.11ax packet generation """
        pass

    def setVsgNumLtf(self, numLtf):
        """ Sets the number of extra OFDM symbols of the HE-LTF field to be used for 802.11ax packet generation.
        The total number of HE-LTF symbols can only take the values 1, 2, 4, 6, or 8.
        """
        pass

    def setVsgUserCodingStandard(self, user, standard):
        """ Sets the Coding type for WiFi 11ax/ac/n/a/g/p wave generation. Settings are for the optionally specified user in case of MU.
            standard = 'BCC' | 'LDPC'
        """
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:USER' +str(user) + ':CODing:TYPE '+ standard + '\n')

    def setVsgUserRuIdx(self, user, ruIdx):
        """ Sets the RU Allocation Index for the optionally specified user. Only applies to 802.11ax trigger-based PPDU.
            ruIdx = 0 to 68
        """
        pass

    def setVsgPreFecfactor(self, fecFactor):
        """ Sets the PreFecfactor for 802.11ax packet generation. Only applies to HE trigger-based PPDU .
            fecFactor = 1 to 4
         """
        pass

##    def setVsgPreFecfactor(self, fecFactor):
##        #DebugPrint("\n disabling trigger frame)
##        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:OFDM:AFAC ' + str(fecFactor) +'\n')

    def vsgEnableDcm(self, user):
        """ Sets whether DCM is enabled for WiFi 11ax wave generation. Settings are for the optionally specified user in case of MU."""
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:USER' +str(user) + ':DCM 1\n')

    def vsgDisableDcm(self, user):
        """ Resets whether DCM is enabled for WiFi 11ax wave generation. Settings are for the optionally specified user in case of MU."""
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:USER' +str(user) + ':DCM 0\n')

    def setMuNumUser(self, numUser):
        """Sets the number of users for generation of OFDM-based packets.
            numUser = 1 to 138
        """
        pass

    def setHetbNumUser(self, numUser):
        """Sets the number of users for purpose of 802.11ax trigger frame generation.
            numUser = 1 to 138
        """
        pass

    def vsgEnableMultiuser(self):
        """Sets the multi-user state for generation of OFDM-based packets"""
        pass

    def vsgEnableDoppler(self):
        """Sets the doppler state for generation of 11ax packets"""
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:DOPPler ON\n')

    def vsgDisableDoppler(self):
        """Resets the doppler state for generation of 11ax packets"""
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:DOPPler OFF\n')

    def setVsgMidamplePeriodicity(self, midample):
        """Sets the midamble periodicity for 802.11ax waveform generation.
            midample = 10 or 20
        """
        pass

    def vsgEnableLtfMode(self):
        """Sets the MU-MIMO HE-LTF Mode for 802.11ax packet generation. Only applies to HE trigger-based full BW PPDU."""
        pass

    def vsgDisableLtfMode(self):
        """ReSets the MU-MIMO HE-LTF Mode for 802.11ax packet generation. Only applies to HE trigger-based full BW PPDU."""
        pass

    def setVsgUserDatarate(self, user, datarate):
        """Sets the Modulation and Coding Scheme for WiFi 11ax/ac/n/a/g/p wave generation. For 20 MHz 11a/g/p,
            the mapping from MCS value to data rate is as follows:
            0: 6 Mbps, 1: 9 Mbps, 2: 12 Mbps, 3: 18 Mbps, 4: 24 Mbps, 5: 36 Mbps, 6: 48 Mbps, 7: 54 Mbps.
            datarate = 0 to 102
        """
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:USER' +str(user) + ':MCS '+ datarate +'\n')

    def setVsgUserNss(self, user, nss):
        """ Sets the number of spatial streams for WiFi 11ax/ac/n/a/g/p wave generation. Settings are for the optionally specified user in case of MU.
        nss = 1 to 8
        """
        pass

    def setVsgBssColor(self, bssColor):
        """ Sets the BSS color, as defined in the HE-SIG-A fields. Only applies to 802.11ax.
        bssColor = 0 to 63
        """
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:BSSColor ' +str(bssColor) + '\n')
        pass

    def setVsgExRangeRuType(self, ruType):
        """ Sets whether the generated Extended Range HE PPDU consists of right 106 tone RU or full BW 242 tone RU.
        Only applies to 802.11ax HE Extended Range PPDU generation.
        ruType = 106 or 242
        """
        if (ruType ==106):
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:RIGHt106tone 1\n')
        else:
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:RIGHt106tone 0\n')

    def setVsgMuRuAllocation(self, cBit, ruAllocation,staIdList):
        """ Sets the HE-SIG-B common bits as defined in 802.11ax and the number of users per resource unit (RU).
             The HE-SIG-B common bits should be 8 bits for 20MHz, 16 bits for 40MHz and 32 bits for 80MHz and 64 Bits for 160MHz bandwidths respectively.
             This setting is only applicable for HE MU PPDU packet format The input is in form of unquoted string of 0s and 1s with MSB first.
             RU allocation is the number of users allocated per RU """
        cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:CCH1:RUSelection1 ' +str(cBit) + '\n')
        for i in range(len(ruAllocation)):
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:USER' +str(ruAllocation[i]) + ':STATe 1\n')
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:USER' +str(ruAllocation[i]) + ':STAid' +str(staIdList[i]) + '\n')
        pass

    #Setting MU MAC Header
##    def set_userMacheader(self, user):
##        cntrl_sckt.sendall('CHAN1;WIFI;CONF:WAVE:PSDU:MACH:ADDR1:USER'+str(user)+ ' 0'+ str(user)+'0000C0FFEE\n')

    def configHE(self,configParams):
        if (configParams.format == 6):
            self.vsgEnableMultiuser()
            self.setMuNumUser(configParams.numUser)
            self.setVsgMuRuAllocation(cBit,ruAllocation,staIdList)
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
##            self.setVsgMidamplePeriodicity(configParams.midamblePeriodicity)
            self.setVsgGiLtfType(configParams.giType, configParams.heLtfType)
##            datarate = configParams.data_rate.split('MCS')[-1]
##            self.setVsgUserDatarate(1, datarate)
            if ((configParams.format == DUT_FrameFormat.HE_ERSU) and (configParams.chBandwidth == 0)):
                self.setVsgExRangeRuType(242)
            else:
                self.setVsgExRangeRuType(106)
            cntrl_sckt.send(':SOURce1:BB:WLNN:FBLock1:USER1:MAC:FCS:STATe 1\n')
        else:
            self.setVsgGiLtfType(configParams.giType, configParams.heLtfType)
            self.setVsgNumLtf(numLtf)
            for user in configParams.userRuIndex :
                self.setVsgUserCodingStandard(user, standard)
                self.setVsgUserDatarate(user, datarate)
                if (configParams.dcm == 1):
                    self.vsgEnableDcm(user)
                else:
                    self.vsgDisableDcm(user)
            if (configParams.doppler == 1):
                self.vsgEnableDoppler()
            else:
                self.vsgDisableDoppler()
            self.setVsgMidamplePeriodicity(midample)

    def configJammer(self,configParams):
        self.setJammerTone(int(configParams.channel),configParams.jammer_tone)
        self.set_aci_amplitude(configParams.streams,str(configParams.jammer_amplt))
        pass

    def setJammerTone(self,chn='',tone=1):
        """Set the Channel and Frequency band in VSG for RX Harness """
        DebugPrint('Applying VSG channel '+str(chn)+' and Tone '+str(tone)+' for RX Harness')
        if(chn < 14):
            cntrl_sckt.send(':SOURce2:FREQuency:CW '+str((chn*5)+2407+tone)+'000000\n')
        elif(chn == 14):
            cntrl_sckt.send(':SOURce2:FREQuency:CW '+str(2484+tone)+'000000\n')
        else:
            cntrl_sckt.send(':SOURce2:FREQuency:CW '+str((chn*5)+5000+tone)+'000000\n')

    #Enable Fading Module
    def enableFadingModule(self):
        """Enable Fading Module."""
        print "\nEnable Fading Module"
        DebugPrint("\nEnable Fading Module")
        cntrl_sckt.send(':SOURce1:FSIMulator:STATe 1\n')

    # Disable Fading Module
    def disableFadingModule(self):
        """disable Fading Module."""
        print "\nDisable Fading Module"
        DebugPrint("\nDisable Fading Module ")
        cntrl_sckt.send(':SOURce1:FSIMulator:STATe 0\n')

    def setFadingChannelType(self, channelType):
        cntrl_sckt.send(':SOURce1:FSIMulator:STANdard WLANNSMOD' + channelType + '\n')

