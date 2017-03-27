# -*- coding: utf-8 -*-
import unittest
import sqlite3
import os

from context import indiecoin, GENESIS_BLOCK_HASH
# from indiecoin.blockchain.database import Database
from indiecoin.util import default_data_directory


class DatabaseTestCase(unittest.TestCase):
    """ Test the functionality for interacting with the database.

        Creates a new database called test_database to test that
        when running the program all the tables are generated,
        the genesis block is inserted into the database.

    """
    def setUp(self):
        """ Create database object with different file_name. Open connection to database.
        """
        self.file_name = 'test_database'
        self.path = os.path.join(default_data_directory(), self.file_name)
        self.database = indiecoin.blockchain.database.Database(file_name=self.file_name)
        self.connection = sqlite3.connect(self.path)
        self.genesis_block = GENESIS_BLOCK_HASH

    def tearDown(self):
        """ Destroy database.
        """
        self.connection.close()
        os.system('rm {}'.format(self.path))

    def test_tables_generated(self):
        """ Test that tables are dynamically generated the first time the program runs.
        """
        sql = 'SELECT * FROM block WHERE hash = "{}";'.format(self.genesis_block)
        cursor = self.connection.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        self.assertEqual(len(data), 1)


if __name__ == '__main__':
    unittest.main()
