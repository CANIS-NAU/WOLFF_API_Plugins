

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
