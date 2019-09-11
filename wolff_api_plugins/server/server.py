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
        pass

    def set_ip( self, ip ):
        self.ip = ip

    def set_port( self, port ):
        self.port = port

    def get_port( self ):
        return self.port

    def start( self ):
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as sock:
            # bind to the socket 

            # listen

            # accept a connection

            # while true
                # receive message

                # get credentials and URL from the message
                # get the method name from the URL 

                # get the params from the message

                # create the OAuth session from our credentials

                # send the message 
            pass

