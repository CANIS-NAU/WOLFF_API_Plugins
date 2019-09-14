import re

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

        # Matches strings of the form:
        #/whatever/you/want/:param/whatever
        # :param is captured
        self.uri_re = r"\S*/(:\S+)/\S*"

    def get_http_method( self ):
        """
        Get the HTTP method this 
        APIMethod uses (GET, POST, etc.)
        """
        return self.http_method

    def get_uri( self, substitute = True ):
        """
        Get the method's URI. If there are substitutable
        parameters (parameters that appear in the URI 
        in the form: /:param_name/ will be substituted if 
        'substitue' is set to true. So if user_id is an argument
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

        if substitue and self._uri_is_substitutable():
            pass
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

    def _uri_is_substitutable( self ):
        """
        Determine if this uri has a parameter 
        that can be substituted by a user-defined value. 
        """
        return re.search( self.uri_re, self.uri) 
