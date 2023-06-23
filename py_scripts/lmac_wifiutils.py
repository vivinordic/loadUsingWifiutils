import time
import serial

class WiFiUtilsClient():
    """Client class to communicate with DUT via Serial"""

    def __init__(self, port='/dev/ttyACM1', baudrate=115200):
        self.port = port
        self.baudrate = baudrate

    def connect(self):
        """
        Establish connection with the device
        :return: an error message
        """
        self.ser = serial.Serial(
            port=self.port,
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
        #print(cmd)
        #cmd = f'{cmd}\n'.encode(encoding='UTF-8')
        try:
            self.ser.write(cmd+'\n')
            self.ser.flush()
        except Exception:
            raise
        time.sleep(0.01)

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

    def read_wrd(self,addr):
        txt="wifiutils read_wrd {}".format(hex(addr))
        self.execute_command(txt)
        #rx = self.read().strip().decode("Ascii").split("\r\n")[-3]
        rx = self.read().decode().split("\r\n")[-3]
        #print(rx)
        rx=int(rx, 0)
        #print(rx)
        return rx

    def empty_read_wrd(self,addr):
        txt="wifiutils read_wrd {}".format(hex(addr))
        self.execute_command(txt)
        #rx = self.read().strip().decode("Ascii").split("\r\n")[-3]
        rx = self.read().decode().split("\r\n")[-3]
        #print(rx)
        return rx


    def write_wrd(self,addr,data):
        txt="wifiutils write_wrd  {} {}".format(hex(addr), hex(data))
        self.execute_command(txt)

    def write_blk(self,addr,pattern,incr,wrd_len):
        txt= "wifiutils write_blk  {} {} {} {}".format(addr, pattern, incr, wrd_len)
        self.execute_command(txt)

    def read_blk(self,addr,wrd_len):
        txt="wifiutils read_blk  {} {}".format(addr, wrd_len)
        self.execute_command(txt)
        lines = int(wrd_len/4)
        num_lines = lines if ((wrd_len%4) == 0) else lines+1
        rx = self.read().decode().split("\r\n")[-(num_lines+1):-1]
        print("\n".join(rx))

    def wifi_on(self):
        txt="wifiutils wifi_on"
        self.execute_command(txt)
        rx = self.read()
        rx = rx.replace("wifiutils wifi_on","")
        rx = rx.replace("uart:~$","")
        print(rx)

    def wifi_off(self):
        txt="wifiutils wifi_off"
        self.execute_command(txt)
        rx = self.read()
        rx = rx.replace("wifiutils wifi_off","")
        rx = rx.replace("uart:~$","")
        print(rx)

    def memmap(self):
        txt="wifiutils memmap"
        self.execute_command(txt)
        rx = self.read().decode()
        rx = rx.replace("wifiutils memmap","")
        rx = rx.replace("uart:~$","")
        print(rx)