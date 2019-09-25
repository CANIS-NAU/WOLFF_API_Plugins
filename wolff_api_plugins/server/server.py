from requests_oauthlib import OAuth1Session
import socket
import json
import paho.mqtt.client as mqtt

class WOLFFServer:
    """ 
        A server for handling messages sent over 
        the WOLFF network.
    """
    def __init__( self, ip = "127.0.0.1", port = 5555 ):
        self.ip = ip
        self.port = port

    def get_ip( self ):
        return self.ip

    def set_ip( self, ip ):
        self.ip = ip

    def set_port( self, port ):
        self.port = port

    def get_port( self ):
        return self.port

    def decode_data( self, data ):
        return json.loads( data.decode( 'utf-8' ) )

    def do_request( self, data_dict ):
        request_handler = self.get_request_handler( data_dict[ 'credentials' ] )
        print( "Doing request" )

        if data_dict[ 'method' ] == 'get':
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ] )
        else:
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ], data = data_dict[ 'method' ][ 'params' ] )
        return result

    def start( self ):
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            # bind to the socket 
            sock.bind( ( self.get_ip(), self.get_port() ) )

            # listen
            sock.listen() 


            while True:
                # accept a connection
                conn, addr = sock.accept()

                # while true
                with conn:
                    
                    # receive message
                    while True:

                        data = conn.recv( 4096 )

                        if not data:
                            break

                        # get the method name from the URL 
                        data_dict = decode_data( data )

                        print( data_dict )
                        result = self.do_request( data_dict )
                        conn.sendall( result.content )





    def get_request_handler( self, credentials ):
        return OAuth1Session( **credentials )


class MQTTServer( WOLFFServer ):
    def __init__( self, ip, port, channels = None ):
        super().__init__( ip, port )
        self._channels = channels if channels else None

        self._client = mqtt.Client()
        self._client.subscribe( 'posts/#' )

        def on_connect( client, userdata, flags, rc, channels = None ):
            print( "Connected with result code " + str( rc )  )

            client.subscribe( 'posts/#' )
            for chan in channels:
                client.subscribe( chan )

        def on_message( client, userdata, msg ):

            print( msg.topic + " " + str( msg.payload ) )

            # get the method name from the URL 

            print( "Topic:", msg.topic )

            data_dict = self.decode_data( msg.payload )
            topic = str( msg.topic ).split( '/' )
            topic[ 0 ] = 'responses'
            # topic.append( data_dict[ 'client_id' ] )
            topic = '/'.join( topic )

            print( "Doing request." )
            result = self.do_request( data_dict )
            print( topic )

            print( "Result: ", result )
            self.get_client().publish( topic, result.text, qos = 1 )

        self.on_connect = lambda client, userdata, flags, rc: \
                          on_connect( client, userdata, flags, rc, channels = self._channels )
        self.on_message = on_message

    def start( self, timeout = 60 ):
        self.get_client().on_connect = self.on_connect
        self.get_client().on_message = self.on_message

        self.get_client().connect( self.get_ip(), self.get_port(), timeout )

        self.get_client().loop_forever()

    def get_client( self ):
        return self._client

    def add_channel( self, channel ):
        self._channels.append( channel )
        self._client.subscribe( channel )

    def add_channels( self, channels ):
        self._channels += channels
