from requests_oauthlib import OAuth1Session
import socket
import json
import paho.mqtt.client as mqtt
import time
from . client_manager import ClientManager
from . decoder import *
from . api_map import *
from . response_handler import *

class WOLFFServer:
    """ 
        A server for handling messages sent over 
        the WOLFF network.
    """
    def __init__( self, db_connection,
                  ip = "127.0.0.1",
                  port = 5555
                ):
        self.ip = ip
        self.port = port
        self.conn = db_connection

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
        """
        Decode a message, generating a dictionary of 
        arguments and their values.
        Details of the encoded message can be found here:
        https://github.com/CANIS-NAU/WOLFF_Protocol/wiki
        """
        decoder_factory = DecoderFactory()
        decoder = decoder_factory.get_decoder( data )
        data_dict = decoder.decode( data )
        return data_dict 

    def do_request( self, data_dict ):
        """
        Perform a request on behalf of the user. Uses the appropriate
        request handler that allows for OAUth authentication using the users' credentials.

        @param  data_dict: A dictionary containing data that allows 
        us to determine the parameters for our request.
                     
        We need the following:
                        credentials: oauth1 (oauth2 not supported currently) credentials 
                                     containing the necessary args to perform authenticated requests.
                        http_method: the http method to perform 
                        url: the base url + the uri to submit the request to.
                        params: The paramaters (and their arguments) to include in the request

        @returns the result object returned by OAuthRequestsLib
        """
        request_handler = self.get_request_handler( data_dict[ 'credentials' ] )

        if data_dict[ 'method' ][ 'http_method' ] == 'get':
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ] )
        else:
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ], data = data_dict[ 'message' ] )
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

            client_manager = ClientManager( 'clients' )

            while True:
                # accept a connection
                conn, addr = sock.accept()
                with conn:
                    # receive message
                    while True:

                        data = conn.recv( 4096 )

                        if not data:
                            break

                        data_dict = self.decode_data( data )
                        result_handler = ResponseHandler( self.conn ) \
                                         .get_handler( data_dict )
                        self.annotate_data( data_dict, client_manager )

                        result = self.do_request( data_dict )
                        id = result_handler \
                             .handle_response( result.content.decode( 'utf-8' ) )
                        conn.sendall( str( id ).encode() )

    def get_request_handler( self, credentials ):
        """
        Get the request handler that allows us to perform
        authenticated http requests on behalf of the client.
        
        @param credentials: The user credentials to use for authenticating the user 
        """
        return OAuth1Session( **credentials )

    def annotate_data( self, data_dict, client_manager ):
        """
        Annotate a data dictionary with client and 
        service-specific information that comes from the 
        message.
        
        @pre data_dict contains the following:
           {'api_details': ('etsy', 'create_listing'), 
            'message': {'title': 'title_1', 'description': 'desc_1', 
                        'quantity': 1, 'price': 16.04, 'who_made': 'collective', 
                        'when_made': '1990s', 'is_supply': 1, 'shipping_template_id': 76575991147
                       }
           }
        'api_details' is a tuple containing the service and method 
        being used.
        Any non-dictionary values are examples, 
        and will be dependent upon the message itself, but the 
        keys are required. 'Message' will be dependent upon 
        the service/method used.


        @post data_dict contains:
        {'api_details': ('etsy', 'create_listing'), 
         'message': {'title': 'title_1', 'description': 'desc_1', 
                     'quantity': 1, 'price': 16.04, 'who_made': 'collective', 
                     'when_made': '1990s', 'is_supply': 1, 'shipping_template_id': 76575991147
                    }, 
         'method': {'http_method': 'post'}, 
         'url': 'https://openapi.etsy.com/v2/listings/', 
         'credentials': {'client_key': '', 'client_secret': '', 
                         'resource_owner_key': '', 
                         'resource_owner_secret': ''
                        }
        }
        The values of method, url, and credentials are again dependent upon 
        api_details and mesage

        @param client_manager A client manager that 
               can be used to identify clients based 
               upon a service.
        @param A dictionary containing the data from a 
               decoded message
        @returns a dictionary that is ready to be sent 
                 as an api request by do_request
        
        """
        api_map = APIMap()
        data_dict[ 'method' ] = dict()
        service, method = data_dict[ 'api_details' ]

        data_dict[ 'url' ] = api_map.get_complete_url( service, method )
        http_method =  api_map.get_http_method( service, method )
        auth_type = api_map.get_auth_type( service )
        service_identifier = api_map.get_service_identifier( service, method )

        client_id = client_manager \
                    .get_client_by_service_identifier( service,
                                                       service_identifier,
                                                       data_dict[ 'message' ][ service_identifier ]
                                                     ).get_id()

        data_dict[ 'method' ][ 'http_method' ] = http_method
        credentials = client_manager \
                      .get_client_by_id( client_id ) \
                      .get_resource( service, auth_type ) \
                      .get_data()

        data_dict[ 'credentials' ] = credentials

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
    def __init__( self, db_connection, ip, port, channels = None ):
        super().__init__( db_connection, ip, port )
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

            client_manager = ClientManager( 'clients' )
            # get the method name from the URL 
            data_dict = self.decode_data( msg.payload )

            self.annotate_data( data_dict, client_manager )

            result = self.do_request( data_dict )

            result_handler = ResponseHandler( self.conn ) \
                             .get_handler( data_dict )

            id = result_handler \
                 .handle_response( result.content.decode( 'utf-8' ) )

            topic = str( msg.topic ).split( '/' )
            topic[ 0 ] = 'responses'

            # Note: topic is of the form /posts/client_x, where x is the ID for the client
            topic = '/'.join( topic )

            time.sleep( 10 )
            self.get_client().publish( topic, id, qos = 1 )

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

    def decode_data( self, encoded_message ):
        pass

    def do_request( self, data, topic ):
        """
        Send a request ot the MQTT broker, with the 
        specified topic.
        
        @param data_dict A dictionary containing the data to send.
        @param topic the string topic to publish the message to,
               'posts/client_1' for example.
        """
        self.get_client().publish( topic,
                                   data,
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

        client_manager = ClientManager( 'clients' )

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
                        topic = f"posts/"
                        result = self.do_request( data, topic )
                        print( result.content )
                        # conn.sendall( result.content )
