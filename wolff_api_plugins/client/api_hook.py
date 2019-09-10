
class APIHook:
    def __init__( self, base_url = "",
                  
                ):
        pass

    def get_methods( self ):
        pass

    def add_method( self, method ):
        pass

    def add_methods( self, methods ):
        pass

class APIMethod:
    """
    Represents the data needed to 
    call an API method. Has a uri for 
    locating the resource necessary and 
    a set of arguments that are included 
    in the call of an API Method.
    """
    def __init__( self, uri = "", args = None, http_method = "" ):
        self.uri = uri
        self.args = args if args else None
        self.http_method = http_method

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

    def set_http_method( self, method ):
        self.http_method = method

    def set_uri( self, uri ):
        self.uri = uri

    def add_arg( self, arg ):
        if self.args is None:
            self.args = dict()
        self.args[ arg ] = ''

    def set_args( self, args ):
        if self.args is None:
            self.args = dict()

        self.args.update( args )
