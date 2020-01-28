import sqlite3

class SQLite3DBConnection:
    def __init__( self, file_name ):
        self.db_file_name = file_name
        self.conn = sqlite3.connect( file_name )

    def add_listing( self, listing_id ):
        c = self.conn.cursor()
        c.execute( '''INSERT INTO 
                      AppRecord (ListingValue) 
                      VALUES( ? )''',
                   ( listing_id, )
                 )
        self.conn.commit()
        c.execute( '''SELECT last_insert_rowid()''' )
        return c.fetchone()[ 0 ]

    def get_listing_id( self, record_id ):
        c = self.conn.cursor()
        c.execute( '''SELECT ListingValue 
                      FROM AppRecord 
                      WHERE RecordID = ?
                   ''', ( record_id, )
                 )
        return c.fetchone()[ 0 ]
