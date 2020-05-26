import sqlite3

class SQLite3DBConnection:
    def __init__( self, file_name ):
        self.db_file_name = file_name
        self.conn = sqlite3.connect( file_name, check_same_thread = False )

    def add_listing( self, listing_id, client_id ):
        c = self.conn.cursor()
        c.execute( '''INSERT INTO 
                      AppRecord (ListingValue) 
                      VALUES( ? )''',
                   ( listing_id, )
                 )
        self.conn.commit()
        c.execute( '''SELECT last_insert_rowid()''' )

        res = c.fetchone()[ 0 ]

        c.execute( '''INSERT INTO 
                      AppUser (EtsyListingID, ClientID )
                      VALUES( ?, ? )''',
                   ( listing_id, client_id )
                 )
        self.conn.commit()

        return res

    def get_client_by_listing_id( self, listing_id ):
        c = self.conn.cursor()
        c.execute( '''SELECT ClientID 
                      FROM AppUser
                      WHERE EtsyListingID = (?)''',
                   ( listing_id, )
                   )
        return c.fetchone()[ 0 ]

        

    def get_listing_id( self, record_id ):
        c = self.conn.cursor()
        c.execute( '''SELECT ListingValue 
                      FROM AppRecord 
                      WHERE RecordID = ?
                   ''', ( record_id, )
                 )
        return c.fetchone()[ 0 ]

    def get_listing_stock( self, record_id ):
        c = self.conn.cursor()
        c.execute(
            '''SELECT QuantityInStock
               FROM EtsyListingStock
               WHERE RecordId = ?
            ''', ( record_id, )

        )

        return c.fetchone()[ 0 ]

    def update_listing_stock( self, record_id, quantity ):
        c = self.conn.cursor()
        c.execute(
            '''UPDATE EtsyListingStock 
               SET QuantityInStock = ?
               WHERE RecordId = ?
            ''', ( quantity, record_id, )

        )

    def add_listing_stock( self, record_id, quantity ):
        c = self.conn.cursor()
        c.execute(
            '''
            INSERT INTO EtsyListingStock (RecordId, QuantityInStock)
            VALUES ( ?, ? )''',
            ( record_id, quantity )
        )
        self.conn.commit()

    def get_record_id( self, listing_id ):
        c = self.conn.cursor()
        c.execute( '''SELECT RecordID 
                      FROM AppRecord 
                      WHERE ListingValue = ?
                   ''', ( listing_id, )
                 )
        return c.fetchone()[ 0 ]
