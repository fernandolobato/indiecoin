# -*- coding: utf-8 -*-
import unittest
import sqlite3
import json
import os

from context import indiecoin
from context import GENESIS_BLOCK_HASH, PUBLIC_KEY_GENESIS, PRIVATE_KEY_GENESIS
from indiecoin.blockchain import transaction
from indiecoin.util import default_data_directory


class TransactionInputTestCase(unittest.TestCase):
    """ Tests the functionality for TransactionInput objects
        inside indeicoin.blockchain.transaction

        @TODO TESTS:
    """
    def setUp(self):
        """ Lookups genesis block and first transaction. Uses private key from genesis
            block to generate address object. This will lookup in the normal database.
            This should no affect since both database have the genesis block in them.

            Starts a database connection to a test database.
        """
        self.file_name = 'test_database'
        self.path = os.path.join(default_data_directory(), self.file_name)
        self.database = transaction.Database(file_name=self.file_name)
        self.block_database = indiecoin.blockchain.block.Database(file_name=self.file_name)

        self.block = indiecoin.blockchain.BlockChain(database=self.block_database).get_block(GENESIS_BLOCK_HASH)

        self.transaction = self.block.transactions[0]
        self.address = indiecoin.wallet.address.Address(private_key=PRIVATE_KEY_GENESIS)

        self.tx_input_data = {
            'signature': self.address.sign(self.transaction.hash),
            'hash_transaction': self.transaction.hash,
            'prev_out_index': '0',
            'database': self.database
        }

    def tearDown(self):
        """ Destroy database.
        """
        os.system('rm {}'.format(self.path))

    def test_create_tx_input_from_dict(self):
        """ Create a TransactionInput object from dictionary data.
        """
        tx_input = transaction.TransactionInput(**self.tx_input_data)

        self.assertEqual('{}'.format(tx_input), self.transaction.hash)
        self.assertEqual(type(tx_input.serialize()), dict)
        self.assertEqual(type(tx_input.to_json()), str)
        self.assertTrue(tx_input.validate_signature())

    def test_get_amount_previous_tx(self):
        """ Get the amount of the TransactionOutput being referenced in
            transaction input.
        """
        tx_input = transaction.TransactionInput(**self.tx_input_data)
        self.assertEqual(self.transaction.hash, tx_input.hash_transaction)
        self.assertEqual(tx_input.amount, 50)

    def test_create_from_json_string(self):
        """ Create an TransactionInput object from a string JSON.
        """
        del self.tx_input_data['database']
        tx_input_data_string = json.dumps(self.tx_input_data)
        tx_input_data = json.loads(tx_input_data_string)
        tx_input_data['database'] = self.database
        tx_input = transaction.TransactionInput(**tx_input_data)
        self.assertTrue(tx_input.validate_signature())


class TransactionOutputTestCase(unittest.TestCase):
    """ Tests the functionality for TransactionOutput objects
        inside indeicoin.blockchain.transaction
    """
    def setUp(self):
        """ Initialized data.
        """
        self.tx_output_data = {
            'amount': 25,
            'public_key_owner': PUBLIC_KEY_GENESIS,
            'unspent': 1
        }

    def test_create_tx_output_from_dict(self):
        """ Generate TransactionOutput from dictionary data.
        """
        tx_output = transaction.TransactionOutput(**self.tx_output_data)
        expected = '{}-{}-True'.format(
            self.tx_output_data['amount'],
            self.tx_output_data['public_key_owner'])

        self.assertEqual(expected, str(tx_output))
        self.assertEqual(type(tx_output.serialize()), dict)
        self.assertEqual(type(tx_output.to_json()), str)


class TransactionTestCase(unittest.TestCase):
    """ Generate new transaction referencing genesis transaction
    """
    def setUp(self):
        """ Initialize database, lookup genesis block to create new
            transaction making reference to the outputs of that
            transaction.
        """
        self.file_name = 'test_database'
        self.path = os.path.join(default_data_directory(), self.file_name)
        self.database = transaction.Database(file_name=self.file_name)
        self.block_database = indiecoin.blockchain.block.Database(file_name=self.file_name)

        self.block = indiecoin.blockchain.BlockChain(database=self.block_database).get_block(GENESIS_BLOCK_HASH)

        self.transaction = self.block.transactions[0]
        self.address = indiecoin.wallet.address.Address(private_key=PRIVATE_KEY_GENESIS)

        signature = self.address.sign(self.transaction.hash)

        self.tx_input_data = {
            'signature': signature,
            'hash_transaction': self.transaction.hash,
            'prev_out_index': '0',
            'database': self.database
        }

        self.transaction_outputs = [
            {
                'amount': 25,
                'public_key_owner': PUBLIC_KEY_GENESIS,
                'unspent': 1
            },
            {
                'amount': 25,
                'public_key_owner': PUBLIC_KEY_GENESIS,
                'unspent': 1
            }
        ]

        self.transaction_data = {
            'hash': '',
            'block_hash': '',
            'num_inputs': 1,
            'num_outputs': '2',
            'timestamp': '1490477410',
            'is_coinbase': 0,
            'is_orphan': 0,
            'tx_inputs': [self.tx_input_data],
            'tx_outputs': self.transaction_outputs,
            'database': self.database
        }

    def tearDown(self):
        """ Destroy database.
        """
        os.system('rm {}'.format(self.path))

    def test_create_transaction(self):
        """ Test creating a Transaction object from dictionary data.
        """
        trans = transaction.Transaction(**self.transaction_data)
        serialized_data = trans.serialize()
        self.assertEqual(type(serialized_data), dict)
        self.transaction_data.pop('database', None)
        self.assertEqual(len(serialized_data), len(self.transaction_data))
        self.assertEqual(type(trans.to_json()), str)
        self.assertEqual(len(str(trans)), 64)
        self.assertTrue(trans.is_valid())

    def test_not_valid_transaction(self):
        """ Test creating a not valid Transaction objet from dictionary data.
        """
        change = self.transaction_data['tx_inputs'][0]['signature'].replace('1', '2')
        self.transaction_data['tx_inputs'][0]['signature'] = change

        try:
            transaction.Transaction(**self.transaction_data)
        except AssertionError as e:
            self.assertEqual(e[0], 'Transaction not valid')

    def test_save_database(self):
        """ Test saving a transaction object to database.
        """
        trans = transaction.Transaction(**self.transaction_data)
        saved = trans.save()
        self.assertNotEqual(None, saved)
        saved_trans = self.database.get_transaction(trans.hash)

        self.assertEqual(saved_trans.hash, trans.hash)

        self.assertEqual(
            saved_trans.tx_inputs[0].signature,
            self.transaction_data['tx_inputs'][0]['signature'])

        self.assertEqual(len(saved_trans.tx_outputs), 2)


class TransactionDatabaseTestCase(unittest.TestCase):
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
        self.database = transaction.Database(file_name=self.file_name)
        self.connection = sqlite3.connect(self.path)
        self.genesis_block = GENESIS_BLOCK_HASH

    def tearDown(self):
        """ Destroy database.
        """
        self.connection.close()
        os.system('rm {}'.format(self.path))

    def test_get_transaction_block(self):
        """ Test that we can get transactions from block.
        """
        transactions = self.database.get_block_transactions(self.genesis_block)
        self.assertEqual(len(transactions), 1)


if __name__ == '__main__':
    unittest.main()
