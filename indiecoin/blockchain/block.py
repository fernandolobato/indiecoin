import json

from ..util.serialization import remove_dict_prefix
from ..util.hash import sha256

from . import transaction

from database import Database


class Block(object):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self.hash = kwargs['hash']
        self.timestamp = kwargs['timestamp']
        self.nonce = kwargs['nonce']
        self.num_transactions = kwargs['num_transactions']
        self.is_orphan = True if kwargs['is_orphan'] == 1 else False
        self.previous_block_hash = kwargs['previous_block_hash']
        self.height = kwargs['height']
        # self.hash_merkle_root = kwargs['hash_merkle_root']
        self.transactions = [transaction.Transaction(**tx) if type(tx) != transaction.Transaction else tx for tx in kwargs['transactions']]

        self.__database = kwargs.get('database')

        if self.__database is None:
            self.__database = Database()

        if len(self.hash) != 64:
            self.hash = self.valid_hash()

        if not self.is_valid():
            raise AssertionError('Block is not valid')

    def valid_hash(self):
        """
        """
        data = self.serialize()
        [data.pop(field, None) for field in ['hash']]

        return sha256(str(data))

    def is_valid(self):
        """
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
        pass

    def serialize(self):
        """
        """
        data = remove_dict_prefix(self.__dict__, '_Block')
        [data.pop(field, None) for field in ['__database']]
        data['transactions'] = [tx.serialize() for tx in data['transactions']]

        return data

    def to_json(self):
        return json.dumps(self.serialize())

    def __str__(self):
        transactions = '{}\n'.format(''.join(
            [str(transaction) for transaction in self.transactions]))
        return '{}-{}\n{}'.format(self.hash, self.timestamp, transactions)


class Database(Database):
    """
    """
    def __init__(self, file_name=None):
        """
        """
        super(Database, self).__init__(file_name=file_name)

    def __assemble(self, block):
        """
        """
        if block == []:
            return None

        block = block[0]
        transactions = transaction.Database().get_block_transactions(block['hash'])
        block['transactions'] = transactions
        return Block(**block)

    def get_block(self, block_hash):
        """
        """
        return(self.__assemble(self.__get_block(block_hash)))

    def get_block_height(self, height):
        """
        """
        return(self.__assemble(self.__get_block_height(height)))

    def get_height(self):
        """
        """
        return(self.__get_height()[0]['height'])
