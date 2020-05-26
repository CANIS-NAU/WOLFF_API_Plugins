#!/usr/bin/env python3
import logging
import json
import time
import binascii
import socket
import time
import sys
import argparse


def main():

    argp = argparse.ArgumentParser( description = "Script to update an existing listing." ) 
    argp.add_argument( '--ip', help = "IP of the Proxy server that an update request will be sent to.", required = True )
    argp.add_argument( '--port', help = "Port of the proxy server's update_listing service.", type = int, required = True )
    argp.add_argument( '--listing_id', help = "Integer ID of the listing to check for an update to. This should be the ID "
                       "returned by the proxy server when the listing was originally posted.", type = int,
                       required = True 
                     )
    argp.add_argument( '--log_file', help = "The name of the file to write log "
                       "information to.", default = "check_product_purchase.log"
                     )

    args = argp.parse_args()

    logging.basicConfig( level = logging.NOTSET,
                         format = '%(asctime)s [%(levelname)-5.5s] %(message)s', 
                         handlers = [
                             logging.FileHandler( args.log_file ),
                             logging.StreamHandler( sys.stdout )
                         ]
    )

    logging.getLogger().debug( "Parsed arguments with values: \n"
                               f"--ip: {args.ip}\n"
                               f"--port: {args.port}\n"
                               f"--listing_id: {args.listing_id}\n"
                               f"--log_file: {args.log_file}\n"
    )

    start_time = time.time()

    logging.getLogger().info( "TIMESTAMP beginning of check_product_purchase: {start_time}" )

    to_hex = lambda x: str( binascii.hexlify( x ) )

    message = bytearray( 2 )
    message[ 0 ] = 0x01
    message[ 1 ] = 0x02

    logging.getLogger().debug( f"First 2 bytes of message: {to_hex( message )}" )

    listing_id_bytes = args.listing_id.to_bytes( 4, byteorder = 'big' )

    logging.getLogger().debug( f"Listing ID: {args.listing_id}, as bytes: {to_hex( listing_id_bytes )}" )

    message += listing_id_bytes

    logging.getLogger().debug( f"Message after adding the ID: {to_hex( message ) }" )

    message += bytearray( 7 )

    logging.getLogger().debug( f"Message after adding padding: {to_hex( message ) }" )
    logging.getLogger().debug( f"Message length: {len( message )}" )


    logging.getLogger().debug( f"Attempting to connect to server at IP: {args.ip}, Port: {args.port}" )
    with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as s:
        s.connect( ( args.ip, args.port ) )

        logging.getLogger().debug( f"Successfully connected to server." )
        logging.getLogger().debug( f"Sending request to server." )

        s.sendall( message )

        logging.getLogger().debug( f"Data succesfully sent, waiting on response..." )

        data = s.recv( 1024 )

        logging.getLogger().debug( f"Response received from server: {to_hex( data )}" )


        response_region = data[ 2:6 ]
        num_purchased = int.from_bytes( response_region, byteorder = 'big' )
        logging.getLogger().debug( f"Number of items that have been purchased: {num_purchased}" )
        
    end_time = time.time()

    logging.getLogger().info( "TIMESTAMP end of check_product_purchase: {end_time}" )

    logging.getLogger().info( f"Elapsed time: {end_time - start_time}" )


if __name__ == '__main__':
    main()
