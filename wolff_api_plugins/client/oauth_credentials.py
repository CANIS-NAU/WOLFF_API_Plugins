
class OAuth1Credentials:
    def __init__( self,
                  api_key      = "",
                  api_secret   = "",
                  access_token = "",
                  acces_secret = ""
                ):
        self.api_key       = api_key
        self.api_secret    = api_secret
        self.access_token  = access_token
        self.access_secret = access_secret

    def get_from_file( self, fname ):
        """
        Parse oauth credentials from a file.
        The file must be tab-delimited with two columns,
        one for each item used in the authentication 
        process. The first column must have names that correspond
        to the items needed for authentication, e.g.:
          - api_key             
          - api_secret
          - access_token
          - access_secret       
        """
        pass

    def set_api_info( self, api_key, api_secret ):
        """
        Set the api information (token and secret) for 
        this class
        
        Args:
          api_token: the api token to set.
          acccess_secret: the api secret to set.
        """

        self.api_key = api_key
        self.api_secret = api_secret

    def set_access_info( self, access_token, access_secret ):
        """
        Set the access information (token and secret) for 
        this class
        
        Args:
          access_token: the access token to set.
          acccess_secret: the access secret to set.
        """
        self.access_key = access_key
        self.access_secret = access_secret

    def as_dict( self ):
        """
        Return the dictionary representation of 
        this object. 

        Returns:
          Dictionary representing this object,
          for example:
           { 'oauth_token_secret': 'adfsdfsdflflslflds' }
        
        """
        return vars( self )
