import sqlite3
import json
import os

from .. import util

TABLE_NAME = 'table_name'
TABLE_FIELDS = 'fields'
FIELD_NAME = 'name'
FIELD_TYPE = 'type'
CONSTRAINTS = 'constraints'


class Database(object):

    """ Database Object for generic table generation
    """

    def __init__(self, data_dir=None, file_name=None):

        if data_dir is None:
            data_dir = util.default_data_directory()

        self.__data_dir = data_dir
        self.__file_name = file_name

        if not os.path.exists(self.__data_dir):
            os.makedirs(self.__data_dir)

        self.__connection = sqlite3.connect(self.__get_sqlite_file_name())
        self.__initialize_database()

    def __initialize_database(self):
        """ Initializes the database in case it is the first time running indiecoin.

            This function reads the database schema definition in the form of a JSON
            from the file database.json in the subfolder genesis. This object the
            definition for each table including its constraints.

            It also reads the genesis block from a JSON in genesis.json, It has
            the definition for the first block of the blockchain.

            The create table function creates the table if they don't exist, then we
            check if the genesis block exists, if it doesn't we inser it.
        """
        path = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(path, 'genesis/database.json')) as database_definition_file:
            database_definition = json.load(database_definition_file)

        with open(os.path.join(path, 'genesis/genesis.json')) as genesis_data_file:
            genesis_data = json.load(genesis_data_file)

        for table in database_definition:
            self.__create_table(table)

        genesis_block = self.__get_block(genesis_data['block']['hash'])

        if len(genesis_block) == 0:
            for table, data in genesis_data.iteritems():
                self.__insert(table, data)

    def __create_table(self, table_data):
        """ Creates a databsae table.

            This function recieves the definition of a table in an object.
            For an example of the format, visit genesis/database.json

        """
        sql = 'CREATE TABLE IF NOT EXISTS {} ('.format(table_data[TABLE_NAME])

        for table_field in table_data[TABLE_FIELDS]:
            sql += '{} {}, '.format(table_field[FIELD_NAME], table_field[FIELD_TYPE])

        for constraint in table_data[CONSTRAINTS]:
            sql += '{}, '.format(constraint['name'])

        sql = '{});'.format(sql[:-2])
        self.__execute(sql)

    def __insert(self, table_name, data):
        """ Inserts dictionary data into a column.

            Parameters:
            ----------

            table_name : string
                name of table into where insert data

            data : dictionary
                dictionary where key represents column name
                and value actual data.

        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, columns, placeholders)
        cursor = self.__connection.cursor()
        cursor.execute(sql, data.values())
        self.__connection.commit()
        return cursor.lastrowid

    def __execute(self, sql, data=None):
        """ Executes an sql command in the database.
        """
        cursor = self.__connection.cursor()
        cursor.execute(sql)

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __get_block(self, block_hash):
        """ Retrieves a block from the database with a hash.
        """
        sql = 'SELECT * FROM block WHERE hash = "{}";'.format(block_hash)
        return self.__query(sql)

    def __get_block_height(self, height):
        sql = 'SELECT * FROM block WHERE height = "{}";'.format(height)
        return self.__query(sql)

    def __get_transactions_block(self, block_hash):
        """ Retrieves a transaction from the database.
        """
        sql = 'SELECT * FROM ic_transaction WHERE block_hash = "{}"'.format(block_hash)
        return self.__query(sql)

    def __get_transaction(self, hash):
        """ Retrieves a transaction from the database.
        """
        sql = 'SELECT * FROM ic_transaction WHERE hash = "{}"'.format(hash)
        return self.__query(sql)

    def __get_height(self):
        sql = 'SELECT MAX(height) as height from block where is_orphan = 0'
        return self.__query(sql)

    def __get_transaction_inputs(self, trans_id):
        """ Retrieves transaction inputs from a transaction in the database.
        """
        sql = 'SELECT * FROM transaction_input WHERE id_transaction = {}'.format(trans_id)
        return self.__query(sql)

    def __get_transaction_outputs(self, trans_id):
        """ Retrieves transaction outputs from a transaction in the database.
        """
        sql = 'SELECT * FROM transaction_output WHERE id_transaction = {}'.format(trans_id)
        return self.__query(sql)

    def __query(self, sql):
        self.__connection.row_factory = lambda c, r: dict(
            [(col[0], r[idx]) for idx, col in enumerate(c.description)])
        cursor = self.__connection.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    def __get_sqlite_file_name(self):
        """ Returns the complete path to the sqlite database file.
        """
        file_name = self.__file_name

        if file_name is None:
            file_name = 'indiecoin.sqlite'
        return os.path.join(self.__data_dir, file_name)
