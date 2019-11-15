import re

class APIHook:
    def __init__( self, service = "",
                  methods = None
                ):
        self.service = service
        self.methods = methods if methods else list()

    def get_methods( self ):
        return self.methods

    def add_method( self, method ):
        self.methods.append( method )

    def add_methods( self, methods ):
        self.methods += methods

    def get_service( self ):
        return self.service

    def set_service( self, service ):
        self.service = service + '/'

    # deprecated with client/server changes
    # def get_complete_url( self, method, substitute = False ):
    #     return f'{self.get_url()}/{method.get_uri( substitute = substitute )}/'

class APIMethod:
    """
    Represents the data needed to 
    call an API method. Has a uri for 
    locating the resource necessary and 
    a set of arguments that are included 
    in the call of an API Method.
    """
    def __init__( self, method = "", args = None, http_method = "", name = "", uri = "" ):
        self.uri = uri
        self.args = args if args else dict()
        self.http_method = http_method
        self.name = name
        self.method = method

        self.substitutable_args = set()

        # Matches strings of the form:
        #/whatever/you/want/:param/whatever
        # param is captured
        self.uri_re = re.compile( ":((?:[a-zA-Z]|_)+)" )

    def get_method( self ):
        return self.method 

    def set_method( self, new_method ):
        self.method = method
        
    def set_parameter_re( self, new_re ):
        self.uri_re = new_re

    def get_http_method( self ):
        """
        Get the HTTP method this 
        APIMethod uses (GET, POST, etc.)
        """
        return self.http_method

    def get_uri_replacement( self, match ):
        self.substitutable_args.add( match.group( 1 ) )
        return self.args[ match.group( 1 ) ]

    def get_uri( self, substitute = True ):
        """
        Get the method's URI. If there are substitutable
        parameters (parameters that appear in the URI 
        in the form: /:param_name/ will be substituted if 
        'substitute' is set to true. So if user_id is an argument
        to a method whose URI looks like:
        '/:user_id/', then the value of user_id wil take place
        of the item between the slashes.

        Args:
           - substitute: Include if URI substitution as explained
             above should be done. This only happens if the 
             value in self.args_as_dict() is set. If false, the 
             unchanged value will be used.
        
        Raises:
          - ValueError if substitute is true but there is no
            valid substitution to make in the args.
        
        Returns:
          - The string URI of this method
        """

        uri = self.uri

        if substitute and self._uri_is_substitutable():
            try:
                uri = self.uri_re.sub( self.get_uri_replacement, self.uri )
            except KeyError:
                raise ValueError( "Substitutable argument for "
                                  "URI has not been set."
                                )
        return uri + '/'

    def args_as_dict( self ):
        ret = self.get_args().copy()

        for arg in self.substitutable_args:
            del ret[ arg ]
        return ret

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

    def set_args( self, p_dict ):
        try:
            for arg, value in p_dict.items():
                if arg not in self.args:
                    raise KeyError()

                self.args[ arg.lower() ] = value
        except KeyError:
            raise TypeError( f"{self.get_name()} got an "
                             f"unexpected keyword argument '{arg}'."
                           )

    def clear_args( self ):
        for arg, value in self.args.items():
            self.args[ arg ] = ""
            
    def get_name( self ):
        return self.name

    def _uri_is_substitutable( self ):
        """
        Determine if this uri has a parameter 
        that can be substituted by a user-defined value. 
        """
        return re.search( self.uri_re, self.uri) 
