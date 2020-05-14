#!/usr/bin/env python3
import wolff_api_plugins.server.server as wolff_server
import wolff_api_plugins.server.DBConnection as wolff_db
import argparse
import sys
import logging

def main():
    argp = argparse.ArgumentParser( description = "Start a WOLFF server than can handle HTTP requests." )

    argp.add_argument( '--ip', help = "The IP address to connect to.", type = str,
                       default = '127.0.0.1' 
                     )
    argp.add_argument( '--port', help = "The port to connect to for "
                       "interacting with the MQTT broker.", type = int, default = 1883
                     )
    argp.add_argument( '--update_port', help = "The port to listen on for "
                       "handling update messages from clients.",
                       type = int, default = 1884
                     )
    argp.add_argument( '--db_file', help = "The name of the file containing a "
                       "SQLite3 database containing WOLFF information. ",
                       type = str, default = 'wolff_db.db'
                     )
    argp.add_argument( '--log_file', help = "The name of the file to write log "
                       "information to.", default = "mqtt_server_main.log"
                     )

    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]

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
                               f"--update_port: {args.update_port}\n"
                               f"--db_file: {args.db_file}\n"
                               f"--log_file: {args.log_file}\n"
    )
    logging.getLogger().debug( f"Creating a SQLITE connection to DB file: {args.db_file}" )
    connection = wolff_db.SQLite3DBConnection( args.db_file )

    logging.getLogger().debug( f"Creating a server connection to server: {args.ip}:{args.port}" )
    logging.getLogger().debug( f"Update port: {args.update_port}" )
    server = wolff_server.MQTTServer( connection,
                                      ip = args.ip,
                                      port = args.port,
                                      update_port = args.update_port
                                     )


    logging.getLogger().debug( "Starting the server" )
    server.start()

if __name__ == '__main__':
    main()
