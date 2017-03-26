from . import block


class BlockChain(object):
    """ Blockchain interhpase to query items directly
        to the blockchain without touching directly object.
        
        Performs basic query operations on blockhain. Can
        get a block, can get the height or can get a transaction.

        Attributes
        ----------
            _blocks: indiecoin.blockchain.block.Database
                A database object representing a connection to
                a db endpoint. can be revieved for testing
                purposes.
    """
    def __init__(self, database=None):
        """ BlockChain Contructor.

            Can receive a database object to query at specific database.
            If None is receieved, created a new instance which will
            point to default database. 
        """
        self._blocks = database

        if self._blocks is None:
            self._blocks = block.Database()

    def get_block(self, block_hash):
        """ Return a block by it's hash

            Returns
            -------
                block: indiecoin.blockchain.block.Block
                    block object instance for that hash.
        """
        return self._blocks.get_block(block_hash)

    def get_block_height(self, height):
        """ Return a block by it's height

            Returns
            -------
                block: indiecoin.blockchain.block.Block
                    block object instance for that height.
        """
        return self._blocks.get_block_height(height)

    def get_height(self):
        """ Returns the height of local blockchain

            Returns
            -------
                height: int
                    height, number of blocks in database.
        """
        return self._blocks.get_height()

    def get_transaction(self, transaction_hash):
        """ Returns a transaction by its hash
            
            @TODO: Implement

            Returns
            -------
                transaction: indiecoin.blockchain.transaction.Transaction
                    transaction object for specified hash.
        """
        raise NotImplemented('Not yet implemented')
