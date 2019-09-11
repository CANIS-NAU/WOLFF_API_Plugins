from .message import Message as Message
import socket 
import time
from numpy import inf as inf

class TCPServerConnection:
    """
        A connection to a server that takes place 
        over the TCP/IP stack using TCP. 
    """

    def __init__( self, ip = "127.0.0.1",
                  port = 0

                ):
        self._ip = ip
        self._port = port

    def send( self, message, timeout = inf ):
        """
        Sends an object of type  message 
        to the specified TCP ip address 
        over the specified port.
        Waits for a specified amount of time 
        for a response from the server, disconnects 
        after waiting and not getting a response.
        """

        # open the socket using this object's host and
        # ip address
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            sock.connect( ( self._ip, self._port ) )

            sock.sendall( str( message ).encode() )

          # if timeout is not inf set the timeout
            return sock.recv( 4096 ).decode( 'ascii' )
          
          # connect to the server using our socket
             # send the string representation of the message
                 # Hint( str() method socket.sendall() method,
                 #  and remember to encode the mesage
