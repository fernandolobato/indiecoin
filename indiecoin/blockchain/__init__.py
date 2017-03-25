from . import block


class BlockChain(object):

    def __init__(self):
        self._blocks = block.Database()

    def get_block(self, block_hash):
        """ Return a block by it's hash
        """
        return self._blocks.get_block(block_hash)

    def get_block_height(self, height):
        """
        """
        return self._blocks.get_block_height(height)

    def get_height(self):
        """
        """
        return self._blocks.get_height()
