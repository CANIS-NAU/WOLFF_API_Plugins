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
            return sock.recv( 4096 ).decode( 'utf-8' )
          
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
        self._channels = set()
        self._received_messages = list()
        self._connected = False
            
        def on_message( client, userdata, msg ):
            print( "ON MESSAGE!" )
            self._received_messages.append( ( str( msg.topic ), str( msg.payload ) ) )

        def on_disconnect( client, userdata, flags, rc ):
            self._connected = False

        def on_connect( client, userdata, flags, rc ):
            print( "CONNECT" )
            self._connected = True
            for item in self.get_channels():
                print( "Subscribing to: ", item )
                client.subscribe( item, qos = 1 )
                
        self._client = mqtt.Client( client_id = "1", clean_session = False )
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect

    def get_channels( self ):
        return self._channels

    def get_ip( self ):
        return self._ip
    
    def get_port( self ):
        return self._port

    def get_timeout( self ):
        return self._timeout

    def get_received_messages( self ):
        return self._received_messages 

    def check_for_messages( self ):

        ret = self.get_received_messages()
        self._received_messages = list()

        return ret

    def get_client( self, connect = False ):
        self._client.on_message = self.on_message
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect

        if connect:
            print( "connecting" )
            self._client.connect( self.get_ip(),
                                  self.get_port(),
                                  self.get_timeout()
                                )
            self._client.loop_start()
        return self._client


    def subscribe_to( self, topic ):
        self._channels.add( topic )
        self.get_client( connect = True )

    def send( self, message ):
        client = self.get_client( connect = not self._connected )
        post_topic = f"posts/{message.get_data()[ 'client_id' ]}"
        resp_topic = f"responses/{message.get_data()[ 'client_id' ]}" 

        print( f"Post topic: {post_topic}." )
        print( f"Resp topic: {resp_topic}." )

        if resp_topic not in self.get_channels():
            self.subscribe_to( resp_topic )

        print( 'publishing' )
        ret = self._client.publish( post_topic, str( message ) )
        print( "published" )

        return ret.mid

