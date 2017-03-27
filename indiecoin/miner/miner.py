import time
import threading

from .. import blockchain
from ..wallet.address import Address
from ..util.hash import sha256d

REWARD = 5
DIFFICULTY = 2 ** (256 - 25)

class Miner(object):

    def __init__(self, address=None):
        self.__interrupt = False
        self.__found = False
        self.__shutdown = False
        self.__address = None
        self.current_block = None
        if self.__address is None:
            self.__address = Address()
            # print(self.__address.public_key)
            # print(self.__address.private_key)

        self.main_thread = threading.Thread( target = self.main_loop, args = [] )

    def __debug(self, msg):
        print(msg)

    @property
    def found(self):
        return self.__found

    def shutdown(self):
        """
        """
        self.__shutdown = True

    def interrupt(self):
        """
        """
        self.__debug('------- INCOMING BLOCK --------')
        self.__interrupt = True

    def begin_mining(self):
        """
        """
        self.__interrupt = False

    def get_current_block(self):
        if self.current_block:
            return self.current_block.serialize()
        return None

    def create_current_block(self, transactions):
        """
        """
        for tx in transactions:
            if tx.is_coinbase:
                transactions.remove(tx)

        max_height = blockchain.BlockChain().get_height()
        prev_block = blockchain.BlockChain().get_block_height(max_height)
        fees = 0

        for tx in transactions:
            fees += tx.miner_fee

        coin_base_output = {
            'amount': REWARD + fees,
            'public_key_owner': self.__address.public_key,
            'unspent': 1,
        }

        coin_base_transaction_data = {
            'hash': '',
            'block_hash': '',
            'num_inputs': 0,
            'num_outputs': 1,
            'timestamp': time.time(),
            'is_coinbase': 1,
            'is_orphan': 0,
            'tx_inputs': [],
            'tx_outputs': [coin_base_output],
        }

        coin_base_transaction = blockchain.transaction.Transaction(**coin_base_transaction_data)

        transactions.append(coin_base_transaction)

        block_data = {
            'hash': '',
            'timestamp': time.time(),
            'nonce': '',
            'num_transactions': len(transactions),
            'is_orphan': 0,
            'previous_block_hash': prev_block.hash,
            'height': int(max_height) + 1,
            'transactions': transactions,
        }

        new_block = blockchain.block.Block(**block_data)
        self.current_block = new_block
        return new_block
    
    def start(self):
        self.__debug('------ BEGIN MINING --------')
        self.main_thread.start()

    def main_loop(self):
        """
        """
        while not self.__shutdown:
            nonce = 0
            
            while self.current_block is None:
                pass

            self.__debug('------- BEGIN MINING BLOCK --------')
            block = self.current_block

            while(not self.__interrupt and not self.__found):
                block.nonce = nonce
                block.hash = block.valid_hash()

                if int(block.hash, 16) < DIFFICULTY:
                    self.__found = True
                    break

                nonce += 1

            if self.__found and not self.__interrupt:
                self.__debug('------- BLOCK FOUND --------')
                self.__interrupt = True
            
            self.__debug('------- INTERRUPTED --------')
            while(self.__interrupt):
                pass

            self.current_block = None
