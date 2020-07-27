#!/usr/bin/env python3
import sqlite3

def main():
    conn = sqlite3.connect( 'wolff_db.db' )
    c = conn.cursor()
    c.execute( '''CREATE TABLE AppRecord ( RecordId INTEGER NOT NULL PRIMARY KEY, 
                                           ListingValue text 
                                         )'''
    )

    c.execute( '''CREATE TABLE AppUser ( EtsyListingID TEXT NOT NULL PRIMARY KEY,
                                         ClientID TEXT
                                       )'''
    )

    c.execute( '''CREATE TABLE EtsyListingStock (
                                                  RecordId INTEGER NOT NULL PRIMARY KEY,
                                                  QuantityInStock INTEGER NOT NULL
                                                )'''
    )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
