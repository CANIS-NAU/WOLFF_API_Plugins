#!/usr/bin/env python3
import logging
import json
import time
import sys
import argparse


def main():
    argp = argparse.ArgumentParser( description = "Script to update an existing listing." ) 
    argp.add_argument( '--ip', help = "IP of the Proxy server that an update request will be sent to.", required = True )
    argp.add_argument( '--port', help = "Port of the proxy server's update_listing service.", type = int, required = True )
    argp.add_argument( '--listing_id', help = "Listing id (as located in the file containing listings) of the id to update.", type = int, required = True )
    argp.add_argument( '--listings_file', help = "Name of the file containing listings that can be updated.",
                       default = "submitted_listings.json"
    )
    argp.add_argument( '--update', action = 'append', required = True,
                       help = "The value you wish to update, combined with its new value, separated by an 'equals'. "
                       'Example: title="This is the new title". To update multiple values, include this argument multiple times.'
    )
    argp.add_argument( '--log_file', help = "The name of the file to write log "
                       "information to.", default = "update_listing.log"
                     )

    args = argp.parse_args()

    update_str = ''
    for update in args.update:
        update_str += f'--update {update}\n'
        

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
                               f"--listings_file: {args.listings_file}\n"
                               f"{update_str}"
                               f"--log_file: {args.log_file}\n"
    )

    listings = list()

    logging.getLogger().debug( f"Attempting to open {args.listings_file} to read listings" )
    with open( args.listings_file, 'r' ) as of:
        listings = get_listing_data( of )

    logging.getLogger().debug( "Successfully parsed listing data" )

    try:
        target_listing = list( filter( lambda x: x[ 'listing_id' ] == args.listing_id, listings ) )[ 0 ]
    except IndexError:
        logging.getLogger().error( "Unable to find the indicated target listing." )
        sys.exit( 1 )

    logging.getLogger().debug( f"Data for target listing: {target_listing}" )
    logging.getLogger().debug( f"Attempting to parse update data." )

    update_dict = format_update_data( args.update )
    logging.getLogger().debug( f"Update dictionary: {update_dict}" )

    logging.getLogger().debug( f"Updating the target listing data with new data." )

    target_listing.update( update_dict )

    logging.getLogger().debug( f"Updated listing data: {target_listing}" )

    request_dict = craft_request( target_listing )

    request_string = json.dumps( request_dict )

    logging.getLogger().debug( f"Post-encoded update message: {request_string}" )


def craft_request( listing_dict ):
    output = dict()
    output[ 'message' ] = listing_dict
    output[ 'api_details' ] = [ 'etsy', 'update_listing' ]
    return output


def format_update_data( data_list ):
    output = dict()

    for item in data_list:
        key, value = item.split( '=' )

        try:
                value = int( value )
                logging.getLogger().debug( f"Converted argument '{key}' into int." )
        except Exception:
            try:
                value = float( value )
                logging.getLogger().debug( f"Converted argument '{key}' into float." )
            except Exception:
                logging.getLogger().debug( f"Argument '{key}' determined to be string." )

    
        output[ key ] = value

            

    return output

def get_listing_data( file_handle ):
    output = list()

    for line in file_handle:
        new_listing = json.loads( line.strip() )
        logging.getLogger().debug( f"Data from file: {new_listing}" )
        output.append( new_listing )
    return output



if __name__ == '__main__':
    main()
