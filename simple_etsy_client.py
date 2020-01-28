#!/usr/bin/env python3
import wolff_api_plugins.client.api_hook as hook
import wolff_api_plugins.client.client as client
import wolff_api_plugins.client.server_connection as conn
import wolff_api_plugins.client.message as message
import time
import argparse

def main():

    argp = argparse.ArgumentParser()

    argp.add_argument( '--ip', default = "127.0.0.1", 
                       help = 'The ip to look for a server on.' 
                     )
    argp.add_argument( '--port', default = 5555, 
                       help = "The port to bind to.",
                       type = int
                     )

    cli_args = argp.parse_args()

    args = { 'quantity': 0, 'title': '', 'description': '',
                'price': 0, 'who_made': '', 'is_supply': True, 'when_made': '',
                'shipping_template_id': 0
           }

    create_listing = hook.APIMethod( uri = 'listings',
                                     args = args,
                                     http_method = 'post',
                                     name = 'create_listing'
                                   )


    connect = conn.TCPServerConnection( ip = cli_args.ip,
                                         port = cli_args.port
                                      )
    args = { 'user_id': '' }

    # 'gubo' = getUserBillingOverview, not currently implemented
    # with encoding/decoding
    # gubo = hook.APIMethod( uri = '/users/:user_id/billing/overview',
    #                        args = args, http_method = 'get', name = 'gubo'
    #                      )

    etsy_hook = hook.APIHook( service = 'etsy',
                              methods = [ create_listing ]
                            )


    etsy_client = client.Client( connection = connect, endpoint = etsy_hook,
                                 message_type = message.EtsyMessage
                                )
    etsy_client.specialize()

    resp = etsy_client.create_listing( quantity = 1, title = "title_1",
            description = "desc_1",
            price = 16.04, who_made = 'collective', is_supply = True,
            when_made = '1990s', shipping_template_id = 84634415230
            )


    # response can take a little bit
    # etsy_client.get_connection().subscribe_to( 'responses/client_1' )
    # result = etsy_client.get_connection().check_for_messages()
    print( resp )


if __name__ == '__main__':
    main()
