#!/usr/bin/env python3
import wolff_api_plugins.client.api_hook as hook
import wolff_api_plugins.client.client as client
import wolff_api_plugins.client.server_connection as conn
import wolff_api_plugins.client.oauth_credentials as cred
import wolff_api_plugins.client.message
import time

def main():

    args = { 'quantity': 0, 'title': '', 'description': '',
                'price': 0, 'who_made': '', 'is_supply': True, 'when_made': '',
                'shipping_template_id': 0
           }

    create_listing = hook.APIMethod( uri = 'listings',
                                     args = args,
                                     http_method = 'post',
                                     name = 'createListing'
                                   )


    connect = conn.MQTTServerConnection( ip = "127.0.0.1",
                                         port = 1883
                                      )
    auth = cred.OAuth1Credentials()
    auth.get_from_file( 'etsy_keys.tsv' )

    args = { 'user_id': '' }

    gubo = hook.APIMethod( uri = '/users/:user_id/billing/overview',
                           args = args, http_method = 'get', name = 'gubo'
                         )

    etsy_hook = hook.APIHook( base_url = 'https://openapi.etsy.com/v2/',
                              methods = [ create_listing, gubo ]
                            )


    etsy_client = client.Client( connection = connect, endpoint = etsy_hook,
                                 credentials = auth,
                                 message_type = message.EtsyMessage
                                )
    etsy_client.specialize()

    time.sleep( 10 )
    etsy_client.createListing( quantity = 1, title = "title_1",
                               description = "desc_1",
                               price = 0.45, who_made = 'i_did', is_supply = True,
                               when_made = 'made_to_order', shipping_template_id = 76575991147
    )

    time.sleep( 35 ) 
    etsy_client.gubo( user_id = 'ezk6e2q6' )

    # response can take a little bit
    # etsy_client.get_connection().subscribe_to( 'responses/client_1' )
    time.sleep( 35 ) 
    result = etsy_client.get_connection().check_for_messages()
    print( result )


if __name__ == '__main__':
    main()
