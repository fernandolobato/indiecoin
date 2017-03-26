import json

from ..util.serialization import remove_dict_prefix
from ..util.hash import sha256

from . import transaction

from database import Database


class Block(object):
    """ Class representing a Block instance

        This class will serve as an interphase to handle blocks. Whenever
        we need to deal with a block we can turn its data into this object
        where we can deal with all the logic. Validates information inside
        a block and serializes if.
        
        Attributtes
        -----------

            hash: string
                string representation of sha256 hash digest of block.
            timestamp: string
                UNIX time representation of time block was created.
            nonce: string
                variable value to change in proof of work.
            num_transaction: int
                number of transaction inside block
            is_orphan: boolean
                boolean value indicating if block is orphan.
            previous_block_hash: string
                string representation of sha256 hash digest of previous block.
            height: int
                height of block (number of blocks behind it)
            transactions: list
                list of indiecoin.blockchain.transactions.Transaction objets
                inside block.
            __database: indiecoin.blockchain.block.Database
                database object instance to which data will be queried and save.


    """
    def __init__(self, *args, **kwargs):
        """ Construtor for Block

            Turns transaction data into objects if their type is different.
            Creates default database if none provided.

            Raises
            ------
                AssertionError:
                    if block is not valid (see is_valid() function) 
        """
        self.hash = kwargs['hash']
        self.timestamp = kwargs['timestamp']
        self.nonce = kwargs['nonce']
        self.num_transactions = kwargs['num_transactions']
        self.is_orphan = True if kwargs['is_orphan'] == 1 else False
        self.previous_block_hash = kwargs['previous_block_hash']
        self.height = kwargs['height']
        self.transactions = [transaction.Transaction(**tx) if type(tx) != transaction.Transaction else tx for tx in kwargs['transactions']]

        self.__database = kwargs.get('database')

        if self.__database is None:
            self.__database = Database()

        if len(self.hash) != 64:  # If no has was provided we can compute it.
            self.hash = self.valid_hash()

        if not self.is_valid():
            raise AssertionError('Block is not valid')

    def valid_hash(self):
        """ Computes the valid sha256 hash of a block.

            Removes the hash field from serialized object.

            Returns
            -------
                hash: string
                    sha256 digest of block
        """
        data = self.serialize()
        [data.pop(field, None) for field in ['hash']]

        return sha256(str(data))

    def is_valid(self):
        """ Checks if a block is valid.

            Verifies number of transactions, verifies only one coinbase
            transaction. verifies that each transaction is valid, that
            block has a previous block and height matches.

            @TODO:
                Validate Proof-of-work
        """
        coinbase_transactions = 0
        if len(self.transactions) != self.num_transactions:
            return False

        for tx in self.transactions:
            if tx.is_coinbase:
                coinbase_transactions += 1
                if coinbase_transactions > 1:
                    return False

            if not tx.is_valid():
                return False

        if self.height > 1:
            previous_block = self.__database.get_block(self.previous_block_hash)

            if previous_block is None:
                return False

            if previous_block.height != self.height - 1:
                return False

        return True

    def save(self):
        """ Saves a block object to the database.

            Removes transactions data from serialized block,
            saves block to database and then save each transaction
            making reference to the newly created block.

            Returns
            -------
                block_id: int or None
                    id of  newly created block or None if could not
                    be saved.
        """
        block_data = self.serialize()
        [block_data.pop(field, None) for field in ['transactions']]
        
        block_id = self.__database.save_block(block_data)

        if block_id:
            for transaction in self.transactions:
                transaction.set_block_hash(self.hash)
                transaction.save(block_id=block_id)

        return block_id

    def serialize(self):
        """ Serializes a block object into a dictionary representation.

            To serialize each input and output we call its serialize method.

            Returns
            -------
                data : dict
                    dictionary representation of objects attributtes.

            Notes
            ------
                self.database is an attribute that is not used for
                serialization hence removed.
        """
        data = remove_dict_prefix(self.__dict__, '_Block')
        [data.pop(field, None) for field in ['__database']]
        data['transactions'] = [tx.serialize() for tx in data['transactions']]

        return data

    def to_json(self):
        """ Returns a strins representation in JSON of Block object.
        """
        return json.dumps(self.serialize())

    def __str__(self):
        transactions = '{}\n'.format(''.join(
            [str(transaction) for transaction in self.transactions]))
        return '{}-{}\n{}'.format(self.hash, self.timestamp, transactions)


class Database(Database):
    """ Database Object abstraction for Blocks that
        will interact directly with the database.
    """
    def __init__(self, file_name=None):
        self.file_name = file_name
        super(Database, self).__init__(file_name=file_name)

    def __assemble(self, block):
        """ Turns database block data into block object, does
            the same for transactions inside block.
        """
        if block == []:
            return None

        block = block[0]
        transactions = transaction.Database(file_name=self.file_name).get_block_transactions(block['hash'])
        block['transactions'] = transactions
        block['database'] = self
        return Block(**block)

    def get_block(self, block_hash):
        """ Retrieves a block through a hash
        """
        return(self.__assemble(self.__get_block(block_hash)))

    def get_block_height(self, height):
        """ Retrieves a block through height
        """
        return(self.__assemble(self.__get_block_height(height)))

    def get_height(self):
        """ Retrieves the current height of local blockchain.
        """
        return(self.__get_height()[0]['height'])

    def save_block(self, block_data):
        """ Saves block object to database.
        """
        block_id = self.__insert('block', block_data)
        return block_id
