#!/usr/bin/env python3
import wolff_api_plugins.client.api_hook as hook
import wolff_api_plugins.client.client as client
import wolff_api_plugins.client.server_connection as conn
import wolff_api_plugins.client.message as message
import json
import sys
import time
import logging
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
    argp.add_argument( '--log_file', help = "The name of the file to write log "
                       "information to.", default = "simple_etsy_client.log"
                     )
    argp.add_argument( '--output_submitted', help = "The name of the file to write information about "
                       "the listings that have been created. This will be used by the script that updates "
                       "listings.", default = "submitted_listings.json"
                     )

    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]


    cli_args = argp.parse_args()

    logging.basicConfig( level = logging.NOTSET,
                         format = '%(asctime)s [%(levelname)-5.5s] %(message)s', 
                         handlers = [
                             logging.FileHandler( cli_args.log_file ),
                             logging.StreamHandler( sys.stdout )
                         ]
    )

    logging.getLogger().debug( "Parsed arguments with values: \n"
                               f"--ip: {cli_args.ip}\n"
                               f"--port: {cli_args.port}\n"
                               f"--log_file: {cli_args.log_file}\n"
    )



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


    start_time = time.time()

    logging.getLogger().info( f"TIMESTAMP Beginning of request: {start_time}" )

    etsy_client = client.Client( connection = connect, endpoint = etsy_hook,
                                 message_type = message.EtsyMessage
                                )
    etsy_client.specialize()

    # save args to a dict so we can write to a file to update later
    request_args = { 'quantity': 2, 'title': "title_1",
                     'description': "desc_1",
                     'price': 1.11, 'who_made': 'i_did', 'is_supply': True,
                     'when_made': 'made_to_order', 'shipping_template_id': 84634415230
    }
    resp = etsy_client.create_listing( **request_args )
    resp_decoded = int.from_bytes( resp, 'big' )

    end_time = time.time()
    logging.getLogger().info( f"TIMESTAMP End of request: {end_time}" )
    logging.getLogger().info( f"Elapsed time: {end_time - start_time}" )
    logging.getLogger().debug( f"ID received from server: {resp_decoded}" )

    logging.getLogger().debug( f"Opening {cli_args.output_submitted} to write listing record" )

    with open( cli_args.output_submitted, 'a' ) as output_file:
        request_args[ 'listing_id' ] = resp_decoded
        to_write = json.dumps( request_args )

        logging.getLogger().debug( f"String that will be written to file: {to_write}" )
        output_file.write( f"{to_write}\n" )
        logging.getLogger().debug( f"Wrote record to file" )
        


if __name__ == '__main__':
    main()
