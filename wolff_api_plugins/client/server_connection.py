from .message import Message as Message
import paho.mqtt.client as mqtt
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


    def get_ip( self ):
        """
        Return the (IPv4) IP this connection will 
        bind to when a connection is initialized
        """
        pass

    def get_port( self ):
        """
        Return the port this connection will bind to 
        when initiating a connection.
        """
        pass
    
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
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            sock.connect( ( self._ip, self._port ) )

            sock.sendall( str( message ).encode() )

          # if timeout is not inf set the timeout
            return sock.recv( 4096 ).decode( 'ascii' )
          
          # connect to the server using our socket
             # send the string representation of the message
                 # Hint( str() method socket.sendall() method,
                 #  and remember to encode the mesage
        # ip address
          # if timeout is not inf set the timeout
          
          # connect to the server using our socket
             # send the string representation of the message
             # create a Message and send it
                 # Hint( str( Method ) method socket.sendall() method,
                 #  and remember to encode the mesage
        pass


class MQTTServerConnection:
    def __init__( self, ip = "127.0.0.1",
                  port = 0,
                  timeout = 60

                ):
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self._client = mqtt.Client()


    def get_ip( self ):
        return self._ip
    
    def get_port( self ):
        return self._port

    def get_timeout( self ):
        return self._timeout


    def send( self, message ):
        self._client.connect( self.get_ip(),
                              self.get_port(),
                              self.get_timeout()
                            )
        self._client.publish( 'arnold', str( message ) )

