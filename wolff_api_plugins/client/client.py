import connection

class Client:
    """ 
    A client sends messages to a server, and receives them.
    Clients are specialized by specifying connection, endpoint, and
    credentials. Connection allows clients to send messages over different 
    backbones, endpoint defines what type of client this is (Etsy, Weebly, etc.),
    and credentials (Typicall Oauth) identify a user using a service. 
    """
    def __init__( self,
                  connection = None,
                  endpoint = None,
                  credentials = None
                ):
        self._connection = connection
        self._endpoint   = endpoint
        self._credentials      = credentials

    def set_connection( self, server_connection ):
        """
        Set this client's server connection. The client 
        will use this connection for sending any messages.
        
        Args: 
            server_connection: A server connection. This connection
            will be used to send any messages that the client sends.
        """
        # set the connection to the passed argument
        pass

    def get_connection( self ):
        """
        Get the connection stored by this client. 

        Returns: 
          The client's connection, or None if 
          the client does not currently have a 
          connection.
        
        """
        # return this object's server connection
        pass

    def has_connection( self ):
        """
        Determine whether the client has a connection. 

        Returns:
           True if the client has a connection, False otherwise.
        """
        # return whethe the client currently has a connection. 
        pass

    """
    Set the client's endpoint. 
    """
    def set_endpoint( self, endpoint ):
        pass

    """
    Get the endpoint this client is able to 
    communicate with. The client uses its connection 
    to send messages to the endpoint.

    Returns:
      The endpoint associated with this client.
    """
    def get_endpoint( self ):
        pass

    """
    Set this objects credentials.

    Args:
      credential: The new credential for this object
    """
    def set_credentials( self, credential ):
        pass

    """
    Return this object's credentials.
    """
    def get_credentials( self ):
        pass

