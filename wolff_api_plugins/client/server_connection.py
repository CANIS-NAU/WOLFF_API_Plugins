from .message import Message as Message
import paho.mqtt.client as mqtt
import socket 
import time
import threading


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
        return self._ip

    def get_port( self ):
        """
        Return the port this connection will bind to 
        when initiating a connection.
        """
        return self._port
    
    def send( self, message ):
        """
        Sends an object of type  message 
        to the specified TCP ip address 
        over the specified port.
        Waits for a specified amount of time 
        for a response from the server, disconnects 
        after waiting and not getting a response.
        """
        message.encode()

        # open the socket using this object's host and
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            sock.connect( ( self._ip, self._port ) )

            sock.sendall( message.encode()  )

          # if timeout is not inf set the timeout
            return sock.recv( 4096 ).decode( 'utf-8' )

class MQTTServerConnection:
    """
    A delay-tolerant connection to an MQTT broker.
    Clients can send a message to the broker and check 
    to see if any responses have been sent. 
    """
    def __init__( self, ip = "127.0.0.1",
                  port = 0,
                  timeout = 60

                ):
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self._channels = set()
        self._received_messages = list()
        self._lock = threading.Lock()
        self._connected = False
            
        def on_message( client, userdata, msg ):
            """
            Callback used by paho-mqtt on receipt of message.
            """
            self._lock.acquire()
            self._received_messages.append( ( str( msg.topic ), str( msg.payload ) ) )
            self._lock.release()

        def on_disconnect( client, userdata, flags, rc ):
            self._connected = False

        def on_connect( client, userdata, flags, rc ):
            self._connected = True

            for item in self.get_channels():
                client.subscribe( item, qos = 1 ) 
                
        # client id initialized to 1 for now, we want a better way to identify clients
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
        """
        Check if our message queue has had any items placed into it.
        Uses this class' mutex to avoid race conditions with the message-watch thread.
        
        @note Calling this method clears the cache of any existing messages
        @returns  A list of string messages that have been received by the client
        """

        self._lock.acquire()

        ret = self.get_received_messages()
        self._received_messages = list()

        self._lock.release()

        return ret

    def get_client( self, connect = False ):
        """
        Return this class' client, optionally connect 
        to the MQTT broker
        If connect is true, a thread will be started that 
        watches for messages.
        """
        self._client.on_message = self.on_message
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect

        if connect:
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
        """
        Sends a message to the broker through the client.
        Subscribes to the topic where the response will be sent. 

        @param message The message to send
        @returns  status of the attempt to send the message
        """
        # connect if we are not already connected
        client = self.get_client( connect = not self._connected )
        service_topic = f"{message.get_data()[ 'service' ]}/" \
                        f"{message.get_data()[ 'name']}"

        post_topic = f"posts/{service_topic}"
        resp_topic = f"responses/{service_topic}/{client.get_id()}" 

        if resp_topic not in self.get_channels():
            self.subscribe_to( resp_topic )

        ret = self._client.publish( post_topic, message.encode() )
        return ret.mid

