
class OAuth1Credentials:
    def __init__( self,
                  api_key      = "",
                  api_secret   = "",
                  access_token = "",
                  acces_secret = ""
                ):
        self.client_key       = api_key
        self.client_secret    = api_secret
        self.resource_owner_key  = access_token
        self.resource_owner_secret = access_secret

    def get_from_file( self, fname ):
        """
        Parse oauth credentials from a file.
        The file must be tab-delimited with two columns,
        one for each item used in the authentication 
        process. The first column must have names that correspond
        to the items needed for authentication, e.g.:
          - client_key             
          - client_secret
          - resource_owner_token
          - resource_owner_secret       
        """
        with open( fname, 'r' ) as of:
            for line in of:
                line = line.strip()
                spl = line.split( '\t' )

                # TODO: this is dangerous, find better way
                setattr( self, spl[ 0 ], spl[ 1 ] )

    def set_client_info( self, client_key, client_secret ):
        """
        Set the client information (token and secret) for 
        this class
        
        Args:
          client_token: the client token to set.
          acccess_secret: the client secret to set.
        """

        self.client_key = client_key
        self.client_secret = client_secret

    def set_resource_owner_info( self, resource_owner_token, resource_owner_secret ):
        """
        Set the resource_owner information (token and secret) for 
        this class
        
        Args:
          resource_owner_token: the resource_owner token to set.
          acccess_secret: the resource_owner secret to set.
        """
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret

    def as_dict( self ):
        """
        Return the dictionary representation of 
        this object. 

        Returns:
          Dictionary representing this object,
          for example:
           { 'resource_owner_secret': 'adfsdfsdflflslflds' }
        
        """
        return vars( self )
