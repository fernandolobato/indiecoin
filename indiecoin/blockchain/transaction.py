import json

from ..util.serialization import remove_dict_prefix
from ..util.hash import sha256
from ..wallet.address import Address

from .database import Database


class Transaction(object):

    def __init__(self, *args, **kwargs):
        self.hash = kwargs['hash']
        self.block_hash = kwargs['block_hash']
        self.num_inputs = kwargs['num_inputs']
        self.num_outputs = kwargs['num_outputs']
        self.timestamp = kwargs['timestamp']
        self.is_coinbase = True if int(kwargs['is_coinbase']) == 1 else False
        self.is_orphan = True if int(kwargs['is_orphan']) == 1 else False
        self.tx_inputs = kwargs['tx_inputs']
        self.tx_outputs = kwargs['tx_outputs']

        self.tx_inputs = [TransactionInput(**tx_in) if type(tx_in) != TransactionInput else tx_in for tx_in in self.tx_inputs]
        self.tx_outputs = [TransactionOutput(**tx_out) if type(tx_out) != TransactionOutput else tx_out for tx_out in self.tx_outputs]

        self.__database = kwargs.get('database')

        if self.__database is None:
            self.__database = Database()

        if len(self.hash) < 64:
            self.hash = self.valid_hash()

        if not self.is_valid():
            raise AssertionError('Transaction not valid')

    def set_block_hash(self, block_hash):
        self.__block_hash = block_hash

    def valid_hash(self):
        data = self.serialize()

        [data.pop(field, None) for field in ['block_hash', 'hash']]

        return sha256(str(data))

    def is_valid(self):
        """
        """
        input_total = 0
        output_total = 0

        for tx_input in self.tx_inputs:
            input_total += tx_input.amount

            if not tx_input.unspent:
                return False
            if not tx_input.validate_signature():
                return False

        for tx_output in self.tx_outputs:
            output_total += tx_output.amount

        if input_total > output_total:
            return False

        return True

    def save(self):
        """
        """
        return self.__database.save_transaction(self.serialize())

    def serialize(self):
        data = remove_dict_prefix(self.__dict__, '_Transaction')

        data['tx_outputs'] = [tx.serialize() for tx in data['tx_outputs']]
        data['tx_inputs'] = [tx.serialize() for tx in data['tx_inputs']]

        fields = ['__database']

        [data.pop(field, None) for field in fields]

        return data

    def to_json(self):
        return json.dumps(self.serialize())

    def __str__(self):
        return '{}'.format(self.hash)


class TransactionInput(object):
    """ Represents a Transaction Input

        Attributes
        ----------
            signature:

            hash:

            prev_out_index:

            database:

            prev_tx:
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self.signature = kwargs['signature']
        self.hash_transaction = kwargs['hash_transaction']
        self.prev_out_index = int(kwargs['prev_out_index'])
        self.__database = kwargs.get('database')

        if self.__database is None:
            self.__database = Database()

        self.__prev_tx = self.__database.get_transaction(self.hash_transaction)

    @property
    def unspent(self):
        """ Property indicating if the transaction output referenced
            by this input has been spent.

            Returns
            --------
                unspent: boolean
        """
        return self.__prev_tx.tx_outputs[self.prev_out_index].unspent

    @property
    def amount(self):
        """ The amount of the output referenced in this input.

            Returns
            -------
                amount : int
                    The amount that the output refeenced by this
                    input has registered in the blockchain.
        """
        return self.__prev_tx.tx_outputs[self.prev_out_index].amount

    def validate_signature(self):
        """ Validates if the signature provided in a transaction input
            is valid for the public key stored in the transaction output
            being referenced.
        """
        public_key = self.__prev_tx.tx_outputs[self.prev_out_index].public_key_owner

        if Address(public_key).verify_signature(self.signature, self.__prev_tx.hash):
            return True

        return False

    def serialize(self):
        """ Serializes the data inside this object into a dictionary
            with the corresponding to be sent through the network.

            Removes the fields that represent internal attributes
            that will not be used for serialization.

            RETURNS
            -------
                data : dict
                    dictionary representing instance.
        """
        data = remove_dict_prefix(self.__dict__, '_TransactionInput')
        fields = ['__prev_tx', '__database']
        [data.pop(field, None) for field in fields]

        return data

    def to_json(self):
        """ Returns a string JSON representation of this objects
            serialization.
        """
        return json.dumps(self.serialize())

    def __str__(self):
        return '{}'.format(self.hash_transaction)


class TransactionOutput(object):
    """ Representation of a Transaction Output

        Attributes
        ----------
            amount : int

            public_key_owner : string

            unspent: boolean

    """

    def __init__(self, *args, **kwargs):
        """
        """
        self.amount = int(kwargs['amount'])
        self.public_key_owner = kwargs['public_key_owner']
        self.unspent = True if kwargs['unspent'] == 1 else False
        self.__database = kwargs.get('database')

        if self.__database is None:
            self.__database = Database()

    def serialize(self):
        """
        """
        data = remove_dict_prefix(self.__dict__, '_TransactionOutput')
        fields = ['__database']
        [data.pop(field, None) for field in fields]
        return data

    def to_json(self):
        return json.dumps(self.serialize())

    def __str__(self):
        return '{}-{}-{}'.format(self.amount, self.public_key_owner, self.unspent)


class Database(Database):
    """ Database Object abstraction for Transactions that
        will interact directly with the database.
    """

    def __init__(self, file_name=None):
        super(Database, self).__init__(file_name=file_name)

    def get_transaction(self, hash_trans):
        """
        """
        transaction = self.__get_transaction(hash_trans)

        if transaction[0]:

            transaction = transaction[0]
            inputs = self.__get_transaction_inputs(transaction['id'])
            outputs = self.__get_transaction_outputs(transaction['id'])

            transaction['tx_inputs'] = inputs
            transaction['tx_outputs'] = outputs

        return Transaction(**transaction)

    def get_block_transactions(self, block_hash):
        """
        """
        transactions = self.__get_transactions_block(block_hash)

        for transaction in transactions:
            transaction['tx_inputs'] = self.__get_transaction_inputs(transaction['id'])
            transaction['tx_outputs'] = self.__get_transaction_outputs(transaction['id'])

        return [Transaction(**tx) for tx in transactions]

    def save_transaction(self, transaction):
        """
        """
        if not self.__get_transaction(transaction['hash']):
            inputs = transaction.pop('tx_inputs')
            outputs = transaction.pop('tx_outputs')

            trans_id = self.__insert('ic_transaction', transaction)

            if trans_id is None:
                return None

            for tx_in in inputs:
                tx_in['id_transaction'] = trans_id
                self.__insert('transaction_input', tx_in)

            for tx_out in outputs:
                tx_out['id_transaction'] = trans_id
                self.__insert('transaction_output', tx_out)
            return trans_id
        return None
