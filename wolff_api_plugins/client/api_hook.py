
class APIHook:
    def __init__( self, base_url = "",
                  methods = None
                ):
        self.base_url = base_url
        self.methods = methods if methods else list()

    def get_methods( self ):
        return self.methods

    def add_method( self, method ):
        self.methods.append( method )

    def add_methods( self, methods ):
        self.methods += methods

    def get_url( self ):
        return self.base_url

    def set_url( self, url ):
        self.base_url = url

    def get_complete_url( self, method ):
        return f'{self.get_url()}/{method.get_uri()}/'

class APIMethod:
    """
    Represents the data needed to 
    call an API method. Has a uri for 
    locating the resource necessary and 
    a set of arguments that are included 
    in the call of an API Method.
    """
    def __init__( self, uri = "", args = None, http_method = "", name = "" ):
        self.uri = uri
        self.args = args if args else dict()
        self.http_method = http_method
        self.name = name

    def get_http_method( self ):
        """
        Get the HTTP method this 
        APIMethod uses (GET, POST, etc.)
        """
        return self.http_method

    def get_uri( self ):
        return self.uri

    def args_as_dict( self ):
        return self.get_args()

    def get_args( self ):
        return self.args

    def set_http_method( self, method ):
        self.http_method = method

    def set_uri( self, uri ):
        self.uri = uri

    def add_arg( self, arg ):
        self.args[ arg ] = ''

    def set_args( self, args ):
        self.args.update( args )

    def set_name( self, name ):
        self.name = name

    def get_name( self ):
        return self.name
