import connection

class Client:
    """ 
    A client sends messages to a server, and receives them.
    """
    def __init__( self, connection = None ):
        self._connection = connection

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

