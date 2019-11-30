from enum import Enum

class Applications( Enum ):
    ETSY = 1

class DecoderFactory:
    """
    Returns a decoder based upon the service
    specified in the encoded method
    
    @param message the message for which a decoder
           is reduced
    @returns A decoder that can decode the message
    """
    def get_decoder( self, message ):
        decoder = self.get_service( message )
        return decoder

    def get_service( self, message ):
        """
        Get a service-specific decoder.
        """
        application = message[ 0 ]

        if application == Applications.ETSY.value:
            return EtsyDecoder()

class EtsyDecoder:
    """
    A class that is capable of decoding
    messages for the Etsy service.
    """
    class Services( Enum ):
        """
        An enum listing the services that are 
        currently available.
        """
        CREATE_LISTING = 1

        @classmethod
        def has_value( cls, value ):
            """
            Determine if this enum has a value.
            We use this to check if a method is supported 
            by the decoder. 
            
            @param value The value to check for
            @returns True if this class has value, 
                     false otherwise.
            """
            return value in cls._value2member_map_

    def __init__( self ):
        """
        A map associating bytes with titles.
        """
        self.title_map       = { 0x01: 'title_1' }
        self.description_map = { 0x02: 'desc_1' }
        self.who_made_map    = { 0x01: 'i_did',
                                 0x02: 'collective',
                                 0x03: 'someone_else'
                               }
        self.when_made_map   = { 0x01: 'made_to_order',
                                 0x02: '2010_2019',
                                 0x03: '2000_2009',
                                 0x04: 'before_2000',
                                 0x05: '1990s',
                                 0x06: '1980s',
                                 0x07: '1970s',
                                 0x08: '1960s'
                               }


    def is_etsy_message( self, message ):
        return EtsyDecoder.Services.has_value( message[ 0 ] )

    def get_service_decoder( self, message ):
        """
        Get a method that will decode messages for a certain service.
        """
        if message[ 1 ] == EtsyDecoder.Services.CREATE_LISTING.value:
            return self._decode_create_listing_message

    def decode( self, message ):
        assert( self.is_etsy_message( message ) )

        decode_fn = self.get_service_decoder( message )

        return decode_fn( message )

    def _get_price( self, price_bytes ):
        """
        Get the price of the product from 
        a list of two bytes representing the price of the product.
        @param price_bytes Two bytes of an encoded method 
               that represent the price portion.
        @returns the price of the product
        """
        integral_byte   = price_bytes[ 0 ]

        # mask off first 4 bits
        fractional_byte = price_bytes[ 1 ] & 0x0F
        fractional_price = int( fractional_byte ) / 100.0

        integral_second_half = ( price_bytes[ 1 ] & 0xF0 ) >> 4

        integral_price = ( int( integral_byte ) * 16 ) + int( integral_second_half )

        price = integral_price + fractional_price

        return price



    def _decode_create_listing_message( self, message ):
        """
        Decode a message that is for creating an Etsy listing.
        @param message an encoded message
        @returns A dictionary containing the arguments for create_listing
                 and their values.
        """
        decoded_message = dict()
        output = dict()

        output[ 'api_details' ] = ( 'etsy', 'create_listing' )

        title = message[ 2 ]
        decoded_message[ 'title' ] = self.title_map[ title ]

        description = message[ 3 ]
        decoded_message[ 'description' ] = self.description_map[ description ]

        quantity = message[ 4 ]
        decoded_message[ 'quantity' ] = quantity

        price = self._get_price( message[ 5:7 ] )
        decoded_message[ 'price' ] = price

        who_made = message[ 7 ] & 0b00001111
        decoded_message[ 'who_made' ] = self.who_made_map[ who_made ]

        when_made_mask = 0b01110000
        when_made = ( message[ 7 ] & when_made_mask ) >> 4
        decoded_message[ 'when_made' ] = self.when_made_map[ when_made ]

        is_supply = ( message[ 7 ] & 0b10000000 ) >> 7
        decoded_message[ 'is_supply' ] = is_supply

        # stp = shipping_template_part
        stp1 = message[ 8 ]
        stp2 = message[ 9 ]
        stp3 = message[ 10 ]
        stp4 = message[ 11 ]
        stp5 = message[ 12 ]

        shipping_template_id = ( stp1 * ( 256 ** 4 ) ) + \
                               ( stp2 * ( 256 ** 3 ) ) + \
                               ( stp3 * ( 256 ** 2 ) ) + \
                               ( stp4 * ( 256 ** 1 ) ) + \
                               ( stp5 * ( 256 ** 0 ) )
        decoded_message[ 'shipping_template_id' ] = shipping_template_id

        output[ 'message' ] = decoded_message

        return output
        
