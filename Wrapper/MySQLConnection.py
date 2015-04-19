#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import ConfigParser
import MySQLdb
import MySQLdb.cursors

"""
Easy read access to the MySQL database.
You can initialise an object with path to the base directory, where the 'mysql.config' file can be found
and which corpus should be read.
The training-corpus is used by default, the development corpus is called 'DEV' and the test-corpus 'TEST'.

To get data from the database, use getRows(), which will return an server-sided courser, that can be used
to iterate over the rows in the database:

> mysql = MySQLConnectionWrapper()
> rows = mysql.getRows()
>
> for row in rows:
>     # do thins

If you are only interested in certain columns, pass them as a string:

> rows = mysql.getRows("tokenised, lan, lat")
>
> for tok, lan, lat in rows:
>     print tok, lan, lat

If you want to pass a condition, use getRowsRaw(). You have to specify the columns to select and all conditions
as astring.
"""
class MySQLConnectionWrapper:
    # corpus = TRAIN, DEV or TEST
    def __init__(self, basedir='', corpus='TRAIN'):
        # Read in config:
        config = ConfigParser.RawConfigParser()
        config.read(basedir + 'mysql.config')

        dbHostDB = config.get('MySQL', 'mySQLHost')
        dbUser = config.get('MySQL', 'mySQLUser')
        dbPassword = config.get('MySQL', 'mySQLPassword')
        dbHost = dbHostDB[:dbHostDB.find("/")]
        dbDB = dbHostDB[dbHostDB.find("/") + 1:]

        # Connect to database
        connection = MySQLdb.connect(host = dbHost, user = dbUser, passwd = dbPassword, db = dbDB)

        # Create a server-sided cursor: http://stackoverflow.com/a/3788777/4587312
        self.readCursor = connection.cursor(MySQLdb.cursors.SSCursor)

        self.dbTable = config.get('MySQL', 'mySQLTablePrefix') + "_" + corpus

    def getRows(self, columns="*"):
        """ Read MySQL database in chunks """
        self.readCursor.execute('SELECT ' + columns + ' FROM ' + self.dbTable)
        return self.readCursor

    def getRowsRaw(self, columns, conditions):
        self.readCursor.execute('SELECT ' + columns + ' FROM ' + self.dbTable + " " + conditions)
        return self.readCursor
