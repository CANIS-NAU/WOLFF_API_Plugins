from .message import Message as Message

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
                  credentials = None,
                  client_id = 1
                ):
        self._connection  = connection
        self._endpoint    = endpoint
        self._credentials = credentials
        self._id = client_id

    def set_connection( self, server_connection ):
        """
        Set this client's server connection. The client 
        will use this connection for sending any messages.
        
        Args: 
            server_connection: A server connection. This connection
            will be used to send any messages that the client sends.
        """
        # set the connection to the passed argument
        self._connection = server_connection

    def get_id( self ):
        return f'client_{self._id}'

    def set_id( self, id ):
        self._id = id
    
    def get_connection( self ):
        """
        Get the connection stored by this client. 

        Returns: 
          The client's connection, or None if 
          the client does not currently have a 
          connection.
        
        """
        # return this object's server connection
        return self._connection

    def has_connection( self ):
        """
        Determine whether the client has a connection. 

        Returns:
           True if the client has a connection, False otherwise.
        """
        return self._connection != None

    """
    Set the client's endpoint. 
    """
    def set_endpoint( self, endpoint ):
        self._endpoint = endpoint

    """
    Get the endpoint this client is able to 
    communicate with. The client uses its connection 
    to send messages to the endpoint.

    Returns:
      The endpoint associated with this client.
    """
    def get_endpoint( self ):
        return self._endpoint

    """
    Set this objects credentials.

    Args:
      credential: The new credential for this object
    """
    def set_credentials( self, credential ):
        self._credentials = credential

    """
    Return this object's credentials.
    """
    def get_credentials( self ):
        return self._credentials


    """
    Specialize this class, adding all of its 
    endpoint methods to itself. 
    This allows a generic 'Client' to 
    become an etsy client. Instead of calling:
    client.get_endpoint().method(), 
    client.method() can be called. 
    """
    def specialize( self ):

        # for each method in api endpoint
        for method in self._endpoint.get_methods():
            self._specialize_with( self._endpoint, method )

    """
    Specialize the client with a certain method.
    Adds the method to the client, allowing 
    client.method( args ) to be called.

    Params:
      method: APIMethod (or equivalent) to add to the class.
    """
    def _specialize_with( self, endpoint, method ):

        """
        A prototype for the new method to add 
        to our client. The actual method that is defined will 
        already have uri and http_method defined by the method 
        passed to this function.
        
        """
        def new_method( self,
                        base_url = "",
                        http_method = "",
                        **kwargs
                      ):
            m_args = dict()

            http_method.set_args( kwargs )

            m_args[ 'url' ] = base_url + http_method.get_uri( substitute = True )
            m_args[ 'credentials' ] = self.get_credentials().as_dict()
            m_args[ 'method' ] = dict()
            m_args[ 'method' ][ 'params' ] = http_method.args_as_dict()
            m_args[ 'method' ][ 'http_method' ] = http_method.get_http_method()
            m_args[ 'client_id' ] = self.get_id()

            ret = self.get_connection().send( Message( m_args ) )

            http_method.clear_args()

            return ret

        url = endpoint.get_url()
        http_method = method.get_http_method()
        args = method.args_as_dict()

        method_name = method.get_name()

        fn = lambda **kwargs: new_method( self, base_url = url,
                                          http_method = method,
                                          **kwargs
                                        )
        
        setattr( self, method_name, fn )
