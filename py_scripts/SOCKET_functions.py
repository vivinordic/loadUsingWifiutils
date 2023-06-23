######################################
import socket

from common_utils import *
######################################

def socket_init():
    """ A socket is also passed for communication between matlab and python
    ClientServer, Start the server and wait
    Creates a TCP socket which is used for communication between MATLAB and Python """
    sock, portNo = server_init()
    sock.listen(5)
    debugPrint('Now Listening')

    return sock, portNo

def server_init():
    """  Create a port to start server """
    debugPrint("Starting Server at port 30001 to control MATLAB")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 0))
        portNo = sock.getsockname()[1]
        print portNo

    except socket.error as msg:
        pass
        debugPrint('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    return sock, portNo
