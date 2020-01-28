#!/usr/bin/env python3
import wolff_api_plugins.server.server as wolff_server
import wolff_api_plugins.server.DBConnection as wolff_db
import argparse

def main():
    argp = argparse.ArgumentParser( description = "Start a WOLFF server than can handle HTTP requests." )

    argp.add_argument( '--ip', help = "The IP address to connect to.", type = str,
                       default = '127.0.0.1' 
                     )
    argp.add_argument( '--port', help = "The port to connect to.", type = int, default = 5555 )
    argp.add_argument( '--db_file', help = "The name of the file containing a "
                       "SQLite3 database containing WOLFF information. ",
                       type = str, default = 'wolff_db.db'
                     )

    args = argp.parse_args()


    connection = wolff_db.SQLite3DBConnection( args.db_file )
    server = wolff_server.WOLFFServer( connection, ip = args.ip, port = args.port )

    server.start()

if __name__ == '__main__':
    main()
