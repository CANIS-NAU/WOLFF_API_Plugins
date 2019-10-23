from requests_oauthlib import OAuth1Session
import socket
import json
import paho.mqtt.client as mqtt
import time

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

    def encode_data( self, data ):
        return json.dumps( data )

    def decode_data( self, data ):
        return json.loads( data.decode( 'utf-8' ) )

    def do_request( self, data_dict ):
        """
        Perform a request on behalf of the user. Uses the appropriate
        request handler that allows for OAUth authentication using the users' credentials.

        Args:
          data_dict: A dictionary containing data that allows 
                     us to determine the parameters for our request.
                     
                     We need the following:
                        credentials: oauth1 (oauth2 not supported currently) credentials 
                                     containing the necessary args to perform authenticated requests.
                        http_method: the http method to perform 
                        url: the base url + the uri to submit the request to.
                        params: The paramaters (and their arguments) to include in the request
        Returns:
            Result: the result object returned by OAuthRequestsLib
                             
        """
        request_handler = self.get_request_handler( data_dict[ 'credentials' ] )

        if data_dict[ 'method' ][ 'http_method' ] == 'get':
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ] )
        else:
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ], data = data_dict[ 'method' ][ 'params' ] )
        return result

    def start( self ):
        """
        Start the server, allow it to run continuously. Requests will be performed 
        on behalf of users, and responses will be forwarded.
        """
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            # bind to the socket 
            sock.bind( ( self.get_ip(), self.get_port() ) )

            # listen
            sock.listen() 


            while True:
                # accept a connection
                conn, addr = sock.accept()
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
        """
        Get the request handler that allows us to perform
        authenticated http requests on behalf of the client.
        
        Args:
           credentials: The user credentials to use for authenticating the user 
        """
        return OAuth1Session( **credentials )


class MQTTServer( WOLFFServer ):
    """
    An MQTTServer that performs requests on behalf of the user, similar to 
    the base WOLFFServer. However, this server interacts with the client through 
    an MQTT broker.
    
    Incoming messages are expected to have the form posts/client_x, where x uniquely identifies 
    a client. 

    The server expects any requests coming from a client to be in the 'posts/#' topic.
    The response will be sent to the client via the 'respones/client_x' topic.
    """
    def __init__( self, ip, port, channels = None ):
        super().__init__( ip, port )
        self._channels = channels if channels else None

        self._client = mqtt.Client()
        self._client.subscribe( 'posts/#' )

        def on_connect( client, userdata, flags, rc, channels = None ):
            """
            Callback used by Paho MQTT upon connection 
            with the MQTT broker.
            """
            print( "Connected with result code " + str( rc )  )

            client.subscribe( 'posts/#' )
            for chan in channels:
                client.subscribe( chan )

        def on_message( client, userdata, msg ):
            """
            Callback used by Paho MQTT upon reception of a message 
            from the MQTT broker.
            """

            # get the method name from the URL 
            data_dict = self.decode_data( msg.payload )
            topic = str( msg.topic ).split( '/' )
            topic[ 0 ] = 'responses'

            # Note: topic is of the form /posts/client_x, where x is the ID for the client
            topic = '/'.join( topic )

            result = self.do_request( data_dict )

            time.sleep( 10 )
            self.get_client().publish( topic, msg.payload, qos = 1 )

        self.on_connect = lambda client, userdata, flags, rc: \
                          on_connect( client, userdata, flags, rc, channels = self._channels )
        self.on_message = on_message

    def start( self, timeout = 60 ):
        """
        Start the server, running continuously.
        Server will handle requests on behalf of the user via the MQTT broker.
        """
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


class WOLFFNodeProxy( MQTTServer ):
    """
    A WOLFFNodeProxy is a MQTTServer that sends requests on behalf of a user 
    to the WOLFF gateway through MQTT via TCP/IP.
    Incoming messages are expected to have the form posts/client_x, where x uniquely identifies 
    a client. 

    The server expects any requests coming from a client to be in the 'posts/#' topic.
    The response will be sent to the client via the 'respones/client_x' topic.
    """
    def __init__( self, client_ip = "127.0.0.1", client_port = 5555,
                  broker_ip = "127.0.0.1", broker_port = 1883,
                  channels = None
                ):
        self.client_ip = client_ip
        self.client_port = client_port
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self._channels = channels if channels else None

        self._client = mqtt.Client()


        def on_connect( client, userdata, flags, rc, channels = None ):
            """
            Callback used by Paho MQTT upon connection 
            with the MQTT broker.
            """
            print( "Connected with result code " + str( rc )  )

            client.subscribe( 'responses/client_#' )
            for chan in channels:
                client.subscribe( chan )

        def on_message( client, userdata, msg ):
            """
            Callback used by Paho MQTT upon reception of a message 
            from the MQTT broker.
            """

            # get the method name from the URL 
            data_dict = self.decode_data( msg.payload )
            topic = str( msg.topic ).split( '/' )
            topic[ 0 ] = 'posts'

            # Note: topic is of the form /posts/client_x, where x is the ID for the client
            topic = '/'.join( topic )

            result = self.do_request( data_dict )

            time.sleep( 10 )
            self.get_client().publish( topic, msg.payload, qos = 1 )

        self.on_connect = lambda client, userdata, flags, rc: \
                          on_connect( client, userdata, flags, rc, channels = self._channels )
        self.on_message = on_message

    def get_client_ip( self ):
        return self.client_ip

    def get_client_port( self ):
        return self.client_port

    def do_request( self, data_dict, topic ):
        """
        Send a request ot the MQTT broker, with the 
        specified topic.
        
        Params:
           data_dict: A dictionary containing the data to send.
           topic: the string topic to publish the message to,
                 'posts/client_1' for example.
        """
        self.get_client().publish( topic,
                                   self.encode_data( data_dict ),
                                   qos = 1
                                 )

    def start( self ):
        """
        Start the server, allow it to run continuously. Requests will be 
        forwarded to the MQTT broker on behalf of the user. 
        """

        self.get_client().on_connect = self.on_connect
        self.get_client().on_message = self.on_message

        self.get_client().connect( self.broker_ip, self.broker_port, 60 )

        self.get_client().loop_start()


        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            # bind to the socket 
            sock.bind( ( self.get_client_ip(), self.get_client_port() ) )

            # listen
            sock.listen() 


            while True:
                # accept a connection
                conn, addr = sock.accept()
                with conn:
                    # receive message
                    while True:

                        data = conn.recv( 4096 )

                        if not data:
                            break

                        # get the method name from the URL 
                        data_dict = self.decode_data( data )
                        topic = f"posts/{ data_dict[ 'client_id' ] }"
                        result = self.do_request( data_dict, topic )
                        # conn.sendall( result.content )
