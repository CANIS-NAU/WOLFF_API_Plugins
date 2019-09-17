from requests_oauthlib import OAuth1Session
import socket
import json

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
                        data_dict = json.loads( data.decode( 'ascii' ) )

                        print( data_dict )

                        request_handler = self.get_request_handler( data_dict[ 'credentials' ] )

                        # get the params from the message
                        # create the OAuth session from our credentials
                        # send the message 
                        if data_dict[ 'method' ] == 'get':
                            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ] )
                        else:
                            result = getattr( request_handler, data_dict[ 'method' ][ 'http_method' ] )( data_dict[ 'url' ], data = data_dict[ 'method' ][ 'params' ] )
                        conn.sendall( result.content )





    def get_request_handler( self, credentials ):
        return OAuth1Session( **credentials )

