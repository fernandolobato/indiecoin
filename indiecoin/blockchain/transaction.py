import json

from ..util.serialization import remove_dict_prefix
from ..util.hash import sha256
from ..wallet.address import Address
from .database import Database

REWARD = 5


class Transaction(object):
    """ Class Representing a Transaction instance.

        @TODO:
            Update when a transaction is spent.

        This class will serve as an interphase to handle transactions. It
        can recieve transaction information an structure it. Validates
        information inside a transaction and can serialize object or
        write to database.

        Attributes
        -----------
            hash : string
                sha256 hash of transaction
            block_hash : string
                sha256 hash of block to which transaction belongs to.
            num_inputs: int
                number of inputs inside a transaction
            num_outputs: int
                number of outputs inside a transaction
            timestamp: string
                UNIX timestamp of when transaction was created
            is_coinbase: boolean
                boolean value representing if transaction is coinbase
            tx_inputs: list[]
                list of indiecoin.blockchain.transaction.TransactionInput objects
            tx_outputs: list[]
                list of indiecoin.blockchain.transaction.TransactionOutput objects
            miner_fee: float
                value indicating difference in inputs vs outputs.
            __database: indiecoin.blockchain.transaction.database
                instance of database on which to perform lookups and writeups.

        Raises
        -------
            AssertionError('Transaction is not valid'):
                If transaction information is not valid
                check is_valid() function.
    """
    def __init__(self, *args, **kwargs):
        """ Transaction Contructor

            Checks if a specific instance of a database was sent through
            constructor. If not, initialized a new instance. If no hash has
            been sent it calculates it with all other information.

            For each tx_input and tx_out recieved, checkes if they are already
            an instance of a TransactionInput or TransactionOutput object. If
            they were just sent a dictionary, a new instance of each object is
            created.

        """
        self.hash = kwargs['hash']
        self.block_hash = kwargs['block_hash']
        self.num_inputs = int(kwargs['num_inputs'])
        self.num_outputs = int(kwargs['num_outputs'])
        self.timestamp = kwargs['timestamp']
        self.is_coinbase = True if int(kwargs['is_coinbase']) == 1 else False
        self.is_orphan = True if int(kwargs['is_orphan']) == 1 else False
        self.tx_inputs = kwargs['tx_inputs']
        self.tx_outputs = kwargs['tx_outputs']
        self.tx_inputs = [TransactionInput(**tx_in) if type(tx_in) != TransactionInput else tx_in for tx_in in self.tx_inputs]
        self.tx_outputs = [TransactionOutput(**tx_out) if type(tx_out) != TransactionOutput else tx_out for tx_out in self.tx_outputs]

        self.miner_fee = 0
        self.__database = kwargs.get('database')

        if self.__database is None:
            self.__database = Database()

        if len(self.hash) < 64:  # Size of sha256 digest as a string
            self.hash = self.valid_hash()

        if not self.is_valid():
            raise AssertionError('Transaction not valid')

    def set_block_hash(self, block_hash):
        """ Sets a block hash on a transaction. This will be called
            once the miner has found a correct hash for the block
            so each transaction can reference it later.
        """
        self.block_hash = block_hash

    def valid_hash(self):
        """ Calculates the valid hash for this transaction.

            Takes data from serialize(), removes hash and block
            hash.

            Returns
            -------
                sha256 representation of object
        """
        data = self.serialize()

        [data.pop(field, None) for field in ['block_hash', 'hash']]

        return sha256(str(data))

    def is_valid(self):
        """ Checks that a transaction is valid.

            @TODO:
                Check coinbase amount is less than or equal to the
                sum of fees and reward.

            Performs the following checks:

                - The sum of inputs most be less than or equal to
                the sum of outputs (no overspending)

                - All tx_outputs referenced in each input most not
                be spent yet.

                - The signature for each input presented most match
                the public key stored in the output it represents.

                - Checks that if the transaction has no inputs its
                a coinbase transaction.

        """
        input_total = 0
        output_total = 0

        if self.num_inputs != len(self.tx_inputs):
            return False

        if self.num_outputs != len(self.tx_outputs):
            return False

        if self.num_inputs == 0 and not self.is_coinbase:
            return False

        for tx_input in self.tx_inputs:
            input_total += tx_input.amount

            if not tx_input.unspent:
                return False
            if not tx_input.validate_signature():
                return False

        for tx_output in self.tx_outputs:
            output_total += tx_output.amount

        if not self.is_coinbase:
            self.miner_fee += (input_total - output_total)

        if self.is_coinbase:
            if input_total + self.miner_fee + REWARD > output_total:
                return False

        if input_total > output_total and not self.is_coinbase:
            return False

        return True

    def exists(self):
        """ Checks if current transaction already exists in the database.

            Returns
            -------
                exists : boolean value
                    boolean indicating if transaction exists in database.
        """
        db_transaction = self.__database.get_transaction(self.hash)
        if db_transaction is not None:
            return True
        return False

    def save(self, block_id=None):
        """ Saves a transaction along with its transaction inputs
            and outputs to local database.

            @TODO:
                Implement Update

            Transaction can recieve a block id to add it to data
            dictionary and save.

            Returns
            -------
                id_new_object: int
                    In the case the object is saved succesfully.
                None: None
                    In the case the object could not be saved.
        """
        if self.exists():
            raise NotImplemented('No update Implemented')

        tx_data = self.serialize()
        if block_id:
            tx_data['block_id'] = block_id
        return self.__database.save_transaction(tx_data)

    def serialize(self):
        """ Serializes a transaction object into a dictionary representation.

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
        data = remove_dict_prefix(self.__dict__, '_Transaction')

        data['tx_outputs'] = [tx.serialize() for tx in data['tx_outputs']]
        data['tx_inputs'] = [tx.serialize() for tx in data['tx_inputs']]

        fields = ['__database', 'miner_fee']

        [data.pop(field, None) for field in fields]

        return data

    def to_json(self):
        """ Returns a strins representation in JSON of Transaction object.
        """
        return json.dumps(self.serialize())

    def __str__(self):
        return '{}'.format(self.hash)


class TransactionInput(object):
    """ Represents a Transaction Input

        Attributes
        ----------
            signature: string
                hexadecimal string representation of an ecdsa signature.
                This signature unlucks the transaction output referenced
                in this input.

            hash_transaction: string
                sha256 hash representing the id of a past transaction.

            prev_out_index: int
                Index pointing to which transaction_output of transaction
                is being referenced in this TransactionInput.
            __database: indiecoin.blockchain.transaction.database
                instance of database on which to perform lookups and writeups.
            __prev_tx: indiecoin.blockchain.transaction.Transaction
                transaction referenced by hash_transaction
    """
    def __init__(self, *args, **kwargs):
        """ Constructor for TransactionInput

            Looks up previous transaction using hash provided in
            constructor.
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
                Value of transaction output.
            public_key_owner : string
                String hexadecimal representation of an ecdsa public
                key representing the entity who can spend transaction.
            unspent: boolean
                Value indicating if transaction has been spent.
    """

    def __init__(self, *args, **kwargs):
        """ Constructor for TransactionOutput
        """
        self.amount = int(kwargs['amount'])
        self.public_key_owner = kwargs['public_key_owner']
        self.unspent = True if kwargs['unspent'] == 1 else False

    def serialize(self):
        """ Serializes a transaction object into a dictionary representation.

            Returns
            -------
                data : dict
                    dictionary representation of objects attributtes.

            Notes
            ------
                self.database is an attribute that is not used for
                serialization hence removed.
        """
        data = remove_dict_prefix(self.__dict__, '_TransactionOutput')
        fields = ['__database']
        [data.pop(field, None) for field in fields]
        return data

    def to_json(self):
        """ Returns a string JSON representation of this objects
            serialization.
        """
        return json.dumps(self.serialize())

    def __str__(self):
        return '{}-{}-{}'.format(self.amount, self.public_key_owner, self.unspent)


class Database(Database):
    """ Database Object abstraction for Transactions that
        will interact directly with the database.
    """
    def __init__(self, file_name=None):
        """ Constructor for transaction.Database calls super
            constructor.
        """
        super(Database, self).__init__(file_name=file_name)

    def get_transaction(self, hash_trans):
        """ Retrieves a transaction through a hash identifier.

            After getting transaction it queries the Inputs and
            Outpus. Turn each dictionary data into an object and
            add them to Transaction instance.

            Returns
            -------
                transaction: indiecoin.blockchain.transaction.Transaction
                    transaction instance
        """
        transaction = self.__get_transaction(hash_trans)

        if len(transaction):

            transaction = transaction[0]
            inputs = self.__get_transaction_inputs(transaction['id'])
            outputs = self.__get_transaction_outputs(transaction['id'])

            transaction['tx_inputs'] = inputs
            transaction['tx_outputs'] = outputs
            [tx_in.update({'database': self}) for tx_in in transaction['tx_inputs']]

            transaction['database'] = self

            return Transaction(**transaction)
        return None

    def get_block_transactions(self, block_hash):
        """ Gets all the transactions belonging to a block

            Returns
            -------
            transactions: list
                list of indiecoin.blockchain.transaction.Transaction

        """
        transactions = self.__get_transactions_block(block_hash)

        for transaction in transactions:
            transaction['tx_inputs'] = self.__get_transaction_inputs(transaction['id'])
            transaction['tx_outputs'] = self.__get_transaction_outputs(transaction['id'])
            [tx_in.update({'database': self}) for tx_in in transaction['tx_inputs']]

        [tx.update({'database': self}) for tx in transactions]
        return [Transaction(**tx) for tx in transactions]

    def save_transaction(self, transaction):
        """ Saves a transaction object to the database.

            After saving transaction object it gets its
            newely created id and uses it to save each
            transaction input and output.
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
