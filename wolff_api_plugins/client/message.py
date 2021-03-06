import json
from . import encoder

"""
Represents a message that can be sent from a client to a server (and vice-versa).
It is expected that the str method will be called by the client to transform this 
message into a representable form before being sent.
"""
class Message:
    def __init__( self, data ):
        """
        Initialize a message with data.
        Args:
          data: the data this message contains.
                Should be a dictionary that is 
                transformable by 'json.dumps'
        """
        self._data = data

    def get_data( self ):
        """
        Get the data that is  
        """
        return self._data

    def __str__( self ):
        return json.dumps( self._data )

    def encode( self ):
        return str( self ).encode()
        


class EtsyMessage( Message ):
    def __init__( self, data ):
        super().__init__( data )
        self._encoder = encoder.EtsyEncoder()

    def __str__( self ):
        return self.get_data()

    def encode( self ):
        return self._encoder.encode( self.get_data() )
