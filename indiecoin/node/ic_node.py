import json
import threading

from .ic_peer import IndieCoinPeer
from .. import blockchain

from protocol.response import Response
from protocol import protocol


class IndieCoinNode(IndieCoinPeer):
    """ Indie Coin P2P Node

        Network module for indiecoin. Mantains communication with
        other nodes, listens and relays transactions and blocks.

        On the contructor we declare a main_thread that will run
        mainloop from our indiecoin.node.bt_peer.BTPeer class.

        Main loop has an infinite loop listening for incomming
        connection in a socket. When it recieves one it creates
        a thread to answer that request. Each request must come
        with an identifier specifing which type of request it is.
        The types are defined in indiecoin.node.protocol.protocol.
        Each type of request is maped to a function that can
        process that request in BTPeer.handlers

        This class has the defined handlers for the indiecoin protocol.
        BTPeer is a generic P2P framework for mantaining and establishing
        connections.

        Attributes
        ----------

            miner: indiecoin.miner.miner.Miner
                miner instance that will be generating a new block
                from the transaction_queue to spread over the network.
            main_thread = threading.Thread
                main thread on which the node runs.
            transactions_queue: list
                list for incoming transactions that will be mined
                in future blocks to enter the blockchain.

        Notes
        -----
        Inherits from an IndieCoinPeer
    """
    def __init__(self, maxpeers, serverport, miner=None):
        """ Constructor for an IndieCoinPeer, declares main thread
            on which node will run main_loop.

            Maps requests types from protocol to handler functions.
            Add this requests types to the handlers from BTPeer.

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
        """ Prints a message to screen.
            @TODO:
                Set variables for debug level so user can specify the
                level of output he want to receive from the program.
        """
        print(msg)

    def start(self):
        """ Begins main thread inherite from indiecoin.node.bt_peer.py,
            runs thread that listens for clientes with incoming transactions.
        """
        self.main_thread.start()

    def connect_and_send(self, peer, msg_type, msg_data='', pid=None, waitreply=True):
        """ Wrapper over BTPeer.connectandsend() function. Send data to a peer for a
            specific purpose.

            Returns
            -------
                response: indiecoin.node.protocol.response
                    response object with response data and protocol message type.

            Raises
            ------
                Exception: Exception
                    If there is no response from peer.
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
        """ function handler for protocol.MAX_BLOCK_HEIGHT, handles a
            request of a peer that want to know the block with maximum
            height of local blockchain. Answers with an integer indicating
            current height of blockchain.
        """
        response = '{}'.format(blockchain.BlockChain().get_height())
        peer_connection.send_data(protocol.REPLY, response)

    def __handle_block_get(self, peer_connection, block_id):
        """ function handler for protocol.BLOCK_GET and protocol.BLOCK_HEIGHT
            handles a peer's query for a block. The peer can ask for a block
            based on its height or on its hash.

            if the query data is 64 characters long we asume its a hash, else
            its asking for a height.

            Answers with the specific block queried or protocol.Error block not
            found.

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
        """ handles relay transaction. Recieves an incomming transaction
            from a peer. Validates transaction. If we already have that
            transaction on queue or on database, we can discard it.

            If we don't, we add it to our queue and we broadcast it to
            all of our peers, (except the one who sent it to us.)
        """
        data = json.loads(data)

        try:
            transaction = blockchain.transaction.Transaction(**data)
        except AssertionError as e:
            self.__debug(e[0])
            return

        if transaction in self.transactions_queue or transaction.exists():
            return

        if transaction.is_valid():
            self.transactions_queue.append(transaction)

            for peer in self.get_peer_ids():
                if peer != peer_connection.id:
                    self.connect_and_send(
                        peer,
                        protocol.RELAY_TRANSACTION,
                        transaction.to_json(),
                        None,
                        False)

    def __handle_relay_block(self, peer_connection, data):
        """ handles relay transaction. Recieves an incomming block
            from a peer. Validates block. If we do not have this block
            yet in our database, we save it. We check for any transaction
            in this block that might be in our queue and clean it.

            Finally we broadcast the block to all peers on the network.

            @TODO:
                If the user is running a miner node, we must notify mining
                thread to stop and begin with a new block and start mining
                again.

                Verify that this block goes to the top, I still haven't
                implemented all the logic that arises from the complexity
                of actually trusting the proof of work.

        """
        data = json.loads(data)

        try:
            block = blockchain.block.Block(**data)
        except AssertionError as e:
            self.__debug(e[0])
            return

        if not block.exists():

            if self.miner:
                # MINER SHIT
                pass

            block.save()

            for transaction in block.transactions:
                for queue_transaction in self.transactions_queue:
                    if queue_transaction.hash == transaction.hash:
                        self.transactions_queue.remove(queue_transaction)

            for peer in self.get_peer_ids():
                if peer != peer_connection.id:
                    self.connect_and_send(peer, protocol.RELAY_BLOCK, block.to_json(), None, False)

    def bootstrap(self):
        """ Bootstraps a node that just went online. After building a list
            of peers, it asks its peers for their blockchain height. It checks
            if the max height is bigger than its own height and if it is, it
            asks for all the blocks its missing.

            Catches up on the network.
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
