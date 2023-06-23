import time

from common_utils import *
#from CSUtils import DA
import DUT_functions
from math import log

#from iqxel import *
totalPktCount = 1000

class Harness_SSH:
    def __init__(self,target):
        #self.com_port = com_port
        global ssh_obj

        global se
        global stats_path
        print(target)
        DA.UseTarget(target)
        target_info = DA.GetTargetInfo()

    #Set Streams
    def set_dut_streams(self,streams='1x1',test='rx'):
        nrx_active = int(streams.split('x')[0])
        ntx_active = int(streams.split('x')[-1])
        #if('rx' in test):
        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.TB_NRX')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, nrx_active, DUT_MemoryTypes.Default)

        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.TB_NTX')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, ntx_active, DUT_MemoryTypes.Default)
        if('tx' in test):
            mtp_address = DA.EvaluateSymbol('&tx_params.num_streams')
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, nrx_active, DUT_MemoryTypes.Default)

            mtp_address = DA.EvaluateSymbol('&tx_params.n_tx')
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, ntx_active, DUT_MemoryTypes.Default)

##            mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.TX_PARAMS_UPDATION')
##            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

##        print 'Setting DUT streams'
##        DebugPrint('Setting DUT streams')
##        if(streams=='1x1'):
##            self.dut_write('echo "uccp_num_spatial_streams=1" >'+stats_path+'params\n')
##            time.sleep(1)
##            self.dut_write('echo "antenna_sel="'+chain_sel_cmd+' >'+stats_path+'params\n')
##            time.sleep(1)
##        elif(streams=='2x2'):
##            self.dut_write('echo "uccp_num_spatial_streams=2" >'+stats_path+'params\n')
##        time.sleep(1)

    #Set Production Mode Settings
    def set_dut_production_mode_settings(self,standard='11ac',ch='40',bw='20',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',test='rx',action='',payload=1024):
#        if('rx' in test):
        pktFrameMode = greenfield_mode
        cbw_flag =  int(log(int(bw.split('in')[0])/20, 2))  # taking log with base 2

        DebugPrint('Configure DUT and do RETUNE for RX')

##            str1 = "configuring Harness with chan_bw = "+ str(obw) + \
##            ", prime20_flag = " + str(p20_flag) + ", nrx_active = " + str(nrx_active) + \
##            ", ntx_active = " + str(ntx_active) + ", channel = " + str(ch_num)


        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.BAND_WIDTH')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, cbw_flag, DUT_MemoryTypes.Default)


        # Decide the frequncy band based on channel number:
        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.FREQ_BAND')
        if(int(ch) <= 14):
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit , DUT_FreqBand.FreqBand2p4GHz, DUT_MemoryTypes.Default)
        else:
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit , DUT_FreqBand.FreqBand5GHz, DUT_MemoryTypes.Default)
        if('tx' in test):
            if (standard =='11g' or  standard =='11b' or standard =='11a'):
                mode = 0
            elif (standard =='11n'):
                mode = 8
            elif (standard =='11ac'):
                mode = 16
            elif (standard =='11ax'):
                if (pktFrameMode == 5):
                    mode = 24  # HESU
                if (pktFrameMode == 6):
                    mode = 32  # HEMU
                if (pktFrameMode == 7):
                    mode = 40  # HEERSU
                if (pktFrameMode == 8):
                    mode = 48  # HETB
            mtp_address = DA.EvaluateSymbol('&tx_params.MODE')
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, mode, DUT_MemoryTypes.Default)
            if (pktFrameMode == 8):  # For HETB 20in40 and 20in80 sbw is 40 and 80 respectively.
                sbw_flag =  int(log(int(bw.split('in')[-1])/20, 2))
            else:  # For remaining frame formats 20in40 and 20in80 sbw is 20.
                sbw_flag =  int(log(int(bw.split('in')[0])/20, 2))
            mtp_address = DA.EvaluateSymbol('&tx_params.sbw')
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit,sbw_flag, DUT_MemoryTypes.Default)

            mtp_address = DA.EvaluateSymbol('&tx_params.smoothing_enable')
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

            wait_time_between_pkts=300; #us  why is this set to 1us?
            #PHY_PERFORMANCE: this parameter can be part of TEST_PARAMS instead of tx_params
            mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.wait_time_us_between_packets')
            #DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, wait_time_between_pkts, DUT_MemoryTypes.Default)

            if (standard =='11g' or  standard =='11b' or standard =='11a'):
                mtp_address = DA.EvaluateSymbol('&tx_params.AGGREGATION')
                DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 0, DUT_MemoryTypes.Default)

            if (standard =='11ac' or  standard =='11n' or standard =='11ax'):
                mtp_address = DA.EvaluateSymbol('&tx_params.AGGREGATION')
                DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)

            if ((standard =='11n') or (standard=='11ac') or (standard =='11ax')):
                if(coding == 'BCC'):
                    codig_type = 0
                else:
                    codig_type = 1
                mtp_address = DA.EvaluateSymbol('&tx_params.LDPC')
                DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, codig_type, DUT_MemoryTypes.Default)
                if(stbc == 'STBC_0'):
                    stbc_type = 0
                else:
                    stbc_type = 1
                mtp_address = DA.EvaluateSymbol('&tx_params.STBC')
                DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, stbc_type, DUT_MemoryTypes.Default)
                if(gi == 'LGI'):
                    gi_type = 0
                else:
                    gi_type = 1
                mtp_address = DA.EvaluateSymbol('&tx_params.SGI')
                DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, gi_type, DUT_MemoryTypes.Default)

            if (standard =='11n'):
                if(greenfield_mode == 'Mixed'):
                    greenfield_type = 0
                else:
                    greenfield_type = 1
                mtp_address = DA.EvaluateSymbol('&tx_params.enable_green_field')
                DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, greenfield_type, DUT_MemoryTypes.Default)

            mtp_address = DA.EvaluateSymbol('&tx_params.psdu_length')
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, payload, DUT_MemoryTypes.Default)

            mtp_address = DA.EvaluateSymbol('&tx_params.mpdu_length')
            DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, payload, DUT_MemoryTypes.Default)

            time.sleep(0.5)


    #SET IBSS Mode
    def set_dut_ibss(self,standard='11ac',channel='40',bw='20',streams='1x1',wait='yes'):                 #  might not be required
        return


    def set_dut_channel(self,ch,p20_flag = 0):

        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.PRIM_20_OFFSET')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, p20_flag, DUT_MemoryTypes.Default)

        mtp_address = DA.EvaluateSymbol('&WLAN_HARNESS_SYS_PARAMS_CONFIG.CHANNEL_NUM')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, ch, DUT_MemoryTypes.Default)

        return        # channel number is set inside set_dut_production_mode_settings function


    def dut_check_prompt(self):                 #  might not be required
        return

    def dut_get_ipaddr(self):                 #  might not be required
        return

    def dut_login(self,res=''):                 #  might not be required
        print dut_mgmt_ip,dut_username,dut_password
        os.system('taskkill /F /im ttermpro.exe')
        time.sleep(3)
        s=serial.Serial(self.com_port,'115200',parity=serial.PARITY_NONE,bytesize=serial.EIGHTBITS,timeout=4)
        print ('Trying to Login the DUT')
        DebugPrint('DUT Login')
        s.write('\x03\n')
        time.sleep(2)
        res=s.read(10000)
        s.write('\x03\n')
        time.sleep(2)
        res=s.read(5000)
        print res
        DebugPrint(res)
        s.write('\n\x03')
        time.sleep(4)
        res=s.read(1000)
        #print '============='
        print res
        prompt=0
        #if((res.find('#')<0) or (res.find('login:')<0) ):
        if('login:' not in res):
            if('#' not in res):
                print '============='
                time.sleep(30)
                s.write('\x03\n')
                time.sleep(4)
                res=s.read(s.inWaiting())
                if('login:' not in res):
                    if('#' not in res):
                        #print '============='
                        time.sleep(30)
                    s.write('\x03\n')
                    time.sleep(4)
                    res=s.read(s.inWaiting())
                #print res
                DebugPrint(res)
                s.write('\n\x03')
                time.sleep(4)
                res=s.read(1000)
        if('login:' not in res):
            if('#' not in res):
                controlPowerSwitch(on_ports_list='8',off_ports_list='8')
                time.sleep(100)
                print ('Trying to Login the DUT')
                DebugPrint('DUT Login')
                s.write('\x03\n')
                time.sleep(2)
                res=s.read(10000)
                s.write('\x03\n')
                time.sleep(2)
                res=s.read(5000)
                print res
                DebugPrint(res)
                s.write('\n\x03')
                time.sleep(4)
                res=s.read(1000)
                #print '============='
                print res

        if('pistachio #' in res):
            DebugPrint('Entered uboot prompt')
            s.write('run usbboot\n')
            time.sleep(80)
            res=s.read(10000)
            s.write('\n\x03')
            time.sleep(3)
            res=s.read(10000)

        #print '============='
        DebugPrint(res)
        if(res.find('\n>')>0):
            print 'Spl chr'
            s.write('\x04\n')
            time.sleep(1)
            s.write('\n\n\n')
            time.sleep(1)
            res=s.read(s.inWaiting())

        if(res.find('pistachio #')>=0):
            #print 'DUT Login:::::'
            #s.write('usb start; ext4load usb 0 0x800F0000 pistachio_bub_new.dtb; ext4load usb 0 0x80400000 uImage.bin; bootm 0x80400000 - 0x800F0000\n')
            s.write('run usbboot\n')
            time.sleep(45)

            res=s.read(6000)
            s.write('\x03\x03\n')
            time.sleep(1)
            res=s.read(s.inWaiting())
            #print res
            s.write('\x03\x03\n')
            #res=s.read(s.inWaiting())
            #print '#####@@@@@@@@@@@@@@@@@'
            #print res
            #s.write('\x03\n')
            res=s.read(9000)
            #print res
        if(res.find('login:')>=0):
            print 'Passing the Login Credentials'
            s.write(dut_username+'\n')
            time.sleep(2)
            s.write(dut_password+'\n')
            time.sleep(1)
            prompt=1
            res=s.read(s.inWaiting())
            DebugPrint(res)
        if((res.find('Login incorrect')>=0) or (res.find('Password:')>=0)):
            s.write('\n')
            time.sleep(4)
            s.write(dut_username+'\n')
            time.sleep(2)
            s.write(dut_password+'\n')
            time.sleep(1)
            res= s.read(s.inWaiting())
            DebugPrint(res)

        if(res.find('#')>=0):
            prompt=1
        if(prompt==0):
            time.sleep(10)
            s.write('\n')
            time.sleep(4)
            res= s.read(s.inWaiting())
            DebugPrint(res)
            if('#' not in res):
                #print '============='
                time.sleep(10)
                s.write('\x03\n')
                time.sleep(4)
                res=s.read(s.inWaiting())
                #print res
                DebugPrint(res)
                s.write('\n\x03')
                time.sleep(4)
                res=s.read(1000)
        print prompt
        DebugPrint(prompt)
        DebugPrint('DUT_CREATE_PASSWD')
        print('DUT_CREATE_PASSWD')
        s.write('killall sshd;sleep 2;echo "PermitRootLogin yes" >> /etc/ssh/sshd_config;sleep 1;/usr/sbin/sshd\n')
        time.sleep(6)
        s.write('date -s 201508101111\n')
        time.sleep(0.5)
        s.write('passwd\n')
        time.sleep(1)
        s.write('root\n')
        time.sleep(1)
        s.write('root\n')
        time.sleep(1)
        s.write('udhcpc -i eth0\n')
        dut_mgmt_ip=self.dut_get_ipaddr()
        time.sleep(5)
        s.close()
        status=self.ssh_access(dut_mgmt_ip=dut_mgmt_ip,dut_username=dut_username,dut_password=dut_password)
        DebugPrint(status)

    def load_release_files(self,release,standard,test):
        return #dut_select_and_load_program_file_and_run(DUT_TestConfigParams)


    def get_phy_stats(self):
        [res,per]=DUT_functions.Read_rx_stats(totalPktCount)
        return res, per # returns RX stats and per

    def get_negative_stats(self):
        res = DUT_functions.readRXstatsFromPeripheralRegs()
        return res # returns RX stats read from peripheral registers

    def    reset_phy_rx_stats(self):
         DUT_functions.reset_rxStats()

    def get_stats_path(self):                 #  might not be required
        return
##        global stats_path
##        # self.dut_write('mount -t debugfs debugfs /sys/kernel/debug/')
##        # time.sleep(0.5)
##        # res=self.dut_write_read('iw phy|grep Wiphy',0.5,1000)
##        # m=re.compile('Wiphy (phy[\d]+)')
##        # print m.findall(res)
##        # try:
##            # phy_iface=m.findall(res)[-1]
##            # res=self.dut_write_read('find /sys/kernel/debug/ -name uccp420wlan')
##            # if('/sys/kernel/debug/ieee80211/'+phy_iface in res):
##                # stats_path='/sys/kernel/debug/ieee80211/'+phy_iface+'/uccp420wlan/'
##            # else:
##                # stats_path='/proc/uccp420/'
##        # except:
##            # stats_path='/proc/uccp420/'
##        stats_path='/proc/uccp420/'
##        # print res
##        #print stats_path

    def dut_reboot(self):                 #  might not be required
        print ('DUT Reboot')
        DebugPrint('DUT Reboot')
        self.dut_write('/sbin/reboot')

    #Setting Datarate
    def set_dut_datarate(self,data_rate,standard):
        print "\nSetting data rate ",data_rate
        DebugPrint("\nSetting data rate "+data_rate)
        mtp_address = DA.EvaluateSymbol('&tx_params.RATE_R_MCS')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, datarate_dict[data_rate], DUT_MemoryTypes.Default)


    #Setting TXPower
    def set_dut_txpower(self,txp):
        # print "\nSetting DUT TX Power ",txp
        DebugPrint("\n-------------------------------------------------------------Setting DUT TX Power to "+str(txp))
        mtp_address = DA.EvaluateSymbol('&tx_params.txpower')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit,int(txp), DUT_MemoryTypes.Default)
        mtp_address = DA.EvaluateSymbol('&TEST_PARAMS.TX_PARAMS_UPDATION')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, 1, DUT_MemoryTypes.Default)
        #self.dut_write('iw dev wlan0 set txpower fixed '+txp+'000\n')
        #self.dut_write('echo set_tx_power='+txp+' > '+stats_path+'params\n')#NEW PRODUCTION MODE

    #Start/Kill pktgen
    def pktgen_tool(self,DUT_TestConfigParams,status):
        DebugPrint('Pktgen '+status)
        global per_clmn
        global row_num_dr
        if(status=='write'):
            return
        if(status=='update'):
            tx_params_updation =1
            value = DA.EvaluateSymbol('&TEST_PARAMS.TX_PARAMS_UPDATION')
            DA.WriteMemoryBlock(value, 1, DUT_ElementTypes.typeUnsigned32bit, tx_params_updation , DUT_MemoryTypes.Default)
            DUT_functions.stop_tx_continuous()
            return
        elif(status=='run'):
            print 'pktgen tool : Start Pumping'
            #print 'pktgen tool : Clear_test_done_indication'
            DUT_functions.Clear_test_done_indication()
            #print 'pktgen tool : Tx_start_indication'
            DUT_functions.Tx_start_indication()
            #print 'pktgen tool : stop_tx_continuous'
            DUT_functions.stop_tx_continuous()
            print 'pktgen tool : wait_retune_done'
            DUT_functions.wait_retune_done()
            print 'sleep 10s'
            time.sleep(10)
        elif(status=='kill'):
            DUT_functions.Tx_end_indication()
            time.sleep(1)
        time.sleep(1)

    #Set RF Params
    def set_dut_rfparams(self,release):
        if(os.path.exists('rf_params_'+release)):
            print 'Reading rf from file'
            DebugPrint('Reading rf from file')
            f_rfparams=open('rf_params_'+release,'r')
            rfparams_string=f_rfparams.read()
            f_rfparams.close()
        else:
            print 'Reading default RF Params'
            DebugPrint('Reading default RF Params')
            res=self.dut_write_read('cat '+stats_path+'params |grep rf_params\ ')
            rfparams_string_read=res
            rfparams_string=rfparams_string_read.split('rf_params =')[1].split('\r\n')[0].replace(' ','').replace('0808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808','2828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828282828')
        #print rfparams_string
        self.dut_write('echo "rf_params='+rfparams_string+'" > '+stats_path+'params')
        return rfparams_string

    def set_production_calib_txpower(self,txp):
        print "\nSetting producttion calib TX Power ",txp
        DebugPrint("\nSetting producttion calib  TX Power "+str(txp))
        self.dut_write('echo set_tx_power='+txp+' > '+stats_path+'params')

    def save_pdout_values(self,dr,txp):
        DebugPrint('Saving PDOut Values')
        res=self.dut_write_read('echo aux_adc_chain_id=1 > '+stats_path+'params;cat '+stats_path+'mac_stats |grep pdout_val')
        DebugPrint(res)
        m=re.compile('pdout_val = ([-\d]*)')
        pdout_val_1x1=m.findall(res)[-1]
        res=self.dut_write_read('echo aux_adc_chain_id=2 > '+stats_path+'params;cat '+stats_path+'mac_stats |grep pdout_val')
        DebugPrint(res)
        m=re.compile('pdout_val = ([-\d]*)')
        pdout_val_2x2=m.findall(res)[-1]
        return float(pdout_val_1x1),float(pdout_val_2x2)

    def dut_state_handle(self,prompt):
        return

    def check_dut_stuck_state(self):                 #  might not be required
        DebugPrint('Trying to check_dut_stuck_state')
        res=self.dut_write_read('ip addr|grep lo:')
        DebugPrint(res)
        if(res.find('LOOPBACK')>=0):
            return 'alive'
        else:
            return 'stuck'

    def check_dut_load_issues(self):                 #  might not be required
        DebugPrint('Trying to check_dut_load_issues')
        res=self.dut_write_read('\n')
        print res
        if(res.find('login:')>=0) or (res.find('#')>=0):
            return 'alive'
        else:
            return 'stuck'

    def dut_down_up(self,action='down',ch='40'):
        DUT_functions.Start_retune()
        DUT_functions.stop_tx_continuous()
        DUT_functions.wait_retune_done()


    def dut_read(self,bytes):
        return
        self.dut_write('')
        res=b.read(1000)
        return res

    def dut_write(self,cmd):
        DebugPrint(cmd)
        try:
            a,b,c=ssh_obj.exec_command(cmd,timeout=10)
            #print 'CMD -> ',cmd
            #print 'READ -> ',b.read()
            #print 'ERROR -> ',c.read()
            DebugPrint(b.read())
            DebugPrint(c.read())
        except:
            pass
    def dut_write_read(self,cmd='',seconds='',bytes=''):
        DebugPrint(cmd)
        try:
            stdin,stdout,stderr=ssh_obj.exec_command(cmd,timeout=10)
            res= stdout.read()
            err_res= stderr.read()
            #print 'CMD -> ',cmd
            #print 'READ -> ',res
            #print 'ERROR -> ',err_res
            DebugPrint(res)
            DebugPrint(err_res)
            if(len(err_res)>1):
                print 'err_res',err_res
                return 'FAIL'
            return res
        except:
            return 'FAIL'

    def ssh_access(self,dut_mgmt_ip='',dut_username='',dut_password=''):                 #  might not be required
        DebugPrint('SSH Access to '+dut_mgmt_ip)
        global ssh_obj
        try:
            ssh_obj=paramiko.SSHClient()
            ssh_obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # ssh_obj.connect(ipaddr, username=username,password=password,allow_agent=False,look_for_keys=False)#imghbvolttest003
            ssh_obj.connect(dut_mgmt_ip, username=dut_username,password=dut_password,allow_agent=False,look_for_keys=False)#imghbvolttest003
            paramiko.util.log_to_file("filename.log")
        except Exception,e:
            err_args=e.args

            if 10060 in err_args:
                print 'CONNECT_FAIL'
                DebugPrint('CONNECT_FAIL')
                return 'CONNECT_FAIL'
            elif 10061 in err_args:
                print 'CONNECT_FAIL'
                DebugPrint('CONNECT_FAIL')
                return 'CONNECT_FAIL'
            else:
                print err_args
                DebugPrint(err_args)
                print 'AUTH_FAIL'
                DebugPrint('AUTH_FAIL')
                return 'AUTH_FAIL'

    #Load DUT
    def load_dut(self,standard='11ac',channel='40',bw='20',streams='1x1',reboot=0,release='',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',test='rx'):
        DebugPrint('Load DUT')
        global dbg_print
        prompt=0
        self.dut_write('\n')
        if(self.check_dut_load_issues()=='alive'):
            DebugPrint('DUT is alive')
            self.dut_reboot()
        else:
            print 'DUT is stuck'
            DebugPrint('DUT is stuck')
            controlPowerSwitch(on_ports_list='8',off_ports_list='8')
        time.sleep(reboot_time)
        prompt=self.dut_login()
        self.dut_state_handle(prompt)
        self.load_release_files(release,standard,test=test)
        self.set_dut_streams(streams=streams,test=test)
        self.set_dut_production_mode_settings(standard=standard,ch=channel,stbc=stbc,bw=bw,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test=test,action='only_enable')
        self.set_dut_channel(channel)
        self.set_dut_ibss(channel=channel)
        #self.set_dut_rfparams(release)

    def init_dut(self,com_port='COM1',reboot=0,standard='11ac',streams='1x1',channel='40',bw='20',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',release='',test='rx',chain_sel=1):
        global chain_sel_cmd
        chain_sel_cmd=chain_sel
        DebugPrint('Init DUT')

        status=self.load_release_files(release,standard,test=test)
        self.set_dut_streams(streams=streams,test=test)
        self.set_dut_production_mode_settings(standard=standard,ch=channel,bw=bw,stbc=stbc,gi=gi,coding=coding,greenfield_mode=greenfield_mode,preamble=preamble,test=test,action='only_enable')
        self.set_dut_channel(channel)
        DUT_functions.Set_chain_selection(chain_sel)
        self.get_stats_path()
        self.set_dut_ibss(standard=standard,channel=channel,bw=bw,streams=streams)
##        if('rx' not in test):
##            self.set_dut_rfparams(release)
        #self.dut_down_up(action='up_down',ch=channel)

    def dut_close(self):
        return

    def dut_setStaID(self,staID):
        DUT_functions.setStationID(staID)
        return


    def setHesuParams(self, testConfigParams):
    #if ('dcm' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.DCM')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.dcm, DUT_MemoryTypes.Default)

        mtp_address = DA.EvaluateSymbol('&tx_params.sbw')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.chBandwidth, DUT_MemoryTypes.Default)

    #if ('doppler' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.doppler')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.doppler, DUT_MemoryTypes.Default)

    #if ('midamblePeriodicity' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.midamble_periodicity')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, (testConfigParams.midamblePeriodicity/10)-1 , DUT_MemoryTypes.Default)

    #if ('giType' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.SGI')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, testConfigParams.giType, DUT_MemoryTypes.Default)

    #if ('heLtfType' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.HE_LTF_type')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.heLtfType, DUT_MemoryTypes.Default)

    #if ('nominalPacketPadding' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.packet_padding')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.nominalPacketPadding, DUT_MemoryTypes.Default)

    #if ('peDuration' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.PE_duration')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.peDuration, DUT_MemoryTypes.Default)

    #if ('noSigExtn' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.no_signal_extension')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.noSigExtn, DUT_MemoryTypes.Default)

    def setHetbParams(self, testConfigParams):

        mtp_address = DA.EvaluateSymbol('&tx_params.DCM')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.dcm, DUT_MemoryTypes.Default)

    #if ('doppler' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.doppler')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.doppler, DUT_MemoryTypes.Default)

    #if ('midamblePeriodicity' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.midamble_periodicity')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, (testConfigParams.midamblePeriodicity/10)-1 , DUT_MemoryTypes.Default)

    #if ('giType' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.SGI')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned32bit, testConfigParams.giType, DUT_MemoryTypes.Default)

    #if ('heLtfType' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.HE_LTF_type')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.heLtfType, DUT_MemoryTypes.Default)

    #if ('nominalPacketPadding' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.packet_padding')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.nominalPacketPadding, DUT_MemoryTypes.Default)

    #if ('peDuration' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.PE_duration')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.peDuration, DUT_MemoryTypes.Default)

    #if ('noSigExtn' in txParams.keys()):
        mtp_address = DA.EvaluateSymbol('&tx_params.no_signal_extension')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.noSigExtn, DUT_MemoryTypes.Default)

        #legacyLength = int(data[0].split(':')[1])

        value = DA.EvaluateSymbol('&tx_params.L_length')
        DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned16bit, testConfigParams.legacyLength, DUT_MemoryTypes.Default )

        #ldpcExtraSymbol = int(data[1].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.ldpc_extra_symbol')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.ldpcExtraSymbol, DUT_MemoryTypes.Default)

        #ruAllocation = int(data[2].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.RU_allocation')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, 2*testConfigParams.ruAllocation, DUT_MemoryTypes.Default)

        #heLtfMode = int(data[3].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.HE_LTF_mode')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.heLtfMode, DUT_MemoryTypes.Default)

        #numOfHeLtfs = int(data[4].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.num_HE_LTF')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.numHeLtf, DUT_MemoryTypes.Default)

        #heSiga2Reserved = int(data[5].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.heSigA2Reserved')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned16bit, testConfigParams.heSiga2Reserved, DUT_MemoryTypes.Default)

        #startingStsNum = int(data[6].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.starting_sts')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.startingStsNum, DUT_MemoryTypes.Default)

        #triggerMethod = int(data[7].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.trigger_method')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.triggerMethod, DUT_MemoryTypes.Default)

        #defaultPeDuration = int(data[8].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.PE_duration')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.peDuration, DUT_MemoryTypes.Default)

        #feedbackStatus = int(data[9].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.feedback_status')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.feedbackStatus, DUT_MemoryTypes.Default)

        #heTbDisambiguity = int(data[10].split(':')[1])

        mtp_address = DA.EvaluateSymbol('&tx_params.HETB_PE_disambiguity')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeUnsigned8bit, testConfigParams.heTbDisambiguity, DUT_MemoryTypes.Default)

        #heTbPreFecFactor = int(data[11].split(':')[1])

        value = DA.EvaluateSymbol('&tx_params.pre_fec_padding')
        DA.WriteMemoryBlock(value,  1, DUT_ElementTypes.typeSigned8bit, testConfigParams.fecPadding, DUT_MemoryTypes.Default )

        #UserRuIndex = int(data[12].split(':')[1])


    def set_dut_cfo_sfo_settings(self, cfoRatio, triggerResponding):

        mtp_address = DA.EvaluateSymbol('&tx_params.CFO')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned32bit, cfoRatio, DUT_MemoryTypes.Default)

        mtp_address = DA.EvaluateSymbol('&tx_params.trigger_responding')
        DA.WriteMemoryBlock(mtp_address, 1, DUT_ElementTypes.typeSigned32bit, triggerResponding, DUT_MemoryTypes.Default)


