import json
import threading

from .ic_peer import IndieCoinPeer
from .. import blockchain

from protocol.response import Response
from protocol import protocol


class IndieCoinNode(IndieCoinPeer):
    """
    """
    def __init__(self, maxpeers, serverport, miner=None):
        """
        """
        IndieCoinPeer.__init__(self, maxpeers, serverport)

        self.miner = miner
        self.main_thread = threading.Thread(target=self.mainloop, args=[])

        handlers = {
            protocol.BLOCK_GET: self.__handle_block_get,
            protocol.MAX_BLOCK_HEIGHT: self.__handle_height_get,
            protocol.BLOCK_HEIGHT: self.__handle_block_get,
            protocol.RELAY_TRANSACTION: self.__handle_relay_transaction,
            protocol.RELAY_BLOCK: self.__handle_relay_block,
        }

        self.transactions_queue = []

        for mt in handlers:
            self.addhandler(mt, handlers[mt])

    def __debug(self, msg):
        """
        """
        print(msg)

    def start(self):
        """
        """
        self.main_thread.start()

    def connect_and_send(self, peer, msg_type, msg_data='', pid=None, waitreply=True):
        """
        """
        try:
            host, port = peer.split(':')
            response = self.connectandsend(host, port, msg_type, msg_data, pid, waitreply)

        except Exception as e:
            response = Response(protocol.ERROR, '')
            self.__debug(e)
            self.__debug('No response from {}'.format(peer))

        return response

    def __handle_height_get(self, peer_connection, data):
        """
        """
        response = '{}'.format(blockchain.BlockChain().get_height())
        peer_connection.send_data(protocol.REPLY, response)

    def __handle_block_get(self, peer_connection, block_id):
        """
        """
        if len(block_id) == 64:
            block = blockchain.BlockChain().get_block(block_id)
        else:
            block = blockchain.BlockChain().get_block_height(block_id)

        if not block:
            peer_connection.send_data(protocol.ERROR, 'Block not found')
        else:
            peer_connection.send_data(protocol.REPLY, block.to_json())

    def __handle_relay_transaction(self, peer_connection, data):
        """
        """
        data = json.loads(data)

        try:
            transaction = blockchain.transaction.Transaction(**data)
        except AssertionError as e:
            self.__debug(e[0])
            return

        if transaction in self.transactions_queue:
            return

        self.transactions_queue.append(transaction)

        if transaction.is_valid() and not transaction.exists():
            for peer in self.get_peer_ids():
                if peer != peer_connection.id:
                    self.connect_and_send(
                        peer,
                        protocol.RELAY_TRANSACTION,
                        transaction.to_json(),
                        None,
                        False)

    def __handle_relay_block(self, peer_connection, data):
        data = json.loads(data)

        try:
            block = blockchain.block.Block(**data)
        except AssertionError as e:
            self.__debug(e[0])
            return

        if self.miner:
            # MINER SHIT
            pass

        if not block.exists():
            block.save()

            for transaction in block.transactions:
                for queue_transaction in self.transactions_queue:
                    if queue_transaction.hash == transaction.hash:
                        self.transactions_queue.remove(queue_transaction)

            for peer in self.get_peer_ids():
                if peer != peer_connection.id:
                    self.connect_and_send(peer, protocol.RELAY_BLOCK, block.to_json(), None, False)

    def bootstrap(self):
        """
        """
        self.__debug('------ BOOTSTRAPPING IN PROGRESS -----')
        current_height = int(blockchain.BlockChain().get_height())
        max_height = 0
        peer_max_height = None

        for peer in self.get_peer_ids():
            response = self.connect_and_send(peer, protocol.MAX_BLOCK_HEIGHT)

            if response.is_successful():
                peer_height = int(response.data)
                if peer_height > max_height:
                    max_height = peer_height
                    peer_max_height = peer

        if current_height < max_height:
            self.__debug('------ UPDATING BLOCKHAIN -------')
            for i in range(current_height+1, int(max_height)+1):
                    response = self.connect_and_send(
                        peer_max_height,
                        protocol.BLOCK_GET,
                        str(i))
                    """
                        @ TODO:
                            What happens when it fails?
                    """
                    block_data = response.data
                    try:
                        block = blockchain.block.Block(**block_data)
                        block.save()
                    except AssertionError as e:
                        self.__debug(e[0])

            self.__debug('------ FINISH UPDATING BLOCKHAIN -------')
        self.__debug('----- BOOTSTRAP DONE --------')
