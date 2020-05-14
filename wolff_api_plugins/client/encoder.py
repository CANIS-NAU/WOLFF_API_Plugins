from enum import Enum

# TODO: Applications is duplicated between encoder/decoder
class Applications( Enum ):
    ETSY = 1

class EtsyEncoder:
    """
    An EtsyDecode handles the details required for 
    the encoding and decoding of Etsy message, including 
    the maps necessary for mapping strings -> byte values in 
    the encoded message
    """
    class Services( Enum ):
        """
        An enum detailing the services that are 
        currently supported by the Encoder
        """
        CREATE_LISTING = 1

    def __init__( self ):

        # TODO: these maps should be placed in a 'create listing class'
        # containing maps and their inverses
        """
        The title map, specifying how titles should be 
        mapped to byte values.
        These can be expanded until there are 0xFF values mapped.
        """
        self.title_map       = { 'title_1': 0x01 }

        """
        The description map, specifying how descriptions should be 
        mapped to byte values.
        These can be expanded until there are 0xFF values mapped.
        """
        self.description_map = { 'desc_1': 0x02 }

        """
        Maps values for create_listing's 'who_made' enum
        """
        self.who_made_map    = { 'i_did': 0x01,
                                 'collective': 0x02,
                                 'someone_else': 0x03
                               }

        """
        Maps values for create_listing's 'when_made' enum
        """
        self.when_made_map   = { 'made_to_order': 0x01,
                                 '2010_2019': 0x02,
                                 '2000_2009': 0x03,
                                 'before_2000': 0x04,
                                 '1990s': 0x05,
                                 '1980s': 0x06,
                                 '1970s': 0x07,
                                 '1960s': 0x08
                                 
                               }


    def encode( self, etsy_data ):
        """
        Encode a dictionary containing etsy data.
        
        @param etsy_data A dictionary containing the data
               necessary to perform a request to an Etsy method.
               The dictionary should be of the form:

               { 'service': 'etsy', 
                 'method': {'params': {}, 'name': '' 
                           },
                 'client_id': ''
               }
        
              Where 'name' is the name of the method, 
              such as 'create_listing', and 'params' contains 
              a dictionary of parameters and their values for 
              the method.
        
        @returns A method that is capable of encoding either etsy_data,
                 or a dictionary of the same type
        """
        encoding_method = self._get_encoding_method( etsy_data )

        return encoding_method( etsy_data[ 'method' ][ 'params' ] )

    def _get_encoding_method( self, etsy_data ):
        if etsy_data[ 'method' ][ 'name' ] == 'create_listing':
            return self._encode_create_listing

    def _encode_create_listing( self, create_listing_data ):
        """
        Encode a create listing request. Encoded message 
        specification can be found here: 
         https://github.com/CANIS-NAU/WOLFF_Protocol/wiki/
        
        @param create_listing_data a dictionary containing the parameters 
               required to create an etsy listing and their values. This 
               dictionary should be of the form: 
        
        { 'quantity': 1, 'title': 'title_1', 'description': 'desc_1', 
          'price': 16.04, 'who_made': 'collective', 'is_supply': True, 
          'when_made': '1990s', 'shipping_template_id': 76575991147
        }
        
        @returns the encoded message
             
        """
        payload = bytearray( [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] )
        payload[ 0 ] |= Applications.ETSY.value
        payload[ 1 ] |= EtsyEncoder.Services.CREATE_LISTING.value

        title = create_listing_data[ 'title' ]
        payload[ 2 ] |= self.title_map[ title ]

        description = create_listing_data[ 'description' ]
        payload[ 3 ] |= self.description_map[ description ]

        quantity = create_listing_data[ 'quantity' ]
        assert( quantity > 0 and quantity < 256 )
        payload[ 4 ] |= quantity

        price = create_listing_data[ 'price' ]
        price_integral = int( price )
        price_fraction = int( ( price * 100 ) % 100 )

        assert( price_integral < 4095 )
        assert( 0 <= price_fraction and price_fraction < 16 )

        integral_left_8digits = price_integral // 16
        integral_right_4digits = price_integral % 16
        price_fraction_digits = price_fraction

        payload[ 5 ] |= integral_left_8digits

        integral_mask = 0b11110000
        fraction_mask = 0b00001111

        payload[ 6 ] |= ( integral_mask & ( integral_right_4digits << 4 ) ) \
                       | ( fraction_mask & price_fraction_digits )

        # who_made, when_made, is_supply
        wm_whm_is_byte = 0x00
        wm_whm_is_byte = 0b10000000 & ( create_listing_data[ 'is_supply' ] << 7 )

        when_made = self.when_made_map[ create_listing_data[ 'when_made' ] ]
        wm_whm_is_byte |= ( ( when_made << 4 ) & 0b01110000 )

        who_made = self.who_made_map[ create_listing_data[ 'who_made' ] ]
        wm_whm_is_byte |=  who_made

        payload[ 7 ] |= wm_whm_is_byte

        shipping_template_id = int( create_listing_data[ 'shipping_template_id' ] )

        stp5 = shipping_template_id % 256
        shipping_template_id //= 256

        stp4 = shipping_template_id % 256
        shipping_template_id //= 256

        stp3 = shipping_template_id % 256
        shipping_template_id //= 256

        stp2 = shipping_template_id % 256
        shipping_template_id //= 256

        stp1 = shipping_template_id

        payload[ 8 ]  = stp1
        payload[ 9 ]  = stp2
        payload[ 10 ] = stp3
        payload[ 11 ] = stp4
        payload[ 12 ] = stp5

        print( ''.join( [ "%02X " %  x for x in payload ] ).strip() )
        return payload



