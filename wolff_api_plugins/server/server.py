from requests_oauthlib import OAuth1Session
import socket
import traceback
import json
import paho.mqtt.client as mqtt
import time
from threading import Thread
import threading
import logging
import binascii
import struct
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
        logging.getLogger().debug( f"Performing a '{data_dict[ 'method' ][ 'http_method' ]}"
                                   "' request on behalf of "
                                   f"client to URL: {data_dict[ 'url' ]}."
        )


        logging.getLogger().info( f"TIMESTAMP Message to etsy: {time.time()}" )
        if data_dict[ 'method' ][ 'http_method' ] == 'get':
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ] )
        else:
            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ], data = data_dict[ 'message' ] )

        logging.getLogger().info( f"TIMESTAMP Response from etsy: {time.time()}" )
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

            client_manager = ClientManager( 'clients', self.conn )

            while True:
                # accept a connection
                conn, addr = sock.accept()
                with conn:
                    # receive message
                    while True:

                        data = conn.recv( 4096 )

                        if not data:
                            break

                        data_str = binascii.hexlify( bytearray( data ) )

                        logging.getLogger().debug( f"Data of length {len(data)} "
                                                   f"received from client: 0x{data_str}"
                        )

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
         'client_id': 'client_x'
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


        logging.getLogger().debug( f"Service: {service}, Method: {method}" )
        http_method =  api_map.get_http_method( service, method )
        logging.getLogger().debug( f"HTTP Method for request: {http_method}" )
        auth_type = api_map.get_auth_type( service )
        logging.getLogger().debug( f"Auth type for request: {auth_type}" )
        service_identifier = api_map.get_service_identifier( service, method )
        logging.getLogger().debug( f"Service identifier type for {service} "
                                   f"{method}: {service_identifier}"
        )

        replacement_value = None

        if api_map.uri_is_substitutable( api_map.get_uri( service, method ) ):
            logging.getLogger().debug( f"URI for {service}/{method} deemed to be substitutable." )
            replacement_value = api_map.get_replacement( service, method, data_dict, self.conn )
            
        logging.getLogger().debug( f"URI Replacement value (may be None): {replacement_value}" )

        data_dict[ 'url' ] = api_map.get_complete_url( service, method,
                                                       replace = replacement_value
        )


        service_identifier_value = api_map.get_identifier_value( service, method, data_dict )
        api_map.add_special_params( service, method, data_dict )

        logging.getLogger().debug( f"Service identifier for request: {service_identifier}" )
        logging.getLogger().debug( f"Service identifier value for request: {service_identifier_value}" )
        logging.getLogger().debug( f"URL for request: {data_dict[ 'url' ]}" )

        client_id = client_manager \
                    .get_client_by_service_identifier( service,
                                                       service_identifier,
                                                       service_identifier_value
                                                     ).get_id()

        data_dict[ 'method' ][ 'http_method' ] = http_method
        credentials = client_manager \
                      .get_client_by_id( client_id ) \
                      .get_resource( service, auth_type ) \
                      .get_data()

        data_dict[ 'credentials' ] = credentials
        data_dict[ 'client_id' ] = client_id

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
    def __init__( self, db_connection, ip, port, update_port, channels = None ):
        super().__init__( db_connection, ip, port )
        self._update_port = update_port
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
            logging.getLogger().debug( "Subscribing to channel: 'posts/#'" )
            for chan in channels:
                logging.getLogger().debug( "Subscribing to channel: {chan}" )
                client.subscribe( chan )

        def on_message( client, userdata, msg ):
            """
            Callback used by Paho MQTT upon reception of a message 
            from the MQTT broker.
            """


            logging.getLogger().debug( "A message has been received from the "
                                       "MQTT server."
            )

            logging.getLogger().info( f"TIMESTAMP Message from broker at: {time.time()}" )

            client_manager = ClientManager( 'clients', self.conn )
            # get the method name from the URL 
            logging.getLogger().debug( "Attempting to decode the data" )
            data_dict = self.decode_data( msg.payload )

            logging.getLogger().debug( f"Decoded data: {data_dict}" )
            self.annotate_data( data_dict, client_manager )
            logging.getLogger().debug( f"Annotated data: {data_dict}" )

            result = self.do_request( data_dict )
            decoded_content = result.content.decode( 'utf-8' )
            logging.getLogger().debug( f"Decoded Response from server: {decoded_content}"  )

            result_handler = ResponseHandler( self.conn ) \
                             .get_handler( data_dict )

            try:
                id = result_handler \
                     .handle_response( decoded_content,
                                       data_dict[ 'client_id' ]
                     )
                logging.getLogger().debug( f"Response from ResultHandler: {str( id )}" )
            except Exception as e:
                logging.getLogger().error( f"ERROR: {str(e)}" )
                sys.exit( 1 )
        
            topic = 'responses'

            # Note: topic is of the form /posts/client_x, where x is the ID for the client
            logging.getLogger().debug( "Publishing response to MQTT server." )
            logging.getLogger().info( f"TIMESTAMP Publish response to client: {time.time()}" )
            self.get_client().publish( topic, id, qos = 1 )
            logging.getLogger().debug( "Successfully published response." )

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

        logging.getLogger().debug( "Connecting to the MQTT server "
                                   f"with IP: {self.get_ip()}, port: {self.get_port()}"
        )

        self.get_client().connect( self.get_ip(), self.get_port(), timeout )

        Thread( target = self.handle_update_requests ).start()
        self.get_client().loop_forever()

    def handle_update_requests( self ):
        client_manager = ClientManager( 'clients', self.conn )

        logging.getLogger().debug( "Creating a socket to listen to incoming "
                                   f"update requests on IP: {self.get_ip()}, "
                                   f"port: {self._update_port}"
        )
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            sock.bind( (self.get_ip(), self._update_port ) )

            while True:

                logging.getLogger().debug( "Waiting for a client to connect" )
                sock.listen()

                conn, addr = sock.accept()
                host, port = conn.getpeername()
                logging.getLogger().debug( "Received a client connection with "
                                           f"IP: {host}, on port: {port}. "
                )

                logging.getLogger().info( "TIMESTAMP Connected to client at: {time.time()}" )

                try:
                    data = conn.recv( 4096 )
                except Exception as e:
                    logging.getLogger().error( "Failure to receive bytes from client." )
                    

                logging.getLogger().debug( f"Received {len( data ) } bytes from client." )

                if not data:
                    break

                decoded_data = data.decode( "utf-8" )
                logging.getLogger().debug( f"Data received: {decoded_data}")
                data_dict = json.loads( decoded_data )
                logging.getLogger().debug( f"Data dictionary (pre-annotation): {data_dict}")

                self.annotate_data( data_dict, client_manager )
                logging.getLogger().debug( f"Data dictionary (post-annotation): {data_dict}")

                result = self.do_request( data_dict )
                result_status = result.status_code
                logging.getLogger().debug( f"Request returned status: {result_status}, reason: '{result.text}'" )
                if result_status == 200:
                    record_id = data_dict[ 'listing_id' ]
                    quantity = data_dict[ 'message' ][ 'quantity' ]

                    logging.getLogger().debug( f"Updating listing with record id '{record_id}' "
                                               f"with quantity {quantity}"
                    )
                    self.conn.update_listing_stock( record_id,
                                                    quantity
                    )
                    logging.getLogger().debug( "Sending success response back to client." )
                    conn.sendall( "SUCCESS\n".encode( 'utf-8' ) )
                else:
                    logging.getLogger().debug( "Sending failure response back to client." )
                    conn.sendall( "FAILURE\n".encode( 'utf-8' ) )

                logging.getLogger().debug( f"TIMESTAMP Sending response back to client: {time.time()}" )

                logging.getLogger().debug( "Sent response back to client." )

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
        self.cond = threading.Condition()

        self._client = mqtt.Client()
        self.message_buffer = None


        def on_connect( client, userdata, flags, rc, channels = None ):
            """
            Callback used by Paho MQTT upon connection 
            with the MQTT broker.
            """
            logging.getLogger().debug( "Connected with result code " + str( rc )  )

            client.subscribe( 'responses' )
            for chan in channels:
                client.subscribe( chan )

        def on_message( client, userdata, msg ):
            """
            Callback used by Paho MQTT upon reception of a message 
            from the MQTT broker.
            """

            logging.getLogger().debug( "Received a message!" )
            # get the method name from the URL 

            logging.getLogger().debug( f"Message topic: {msg.topic}")
            # logging.getLogger().debug( f"Data: {int.from_bytes( msg.msg, byteorder = 'big' )}" )
            if msg.payload is None:
                logging.getLogger().debug( "Message received is None!" )
            self.message_buffer = msg.payload
            with self.cond:
                self.cond.notify()
            logging.getLogger().debug( f"Message data: {self.message_buffer}" )

            ## Note: topic is of the form /posts/client_x, where x is the ID for the client


        self.on_connect = lambda client, userdata, flags, rc: \
                          on_connect( client, userdata, flags, rc, channels = self._channels )
        self.on_message = on_message

    def get_client_ip( self ):
        return self.client_ip

    def get_client_port( self ):
        return self.client_port

    def decode_data( self, encoded_message ):
        logging.getLogger().warning( "Uh oh! This implementation of 'decode_data' is empty! "
                                     "Are you sure you meant to call it?"
        )
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

        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            # bind to the socket 
            sock.bind( ( self.get_client_ip(), self.get_client_port() ) )
            logging.getLogger().debug( "Creating a socket to listen to incoming "
                                       f"requests on IP: {self.client_ip}, "
                                       f"port: {self.client_port}"
            )


            # listen
            sock.listen() 


            while True:
                # accept a connection
                conn, addr = sock.accept()

                with conn:
                    # receive message
                    host, port = conn.getpeername()
                    logging.getLogger().debug( "Received a client connection with "
                                               f"IP: {host}, on port: {port}. "
                    )


                    data = conn.recv( 4096 )

                    if not data:
                        logging.getLogger().error( "ERROR: Data received is empty!" )
                        break

                    data_str = binascii.hexlify( bytearray( data ) )
                    logging.getLogger().debug( f"Data received from client: {data_str}" )
                    topic = "posts/1"
                    result = self.do_request( data, topic )

                    logging.getLogger().debug( f"Waiting for response." )
                    with self.cond:
                        self.cond.wait_for( lambda: self.message_buffer is not None )


                    logging.getLogger().debug( "Response received, "
                                               f"sending '{self.message_buffer}' to client."
                    )
                    conn.sendall( self.message_buffer )
                    self.message_buffer = None
