import time
import serial

class wifiRadioTest():
    """Client class to communicate with DUT via Serial"""

    def __init__(self, port = '/dev/ttyACM1', baudrate = 115200):
        self.port = port
        self.baudrate = baudrate

    def connect(self):
        """
        Establish connection with the device
        :return: an error message
        """
        self.ser = serial.Serial(
            port = self.port,
            baudrate=self.baudrate,
            bytesize = serial.EIGHTBITS, #number of bits per bytes
            parity = serial.PARITY_NONE ,#set parity check: no parity
            stopbits = serial.STOPBITS_ONE , #number of stop bits
            timeout = 0.5
        )

        if self.ser.isOpen() :
          return 'CONNECTED'
        else :
          return 'CONNECTION FAILED!!'

    def close(self):
        """Close connection with the device"""
        #print('Closing Serial connection')
        self.ser.close()

    def execute_command(self, cmd, timeout=5):
        """Send command to the device"""
        print(cmd)
        #cmd = f'{cmd}\n'.encode(encoding='UTF-8')
        try:
            self.ser.write(cmd+'\n')
        except Exception:
            raise
        time.sleep(0.1)

    def read(self, size=1):
        """Read data from the device"""
        #self.ser.reset_input_buffer()
        out = bytes()
        try:
            while True:
                data = self.ser.inWaiting()
                #print(data)
                #out = self.ser.read(2)
                if not data:
                    return out
                out = out + self.ser.read(data)
                #time.sleep(1)
        except Exception:
            raise
        #print(out)
        return out

    def setPhyCalibRxDcMode(self, calibMode):
        """phy_calib_rxdc    :0 - Disable RX DC calibration
                     1 - Enable RX DC calibration"""
        txt = "wifi_radio_test phy_calib_rxdc {}".format(str(calibMode))
        self.execute_command(txt)

    def setPhyCalibTxDcMode(self, calibMode):
        """phy_calib_txdc    :0 - Disable TX DC calibration
                     1 - Enable TX DC calibration"""
        txt = "wifi_radio_test phy_calib_txdc {}".format(str(calibMode))
        self.execute_command(txt)

    def setPhyCalibTxPow(self, calibMode):
        """phy_calib_txpow   :0 - Disable TX power calibration
                     1 - Enable TX power calibration"""
        txt = "wifi_radio_test phy_calib_txpow {}".format(str(calibMode))
        self.execute_command(txt)

    def setPhyCalibRxIQ(self, calibMode):
        """phy_calib_rxiq    :0 - Disable RX IQ calibration
                     1 - Enable RX IQ calibration"""
        txt = "wifi_radio_test phy_calib_rxiq {}".format(str(calibMode))
        self.execute_command(txt)

    def setPhyCalibTxIQ(self, calibMode):
        """phy_calib_txiq    :0 - Disable TX IQ calibration
                     1 - Enable TX IQ calibration"""
        txt = "wifi_radio_test phy_calib_txiq {}".format(str(calibMode))
        self.execute_command(txt)

    def setHeltfMode(self, heltf):
        """he_ltf            :0 - 1x HE LTF
                     1 - 2x HE LTF
                     2 - 3x HE LTF"""
        txt = "wifi_radio_test he_ltf {}".format(str(heltf))
        self.execute_command(txt)

    def setHeGiMode(self, heGi):
        """he_gi             :0 - 0.8 us
                     1 - 1.6 us
                     2 - 3.2 us"""
        txt = "wifi_radio_test he_gi {}".format(str(heGi))
        self.execute_command(txt)

    def setRfParams(self, rfParams):
        """rf_params         :RF parameters in the form of a 42 byte hex value string"""
        txt = "wifi_radio_test rf_params {}".format(str(rfParams))
        self.execute_command(txt)
        pass

    def setFrameformat(self, frameformat):
        """tx_pkt_tput_mode  :0 - Legacy mode
                     1 - HT mode
                     2 - VHT mode
                     3 - HE(SU) mode
                     4 - HE(ER SU) mode"""
        txt = "wifi_radio_test tx_pkt_tput_mode {}".format(str(frameformat))
        self.execute_command(txt)

    def setGaurdInterval(self, gi):
        """tx_pkt_sgi        :0 - Disable
                     1 - Enable"""
        txt = "wifi_radio_test tx_pkt_sgi {}".format(str(gi))
        self.execute_command(txt)

    def setPreamble(self, preamble):
        """tx_pkt_preamble   :0 - Short preamble
                     1 - Long preamble
                     2 - Mixed preamble"""
        txt = "wifi_radio_test tx_pkt_preamble {}".format(str(preamble))
        self.execute_command(txt)

    def setPktMCS(self, MCS):
        """tx_pkt_mcs        :-1    - Not being used
                     <val> - MCS index to be used"""
        txt = "wifi_radio_test tx_pkt_mcs {}".format(str(MCS))
        self.execute_command(txt)

    def setPktDataRate(self, dataRate):
        """tx_pkt_rate       :-1    - Not being used
                     <val> - Legacy rate to be used in Mbps (1, 2, 5.5, 11, 6,
                     9, 12, 18, 24, 36, 48, 54)"""
        txt = "wifi_radio_test tx_pkt_rate {}".format(str(dataRate))
        self.execute_command(txt)

    def setPktGap(self, gap):
        """tx_pkt_gap        :<val> - Interval between TX packets in us (Min: 200, Max:
                     200000, Default: 200)"""
        txt = "wifi_radio_test tx_pkt_gap {}".format(str(gap))
        self.execute_command(txt)

    def setChannel(self, channel):
        """chnl_primary      :<val> - Primary channel number (Default: 1)"""
        txt = "wifi_radio_test chnl_primary {}".format(str(channel))
        self.execute_command(txt)

    def setPktNumber(self, num):
        """tx_pkt_num        :-1    - Transmit infinite packets
                     <val> - Number of packets to transmit"""
        txt = "wifi_radio_test tx_pkt_num {}".format(str(num))
        self.execute_command(txt)

    def setPktLen(self, length):
        """tx_pkt_len        :<val> - Length of the packet (in bytes) to be transmitted
                     (Default: 1400)"""
        txt = "wifi_radio_test tx_pkt_len {}".format(str(length))
        self.execute_command(txt)

    def setTxPower(self, power):
        """tx_power          :<val> - Value in db"""
        txt = "wifi_radio_test tx_power {}".format(str(power))
        self.execute_command(txt)

    def setTxMode(self, mode):
        """tx                :0 - Disable TX
                     1 - Enable TX"""
        txt = "wifi_radio_test tx {}".format(str(mode))
        self.execute_command(txt)

    def setRxMode(self, mode):
        """rx                :0 - Disable RX
                     1 - Enable RX"""
        txt = "wifi_radio_test rx {}".format(str(mode))
        self.execute_command(txt)

    def setAdcCapLen(self, length):
        """rx_adc_cap        :<val> - Number of RX ADC samples to be captured"""
        txt = "wifi_radio_test rx_adc_cap {}".format(str(length))
        self.execute_command(txt)

    def setRxStaticCap(self, length):
        """rx_stat_pkt_cap   :<val> - Number of RX static pkt samples to be captured"""
        txt = "wifi_radio_test rx_stat_pkt_cap {}".format(str(length))
        self.execute_command(txt)

    def setRxDynamicCap(self, length):
        """rx_dyn_pkt_cap    :<val> - Number of RX dynamic pkt samples to be captured"""
        txt = "wifi_radio_test rx_dyn_pkt_cap {}".format(str(length))
        self.execute_command(txt)

    def setTxToneMode(self, mode):
        """tx_tone           :0 - Disable TX tone
                     1 - Enable TX tone"""
        txt = "wifi_radio_test tx_tone {}".format(str(mode))
        self.execute_command(txt)

    def getTemprature(self):
        """temp_measure      :No arguments required"""
        txt="wifi_radio_test temp_measure"
        self.execute_command(txt)
        rx = self.read()
        rx = rx.replace("wifi_radio_test temp_measure","")
        rx = rx.replace("uart:~$","")
        print(rx)

    def setXoValue(self, xo):
        """xo_val            :<val> - XO value"""
        txt = "wifi_radio_test xo_val {}".format(str(xo))
        self.execute_command(txt)

    def getRfRssi(self):
        """rf_rssi           :No arguments required"""
        txt="wifi_radio_test rf_rssi"
        self.execute_command(txt)
        rx = self.read()
        rx = rx.replace("wifi_radio_test rf_rssi","")
        rx = rx.replace("uart:~$","")
        print(rx)

    def setDpdMode(self, mode):
        """dpd               :0 - DPD bypass
                     1 - Enable DPD"""
        txt = "wifi_radio_test dpd {}".format(str(mode))
        self.execute_command(txt)

    def getCurrentConfig(self):
        """show_config       :Display the current configuration values"""
        txt="wifi_radio_test show_config"
        self.execute_command(txt)
        rx = self.read()
        rx = rx.replace("wifi_radio_test show_config","")
        rx = rx.replace("uart:~$","")
        print(rx)

    def getStats(self):
        """get_stats         :Display statistics"""
        txt="wifi_radio_test get_stats"
        self.execute_command(txt)
        rx = self.read()
        rx = rx.replace("wifi_radio_test get_stats","")
        rx = rx.replace("uart:~$","")
        print(rx)


